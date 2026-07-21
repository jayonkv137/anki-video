"""Stages — one pure function per pipeline stage.

Each stage: (RCP, inputs) → artifact(s). The CLI dispatches stages
based on ledger state. Stages don't know about each other — they're
wired together by cli.py.
"""

import json
import os
import random
import re
from pathlib import Path

import requests
from anthropic import Anthropic

from . import ledger
from .rcp import RunContextPack, REPO

MODEL = "claude-sonnet-5"
HAIKU = "claude-haiku-4-5"  # quality-check / chore tier — cheap, fast
SKILLS = REPO / "prompts" / "skills"
RESOURCES = REPO / "resources"
ARTICLES = ("der ", "die ", "das ")


def _load_skill(name: str) -> str:
    return (SKILLS / name).read_text(encoding="utf-8")


def _schema(**props):
    req = list(props)
    return {"type": "object", "properties": props, "required": req, "additionalProperties": False}


def _arr(item):
    return {"type": "array", "items": item}


STR = {"type": "string"}
INT = {"type": "integer"}
BOOL = {"type": "boolean"}

# ── Schemas ──────────────────────────────────────────────────────

STORY_SCHEMA = _schema(
    title_de=STR, scenario=STR, environment=STR, mains=_arr(STR), cameos=_arr(STR),
    belief_challenged=_schema(character=STR, belief=STR, how=STR),
    hook_visual=STR, human_beat=STR,
    beats=_arr(STR),
    word_plan=_arr(_schema(position=INT, german=STR, beat_index=INT, how_used=STR, sense_note=STR)),
)

# Story options: three premises (lighter schema for Gate A)
OPTION_SCHEMA = _schema(
    title_de=STR, scenario=STR, scenario_en=STR,
    environment=STR, environment_en=STR, mains=_arr(STR),
    hook_visual=STR, hook_visual_en=STR,
    human_beat=STR, human_beat_en=STR,
    four_beat_sketch=_arr(STR), sketch_en=STR,
    word_fit_notes=STR, self_score=INT,
)

OPTIONS_SCHEMA = _schema(options=_arr(OPTION_SCHEMA))

SCREENPLAY_SCHEMA = _schema(
    title_de=STR, environment=STR,
    scenes=_arr(_schema(
        scene_number=INT, position=INT, german_word=STR, duration_s=INT,
        setting=STR, action_en=STR,
        dialogue=_arr(_schema(speaker=STR, german=STR, english=STR)),
        target_word_emphasis=STR, continuity_notes=STR, learning_check=STR,
    )),
)

REF_SCHEMA = _schema(slot=STR, binds=STR, role=STR)

PROMPTS_SCHEMA = _schema(
    scenes=_arr(_schema(
        scene_number=INT,
        characters_in_frame=_arr(STR),
        seedance=_schema(prompt=STR, reference_assets=_arr(REF_SCHEMA)),
        omni=_schema(base_prompt=STR, edit_turns=_arr(STR), reference_images=_arr(REF_SCHEMA)),
    )),
)

# Quality check: binary checklist + JSON verdict (skill-2q on Haiku 4.5)
QC_SCHEMA = _schema(
    passed=BOOL,
    checks=_arr(_schema(name=STR, passed=BOOL, issue=STR)),
    feedback=STR,
)


# ── LLM call helper ─────────────────────────────────────────────

def _call(client: Anthropic, system: str, user: str, label: str,
          schema: dict, run_id: str, stage: str,
          model: str = MODEL, max_tokens: int = 24000) -> tuple[dict, int, int]:
    """Call Anthropic with structured output. Returns (parsed_json, tokens_in, tokens_out)."""
    with client.messages.stream(
        model=model, max_tokens=max_tokens, system=system,
        output_config={"format": {"type": "json_schema", "schema": schema}},
        messages=[{"role": "user", "content": user}],
    ) as stream:
        resp = stream.get_final_message()

    t_in, t_out = resp.usage.input_tokens, resp.usage.output_tokens
    print(f"[{label}: {t_in} in / {t_out} out]")

    text = next(b.text for b in resp.content if b.type == "text")
    result = json.loads(text)

    # Track cost
    ledger.add_cost(run_id, t_in, t_out)

    return result, t_in, t_out


# ── Word fetching ────────────────────────────────────────────────

def fetch_words(start: int | None, randomize: bool) -> list[dict]:
    """Fetch 10 words from Supabase."""
    url = os.environ["SUPABASE_URL"].rstrip("/") + "/rest/v1/words"
    h = {"apikey": os.environ["SUPABASE_SECRET_KEY"],
         "Authorization": f"Bearer {os.environ['SUPABASE_SECRET_KEY']}"}
    sel = "position,german,english,sentence_de,sentence_en,word_type"
    if randomize:
        pos = sorted(random.sample(range(1, 606), 10))
        params = {"position": f"in.({','.join(map(str, pos))})", "order": "position.asc", "select": sel}
    else:
        params = {"position": f"gte.{start or 1}", "order": "position.asc", "limit": "10", "select": sel}
    r = requests.get(url, headers=h, params=params, timeout=15)
    r.raise_for_status()
    words = r.json()
    assert len(words) == 10, f"expected 10 words, got {len(words)}"
    return words


def fetch_words_by_positions(positions: list[int]) -> list[dict]:
    """Fetch EXACTLY these word positions (choose/resume: reload a run's own words —
    a gte+limit fetch would silently return the wrong set for --random runs)."""
    url = os.environ["SUPABASE_URL"].rstrip("/") + "/rest/v1/words"
    h = {"apikey": os.environ["SUPABASE_SECRET_KEY"],
         "Authorization": f"Bearer {os.environ['SUPABASE_SECRET_KEY']}"}
    sel = "position,german,english,sentence_de,sentence_en,word_type"
    params = {"position": f"in.({','.join(map(str, positions))})",
              "order": "position.asc", "select": sel}
    r = requests.get(url, headers=h, params=params, timeout=15)
    r.raise_for_status()
    words = r.json()
    assert len(words) == len(positions), \
        f"expected {len(positions)} words for {positions}, got {len(words)}"
    return words


# ── Stage 1: Words ───────────────────────────────────────────────

def stage_words(run_id: str, start: int | None, randomize: bool) -> list[dict]:
    """Fetch words and record in ledger."""
    words = fetch_words(start, randomize)
    positions = [w["position"] for w in words]
    ledger.update_run(run_id, word_positions=positions, stage="words")
    ledger.log_event(run_id, "words", "completed",
                     detail={"positions": positions,
                             "words": [w["german"] for w in words]})
    print("words:", ", ".join(f"{w['position']}:{w['german']}" for w in words))
    return words


# ── Stage 2: Story options (3 premises for Gate A) ───────────────

def stage_story_options(run_id: str, rcp: RunContextPack, words: list[dict],
                        note: str, ep_dir: Path, client: Anthropic) -> dict:
    """Generate 3 story premise options. Pipeline pauses after this for Gate A."""
    skill = _load_skill("skill-1a-story-options.md")
    skill = (
        skill.replace("{{CHARACTER_BIBLE}}", rcp.character_bible)
        .replace("{{WORDS_JSON}}", json.dumps(words, ensure_ascii=False))
        .replace("{{EPISODE_LOG}}", json.dumps(rcp.episode_log_raw, ensure_ascii=False))
        .replace("{{JAYON_DIRECTIVE}}", note or "(none)")
    )
    options_system = rcp.for_story_stage() + "\n\n" + skill

    options, t_in, t_out = _call(
        client, options_system,
        "Produce exactly 3 story premise options as JSON now.",
        "skill-1a options", OPTIONS_SCHEMA, run_id, "story_options",
    )

    # Save options
    ep_dir.mkdir(parents=True, exist_ok=True)
    options_path = ep_dir / "options.json"
    options_path.write_text(json.dumps(options, ensure_ascii=False, indent=2), encoding="utf-8")

    # Write human-readable options.md (German + English side by side)
    md = ["# Story Options — choose one\n"]
    for i, opt in enumerate(options.get("options", []), 1):
        md.append(f"## Option {i}: {opt.get('title_de', '?')} (score: {opt.get('self_score', '?')}/10)\n")
        md.append(f"**Scenario (DE):** {opt.get('scenario', '')}\n")
        md.append(f"**Scenario (EN):** {opt.get('scenario_en', '')}\n")
        md.append(f"**Environment:** {opt.get('environment', '')} — {opt.get('environment_en', '')}\n")
        md.append(f"**Mains:** {', '.join(opt.get('mains', []))}\n")
        md.append(f"**Hook (DE):** {opt.get('hook_visual', '')}\n")
        md.append(f"**Hook (EN):** {opt.get('hook_visual_en', '')}\n")
        md.append(f"**Human beat (DE):** {opt.get('human_beat', '')}\n")
        md.append(f"**Human beat (EN):** {opt.get('human_beat_en', '')}\n")
        md.append(f"**Sketch (DE):** {' → '.join(opt.get('four_beat_sketch', []))}\n")
        md.append(f"**Sketch (EN):** {opt.get('sketch_en', '')}\n")
        md.append(f"**Word fit:** {opt.get('word_fit_notes', '')}\n")
    md.append("\n---\n")
    md.append("Choose with: `python -m pipeline choose <1|2|3> [--note \"...\"]`\n")
    (ep_dir / "options.md").write_text("\n".join(md), encoding="utf-8")

    # Record in ledger
    sha = ledger.sha256_file(options_path)
    ledger.log_event(run_id, "story_options", "completed",
                     artifact_path=str(options_path.relative_to(REPO)),
                     artifact_sha256=sha, tokens_in=t_in, tokens_out=t_out)
    ledger.update_run(run_id, status="awaiting_choice", stage="gate_a")

    print(f"\n{'='*60}")
    print(f"Gate A: 3 options written to {ep_dir.relative_to(REPO)}/options.md")
    print(f"Read them, then: python -m pipeline choose <1|2|3> [--note \"...\"]")
    print(f"{'='*60}")

    return options


# ── Stage 4: Story expand (chosen premise → full story) ──────────

def stage_story_expand(run_id: str, rcp: RunContextPack, words: list[dict],
                       chosen_option: dict, note: str, ep_dir: Path,
                       client: Anthropic) -> dict:
    """Expand chosen premise into a full 12-16 beat story."""
    skill = _load_skill("skill-1b-story-expand.md")
    skill = (
        skill.replace("{{CHARACTER_BIBLE}}", rcp.character_bible)
        .replace("{{WORDS_JSON}}", json.dumps(words, ensure_ascii=False))
        .replace("{{EPISODE_LOG}}", json.dumps(rcp.episode_log_raw, ensure_ascii=False))
        .replace("{{CHOSEN_PREMISE}}", json.dumps(chosen_option, ensure_ascii=False, indent=2))
        .replace("{{JAYON_DIRECTIVE}}", note or "(none)")
    )
    expand_system = rcp.for_story_stage() + "\n\n" + skill

    story, t_in, t_out = _call(
        client, expand_system,
        "Expand this chosen premise into the full story decision JSON now.",
        "skill-1b expand", STORY_SCHEMA, run_id, "story_expand",
    )

    story_path = ep_dir / "story.json"
    story_path.write_text(json.dumps(story, ensure_ascii=False, indent=2), encoding="utf-8")
    sha = ledger.sha256_file(story_path)
    ledger.log_event(run_id, "story_expand", "completed",
                     artifact_path=str(story_path.relative_to(REPO)),
                     artifact_sha256=sha, tokens_in=t_in, tokens_out=t_out)
    ledger.update_run(run_id, stage="story_expand")

    print(f"→ {story.get('title_de')} | {story.get('scenario')} | mains: {story.get('mains')}")
    return story


# ── Stage 5: Screenplay ─────────────────────────────────────────

def word_stem(g: str) -> str:
    w = g.lower()
    for a in ARTICLES:
        if w.startswith(a):
            return w[len(a):]
    if (w.endswith("eln") or w.endswith("ern")) and len(w) > 4:
        return w[:-1]
    if w.endswith("en") and len(w) > 4:
        return w[:-2]
    return w


def validate_screenplay(sp: dict, words: list[dict]) -> list[str]:
    problems = []
    scenes = sp.get("scenes", [])
    if len(scenes) != 10:
        problems.append(f"expected 10 scenes, got {len(scenes)}")
    by_pos = {w["position"]: w for w in words}
    seen = set()
    for sc in scenes:
        pos = sc.get("position")
        if pos not in by_pos:
            problems.append(f"scene {sc.get('scene_number')}: unknown position {pos}")
            continue
        seen.add(pos)
        text = " ".join(d.get("german", "") for d in sc.get("dialogue", [])).lower()
        if word_stem(by_pos[pos]["german"]) not in text:
            problems.append(f"scene {sc.get('scene_number')}: '{by_pos[pos]['german']}' not in its German dialogue")
        for d in sc.get("dialogue", []):
            if d.get("speaker", "").startswith("Müller") and len(d.get("german", "").split()) > 3:
                problems.append(f"scene {sc.get('scene_number')}: Müller exceeds word budget: {d['german']!r}")
    missing = set(by_pos) - seen
    if missing:
        problems.append(f"words without scenes: {sorted(missing)}")
    return problems


def stage_screenplay(run_id: str, rcp: RunContextPack, words: list[dict],
                     story: dict, ep_dir: Path, client: Anthropic,
                     qc_feedback: str = "") -> tuple[dict, list[str]]:
    """Generate screenplay with validate → one retry.

    qc_feedback: when set (the ONE post-QC rewrite), the writer gets the
    quality-check verdict and must address it — dialogue naturalness first.
    """
    skill = _load_skill("skill-2-screenplay-writer.md")
    skill = (
        skill.replace("{{CHARACTER_BIBLE}}", rcp.character_bible)
        .replace("{{WORDS_JSON}}", json.dumps(words, ensure_ascii=False))
        .replace("{{STORY_JSON}}", json.dumps(story, ensure_ascii=False))
    )
    system = rcp.for_screenplay_stage() + "\n\n" + skill

    if qc_feedback:
        user_msg = (
            "A previous screenplay draft FAILED the quality check. "
            "The judge's feedback:\n" + qc_feedback +
            "\n\nWrite the screenplay again, fixing every issue named above. "
            "Produce the corrected screenplay JSON now."
        )
        label = "skill-2 qc-rewrite"
    else:
        user_msg = "Produce the screenplay JSON now."
        label = "skill-2 screenplay"

    sp, t_in, t_out = _call(
        client, system, user_msg,
        label, SCREENPLAY_SCHEMA, run_id, "screenplay",
    )

    problems = validate_screenplay(sp, words)
    if problems:
        print("! screenplay validation failed, retrying with feedback:")
        for p in problems:
            print("  -", p)
        sp, t_in2, t_out2 = _call(
            client, system,
            "Your previous attempt failed validation:\n"
            + "\n".join(problems) + "\nFix these issues. Produce the corrected screenplay JSON now.",
            "skill-2 retry", SCREENPLAY_SCHEMA, run_id, "screenplay",
        )
        t_in += t_in2
        t_out += t_out2
        problems = validate_screenplay(sp, words)

    sp_path = ep_dir / "screenplay.json"
    sp_path.write_text(json.dumps(sp, ensure_ascii=False, indent=2), encoding="utf-8")
    sha = ledger.sha256_file(sp_path)
    ledger.log_event(run_id, "screenplay", "completed" if not problems else "completed",
                     artifact_path=str(sp_path.relative_to(REPO)),
                     artifact_sha256=sha, tokens_in=t_in, tokens_out=t_out,
                     detail={"validation_problems": problems})
    ledger.update_run(run_id, stage="screenplay")

    return sp, problems


# ── Stage 6: Quality check (code validators + skill-2q LLM checklist) ──

def stage_quality_check(run_id: str, rcp: RunContextPack, sp: dict,
                        words: list[dict], client: Anthropic) -> tuple[bool, list[str], str]:
    """Quality check = code validators + skill-2q LLM checklist (Haiku 4.5).

    Returns (passed, problems, feedback). On failure the CLI feeds `feedback`
    into ONE rewrite of stage 5, then re-judges once. The verdict is always
    recorded truthfully in the ledger either way.
    """
    # 1. Code validators (scene count, word coverage, Müller budget)
    code_problems = validate_screenplay(sp, words)

    # 2. LLM checklist — skill-2q judged by Haiku 4.5 (cheap, strict)
    skill = _load_skill("skill-2q-quality-check.md")
    skill = (
        skill.replace("{{CHARACTER_BIBLE}}", rcp.character_bible)
        .replace("{{WORDS_JSON}}", json.dumps(words, ensure_ascii=False))
        .replace("{{SCREENPLAY_JSON}}", json.dumps(sp, ensure_ascii=False))
    )
    system = rcp.for_screenplay_stage() + "\n\n" + skill

    verdict, t_in, t_out = _call(
        client, system,
        "Judge this screenplay against the checklist. Return the JSON verdict now.",
        "skill-2q quality", QC_SCHEMA, run_id, "quality_check",
        model=HAIKU, max_tokens=4000,
    )

    # 3. Merge code + LLM verdicts — pass only if BOTH pass
    llm_problems = [
        f"{c.get('name')}: {c.get('issue')}"
        for c in verdict.get("checks", [])
        if not c.get("passed", True) and c.get("issue")
    ]
    problems = code_problems + llm_problems
    passed = (not code_problems) and bool(verdict.get("passed", False))

    ledger.log_event(run_id, "quality_check", "completed" if passed else "failed",
                     tokens_in=t_in, tokens_out=t_out,
                     detail={"passed": passed, "code_problems": code_problems,
                             "llm_verdict": verdict})
    ledger.update_run(run_id, stage="quality_check")

    feedback = verdict.get("feedback", "") or ""
    if passed:
        print("✓ quality check passed (code + skill-2q)")
    else:
        print("⚠ quality check issues:")
        for p in problems:
            print(f"  - {p}")
        if feedback:
            print(f"  → feedback for rewrite: {feedback}")
    return passed, problems, feedback


# ── Stage 7: Prompt writer + canon substitution + refs manifest ──────

def _norm(s: str) -> str:
    """Fold umlauts/ß so canonical names match resources/ folder names."""
    return (s.lower().replace("ü", "u").replace("ö", "o")
            .replace("ä", "a").replace("ß", "ss").strip())


def _character_ref_path(name: str) -> str | None:
    """Resolve a canonical character name → its primary identity image (absolute path)."""
    if not RESOURCES.exists():
        return None
    target = _norm(name)
    for d in sorted(RESOURCES.iterdir()):
        if d.is_dir() and _norm(d.name) == target:
            pngs = sorted(d.glob("*.png"))
            for pref in ("main", "master", "sheet"):
                for p in pngs:
                    if pref in p.name.lower():
                        return str(p.resolve())
            return str(pngs[0].resolve()) if pngs else None
    return None


def _resolve_binds(binds: str, role: str) -> dict:
    """Resolve a ref 'binds' target → {path, status}. Character refs resolve to real
    files; style/audio are pending until C1 (style-lock) / C3 (per-run audio)."""
    if binds == "style" or role == "style":
        return {"path": None, "status": "pending — C1 style-lock"}
    if binds in ("audio-master", "audio") or role == "audio":
        return {"path": None, "status": "pending — per-run audio (C3)"}
    path = _character_ref_path(binds)
    if path:
        return {"path": path, "status": "resolved"}
    return {"path": None, "status": f"unresolved — no asset for '{binds}'"}


def build_refs_manifest(prompts: dict, run_id: str, ep_dir: Path) -> dict:
    """scene → the unique reference assets it needs, each resolved to a file path
    (or pending). Aggregated across both engine packages, deduped by (binds, role)."""
    scenes = {}
    for sc in prompts.get("scenes", []):
        refs, seen = [], set()
        pooled = (sc.get("seedance", {}).get("reference_assets", [])
                  + sc.get("omni", {}).get("reference_images", []))
        for r in pooled:
            binds, role = r.get("binds", ""), r.get("role", "")
            if (binds, role) in seen:
                continue
            seen.add((binds, role))
            refs.append({"binds": binds, "role": role, **_resolve_binds(binds, role)})
        scenes[str(sc.get("scene_number"))] = refs
    return {"run_id": run_id, "episode": ep_dir.name, "scenes": scenes}


def substitute_canon(prompts: dict) -> dict:
    """Mechanically substitute {{STYLE_BLOCK}} and {{CHAR_BLOCK:Name}} placeholders
    in both engine packages (seedance.prompt, omni.base_prompt, omni.edit_turns)."""
    canon = (REPO / "prompts" / "canon" / "canon_blocks.md").read_text(encoding="utf-8")

    def block(header):
        m = re.search(rf"## {re.escape(header)}\n(.+?)(?=\n## |\Z)", canon, re.S)
        if not m:
            first = header.split(":")[-1].strip().split()[0]
            m = re.search(rf"## CHAR_BLOCK: {re.escape(first)}[^\n]*\n(.+?)(?=\n## |\Z)", canon, re.S)
        return m.group(1).strip() if m else f"[MISSING CANON: {header}]"

    style = block("STYLE_BLOCK")

    def sub(text):
        text = text.replace("{{STYLE_BLOCK}}", style)
        return re.sub(r"\{\{CHAR_BLOCK:([^}]+)\}\}", lambda m: block(f"CHAR_BLOCK: {m.group(1).strip()}"), text)

    for sc in prompts.get("scenes", []):
        sd = sc.get("seedance", {})
        if isinstance(sd, dict) and "prompt" in sd:
            sd["prompt"] = sub(sd.get("prompt") or "")
        om = sc.get("omni", {})
        if isinstance(om, dict):
            if "base_prompt" in om:
                om["base_prompt"] = sub(om.get("base_prompt") or "")
            if "edit_turns" in om:
                om["edit_turns"] = [sub(t) for t in om.get("edit_turns", [])]
    return prompts


def stage_prompts(run_id: str, rcp: RunContextPack, sp: dict,
                  ep_dir: Path, client: Anthropic) -> dict:
    """Generate dual Seedance/Omni packages → canon substitution → per-scene split + refs manifest."""
    skill = _load_skill("skill-3-prompt-writer.md")
    skill = skill.replace("{{SCREENPLAY_JSON}}", json.dumps(sp, ensure_ascii=False))
    system = rcp.for_prompt_stage() + "\n\n" + skill

    prompts, t_in, t_out = _call(
        client, system, "Produce the dual Seedance/Omni prompt packages JSON now.",
        "skill-3 prompts", PROMPTS_SCHEMA, run_id, "prompts",
    )
    prompts = substitute_canon(prompts)

    # Combined artifact (hashed in ledger)
    prompts_path = ep_dir / "prompts.json"
    prompts_path.write_text(json.dumps(prompts, ensure_ascii=False, indent=2), encoding="utf-8")

    # Per-scene split into scene_NN.{seedance,omni}.json + refs_manifest.json
    prompts_dir = ep_dir / "prompts"
    prompts_dir.mkdir(parents=True, exist_ok=True)
    for sc in prompts.get("scenes", []):
        n = sc.get("scene_number")
        (prompts_dir / f"scene_{n:02d}.seedance.json").write_text(
            json.dumps(sc.get("seedance", {}), ensure_ascii=False, indent=2), encoding="utf-8")
        (prompts_dir / f"scene_{n:02d}.omni.json").write_text(
            json.dumps(sc.get("omni", {}), ensure_ascii=False, indent=2), encoding="utf-8")
    manifest = build_refs_manifest(prompts, run_id, ep_dir)
    manifest_path = prompts_dir / "refs_manifest.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

    sha = ledger.sha256_file(prompts_path)
    n_scenes = len(prompts.get("scenes", []))
    ledger.log_event(run_id, "prompts", "completed",
                     artifact_path=str(prompts_path.relative_to(REPO)),
                     artifact_sha256=sha, tokens_in=t_in, tokens_out=t_out,
                     detail={"scenes": n_scenes,
                             "refs_manifest": str(manifest_path.relative_to(REPO))})
    ledger.update_run(run_id, stage="prompts")

    print(f"→ {n_scenes} scenes: seedance + omni packages + refs_manifest → {prompts_dir.relative_to(REPO)}/")
    return prompts


# ── Stage 8: Finalize ────────────────────────────────────────────

def stage_finalize(run_id: str, story: dict, sp: dict, prompts: dict,
                   words: list[dict], ep_dir: Path):
    """Write episode.md, save to series memory, mark run complete."""
    # Pretty episode.md
    md = [
        f"# {sp.get('title_de', story.get('title_de'))}\n",
        f"Scenario: {story.get('scenario')} · Environment: {sp.get('environment')}",
        f"Mains: {', '.join(story.get('mains', []))} · Cameos: {', '.join(story.get('cameos', []))}",
        f"Hook: {story.get('hook_visual')}\nHuman beat: {story.get('human_beat')}\n",
    ]
    for sc in sp.get("scenes", []):
        md.append(f"\n## Scene {sc['scene_number']} — {sc['german_word']} ({sc['duration_s']}s)")
        md.append(f"*{sc['setting']}*\n\n{sc['action_en']}\n")
        for d in sc.get("dialogue", []):
            line = '- **' + d['speaker'] + ':** „' + d['german'] + '"  *(' + d.get('english', '') + ')*'
            md.append(line)
        md.append(f"\n> learns: {sc.get('learning_check', '')}")
        pr = next((p for p in prompts.get("scenes", []) if p.get("scene_number") == sc["scene_number"]), {})
        if pr:
            sd_text = pr.get("seedance", {}).get("prompt", "")
            om_text = pr.get("omni", {}).get("base_prompt", "")
            md.append(f'\n<details><summary>Seedance prompt</summary>\n\n```\n{sd_text}\n```\n</details>')
            md.append(f'\n<details><summary>Omni base prompt</summary>\n\n```\n{om_text}\n```\n</details>')
    (ep_dir / "episode.md").write_text("\n".join(md), encoding="utf-8")

    # Save to series memory
    ledger.save_episode(
        run_id=run_id,
        title_de=story.get("title_de", ""),
        scenario=story.get("scenario", ""),
        environment=sp.get("environment", ""),
        mains=story.get("mains", []),
        cameos=story.get("cameos", []),
        word_positions=[w["position"] for w in words],
    )

    # Mark complete
    ledger.log_event(run_id, "finalize", "completed",
                     artifact_path=str((ep_dir / "episode.md").relative_to(REPO)))
    run = ledger.update_run(run_id, status="completed", stage="finalize",
                            completed_at="now()")

    print(f"\n{'='*60}")
    print(f"✅ Run complete! Saved to {ep_dir.relative_to(REPO)}/")
    print(f"   Total cost: ~{run.get('cost_cents', 0)} cents")
    print(f"   Read episode.md and judge the quality.")
    print(f"{'='*60}")

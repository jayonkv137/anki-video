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
SKILLS = REPO / "prompts" / "skills"
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
    title_de=STR, scenario=STR, environment=STR, mains=_arr(STR),
    hook_visual=STR, human_beat=STR,
    four_beat_sketch=_arr(STR),
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

PROMPTS_SCHEMA = _schema(
    scenes=_arr(_schema(
        scene_number=INT, characters_in_frame=_arr(STR),
        veo_flow_prompt=STR, seedance_prompt=STR,
        avoid_list=STR,
        continuity=_schema(use_last_frame={"type": "boolean"}, reason=STR),
        reference_images=_arr(STR),
        dialogue_check=_arr(_schema(speaker=STR, german=STR)),
    )),
)


# ── LLM call helper ─────────────────────────────────────────────

def _call(client: Anthropic, system: str, user: str, label: str,
          schema: dict, run_id: str, stage: str) -> tuple[dict, int, int]:
    """Call Anthropic with structured output. Returns (parsed_json, tokens_in, tokens_out)."""
    with client.messages.stream(
        model=MODEL, max_tokens=24000, system=system,
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
    skill = _load_skill("skill-1-story-selector.md")
    skill = (
        skill.replace("{{CHARACTER_BIBLE}}", rcp.character_bible)
        .replace("{{WORDS_JSON}}", json.dumps(words, ensure_ascii=False))
        .replace("{{EPISODE_LOG}}", json.dumps(rcp.episode_log_raw, ensure_ascii=False))
        .replace("{{JAYON_DIRECTIVE}}", note or "(none)")
    )

    # Modify system prompt to request 3 options instead of 1 committed story
    options_system = (
        rcp.for_story_stage() + "\n\n" + skill + "\n\n"
        "OVERRIDE: Instead of committing to ONE story, produce EXACTLY 3 premise options.\n"
        "For each option: title_de, scenario, environment, mains, hook_visual, human_beat, "
        "four_beat_sketch (4 strings), word_fit_notes (how the hard words fit), self_score (1-10).\n"
        "Return JSON: {\"options\": [option1, option2, option3]}"
    )

    options, t_in, t_out = _call(
        client, options_system,
        "Produce exactly 3 story premise options as JSON now.",
        "skill-1a options", OPTIONS_SCHEMA, run_id, "story_options",
    )

    # Save options
    ep_dir.mkdir(parents=True, exist_ok=True)
    options_path = ep_dir / "options.json"
    options_path.write_text(json.dumps(options, ensure_ascii=False, indent=2), encoding="utf-8")

    # Write human-readable options.md
    md = ["# Story Options — choose one\n"]
    for i, opt in enumerate(options.get("options", []), 1):
        md.append(f"## Option {i}: {opt.get('title_de', '?')} (score: {opt.get('self_score', '?')}/10)\n")
        md.append(f"**Scenario:** {opt.get('scenario', '')}\n")
        md.append(f"**Environment:** {opt.get('environment', '')}\n")
        md.append(f"**Mains:** {', '.join(opt.get('mains', []))}\n")
        md.append(f"**Hook:** {opt.get('hook_visual', '')}\n")
        md.append(f"**Human beat:** {opt.get('human_beat', '')}\n")
        md.append(f"**Sketch:** {' → '.join(opt.get('four_beat_sketch', []))}\n")
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
    skill = _load_skill("skill-1-story-selector.md")
    skill = (
        skill.replace("{{CHARACTER_BIBLE}}", rcp.character_bible)
        .replace("{{WORDS_JSON}}", json.dumps(words, ensure_ascii=False))
        .replace("{{EPISODE_LOG}}", json.dumps(rcp.episode_log_raw, ensure_ascii=False))
        .replace("{{JAYON_DIRECTIVE}}", note or "(none)")
    )

    expand_system = (
        rcp.for_story_stage() + "\n\n" + skill + "\n\n"
        "CONTEXT: Jayon chose the following premise. Expand it into the full story output "
        "(the standard Skill 1 JSON schema with all fields including beats and word_plan).\n\n"
        f"CHOSEN PREMISE:\n{json.dumps(chosen_option, ensure_ascii=False, indent=2)}\n"
    )
    if note:
        expand_system += f"\nJAYON'S STEERING NOTE: {note}\n"

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
                     story: dict, ep_dir: Path, client: Anthropic) -> tuple[dict, list[str]]:
    """Generate screenplay with validate → one retry."""
    skill = _load_skill("skill-2-screenplay-writer.md")
    skill = (
        skill.replace("{{CHARACTER_BIBLE}}", rcp.character_bible)
        .replace("{{WORDS_JSON}}", json.dumps(words, ensure_ascii=False))
        .replace("{{STORY_JSON}}", json.dumps(story, ensure_ascii=False))
    )
    system = rcp.for_screenplay_stage() + "\n\n" + skill

    sp, t_in, t_out = _call(
        client, system, "Produce the screenplay JSON now.",
        "skill-2 screenplay", SCREENPLAY_SCHEMA, run_id, "screenplay",
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


# ── Stage 6: Quality check (placeholder — E5 builds the real one) ──

def stage_quality_check(run_id: str, sp: dict, words: list[dict]) -> tuple[bool, list[str]]:
    """Code-based quality check (E5 adds LLM checklist)."""
    problems = validate_screenplay(sp, words)
    passed = len(problems) == 0
    ledger.log_event(run_id, "quality_check", "completed" if passed else "failed",
                     detail={"passed": passed, "problems": problems})
    ledger.update_run(run_id, stage="quality_check")
    if passed:
        print("✓ quality check passed")
    else:
        print("⚠ quality check issues:")
        for p in problems:
            print(f"  - {p}")
    return passed, problems


# ── Stage 7: Prompt writer + canon substitution ──────────────────

def substitute_canon(prompts: dict) -> dict:
    """Mechanically substitute {{STYLE_BLOCK}} and {{CHAR_BLOCK:Name}} placeholders."""
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
        sc["veo_flow_prompt"] = sub(sc.get("veo_flow_prompt", ""))
        sc["seedance_prompt"] = sub(sc.get("seedance_prompt", ""))
    return prompts


def stage_prompts(run_id: str, rcp: RunContextPack, sp: dict,
                  ep_dir: Path, client: Anthropic) -> dict:
    """Generate video prompts + apply canon substitution."""
    skill = _load_skill("skill-3-prompt-writer.md")
    skill = skill.replace("{{SCREENPLAY_JSON}}", json.dumps(sp, ensure_ascii=False))
    system = rcp.for_prompt_stage() + "\n\n" + skill

    prompts, t_in, t_out = _call(
        client, system, "Produce the prompts JSON now.",
        "skill-3 prompts", PROMPTS_SCHEMA, run_id, "prompts",
    )
    prompts = substitute_canon(prompts)

    prompts_path = ep_dir / "prompts.json"
    prompts_path.write_text(json.dumps(prompts, ensure_ascii=False, indent=2), encoding="utf-8")
    sha = ledger.sha256_file(prompts_path)
    ledger.log_event(run_id, "prompts", "completed",
                     artifact_path=str(prompts_path.relative_to(REPO)),
                     artifact_sha256=sha, tokens_in=t_in, tokens_out=t_out)
    ledger.update_run(run_id, stage="prompts")

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
            veo_text = pr.get('veo_flow_prompt', '')
            md.append(f'\n<details><summary>Veo/Flow prompt</summary>\n\n```\n{veo_text}\n```\n</details>')
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

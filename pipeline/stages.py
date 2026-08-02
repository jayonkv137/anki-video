"""Stages — one pure function per pipeline stage.

Each stage: (RCP, inputs) → artifact(s). The CLI dispatches stages
based on ledger state. Stages don't know about each other — they're
wired together by cli.py.
"""

import json
import os
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


# Story options: three premises (lighter schema for Gate A)


# V3 screenplay (2026-07-22): stereotype-driven, 2–3 SEGMENTS = 2–3 Seedance clips
# (~15s each, one multi-shot generation per segment), NOT 10 one-per-word scenes.
DIALOGUE_LINE = _schema(speaker=STR, german=STR, english=STR)

# V3 director layer (2026-07-22, DESIGN_v3_data_flow.md): the filmmaker decisions the
# screenplay locks per shot — they feed BOTH the storyboard panel and the Seedance motion
# prompt. No on-screen/diegetic text (subtitles are a separate post step).
SHOT_SCHEMA = _schema(
    shot_number=INT,
    duration_s=INT,       # seconds this shot runs; a segment's shots sum to its ~15s
    shot_size=STR,        # ECU | CU | MCU | MS | MWS | WS | OTS
    camera_angle=STR,     # eye-level | low | high | dutch | POV
    camera_move=STR,      # the MOTION the video uses: "slow push-in" | "static" | "tracking" …
    action=STR,           # ONE visible action (canon §6 one-action rule)
    blocking=STR,         # who is where in the 9:16 vertical frame
    gaze=STR,             # eyelines (who looks at what)
    expression=STR,       # emotional beat (per character)
    dialogue=_arr(DIALOGUE_LINE),
)

SEGMENT_SCHEMA = _schema(
    segment_number=INT,
    duration_s=INT,       # ~15 — a single Seedance clip
    time_and_weather=STR, # time of day and weather for this segment
    shots=_arr(SHOT_SCHEMA),
)

SCREENPLAY_SCHEMA = _schema(
    title_de=STR,
    stereotype=STR,        # the German micro-behavior (from the compendium)
    typology=STR,          # one of the 5 (fixes grammar target + character pairing)
    cefr_level=STR,        # A1 | A2 | B1 — sets word/sentence/duration caps
    grammar_target=STR,    # the structure this episode teaches
    total_duration_s=INT,  # 30 (2×15) default, 45 (3×15) when needed
    environment=STR,
    global_aesthetic_rules=STR, # overall look, e.g. Cinematic 35mm, photorealistic
    target_vocab=_arr(_schema(german=STR, english=STR, gender=STR)),  # emergent; gender ∈ der/die/das/— for color-coding
    segments=_arr(SEGMENT_SCHEMA),
)

# ── Co-creation stage (V3) schemas — stereotype + human seed → Story Brief ──
# (see docs/planning/DESIGN_cocreation_stage.md). The Brief is the handoff into skill-2.

# skill-1a-align → options for the human (Ask-Don't-Guess); lesson_options carry BOTH particle + structure

# skill-1b-diverge → 3–5 distinct comedic angles (Refine-via-Examples)

# skill-1c-commit → critique + the locked Story Brief (the handoff into skill-2)

REF_SCHEMA = _schema(slot=STR, binds=STR, role=STR)

# V3 storyboard (skill-2b v2.0): ONE multi-panel SHEET prompt per SEGMENT (not per shot).
# The single generation locks identity+style across the segment's shots; the sheet is sliced
# back into per-shot 9:16 panels downstream. See RESEARCH_storyboard_sheet_method.md.
SHEET_PROMPT_SCHEMA = _schema(
    segment_number=INT,
    shot_numbers=_arr(INT),   # the shots this sheet contains, in reading order
    layout=STR,               # grid law "<rows>x<cols>": 1x2 | 1x3 | 2x2 | 2x3 (cells stay 9:16)
    sheet_aspect_ratio=STR,   # the SHEET's overall ratio "W:H" (cols·9 : rows·16); each CELL is 9:16
    sheet_prompt=STR,         # the ONE prompt that renders the whole multi-panel sheet
    continuity_ref=STR,       # "" for the first segment; else the prior sheet key "sheet_s<NN>"
)
STORYBOARD_SCHEMA = _schema(style_clause=STR, sheets=_arr(SHEET_PROMPT_SCHEMA))

# V3 (2026-07-22): ONE Seedance prompt per 15s SEGMENT (Omni dropped, canon look-blocks
# dropped — the panels + sheets carry the look). role ∈ identity | voice | style | panel.
PROMPTS_SCHEMA = _schema(
    segments=_arr(_schema(
        segment_number=INT,
        characters=_arr(STR),
        seedance_prompt=STR,
        reference_assets=_arr(REF_SCHEMA),
    )),
)

# Quality check: binary checklist + JSON verdict (skill-2q on Haiku 4.5)
QC_SCHEMA = _schema(
    passed=BOOL,
    checks=_arr(_schema(name=STR, passed=BOOL, issue=STR)),
    feedback=STR,
)



# ── LLM call helper ─────────────────────────────────────────────

def _call_gemini(system: str, user: str, schema: dict, temperature: float | None = None) -> tuple[dict, int, int]:
    from google import genai
    from google.genai import types
    import time
    api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
    primary_model = os.getenv("GEMINI_MODEL", "gemini-3.6-flash")
    # De-duplicate fallback list preserving order
    fallback_models = []
    for m in [primary_model, "gemini-3.6-flash"]:
        if m not in fallback_models:
            fallback_models.append(m)
            
    client = genai.Client(api_key=api_key)
    
    config = types.GenerateContentConfig(
        system_instruction=system,
        response_mime_type="application/json",
        temperature=temperature if temperature is not None else 0.7,
    )
    
    last_err = None
    for model_name in fallback_models:
        for attempt in range(2):
            try:
                response = client.models.generate_content(
                    model=model_name,
                    contents=user,
                    config=config,
                )
                text = response.text
                try:
                    parsed = json.loads(text, strict=False)
                except json.JSONDecodeError:
                    import re
                    sanitized = re.sub(r'[\x00-\x1f\x7f-\x9f]', lambda m: '\\n' if m.group(0) == '\n' else '', text)
                    parsed = json.loads(sanitized, strict=False)
                t_in = response.usage_metadata.prompt_token_count if response.usage_metadata else 500
                t_out = response.usage_metadata.candidates_token_count if response.usage_metadata else 500
                return parsed, t_in, t_out
            except Exception as e:
                last_err = e
                err_str = str(e)
                if any(tok in err_str for tok in ("503", "UNAVAILABLE", "429", "RESOURCE_EXHAUSTED")):
                    time.sleep(1.0)
                    continue
                raise e
    if last_err:
        raise last_err


def _call(client: Anthropic, system: str, user: str, label: str,
          schema: dict, run_id: str, stage: str,
          model: str = MODEL, max_tokens: int = 24000,
          temperature: float | None = None) -> tuple[dict, int, int]:
    """Call LLM (Google Gemini or Anthropic) with structured output."""
    google_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
    if google_key:
        try:
            parsed, t_in, t_out = _call_gemini(system, user, schema, temperature)
            print(f"[{label} (Gemini 2.5): {t_in} in / {t_out} out]")
            ledger.add_cost(run_id, t_in, t_out, model="gemini-2.5-flash")
            return parsed, t_in, t_out
        except Exception as e:
            print(f"[Gemini call error, falling back to Anthropic: {e}]")

    extra = {"temperature": temperature} if temperature is not None else {}
    with client.messages.stream(
        model=model, max_tokens=max_tokens, system=system,
        output_config={"format": {"type": "json_schema", "schema": schema}},
        messages=[{"role": "user", "content": user}],
        **extra,
    ) as stream:
        resp = stream.get_final_message()

    t_in, t_out = resp.usage.input_tokens, resp.usage.output_tokens
    print(f"[{label}: {t_in} in / {t_out} out]")

    text = next(b.text for b in resp.content if b.type == "text")
    result = json.loads(text)

    # Track cost
    ledger.add_cost(run_id, t_in, t_out, model=model)

    return result, t_in, t_out


# ── Co-creation stage (V3): stereotype + human seed → Story Brief ──────────
# Three human-gated steps (align → diverge → commit). See DESIGN_cocreation_stage.md.
# For V3 runs these replace the word-based story stages above (kept for the legacy deck flow).



# CEFR caps — from RESEARCH_shortform_pedagogy_framework.md §3.2.
# level → (max_total_duration_s, max_sentence_words, max_total_words)
CEFR_CAPS = {"A1": (30, 8, 30), "A2": (40, 12, 55), "B1": (45, 15, 80)}


# ── Co-creation safeguards (anti-slop / anti-didactic — DESIGN_cocreation_stage §4) ──


def _all_dialogue_lines(sp: dict) -> list[dict]:
    """Every dialogue line dict across a segment/shot screenplay."""
    return [d for seg in sp.get("segments", [])
            for sh in seg.get("shots", [])
            for d in sh.get("dialogue", [])]


def find_forbidden_in_dialogue(sp: dict, terms: list[str]) -> list[str]:
    """Safeguard: report any dialogue line containing a forbidden term (the stereotype
    name + synonyms, or pedagogical tokens). Case-insensitive substring. [] = clean."""
    hits = []
    for d in _all_dialogue_lines(sp):
        line = d.get("german") or ""
        low = line.lower()
        for t in terms:
            t = (t or "").strip().lower()
            if t and t in low:
                hits.append(f"forbidden '{t}' in dialogue: \"{line[:50]}\"")
    return hits


def validate_screenplay(sp: dict) -> list[str]:
    """V3 structural + pedagogical validators (stereotype-first — no deck coverage).

    Checks the segment/shot shape, the 15s Seedance-clip cap, the CEFR word/sentence
    caps, the speaker cap, and that the teaching metadata is declared. Whether the
    grammar target actually surfaces *naturally* in the dialogue is a linguistic
    judgment — that lives in skill-2q (the LLM quality check), not here.
    """
    problems = []
    segs = sp.get("segments", [])
    if not (2 <= len(segs) <= 3):
        problems.append(f"expected 2–3 segments, got {len(segs)}")

    total = sum(int(s.get("duration_s", 0) or 0) for s in segs)
    if not (28 <= total <= 47):
        problems.append(f"total duration {total}s not ~30 or ~45s")
    for s in segs:
        d = int(s.get("duration_s", 0) or 0)
        if d > 15:
            problems.append(f"segment {s.get('segment_number')}: {d}s over the 15s Seedance clip cap")
        shots = s.get("shots", [])
        if len(shots) < 1:
            problems.append(f"segment {s.get('segment_number')}: no shots")
        shot_sum = sum(int(sh.get("duration_s", 0) or 0) for sh in shots)
        if shots and abs(shot_sum - d) > 2:
            problems.append(f"segment {s.get('segment_number')}: shot durations sum {shot_sum}s ≠ segment {d}s")
        # Shot COUNT is story-driven — NO arbitrary cap. The real bound is readability: every
        # shot needs enough time on screen to read, and a shot that carries a spoken line needs
        # enough to deliver + lip-sync it (~2s). Warn only on that (the sheet storyboard puts all
        # a segment's shots in ONE image, so many shots no longer blow the Seedance ref budget).
        for sh in shots:
            dur = int(sh.get("duration_s", 0) or 0)
            has_line = bool(sh.get("dialogue"))
            floor = 2 if has_line else 1
            if dur and dur < floor:
                what = "deliver its spoken line" if has_line else "read on screen"
                problems.append(f"segment {s.get('segment_number')} shot {sh.get('shot_number')}: "
                                f"{dur}s too short to {what} (min ~{floor}s)")

    lines = [d for s in segs for sh in s.get("shots", []) for d in sh.get("dialogue", [])]
    level = (sp.get("cefr_level") or "").upper()
    caps = CEFR_CAPS.get(level)
    if not caps:
        problems.append(f"unknown cefr_level '{sp.get('cefr_level')}' (expect A1/A2/B1)")
    else:
        _, max_sent, max_words = caps
        total_words = sum(len((d.get("german") or "").split()) for d in lines)
        if total_words > max_words:
            problems.append(f"{level}: {total_words} words over the {max_words}-word cap")
        for d in lines:
            n = len((d.get("german") or "").split())
            if n > max_sent:
                problems.append(f"{level}: {n}-word line over the {max_sent}-word sentence cap — "
                                f"'{(d.get('german') or '')[:40]}…'")

    speakers = {d.get("speaker") for d in lines if d.get("speaker")}
    if len(speakers) > 3:
        problems.append(f"{len(speakers)} speakers {sorted(speakers)} — cap is 2 mains (rare 3rd)")

    for field in ("stereotype", "typology", "grammar_target"):
        if not (sp.get(field) or "").strip():
            problems.append(f"{field} missing (V3 teaching metadata)")
    return problems


def stage_screenplay(run_id: str, rcp: RunContextPack, words: list[dict],
                     story: dict, ep_dir: Path, client: Anthropic,
                     qc_feedback: str = "") -> tuple[dict, list[str]]:
    """Generate screenplay with validate → one retry.

    qc_feedback: when set (the ONE post-QC rewrite), the writer gets the
    quality-check verdict and must address it — dialogue naturalness first.
    """
    skill = _load_skill("skill-2-screenplay-writer.md")
    # V3: stereotype-first — the screenplay is driven by the story/scenario, not a
    # fixed deck-word set. `words` stays in the signature for CLI compatibility but
    # no longer constrains the screenplay (see BUILD_PLAN_v3.md Phase 3).
    skill = (
        skill.replace("{{CHARACTER_BIBLE}}", rcp.character_bible)
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

    problems = validate_screenplay(sp)
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
        problems = validate_screenplay(sp)

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
    # 1. Code validators (segment/shot shape, 15s clip cap, CEFR word caps — V3)
    code_problems = validate_screenplay(sp)

    # 2. LLM checklist — skill-2q judged by Haiku 4.5 (cheap, strict)
    skill = _load_skill("skill-2q-quality-check.md")
    skill = (
        skill.replace("{{CHARACTER_BIBLE}}", rcp.character_bible)
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


# ── Stage 6.5: Storyboard (screenplay → per-shot image prompts → panels) ──

def stage_storyboard(run_id: str, rcp: RunContextPack, sp: dict, ep_dir: Path,
                     client: Anthropic, image_provider: str = "mock") -> tuple[dict, list]:
    """V3 storyboard v2 (2026-07-24): screenplay → ONE multi-panel SHEET prompt per SEGMENT
    (skill-2b v2.0) → one image generation per segment → sliced into per-shot 9:16 panels.
    The single generation locks character + style across the segment's shots (fixes the v1
    per-shot drift); cross-segment continuity via a chaining ref (each segment's sheet is
    attached when generating the next). Panels keep the SAME panel_s<seg>_<shot>.png contract
    the Seedance step resolves (DESIGN_v3_data_flow.md §3–4)."""
    skill = _load_skill("skill-2b-storyboard.md")
    skill = (skill.replace("{{CHARACTER_BIBLE}}", rcp.character_bible)
             .replace("{{CANON_BLOCKS}}", rcp.canon_blocks)
             .replace("{{SCREENPLAY_JSON}}", json.dumps(sp, ensure_ascii=False)))
    system = rcp.for_prompt_stage() + "\n\n" + skill
    board, t_in, t_out = _call(
        client, system, "Produce the per-segment storyboard SHEET prompts JSON now.",
        "skill-2b storyboard", STORYBOARD_SCHEMA, run_id, "storyboard", max_tokens=32000)

    ep_dir.mkdir(parents=True, exist_ok=True)
    bp = ep_dir / "storyboard.json"
    bp.write_text(json.dumps(board, ensure_ascii=False, indent=2), encoding="utf-8")

    from .providers import get_image_provider
    from .providers import image as _img
    provider = get_image_provider(image_provider)
    panels_dir = ep_dir / "storyboard"
    panels_dir.mkdir(parents=True, exist_ok=True)

    seg_by_n = {seg.get("segment_number"): seg for seg in sp.get("segments", [])}
    sheets = sorted(board.get("sheets", []), key=lambda s: s.get("segment_number") or 0)
    all_panels, sheet_files, prev_sheet = [], [], None
    for sheet in sheets:
        seg_n = sheet.get("segment_number")
        seg = seg_by_n.get(seg_n, {})
        shot_numbers = sheet.get("shot_numbers") or [sh.get("shot_number") for sh in seg.get("shots", [])]
        rows, cols, _, _ = _img.sheet_grid(len(shot_numbers))

        # Presence-based identity refs — every roster character present ANYWHERE in the
        # segment (blocking/gaze/action + dialogue), NOT dialogue-speakers only (v1 bug).
        refs = []
        for name in _segment_characters(seg):
            for e in _character_ref_paths(name):
                refs.append({"binds": name, "role": "character", **e})
        # Cross-segment chaining: attach the previous segment's sheet for continuity.
        if prev_sheet is not None and sheet.get("continuity_ref"):
            refs.append({"binds": sheet["continuity_ref"], "role": "continuity",
                         "variant": "sheet", "path": str(prev_sheet.resolve())})

        sheet_path = panels_dir / f"sheet_s{int(seg_n):02d}.png"
        try:
            provider.generate_sheet(sheet, sheet.get("sheet_prompt", ""), refs, sheet_path)
            panels = _img.slice_sheet(sheet_path, rows, cols, shot_numbers, panels_dir, seg_n)
            all_panels.extend(panels)
            sheet_files.append(sheet_path)
            prev_sheet = sheet_path
            print(f"  ✓ sheet seg {seg_n} ({rows}x{cols}) → {sheet_path.name} → {len(panels)} panels")
        except Exception as e:
            print(f"  ✗ sheet seg {seg_n}: {e}")
            ledger.log_event(run_id, "storyboard", "failed",
                             detail={"segment": seg_n, "error": str(e)})
            raise

    ledger.log_event(run_id, "storyboard", "completed",
                     artifact_path=str(bp.relative_to(REPO)), artifact_sha256=ledger.sha256_file(bp),
                     tokens_in=t_in, tokens_out=t_out,
                     detail={"sheets": len(sheet_files), "panels": len(all_panels),
                             "provider": provider.name})
    ledger.update_run(run_id, stage="storyboard")
    print(f"✅ {len(sheet_files)} sheets → {len(all_panels)} panels → "
          f"{panels_dir.relative_to(REPO)}/  (provider: {provider.name})")
    return board, all_panels


# ── Stage 7: Prompt writer + canon substitution + refs manifest ──────

def _norm(s: str) -> str:
    """Fold umlauts/ß so canonical names match resources/ folder names."""
    return (s.lower().replace("ü", "u").replace("ö", "o")
            .replace("ä", "a").replace("ß", "ss").strip())


def _character_ref_paths(name: str) -> list[dict]:
    """Resolve a canonical character name → its identity images, SHEET FIRST.

    Multi-angle character sheet = primary (structural map: keeps backs/sides/turns
    consistent); main/master portrait = secondary (high-res close-up anchor).
    """
    if not RESOURCES.exists():
        return []
    target = _norm(name)
    for d in sorted(RESOURCES.iterdir()):
        if not (d.is_dir() and _norm(d.name) == target):
            continue
        pngs = sorted(d.glob("*.png"))

        def pick(prefs):
            for pref in prefs:
                for p in pngs:
                    if pref in p.name.lower():
                        return str(p.resolve())
            return None

        out = []
        sheet = pick(("sheet", "profiles"))
        portrait = pick(("main", "master"))
        if sheet:
            out.append({"variant": "sheet", "path": sheet})
        if portrait and portrait != sheet:
            out.append({"variant": "portrait", "path": portrait})
        if not out and pngs:
            out.append({"variant": "portrait", "path": str(pngs[0].resolve())})
        return out
    return []


CANON_ROSTER = ["Rolf die Wurst", "Bert das Bier", "Kati die Kartoffel", "Müller das Brot"]


def _segment_characters(seg: dict) -> list[str]:
    """Canonical roster characters PRESENT anywhere in the segment — matched from blocking,
    gaze, action AND dialogue, not dialogue speakers alone. A character can appear silently
    (reaction/listener shots); the v1 storyboard resolved refs from `dialogue[].speaker` only,
    so silent-but-present characters got NO identity reference → drift. This fixes that."""
    parts, speakers = [], []
    for sh in seg.get("shots", []):
        for f in ("blocking", "gaze", "action", "expression"):
            parts.append(sh.get(f) or "")
        for d in sh.get("dialogue", []):
            if d.get("speaker"):
                speakers.append(d["speaker"])
    blob = _norm(" ".join(parts + speakers))
    present = []
    for full in CANON_ROSTER:
        first = _norm(full.split()[0])
        if first and first in blob and full not in present:
            present.append(full)
    return present


def _character_voice_path(name: str) -> str | None:
    """Resolve a canonical character name → its voice-identity audio clip (.mp3)."""
    if not RESOURCES.exists():
        return None
    target = _norm(name)
    for d in sorted(RESOURCES.iterdir()):
        if d.is_dir() and _norm(d.name) == target:
            mp3s = sorted(d.glob("*.mp3"))
            return str(mp3s[0].resolve()) if mp3s else None
    return None


def _resolve_binds(binds: str, role: str) -> list[dict]:
    """Resolve a ref 'binds' target → list of {[variant,] path, status} entries.
    Character identities resolve to sheet+portrait images; `voice` to the character's
    voice-identity clip; style is pending until C1; audio-master pending until C3."""
    if binds == "style" or role == "style":
        return [{"path": None, "status": "pending — C1 style-lock"}]
    if role == "voice":
        vp = _character_voice_path(binds)
        if vp:
            return [{"variant": "voice", "path": vp, "status": "resolved"}]
        return [{"path": None, "status": f"unresolved — no voice clip for '{binds}'"}]
    if binds in ("audio-master", "audio") or role == "audio":
        return [{"path": None, "status": "pending — per-run merged audio (C3)"}]
    entries = _character_ref_paths(binds)
    if entries:
        return [{**e, "status": "resolved"} for e in entries]
    return [{"path": None, "status": f"unresolved — no asset for '{binds}'"}]


def build_refs_manifest(prompts: dict, run_id: str, ep_dir: Path) -> dict:
    """segment → the reference assets it needs, each resolved to a file path (or pending),
    deduped by (binds, role). identity → sheet+portrait · voice → mp3 · style → pending ·
    panel → the storyboard panel file for that shot key (s<seg>_<shot>)."""
    segments = {}
    for seg in prompts.get("segments", []):
        refs, seen = [], set()
        for r in seg.get("reference_assets", []):
            binds, role = r.get("binds", ""), r.get("role", "")
            if (binds, role) in seen:
                continue
            seen.add((binds, role))
            if role == "panel":
                panel = ep_dir / "storyboard" / f"panel_{binds}.png"
                ok = panel.exists()
                refs.append({"binds": binds, "role": role, "variant": "panel",
                             "path": str(panel.resolve()) if ok else None,
                             "status": "resolved" if ok else f"pending — panel {binds} not generated yet"})
            else:
                for entry in _resolve_binds(binds, role):
                    refs.append({"binds": binds, "role": role, **entry})
        segments[str(seg.get("segment_number"))] = refs
    return {"run_id": run_id, "episode": ep_dir.name, "segments": segments}


def stage_prompts(run_id: str, rcp: RunContextPack, sp: dict,
                  ep_dir: Path, client: Anthropic) -> dict:
    """V3: screenplay + storyboard panels → ONE thin multi-shot Seedance prompt per 15s segment
    (skill-3 v4). Binds panels + character sheets + voices + style; no Omni, no canon look-blocks."""
    skill = _load_skill("skill-3-prompt-writer.md")
    skill = skill.replace("{{SCREENPLAY_JSON}}", json.dumps(sp, ensure_ascii=False))
    system = rcp.for_prompt_stage() + "\n\n" + skill

    prompts, t_in, t_out = _call(
        client, system, "Produce the per-segment Seedance prompt packages JSON now.",
        "skill-3 prompts", PROMPTS_SCHEMA, run_id, "prompts", max_tokens=32000,
    )

    # Seedance 3000-char cap check (per segment — easy now, no canon blocks)
    over_cap = [(seg.get("segment_number"), len(seg.get("seedance_prompt", "")))
                for seg in prompts.get("segments", [])
                if len(seg.get("seedance_prompt", "")) > 3000]
    if over_cap:
        print(f"⚠ Seedance 3000-char cap EXCEEDED in {len(over_cap)} segment(s): "
              + ", ".join(f"segment {n} ({l} chars)" for n, l in over_cap))

    prompts_path = ep_dir / "prompts.json"
    prompts_path.write_text(json.dumps(prompts, ensure_ascii=False, indent=2), encoding="utf-8")

    # Per-segment split: segment_NN.seedance.json + refs_manifest.json
    prompts_dir = ep_dir / "prompts"
    prompts_dir.mkdir(parents=True, exist_ok=True)
    for seg in prompts.get("segments", []):
        n = seg.get("segment_number")
        (prompts_dir / f"segment_{int(n):02d}.seedance.json").write_text(
            json.dumps(seg, ensure_ascii=False, indent=2), encoding="utf-8")
    manifest = build_refs_manifest(prompts, run_id, ep_dir)
    manifest_path = prompts_dir / "refs_manifest.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

    sha = ledger.sha256_file(prompts_path)
    n_seg = len(prompts.get("segments", []))
    ledger.log_event(run_id, "prompts", "completed",
                     artifact_path=str(prompts_path.relative_to(REPO)),
                     artifact_sha256=sha, tokens_in=t_in, tokens_out=t_out,
                     detail={"segments": n_seg,
                             "refs_manifest": str(manifest_path.relative_to(REPO)),
                             "seedance_over_cap": over_cap})
    ledger.update_run(run_id, stage="prompts")

    print(f"→ {n_seg} segment Seedance prompts + refs_manifest → {prompts_dir.relative_to(REPO)}/")
    return prompts


# ── Removed 2026-08-02 (Phase 1 quarantine) ──────────────────────────
# V2 word-deck: fetch_words/fetch_words_by_positions/stage_words/
# stage_story_options/stage_story_expand/stage_caption + their schemas.
# Superseded co-creation: stage_align/stage_diverge/stage_commit/validate_brief
# (skill-1-story-strategist owns this now).
# Broken since the V3 reshape (all read screenplay['scenes'], a shape that no
# longer exists): substitute_canon · stage_finalize · stage_generate.
# Recover with: git show v3-wizard-archive:pipeline/stages.py

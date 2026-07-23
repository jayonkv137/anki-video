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
    lighting_mood=STR,    # lighting + mood
    dialogue=_arr(DIALOGUE_LINE),
)

SEGMENT_SCHEMA = _schema(
    segment_number=INT,
    duration_s=INT,       # ~15 — a single Seedance clip
    setting=STR,
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
    target_vocab=_arr(_schema(german=STR, english=STR, gender=STR)),  # emergent; gender ∈ der/die/das/— for color-coding
    segments=_arr(SEGMENT_SCHEMA),
)

# ── Co-creation stage (V3) schemas — stereotype + human seed → Story Brief ──
# (see docs/planning/DESIGN_cocreation_stage.md). The Brief is the handoff into skill-2.
CAST_SCHEMA = _schema(main=STR, side=STR, guest=STR, background=STR)  # "" = unused role
LESSON_SCHEMA = _schema(particle=STR, structure=STR, pragmatic_function=STR, pop_up_grammar=STR)
TARGET_LINE_SCHEMA = _schema(speaker=STR, german=STR, english=STR, why=STR)

# skill-1a-align → options for the human (Ask-Don't-Guess); lesson_options carry BOTH particle + structure
LOCATION_OPTION = _schema(setting_type=STR, environment=STR, time_of_day=STR, why=STR)
LESSON_OPTION = _schema(kind=STR, lesson=STR, pragmatic_function=STR, pop_up_grammar=STR, why=STR)  # kind: particle|structure
ALIGN_SCHEMA = _schema(
    stereotype_id=STR, stereotype_name=STR, cefr_level=STR, cast=CAST_SCHEMA,
    location_options=_arr(LOCATION_OPTION),
    lesson_options=_arr(LESSON_OPTION),
    comedic_angle_suggestion=STR,
)

# skill-1b-diverge → 3–5 distinct comedic angles (Refine-via-Examples)
ANGLE_SCHEMA = _schema(label=STR, operator=STR, premise=STR, game=STR,
                       lesson_integration=STR, button=STR)
DIVERGE_SCHEMA = _schema(options=_arr(ANGLE_SCHEMA))

# skill-1c-commit → critique + the locked Story Brief (the handoff into skill-2)
STORY_BRIEF_SCHEMA = _schema(
    title_de=STR,
    stereotype_id=STR, stereotype_name=STR, category=STR, cefr_level=STR,
    seed=STR,                     # the human's braindump (anti-slop anchor)
    cast=CAST_SCHEMA,
    location=STR,
    comedic_angle=STR,            # chosen typology / sub-genre
    lesson=LESSON_SCHEMA,         # particle and/or structure (both offered, chosen)
    premise=STR,
    game_of_scene=STR,            # implicit stereotype "game" — never named in dialogue
    escalation_beats=_arr(STR),   # base reality → first unusual → framing → escalation
    button=STR,
    target_line=TARGET_LINE_SCHEMA,
    oblique_constraint=STR,       # the lateral curveball ("" if none)
    banned_terms=_arr(STR),       # stereotype name+synonyms + pedagogical tokens kept OUT of dialogue
)
BRIEF_COMMIT_SCHEMA = _schema(
    critique=_arr(_schema(check=STR, passed=BOOL, note=STR)),
    brief=STORY_BRIEF_SCHEMA,
)

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

# Caption: Instagram post copy (skill-4)
CAPTION_SCHEMA = _schema(caption=STR, hashtags=_arr(STR))


# ── LLM call helper ─────────────────────────────────────────────

def _call_gemini(system: str, user: str, schema: dict, temperature: float | None = None) -> tuple[dict, int, int]:
    from google import genai
    from google.genai import types
    api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
    model_name = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
    client = genai.Client(api_key=api_key)
    
    config = types.GenerateContentConfig(
        system_instruction=system,
        response_mime_type="application/json",
        temperature=temperature if temperature is not None else 0.7,
    )
    
    response = client.models.generate_content(
        model=model_name,
        contents=user,
        config=config,
    )
    
    # Clean control characters if present and use strict=False to allow unescaped newlines in JSON strings
    text = response.text
    try:
        parsed = json.loads(text, strict=False)
    except json.JSONDecodeError:
        # Fallback sanitize raw control characters inside strings
        import re
        sanitized = re.sub(r'[\x00-\x1f\x7f-\x9f]', lambda m: '\\n' if m.group(0) == '\n' else '', text)
        parsed = json.loads(sanitized, strict=False)
    t_in = response.usage_metadata.prompt_token_count if response.usage_metadata else 500
    t_out = response.usage_metadata.candidates_token_count if response.usage_metadata else 500
    return parsed, t_in, t_out


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

def stage_words(run_id: str, start: int | None, randomize: bool,
                positions: list[int] | None = None) -> list[dict]:
    """Fetch words and record in ledger. `positions` pins an exact word set
    (golden-batch / regression runs)."""
    words = fetch_words_by_positions(positions) if positions else fetch_words(start, randomize)
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


# ── Co-creation stage (V3): stereotype + human seed → Story Brief ──────────
# Three human-gated steps (align → diverge → commit). See DESIGN_cocreation_stage.md.
# For V3 runs these replace the word-based story stages above (kept for the legacy deck flow).

OBLIQUE_STRATEGIES = [
    "The supporting character controls the space through silence.",
    "The conflict centers on an object smaller than a coin.",
    "One character never once breaks their routine, whatever happens.",
    "The escalation happens entirely through a single repeated gesture.",
    "The main character treats a mundane chore as a high-stakes emergency.",
    "The room's temperature or air is the real antagonist.",
    "Nobody ever raises their voice; the tension is all in restraint.",
]


def stage_align(run_id: str, rcp: RunContextPack, stereotype: dict, seed: str,
                cast: dict, cefr_level: str, ep_dir: Path, client: Anthropic) -> dict:
    """Co-creation step 1 (skill-1a): stereotype + seed + cast → location & lesson options."""
    skill = _load_skill("skill-1a-align.md")
    skill = (skill.replace("{{CHARACTER_BIBLE}}", rcp.character_bible)
             .replace("{{STEREOTYPE_JSON}}", json.dumps(stereotype, ensure_ascii=False))
             .replace("{{SEED}}", seed or "(none — invent something grounded and relatable)")
             .replace("{{CAST_JSON}}", json.dumps(cast, ensure_ascii=False))
             .replace("{{CEFR_LEVEL}}", cefr_level))
    system = rcp.for_story_stage() + "\n\n" + skill
    aligned, t_in, t_out = _call(
        client, system,
        "Produce the alignment JSON (location options + BOTH-kind lesson options) now.",
        "skill-1a align", ALIGN_SCHEMA, run_id, "align")
    ep_dir.mkdir(parents=True, exist_ok=True)
    p = ep_dir / "align.json"
    p.write_text(json.dumps(aligned, ensure_ascii=False, indent=2), encoding="utf-8")
    ledger.log_event(run_id, "align", "completed", artifact_path=str(p.relative_to(REPO)),
                     artifact_sha256=ledger.sha256_file(p), tokens_in=t_in, tokens_out=t_out)
    ledger.update_run(run_id, stage="align")
    return aligned


def stage_diverge(run_id: str, rcp: RunContextPack, aligned_chosen: dict,
                  oblique: str | None, ep_dir: Path, client: Anthropic) -> dict:
    """Co-creation step 2 (skill-1b, HOT temp): chosen params → 3–5 comedic angles."""
    oblique = oblique or random.choice(OBLIQUE_STRATEGIES)
    skill = _load_skill("skill-1b-diverge.md")
    skill = (skill.replace("{{CHARACTER_BIBLE}}", rcp.character_bible)
             .replace("{{ALIGNED_JSON}}", json.dumps(aligned_chosen, ensure_ascii=False))
             .replace("{{OBLIQUE_CONSTRAINT}}", oblique))
    system = rcp.for_story_stage() + "\n\n" + skill
    diverge, t_in, t_out = _call(
        client, system, "Produce 3–5 distinct comedic angle options as JSON now.",
        "skill-1b diverge", DIVERGE_SCHEMA, run_id, "diverge", temperature=1.0)
    p = ep_dir / "diverge.json"
    p.write_text(json.dumps({"oblique_constraint": oblique, **diverge}, ensure_ascii=False, indent=2),
                 encoding="utf-8")
    ledger.log_event(run_id, "diverge", "completed", artifact_path=str(p.relative_to(REPO)),
                     artifact_sha256=ledger.sha256_file(p), tokens_in=t_in, tokens_out=t_out)
    ledger.update_run(run_id, stage="diverge")
    return diverge


def stage_commit(run_id: str, rcp: RunContextPack, aligned_chosen: dict, chosen_angle: dict,
                 seed: str, ep_dir: Path, client: Anthropic) -> tuple[dict, list[str]]:
    """Co-creation step 3 (skill-1c, COLD temp): chosen angle → critique → locked Story Brief."""
    skill = _load_skill("skill-1c-commit.md")
    skill = (skill.replace("{{CHARACTER_BIBLE}}", rcp.character_bible)
             .replace("{{ALIGNED_JSON}}", json.dumps(aligned_chosen, ensure_ascii=False))
             .replace("{{CHOSEN_ANGLE_JSON}}", json.dumps(chosen_angle, ensure_ascii=False))
             .replace("{{SEED}}", seed or "(none)"))
    system = rcp.for_story_stage() + "\n\n" + skill
    out, t_in, t_out = _call(
        client, system, "Run the critique and output the committed brief JSON now.",
        "skill-1c commit", BRIEF_COMMIT_SCHEMA, run_id, "commit", temperature=0.2)
    brief = out.get("brief", {})
    problems = validate_brief(brief)
    p = ep_dir / "brief.json"
    p.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    ledger.log_event(run_id, "commit", "completed", artifact_path=str(p.relative_to(REPO)),
                     artifact_sha256=ledger.sha256_file(p), tokens_in=t_in, tokens_out=t_out,
                     detail={"brief_problems": problems})
    ledger.update_run(run_id, stage="commit")
    # Mark the stereotype covered so it drops out of future daily picks.
    sid = brief.get("stereotype_id")
    if sid:
        from . import stereotypes as stlib
        try:
            stlib.mark_covered(sid, ep_dir.name)
        except Exception as e:
            print(f"  (note: could not mark stereotype {sid} covered: {e})")
    return brief, problems


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


# CEFR caps — from RESEARCH_shortform_pedagogy_framework.md §3.2.
# level → (max_total_duration_s, max_sentence_words, max_total_words)
CEFR_CAPS = {"A1": (30, 8, 30), "A2": (40, 12, 55), "B1": (45, 15, 80)}


# ── Co-creation safeguards (anti-slop / anti-didactic — DESIGN_cocreation_stage §4) ──
DEFAULT_BANNED_TOKENS = ["lernen", "bedeutet", "grammatik", "vokabel", "lektion"]


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


def validate_brief(brief: dict) -> list[str]:
    """Structural + safeguard checks on a Story Brief (skill-1c commit output)."""
    problems = []
    if not (brief.get("cast", {}).get("main") or "").strip():
        problems.append("cast.main is required (≥1 main character)")
    lesson = brief.get("lesson", {})
    if not ((lesson.get("particle") or "").strip() or (lesson.get("structure") or "").strip()):
        problems.append("lesson needs a particle OR a structure (both-offered → one chosen)")
    if len(brief.get("escalation_beats", [])) < 2:
        problems.append("escalation_beats: need ≥2 (base reality → … → escalation)")
    for f in ("stereotype_name", "cefr_level", "premise", "button"):
        if not (brief.get(f) or "").strip():
            problems.append(f"{f} missing")
    name = (brief.get("stereotype_name") or "").strip().lower()
    banned = [b.lower() for b in brief.get("banned_terms", [])]
    if name and not any(name in b or b in name for b in banned):
        problems.append("banned_terms should include the stereotype name (kept out of dialogue)")
    return problems


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
        if not (1 <= len(shots) <= 5):
            problems.append(f"segment {s.get('segment_number')}: {len(shots)} shots (expect 1–5 per 15s)")
        shot_sum = sum(int(sh.get("duration_s", 0) or 0) for sh in shots)
        if shots and abs(shot_sum - d) > 2:
            problems.append(f"segment {s.get('segment_number')}: shot durations sum {shot_sum}s ≠ segment {d}s")

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


# ── Stage 8.5: Video generation (per-scene clips) ────────────────

def stage_generate(run_id: str, sp: dict, ep_dir: Path, provider_name: str = "mock") -> list[Path]:
    """Generate one clip per scene via the chosen video provider (mock | fal | …).
    Reads prompts/scene_NN.seedance.json + refs_manifest; writes clips/scene_NN.mp4."""
    from .providers import get_video_provider
    provider = get_video_provider(provider_name)
    pdir, clips = ep_dir / "prompts", ep_dir / "clips"
    clips.mkdir(parents=True, exist_ok=True)
    manifest = {}
    mp = pdir / "refs_manifest.json"
    if mp.exists():
        manifest = json.loads(mp.read_text(encoding="utf-8")).get("scenes", {})

    print(f"→ generating {len(sp.get('scenes', []))} clips via provider '{provider.name}'…")
    out = []
    for sc in sp.get("scenes", []):
        n = sc.get("scene_number")
        seedance = {}
        sf = pdir / f"scene_{n:02d}.seedance.json"
        if sf.exists():
            seedance = json.loads(sf.read_text(encoding="utf-8"))
        refs = manifest.get(str(n), [])
        dest = clips / f"scene_{n:02d}.mp4"
        try:
            provider.generate(sc, seedance, refs, dest)
            out.append(dest)
            print(f"  ✓ scene {n} → {dest.name}")
            ledger.log_event(run_id, "generate", "completed",
                             artifact_path=str(dest.relative_to(REPO)),
                             detail={"scene": n, "provider": provider.name})
        except Exception as e:
            print(f"  ✗ scene {n}: {e}")
            ledger.log_event(run_id, "generate", "failed",
                             detail={"scene": n, "provider": provider.name, "error": str(e)})
            raise
    ledger.update_run(run_id, stage="generate")
    print(f"✅ {len(out)} clips in {clips.relative_to(REPO)}/  (provider: {provider.name})")
    return out


# ── Stage 9: Caption (Instagram post copy) ───────────────────────

def _norm_hashtags(tags: list[str]) -> list[str]:
    out, seen = [], set()
    for t in tags:
        t = "#" + t.lstrip("#").strip().replace(" ", "")
        if t != "#" and t.lower() not in seen:
            seen.add(t.lower())
            out.append(t)
    return out


def stage_caption(run_id: str, rcp: RunContextPack, story: dict,
                  words: list[dict], ep_dir: Path, client: Anthropic) -> dict:
    """Generate the Instagram caption + hashtags (skill-4). Writes caption.json +
    caption.md; the post-ready copy for M6."""
    skill = _load_skill("skill-4-caption.md")
    skill = (skill.replace("{{STORY_JSON}}", json.dumps(story, ensure_ascii=False))
             .replace("{{WORDS_JSON}}", json.dumps(words, ensure_ascii=False)))
    system = f"# PROJECT MISSION\n{rcp.mission}\n\n" + skill

    cap, t_in, t_out = _call(
        client, system, "Write the Instagram caption JSON now.",
        "skill-4 caption", CAPTION_SCHEMA, run_id, "caption", max_tokens=2000,
    )
    cap["hashtags"] = _norm_hashtags(cap.get("hashtags", []))

    ep_dir.mkdir(parents=True, exist_ok=True)
    (ep_dir / "caption.json").write_text(json.dumps(cap, ensure_ascii=False, indent=2), encoding="utf-8")
    post = cap.get("caption", "").rstrip() + "\n\n" + " ".join(cap.get("hashtags", []))
    (ep_dir / "caption.md").write_text(post, encoding="utf-8")

    sha = ledger.sha256_file(ep_dir / "caption.json")
    ledger.log_event(run_id, "caption", "completed",
                     artifact_path=str((ep_dir / "caption.md").relative_to(REPO)),
                     artifact_sha256=sha, tokens_in=t_in, tokens_out=t_out)

    print(f"\n✅ caption → {ep_dir.relative_to(REPO)}/caption.md ({len(cap.get('hashtags', []))} hashtags)")
    return cap

"""Schemas v4 — the lesson-first artifact contracts (brief · screenplay) + validators.

Replaces the V3 stereotype-first shapes (stages.STORY_BRIEF_SCHEMA / SCREENPLAY_SCHEMA),
which remain in stages.py only for the legacy wizard until Phase 3.5.

What changed vs V3 (BUILD_PLAN_v4 §5 + the contradiction audit):
- lesson-first: `module_id` / `block_no` / `atom_ids[]` replace stereotype/typology;
  the stereotype becomes an optional `encounter` (HOST/TEXTURE, never forced).
- `format: lesson | synthese | season_zero` (C10 — Synthese teaches zero NEW atoms;
  Season 0 is language-load ≈ 0 by design; the audit applies the right ruleset).
- the director layer gains `light_source` + `light_ratio` (TREATMENT §5 — named
  source and ratio, never moods; replaces `lighting_mood`), `negative_prompt`,
  `revision_prompt`, and first-class `props[]` with sound behaviour (TREATMENT §13/§15).
- `global_aesthetic_rules` is GONE — TREATMENT is the execution truth; compilers
  assemble style mechanically, the screenplay never carries it.

Validators split HARD (blocks) from SOFT (flags) exactly as PEDAGOGY §8–§9 does.
Word/sentence ceilings = PEDAGOGY §2, the single source (C1).
"""

import re

# ── schema helpers (same idiom as stages.py) ─────────────────────

def _schema(**props):
    return {"type": "object", "properties": props, "required": list(props),
            "additionalProperties": False}


def _arr(item):
    return {"type": "array", "items": item}


STR = {"type": "string"}
INT = {"type": "integer"}
BOOL = {"type": "boolean"}

# ── PEDAGOGY §2 — the level ceilings (HARD) ──────────────────────

LEVEL_CEILINGS = {  # level → (max total words, max words per sentence, max new words)
    "A1": (30, 8, 5),
    "A2": (55, 12, 6),
    "B1": (80, 15, 8),
}

EPISODE_FORMATS = ("lesson", "synthese", "season_zero")
LIGHT_RATIO_RE = re.compile(r"^\d{1,2}:\d{1,2}$")
DEFAULT_BANNED_TOKENS = ["lernen", "bedeutet", "grammatik", "vokabel", "lektion"]

# ── BRIEF v4 ─────────────────────────────────────────────────────

TARGET_LINE = _schema(speaker=STR, german=STR, english=STR, why=STR)
VOCAB_ITEM = _schema(german=STR, english=STR, gender=STR)  # gender ∈ der|die|das|—
ENCOUNTER = _schema(stereotype_id=STR, name=STR, mode=STR)  # mode ∈ host|texture|none

BRIEF_V4 = _schema(
    title_de=STR,
    format=STR,                # lesson | synthese | season_zero
    module_id=STR,             # e.g. "A1.4"
    block_no=INT,              # position in the module's block plan
    atom_ids=_arr(STR),        # NEW atoms this block teaches ([] for synthese/season_zero)
    recycled_atom_ids=_arr(STR),  # previously-taught atoms deliberately recycled
    cefr_level=STR,
    lead=STR,                  # canonical name (rotation-checked upstream)
    cast=_arr(STR),            # everyone present, canonical names, lead included
    location=STR,
    premise=STR,
    beats=_arr(STR),           # escalation beats, in order
    button=STR,                # the turn it ends on (never a resolution)
    target_structure=STR,      # the pattern being taught, human-readable
    target_line=TARGET_LINE,
    encounter=ENCOUNTER,       # mode "none" + empty ids when no stereotype fits
    new_vocab=_arr(VOCAB_ITEM),
    banned_terms=_arr(STR),
    director_notes=_arr(STR),
)

# ── SCREENPLAY v4 — the LOCK ─────────────────────────────────────

DIALOGUE_LINE = _schema(speaker=STR, german=STR, english=STR)
PROP = _schema(name=STR, material=STR, sound_behaviour=STR)  # TREATMENT §13

SHOT_V4 = _schema(
    shot_number=INT,
    duration_s=INT,        # shots sum to the segment's ~15s
    shot_size=STR,         # ECU|CU|MCU|MS|MWS|WS|OTS (TREATMENT §4 vocabulary)
    camera_angle=STR,      # eye-level|low|high|dutch|POV
    camera_move=STR,       # explicit always (TREATMENT §2)
    action=STR,            # ONE atomic visible action (TREATMENT §8)
    blocking=STR,          # spatial coordinates in the 9:16 frame (TREATMENT §7)
    gaze=STR,
    expression=STR,
    light_source=STR,      # NAMED source (TREATMENT §5) — never a mood word
    light_ratio=STR,       # "70:30" light-to-shadow
    props=_arr(PROP),      # [] when none; material determines sound (TREATMENT §13)
    negative_prompt=STR,   # per-shot additions beyond the permanent list ("" = none)
    revision_prompt=STR,   # the pre-planned correction (TREATMENT §15)
    dialogue=_arr(DIALOGUE_LINE),
)

SEGMENT_V4 = _schema(
    segment_number=INT,
    duration_s=INT,        # ~15 — one Seedance clip
    time_and_weather=STR,
    shots=_arr(SHOT_V4),
)

SCREENPLAY_V4 = _schema(
    title_de=STR,
    format=STR,
    module_id=STR,
    block_no=INT,
    atom_ids=_arr(STR),
    recycled_atom_ids=_arr(STR),
    cefr_level=STR,
    target_structure=STR,
    total_duration_s=INT,  # 30 default; 45 = rare explicit exception
    environment=STR,       # ONE legible environment (STORY_SYSTEM §10.3)
    target_vocab=_arr(VOCAB_ITEM),
    segments=_arr(SEGMENT_V4),
)

# ── shared helpers ───────────────────────────────────────────────

def all_dialogue(sp: dict) -> list[dict]:
    return [d for seg in sp.get("segments", [])
            for sh in seg.get("shots", [])
            for d in sh.get("dialogue", [])]


def forbidden_in_dialogue(sp: dict, terms: list[str]) -> list[str]:
    """Case-insensitive substring scan of every German line. [] = clean."""
    hits = []
    for d in all_dialogue(sp):
        line, low = d.get("german") or "", (d.get("german") or "").lower()
        for t in terms:
            t = (t or "").strip().lower()
            if t and t in low:
                hits.append(f"forbidden '{t}' in dialogue: \"{line[:50]}\"")
    return hits


def _atom_index(curriculum: dict) -> dict:
    return {a["id"]: {**a, "level": m["level"]}
            for m in curriculum["modules"] for a in m["atoms"]}


_LEVEL_ORDER = {"A1": 0, "A2": 1, "B1": 2}


# ── validators — return {"blocks": [...], "flags": [...]} ────────

def validate_brief_v4(brief: dict, curriculum: dict) -> dict:
    blocks, flags = [], []
    fmt = brief.get("format")
    if fmt not in EPISODE_FORMATS:
        blocks.append(f"format '{fmt}' not in {EPISODE_FORMATS}")
    level = (brief.get("cefr_level") or "").upper()
    if level not in LEVEL_CEILINGS:
        blocks.append(f"cefr_level '{brief.get('cefr_level')}' not A1/A2/B1")

    idx = _atom_index(curriculum)
    mod_ids = {m["id"] for m in curriculum["modules"]}
    mid = brief.get("module_id")
    if fmt != "season_zero" and mid not in mod_ids:
        blocks.append(f"module_id '{mid}' not in the curriculum")
    for aid in brief.get("atom_ids", []):
        if aid not in idx:
            blocks.append(f"atom '{aid}' not in the curriculum")
        elif mid and not aid.startswith(str(mid) + "."):
            blocks.append(f"atom '{aid}' does not belong to module {mid}")
        elif level in _LEVEL_ORDER and _LEVEL_ORDER.get(idx[aid]["level"], 9) > _LEVEL_ORDER[level]:
            blocks.append(f"atom '{aid}' is above the declared level {level}")
    for aid in brief.get("recycled_atom_ids", []):
        if aid not in idx:
            blocks.append(f"recycled atom '{aid}' not in the curriculum")

    if fmt == "lesson" and not brief.get("atom_ids"):
        blocks.append("format 'lesson' requires atom_ids (the block exists to teach)")
    if fmt == "synthese":
        if brief.get("atom_ids"):
            blocks.append("synthese teaches zero NEW atoms — atom_ids must be empty")
        if not brief.get("recycled_atom_ids"):
            blocks.append("synthese must name the recycled_atom_ids it spirals")
    if len(brief.get("atom_ids", [])) > 3:
        blocks.append("a block bundles at most 3 tightly-related atoms (the packing law)")

    lead, cast = brief.get("lead"), brief.get("cast", [])
    if lead and cast and lead not in cast:
        blocks.append(f"lead '{lead}' missing from cast {cast}")
    if len(brief.get("beats", [])) < 2 and fmt != "season_zero":
        blocks.append("beats: need ≥2 (base reality → … → escalation)")

    enc = brief.get("encounter", {})
    if enc.get("mode") not in ("host", "texture", "none"):
        blocks.append(f"encounter.mode '{enc.get('mode')}' not host/texture/none")
    if enc.get("mode") in ("host", "texture"):
        name = (enc.get("name") or "").strip().lower()
        banned = [b.lower() for b in brief.get("banned_terms", [])]
        if name and not any(name in b or b in name for b in banned):
            flags.append("banned_terms should include the encounter's name (shown, never said)")

    if level in LEVEL_CEILINGS and len(brief.get("new_vocab", [])) > LEVEL_CEILINGS[level][2]:
        flags.append(f"new_vocab {len(brief['new_vocab'])} over the {level} budget "
                     f"({LEVEL_CEILINGS[level][2]})")
    return {"blocks": blocks, "flags": flags}


def validate_screenplay_v4(sp: dict, curriculum: dict,
                           banned_terms: list[str] | None = None) -> dict:
    blocks, flags = [], []
    level = (sp.get("cefr_level") or "").upper()
    fmt = sp.get("format")
    if fmt not in EPISODE_FORMATS:
        blocks.append(f"format '{fmt}' not in {EPISODE_FORMATS}")
    if level not in LEVEL_CEILINGS:
        blocks.append(f"cefr_level '{sp.get('cefr_level')}' not A1/A2/B1")

    # structure: 2–3 segments, ≤15s each, total ≈30 (45 = the explicit exception)
    segs = sp.get("segments", [])
    if not (2 <= len(segs) <= 3):
        blocks.append(f"expected 2–3 segments, got {len(segs)}")
    total = sum(int(s.get("duration_s", 0) or 0) for s in segs)
    if not (28 <= total <= 47):
        blocks.append(f"total duration {total}s not ~30s (or the 45s exception)")
    for s in segs:
        d = int(s.get("duration_s", 0) or 0)
        n = s.get("segment_number")
        if d > 15:
            blocks.append(f"segment {n}: {d}s over the 15s clip cap")
        shots = s.get("shots", [])
        if not shots:
            blocks.append(f"segment {n}: no shots")
        shot_sum = sum(int(sh.get("duration_s", 0) or 0) for sh in shots)
        if shots and abs(shot_sum - d) > 2:
            blocks.append(f"segment {n}: shot durations sum {shot_sum}s ≠ segment {d}s")
        for sh in shots:
            dur = int(sh.get("duration_s", 0) or 0)
            has_line = bool(sh.get("dialogue"))
            floor = 2 if has_line else 1
            if dur and dur < floor:
                what = "deliver its line" if has_line else "read on screen"
                flags.append(f"segment {n} shot {sh.get('shot_number')}: {dur}s too short to {what}")
            # TREATMENT §5 — named source + ratio, never moods
            if not (sh.get("light_source") or "").strip():
                blocks.append(f"segment {n} shot {sh.get('shot_number')}: light_source empty "
                              f"(TREATMENT §5: named source, never a mood)")
            if not LIGHT_RATIO_RE.match((sh.get("light_ratio") or "").strip()):
                blocks.append(f"segment {n} shot {sh.get('shot_number')}: light_ratio "
                              f"'{sh.get('light_ratio')}' not 'NN:NN'")
            for p in sh.get("props", []):
                if not (p.get("sound_behaviour") or "").strip():
                    flags.append(f"segment {n} shot {sh.get('shot_number')}: prop "
                                 f"'{p.get('name')}' missing sound_behaviour (TREATMENT §13)")

    # PEDAGOGY §2 ceilings — HARD
    lines = all_dialogue(sp)
    if level in LEVEL_CEILINGS:
        max_words, max_sent, _ = LEVEL_CEILINGS[level]
        total_words = sum(len((d.get("german") or "").split()) for d in lines)
        if total_words > max_words:
            blocks.append(f"{level}: {total_words} spoken words over the {max_words} ceiling")
        for d in lines:
            nw = len((d.get("german") or "").split())
            if nw > max_sent:
                blocks.append(f"{level}: {nw}-word sentence over the {max_sent} cap — "
                              f"'{(d.get('german') or '')[:40]}…'")

    speakers = {d.get("speaker") for d in lines if d.get("speaker")}
    if len(speakers) > 3:
        blocks.append(f"{len(speakers)} speakers {sorted(speakers)} — cap is 2 mains + rare cameo")
    elif len(speakers) == 3:
        flags.append("3 speakers — allowed only as a one-beat cameo (SHOW_BIBLE §5.5)")

    # curriculum consistency
    idx = _atom_index(curriculum)
    for aid in sp.get("atom_ids", []):
        if aid not in idx:
            blocks.append(f"atom '{aid}' not in the curriculum")
        elif level in _LEVEL_ORDER and _LEVEL_ORDER.get(idx[aid]["level"], 9) > _LEVEL_ORDER[level]:
            blocks.append(f"atom '{aid}' is above the declared level {level}")
    if fmt == "lesson" and not sp.get("atom_ids"):
        blocks.append("format 'lesson' with no atom_ids — the block exists to teach")

    # banned terms + the pedagogical fourth wall
    scrub = list(DEFAULT_BANNED_TOKENS) + [t for t in (banned_terms or [])]
    blocks.extend(forbidden_in_dialogue(sp, scrub))

    if level in LEVEL_CEILINGS and len(sp.get("target_vocab", [])) > LEVEL_CEILINGS[level][2]:
        flags.append(f"target_vocab {len(sp['target_vocab'])} over the {level} new-word budget")
    for v in sp.get("target_vocab", []):
        if (v.get("gender") or "") not in ("der", "die", "das", "—"):
            flags.append(f"target_vocab '{v.get('german')}': gender '{v.get('gender')}' "
                         f"not der/die/das/—")
    return {"blocks": blocks, "flags": flags}


# ── self-test (synthetic pass/fail, no LLM) ──────────────────────

def _selftest():
    import json as _json
    from pathlib import Path
    cur = _json.loads((Path(__file__).parent.parent / "resources" / "curriculum.json")
                      .read_text(encoding="utf-8"))

    shot = dict(shot_number=1, duration_s=8, shot_size="MS", camera_angle="eye-level",
                camera_move="static, locked-off, subtle handheld breathing",
                action="Rolf die Wurst stops at the empty crossing",
                blocking="Rolf die Wurst centre midground", gaze="at the red light",
                expression="flat disbelief",
                light_source="sodium street lamp camera-left", light_ratio="70:30",
                props=[], negative_prompt="", revision_prompt="hold the frame, re-render",
                dialogue=[{"speaker": "Rolf die Wurst", "german": "Warum?", "english": "Why?"}])
    shot2 = {**shot, "shot_number": 2, "duration_s": 7,
             "dialogue": [{"speaker": "Rolf die Wurst", "german": "Man darf hier nicht gehen.",
                           "english": "You may not walk here."}]}
    sp = dict(title_de="Bei Rot", format="lesson", module_id="A1.8", block_no=1,
              atom_ids=["A1.8.4"], recycled_atom_ids=[], cefr_level="A1",
              target_structure="man darf … nicht", total_duration_s=30,
              environment="empty street crossing, 3 a.m.",
              target_vocab=[{"german": "die Ampel", "english": "traffic light", "gender": "die"}],
              segments=[
                  dict(segment_number=1, duration_s=15, time_and_weather="night, dry",
                       shots=[shot, shot2]),
                  dict(segment_number=2, duration_s=15, time_and_weather="night, dry",
                       shots=[{**shot, "shot_number": 1, "duration_s": 15, "dialogue": []}]),
              ])
    ok = validate_screenplay_v4(sp, cur)
    assert ok["blocks"] == [], f"valid screenplay blocked: {ok['blocks']}"

    bad = _json.loads(_json.dumps(sp))
    bad["segments"][0]["shots"][0]["light_source"] = ""            # TREATMENT §5
    bad["segments"][0]["shots"][0]["light_ratio"] = "moody"        # ratio law
    bad["atom_ids"] = ["B1.6.3"]                                   # above level
    bad["segments"][0]["shots"][1]["dialogue"][0]["german"] = \
        "Man darf hier nicht gehen, das ist die Grammatik-Lektion für heute alle zusammen"  # cap + banned
    bad_r = validate_screenplay_v4(bad, cur)
    assert len(bad_r["blocks"]) >= 5, f"expected ≥5 blocks, got {bad_r['blocks']}"

    brief = dict(title_de="Bei Rot", format="lesson", module_id="A1.8", block_no=1,
                 atom_ids=["A1.8.4"], recycled_atom_ids=[], cefr_level="A1",
                 lead="Rolf die Wurst", cast=["Rolf die Wurst"],
                 location="empty street crossing", premise="p",
                 beats=["base reality", "first unusual thing", "escalation"],
                 button="he waits anyway",
                 target_structure="man darf … nicht",
                 target_line={"speaker": "Rolf die Wurst", "german": "Man darf hier nicht gehen.",
                              "english": "x", "why": "the lesson"},
                 encounter={"stereotype_id": "001", "name": "Bei Rot bleibt man stehen!",
                            "mode": "host"},
                 new_vocab=[], banned_terms=["rot bleibt man stehen", "ampel-regel",
                                             "bei rot bleibt man stehen!"],
                 director_notes=[])
    br = validate_brief_v4(brief, cur)
    assert br["blocks"] == [], f"valid brief blocked: {br['blocks']}"

    bad_b = dict(brief, format="synthese", recycled_atom_ids=[])
    assert validate_brief_v4(bad_b, cur)["blocks"], "synthese with atoms should block"
    print("schemas v4 self-test: PASS "
          f"(valid clean · invalid caught {len(bad_r['blocks'])} blocks/{len(bad_r['flags'])} flags)")


if __name__ == "__main__":
    _selftest()

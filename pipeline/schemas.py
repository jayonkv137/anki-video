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

# ── LESSON v4 — the layer above episodes (DESIGN_lesson_layer.md) ──
# A lesson is the unit of PLANNING; an episode is the unit of PRODUCTION. The
# block plan is decided once, in the Plan phase, before any episode's brief, and
# is a standing input to every phase of every episode in that lesson.

BLOCK = _schema(
    episode_no=INT,
    atom_ids=_arr(STR),        # the NEW atoms this episode teaches ([] for synthese)
    recycles=_arr(STR),        # previously-taught atoms deliberately spiralled back
    working_title=STR,
    shape=STR,                 # ONE line. A skeleton, never beats — beats are the Idea phase.
    format=STR,                # lesson | synthese | season_zero
    episode_id=STR,            # "" until an episode is started from this block
    state=STR,                 # planned | in_progress | made
)

LESSON_ENCOUNTER = _schema(stereotype_id=STR, name=STR, mode=STR, episode_no=INT)

LESSON_V4 = _schema(
    module_id=STR,
    level=STR,
    title=STR,
    why=STR,                   # learner language — what this lesson is about
    topics=_arr(STR),          # the module's atom ids, from curriculum.json
    lead=STR,
    recurring_cast=_arr(STR),
    world=STR,                 # the lesson's place; episodes pick a corner of it
    through_line=STR,          # how the episodes relate — the arc, in one line
    encounter=LESSON_ENCOUNTER,  # mode "none" + episode_no 0 when none fits
    blocks=_arr(BLOCK),
    deferred_atoms=_arr(STR),  # deliberately not taught here — never silently lost
    deferred_reason=STR,
    state=STR,                 # planned | in_progress | complete
    plan_version=INT,
)

LESSON_STATES = ("planned", "in_progress", "complete")
BLOCK_STATES = ("planned", "in_progress", "made")
ENCOUNTER_MODES = ("host", "texture", "none")


def validate_lesson_v4(lesson: dict, curriculum: dict) -> dict:
    """The Plan gate's check. The invariant it exists to protect:

        every atom of the lesson appears in exactly ONE block's atom_ids,
        or in deferred_atoms with a reason.

    Nothing may be silently lost between episodes of a lesson.
    """
    blocks_out, flags = [], []
    mod = next((m for m in curriculum["modules"]
                if m["id"] == lesson.get("module_id")), None)
    if not mod:
        return {"blocks": [f"module_id '{lesson.get('module_id')}' not in the curriculum"],
                "flags": []}

    if lesson.get("state") not in LESSON_STATES:
        blocks_out.append(f"lesson state '{lesson.get('state')}' not in {LESSON_STATES}")
    blocks = lesson.get("blocks", [])
    if not blocks:
        blocks_out.append("a lesson plan needs at least one block")

    nos = [b.get("episode_no") for b in blocks]
    if sorted(nos) != list(range(1, len(nos) + 1)):
        blocks_out.append(f"episode_no must be 1..N with no gaps or duplicates — got {nos}")

    module_atoms = {a["id"] for a in mod["atoms"]}
    assigned, seen_twice = [], set()
    for b in blocks:
        if b.get("state") not in BLOCK_STATES:
            blocks_out.append(f"block {b.get('episode_no')}: state '{b.get('state')}' invalid")
        if b.get("format") not in EPISODE_FORMATS:
            blocks_out.append(f"block {b.get('episode_no')}: format '{b.get('format')}' invalid")
        if b.get("format") == "lesson" and not b.get("atom_ids"):
            blocks_out.append(f"block {b.get('episode_no')}: a 'lesson' block must teach "
                              f"at least one atom (use format 'synthese' for a zero-new block)")
        if b.get("format") == "synthese" and b.get("atom_ids"):
            blocks_out.append(f"block {b.get('episode_no')}: synthese teaches zero NEW atoms")
        if len(b.get("atom_ids", [])) > 3:
            blocks_out.append(f"block {b.get('episode_no')}: more than 3 atoms — the packing "
                              f"law bundles at most 3 tightly-related atoms per 30s block")
        for aid in b.get("atom_ids", []):
            if aid not in module_atoms:
                blocks_out.append(f"block {b.get('episode_no')}: atom '{aid}' is not in "
                                  f"module {mod['id']}")
            elif aid in assigned:
                seen_twice.add(aid)
            assigned.append(aid)
        if not (b.get("shape") or "").strip():
            flags.append(f"block {b.get('episode_no')}: no shape — one line is enough, "
                         f"but a block with none is not planned")

    for aid in sorted(seen_twice):
        blocks_out.append(f"atom '{aid}' is taught as NEW in more than one episode "
                          f"(recycling is fine — put it in `recycles`)")

    # THE COVERAGE INVARIANT
    deferred = set(lesson.get("deferred_atoms", []))
    covered = set(assigned) | deferred
    missing = module_atoms - covered
    if missing:
        blocks_out.append(f"{len(missing)} atom(s) of {mod['id']} are in no block and not "
                          f"deferred: {sorted(missing)}")
    if deferred and not (lesson.get("deferred_reason") or "").strip():
        blocks_out.append("deferred_atoms needs a reason — deferring is a decision, not a gap")
    stray = deferred - module_atoms
    if stray:
        blocks_out.append(f"deferred atoms not in this module: {sorted(stray)}")

    enc = lesson.get("encounter", {})
    if enc.get("mode") not in ENCOUNTER_MODES:
        blocks_out.append(f"encounter.mode '{enc.get('mode')}' not {ENCOUNTER_MODES}")
    if enc.get("mode") == "host":
        if enc.get("episode_no") not in nos:
            blocks_out.append(f"a HOST encounter must name an episode of this lesson "
                              f"(got {enc.get('episode_no')})")
    lead = lesson.get("lead")
    if lead and lead not in ([lead] + lesson.get("recurring_cast", [])):
        blocks_out.append("lead must be part of the lesson cast")
    if len(blocks) > 4:
        flags.append(f"{len(blocks)} episodes for one lesson — rarely justified by the "
                     f"atom count; check the split")
    if not (lesson.get("through_line") or "").strip() and len(blocks) > 1:
        flags.append("no through_line — episodes of one lesson should relate to each other")
    return {"blocks": blocks_out, "flags": flags}


def lesson_progress(lesson: dict) -> dict:
    """'2 of 3 episodes' — the number that could not previously be computed."""
    blocks = lesson.get("blocks", [])
    made = sum(1 for b in blocks if b.get("state") == "made")
    return {"made": made, "total": len(blocks),
            "label": f"{made} of {len(blocks)} episodes"}


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
    depth_of_field=STR,    # deep|medium|shallow (TREATMENT §3.1)
    action=STR,            # ONE atomic visible action (TREATMENT §8)
    blocking=STR,          # spatial coordinates in the 9:16 frame (TREATMENT §7)
    gaze=STR,
    expression=STR,
    light_source=STR,      # NAMED source (TREATMENT §5) — never a mood word
    light_ratio=STR,       # "70:30" light-to-shadow
    atmosphere=STR,        # none|haze|dust|steam|smoke|rain|snow|fog (TREATMENT §8.1)
    atmosphere_density=STR,  # ""(none)|light|medium|heavy
    props=_arr(PROP),      # [] when none; material determines sound (TREATMENT §13)
    contact_shot=BOOL,     # characters touching/carrying/sharing a prop → fused sheet (§8.2)
    needs_blocking_reference=BOOL,  # POV or complex camera → mock reference (§8.2)
    negative_prompt=STR,   # per-shot additions beyond the permanent list ("" = none)
    revision_prompt=STR,   # the pre-planned correction (TREATMENT §15)
    dialogue=_arr(DIALOGUE_LINE),
)

SEGMENT_V4 = _schema(
    segment_number=INT,
    duration_s=INT,        # ~15 — one Seedance clip
    time_and_weather=STR,
    tonal_mode=STR,        # ONE named colour+light condition per segment (TREATMENT §6.5)
    shots=_arr(SHOT_V4),
)

# TREATMENT §3.1 / §8.1 vocabularies (HARD — closed sets)
DOF_VALUES = ("deep", "medium", "shallow")
ATMOSPHERE_VALUES = ("none", "haze", "dust", "steam", "smoke", "rain", "snow", "fog")
ATMOSPHERE_DENSITIES = ("", "light", "medium", "heavy")

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
        if not (s.get("tonal_mode") or "").strip():
            blocks.append(f"segment {n}: tonal_mode empty (TREATMENT §6.5: one named "
                          f"colour+light condition per segment)")
        # §8.1 — atmosphere is a continuity property of the segment, not of a shot
        atmos = {(sh.get("atmosphere") or "").strip().lower() for sh in shots}
        if len(atmos) > 1:
            blocks.append(f"segment {n}: mixed atmosphere {sorted(atmos)} inside one segment "
                          f"— the cut will read as a location change (TREATMENT §8.1)")
        # §8.3 — the density stress-test, at the lock
        speaking = sum(1 for sh in shots if sh.get("dialogue"))
        if d and shots and (d / len(shots)) < 2 and speaking:
            flags.append(f"segment {n}: {len(shots)} shots in {d}s averages "
                         f"{d / len(shots):.1f}s — too dense to read AND deliver lines; "
                         f"propose a split (TREATMENT §8.3)")
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
            sid = f"segment {n} shot {sh.get('shot_number')}"
            if (sh.get("depth_of_field") or "").strip().lower() not in DOF_VALUES:
                blocks.append(f"{sid}: depth_of_field '{sh.get('depth_of_field')}' not "
                              f"{'/'.join(DOF_VALUES)} (TREATMENT §3.1)")
            atm = (sh.get("atmosphere") or "").strip().lower()
            if atm not in ATMOSPHERE_VALUES:
                blocks.append(f"{sid}: atmosphere '{sh.get('atmosphere')}' not in "
                              f"{'/'.join(ATMOSPHERE_VALUES)} (TREATMENT §8.1)")
            dens = (sh.get("atmosphere_density") or "").strip().lower()
            if dens not in ATMOSPHERE_DENSITIES:
                blocks.append(f"{sid}: atmosphere_density '{dens}' not "
                              f"light/medium/heavy (or empty when atmosphere is none)")
            elif atm != "none" and not dens:
                blocks.append(f"{sid}: atmosphere '{atm}' needs a density")
            # §1 — the Live-Action Integration Rule names the screenplay explicitly
            banned_medium = ("puppet", "claymation", "needle-felt", "stop-motion",
                             "miniature", "toy", "handcrafted")
            blob = " ".join(str(sh.get(f) or "") for f in
                            ("action", "blocking", "expression", "camera_move",
                             "negative_prompt", "revision_prompt")).lower()
            for w in banned_medium:
                if w in blob:
                    blocks.append(f"{sid}: '{w}' appears in the shot — banned in any "
                                  f"screenplay by TREATMENT §1 (latent-space poison)")
            # §8.2 — the two pre-generation reference duties, flagged at the lock
            if (sh.get("camera_angle") or "").strip().upper() == "POV" \
                    and not sh.get("needs_blocking_reference"):
                flags.append(f"{sid}: POV shot without needs_blocking_reference — POV is a "
                             f"documented model weak point; flag it for a mock reference "
                             f"(TREATMENT §8.2)")
            if sh.get("contact_shot") and len({d.get("speaker") for d in sh.get("dialogue", [])
                                               if d.get("speaker")}) == 0 and not sh.get("props"):
                flags.append(f"{sid}: contact_shot set — confirm the fused reference sheet "
                             f"exists before this shot is generated (TREATMENT §8.2)")
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
    # PEDAGOGY §8.3 — vocabulary is taught by being USED. A word declared in
    # target_vocab but never spoken teaches nothing, and it also silently disables
    # its subtitle colour-coding (the colour map is built from target_vocab, so an
    # unspoken word is a colour that never renders). Advisory, not blocking:
    # German inflects, so exact-match absence is evidence rather than proof.
    spoken = " ".join((d.get("german") or "") for d in lines).lower()
    for v in sp.get("target_vocab", []):
        content = [t for t in (v.get("german") or "").lower().split()
                   if t not in ("der", "die", "das", "ein", "eine")]
        if content and not any(t[:max(4, len(t) - 2)] in spoken for t in content):
            flags.append(f"target_vocab '{v.get('german')}' never appears in the dialogue "
                         f"— it teaches nothing and its subtitle colour will never render")
    return {"blocks": blocks, "flags": flags}


# ── self-test (synthetic pass/fail, no LLM) ──────────────────────

def _selftest():
    import json as _json
    from pathlib import Path
    cur = _json.loads((Path(__file__).parent.parent / "resources" / "curriculum.json")
                      .read_text(encoding="utf-8"))

    shot = dict(shot_number=1, duration_s=8, shot_size="MS", camera_angle="eye-level",
                camera_move="static, locked-off, subtle handheld breathing",
                depth_of_field="deep",
                action="Rolf die Wurst stops at the empty crossing",
                blocking="Rolf die Wurst centre midground", gaze="at the red light",
                expression="flat disbelief",
                light_source="sodium street lamp camera-left", light_ratio="70:30",
                atmosphere="haze", atmosphere_density="light",
                props=[], contact_shot=False, needs_blocking_reference=False,
                negative_prompt="", revision_prompt="hold the frame, re-render",
                dialogue=[{"speaker": "Rolf die Wurst", "german": "Die Ampel ist rot.",
                           "english": "The traffic light is red."}])
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
                       tonal_mode="Sodium Street Night", shots=[shot, shot2]),
                  dict(segment_number=2, duration_s=15, time_and_weather="night, dry",
                       tonal_mode="Sodium Street Night",
                       shots=[{**shot, "shot_number": 1, "duration_s": 15, "dialogue": []}]),
              ])
    ok = validate_screenplay_v4(sp, cur)
    assert ok["blocks"] == [], f"valid screenplay blocked: {ok['blocks']}"
    assert ok["flags"] == [], f"valid screenplay flagged: {ok['flags']}"

    bad = _json.loads(_json.dumps(sp))
    bad["segments"][0]["shots"][0]["light_source"] = ""            # §5 named source
    bad["segments"][0]["shots"][0]["light_ratio"] = "moody"        # §5 ratio law
    bad["segments"][0]["shots"][0]["depth_of_field"] = "cinematic"  # §3.1 closed set
    bad["segments"][0]["shots"][0]["atmosphere"] = "moody"          # §8.1 closed set
    bad["segments"][0]["shots"][1]["atmosphere"] = "fog"            # §8.1 mixed in segment
    bad["segments"][0]["shots"][1]["action"] = "the puppet stands still"  # §1 banned medium
    bad["segments"][1]["tonal_mode"] = ""                           # §6.5 required
    bad["atom_ids"] = ["B1.6.3"]                                    # above declared level
    bad["segments"][0]["shots"][1]["dialogue"][0]["german"] = \
        "Man darf hier nicht gehen, das ist die Grammatik-Lektion für heute alle zusammen"  # cap + banned
    bad_r = validate_screenplay_v4(bad, cur)
    assert len(bad_r["blocks"]) >= 9, f"expected ≥9 blocks, got {bad_r['blocks']}"
    joined = " ".join(bad_r["blocks"])
    for expect in ("depth_of_field", "atmosphere", "mixed atmosphere", "tonal_mode",
                   "puppet", "light_ratio"):
        assert expect in joined, f"{expect} not caught: {bad_r['blocks']}"

    # §8.3 density stress-test fires as a FLAG, never a block
    dense = _json.loads(_json.dumps(sp))
    dense["segments"][0]["shots"] = [
        {**shot, "shot_number": i + 1, "duration_s": 2} for i in range(8)]
    dense["segments"][0]["duration_s"] = 15
    dr = validate_screenplay_v4(dense, cur)
    assert any("too dense" in f for f in dr["flags"]), f"density test silent: {dr}"

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

    # ── LESSON layer: the coverage invariant ──
    mod = next(m for m in cur["modules"] if m["id"] == "A1.8")
    ids = [a["id"] for a in mod["atoms"]]              # A1.8.1 … A1.8.6 (last is Synthese)
    lesson = dict(
        module_id="A1.8", level="A1", title="Regeln",
        why="What you may and may not do.", topics=ids,
        lead="Müller das Brot", recurring_cast=["Müller das Brot", "Rolf die Wurst"],
        world="the neighbourhood", through_line="Rolf tests rules; Müller doesn't react.",
        encounter={"stereotype_id": "001", "name": "Bei Rot bleibt man stehen!",
                   "mode": "host", "episode_no": 1},
        blocks=[
            dict(episode_no=1, atom_ids=ids[3:4], recycles=[], working_title="Bei Rot",
                 shape="Rolf tests the rule; Müller doesn't look", format="lesson",
                 episode_id="ep_a1-8_1", state="made"),
            dict(episode_no=2, atom_ids=ids[0:3], recycles=ids[3:4],
                 working_title="Ich kann das", shape="the permission ladder",
                 format="lesson", episode_id="", state="planned"),
            dict(episode_no=3, atom_ids=[], recycles=ids[0:4], working_title="Die Regeln",
                 shape="the gauntlet", format="synthese", episode_id="", state="planned"),
        ],
        deferred_atoms=ids[4:5], deferred_reason="Imperativ Sie lands better in A1.9",
        state="in_progress", plan_version=1)
    # ids[5] is the module's own Synthese atom — assign it to the synthese block
    lesson["blocks"][2]["recycles"] = ids[0:4]
    lesson["deferred_atoms"] = [ids[4], ids[5]]
    lr = validate_lesson_v4(lesson, cur)
    assert lr["blocks"] == [], f"valid lesson plan blocked: {lr['blocks']}"
    assert lesson_progress(lesson)["label"] == "1 of 3 episodes", lesson_progress(lesson)

    # the invariant: an atom in no block and not deferred must BLOCK
    lost = _json.loads(_json.dumps(lesson))
    lost["deferred_atoms"] = []
    assert any("in no block and not deferred" in b
               for b in validate_lesson_v4(lost, cur)["blocks"]), "coverage invariant not enforced"

    # an atom taught as NEW twice must BLOCK (recycling is the correct route)
    dup = _json.loads(_json.dumps(lesson))
    dup["blocks"][1]["atom_ids"] = dup["blocks"][1]["atom_ids"] + [ids[3]]
    assert any("more than one episode" in b
               for b in validate_lesson_v4(dup, cur)["blocks"]), "duplicate NEW atom not caught"

    # a HOST encounter must name a real episode of this lesson
    bad_enc = _json.loads(_json.dumps(lesson))
    bad_enc["encounter"]["episode_no"] = 9
    assert validate_lesson_v4(bad_enc, cur)["blocks"], "stray HOST episode_no not caught"

    # deferring without a reason is a gap pretending to be a decision
    no_reason = _json.loads(_json.dumps(lesson))
    no_reason["deferred_reason"] = ""
    assert any("needs a reason" in b for b in validate_lesson_v4(no_reason, cur)["blocks"])
    print("schemas v4 self-test: PASS "
          f"(valid clean · invalid caught {len(bad_r['blocks'])} blocks/{len(bad_r['flags'])} flags "
          f"· lesson layer: coverage invariant + duplicate-atom + HOST + deferred-reason enforced)")


if __name__ == "__main__":
    _selftest()

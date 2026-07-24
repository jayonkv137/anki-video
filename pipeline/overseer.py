"""Overseer ('Director') — the always-present editor over a run's persisted artifacts.

Two-phase and human-gated (propose → confirm → apply), NOT a free-form function-calling loop:
- `plan()`  : human instruction + current run state → Gemini STRUCTURED-OUTPUT edit plan
              (typed ops + a human-readable diff + the recompile set). Planning is structured
              output (reliable), never model-driven file writes.
- `apply()` : execute the typed ops DETERMINISTICALLY in Python, then run only the TARGETED
              downstream recompiles the dependency graph dictates, logging each to the ledger.

Dependency graph (the lock + compiler design is what makes this tractable):
    brief.json → screenplay.json (THE LOCK) → storyboard.json (sheets) → prompts.json (Seedance)
  edit a shot in segment K → recompile K's sheet-prompt + K's Seedance-prompt (only)
  edit the brief          → rebuild screenplay → ALL sheets + ALL prompts
See docs/planning/DESIGN_story_ideation_and_overseer.md Part B.
"""

import json
import re
from pathlib import Path

from . import ledger
from .rcp import REPO
from .stages import (_call_gemini, _load_skill, _schema, _arr, STR, INT, BOOL,
                     SCREENPLAY_SCHEMA, STORYBOARD_SCHEMA, PROMPTS_SCHEMA, SEGMENT_SCHEMA,
                     build_refs_manifest)

SHOT_FIELDS = {"shot_size", "camera_angle", "camera_move", "action", "blocking",
               "gaze", "expression", "lighting_mood", "duration_s"}

# Director → subtitle recolour vocabulary (natural words → colourLabel)
SUB_COLOR = {"der": "der", "blue": "der", "masculine": "der",
             "die": "die", "red": "die", "feminine": "die",
             "das": "das", "green": "das", "neuter": "das",
             "grammar": "grammar", "yellow": "grammar",
             "white": "", "default": "", "none": "", "plain": ""}

# ── Plan schema (Gemini structured output) ───────────────────────────
OP_SCHEMA = _schema(
    op=STR,                       # edit_shot | rewrite_segment | edit_brief | answer_only
    segment_number=INT,           # 0 if n/a
    shot_number=INT,              # 0 if n/a
    field_edits=_arr(_schema(field=STR, value=STR)),               # [] if n/a
    dialogue_edits=_arr(_schema(speaker=STR, german=STR, english=STR)),  # [] if n/a
    note=STR,                     # for rewrite_segment; "" otherwise
    summary=STR,                  # one-line human-readable diff for this op
)
PLAN_SCHEMA = _schema(reply=STR, operations=_arr(OP_SCHEMA), needs_confirmation=BOOL)


def _ep(run_id: str) -> Path:
    return REPO / "output" / "episodes" / f"ep_{run_id[:8]}"


def _read(ep: Path, name: str):
    p = ep / name
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else None


def _write(ep: Path, name: str, obj) -> None:
    (ep / name).write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding="utf-8")


# ── State digest for the planner ─────────────────────────────────────

def _state_summary(ep: Path) -> str:
    brief, sp = _read(ep, "brief.json"), _read(ep, "screenplay.json")
    board, prompts = _read(ep, "storyboard.json"), _read(ep, "prompts.json")
    lines = []
    if brief:
        lines.append(f"BRIEF: title={brief.get('title_de')} · lesson={json.dumps(brief.get('lesson'), ensure_ascii=False)} "
                     f"· premise={(brief.get('premise') or '')[:140]}")
    if sp:
        lines.append(f"SCREENPLAY: {sp.get('title_de')} · grammar_target={sp.get('grammar_target')} "
                     f"· {len(sp.get('segments', []))} segments")
        for seg in sp.get("segments", []):
            for sh in seg.get("shots", []):
                dlg = " / ".join(f"{d.get('speaker')}: „{d.get('german')}“" for d in sh.get("dialogue", []))
                lines.append(
                    f"  seg{seg.get('segment_number')} shot{sh.get('shot_number')} "
                    f"({sh.get('duration_s')}s {sh.get('shot_size')}/{sh.get('camera_angle')}): "
                    f"action={(sh.get('action') or '')[:70]} | light={sh.get('lighting_mood')} "
                    f"| gaze={sh.get('gaze')} | expr={sh.get('expression')} | dialogue=[{dlg}]")
    subs = _read(ep, "subtitles.json")
    if subs:
        lines.append(f"SUBTITLES: {len(subs.get('subtitles', []))} cues (colour-coded German)")
        for c in subs.get("subtitles", []):
            cols = ",".join(f"{w['word']}:{w['colorLabel']}" for w in c.get("words", []) if w.get("colorLabel"))
            lines.append(f"  {c.get('id')} seg{c.get('segment')} f{c.get('startFrame')}-{c.get('endFrame')}: "
                         f"{c.get('text')!r}" + (f" [{cols}]" if cols else ""))
    lines.append(f"ARTIFACTS present → brief={bool(brief)} screenplay={bool(sp)} "
                 f"storyboard={bool(board)} prompts={bool(prompts)} subtitles={bool(subs)}")
    return "\n".join(lines) or "(empty run — nothing generated yet)"


# ── PLAN ─────────────────────────────────────────────────────────────

def plan(run_id: str, instruction: str, step: str, rcp) -> dict:
    """Human instruction → a proposed, typed edit plan (structured output). Applies nothing."""
    ep = _ep(run_id)
    skill = _load_skill("skill-5-overseer.md")
    system = (rcp.for_screenplay_stage() + "\n\n" + skill
              + "\n\n## CURRENT RUN STATE\n" + _state_summary(ep)
              + f"\n\nThe human is currently on studio step: {step or 'unknown'}.")
    parsed, _, _ = _call_gemini(system, f"Human instruction: {instruction}", PLAN_SCHEMA, temperature=0.3)
    ops = parsed.get("operations") or []
    parsed["operations"] = ops
    parsed.setdefault("reply", "")
    parsed["needs_confirmation"] = bool(parsed.get("needs_confirmation") and _real_ops(ops))
    parsed["recompile"] = _describe_recompile(ep, ops)   # the GRAPH decides, not the model
    return parsed


def _real_ops(ops: list) -> list:
    return [o for o in ops if o.get("op") in ("edit_shot", "rewrite_segment", "edit_brief")]


def _affected(ops: list):
    segs, brief_touched = set(), False
    for op in ops:
        t = op.get("op")
        if t == "edit_brief":
            brief_touched = True
        elif t in ("edit_shot", "rewrite_segment") and op.get("segment_number"):
            segs.add(int(op["segment_number"]))
    return segs, brief_touched


def _describe_recompile(ep: Path, ops: list) -> list:
    segs, brief_touched = _affected(ops)
    if brief_touched:
        return ["brief → screenplay → ALL storyboard sheets + ALL Seedance prompts (full rebuild)"]
    has_board, has_prompts = (ep / "storyboard.json").exists(), (ep / "prompts.json").exists()
    out = []
    for s in sorted(segs):
        chain = f"screenplay segment {s}"
        if has_board:
            chain += f" → storyboard sheet {s}"
        if has_prompts:
            chain += f" → Seedance prompt {s}"
        out.append(chain)
    return out or (["(no downstream to recompile yet)"] if _real_ops(ops) else [])


# ── APPLY ────────────────────────────────────────────────────────────

def apply(run_id: str, operations: list, rcp) -> dict:
    """Execute the confirmed ops deterministically, then run the targeted recompiles."""
    ep = _ep(run_id)
    sp, brief = _read(ep, "screenplay.json"), _read(ep, "brief.json")
    sub_state = _read(ep, "subtitles.json")
    applied, segs, brief_touched, subs_touched = [], set(), False, False

    for op in operations:
        t = op.get("op")
        if t in ("recolor_word", "edit_subtitle", "shift_subtitles") and sub_state:
            if _apply_sub_op(sub_state, op):
                subs_touched = True
                applied.append(op.get("summary") or t.replace("_", " "))
        elif t == "edit_shot" and sp:
            seg_n, shot_n = int(op.get("segment_number") or 0), int(op.get("shot_number") or 0)
            sh = _find_shot(sp, seg_n, shot_n)
            if sh is None:
                continue
            for fe in op.get("field_edits", []):
                _set_shot_field(sh, fe.get("field", ""), fe.get("value", ""))
            for de in op.get("dialogue_edits", []):
                _set_dialogue(sh, de)
            segs.add(seg_n)
            applied.append(op.get("summary") or f"edited segment {seg_n} shot {shot_n}")
        elif t == "rewrite_segment" and sp:
            seg_n = int(op.get("segment_number") or 0)
            if _rewrite_segment(sp, seg_n, op.get("note", ""), rcp):
                segs.add(seg_n)
                applied.append(op.get("summary") or f"rewrote segment {seg_n}")
        elif t == "edit_brief" and brief:
            for fe in op.get("field_edits", []):
                _set_dotted(brief, fe.get("field", ""), fe.get("value", ""))
            brief_touched = True
            applied.append(op.get("summary") or "edited the brief")

    # persist the lock edits + subtitle edits
    if brief_touched:
        _write(ep, "brief.json", brief)
    if sp:
        _write(ep, "screenplay.json", sp)
    if subs_touched:
        _write(ep, "subtitles.json", sub_state)

    # targeted downstream recompiles (the dependency graph)
    recompiled = []
    if brief_touched:
        sp = _regen_screenplay(run_id, brief, rcp, ep)
        recompiled.append("screenplay")
        segs = {seg.get("segment_number") for seg in sp.get("segments", [])}
    for s in sorted(segs):
        if (ep / "storyboard.json").exists() and _regen_sheet(run_id, sp, s, rcp, ep):
            recompiled.append(f"storyboard sheet {s}")
        if (ep / "prompts.json").exists() and _regen_prompt(run_id, sp, s, rcp, ep):
            recompiled.append(f"Seedance prompt {s}")

    try:  # audit logging is best-effort — never let it break an applied edit
        ledger.log_event(run_id, "overseer", "completed",
                         detail={"applied": applied, "recompiled": recompiled})
    except Exception as e:
        print(f"[overseer: ledger log skipped: {e}]")
    return {
        "applied": applied,
        "recompiled": recompiled,
        "artifacts": {
            "brief": _read(ep, "brief.json"),
            "screenplay": _read(ep, "screenplay.json"),
            "storyboard": _read(ep, "storyboard.json"),
            "prompts": _read(ep, "prompts.json"),
            "refs_manifest": _read(ep, "prompts/refs_manifest.json"),
            "subtitles": _read(ep, "subtitles.json"),
        },
    }


def _apply_sub_op(state: dict, op: dict) -> bool:
    """Mutate the subtitle STATE (the leaf artifact — no recompile). Supports recolour_word,
    edit_subtitle (retext a cue by segment/shot), and shift_subtitles (nudge a segment's cues)."""
    from . import subtitles as subs
    t, cues = op.get("op"), state.get("subtitles", [])
    changed = False
    if t == "recolor_word":
        for fe in op.get("field_edits", []):
            target, label = subs._norm(fe.get("field", "")), SUB_COLOR.get((fe.get("value") or "").lower().strip(), "")
            for cue in cues:
                for w in cue.get("words", []):
                    if subs._norm(w.get("word", "")) == target:
                        w["colorLabel"] = label
                        changed = True
    elif t == "edit_subtitle":
        seg_n, shot_n = int(op.get("segment_number") or 0), int(op.get("shot_number") or 0)
        text = op.get("note") or ""
        for cue in cues:
            if cue.get("segment") == seg_n and (not shot_n or cue.get("shot") == shot_n) and text:
                look = {subs._norm(w["word"]): w.get("colorLabel", "")
                        for c in cues for w in c.get("words", [])}
                cue["text"] = text
                cue["words"] = subs._distribute_words(text.split(), cue["startFrame"], cue["endFrame"],
                                                      {}, set())
                for w in cue["words"]:
                    w["colorLabel"] = look.get(subs._norm(w["word"]), "")
                changed = True
                break
    elif t == "shift_subtitles":
        seg_n = int(op.get("segment_number") or 0)
        df = 0
        for fe in op.get("field_edits", []):
            try:
                df = int(str(fe.get("value", "0")).strip())
            except ValueError:
                df = 0
        if not df and op.get("note"):
            m = re.search(r"-?\d+", op["note"])
            df = int(m.group()) if m else 0
        for cue in cues:
            if seg_n and cue.get("segment") != seg_n:
                continue
            cue["startFrame"] = max(0, cue["startFrame"] + df)
            cue["endFrame"] = max(cue["startFrame"] + 1, cue["endFrame"] + df)
            for w in cue.get("words", []):
                w["startFrame"] = max(0, w["startFrame"] + df)
                w["endFrame"] = max(w["startFrame"] + 1, w["endFrame"] + df)
            changed = True
    return changed


# ── Deterministic edit helpers ───────────────────────────────────────

def _find_shot(sp: dict, seg_n, shot_n):
    for seg in sp.get("segments", []):
        if seg.get("segment_number") == seg_n:
            for sh in seg.get("shots", []):
                if sh.get("shot_number") == shot_n:
                    return sh
    return None


def _set_shot_field(shot: dict, field: str, value: str) -> None:
    if field not in SHOT_FIELDS:
        return
    if field == "duration_s":
        try:
            shot[field] = int(str(value).strip())
        except ValueError:
            pass
    else:
        shot[field] = value


def _set_dialogue(shot: dict, de: dict) -> None:
    speaker = (de.get("speaker") or "").strip()
    if not speaker:
        return
    shot.setdefault("dialogue", [])
    for line in shot["dialogue"]:
        if (line.get("speaker") or "").strip().lower() == speaker.lower():
            if de.get("german"):
                line["german"] = de["german"]
            if de.get("english"):
                line["english"] = de["english"]
            return
    shot["dialogue"].append({"speaker": speaker, "german": de.get("german", ""),
                             "english": de.get("english", "")})


def _set_dotted(obj: dict, path: str, value: str) -> None:
    """Set a possibly-dotted path (e.g. 'lesson.particle') on a dict."""
    if not path:
        return
    keys = path.split(".")
    cur = obj
    for k in keys[:-1]:
        if not isinstance(cur.get(k), dict):
            cur[k] = {}
        cur = cur[k]
    cur[keys[-1]] = value


# ── Recompile helpers (call the compiler skills, splice surgically) ──

def _gemini(skill_name: str, replacements: dict, schema: dict, context: str) -> dict:
    skill = _load_skill(skill_name)
    for k, v in replacements.items():
        skill = skill.replace(k, v)
    parsed, _, _ = _call_gemini(context + "\n\n" + skill, "Produce the required JSON now.", schema)
    return parsed


def _rewrite_segment(sp: dict, seg_n: int, note: str, rcp) -> bool:
    """Regenerate ONE segment's shots from an instruction, splice back into the screenplay."""
    target = next((seg for seg in sp.get("segments", []) if seg.get("segment_number") == seg_n), None)
    if target is None:
        return False
    system = (rcp.for_screenplay_stage()
              + "\n\nYou are revising ONE segment of a locked screenplay. Keep the SAME "
              "segment_number and duration_s; the shots MUST sum to that duration; ≤2 speaking "
              "characters; keep the director layer per shot (shot_size/camera_angle/camera_move/"
              "action/blocking/gaze/expression/lighting_mood/dialogue); the stereotype stays "
              "SHOWN-not-explained and the episode's lesson still emerges. Return the revised "
              "segment object only.\n\n"
              f"CHARACTER BIBLE:\n{rcp.character_bible}\n\n"
              f"FULL SCREENPLAY (context):\n{json.dumps(sp, ensure_ascii=False)}\n\n"
              f"SEGMENT TO REVISE (number {seg_n}):\n{json.dumps(target, ensure_ascii=False)}")
    new_seg, _, _ = _call_gemini(system, f"Revision instruction: {note}", SEGMENT_SCHEMA, temperature=0.5)
    new_seg["segment_number"] = seg_n
    for i, seg in enumerate(sp["segments"]):
        if seg.get("segment_number") == seg_n:
            sp["segments"][i] = new_seg
            return True
    return False


def _regen_screenplay(run_id: str, brief: dict, rcp, ep: Path) -> dict:
    sp = _gemini("skill-2-screenplay-writer.md",
                 {"{{CHARACTER_BIBLE}}": rcp.character_bible,
                  "{{STORY_JSON}}": json.dumps(brief, ensure_ascii=False)},
                 SCREENPLAY_SCHEMA, rcp.for_screenplay_stage())
    _write(ep, "screenplay.json", sp)
    try:
        ledger.update_run(run_id, stage="screenplay")
    except Exception as e:
        print(f"[overseer: ledger update skipped: {e}]")
    return sp


def _regen_sheet(run_id: str, sp: dict, seg_n: int, rcp, ep: Path) -> bool:
    """Recompile ONE segment's storyboard sheet-PROMPT; splice into storyboard.json (keep the
    others + the mirrored style_clause). The panel IMAGE is regenerated manually by the human."""
    board = _read(ep, "storyboard.json") or {"style_clause": "", "sheets": []}
    fresh = _gemini("skill-2b-storyboard.md",
                    {"{{CHARACTER_BIBLE}}": rcp.character_bible,
                     "{{SCREENPLAY_JSON}}": json.dumps(sp, ensure_ascii=False)},
                    STORYBOARD_SCHEMA, rcp.for_prompt_stage())
    new_sheet = next((s for s in fresh.get("sheets", []) if s.get("segment_number") == seg_n), None)
    if new_sheet is None:
        return False
    sheets = [s for s in board.get("sheets", []) if s.get("segment_number") != seg_n]
    sheets.append(new_sheet)
    board["sheets"] = sorted(sheets, key=lambda s: s.get("segment_number") or 0)
    if not board.get("style_clause"):
        board["style_clause"] = fresh.get("style_clause", "")
    _write(ep, "storyboard.json", board)
    return True


def _regen_prompt(run_id: str, sp: dict, seg_n: int, rcp, ep: Path) -> bool:
    """Recompile ONE segment's Seedance prompt; splice into prompts.json + rewrite the split
    files + refs_manifest."""
    prompts = _read(ep, "prompts.json") or {"segments": []}
    fresh = _gemini("skill-3-prompt-writer.md",
                    {"{{SCREENPLAY_JSON}}": json.dumps(sp, ensure_ascii=False)},
                    PROMPTS_SCHEMA, rcp.for_prompt_stage())
    new_seg = next((s for s in fresh.get("segments", []) if s.get("segment_number") == seg_n), None)
    if new_seg is None:
        return False
    segs = [s for s in prompts.get("segments", []) if s.get("segment_number") != seg_n]
    segs.append(new_seg)
    prompts["segments"] = sorted(segs, key=lambda s: s.get("segment_number") or 0)
    _write(ep, "prompts.json", prompts)
    pdir = ep / "prompts"
    pdir.mkdir(parents=True, exist_ok=True)
    (pdir / f"segment_{int(seg_n):02d}.seedance.json").write_text(
        json.dumps(new_seg, ensure_ascii=False, indent=2), encoding="utf-8")
    manifest = build_refs_manifest(prompts, run_id, ep)
    (pdir / "refs_manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2),
                                             encoding="utf-8")
    return True

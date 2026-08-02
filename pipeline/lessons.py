"""Lessons — the layer above episodes (PIPELINE §3.0, DESIGN_lesson_layer.md).

A **lesson** is a curriculum module and the unit of PLANNING.
An **episode** is one ~30s video and the unit of PRODUCTION.

The Plan phase runs ONCE per lesson, before any episode's brief, and produces
`lesson.json` — the block plan. That artifact is then a standing input to every
phase of every episode in the lesson, which is what lets three episodes of one
lesson form an arc instead of three unrelated thirty-second gags.

The invariant this module exists to protect:

    every atom of the lesson appears in exactly ONE block,
    or in deferred_atoms WITH A REASON.

Reality outranks the plan: a made episode is never invalidated by a re-plan. The
plan is corrected and the episode marked stale, with re-making offered as the
deliberate alternative — never the automatic one.
"""

import json
from datetime import datetime, timezone
from pathlib import Path

from . import context as ctx
from . import schemas as S
from . import universe_state as st
from .rcp import REPO

LESSONS = REPO / "output" / "lessons"
SEASON_ZERO = "S0"


class LessonError(RuntimeError):
    """An illegal lesson-plan operation."""


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def path_for(module_id: str) -> Path:
    return LESSONS / module_id.replace(".", "-") / "lesson.json"


def exists(module_id: str) -> bool:
    return path_for(module_id).exists()


def load(module_id: str) -> dict:
    p = path_for(module_id)
    if not p.exists():
        raise LessonError(f"lesson '{module_id}' has no plan yet — run the Plan phase first")
    return json.loads(p.read_text(encoding="utf-8"))


def save(lesson: dict) -> dict:
    p = path_for(lesson["module_id"])
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(lesson, ensure_ascii=False, indent=2), encoding="utf-8")
    return lesson


def validate(lesson: dict) -> dict:
    return S.validate_lesson_v4(lesson, ctx.curriculum())


# ── Creating a plan ──────────────────────────────────────────────

def scaffold(module_id: str) -> dict:
    """An empty, INVALID plan seeded from the curriculum — the Plan conversation's
    starting point. It is deliberately invalid (no blocks) so it cannot be
    approved before anyone has decided anything."""
    mod = ctx.module(module_id)
    if not mod and module_id != SEASON_ZERO:
        raise LessonError(f"'{module_id}' is not a curriculum module")
    if mod:
        topics = [a["id"] for a in mod["atoms"]]
        return {"module_id": mod["id"], "level": mod["level"], "title": mod["title"],
                "why": "", "topics": topics, "lead": "", "recurring_cast": [],
                "world": "", "through_line": "",
                "encounter": {"stereotype_id": "", "name": "", "mode": "none",
                              "episode_no": 0},
                "blocks": [], "deferred_atoms": [], "deferred_reason": "",
                "state": "planned", "plan_version": 1, "created_at": _now()}
    # Season 0 — four portal intros, outside the curriculum, no atoms at all.
    return {"module_id": SEASON_ZERO, "level": "S0", "title": "Season 0 — the arrivals",
            "why": "Four characters torn out of their own worlds and dropped into Germany.",
            "topics": [], "lead": "", "recurring_cast": [], "world": "",
            "through_line": "Each arrives alone, convinced they are the only one.",
            "encounter": {"stereotype_id": "", "name": "", "mode": "none", "episode_no": 0},
            "blocks": [], "deferred_atoms": [], "deferred_reason": "",
            "state": "planned", "plan_version": 1, "created_at": _now()}


def create(module_id: str) -> dict:
    if exists(module_id):
        raise LessonError(f"lesson '{module_id}' already has a plan — reopen it to change it")
    return save(scaffold(module_id))


def approve_plan(module_id: str) -> dict:
    """The Plan gate. Blocks on the coverage invariant and every hard rule."""
    lesson = load(module_id)
    r = validate(lesson)
    if r["blocks"]:
        raise LessonError(f"the plan cannot be approved — {len(r['blocks'])} problem(s); "
                          f"first: {r['blocks'][0]}")
    lesson["state"] = "in_progress"
    lesson["approved_at"] = _now()
    save(lesson)
    try:
        st.log("lesson_planned", ref=module_id,
               detail={"episodes": len(lesson["blocks"]),
                       "plan_version": lesson["plan_version"],
                       "formats": [b["format"] for b in lesson["blocks"]]})
    except Exception as e:
        print(f"[lessons: state log skipped: {e}]")
    return {"module_id": module_id, "episodes": len(lesson["blocks"]), "flags": r["flags"]}


# ── Progress — the number that was previously impossible ─────────

def progress(module_id: str) -> dict:
    lesson = load(module_id)
    p = S.lesson_progress(lesson)
    return {**p, "module_id": module_id, "title": lesson["title"],
            "state": lesson["state"],
            "blocks": [{"episode_no": b["episode_no"], "state": b["state"],
                        "format": b["format"], "working_title": b["working_title"],
                        "episode_id": b["episode_id"] or None} for b in lesson["blocks"]]}


def block_for_episode(module_id: str, episode_no: int) -> dict:
    lesson = load(module_id)
    b = next((x for x in lesson["blocks"] if x["episode_no"] == episode_no), None)
    if not b:
        raise LessonError(f"lesson '{module_id}' has no episode {episode_no}")
    return b


def bind_episode(module_id: str, episode_no: int, episode_id: str) -> dict:
    """Attach a started episode to its block."""
    lesson = load(module_id)
    b = next((x for x in lesson["blocks"] if x["episode_no"] == episode_no), None)
    if not b:
        raise LessonError(f"no block {episode_no} in lesson '{module_id}'")
    b["episode_id"] = episode_id
    if b["state"] == "planned":
        b["state"] = "in_progress"
    save(lesson)
    return b


def mark_made(module_id: str, episode_no: int) -> dict:
    lesson = load(module_id)
    b = next((x for x in lesson["blocks"] if x["episode_no"] == episode_no), None)
    if not b:
        raise LessonError(f"no block {episode_no} in lesson '{module_id}'")
    b["state"] = "made"
    b["made_under_plan_version"] = lesson["plan_version"]
    if all(x["state"] == "made" for x in lesson["blocks"]):
        lesson["state"] = "complete"
    save(lesson)
    return progress(module_id)


# ── Re-planning (Jayon: allowed, after episodes exist) ───────────

def replan_preview(module_id: str, new_blocks: list, *,
                   deferred_atoms: list | None = None,
                   deferred_reason: str | None = None) -> dict:
    """The blast radius, as a READ — shown BEFORE the change, never after.

    Previews the WHOLE proposed change: the blocks AND the deferred list must be
    validated together, because re-homing an atom into a new block while leaving
    it in `deferred` makes the plan claim two contradictory things.

    Reality outranks the plan: an already-made episode is a fact. This reports
    what a re-plan would disturb; it never silently invalidates finished work.
    """
    lesson = load(module_id)
    old = {b["episode_no"]: b for b in lesson["blocks"]}
    new = {b["episode_no"]: b for b in new_blocks}
    made = {n for n, b in old.items() if b["state"] == "made"}

    stale, removed, added, reordered = [], [], [], []
    for n in made:
        if n not in new:
            removed.append(n)
        elif set(new[n].get("atom_ids", [])) != set(old[n].get("atom_ids", [])):
            stale.append(n)                      # its screenplay now teaches the wrong thing
    for n in new:
        if n not in old:
            added.append(n)
    old_titles = [b["working_title"] for b in lesson["blocks"]]
    new_titles = [b["working_title"] for b in new_blocks]
    if [t for t in new_titles if t in old_titles] != [t for t in old_titles if t in new_titles]:
        reordered = [t for t in new_titles if t in old_titles]

    probe = {**lesson, "blocks": new_blocks, "plan_version": lesson["plan_version"] + 1}
    if deferred_atoms is not None:
        probe["deferred_atoms"] = deferred_atoms
        probe["deferred_reason"] = (deferred_reason if deferred_reason is not None
                                    else lesson.get("deferred_reason", ""))
    check = validate(probe)
    return {
        "module_id": module_id,
        "made_episodes": sorted(made),
        "added": sorted(added),
        "removed_from_plan": sorted(removed),
        "made_but_now_stale": sorted(stale),
        "reordered": bool(reordered),
        "warning": ("⚠ Reordering moves a made episode relative to ones that may reference it "
                    "— the through-line can break silently." if reordered else ""),
        "note": ("A made episode is never deleted or overwritten by a re-plan. Removed blocks "
                 "are unlinked and their atoms return to deferred; stale ones keep their "
                 "screenplay and are flagged so you can correct the plan or re-make them."),
        "validation": check,
        "can_apply": not check["blocks"],
    }


def replan(module_id: str, new_blocks: list, *, deferred_atoms: list | None = None,
           deferred_reason: str = "", confirmed: bool = False) -> dict:
    """Apply a re-plan. Requires `confirmed=True` — the caller must have shown
    `replan_preview` first."""
    if not confirmed:
        raise LessonError("a re-plan must be confirmed after seeing replan_preview()")
    lesson = load(module_id)
    pv = replan_preview(module_id, new_blocks, deferred_atoms=deferred_atoms,
                        deferred_reason=deferred_reason or None)
    if not pv["can_apply"]:
        raise LessonError(f"the new plan is invalid: {pv['validation']['blocks'][0]}")

    old = {b["episode_no"]: b for b in lesson["blocks"]}
    merged = []
    for b in new_blocks:
        prev = old.get(b["episode_no"])
        if prev and prev["state"] == "made":
            # reality outranks the plan — keep the made episode intact
            b = {**b, "state": "made", "episode_id": prev["episode_id"],
                 "made_under_plan_version": prev.get("made_under_plan_version",
                                                     lesson["plan_version"]),
                 "stale": b["episode_no"] in pv["made_but_now_stale"]}
        merged.append(b)

    lesson["blocks"] = merged
    if deferred_atoms is not None:
        lesson["deferred_atoms"] = deferred_atoms
        lesson["deferred_reason"] = deferred_reason or lesson.get("deferred_reason", "")
    lesson["plan_version"] += 1
    lesson["replanned_at"] = _now()
    if lesson["state"] == "complete" and any(b["state"] != "made" for b in merged):
        lesson["state"] = "in_progress"
    save(lesson)
    return {"module_id": module_id, "plan_version": lesson["plan_version"],
            "stale_episodes": pv["made_but_now_stale"], "progress": progress(module_id)}


# ── Context for the agents ───────────────────────────────────────

def plan_block(module_id: str) -> str:
    """`lesson.json` as a standing input for any phase of any episode in it."""
    lesson = load(module_id)
    lines = [f"# LESSON PLAN — {lesson['module_id']} “{lesson['title']}” ({lesson['level']})",
             f"{lesson['why']}",
             f"Through-line: {lesson['through_line'] or '—'}",
             f"World: {lesson['world'] or '—'} · Lead: {lesson['lead'] or '—'}"]
    enc = lesson.get("encounter", {})
    if enc.get("mode") in ("host", "texture"):
        lines.append(f"Encounter: {enc['name']} ({enc['mode']}"
                     + (f", episode {enc['episode_no']}" if enc.get("episode_no") else "") + ")")
    lines.append(f"\n{S.lesson_progress(lesson)['label']}:")
    for b in lesson["blocks"]:
        atoms = ", ".join(b["atom_ids"]) or "—"
        extra = f" · moves: {b['moves']}" if b.get("moves") else ""
        lines.append(f"  {b['episode_no']}. [{b['format']}/{b['state']}] "
                     f"“{b['working_title']}” — {b['shape']} (teaches: {atoms}){extra}")
    if lesson.get("deferred_atoms"):
        lines.append(f"\nDeferred from this lesson: {', '.join(lesson['deferred_atoms'])} "
                     f"— {lesson.get('deferred_reason', '')}")
    return "\n".join(lines)


def siblings_block(module_id: str, episode_no: int, screenplay_of) -> str:
    """Sibling episodes as `[EARLIER IN THIS LESSON]` SUMMARIES — never transcripts.

    Backwards is fact (locked), forwards is intention (still movable). The
    standalone rule outranks the arc: an episode may reference an earlier one,
    never require it. `screenplay_of(episode_id) -> dict | None` is injected so
    this module stays free of episode-storage concerns.
    """
    lesson = load(module_id)
    earlier, later = [], []
    for b in lesson["blocks"]:
        if b["episode_no"] == episode_no:
            continue
        if b["episode_no"] < episode_no and b["state"] == "made" and b.get("episode_id"):
            sp = screenplay_of(b["episode_id"]) or {}
            hook = ""
            for seg in sp.get("segments", []):
                for sh in seg.get("shots", []):
                    hook = sh.get("action", "")
                    break
                break
            earlier.append(f"  Ep{b['episode_no']} “{sp.get('title_de', b['working_title'])}”: "
                           f"{hook or b['shape']}")
        elif b["episode_no"] > episode_no:
            later.append(f"  Ep{b['episode_no']} [{b['format']}]: {b['shape']}")
    out = []
    if earlier:
        out.append("# EARLIER IN THIS LESSON (locked — these are facts)\n" + "\n".join(earlier))
    if later:
        out.append("# LATER IN THIS LESSON (planned — intention, still movable; "
                   "do not resolve their beats here)\n" + "\n".join(later))
    if out:
        out.append("Reference them if it helps, but this episode must stand alone for "
                   "someone who has seen none of them (STORY_SYSTEM §6).")
    return "\n\n".join(out)


def list_plans() -> list[dict]:
    out = []
    if not LESSONS.exists():
        return out
    for d in sorted(LESSONS.iterdir()):
        p = d / "lesson.json"
        if p.exists():
            try:
                out.append(progress(json.loads(p.read_text(encoding="utf-8"))["module_id"]))
            except Exception:
                continue
    return out

#!/usr/bin/env python3
"""Lesson layer test — the block plan, the coverage invariant, re-planning,
narrative episodes, and the sibling context that makes a lesson an arc.

    .venv/bin/python scripts/test_lessons.py

No LLM calls, no spend. Writes to output/lessons/ and cleans up.
"""

import shutil
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from pipeline import context as ctx      # noqa: E402
from pipeline import lessons as L        # noqa: E402
from pipeline import schemas as S        # noqa: E402

MOD = "A1.8"
PASS, FAIL = [], []


def check(name, cond, detail=""):
    (PASS if cond else FAIL).append(name)
    print(f"  {'✓' if cond else '✗'} {name}" + (f"  — {detail}" if detail else ""))
    return cond


def cleanup():
    shutil.rmtree(L.LESSONS / MOD.replace(".", "-"), ignore_errors=True)
    shutil.rmtree(L.LESSONS / "S0", ignore_errors=True)


def blocks(ids):
    return [
        dict(episode_no=1, atom_ids=[ids[3]], recycles=[], working_title="Bei Rot",
             shape="Rolf tests the rule; Müller doesn't look", moves="", format="lesson",
             episode_id="", state="planned"),
        dict(episode_no=2, atom_ids=ids[0:3], recycles=[ids[3]],
             working_title="Ich kann das", shape="the permission ladder", moves="",
             format="lesson", episode_id="", state="planned"),
        dict(episode_no=3, atom_ids=[], recycles=ids[0:4], working_title="Die Regeln",
             shape="the gauntlet", moves="", format="synthese",
             episode_id="", state="planned"),
    ]


def main():
    cleanup()
    print("LESSON LAYER TEST")
    cur = ctx.curriculum()
    ids = [a["id"] for a in ctx.module(MOD)["atoms"]]

    # ── 1 · scaffold + the gate refuses an unplanned lesson ──
    print("\n[1] scaffold + the Plan gate")
    p = L.create(MOD)
    check("scaffold seeds topics from the curriculum", p["topics"] == ids, f"{len(ids)} topics")
    check("scaffold starts INVALID (nothing decided yet)",
          L.validate(p)["blocks"] != [])
    try:
        L.approve_plan(MOD)
        check("an empty plan cannot be approved", False)
    except L.LessonError as e:
        check("an empty plan cannot be approved", True, str(e)[:46])
    check("duplicate create refused", _raises(lambda: L.create(MOD)))

    # ── 2 · the coverage invariant ──
    print("\n[2] the coverage invariant")
    p = L.load(MOD)
    p.update(why="Rules and permission.", lead="Müller das Brot",
             recurring_cast=["Müller das Brot", "Rolf die Wurst"],
             world="the neighbourhood", through_line="Rolf tests; Müller doesn't react.",
             blocks=blocks(ids))
    L.save(p)
    r = L.validate(p)
    check("atoms in no block and not deferred → BLOCK",
          any("in no block and not deferred" in b for b in r["blocks"]), str(r["blocks"][:1]))
    p["deferred_atoms"] = [ids[4], ids[5]]
    p["deferred_reason"] = "Imperativ Sie lands better in A1.9"
    L.save(p)
    check("deferring WITH a reason satisfies it", L.validate(p)["blocks"] == [])
    p["deferred_reason"] = ""
    L.save(p)
    check("deferring WITHOUT a reason → BLOCK", L.validate(p)["blocks"] != [])
    p["deferred_reason"] = "Imperativ Sie lands better in A1.9"
    L.save(p)

    res = L.approve_plan(MOD)
    check("a complete plan approves", res["episodes"] == 3)
    check("lesson moves to in_progress", L.load(MOD)["state"] == "in_progress")

    # ── 3 · '2 of 3' — the number that did not exist ──
    print("\n[3] progress")
    check("progress starts at 0 of 3", L.progress(MOD)["label"] == "0 of 3 episodes")
    L.bind_episode(MOD, 1, "ep_a1-8_1")
    L.mark_made(MOD, 1)
    L.bind_episode(MOD, 2, "ep_a1-8_2")
    L.mark_made(MOD, 2)
    check("progress reads '2 of 3 episodes'", L.progress(MOD)["label"] == "2 of 3 episodes")
    check("the made episodes are bound to their blocks",
          L.block_for_episode(MOD, 1)["episode_id"] == "ep_a1-8_1")
    L.mark_made(MOD, 3)
    check("all made → lesson complete", L.load(MOD)["state"] == "complete")

    # ── 4 · re-planning: reality outranks the plan ──
    print("\n[4] re-planning (Jayon: allowed after episodes exist)")
    nb = [dict(b) for b in L.load(MOD)["blocks"]]
    nb.append(dict(episode_no=4, atom_ids=[ids[4]], recycles=[], working_title="Warten Sie!",
                   shape="the official", moves="", format="lesson",
                   episode_id="", state="planned"))
    pv = L.replan_preview(MOD, nb)
    check("adding an episode leaves made ones untouched", pv["made_but_now_stale"] == [])
    check("preview is a READ — nothing changed",
          L.load(MOD)["plan_version"] == 1 and len(L.load(MOD)["blocks"]) == 3)
    check("preview blocks while the new atom is still ALSO deferred",
          not pv["can_apply"], "an atom cannot be taught AND deferred")
    pv_full = L.replan_preview(MOD, nb, deferred_atoms=[ids[5]],
                               deferred_reason="the module Synthese rides in episode 3")
    check("previewing the WHOLE change (blocks + deferred) is valid", pv_full["can_apply"],
          str(pv_full["validation"]["blocks"][:1]))
    out = L.replan(MOD, nb, deferred_atoms=[ids[5]],
                   deferred_reason="the module Synthese rides in episode 3", confirmed=True)
    check("re-plan applies with the atom re-homed", out["plan_version"] == 2)
    check("progress becomes 3 of 4", L.progress(MOD)["label"] == "3 of 4 episodes")
    check("a completed lesson reopens when a block is added",
          L.load(MOD)["state"] == "in_progress")
    check("an unconfirmed re-plan raises",
          _raises(lambda: L.replan(MOD, nb, confirmed=False)))

    # moving an atom out of a MADE episode marks it stale, never deletes it
    moved = [dict(b) for b in L.load(MOD)["blocks"]]
    moved[0] = {**moved[0], "atom_ids": []}
    moved[0]["format"] = "narrative"
    moved[0]["moves"] = "plants the photo in Müller's jacket"
    moved[3] = {**moved[3], "atom_ids": [ids[4], ids[3]]}
    pv2 = L.replan_preview(MOD, moved)
    check("re-homing a made episode's atom marks it STALE, not deleted",
          pv2["made_but_now_stale"] == [1], str(pv2["made_but_now_stale"]))
    check("the preview says made work is never overwritten",
          "never deleted or overwritten" in pv2["note"])

    # ── 5 · narrative episodes ──
    print("\n[5] narrative episodes")
    narr = [dict(b) for b in L.load(MOD)["blocks"]]
    narr[2] = {**narr[2], "format": "narrative", "atom_ids": [], "moves": ""}
    r = S.validate_lesson_v4({**L.load(MOD), "blocks": narr}, cur)
    check("a narrative block with no story job → BLOCK",
          any("must declare what it MOVES" in b for b in r["blocks"]))
    narr[2]["moves"] = "Rolf and Kati acknowledge each other for the first time"
    r = S.validate_lesson_v4({**L.load(MOD), "blocks": narr}, cur)
    check("with a job declared, it validates", r["blocks"] == [], str(r["blocks"][:1]))

    # ── 6 · Season 0 needs no special case ──
    print("\n[6] Season 0")
    s0 = L.create("S0")
    check("Season 0 scaffolds with zero topics", s0["topics"] == [])
    s0["blocks"] = [dict(episode_no=i + 1, atom_ids=[], recycles=[],
                         working_title=f"Arrival {i + 1}", shape="portal → Germany",
                         moves=f"establishes character {i + 1} in the world",
                         format="season_zero", episode_id="", state="planned")
                    for i in range(4)]
    s0.update(why="The arrivals.", lead="—", world="four worlds, then Germany",
              through_line="Each arrives alone.")
    L.save(s0)
    check("Season 0 validates as an ordinary lesson",
          S.validate_lesson_v4(s0, {"modules": [{"id": "S0", "atoms": []}]})["blocks"] == [])

    # ── 7 · the context blocks agents actually receive ──
    print("\n[7] agent context")
    blk = L.plan_block(MOD)
    check("plan block states the progress", "3 of 4 episodes" in blk)
    check("plan block carries the through-line", "Rolf tests" in blk)
    check("plan block shows each block's format and atoms", "[lesson/made]" in blk)
    sib = L.siblings_block(MOD, 2, lambda eid: {"title_de": "Bei Rot", "segments": [
        {"shots": [{"action": "Müller stops dead at the empty crossing"}]}]})
    check("earlier episodes appear as FACTS", "EARLIER IN THIS LESSON" in sib
          and "locked" in sib)
    check("later episodes appear as INTENTION", "LATER IN THIS LESSON" in sib
          and "still movable" in sib)
    check("the standalone rule is restated in the context",
          "must stand alone" in sib)
    check("siblings are summaries, not transcripts", "Müller stops dead" in sib
          and len(sib) < 900, f"{len(sib)} chars")

    cleanup()
    print(f"\n{'=' * 60}\n{len(PASS)} passed · {len(FAIL)} failed")
    for f in FAIL:
        print(f"  ✗ {f}")
    return 1 if FAIL else 0


def _raises(fn):
    try:
        fn()
        return False
    except Exception:
        return True


if __name__ == "__main__":
    sys.exit(main())

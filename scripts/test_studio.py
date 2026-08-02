#!/usr/bin/env python3
"""Studio shell test — the thread, the gates, the modes, and the view compiler.

    .venv/bin/python scripts/test_studio.py

The view compiler is the piece most worth testing: it is the anti-role-bleed
mechanism, and a bug there is invisible in output but poisons every agent.
No LLM calls, no spend — this exercises the shell only.
"""

import shutil
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from pipeline import studio as S  # noqa: E402

EP = "ep___studio_test__"
PASS, FAIL = [], []


def check(name, cond, detail=""):
    (PASS if cond else FAIL).append(name)
    print(f"  {'✓' if cond else '✗'} {name}" + (f"  — {detail}" if detail else ""))
    return cond


def cleanup():
    shutil.rmtree(S.EPISODES / EP, ignore_errors=True)


def main():
    cleanup()
    print("STUDIO SHELL TEST — thread · gates · modes · view compiler")

    # ── 1 · thread + approved defaults ──
    print("\n[1] thread + D8 defaults")
    t = S.Thread.create(EP)
    check("thread created at phase 'idea'", t.phase == "idea")
    check("Script defaults to Co-create", t.mode("script") == S.CO_CREATE)
    check("Vision/Shoot/Post default to Draft",
          all(t.mode(p) == S.DRAFT for p in ("vision", "shoot", "post")))
    check("auto-reroll defaults to 0 (no surprise spend)",
          t.data["settings"]["auto_reroll_on_technical_failure"] == 0)
    check("reloads from disk", S.Thread.load(EP).phase == "idea")

    # ── 2 · gates are human, and refuse to be rushed ──
    print("\n[2] the gate")
    st = S.gate_status(t)
    check("gate names itself correctly", st["gate"] == "brief lock")
    check("cannot approve a phase with no artifact", not st["can_approve"])
    try:
        S.approve(t)
        check("approving with no artifact raises", False)
    except S.StudioError as e:
        check("approving with no artifact raises", True, str(e)[:44])

    # real conversation in the Idea phase, so compaction has something to compact
    t.human("something about a crossing at 3am")
    t.agent("Which lesson — A1.8.4 'man darf … nicht' fits that exactly.")
    t.human("yes, that one")

    (S.EPISODES / EP / "brief.json").write_text('{"title_de":"Bei Rot"}', encoding="utf-8")
    t.qc(blocks=["A1: 41 words over the 30-word ceiling"], flags=[])
    try:
        S.approve(t)
        check("a hard QC block prevents approval", False)
    except S.StudioError as e:
        check("a hard QC block prevents approval", True, str(e)[:44])

    t.qc(blocks=[], flags=["target structure appears only once"])
    st = S.gate_status(t)
    check("a FLAG does not block approval", st["can_approve"])
    res = S.approve(t, note="good, ship it")
    check("approval advances to the next phase", res["now"] == "script")
    check("flags are carried into the record, never laundered",
          res["flags_carried"] == ["target structure appears only once"])
    check("the locked phase stays locked", t.data["gates"]["idea"]["state"] == "locked")

    # ── 3 · rejection is bounded ──
    print("\n[3] rejection")
    (S.EPISODES / EP / "screenplay.json").write_text("{}", encoding="utf-8")
    try:
        S.reject(t, "  ")
        check("an empty rejection raises ('no' is not a constraint)", False)
    except S.StudioError:
        check("an empty rejection raises ('no' is not a constraint)", True)
    r1 = S.reject(t, "the button should land on Müller")
    r2 = S.reject(t, "still not landing")
    r3 = S.reject(t, "again")
    check("redrafts are counted", r1["redraft"] == 1 and r2["redraft"] == 2)
    check("past the budget the agent must ASK, not loop", r3["must_ask_instead"])

    # ── 4 · draft mode: journal + assumptions ──
    print("\n[4] draft mode")
    t.set_mode("script", S.DRAFT)
    check("mode switches mid-episode", t.mode("script") == S.DRAFT)
    t.journal("Lead: Müller das Brot",
              "coldest in rotation; the Pfand situation fits his thrift",
              considered=["Rolf die Wurst — led A1.8.2 two episodes ago"],
              assumption="assumed the bakery is the one from A1.6")
    t.journal("Segment 2 at dusk", "the tonal mode shifts with the story beat")
    check("journal entries are recorded",
          sum(1 for m in t.messages if m["kind"] == "journal") == 2)
    check("an assumption rides to the gate instead of parking the episode",
          S.gate_status(t)["open_questions"] == ["assumed the bakery is the one from A1.6"])

    sp = S.system_prompt(t, "SKILL TEXT HERE",
                         data_blocks={"curriculum slice": "A1.8.4 · man darf … nicht"})
    check("draft prompt demands a journal", "JOURNAL entry" in sp)
    check("draft prompt demands assumptions be recorded", "ASSUMPTION" in sp)
    check("both modes are told the creator approves, not them",
          "You never approve it" in sp)
    check("data blocks ride after canon, never mixed in", "# CURRICULUM SLICE" in sp)
    t.set_mode("script", S.CO_CREATE)
    check("co-create prompt asks for conversation, not a finished artifact",
          "do not write it alone" in S.system_prompt(t, "X"))

    # ── 5 · THE VIEW COMPILER (anti-role-bleed) ──
    print("\n[5] view compiler")
    t.human("make the ending quieter")
    t.agent("Quieter how — fewer words, or a longer hold?")
    # a neighbouring agent's chatter, which must never reach the Writer
    t.append("assistant", "director", phase="vision", kind="chat",
             content="DIRECTOR CHATTER: panel 2 needs a tighter lens")
    view = S.compile_view(t)
    blob = "\n".join(m["content"] for m in view)

    check("the human's turns survive", "make the ending quieter" in blob)
    check("the acting agent's own turns survive", "Quieter how" in blob)
    check("ANOTHER agent's chatter is dropped (role bleed)",
          "DIRECTOR CHATTER" not in blob)
    check("a locked upstream phase appears as [APPROVED …], not as transcript",
          "[APPROVED IDEA]" in blob and "brief.json is locked" in blob)
    check("the locked phase's conversation is compacted to a digest",
          "[IDEA LOCKED" in blob and "3 turns" in blob)
    check("the locked phase's raw turns are gone",
          "something about a crossing at 3am" not in blob)
    check("the creator's note on approval rides forward (it is a human instruction)",
          "good, ship it" in blob)
    check("QC from another phase is not shown", "QC blocked" not in blob)
    check("every projected message is a valid chat role",
          all(m["role"] in ("system", "user", "assistant") for m in view))

    for _ in range(30):
        t.human("more notes")
    windowed = S.compile_view(t, window=6)
    convo = [m for m in windowed if m["role"] in ("user", "assistant")]
    check("the working window bounds the conversational tail", len(convo) <= 6,
          f"{len(convo)} turns")
    check("system declarations survive windowing",
          any("[APPROVED IDEA]" in m["content"] for m in windowed))

    # ── 6 · reopening shows its blast radius ──
    print("\n[6] reopen + recompile set")
    check("the graph knows what a reopen invalidates",
          S.recompile_set("script") == ["vision", "shoot", "post"])
    (S.EPISODES / EP / "screenplay.json").write_text('{"ok":1}', encoding="utf-8")
    t.qc(blocks=[], flags=[])
    S.approve(t)
    check("advanced to vision", t.phase == "vision")
    rr = S.reopen(t, "idea", reason="wrong lesson")
    check("reopening an upstream phase invalidates what followed",
          rr["invalidated"] == ["script"], str(rr))
    check("reopen returns you to that phase", t.phase == "idea")
    check("the invalidated phase is open again",
          t.data["gates"]["script"]["state"] == "open")

    # ── 7 · overview ──
    print("\n[7] overview")
    ov = S.overview(t)
    check("overview reports all five gates", len(ov["gates"]) == 5)
    check("overview carries the modes", ov["modes"]["vision"] == S.DRAFT)
    check("episode is listable", any(e["episode_id"] == EP for e in S.list_episodes()))

    cleanup()
    print(f"\n{'=' * 60}\n{len(PASS)} passed · {len(FAIL)} failed")
    for f in FAIL:
        print(f"  ✗ {f}")
    return 1 if FAIL else 0


if __name__ == "__main__":
    sys.exit(main())

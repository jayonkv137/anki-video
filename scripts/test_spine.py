#!/usr/bin/env python3
"""Spine integration test — exercises the V4 modules against REAL infrastructure.

    .venv/bin/python scripts/test_spine.py [--live-llm]

Unit self-tests (schemas, canon-audit) prove a module agrees with itself. This
proves the modules agree with each other and with Supabase/Gemini: state writes
land and read back, curriculum status derives from the progression log, rotation
reflects real appearances, constraints inject, contradiction checks halt, and the
whole brief→screenplay contract validates on data shaped like a real episode.

Everything it writes is namespaced `__spine_test__` and deleted at the end, so it
is safe to run against the live project. --live-llm adds two paid Gemini calls
(~$0.001) that prove schema enforcement and loud failure end-to-end.
"""

import argparse
import json
import sys
import uuid
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from pipeline import context as ctx          # noqa: E402
from pipeline import ledger                  # noqa: E402
from pipeline import schemas as S            # noqa: E402
from pipeline import subtitles               # noqa: E402
from pipeline import universe_state as st    # noqa: E402

TAG = "__spine_test__"
PASS, FAIL = [], []


def check(name, cond, detail=""):
    (PASS if cond else FAIL).append(name)
    print(f"  {'✓' if cond else '✗'} {name}" + (f"  — {detail}" if detail else ""))
    return cond


def cleanup():
    for table, col in ((st.WORLD, "entity_key"), (st.PROGRESSION, "episode_ref"),
                       (st.DECISIONS, "source")):
        try:
            ledger._delete(table, {col: f"like.{TAG}*"})
        except Exception as e:
            print(f"  (cleanup {table}: {e})")


# ── 1 · Canon + curriculum reachable and coherent ────────────────

def test_canon():
    print("\n[1] canon + curriculum")
    cur = ctx.curriculum()
    check("curriculum loads, 164 atoms", cur["meta"]["totals"]["atoms"] == 164)
    check("module lookup", ctx.module("A1.8")["title"] == "Regeln")
    check("atom lookup", ctx.atom("A1.8.4") is not None)
    check("unknown atom returns None", ctx.atom("Z9.9.9") is None)
    check("guardrails match PEDAGOGY", ctx.guardrails("A1")["max_words"] == 30)
    for phase in ctx.PHASES:
        c = ctx.canon_context(phase)
        if not check(f"phase '{phase}' assembles context", len(c) > 5000,
                     f"{ctx.estimate_tokens(c)} tok"):
            break
    check("QC is never given TREATMENT", "TREATMENT" not in ctx.PHASE_CANON["qc"])
    check("Writer IS given TREATMENT whole",
          "## 15 · PROMPT ASSEMBLY" in ctx.doc_for_phase("script", "TREATMENT"))


# ── 2 · State: real writes, real reads ───────────────────────────

def test_state():
    print("\n[2] UNIVERSE_STATE (live Supabase)")
    ready = st.tables_ready()
    if not check("all three strata tables exist", all(ready.values()), str(ready)):
        return False
    ep = f"{TAG}_{uuid.uuid4().hex[:6]}"

    # stratum 2 — upsert semantics
    st.put_entity("location", f"{TAG}_crossing", {"desc": "empty crossing", "v": 1})
    st.put_entity("location", f"{TAG}_crossing", {"desc": "empty crossing", "v": 2})
    got = st.get_entity("location", f"{TAG}_crossing")
    check("entity write + read back", got is not None)
    check("entity UPDATES rather than duplicating", (got or {}).get("data", {}).get("v") == 2)

    key = st.relationship_key("Müller das Brot", "Rolf die Wurst")
    check("relationship key is order-independent",
          key == st.relationship_key("Rolf die Wurst", "Müller das Brot"))

    # stratum 3 + derived stratum 5
    before = st.curriculum_status()
    st.log("atom_taught", ref="A1.8.4", episode_ref=ep, detail={"module_id": "A1.8"})
    st.log("appearance", ref="Rolf die Wurst", episode_ref=ep)
    after = st.curriculum_status()
    check("curriculum status DERIVES from the progression log",
          after["taught_atoms"] == before["taught_atoms"] + 1,
          f"{before['taught_atoms']} → {after['taught_atoms']}")
    check("taught_atoms maps atom → episodes", ep in st.taught_atoms().get("A1.8.4", []))
    check("rotation sees the appearance", st.rotation_report()["counts"]["Rolf die Wurst"] >= 1)
    check("least-recent-first excludes who just appeared",
          st.rotation_report()["least_recent_first"][0] != "Rolf die Wurst")

    # stratum 4 — the constraint actually injects
    st.add_decision("rejection", f"{TAG} never open on an establishing wide",
                    scope="global", source=ep)
    block = st.constraints_block()
    check("rejection becomes an injectable NEVER", f"NEVER" in block and TAG in block)

    # contradiction check halts rather than overwriting
    st.establish_fact(f"{TAG}_bakery_city", "Hamburg", episode_ref=ep)
    ok = st.check_contradiction(f"{TAG}_bakery_city", "Hamburg")["ok"]
    dup = st.check_contradiction(f"{TAG}_bakery_city", "München")
    check("re-asserting the same fact is fine", ok)
    check("a contradicting fact is caught", not dup["ok"], dup.get("message", "")[:60])
    raised = False
    try:
        st.establish_fact(f"{TAG}_bakery_city", "München", episode_ref=ep)
    except st.StateError:
        raised = True
    check("contradicting write RAISES without confirmation", raised)
    st.establish_fact(f"{TAG}_bakery_city", "München", episode_ref=ep, confirmed=True)
    check("confirmed override succeeds",
          st.get_entity("canon_fact", f"{TAG}_bakery_city")["data"]["value"] == "München")

    # finalize is idempotent
    sp = _screenplay()
    sp["atom_ids"] = ["A1.8.4"]
    r1 = st.finalize_episode(ep, sp)
    r2 = st.finalize_episode(ep, sp)
    check("finalize is idempotent (a retry writes nothing twice)",
          len(r2["written"]) == 0, f"first={len(r1['written'])} second={len(r2['written'])}")
    return True


# ── 3 · Schemas against realistic data ───────────────────────────

def _shot(n, dur, **over):
    base = dict(shot_number=n, duration_s=dur, shot_size="MS", camera_angle="eye-level",
                camera_move="static, locked-off, subtle handheld breathing",
                depth_of_field="deep", action="Rolf die Wurst waits at the crossing",
                blocking="Rolf die Wurst centre midground", gaze="at the red light",
                expression="flat disbelief", light_source="sodium street lamp camera-left",
                light_ratio="70:30", atmosphere="haze", atmosphere_density="light",
                props=[], contact_shot=False, needs_blocking_reference=False,
                negative_prompt="", revision_prompt="hold frame, re-render", dialogue=[])
    base.update(over)
    return base


def _screenplay():
    return dict(
        title_de="Bei Rot", format="lesson", module_id="A1.8", block_no=1,
        atom_ids=["A1.8.4"], recycled_atom_ids=[], cefr_level="A1",
        target_structure="man darf … nicht", total_duration_s=30,
        environment="empty pedestrian crossing, 3 a.m.",
        target_vocab=[{"german": "die Ampel", "english": "traffic light", "gender": "die"}],
        segments=[
            dict(segment_number=1, duration_s=15, time_and_weather="night, dry",
                 tonal_mode="Sodium Street Night",
                 shots=[_shot(1, 8, dialogue=[{"speaker": "Rolf die Wurst",
                                               "german": "Die Ampel ist rot.",
                                               "english": "The traffic light is red."}]),
                        _shot(2, 7, dialogue=[{"speaker": "Rolf die Wurst",
                                               "german": "Man darf hier nicht gehen.",
                                               "english": "You may not walk here."}])]),
            dict(segment_number=2, duration_s=15, time_and_weather="night, dry",
                 tonal_mode="Sodium Street Night", shots=[_shot(1, 15)]),
        ])


def test_schemas():
    print("\n[3] schemas v4 against realistic data")
    cur = ctx.curriculum()
    sp = _screenplay()
    r = S.validate_screenplay_v4(sp, cur)
    check("a clean screenplay passes", r["blocks"] == [] and r["flags"] == [], str(r))

    # the whole 30s shape holds together
    total = sum(s["duration_s"] for s in sp["segments"])
    check("30s = 2 × 15s segments", total == 30 and len(sp["segments"]) == 2)
    for seg in sp["segments"]:
        check(f"segment {seg['segment_number']} shots sum to its 15s",
              sum(sh["duration_s"] for sh in seg["shots"]) == seg["duration_s"])

    # every HARD canon rule blocks
    cases = {
        "TREATMENT §5 mood word as ratio": ("light_ratio", "moody"),
        "TREATMENT §3.1 DOF outside its set": ("depth_of_field", "cinematic"),
        "TREATMENT §8.1 atmosphere outside its set": ("atmosphere", "vibes"),
        "TREATMENT §1 banned medium in a screenplay": ("action", "the puppet waits"),
    }
    for label, (field, val) in cases.items():
        bad = json.loads(json.dumps(sp))
        bad["segments"][0]["shots"][0][field] = val
        check(f"blocks: {label}", S.validate_screenplay_v4(bad, cur)["blocks"] != [])

    bad = json.loads(json.dumps(sp))
    bad["segments"][0]["shots"][1]["atmosphere"] = "fog"
    check("blocks: atmosphere mixed inside one segment (TREATMENT §8.1)",
          any("mixed atmosphere" in b for b in S.validate_screenplay_v4(bad, cur)["blocks"]))

    bad = json.loads(json.dumps(sp))
    bad["segments"][1]["tonal_mode"] = ""
    check("blocks: segment without a tonal mode (TREATMENT §6.5)",
          any("tonal_mode" in b for b in S.validate_screenplay_v4(bad, cur)["blocks"]))

    bad = json.loads(json.dumps(sp))
    bad["segments"][0]["shots"][1]["dialogue"][0]["german"] = " ".join(["Wort"] * 40)
    r = S.validate_screenplay_v4(bad, cur)
    check("blocks: A1 word + sentence ceilings (PEDAGOGY §2)",
          sum("over the" in b for b in r["blocks"]) >= 2)

    bad = json.loads(json.dumps(sp))
    bad["atom_ids"] = ["B1.6.3"]
    check("blocks: an atom above the declared level",
          any("above the declared level" in b for b in S.validate_screenplay_v4(bad, cur)["blocks"]))

    dense = json.loads(json.dumps(sp))
    dense["segments"][0]["shots"] = [_shot(i + 1, 2, dialogue=[{"speaker": "Rolf die Wurst",
                                     "german": "Ja.", "english": "Yes."}]) for i in range(8)]
    r = S.validate_screenplay_v4(dense, cur)
    check("FLAGS (never blocks) an over-dense segment — TREATMENT §8.3",
          any("too dense" in f for f in r["flags"]) and
          not any("too dense" in b for b in r["blocks"]))

    # brief ↔ screenplay agree on the curriculum
    brief = dict(title_de="Bei Rot", format="lesson", module_id="A1.8", block_no=1,
                 atom_ids=["A1.8.4"], recycled_atom_ids=[], cefr_level="A1",
                 lead="Rolf die Wurst", cast=["Rolf die Wurst"],
                 location="empty crossing", premise="p",
                 beats=["base", "unusual", "escalation"], button="he waits anyway",
                 target_structure="man darf … nicht",
                 target_line={"speaker": "Rolf die Wurst", "german": "Man darf hier nicht gehen.",
                              "english": "x", "why": "the lesson"},
                 encounter={"stereotype_id": "001", "name": "Bei Rot bleibt man stehen!",
                            "mode": "host"},
                 new_vocab=[], banned_terms=["bei rot bleibt man stehen!"], director_notes=[])
    check("a clean brief passes", S.validate_brief_v4(brief, cur)["blocks"] == [])
    check("blocks: synthese declaring NEW atoms",
          S.validate_brief_v4({**brief, "format": "synthese"}, cur)["blocks"] != [])
    check("blocks: a lead who is not in the cast",
          S.validate_brief_v4({**brief, "lead": "Bert das Bier"}, cur)["blocks"] != [])


# ── 4 · Subtitles: the 30s shape end to end ──────────────────────

def test_subtitles():
    print("\n[4] subtitle engine (PEDAGOGY §5)")
    sp = _screenplay()
    state = subtitles.build_subtitle_state(sp, [15.0, 15.0])
    cues = state["subtitles"]
    check("cues built from the screenplay", len(cues) >= 2, f"{len(cues)} cues")
    check("30s at 30fps = 900 frames", state["composition"]["durationInFrames"] == 900)
    check("colours are PEDAGOGY §5.3", state["colors"]["das"] == "#10B981"
          and state["colors"]["grammar"] == "#F59E0B")
    ass = subtitles.render_ass(state)
    check("render emits colour tags", "\\c&H" in ass)
    check("render emits NO karaoke reveal (PEDAGOGY §5.2)", "\\k" not in ass)
    check("cues sit in the safe zone (TREATMENT §7)", f"\\pos(540,1150)" in ass)
    inside = all(0 <= c["startFrame"] < c["endFrame"] <= 900 for c in cues)
    check("every cue lies inside the episode", inside)
    # der/die/das colouring actually fires off target_vocab appearing in dialogue
    labels = {w["colorLabel"] for c in cues for w in c["words"]}
    check("gender colour-coding fires on a spoken target word", "die" in labels, str(labels))

    # the new guard: declaring vocabulary you never speak
    sp_unspoken = _screenplay()
    sp_unspoken["target_vocab"] = [{"german": "der Zebrastreifen",
                                    "english": "crossing", "gender": "der"}]
    r = S.validate_screenplay_v4(sp_unspoken, ctx.curriculum())
    check("FLAGS target_vocab that is never spoken (PEDAGOGY §8.3)",
          any("never appears" in f for f in r["flags"]))


# ── 5 · LLM layer (optional, paid) ───────────────────────────────

def test_llm():
    print("\n[5] LLM gateway (live Gemini)")
    from pipeline import llm
    Sch = S._schema(module_id=S.STR, atoms=S._arr(S.STR))
    data, usage = llm.call_json(
        "You are a curriculum assistant. Obey the schema exactly.",
        "Return module_id 'A1.8' and the atom ids ['A1.8.4'].",
        Sch, label="spine", temperature=0.0)
    check("schema-enforced call returns the exact shape",
          set(data) == {"module_id", "atoms"}, json.dumps(data))
    check("usage is reported honestly", usage["tokens_in"] > 0 and "model" in usage)

    raised = False
    try:
        llm.call_json("Obey the schema.", "Give a module id.", S._schema(module_id=S.STR),
                      label="spine-fail", temperature=0.0,
                      validate=lambda d: ["module_id must equal IMPOSSIBLE-XYZ"])
    except llm.LLMError:
        raised = True
    check("an unsatisfiable validator RAISES (never invents)", raised)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--live-llm", action="store_true", help="include two paid Gemini calls")
    args = ap.parse_args()
    print("SPINE INTEGRATION TEST — real Supabase, real canon, real curriculum")
    try:
        test_canon()
        state_ok = test_state()
        test_schemas()
        test_subtitles()
        if args.live_llm:
            test_llm()
        elif state_ok:
            print("\n[5] LLM gateway — skipped (pass --live-llm to include it)")
    finally:
        print("\ncleaning up test rows…")
        cleanup()
    print(f"\n{'=' * 60}\n{len(PASS)} passed · {len(FAIL)} failed")
    if FAIL:
        for f in FAIL:
            print(f"  ✗ {f}")
    return 1 if FAIL else 0


if __name__ == "__main__":
    sys.exit(main())

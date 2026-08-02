#!/usr/bin/env python3
"""Studio API test — every endpoint, against the real app + real Supabase.

    .venv/bin/python scripts/test_studio_api.py

Uses FastAPI's TestClient, so no server needs to be running. Namespaced and
self-cleaning. No LLM calls, no generation, no spend.
"""

import shutil
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from fastapi.testclient import TestClient  # noqa: E402

from dashboard.app import app  # noqa: E402
from pipeline import studio as S  # noqa: E402

EP = "ep___api_test__"
c = TestClient(app)
PASS, FAIL = [], []


def check(name, cond, detail=""):
    (PASS if cond else FAIL).append(name)
    print(f"  {'✓' if cond else '✗'} {name}" + (f"  — {detail}" if detail else ""))
    return cond


def cleanup():
    shutil.rmtree(S.EPISODES / EP, ignore_errors=True)


def main():
    cleanup()
    print("STUDIO API TEST — real app, real state")

    print("\n[1] health + curriculum")
    h = c.get("/api/studio/health").json()
    check("health reports canon + curriculum", h["curriculum_atoms"] == 164)
    check("health reports state readiness", h["state_ready"] is True, str(h["state_tables"]))
    check("health is honest that agents are not built", h["agents_built"] is False)
    cur = c.get("/api/studio/curriculum").json()
    check("curriculum returns 30 modules", len(cur["modules"]) == 30)
    check("every atom carries a taught flag",
          all("taught" in a for m in cur["modules"] for a in m["atoms"]))

    nl = c.get("/api/studio/next-lesson").json()
    check("next-lesson names the next module", bool(nl.get("module", {}).get("id")),
          nl.get("module", {}).get("id", "?"))
    check("next-lesson recommends a lead from rotation",
          nl["lead_recommendation"]["character"] is not None,
          nl["lead_recommendation"]["character"] or "")
    check("next-lesson carries the level ceilings", nl["guardrails"]["max_words"] in (30, 55, 80))

    print("\n[2] episode lifecycle")
    r = c.post("/api/studio/episodes", json={"episode_id": EP})
    check("create returns 200", r.status_code == 200, str(r.status_code))
    ov = r.json()
    check("starts at idea", ov["phase"] == "idea")
    check("D8 defaults applied",
          ov["modes"]["script"] == "co_create" and ov["modes"]["vision"] == "draft")
    check("duplicate create is refused (409)",
          c.post("/api/studio/episodes", json={"episode_id": EP}).status_code == 409)
    check("episode is listed", any(e["episode_id"] == EP
                                   for e in c.get("/api/studio/episodes").json()))
    check("unknown episode is 404",
          c.get("/api/studio/episodes/ep_nope").status_code == 404)

    print("\n[3] conversation + modes")
    check("empty message refused",
          c.post(f"/api/studio/episodes/{EP}/message", json={"content": " "}).status_code == 400)
    c.post(f"/api/studio/episodes/{EP}/message", json={"content": "empty crossing at 3am"})
    th = c.get(f"/api/studio/episodes/{EP}/thread").json()
    check("human turn recorded",
          any(m["content"] == "empty crossing at 3am" for m in th["messages"]))
    check("mode switch works",
          c.post(f"/api/studio/episodes/{EP}/mode",
                 json={"phase": "script", "mode": "draft"}).json()["modes"]["script"] == "draft")
    check("bogus mode refused (409)",
          c.post(f"/api/studio/episodes/{EP}/mode",
                 json={"phase": "script", "mode": "yolo"}).status_code == 409)

    print("\n[4] the gate is human and refuses to be rushed")
    g = c.get(f"/api/studio/episodes/{EP}/gate").json()
    check("gate names itself", g["gate"] == "brief lock")
    check("cannot approve without an artifact", not g["can_approve"])
    check("approving without an artifact is 409",
          c.post(f"/api/studio/episodes/{EP}/approve", json={}).status_code == 409)

    (S.EPISODES / EP / "brief.json").write_text('{"title_de":"Bei Rot"}', encoding="utf-8")
    t = S.Thread.load(EP)
    t.qc(blocks=["A1: 41 words over the ceiling"], flags=[])
    check("a hard block still refuses approval",
          c.post(f"/api/studio/episodes/{EP}/approve", json={}).status_code == 409)
    t = S.Thread.load(EP)
    t.qc(blocks=[], flags=["target structure appears once"])
    r = c.post(f"/api/studio/episodes/{EP}/approve", json={"note": "ship it"}).json()
    check("approval advances the phase", r["now"] == "script")
    check("flags are carried, not laundered", r["flags_carried"] == ["target structure appears once"])

    print("\n[5] rejection")
    (S.EPISODES / EP / "screenplay.json").write_text("{}", encoding="utf-8")
    check("empty rejection refused (409)",
          c.post(f"/api/studio/episodes/{EP}/reject", json={"note": ""}).status_code == 409)
    rj = c.post(f"/api/studio/episodes/{EP}/reject",
                json={"note": "button should land on Müller"}).json()
    check("redraft counted", rj["redraft"] == 1)

    print("\n[6] the money rule")
    cp = c.get(f"/api/studio/episodes/{EP}/cost-preview").json()
    check("script phase costs nothing", cp["estimate_usd"] == 0.0)
    S.Thread.load(EP)  # advance to vision to price the sheets
    t = S.Thread.load(EP)
    t.qc(blocks=[], flags=[])
    c.post(f"/api/studio/episodes/{EP}/approve", json={})
    cp = c.get(f"/api/studio/episodes/{EP}/cost-preview").json()
    check("vision quotes a real, verified sheet price",
          cp["verified"] is True and cp["estimate_usd"] > 0, f"${cp['estimate_usd']}")
    check("cost preview names the unit", "sheet" in (cp["unit"] or ""))

    print("\n[7] reopen shows its blast radius FIRST")
    pv = c.get(f"/api/studio/episodes/{EP}/recompile/idea").json()
    check("recompile preview is a READ (no state change)",
          c.get(f"/api/studio/episodes/{EP}").json()["gates"]["idea"]["state"] == "locked")
    check("it names what becomes stale", pv["invalidates"] == ["script"], str(pv["invalidates"]))
    check("it names the artifacts to rebuild", "screenplay.json" in pv["artifacts_rebuilt"])
    ro = c.post(f"/api/studio/episodes/{EP}/reopen",
                json={"phase": "idea", "reason": "wrong lesson"}).json()
    check("reopen invalidates downstream", ro["invalidated"] == ["script"])
    check("reopen returns to that phase", ro["overview"]["phase"] == "idea")

    print("\n[8] the compiled agent view is inspectable")
    v = c.get(f"/api/studio/episodes/{EP}/view").json()["view"]
    check("view is a valid message array",
          all(m["role"] in ("system", "user", "assistant") for m in v))
    check("the human's turn survives the projection",
          any("empty crossing at 3am" in m["content"] for m in v))

    print("\n[9] seed bank")
    s = c.post("/api/studio/seeds", json={"text": "__api_test__ nobody crosses at 3am"}).json()
    check("seed added", bool(s["key"]))
    seeds = c.get("/api/studio/seeds").json()
    check("seed listed and unused",
          any(x["key"] == s["key"] and not x["used"] for x in seeds))
    c.post(f"/api/studio/seeds/{s['key']}/consume", params={"episode_id": EP})
    seeds = c.get("/api/studio/seeds").json()
    check("seed marked consumed",
          any(x["key"] == s["key"] and x["used_by"] == EP for x in seeds))
    from pipeline import ledger
    ledger._delete("universe_world", {"entity_key": f"eq.{s['key']}"})

    cleanup()
    print(f"\n{'=' * 60}\n{len(PASS)} passed · {len(FAIL)} failed")
    for f in FAIL:
        print(f"  ✗ {f}")
    return 1 if FAIL else 0


if __name__ == "__main__":
    sys.exit(main())

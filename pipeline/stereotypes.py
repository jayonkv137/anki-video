"""Stereotypes library — the tracked content backbone (100 German micro-behaviors).

Data lives in `resources/stereotypes_library.json` (ingested from the Excel via
`scripts/ingest_stereotypes.py`). This module is the read/write API the co-creation
studio + pipeline use to surface a daily pick and record coverage.

The daily-pick contract (VISION_v3 §4 step 2): `pick_options(3)` returns 3 random
UNCOVERED stereotypes for the human to choose from; `mark_covered(id, episode_id)`
logs one as done so it won't be offered again.
"""
import json
import random
import datetime
from pathlib import Path

from .rcp import REPO

LIBRARY = REPO / "resources" / "stereotypes_library.json"


def _load() -> dict:
    return json.loads(LIBRARY.read_text(encoding="utf-8"))


def _save(doc: dict) -> None:
    LIBRARY.write_text(json.dumps(doc, ensure_ascii=False, indent=2), encoding="utf-8")


def all_stereotypes() -> list[dict]:
    return _load().get("stereotypes", [])


def get(sid) -> dict | None:
    return next((s for s in all_stereotypes() if s["id"] == str(sid)), None)


def categories() -> list[str]:
    return sorted({s["category"] for s in all_stereotypes()})


def pick_options(n: int = 3, seed=None, category: str | None = None) -> list[dict]:
    """Surface n random UNCOVERED stereotypes for the daily Gate-A pick.
    `seed` makes a pick reproducible; `category` optionally constrains the pool."""
    pool = [s for s in all_stereotypes() if s.get("status") != "covered"]
    if category:
        pool = [s for s in pool if s["category"] == category]
    return random.Random(seed).sample(pool, min(n, len(pool)))


def mark_covered(sid, episode_id: str) -> dict | None:
    """Record a stereotype as covered by an episode (so it drops out of the pool)."""
    doc = _load()
    hit = None
    for s in doc["stereotypes"]:
        if s["id"] == str(sid):
            s["status"] = "covered"
            s["episode_id"] = episode_id
            s["covered_at"] = datetime.datetime.now().isoformat(timespec="seconds")
            hit = s
            break
    if hit:
        _save(doc)
    return hit


def coverage_summary() -> dict:
    s = all_stereotypes()
    by_cat: dict[str, dict] = {}
    for x in s:
        c = by_cat.setdefault(x["category"], {"total": 0, "covered": 0})
        c["total"] += 1
        if x.get("status") == "covered":
            c["covered"] += 1
    covered = sum(1 for x in s if x.get("status") == "covered")
    return {"total": len(s), "covered": covered, "uncovered": len(s) - covered,
            "by_category": by_cat}

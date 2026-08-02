"""UNIVERSE_STATE — the cross-episode memory (strata 2–4 in Postgres; 5 derived).

DESIGN_universe_state.md §5 · BUILD_PLAN_v4 §6. Retrieval is **deterministic and
relational** — typed lookups only, never semantic/vector search (a near-miss is
worse than nothing in a consistency system).

  Stratum 1  immutable canon      → files + git (REGISTRY-pinned). Not here.
  Stratum 2  mutable world state  → universe_world      (characters, locations,
                                     relationships, tonal modes, directions, canon facts)
  Stratum 3  progression log      → universe_progression (append-only)
  Stratum 4  decisions/constraints→ universe_decisions   (approvals bind, rejections persist)
  Stratum 5  the plan             → resources/curriculum.json; live status DERIVED
                                     from stratum 3 (one source of truth for "taught")

Write policy: stratum 1 human-only · 2–3 written at gates, contradiction-checked
first · 4 written on explicit human approve/reject. Reads degrade gracefully
(an unreachable ledger must never break a working studio); writes do not — a
silent state write failure would corrupt continuity, so writes raise.
"""

from collections import Counter

from . import context as ctx
from . import ledger

WORLD = "universe_world"
PROGRESSION = "universe_progression"
DECISIONS = "universe_decisions"

ENTITY_TYPES = ("character", "location", "relationship", "tonal_mode",
                "direction", "canon_fact", "world")
PROGRESSION_KINDS = ("episode_made", "atom_taught", "appearance",
                     "story_beat", "stereotype_encounter", "thread")


class StateError(RuntimeError):
    """A state write failed. Continuity is only as good as this layer."""


def _safe_get(table: str, params: dict) -> list[dict]:
    """Reads degrade to empty — the studio still runs, just without memory."""
    try:
        return ledger._get(table, params)
    except Exception as e:
        print(f"[universe_state: read of {table} failed ({e}) — continuing without it]")
        return []


def tables_ready() -> dict:
    """Which strata tables exist (run 002_universe_state.sql if any are False)."""
    out = {}
    for t in (WORLD, PROGRESSION, DECISIONS):
        try:
            ledger._get(t, {"select": "id", "limit": "1"})
            out[t] = True
        except Exception:
            out[t] = False
    return out


# ── Stratum 2 · world ────────────────────────────────────────────

def put_entity(entity_type: str, entity_key: str, data: dict) -> dict:
    if entity_type not in ENTITY_TYPES:
        raise StateError(f"unknown entity_type '{entity_type}' (have: {ENTITY_TYPES})")
    existing = _safe_get(WORLD, {"select": "id", "entity_type": f"eq.{entity_type}",
                                 "entity_key": f"eq.{entity_key}", "limit": "1"})
    try:
        if existing:
            return ledger._patch(WORLD, {"id": f"eq.{existing[0]['id']}"},
                                 {"data": data, "updated_at": "now()"})
        return ledger._post(WORLD, {"entity_type": entity_type,
                                    "entity_key": entity_key, "data": data})
    except Exception as e:
        raise StateError(f"failed to write {entity_type}/{entity_key}: {e}") from e


def get_entity(entity_type: str, entity_key: str) -> dict | None:
    rows = _safe_get(WORLD, {"select": "*", "entity_type": f"eq.{entity_type}",
                             "entity_key": f"eq.{entity_key}", "limit": "1"})
    return rows[0] if rows else None


def list_entities(entity_type: str) -> list[dict]:
    return _safe_get(WORLD, {"select": "*", "entity_type": f"eq.{entity_type}",
                             "order": "entity_key.asc"})


def relationship_key(a: str, b: str) -> str:
    """Order-independent pair key, so A|B and B|A are the same relationship."""
    return "|".join(sorted([a, b]))


# ── Stratum 3 · progression ──────────────────────────────────────

def log(kind: str, *, ref: str = "", episode_ref: str = "", detail: dict | None = None) -> dict:
    if kind not in PROGRESSION_KINDS:
        raise StateError(f"unknown progression kind '{kind}' (have: {PROGRESSION_KINDS})")
    try:
        return ledger._post(PROGRESSION, {"kind": kind, "ref": ref or None,
                                          "episode_ref": episode_ref or None,
                                          "detail": detail or {}})
    except Exception as e:
        raise StateError(f"failed to log {kind}/{ref}: {e}") from e


def progression(kind: str, ref: str | None = None, limit: int = 500) -> list[dict]:
    params = {"select": "*", "kind": f"eq.{kind}",
              "order": "created_at.desc", "limit": str(limit)}
    if ref:
        params["ref"] = f"eq.{ref}"
    return _safe_get(PROGRESSION, params)


# ── Stratum 5 · curriculum status (DERIVED from stratum 3) ───────

def taught_atoms() -> dict[str, list[str]]:
    """atom_id → [episode_refs] that taught it. The single source for 'taught'."""
    out: dict[str, list[str]] = {}
    for row in progression("atom_taught", limit=2000):
        if row.get("ref"):
            out.setdefault(row["ref"], []).append(row.get("episode_ref") or "")
    return out


def curriculum_status() -> dict:
    """Live plan status: totals, per-module counts, and the next untaught module."""
    cur = ctx.curriculum()
    taught = taught_atoms()
    modules = []
    next_module = None
    for m in cur["modules"]:
        ids = [a["id"] for a in m["atoms"]]
        done = [i for i in ids if i in taught]
        complete = len(done) == len(ids)
        modules.append({"id": m["id"], "level": m["level"], "title": m["title"],
                        "atoms": len(ids), "taught": len(done), "complete": complete})
        if next_module is None and not complete:
            next_module = m["id"]
    return {
        "total_atoms": cur["meta"]["totals"]["atoms"],
        "taught_atoms": len(taught),
        "next_module": next_module,
        "modules": modules,
    }


def next_module_brief() -> dict | None:
    """The Showrunner's front door: the next module + its untaught atoms in order."""
    status = curriculum_status()
    mid = status["next_module"]
    if not mid:
        return None
    m = ctx.module(mid)
    taught = taught_atoms()
    return {
        "module": m,
        "level": m["level"],
        "untaught_atoms": [a for a in m["atoms"] if a["id"] not in taught],
        "taught_atoms": [a for a in m["atoms"] if a["id"] in taught],
        "guardrails": ctx.guardrails(m["level"]),
    }


# ── Rotation (SHOW_BIBLE §8 — appearances are a real input) ──────

def appearances(limit: int = 200) -> dict[str, int]:
    return dict(Counter(r["ref"] for r in progression("appearance", limit=limit) if r.get("ref")))


def rotation_report() -> dict:
    """Appearance counts + who has been off screen longest (lead recommendation input)."""
    from .schemas import LEVEL_CEILINGS  # noqa: F401  (keeps roster/schema imports together)
    roster = ["Rolf die Wurst", "Bert das Bier", "Kati die Kartoffel", "Müller das Brot"]
    counts = appearances()
    recent = [r["ref"] for r in progression("appearance", limit=40) if r.get("ref")]
    seen, order = set(), []
    for name in recent:  # newest first
        if name not in seen:
            seen.add(name)
            order.append(name)
    coldest = [n for n in roster if n not in seen] + list(reversed(order))
    return {"counts": {n: counts.get(n, 0) for n in roster},
            "least_recent_first": coldest}


# ── Stratum 4 · decisions & constraints ──────────────────────────

def add_decision(kind: str, rule: str, *, scope: str = "global",
                 scope_key: str = "", source: str = "") -> dict:
    if kind not in ("approval", "rejection", "taste"):
        raise StateError(f"unknown decision kind '{kind}'")
    try:
        return ledger._post(DECISIONS, {"kind": kind, "scope": scope,
                                        "scope_key": scope_key or None, "rule": rule,
                                        "source": source or None, "active": True})
    except Exception as e:
        raise StateError(f"failed to record {kind}: {e}") from e


def active_constraints(scopes: dict | None = None) -> list[dict]:
    """Global constraints + those matching the given {scope: key} pairs.
    These are injected into every generation — this is what makes a rejection stick."""
    rows = _safe_get(DECISIONS, {"select": "*", "active": "eq.true",
                                 "order": "created_at.desc", "limit": "300"})
    keep = []
    for r in rows:
        if r.get("scope") == "global":
            keep.append(r)
        elif scopes and r.get("scope") in scopes:
            wanted = scopes[r["scope"]]
            wanted = wanted if isinstance(wanted, (list, tuple, set)) else [wanted]
            if r.get("scope_key") in wanted:
                keep.append(r)
    return keep


def constraints_block(scopes: dict | None = None) -> str:
    """The active constraints as an injectable block ('settled stays settled')."""
    rows = active_constraints(scopes)
    if not rows:
        return ""
    lines = []
    for r in rows:
        tag = "MUST" if r["kind"] == "approval" else "NEVER" if r["kind"] == "rejection" else "PREFER"
        where = f" [{r['scope']}:{r['scope_key']}]" if r.get("scope_key") else ""
        lines.append(f"- {tag}{where}: {r['rule']}")
    return ("# STANDING DECISIONS (settled — do not reopen)\n"
            "These came from the creator's own approvals and rejections.\n"
            + "\n".join(lines))


# ── Contradiction check (before any canon-fact write) ────────────

def check_contradiction(fact_key: str, fact_value: str) -> dict:
    """Deterministic v1: same key, different value → halt and ask. Never overwrite
    silently (SHOW_BIBLE §15.3). Semantic checking is a later upgrade."""
    existing = get_entity("canon_fact", fact_key)
    if existing and (existing.get("data") or {}).get("value") not in (None, fact_value):
        return {"ok": False, "existing": existing["data"].get("value"),
                "proposed": fact_value,
                "message": (f"'{fact_key}' is already established as "
                            f"\"{existing['data'].get('value')}\" — the episode proposes "
                            f"\"{fact_value}\". A human decides which is right.")}
    return {"ok": True}


def establish_fact(fact_key: str, fact_value: str, *, episode_ref: str = "",
                   confirmed: bool = False) -> dict:
    """Write a canon fact. Requires an explicit human confirmation on contradiction."""
    check = check_contradiction(fact_key, fact_value)
    if not check["ok"] and not confirmed:
        raise StateError(check["message"])
    return put_entity("canon_fact", fact_key,
                      {"value": fact_value, "episode_ref": episode_ref})


# ── Episode finalize (the gate write) ────────────────────────────

def finalize_episode(episode_ref: str, screenplay: dict, *, cast: list[str] | None = None) -> dict:
    """One transactional-ish write at the export gate: episode, atoms taught,
    appearances, the encounter. Idempotent per (episode_ref, kind, ref)."""
    already = {(r.get("kind"), r.get("ref"))
               for r in _safe_get(PROGRESSION, {"select": "kind,ref",
                                                "episode_ref": f"eq.{episode_ref}",
                                                "limit": "500"})}
    written = []

    def _once(kind, ref, detail=None):
        if (kind, ref or None) in already:
            return
        log(kind, ref=ref, episode_ref=episode_ref, detail=detail or {})
        written.append(f"{kind}:{ref}" if ref else kind)

    _once("episode_made", screenplay.get("module_id", ""),
          {"title_de": screenplay.get("title_de"), "format": screenplay.get("format"),
           "block_no": screenplay.get("block_no"),
           "environment": screenplay.get("environment")})
    for aid in screenplay.get("atom_ids", []):
        _once("atom_taught", aid, {"module_id": screenplay.get("module_id")})
    names = cast or sorted({d.get("speaker") for d in
                            [d for seg in screenplay.get("segments", [])
                             for sh in seg.get("shots", [])
                             for d in sh.get("dialogue", [])] if d.get("speaker")})
    for name in names:
        _once("appearance", name)
    return {"episode_ref": episode_ref, "written": written}

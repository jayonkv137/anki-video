"""Context — Tier-1 (hot) canon assembly, per studio phase.

Replaces the blanket RCP inject for the V4 studio: each phase loads ONLY the canon
its stations read (PIPELINE.md §3 read-lists + §7 context scoping) plus its own
station contract extracted from PIPELINE.md — never the whole pipeline map.

Three-tier architecture (BUILD_PLAN_v4 §6 · the context-engineering research):
  Tier 1 (HOT, this module)  — canon documents + the station contract, always inlined.
  Tier 2 (WARM, studio.py)   — the working window of the episode conversation.
  Tier 3 (COLD, studio.py)   — locked phases compacted; artifacts carry the detail.

Legacy note: `rcp.py` remains for the V3 wizard until Phase 3.5. New code only here.
"""

import json
import re
from functools import lru_cache

from .rcp import REPO, verify_canon

# ── The canon surface ────────────────────────────────────────────

CANON_PATHS = {
    "MISSION": "prompts/canon/MISSION.md",
    "SHOW_BIBLE": "prompts/canon/SHOW_BIBLE.md",
    "STORY_SYSTEM": "prompts/canon/STORY_SYSTEM.md",
    "PEDAGOGY": "prompts/canon/PEDAGOGY.md",
    "TREATMENT": "prompts/canon/TREATMENT.md",
    "PIPELINE": "prompts/canon/PIPELINE.md",
    "SEEDANCE": "prompts/canon/prompting_guidelines_seedance.md",
    "NANOBANANA": "prompts/canon/prompting_guidelines_nanobanana.md",
}

# Which canon each phase inlines (PIPELINE §3 read-lists; MISSION always).
# Dynamic data blocks (curriculum slice, UNIVERSE_STATE, stereotype options,
# artifacts) are appended by studio.py per turn — they are data, not canon.
PHASE_CANON = {
    "idea":   ["MISSION", "SHOW_BIBLE", "STORY_SYSTEM", "PEDAGOGY"],
    "script": ["MISSION", "SHOW_BIBLE", "STORY_SYSTEM", "PEDAGOGY", "TREATMENT"],
    "qc":     ["PEDAGOGY", "STORY_SYSTEM", "SHOW_BIBLE"],
    "vision": ["MISSION", "TREATMENT", "NANOBANANA", "SHOW_BIBLE"],
    "shoot":  ["MISSION", "TREATMENT", "SEEDANCE"],
    "post":   ["MISSION", "PEDAGOGY", "TREATMENT"],
}

# Section-level scoping (PIPELINE §7: a station gets the canon it needs, not more).
# PIPELINE §3.4 gives the Writer "TREATMENT (what is filmable)" and forbids it from
# deciding style, colour, lens, grade, reference bindings or prompt syntax — so the
# Writer never sees those sections. The Vision/Shoot compilers get TREATMENT whole.
DOC_SECTIONS = {
    ("script", "TREATMENT"): ["4", "5", "7", "8", "12", "13", "17"],
}

# PIPELINE.md stations each phase owns (§2.1). Every phase also gets §1 (the lock
# principle) and §3.9 (the change protocol — available at every phase by design).
PHASE_STATIONS = {
    "idea":   ["3.1", "3.2", "3.3"],
    "script": ["3.4"],
    "qc":     ["3.5"],
    "vision": ["3.6"],
    "shoot":  ["3.7"],
    "post":   ["3.8"],
}

PHASES = list(PHASE_CANON)


@lru_cache(maxsize=1)
def _canon() -> dict:
    """Verify the registry once, then load every canon text. Hash mismatch aborts."""
    verify_canon()
    return {name: (REPO / path).read_text(encoding="utf-8")
            for name, path in CANON_PATHS.items()}


# ── PIPELINE.md section extraction (station contracts) ──────────

def _pipeline_slice(pattern: str) -> str:
    """Extract one heading's block from PIPELINE.md (from the heading to the next
    same-or-higher-level heading)."""
    text = _canon()["PIPELINE"]
    m = re.search(pattern, text, re.M)
    if not m:
        return ""
    start = m.start()
    nxt = re.search(r"^#{2,3} ", text[m.end():], re.M)
    end = m.end() + nxt.start() if nxt else len(text)
    return text[start:end].strip()


def _doc_sections(name: str, numbers: list[str]) -> str:
    """Extract selected top-level `## N ·` sections from a canon doc, keeping the
    header so the agent knows which document (and which parts of it) it is reading."""
    text = _canon()[name]
    head = text.split("\n## ", 1)[0].strip()
    out = [head]
    for num in numbers:
        m = re.search(rf"^## {re.escape(num)} ·.*$", text, re.M)
        if not m:
            continue
        nxt = re.search(r"^## ", text[m.end():], re.M)
        end = m.end() + nxt.start() if nxt else len(text)
        out.append(text[m.start():end].strip())
    return "\n\n".join(out)


def doc_for_phase(phase: str, name: str) -> str:
    """The canon text this phase sees — whole, or scoped to its read-list sections."""
    sections = DOC_SECTIONS.get((phase, name))
    return _doc_sections(name, sections) if sections else _canon()[name]


def station_contract(phase: str) -> str:
    """The lock principle + this phase's station contracts + the change protocol.
    Deliberately NOT the whole of PIPELINE.md (§7: knowing too much is a failure mode)."""
    parts = [_pipeline_slice(r"^## 1 · THE ONE PRINCIPLE.*$")]
    for num in PHASE_STATIONS[phase]:
        parts.append(_pipeline_slice(rf"^### {re.escape(num)} .*$"))
    if phase != "qc":  # QC never speaks and never edits
        parts.append(_pipeline_slice(r"^### 3\.9 .*$"))
    return "\n\n".join(p for p in parts if p)


# ── Curriculum access ────────────────────────────────────────────

@lru_cache(maxsize=1)
def curriculum() -> dict:
    """The locked plan (resources/curriculum.json, registry-verified via _canon)."""
    _canon()  # ensures verify_canon ran (curriculum.json is registry-pinned)
    return json.loads((REPO / "resources" / "curriculum.json").read_text(encoding="utf-8"))


def guardrails(level: str) -> dict:
    return curriculum()["guardrails"][level.upper()]


def module(module_id: str) -> dict | None:
    return next((m for m in curriculum()["modules"] if m["id"] == module_id), None)


def atom(atom_id: str) -> dict | None:
    for m in curriculum()["modules"]:
        for a in m["atoms"]:
            if a["id"] == atom_id:
                return a
    return None


def module_order() -> list[str]:
    return [m["id"] for m in curriculum()["modules"]]


# ── Assembly + budget ────────────────────────────────────────────

def estimate_tokens(text: str) -> int:
    return (len(text) + 3) // 4  # honest chars/4 estimate (no Gemini tokenizer offline)


def canon_context(phase: str) -> str:
    """The phase's Tier-1 hot block: canon docs in read order + the station contract."""
    if phase not in PHASE_CANON:
        raise ValueError(f"unknown phase '{phase}' (have: {', '.join(PHASES)})")
    blocks = []
    for name in PHASE_CANON[phase]:
        scoped = " (the sections your station reads)" if (phase, name) in DOC_SECTIONS else ""
        blocks.append(f"# CANON — {name}{scoped}\n\n{doc_for_phase(phase, name)}")
    blocks.append(f"# YOUR STATION CONTRACT (from PIPELINE.md — read only this)\n\n"
                  f"{station_contract(phase)}")
    return "\n\n---\n\n".join(blocks)


def budget_report(phase: str, budget_tokens: int = 32000) -> dict:
    """Measure the hot block against the phase budget; warn past 60% (the research
    threshold where static rules start crowding out working context)."""
    ctx = canon_context(phase)
    per_doc = {name: estimate_tokens(doc_for_phase(phase, name))
               for name in PHASE_CANON[phase]}
    total = estimate_tokens(ctx)
    return {
        "phase": phase,
        "per_doc_tokens": per_doc,
        "hot_total_tokens": total,
        "budget_tokens": budget_tokens,
        "hot_share": round(total / budget_tokens, 3),
        "warn": total > 0.6 * budget_tokens,
    }

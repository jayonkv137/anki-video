#!/usr/bin/env python3
"""Build resources/curriculum.json (the LOCKED machine artifact) from
docs/planning/CURRICULUM_v1_universe.md §3.

Idempotent, tracked-asset pattern (same as ingest_stereotypes.py). Re-run after
any curriculum /tune, then re-pin the new hash in prompts/canon/REGISTRY.md.

Validates on every run: 30 modules · 164 atoms · A1=61 · A2=56 · B1=47 ·
unique ids · every atom id prefixed by its module id.

NOTE: the artifact is the IMMUTABLE PLAN (UNIVERSE_STATE stratum 1/5).
Teaching status (planned|taught, taught_in[]) lives in UNIVERSE_STATE (Postgres),
never in this file — locking status into a hash-pinned artifact would force a
canon ritual per episode.
"""

import hashlib
import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SRC = REPO / "docs" / "planning" / "CURRICULUM_v1_universe.md"
OUT = REPO / "resources" / "curriculum.json"

EXPECTED = {"A1": 61, "A2": 56, "B1": 47}

MODULE_RE = re.compile(
    r"^\*\*(?P<id>[AB][12]\.\d+) (?P<title>.+?)\*\* — (?P<cluster>.+?) \| (?P<functions>.+)$"
)
ATOM_ID_RE = re.compile(r"^[AB][12]\.\d+\.\d+$")


def parse(text: str) -> list[dict]:
    modules: list[dict] = []
    current: dict | None = None
    in_section3 = False
    for line in text.splitlines():
        line = line.rstrip()
        if line.startswith("## 3 ·"):
            in_section3 = True
            continue
        if in_section3 and line.startswith("## ") and not line.startswith("## 3"):
            break  # end of §3
        if not in_section3:
            continue

        m = MODULE_RE.match(line)
        if m:
            current = {
                "id": m.group("id"),
                "level": m.group("id").split(".")[0],
                "title": m.group("title").strip(),
                "grammar_cluster": m.group("cluster").strip(),
                "functions": m.group("functions").strip(),
                "atoms": [],
            }
            modules.append(current)
            continue

        if current is None or not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.split("|")]
        # a well-formed atom row splits into ['', id, title, pattern, exemplar, '']
        if len(cells) != 6 or not ATOM_ID_RE.match(cells[1]):
            continue
        atom_id, title, pattern, exemplar = cells[1], cells[2], cells[3], cells[4]
        title = title.replace("**", "").strip()
        current["atoms"].append({
            "id": atom_id,
            "module": current["id"],
            "title": title,
            "pattern": pattern,
            "exemplar_de": exemplar,
            "synthese": "synthese" in title.lower(),
            "chunk": "chunk" in pattern.lower(),
            "recycles": [],  # informal recycle notes live in `pattern`; structured
                             # recycles are populated when the spiral wires up (Phase 1)
            "format": "single",  # single | mini_arc | campaign (§0, later expansion)
        })
    return modules


def validate(modules: list[dict]) -> dict:
    errors = []
    if len(modules) != 30:
        errors.append(f"expected 30 modules, got {len(modules)}")
    ids = [a["id"] for mod in modules for a in mod["atoms"]]
    if len(ids) != len(set(ids)):
        dupes = sorted({i for i in ids if ids.count(i) > 1})
        errors.append(f"duplicate atom ids: {dupes}")
    per_level = {lvl: 0 for lvl in EXPECTED}
    for mod in modules:
        per_level[mod["level"]] = per_level.get(mod["level"], 0) + len(mod["atoms"])
        for a in mod["atoms"]:
            if not a["id"].startswith(mod["id"] + "."):
                errors.append(f"atom {a['id']} not prefixed by module {mod['id']}")
    for lvl, want in EXPECTED.items():
        if per_level.get(lvl) != want:
            errors.append(f"{lvl}: expected {want} atoms, got {per_level.get(lvl)}")
    if errors:
        for e in errors:
            print("✗", e)
        sys.exit(1)
    return per_level


def main() -> None:
    text = SRC.read_text(encoding="utf-8")
    modules = parse(text)
    per_level = validate(modules)

    # Guardrails = PEDAGOGY.md §2–§3 verbatim (harmonized at CURRICULUM v2.2 / C1).
    artifact = {
        "meta": {
            "version": "1.0",
            "locked": "2026-08-02",
            "source": "docs/planning/CURRICULUM_v1_universe.md",
            "source_version": "2.2",
            "source_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
            "totals": {"modules": len(modules), "atoms": sum(per_level.values()), **per_level},
            "note": ("Immutable plan (UNIVERSE_STATE stratum 1/5). Teaching status "
                     "(planned|taught, taught_in[]) lives in UNIVERSE_STATE, never here. "
                     "Guardrail numbers are PEDAGOGY.md §2–§3, the single source."),
        },
        "block_law": {
            "duration_s": 30,
            "segments": "2 x 15s Seedance clips (45s / 3 segments = rare, explicit exception)",
            "packing": ("1 block = ONE communicative function = 1-3 tightly-related atoms; "
                        "an atom may stretch across 2-3 blocks; never stack unrelated "
                        "patterns; Synthese atoms = zero-new blocks (story-heavy slots)"),
            "formats": ["single", "mini_arc", "campaign"],
            "default_format": "single",
        },
        "guardrails": {
            "A1": {"max_words": 30, "max_sentence_words": 8, "wpm_target": 80,
                   "max_new_words": 5, "min_pattern_reps": 2,
                   "prohibited_until_introduced": [
                       "Perfekt (except sanctioned chunks)", "Nebensaetze", "Genitiv",
                       "Passiv", "Konjunktiv II (except sanctioned chunks)"]},
            "A2": {"max_words": 55, "max_sentence_words": 12, "wpm_target": 100,
                   "max_new_words": 6, "min_pattern_reps": 2,
                   "prohibited_until_introduced": [
                       "Genitiv", "Passiv", "Konjunktiv II beyond 'haette gern'",
                       "Plusquamperfekt"]},
            "B1": {"max_words": 80, "max_sentence_words": 15, "wpm_target": 125,
                   "max_new_words": 8, "min_pattern_reps": 2,
                   "prohibited_until_introduced": []},
        },
        "proper_noun_rule": "fixed cast; max 1 new proper noun per module",
        "modules": modules,
    }

    OUT.write_text(json.dumps(artifact, ensure_ascii=False, indent=2) + "\n",
                   encoding="utf-8")
    sha = hashlib.sha256(OUT.read_bytes()).hexdigest()
    print(f"✓ {len(modules)} modules · {sum(per_level.values())} atoms "
          f"({' · '.join(f'{k}={v}' for k, v in sorted(per_level.items()))})")
    print(f"✓ wrote {OUT.relative_to(REPO)}")
    print(f"  sha256 (pin this in REGISTRY.md): {sha}")


if __name__ == "__main__":
    main()

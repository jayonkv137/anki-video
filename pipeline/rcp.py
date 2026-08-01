"""RCP — Run Context Pack builder.

Assembles the "creator's mind" that is injected into every LLM stage:
  MISSION + Character Bible + Canon Blocks + Prompting Guidelines + Series Memory Digest

Also hash-verifies all canon files against REGISTRY.md.
"""

import hashlib
import json
import os
import re
from pathlib import Path

import requests
from dotenv import load_dotenv

REPO = Path(__file__).parent.parent
CANON = REPO / "prompts" / "canon"

load_dotenv(REPO / ".env")

SUPABASE_URL = os.environ["SUPABASE_URL"].rstrip("/")
SUPABASE_KEY = os.environ["SUPABASE_SECRET_KEY"]
HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
}


# ── Canon loading + hash verification ────────────────────────────

def _parse_registry() -> dict[str, tuple[str, str]]:
    """Parse REGISTRY.md → {relative_path: (version, sha256)}."""
    text = (CANON / "REGISTRY.md").read_text(encoding="utf-8")
    registry = {}
    for line in text.splitlines():
        m = re.match(r"\|\s*`([^`]+)`\s*\|\s*([^|]+)\|\s*`([a-f0-9]{64})`\s*\|", line)
        if m:
            registry[m.group(1).strip()] = (m.group(2).strip(), m.group(3).strip())
    return registry


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_canon() -> dict[str, str]:
    """Verify all canon files match REGISTRY.md hashes. Returns {file: version} map.
    Raises RuntimeError on mismatch."""
    registry = _parse_registry()
    versions = {}
    for rel_path, (version, expected_hash) in registry.items():
        full_path = REPO / rel_path
        if not full_path.exists():
            raise RuntimeError(f"Canon file missing: {rel_path}")
        actual = _sha256(full_path)
        if actual != expected_hash:
            raise RuntimeError(
                f"Canon hash mismatch: {rel_path}\n"
                f"  expected: {expected_hash}\n"
                f"  actual:   {actual}\n"
                f"  → Edit REGISTRY.md after intentional canon changes."
            )
        versions[rel_path] = version
    return versions


def _load(rel_path: str) -> str:
    return (REPO / rel_path).read_text(encoding="utf-8")


# ── Series memory digest ─────────────────────────────────────────

def _fetch_series_memory(limit: int = 5) -> list[dict]:
    """Fetch last N episodes from Supabase for the RCP digest."""
    resp = requests.get(
        f"{SUPABASE_URL}/rest/v1/episodes",
        headers=HEADERS,
        params={
            "select": "title_de,scenario,environment,mains,cameos,word_positions,verdict",
            "order": "created_at.desc",
            "limit": str(limit),
        },
        timeout=15,
    )
    resp.raise_for_status()
    return resp.json()


def _build_digest(episodes: list[dict]) -> str:
    """Compress recent episodes into a concise digest for the RCP."""
    if not episodes:
        return "(No episodes yet — this is the first run.)"

    lines = [f"## Recent episodes ({len(episodes)} most recent)\n"]
    scenarios_used = set()
    mains_used: dict[str, int] = {}

    for i, ep in enumerate(episodes, 1):
        verdict = ep.get("verdict", "?")
        lines.append(
            f"{i}. [{verdict}] **{ep['title_de']}** — {ep['scenario'][:100]}\n"
            f"   Mains: {', '.join(ep.get('mains', []))} · "
            f"Environment: {ep.get('environment', '?')}"
        )
        scenarios_used.add(ep.get("scenario", "")[:60])
        for m in ep.get("mains", []):
            mains_used[m] = mains_used.get(m, 0) + 1

    lines.append(f"\n## Aggregates")
    lines.append(f"- Scenarios used: {', '.join(scenarios_used)}")
    lines.append(f"- Character appearances: {mains_used}")
    lines.append(f"- DO NOT repeat any of the above scenarios or main-cast pairings.")
    return "\n".join(lines)


# ── RCP assembly ─────────────────────────────────────────────────

class RunContextPack:
    """The Run Context Pack — everything the LLM needs to know."""

    def __init__(self):
        self.canon_versions = verify_canon()
        self.mission = _load("prompts/canon/MISSION.md")
        self.character_bible = _load("resources/Characters-Main-Sheet.md")
        self.canon_blocks = _load("prompts/canon/canon_blocks.md")
        self.guidelines_seedance = _load("prompts/canon/prompting_guidelines_seedance.md")

        episodes = _fetch_series_memory(limit=5)
        self.series_digest = _build_digest(episodes)
        self.episode_log_raw = episodes  # for skill-1 compatibility

    def for_story_stage(self) -> str:
        """Context for story generation stages (skill-1a, skill-1b)."""
        return (
            f"# PROJECT MISSION\n{self.mission}\n\n"
            f"# SERIES MEMORY (avoid repetition)\n{self.series_digest}\n"
        )

    def for_screenplay_stage(self) -> str:
        """Context for screenplay generation."""
        return f"# PROJECT MISSION\n{self.mission}\n"

    def for_prompt_stage(self) -> str:
        """Context for prompt writing — includes video model guidelines."""
        return (
            f"# PROJECT MISSION\n{self.mission}\n\n"
            f"# SEEDANCE GUIDELINES\n{self.guidelines_seedance}\n"
        )

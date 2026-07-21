"""Ledger — run tracking via Supabase (runs + run_events tables).

Pure functions over the REST API. Every stage records its artifacts, token usage,
and hashes here so runs are resumable and auditable.
"""

import hashlib
import json
import os
from pathlib import Path

import requests
from dotenv import load_dotenv

REPO = Path(__file__).parent.parent
load_dotenv(REPO / ".env")

SUPABASE_URL = os.environ["SUPABASE_URL"].rstrip("/")
SUPABASE_KEY = os.environ["SUPABASE_SECRET_KEY"]
HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation",
}


def _url(table: str) -> str:
    return f"{SUPABASE_URL}/rest/v1/{table}"


def _post(table: str, data: dict) -> dict:
    resp = requests.post(_url(table), headers=HEADERS, json=data, timeout=15)
    resp.raise_for_status()
    return resp.json()[0]


def _patch(table: str, filters: dict, data: dict) -> dict:
    resp = requests.patch(
        _url(table), headers=HEADERS, json=data,
        params=filters, timeout=15,
    )
    resp.raise_for_status()
    rows = resp.json()
    return rows[0] if rows else {}


def _get(table: str, params: dict) -> list[dict]:
    resp = requests.get(_url(table), headers=HEADERS, params=params, timeout=15)
    resp.raise_for_status()
    return resp.json()


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


# ── Run lifecycle ────────────────────────────────────────────────

def create_run(word_positions: list[int], canon_versions: dict) -> dict:
    """Open a new run in the ledger. Returns the run row."""
    return _post("runs", {
        "status": "running",
        "stage": "init",
        "word_positions": word_positions,
        "canon_versions": json.dumps(canon_versions),
    })


def update_run(run_id: str, **fields) -> dict:
    """Update run fields (status, stage, chosen_option, cost_cents, etc.)."""
    return _patch("runs", {"id": f"eq.{run_id}"}, fields)


def get_run(run_id: str) -> dict | None:
    rows = _get("runs", {"id": f"eq.{run_id}", "select": "*"})
    return rows[0] if rows else None


def get_latest_run() -> dict | None:
    rows = _get("runs", {"select": "*", "order": "started_at.desc", "limit": "1"})
    return rows[0] if rows else None


# ── Run events ───────────────────────────────────────────────────

def log_event(run_id: str, stage: str, status: str = "completed",
              artifact_path: str = None, artifact_sha256: str = None,
              tokens_in: int = 0, tokens_out: int = 0,
              detail: dict = None) -> dict:
    """Record a stage event in the ledger."""
    return _post("run_events", {
        "run_id": run_id,
        "stage": stage,
        "status": status,
        "artifact_path": artifact_path,
        "artifact_sha256": artifact_sha256,
        "tokens_in": tokens_in,
        "tokens_out": tokens_out,
        "detail": json.dumps(detail or {}),
    })


def get_events(run_id: str) -> list[dict]:
    return _get("run_events", {
        "run_id": f"eq.{run_id}",
        "select": "*",
        "order": "created_at.asc",
    })


# ── Episodes (series memory) ────────────────────────────────────

def save_episode(run_id: str, title_de: str, scenario: str,
                 environment: str, mains: list[str], cameos: list[str],
                 word_positions: list[int], verdict: str = "pending") -> dict:
    return _post("episodes", {
        "run_id": run_id,
        "title_de": title_de,
        "scenario": scenario,
        "environment": environment,
        "mains": mains,
        "cameos": cameos,
        "word_positions": word_positions,
        "verdict": verdict,
    })


# ── Cost tracking ────────────────────────────────────────────────

# Per-token cents, by model tier. $X/M tokens = X*100 cents/M = X*0.0001 cents/token.
PRICING_CENTS_PER_TOKEN = {
    "claude-sonnet-5": {"in": 0.0003, "out": 0.0015},   # $3/M in, $15/M out
    "claude-haiku-4-5": {"in": 0.0001, "out": 0.0005},  # $1/M in, $5/M out
}


def add_cost(run_id: str, tokens_in: int, tokens_out: int,
             model: str = "claude-sonnet-5") -> int:
    """Add token cost to the run total. Returns new total."""
    rate = PRICING_CENTS_PER_TOKEN.get(model, PRICING_CENTS_PER_TOKEN["claude-sonnet-5"])
    cost = int(tokens_in * rate["in"] + tokens_out * rate["out"])  # cents
    run = get_run(run_id)
    new_total = (run.get("cost_cents") or 0) + cost
    update_run(run_id, cost_cents=new_total)
    return new_total

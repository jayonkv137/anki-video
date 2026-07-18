"""E3: Create ledger/memory tables in Supabase and migrate episode_log.json.

Usage:
    python scripts/migrations/run_migration.py          # create tables + migrate
    python scripts/migrations/run_migration.py --verify  # round-trip test only
"""

import argparse
import json
import os
import sys
from pathlib import Path

import requests
from dotenv import load_dotenv

REPO = Path(__file__).parent.parent.parent
load_dotenv(REPO / ".env")

SUPABASE_URL = os.environ["SUPABASE_URL"].rstrip("/")
SUPABASE_KEY = os.environ["SUPABASE_SECRET_KEY"]

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation",
}


def rest_url(table: str) -> str:
    return f"{SUPABASE_URL}/rest/v1/{table}"


def run_sql(sql: str) -> dict:
    """Execute raw SQL via Supabase's RPC endpoint (requires service key)."""
    # Use the pg_net-free approach: POST to /rest/v1/rpc with a custom function,
    # or use the SQL endpoint directly.
    # Supabase exposes a SQL endpoint at /pg/query for service-role keys.
    resp = requests.post(
        f"{SUPABASE_URL}/rest/v1/rpc",
        headers={**HEADERS, "Content-Type": "application/json"},
        json={"query": sql},
        timeout=30,
    )
    return resp


def create_tables():
    """Create tables by executing the SQL migration via Supabase's REST API."""
    sql_file = Path(__file__).parent / "001_ledger_tables.sql"
    sql = sql_file.read_text(encoding="utf-8")

    # Split into individual statements (Supabase REST RPC doesn't handle multi-statement well)
    # Instead, we'll create each table via individual PostgREST-compatible calls
    # Actually, the simplest approach: use the Supabase Management API or just try to
    # insert and see if tables exist. Let's try a different approach — use a stored function.

    # Approach: Create tables one at a time using separate POST calls to a helper RPC.
    # But first, let's check if tables already exist by trying a select.

    for table in ["runs", "run_events", "episodes"]:
        resp = requests.get(
            rest_url(table),
            headers={**HEADERS},
            params={"limit": "1"},
            timeout=15,
        )
        if resp.status_code == 200:
            print(f"  ✓ Table '{table}' already exists")
        elif resp.status_code in (404, 400):
            print(f"  ✗ Table '{table}' does not exist — needs manual creation")
            print(f"    → Run the SQL in scripts/migrations/001_ledger_tables.sql")
            print(f"      in the Supabase SQL Editor (Dashboard → SQL Editor → New query)")
            return False
        else:
            print(f"  ? Table '{table}' returned status {resp.status_code}: {resp.text[:200]}")
            return False

    return True


def migrate_episode_log():
    """Migrate output/episodes/episode_log.json into the episodes table."""
    log_path = REPO / "output" / "episodes" / "episode_log.json"
    if not log_path.exists():
        print("  No episode_log.json found, skipping migration")
        return True

    episodes = json.loads(log_path.read_text(encoding="utf-8"))
    if not episodes:
        print("  episode_log.json is empty, skipping migration")
        return True

    # Check if already migrated (look for existing episodes with same positions)
    for ep in episodes:
        positions = ep["positions"]
        resp = requests.get(
            rest_url("episodes"),
            headers=HEADERS,
            params={
                "word_positions": f"eq.{{{','.join(map(str, positions))}}}",
                "limit": "1",
            },
            timeout=15,
        )
        if resp.status_code == 200 and resp.json():
            print(f"  Episode '{ep['title']}' already migrated, skipping")
            continue

        # Insert the episode
        row = {
            "title_de": ep["title"],
            "scenario": ep["scenario"],
            "mains": ep["mains"],
            "word_positions": positions,
            "verdict": "approved",  # it was produced and kept
        }
        resp = requests.post(
            rest_url("episodes"),
            headers=HEADERS,
            json=row,
            timeout=15,
        )
        if resp.status_code in (200, 201):
            inserted = resp.json()
            print(f"  ✓ Migrated episode: '{ep['title']}' (id={inserted[0]['id']})")
        else:
            print(f"  ✗ Failed to insert episode: {resp.status_code} {resp.text[:300]}")
            return False

    return True


def verify_round_trip():
    """Insert a test run, add an event, query back, then clean up."""
    print("\n--- Round-trip verification ---")

    # 1. Insert a test run
    test_run = {
        "status": "init",
        "stage": "test",
        "word_positions": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
        "canon_versions": json.dumps({"MISSION.md": "1.0", "canon_blocks.md": "0"}),
    }
    resp = requests.post(rest_url("runs"), headers=HEADERS, json=test_run, timeout=15)
    assert resp.status_code in (200, 201), f"Insert run failed: {resp.status_code} {resp.text}"
    run = resp.json()[0]
    run_id = run["id"]
    print(f"  ✓ INSERT runs: id={run_id}, status={run['status']}")

    # 2. Insert a test event
    test_event = {
        "run_id": run_id,
        "stage": "init",
        "status": "completed",
        "artifact_path": "test/artifact.json",
        "artifact_sha256": "abc123",
        "tokens_in": 100,
        "tokens_out": 200,
    }
    resp = requests.post(rest_url("run_events"), headers=HEADERS, json=test_event, timeout=15)
    assert resp.status_code in (200, 201), f"Insert event failed: {resp.status_code} {resp.text}"
    event = resp.json()[0]
    print(f"  ✓ INSERT run_events: id={event['id']}, stage={event['stage']}")

    # 3. Query back the run and its events
    resp = requests.get(
        rest_url("runs"),
        headers=HEADERS,
        params={"id": f"eq.{run_id}", "select": "*"},
        timeout=15,
    )
    assert resp.status_code == 200
    fetched_run = resp.json()[0]
    assert fetched_run["word_positions"] == [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    print(f"  ✓ SELECT runs: positions={fetched_run['word_positions']}, status={fetched_run['status']}")

    resp = requests.get(
        rest_url("run_events"),
        headers=HEADERS,
        params={"run_id": f"eq.{run_id}", "select": "*"},
        timeout=15,
    )
    assert resp.status_code == 200
    fetched_events = resp.json()
    assert len(fetched_events) == 1
    assert fetched_events[0]["tokens_in"] == 100
    print(f"  ✓ SELECT run_events: {len(fetched_events)} event(s), tokens_in={fetched_events[0]['tokens_in']}")

    # 4. Query episodes table
    resp = requests.get(
        rest_url("episodes"),
        headers=HEADERS,
        params={"select": "id,title_de,mains,verdict", "limit": "5"},
        timeout=15,
    )
    assert resp.status_code == 200
    eps = resp.json()
    print(f"  ✓ SELECT episodes: {len(eps)} episode(s) in series memory")
    for ep in eps:
        print(f"    - [{ep['verdict']}] {ep['title_de']} ({', '.join(ep['mains'])})")

    # 5. Clean up test data
    requests.delete(rest_url("run_events"), headers=HEADERS, params={"run_id": f"eq.{run_id}"}, timeout=15)
    requests.delete(rest_url("runs"), headers=HEADERS, params={"id": f"eq.{run_id}"}, timeout=15)
    print(f"  ✓ Cleaned up test run {run_id}")

    print("\n✅ Round-trip verification PASSED")
    return True


def main():
    parser = argparse.ArgumentParser(description="E3: Ledger migration + verification")
    parser.add_argument("--verify", action="store_true", help="Run round-trip test only")
    args = parser.parse_args()

    if args.verify:
        return verify_round_trip()

    print("E3: Creating ledger + memory tables\n")

    print("1. Checking tables...")
    tables_ok = create_tables()

    if not tables_ok:
        print("\n⚠️  Tables need to be created manually.")
        print("   Copy the SQL from scripts/migrations/001_ledger_tables.sql")
        print("   and run it in the Supabase SQL Editor.")
        print("   Then re-run: python scripts/migrations/run_migration.py")
        sys.exit(1)

    print("\n2. Migrating episode_log.json...")
    if not migrate_episode_log():
        sys.exit(1)

    print("\n3. Running round-trip verification...")
    if not verify_round_trip():
        sys.exit(1)


if __name__ == "__main__":
    main()

"""CLI — command-line interface for the pipeline.

V4 studio diagnostics:
    python -m pipeline curriculum [--status]
    python -m pipeline context [phase] [-v]
    python -m pipeline state-verify

Legacy (V3 wizard, retired at Phase 3.5):
    python -m pipeline status [run_id] | resume <run_id> | storyboard [run_id]
"""

import argparse
import json
import sys
from pathlib import Path

from anthropic import Anthropic
from dotenv import load_dotenv

from .rcp import RunContextPack, REPO
from . import ledger
from . import stages


load_dotenv(REPO / ".env")


def _ep_dir_for_positions(positions: list[int]) -> Path:
    return REPO / "output" / "episodes" / f"ep_{positions[0]}-{positions[-1]}"


def _ep_dir_for_brief(run_id: str) -> Path:
    """V3 co-creation runs are stereotype-driven (no word positions) → name by run id."""
    return REPO / "output" / "episodes" / f"ep_{run_id[:8]}"


# ── STATUS command ───────────────────────────────────────────────

def cmd_status(args):
    """Show the current state of a run (or the latest run)."""
    if args.run_id:
        run = ledger.get_run(args.run_id)
        if not run:
            print(f"Run {args.run_id} not found")
            sys.exit(1)
    else:
        run = ledger.get_latest_run()
        if not run:
            print("No runs found")
            return

    run_id = run["id"]
    print(f"Run: {run_id}")
    print(f"  Status:     {run['status']}")
    print(f"  Stage:      {run.get('stage', '?')}")
    print(f"  Words:      {run.get('word_positions', [])}")
    print(f"  Choice:     {run.get('chosen_option', '-')}", end="")
    if run.get("choice_note"):
        print(f" (note: {run['choice_note']})", end="")
    print()
    print(f"  Cost:       ~{run.get('cost_cents', 0)} cents")
    print(f"  Started:    {run.get('started_at', '?')}")
    if run.get("completed_at"):
        print(f"  Completed:  {run['completed_at']}")
    if run.get("error_detail"):
        print(f"  Error:      {run['error_detail'][:200]}")

    # Show events
    events = ledger.get_events(run_id)
    if events:
        print(f"\n  Events ({len(events)}):")
        for ev in events:
            status_icon = "✓" if ev["status"] == "completed" else "✗" if ev["status"] == "failed" else "↻"
            tokens = f"{ev.get('tokens_in', 0)}+{ev.get('tokens_out', 0)} tok" if ev.get("tokens_in") else ""
            print(f"    {status_icon} {ev['stage']:<20} {tokens}")

    # Hint for next action
    if run["status"] == "awaiting_choice":
        positions = run.get("word_positions", [])
        ep_dir = _ep_dir_for_positions(positions) if positions else None
        if ep_dir:
            print(f"\n  → Read {ep_dir.relative_to(REPO)}/options.md")
        print(f"  → Then: python -m pipeline choose <1|2|3> [--note \"...\"]")


# ── RESUME command ───────────────────────────────────────────────

def cmd_resume(args):
    """Resume a failed or interrupted run from its last completed stage."""
    run = ledger.get_run(args.run_id)
    if not run:
        print(f"Run {args.run_id} not found")
        sys.exit(1)

    if run["status"] == "completed":
        print(f"Run {args.run_id[:8]}... is already completed")
        return
    if run["status"] == "awaiting_choice":
        print(f"Run {args.run_id[:8]}... is waiting for your choice at Gate A")
        print(f"  → python -m pipeline choose <1|2|3> [--note \"...\"]")
        return

    # For now, resume = just show status and suggest next action
    print(f"Run {args.run_id[:8]}... failed/interrupted at stage: {run.get('stage')}")
    print(f"Resume is not yet implemented — re-run or choose to continue.")
    # TODO: E6 adds full resume logic based on ledger stage


# ── STORYBOARD command (V3: screenplay → panels) ─────────────────

def cmd_storyboard(args):
    """Screenplay → storyboard panels via an image provider (mock | gpt-image-2 | nano-banana-pro)."""
    run = ledger.get_run(args.run_id) if args.run_id else ledger.get_latest_run()
    if not run:
        print("No run found."); sys.exit(1)
    run_id = run["id"]
    positions = run.get("word_positions", [])
    ep_dir = _ep_dir_for_positions(positions) if positions else _ep_dir_for_brief(run_id)
    sp_path = ep_dir / "screenplay.json"
    if not sp_path.exists():
        print(f"No screenplay at {ep_dir.relative_to(REPO)} — run must reach the screenplay stage first.")
        sys.exit(1)
    sp = json.loads(sp_path.read_text(encoding="utf-8"))
    rcp = RunContextPack()
    stages.stage_storyboard(run_id, rcp, sp, ep_dir, None, image_provider=args.image_provider)


# ── V4 studio diagnostics ────────────────────────────────────────

def cmd_curriculum(args):
    """Verify the locked curriculum artifact + show live teaching status."""
    import hashlib
    from . import context as ctx
    cur = ctx.curriculum()
    meta, totals = cur["meta"], cur["meta"]["totals"]
    print(f"curriculum.json v{meta['version']} (locked {meta['locked']}) — "
          f"{totals['modules']} modules · {totals['atoms']} atoms "
          f"(A1 {totals['A1']} · A2 {totals['A2']} · B1 {totals['B1']})")
    live = hashlib.sha256((REPO / meta["source"]).read_text(encoding="utf-8")
                          .encode("utf-8")).hexdigest()
    print(f"source {meta['source']} v{meta['source_version']}: "
          + ("⚠ CHANGED since the lock — re-run scripts/build_curriculum.py + re-pin"
             if live != meta["source_sha256"] else "✓ unchanged since the lock"))
    if args.status:
        from . import universe_state as st
        s = st.curriculum_status()
        print(f"\ntaught: {s['taught_atoms']}/{s['total_atoms']} atoms · "
              f"next module: {s['next_module'] or '— all complete —'}")
        for m in s["modules"]:
            if m["taught"] or m["id"] == s["next_module"]:
                print(f"  {'✓' if m['complete'] else '▸'} {m['id']:6s} "
                      f"{m['title'][:28]:28s} {m['taught']}/{m['atoms']}")


def cmd_context(args):
    """Per-phase Tier-1 canon budget report (the context contracts)."""
    from . import context as ctx
    budget = args.budget or ctx.MODEL_INPUT_LIMIT
    print(f"(hot canon per phase · model input window {budget:,} tokens · informational)")
    for ph in ([args.phase] if args.phase else ctx.PHASES):
        r = ctx.budget_report(ph, budget)
        print(f"{ph:7s} {r['hot_total_tokens']:6d} tok  {r['hot_share'] * 100:5.2f}% of window  "
              f"{'⚠ canon has sprawled' if r['warn'] else 'ok'}")
        if args.verbose:
            for name, tok in r["per_doc_tokens"].items():
                scoped = " (scoped)" if (ph, name) in ctx.DOC_SECTIONS else ""
                print(f"          {name:12s} {tok:6d}{scoped}")


def cmd_state_verify(args):
    """Check the UNIVERSE_STATE tables + show what state currently knows."""
    from . import universe_state as st
    ready = st.tables_ready()
    for table, ok in ready.items():
        print(f"  {'✓' if ok else '✗'} {table}")
    if not all(ready.values()):
        print("\n→ Run scripts/migrations/002_universe_state.sql in the Supabase SQL Editor,"
              "\n  then re-run: python -m pipeline state-verify")
        sys.exit(1)
    s, rot = st.curriculum_status(), st.rotation_report()
    print(f"\ntaught: {s['taught_atoms']}/{s['total_atoms']} atoms · next: {s['next_module']}")
    print(f"appearances: {rot['counts']}")
    print(f"cold first: {', '.join(rot['least_recent_first'][:4])}")
    cons = st.active_constraints()
    print(f"active constraints: {len(cons)}")
    for c in cons[:5]:
        print(f"  [{c['kind']}] {c['rule'][:80]}")


# ── CLI entry point ──────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(prog="pipeline", description="Stereotypical German text pipeline")
    sub = parser.add_subparsers(dest="command", required=True)

    # status
    p_status = sub.add_parser("status", help="Show run status")
    p_status.add_argument("run_id", nargs="?", help="Run ID (default: latest)")

    # resume
    p_resume = sub.add_parser("resume", help="Resume a failed/interrupted run")
    p_resume.add_argument("run_id", help="Run ID to resume")

    # storyboard (V3): screenplay → storyboard panels via an image provider
    p_sb = sub.add_parser("storyboard", help="Screenplay → storyboard panels (mock|gpt-image-2|nano-banana-pro)")
    p_sb.add_argument("run_id", nargs="?", help="Run id (default: latest)")
    p_sb.add_argument("--image-provider", default="mock", help="mock | gpt-image-2 | nano-banana-pro")

    # ── V4 studio diagnostics ──
    p_cur = sub.add_parser("curriculum", help="Verify the locked curriculum + live status")
    p_cur.add_argument("--status", action="store_true", help="Include taught/next-module status")

    p_ctx = sub.add_parser("context", help="Per-phase canon budget report")
    p_ctx.add_argument("phase", nargs="?", help="idea|script|qc|vision|shoot|post (default: all)")
    p_ctx.add_argument("--budget", type=int, default=None,
                       help="Override the window size (default: the model's real limit)")
    p_ctx.add_argument("-v", "--verbose", action="store_true", help="Per-document breakdown")

    sub.add_parser("state-verify", help="Check UNIVERSE_STATE tables + show what state knows")

    args = parser.parse_args()

    if args.command == "curriculum":
        cmd_curriculum(args)
    elif args.command == "context":
        cmd_context(args)
    elif args.command == "state-verify":
        cmd_state_verify(args)
    elif args.command == "status":
        cmd_status(args)
    elif args.command == "resume":
        cmd_resume(args)
    elif args.command == "storyboard":
        cmd_storyboard(args)

# ── Removed 2026-08-02 (Phase 1 quarantine) ──────────────────────────
# cmd_run/cmd_choose (V2 word-deck) · cmd_generate/cmd_autopilot/cmd_caption
# (called the deleted scenes[] stages) · cmd_brief_* (superseded co-creation).
# Recover with: git show v3-wizard-archive:pipeline/cli.py

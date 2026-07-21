"""CLI — command-line interface for the pipeline.

Usage:
    python -m pipeline run [--start N | --random] [--note "..."]
    python -m pipeline choose <1|2|3> [--note "..."]
    python -m pipeline status [run_id]
    python -m pipeline resume <run_id>
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


# ── RUN command ──────────────────────────────────────────────────

def cmd_run(args):
    """Start a new pipeline run → reaches Gate A and pauses."""
    print("Initializing pipeline run...\n")

    # 1. Build RCP (loads + verifies all canon)
    rcp = RunContextPack()
    print(f"✓ Canon verified ({len(rcp.canon_versions)} files)")
    print(f"✓ Series memory: {len(rcp.episode_log_raw)} recent episode(s)\n")

    # 2. Create run in ledger
    run = ledger.create_run(
        word_positions=[],  # updated after word fetch
        canon_versions=rcp.canon_versions,
    )
    run_id = run["id"]
    print(f"Run {run_id[:8]}... created\n")

    client = Anthropic()

    try:
        # Stage 1: Words
        positions_arg = ([int(p) for p in args.positions.split(",")]
                         if getattr(args, "positions", None) else None)
        words = stages.stage_words(run_id, args.start, args.random, positions=positions_arg)
        positions = [w["position"] for w in words]
        ep_dir = _ep_dir_for_positions(positions)
        print()

        # Stage 2: Story options (3 premises)
        stages.stage_story_options(run_id, rcp, words, args.note, ep_dir, client)

        # Pipeline pauses here — Gate A awaiting choice
        print(f"\n⏸  Run {run_id[:8]}... paused at Gate A.")

    except Exception as e:
        ledger.update_run(run_id, status="failed", error_detail=str(e))
        ledger.log_event(run_id, ledger.get_run(run_id).get("stage", "unknown"),
                         "failed", detail={"error": str(e)})
        raise


# ── CHOOSE command ───────────────────────────────────────────────

def cmd_choose(args):
    """Choose a story option and resume the pipeline through to completion."""
    choice = args.choice
    if choice not in (1, 2, 3):
        print("Error: choice must be 1, 2, or 3")
        sys.exit(1)

    # Find the run awaiting choice
    run = ledger.get_latest_run()
    if not run:
        print("Error: no runs found")
        sys.exit(1)
    if run["status"] != "awaiting_choice":
        print(f"Error: latest run {run['id'][:8]}... is '{run['status']}', not 'awaiting_choice'")
        print(f"Use 'python -m pipeline status' to check run state.")
        sys.exit(1)

    run_id = run["id"]
    positions = run["word_positions"]
    ep_dir = _ep_dir_for_positions(positions)

    print(f"Resuming run {run_id[:8]}... with choice {choice}\n")

    # Record choice
    ledger.update_run(run_id, status="running", chosen_option=choice,
                      choice_note=args.note or None)
    ledger.log_event(run_id, "gate_a", "completed",
                     detail={"choice": choice, "note": args.note})

    # Load the chosen option
    options = json.loads((ep_dir / "options.json").read_text(encoding="utf-8"))
    chosen = options["options"][choice - 1]
    print(f"Chosen: {chosen.get('title_de')} — {chosen.get('scenario', '')[:80]}...\n")

    # Rebuild context — reload the run's EXACT words (not a sequential re-fetch,
    # which would return the wrong set for --random runs)
    rcp = RunContextPack()
    client = Anthropic()
    words = stages.fetch_words_by_positions(positions)

    try:
        # Stage 4: Expand chosen premise → full story
        story = stages.stage_story_expand(run_id, rcp, words, chosen, args.note, ep_dir, client)
        print()

        # Stage 5: Screenplay
        sp, problems = stages.stage_screenplay(run_id, rcp, words, story, ep_dir, client)
        if problems:
            print(f"⚠ Screenplay has {len(problems)} issue(s) after retry")
        print()

        # Stage 6: Quality check (code validators + skill-2q on Haiku 4.5)
        passed, qc_problems, qc_feedback = stages.stage_quality_check(run_id, rcp, sp, words, client)
        if not passed:
            # ONE retry of stage 5 with the judge's feedback, then re-judge once.
            print("\n↻ Quality check failed — one screenplay rewrite with feedback:\n")
            feedback_full = qc_feedback or ""
            if qc_problems:
                feedback_full += ("\n\nSpecific failed checks:\n- " + "\n- ".join(qc_problems))
            sp, problems = stages.stage_screenplay(run_id, rcp, words, story, ep_dir, client,
                                                   qc_feedback=feedback_full)
            if problems:
                print(f"⚠ Rewrite still has {len(problems)} validator issue(s)")
            passed, qc_problems, qc_feedback = stages.stage_quality_check(run_id, rcp, sp, words, client)
            if not passed:
                print("\n⚠ Quality check STILL failing after the one allowed rewrite.")
                print("  Proceeding to prompts — judge the episode yourself at the end")
                print("  (verdicts are in the ledger; fix patterns via /tune, not by thrashing).")
        print()

        # Stage 7: Prompts
        prompts = stages.stage_prompts(run_id, rcp, sp, ep_dir, client)
        print()

        # Stage 8: Finalize
        stages.stage_finalize(run_id, story, sp, prompts, words, ep_dir)

    except Exception as e:
        ledger.update_run(run_id, status="failed", error_detail=str(e))
        ledger.log_event(run_id, ledger.get_run(run_id).get("stage", "unknown"),
                         "failed", detail={"error": str(e)})
        raise


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


# ── GENERATE command ─────────────────────────────────────────────

def cmd_generate(args):
    """Generate scene clips for a run via a video provider (mock | fal)."""
    run = ledger.get_run(args.run_id)
    if not run:
        print(f"Run {args.run_id} not found")
        sys.exit(1)
    ep_dir = _ep_dir_for_positions(run.get("word_positions", []))
    sp_path = ep_dir / "screenplay.json"
    if not sp_path.exists():
        print(f"No screenplay at {ep_dir.relative_to(REPO)} — run must reach the screenplay stage first.")
        sys.exit(1)
    sp = json.loads(sp_path.read_text(encoding="utf-8"))
    stages.stage_generate(run["id"], sp, ep_dir, provider_name=args.provider)


# ── AUTOPILOT command (generate → assemble → caption) ────────────

def cmd_autopilot(args):
    """Full post-Gate-A finish in one command: clips → subtitled video → caption."""
    run = ledger.get_run(args.run_id)
    if not run:
        print(f"Run {args.run_id} not found"); sys.exit(1)
    ep_dir = _ep_dir_for_positions(run.get("word_positions", []))
    sp_path = ep_dir / "screenplay.json"
    if not sp_path.exists():
        print(f"No screenplay at {ep_dir.relative_to(REPO)} — needs a completed run."); sys.exit(1)
    sp = json.loads(sp_path.read_text(encoding="utf-8"))

    print("── AUTOPILOT 1/3 · generate clips ──")
    stages.stage_generate(run["id"], sp, ep_dir, provider_name=args.provider)
    print("\n── AUTOPILOT 2/3 · assemble + subtitles ──")
    from .assemble import assemble_episode
    assemble_episode(ep_dir)
    print("\n── AUTOPILOT 3/3 · caption ──")
    story = json.loads((ep_dir / "story.json").read_text(encoding="utf-8"))
    rcp = RunContextPack()
    client = Anthropic()
    words = stages.fetch_words_by_positions(run.get("word_positions", []))
    stages.stage_caption(run["id"], rcp, story, words, ep_dir, client)
    print(f"\n✅ AUTOPILOT complete — {ep_dir.relative_to(REPO)}/final.mp4 + caption.md ready to post.")


# ── CAPTION command ──────────────────────────────────────────────

def cmd_caption(args):
    """Generate the Instagram caption for a run (needs story.json)."""
    run = ledger.get_run(args.run_id)
    if not run:
        print(f"Run {args.run_id} not found")
        sys.exit(1)
    positions = run.get("word_positions", [])
    ep_dir = _ep_dir_for_positions(positions)
    story_path = ep_dir / "story.json"
    if not story_path.exists():
        print(f"No story.json at {ep_dir.relative_to(REPO)} — run must be past Gate A first.")
        sys.exit(1)

    story = json.loads(story_path.read_text(encoding="utf-8"))
    rcp = RunContextPack()
    client = Anthropic()
    words = stages.fetch_words_by_positions(positions)
    stages.stage_caption(run["id"], rcp, story, words, ep_dir, client)


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


# ── CLI entry point ──────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(prog="pipeline", description="Stereotypical German text pipeline")
    sub = parser.add_subparsers(dest="command", required=True)

    # run
    p_run = sub.add_parser("run", help="Start a new pipeline run")
    p_run.add_argument("--start", type=int, help="Start at word position N")
    p_run.add_argument("--random", action="store_true", help="Pick 10 random words")
    p_run.add_argument("--positions", help="Comma-separated exact positions (golden-batch/regression)")
    p_run.add_argument("--note", default="", help="Director's note for story generation")

    # choose
    p_choose = sub.add_parser("choose", help="Choose a story option at Gate A")
    p_choose.add_argument("choice", type=int, help="Option number (1, 2, or 3)")
    p_choose.add_argument("--note", default="", help="Steering note for story expansion")

    # status
    p_status = sub.add_parser("status", help="Show run status")
    p_status.add_argument("run_id", nargs="?", help="Run ID (default: latest)")

    # resume
    p_resume = sub.add_parser("resume", help="Resume a failed/interrupted run")
    p_resume.add_argument("run_id", help="Run ID to resume")

    # generate (M4): scene prompts → video clips via a provider
    p_gen = sub.add_parser("generate", help="Generate scene clips via a video provider")
    p_gen.add_argument("run_id", help="Run ID (must have prompts)")
    p_gen.add_argument("--provider", default="mock", help="mock | fal (default mock — no key needed)")

    # autopilot: generate → assemble → caption, one command
    p_auto = sub.add_parser("autopilot", help="generate clips → assemble subtitled video → caption")
    p_auto.add_argument("run_id", help="Run ID (completed run)")
    p_auto.add_argument("--provider", default="mock", help="mock | fal")

    # caption (M6): episode → Instagram post copy
    p_cap = sub.add_parser("caption", help="Generate the Instagram caption for a run")
    p_cap.add_argument("run_id", help="Run ID (must have a completed story)")

    # assemble (M5): clips + screenplay → subtitled 9:16 episode video
    p_asm = sub.add_parser("assemble", help="Stitch clips/scene_NN.mp4 into a subtitled episode video")
    p_asm.add_argument("episode", help="Episode dir name under output/episodes/ (e.g. ep_22-499)")
    p_asm.add_argument("--clips", help="Clips dir (default <ep_dir>/clips)")
    p_asm.add_argument("--audio", help="Master audio file replacing clip audio")
    p_asm.add_argument("--out", help="Output file (default <ep_dir>/final.mp4)")

    args = parser.parse_args()

    if args.command == "run":
        cmd_run(args)
    elif args.command == "choose":
        cmd_choose(args)
    elif args.command == "status":
        cmd_status(args)
    elif args.command == "resume":
        cmd_resume(args)
    elif args.command == "generate":
        cmd_generate(args)
    elif args.command == "autopilot":
        cmd_autopilot(args)
    elif args.command == "caption":
        cmd_caption(args)
    elif args.command == "assemble":
        from .assemble import assemble_episode
        ep_dir = REPO / "output" / "episodes" / args.episode
        assemble_episode(
            ep_dir,
            clips_dir=Path(args.clips) if args.clips else None,
            audio=Path(args.audio) if args.audio else None,
            out=Path(args.out) if args.out else None,
        )

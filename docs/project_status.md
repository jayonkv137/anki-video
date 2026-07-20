# Project Status

> Where we are, what's done, where we left off. Update at the end of every working session.

## Milestone: MVP (see planning/PROJECT_GOAL_AND_MILESTONES.md §3)

## Phase checklist (V2)

- [x] V1: Plan + Setup + B0 (n8n) + B1 (word source) + B2 (story stage)
- [x] 2026-07-14 PIVOT → V2 Instagram content pipeline (docs re-cut)
- [ ] **C1 — Character & Art Bible (Jayon's creative step + research on AI-reproducible character design)**
- [~] C2 — Screenplay chain: v1 shipped (3 skills + harness, 1 episode passed). **E1–E4 DONE** (canon system, ledger, pipeline package with Gate A). **E5–E7 NEXT** to reach C2 win condition (3 batches Jayon approves).
- [ ] C3 — Video prototyping (model + style lock; shortlist in RESEARCH_video_generation.md §5)
- [ ] C4 — Gated scene pipeline (n8n port) · C5 — Assembly · C6 — Publishing + Gate 2 · C7 — Daily ops (MVP done)

## PARKING LOT → moved to docs/planning/IDEAS_PARKING_LOT.md (system doc)

## Where we left off

→ **CONTINUE EXECUTION: docs/planning/EXECUTION_PLAN_text_pipeline.md — tasks E5–E7.** E1–E4 done and committed. Pipeline package live (`python -m pipeline run/choose/status`). One test run paused at Gate A (run `e0c04e38`, words 27-575).
→ Handoff packets: docs/handoffs/ (newest first) — new sessions: run `/pickup`.

2026-07-20 (latest): E1-E4 completed in Antigravity (Opus) session. E1: prompting canon distilled (Seedance + Omni guidelines, ≤100 lines each, Jayon-approved). E2: MISSION.md + REGISTRY.md (hash-verified canon). E3: Supabase ledger tables (runs, run_events, episodes) + migration of episode_log.json. E4: pipeline/ package refactor (rcp.py, ledger.py, stages.py, cli.py) — proven live: `pipeline run --random` reaches Gate A, `pipeline status` shows ledger truth. Learning system added by Jayon in parallel session (.agents/skills/learn/, docs/learning_system/).

Earlier: 2026-07-18: Execution plan locked (E1-E7 tasks, single source of truth). 2026-07-17: C2 v1 shipped — 3-skill chain + harness, first episode passed. Content strategy, Flow research, pipeline map. 2026-07-15: Canon names finalized. 2026-07-14: THE PIVOT to V2. Prior: B0-B2 complete, research library built.

## Learning log

- Covered: PSB method, evidence-chained decisions, git/gh, Docker+n8n basics, Supabase/PostgREST, structured outputs + semantic validate→retry (incl. two real failure lessons: -eln stemming false positive, max_tokens truncation). NEW: RCP architecture (why stateless-with-shared-pack beats one-long-conversation), hash-verified canon (tamper detection), ledger-based run tracking (resumability + auditability), Gate A pattern (human choice before committing resources).
- Up next (E5): skill splitting (story options vs expand), quality-check skill design, dual video-model prompt packages.
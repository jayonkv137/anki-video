# Project Status

> Where we are, what's done, where we left off. Update at the end of every working session.

## Milestone: MVP (see planning/PROJECT_GOAL_AND_MILESTONES.md §3)

## Phase checklist (V2)

- [x] V1: Plan + Setup + B0 (n8n) + B1 (word source) + B2 (story stage)
- [x] 2026-07-14 PIVOT → V2 Instagram content pipeline (docs re-cut)
- [ ] **C1 — Character & Art Bible (Jayon's creative step + research on AI-reproducible character design)**
- [~] C2 — Screenplay chain: v1 shipped (3 skills + harness, 1 episode passed). **E1–E6 DONE** — canon system, ledger, pipeline package with Gate A, skills v2, dual-package prompts + first full live run completed. **E7 NEXT**: 2 more Jayon-approved batches (this run is the 1st candidate) = C2 win condition.
- [ ] C3 — Video prototyping (model + style lock; shortlist in RESEARCH_video_generation.md §5)
- [ ] C4 — Gated scene pipeline (n8n port) · C5 — Assembly · C6 — Publishing + Gate 2 · C7 — Daily ops (MVP done)

## PARKING LOT → moved to docs/planning/IDEAS_PARKING_LOT.md (system doc)

## Where we left off

→ **CONTINUE EXECUTION: docs/planning/EXECUTION_PLAN_text_pipeline.md — E7.** E1–E6 all done. E5 committed on branch `feat/e5-skills-v2` (`491fd61`, still NOT merged to main). E6 code (stage-7 dual-package rewiring, QC-retry, cost/word-reload fixes) is **uncommitted** in the working tree as of this line — commit before starting E7.
→ **First live run complete:** run `3baf6a40` (words 22-499) → chose option 3 "Müller, der Soldat" → full episode produced (`output/episodes/ep_22-499/episode.md` + dual prompts + refs_manifest). QC failed twice (after the 1 allowed retry) — proceeded per design; Jayon still needs to judge whether this episode is E7-approval-worthy or needs a `/tune` pass first (skill-2q itself flagged Scene 10's dialogue style as inconsistent with Müller's "clipped" voice — worth a look).
→ **Resolved:** the pending-style/audio-refs question — accepted as correct-by-design (C1/C3 not built yet, manifest is honest, doesn't block text-pipeline completion).
→ Handoff packets: docs/handoffs/ (newest first) — new sessions: run `/pickup`.

2026-07-21 (latest): **E6 complete** — first full pipeline run end-to-end (Gate A → episode.md), 3 bugs fixed along the way: skill-3 `max_tokens` truncation (24k→64k for the dual-package output), `ledger.add_cost` 10x overcount + wrong-tier pricing (now per-model rate table), `choose`/`resume` reloading the wrong words for `--random` runs (`fetch_words_by_positions`). Also this session: tuned `Characters-Main-Sheet.md` v1.2 + skill-2 v1.1 to fix an observed "quiet characters became mute" pattern (Müller/Rolf) — verified in the live run: Müller spoke real dialogue in all 10 scenes.

2026-07-21: E5 skills v2 shipped + committed (`491fd61`, branch `feat/e5-skills-v2`) — skill-1 split into 1a (Gate A options) / 1b (expand); skill-2q quality-check on Haiku 4.5 (code validators + LLM checklist, verdict → ledger); skill-3 v2 dual Seedance/Omni packages; version headers on all skills; `_call` model/max_tokens parameterized.

2026-07-20: E1-E4 completed in Antigravity (Opus) session. E1: prompting canon distilled (Seedance + Omni guidelines, ≤100 lines each, Jayon-approved). E2: MISSION.md + REGISTRY.md (hash-verified canon). E3: Supabase ledger tables (runs, run_events, episodes) + migration of episode_log.json. E4: pipeline/ package refactor (rcp.py, ledger.py, stages.py, cli.py) — proven live: `pipeline run --random` reaches Gate A, `pipeline status` shows ledger truth. Learning system added by Jayon in parallel session (.agents/skills/learn/, docs/learning_system/).

Earlier: 2026-07-18: Execution plan locked (E1-E7 tasks, single source of truth). 2026-07-17: C2 v1 shipped — 3-skill chain + harness, first episode passed. Content strategy, Flow research, pipeline map. 2026-07-15: Canon names finalized. 2026-07-14: THE PIVOT to V2. Prior: B0-B2 complete, research library built.

## Learning log

- Covered: PSB method, evidence-chained decisions, git/gh, Docker+n8n basics, Supabase/PostgREST, structured outputs + semantic validate→retry (incl. two real failure lessons: -eln stemming false positive, max_tokens truncation). NEW: RCP architecture (why stateless-with-shared-pack beats one-long-conversation), hash-verified canon (tamper detection), ledger-based run tracking (resumability + auditability), Gate A pattern (human choice before committing resources).
- Covered (2026-07-21): single-responsibility skill splitting (one behavior = one versioned file, so `/tune` owns exactly one place); model-tier routing (Haiku 4.5 for cheap strict quality-checks — the R10 rubber-stamping risk, the "fail if unsure" mitigation, and the one-line model-upgrade path once `_call` is parameterized); dual video-model prompt design (Seedance first-30-words law + ref-mirroring vs Omni narrative brief + stateful edit-turns); reference-asset role mapping and resolving canonical names → assets (umlaut folding) with honest `pending` for assets not yet produced (don't fabricate); structured-output JSON schema discipline (`additionalProperties:false` + all-required).
- Covered (2026-07-21, E6): the "16k+ max_tokens" truncation lesson recurring at a new output shape (dual packages need proportionally more room — always re-check the ceiling when an output shape grows); a cost-tracking bug that was silently 10x wrong for months (E3-era code) — cents-per-token math is easy to get an order of magnitude wrong; per-model-tier pricing (don't apply Sonnet rates to Haiku calls); why `choose`/`resume` must reload by exact word positions, not re-fetch sequentially, once `--random` runs exist.
- Up next (E7): judge this first live episode (episode.md + prompts), 2 more Jayon-approved batches on fresh word sets = C2 win. Merge `feat/e5-skills-v2` to main once E6 commit lands.
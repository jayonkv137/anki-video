# HANDOFF — 2026-07-18 — Execution plan locked; build moves to Antigravity

## Objective + non-goals
Execute the TEXT pipeline v2 (words → Gate-A story choice → screenplay → QC → dual Seedance/Omni prompt packages) per docs/planning/EXECUTION_PLAN_text_pipeline.md, tasks E1–E7. NON-goals: video generation (C3 after), n8n port (C4), anything parked.

## Exact position
- All planning/docs synced to the execution plan (single source of truth). C2 v1 chain + harness work (1 episode passed). C1 open items unchanged (style system, humans-in-world decision, image text fixes — Jayon).
- NEW since last packet: Jayon's prompting research landed in resources/ (AI Prompting Consistency Research.md — Seedance 2.5 first-20-30-words weighting, ≤3000 chars, no adjective stacking, ref hierarchy audio>video>image, up to 50 refs; Omni Flash stateful Interactions API previous_interaction_id, ≤10s/720p, ≤10 images + 12-page PDF companion). E1 distills these into canon.
- Skills/rituals live: /pickup /context-handoff /idea /phase-gate /tune /update-docs /handoff.

## UNVERIFIED assumptions
Same as previous packet (interim canon blocks unvalidated in video; German audio untested; humans-in-world OPEN) + new: Seedance/Omni API access & exact parameter names not yet provisioned/verified (E-tasks stop at prompt TEXT, so not blocking).

## Failures distilled (carry forward)
Big JSON → always structured outputs + streaming ≥16k. Short char names broke canon substitution → Naming Law + fuzzy match. Sonnet thinking eats max_tokens.

## Next 3 steps
1. Jayon opens Antigravity (Opus) in the repo with the opening prompt from EXECUTION_PLAN §4 → E1, stop for review.
2. E2–E7 one at a time, commit per task, Jayon judges at gates.
3. Parallel Jayon: STYLE_SYSTEM + humans-in-world decision + Flow Episode-01 shoot (logs → C3).

## Reread first
CLAUDE.md · EXECUTION_PLAN_text_pipeline.md · this packet · docs/project_status.md · prompts/skills/ + prompts/canon/ · resources/AI Prompting Consistency Research.md

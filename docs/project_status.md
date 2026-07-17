# Project Status

> Where we are, what's done, where we left off. Update at the end of every working session.

## Milestone: MVP (see planning/PROJECT_GOAL_AND_MILESTONES.md §3)

## Phase checklist (V2)

- [x] V1: Plan + Setup + B0 (n8n) + B1 (word source) + B2 (story stage)
- [x] 2026-07-14 PIVOT → V2 Instagram content pipeline (docs re-cut)
- [ ] **C1 — Character & Art Bible (NEXT; Jayon's creative step + research on AI-reproducible character design)**
- [~] C2 — Screenplay chain v1 BUILT (3 skills + harness, 1 episode passed); remaining: Jayon quality iteration on multiple batches, then win condition (3 batches pass him)
- [ ] C3 — Video prototyping (model + style lock; shortlist in RESEARCH_video_generation.md §5)
- [ ] C4 — Gated scene pipeline · C5 — Assembly · C6 — Publishing + Gate 2 · C7 — Daily ops (MVP done)

## PARKING LOT → moved to docs/planning/IDEAS_PARKING_LOT.md (system doc)

## Where we left off

→ **EXECUTE NOW (Antigravity, Opus): docs/planning/EXECUTION_PLAN_text_pipeline.md — tasks E1–E7.** Opening prompt is in the plan §4.
→ Handoff packets: docs/handoffs/ (newest first) — Claude Code sessions: run `/pickup`.

2026-07-17 (latest): C2 v1 shipped — run `./.venv/bin/python scripts/generate_episode.py --random` (or --start N / --note "..."), read output/episodes/ep_*/episode.md, judge quality, iterate skills. Earlier: Jayon's content-structure session fully filed: CONTENT_STRATEGY_instagram.md (triptych, launch sequence, card pipeline 6b, subtitles+hook requirements, scenario-first story stage, Ted-in-real-world direction) + RESEARCH_BACKLOG.md (system: 14 items, 5 done). Episode-01 gold-standard screenplay in episodes/episode-01.md — Jayon shoots it manually in Flow. useapi verdict: parked (#7). Earlier 2026-07-17: Google Flow researched (RESEARCH_google_flow.md): no public API → Flow = manual cockpit (C1 assets, C3 tests, Episode-0 mockup protocol §4); automated pipeline stays n8n + Gemini API. Full pipeline map drawn: PIPELINE_MVP.md. Jayon has full cast in Flow incl. voices — ACTION for Jayon: rename Flow characters to canon grammar (Rolf die Wurst · Bert das Bier · Kati die Kartoffel · Müller das Brot). Prior 2026-07-15: names finalized+synced (Rolf/Bert/Kati/Müller). Jayon doing: image text fixes, style system. Claude doing: art-style-system research. Prior: Jayon delivered C1 cast (resources/: Characters-Main-Sheet.md + 4 character folders with bibles & reference images). Claude review in docs/planning/C1_character_review.md — 2 blockers before generation: (1) canon naming conflicts across docs/folders, (2) umlaut/text errors on rendered characters. C1 remainder: Jayon's art-style sheet + naming decision. Then C2 (screenplay chain). Idea system live: IDEAS_PARKING_LOT.md + VISION_HISTORY.md.

## Learning log

- Covered: PSB method, evidence-chained decisions, git/gh, Docker+n8n basics, Supabase/PostgREST, structured outputs + semantic validate→retry (incl. two real failure lessons: -eln stemming false positive, max_tokens truncation).
- Up next (C1): image-model prompting, reference/seed consistency techniques, character design for AI reproducibility.
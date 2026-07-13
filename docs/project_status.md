# Project Status

> Where we are, what's done, where we left off. Update at the end of every working session.

## Milestone: MVP (see planning/PROJECT_GOAL_AND_MILESTONES.md §3)

## Phase checklist

- [x] Plan — goal, product spec, engineering spec (2026-07-13)
- [ ] **Setup — Claude Code (IN PROGRESS)**
  - [x] 1. GitHub repo
  - [x] 2. CLAUDE.md (researched best practices, tailored)
  - [x] 3. Automated docs (this file + architecture.md + changelog.md)
  - [x] 4. `.env` — just-in-time (template exists; keys added as services are provisioned)
  - [x] 5. Plugins — just-in-time: Jayon installs via `/plugins` in an interactive `claude` session in this repo when Build starts (Anthropic feature-dev; frontend plugin when app work begins)
  - [x] 6. MCPs — just-in-time: Supabase MCP when Supabase is provisioned; n8n MCP when the instance runs; Playwright MCP when the frontend exists
  - [x] 7. Slash commands: `/update-docs` (living-docs refresh), `/handoff` (self-contained Antigravity prompt generator) in `.claude/commands/`
- [ ] **Build — plan LOCKED** (`planning/BUILD_PLAN_MVP.md`): B0 heartbeat → B1 words → B2 story → B3 video design ⭐ → B4 scenes → B5 assembly → B6 app → B7 daily automation
  - [x] B0 — Engine heartbeat (2026-07-13): Docker + n8n container on volume `n8n_data`; `B0 Heartbeat` webhook workflow returns 200 and survives restart. Workflow in `workflows/b0-heartbeat.json`.
  - [ ] B1 — Word source (NEXT): Supabase project, `words` table, import 625-deck, "next 10 unseen" query, n8n reads it.

## Where we left off

2026-07-13: **B0 done** — n8n runs in Docker with persistent storage (`n8n_data` volume) and serves a webhook-triggered heartbeat workflow; both win-condition halves demonstrated (runs on webhook call + survives container stop/start). **Next: B1 — provision Supabase (free tier, just-in-time), create the `words` table, import the Fluent Forever 625 export, build the "next 10 unseen words" query, and have n8n fetch it.** Work happens in fresh Claude Code sessions opened inside this repo (CLAUDE.md carries the working agreement).

## Learning log (concepts Jayon has covered / needs next)

- Covered so far: project spec method (PSB), chain tool-decisions with evidence, git repo + gh CLI auth basics; **Docker (image vs container vs volume, disposable containers, port mapping, why n8n data needs a volume); n8n anatomy (nodes, webhook trigger, executions, workflow-as-JSON in repo, CLI import/activate).**
- Up next (B1): relational DB basics (tables/rows/keys), Supabase, n8n credentials + HTTP fetch against a real API.
- Reference (B0): Docker basics + n8n foundations.
  - n8n resources (chosen 2026-07-13): official n8n Beginner course playlist (YouTube) + official Level 1 text course (docs.n8n.io/courses/level-one/) done hands-on inside our own instance; single-video alternative: "Master n8n in 2 Hours (2026)". Skip AI-agent content for now.
  - Must-understand checklist: nodes & executions · triggers (Webhook) · credentials · expressions {{ }} · HTTP Request node · Split In Batches loops · error workflows.
- Later: prompt engineering for structured JSON, validate→retry pattern (B2).

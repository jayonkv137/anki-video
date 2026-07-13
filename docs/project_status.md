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
  - [ ] B0 — Engine heartbeat (NEXT)

## Where we left off

2026-07-13: Plan + Setup phases fully complete; build plan locked. **Next: B0 — install Docker Desktop, run n8n container with persistent volume, first cron workflow.** Work happens in fresh Claude Code sessions opened inside this repo (CLAUDE.md carries the working agreement).

## Learning log (concepts Jayon has covered / needs next)

- Covered so far: project spec method (PSB), chain tool-decisions with evidence, git repo + gh CLI auth basics.
- Up next: Docker basics, n8n core concepts (nodes, cron triggers, credentials, loops, error workflows), prompt engineering for structured JSON, validate→retry pattern.

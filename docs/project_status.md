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
- [ ] Build — MVP phases (to be broken down next: sub-goals with win conditions + learning objectives)

## Where we left off

2026-07-13: Setup phase COMPLETE (just-in-time items tracked above). Next session: break the Build phase into ordered sub-goals — each with a win condition and a learning objective — starting from the pipeline core.

## Learning log (concepts Jayon has covered / needs next)

- Covered so far: project spec method (PSB), chain tool-decisions with evidence, git repo + gh CLI auth basics.
- Up next: Docker basics, n8n core concepts (nodes, cron triggers, credentials, loops, error workflows), prompt engineering for structured JSON, validate→retry pattern.

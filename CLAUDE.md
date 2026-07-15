# CLAUDE.md

**"Stereotypical German"** — an Instagram page teaching German through entertaining daily AI-generated stories. Four original stereotypical-German comic characters in one art-directed world. Pipeline: 10 deck words → story LLM → screenplay LLM → prompt-writer → [Gate 1: approve before spending] → 10 scene videos + combined episode → [Gate 2: approve before publishing] → Instagram. **V2 vision (pivoted 2026-07-14 from the V1 learner app — V1 docs in git history).**

## Working agreement (overrides default behavior)

This is Jayon's **learning-by-doing** project. Success = his understanding, not shipped code.

- Never build ahead of the current phase; one step at a time; phases are discussed and explicitly locked before moving on.
- Actively teach: explain new concepts before implementing; point to what to learn.
- **Mandatory research step:** every phase and significant design decision starts with background research (web evidence, prior art) recorded as `docs/planning/RESEARCH_*.md` BEFORE deciding. Big decisions: researched options with proof → **Jayon decides**.
- All project context lives in files (below), never only in chat — future sessions and other tools must pick up cold.
- New ideas mid-phase → PARKING LOT in `docs/project_status.md`, not into scope (see RISKS doc R9).

## Model selection (for sessions, subagents, and handoffs)

Name the model tier in every delegation. Rule of thumb — match cost to irreversibility:

| Tier | Use for | Examples here |
|---|---|---|
| **Haiku 4.5** | Mechanical, low-ambiguity work | doc formatting, JSON wrangling, renames, changelog entries, simple n8n node edits |
| **Sonnet 5** | DEFAULT workhorse | building workflows/scripts, story-prompt iteration, routine research, most phases' implementation |
| **Opus 4.8** | Complex/architectural, hard debugging, multi-constraint design | pipeline chain design, gnarly consistency debugging, evaluator-prompt design |
| **Fable 5** | Rare: hardest cross-cutting synthesis where being wrong is expensive | major pivots/strategy re-planning, deep multi-source research synthesis |

Switch DOWN eagerly (Haiku for chores), UP only when a task resists two attempts at the current tier. In-pipeline LLM calls: story/screenplay = Sonnet 5 (locked); evaluator/checklist passes = Haiku 4.5 first, upgrade only if rubber-stamping (R10).

## Source of truth (read before planning any work)

- `docs/planning/PROJECT_GOAL_AND_MILESTONES.md` — V2 vision, milestones, working agreement
- `docs/planning/BUILD_PLAN_MVP.md` — phases C1–C7 (B0–B2 done, reusable)
- `docs/planning/RISKS_AND_REALITY_CHECKS.md` — known failure modes; consult before big spends
- `docs/planning/RESEARCH_*.md` — evidence library (efficacy, story design, video models, Instagram market, business strategy)
- `docs/architecture.md` · `docs/changelog.md` · `docs/project_status.md` — living docs, update after every meaningful change
- `docs/planning/CHARACTER_ART_BIBLE.md` — (C1, upcoming) canonical characters + art style; ALL visual generation derives from it

## Hard constraints

- Secrets only in `.env` (git-ignored); provisioning is just-in-time.
- Video-model choice stays open until C3's win condition; never hardcode a model into pipeline design.
- **Never spend video credits on a script that hasn't passed Gate 1**; never publish without Gate 2.
- Language in stories: A1/A2, short sentences; characters always true to their trait sheets; max 2 main characters per story.
- n8n workflows exported as JSON to `workflows/` whenever changed — the repo, not the instance, is the source of truth.

## Conventions

- Branch per feature; commit style `type: summary`; never commit generated media.
- After finishing work: update `docs/changelog.md` + `docs/project_status.md` (and `docs/architecture.md` if structure changed) — or run `/update-docs`.

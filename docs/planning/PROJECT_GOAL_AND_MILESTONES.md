# Project Goal & Milestones — V2 (THE PIVOT)

**Project:** Stereotypical German — automated comprehensible-input story content for Instagram
**Status:** V2 DRAFT — supersedes V1 (learner app) per Jayon's pivot, 2026-07-14. V1 text preserved in git history of this file.
**Owners:** Jayon (creator, decision-maker) · Claude Code (command center: structure, research, tutoring, execution support)

---

## 1. The Vision (V2 — Jayon, 2026-07-14)

An **Instagram page** built on a self-made world: **four stereotypical-German comic characters** (Jayon's original creations — trait sheets coming in the Character & Art Bible) in a consistent, deliberately art-directed universe. Purpose: **teach German in an entertaining, engaging way through simple stories you can watch every day.**

- Daily content keeps the **Anki-derived structure**: 10 words/day from the 605-word deck → one story → 10 scenes (one word each) → combined story video. Exact posting format (scene-by-scene? word-reveal-then-scene? combined only?) = OPEN design question, to be tested against real audience data.
- Stories: any genre, weird/absurd welcome — **absurdity and quirk are the product** — but structured (fixed episode skeleton), **max 2 main characters per story** (guest appearances allowed per scene), characters always true to their trait sheets, language strictly A1/A2.
- **Quality is the differentiator.** Observed competitors (e.g. "Deutsche Aktive"-style automated pages) get views with careless AI slop. Our position: *visibly deliberate* — real art direction, real characters, real pedagogy. "AI-made, but made with intention."
- The world is the asset: once characters + art style exist, other series run on the same universe (podcast, news-roast, specials) as parallel pipelines later.

## 2. The Pipeline (target architecture)

```
10 words (Supabase, Anki structure)
  → STORY LLM (genre-free, trait-faithful, A1/A2, absurd-but-structured)
  → SCREENPLAY LLM (scene-by-scene dissection: CI values, dialogue,
     word placement, video-model limitations respected)
  → PROMPT-WRITER stage (per scene: character sheets + art-style bible
     → strict video prompts)
  → [GATE 1: Jayon approves BEFORE video credits are spent]
  → 10 scene videos (consistency via reference images / frame chaining)
  → assembly → combined video
  → [GATE 2: Jayon approves BEFORE publishing]
  → scheduled Instagram posting
```

**2026-07-18 additions:** every run starts from a Run Context Pack (mission+canon+series-memory digest) so the automation acts like a creator who knows the whole project; a run ledger + series memory make history verifiable; Jayon chooses among 3 story premises at Gate A; /tune is the governed way to change any pipeline behavior. Detail: EXECUTION_PLAN_text_pipeline.md.

Quality loops ("loop engineering") at each LLM stage: outputs evaluated against checklists before flowing downstream — never waste video credits on a weak script. The human gates are FEATURES of the design, not gaps in it.

## 3. Intention (unchanged from V1)

**Learning by doing remains the primary goal** — AI automation, pipelines, agents; success = Jayon understands every part he built. New secondary goals: audience reach, portfolio value for gen-AI work in Germany, later monetization options (see STRATEGY_business_direction.md).

## 4. Milestones (V2)

| Version | Core | Done means |
|---|---|---|
| **MVP** | Full pipeline words → story → screenplay → prompts → [gate] → 10 scenes + combined video → [gate] → posted. Characters + art style established. Video step may be semi-manual. | 3 consecutive daily episodes published end-to-end through both gates. |
| **v1** | Quality-evaluation loops before every spend, scheduling, posting-format testing against audience data, cost tuning. | Pipeline runs for days; Jayon touches only the two gates. |
| **v2** | Parallel series on the same world (podcast, news-roast); optionally the learner app as premium layer; B2B samples. | A second content format is live. |

**Explicitly parked (from V1):** React learner app + recall-first session flow (the fixed deck still yields a ~61-episode course later — STRATEGY doc §1); AnkiConnect integration.

## 5. Working agreement (V2 — two additions)

All V1 rules stand: one phase at a time, phases locked explicitly, teach-first, researched options + Jayon decides, all context lives in repo files. New:

1. **Mandatory research step:** every phase and significant design decision begins with background research (web evidence, prior art, forums) recorded as `docs/planning/RESEARCH_*.md` BEFORE deciding. No decisions from vibes.
2. **Model selection accompanies every delegation:** each handoff/sub-task names the Claude model tier to use (CLAUDE.md → "Model selection"), so tokens are spent where intelligence is needed.

## 6. Current position

- [x] V1 Plan/Setup + B0 (n8n engine) + B1 (word source, 605 words) + B2 (story stage, 3 validated stories) — ALL still load-bearing for V2
- [x] Research library: efficacy, story design, video models/cost, Instagram market, business direction
- [x] PIVOT recorded (2026-07-14, this doc) + risks register (RISKS_AND_REALITY_CHECKS.md)
- [x] V2 build plan · C1 ~80% (cast canon; style system pending) · C2 v1 proven → **NOW: EXECUTION_PLAN_text_pipeline.md (E1–E7 in Antigravity)** → then C3 video prototyping

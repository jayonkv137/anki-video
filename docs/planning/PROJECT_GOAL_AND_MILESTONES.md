# Project Goal & Milestones

**Project:** Anki Video — comprehensible-input story videos for daily Anki words
**Status:** LOCKED (confirmed by Jayon, 2026-07-13)
**Post-research decision (2026-07-13):** After the efficacy/competitor research (`RESEARCH_efficacy_and_competitors.md`), Jayon chose to keep the full story-video concept as-is — the story + video generation challenge IS the learning goal. Cost/coherence mitigations (word-type routing, recurring characters, clip caching) are noted as v1+ options, not MVP scope.
**Created:** 2026-07-13
**Owners:** Jayon (builder, decision-maker) · Claude Code (command center: structure, research, tutoring, execution support)

---

## 1. The End Goal (what we are building)

A mobile-friendly app for an Anki German learner using the Fluent Forever 625-based German deck (AnkiWeb 1970793696), learning ~10 new words per day:

1. The learner recalls a word first, Anki-style (German word shown → active retrieval). **Recall always comes first.**
2. After recall, a short AI-generated comprehensible-input video plays, showing that word in action — visually, contextually, with audio, in a narrative scene.
3. Each word's video is one scene of a single continuous story for that session.
4. At the end of the session, the full combined story video (all 10 words woven together) plays as the finale.
5. When the learner returns the next day, the new day's story and videos are already generated and waiting.

**Locked design principle (from research):** the video is feedback and reward after retrieval — it never replaces active recall. This preserves the testing effect that makes Anki work.

## 2. The Intention (why we are doing it)

The app is the vehicle; the destination is **learning by doing**.

- Jayon's primary goal is to learn AI automation, pipeline building, agents, and the full anatomy of a real production-style system — by designing and building every part himself, with Claude as guide.
- **Success is defined by understanding, not polish.** A rough, ugly MVP that Jayon fully understands end-to-end is a win. A beautiful app he can't explain is a failure.
- At each stage, Claude directs Jayon to the foundational concepts he needs, asks sharpening questions, and never dumps finished solutions ahead of the current phase.

## 3. Milestones

| Version | Core functionality | Done means |
|---|---|---|
| **MVP** | Fully automated pipeline: today's 10 words in → 10 scene videos + 1 combined story video out, next day's batch ready before the user arrives — shown in a simple app UI. Skeleton quality is fine: consistent story template, basic video style, no fine-tuning. | The full loop runs without manual steps and the output is watchable end-to-end. |
| **v1** | Improve the core: better story generation, better/more consistent video output. Still core functionality only. | Noticeably better stories and videos on the same pipeline. |
| **v2** | Support for more deck types (where feasible). Improved story prompts, fine-tuned consistent video style. UI improvements. | Works beyond the single starting deck; videos have a deliberate, consistent style. |
| **v3** | Ambitious / speculative features discovered along the way. | Defined later. |

**Not in scope for MVP:** perfect stories, polished video style, multiple decks, multiple languages, auth/accounts, production hardening.

## 4. How we work (the working agreement)

- **Process:** PSB — Plan → Setup → Build. Strictly one phase at a time; each phase is discussed and explicitly agreed before moving on.
  1. **Plan:** this doc → Product Requirements → Engineering Requirements (tool decisions researched with proof, decided one at a time together) → provision infra.
  2. **Setup:** GitHub repo, .env, CLAUDE.md, automated docs (architecture.md, changelog.md, project_status.md, reference docs), plugins, MCPs, slash commands.
  3. **Build:** phased sub-goals, each with a win condition **and** a learning objective for Jayon. Plan mode before implementing.
- **Command center:** this Claude Code chat. Antigravity IDE (Opus, Sonnet, Gemini) is used for overflow/execution tasks when handed a self-contained prompt.
- **Consequence:** all project context lives in documents in this folder — never only in chat memory — so any tool (Claude Code, Antigravity, future sessions) can pick up the full context.
- **Project home:** `~/Desktop/Anki Video/` — planning docs at top level, `Context Docs From other chats/` for chat context, code in a repo folder created during Setup.

## 5. Current position

- [x] Step 1 — Goal & Intentions + Milestones (this doc; awaiting lock)
- [x] Step 2a — Product Requirements (LOCKED 2026-07-13)
- [x] Step 2b — Engineering Requirements (complete draft 2026-07-13; awaiting lock)
- [x] Step 2c — Provisioning policy: JUST-IN-TIME — each service provisioned at the build step that first needs it (checklist tracked in Engineering Requirements doc)
- [ ] Phase 2 — Claude Code setup
- [ ] Phase 3 — Build MVP

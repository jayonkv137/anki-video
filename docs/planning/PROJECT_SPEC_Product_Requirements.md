# Project Spec — Product Requirements

**2026-07-18 (V2 product behavior additions, authoritative in EXECUTION_PLAN_text_pipeline.md):** Jayon selects among 3 story-premise options at Gate A (with optional steering note); every run is initialized with full project context + episode history; all pipeline behavior changes go through the versioned /tune process.

**Status:** V1 — SUPERSEDED by the 2026-07-14 pivot (see PROJECT_GOAL_AND_MILESTONES.md V2). Kept as reference: the pipeline structure (10 words → story → 10 scenes → combined video) and story rules survive; the learner app + recall-first session flow are PARKED. A V2 product spec (Instagram content product) will be drafted during C1/C6 design steps.
**Date:** 2026-07-13 · Supersedes `Project Spec Product Requirements.docx` (original draft kept for reference)
**Related:** `PROJECT_GOAL_AND_MILESTONES.md` (locked) · `RESEARCH_efficacy_and_competitors.md`

---

## 1. Product purpose

For language learners using Anki-style spaced repetition to learn vocabulary: combine active recall (SRS) with an AI-generated **comprehensible-input story video** for each new word — visual, contextual, narrative — as an additional learning aid to improve retention and make daily review genuinely enjoyable.

## 2. Who is it for?

- **MVP persona:** a German learner working through the Fluent Forever 625-based deck (AnkiWeb 1970793696) at ~10 new words/day. Concretely: Jayon himself.
- **Eventually:** anyone using SRS flashcards to learn vocabulary (v2+).

## 3. What problem does it solve?

Bare flashcards give a word only one retrieval path (text). Learners forget words they "know," and daily review is boring — boredom raises the affective filter and kills consistency. This product gives every new word a story-scene video (dual coding: visual + audio + narrative context) and turns finishing the session into a reward (the combined story), attacking both retention and motivation.

## 4. What does the product do? (core mechanic)

Every day, for that day's 10 new words:

1. Generate **one coherent story** that properly uses all 10 target words (other known vocabulary may appear freely; the 10 targets must each be genuinely used).
2. Split the story into **10 scenes — one scene per word** — each scene advancing the story, not standalone clips.
3. Render each scene as a short video (**~6–8 s**, German audio; exact on-screen elements decided in the design stage).
4. Produce a **combined full-story video** (all scenes stitched, ~60–80 s) as the session finale.
5. Have **tomorrow's batch pre-generated** before the user returns — this is a pipeline that runs every day, mirroring Anki's daily rhythm.

## 5. The user experience (specific flow — decided 2026-07-13)

**Platform (MVP): standalone app — no Anki dependency.** The 625 deck is imported once into the app's own word store; a simple scheduler serves the next 10 unseen words each day. The pipeline reads words through a **"word source" abstraction** so AnkiConnect can swap in at v1 without changing anything downstream.

**Daily session, screen by screen (in-app recall — locked):**

1. User opens the app → today's session is ready (pre-generated overnight).
2. **Word card:** German word shown alone. User attempts recall (active retrieval). *(Amended 2026-07-13: words are presented in STORY order, not deck order — the LLM assigns each word its scene; see RESEARCH_story_design.md §4.)*
3. User taps **reveal** → meaning/translation shown → user **self-grades** (knew it / didn't).
4. **Only then** the word's story-scene video plays (~6–8 s). → next word.
5. After all 10 words: the **combined story video** plays as the finale/reward.
6. Session ends. Overnight, the pipeline generates tomorrow's story + videos for the next 10 words.

**Locked pedagogical rule:** the video NEVER appears before the recall attempt. Recall-first is load-bearing (see research doc §2c) — video is feedback/reward, not study material shown up front.

## 6. Deliberately deferred to their own design stages (per the plan-as-we-go method)

These get researched, prototyped (2–3 sample videos), and decided when we reach them in the Build phase — not now:

- **Video style / design language** (2D animated vs whiteboard vs other; the consistent visual template)
- **Exact scene composition** (subtitles? target word on screen? camera language?)
- **Story template & prompt design** (how 10 words become one coherent narrative — flagged as the top quality risk in the research doc)
- **Voice/narration style**

## 7. MVP definition of done

Today's 10 words in → 10 scene videos + 1 combined story video out, fully automated, viewable in the simple app flow above, with tomorrow's batch ready before the user returns. Skeleton quality acceptable everywhere; the loop must be real.

## 8. Out of scope for MVP

- Anki/AnkiConnect sync (v1 — enabled by the word-source abstraction)
- Real SRS scheduling of reviews (MVP: fixed "next 10 unseen words"; only new words, no review-day logic)
- Multiple decks, languages, or users; auth/accounts
- Polished video style, story fine-tuning (v1/v2)
- Missed-day / partial-session handling (MVP: pipeline simply generates for the next 10 unseen words regardless)
- Cost optimization (clip caching, word-type routing — v1+ candidates from research doc §4)

## 9. Success criteria (beyond the loop working)

- Jayon can explain every stage of the pipeline and rebuilt-understanding is demonstrated at each phase gate (primary goal).
- The generated story actually uses all 10 words correctly and is watchable as one narrative (quality bar: "coherent," not "beautiful").
- Daily generation completes unattended (no manual steps).

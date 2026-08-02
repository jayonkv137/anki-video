# DESIGN — The Studio Chat (the control centre) + the LESSON layer

> **Status: PROPOSAL for Jayon's confirmation (2026-08-02).** Two things that turned out to be one thing: the always-available conversation with the *studio itself* (not an episode), and the **lesson layer** that conversation needs in order to be truthful.
> Triggered by Jayon's questions: *"is the stereotype mapping built?"* (no), *"does the whole system understand that a lesson is N episodes?"* (no — gap found), and *"how is the chat connected to the system, and what can it change?"*
> Companions: `DESIGN_screen_home.md` · `DESIGN_autopilot.md` · `PIPELINE.md` §3.9 (the change protocol) · `SHOW_BIBLE.md` §15 (the three maintenance tiers) · `DESIGN_universe_state.md`.

---

## 1 · The gap found while answering the question

`CURRICULUM` §2's module workflow has four steps. **Steps 1–2 are LESSON-scoped** (the Showrunner surfaces the module; Jayon and it agree the *block plan* — how many episodes this lesson needs and which topics go in each). **Step 3 is EPISODE-scoped.** `studio.py` models only step 3.

Consequence, verified in code: `block_no` exists on the brief and screenplay, but **nothing declares how many blocks a lesson has.** The interface cannot say "2 of 3 episodes" because the 3 is not stored anywhere.

### 1.1 The fix — a lesson layer above episodes

```
LESSON  A1.8 Regeln                          lesson.json      ← NEW
  · why this lesson exists, in plain language
  · its 6 topics
  · THE BLOCK PLAN: 3 episodes, topics distributed
  · the arc across them · the lead · the encounter (if any)
      ├── EPISODE 1 (block 1)  brief → screenplay → … → export
      ├── EPISODE 2 (block 2)
      └── EPISODE 3 (block 3)
```

- **`lesson.json`** lives at `output/lessons/<module_id>/`. It is an artifact with a gate like any other: **the lesson plan is approved once**, and every episode in that lesson inherits it.
- **The planning conversation is a lesson-level phase** ("Plan"), run once, not once per episode. The five episode phases are unchanged.
- **Re-planning a lesson** has a recompile set like everything else: changing the block plan invalidates the episodes not yet made, and *warns loudly* about the ones already exported.
- **`universe_state` gains `lesson_planned`** so progress is real: *Lesson 8 · 2 of 3 episodes*.

**Why it matters beyond the label:** without it, each episode re-derives its own context and nothing guarantees three episodes of one lesson form an arc rather than three unrelated 30-second gags. The block plan is where "this lesson is a story" is decided.

## 2 · The stereotype mapping — designed, never built

`DESIGN_stereotype_integration.md` specifies the tag schema (`module_affinity`, `structures`, `cefr_earliest`, `setting`, `visual_legibility`, `encounter_type`, `cast_affinity`) and the HOST / TEXTURE / RUNNER modes. **Verified 2026-08-02: 0 of 100 stereotypes carry any of it**, and `stereotypes.py` cannot match a stereotype to a lesson. The `encounter` slot in the brief schema is an empty socket.

**The work (one time, ~2 hours):** an AI pass tags all 100 against the 30 lessons → Jayon reviews in a simple accept/adjust screen → `stereotypes.py` gains `suggest_for_lesson(module_id, level)` doing a **deterministic filter** (module affinity · level ≤ current · visual legibility high · not covered) then a rank (locked location > cast fit > variety > never used). **Zero matches is a valid answer and must be said plainly.**

**Where it surfaces:** the Lesson Plan conversation offers 0–3, with the reason. Never forced, never a quota, one HOST per episode maximum.

## 3 · The Studio Chat — what it is

**One continuous conversation with the studio itself.** Not an episode. It is where Jayon arrives when the thought is not "make episode 47" but *"how is the story going"*, *"I had an idea"*, *"Kati should be different now"*, *"what have we taught?"*, *"here's a script I wrote"*.

It is the **control centre**: it knows everything, it can change most things, and everything it changes goes through propose → show consequences → confirm.

### 3.1 Its character
Not a chatbot, not an assistant. **The producer who has been on the show since episode one.** Concretely:
- **It knows the show better than it knows you.** It answers about *the work*, not about itself.
- **It states, then offers.** "Kati hasn't led since A1.4. Lesson 9 is time and order — that's her. Want her?" — not "How can I help you today?"
- **It disagrees.** Canon-backed pushback is required, not optional: *"That contradicts A1.6 — the bakery was established in Hamburg. Change the fact, or change the scene?"* An agent that agrees with everything is useless to a creator (`Production Engineering Guide`, anti-sycophancy).
- **It never fabricates.** "I don't know" and "that hasn't been decided" are correct answers. It never invents a fact to be helpful.
- **It asks one question, not five**, and only when the answer is structural.
- **No filler.** No "Great idea!", no "I'd be happy to", no re-stating the request before answering.

### 3.2 What it knows (context, assembled deterministically)
Tier 1 canon (MISSION · SHOW_BIBLE · STORY_SYSTEM · PEDAGOGY — the whole knowledge layer, since it is not a station) · the curriculum and live teaching status · `UNIVERSE_STATE` strata 2–4 (world, relationships, progression, standing decisions) · the lesson/episode index with each one's stage · the seed bank · the stereotype library. **Never** an episode's internal conversation — for that it opens the episode.

## 4 · What can be changed — the complete map

Jayon asked for *every possibility in the system that can be edited*. This is it, with who may write and by what process. **This table is the chat's actual specification.**

| # | What | Where it lives | Who writes | Process |
|---|---|---|---|---|
| 1 | **Identity canon** — premise, the conceit, tone, a character's core, world rules, naming | `SHOW_BIBLE` §1–9,12,13 (Tier 1) | **Jayon only** | chat **proposes** → shows the diff and what it affects → Jayon confirms → the `/tune` ritual runs (version bump, rehash, registry, commit). Agents never write Tier 1. |
| 2 | **Directions** — arcs being considered, threads to plant, people they might meet | `SHOW_BIBLE` §10 → `UNIVERSE_STATE` s2 | Jayon freely; chat may suggest | **write immediately.** No ceremony — this is where ideas go to survive, and friction here means they stop being written down. |
| 3 | **Canon facts** — what episodes established | §11 → `UNIVERSE_STATE` s2 | pipeline, on confirmation | **contradiction-checked first**; a conflict halts and asks (built + tested). Never silently overwritten. |
| 4 | **Character state** — where they are, what they want now, wardrobe deltas | `UNIVERSE_STATE` s2 | chat, on confirmation | propose → confirm. Distinguishes *identity* (§1, Tier 1) from *state* (changes constantly). |
| 5 | **Relationships** — the evolving matrix | s2 | chat, on confirmation | propose → confirm. The premise is four strangers finding each other; this must move. |
| 6 | **Locations & tonal modes** | s2 | chat / Vision phase | created once, reused identically forever (`TREATMENT` §6.3) |
| 7 | **Standing decisions** — approvals that bind, rejections that persist, taste notes | s4 | chat, explicitly | **This is the flywheel.** Every "never do that again" becomes a constraint injected into every later generation. |
| 8 | **The seed bank** | s2 (`direction`, tagged `seed`) | Jayon, freely | write immediately; drawn and marked consumed by Draft mode |
| 9 | **Lesson block plan** — how many episodes, which topics in each | `lesson.json` (§1.1) | chat (the Plan phase) | approved once per lesson; re-planning warns about episodes already made |
| 10 | **Curriculum order / content** | `curriculum.json` (registry-pinned) | **Jayon only** | propose → confirm → rebuild + re-pin. Rare and deliberate — this is the spine. |
| 11 | **Stereotype tags & coverage** | `stereotypes_library.json` | AI pass + Jayon review | one-time tagging; coverage marked automatically |
| 12 | **Episode artifacts** — brief, screenplay, boards, prompts, subtitles | `output/episodes/<id>/` | the episode's own change protocol | **the chat routes, it does not reach in.** It opens the episode at the right phase. |
| 13 | **Reference assets** — character sheets, style plate, location plates, the fused contact sheet | `resources/` + s2 | Jayon uploads; chat registers | new assets are registered with what they supersede (`TREATMENT` §9) |
| 14 | **Visual/production law** — TREATMENT, PEDAGOGY numbers | canon, Tier 1 | **Jayon only** | propose → `/tune`. When a real episode disproves a number, that is a Tier-1 edit, not a drift. |
| 15 | **Publishing** | — | **Jayon only, manually** | never delegated, permanently |

**Three rules over the whole table:** (a) anything hash-pinned is *proposed*, never written by an agent; (b) anything that could contradict established fact is checked before it is written; (c) **every write is journaled** — the chat's history is the audit trail of how the world changed.

## 5 · Routing — the chat is a front door, not a workshop

Its jobs split cleanly into four, and it must recognise which one it is in:

1. **ANSWER** — status, story so far, what a character has done, what's been taught. Read-only, no ceremony.
2. **RECEIVE** — an idea, a seed, a script, an observation. **Default is to store, not to act.** "Filed to Directions" is a complete and correct outcome; jumping to "shall I write it?" is how a creator stops sharing half-formed thoughts.
3. **CHANGE** — anything in §4. Propose → consequences → confirm.
4. **ROUTE** — *"start lesson 9"*, *"continue Bei Rot"*, *"the boards for episode 2 are wrong"* → hands off to the lesson or episode workspace **at the right phase**, carrying the intent. It does not do the episode's work in the chat.

**The distinction that matters:** the studio chat is where you change *the world*; the episode chat is where you make *one thing*. Blur them and the world gets edited by accident while you are thinking about a shot.

## 6 · Edge cases — decided in advance

| Situation | Behaviour |
|---|---|
| Vague idea (*"something about queues"*) | file it as a seed; **do not** interrogate it into a scene |
| Idea contradicts canon | say which rule, offer both routes (change the idea / change the rule) — never silently pick |
| Asked for a fact we don't have | "not established" — offer to establish it, never invent |
| Change would invalidate finished work | show the blast radius **and the money already spent** before confirming |
| Character change mid-lesson | asks whether it applies from the *next* episode or retroactively (retroactive = re-plan) |
| Jayon changes his mind about a standing rejection | rejections are revocable, and revoking is a journaled decision |
| State unreachable | say so and refuse writes; a chat that silently loses a decision is worse than one that is down |
| Two contradicting instructions in one message | do the unambiguous part, ask about the other |
| A drop of ten ideas at once | file all ten, confirm the count, do not respond to each |
| Something outside the studio (deploy, billing, pricing) | say plainly it is out of scope |

## 7 · The three-screen shape (Jayon's structure, confirmed)

1. **The Universe** — the landing. The world, the characters, the story so far. Showcase and orientation. → *Continue the story*
2. **The Studio Chat** — the control centre described here. The everyday home.
3. **The workspaces** — a lesson plan, or an episode's five phases.
Plus **Curriculum — one page**, all 30 lessons.

## 8 · Build order

1. **The lesson layer** (§1.1) — `lesson.json`, the Plan phase, `lesson_planned` in state, `2 of 3` everywhere. *Blocks the Idea phase; do it first.*
2. **The stereotype tagging pass** (§2) + `suggest_for_lesson`. *Cheap; makes the Plan conversation good.*
3. **The studio chat** — context assembly, the §4 change map, the §5 router, the §6 edge cases.
4. Screens, once the design is settled.

## 9 · Open for Jayon

1. **Does the Plan phase get its own gate**, or is approving the block plan part of the first episode's Idea gate? *(I recommend its own — it is a real decision that three episodes inherit.)*
2. **Can a lesson's episode count change after episodes exist?** *(I recommend yes, with a loud warning naming what was already made.)*
3. **Should the chat be able to start generations at all**, or only route? *(I recommend route only — spend belongs where the artifact is visible.)*

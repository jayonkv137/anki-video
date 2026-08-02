# DESIGN — Screen 01: HOME

> **Status: BRIEF for Jayon's confirmation (2026-08-02).** The first of the screen-by-screen rebuild. The 2.2 wireframe's Home was rejected: it rendered the data model instead of designing a screen. This is the brief that should have existed before any pixels.
> **Governing principle, Jayon's words: KISS — keep it stupid simple.**
> Companions: `DESIGN_studio_ux.md` (the five phases) · `DESIGN_autopilot.md` (the two modes) · `DESIGN_screenplay_document.md` (screen 02).

---

## 0 · The naming correction that comes first

`CURRICULUM_v1_universe.md` calls the atoms "lessons" ("10 modules · 61 lessons"). **That word is wrong and it leaked into the interface**, which is why Home showed `A1.8.4` as "the lesson" and read as code.

| Term | Is | Count | Where the user meets it |
|---|---|---|---|
| **Lesson** | a module — `A1.1 Ankunft` | **30** | everywhere. This is the unit a person thinks in. |
| **Topic** | an atom — `A1.1.1 … A1.1.6` | 164 | inside a lesson, on the Curriculum page |
| **Episode** | one ~30s video | **N per lesson**, decided at the brief | the thing you actually make |

**A lesson is not one episode.** At the brief, Jayon decides this lesson needs 2, or 3, or 4 — because that is what the content honestly requires. The interface must show that relationship (`Lesson 8 · 2 of 3 episodes`), never imply one-to-one. Data is unaffected (`curriculum.json` is already modules→atoms); the fix is language + presentation.

## 1 · Who arrives here, and what they need in five seconds

Six users, and they are not variations of one person. The screen is only right if all six are served **without adding anything**.

| # | Who | Their state of mind | What they need first |
|---|---|---|---|
| 1 | **Jayon, returning** (most common) | "where was I" | the unfinished thing, one click |
| 2 | **Jayon, starting today** | "what's next" | the next lesson, plainly named |
| 3 | **Jayon, with an idea** | "I thought of something" | somewhere to just *say it* |
| 4 | **Jayon, late** (ep 120) | "where does the series stand" | the story so far, the shape of the whole |
| 5 | **A new person he hires** | "what IS this? what do I do?" | orientation without a manual |
| 6 | **LinkedIn / a client** | "is this real? is this any good?" | **the universe** — craft, characters, world |

**The tension, named honestly:** 1–4 want a tool; 6 wants a showcase; 5 wants orientation. The wrong resolution is to add a marketing header to a dashboard.

**The right resolution:** the best creative tools *are* showcases, because they show **the work**. Figma's file browser, a DAW's waveforms, an NLE's bins. The impressiveness comes from presenting the work with restraint — never from decoration. So Home shows **the universe and what has been made of it**, and hides everything that is the system talking about itself.

This also solves user 5 for free: a newcomer who can see the characters, the story so far, and a chat box can simply *ask*. That is the most forgiving onboarding that exists, and it costs one input field.

## 2 · What was on the old Home, and why each thing is wrong

| Was there | Verdict |
|---|---|
| `A1.8 Regeln · block 3 of 4` | **Cut.** Internal production scheduling. "Block 3 of 4" is a fact about our pipeline, not about his work. |
| `teaches A1.8.4 — dürfen + man` | **Cut from Home.** Code, not language. Belongs on the Curriculum page where someone is *studying* the course. |
| `lead rec: Müller das Brot (coldest in rotation)` | **Cut.** Exposes the algorithm rather than the decision. The Showrunner can *say* it in conversation, where a reason belongs. |
| Five Co-create/Draft toggles | **Cut.** A settings panel wearing a hat. Nobody configures five things before starting. Default them; switch inside the episode, where the phase is actually happening. |
| The 164-square grid | **Cut.** A progress bar pretending to be information. Nobody can read 164 squares. |
| `Draft mode will draw one seed: "…"` | **Cut.** Implementation detail narrated at the user. |
| Seed bank, full list | **Moved.** It is an input surface, not a landing surface. |

Removing all of it leaves the screen with almost nothing on it — **which is the point.**

## 3 · The structure — one input, two actions, one universe

### 3.1 THE CHAT — the primary way in *(new; Jayon's core ask)*
A single always-available conversation with the **studio itself**, not with an episode. It is the first thing on the screen and the widest.

It exists because the most common real thought is not "start episode 47" — it is *"how is the story going?"*, *"I had an idea"*, *"change something about Kati"*, *"what have we taught so far?"*, *"here's a script I wrote"*.

What it can do:
- **answer** — status, story so far, what's been taught, what a character has been doing
- **receive** — ideas and seeds, story directions, future arcs, a script pasted in, a note about a character
- **change** — propose edits to the world (a character trait, a story beat, a planned arc, curriculum order) through the same propose → show consequences → confirm protocol the episodes use
- **route** — "start the next lesson" typed as a sentence should just work

Design consequences: it is an *input*, not a transcript wall — it opens as one line with the history one scroll away. Series-level changes are **proposals**, never silent writes, because this chat can touch canon and state.

### 3.2 CONTINUE — only when it exists
One card, only if something is unfinished. What it is, where it stopped, in plain words: *"Lesson 8, episode 2 — the script is drafted and waiting for you."* Nothing else. If nothing is unfinished, **the card is not there** (not an empty state with a sad face — simply absent).

### 3.3 START THE NEXT LESSON — minimal
Jayon's instruction, taken literally: *the German lesson number and a description. That's all.*

> **Lesson 8 — Regeln**
> Rules and permission: what you may and may not do.
> *2 of 3 episodes made.*

No grammar codes, no lead recommendation, no mode toggles, no atom list. All of it is available on the Curriculum page for whoever wants it; none of it belongs on the first screen. **Starting is one click, and the conversation about *what* this episode is happens where it belongs — in the Idea phase, with the Showrunner.**

### 3.4 THE UNIVERSE — the showcase layer, which is also the orientation layer
The four characters, present and beautiful. Not avatars in a settings row — the actual world. Plus one line of *story so far*.

This is what makes user 6 take it seriously and user 5 understand it, and it costs the working users nothing because they are not reading it — they are clicking Continue.

### 3.5 NAVIGATION — four places, no more
- **Curriculum** — the whole course, Nicos-Weg style: 30 lessons, numbered, plainly named, each showing its topics and its episodes. Browsable and meaningful, *not* a grid of squares.
- **Characters** — a page per character: art, who they are, their arc, where they are in the story, what they have appeared in.
- **Story** — the story so far: what has happened, established facts, threads planted and unpaid, the directions Jayon is circling.
- **Episodes** — everything made, as real frames. This doubles as the portfolio view.

## 4 · The interaction rules that keep it simple

1. **Nothing on Home configures anything.** Every setting has a home *inside* the thing it affects.
2. **No abbreviation a stranger cannot read.** `A1.8.4`, "block 3 of 4", "coldest in rotation" — none of it survives to Home. Codes live on the Curriculum page, where they are the subject.
3. **Absent beats empty.** If there is nothing to continue, no card. The screen should feel different on day 1 and day 200 because it *has* different content, not because it has different placeholders.
4. **One primary action.** Continue if it exists; otherwise start the next lesson. Never two competing dark buttons.
5. **The chat is always reachable and never modal.**

## 5 · The states this screen has

| State | What Home shows |
|---|---|
| **Day one** (nothing made) | the universe + the chat + Lesson 1. No Continue. The chat carries onboarding. |
| **Something unfinished** | Continue first, everything else quieter |
| **Nothing unfinished** | Start the next lesson is primary |
| **A lesson part-made** (2 of 3 episodes) | Continue shows the *lesson's* remaining episode, not a new lesson |
| **Series complete** | the archive becomes the point |
| **State unreachable** (Supabase down) | say so plainly at the top; do not render zeros as if they were true |

## 6 · The future look — recorded, not yet actioned

Jayon's reference for a **later** visual direction (supplied 2026-08-02): a cinematic dark-space landing page — full-bleed video, heavy display type, a single neon accent, glass-morphic panels, the characters as the subject. The intent: **the landing page should feel like the universe itself**, with the four characters, the story and the genre carrying it.

Recorded as direction, deliberately **not** built now: the structure has to be right before it is dressed, and a cinematic treatment on an unresolved layout hides the problems instead of solving them. Revisit once Home's structure is settled and the first real episodes (and character renders) exist to fill it — at which point the showcase is made of *real work*, which is the only thing that would actually impress user 6.

## 7 · Open questions for Jayon

1. **Does the chat lead, or does Continue lead?** My instinct: the chat is the widest element and sits first, because it serves the most common real thought and it onboards a stranger — but Continue is the most *frequent click*. Both can be above the fold; which one is the eye's first stop?
2. **How much universe on Home?** Four characters as the visual anchor, or one line of "story so far" and the characters live on their own page?
3. **Curriculum: one page or two levels?** All 30 lessons in a single scroll, or A1/A2/B1 as sections you open?
4. **A reference.** One tool whose home screen you like — naming it tells me more than a paragraph. (Cosmos is a good place to pull two or three.)

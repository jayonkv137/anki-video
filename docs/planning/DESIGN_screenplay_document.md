# DESIGN — The Screenplay Document (the AI screenplay: what it contains, how it reads, how it is shown)

> **Status: PROPOSAL for Jayon's confirmation (2026-08-02).** Answers the question no document answered: *what does our AI screenplay actually look like — as a finished, readable artifact — and how is it shown after the script is confirmed?*
> **This document derives; it never restates.** Field law lives in `TREATMENT.md` §15 (the per-shot/per-segment specification). The machine contract lives in `pipeline/schemas.py` (`SCREENPLAY_V4`). Method lives in `STORY_SYSTEM.md`. **If this document ever disagrees with those, they win** — a second source of field law is exactly the drift that retired `canon_blocks.md`.
> Companions: `PIPELINE.md` §3.4 (the Writer's station contract) · `PEDAGOGY.md` §8 (the audit) · `DESIGN_studio_ux.md` (the workspace) · `BUILD_PLAN_v4_studio.md` §7.
> Sourcing: the invideo guides *AI Script Breakdown* and *AI Shot Planning* (absorbed into TREATMENT v1.3, 2026-08-02).

---

## 1 · Why this exists

A traditional screenplay is prose that a crew interprets. **Ours is not prose — it is a shot plan that a model executes**, and the difference is total: a physical crew supplies continuity for free (same actor, same set, same light persist because they physically exist), while every generated clip renders in isolation with no memory of the one before it. Anything the plan does not carry, the render invents.

So our screenplay is three things at once, and it has three consumers:

| Consumer | Needs it to be |
|---|---|
| **The Writer** (produces it) | a complete brief — every field decided, nothing left for a compiler to guess |
| **QC** (audits it) | checkable — every rule expressible against a field |
| **Jayon** (reads, approves, edits it) | **legible as a film** — not a JSON dump |

The third has never been designed. That is what this document is for.

## 2 · Two views, one artifact

The screenplay has **two presentations**, and conflating them is why the old wizard's step 5 felt like a form:

- **The DRAFT view** — during the Script phase, while it is being written. Working, editable, incomplete-by-definition, QC chips amber. The creator is *authoring* here.
- **The SHEET** — after the lock. The full screenplay rendered as one continuous, formal document: every segment, every shot, every parameter, the dialogue in place, the subtitle preview, the reference requirements. Print-like. Scrollable. **This is the "show me the whole thing" view** — the artifact you read end-to-end before committing generation credits, and the thing you come back to at any later phase to see what was decided.

The lock is the transition. Confirming the screenplay does not just set a flag — **it changes how the document is presented**, from a thing being built into a thing that has been decided.

## 3 · The anatomy of the sheet

Top to bottom, the locked screenplay reads:

### 3.1 The head — what this episode is
One block, always visible (sticky on scroll):
> **Title (DE)** · format (`lesson · synthese · season_zero`)
> **Module** A1.8 *Regeln* — block 2 of 4 · **teaches** A1.8.4 `dürfen + man` · recycles A1.2.5, A1.8.3
> **Level** A1 — ceilings: ≤30 words · ≤8 per sentence · ≤5 new · ~80 WPM
> **Lead** Rolf die Wurst · with Müller das Brot
> **Environment** empty pedestrian crossing, 3 a.m. · **30 s** = 2 × 15 s
> **Target structure** `man darf hier nicht …`

Why the head carries the teaching data: the lesson is the reason the episode exists (`MISSION` §6), so it is the first thing read, not a footnote. The ceilings are shown *as numbers* because they are what the page is being judged against.

### 3.2 The segment band
Each segment opens with its own band — the properties that are **constant across every shot inside it**:
> **SEGMENT 1** · 15 s · night, dry · **tonal mode:** Sodium Street Night · **atmosphere:** light haze

Segment-level, not shot-level, is a rule with teeth (`TREATMENT` §6.5, §8.1): a tonal mode or an atmosphere that changes between two shots of one continuous moment makes the cut read as a location change. Showing them on the band is what makes a violation *visible* rather than buried in a field.

### 3.3 The shot block — the unit of the document
Every shot renders as one block. This is the heart of the format:

```
┌─ SHOT 1 ────────────────────────────────────── 8 s ─┐
│  MS · eye-level · static, locked-off, subtle        │
│  handheld breathing · DOF deep                      │
│                                                     │
│  Rolf die Wurst stops at the empty crossing.        │
│                                                     │
│  BLOCKING   Rolf die Wurst centre midground         │
│  GAZE       at the red light                        │
│  EXPRESSION flat disbelief                          │
│  LIGHT      sodium street lamp camera-left · 70:30  │
│  PROPS      —                                       │
│                                                     │
│      ROLF DIE WURST                                 │
│           Warum?                                    │
│           (Why?)                                    │
│                                                     │
│  ▸ negative: —   ▸ revision: hold the frame, re-run │
└─────────────────────────────────────────────────────┘
```

Design decisions inside that block, each with a reason:

- **The action is the largest text.** It is the one thing that must read at a glance, and it is what the model actually renders. Everything else is specification around it.
- **Camera line sits under the shot number**, in the canon vocabulary (`TREATMENT` §4) — the grammar of the cut, readable as a strip when you scan the whole segment.
- **Dialogue uses screenplay convention** — speaker centred and capitalised, line beneath, English in parentheses. This is the one place we borrow traditional formatting, because it is the only part a human reads *as performance*. The German is what ships; the English is a gloss and is never rendered on screen (`PEDAGOGY` §5.1 — no translation line, ever).
- **The technical fields are labelled and aligned**, not prose. They are checked, not read.
- **Negative and revision prompts sit at the foot**, dimmed — present because `TREATMENT` §15 requires them, quiet because they only matter when something failed.
- **Duration is on the shot's right edge**, so a segment's shots visually sum to their 15 s.

### 3.4 Flags that change the block
Two flags are drawn on the block itself, because they carry a **pre-generation obligation** (`TREATMENT` §8.2):
- **⚯ CONTACT** — needs a fused reference sheet of the two bodies in their arrangement before this shot can be generated.
- **⌖ BLOCKING REF** — POV or complex camera; needs a phone-mock reference.
A flagged shot is not blocked from existing — it is blocked from being *generated* until its reference exists. The sheet shows the obligation at the point of decision.

### 3.5 The foot — the subtitle preview
After the last segment: the German, in cue order, colour-coded as it will burn (`PEDAGOGY` §5.3 — der blue · die red · das green · target yellow). This is where the creator sees **the lesson as the learner will meet it**, which is the only view that answers "does this actually teach?" at a glance.

## 4 · The completeness contract

> **A shot missing any field in `TREATMENT` §15 is not a finished shot.**

The sheet makes incompleteness *visible* rather than discoverable at generation time: an unfilled field renders as a red `—` in place, never as an omitted row. That is the whole reason to render every field even when empty.

Completeness is machine-checked (`validate_screenplay_v4`) and splits exactly as PEDAGOGY does:
- **BLOCK** — the gate button is disabled; the screenplay cannot lock. (Missing named light source, mood-word ratio, DOF outside its set, atmosphere mixed inside a segment, missing tonal mode, level ceilings exceeded, banned medium vocabulary, an atom above level.)
- **FLAG** — advisory chip, gate stays open, Jayon decides. (Density too high for the clip, POV without a blocking-reference flag, a prop without sound behaviour, target vocab over budget.)

## 5 · What is editable, and where

The sheet is not a read-only export. But **not everything is edited the same way**, and the difference is the lock:

| Edit | How |
|---|---|
| Typo in a German line, a gaze, an expression, a prop's sound note | **Inline.** Click the field, change it, it saves to the screenplay. |
| Anything that changes what a shot *is* — action, blocking, shot size, duration, adding/removing a shot | **Through the change protocol** — proposed in the chat, shown with its recompile set, confirmed, applied. |
| Anything above the screenplay — premise, lesson, cast, location | **Edit the brief**, which rebuilds the screenplay. The sheet warns that this is a full rebuild. |

The rule underneath: **an edit that changes the recompile set must show the recompile set first.** A typo recompiles nothing; a blocking change recompiles that segment's sheet prompt and video prompt. The creator should never learn the cost of an edit *after* making it.

Once a segment's storyboard sheet is approved, re-opening any shot in that segment **re-opens its panels too** — the sheet says so before the edit, not after.

## 6 · How the agent works shot by shot

*(The procedure belongs to `skill-2` v4 — `PIPELINE` §7 keeps station method in the station. Recorded here only so the document and the method are known to match.)*

The Writer receives an agreed brief and works **downward**, never field-by-field:

1. **Beats → segments.** The brief's escalation beats are grouped into 2 (rarely 3) 15-second segments. A segment is one continuous moment in one condition — which is why it can hold exactly one tonal mode and one atmosphere.
2. **Segment → shots.** Cut where meaning changes, not on a clock: a new subject, a reaction, a reveal, a new spatial relationship. Shot count is story-driven with **no cap** — but is immediately stress-tested against the clip (`TREATMENT` §8.3). A shot that carries a line needs ~2 s+ to deliver it.
3. **Shot → the full brief.** Every field from `TREATMENT` §15, decided, not defaulted. The action first (one atomic action), then the camera that serves it, then the light that motivates the frame.
4. **The tie-back.** Each shot is checked against the atom: *is the target structure tied to a visible action here?* (`STORY_SYSTEM` §5). A line whose meaning is not on screen has failed regardless of grammar.
5. **Argue with the page.** If a beat cannot be filmed inside its clip, or a contact/POV shot needs a reference that does not exist, or an atom cannot be taught inside the level ceiling — **the Writer says so and proposes the fix** rather than quietly complying. This is a duty, not a permission: a screenplay agent that stays agreeable to avoid friction has failed its station.

## 7 · Open

- **Print/export.** A PDF or Markdown export of the locked sheet is obvious and cheap; deferred until the sheet exists on screen.
- **Diff view.** Showing what changed between two locked versions of a screenplay would make the change protocol's blast radius concrete. Wanted; not Phase 2.
- **Per-shot generation status.** Once boards and clips exist, each shot block will want a small state marker (planned → boarded → generated → accepted). The layout above leaves the shot block's right edge free for it.

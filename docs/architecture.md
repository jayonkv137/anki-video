# Architecture — how this system works, and why

> Living doc · rewritten 2026-07-29. **This is the human-facing companion to `prompts/canon/PIPELINE.md`.** The canon file defines the station *contracts* (and is read by agents); this file explains **the whole machine, the reasoning behind its design, and what is actually built today.** If you are new here — or returning after a break — read this first.

---

## 1 · What this is

**The product:** a serialized German-learning series. Four recurring characters, dropped into Germany, learning to live there — published as short vertical episodes that carry a learner from **A1 to B1** across roughly 170 of them.

**The platform:** a co-creation studio where one person and a crew of specialised agents make those episodes, one at a time. The human brings the story; the agents carry everything else — the curriculum, the world, the craft rules, the visual system, the technical limits — so none of it has to be re-explained per episode.

**The bet:** consistency at scale is what makes a universe compound. Any single AI video is easy; 170 that look, sound and feel like one show is the hard part, and it is the whole engineering problem.

## 2 · Why it is built this way

This section exists because every one of these decisions will look arbitrary in six months, and somebody (possibly a future me) will try to "improve" it.

### 2.1 Why 30 seconds
Four independent constraints converge on the same number, which is why it is a law rather than a preference:
1. **The video model generates in ~15-second units.** Two segments is exactly one natural production call.
2. **At A1 pacing (~80 WPM) a 30-second block holds ~40 spoken words** — precisely one teachable pattern, heard two or three times. Longer overflows working memory; shorter can't land the pattern.
3. **It is the platform-native reel length.**
4. **A fixed unit means fixed cost and predictable production** across a very long series.

### 2.2 Why the screenplay is a "lock" and everything after is a "compiler"
Generative models are stateless. If each stage were free to re-decide, drift would compound at every step and nothing would be reproducible. So **every creative decision is made once**, in the screenplay, and each later stage only *translates* it. The payoff is concrete: an edit has a **knowable recompile set**, so changing one shot rebuilds one sheet and one prompt — not the episode. Without this, an "always-present editor" like the Director would be impossible.

### 2.3 Why canon is hash-pinned
The pipeline's behaviour is defined by documents, not just code. Hashing them means an accidental edit **aborts the run** instead of silently changing the show. It also forces the discipline that keeps documents honest: change one thing for one reason, bump the version, record why.

### 2.4 Why there are human gates
Because generation costs money and taste cannot be automated. Gates sit exactly where a bad decision becomes expensive: before generation effort, before video credits, before publication. **A station that waits for a person is doing its job, not failing.**

### 2.5 Why no fine-tuning
Character consistency comes from **locked reference images** (a multi-angle sheet plus a portrait per character) and prompt discipline. This is documented practice at production quality, it costs nothing, it updates instantly when a character changes, and it avoids a training pipeline we would then have to maintain forever.

### 2.6 Why storyboards are generated as one sheet per segment
Generating each shot separately means N independent generations with no shared context — and characters drift between them. Generating **all of a segment's shots in one image** holds them in one context, so wardrobe, lighting and identity stay identical; the sheet is then sliced back into per-shot panels. This was a real bug we hit and fixed.

### 2.7 Why lesson-first, not stereotype-first
The earlier design started from a cultural stereotype and found a lesson to fit. That produces charming episodes with no learning spine. Now the **curriculum decides what an episode teaches**, and the stereotype library serves as a *bank of real situations* the method can draw on — which is exactly what the story method needs anyway (§2.8).

### 2.8 Why "reverse scenario generation"
Picking a setting and forcing grammar into it produces scenes where a rule is demonstrated. Starting from the structure and asking *what real situation naturally demands this?* produces scenes where the grammar is unavoidable — and therefore invisible, and therefore learned.

### 2.9 Why retrieval is deterministic, never semantic
Memory is resolved by typed relationships (this shot → these characters → their approved references), not vector similarity. Semantic search returns *near-misses*, which in a consistency system is worse than returning nothing.

### 2.10 Why ffmpeg and not a rendering stack
Assembly and subtitles run on ffmpeg with a declarative subtitle state. A React/Remotion/Lambda stack was researched and rejected: it buys parallel-render scale we do not need at one episode at a time, and costs a second toolchain. Same ideas — declarative state, instant preview, non-destructive editing — at zero infrastructure.

## 3 · The knowledge layer (canon)

Six documents carry everything the agents know. Each answers exactly one question, and no two overlap.

| Document | Answers |
|---|---|
| `MISSION.md` | What are we making, for whom, at what bar? *(injected into every call)* |
| `SHOW_BIBLE.md` | Who are these characters and what is this universe becoming? |
| `STORY_SYSTEM.md` | How do I turn a lesson + the story so far into a scene? |
| `PEDAGOGY.md` | Does this actually teach — and how do I check? |
| `TREATMENT.md` | How does it look and sound? |
| `PIPELINE.md` | Which station am I, and what must I not decide? |
| *(+ curriculum)* | What is taught, in what order? |
| `prompting_guidelines_seedance.md` | Engine syntax and limits |

**Design rules that apply to all of them:** every line must be checkable · each splits **HARD** (blocks; kept very short) from **SOFT** (flags; advisory) · they exist so the creator does *not* have to hold them · they are corrected by evidence when real episodes disagree.

## 4 · The stage spine

| Stage | Produces | Notes |
|---|---|---|
| Curriculum → module | the atoms this block teaches | the spine; lesson-first |
| **Lesson Plan** *(new, per lesson)* | `lesson.json` — the block plan: N episodes, topics per episode, the through-line | *shell built, agent not* |
| **Showrunner** *(per episode)* | framing, lead, situation options | *designed, not built* |
| **Strategist chat** | the agreed scenario | asks before it offers |
| **Commit** | `brief.json` | extracts; never invents |
| **Screenplay** | `screenplay.json` — **the lock** | all creative decisions land here |
| **Quality check** | verdict + flags | judges, never rewrites |
| **Storyboard sheets** | one sheet prompt per segment | human generates → upload → auto-sliced into panels |
| **Video prompts** | one prompt + reference manifest per segment | human generates clips → upload |
| **Assembly / subtitles / export** | joined cut → `subtitles.json` → `final.mp4` | subtitles are a separate post layer, never in-frame |
| **Publish** | — | *not built* |
| **The Director** | typed edits + targeted recompiles | floats over every stage |

**Generation is currently manual by design:** the studio produces prompts and reference lists; the creator generates images and video externally and uploads the results. The station contracts are unaffected by that later becoming automatic.

## 5 · Cross-cutting systems
- **RCP (Run Context Pack)** — assembles the per-call context: mission, canon, series memory. Verifies every canon hash at run start; a mismatch aborts.
- **Ledger (Supabase)** — runs, per-stage events with artifact hashes, and episodes. Non-fatal by design: audit logging never breaks a working pipeline.
- **The Director / overseer** — `plan → confirm-with-diff → apply`. Plans come from structured output; the **dependency graph** (not the model) decides what recompiles; edits are deterministic Python.
- **Artifacts** — every stage writes to disk before the next runs. The artifact is the contract; no stage reads another's reasoning.
- **The studio UI** — a 7-step wizard over a FastAPI backend; state resumes by run id.

**Stack:** Python · FastAPI · vanilla-JS single page · Gemini (structured output) · ffmpeg · Supabase · JSON artifacts on disk. Image generation: Nano Banana Pro. Video: Seedance 2.0 reference-to-video.

## 6 · Build status (this is the part that changes)

*(rewritten 2026-08-02)*

**Built and tested (V4):** `curriculum.json` (30 lessons · 164 topics, registry-pinned) · `llm.py` (schema-enforced, loud failures — the old Gemini path accepted a schema and silently ignored it) · `context.py` (per-phase canon from PIPELINE §3 read-lists) · `universe_state.py` (strata 2–4 live in Supabase; teaching status DERIVED from the progression log) · `schemas.py` (lesson/brief/screenplay v4 + HARD/SOFT validators) · `studio.py` (the episode thread · phase router · **view compiler** · the six gates) · `lessons.py` (the block plan, the coverage invariant, re-planning) · `canon_audit.py` (the cross-layer drift detector) · `dashboard/studio_api.py` (`/api/studio/*`, layout-agnostic). **169 assertions green** across four suites.

**Designed, not built:** every **agent** (Phase 3 — `studio.py` is the shell) · the **studio chat** control centre · stereotype tagging + `suggest_for_lesson` · publishing · the `ui-audit` token-drift detector.

**Rejected and being rebuilt:** the **UI**. The 2.2 wireframe's information architecture was confirmed; its presentation was not (dense, flat, no hierarchy, no design system). Method in `DESIGN_system_ui.md`, screen 01 brief in `DESIGN_screen_home.md`.

**Unproven — the honest headline:** **nothing has ever been generated.** One Nano Banana Pro test (abstract shapes, not characters) proved the API works on the existing `GOOGLE_API_KEY`, so **images need no FAL_KEY**. No Seedance call has ever run, so German lip-sync is unsolved and the per-clip price is unknown. The C1 identity test — the same character twice, independently, reading as the same character — has been pending since 2026-07-15.

## 7 · Known gaps
1. **Skills don't read the new canon** (the wiring step) — includes folding `canon_blocks.md` into `TREATMENT` and deleting `global_aesthetic_rules` from the screenplay schema.
2. **No style plate and no location plates** — the global look has no visual anchor; deferred deliberately until real episodes exist.
3. **Gemini structured output is not schema-enforced** (`response_schema` is unset), so field drift is possible.
4. **`director_notes` is never captured at commit**, so specific creative decisions from the chat can be lost.
5. **QC never runs in the studio flow**; validator problems are shown but block nothing.
6. **Sheet slicing is blind** — equal-division crop with no gutter detection.
7. **Subtitles need two corrections** — static clauses instead of word-by-word karaoke, and `das` → `#10B981`.
8. **Canon updates are manual** (hand-computed hashes) — friction that already caused one document to rot.
9. **Clip trimming, Deepgram precision timing, an Overseer undo button, and publishing** are all unbuilt.

## 8 · Where the reasoning lives
Decisions and their evidence: `docs/planning/` — the `DESIGN_*` files hold conclusions, `RESEARCH_*` files hold the evidence they came from, `PLAN_*` and `BLUEPRINT_*` hold work in progress. `docs/changelog.md` is chronological. Session handoffs are in `docs/handoffs/`.

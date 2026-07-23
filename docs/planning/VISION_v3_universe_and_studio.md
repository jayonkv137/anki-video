# VISION v3 — The Universe & the Co-Creation Studio

> **Status: CAPTURED, PENDING JAYON'S LOCK.** This records the redesign direction Jayon set on **2026-07-22**. It is faithful to his words + annotated; nothing here is scope until promoted into `MVP_ROADMAP_command_center.md` / build docs and logged in `VISION_HISTORY.md`. Claude annotations are marked _(CN:)_.
> **Companion research (filed same day):** `RESEARCH_shortform_pedagogy_framework.md` (format/pedagogy) · `RESEARCH_german_stereotypes_compendium.md` (content database).
> **What it changes:** this un-parks and expands **idea #16** (episode shape/duration/curriculum) plus parked ideas **#4** (Nicos-Weg structured arc), **#5** (universe continuity memory), **#8/#13** (subtitle design), and elevates the Command Center (M7) from a run-viewer into a full **co-creation studio**.

---

## 1. The core shift

| Dimension | V2 (current, built) | V3 (this direction) |
|---|---|---|
| **Episode shape** | **10 scenes**, each generated **one-by-one**, one per dialogue beat | **2–3 Seedance clips of ~15s**, each clip containing **multiple shots in a single prompt** → **30–45s total** (Jayon: 45s preferred) |
| **Why** | — | Per-scene generation causes environment/consistency drift and weak cutting; Seedance's native multi-shot gives in-clip continuity + smoother cuts |
| **Structure** | Fixed 10 words → episode | Stereotype-driven scenarios; word/lesson count flexible (see pedagogy research CEFR caps) |
| **Narrative** | Standalone daily episodes | A **serialized universe**: character introductions first, then a growing story (Nicos Weg / Dreaming Spanish DNA) |
| **New pipeline stage** | screenplay → prompts | screenplay → **storyboard (new skill, image-gen)** → prompts |
| **Interface** | Command Center = run viewer + gates | Full **co-creation studio**: pick stereotype → brainstorm → screenplay → storyboard → prompts → generate → subtitle/edit, all human-gated |

_(CN: the "10×short scenes may be the wrong shape" hypothesis was already logged as idea #16 on 2026-07-21. This is the deliberate act of testing/adopting it — earlier than the M6 "prove-loop-first" plan intended. That re-sequencing is the one decision to make explicitly; see §8.)_

---

## 2. The new video shape (Seedance multi-shot)

- Target total duration **30–45s** (Jayon leans 45s). Composed of **2–3 clips of ~15s**.
- Each ~15s clip is a **Seedance multi-shot generation** — several shots described in **one prompt**, so cuts happen *inside* a coherent generation (continuity + better cutting than stitching 10 independent clips).
- For each 15s clip we must decide, up front and explicitly, **how many shots** it contains and what each shot is.
- Consistency is held by attaching, per clip: **character reference image(s) + style reference image + audio/voice reference + the storyboard frame(s)** for that clip.
- _(CN: this replaces the current `assemble` model of concatenating 10 separate clips. Subtitle burning + master audio from C5/M5 still apply, but over 2–3 long clips instead of 10 short ones. Validate Seedance's real multi-shot behavior + the 15s ceiling in `RESEARCH_video_generation.md` before locking — flagged open in §7.)_

---

## 3. The universe & narrative design

**Establish a universe, then grow a story inside it** — inspired by **Nicos Weg** (follow a character through scenarios/stories) and **Dreaming Spanish** (comprehensible-input progression).

**Launch = character introductions, one at a time.**
- Start by introducing **Rolf** — who he is, where he's from (a Berliner; "techno sausage"), established through a stereotype that *is* his character (the irony: the characters themselves are stereotypes — Rolf is literally a sausage). An **Instagram-grid establishing post/scenario**.
- Then **Bert** — where he's from, an intro built on his character/stereotype.
- Then the others, each introduced via a stereotype.
- After the cast is established, **begin a serialized story** that grows over time.

**Continuity:** the universe needs memory — what happened in which episode, what was taught, character continuity across episodes _(CN: = parked idea #5 / #9, the cross-episode continuity engine; the Supabase `episodes` + series-memory layer is the seed of this)._

_(CN: Jayon can hand-write the opening/introductory story himself, or co-write it with AI — the studio supports both. The intro arc for the first ~4 characters is the first concrete content deliverable of V3.)_

---

## 4. The co-creation studio (human-in-the-loop interface)

The end-state UI Jayon described, in order. Every arrow is a **human gate** (review / approve / edit / redo).

1. **Landing / dashboard.** Opens on previously-completed episodes — a cool landing page / grid of finished videos with titles ("we've done these N videos"), each with a short blurb: **which stereotype, which lesson, which topic**. This is the portfolio + the library + the entry point.
2. **Pick a stereotype.** A browsable list of stereotypes (from `RESEARCH_german_stereotypes_compendium.md`), each with a short description. Jayon picks one.
3. **Brainstorm the scenario (co-creation).** AI proposes **3–5 scenario ideas** for that stereotype, asks Jayon for input; they iterate together and converge; Jayon **confirms the idea**.
4. **Screenplay.** The confirmed idea → a full screenplay, **emphasizing the language-learning aspect**. A **quality check** verifies the language-learning aspect is actually present/surfaced; Jayon can read the full screenplay and review it. → confirm.
5. **Storyboard (NEW stage).** A **storyboarding skill** + **image generation** turns the screenplay into a **storyboard sequence**. Split into **per-15s-segment storyboards** (segment 1 / segment 2 / [segment 3]); for each segment, decide the **shot count/breakdown**. Uses **character ref + style ref** for consistency. Jayon **reviews the storyboard** → approve, or redo.
6. **Prompt writing.** From the storyboard images, write each **~15s multi-shot prompt**, binding **character ref + audio/voice ref + style ref + storyboard ref**. Jayon **confirms**, then generation runs **one clip at a time**: generate clip 1 → Jayon approves → clip 2 → … 
7. **German text layer.** Design how the German text overlays the video (safe zones, gender color-coding, kinetic typography — per pedagogy research §2.3). The agent adds subtitles/text **automatically first**; Jayon can then **override and edit** them inside the UI.
8. **Editing.** The next editing step runs **automatically**, but with an **interface for Jayon to take over and edit** manually.

_(CN: steps 1–2 and 7–8 are the genuinely new UI surfaces; 3–6 already have pipeline skills (skill-1a/1b, skill-2/2q, skill-3) that get re-shaped rather than rebuilt. The storyboard skill (step 5) is net-new.)_

---

## 5. What's reused vs changed vs net-new

| Layer | Verdict | Notes |
|---|---|---|
| Supabase ledger (runs/events/episodes) | **Reuse** | Already the studio's data model; add stereotype/lesson/topic metadata for the library view |
| Gate A + `--note` director input | **Reuse** | Becomes the studio's gates + idea injection |
| skill-1a/1b (story options/expand) | **Re-shape** | Input becomes a **chosen stereotype**; output is the brainstorm→confirm loop (3–5 ideas) |
| skill-2 / skill-2q (screenplay + QC) | **Re-shape** | QC gains an explicit **language-learning-aspect** check; screenplay targets the 2–3-clip / multi-shot structure, not 10 scenes |
| skill-3 (prompt writer) | **Re-shape** | Emits **per-15s multi-shot** Seedance prompts binding storyboard refs, not per-scene prompts |
| **Storyboard skill (image-gen)** | **NET-NEW** | Screenplay → storyboard frames per 15s segment; needs a chosen image model (deep-research task) |
| Video provider (`providers/video.py`, fal/Seedance) | **Reuse + verify** | Real Seedance call still unverified; must confirm multi-shot + 15s behavior |
| `assemble` (subtitles/concat) | **Re-shape** | Concatenate 2–3 long clips; subtitle layer becomes the color-coded kinetic-typography system |
| Command Center dashboard | **Extend** | From run viewer → full co-creation studio (steps 1–8) + subtitle/edit surfaces |
| canon_blocks / character bibles / voice refs | **Reuse** | Photoreal-CGI material laws + per-character voices carry straight over |

---

## 6. Pedagogy adopted from the research (the guardrails)

From `RESEARCH_shortform_pedagogy_framework.md` — these become concrete pipeline rules:
- **Duration/word caps by CEFR:** A1 30s/≤30 words · A2 40s/≤55 · B1 45s/≤80 (the 45s target ⇒ B1-ish budget).
- **Single-line L2 (German) subtitles only** — never dual L1+L2 (split-attention trap).
- **Gender color-coding:** der=blue `#3B82F6`, die=red `#EF4444`, das=green `#10B981`; **yellow `#F59E0B`** for target grammar (modals, separable prefixes, cases).
- **Stereotype = scenography + conflict**, visible in first 3s; dialogue never explains the habit.
- **Five reusable typologies** (Hausordnung / Missverständnis / Allzeit Bereit / Pfand-Krieg / stummer Vorwurf) fix grammar target + character pairing per episode.

---

## 7. Open questions / decisions pending (Jayon)

1. **Sequencing:** adopt V3 shape **now**, or finish the current "prove-the-loop" plan (M1–M6) on the 10-scene shape first, then redesign? _(The locked roadmap says redesign-after-M6. Blockers — Anthropic credits exhausted, real Seedance unverified, Flashboard test pending — currently stall M1–M6 anyway, which may favor doing design work now.)_
2. **Duration:** lock **45s (3×15s)** as default, or **30s (2×15s)**, or make it per-episode/per-CEFR-level?
3. **Storyboard image model:** ~RESEARCHED — `RESEARCH_v3_tech_derisk_seedance_and_storyboard.md` §6. Shortlist = **Nano Banana Pro** (best storyboard-specific) vs **Seedream 4.x** (ByteDance same-family as Seedance). Pending: a ~$1 head-to-head on our own sheets → Jayon decides.
4. **Seedance reality check:** ✅ RESOLVED — `RESEARCH_v3_tech_derisk_seedance_and_storyboard.md`. Multi-shot / 15s / 9:16 / ≤9 image refs / ≤3 voice refs all confirmed on fal `seedance-2.0/reference-to-video`. One residual: does it truly clone+lip-sync a German voice ref (needs one paid ~$3.6 test — already the packet's next-step #3).
5. **Character canon:** reconcile the research briefs' archetype→role/origin mapping (Rolf=Berlin/cynical, Kati=Bavarian/traditional) with `resources/Characters-Main-Sheet.md`.
6. **Intro arc:** hand-write the first-4-characters introduction stories, co-write with AI, or hybrid?

## 8. Relationship to the locked roadmap

`MVP_ROADMAP_command_center.md` explicitly parks "10-words curriculum, 60s→30s duration, story-structure changes (idea #16)" until **after M6** (post-it proof) "with real data." **V3 pulls that redesign forward.** That is a legitimate re-prioritization given the current blockers, but it reverses an explicit prior decision — so it should be locked by Jayon (Decision #1 above) and, once locked, reflected by an update to the roadmap + a `VISION_HISTORY.md` entry in the same commit.

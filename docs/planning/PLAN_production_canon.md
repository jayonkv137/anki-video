# PLAN — The production canon set (the agents' "superpower" documents)

> **Status: PROPOSAL for Jayon's confirmation (2026-07-29).** Audit of every research document we hold, → what production knowledge must become **canon** (hash-pinned, injected into agents) versus stay research, → the proposed document set, → **four contradictions that must be resolved before writing.** Nothing written yet.

## 1 · The core finding
**The visual half of the show is now canon; the narrative and pedagogical halves are not.** `TREATMENT.md` v1.1 governs how the show *looks and sounds*. But the knowledge that decides whether an episode actually **teaches** and actually **works as a story** sits in `docs/planning/` research files that **no agent has ever read**. Everything the agents currently know about story and teaching is whatever prose happens to be inside a skill file.

**What is provably in canon today** (`verify_canon`): `MISSION.md` · `TREATMENT.md` · `canon_blocks.md` · `prompting_guidelines_seedance.md` · `prompting_guidelines_omni.md` · `Characters-Main-Sheet.md`.
**What is NOT, but must be:** pacing/word/pause caps per CEFR level · the subtitle science · cognitive-load rules · the micro-story grammar · the episode typologies · humour theory · the character↔grammar mapping · the curriculum spine · the universe premise.

## 2 · Proposed canon set (6 documents, each with one owner and no overlap)
| # | Document | Answers | Status | Read by |
|---|---|---|---|---|
| 1 | **MISSION.md** | *What is this and what is the bar?* | ⚠ **REWRITE** — currently V2-era | every agent (RCP prefix) |
| 2 | **SHOW_BIBLE.md** | *Who are these characters and what is this universe?* | **NEW** — merges `Characters-Main-Sheet` + `NARRATIVE_BIBLE_seed` + the character↔grammar map | Showrunner · screenplay · storyboard |
| 3 | **STORY_SYSTEM.md** | *How is a story BUILT?* (craft) | **NEW** — the biggest gap | Showrunner · screenplay · QC |
| 4 | **PEDAGOGY.md** | *How is language TAUGHT?* (science + numbers) | **NEW** | Showrunner · screenplay · QC · subtitle engine |
| 5 | **TREATMENT.md** | *How does it LOOK and SOUND?* | ✅ **DONE** v1.1 | storyboard · video · Overseer · subtitles |
| 6 | **CURRICULUM** (`curriculum.json` + doc) | *What is taught, in what order?* | drafted, awaiting lock | Showrunner · screenplay · QC |
Plus the model-technical file `prompting_guidelines_seedance.md` (keep as-is — it is engine documentation, not creative law).

### Retire
- **`prompting_guidelines_omni.md`** — Omni was dropped in the V3 reshape; it is dead canon still being hash-verified and injected at the prompt stage.
- **`canon_blocks.md`** — its STYLE_BLOCK and material laws are now duplicated verbatim inside `TREATMENT.md` §10. Two sources for one truth is exactly the drift risk we are trying to eliminate. Fold and retire.

### Contents at a glance
**STORY_SYSTEM.md** — the micro-story grammar (base reality → first unusual thing → framing → escalation → button); the five episode typologies; the fixed story skeleton and *why consistency compounds comprehension*; **bizarreness works only when funny — humour lives in the visual situation, never in wordplay the learner cannot parse**; "visually comic, linguistically plain"; how a scenario is derived from a lesson atom (reverse scenario generation: pick the structure → pick the situation that naturally demands it → write the scene); how a stereotype enters as **scenography, never as explanation**; the 30-second block anatomy and hook-in-3-seconds retention rule; dialogue as the universal solvent for un-filmable words; the anti-slop / variety engine (so 170 episodes don't homogenise).

**PEDAGOGY.md** — the pacing formula `WPM = (syll_per_sec / 1.7) × 60` and the per-level table (A1 ≈ 80 WPM / 25–30 words / ≤8-word sentences / ~10 s pause budget · A2 ≈ 100 / 50–55 / ≤12 · B1 ≈ 120 / 75–80 / ≤15); **pauses as structure, placed at syntactic boundaries** (before separable prefixes, around subclauses, at turn switches); the dual-subtitle trap (L1+L2 collapses gaze to ~70 % L1 → shallow processing) and the winning mode (**L2 + colour key → 80 % L2 gaze, very high retention *and* grammar acquisition**); the gender colour hexes; Mayer dual-channel limits; high-yield short-form grammar (modals, separable verbs, particles); TPRS meaning-first and the 3–7 exposure window with *informative context over raw repetition*; the CEFR scripting matrix (tenses, syntax, lexicon per level); the QC checklist this generates.

**SHOW_BIBLE.md** — the premise and Season-0 portal intros; **fluent-but-foreign** canon; per character: belief, wound, voice, speech signature, vocabulary domain, **and the pedagogical role** (§3.2); cast-dynamics matrix; world rules; the ≤2-speaking-characters law.

## 3 · ⚠ Four contradictions to resolve before writing

### 3.1 `MISSION.md` is V2-era and actively harmful
It is hash-pinned canon injected into **every LLM call**, and it currently states: *"Ten Anki-derived vocabulary words become one story… ten scene video prompts, ten generated videos"*, *"the 605-word deck yields a ~61-episode course"*, and describes the cast as **"food-puppet characters"** — while `TREATMENT.md` §1 bans the word *puppet* as latent-space poison. Every agent is being told the old shape of the product and a banned word, on every call. **Must be rewritten for V4.**

### 3.2 The pedagogical character roles contradict the character bible
`RESEARCH_shortform_pedagogy_framework.md` §3.1 assigns roles from a **different personality set** than the bible — and flags it itself ("reconcile before locking"):
| | Pedagogy research says | The character bible says |
|---|---|---|
| Rolf | rule-enforcing Bratwurst; formal/imperative, modal obligation | Berlin deadpan; *"nothing impresses me"*; negation, one-word answers |
| Kati | easy-going, confused by regulations | perfectionist; *"perfection is achievable"*; punctuality, precision, judgement |
| Bert | social, particle-heavy Pilsner | loud Bavarian professor; *"I understand everything"*; wrong-but-committed explanations |
| Müller | melancholic sourdough; passive, Konjunktiv II | North German reserved; *"words are expensive"*; short firm sentences |
**The role *idea* is valuable** — who elicits which structures is real pedagogical design — but it must be re-derived from the true bible. Proposed re-derivation:
- **Müller — the Minimalist.** Shortest complete sentences in the show → ideal A1 host (greetings, ja/nein, weather, numbers, SVO).
- **Rolf — the Negator.** *Egal · Ne · Doch · Warum?* → negation (nicht/kein), question forms, refusal.
- **Kati — the Corrector.** Punctual, precise, judges choices → imperatives, time expressions, comparatives/superlatives, adjective precision, correction structures.
- **Bert — the Explainer/Catalyst.** Explains everything (wrongly), invites, toasts → *weil*-clauses, exclamations, invitations, modal desire, questions that elicit answers from others.
This mapping *follows from* the bibles and gives the Showrunner a principled reason to cast a given lesson to a given character.

### 3.3 Two of your research documents disagree about subtitles
- `RESEARCH_shortform_pedagogy_framework.md`: **word-by-word kinetic typography** is part of the winning mode.
- The micro-learning architecture research (Downloads): **karaoke-style word-by-word captions harm learning** — they destroy the perceptual span, force reading at the speaker's exact pace, and raise extraneous load; it recommends static full-clause lines.
**They agree on colour-coding** (both rate input enhancement highly). Proposed resolution: **keep the gender/grammar colour key, drop the word-by-word reveal in favour of static full-clause lines.** This also matches the platform reality that a reel is re-watched. Our subtitle engine currently does word-by-word `\k` karaoke, so this is a code change.

### 3.4 A colour-value mismatch
Research specifies *das* = `#10B981`; `pipeline/subtitles.py` uses `#22C55E`. Trivial, but the canon value should be the one in code.

## 4 · Also carried into the new docs (decisions already made, currently only in chat/research)
Fluent-but-foreign · 1 reel = 1 lesson-block, format upgradeable · module = story-arc unit with one lead character · rotating-lead casting · stereotypes as a tagged, optional encounter library · guardrails-not-quotas · ≤2 speaking characters · the 30-second block law.

## 5 · Proposed build order
1. Jayon resolves §3.1–3.4.
2. **PEDAGOGY.md** (most mechanical — the numbers already exist and it unblocks the QC gate).
3. **STORY_SYSTEM.md** (the biggest craft gap).
4. **SHOW_BIBLE.md** (merge + the re-derived roles).
5. **MISSION.md** rewrite; retire `omni` + fold `canon_blocks`.
6. Re-hash REGISTRY; wire every skill to read the new canon; delete `global_aesthetic_rules`.

## 6 · Open asset question
`resources/Rolf die Wurst/` contains only `Rolf Main.png`, `Rolf sheet.png` and the voice mp3 — **no profiles sheet and no close-up**, while Bert, Kati and Müller each have four images. Jayon indicated Rolf has a profile; if that file exists elsewhere it should be dropped into his folder, otherwise it needs generating (`TREATMENT.md` §9.5).

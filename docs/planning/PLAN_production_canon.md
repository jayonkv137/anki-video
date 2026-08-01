# PLAN — The production canon set (the agents' knowledge layer)

> **Status: PROPOSAL v2, for Jayon's confirmation (2026-07-29).** v2 incorporates Jayon's corrections: characters keep personality but **lose all speech constraints** · the story system is **reverse scenario generation**, not a beat formula · pedagogy is a **minimum bar for QC**, not a specification · the Show Bible must hold his **evolving arc ideas** · and the honest answer to *"will this become a bottleneck?"*.
> Companion: `TREATMENT.md` v1.1 (already canon) · `AUDIT_visual_identity.md` · `CURRICULUM_v1_universe.md`.

---

## 0 · The question that governs the whole design: *will this strangle the writing?*

**Yes — if these are written as constraints the writer must satisfy. No — if they are written as knowledge the AGENT carries.** That distinction decides everything, so it is a design rule for all four documents:

1. **The documents exist so Jayon does NOT have to hold them.** He arrives with a story idea; the agent already knows the pacing ceiling, the reference-attachment order, the negative list. Knowledge in canon is knowledge *off* the creator's mind. If a doc ever becomes something Jayon must remember, it has failed.
2. **Two tiers, explicitly labelled, in every document.**
   - **HARD** — a very short list: things that genuinely break the video, the teaching, or the platform (model limits, the 3000-char cap, the safe zone, "no text in frame", the CEFR ceiling for the level). These are checked and blocked.
   - **SOFT** — everything else: craft guidance the agent uses to *make suggestions* and *run checks*. Flagged, never blocked. This is Jayon's "guardrails, not quotas" decision applied to prose.
3. **Checked at QC, not enforced at write time.** The story is written freely; the audit reports afterwards; Jayon decides. A flag is information, not a veto.
4. **Defaults with escape hatches**, exactly as `TREATMENT.md` was corrected — "the camera holds unless the action motivates a move", not "these moves are forbidden".
5. **The bottleneck test, applied to every line before it is written:** *does this help the agent make a better suggestion, or does it only tell the writer "no"?* If only the latter, it does not go in.

---

## 1 · The core finding (unchanged)
The **visual** half of the show is now canon (`TREATMENT.md`). The **narrative** and **pedagogical** halves are not — they sit in `docs/planning/` where no agent reads them. The agents' entire knowledge of story and teaching is currently whatever prose happens to be inside a skill file.

## 2 · The set — six documents, each answering one question

| # | Document | The one question it answers | Status |
|---|---|---|---|
| 1 | **MISSION** | *What is this, for whom, at what bar?* | ⚠ rewrite (V2-era) |
| 2 | **SHOW_BIBLE** | *Who are these characters and what is this universe becoming?* | NEW |
| 3 | **STORY_SYSTEM** | *How do I turn a lesson + the story so far into a scene?* | NEW |
| 4 | **PEDAGOGY** | *Does this episode actually teach — and how do I check?* | NEW |
| 5 | **TREATMENT** | *How does it look and sound?* | ✅ done |
| 6 | **CURRICULUM** | *What is taught, in what order, and what's left?* | drafted |

Kept as engine documentation (not creative law): `prompting_guidelines_seedance.md`.
**Retire:** `prompting_guidelines_omni.md` (Omni dropped in V3 — dead canon still hash-verified and injected) · `canon_blocks.md` (its material laws now live verbatim in `TREATMENT.md` §10; two sources for one truth is the drift risk we're removing).

---

## 3 · Each document: role, users, and when it fires

### 3.1 MISSION — *the frame*
- **Role:** the shortest possible statement of what we're making, for whom, and the quality bar.
- **Used by:** every agent, on every call (RCP prefix).
- **Fires:** always, invisibly.
- **Biggest value:** it is the only thing that makes an agent's *judgement* align with ours when a rule doesn't cover the case.
- **⚠ Must be rewritten.** It is currently V2-era and actively harmful: injected into every LLM call while stating *"Ten Anki-derived vocabulary words become one story… ten scene video prompts, ten generated videos"*, *"the 605-word deck yields a ~61-episode course"*, and calling the cast **"food-puppet characters"** — a word `TREATMENT.md` §1 bans as latent-space poison.
- **Length target:** one page. Anything longer belongs in another document.

### 3.2 SHOW_BIBLE — *the universe*
- **Role:** who these characters are, what world they're in, and **where the story might go**.
- **Used by:** Showrunner (constantly), screenplay agent (voice), storyboard agent (who's present).
- **Fires:** at ideation, when casting a lesson, and whenever a character speaks.
- **Biggest value:** it is what makes the four feel like *people* rather than costume slots — and it is where Jayon's long-range narrative thinking is captured instead of being lost in chat.
- **Contents:**
  - The premise + Season-0 portal intros + **fluent-but-foreign** canon.
  - **Per character: personality, attitude, register, how they carry themselves, what they care about, what they'd never do, signature phrases, relationships.** Written as *characterisation*, never as a speech budget (§4.1).
  - Cast-dynamics matrix (who sparks off whom).
  - World rules and accumulated canon facts.
  - **A living "Directions" section** — Jayon's evolving ideas about where the series could go: arcs he's considering, characters they might meet, threads he wants to plant, endings he's circling. Explicitly marked as *possibilities, not commitments*, so the Showrunner can propose against them without treating them as locked. This is the thing he asked for: *"so that the global thing can be tracked somewhere with my ideas."*

### 3.3 STORY_SYSTEM — *how a scene comes into being*
- **Role:** the method for turning **a lesson + the story so far + a cast** into a scenario worth filming.
- **Used by:** Showrunner (primary), screenplay agent, QC.
- **Fires:** at the exact moment Jayon says "okay, what do we do with this lesson?"
- **Biggest value:** this is the brain of the whole platform. Everything else is bookkeeping by comparison.
- **The core mechanism — REVERSE SCENARIO GENERATION** (Jayon's correction; the method Nicos Weg is built on):
  > Do **not** pick a setting and force a grammar point into it. Go backwards: **(1)** take the target structure → **(2)** find the real-world situation that *naturally and frequently demands* that exact structure → **(3)** write the scene around that situation.
  > *Worked example from the research: the target is two-way prepositions with static location → the situation that demands it is moving into a room and describing where the furniture goes → the scene is Nico's Einzug.* The grammar is invisible because the situation genuinely requires it.
- **Also contains:**
  - How the **story so far** constrains and feeds the next scenario (continuity as a creative asset, not a chore).
  - **Serialized arc thinking** — how a long-running journey is structured across a season (the Nicos Weg progression: arrival → daily life → independence), how a module's scenario advances an arc, how threads are planted and paid off. Jayon drives the arcs; this documents *how they're built and tracked*.
  - **Scene craft:** the situation must be visually legible with sound off · **humour lives in the situation, never in wordplay the learner can't parse** (bizarreness only aids memory when it's funny) · "visually comic, linguistically plain" · dialogue as the universal solvent for un-filmable words.
  - **Optional shapes, not templates:** the escalation grammar (base reality → first unusual thing → escalation → button) and the five episode typologies are offered as *tools the agent can suggest*, never as a form to fill.
  - How a **stereotype** enters when one fits: as **scenography and situation**, never explained in dialogue.
  - The **anti-slop / variety engine** — how 170 episodes avoid homogenising.

### 3.4 PEDAGOGY — *the minimum bar and the check*
- **Role:** the smallest set of numbers and principles that keep an episode teachable — **and the checklist the QC agent runs.** Explicitly **not** a specification for how to write.
- **Used by:** QC agent (primary), screenplay agent (as a ceiling it stays under), Showrunner (when framing a lesson), subtitle engine (colour + placement).
- **Fires:** mostly *after* writing, as an audit.
- **Biggest value:** it lets Jayon write freely and still know the episode won't be pedagogically broken.
- **HARD (blocked):** the CEFR ceiling for the level (word count, sentence length, permitted tenses/structures) · no text in frame · subtitle safe zone.
- **SOFT (flagged, advisory):** the pacing target (`WPM = syll_per_sec ÷ 1.7 × 60` → A1 ≈ 80 / A2 ≈ 100 / B1 ≈ 120) · pauses placed at syntactic boundaries rather than as dead air · the target pattern appearing more than once in genuinely different contexts (3–7 exposures is the useful window; *informative context beats raw repetition*) · meaning made visible before or as it is spoken · one clear objective per block.
- **The subtitle finding** (both research docs agree): dual L1+L2 subtitles collapse gaze onto the L1 line (~70 %) and produce shallow, translation-based processing; **L2 alone plus a colour key** produces ~80 % L2 gaze with the highest retention *and* the highest structural-grammar acquisition. Colour key: der `#3B82F6` · die `#EF4444` · das `#10B981` · target grammar `#F59E0B`.

### 3.5 TREATMENT ✅ · 3.6 CURRICULUM
As built / as drafted. No change.

---

## 4 · Corrections to make when writing (Jayon's direction)

### 4.1 Characters: keep the personality, delete the speech constraints
The bibles currently constrain **how much and how simply** each character may speak — Müller's *"words are expensive, spend them carefully"* and *"shortest complete sentences in the show"*, Rolf's *"grammar habit: shortest possible sentences, subject-verb-done"*, and each character's assigned "teaches: …" grammar list. **All of that goes.**
- **Keep:** personality, attitude, register, humour, what they care about, how they carry themselves, signature phrases, relationships — everything that makes them *people*.
- **Delete:** speech budgets, brevity rules, assigned grammar habits, "this character teaches X".
- **Why this is required, not merely preferred:** the curriculum runs **A1 → B1**. At B1 characters must speak in relative clauses, the passive, and Konjunktiv II. A character rule that says *"shortest sentences in the show"* makes B1 impossible for that character — the constraint and the curriculum cannot both be satisfied. **Personality must survive the whole level range; speech style must be free to grow with it.**
- **Consequence: no character↔grammar assignment anywhere.** Any character can carry any lesson. Casting is driven by story and rotation (`CURRICULUM` §2), not by a grammar table. The pedagogy research's "enforcer/target/catalyst/victim" roles are **dropped entirely** — they were derived from personalities that aren't ours.

### 4.2 The story system is a method, not a formula
The escalation beats and the five typologies are **tools on offer**, not the system. The system is **reverse scenario generation** (§3.3).

### 4.3 Pedagogy is a floor, not a mould
Written as "here is the bar and here is how we check", not "here is how to write". Most of it is SOFT.

### 4.4 Subtitles: one open decision
Your two research documents disagree — the pedagogy framework wants **word-by-word kinetic typography**; the micro-learning research says karaoke captions **harm** learning (they destroy the perceptual span and force reading at the speaker's pace). **They agree on colour-coding.** Proposal: **keep the colour key, drop the word-by-word reveal in favour of static full-clause lines.** This is a change to `pipeline/subtitles.py` (currently `\k` karaoke). Also align *das* to `#10B981` (code has `#22C55E`).

---

## 5 · Do we need more research first? — **No.**
We already hold the answer to every question these documents must settle:
- **Reverse scenario generation** — specified in the DaF syllabus research (with the worked *Einzug* example).
- **Serialized arc structure** — the Nicos Weg A1/A2/B1 progression and the grammar→arc mapping table are both in the narrative-design research.
- **Scene craft, humour, story grammar, exposure** — `RESEARCH_story_design.md`.
- **Micro-story grammar, anti-slop, variety** — `RESEARCH_cocreation_system_design.md`.
- **All pedagogy numbers** — `RESEARCH_shortform_pedagogy_framework.md`.
The bottleneck is not knowledge; it is that none of it is written where an agent can read it. **More research now would be procrastination.** The one genuinely thin area — the shape of *your* multi-season arc — is creative work you said you'd drive, and the Show Bible's Directions section is the container for it.

## 6 · Build order
1. Jayon confirms §3–§4 (especially the subtitle decision in §4.4).
2. **SHOW_BIBLE** — merge the bibles, strip the speech constraints, add Directions.
3. **STORY_SYSTEM** — reverse scenario generation + arc thinking + scene craft.
4. **PEDAGOGY** — the floor + the QC checklist.
5. **MISSION** rewrite · retire `omni` · fold `canon_blocks`.
6. Re-hash `REGISTRY`; wire every skill to read the new canon; delete `global_aesthetic_rules`.

## 7 · Settled
Rolf's asset set is correct as-is (Jayon confirmed) — `TREATMENT.md` §9.5's note about missing profiles/close-up is withdrawn and will be removed at the next canon edit.

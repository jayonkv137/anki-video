# RESEARCH — System Design for Computational Co-Creativity (Pre-Scripting)

> **Source:** Deep-research result supplied by Jayon (2026-07-22), produced from `DEEP_RESEARCH_PROMPT_cocreation_ideation.md`. Faithful archive (citation noise stripped).
> **Status:** Evidence library — the **blueprint for the co-creation stage** (stereotype → locked story brief → screenplay). Adapted to our pipeline in `DESIGN_cocreation_stage.md`. Companions: `RESEARCH_shortform_pedagogy_framework.md`, `RESEARCH_german_stereotypes_compendium.md`.
> **One-line:** a mixed-initiative, human-in-the-loop wizard that moves **divergent → convergent** through explicit gates, anchored on a human seed, guarded against AI-slop, ending in a structured JSON brief.

---

## 1. Prior art (what to borrow)

| Tool | Borrow this | Avoid this |
|---|---|---|
| **Dramatron** (DeepMind) | Hierarchical prompt-chaining: lock **logline → characters → scene → beats** BEFORE dialogue | Flat character arcs, repetitive dialogue |
| **Fabula** | "Drama Managers" tracking each character's objective/stakes/obstacle | — |
| **Sudowrite** Story Engine | Centralized **Story Bible** context management | Mechanical beat-to-beat feel |
| **NovelAI** | Keyword-triggered **Lorebook** injection | Structural drift, needs constant steering |
| **LTX Studio** | Auto-extract recurring **"Elements"** (chars/objects/locations) for continuity | Visual drift frame-to-frame |
| **Showrunner** (SHOW-1/2) | Character agents with history/emotion/goals under a director agent | Flat/formulaic when fully auto |
| **Subtxt** (Dramatica) | A **"divergence factor" slider** (how far from formula) | Over-rigid |
| **Plotdrive** | Sidebar with **toggleable context** per reference doc | Falls back on stock structure if context too broad |

**Meta-lesson:** modularize (structure before dialogue) + keep an immutable bible + give the human explicit control points.

## 2. Mixed-initiative co-creativity (the interaction theory)

**Intent-elicitation patterns (Kreminski & Chung):**
- **Ask Don't Guess** — the system asks targeted questions instead of hallucinating details.
- **Refine via Examples** — generate a slate of **distinct, contrasting options** so the human finds their preference boundary.
- **Gauge Creative Momentum** — track the human's pace; offer suggestions vs. let them write.

**Casual vs Reflective creators:** casual = low-friction, high-variety, fast feedback (good for the *divergent* phase); **reflective = deliberate friction / decision gates that force the human to own the choices** (good for the *convergent* phase — the antidote to "dearth of the author"). → **Separate divergent brainstorming from convergent evaluation.**

## 3. Anti-homogenization / anti-slop (the "Artificial Hivemind" problem)

LLMs collapse toward the statistically-average trope (RLHF amplifies it). Enforce a multi-layer defense:
1. **Dynamic temperature** — divergent phase **T≈1.15 / p≈0.95** (max entropy); convergent commit **T≈0.2 / p≈0.1** (compliance).
2. **Morphological disruption + banned buzzwords** — supply a specific parameter matrix; **ban lazy thematic words** (schadenfreude, Ordnung, gemütlichkeit…) from dialogue.
3. **Self-critique auto-rater** — a second "critic" pass scans for predictable AI phrasing/didacticism; regenerate if a "Hivemind Coefficient" is exceeded.
4. **Human-seed injection** — every cycle is **anchored on a user-provided real anecdote/seed**, injecting idiosyncratic data that disrupts the average.

## 4. The block-by-block pipeline (the skill blueprints)

**STEP 1 Matrix Alignment (Morphological) → STEP 2 Option Generation (What-If/SCAMPER) → STEP 3 Parallel Critique (Six Hats/TRIZ) → Commit.**

### Block 1–3 — Parameter Alignment (Focus, no dialogue yet)
> SYSTEM: senior structural analyst. Align the input creative seed to the morphological matrix.
> MATRIX: Characters (fixed 4, with trait tags) · Locations (fixed set) · Stereotypes ST01–ST100 · Pedagogical Targets (e.g. modal particles).
> INPUT SEED: "<the human's real-world observation>"
> TASK: map seed → best Stereotype; cast exactly ONE main (embodies it) + ONE foil; pick the logical Location; pick the target Language Lesson. Output aligned params as structured markdown. **Do not generate dialogue yet.**

### Block 4–6 — Divergent Options (Flow, high T)
> SYSTEM: writer of dry, character-driven situational comedy. Propose **exactly 3 distinct comedic angles** for a 30–45s scene from the aligned params.
> Apply creative operators: **Option 1 SCAMPER-Substitute** (swap verbal argument for physical action), **Option 2 SCAMPER-Reverse** (invert expectations), **Option 3 What-If Laddering** (push one premise to a hyper-literal extreme). For each: Comedic Premise · Comedic Integration (how the stereotype is the *game*) · Pedagogical Integration (how the particle lands naturally). Invite the user to select or adjust.

### Block 7 — Convergent Critique + Commit (Focus, low T)
> SYSTEM: structural editor + pedagogical director. Review the selected option.
> **Critic pass (Black Hat):** Does dialogue name/explain the stereotype? (remove). Too complex to show in 30s? Is the particle in the **Mittelfeld**?
> **Realist pass (TRIZ inversion):** ensure the physical actions make the dialogue's meaning clear without translation.
> **Commit (Blue Hat):** output the finalized **story brief JSON** (episode_metadata · cast · scene_design{visual_setup, inciting_incident, escalation_beats[], button_climax} · dialogue_blueprint{target_line, contextual_meaning}). No prose, no citations.

## 5. Micro-story grammar — 30–45s (UCB "Game of the Scene")

```
0s            10s              20s            35s        45s
Base Reality  First Unusual    Framing +      Escalation Button/Tag
(who/what/    Thing (the       "If-Then"      (logical   (payoff, no
 where, in    stereotype       (foil reacts)   doubling)  resolution)
 medias res)  behavior)
```
The stereotype is the implicit **"game"** — **never named or explained** in dialogue (that turns it into a didactic ad). Humor = contrast between expected and the stereotype's absurd reality. ~50–80 words; visuals carry the narrative.

## 6. Pedagogy — Modal Particles as the curriculum spine

Grounded in Krashen (Comprehensible Input) + TPRS (story-asking, no explicit grammar) + TBLT (language mapped to visible action). Primary target: **German Modal Particles (Modalpartikeln)** — uninflected, high-frequency in native speech, live in the **Mittelfeld**, convey stance not truth-value. "Pop-up grammar" notes shown at the option stage.

| Level | Particle | Pragmatic function | Stereotype alignment | Example |
|---|---|---|---|---|
| A1 | **mal** | softens a request/imperative | Kehrwoche | "Feg **mal** kurz!" |
| A1 | **ruhig** | reassurance / permission | Sonntagsruhe | "Mach **ruhig** die Musik aus." |
| A2 | **doch** | appeal to shared obvious knowledge | Pünktlichkeit | "Wir haben uns **doch** um fünf verabredet!" |
| A2 | **denn** | curiosity/mild irritation in questions | Ruhestörung | "Was machst du **denn** da?" |
| B1 | **ja** | surprise / highlights an obvious fact | Stoßlüften | "Hier ist es **ja** arktisch!" |
| B1 | **halt / eben** | resignation / inevitability | Bürokratie | "Das ist **halt** das Gesetz." |
| B1 | **wohl** | assumption / probability | Mülltrennung | "Das ist **wohl** der falsche Eimer." |
| B1 | **aber** | strong surprise in exclamations | Feierabendbier | "Das ist **aber** ein früher Feierabend!" |

## 7. Interaction / UX — the guided wizard

Two modes: **Flow** (spontaneous human brainstorm/prose) vs **Focus** (structural analysis / rule enforcement). Steps:
1. **Seed capture** (Flow) — clean editor; human braindumps a real observation.
2. **Parameter integration** (Focus) — system aligns seed to DB; sidebar to pick stereotype / cast / location / lesson / sub-genre; persistent state tracker.
3. **Option presentation** (Flow) — 3–5 **option cards** (premise + dynamics + pedagogy).
4. **Iterative refinement / backtracking** — freeform notes; swap any earlier choice without losing work.
5. **Convergent critique** (Focus) — Thinking-Hats critique shown **side-by-side** with the draft.
6. **Commit + JSON export** — verify (stereotype not named · particle in Mittelfeld · fits 30–45s) → "Commit Brief" → JSON to downstream.

## 8. Variety engine (replicability across 100 episodes)

- **Character dyads:** 4 chars → **6 pairs**; rotate them (each pair has a distinct friction) so dynamics don't repeat.
- **Typology/thematic rotation:** 5 classes (Domestic · Public conduct · Workplace · Social organization · Consumer) rotated sequentially.
- **Coverage log:** central DB of used {character/location/stereotype/lesson/angle} to prevent overlap.
- **Controlled randomness ("Oblique Strategies"):** inject a lateral constraint into the divergent prompt (e.g. "the supporting character controls the space through silence"; "the conflict centers on an object smaller than a coin").

## 9. Pitfalls & programmatic safeguards

| Pitfall | Consequence | Safeguard |
|---|---|---|
| **Didactic trap** (characters explain grammar) | reads as an instructional ad | **ban pedagogical tokens** (lernen, bedeutet, Grammatik); no fourth-wall |
| **Visual slapstick drift** | unfilmable / off-budget | **restrict actions** to approved props/coordinates |
| **Character persona bleed** | uniform, generic voices | **re-inject immutable character dossiers** every cycle |
| **Dialogue loop inflation** | bloated, >45s | **repetition-detection filter** → regenerate |
| **Stereotype explaining** (naming it in dialogue) | kills the "game" | **stereotype-name banning filter** (name + synonyms) blocks commit |

## 10. Key sources
Dramatron (Mirowski et al. 2022); Fabula (arXiv 2606.14411); Kreminski & Chung "Intent Elicitation in MICI" (CEUR Vol-3660); Kreminski & Mateas "Reflective Creators" (2021); Compton & Mateas "Casual Creators" (2015); Guzdial & Riedl; Deterding (playful systems); "Artificial Hivemind" (NeurIPS 2025); German Modal Particles (Vyatkina & Johnson, CALPER); UCB "Game of the Scene"; Six Thinking Hats; Morphological Analysis (Zwicky).

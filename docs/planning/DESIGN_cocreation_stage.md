# DESIGN — The Co-Creation Stage (stereotype → story brief → screenplay)

> **Status: DESIGN, ready to build (2026-07-22).** Adapts `RESEARCH_cocreation_system_design.md` to *our* pipeline. Governed by CLAUDE.md working agreement. Decisions locked by Jayon inline.
> **Where it sits:** this is the **story stage** — it replaces the generic skill-1a/1b and produces a **Story Brief** that feeds the already-built screenplay writer (skill-2 v2.0 → segments/shots).

---

## 1. The flow (runtime), mapped to what exists

```
[0 PICK]      library.pick_options(3) ─ pick 1 stereotype        ✅ BUILT (pipeline/stereotypes.py)
[1 SEED]      human braindump (real take/anecdote)               ← anti-slop anchor
[2 CAST]      main (required) + side/guest/background            ✅ bibles exist; + dyad rotation
[3 ALIGN]     skill-1a → location options + lesson options       ← NEW skill (Focus)
[4 DIVERGE]   skill-1b → 3–5 comedic angles                      ← NEW skill (Flow, high temp)
[5 COMMIT]    skill-1c → critique → STORY BRIEF JSON             ← NEW skill (Focus, low temp)
                    │
                    ▼
[6 SCREENPLAY] skill-2 v2.0 (brief → 2–3 segments × shots)       ✅ BUILT
[6q QC]        skill-2q v2.0 (grammar-taught, not-explained…)    ✅ BUILT
                    ▼  → storyboard (Phase 4) → prompts → video
```

**Locked decisions**
- **Lesson = BOTH offered every time** (Jayon): skill-1a always proposes a **modal-particle** option AND a **grammar-structure** option (each with a pop-up-grammar note); the human picks one (or both) per episode; the brief records the choice.
- **Cast model** (Jayon, earlier): exactly one **main (mandatory)**; optional **side / guest / background** (the four selectable shapes).
- **Character mapping:** research placeholders → our canon food cast, roles preserved — **Rolf** = Enforcer/formal · **Kati** = Target/informal · **Bert** = Catalyst/slang · **Müller** = Victim/melancholic. (Reconcile against `resources/Characters-Main-Sheet.md` when building skill-1a.)

## 2. The Story Brief schema (the handoff artifact)

The commit step (skill-1c) emits this; skill-2 consumes it. Draft `STORY_BRIEF_SCHEMA`:

```
{
  "episode":   { "title_de", "stereotype_id", "stereotype_name", "category", "cefr_level" (A1|A2|B1) },
  "seed":      "<the human's braindump — the anti-slop anchor>",
  "cast":      { "main", "side"|"", "guest"|"", "background"|"" },   // canonical names
  "location":  "<chosen setting>",
  "comedic_angle": "<chosen typology / sub-genre>",
  "lesson":    { "particle"|"", "structure"|"", "pragmatic_function", "pop_up_grammar" },  // BOTH-offered → chosen
  "premise":   "<one line>",
  "game_of_scene": "<the implicit stereotype 'game' — NEVER named in dialogue>",
  "escalation_beats": [ "<base reality>", "<first unusual thing>", "<framing/if-then>", "<escalation>" ],
  "button":    "<the tag / payoff — no resolution>",
  "target_line": { "speaker", "german", "english", "why" },   // the anchor pedagogical line
  "oblique_constraint": "<the lateral curveball used, or ''>",
  "banned_terms": [ "<stereotype name + synonyms>", "lernen", "bedeutet", "Grammatik" ]  // kept OUT of dialogue
}
```

skill-2 (v2.1 tweak) then **consumes** the decided fields (stereotype/cast/lesson/beats) instead of re-deciding them, and turns `escalation_beats`+`button` into the 2–3 segment / multi-shot breakdown with the actual German dialogue — realizing the chosen lesson, honoring `banned_terms`.

## 3. The three new skills

| Skill | Mode / temp | In | Out |
|---|---|---|---|
| **skill-1a-align** | Focus / mid | stereotype + seed + cast + bibles + particle curriculum + location set | aligned params + **3–4 location options** + **lesson options (1 particle + 1 structure)**, each with reasoning + pop-up grammar |
| **skill-1b-diverge** | Flow / **high (T≈1.1)** | chosen location + lesson + cast + an injected **oblique constraint** | **3–5 distinct comedic angles** (SCAMPER-substitute / SCAMPER-reverse / What-If-ladder), each: premise · how the stereotype is the *game* · how the lesson lands naturally · button |
| **skill-1c-commit** | Focus / **low (T≈0.2)** | chosen angle + params | critique passes (didactic? filmable in 30s? particle in Mittelfeld? stereotype named? within 30–45s?) → the **Story Brief JSON** |

## 4. Cross-cutting mechanics to add

- **Per-stage temperature** in `stages._call()` (add a `temperature` arg): diverge hot, commit cold. *(New — `_call` currently has no temperature.)*
- **Safeguards (code validators on the brief + screenplay):**
  - **stereotype-name filter** — block commit if the stereotype name/synonyms appear in any dialogue line (extends skill-2q's `stereotype_shown_not_explained`).
  - **banned-token filter** — no `lernen / bedeutet / Grammatik`, no fourth-wall.
  - **repetition filter** — flag near-duplicate lines.
- **Variety engine:** dyad-rotation tracker (6 pairs) + typology rotation + the **oblique-constraint** injector (a small list surfaced randomly into skill-1b). Coverage already lives in `stereotypes_library.json`.

## 5. What's built vs new

| Have ✅ | Build 🔨 |
|---|---|
| Library + `pick_options` + coverage (Step 0) | 3 co-creation skills (Steps 3–5) |
| Character bibles (Step 2) | `STORY_BRIEF_SCHEMA` + `stage_story_brief` stages |
| Screenplay skill-2 / skill-2q v2.0 (Step 6) — **already has the not-explained + grammar-taught checks** | per-stage temperature + safeguard validators |
| Segment/shot schema + CEFR caps | dyad/oblique variety engine |
| — | the **wizard UI** (Phase 7 studio) that renders Steps 0–5 |

## 6. Build order (updates BUILD_PLAN_v3)
1. `STORY_BRIEF_SCHEMA` + the align/diverge/commit **stage functions** (mock-testable structure).
2. **skill-1a / 1b / 1c** prose skills.
3. Per-stage temperature + safeguard validators (unit-testable now).
4. skill-2 v2.1 tweak: consume the brief's decided fields.
5. Wire into `cli.py` (a `brief` / gated flow) — verifiable structurally; live runs need Anthropic credits.
6. Then the **wizard UI** (Phase 7).

*(1–4 are buildable and unit-testable WITHOUT credits; only live LLM runs are blocked.)*

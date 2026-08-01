# DESIGN — Stereotype integration (how 100 stereotypes serve a lesson-first system)

> **Status: PROPOSAL for Jayon's confirmation (2026-07-29).** How the 100-item stereotype library stays a first-class creative asset now that the pipeline is **lesson-first** rather than stereotype-first. Companions: `BLUEPRINT_story_system.md` · `CURRICULUM_v1_universe.md` · `SHOW_BIBLE.md` · `resources/stereotypes_library.json`.

---

## 1 · The insight that makes this easy
The story method (`STORY_SYSTEM` §1) is **reverse scenario generation**, and its central question is:

> *"What real-world situation naturally and frequently demands this grammatical structure?"*

**The stereotype library is a curated database of exactly 100 real German situations.** It is not a bolt-on to the method — it is a **pre-built answer bank for the method's core question.** Every entry is a specific, observable, culturally-loaded scene that already exists in the world.

And it fits the premise twice over: our characters are newcomers who don't understand this country, so **a stereotype encounter is the show's premise in action** — the moment someone collides with a rule nobody explained.

## 2 · Proof it works: the curriculum and the library already align
The curriculum (164 atoms) and the stereotype library (100 items) were built independently. They **already** overlap — which is the strongest evidence the matching will work:

| Curriculum atom | Stereotype | Fit |
|---|---|---|
| **A1.5.4 "Das Pfand"** (bottle deposit vocabulary) | **[003] Das Pfand-System** | The atom *is* the stereotype |
| **A2.2.5 "Verspätung!"** (delay frames) | **[081] Sonderverspätung der DB** | The atom *is* the stereotype |
| **A1.9 Wetter & Small Talk** | **[061] Jammern & Meckern** (opening social contact by complaining about weather/trains/prices) | Complaining about the weather *is* German small talk |
| **A1.9.5 "Schönes Wetter, oder?"** | **[065] Kein Smalltalk** | Perfect **inversion** — our newcomer attempts small talk and is shut down. The lesson is taught *by* the stereotype defeating it |
| **A1.8 Regeln** (`man darf nicht`, imperatives) | **[001] Bei Rot bleibt man stehen · [004] Mülltrennung · [005] Sonn- und Feiertagsruhe** | Rule-stereotypes *are* modal-verb generators |
| **A2.6 Feste** (toasting, invitations) | **[063] Prost & Augenkontakt** | The ritual demands the language |
| **A2.8 Ämter & Papiere** | **[006] Der Laminierte Zettel** (complaints via laminated notices) | Bureaucratic register, on a doorframe |

Two are already *character*, not situation: **Müller collects Pfand [003]** and **Müller has "the stare" [062] Der Deutsche Blick.** Which reveals the third mode of use, below.

## 3 · Three modes of use (not every use is the same)
| Mode | What it means | Cost | Frequency |
|---|---|---|---|
| **HOST** | The stereotype **is** the situation carrying the lesson. The scene happens because of it. | A full episode's creative weight | **Max one per episode** |
| **TEXTURE** | It happens in the background and is not the point — someone else frozen at the empty crossing while our scene plays out. | Nearly free; adds world density | Any time it fits |
| **RUNNER** | A stereotype has attached to a character permanently and become a trait. **Already happening:** Müller's Pfand-collecting and his stare. | One-time; then it's character | Rare, and it **graduates into `SHOW_BIBLE`** |

## 4 · The tagging schema (what must be added to each of the 100)
Matching must be a **deterministic filter, not a semantic search** (the context-agent research is explicit that vector retrieval returns near-misses). So each entry gains six fields:

| Field | Values | Why it exists |
|---|---|---|
| `module_affinity` | list of module ids, e.g. `["A1.8","A2.8"]` | The primary join to the curriculum |
| `structures` | free list, e.g. `["dürfen","müssen","man","imperative"]` | The language this situation naturally produces — human-readable nuance behind the module ids |
| `cefr_earliest` | `A1 \| A2 \| B1` | Earliest level at which the *behaviour* is legible and the required language exists |
| `setting` | e.g. `street · supermarket · apartment · transit · office · outdoors` | Enables the cheap-reuse rank: a stereotype set where we already have a locked location plate costs less |
| `visual_legibility` | `high \| medium \| low` | **The hard filter.** Can it be read with the sound off in 30 s? "Standing still at an empty crossing" = high. "Germans value privacy" = low |
| `encounter_type` | `rule_they_break · ritual_they_witness · expectation_they_fail · system_they_navigate` | Determines the **scene shape** — and maps directly onto the newcomer premise |
| `cast_affinity` | list of names (suggestion only) | Whose personality collides best — Kati × punctuality, Bert × hospitality, Müller × thrift, Rolf × anything requiring him not to care |

Coverage (`status`, `episode_id`) already exists and stays.

**How the tagging gets done:** one AI pass over all 100 entries against the curriculum module list, written back into `stereotypes_library.json`, then **human-reviewed by Jayon in the UI** (a simple review screen — accept/adjust per item). One-time job, a few hours.

## 5 · How the agent actually uses it
**At module ideation, the Showrunner runs this alongside its own scenario thinking — not instead of it:**

1. **Filter** (deterministic): `module_affinity` contains this module · `cefr_earliest ≤ current level` · `visual_legibility = high` (medium allowed with a warning) · `status ≠ covered`.
2. **Rank:** setting matches an already-locked location > `cast_affinity` includes the rotation's lead > category not used recently (variety) > never used.
3. **Surface 0–3 as options, each with the reason** — never as a decision. For example, for module **A1.8 Regeln**:
   > *"**[001] Bei Rot bleibt man stehen** — 3 a.m., an empty street, and everyone is standing motionless at a red light. It naturally produces `Man darf hier nicht…` and imperatives, which is exactly this module. We already have a street plate. Never used. Rolf would find it unbearable."*
4. **Zero matches is a valid outcome** and is stated plainly: *"No stereotype fits this module well — proposing original situations instead."*
5. **If Jayon picks one**, it becomes the situation that feeds reverse scenario generation. If he ignores them, nothing is lost.
6. **On episode completion**, coverage is marked, and the encounter is written to `UNIVERSE_STATE` (the characters now *know* this rule — which is itself a story fact).

## 6 · Guardrails
- **Never forced.** No quota, no "every module needs one". A module with no good match simply has none.
- **Never explained in dialogue** (`SHOW_BIBLE` §12.4, `TREATMENT` §11). The stereotype is scenography and situation; nobody narrates it.
- **One HOST per episode maximum.** Two competing cultural jokes crowd out the lesson.
- **Never mockery.** Per the bible: these are played as loving, self-aware archetypes — the characters are *confused by* the behaviour, and the joke is on the situation, never on real people.
- **Coverage is tracked, not chased.** The log prevents repetition; it is never a burn-down list.
- **Some of the 100 will never be used** — the low-legibility ones can't be shown in 30 seconds with the sound off. That is an honest outcome, and knowing it upfront is better than forcing them.

## 7 · The narrative dividend
Because our characters *don't know these rules*, every stereotype encounter does three jobs at once: it **teaches the grammar** the situation demands, it **generates the comedy** (the premise in action), and it **advances the arc** — each encounter is one more thing they've learned about living here. Over a season, the accumulated encounters *are* the assimilation story. The library isn't decoration on the curriculum; it's the texture of the world they're learning to survive.

## 8 · Build order
1. Jayon confirms this design.
2. `STORY_SYSTEM.md` is written with a short section pointing at this mechanism (the method owns the *question*; this owns the *answer bank*).
3. The tagging pass (AI + Jayon's review) — can happen any time before the first module ideation.
4. Showrunner implements the filter/rank/surface flow.
5. Coverage + encounter facts wire into `UNIVERSE_STATE`.

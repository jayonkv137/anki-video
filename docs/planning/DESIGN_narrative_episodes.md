# DESIGN — Narrative episodes: when the story is the priority

> **Status: PROPOSAL for Jayon's confirmation (2026-08-02).** He asked for episodes where *"the story is the priority and some of the language things are not"* — Season 0's portal intros as the primary case, but also, occasionally, inside a lesson: an episode that moves the arc, builds the world, or pays off a thread, taken with real cinematic ambition.
> He also asked for my concerns and how the agent should behave. Both are here, including one correction to what he described.
> Companions: `DESIGN_lesson_layer.md` (where the format is declared) · `PEDAGOGY.md` · `STORY_SYSTEM.md` · `SHOW_BIBLE.md` §9 (Season 0).

---

## 1 · The correction that shapes everything else

Jayon described narrative episodes as having *"more shots and much more creative storytelling"*. The second half is right and is the whole point. **The first half is not available, and it is worth being precise about why.**

- **More shots is a physical limit, not a policy one.** `TREATMENT` §8.3: a 15-second segment can hold only so many cuts before the model degrades, and the density stress-test applies identically in every mode. Declaring an episode "narrative" does not buy the video model more capability. **Eighteen cuts in fifteen seconds fails for a story reason too — nobody can read it.**
- **And more dialogue is the wrong direction.** `SHOW_BIBLE` §9 already describes Season 0 correctly: *"near-zero dialogue, maximum hook."* A learner at A1 cannot parse sixty words whether or not we are "teaching" them — the ceiling is about **comprehensibility**, not about teaching load. A narrative episode that talks more is *less* watchable, not more cinematic.

> **So the freedom is VISUAL, not verbal and not numeric.** What relaxes is *what the story is allowed to do* — cross worlds, withhold, reveal, end on a cliffhanger, follow an image instead of a lesson. What does not relax is physics, identity, or comprehensibility.

That is a stronger design than "the rules are looser here", because it points the liberty at the thing that actually makes these episodes good.

## 2 · What changes, exactly

| Rule | Teaching episode | **Narrative episode** |
|---|---|---|
| New atoms taught | required | **none** — the block teaches nothing new |
| Recycled language | optional | encouraged — the words already owned |
| Word ceiling | ≤30 / 55 / 80 | **stays, and should be spent far under it** — Season 0 targets near-zero |
| Target structure ≥2× | required | **not applicable** |
| One legible environment | required | **may break** — a portal sequence crosses worlds *by design* |
| Ends on a button, not a resolution | required | **may be a reveal, a cliffhanger, or a held image** |
| The optional shapes (§7) | offered | **set aside** — this is where invention belongs |
| Hook readable muted in 1s | required | **required, and it is the entire job** |
| Meaning visible on screen | required | **more important** — with less language, the image carries everything |
| No character explains language | required | **unchanged** |
| Material laws · silhouettes · naming | required | **absolutely unchanged** — identity is the series |
| Model limits (density, contact, hands, speed) | required | **unchanged** — physics does not read the format field |
| 30 seconds = 2 × 15s | required | **unchanged** |

## 3 · My concerns (he asked)

**C1 — The escape hatch.** The real risk is that any episode that is hard to write pedagogically gets reclassified as narrative, and the curriculum quietly stops advancing.
→ **Guard, already built:** the lesson layer's **coverage invariant**. A narrative block teaches no atoms, so its atoms must move to another block or be explicitly deferred *with a reason*. You cannot silently escape a hard atom — you can only visibly move it. Plus a flag when a lesson's narrative episodes outnumber its teaching ones.

**C2 — "Creative liberty" as a synonym for "unplanned".** These episodes are *more* expensive to get right, not less: no ceiling is catching bad work.
→ **Guard:** a narrative block still declares its **job** in the plan — *what it moves* (a thread planted, a relationship changed, a world fact established). "It's a cool scene" is not a job. If it moves nothing, it is decoration and the plan should say so.

**C3 — Continuity risk is higher.** A portal sequence, a flashback, a new world — these are exactly the episodes that establish canon facts, and they are the ones most likely to contradict something.
→ **Guard:** the contradiction check already exists and runs before any fact is written. Narrative episodes should be expected to *produce* canon facts, so the finalize step matters more here.

**C4 — The visual bar is higher and we cannot yet meet it.** Season 0's portal sequences (a world of dancing wurst; a bread-world football match; a transformation) are far harder to generate than two characters at a crossing. Crowds are on `TREATMENT` §8's known-failure list, and a "world full of them" is a crowd.
→ **Honest position:** Season 0 is the **hardest** thing in the series to generate and we have not generated anything yet. It should not be attempted until the C1 identity test passes and a simple two-character episode has actually worked. **The right first episode is a talking one, not a cinematic one** — which is the opposite of the instinct, and worth saying plainly.

**C5 — Mode drift within a lesson.** If episode 2 of a lesson is narrative and 1 and 3 are teaching, the lesson's rhythm can feel broken.
→ **Guard:** the through-line in `lesson.json` must account for it — the plan says *why* this beat is the narrative one.

## 4 · How the agent behaves — and the principle underneath

> **When the rules relax, the agent's judgement must tighten.**

In a teaching episode the agent is largely a constraint-satisfier: fit this atom into thirty seconds under these ceilings, and the ceilings catch a lot of bad work. In a narrative episode **nothing catches bad work except taste** — so this is the mode where an agreeable agent is most dangerous.

What changes in its behaviour:

| | Teaching mode | Narrative mode |
|---|---|---|
| **Its question** | "does this teach, inside the limits?" | **"is this worth watching, and what does it move?"** |
| **Options offered** | 2–3 workable scenarios | **more, and bolder** — including one deliberately outside the obvious |
| **Its critique** | compliance-shaped (ceilings, atoms, caps) | **story-shaped** — is the image strong, is the beat earned, does it land muted |
| **Pushback** | cites a rule | **cites the story** — "this ends on a joke where you wanted a wound" |
| **What it protects** | the lesson | **the world** — continuity, identity, and what a scene establishes forever |

**It is a collaborator, not a permission-granter.** Concretely: it should *offer the image Jayon did not ask for*, argue for a stronger version of his idea, and say plainly when a beat is not landing — while never touching identity, the material laws, or the model's real limits, which are not matters of taste.

**Anti-sycophancy applies harder here, not softer.** "Creative partner" does not mean "agrees". The Production Engineering Guide's mandatory-critique mechanic is *most* load-bearing in the mode with no ceilings.

## 5 · How it is declared, and where

A **block format**, set in the Plan phase — the mode is a property of the episode, decided when the lesson is planned:

| `format` | Means | Atoms |
|---|---|---|
| `lesson` | teaches new language | required |
| `synthese` | recycles the lesson, zero new | none new, `recycles` required |
| `narrative` | **serves the story; language is secondary** | none; must declare what it moves |
| `season_zero` | a portal intro — outside the curriculum | none; near-zero dialogue |

**Season 0 is modelled as a lesson with all atoms deferred** (`module_id: "S0"`, four blocks, one per character), so nothing needs a special case. It is planned, gated, produced and continuity-tracked exactly like every other lesson.

`narrative` blocks additionally require a **`moves`** field — the story job, in one line: *"plants the photo in Müller's jacket"*, *"Rolf and Kati acknowledge each other for the first time"*. Empty `moves` is a block.

## 6 · Edge cases

| Case | Decision |
|---|---|
| A lesson is *all* narrative | allowed only if every atom is deferred with a reason; flagged loudly — that is a story lesson, and the curriculum did not advance |
| A narrative episode ends up teaching something | fine, and welcome — record it in `recycles`, never in `atom_ids` (an atom is "taught" once, deliberately) |
| Jayon wants 45s for a narrative beat | allowed — `TREATMENT` §17's explicit exception. Still 15s segments; three of them. |
| Season 0 before any character is validated | **blocked by judgement, not by code** — see C4 |
| A narrative episode contradicts canon | the contradiction check halts it, as everywhere |
| A narrative episode with *no* dialogue at all | legitimate and expected; the subtitle stage simply produces nothing |
| Mid-production reclassification (teaching → narrative) | it is a re-plan: the atoms must be re-homed, and the invariant enforces it |

## 7 · Build

1. `narrative` added to `EPISODE_FORMATS`; `moves` required on narrative blocks; validators branch on format. *(done in this change)*
2. `PEDAGOGY` §2.1 — one short section: which ceilings still bind when nothing is being taught. *(Tier-1 /tune)*
3. `STORY_SYSTEM` §7.1 — the narrative episode as a named shape, with the "judgement tightens" rule. *(Tier-1 /tune)*
4. The Plan agent offers the format per block and must justify a narrative one (Phase 3).

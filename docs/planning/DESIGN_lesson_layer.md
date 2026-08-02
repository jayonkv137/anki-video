# DESIGN — The LESSON layer: the Plan phase, the block plan, and where stereotypes actually live

> **Status: PROPOSAL for Jayon's confirmation (2026-08-02).** Closes the architectural gap found on 2026-08-02: `block_no` exists on every episode, but nothing declares how many blocks a lesson has, so the system cannot say "2 of 3" and nothing guarantees three episodes of one lesson form an arc.
> **Jayon's decisions, incorporated:** the Plan phase gets its own gate · **Plan comes first, before the project brief** · each episode is generated as a separate unit but all episodes of a lesson are considered together for continuity and order · the episode count **can** change after episodes exist (add, reorder) · every episode must still declare what it teaches.
> **Constraint he set:** *"this does not need to be too much complicated or cross-change — just a normal update."* This is an **addition of one layer**, not a redesign. Nothing about the five episode phases changes.
> Companions: `PIPELINE.md` (stations) · `CURRICULUM_v1_universe.md` §2 (the module workflow this implements) · `DESIGN_stereotype_integration.md` (the tag schema) · `DESIGN_studio_chat.md` §1.

---

## 1 · The shape

```
LESSON  A1.8 “Regeln”                    ← lesson.json · ONE Plan phase · ONE gate
   the block plan: 3 episodes · which topics in each · the arc · the lead
        │
        ├── EPISODE 1 (block 1)   Idea → Script → Vision → Shoot → Post
        ├── EPISODE 2 (block 2)   Idea → Script → Vision → Shoot → Post
        └── EPISODE 3 (block 3)   Idea → Script → Vision → Shoot → Post
```

- **The lesson is the unit of planning. The episode is the unit of production.** Both are real; neither absorbs the other.
- **Plan runs once per lesson, first** — before any episode's brief. Its artifact `lesson.json` is a standing input to every phase of every episode in that lesson, exactly like canon, but lesson-scoped.
- **The five episode phases are untouched.** No station contract changes. This is one new station above them.

## 2 · What is decided where — the line that keeps it simple

The failure mode to avoid is planning all three episodes in detail before making one. That is waterfall, and it guarantees the plan is wrong by episode 2. So the split is deliberately uneven:

| Decided at the LESSON (once, in Plan) | Decided per EPISODE (in Idea, as now) |
|---|---|
| how many episodes, and **why that number** | the actual scenario and premise |
| **which topics go in which episode** | the beats, the button |
| the **through-line** — how the episodes relate | the target line, the dialogue |
| the **lead**, and who else recurs | the specific cast of that episode |
| the **world** — where this lesson lives | the exact location within it |
| the **stereotype encounter**, if one fits, and which episode HOSTs it | how it is shown |

**The lesson plan is a skeleton, not a script.** One line per episode is the target: *"Ep 2 — Rolf tests the rule and loses."* If a Plan conversation starts writing beats, it has crossed into the Idea phase and should say so.

## 3 · `lesson.json`

```jsonc
{
  "module_id": "A1.8", "level": "A1", "title": "Regeln",
  "why": "Rules and permission — what you may and may not do.",   // learner language
  "topics": ["A1.8.1", ...],                                       // from curriculum.json
  "lead": "Müller das Brot",
  "recurring_cast": ["Rolf die Wurst"],
  "world": "the neighbourhood — street, crossing, Späti",
  "through_line": "Rolf keeps testing rules; Müller keeps not reacting.",
  "encounter": { "stereotype_id": "001", "name": "Bei Rot bleibt man stehen!",
                 "mode": "host", "episode_no": 1 },
  "blocks": [
    { "episode_no": 1, "atom_ids": ["A1.8.4"], "recycles": [],
      "working_title": "Bei Rot", "shape": "Rolf tests the rule, Müller doesn't look",
      "episode_id": "ep_a1-8_1", "state": "made" },
    { "episode_no": 2, "atom_ids": ["A1.8.1","A1.8.2"], "recycles": ["A1.8.4"],
      "working_title": "Ich kann das", "shape": "…", "episode_id": null, "state": "planned" },
    { "episode_no": 3, "atom_ids": [], "recycles": ["A1.8.1","A1.8.4"],
      "format": "synthese", "working_title": "Regeln sind Regeln",
      "shape": "the gauntlet", "episode_id": null, "state": "planned" }
  ],
  "deferred_atoms": [],          // explicitly not taught in this lesson, with a reason
  "state": "in_progress",        // planned | in_progress | complete
  "plan_version": 2              // increments on re-plan; episodes record which they were made under
}
```

**The coverage invariant, and it is checkable:**
> every atom of the lesson appears in exactly one block's `atom_ids`, **or** in `deferred_atoms` with a reason.

Nothing may be silently lost between episodes. A validator enforces this at the Plan gate, and `deferred` is a legitimate, deliberate answer — not a failure.

## 4 · Continuity — how episode 2 knows about episode 1

This is the part Jayon named: *"every episode is generated separately, but all three are considered together."*

**Mechanism, using what already exists.** The view compiler (`studio.py`) already projects other phases of an episode as `[APPROVED …]` declarations. It gains one rule:

> **An episode of a lesson also receives its SIBLING episodes' locked screenplays — as `[EARLIER IN THIS LESSON]` summaries, never as transcripts.**

```
[LESSON PLAN A1.8] 3 episodes. Through-line: Rolf keeps testing rules;
                   Müller keeps not reacting. You are episode 2 of 3.
[EARLIER IN THIS LESSON] Ep1 “Bei Rot”: Rolf stepped off the kerb at an empty
                   crossing; Müller said “Man darf hier nicht gehen” without
                   looking at him. Ends on both waiting.
[LATER IN THIS LESSON]   Ep3 is the Synthese — plan for it, do not resolve it here.
```

Three consequences, all deliberate:
- **Backwards is fact, forwards is intention.** Earlier episodes are locked and binding; later ones are a plan and may still move.
- **Summaries, never transcripts** — the anti-role-bleed rule holds; an agent reading a sibling's full conversation would start re-deciding it.
- **The standalone rule still wins.** `STORY_SYSTEM` §6 requires every episode to land for a drop-in viewer. The arc is a *thread*, not a dependency: episode 2 may reference episode 1, but must not *require* it. QC checks this, and it is the single most important guard in this document.

## 5 · Editing the plan after episodes exist (Jayon: yes, allowed)

Four operations, each with a defined blast radius shown **before** it runs:

| Operation | What happens |
|---|---|
| **Add an episode** | new block appended or inserted; its atoms come from `deferred_atoms` or are split from a planned block. **Made episodes are untouched.** |
| **Reorder** | ⚠ the loudest warning in the system. If a made episode moves *after* one that referenced it, the through-line breaks. Allowed, but names exactly which episodes now reference something that follows them. |
| **Move atoms between blocks** | if the source block is already **made**, its screenplay is now teaching something the plan no longer assigns → the episode is marked **stale**, with the choice: re-plan around reality, or re-make the episode. |
| **Remove an episode** | its atoms return to `deferred_atoms` (never vanish). A made episode is never deleted by a re-plan — it is unlinked and kept. |

**The rule underneath: reality outranks the plan.** A made, exported episode is a fact. When the plan and a finished episode disagree, the default is to **correct the plan**, not to invalidate the work — with re-making offered as the deliberate alternative. `plan_version` records that a re-plan happened, and each episode records the version it was made under, so drift is visible rather than silent.

## 6 · New problems this introduces (named honestly)

| Problem | Guard |
|---|---|
| **Over-planning** — deciding all 3 episodes in detail up front | the plan is a skeleton (§2); one line per episode; a Plan agent that writes beats is told it has crossed into Idea |
| **Plan/reality drift** — ep 1 turns out different, plan is stale | `plan_version` + a stale marker; the plan is revisable and the Plan gate can be reopened like any other |
| **Arc vs standalone tension** | already resolved in canon: standalone *situation*, serial *thread*. QC enforces the standalone side, which is the one that pays. |
| **Atoms lost between episodes** | the coverage invariant (§3), validated at the gate |
| **A lesson that never finishes** | `complete` with `deferred_atoms` is legitimate — finishing 2 of 3 and moving on is a real decision, not an error state |
| **Lesson bloat** — 6 episodes for one lesson | soft flag past 4: the level's atom count and the 30s block law rarely justify more |
| **Two episodes teaching the same NEW atom** | blocked (an atom is new once); appearing as `recycles` is encouraged |
| **Reordering silently breaking continuity** | see §5 |
| **The lead changing mid-lesson** | allowed, flagged: it weakens the through-line, and the Plan should say so rather than the Writer discovering it |

## 7 · Where stereotypes plug in — the complete map

Jayon's question was *"is this known anywhere, by any agent, at any step?"* Today: no. Here is every touchpoint, in order.

| # | Where | What happens |
|---|---|---|
| 1 | **`stereotypes_library.json`** | gains the tags `DESIGN_stereotype_integration` §4 already specifies: `module_affinity` · `structures` · `cefr_earliest` · `setting` · `visual_legibility` · `encounter_type` · `cast_affinity`. **One AI pass over 100 items → Jayon reviews accept/adjust.** |
| 2 | **`stereotypes.py`** | gains `suggest_for_lesson(module_id, level)` — a **deterministic filter** (affinity contains the module · level ≤ current · legibility high · not covered) then a rank (locked location > cast fit > variety > never used). Never semantic search. |
| 3 | **PLAN phase** ← *the primary integration point* | the Showrunner surfaces **0–3 candidates with the reason**, and **zero is a valid, stated outcome**. If one is taken, it is assigned a **mode** and, for HOST, a specific `episode_no`. |
| 4 | **IDEA phase** | the chosen encounter flows into `brief.encounter` (the schema slot that already exists and is currently always empty) |
| 5 | **SCRIPT phase** | the Writer realises it as **situation and scenography** — `SHOW_BIBLE` §12.4 and `STORY_SYSTEM` §10.2 already forbid naming or explaining it in dialogue |
| 6 | **QC** | checks *shown-not-explained*, and that `banned_terms` (the stereotype's name and synonyms) never appear in a line — already partly enforced by `forbidden_in_dialogue` |
| 7 | **POST / finalize** | `mark_covered(id, episode)`; the encounter is written to `UNIVERSE_STATE` as a story fact — **the characters now know this rule**, which is itself continuity |
| 8 | **The studio chat** | can answer "which stereotypes fit lesson 9?", and can retag one on Jayon's confirmation |
| 9 | **`SHOW_BIBLE`** | a **RUNNER** — a stereotype that has become a character trait (Müller's Pfand, his stare) — graduates out of the library into the bible as identity. A Tier-1 edit, proposed never written. |

**The three modes stay as designed:** **HOST** (the stereotype *is* the situation — max one per episode, assigned to one episode of the lesson) · **TEXTURE** (background density, any episode, free) · **RUNNER** (graduated to character).

**Why the Plan phase is the right home for it:** a stereotype is a *situation*, and `STORY_SYSTEM` §1's reverse scenario generation asks "what real situation naturally demands this structure?" — which is a **lesson-level** question, asked once, when the lesson's world is being decided. Offering stereotypes per-episode would invite a different cultural joke every 30 seconds; offering them per-lesson gives the lesson a world.

## 8 · What each agent must now know

The addition is one artifact in each context contract. Nothing else moves.

| Phase | Gains |
|---|---|
| **Plan** *(new)* | curriculum module + state + rotation + **stereotype candidates** + the seed bank |
| **Idea** | `lesson.json` + sibling summaries + its own block's `atom_ids` |
| **Script** | `lesson.json` (through-line, world) + sibling summaries |
| **Vision / Shoot** | `lesson.json` (world, tonal mode, locked location plates) — so three episodes of a lesson look like one place |
| **Post** | `lesson.json` (which atoms this episode was responsible for, for the final audit) |
| **QC** | the block's `atom_ids` + the standalone check + shown-not-explained |

## 9 · Canon changes required

1. **`PIPELINE.md` → v1.3 (Tier-1 `/tune`)** — a new station **§3.0 LESSON PLAN**, placed before §3.1, with its own `MUST NOT decide` list; §2.1 gains the Plan phase; §5 gains the **lesson plan gate**; §6's dependency graph gains `lesson.json → all episodes of the lesson`.
2. **`CURRICULUM_v1_universe.md`** — §2's four-step workflow is already exactly this; add a pointer noting where step 1–2 now live.
3. **`STORY_SYSTEM.md`** — one line in §8 (Arc & Continuity): a lesson's episodes share a through-line, and the standalone rule still outranks it.
4. **No change** to TREATMENT, PEDAGOGY, SHOW_BIBLE, MISSION.

## 10 · Build order

1. `LESSON_V4` schema + the coverage validator (cheap, and makes the invariant real)
2. `PIPELINE` v1.3 + registry re-pin
3. `lesson.json` store + the Plan phase in `studio.py` + `lesson_planned` in state → **"2 of 3" becomes true**
4. The stereotype tagging pass + `suggest_for_lesson`
5. The Plan agent (Phase 3, with the Showrunner)

## 11 · Open

- **Does a lesson share ONE location plate across its episodes by default?** (I would say yes — it is cheaper, it makes the lesson feel like a place, and `TREATMENT` §16.4 wants location plates accumulated anyway.)
- **Should Season 0 intros be modelled as a lesson with no atoms**, or as a separate kind? (I would say a lesson with `deferred_atoms` = all and `format: season_zero`, so nothing needs a special case.)

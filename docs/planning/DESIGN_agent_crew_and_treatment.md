# DESIGN — Agent crew + the Treatment document (from the invideo production method)

> **Status: DECISIONS DRAFTED (2026-07-29), not built.** Source: 12 invideo production guides (Jayon, Desktop PDFs; text extracted to scratchpad — key ones read in full: *Showrunner + Director Agent Hierarchy*, *The Treatment Document*, *Treatment-First Screenplay Method*). This doc is the **filter + build plan**, not an archive. Companions: `DESIGN_universe_state.md` (the memory layer) · `CURRICULUM_v1_universe.md` (the spine) · `architecture.md` (what exists today).

## 1 · The method in one paragraph
**Two-tier crew.** ONE **showrunner agent** holds the show bible — tone, characters, world, canon, locked cast + location sheets, locked scripts — and is the single source of truth; it *never generates footage*. Per episode you spin a **director agent** with its own isolated workspace that **reads the locked script and pulls canon (never modifies it)**, derives a shot breakdown, and runs generation. Setup order is fixed: one project per series → showrunner + bible → **lock cast & location sheets** → **lock scripts** ("locked scripts put agents into execution mode; unlocked scripts invite drift") → spin directors. Mid-series changes are cheap because **"update the context once, the agent remembers for every episode."** Directors can run in parallel because **"agents inherit context, they never own copies of it."**
**The controlling document is not the screenplay — it's the TREATMENT:** a ~14-section rule system (camera, lenses, angles, lighting *as ratios*, color as *named modes*, composition, movement, atmosphere, mood registers, references, sound, prompt-assembly order, negative/never-do rules, quick-reference card), loaded once, against which the agent **gates every shot**. Its quality bar: **"write rules, not descriptions"** — *"warm lighting"* is a description; *"warm yellow from the lamps only"* is a rule a frame can be checked against.

## 2 · Mapping: what we already have vs. the gap
| invideo practice | Our status |
|---|---|
| Showrunner holds bible, never generates | **Designed, not built** (`DESIGN_story_ideation_and_overseer.md`) |
| Director agent per episode, isolated workspace, executes locked script | **Effectively exists** — our per-run pipeline + `ep_<run_id>/` compartmentalisation |
| "Locked scripts = execution mode" | **Core principle already** — screenplay = THE LOCK; downstream are compilers |
| Canon read-only to executors; showrunner owns it | Overseer already edits the lock + recompiles; permissions **not formalised** |
| Locked **character** sheets before any generation | **Have** (sheet + portrait + voice per character) |
| Locked **location** reference sheets | ❌ **MISSING** — real gap for a recurring-world series |
| **Treatment document** (14-section rule system, gates every shot) | ❌ **Scattered** across `canon_blocks.md`, skill prose, `global_aesthetic_rules` — and partly *descriptive* rather than rule-form |
| Fixed **prompt-assembly order** | **Have** (Seedance canon order in skill-3; sheet template in skill-2b) |
| **12 parameters per shot** | **Partially** — our director layer covers ~7; missing lens, colour script, atmosphere, negative + **revision prompt** |
| Agent **gates output** against the treatment before returning | ❌ **Missing** — no pre-generation validation |
| **Script audited against model limits** before spending credits | ❌ Missing (their example: 18 cuts in 15s flagged pre-generation) |
| Validation test that the agent *internalised* the style | ❌ Missing |
| 3–4 options per shot; "overgeneration is a planned budget line" | We generate 1 |
| Update context once → every later episode inherits | = `UNIVERSE_STATE` (designed, not built) |

**Conclusion: the delta is small and well-defined.** We are not missing an architecture — we are missing (a) the persistent state layer, (b) the Showrunner front door, (c) a consolidated Treatment, (d) location sheets.

## 3 · What we adopt (ranked by leverage)
1. **The Treatment document** — consolidate `canon_blocks` + style + character bible + our pedagogy constraints into ONE rule-form directive doc that every visual stage reads. Rewrite descriptive lines as checkable rules. *This is creative work, not code, and it is the highest-leverage thing available.*
2. **Location reference sheets** — lock a plate per recurring location, exactly as we lock character sheets. Feeds the sheet prompts + `UNIVERSE_STATE`.
3. **Formal read/write split** — Showrunner owns canon; every downstream stage reads. (Same conclusion the context-agent research reached via its write-permission matrix — two independent sources agreeing.)
4. **Pre-generation gates** — (a) audit the block plan/screenplay against model limits + our guardrails *before* generating; (b) check the assembled prompt against the treatment before spending credits.
5. **Add the missing per-shot parameters** — notably **negative prompt** and **revision prompt** (pre-planned fix so iteration stays on-grammar).
6. **The internalisation test** — before production, ask the agent to apply our visual system to a scene type the show has never done; clarifying questions + coherent output = it absorbed grammar, not surface.
7. *(Later)* 3–4 options per shot once real generation is running.

**Not adopting:** per-episode *separate agent instances* (invideo's "notebook page" per director is their UI's isolation primitive — our `ep_<run_id>` directories + typed Overseer already give us the same compartmentalisation without spawning agents); their $/minute economics (different scale); model-routing across many video models (we're on Seedance).

## 4 · The build plan — one thin vertical slice, in order
**Principle: stop researching, build the narrowest path that produces one real lesson end-to-end.**

- **Step 0 (no code):** write the **Treatment** + lock **location sheets** for the first module's world. Freeze `curriculum.json`.
- **Step 1:** `UNIVERSE_STATE` (5 strata per `DESIGN_universe_state.md`) + curriculum status.
- **Step 2:** **Showrunner front door** = Jayon's screen flow: *New lesson / Resume / Completed* → agent explains the lesson (left panel + approve) → story-so-far (left panel + approve) → **asks for HIS ideas first, offers options only on request** → **project brief** (N episodes, cast, rough narrative).
- **Step 3:** **Director/screenplay agent per episode** — drafts the full parameterised screenplay from the brief + treatment + state, then discusses/edits → confirm → formatted editable document view.
- **Step 4:** everything downstream **already exists and is verified** (storyboard sheets → Seedance prompts → assembly → subtitles → export, with the Overseer floating over all of it).

## 5 · Required changes to the current build
Step 01 becomes **"New lesson"** (stereotype pick demoted to an *offer* inside ideation) · brief gains `lesson_id`, `block_plan`, `lead_character` · skill-2 reads the Treatment + `UNIVERSE_STATE` instead of a bare brief · skill-2q becomes the guardrail + model-limit audit · storyboard/prompt skills read the Treatment's rule blocks rather than improvising a `style_clause`.

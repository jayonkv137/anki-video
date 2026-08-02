# Handoff Packet — 2026-07-29 · V4 pivot + the production canon

## Objective / non-goals
Two things happened this session. **(1)** Finished and shipped the storyboard/Strategist/Overseer/subtitle work from the previous packet. **(2)** The **V4 pivot**: from "daily standalone stereotype reels" to a **curriculum-driven serialized story universe** (A1→B1, ~170 × 30s episodes), and built the **production canon** — six hash-pinned documents that carry everything the agents need to know.
**Non-goals:** nothing was wired. The canon exists and verifies; **no skill reads it yet**. No agent was built.

## Exact position
- **Built + verified earlier this session:** storyboard **sheet method** (one generation per segment → slice → chain) · **Story Strategist** wired into the chat · the **Overseer** (propose→confirm→apply with graph-computed recompiles) · **subtitle engine + Assembly Studio** (declarative `subtitles.json`, live overlay, burn/export) · shots-per-segment cap removed.
- **Designed this session, not built:** the entire V4 layer — curriculum, Showrunner, `UNIVERSE_STATE`, the 4-agent/5-phase studio.
- **The critical gap:** six canon documents are correct, hash-pinned and green — and **the pipeline still runs on the old improvised prose.**

## Files touched (36 commits, `dde3108..bd33f2d`; all pushed)
**New canon:** `prompts/canon/{TREATMENT,SHOW_BIBLE,STORY_SYSTEM,PEDAGOGY,PIPELINE}.md` · `MISSION.md` rewritten v2.0 · `prompting_guidelines_omni.md` **retired**.
**New planning:** `CURRICULUM_v1_universe.md` · `NARRATIVE_BIBLE_seed.md` · `AUDIT_visual_identity.md` · `WORKFLOW_visual_identity_lock.md` · `PLAN_production_canon.md` · `BLUEPRINT_story_system.md` · `DESIGN_{universe_state,agent_crew_and_treatment,stereotype_integration,studio_ux,board_iteration}.md` · `RESEARCH_context_agent_architecture.md` · `DEEP_RESEARCH_PROMPT_{context_agent,nanobanana,agent_implementation}.md` · `architecture.md` rewritten twice.
**Code:** `pipeline/rcp.py` (omni removed from the RCP).

## Decisions + why
- **V4: curriculum-driven universe** — 3 levels × 10 modules × **164 teaching atoms**; atoms are an *inventory*, packed into universal **30-second blocks** at ideation (`CURRICULUM_v1_universe.md`).
- **Story method = reverse scenario generation** — structure → the situation that naturally demands it → the scene (`STORY_SYSTEM.md` §1).
- **Characters keep personality, lose all speech constraints** — required, not preferred: a "shortest sentences in the show" rule makes B1 impossible for that character (`SHOW_BIBLE.md` §5).
- **Colour = a hierarchy rule, not a hue rule** — "the cast always wins the frame"; the earlier northern-Germany justification was wrong (`TREATMENT.md` §6.1).
- **Lighting = named source + ratio**, never mood words (`TREATMENT.md` §5).
- **Subtitles = static colour-coded clauses** — keep the colour key (the retention win), drop word-by-word karaoke (destroys perceptual span) (`PEDAGOGY.md` §5.2).
- **Studio = 4 agents / 5 phases / one continuous chat** (Idea·Script·Vision·Shoot·Post); QC never speaks; **the always-present chat replaces the separate overseer window** (`DESIGN_studio_ux.md`).
- **Board edits route by ownership** — "anything the screenplay describes changes in the screenplay; anything it doesn't may be fixed in the image" (`DESIGN_board_iteration.md`).
- **Stereotypes = a situation bank**, the answer bank for reverse scenario generation; three modes HOST/TEXTURE/RUNNER (`DESIGN_stereotype_integration.md`).

## UNVERIFIED (do not trust without testing)
- **No skill has ever read the new canon.** All six documents are untested in a live generation.
- **No `FAL_KEY`** — real Nano Banana Pro and Seedance have still never been called. Mock providers only.
- **The curriculum is unlocked** — `curriculum.json` does not exist; the 164 atoms live only in markdown.
- **The colour law is theory** — deferred by Jayon until real episodes exist (`WORKFLOW_visual_identity_lock.md`).
- **`UNIVERSE_STATE` does not exist**, so `SHOW_BIBLE` §10 Directions and §11 Canon Facts have no home.

## Commands run + real results
- `verify_canon()` → **GREEN**, 9 files: PIPELINE 1.1 · PEDAGOGY 1.0 · STORY_SYSTEM 1.0 · SHOW_BIBLE 1.1 · TREATMENT 1.1 · MISSION 2.0 · canon_blocks 1.0 · seedance 2.2 · Characters-Main-Sheet 1.3.
- Omni retirement verified by assertion: `'OMNI' not in rcp.for_prompt_stage()` ✓ (context now 10,423 chars).
- `import dashboard.app, pipeline.stages, pipeline.overseer` → OK.
- Constraint scrub on `SHOW_BIBLE` → only hit is the anti-constraint rule itself ✓.

## Failures distilled
- **`MISSION.md` had rotted for months** — V2-era text injected into every call, including the word "puppet" which `TREATMENT` bans. Cause: manual hash ritual made updating painful. *A canon-update helper would have prevented this.*
- **`prompting_guidelines_omni.md` was dead since the V3 reshape** yet still hash-verified and injected into every prompt-stage call.
- **My "northern Germany = cool desaturated" colour law was wrong** — contradicted the cast's own regional spread. Corrected to a hue-independent hierarchy rule.
- **I over-specified the first context-agent research prompt**, which would have produced validation instead of research. Rewritten open, ~60% shorter.

## Open risks
- The canon is **large and unread by any agent** — value is zero until wiring lands.
- The **studio UI redesign and the canon wiring are now the same job**; doing them separately would waste the work.
- Gemini structured output is **not schema-enforced** (`response_schema` unset) → field drift.
- `canon_blocks.md` is still live and duplicated inside `TREATMENT` §10 — two sources for one truth until it is folded.

## Next 3 steps
1. **Run the two research prompts** — `DEEP_RESEARCH_PROMPT_nanobanana.md` (→ becomes `prompting_guidelines_nanobanana.md`, the image-model canon file that does not exist) and `DEEP_RESEARCH_PROMPT_agent_implementation.md` (→ how to actually build the four agents).
2. **Lock the curriculum** → `resources/curriculum.json` + registry pin.
3. **Build the combined slice: UNIVERSE_STATE → the 5-phase studio + canon wiring** (the phases load the canon by definition, so wiring happens as each phase is built). Includes: fold `canon_blocks` into `TREATMENT`, delete `global_aesthetic_rules`, fix the UI storyboard path's missing canon substitution, apply `TREATMENT` §9 reference order/budgets, and correct the subtitle engine (static clauses, `das` → `#10B981`).

## Also outstanding (smaller)
Screenplay schema is missing three fields the Treatment specifies — **named light source + ratio, negative prompt, revision prompt** — and **props are not a first-class field** (buried in `action`, though `TREATMENT` §13 requires specifying a prop's sound behaviour). The screenplay stage should also gain the "argue with the page" duty: flag ungeneratable shot density *before* boards are generated.

**⚠ Dangling reference found during handoff:** `skill-3-prompt-writer.md` still carries a **Wardrobe Override Rule** referencing a `wardrobe_overrides` screenplay field that **no longer exists** — Jayon added the feature (changelog 2026-07-24) and removed it again in commit `7764af7`, but skill-3 was not cleaned up. The changelog entry for that feature is therefore also stale. Fix during wiring.

## Reread-first
1. `docs/architecture.md` — the whole machine, the reasoning, and honest build status
2. `prompts/canon/PIPELINE.md` — stations, the studio layer (§2.1), the dependency graph (§6)
3. `docs/planning/DESIGN_studio_ux.md` — 4 agents / 5 phases / one chat
4. `docs/planning/CURRICULUM_v1_universe.md` — the spine (164 atoms, the 30s block law)
5. `prompts/canon/{SHOW_BIBLE,STORY_SYSTEM,PEDAGOGY,TREATMENT}.md` — the knowledge layer
6. `docs/planning/DESIGN_universe_state.md` — the memory layer to build next

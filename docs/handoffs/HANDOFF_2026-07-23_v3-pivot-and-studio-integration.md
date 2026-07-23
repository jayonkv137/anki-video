# Handoff Packet — 2026-07-23 · V3 pivot + full studio integration

## Objective / non-goals
Execute the **V3 pivot**: pipeline redesigned from 10 word-scenes → **stereotype-driven, 2–3 × ~15s Seedance multi-shot clips**, with a human-in-the-loop **co-creation studio**, and the whole pipeline **wired into the UI** so a human walks stereotype → brief → screenplay → storyboard prompts → video prompts (generate images/video MANUALLY, upload back).
**Non-goals this session:** automated video gen (still old per-scene); the overseer agent (designed, not built); the Socratic chat upgrade (skill drafted, not wired).

## Exact position (see `BUILD_PLAN_v3.md`)
**Done + verified:** Phase 0 governance · 1 canon /tune (seedance **v2.2**, REGISTRY 1.4) · 2 adapter → `seedance-2.0/reference-to-video` · 3 screenplay reshape (episode→**segments→shots**, director layer + per-shot `duration_s`) · **3L** stereotypes library (100 + coverage) · **3C** co-creation (skills 1a/1b/1c + stage_align/diverge/commit + CLI `brief-*`) · **4** storyboard (skill-2b + `providers/image.py` + stage_storyboard + `pipeline storyboard`) · **5** skill-3 **v4** thin per-15s-segment Seedance compiler · **UI integration** (7 `/api/v3/*` endpoints + `index.html` steps 04–07 wired).
**In-flight / next:** Phase 6 (reshape `stage_generate`/`assemble`); wire `skill-1-story-strategist` into the chat; the overseer.

## Files touched (git: 23 new + 18 modified, ALL uncommitted before this handoff)
New: `docs/planning/{BUILD_PLAN_v3, DESIGN_v3_data_flow, DESIGN_cocreation_stage, DESIGN_story_ideation_and_overseer, VISION_v3_universe_and_studio, RESEARCH_shortform_pedagogy_framework, RESEARCH_german_stereotypes_compendium, RESEARCH_v3_tech_derisk_seedance_and_storyboard, RESEARCH_cocreation_system_design, RESEARCH_storyboard_stage_design, RESEARCH_story_ideation_agent, DEEP_RESEARCH_PROMPT_*}.md` · `prompts/skills/{skill-1-story-strategist,1a-align,1b-diverge,1c-commit,2b-storyboard}.md` · `pipeline/{stereotypes.py, providers/image.py}` · `scripts/ingest_stereotypes.py` · `resources/stereotypes_{library.json, source.xlsx}`.
Modified: `pipeline/{stages.py, cli.py, providers/{video.py,__init__.py}}` · `prompts/skills/skill-{2,2q,3}` · `prompts/canon/{prompting_guidelines_seedance.md, REGISTRY.md}` · `dashboard/{app.py, static/index.html}` · all `docs/`.

## Decisions + why (doc where recorded)
- **V3 shape** 10→2–3×15s, stereotype-first — `VISION_v3` / `VISION_HISTORY`.
- **Seedance 2.0** (2.5 announced, NOT live — web-verified) — `RESEARCH_v3_tech_derisk` §, `RESEARCH_storyboard_stage_design` §6.
- **30s default · stereotype-first vocab · lesson = BOTH particle + structure offered** — `DESIGN_cocreation_stage`.
- **Screenplay = the LOCK; storyboard+prompt skills = thin COMPILERS; NO text in Seedance; subtitles = separate post step; director-layer in screenplay** — `DESIGN_v3_data_flow`.
- **Storyboard model = GPT Image 2 AND Nano Banana Pro (both selectable, test to pick)** — `RESEARCH_storyboard_stage_design`.
- **Co-creation = one Socratic "Story Strategist" (unifies align/diverge/commit); overseer feasible via lock+compiler dependency graph** — `DESIGN_story_ideation_and_overseer`.
- **LLM = Gemini** (Anthropic credits exhausted) — Jayon wired `stages._call → _call_gemini`.

## UNVERIFIED (do not trust without testing)
- **The LLM stages never ran live end-to-end via Gemini.** Gemini structured-output on the deep `SCREENPLAY_SCHEMA` (episode→segments→shots→dialogue) is the **most likely failure point**.
- **No `FAL_KEY`** → GPT Image 2 / Nano Banana / real Seedance never called; those adapters are `⚠ confirm`-flagged in code.
- **The UI flow was never live-clicked** (in-app browser blocks `localhost`). Verified only: server boots, `/api/stereotypes` real, frontend JS parses.
- **`skill-1-story-strategist` is NOT wired** — `/api/co-creation/chat` still uses a thin inline prompt (pedagogy weak in the chat).
- **Possible puppet-vs-photoreal contradiction**: character sheets look puppet-styled in the UI while canon/skills demand photoreal + ban puppet words. Not verified against `resources/`.

## Commands run + real results
- `verify_canon()` → **canon GREEN** (seedance 2.2, omni 1.2, canon_blocks 1.0, main-sheet 1.3, MISSION 1.0).
- `import pipeline.stages, pipeline.cli, dashboard.app` → **OK**; all 7 `/api/v3/*` routes registered.
- Unit tests: `validate_screenplay` good→`[]` / bad→flags (segment count, 15s cap, CEFR, shot-duration-sum) ✓ · `validate_brief` 7-defect catch ✓ · `stage_storyboard` mock **3 panels + storyboard.json** ✓ · `stage_prompts` stubbed → per-segment `segment_NN.seedance.json` + refs_manifest **resolves panel s01_01** ✓ · image mock **720×1280 PNG** ✓ · library `pick_options(3)` + `mark_covered` ✓.
- Dashboard booted on :8790 → `/api/stereotypes/summary` = **100 stereotypes / 100 uncovered**; frontend `node --check` **clean**.
- `git log` HEAD=`1c601ae` (learning-ledger); last work commit `750ce52`.

## Failures distilled
- Storyboard research assumed **Seedance 2.5** → it's announced, not live → build on **2.0** (15s, 9-image budget); earlier canon 2.5→2.0 correction was right.
- UI co-creation **forked** (governed skills vs thin inline chat) → chat lost the pedagogy; `/api/v3/commit` now produces a real full brief but the chat itself is still thin.
- Heredoc `$` mangling made a `node --check` falsely fail → the JS actually parses clean (harness bug, not code).

## Open risks
- Gemini structured-output failing on the deep screenplay schema (untested).
- **Downstream `stage_generate`/`stage_finalize`/`assemble.py` still on old per-scene `scenes[]`** → automated video not runnable (Phase 6). Manual-upload path (UI) works around it.
- **Two co-creation implementations coexist** (legacy `/api/co-creation/{align,diverge,chat/extract}` vs new `/api/v3/commit`) — drift risk.
- Anthropic credits exhausted (on Gemini); no `FAL_KEY`; puppet-vs-photoreal asset flag.

## Next 3 steps
1. **Restart uvicorn (:8787)** and walk the full UI flow; capture any Gemini structured-output error (screenplay stage most likely).
2. **Wire `skill-1-story-strategist` into `/api/co-creation/chat`** (phases + `ready_to_commit`) so the chat becomes the disciplined Socratic partner.
3. **Phase 6** (`stage_generate`/`assemble` per-segment) **or** the **overseer agent** (typed edit/regen tools over the persisted `ep_<run_id>` artifacts + the dependency graph).

## Reread-first
1. `docs/planning/BUILD_PLAN_v3.md` — map + live phase status
2. `docs/planning/DESIGN_v3_data_flow.md` — lock/compiler contracts, image/audio budget, no-text rule
3. `docs/planning/DESIGN_cocreation_stage.md` + `DESIGN_story_ideation_and_overseer.md`
4. `dashboard/app.py` (`/api/v3/*`) + `dashboard/static/index.html` (steps 04–07)
5. `pipeline/stages.py` (schemas + stages; `_call`→Gemini) + `prompts/skills/skill-1-story-strategist.md`
6. `docs/project_status.md` — Where we left off

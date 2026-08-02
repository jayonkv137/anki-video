# Handoff Packet — 2026-08-02 · The V4 spine, the lesson layer, and the UI reset

## Objective / non-goals
Three things happened. **(1)** The V4 studio went from *designed* to *built*: canon locked and corrected, a schema-enforced LLM layer, per-phase context, UNIVERSE_STATE live, the studio shell, the lesson layer, and a layout-agnostic API. **(2)** A **drift detector** (`canon-audit`) and four test suites now verify the system mechanically — they found real bugs, repeatedly. **(3)** The UI was built, **reviewed by Jayon, and rejected**; the information architecture survived, the presentation did not, and the rebuild is now the open work.
**Non-goals:** no agent has been built (Phase 3). **Nothing has ever been generated** — no real Seedance call, no character render, no episode. The C1 identity test remains unrun.

## Exact position
- **Canon: 9 files, `verify_canon` GREEN, and now the RIGHT nine.** MISSION 2.1 · SHOW_BIBLE 1.2 · STORY_SYSTEM 1.1 · PEDAGOGY 1.1 · TREATMENT 1.4 · PIPELINE 1.3 · seedance 2.2 · **nanobanana 1.0 (new)** · **`curriculum.json` 1.0 (new)**. REGISTRY 1.19.
- **Built and tested:** `llm.py` (schema-enforced, loud failures) · `context.py` (per-phase canon) · `universe_state.py` (strata 2–4 live in Supabase) · `schemas.py` (lesson/brief/screenplay v4 + validators) · `studio.py` (thread, phase router, **view compiler**, gates) · `lessons.py` (the block plan) · `canon_audit.py` · `dashboard/studio_api.py` (`/api/studio/*`).
- **Suites: lessons 34 · studio 44 · api 39 · spine 52 · canon-audit 12 (0 errors, 1 expected warning).** All green.
- **The open work:** the UI. `DESIGN_screen_home.md` (the brief) and `DESIGN_system_ui.md` (the method) are written; **no design system and no screens exist**.

## Files touched (18 commits, `f5d06bd..HEAD`, all pushed)
**New canon:** `prompting_guidelines_nanobanana.md` · `resources/curriculum.json` (+ `scripts/build_curriculum.py`).
**New code:** `pipeline/{llm,context,schemas,universe_state,studio,lessons,canon_audit}.py` · `dashboard/studio_api.py` · `scripts/test_{spine,studio,studio_api,lessons}.py` · `scripts/migrations/002_universe_state.sql`.
**New design docs:** `BUILD_PLAN_v4_studio` (governing) · `DESIGN_{screenplay_document,autopilot,studio_chat,lesson_layer,narrative_episodes,screen_home,system_ui}` · `RESEARCH_invideo_production_guides` · `DEEP_RESEARCH_PROMPT_design_system_workflow`.
**Deleted:** `assemble.py`, `stage_finalize/generate/caption`, `substitute_canon`, word-deck stages, 6 skills → `_retired/`, ~185 lines of fabrication in `app.py`.

## Decisions + why
- **D1–D7 approved** (BUILD_PLAN §9): PEDAGOGY's word ceilings win · `Character-X` tokens in image prompts only · characters-first reference order · ≥5-shot segments split into two chained sheets · §3.9 renamed **the change protocol** · phases Idea·Script·Vision·Shoot·Post.
- **D8 — two working modes, not autopilot.** Jayon rejected the trust ladder: unattended generation spends money on unseen work. **Every gate stays human**; what becomes optional is the *conversation*. `Co-create` (default at Idea+Script) / `Draft` (default at Vision/Shoot/Post, which are draft-by-nature since their contracts forbid invention). `auto_reroll = 0`. **No canon change was needed** — MISSION §5 is satisfied as written.
- **A LESSON is a MODULE.** 30 lessons, 164 topics, **N episodes per lesson decided at the brief**. The source doc called atoms "lessons" and that leaked into the UI.
- **The lesson layer** (PIPELINE §3.0): Plan runs once, before any brief. Coverage invariant: *every atom in exactly one block, or deferred with a reason.* **Reality outranks the plan** — a made episode is never invalidated by a re-plan.
- **Narrative episodes:** the liberty is **visual, never verbal**. More cuts is a physical limit; more dialogue is the wrong direction (ceilings are about comprehensibility, not teaching load). **When constraints relax, judgement tightens.**
- **UI: Claude Design + code is primary; Figma is a sketchpad.** Our components *are* HTML, so `/design-sync` round-trips without translation loss.

## UNVERIFIED (do not trust without testing)
- **Nothing has ever been generated.** No Seedance call ever. One NBP test (abstract shapes, **not characters**). No style plate. `resources/style_references/` holds only a README.
- **The C1 identity test has never run** — pending since 2026-07-15.
- **German lip-sync is unsolved and load-bearing.** Voice-reference (Path A) never executed.
- **The per-clip Seedance price is unknown**, so the dominant cost is unbudgeted. `cost-preview` returns `verified:false` for it deliberately.
- **`fal-ai/bytedance/seedance-2.0/reference-to-video`** slug still marked `⚠ confirm`. Seedance **2.5** (native 30s multi-shot) may obsolete the 2×15s split — check fal before building more on it.
- **No agent exists.** `studio.py` is the shell; `draft()` and the phase agents are Phase 3.
- **Stereotypes: 0 of 100 tagged.** `suggest_for_lesson` not built.
- **The legacy V3 wizard still runs** at `/` and dies at Phase 3.5.

## Commands run + real results
- `canon-audit` → **12 passed, 0 errors, 1 warning** (`canon_blocks.md` retired-but-on-disk, correct).
- `test_spine.py` → **52 passed** vs live Supabase + Gemini.
- `test_studio.py` **44** · `test_studio_api.py` **39** · `test_lessons.py` **34** — all 0 failed.
- NBP native API: `gemini-3-pro-image` live on the existing `GOOGLE_API_KEY`, 3-panel sheet generated, `thoughtSignature` returned → **images need no FAL_KEY**.
- Model window verified: `gemini-3.6-flash` = **1,048,576** in / 65,536 out.

## Failures distilled (the pattern matters more than the list)
Every defect this session was **drift between layers**, and Jayon caught three of them:
- **The curriculum contradicted PEDAGOGY** on word ceilings (~40–75 vs ≤30 at A1) — caught one step before the lock.
- **I scoped TREATMENT away from the Writer on a token-budget rationale.** Wrong twice: "must not decide X" ≠ "must not know X", and a *metric drove a correctness decision*. The budget itself was invented — 32k copied from a paper's example, against a real 1M window.
- **Four invideo guides were supplied and never read**, and the cost had been logged on 2026-07-29 and left unactioned.
- **`canon-audit`, on its first run, found the subtitle engine had rendered `das` and the target structure in the wrong colours since 2026-07-24** — nobody had noticed the second one.
- **Compaction was swallowing Jayon's own words**; rule 1 (human turns never drop) had to outrank it.
- The lesson tests found an atom could be **both assigned and deferred**, which then exposed `replan_preview` validating **half the change**.
> **The lesson: don't promise more care — build the detector.** That is why `canon-audit` exists and why a `ui-audit` is planned.

## Open risks
1. **Everything visual is unproven.** Bert das Bier — glass body, caustics, volumetric foam — may be near-impossible to hold consistently, and he fronts ~25% of episodes.
2. **The A1→B1 claim vs 85 minutes of content** is arithmetically unsupportable (MISSION §1). Either the claim changes or the format does.
3. **Season 0 is the hardest thing to generate** (worlds of characters = crowds, a known-failure case) and is what Jayon wants to start with. **The right first episode is a talking one.**
4. **No kill criterion** for a 170-episode plan.
5. Time, not credits, is the real cost: 5 gates × 170 episodes.

## Next 3 steps
1. **Continue the UI rebuild, screen by screen, Jayon leading.** Home's brief exists (`DESIGN_screen_home.md`); the method exists (`DESIGN_system_ui.md`). **Build the design system FIRST** (three-tier tokens in `:root` → Claude Design project → component library), then screens against it. Jayon still owes: does the chat or Continue lead · how much universe on Home · one reference tool he likes.
2. **The Plan agent + stereotype tagging** — both upstream of the Idea agent. Tagging is one AI pass + review.
3. **Generate something.** The style plate + C1 identity test cost ~$2 and unblock five architectural questions. It has been "next" since 2026-07-15.

## Also outstanding (smaller)
`ui-audit` (the token-drift detector) · fold `canon_blocks.md`'s deletion when the wizard dies · `skill-3`'s dangling `wardrobe_overrides` line · location plates · `DESIGN_screenplay_document` §7 (where takes live on disk) · Season-0-as-a-lesson is designed but never instantiated.

## Reread-first — **read these, not everything**
A full re-read is no longer the right move: `canon-audit` + the four suites verify in seconds what took dozens of tool calls, and "everything" now includes superseded V3 material that will mislead. Read, in order:

1. **`docs/planning/BUILD_PLAN_v4_studio.md`** — the governing doc: the contradiction audit, keep/rewrite/delete, the phase plan.
2. **This packet**, then **`docs/project_status.md`**.
3. **`prompts/canon/PIPELINE.md`** — the stations, incl. §3.0 Lesson Plan and §3.9 the change protocol.
4. **`docs/planning/DESIGN_screen_home.md`** + **`DESIGN_system_ui.md`** — the open work.
5. **`DESIGN_autopilot.md`** (the two modes) · **`DESIGN_lesson_layer.md`** · **`DESIGN_studio_chat.md`** §4 (the complete change map).
6. Skim `pipeline/studio.py` (the view compiler) and `dashboard/studio_api.py` (the API the UI consumes).
7. Canon on demand — the agents read it; you rarely need it in full.

**Then run these three, and trust them over reading:**
```bash
cd "/Users/jayonkvinod/Desktop/Anki Video/anki-video" && .venv/bin/python -m pipeline canon-audit -v
```
```bash
cd "/Users/jayonkvinod/Desktop/Anki Video/anki-video" && .venv/bin/python -m pipeline curriculum --status && .venv/bin/python -m pipeline state-verify
```
```bash
cd "/Users/jayonkvinod/Desktop/Anki Video/anki-video" && for t in lessons studio studio_api spine; do .venv/bin/python scripts/test_$t.py | tail -2; done
```

**⚠ Two habits this project earned the hard way:** never let a metric drive a canon-correctness decision, and when research is supplied, read it *and log that you read it* (`RESEARCH_invideo_production_guides.md` is the ledger).

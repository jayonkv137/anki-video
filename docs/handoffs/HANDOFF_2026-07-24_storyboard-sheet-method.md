# Handoff Packet — 2026-07-24 · Storyboard SHEET method

## Objective / non-goals
Fix the storyboard **cross-shot inconsistency** Jayon observed: v1 generated **one image per shot** (N independent calls) → identity/style drift. Rebuild as the **multi-panel SHEET method** — ONE generation per segment (all shots as 9:16 panels) → slice into per-shot panels → chain segment→segment — targeting **Nano Banana Pro**, surfaced in the studio UI.
**Non-goals this session (all flagged NEXT):** real NBP/FAL live verification (no key); the **overseer agent**; wiring **skill-1-story-strategist** into the chat; removing the **shots-per-segment cap**.

## Exact position
V3 storyboard **Phase 4 — DONE + verified** (mock + live-Gemini + UI). Downstream skill-3 / `refs_manifest` **unchanged** and resolving the sliced panels. Phase 6 (`stage_generate`/`assemble` per-segment) still pending.

## Files touched this session (git status: 6 modified + 1 new; UNCOMMITTED before this packet)
`dashboard/app.py` · `dashboard/static/index.html` · `docs/planning/DESIGN_v3_data_flow.md` · `pipeline/providers/image.py` · `pipeline/stages.py` · `prompts/skills/skill-2b-storyboard.md` · **new** `docs/planning/RESEARCH_storyboard_sheet_method.md`.

## Decisions + why (doc where recorded)
- **Storyboard = per-segment SHEET → slice → chain**, NOT per-shot (root cause of drift) — `RESEARCH_storyboard_sheet_method.md`, `DESIGN_v3_data_flow.md` §3.
- **Model = Nano Banana Pro** primary (14 refs, native still-extract, umlauts; GPT Image 2's text-accuracy edge is moot — no in-frame text) — Jayon's call.
- **Layout law:** every cell 9:16; 1×2/1×3 filmstrip, 2×2/2×3 grid — `image.sheet_grid()`.
- **Char refs = presence-based** (blocking/gaze/action + dialogue), fixing silent-but-present drift — `stages._segment_characters`.
- **Downstream panel filename contract unchanged** (`panel_s<seg>_<shot>.png`) → skill-3 / `build_refs_manifest` untouched.
- **Seedance stays 2.0** (2.5 launched on ByteDance ~07-17 but NOT on fal yet) — `RESEARCH_storyboard_sheet_method.md` §6.

## UNVERIFIED (do not trust without testing)
- **Real Nano Banana Pro `generate_sheet()` never called** (no FAL_KEY) — `aspect_ratio` tokens + `image_urls` key are `⚠ confirm`-flagged in `providers/image.py`.
- **The core visual hypothesis** (one generation → genuinely consistent, cleanly-sliceable 9:16 panels) is unproven on a real model — needs **Jayon's manual NBP test** (paste-ready template in `RESEARCH_storyboard_sheet_method.md`).
- **Slicing assumes an even grid**; imperfect real-model gutters may need NBP's native `extract the still [r.c]`.

## Commands run + real results
- `sheet_grid(1..6)` → `1x1/9:16 · 1x2/9:8 · 1x3/27:16 · 2x2/9:16 · 2x3/27:32` ✓
- `_segment_characters` on `ep_95c24d43` → **Müller in all 3 segments** (incl. the 3 silent shots v1 would have missed) ✓
- mock `generate_sheet`+`slice_sheet` → sheet 1080×640 → **3 panels 720×1280** ✓
- **LIVE Gemini skill-2b v2.0** (`ep_95c24d43`) → **3 sheets**: seg1 `1x3` chain=`''`; seg2 `1x2` chain=`sheet_s01`; seg3 `1x2` chain=`sheet_s02` ✓ — **clears the 2026-07-23 "Gemini structured-output never run live" risk.**
- UI Step 06 renders sheet cards (screenshotted, live on :8791) · `build_refs_manifest` → sliced panels **"resolved"** ✓
- `py_compile` + `node --check` clean.

## Failures distilled
- v1 storyboard: 1 PNG/shot via N independent generations → identity/style drift (the bug this fixes).
- v1 refs: gathered from `dialogue[].speaker` ONLY → silent-but-present characters got NO identity ref (2nd drift source) → fixed by `_segment_characters`.

## Open risks
- No `FAL_KEY` → the whole image/video half is unproven live.
- **`validate_screenplay` caps shots at 1–5/segment (`stages.py:578`)** — Jayon flagged as arbitrary + story-blocking; make story-driven next.
- **Overseer agent NOT built**; **`/api/co-creation/chat` STILL thin** (inline "Co-Director" `app.py:345`, not skill-1-story-strategist) — both confirmed not wired this session.
- Two co-creation impls coexist (legacy vs v3) — drift risk (carried over).

## Next 3 steps
1. **Make shots/segment STORY-DRIVEN** — replace the hard `1–5` cap (`stages.py:578`) + skill-2 "~3 shots" + the "3 panels/15s" docs with principled *soft* guidance (Seedance ≤9-image ref budget; min readable shot duration), NOT a hard number. Confirm `sheet_grid` handles any N cleanly (it has an else-branch already).
2. **Wire `skill-1-story-strategist` into `/api/co-creation/chat`** (phases + `ready_to_commit`) — upgrade the thin chat to the Socratic Strategist.
3. **Build the OVERSEER agent** — Gemini function-calling loop + typed edit/regen tools over the persisted `ep_<run_id>` artifacts + the lock→compiler dependency graph + confirm-with-diff + ledger undo. See `DESIGN_story_ideation_and_overseer.md`.

## Reread-first
1. `docs/planning/RESEARCH_storyboard_sheet_method.md` — the sheet method + open items
2. `docs/planning/DESIGN_v3_data_flow.md` §3 + Time-split — updated contracts
3. `pipeline/stages.py` — `stage_storyboard`, `_segment_characters`, `validate_screenplay` (:578 cap)
4. `pipeline/providers/image.py` — `sheet_grid`, `slice_sheet`, `generate_sheet`, `_fal_ratio`
5. `dashboard/app.py` (`/api/v3/.../sheet/{seg}`) + `static/index.html` (`renderStoryboardView`)
6. `docs/planning/DESIGN_story_ideation_and_overseer.md` — overseer design (for next step 3)

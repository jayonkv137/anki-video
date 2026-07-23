# RESEARCH — Storyboard SHEET Method (per-segment multi-panel generation → slice → chain)

> **Created:** 2026-07-24, for Jayon. **Status:** implemented (skill-2b v2.0 + `stage_storyboard` v2 + `providers/image.py` + UI Step 06). Supersedes the per-shot half of `RESEARCH_storyboard_stage_design.md` §3.
> **Trigger:** Jayon observed that generating **each shot as a separate image** gave good individual frames but **no consistency between shots**. This is the research + design that fixed it.

## The problem (root cause, confirmed in code)
`stage_storyboard` v1 looped over every shot and called `provider.generate()` **once per shot** — N independent generations with no shared context. Identity, wardrobe, lighting and grade drifted between shots because the model never saw the shots together. (A second, independent bug: refs were gathered from `dialogue[].speaker` only, so **silent-but-present** characters got no identity reference at all.)

## What the research established (2026 state of the art)
Consistent sources agree the fix is a **multi-panel storyboard SHEET generated in ONE pass**, then used to drive the video:
1. **One sheet per segment, one generation.** Published GPT Image 2→Seedance and Nano Banana Pro→Seedance workflows put **7–12 numbered panels in a single image** for a 15s clip. The single generation is *why* characters stay consistent — all panels share one latent context. One source states it directly: the grid "prevents character and stylistic inconsistencies that occur when generating individual shots independently."
2. **The 9:16-cell problem (our nuance).** Generic online grids are **16:9 sheets with square-ish cells**; our video is 9:16, so each *panel* must itself be 9:16 or Seedance re-frames and drifts. Fix: **keep every cell 9:16**, arrange as a filmstrip (≤3 shots) or a 2-row grid (4–6), then **slice** the sheet back into clean per-shot 9:16 frames. Nano Banana Pro even supports `extract the still [row].[column]` natively.
3. **Seedance handoff.** Verified on fal's live schema `bytedance/seedance-2.0/reference-to-video`: ≤9 images (`image_urls`) + ≤3 audio (`audio_urls`), referenced in-prompt as **`@Image1`/`@Audio1`** (our skills already use this — correct), `aspect_ratio: "9:16"` supported, 4–15s, native lip-sync. Winning pattern: sliced panels as **per-shot `@Image` anchors** + a timeline prompt — which is exactly what skill-3 already emits, so **downstream is unchanged**.
4. **Cross-segment chaining.** "Frame chaining" (feed the previous generation as a reference for the next) "significantly reduces identity drift across scenes." So each later segment's sheet is generated **with the prior segment's sheet attached** as a continuity reference.
5. **Model choice = Nano Banana Pro** (Jayon's call). GPT Image 2's headline edge is ~99% in-frame text accuracy — irrelevant to us (canon bans in-frame text). NBP gives 14 refs (fits style + 2 char sheets + 2 portraits + prev-segment sheet), up to 5 people, native umlauts, and native still-extraction. GPT Image 2 stays wired as the alternate.
6. **Seedance version.** 2.5 launched on ByteDance's own platform ~2026-07-17 (native 30s single-generation multi-shot, 50 refs) but is **not yet on fal** (fal still hosts 2.0 + 2.0 4K). **Canon stays on 2.0.** Re-check fal periodically — 2.5's native multi-shot would eventually let us drop the 2-segment split.

## The universal template (the "layout law")
`sheet_grid(n_shots)` in `pipeline/providers/image.py`. Every CELL is 9:16; the SHEET's overall ratio is `cols·9 : rows·16`:

| Shots | Layout | Sheet ratio | Note |
|---|---|---|---|
| 1 | 1×1 | 9:16 | single frame |
| 2 | 1×2 | 9:8 | filmstrip |
| 3 | 1×3 | 27:16 | filmstrip — **typical** |
| 4 | 2×2 | 9:16 | grid |
| 5–6 | 2×3 | 27:32 | grid |

Shot numbers print in the **gutter only** (never inside a panel) so they are cropped out on slice — the canon no-text-in-frame rule holds.

## How it was implemented
- **`skill-2b-storyboard.md` → v2.0** — one `sheet_prompt` per segment (sheet-format line + mirrored style clause + identity + environment + per-panel lines compiled from the shot fields + consistency lock + gutter-label rule + negatives + chaining note). Output: `{ style_clause, sheets:[{segment_number, shot_numbers, layout, sheet_aspect_ratio, sheet_prompt, continuity_ref}] }`.
- **`stages.py`** — `STORYBOARD_SCHEMA` reshaped (`panels[]`→`sheets[]`); `stage_storyboard` loops per **segment**: presence-based identity refs (`_segment_characters`, the wiring fix) + prev-segment sheet (chaining) → `provider.generate_sheet` → `slice_sheet` → `panel_s<seg>_<shot>.png` (**same downstream filename contract**).
- **`providers/image.py`** — `sheet_grid`, `slice_sheet` (deterministic equal-division crop → centre-crop/scale to 720×1280), `generate_sheet` on mock + NBP + GPT Image 2, `_fal_ratio` (ideal ratio → nearest fal token).
- **UI** — `/api/v3/runs/{id}/sheet/{seg}` accepts a sheet and **auto-slices** it; Step 06 renders one sheet card per segment (layout, ratio, chaining) with an auto-slice upload.

## Verified (2026-07-24)
Layout law ✓ · presence detection (Müller in all 3 segments of `ep_95c24d43`, incl. silent shots) ✓ · mock sheet→slice = clean 720×1280 panels ✓ · umlaut ref resolution ✓ · **live Gemini skill-2b v2.0 = 3 sheets, correct layouts, chaining `sheet_s01`→`sheet_s02`** (clears the handoff's structured-output risk) ✓ · UI Step 06 renders the sheets ✓ · downstream `build_refs_manifest` resolves the sliced panels ✓.

## Open / unverified
- **Real Nano Banana Pro `generate_sheet`** (FAL_KEY-gated) is coded but **not run live** — `aspect_ratio` tokens + `image_urls` key are `⚠ confirm`-flagged against fal's current schema. The core hypothesis (one generation → genuinely consistent, sliceable 9:16 panels) can only be proven on a real key — **Jayon to validate manually** (the paste-ready template is in chat / this method).
- Slicing assumes an even grid; imperfect real-model gutters may need NBP's native `extract the still [r.c]` as a refinement.

## Sources (key)
oimi.ai (GPT Image 2→Seedance 2 workflow) · learn.metalabs.global (cinematic grids w/ Nano Banana Pro) · fal.ai/models/bytedance/seedance-2.0/reference-to-video · crepal.ai (GPT Image 2 storyboards/comics) · picsart.com (Seedance 2.0 prompts) · kittl.com (frame-chaining consistency) · fal.ai/learn (What is Seedance 2.5).

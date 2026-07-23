# BUILD PLAN v3 — Universe & Co-Creation Studio (ordered change map)

> **Status: ACTIVE (2026-07-22).** The file-by-file execution plan for `VISION_v3_universe_and_studio.md`. Governed by CLAUDE.md working agreement: one phase at a time, explained, human-gated. **Canon edits follow the hash ritual** (edit → bump version → recompute SHA-256 → update `REGISTRY.md`, together). Skills are versioned (headers) but **not** hash-pinned.
> **De-risk verdict:** 🟢 GREEN — `RESEARCH_v3_tech_derisk_seedance_and_storyboard.md`.
> **Standing blockers (affect RUNNING, not editing):** Anthropic credits exhausted → LLM stages can't execute; no `FAL_KEY` → real Seedance / image-gen can't execute. All file changes + code/schema/dashboard verification proceed now; end-to-end runs wait on keys.
> **Progress (2026-07-22):** ✅ Phases 0–3 · ✅ 3L library · ✅ 3C co-creation · ✅ **Phase 4 storyboard + Phase 5 video-prompt** (director layer + per-shot durations, dual image provider, `skill-2b` storyboard stage, `skill-3` **v4** per-15s-segment Seedance compiler; mock/structure-verified) · ⏭ next: **Phase 6** reshape `stage_generate`/`assemble` per-segment + subtitle post step; then **Phase 7** studio UI. ⚠ `stage_generate`/`generate`/`autopilot` still on the OLD per-scene shape (the per-segment **prompts** are produced — test manually).

## Ordered phases — all the important files

| # | Phase | Files touched | The change | Runnable-verify now? |
|---|---|---|---|---|
| **0** | **Governance (lock)** | `VISION_HISTORY.md`, `IDEAS_PARKING_LOT.md`, `MVP_ROADMAP_command_center.md`, `BUILD_PLAN_v3.md` (this) | Record that the redesign is pulled forward; promote idea #16 | n/a (docs) |
| **1** | **Canon /tune** | `prompts/canon/prompting_guidelines_seedance.md`, `prompts/canon/REGISTRY.md` | Seedance **2.5→2.0**; image cap **≤9**; ver 2.1→2.2; hash | ✓ hash green-check |
| **2** | **Adapter fix** | `pipeline/providers/video.py` | `MODEL`→`…/seedance-2.0/reference-to-video`; `duration=15`; `generate_audio`; keep `resolution`/`aspect_ratio` | import ✓; real call needs `FAL_KEY` |
| **3** | **Screenplay reshape** | `pipeline/stages.py` (`validate_screenplay`, `SCREENPLAY_SCHEMA`, `stage_quality_check`), `prompts/skills/skill-2-screenplay-writer.md`, `prompts/skills/skill-2q-quality-check.md` | 10 scenes → **2–3 × ~15s segments, each multi-shot**; word/CEFR caps; QC gains explicit **language-learning-aspect** check | schema/validators unit-testable; full run needs credits |
| **3L** | **Stereotypes library** *(done)* | `resources/stereotypes_library.json`, `resources/stereotypes_source.xlsx`, `scripts/ingest_stereotypes.py`, `pipeline/stereotypes.py` | 100 stereotypes ingested + coverage tracking + `pick_options(3)` daily-pick API | ✅ **verified** (pick + tracking) |
| **3C** | **Co-creation stage (story→brief)** *(BUILT ✅)* | `pipeline/stages.py` (`STORY_BRIEF_SCHEMA`, `stage_align`/`diverge`/`commit`, `OBLIQUE_STRATEGIES`), `prompts/skills/skill-1a-align`/`1b-diverge`/`1c-commit.md`, `_call` temperature, safeguards, `cli.py` (`brief-start`/`diverge`/`commit`), skill-2 v2.1 | stereotype+seed+cast → align → 3–5 angles → **Story Brief JSON** → skill-2; anti-slop (temp, banned-terms, human-seed, oblique); lesson = **both particle + structure offered** | ✅ structure-verified (imports, signatures, placeholders, CLI); live runs need credits |
| **4** | **Storyboard stage (NET-NEW)** | `prompts/skills/skill-2b-storyboard.md` (new), `pipeline/providers/image.py` (new), `pipeline/stages.py` (`stage_storyboard`), `pipeline/cli.py` | screenplay → **per-segment storyboard frames** from char-ref + style-ref (GPT Image 2 / Nano Banana Pro; mock first) | mock testable; real needs image key |
| **5** | **Prompt reshape** | `prompts/skills/skill-3-prompt-writer.md` | emit **per-15s multi-shot** Seedance prompts binding storyboard frames as `@ImageN` | needs credits to run |
| **6** | **Assembly reshape** | `pipeline/assemble.py` | concat **2–3** clips; subtitles → **color-coded kinetic typography** (der=blue/die=red/das=green; yellow=grammar) | ffmpeg testable on mock clips |
| **7** | **Studio UI (increments)** | `dashboard/app.py`, `dashboard/static/index.html` | library/landing → stereotype picker → brainstorm loop → screenplay/storyboard review gates → subtitle editor → edit interface | browser-verifiable |
| **8** | **Content: the intro arc** | new episodes (Rolf → Bert → …) | first character-introduction episodes = launch content | needs full pipeline |

## Sequencing logic
- **Phases 1–2** are the *factual corrections* the de-risk surfaced — low-risk, no design decisions, do first.
- **Phase 3** is the pivot (episode shape). It needs a small design lock: the segment/shot JSON schema. Everything downstream (4–6) depends on it.
- **Phase 4** (storyboard) is the one genuinely new capability; it can be built against a **mock image provider** now and swapped to the chosen model (GPT Image 2 vs Nano Banana Pro head-to-head) when a key exists.
- **Phase 7** (studio UI) can proceed in parallel after Phase 3 fixes the data shape; v0 (library/read-only) needs nothing from 4–6.
- **Duration default = 30s (2×15s), 45s (3×15s) only when a scenario needs it** (Jayon, 2026-07-22).

## Checkpoints (learning-by-doing gates)
Stop-and-explain before: **Phase 3** (schema redesign — the shape everything keys off), **Phase 4** (new provider pattern), **Phase 7** (UX design). Phases 1–2 are safe to land as one chunk.

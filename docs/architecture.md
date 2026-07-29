# Architecture

> Living doc — updated after every structural change. **Rewritten 2026-07-29** to reflect the complete V3 system (previous version described the V2/E-phase state). Companion detail docs: `planning/DESIGN_v3_data_flow.md` (stage contracts) · `planning/DESIGN_cocreation_stage.md` · `planning/DESIGN_story_ideation_and_overseer.md` · `planning/DESIGN_subtitle_and_assembly.md` · `planning/RESEARCH_storyboard_sheet_method.md`.

## The one principle

**The screenplay is the LOCK; everything after it is a COMPILER.** Every creative + pedagogical decision is made once (brief → screenplay); storyboard and video prompts are deterministic compiles that attach the asset spine (character sheets/portraits/voices, style, panels). Every edit therefore has a well-defined recompile set — which is what makes the Overseer tractable.

```
stereotype pick → cast+seed → co-creation chat → STORY BRIEF → SCREENPLAY (lock)
   → storyboard SHEETS (1 gen/segment → slice → per-shot panels)
   → Seedance prompts (1/segment, ≤9 @Image + ≤3 @Audio)
   → [human generates clips in Nano Banana Pro / Seedance manually]
   → assemble (ffmpeg concat) → subtitles.json (word-level, color-coded) → burn → final.mp4
```

## The stage spine (what happens where)

| # | Stage | UI step | Endpoint | Skill / logic | Artifact |
|---|---|---|---|---|---|
| 1 | Stereotype pick | 01 | `GET /api/stereotypes/all` (searchable library; `options`/`summary` also exist) | `pipeline/stereotypes.py` over `resources/stereotypes_library.json` (100 items · categories · `status:covered` + `episode_id` coverage log) | selection in JS state |
| 2 | Cast & seed | 02 | — (client-side) | roles main/side/guest/bg from the 4-character roster; human seed text; CEFR pick | JS state |
| 3 | Co-creation chat | 03 | `POST /api/co-creation/chat` | **skill-1-story-strategist** (Socratic; Hook→Arc→Beats→Verify phases; option-widgets; Elenchus constraint checks; `ready_to_commit` signal). Context server-injected per turn: MISSION + series digest (RCP) + stereotype + cast + bible + seed + CEFR | chat transcript (JS) |
| 4 | Commit → Brief | 03→04 | `POST /api/v3/commit` | **inline prompt in app.py** (NOT skill-1c) extracts `STORY_BRIEF_SCHEMA` from the chat; creates/reuses run (ledger UUID or stereotype-match); writes brief; `mark_covered` | `brief.json` |
| 5 | Screenplay | 05 | `POST …/screenplay` | **skill-2 v2.2+** — brief → episode→segments→shots with the **director layer** (`shot_size/camera_angle/camera_move/action/blocking/gaze/expression/duration_s` + dialogue); STRICT SHOT MAPPING + DIALOGUE ENFORCEMENT when `director_notes`/beats carry a breakdown; `global_aesthetic_rules` + per-segment `time_and_weather` (Jayon 07-28); `validate_screenplay` (shape, ~15s sums, CEFR caps, readability floor) — problems returned, **not gating** | `screenplay.json` |
| 6 | Storyboard | 06 | `POST …/storyboard-prompts` + `POST …/sheet/{seg}` (upload→auto-slice) | **skill-2b v2.0+** — ONE multi-panel **sheet prompt per segment** (reference-binding-first → sheet format + style_clause → coordinate-based panels → constraints; gutter-only labels; cells always 9:16; layout law in `providers/image.py:sheet_grid`); cross-segment **chaining** (`continuity_ref` + prev sheet attached); presence-based char refs (`_segment_characters`) | `storyboard.json` + `storyboard/sheet_sNN.png` → sliced `panel_sNN_MM.png` |
| 7 | Video prompts | 07 | `POST …/video-prompts` | **skill-3 v4+** — ONE thin Seedance prompt per segment in canon order (bindings → timecoded shot list with exact `{German}` transcripts → lip-sync line → constraints; ≤3000 chars; wardrobe-override rule); `build_refs_manifest` resolves binds → files (identity=sheet+portrait, voice=mp3, panel=sliced file, style=pending) | `prompts.json` + `prompts/segment_NN.seedance.json` + `refs_manifest.json` |
| 8 | Assembly & subtitles | 07 (studio) | `POST …/assemble` · `GET/POST …/subtitles` · `POST …/export` · `GET …/video/{joined\|final}` · `POST …/mock-clips` | `pipeline/subtitles.py` — ffmpeg concat → **`subtitles.json`** (frame-based declarative state; cues+words; colors computed from `target_vocab` gender: der=blue/die=red/das=green, grammar=yellow; screenplay-derived word timing) → live DOM-overlay preview (no re-render) + cue editor → ASS render (`\k` karaoke, `\c` colors, `\pos(540,1150)`, box) → libass burn | `assembly/joined.mp4` · `subtitles.json` · `assembly/final.mp4` |

**Manual-generation contract:** the studio produces *prompts + reference lists*; the human generates images (Nano Banana Pro primary, GPT Image 2 alternate) and video (Seedance 2.0 `reference-to-video` on fal) externally and uploads results back (`/sheet/{seg}` auto-slices; `/clips/{seg}` stores segment MP4s). `FAL_KEY`-gated adapters exist in `providers/image.py` + `providers/video.py` (`⚠ confirm`-flagged, never called live). Mock providers (`mock` images, `mock_clip`) prove the whole chain without keys.

## Cross-cutting systems

- **Canon + governance:** `prompts/canon/` (MISSION 1.0 · canon_blocks 1.0 — STYLE_BLOCK + per-character PBR material CHAR_BLOCKs + AVOID list · seedance guidelines 2.2 — first-30-words, ≤3000 chars, `@ImageN`/`@AudioN` binding syntax, prompt-mirroring, live-action-integration rule, one-action rule, camera syntax, voice-ref lip-sync method) + `resources/Characters-Main-Sheet.md` v1.3 (belief+wound per character, voice flavors, cast dynamics, pipeline rules). All hash-pinned in `REGISTRY.md`; `rcp.verify_canon()` aborts on mismatch. Skills are versioned but NOT hash-pinned.
- **RCP (`rcp.py`):** per-run "creator's mind" — `for_story_stage()` = MISSION + series-memory digest (last 5 episodes from Supabase, with "do not repeat" aggregates); `for_screenplay_stage()` = MISSION; `for_prompt_stage()` = MISSION + Seedance/Omni guidelines. Injected as the system-prompt prefix of every LLM stage.
- **LLM:** all stages on **Gemini** (`stages._call_gemini`; `GEMINI_MODEL=gemini-3.6-flash`; retry ×2 on 503/429 then raise — Jayon 07-28). ⚠ JSON mode only — the JSONSchema args are **not enforced** (no `response_schema`); output shape is governed by skill prose. Anthropic path exists as fallback (credits exhausted).
- **Ledger (Supabase):** runs / run_events / episodes; short-prefix→UUID resolution + all calls non-fatal (Jayon 07-28). Coverage additionally in the stereotypes library itself.
- **Overseer ("Director"):** floating window on every step (`index.html`) → `POST /api/overseer/plan` (Gemini structured plan: typed ops + summary; graph computes the recompile set) → human confirm-with-diff → `POST /api/overseer/apply` (deterministic edits + targeted recompiles + ledger log). Ops: `edit_shot` · `rewrite_segment` · `edit_brief` (full rebuild) · subtitle leaf ops `recolor_word`/`edit_subtitle`/`shift_subtitles` · `answer_only`. `pipeline/overseer.py` + `skill-5-overseer.md`.
- **Frontend (`dashboard/static/index.html`, vanilla JS):** 7-step wizard + sidebar blueprint; state in globals (`selectedStereotype/Cast`, `chatMessages`, `activeRunId/Brief/Screenplay/Storyboard/VideoPrompts/Subtitles`); resume via `GET /api/v3/runs/{id}` + `localStorage.activeRunId` (auto-jumps to the furthest artifact); searchable stereotype library (Jayon 07-28).
- **Legacy surfaces (dormant):** V2 per-scene pipeline (`stage_generate`/`stage_finalize`/`assemble.py`/`providers/video.py` old `scenes[]` shape — Phase 6 never done, superseded by the manual V3 path); `/api/co-creation/{align,diverge,chat/extract}` endpoints + skill-1a/1b/1c + skill-1-story-selector/1a-story-options/1b-story-expand (not called by the UI); n8n B0/B1 workflows; Omni guidelines (dual-engine dropped in V3).

## Known gaps (audited 2026-07-29 — the fix backlog feeding Jayon's change wave)

1. **UI storyboard path misses `{{CANON_BLOCKS}}`** — `app.py:v3_storyboard` substitutes only bible+screenplay, so skill-2b's "mechanically merge STYLE_BLOCK" instruction gets a literal placeholder → the style_clause is **improvised per run** (CLI `stage_storyboard` has the substitution; the UI doesn't). Direct cause of style inconsistency concerns.
2. **No global style anchor:** the style plate is still `pending — C1 style-lock`; cross-segment consistency rests on sheet-chaining alone, and skill-3 still numbers a nonexistent `@Image2` style ref.
3. **`@ImageN` numbering contract is fictional:** identity resolves to TWO files (sheet+portrait), style is pending — so the prompt's numbering ≠ what the human actually attaches; no UI showing "attach these files in this order" for either NBP sheets (Image 1=Portrait, Image 2=Sheet is implicit) or Seedance.
4. **Schema non-enforcement drift:** Gemini returns extra/renamed fields (`bg` vs `background`, ghost `lighting_mood` — the stale mention in skill-2's v2.2 header line leaks into output). Fix = `response_schema` in `_call_gemini` + purge stale skill text.
5. **`director_notes` never captured:** `v3_commit`'s inline prompt (the one actually used) predates the field; only unused skill-1c asks for it. The chat's specific creative decisions are being dropped at commit — which then defeats skill-2's STRICT SHOT MAPPING.
6. **No quality gate in the studio:** skill-2q exists but only the old CLI runs it; `validate_screenplay` problems render as a banner but blocks nothing; environment coherence isn't validated at all (fresh run drifted indoors against the one-environment law).
7. **Sheet slicing is blind:** equal-division crop assumes a perfect grid; no gutter detection, no post-slice visual check; imperfect NBP grids will cut through content.
8. **Prompt-mirroring drift in skill-3 output** (binding-line phrasing varies between segments) and skill-2 output pacing collapses to uniform 3×5s shots.
9. **Stale remnants:** screenplay view renders removed `seg.setting` (shows "undefined"); overseer `SHOT_FIELDS`/skill-5 still list `lighting_mood`; skill-2 header still names it; legacy endpoints/skills above.
10. **Opaque 500s:** stage endpoints surface raw `Internal Server Error` (e.g. transient Gemini overload after retries — the 07-28 screenplay failure; note the model fallback list de-dupes to a single model, so there is no real fallback).
11. Real-model unknowns: `FAL_KEY` adapters unverified; subtitle timing is screenplay-derived (Deepgram precision is a designed-not-built upgrade); no Overseer undo UI; publish adapter (Gate 2) not built.

# DESIGN — V3 Data Flow (screenplay → storyboard → Seedance)

> **Status: LOCKED CONTRACTS (2026-07-22).** The single reference for how the visual half connects. Consolidates the screenplay / storyboard / Seedance discussions. Governs the Phase 4+ build. Companions: `DESIGN_cocreation_stage.md` (the story half), `RESEARCH_storyboard_stage_design.md`, `prompts/canon/prompting_guidelines_seedance.md`.

## The one principle
**The screenplay is the LOCK** — every creative + pedagogical decision is made once, there. Everything after is a **COMPILER**: it reads the screenplay and attaches the established assets (the asset spine); it never re-decides, and re-describes as little as possible. Human visual edits at the storyboard gate **propagate back into the lock**, then forward again. One source of truth, always.

## Stage contracts (what each stage MAY / MUST NOT add)

### 1 · CO-CREATION → Story Brief  (skill-1a/1b/1c) — BUILT
Human + AI decide the concept. Output: **Story Brief** (stereotype, cast, location, lesson, premise, escalation_beats, button, target_line, banned_terms).

### 2 · SCREENPLAY — the lock  (skill-2)
Brief → episode → segments (2–3 × ~15s) → shots (~3/segment). Each shot carries the **director layer**:
`shot_size · camera_angle · camera_move · action · blocking · gaze · expression · lighting_mood · dialogue`
- **MAY decide:** all shot framing, blocking, motion intent, expression, lighting, and the German dialogue that realizes the lesson.
- **MUST NOT:** prompt-engineering, `@Image` bindings, style codes (compilers' job); **no on-screen / diegetic text**.
- **Language-learning:** realizes the brief's `lesson` naturally; CEFR caps; skill-2q hard-checks it is actually taught + shown-not-explained.

### 3 · STORYBOARD skill  (skill-2b **v2.0** — SHEET method) · image-prompt compiler
**One multi-panel SHEET prompt per SEGMENT** (not per shot). All of a segment's shots are drawn as 9:16 panels in **one generation** — that single pass is what locks identity + style across the shots (per-shot generation drifted). The sheet is then **sliced** back into per-shot 9:16 panels. Segment → ONE sheet prompt:
`[sheet format: N×M of 9:16 cells] + [mirrored style clause] + [character identity ← presence] + [environment] + [per-panel lines ← shot fields] + [consistency lock] + [gutter-label rule] + [negatives] + [chaining ref for seg 2+]`
- **MAY add:** the sheet-layout description, the mirrored style clause, `@Image` identity bindings, negatives, a terse restatement of each shot's own fields, a continuity ref to the prior segment's sheet.
- **MUST NOT:** invent new creative decisions; render subtitles or ANY text inside a panel (shot numbers live in the gutter, cropped out on slice); add narrative.
- **Layout law:** cells stay 9:16; 1×2 / 1×3 filmstrip (≤3 shots) or 2×2 / 2×3 grid (4–6). One sheet per 15s segment → sliced into 2–3 panels. See `RESEARCH_storyboard_sheet_method.md`.
- **Consistency mechanics:** single-generation sheet (in-context) + mirrored style clause + presence-based identity refs + **cross-segment chaining** (prior sheet attached to the next).

### 4 · IMAGE PROVIDER  (providers/image.py — NET-NEW)
`mock | gpt-image-2 | nano-banana-pro` — both real models selectable (Jayon: "have both, try either"). 9:16 native. Consistency: **seed-lock** (lock the first approved panel's seed for the segment) + **prompt-mirror** (identical style clause every panel) + **reference re-injection** (reuse the background plate). Single-panel fix = edit endpoint + mask.

### 5 · STORYBOARD REVIEW GATE  (studio UI + backend)
Per panel: **approve / comment→regenerate / redo**. Nothing proceeds to video until every panel is confirmed. **Feedback propagation (the important part):**
| Comment | Regenerates | Writes back to |
|---|---|---|
| "colder light / different expression / tighter framing / move her left" | that panel | the **shot's fields** (lighting/gaze/framing) — the lock stays honest |
| "camera should push in / she picks up the cup" | that panel | the **shot in the screenplay** → panel **and** Seedance motion prompt inherit it |
| "this whole scene is wrong" | — | rewrite the **shot/segment**, then re-storyboard |

### 6 · SEEDANCE PROMPT skill  (skill-3 — RESHAPE, drop Omni)
Segment + its panels → ONE multi-shot Seedance prompt in **canon order** (`[Ref Assignments] → [Shot Structure] → [Camera] → [Env/Light] → [Style] → [Audio] → [Constraints]`).
- **MAY add:** ref bindings, per-shot structure, camera **motion**, transcript-for-lipsync, constraints.
- **MUST NOT:** re-describe static look (images carry it); heavy `CHAR_BLOCK`/`STYLE_BLOCK`; any text/subtitle; the Omni package.
- This is what fixes the 3000-char cap — no look-blocks.

### 7 · VIDEO → POST  (assembly + a SEPARATE later step)
2–3 clips → concat → **subtitles as a separate post step**: color-coded kinetic typography, editable in the UI. **No text ever goes into Seedance.**

## Seedance reference budget (per 15s clip — cap 9 images / 3 audio)
| Ref | Content | Role |
|---|---|---|
| `@Image1` | style plate *(future)* | global look |
| `@Image2`, `@Image3` | Character A — sheet + portrait | identity A |
| `@Image4`, `@Image5` | Character B — sheet + portrait | identity B |
| `@Image6–8` | storyboard panels (shots 1–3) | composition anchors |
| `@Audio1`, `@Audio2` | each character's voice clip | lip-sync |

## Seedance prompt shape (canon) — example
```
Define [Rolf description] in @Image2 and @Image3 as Rolf.
Define [Kati description] in @Image4 and @Image5 as Kati.
Use @Image1 as the global stylistic reference for lighting and color.
Use @Audio1 as the voice of Rolf. Use @Audio2 as the voice of Kati.

Shot 1: 0-8s. @Image6 — Rolf throws the window open, cold wind rushes in.
  Rolf says in German {Mach das Fenster auf!}. Camera: slow push in, smooth gimbal, steady. no zoom.
Shot 2: 8-15s. @Image7 — Kati bundles into a blanket, shivering.
  Kati says in German {Es ist ja eiskalt!}. Camera: static, tripod stable.

Synchronize each character's lip movements to their spoken line.
Live-action integration; physically real characters, human-scale room.
Audio Constraints: No background music, purely spoken dialogue.
```
No look-blocks, no on-screen text, no subtitles — but every canon-required element present.

## Where the language-learning lives (ALWAYS on)
`MISSION (every stage)` → `brief.lesson` (particle/structure + pragmatic_function + pop_up_grammar + target_line) → `screenplay dialogue` realizes it under CEFR caps → **`skill-2q` HARD-CHECKS** `grammar_target_taught` + `cefr_caps_respected` + `stereotype_shown_not_explained` → **subtitles** reinforce (gender color-coding) in post. Never dropped at any stage.

## No-text rule (locked)
- **No diegetic text** (signs/chalkboards) by default — the stereotype is shown by action/props/body language.
- **No text in Seedance.** German is **spoken** (voice refs → lip-sync).
- **Subtitles = a separate post step** (editable), not baked into panels or video.

## Phase 4+5 build order (status)
1. ✅ **`SHOT_SCHEMA` director layer** + per-shot `duration_s` (the 15s time-split) + `skill-2` **v2.2**.
2. ✅ **`providers/image.py`** (mock + GPT Image 2 + Nano Banana Pro, selectable).
3. ✅ **`skill-2b-storyboard` v2.0 (SHEET method)** + `stage_storyboard` v2 (per-segment sheet → slice → chain, presence-based refs) + `providers/image.py` (`sheet_grid`/`generate_sheet`/`slice_sheet`) + UI Step 06 + `/sheet/{seg}` auto-slice. Mock-proven + **live-Gemini-proven** (2026-07-24). Real NBP path FAL_KEY-gated (`⚠ confirm`). See `RESEARCH_storyboard_sheet_method.md`.
4. ✅ **`skill-3` v4** thin per-15s-segment Seedance compiler + per-segment `PROMPTS_SCHEMA` / `stage_prompts` / `build_refs_manifest` (resolves panels; Omni + canon-blocks dropped).
5. ⏭ *(Phase 6)* reshape `stage_generate`/`assemble` per-segment (one Seedance call per clip) + the subtitle post step; then the storyboard **review-and-propagate gate** in the UI (Phase 7).

## Time-split (the 15s logic)
Each **segment = one 15s Seedance clip**. The screenplay divides time explicitly: every shot has `duration_s`, and a segment's shots **sum to ~15s** (validator-enforced). A segment can be **1 shot (15s) or several** (e.g. 6+7+2). 30s = 2 segments, 45s = 3. The storyboard makes **one multi-panel sheet per segment**, generated in a single pass and **sliced into one 9:16 panel per shot**; those sliced panels are the Seedance anchors for that clip's cuts.

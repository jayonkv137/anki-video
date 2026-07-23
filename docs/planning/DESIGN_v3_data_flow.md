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

### 3 · STORYBOARD skill  (skill-2b — NET-NEW) · image-prompt compiler
Enriched shot → ONE image-gen prompt:
`[style ref] + [environment & lighting] + [character identity @Image] + [framing & composition ← shot fields] + [negative constraints]`
- **MAY add:** style-ref code, `@Image` identity bindings, negatives, a terse restatement of the shot's own fields.
- **MUST NOT:** invent new creative decisions; render subtitles; add narrative.
- **Density:** 3 panels / 15s segment → 6–9 panels per episode (a shot change ~every 5s).

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
3. ✅ **`skill-2b-storyboard`** + `stage_storyboard` + `pipeline storyboard` (mock-proven).
4. ✅ **`skill-3` v4** thin per-15s-segment Seedance compiler + per-segment `PROMPTS_SCHEMA` / `stage_prompts` / `build_refs_manifest` (resolves panels; Omni + canon-blocks dropped).
5. ⏭ *(Phase 6)* reshape `stage_generate`/`assemble` per-segment (one Seedance call per clip) + the subtitle post step; then the storyboard **review-and-propagate gate** in the UI (Phase 7).

## Time-split (the 15s logic)
Each **segment = one 15s Seedance clip**. The screenplay divides time explicitly: every shot has `duration_s`, and a segment's shots **sum to ~15s** (validator-enforced). A segment can be **1 shot (15s) or several** (e.g. 6+7+2). 30s = 2 segments, 45s = 3. The storyboard makes **one 9:16 panel per shot**; those panels are the Seedance anchors for that clip's cuts.

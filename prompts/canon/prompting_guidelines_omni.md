> ⚠ **DEPRECATED — NOT CANON.** Omni was dropped in the V3 reshape (skill-3 v4 is Seedance-only).
> Removed from `REGISTRY.md` and from the Run Context Pack on 2026-07-29. Kept for reference only;
> nothing in the pipeline reads this file. Do not inject it into any prompt.

# Prompting Guidelines — Gemini Omni Flash

> version: 1.2 · canon file · v1.2 (2026-07-21): per-character fixed voice identity

## 0. The Live-Action Integration Rule

- **Never** use terminology related to puppets, claymation, needle-felt, stop-motion, miniatures, or toys — these terms poison the latent space toward visible seams, stepped framerates, and tilt-shift miniature depth of field.
- All generated scenes must be treated as **live-action visual effects integration**. The characters are physically real entities interacting with human-scale, real-world environments.

## 1. Prompt structure (narrative production brief — NOT bracketed formulas)

Write as a cohesive, flowing director's brief. Order:

`[# References] → [Role assignments in prose] → [Scene: subject + motion + physics] → [Camera in prose] → [Audio in prose] → [Format: Ns, aspect]`

## 2. Reference-image mapping (≤ 10 images)

Declaration syntax:
```
[# References <IMAGE_REF_0>@Image1 <IMAGE_REF_1>@Image2 <IMAGE_REF_2>@Image3]
Use Image 1 and Image 2 strictly as aesthetic references for visual style, color grading, and lighting.
Use Image 3 as a reference for [character] identity.
These images should not be used as literal initial frames.
```

Always append the **"not literal initial frames" exclusion** — without it, reference images get used as the actual first frame of the video instead of as style/identity anchors.

## 3. Continuity constraint (CRITICAL)

Gemini's default behavior is to spontaneously insert AI-generated cuts and varying shot angles within its 10-second window. **Always** include one of:
- `In a single unbroken scene`
- `In a single continuous shot`
- `No scene cuts`

Without this, expect hallucinatory editing.

## 4. Duration & resolution

- Max output: **10 seconds**, 720p, 24 fps
- Every action must logically resolve within this window — no extensions, no interpolation
- Always specify: `Format: Ns, 16:9` (or `9:16` for vertical)

## 5. Camera & physics in natural prose

Tie camera movement to the action organically — not as sterile technical brackets:

> "The camera slowly pulls back to a medium shot, then gently orbits left."

Never vague: ❌ "make it dynamic" or "interesting camera." Be specific about the movement.

Gemini has robust real-world physics understanding. Direct physics explicitly in the scene description:
> "water dripping from the needles," "heavy droplets hitting leaves"

Audio also goes in prose:
> "Audio: pan sizzle, soft kitchen ambience, and a voice saying 'Service.'"

## 6. Stateful editing — the Interactions API (core advantage)

Gemini is an **iterative sculpting tool**, not a single-shot generator. The initial prompt does not need to be flawless.

**Workflow:**
1. **Base generation:** Perfect the subject, action, camera, and character identity in the first prompt.
2. **Refinement turns:** Chain via `previous_interaction_id`. Issue natural-language edit commands:
   - `"Keep the character, motion, and camera identical. Remove the coffee cup from the table and shift the lighting to sunset."`
   - `"Change the subject's jacket to deep green."`
   - `"Add heavy rain."`
3. The model preserves underlying character identity and spatial geometry across edits — vastly less drift than regenerating from scratch.
4. **Plan an ordered edit-turn sequence** for each scene: generate base → refinement 1 → refinement 2…

## 7. German dialogue — TTS inline-tag workflow

### Inline tags (Gemini 3.1 Flash TTS)

Tags control emotional delivery, pacing, and tone. Tags go in `[]` and are **always written in English**, even when the spoken text is in German.

Example:
```
[cautious] Wir müssen aufpassen. [whispers] Sie könnten uns hören. [short pause] [panic] Lauf!
```

**Tag syntax rules:**
- Tags and spoken text must **alternate** — two adjacent tags with nothing between them = syntax error
- Separate tags with text or punctuation
- Common tags: `[whispers]`, `[panic]`, `[cautious]`, `[short pause]`, `[excited]`, `[stern]`, `[gentle]`

### Fixed per-character voice identity
Each character has a persistent voice identity (matching their voice-reference clip). Assign the SAME voice profile to a given character in every scene — never let it drift. Describe the voice consistently in prose (e.g. "deep, clipped northern German") and, where the API supports it, pin the same named voice profile (Zephyr/Charon/Kore/Puck) to that character across all calls.

### 2-speaker limit workaround

Gemini TTS supports a maximum of **2 distinct speakers per API call** (Speaker A + Speaker B, each assigned a voice profile like Zephyr, Charon, Kore, or Puck).

For 4-character scenes, chain sequential calls via `previous_interaction_id`:
1. **Call 1:** Characters A + B dialogue — establish the physical environment
2. **Call 2:** Characters C + D dialogue — command: `"maintain the exact spatial environment and lighting as the previous interaction"`
3. Each call assigns its own 2 voice profiles

This preserves spatial geometry and identity while bypassing the 2-speaker limit.

## 8. DON'Ts

- ❌ **Single-shot perfectionism** — use iterative refinement via Interactions API
- ❌ **Omitting continuity constraint** — model will insert random cuts within 10 s
- ❌ **Vague camera direction** — describe exact movement in prose
- ❌ **Actions exceeding 10 seconds** — no extension/interpolation available
- ❌ **Refs without explicit role assignments** — will be used as literal first frames
- ❌ **Adjacent TTS tags** without intervening text — causes syntax errors
- ❌ **More than 2 speakers per TTS call** — voices will conflate; chain stateful calls
- ❌ **Forgetting language spec** — phoneme mapping defaults to English if German not declared

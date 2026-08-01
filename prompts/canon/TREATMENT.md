# TREATMENT — "Stereotypical German" · the directorial rule system

> version: 1.0 · canon file · 2026-07-29
> **This is the controlling document of the production.** The screenplay is the narrative source of truth; THIS is the execution source of truth. Every visual stage (storyboard sheets, video prompts) reads it and every generated frame is gated against it. **Rules, not descriptions** — every line below must be checkable against a frame. If a line cannot be checked, it does not belong here.
> **Consolidates:** `canon_blocks.md` v1.0 · `prompting_guidelines_seedance.md` v2.2 · `Characters-Main-Sheet.md` v1.3 · the 2026-07-21 VISUAL PIVOT · `AUDIT_visual_identity.md` · `WORKFLOW_visual_identity_lock.md`. Sections marked **⧖ OPEN** are deliberately unfilled until the first real episodes exist — see §15.

---

## 1 · MEDIUM (what the images ARE — the load-bearing line)
High-end **cinematic live-action cinematography integrated with photorealistic CGI characters**, exhibiting macro-level tactile materiality and true physical presence within real-world environments.
- The characters are **physically real entities at human scale**, present in real locations. They are never depicted as objects, toys, models, or animation.
- **Live-Action Integration Rule (absolute):** the words *puppet · claymation · needle-felt · stop-motion · miniature · toy · handcrafted* never appear in any canon file, skill, screenplay, or prompt. These terms poison the latent space toward visible seams, stepped framerates and tilt-shift miniature depth of field. This ban supersedes all pre-2026-07-21 documentation, which described a puppet aesthetic and is void.

## 2 · CAMERA
- **Body:** locked-off on a heavy tripod, with **subtle handheld breathing**. Natural motion blur.
- **Default state is HOLD.** The camera moves only when the action motivates it. Restraint is the style.
- **Permitted moves:** slow push-in · slow pull-out · slow pan · tracking that follows a subject.
- **Forbidden moves:** dynamic sweeps · drone/aerial · crash zooms · whip pans · orbiting · any move whose purpose is energy rather than meaning.
- **Move syntax (video stage):** `Camera: [move] + [speed] + [stability]`.
- **Zoom-creep constraint (mandatory):** any tracking or panning instruction must carry `no zoom, maintain subject size in frame`. The engine otherwise confuses physical dolly movement with focal-length change and warps the background.
- **One camera idea per shot.** Compound moves are not used.

## 3 · LENS
- **35mm anamorphic**, consistently, everywhere.
- **Subtle lens halation** and **slight edge fringing** are present; both are subtle — visible on inspection, never the subject.
- Depth of field is **not** fixed globally (a hardcoded shallow DOF produced a "pasted-in" look and was removed 2026-07-21). DOF is chosen per shot to serve the subject, and never so shallow that the environment becomes unreadable mush.

## 4 · ANGLES & SHOT SIZES
- **Eye-level is the default** and must be the majority of any episode.
- **Permitted angles:** eye-level · low (power) · high (vulnerability) · dutch (tension, sparingly) · POV.
- **Shot-size vocabulary (closed set):** ECU · CU · MCU · MS · MWS · WS · OTS.
- **Vary size and angle shot-to-shot** within a segment. Two adjacent shots must not share both size and angle.
- **Forbidden:** any angle that implies a camera position a physical crew could not occupy.

## 5 · LIGHTING — *ratios and named sources, never moods*
- **Every scene's light is expressed two ways and only these two:** a **named source** (what is emitting the light — "overhead supermarket fluorescents", "low winter sun through the window", "sodium street lamp camera-left") and a **ratio** (light-to-shadow, e.g. `70:30`).
- **Mood words are forbidden as lighting direction.** "Moody", "dramatic", "beautiful lighting" are not directives and must be rewritten as a source + ratio. *"Warm lighting"* is a description; *"warm yellow from the practical lamps only"* is a rule.
- **Motivated light only:** every light must come from a source that is visible in frame or logically implied by the location. No unmotivated key light.
- **Light adapts to the environment; it is never imposed on it.** There is no global colour temperature and no global key-fill ratio — those are properties of the **tonal mode** (§6.3), not of the show.
- **Shadow discipline:** shadows are shaped and directional, consistent with the named source. Flat, sourceless ambient light is a failure state.

## 6 · COLOUR
### 6.1 The separation rule (absolute, hue-independent)
> **The cast always wins the frame.** In every shot each character is the most present thing in it, separated from the environment by at least one of **value** (they sit lighter or darker than what is behind them), **saturation** (their material colour is more saturated than the surrounding surfaces), or **hue** (the environment sits in a different family from their warm earth tones).
- **The environment yields.** Where a location's natural palette competes with a character, the location is pushed back — in value, saturation, or both.
- **Character material colour is never desaturated to match a scene.** The grade acts on the world, not on the cast.
- **Checkable as:** *does any surface out-compete a character for attention?* If yes, the frame fails.
- **This rule is deliberately not a hue rule.** The series moves across all of Germany — a Bavarian beer tent, a Berlin club, a northern harbour — and each may be warm, cool, saturated or grey. Only the hierarchy is fixed.
- **Deliberate violation is a dramatic instrument:** a character overwhelmed by their environment is permitted *when the story requires it*, and must be an explicit choice in the shot, never an accident.

### 6.2 Character accents (fixed — material properties, not styling)
| Character | Primary | Secondary accents |
|---|---|---|
| Müller das Brot | golden crust | navy · white · **red** bag |
| Bert das Bier | **amber** + clear glass | white foam · grey |
| Rolf die Wurst | red-brown casing | black · silver |
| Kati die Kartoffel | yellow-brown | blonde · **green** · brown · white |
All four are **warm earth tones**. This is a material fact of what they are and is never adjusted.

### 6.3 Tonal modes — a GROWING LIBRARY ⧖ OPEN
- A **mode** is a named, reusable colour+light condition. It records: **name · named source(s) · ratio · shadow tint · highlight tint · saturation note · how §6.1 separation is achieved in this condition.**
- **A mode is created the first time a condition appears in the series, and reused identically every time it recurs.** The constraint is *"once named, always rendered the same"* — never *"only these modes exist."* The library has no ceiling.
- The library **starts empty** and is filled from real episodes. Modes live in `UNIVERSE_STATE` beside locations.

### 6.4 The grade (constant)
Environment saturation always yields to character material colour · shadow and highlight tint are deliberate per mode, never incidental · character material colours are exempt from any scene-wide desaturation.

## 7 · COMPOSITION (9:16 vertical)
- **Frame:** 1080 × 1920. Every composition is built for vertical — subjects are stacked and layered in depth, not spread horizontally.
- **One clear subject per frame.** If two characters share a frame, one is dominant by placement, scale or focus.
- **Subtitle safe zone:** the band around **y ≈ 1150** carries burned subtitles. **No critical action, face, or story-bearing detail may sit there.** Faces belong in the upper-middle third.
- **Platform safe zone:** keep story-critical content clear of the extreme top and bottom of frame (platform UI).
- **Blocking is stated in spatial coordinates** — "left foreground", "centre midground", "right background" — never as vague relations. Coordinates prevent subject overlap and merged limbs.

## 8 · MOVEMENT & ACTION
- **One atomic action per shot.** A shot containing "walks over, picks it up, turns, waves" must be split. Multi-action in a single generation causes temporal morphing.
- **Actions are written as active physical verbs**, observable by a viewer with the sound off.
- **No crowds. No complex hand manipulation. No fast movement.** These are documented failure modes of the video model.
- **Physical contact between characters is a flagged case** — it breaks video models faster than almost anything else. Any shot with characters touching, carrying, or sharing a prop must be identified at planning time and given its own reference treatment.

## 9 · CHARACTER MATERIAL LAWS (identity, written as physics)
These are the reason identity survives. They are **PBR/VFX material specifications, not adjectives**, and are used verbatim — never paraphrased.
- **Müller das Brot** — golden flaky crust with **matte light absorption**; a metallic silver zipper bisects him vertically, revealing interior crumb with **extreme high displacement mapping and maximum ambient occlusion** (deep shadow trapped in porous, cavernous dough); limbs of the same porous crumb; ribbed white knit beanie; navy nylon bomber with ribbed cuffs and a "1. FC BROT" patch requiring **anisotropic fabric reflection**; red semi-translucent plastic grocery bag requiring **specular gloss and crinkle displacement**.
- **Bert das Bier** — heavy thick-walled dimpled glass Maßkrug forming body and limbs, feet resting on cardboard coasters; **high optical index of refraction with caustic light dispersion cast onto the ground**; interior amber liquid with **volumetric translucency**; hair and sprawling moustache of dynamic white beer foam requiring **volumetric subsurface scattering and porous micro-bubbles**; clear glass bulbous nose; wire-rimmed spectacles; textured pink organic tongue; grey **brushed-wool-textured** Bavarian hat with feather and twisted rope band.
- **Rolf die Wurst** — cylindrical sausage with semi-translucent reddish-brown casing showing subtle grease variation and specular highlights; **precise subsurface scattering** implying dense fleshy meat, fat speckles and spices beneath the casing; segmented pinches and tied casing ends forming head and feet; human-like red ears heavily pierced with silver rings; hooded cynical eyes; wet jet-black choppy hair; black tattoos **embedded beneath** the translucent casing; sharply tailored open woven black blazer.
- **Kati die Kartoffel** — **strictly matte albedo with diffuse light absorption and zero specular reflection on the body**; starchy yellow-brown skin with asymmetrical dirt residue, rosy cosmetic pigmentation and deep natural dimples with **high ambient occlusion**; long wavy blonde pigtails requiring **anisotropic hair shading**, green ties; brown leather bodice with green cross-lacing and matching satchel requiring **micro-bump mapping and specular roughness**; pleated skirt; pristine glossy white block-heel boots.

**Silhouette law:** each character must be identifiable from silhouette alone — round blob (Müller) · tall thin cylinder (Rolf) · hourglass (Kati) · square-with-handle (Bert). Silhouette contrast is the strongest defence against drift and must never be compromised by pose or wardrobe.

## 10 · EXCEPTIONS (fenced off so general rules are not misapplied)
- **Kati's glossy white boots** are exempt from her zero-specular body rule. Her polish is a character trait, deliberately retained (ruled 2026-07-15). The exemption covers footwear and cosmetic pigmentation only — never her skin.
- **Bert's minimum identity** = glass-mug body structure + foam hair (+ moustache and spectacles). His hat, feather, mini-mug and coasters are optional per scene and may be dropped without breaking identity.
- **Bert's hat is described as "brushed-wool-textured", never "felt"** — "felt" is on the permanent AVOID list (§13) and the word alone drags the render toward craft-material territory.

## 11 · EMOTIONAL REGISTERS (the show's tonal law)
- **The hook (segment 1, shot 1)** must be readable **with the sound off, in the first second, with no prior context**. If it needs dialogue to land, it fails.
- **Register is deadpan.** Comedy comes from behaviour and situation, played straight. Characters are never winking at the audience.
- **The stereotype is SHOWN, never explained.** No line of dialogue may narrate, name, or justify the cultural behaviour on display.
- **Every episode ends on the human beat, not the punchline** — one small unspoken moment of warmth or vulnerability. The last frame belongs to the character, not the joke.
- **Never-do per register:** no mugging to camera · no reaction shots held past the beat · no visual gag that requires text to read.

## 12 · SOUND (rules, though this document renders no audio — sound logic shapes what is shot)
- **No background music. Ever.** Spoken dialogue and diegetic sound only. This is a fixed audio constraint on every generation.
- **Voice identity:** each character carries a persistent voice-reference clip, attached to every generation in which they appear. Their spoken German is written in `{curly braces}` to lock phoneme-level lip-sync.
- **Diegetic sound is written in four slots, in this order, adjacent to the action that causes it:** `[visual subject + action] → [the sound that action makes, with material and texture] → [ambient bed] → [register]`. Encode physical sound logic beside the visual it belongs to — mass, surface, distance.
- **Props are specified by their physical sound behaviour**, not just their look — a prop's material determines the sound it makes and therefore how it generates.
- **Offscreen sound is tagged as offscreen**, so the model places it spatially instead of trying to render its source in frame.
- **Room tone is always specified.** Silence is a choice, never an omission.
- **Absent by rule:** background music · score stings · sound effects with no visible or implied source.

## 13 · NEGATIVE PROMPT & NEVER-DO LIST (carried into every generation)
**Permanent negative list:** cartoon rendering · 2D illustration · 3D animated movie style · Pixar style · Dreamworks style · plastic skin · glossy CG · hyper-smooth interpolation · floating objects · miniature scale · stop-motion · felt · clay · puppetry · visible seams · text · watermarks · dynamic camera sweeps · impossible physics.
**Never-do (production rules):**
- Never render **any text inside the frame** — no signs, chalkboards, subtitles, captions, or letters. The German is spoken; subtitles are a separate post layer.
- Never **paraphrase** the material laws (§9) or the medium statement (§1) — verbatim or not at all.
- Never **vary a character's description between shots**. Character-for-character identical wording, always (prompt mirroring). A changed word grants permission to alter the character.
- Never let the LLM **write** style or identity text — the pipeline concatenates it mechanically from this file.
- Never exceed **3000 characters** in a video prompt.
- Never **stack adjectives** — one precise word per quality.

## 14 · PROMPT ASSEMBLY (fixed order — no element may silently drop)
**Video (Seedance):** `[Reference assignments] → [Shot structure with timecodes] → [Camera] → [Environment & light: named source + ratio] → [Style] → [Audio] → [Constraints]`
- **First-30-words law:** the primary subject and core action occupy the opening of the prompt, before any style, camera or environment text.
**Storyboard sheet (Nano Banana Pro):** `[Reference binding] → [Sheet format + style clause] → [Environment + per-panel coordinate blocking] → [Constraints]`
**Reference binding law:** identity comes from images, not from words. Bind each character to their **multi-angle sheet (primary — the structural map that prevents back/side dissolution) and portrait (secondary — close-up anchor)**, instruct the model to lock geometry, texture and wardrobe *from the references only*, and never restate their appearance in prose.
**Per-shot specification** — every shot carries: `shot_size · camera_angle · camera_move · one action · blocking (spatial coordinates) · gaze · expression · duration · dialogue · named light source + ratio · negative prompt · revision prompt (the pre-planned correction, so iteration stays inside this treatment's language)`.

## 15 · ⧖ OPEN — deliberately unfilled until first production
These are **not oversights**; they are decisions that require real footage rather than theory (Jayon, 2026-07-29). Method for closing them: `WORKFLOW_visual_identity_lock.md`.
1. **Tonal-mode library** (§6.3) — starts empty, fills from real episodes.
2. **Reference palettes** — 15–25 real film/photography frames → `resources/style_references/`, from which the specific value/saturation/tint discipline is extracted.
3. **The style plate** — one locked canonical frame, generated in Nano Banana Pro, attached to every later generation as the global style reference. Until it exists, the style reference slot resolves as `pending`.
4. **Location plates** — accumulated one per recurring location as the series establishes them.
5. **Identity validation** — the never-run C1 win condition: the same character generated twice, independently, in different environments, must read as unmistakably the same character in the same show.

## 16 · FORMAT & DELIVERY (fixed)
9:16 vertical · 1080 × 1920 · 30 fps · one episode ≈ **30 s** = 2 × 15 s generated segments (45 s = 3 segments is an explicit exception) · burned subtitles are a **separate post layer**, never generated in-frame, positioned in the §7 safe zone, colour-coded **der = blue · die = red · das = green · target grammar = yellow**.

## 17 · QUICK-REFERENCE CARD (the fast check — if a frame fails any line, it fails)
1. Live-action VFX integration, photoreal CGI characters at human scale. Never puppet/miniature/stop-motion.
2. 35mm anamorphic · eye-level default · locked-off tripod with subtle breathing · camera holds unless motivated.
3. Light = **named source + ratio**. No mood words. Motivated only.
4. **The cast wins the frame** — separated by value, saturation or hue. The environment yields; characters are never desaturated.
5. Material laws verbatim. Silhouettes distinct. Identity from reference images, never from prose.
6. One atomic action per shot. Blocking in spatial coordinates. No crowds, no fast movement, no complex hands.
7. Nothing in the subtitle band. **No text in frame, ever.**
8. No background music. Diegetic sound written beside the action that causes it.
9. Hook readable muted in one second. Stereotype shown, never explained. End on the human beat.
10. Negative list attached. ≤3000 chars. No adjective stacking. Never paraphrase canon.

## 18 · NAMING LAW
Full canonical names, always: **Rolf die Wurst · Bert das Bier · Kati die Kartoffel · Müller das Brot**. Never abbreviations, titles, or variants.

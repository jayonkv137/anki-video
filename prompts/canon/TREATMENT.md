# TREATMENT — "Stereotypical German" · the directorial rule system

> version: 1.4 · canon file · 2026-08-02
> v1.4 (2026-08-02): the last five invideo guides absorbed (ledger: `RESEARCH_invideo_production_guides.md`). **§16.3 the style anchor is now a two-stage strategy** — the plate bootstraps, a *graded episode segment* supersedes it (footage is a lossless style reference; prose is a lossy one) via the `@VideoN` slot our Seedance canon documents and we have never used. **§6.3 tonal modes carry hex tints** (a named mode with unnamed tints is not reusable). **§16.6 the pre-return frame gate** — generated frames are checked against this document *before* they are shown.
> v1.3 (2026-08-02): absorbs the four invideo production guides that were supplied but never read in full (`AI Script Breakdown`, `AI Shot Planning`, `Diegetic Sound Cues`, `AI Micro-Drama`) — closing the "12 parameters per shot: we cover ~7" gap logged in `DESIGN_agent_crew_and_treatment.md` §2 on 2026-07-29. New: **§3.1 depth of field per shot** · **§6.5 the tonal mode is declared per segment** · **§8.1 atmosphere layers** · **§8.2 the two pre-generation reference duties** (fused sheet for contact, mock blocking reference for POV/complex camera) · **§8.3 the density stress-test** (the screenplay agent argues with the page *before* credits are spent) · **§13 sound is anchored to the visual beat** · **§9.6 turnaround-sheet hygiene**.
> v1.2 (2026-08-02): **§9 corrected to the image model's real reference mechanics** (typed slots 5 human / 6 object / 3 style; characters FIRST, style LAST — the v1.1 order was contradicted by the model) · **image-prompt identity TOKENS** (`Character-X`) added as the naming law's one fenced exception (§9.4, §19) · §14 stage-scoped (the negative list is video language; the image model uses a constraints block) · §9.5 asset-gap note withdrawn (Jayon: Rolf's set is correct as-is, `PLAN_production_canon` §7) · `canon_blocks.md` formally retired from the registry — §10 is the sole source (the retired file still said "felt"). Basis: `prompting_guidelines_nanobanana.md` v1.0.
> **This is the controlling document of the production.** The screenplay is the narrative source of truth; THIS is the execution source of truth. Every visual stage (storyboard sheets, video prompts) reads it and every generated frame is gated against it. **Rules, not descriptions** — every line below must be checkable against a frame. If a line cannot be checked, it does not belong here.
> v1.1 (Jayon's review): camera and angle sections reframed from prohibitions to **defaults + a standard vocabulary** (the story may demand anything; only technical limits are hard) · V3-era tonal locks removed · **§9 REFERENCE ASSETS added** — the missing rule for which character images attach where, in what order, at each stage.
> **Consolidates:** `canon_blocks.md` v1.0 · `prompting_guidelines_seedance.md` v2.2 · `Characters-Main-Sheet.md` v1.3 · `AUDIT_visual_identity.md` · `WORKFLOW_visual_identity_lock.md`. Sections marked **⧖ OPEN** are deliberately unfilled until the first real episodes exist — see §16.

---

## 1 · MEDIUM (what the images ARE — the load-bearing line)
High-end **cinematic live-action cinematography integrated with photorealistic CGI characters**, exhibiting macro-level tactile materiality and true physical presence within real-world environments.
- The characters are **physically real entities at human scale**, present in real locations. They are never depicted as objects, toys, models, or animation.
- **Live-Action Integration Rule (absolute):** the words *puppet · claymation · needle-felt · stop-motion · miniature · toy · handcrafted* never appear in any canon file, skill, screenplay, or prompt. These terms poison the latent space toward visible seams, stepped framerates and tilt-shift miniature depth of field.

## 2 · CAMERA
- **House default:** locked-off on a heavy tripod with **subtle handheld breathing**; natural motion blur. **The camera holds unless the action motivates a move** — restraint is the show's grammar and should be the majority of any episode.
- **Every shot states its camera explicitly.** Omitting camera direction makes the model default to a static medium shot and produces localised hallucination.
- **Syntax:** `Camera: [move] + [speed] + [stability]`.
- **Technical limits (model constraints, not taste — these are hard):**
  - Any tracking or panning instruction must carry `no zoom, maintain subject size in frame`. The engine otherwise confuses physical dolly movement with focal-length change and warps the background.
  - **Fast camera movement degrades the render.** Where a scene needs speed, take it from subject motion or from cutting, not from camera velocity.
  - **One camera idea per shot.** Compound moves are possible (joined with "then") but cost fidelity — spend that deliberately.
- **Deviating from the default is allowed whenever the story requires it**, stated as a deliberate choice rather than drift. *Note: `dynamic camera sweeps` sits on the inherited AVOID list (§14); removing it is a canon decision to make consciously, not a per-episode one.*

## 3 · LENS
- **35mm anamorphic**, consistently, everywhere.
- **Subtle lens halation** and **slight edge fringing** are present; both are subtle — visible on inspection, never the subject.
- Depth of field is **not fixed globally**. DOF is chosen per shot to serve the subject, and never so shallow that the environment becomes unreadable.

### 3.1 Depth of field is a per-shot decision, stated
Every shot **states its DOF** — `deep` (environment legible, the default for teaching shots, since the situation carries the meaning) · `medium` · `shallow` (isolates the subject; reserve it for a beat that earns it). Unstated DOF is how a series drifts into uniform blur. **A shot whose meaning must be readable with the sound off should not be shallow** — `PEDAGOGY` §1 outranks the aesthetic here.

## 4 · ANGLES & SHOT SIZES
- **Standard vocabulary** — used so the pipeline, the agents and the shot schema parse consistently. It is a shared language, not a ceiling:
  - **Sizes:** ECU · CU · MCU · MS · MWS · WS · OTS
  - **Angles:** eye-level · low (power) · high (vulnerability) · dutch (tension) · POV
- **Eye-level is the default**, not a limit.
- **Vary size and angle shot-to-shot.** Two adjacent shots must not share both.
- **Anything outside the vocabulary is available when the story calls for it** — name it explicitly in the shot so it can be reused consistently and, if it recurs, added to the vocabulary.

## 5 · LIGHTING — *named sources and ratios, never moods*
- **Every scene's light is expressed two ways and only these two:** a **named source** (what is emitting the light — "overhead supermarket fluorescents", "low winter sun through the window", "sodium street lamp camera-left") and a **ratio** (light-to-shadow, e.g. `70:30`).
- **Mood words are not lighting direction.** "Moody", "dramatic", "beautiful lighting" must be rewritten as a source + ratio. *"Warm lighting"* is a description; *"warm yellow from the practical lamps only"* is a rule.
- **Motivated light only:** every light comes from a source visible in frame or logically implied by the location.
- **Light adapts to the environment; it is never imposed on it.** There is no global colour temperature and no global key-fill ratio — those are properties of the **tonal mode** (§6.3), not of the show.
- **Shadow discipline:** shadows are shaped and directional, consistent with the named source. Flat, sourceless ambient light is a failure state.

## 6 · COLOUR
### 6.1 The separation rule (absolute, hue-independent)
> **The cast always wins the frame.** In every shot each character is the most present thing in it, separated from the environment by at least one of **value** (they sit lighter or darker than what is behind them), **saturation** (their material colour is more saturated than the surrounding surfaces), or **hue** (the environment sits in a different family from their warm earth tones).
- **The environment yields.** Where a location's natural palette competes with a character, the location is pushed back in value, saturation, or both.
- **Character material colour is never desaturated to match a scene.** The grade acts on the world, not on the cast.
- **Checkable as:** *does any surface out-compete a character for attention?* If yes, the frame fails.
- **Deliberately not a hue rule.** The series moves across all of Germany — a Bavarian beer tent, a Berlin club, a northern harbour — each may be warm, cool, saturated or grey. Only the hierarchy is fixed.
- **Deliberate violation is a dramatic instrument:** a character overwhelmed by their environment is permitted when the story requires it, as an explicit choice.

### 6.2 Character accents (fixed — material properties, not styling)
| Character | Primary | Secondary accents |
|---|---|---|
| Müller das Brot | golden crust | navy · white · **red** bag |
| Bert das Bier | **amber** + clear glass | white foam · grey |
| Rolf die Wurst | red-brown casing | black · silver |
| Kati die Kartoffel | yellow-brown | blonde · **green** · brown · white |
All four are **warm earth tones** — a material fact of what they are, never adjusted.

### 6.3 Tonal modes — a GROWING LIBRARY ⧖ OPEN
- A **mode** is a named, reusable colour+light condition recording: **name · named source(s) · ratio · shadow tint (hex) · highlight tint (hex) · saturation note · how §6.1 separation is achieved here.** Tints are written as **hex values, not adjectives** — "cool shadows" is a description two people render differently; `#1E2A38` is a mode. A named mode whose tints are unnamed is not reusable, which defeats the point of naming it.
- **Created the first time a condition appears; reused identically every time it recurs.** The constraint is *"once named, always rendered the same"* — never *"only these modes exist."* No ceiling.
- Library **starts empty**, fills from real episodes, lives in `UNIVERSE_STATE` beside locations.

### 6.5 The mode is declared per SEGMENT, never per shot
A tonal mode is a **colour + light condition**, and a condition does not change between two shots of the same continuous moment. **Each segment declares exactly one tonal mode**, by name; every shot inside it inherits that mode and varies only its own named source and ratio (§5). Two segments may differ (time passes, the scene moves) — two shots inside one segment may not. This is what makes a mode reusable rather than decorative, and it is why the mode lives on the segment in the screenplay.

### 6.4 The grade (constant)
Environment saturation always yields to character material colour · shadow and highlight tint are deliberate per mode, never incidental · character material colours are exempt from any scene-wide desaturation.

## 7 · COMPOSITION (9:16 vertical)
- **Frame:** 1080 × 1920. Compositions are built for vertical — subjects stacked and layered in depth, not spread horizontally.
- **One clear subject per frame.** If two characters share a frame, one is dominant by placement, scale or focus.
- **Subtitle safe zone:** the band around **y ≈ 1150** carries burned subtitles. **No critical action, face, or story-bearing detail may sit there.** Faces belong in the upper-middle third.
- **Platform safe zone:** keep story-critical content clear of the extreme top and bottom of frame (platform UI).
- **Blocking is stated in spatial coordinates** — "left foreground", "centre midground", "right background" — never as vague relations. Coordinates prevent subject overlap and merged limbs.

## 8 · MOVEMENT & ACTION
- **One atomic action per shot.** A shot containing "walks over, picks it up, turns, waves" must be split. Multi-action in a single generation causes temporal morphing.
- **Actions are written as active physical verbs**, observable with the sound off.
- **Known model failure cases — plan around them:** crowds · complex hand manipulation · very fast movement · **physical contact between characters** (touching, carrying, shared props). Contact shots break video models faster than almost anything else and must be identified at planning time and given their own reference treatment (§8.2).

### 8.1 Atmosphere layers
**Every shot states its atmosphere**, because the model renders air: `none · haze · dust · steam · smoke · rain · snow · fog`, with a density (`light · medium · heavy`). Atmosphere is what makes light *visible* — a named source with no medium to travel through reads flat. It is also a continuity trap: two shots in one segment must carry the **same** atmosphere, or the cut looks like a location change. `none` is a legitimate, and the most common, answer — state it rather than omitting it.

### 8.2 The two pre-generation reference duties
Two shot types cannot be fixed by better wording and must be **flagged in the screenplay**, so the reference exists before generation is attempted:
1. **Contact shots** (characters touching, carrying, a shared prop between them). A sheet per character is **not enough** — the model must see the two bodies *in their arrangement*. The shot is flagged, and a **fused reference sheet of the contact configuration** is generated and locked before the shot is. Where a prompt cannot produce the fused sheet, a hand sketch is a valid input to it.
2. **POV and complex-camera shots**, a documented weak point of current video models. These are flagged for a **mock blocking reference** — the move acted out and filmed on a phone, supplied as a spatial anchor. Prompting harder does not substitute; the reference is the fix.
**Both flags are the screenplay's job**, not the compiler's: they are identified while the shot is being written, which is the last moment they are cheap.

### 8.3 The density stress-test — argue with the page before credits
Cut density is checked **at the lock, against the model's real limit**, never discovered mid-generation. A segment is ~15 s: count its shots and ask whether each can read and (if it speaks) deliver its line. **If the beat needs more cuts than the clip can hold, the screenplay agent says so and proposes the split** — a segment divided at the lock cuts better than one crammed and salvaged. This duty runs *backwards* into the writing: flagging an ungeneratable shot is the cheapest correction in the pipeline, and the agent that stays silent to be agreeable has failed its station.

## 9 · REFERENCE ASSETS — what attaches, where, in what order
Identity comes from **images, not from words**. This section is the binding contract between the asset library and every generation.

### 9.1 The canonical asset set (per character)
| Asset | Role | Notes |
|---|---|---|
| **Multi-angle character sheet** | **PRIMARY** — the structural map; prevents back/side/turn dissolution | always attached |
| **Profiles sheet** | additional angle coverage | attach when present and budget allows |
| **Portrait / Master** | close-up identity anchor | always attached |
| **Close-up** | facial and small-detail fidelity | small details only hold across models if shown at close range |
| **Voice clip (.mp3)** | phoneme-level lip-sync | video stage only, as `@AudioN` |

### 9.2 The attachment-order law
**The numbering written in a prompt must match the order the files are attached, exactly.** A prompt that says "Image 2 is the multi-angle sheet" while the sheet is attached third is a broken prompt. Fixed order per stage, skipping anything that does not exist yet — **characters first, style last** (the image model routes references through typed slots — 5 human · 6 object · 3 style — and weights the earliest indices heaviest; `prompting_guidelines_nanobanana.md` §3):
**Storyboard sheet (Nano Banana Pro):**
1. **Character A** — sheet → portrait
2. **Character B** — sheet → portrait *(a rare third cameo: portrait only)*
3. **Close-up** — only when a single character carries the scene and the human budget (≤5) allows
4. **Location plate** ⧖ (object slot)
5. **Continuity reference** — the previous segment's sheet (style slot, low weight)
6. **Style plate** ⧖ — always last (style slot)
**Video (Seedance):** Character A (sheet → portrait) → Character B (sheet → portrait) → style plate ⧖ → **storyboard panels**, one per shot, in shot order.
Audio, in cast order: Character A voice → Character B voice.

### 9.3 Per-stage budget
- **Storyboard sheet (Nano Banana Pro, ≤14 refs = 5 human · 6 object · 3 style):** two characters × (sheet + portrait) = **4 of 5 human slots** · location plate (object) · previous-segment sheet + style plate (style) ≈ **7 of 14**. **The human-slot ceiling, not the total, is the binding limit** — close-ups fit only when one character carries the scene.
- **Video (Seedance, ≤9 images, ≤3 audio):** the panels already carry environment and composition, so **drop the location plate and the close-ups**: two characters × (sheet + portrait) + style plate + one panel per shot ≈ **8–9 of 9**. Tight by design.
- **≤3 speaking characters per segment** (audio cap); the show's own limit is 2 mains.

### 9.4 Binding language
Bind each character to their images explicitly and instruct the model to take identity **from the references only** — never restate a character's appearance in prose alongside the reference (competing descriptions cause drift). The material laws (§10) are the exception: they are the canonical wording when text description is required at all.
**In image-model prompts, identity binds to TOKENS** — `Character-Rolf · Character-Bert · Character-Kati · Character-Mueller` — never the full canonical names, whose German common nouns (*die Wurst, das Bier…*) pull generic imagery into the render (the fenced exception, §19 / `SHOW_BIBLE` §13). Video prompts keep the full canonical names.

### 9.5 Turnaround-sheet hygiene (when a sheet is generated or replaced)
- **Empty the hands.** Held props drift across angles and contaminate the identity reference — generate turnarounds prop-free and reintroduce props at shot level.
- **Include close-up panels.** Small details (Rolf's ear rings, Müller's "1. FC BROT" patch, Kati's green lacing) only survive across models if the sheet shows them at close range.
- **Generate several options, pick one, lock it.** A locked identity is the cheapest insurance in the pipeline; re-rolling finished shots because identity was never locked is the expensive failure.
- **The fused contact sheet** (§8.2) is generated the same way and locked the same way — it is an identity asset, not a per-shot fix.

## 10 · CHARACTER MATERIAL LAWS (identity, written as physics)
These are the reason identity survives. They are **PBR/VFX material specifications, not adjectives**, and are used verbatim — never paraphrased.
- **Müller das Brot** — golden flaky crust with **matte light absorption**; a metallic silver zipper bisects him vertically, revealing interior crumb with **extreme high displacement mapping and maximum ambient occlusion** (deep shadow trapped in porous, cavernous dough); limbs of the same porous crumb; ribbed white knit beanie; navy nylon bomber with ribbed cuffs and a "1. FC BROT" patch requiring **anisotropic fabric reflection**; red semi-translucent plastic grocery bag requiring **specular gloss and crinkle displacement**.
- **Bert das Bier** — heavy thick-walled dimpled glass Maßkrug forming body and limbs, feet resting on cardboard coasters; **high optical index of refraction with caustic light dispersion cast onto the ground**; interior amber liquid with **volumetric translucency**; hair and sprawling moustache of dynamic white beer foam requiring **volumetric subsurface scattering and porous micro-bubbles**; clear glass bulbous nose; wire-rimmed spectacles; textured pink organic tongue; grey **brushed-wool-textured** Bavarian hat with feather and twisted rope band.
- **Rolf die Wurst** — cylindrical sausage with semi-translucent reddish-brown casing showing subtle grease variation and specular highlights; **precise subsurface scattering** implying dense fleshy meat, fat speckles and spices beneath the casing; segmented pinches and tied casing ends forming head and feet; human-like red ears heavily pierced with silver rings; hooded cynical eyes; wet jet-black choppy hair; black tattoos **embedded beneath** the translucent casing; sharply tailored open woven black blazer.
- **Kati die Kartoffel** — **strictly matte albedo with diffuse light absorption and zero specular reflection on the body**; starchy yellow-brown skin with asymmetrical dirt residue, rosy cosmetic pigmentation and deep natural dimples with **high ambient occlusion**; long wavy blonde pigtails requiring **anisotropic hair shading**, green ties; brown leather bodice with green cross-lacing and matching satchel requiring **micro-bump mapping and specular roughness**; pleated skirt; pristine glossy white block-heel boots.

**Silhouette law:** each character must be identifiable from silhouette alone — round blob (Müller) · tall thin cylinder (Rolf) · hourglass (Kati) · square-with-handle (Bert). Silhouette contrast is the strongest defence against drift and is never compromised by pose or wardrobe.

## 11 · EXCEPTIONS (fenced off so general rules are not misapplied)
- **Kati's glossy white boots** are exempt from her zero-specular body rule. Her polish is a character trait, deliberately retained (ruled 2026-07-15). The exemption covers footwear and cosmetic pigmentation only — never her skin.
- **Bert's minimum identity** = glass-mug body structure + foam hair (+ moustache and spectacles). His hat, feather, mini-mug and coasters are optional per scene and may be dropped without breaking identity.
- **Bert's hat is "brushed-wool-textured", never "felt"** — "felt" is on the permanent AVOID list (§14) and the word alone drags the render toward craft-material territory.

## 12 · REGISTER
- **The hook (segment 1, shot 1)** must be readable **with the sound off, in the first second, with no prior context**. If it needs dialogue to land, it fails.
- **Register is deadpan.** Comedy comes from behaviour and situation, played straight.

## 13 · SOUND (rules, though this document renders no audio — sound logic shapes what is shot)
- **No background music. Ever.** Spoken dialogue and diegetic sound only. A fixed audio constraint on every generation.
- **Voice identity:** each character carries a persistent voice-reference clip, attached to every generation in which they appear. Spoken German is written in `{curly braces}` to lock phoneme-level lip-sync.
- **Diegetic sound is written in four slots, in this order, adjacent to the action that causes it:** `[visual subject + action] → [the sound that action makes, with material and texture] → [ambient bed] → [register]`. Encode physical sound logic beside the visual it belongs to — mass, surface, distance.
- **Props are specified by their physical sound behaviour**, not only their look — material determines the sound and therefore how the prop generates.
- **Offscreen sound is tagged as offscreen**, so the model places it spatially instead of rendering its source in frame.
- **Sound is anchored to the visual beat**, not floated across the clip: *"the door slams shut at the moment she turns"*. A cue with no stated timing lands wherever the model likes, and a mistimed impact reads as a rendering fault even when the image is perfect.
- **Room tone is always specified.** Silence is a choice, never an omission.
- **Absent by rule:** background music · score stings · sound effects with no visible or implied source.

## 14 · NEGATIVE PROMPT & NEVER-DO LIST (carried into every generation)
**Permanent negative list:** cartoon rendering · 2D illustration · 3D animated movie style · Pixar style · Dreamworks style · plastic skin · glossy CG · hyper-smooth interpolation · floating objects · miniature scale · stop-motion · felt · clay · puppetry · visible seams · text · watermarks · dynamic camera sweeps · impossible physics.
**Stage scoping (v1.2):** the list above is **video-stage (Seedance) language**. The image model has no negative-prompt channel — naming artifacts there *causes* them; the image stage expresses the same intents as a positive **constraints block** (`prompting_guidelines_nanobanana.md` §7). The intents bind both stages.
**Never-do (production rules):**
- Never render **any text inside the frame** — no signs, chalkboards, subtitles, captions, or letters. The German is spoken; subtitles are a separate post layer.
- Never **paraphrase** the material laws (§10) or the medium statement (§1) — verbatim or not at all.
- Never **vary a character's description between shots**. Character-for-character identical wording, always (prompt mirroring). A changed word grants permission to alter the character.
- Never let the LLM **write** style or identity text — the pipeline concatenates it mechanically from this file.
- Never exceed **3000 characters** in a video prompt.
- Never **stack adjectives** — one precise word per quality.

## 15 · PROMPT ASSEMBLY (fixed order — no element may silently drop)
**Video (Seedance):** `[Reference assignments] → [Shot structure with timecodes] → [Camera] → [Environment & light: named source + ratio] → [Style] → [Audio] → [Constraints]`
- **First-30-words law:** the primary subject and core action occupy the opening of the prompt, before any style, camera or environment text.
**Storyboard sheet (Nano Banana Pro):** `[Reference binding] → [Sheet format + style clause] → [Environment + per-panel coordinate blocking] → [Constraints]`
**Per-shot specification (v1.3 — the complete brief)** — every shot carries:
`shot_size · camera_angle · camera_move · depth_of_field (§3.1) · one action · blocking (spatial coordinates) · gaze · expression · duration · dialogue · named light source + ratio (§5) · atmosphere + density (§8.1) · props with sound behaviour (§13) · contact-shot flag (§8.2) · blocking-reference flag (§8.2) · negative prompt · revision prompt (the pre-planned correction, so iteration stays inside this treatment's language)`.
**Per-segment specification** — every segment carries: `duration · time and weather · tonal mode (§6.5)`.
**A shot missing any of these is not a finished shot.** The list is the definition of "complete", and it is what the quality gate checks before a sheet is generated.

## 16 · ⧖ OPEN — deliberately unfilled until first production
Not oversights — decisions that require real footage rather than theory (Jayon, 2026-07-29). Method: `WORKFLOW_visual_identity_lock.md`.
1. **Tonal-mode library** (§6.3) — starts empty, fills from real episodes.
2. **Reference palettes** — 15–25 real film/photography frames → `resources/style_references/`, from which the value/saturation/tint discipline is extracted.
3. **The style anchor — a two-stage strategy.**
   - **Stage 1 (bootstrap, until a graded episode exists):** one locked canonical frame generated in Nano Banana Pro — the **style plate** — attached to every later generation. Until it exists, the style slot resolves as `pending`.
   - **Stage 2 (once a graded episode exists):** the plate is superseded as the primary anchor by **a representative graded segment of a finished episode**, attached as a video reference (`prompting_guidelines_seedance.md` §4: `@VideoN`, ≤3, ≤15s total — which is why the reference is *one 15s segment*, never a whole 30s episode). A written description of a look is a lossy translation of footage; the footage is lossless. It transfers **camera angles, camera movement, environment logic and tonal feel — never character identity**, which stays with the sheets (§9). The reference must be the **final graded cut**: an ungraded rough cut transfers an ungraded look. The current reference segment is recorded in `UNIVERSE_STATE` and changes only by deliberate decision.
4. **Location plates** — accumulated one per recurring location.
5. **Identity validation** — the C1 win condition: the same character generated twice, independently, in different environments, must read as unmistakably the same character in the same show.

### 16.6 The pre-return frame gate
A generated frame is checked **against this document before it is shown**, not after it is chosen: the quick-reference card (§18) is run over every returned sheet and clip, and a frame failing a line is surfaced *with the failing line named*. Catching a violation at return costs one regeneration; catching it at assembly costs everything built on top of it. The same discipline applies to a finished cut — read it back against the screenplay and this document rather than scrubbing a timeline by eye.

## 17 · FORMAT & DELIVERY (fixed)
9:16 vertical · 1080 × 1920 · 30 fps · one episode ≈ **30 s** = 2 × 15 s generated segments (45 s = 3 segments is an explicit exception) · burned subtitles are a **separate post layer**, never generated in-frame, positioned in the §7 safe zone, colour-coded **der = blue · die = red · das = green · target grammar = yellow**.

## 18 · QUICK-REFERENCE CARD (the fast check — if a frame fails any line, it fails)
1. Live-action VFX integration, photoreal CGI characters at human scale. Never puppet/miniature/stop-motion.
2. 35mm anamorphic · eye-level default · camera holds unless motivated · every shot states its camera.
3. Light = **named source + ratio**. No mood words. Motivated only.
4. **The cast wins the frame** — separated by value, saturation or hue. The environment yields; characters are never desaturated.
5. Material laws verbatim. Silhouettes distinct. **Identity from reference images in the fixed order (§9), never from prose.**
6. One atomic action per shot. Blocking in spatial coordinates. DOF and atmosphere stated. Contact and POV shots flagged for their reference (§8.2). Density checked against the clip (§8.3).
7. Nothing in the subtitle band. **No text in frame, ever.**
8. No background music. Diegetic sound written beside the action that causes it.
9. Hook readable muted in one second. Deadpan register.
10. Negative list attached. ≤3000 chars. No adjective stacking. Never paraphrase canon.

## 19 · NAMING LAW
Full canonical names, always: **Rolf die Wurst · Bert das Bier · Kati die Kartoffel · Müller das Brot**. Never abbreviations, titles, or variants.
**One fenced exception:** image-model prompts bind identity via the `Character-X` tokens (§9.4) — everywhere else, the full names, always.

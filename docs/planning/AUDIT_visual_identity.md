# AUDIT — The Visual Identity, as it exists today (complete inventory)

> **Status: AUDIT (2026-07-29), for Jayon's confirmation.** Everything about how the show LOOKS that has been decided across all sessions/docs, pulled together in one place, then split into **UNIVERSAL (constant, every episode)** vs **PER-EPISODE (variable, you specify at storyboard time)** — plus the gaps that must be closed. This is the direct input to the **Treatment document** (`DESIGN_agent_crew_and_treatment.md`).
> **Sources audited:** `prompts/canon/canon_blocks.md` v1.0 · `prompts/canon/prompting_guidelines_seedance.md` v2.2 · `resources/Characters-Main-Sheet.md` v1.3 · the four per-character Character Bibles · `docs/changelog.md` (THE VISUAL PIVOT, 2026-07-21) · `docs/planning/RESEARCH_art_style_system.md` (2026-07-15, partly superseded) · `C1_character_review.md` · `VISION_HISTORY.md` · `RESEARCH_storyboard_sheet_method.md` · `DESIGN_subtitle_and_assembly.md` · live artifacts (`screenplay.json`, `storyboard.json`).

---

## 0 · The one decisive event: THE VISUAL PIVOT (2026-07-21)
The show's look was **re-founded** on 2026-07-21, from Jayon's three research docs (CGI Integration research + Lookbook + Pipeline Design). **Everything written before that date about puppets, felt, handcrafted imperfection and stop-motion is SUPERSEDED and is now explicitly banned vocabulary.**
- **Before:** "photographed handcrafted puppets on miniature sets", matte felt/wool materials, deliberate handmade flaws, shallow-DOF miniature scale, the "is it real?" puppet×real hybrid.
- **After (current law):** **high-end cinematic live-action cinematography integrated with photorealistic CGI characters**, macro-level tactile materiality, real-world environments at human scale.
- **Why:** the old canon literally commanded what the new AVOID list bans; aesthetic vocabulary was poisoning the latent space (felt/puppet words *caused* seams and stop-motion looks).
- **Also decided the same day — the Constants-vs-Variables architecture:** hardcoded lighting (3200K/5600K, high-key) and depth-of-field were **REMOVED from the permanent style block** because they fought outdoor scenes and produced a "pasted-in" look. Lighting became a per-scene variable written by the prompt skill acting as a *virtual Director of Photography*.

---

## 1 · UNIVERSAL — the constants (same in every single episode, forever)

### 1.1 Medium statement (the most important line — declares what the images ARE)
> "High-end cinematic live-action cinematography integrated with photorealistic CGI characters, exhibiting macro-level tactile materiality and perfect physical presence within real-world environments."

### 1.2 Camera law
35mm **anamorphic** lens · **eye-level** framing · **locked-off camera on a heavy tripod** · subtle **handheld breathing** · **natural motion blur**. *Restraint is the style* — no drone shots, no dynamic sweeps.

### 1.3 Lens artifacts
Subtle **lens halation** · slight **edge fringing**.

### 1.4 The AVOID list (permanent negative grammar)
cartoon rendering · 2D illustration · 3D animated movie style · **Pixar style** · **Dreamworks style** · **plastic skin** · **glossy CG** · hyper-smooth interpolation · floating objects · **miniature scale** · **stop-motion** · **felt** · **clay** · **puppetry** · visible seams · text · watermarks · dynamic camera sweeps · impossible physics.

### 1.5 The Live-Action Integration Rule (vocabulary ban, enforced at every stage)
**Never** use puppet / claymation / needle-felt / stop-motion / miniature / toy words *anywhere* — not in canon, skills, screenplays, or prompts. Characters are physically real entities interacting with human-scale, real-world environments. These terms poison the latent space toward visible seams, stepped framerates and tilt-shift miniature DOF.

### 1.6 The four character MATERIAL LAWS (per-character, but constant across all episodes)
Written as **PBR/VFX material vocabulary**, not adjectives — this is what makes identity survive:
| Character | Structure | The material law (verbatim intent) |
|---|---|---|
| **Müller das Brot** | artisan loaf; round/blob silhouette | golden flaky crust with **matte light absorption**; metallic silver zipper bisecting him vertically revealing interior crumb with **extreme high displacement mapping + maximum ambient occlusion** (deep shadows in porous cavernous dough); limbs of the same porous crumb; ribbed white knit beanie; navy nylon bomber with ribbed cuffs + "1. FC BROT" patch requiring **anisotropic fabric reflections**; red semi-translucent plastic grocery bag requiring **specular gloss + crinkle displacement** |
| **Bert das Bier** | thick glass Maßkrug; square-with-handle silhouette | heavy thick-walled dimpled glass body/limbs on cardboard coasters; **high optical IOR + caustic light dispersion cast onto the ground**; interior amber liquid with **volumetric translucency**; hair + sprawling moustache of dynamic white beer foam requiring **volumetric subsurface scattering + porous micro-bubbles**; clear glass bulbous nose; wire-rimmed spectacles; textured pink organic tongue; grey felt Bavarian hat with feather + twisted rope band |
| **Rolf die Wurst** | cylindrical sausage; tall thin silhouette | semi-translucent reddish-brown casing with subtle grease variation + specular highlights; **precise subsurface scattering** implying dense fleshy meat, fat speckles and spices beneath; segmented pinches + tied casing ends forming head and feet; human-like red ears heavily pierced with silver rings; hooded cynical eyes; wet jet-black choppy hair; black tattoos **embedded beneath** the translucent casing; sharply tailored open woven black blazer |
| **Kati die Kartoffel** | potato; hourglass silhouette | **strictly matte albedo + diffuse light absorption, ZERO specular reflection on the body**; starchy yellow-brown skin with asymmetrical dirt residue, rosy cosmetic pigmentation, deep natural dimples with **high ambient occlusion**; long wavy blonde pigtails requiring **anisotropic hair shading**, green ties; brown leather bodice with green cross-lacing + satchel requiring **micro-bump mapping + specular roughness**; pleated skirt; pristine glossy white block-heel boots |

### 1.7 Cast-design principles (why the cast survives drift — from the C1 review)
- **Silhouette contrast is the single best predictor of surviving AI drift:** round blob (Brot) · tall thin cylinder (Wurst) · hourglass (Kartoffel) · square mug with handle (Bier). Any character identifiable from silhouette alone.
- **Distinct eye signatures:** wide blue googly · heavy-lidded deadpan · sultry side-glance · bulging amber.
- **Material gags are identity:** the zipper carved into crust with exposed crumb · the dirndl carved from her own peel · casing-knot toes + tattoos embedded in the casing · foam as Einstein hair. *These are characters, not objects in clothes.*
- **Ruled exceptions (Jayon, 2026-07-15):** Kati's polished/glossier render is **KEPT** as a character trait (her polish IS the character) despite the matte rule. **Bert's minimum identity** = beer-glass structure + foam hair (+moustache/glasses); individual props (mini-mug, coasters) may drop per scene.

### 1.8 Identity reference mechanism (how the look is enforced technically)
**Sheet-first dual resolution** per character: (1) **multi-angle character sheet** = PRIMARY (structural map that prevents back/side dissolution on turns), (2) **main portrait** = secondary close-up anchor, (3) **voice clip** (.mp3) for lip-sync. All auto-attached to every generation where the character is present. **No LoRA / no fine-tuning** — consistency comes from references + prompt discipline.

### 1.9 Prompt-architecture law
- **Verbatim style block:** the style text is pasted **identically** into every prompt — never paraphrased, **not even synonym swaps** (a changed word signals permission to alter the latent representation → drift).
- **Prompt mirroring:** each character's description is character-for-character identical across every shot.
- **The engineering rule:** the LLM never *writes* style or character text — the pipeline **mechanically concatenates** the canon blocks. Style consistency is a code guarantee, not hoped-for model behaviour.
- **Fixed assembly order** (Seedance): `[Ref Assignments] → [Shot Structure] → [Camera] → [Environment/Light] → [Style] → [Audio] → [Constraints]`; first-30-words law; ≤3000 chars; one adjective per quality (no stacking).

### 1.10 Format & delivery constants
**9:16 vertical, 1080×1920** · 30 fps · ~30s episode = 2×15s Seedance segments · **no on-screen text inside the frame ever** (German is spoken; subtitles are a separate post layer) · subtitle system: safe zone x540/y1150, bold 64pt with opaque box, colour-coding **der=blue · die=red · das=green · grammar=yellow**.

---

## 2 · PER-EPISODE — the variables (you specify these at storyboard/ideation time)
| Variable | Where it lives today | Notes |
|---|---|---|
| **Environment / location** | `screenplay.environment` | One environment per episode (vary by corner/angle/props, not by location) |
| **Time of day + weather** | `segment.time_and_weather` | Your 07-28 addition; drives lighting adaptation across segments |
| **Lighting mood** | *currently improvised* | Was per-shot `lighting_mood`; you removed that field 07-28 |
| **Props** | inside `shot.action` | Research says props deserve explicit physical specification |
| **Camera move per shot** | `shot.camera_move` | Chosen *within* the camera law (§1.2) |
| **Shot size / angle** | `shot.shot_size`, `shot.camera_angle` | ECU…WS/OTS · eye-level/low/high/dutch/POV |
| **Blocking / gaze / expression** | `shot.*` | The director layer |
| **Cast present** | derived per segment | Presence-based reference attachment |
| **Wardrobe deltas** | *not modelled* | e.g. a coat for a winter episode — no mechanism today |

---

## 3 · THE GAPS (what is missing or contradictory — needs your decision)
1. **⛔ No style-lock plate exists.** The C1 exit checklist required a locked style reference image; `refs_manifest` still emits `style → pending — C1 style-lock` and skill-3 still binds a nonexistent `@Image` style slot. **The global look currently has no visual anchor at all.**
2. **⛔ No COLOR LAW.** The original style-system spec demanded one (background palette family + each character's accent colour popping against it). `canon_blocks` has **no colour/palette section** — so every episode invents its own grade. *This is the biggest single cause of episode-to-episode look drift.*
3. **⚠ Lighting has a hole, not a rule.** Hardcoded lighting was deliberately removed (correctly — it broke outdoor scenes), but nothing replaced it as a *rule*; it is now 100% improvised per episode. The research's answer: express lighting as **ratios and named sources**, not moods ("85:15 dark-to-light", "warm yellow from the lamps only") — a rule that adapts to any environment while staying recognisable.
4. **⚠ `global_aesthetic_rules` competes with the STYLE_BLOCK.** Your 07-28 field is written **per episode by the model** — meaning the *universal* look is being re-invented every run. It should be a constant that the treatment supplies, not an LLM output.
5. **⛔ No location/environment plates.** Recurring locations have no locked reference (invideo locks these alongside cast).
6. **⚠ The UI storyboard path never substitutes `{{CANON_BLOCKS}}`** (`app.py`), so from the studio the style clause is improvised even though skill-2b orders a mechanical merge.
7. **⚠ C1 win condition never run** — "generate the same character twice from canon alone; both recognisably identical" has never been tested. This is the cheapest possible proof the identity system works.
8. **Minor tensions:** Kati's "zero specular body" vs "pristine glossy white boots" (deliberate, but should be stated as an explicit exception) · Bert's grey **felt** hat vs the AVOID-list ban on "felt" (a real latent-space risk — needs rewording, e.g. "brushed wool-textured hat").

---

## 4 · What this means for the Treatment
The Treatment document = **§1 (universal) written as enforceable rules**, with §3's gaps filled — specifically a **colour law**, a **lighting law expressed as ratios/sources**, an **exceptions section** (Kati's polish, Bert's minimum identity), and a **quick-reference card**. §2 stays variable and is supplied by you per episode through the storyboard conversation. Once the Treatment exists, `global_aesthetic_rules` is deleted from the screenplay schema (the treatment replaces it), and every visual stage reads the treatment instead of improvising.

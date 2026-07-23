# RESEARCH — Storyboard Stage Design (screenplay → storyboard frames → Seedance)

> **Source:** Deep-research result supplied by Jayon (2026-07-22), "Architectural Blueprint for the Storyboard Stage", from `DEEP_RESEARCH_PROMPT_storyboard_stage.md`. Faithful archive (citation noise stripped).
> **Status:** Evidence library — the blueprint for **Phase 4 (storyboard)** + the screenplay-schema enrichment it implies. Companions: `RESEARCH_v3_tech_derisk_seedance_and_storyboard.md`, `RESEARCH_shortform_pedagogy_framework.md`.
> **Headline recommendation:** **GPT Image 2** as the storyboard engine (≈99% text accuracy — critical for German spelling; up to 8 consistent images/prompt; neutral color = less grading). Nano Banana Pro is the strong alternative (14 refs, thinking pass, native umlauts/ß, web grounding).

---

## 1. Storyboard image models (both do native 9:16)

| Metric | Nano Banana Pro (gemini-3-pro-image) | GPT Image 2 (gpt-image-2) |
|---|---|---|
| Reference images | **14** (560 tokens ea.) | **4** text-endpoint / **16** edit-endpoint |
| Consistency | up to 5 people; relationship-formula binding | up to **8 consistent images from one prompt**; autoregressive |
| Text-in-image | correct umlauts/ß, multiple fonts | **≈99% accuracy**, complex formatting |
| Color | Fujifilm warm science | **neutral, zero yellow cast** |
| 9:16 | native (10 ratios) | multiples-of-16 (e.g. 1088×1920) |
| Temp / params | 0.0–2.0 (storyboard sweet spot **0.4–0.6**), topP 0.95, topK 64 | `quality` low/med/high · `thinking` off/low/med/high |
| Cost / speed | ~$0.13/img output; 8–12s (thinking) | $0.005 (low) → $0.165 (high); 3s → up to 2 min |
| Edge | real-time web grounding | text accuracy + consistency + neutral color |

No numeric weight sliders on either — **weight is controlled semantically** (relationship instructions, "isolate facial geometry / hair / wardrobe from the sheet").

## 2. Screenplay → storyboard: the data boundary

**Two documents, clear responsibilities:**
- **Screenplay** = narrative + dialogue + pedagogical metadata (German vocab, translation, overlay type). *The creative/teaching layer.*
- **Storyboard Frame Schema** = enriches each shot with **camera work, composition, lighting, reference bindings** → the interface for both human review AND the video model.

**The `ScreenplayShot` fields the research specifies** (per shot):
- `shot_id` (e.g. `SC_01_SHOT_02`)
- `pedagogical_metadata`: `german_vocab`, `english_translation`, `visual_overlay_type` (CHALKBOARD | UI_CARD | SPEECH_BUBBLE | BURNED_SUBTITLE)
- `visual_attributes`: `shot_size` (ECU/CU/MCU/MS/MWS/WS/OTS), `camera_angle` (EYE_LEVEL/LOW/HIGH/DUTCH/POV), `lens_feel` (35mm/50mm/85mm/24mm), `composition_rule` (thirds/central/golden), `blocking_description` (positions in the 9:16 frame), `gaze_direction`, `lighting_setup`
- `cast[]`: `character_id`, `expression`, `wardrobe`
- `props[]`, `action_beat`, `dialogue{speaker_id, german_dialogue_text}`

> **Design note for us:** this is richer than our current shot (`beat / camera / on_screen_text / dialogue`). The enrichment is where the *filmmaker sensibility* lives — see the DESIGN decision in chat (director-layer in screenplay vs technical compilation in the storyboard skill).

## 3. The storyboard SKILL (LLM orchestrator)

Ingests a `ScreenplayShot` → emits an image-gen prompt in a **rigid template**:
```
[STYLE REFERENCE CODES] + [ENVIRONMENT & LIGHTING] + [CHARACTER IDENTITY COHERENCE]
+ [FRAMING & COMPOSITION] + [ON-SCREEN TEXT DESCRIPTORS] + [NEGATIVE CONSTRAINTS]
```
Rules: map `character_id` → `@Image1/@Image2` (multi-angle sheets); style plate = `@Image0`; on-screen German text in **double quotes** with explicit layout/placement/color; explicit gaze + blocking + hand positions; always append negatives.

**Consistency tactics:**
- **Seed locking** — first panel of a segment gets a random seed; once approved, lock it and reuse for all panels in that scene.
- **Prompt mirroring** — style clauses (lens, camera body, color grade, grain) identical across every panel in a segment.
- **Reference re-injection** — extract the first panel's background plate, re-inject into later panels for environmental consistency.
- **Negative prompt (standard):** `avoid double limbs, mutated hands, blurred facial features, letter mutation, background warping, perspective distortion, yellow color casts`.

**Density:** **3 panels per 15s clip → 6–9 panels per video** (a shot change every ~5s).
**Single-frame fix:** re-generate one failed panel via the **edit endpoint + a binary mask** over the error region ("change 'Deustch' → 'Deutsch'"), preserving identity + background.

## 4. Storyboard → Seedance handoff

**@Image budget for Seedance 2.0 (9-image cap) — the research's allocation:**
| Slot | Content | Role |
|---|---|---|
| @Image1 | global style plate | color/lighting/art style |
| @Image2 | Character A multi-angle sheet | identity A |
| @Image3 | Character B portrait | identity B |
| @Image4–6 | **storyboard panels 1–3** | shot layouts / latent init + cross-attention |
| @Image7 | subtitle card | text overlay |
| @Image8 | vocabulary graphic | on-screen graphic |
| @Image9 | background plate | environment/depth |

**Composed panels vs style plates:** **fully-composed panels** (characters + props + background pre-assembled) = strict layout control, best for text placement + interactions (recommended). Separate plates = more dynamic motion but more drift.

**Endpoint:** **reference-to-video** (multi-ref, multi-shot, lip-sync) is the narrative choice; image-to-video (single image) is for simple motion only.

**Multi-shot prompt shape** (cuts inside one clip):
```
Shot 1: @Image4 … says: "Wie geht es dir heute?". Camera: slow push-in, locked-off.
Cut scene to Shot 2: @Image5, close-up … says: "Mir geht es gut!". Camera: medium, tripod stable.
Cut scene to Shot 3: @Image6, medium two-shot. Sound: soft room tone.
```
Dialogue in double quotes → Seedance aligns phonemes to `@Audio1` for lip-sync. **Camera syntax:** `Camera: [move] + [pacing] + [subject_lock] + [stability]`, compound moves joined by "then"; natural speed words only (slow/gentle/gradual) — no `f/2.8`, no `24fps`.

## 5. Full-chain consistency (the real risk)

Image model and video model **don't share a latent space** → panels are exported as PNGs and re-compressed by Seedance → **visual drift** over 10–15s ("copy-of-a-copy" cascade; high-frequency detail/text muddies on camera moves).
- **Same-lab (Seedream → Seedance) drifts less** than **cross-lab (GPT Image 2 / Nano Banana → Seedance)**.
- **Anti-drift:** Seedance 2.5's persistent latent propagation + restorative flow matching; **visual-matching framing** (panel framing must match the clip's portrait framing); normalized LUT/upscale pass in post.

## 6. ⚠ Version flag — Seedance 2.0 vs 2.5

This research repeatedly references **Seedance 2.5** (persistent latent propagation, restorative flow matching, multi-shot anchor sequencing, 30s continuous 4K) and its example code calls `bytedance/seedance-2.5/reference-to-video`. **Our canon + earlier de-risk locked Seedance 2.0** as the live fal model. **This discrepancy MUST be verified against fal.ai's current model list before building** — if 2.5 is live, its anti-drift + native multi-shot materially improves our chain (and re-opens the canon naming).

## 7. Model selection + end-to-end (research's recommendation)
**GPT Image 2 primary** → generate 9:16 composed panels → hand panels + style + character sheets (+ voice) to **Seedance reference-to-video** → 15s clip with native lip-sync. The research includes a full `fal_client` Python reference implementation (GPT Image 2 edit endpoint → Seedance 2.5 reference-to-video) — see the source doc.

## 8. Sources (key)
fal.ai model pages (Seedance 2.0 reference-to-video / image-to-video / text-to-video; GPT Image 2 + /edit; "What is Seedance 2.5"); Google AI (Gemini 3 Pro Image, prompting guide); Picsart/Luma/Apidog (GPT Image 2); PromeAI + BytePlus + apiyi (Seedance camera syntax); arXiv EverAnimate (latent flow restoration); story-shot-agent (screenplay→shot→prompt agent, LangGraph).

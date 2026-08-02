# Prompting Guidelines — Nano Banana Pro (Gemini 3 Pro Image)

> version: 1.0 · canon file · 2026-08-02
> The **image-model** engine documentation: storyboard-sheet generation + iteration. Companion to `prompting_guidelines_seedance.md` (video) — same shape, same purpose. Basis: `resources/Production Prompting Manual for Gemini 3 Pro.md` (2026-08 deep research). Read by the Vision phase (sheet compiler + board iteration); answers `DESIGN_board_iteration.md` §6.

## 1. Prompt structure (strict order — TREATMENT §15)

`[Reference binding] → [Sheet format + style clause] → [Environment + per-panel coordinate blocking] → [Constraints block]`

## 2. Identity binding — the TOKEN law

- Bind identity by **index → token**: *"Using the attached Image [0] strictly as the sole visual identity anchor for the facial geometry, textures and wardrobe of 'Character-Rolf' …"*
- **Image-prompt tokens, always:** `Character-Rolf · Character-Bert · Character-Kati · Character-Mueller`. The full canonical names contain German **common nouns** (*die Wurst, das Bier, das Brot, die Kartoffel*) that pull generic training imagery into the render and dilute identity. This is the naming law's one fenced exception (`SHOW_BIBLE` §13, `TREATMENT` §9.4); everywhere outside image prompts the full names stand.
- **Never describe what a reference image contains** — no wardrobe restating, no "the young woman". Prose descriptions compete with the vision encoder and cause drift. The index binding carries identity; the material laws (`TREATMENT` §10) are the only sanctioned descriptive text, verbatim, when text is required at all.
- **Two+ characters — spatial isolation clause, verbatim shape:** *"Character-A (Image [0]) and Character-B (Image [1]) are physically separated in space. Render each strictly with their own referenced features and wardrobe in all panels. Attribute mixing or visual crossovers between the two characters is strictly prohibited."*
- Face references below **512 px** cause face morphing — attach full-resolution sheets only.

## 3. Reference slots + ordering (hard limits)

- **14 refs max**, routed through typed slots: **5 HUMAN** (character identity) · **6 OBJECT** (props, wardrobe items, location plates) · **3 STYLE** (grade, grain, lighting physics).
- **Attention weights bias to the earliest indices** → characters occupy indices 0–3; style references go **LAST**.
- Budget (= `TREATMENT` §9.2–9.3): Char A sheet+portrait · Char B sheet+portrait (**4 of 5 human**) · close-up only when one character carries the scene · location plate (object slot) · previous-segment sheet + style plate at the **end** (≤3 style). A rare third cameo = portrait only. **The human-slot ceiling, not the total 14, is the binding limit.**

## 4. Sheet geometry (the slicing contract)

- 3 × 9:16 panels = ONE **16:9 sheet at 2K (2048×1152)**, separated by *"solid, clean, 20px wide, non-diegetic white gutters"* — say exactly that; **"non-diegetic"** is what stops gutters rendering as physical pillars.
- **Slice offsets** (2048 px canvas, 20 px gutters): P1 `(0, 0, 656, 1152)` · P2 `(676, 0, 1332, 1152)` · P3 `(1352, 0, 2008, 1152)` → ~656 px per panel, above the face threshold. **Never generate sheets at 1K** (≈341 px panels → facial melting).
- **Panel capacity law:** 3 panels optimal · 4 marginal (faces soften — consider 21:9 or 4K) · **5+ unstable** (gutter collapse, artifacts). A segment with ≥5 shots gets **two chained sheets** — the sheet splits, the story never does (`TREATMENT` §15 / BUILD_PLAN D4).
- **Per-panel spec:** sequential narrative mapped to named positions with distinct framing — *"Panel 1 (Left): CU, Character-X …"* — and demand *"each panel must utilize a completely distinct camera framing"* (kills composition mirroring).
- **No text anywhere on the sheet** — no gutter labels, no shot numbers. Panel order is positional.

## 5. Iteration — the Vision phase's edit grammar

- Edits are **maskless, semantic, conversational** (edit endpoint). Frame EVERY edit as **Lock–Change–Constraint**:
  1. **LOCK** — name the panels + identities that stay identical ("Keep Panels 1 and 2 completely identical; lock all facial structures").
  2. **CHANGE** — the ONE modification, located ("In Panel 3, change only the background to …").
  3. **CONSTRAINT** — secondary effects controlled ("Adjust ambient light to match; do not alter facial structure, pose, grading").
- **Edit vs regenerate — the decision metric:** `M = (panels needing structural change ÷ total panels) + identity_drifted(0|1) + layout_degraded(0|1)`. **M ≥ 0.66 → regenerate the whole sheet from raw references**; otherwise edit in place. Never accumulate many small edits — composition decays.
- **Continuity chaining:** the previous sheet may be re-attached **as a low-weight STYLE reference only**; identity always grounds in the **raw character sheets**. **Photocopy degradation:** never chain generated→generated more than **3 deep** — contrast compression and facial drift accumulate per loop.
- **Native API only:** echo the returned `thoughtSignature` back in the next turn for compositional locking across edit turns. fal does not expose it.

## 6. Determinism & parameters

- **Non-deterministic.** `seed` is best-effort; identical inputs give similar, not identical, output. Reproducibility comes from references + prompt discipline, never from seeds.
- **Temperature stays 1.0.** Lowering it breaks spatial-layout reasoning → compositional errors, looping artifacts, flat synthetic lighting.
- Parameters (fal names): `aspect_ratio` `16:9` (sheet) / `9:16` (single panel) · `resolution` **"2K"** (4K = 2× rate) · `num_images` 1 · `output_format` png · `safety_tolerance` 4 (escalate to 5–6 when cinematic terms trigger false blocks) · `enable_web_search` false.
- **Native Google differs:** `image_size` (not `resolution`) · per-input `media_resolution` · `thinking_level` · `thoughtSignature`. **Prefer native for iteration work**; fal locks max-thinking (10–20 s) and hides the stateful controls.

## 7. Prohibitions = constraints block (there is NO negative prompt)

- No negative-prompt channel exists. **Never write "no mutated hands, no extra limbs, no blurred faces"** — the planner processes the named concepts and renders them.
- End every prompt with a positive **"Constraints and Prohibitions:"** block: frame entirely clear of overlays/watermarks/text · all figures with physically accurate anatomy, **exactly five fingers per hand** · no duplicate or mirrored characters within a panel · backgrounds sharp, free of unnatural blur.
- `TREATMENT` §14's permanent negative list is **video-stage (Seedance) language**; for NBP, translate its intents into constraints-block phrasing.

## 8. Style control

- **Hybrid lock:** style reference image(s) at the END of the array **+** the fixed text style clause (assembled from `TREATMENT` §1–§3, never improvised). Style slots are processed separately and do not compete with character slots.
- **Technical vocabulary only** — named lens + f-stop, film stock, named light source + ratio (`TREATMENT` §5). Generic hype words ("cinematic", "stunning", "hyper-detailed") degrade composition and drag toward generic-AI style.

## 9. Failure modes → fixes

| Failure | Fix |
|---|---|
| Grid collapse (panels merge; gutters become walls) | "divided strictly into three non-overlapping 9:16 vertical boxes separated by 20px non-diegetic solid white graphic borders" |
| Attribute swap between characters | unique `Character-X` tokens bound to indices; no generic nouns; the spatial-isolation clause (§2) |
| Composition mirroring across panels | distinct framing + distinct action stated per panel (§4) |
| Facial melting in wide/multi-panel shots | 2K+ resolution; "captured on an 85mm portrait lens, sharp focal plane alignment" |
| False safety block on cinematic terms | raise `safety_tolerance` to 5–6; neutralize dramatic wording |

## 10. DON'Ts

- ❌ Full canonical character names inside image prompts (the token law, §2)
- ❌ Describing a reference image's content in prose
- ❌ Negative-prompt phrasing (§7)
- ❌ Temperature below 1.0
- ❌ 1K sheets · ❌ five or more panels in one sheet
- ❌ Generated images as **identity** references (style-continuity only, ≤3 deep)
- ❌ Any text on the sheet — gutter labels included
- ❌ Puppet / claymation / stop-motion / miniature / felt vocabulary (Live-Action Integration Rule, `TREATMENT` §1)

# Research: Art-Style System for an Automated Video Pipeline

**Date:** 2026-07-15 · **Question (Jayon):** what must the style system contain so that a fully automated pipeline produces ONE recognizable look across changing stories/environments — including the puppet×real hybrid ("wait, is this real?") aesthetic, deliberate imperfections, and honest disclosure?

---

## 1. The core mechanism: a verbatim Style Block, never paraphrased

The consistent finding across creator practice: consistency comes from a **fixed "style DNA" text block pasted IDENTICALLY into every single prompt** — never rewritten, never paraphrased, not even synonym swaps. The prompt is split into CONSTANT parts (style block + character block) and VARIABLE parts (action + setting); only the variable parts change per scene ([character-consistency workflow](https://www.neolemon.com/blog/kling-ai-grok-ai-character-consistency-tips/), [consistent-character prompt libraries](https://ampifire.com/blog/ampcast-video-generator-prompt-library/), [Artlist pro workflow](https://artlist.io/blog/consistent-character-ai/)). Professional 2026 pipelines operationalize exactly our architecture: brief → beat sheet → shot list → prompts, with persistent style bibles injected as context at the prompt-writing stage ([2026 cinematic playbook](https://www.truefan.ai/blogs/cinematic-ai-video-prompts-2026)).

**Engineering rule this creates for our C2 prompt-writer stage:** the LLM never *writes* style or character text — it writes only ACTION + SETTING, and the pipeline **mechanically concatenates** the canon style block + the relevant character blocks from the repo. Style consistency becomes a code guarantee, not an LLM behavior we hope for.

## 2. What `resources/STYLE_SYSTEM.md` must contain (the deliverable spec)

1. **Medium statement** (1 sentence): e.g. "photographed handcrafted puppets on miniature sets" — the single most important line; it declares what the images ARE.
2. **Material law:** per-zone material vocabulary (real bread crumb, salami marbling, glass, felt, wool) + the matte rule for organic surfaces (gloss = the #1 CG tell).
3. **Lighting law:** one lighting philosophy everywhere (e.g. soft practical studio light / warm tungsten miniature-set light). Lighting is the strongest subconscious "same show" signal.
4. **Camera law:** lens feel (e.g. 35mm, shallow depth-of-field at puppet scale = the "miniature" tell), eye-level framing, mostly locked-off or slow moves (puppetry doesn't do drone shots — restraint IS the style).
5. **Color law:** background palette family + the rule that each character's accent color must pop against it.
6. **World rule:** environments may change freely BUT are always rendered as the same physical reality (miniature set / real location at puppet scale) — this is what lets "backgrounds change, style holds."
7. **Imperfection law (Jayon's instinct, confirmed by practice):** deliberately specified handmade flaws — visible seams, fabric fuzz, fingerprint-scale texture, slight set wobble, dust — are exactly how creators avoid the too-clean CG look ([AI stop-motion technique guide](https://soprompts.com/wiki/stop-motion)). Imperfections are written INTO the style block, so even automated output reads handcrafted.
8. **AVOID list:** glossy/waxy surfaces, smooth CG interpolation, hyperreal humans, floating objects, brand logos, text unless quoted.
9. **THE STYLE BLOCK:** the final ≤80-word paste-ready paragraph distilling 1–8, plus (optional) 2–3 named shot-modifiers ("close-up", "wide establishing"). This paragraph is the product of the whole document — everything else exists to justify and regenerate it.

## 3. The puppet × real hybrid ("is this real?") — why it works and how

- **Why it works:** viewers' AI-detectors are calibrated to smooth CG and uncanny humans. Tactile handmade aesthetics — felt, clay, fabric, real-material puppets — sit in a blind spot: real needle-felt stop-motion communities and AI imitations are already genuinely hard to tell apart ([AI stop-motion overview](https://soprompts.com/wiki/stop-motion), [puppets & AI](https://reelmind.ai/blog/film-puppets-ai-stop-motion-animation-with-ai)). The doubt ("is that a real puppet??") is itself engagement — comments arguing about it feed the algorithm.
- **How:** (a) extreme material specificity in the style block; (b) the imperfection law; (c) *scale honesty* — puppets photographed at puppet scale (shallow DOF, miniature sets) even when the "set" is a real Berlin street; (d) optionally a stop-motion cadence (slightly stepped motion) as a series signature — worth testing in C3; (e) occasional REAL footage backgrounds with the puppet composited at correct scale = the reality-blend moments Jayon described.
- **Fits the cast as-built:** all four references already read as photographed physical puppets — the style system codifies what the images already are.

## 4. Honesty & disclosure (Jayon's constraint: "don't cheat people")

Position, don't confess: the brand is literally **"AI-made, with intention"** — put it in the bio ("KI-gemacht, mit Liebe" or similar), use Instagram's AI-content label where applicable (Meta auto-labels + requires disclosure for realistic AI media; EU transparency rules are tightening in this direction). The "is it real?" game stays fun precisely because the answer is one tap away — mystery in the craft, honesty in the profile. This also inoculates against "you tricked us" backlash cycles that hit undisclosed AI accounts.

## 5. C1 win condition — defined (Jayon asked)

**What it is:** *Generate a brand-new scene image of each character (new pose, new setting, using only the canon: bible text + reference images + style block) — twice, independently. Both outputs must be recognizably the SAME character in the SAME show, per Jayon's eye.*

**Why this matters:** it is the smallest possible test of the thing the whole MVP must prove — **repeatability**. The hero images prove the characters exist once; the pipeline needs them to exist *on demand, every day, in scenes nobody hand-crafted*. If a character can't be reproduced twice deliberately from canon assets, no amount of automation downstream can hold them across 10 scenes/day — we'd be automating drift (risk R1). Passing it converts the cast from "nice images" into a **reusable production asset**, and it directly gates C3 (no video money until identity reproduces). It also stress-tests the canon itself: whatever drifts in the two generations tells us which sentence of the bible/style block needs strengthening — the cheapest possible place to learn that.

**C1 exit checklist:** canon names ✅ (2026-07-15) · image text fixes (Jayon, in progress) · STYLE_SYSTEM.md written & locked (Jayon drafting, per §2 spec) · turnaround coverage verified (sheets exist; check back views) · win-condition run passed → then C2.

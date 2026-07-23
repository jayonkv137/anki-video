# Deep-Research Prompt — The Storyboard Stage (screenplay → storyboard frames → Seedance)

> **Purpose:** paste the block below into Gemini Deep Research. It researches the storyboard stage: how to generate consistent storyboard frames with **Nano Banana Pro** and **GPT Image 2**, what the screenplay must carry to feed them, how to write the storyboard skill, and — critically — the **best format to hand storyboard frames to Seedance 2.0 reference-to-video** so the video output is best.
> **Created:** 2026-07-22, for Jayon. Feeds Phase 4 (storyboard) + possible screenplay-schema tweaks.

---

## THE PROMPT (copy from here) ⬇

You are a senior research analyst specializing in **generative visual pipelines and AI video (2026 state of the art)**. Produce a comprehensive, citation-backed report to help me design ONE stage of a content pipeline: the **storyboard stage**, which sits between a written screenplay and AI video generation.

**What I'm building (context):** short-form (30–45s, 9:16 vertical) German-learning videos with a fixed cast of recurring photorealistic characters. My pipeline is: screenplay → **STORYBOARD (generate keyframe images)** → **Seedance 2.0 video**. Key facts:
- A **screenplay** is structured as **2–3 segments (~15s each); each segment is ONE Seedance clip built from multiple shots** (shot-reverse-shot / cut-ins within one generation).
- I already have, per character, **reference images** (a multi-angle character sheet + a portrait). I will also have **one style reference image**. There is a **per-character voice reference** (audio) too.
- The video model is **Seedance 2.0 `reference-to-video`** (ByteDance, on fal.ai): accepts **≤9 images** (referenced `@Image1…`), **≤3 audio** (`@Audio`, ≤15s), **duration 4–15s**, **9:16**, and natively does **multi-shot in one generation**. (There may also be a Seedance 2.5 — confirm and cover it if it exists.)
- The storyboard frames I generate should serve a **DUAL role**: (1) a human review gate, AND (2) the actual **`@Image` visual anchors fed into Seedance** to drive the clip. So the storyboard model choice and frame format matter *technically*, not just for review.
- The two candidate storyboard image models are **Nano Banana Pro** (Google, `gemini-3-pro-image`) and **GPT Image 2** (OpenAI).

**Research these questions in depth, each as its own section:**

1. **Consistent image generation — Nano Banana Pro AND GPT Image 2 (cover both separately).** For each model: the best strategy to produce **character-consistent + style-consistent** frames across a *sequence* of shots, given multiple reference images (character sheet + portrait per character, plus a style reference). Cover: how many reference images it accepts and how it weights/blends them; prompt structure to lock identity; techniques to hold a character consistent across different poses/angles/expressions/frames; how to apply a **style reference**; multi-character framing (2 characters in one frame); in-image text handling; controlling **9:16 aspect + resolution**; key parameters/settings; documented failure modes and fixes; batch cost & speed.

2. **Screenplay → storyboard: what the screenplay must specify.** Enumerate what a storyboard frame needs to be well-generated and useful: **shot size, camera angle/height, lens/focal feel, composition & framing, character blocking/positions, gaze/expression, key props, lighting/mood, the single action beat.** For each, state whether it should be **decided in the SCREENPLAY** (so the storyboard skill receives it) or **decided by the storyboard skill**. Then recommend the **exact fields a screenplay "shot" object should carry** to feed a strong storyboard prompt.

3. **The storyboard SKILL (LLM prompt design).** How to design an LLM skill that converts a screenplay (segments → shots) into **per-frame image-generation prompts** for Nano Banana Pro / GPT Image 2: the per-shot prompt template; how to bind the **character + style references**; consistency techniques (seed reuse, reference re-injection, "prompt mirroring" of identical character descriptions, negative prompts); **how many frames per shot/segment**; batching, iteration and regeneration of a single failed frame without breaking sequence continuity.

4. **Storyboard → Seedance handoff (THE CRITICAL QUESTION).** The **best format to feed storyboard frames into Seedance 2.0 (and 2.5 if it exists) `reference-to-video`** for the best video output. Resolve concretely: keyframe strategy — **start-frame only, start+end frames (image-to-video), or one anchor per shot?** How many storyboard frames per **15s multi-shot** clip, and how to reference them (`@ImageN`) alongside the character-sheet/portrait/style/voice refs (within the ≤9-image budget)? Should a storyboard frame be a **fully-composed scene** or a **character-on-style plate**? How does a frame's **camera/composition transfer into the generated motion**? How should the Seedance **text prompt** be phrased so the clip follows the storyboard frames **shot-by-shot**? Explicitly weigh **`reference-to-video` (many refs) vs `image-to-video` (start/end keyframes)** for storyboard-driven generation, and whether to generate **one Seedance clip per shot vs one per segment (multi-shot)**. Give a recommended prompt + reference-binding structure.

5. **Full-chain consistency & latent transfer.** Maintaining character identity + style through the whole chain: **reference image → storyboard frame → Seedance clip.** Does a Nano Banana Pro / GPT Image 2 frame **transfer faithfully into Seedance's latent space** (same-lab vs cross-lab effects — e.g. ByteDance Seedream→Seedance vs Google/OpenAI→Seedance)? Concrete anti-drift techniques across the chain.

6. **Recommendation.** For MY exact use — storyboard frames that both gate human review AND anchor Seedance — **which model (Nano Banana Pro vs GPT Image 2)** and what **end-to-end workflow**, including the concrete storyboard-skill output format and the storyboard→Seedance handoff format.

**Deliverable format:** (a) executive summary + the recommended end-to-end storyboard workflow (diagram if useful); (b) a per-model prompting + reference-conditioning **playbook** for Nano Banana Pro and GPT Image 2; (c) the recommended **screenplay "shot" fields** + a **storyboard-frame schema**; (d) the **storyboard→Seedance handoff format** (frames per clip, `@Image` binding within the ≤9 budget, prompt structure), with the reference-to-video vs image-to-video tradeoff explicitly resolved; (e) full-chain consistency / anti-drift techniques; (f) an annotated source list; (g) pitfalls to design against. **Prioritize specific, current (2026), implementable guidance with citations over generic overviews.** Where Seedance 2.0/2.5, Nano Banana Pro, or GPT Image 2 specifics are uncertain, say so and cite the most authoritative available source (fal.ai API docs, ByteDance, Google, OpenAI).

## ⬆ (copy to here)

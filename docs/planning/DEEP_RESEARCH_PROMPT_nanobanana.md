# Deep-Research Prompt — Nano Banana Pro: storyboard generation and iterative refinement

> **Purpose:** paste the block below into a deep-research tool. We have a canon prompting guide for our **video** model but **none for our image model**. This research produces it — and answers the specific question of how to *iterate* on an already-generated storyboard sheet without breaking character consistency.
> **Created:** 2026-07-29. Feeds `prompting_guidelines_nanobanana.md` (new canon file) and the Vision phase (`DESIGN_board_iteration.md` §6).
> **Note:** the equivalent document for our video model is `prompts/canon/prompting_guidelines_seedance.md` — same shape, same purpose. That is the target format.

---

## THE PROMPT (copy from here) ⬇

You are a senior technical researcher on generative image models. Produce a **practical, citation-backed prompting and iteration guide for Google's Nano Banana Pro** (the Gemini 3 Pro image model), written for a production pipeline — not a feature overview.

### What I use it for
I generate **storyboard sheets** for a serialized short-video series with a fixed cast of four recurring characters:
- Each generation produces **one image containing several 9:16 vertical panels side by side** (a filmstrip or grid), each panel being one shot of a scene. The whole sheet is generated **in a single pass** specifically so the characters, wardrobe, lighting and colour stay identical across the panels.
- Character identity comes from **locked reference images** — a multi-angle character sheet plus a portrait per character (no fine-tuning, no LoRA).
- The sheet is then **sliced back into individual panels**, and those panels are fed to a **video model as visual references** for generating the actual clips.
- Consistency across ~170 episodes matters more than any single beautiful image.

### Research these, in order of importance

**1 · Reference conditioning and identity.** How many reference images does it accept, and how are they weighted? What is the most reliable prompt structure for binding a specific reference to a specific character *when two or more characters appear in one image*? How do you stop attribute blending between two characters? Does the order in which references are attached matter? How should reference images be described in the prompt — or should they not be described at all? What breaks identity?

**2 · Multi-panel sheets.** Best practice for generating a single image containing several distinct panels: how to specify layout reliably, keep every panel the same size, get clean gutters, and stop content bleeding between panels. How many panels before quality degrades? How do you keep a character identical *across panels within one image*? Any known failure modes specific to grids/filmstrips.

**3 · ITERATION — the critical question.** Given a sheet that is already generated and mostly right:
- Can it perform a **targeted edit on one region or one panel** while leaving the rest untouched? How, exactly — what is the mechanism (edit endpoint, mask, inpainting, conversational refinement)?
- Does an **edit preserve character identity** as reliably as a fresh generation with references, or does it degrade?
- What is the correct prompt phrasing for *"keep everything identical, change only X"*?
- Is there **seed control or any reproducibility** guarantee? If I regenerate with identical inputs, how close is the result?
- When is it better to **regenerate the whole sheet** versus edit in place? Give a decision rule.
- Can I feed a **previously generated image back in as a reference** to continue a series (e.g. the previous scene's sheet, for continuity)? How well does that hold?

**4 · Style and look control.** How to apply a consistent visual style across hundreds of generations — a style reference image, a fixed style clause, or both? Does a style reference compete with character references, and how is that balanced? How are lighting and colour instructions best expressed for this model specifically?

**5 · Aspect ratio, resolution, output.** Supported aspect ratios and how they're specified; the practical maximum resolution; whether an unusual sheet ratio (e.g. three 9:16 panels side by side) is handled well or should be approximated.

**6 · Negative instruction.** Does it support negative prompts, and if not, what is the correct way to express prohibitions? What actually works to suppress common artifacts (extra limbs, mutated hands, blurred faces, text appearing in frame)?

**7 · Parameters, cost and limits.** Every meaningful generation parameter and its effect. Cost per image, latency, rate limits. Any differences between calling it directly via Google versus through an aggregator (we use fal.ai) — including whether parameter names or supported values differ.

**8 · Failure modes and fixes.** The documented ways it goes wrong, with the mitigation for each — especially anything relevant to multi-character, multi-panel, or long-series work.

**9 · Comparison, briefly.** Where GPT Image 2 or Seedream would do this job better, so I know when to route elsewhere. (We chose Nano Banana Pro primarily for its reference capacity and identity handling; I want to know if that's still the right call.)

### Deliverable
A **practical guide I can hand to an engineer**: the recommended prompt structure with a worked example for a two-character multi-panel sheet · a decision rule for edit-versus-regenerate · the parameter table · a negative/prohibition strategy · failure modes with fixes · and a one-page quick reference. Prefer current (2026) primary sources — Google's model documentation and prompting guide, fal.ai's API schema, and hands-on production reports — over feature listicles. **Where behaviour is undocumented, say so explicitly rather than guessing**, and mark what would need to be established by testing.

## ⬆ (copy to here)

# Research: Google Flow — capabilities, API reality, and its place in our pipeline

**Date:** 2026-07-17 · **Trigger:** Jayon rebuilt the full cast inside Flow (characters + bibles pasted + voices assigned + auto-generated expression/turnaround sheets) and asks: can Flow BE the pipeline's video layer?

---

## 1. What Flow is (July 2026)

Google's unified AI filmmaking workspace (merged Whisk + ImageFX + Flow, Feb 2026): **Ingredients** (reusable characters with consistent visual AND vocal identity — exactly what Jayon set up), **SceneBuilder** (timeline editor: arrange/extend/connect clips into scenes), **Camera controls**, and since I/O 2026 the **Flow Agent** — multi-step conversational creation: batch scene variations, plot/dialogue suggestions, iterative editing in one session, with a **"Confirm before generating" setting (Always/Never)** — literally our Gate 1 philosophy built into the app. Models inside: Veo 3.1 (Lite/Fast/Quality), Gemini **Omni Flash**, Nano Banana 2 (images), Imagen, Gemini for language. Native 48kHz audio incl. dialogue. Sources: [Google's Flow announcement](https://blog.google/innovation-and-ai/products/google-flow-veo-ai-filmmaking-tool/), [2026 complete guide](https://whiskailabs.net/google-flow-ai-complete-guide/), [Omni Flash editing tutorial](https://www.mindstudio.ai/blog/how-to-use-google-flow-gemini-omni-video-editing).

## 2. The decisive fact: NO public API

**Flow itself cannot be automated.** There is no official Flow API — it's a web app driven by humans ([confirmed](https://linkgo.dev/faq/there-an-api-for-google-flow-and-it-be-integrated)). Programmatic access to the SAME models goes through the **Gemini API / Vertex AI** — a separate product with separate billing: Flow credits (subscription) and API dollars don't transfer ([pricing breakdown](https://diyai.io/ai-tools/video-generation/google-veo-pricing/), [credit system explained](https://www.aifeaturedrop.com/2026/05/google-flow-and-veo-3-credits-explained.html)). An unofficial reverse-engineered "Flow API" exists (useapi.net) — **not recommended**: ToS violation, account-ban risk on the Google account that holds our characters.

**Consequence (the architecture answer):** Flow = the **manual creative cockpit**; the **automated pipeline calls the same models via Gemini API** (Veo 3.1 supports reference-image conditioning via API — the scriptable equivalent of Ingredients). Our n8n+API architecture remains the only automatable route — now validated rather than changed.

## 3. Where Flow fits our pipeline, stage by stage

| Pipeline stage | Flow's role | Verdict |
|---|---|---|
| Words (Supabase/n8n) | none | ours |
| Story LLM (word-constrained, A1/A2, bible-faithful) | Agent suggests generic plots — can't enforce our pedagogy/canon | **ours (Claude API)** |
| Screenplay + prompt-writer | manual conversational prompting only | **ours** |
| **Character lock (C1)** | **Ingredients + voices + auto expression/turnaround sheets — best-in-class, already done by Jayon** | **FLOW** |
| **Style/model prototyping (C3)** | **Perfect testbed: same models as our API shortlist, prepaid via Pro credits, confirm-each-generation ON** | **FLOW (manual)** |
| Scene generation (C4, automated) | no API | **Gemini API (Veo 3.1 + refs) via n8n** |
| Assembly | SceneBuilder (manual timeline) | Creatomate (automated) / SceneBuilder (mockups) |
| Publishing + Gate 2 | none | ours |

**Bonus discovered:** Flow already auto-produced expression sheets (STARE/FLIRTY/ALARM/SIDE-EYE) and 4-view turnarounds for Müller — Flow is the cheapest **C1 asset factory** (download everything into `resources/`).

## 4. The manual mockup protocol (Episode 0 — Jayon can do this TODAY)

1. In Flow: fix character names to canon first (currently "Rolf Die Würste", "Bert - Der Bier", "Kati Die kartoffel" — grammar violations of our own principle; rename to **Rolf die Wurst · Bert das Bier · Kati die Kartoffel · Müller das Brot**).
2. Take an existing B2 story (`output/stories/story_1-10.json`) — or generate a fresh 2-character one.
3. New Flow project → attach the 2 characters → Agent settings: Confirm=Always, x1 samples, video model = Omni Flash (cheapest) or Veo 3.1 Fast → feed scene-by-scene: style-block + visual description + dialogue line (colon trick: `Müller says: Moin.`).
4. Generate scenes 1–3 first; judge consistency ruthlessly before continuing; use SceneBuilder to stitch; export 9:16.
5. Log per-scene credit cost + retake count → this becomes our C3 data AND the first real "is 10 scenes coherent?" test (risk R2).

## 5. Competitors / alternatives compared

- **LTX Studio** ([platform](https://ltx.io/studio), [review](https://vidmuse.ai/blog/ltx-studio-review)): the closest "platform as base" — full script→storyboard→scenes→timeline production flow with persistent character profiles across projects. Same pattern though: the platform is manual; the **LTX-2.3 API** ([endpoints guide](https://wavespeed.ai/blog/posts/ltx-2-3-api-endpoints-guide/)) exposes the MODEL (already #1 on our C3 shortlist at $0.04/s), not the studio workflow. LTX Studio = strongest Flow alternative to evaluate in C3 if Flow disappoints.
- **Higgsfield**: preset-driven quick generation — wrong shape for serialized character stories.
- **Runway**: strong models/editor, weaker persistent-character workflow for our style.
- **NVIDIA** (Jayon asked): Omniverse/ACE is 3D-engine + avatar infrastructure — a different, far heavier paradigm (real 3D assets, rigging); not relevant at MVP scale.
- **Verdict:** nothing offers "story-in → consistent episode-out" as an API. The market splits into manual studios (Flow, LTX Studio) and model APIs (Gemini, fal.ai/LTX-2, Kling). Our pipeline = orchestrate model APIs; use studios as cockpits. **Plan unchanged, confidence increased.**

## 6. Getting maximum out of Flow (where to look)

- **Official:** [Flow announcement + guides](https://blog.google/innovation-and-ai/products/google-flow-veo-ai-filmmaking-tool/) · labs.google/flow Help Center · **Flow TV** (in-app gallery of community creations WITH their prompts visible — the single best learning resource: reverse-engineer what works).
- **Prompting:** [Google's Veo prompt guide](https://deepmind.google/models/veo/prompt-guide/) + [Veo 3.1 prompting playbook](https://cloud.google.com/blog/products/ai-machine-learning/ultimate-prompting-guide-for-veo-3-1) (dialogue colon-trick, camera vocabulary) — applies 1:1 inside Flow.
- **Deep dives:** [whiskailabs complete guide](https://whiskailabs.net/google-flow-ai-complete-guide/) · [SceneBuilder/Omni editing tutorial](https://www.mindstudio.ai/blog/how-to-use-google-flow-gemini-omni-video-editing) · Google Labs Discord + r/VeoAI for daily technique threads.
- **Credit hygiene:** x1 samples while exploring (x2+ doubles spend per prompt), Fast/Flash tiers for drafts, Quality only for approved finals; Ultra tier only if credits actually run out ([plan comparison](https://whiskailabs.net/google-flow-ai-pricing/)).

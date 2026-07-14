# Research: Video Generation for B3 — models, cost, ComfyUI, prior art, prompting

**Date:** 2026-07-14 · **Format researched:** 10 scenes × ~6s/day (~60s generated; finale stitched from same clips, no extra generation)
**Jayon's priorities:** cheap ▸ native video+audio ▸ good German. Deep-dive across current market, open-source, and community practice.

---

## 1. The market: models with NATIVE audio (video + sound in one pass)

| Model | Price (w/ audio) | Your 60s/day | Max clip | German dialogue? | Access |
|---|---|---|---|---|---|
| **LTX-2.3 Fast** | **$0.04/s @1080p** | **$2.40** | 20s (!) | Lip-synced speech native; language list unverified — TEST | [fal.ai](https://fal.ai/models/fal-ai/ltx-2/text-to-video/fast), [pricing](https://docs.ltx.io/pricing) |
| LTX-2.3 Pro | $0.06/s (i2v) – $0.08/s (t2v) | $3.60–4.80 | 20s | same | fal.ai |
| **Gemini Omni Flash** (preview since 2026-06-30) | ~$0.10/s (≈$1/10s clip) | ~$6 | 10s | Unverified — TEST | [Gemini API `gemini-omni-flash-preview`](https://coursiv.io/blog/gemini-omni-flash); resellers ~$0.112/s |
| **Kling 3.0 (Omni)** | ~$0.126–0.168/s | $7.60–10 | 10–15s | **Multilingual lip-sync since Feb 2026** (explicit list unconfirmed; HappyHorse-1.0 confirms German elsewhere) | fal.ai / Kling API |
| Veo 3.1 Fast | ~$0.15/s | $9 | 12s | Best-in-class 48kHz speech; German likely (Google) | Google Cloud |
| Veo 3.1 Standard | $0.40/s | $24 | 12s | same | Google Cloud |
| **Veo 3.1 Lite (NO audio)** | $0.05/s | $3.00 + TTS ≈ $3.20 | — | n/a — pair w/ ElevenLabs German TTS | Google Cloud |

⚠️ **Pricing conflicts exist between sources** (e.g. one lists Veo 3.1 at "$0.03/s" — likely a reseller loss-leader or error; Google-direct standard is $0.40/s). Resellers (Kie.ai, EvoLink, Atlas Cloud) undercut official rates; verify at signup before trusting any number here. Sources: [buildmvpfast July 2026](https://www.buildmvpfast.com/api-costs/ai-video), [Atlas Cloud comparison](https://www.atlascloud.ai/blog/guides/cheapest-ai-video-generation-api-2026), [WaveSpeed LTX-2.3 pricing](https://wavespeed.ai/blog/posts/ltx-2-3-pricing-api-cost-2026/), [3-way comparison](https://lushbinary.com/blog/ai-video-generation-sora-veo-kling-seedance-comparison/).

**The headline find — LTX-2:** Lightricks **open-sourced LTX-2 on Jan 6, 2026** — the first production-grade model generating video + synchronized stereo audio + **lip-synced speech in one pass**, up to 20s clips (longer than Veo/Sora/Kling), 14B video + 5B audio params ([the-decoder](https://the-decoder.com/lightricks-open-sources-ai-video-model-ltx-2-challenges-sora-and-veo/), [technical report](https://arxiv.org/html/2601.03233v1), [DigitalOcean guide](https://www.digitalocean.com/community/tutorials/ltx-2-video-generation-audio-video-model)). It is BOTH the cheapest hosted API (fal.ai $0.04/s) AND the open-weights model you could self-host later. One model serves both of Jayon's paths.

## 2. ComfyUI / self-hosting — honest verdict

- **Your Mac: no.** Open video models need 60–80GB VRAM full-precision (Wan needs ~60–70GB; [Spheron guide](https://www.spheron.network/blog/comfyui-gpu-cloud-2026/)); quantized LTX-2 (NVFP4, −60% VRAM) targets NVIDIA RTX — not Apple Silicon.
- **Cloud GPU math:** RTX 5090 rents at ~$0.50–0.76/hr ([Vast.ai/Spheron](https://www.spheron.network/blog/comfyui-gpu-cloud-2026/)), RunPod 4090 ~$0.39–0.74/hr ([RunPod review](https://wavespeed.ai/blog/posts/runpod-review-2026/)). Generating ~10×6s clips ≈ 30–60 GPU-minutes ≈ **$0.30–0.80/day** in pure GPU time — IF the pipeline never babysits.
- **The catch:** vs LTX-2.3 Fast API at $2.40/day, self-hosting saves **~$2/day** and costs: ComfyUI workflow setup, tens of GB of model downloads, cold starts, node/version breakage, and an orchestration layer to start/stop pods — a whole second infrastructure project. Hosted middle-grounds exist (RunComfy ~$2.34/hr, ComfyICU $0.50/hr — [comparison](https://www.aipromix.com/2026/04/comfyui-cloud-services.html)) but still add ops.
- **Verdict (unchanged from engineering spec, now with numbers):** NOT for MVP. The revisit triggers get sharper: (a) daily cost exceeds ~$5/day sustained, or (b) you need custom character-consistency control (LoRA training on Lena+Bruno) that APIs can't give. Since LTX-2 is open-weights, the migration path API→self-hosted is *the same model* — nothing learned is wasted.

## 3. Prior art — how others already built story→scenes pipelines

- **The keyframe-anchoring pattern (the industry's consistency answer):** LLM writes script → an **image model** (Nano Banana/Gemini) generates character **keyframes** for scene start/end → **image-to-video** fills motion between anchors. Same face across 100+ scenarios ([n8n storytelling deep-dive](https://medium.com/deep-tech-insights/automate-your-entire-video-pipeline-a-technical-deep-dive-into-a-custom-n8n-storytelling-workflow-4286201382dc)). Bonus: i2v is cheaper than t2v (LTX Pro: $0.06 vs $0.08/s). **This maps directly onto our fixed-duo design — generate ONE canonical Lena+Bruno reference set, reuse daily.**
- **Kling's Elements 3.0**: upload a reference video/photo of a character → model replicates it across scenes ([Kling guide](https://aitoolanalysis.com/kling-ai-complete-guide/)).
- **n8n community precedents:** [Fully Autonomous AI Animation Studio (character consistency + FFmpeg jitter solved)](https://community.n8n.io/t/fully-autonomous-ai-animation-studio-solving-character-consistency-ffmpeg-jitter/291814) — closest existing build to ours; [faceless-video template: Gemini + ElevenLabs + Leonardo + Shotstack](https://n8n.io/workflows/6014-create-faceless-videos-with-gemini-elevenlabs-leonardo-ai-and-shotstack/); [visual storytelling factory w/ human-in-the-loop](https://n8n.io/workflows/7951-visual-storytelling-content-factory-gemini-and-replicate-ai-with-human-in-the-loop-publishing/). Their cost tactics: still images + voiceover where motion isn't needed, template-based stitching (Creatomate/Shotstack — we already chose this), human review gates before spending on video.

## 4. Prompting for dialogue scenes (applies at B3 prototyping)

- **Exact speech:** Veo: `The parrot says: Elf! Es sind elf Brötchen!` (colon form prevents improvised lines — [Replicate Veo guide](https://replicate.com/blog/using-and-prompting-veo-3), [Google's prompt guide](https://deepmind.google/models/veo/prompt-guide/)). Kling: `Bruno says, "..."` with speaker/line/delivery kept adjacent ([Kling 3.0 prompt guide](https://klingaio.com/blogs/kling-3-prompt-guide)).
- **Keep spoken lines 3–5s** — long lines desync lips. Our 1–3 short sentences/scene fits.
- **Label speakers explicitly** in multi-character scenes or models mix up who talks.
- **Consistent style prefix** on every clip + image-to-video anchoring = the two consistency levers.
- Our `narration_de` + `visual_description_en` schema already separates these cleanly — the video prompt becomes: style prefix + visual description + spoken line.

## 5. Recommended B3 test protocol (Jayon executes, ~€10 budget)

Shortlist to try hands-on, cheapest-first, all against the SAME 2 scenes (one dialogue scene, one action scene, from a generated story):

1. **LTX-2.3 Fast via fal.ai** ($0.04/s) — the cost king; the critical unknown is German speech quality. If German passes YOUR ear, this wins on price ($2.40/day) and gives the open-weights escape hatch.
2. **Veo 3.1 Lite + ElevenLabs** (~$3.20/day) — the control option: silent video + separately generated slow German narration (no lip-sync risk at all; narrator style like Shaun-the-Sheep = characters don't need to speak on-screen). Pedagogically strongest (pace control).
3. **Gemini Omni Flash preview** (~$6/day) — Jayon's pick to explore: conversational editing + multimodal input; check German + API quota limits in preview.
4. **Kling 3.0 Omni** (~$8–10/day) — the consistency king with multi-shot storyboard + Elements; the benchmark to beat on character stability.

Judge on the locked criterion order: consistency > German narration quality/control > cost. Note the narrator-vs-lip-sync fork: if scenes are NARRATED (not spoken by characters on screen), the German-lip-sync question disappears entirely and option 2's architecture (or any model + TTS) becomes much safer — decide this during prototyping.

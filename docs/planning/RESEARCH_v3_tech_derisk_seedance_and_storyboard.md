# RESEARCH — V3 Tech De-Risk: Seedance Multi-Shot + Storyboard Image Model

> **Date:** 2026-07-22 · **Trigger:** V3 direction locked (`VISION_v3_universe_and_studio.md`); Jayon chose "de-risk the tech first." · **Method:** fal.ai API docs (authoritative) + ByteDance tech report + 2026 model comparisons.
> **Verdict: 🟢 GREEN — V3's core technical premise is validated.** Seedance really does multi-shot-in-one-prompt, up to 15s, 9:16, with reference images **and** our per-character voice refs. One residual risk (German voice fidelity) needs a single paid test that was already on the roadmap.

---

## 1. The question we were de-risking

V3 replaces "10 clips stitched" with "**2–3 Seedance clips of ~15s, each doing multiple shots in one prompt**." That only works if Seedance can actually: (a) do multi-shot in a single generation, (b) reach ~15s, (c) output 9:16, (d) accept our character/style **reference images**, and (e) accept our per-character **voice references** (Path A). If any failed, the whole V3 shape would change.

**All five hold.** Details below.

## 2. Seedance 2.0 on fal.ai — verified capabilities

> ⚠ **Naming correction:** our canon says "Seedance 2.5." The live model on fal is **Seedance 2.0** (ByteDance also shipped Seedream **image** models up to 5.0 Lite — easy to conflate). The `/tune` in §5 fixes this.

fal hosts several Seedance 2.0 routes. The one V3 needs is **`bytedance/seedance-2.0/reference-to-video`** (it's the only one taking *many* image refs **and** audio refs):

| Param | Type | Allowed / limit | V3 use |
|---|---|---|---|
| `prompt` | string | ≤3000 chars (canon cap holds) | multi-shot script; shots via prompt text ("Cut to…") |
| `image_urls` | list | **≤9 images**, JPEG/PNG/WebP, ≤30 MB ea., referenced `@Image1…` | **char sheet + portrait + style ref + storyboard frame(s)** |
| `audio_urls` | list | **≤3**, MP3/WAV, **≤15s combined**, `@Audio1…` | **our per-character voice refs (Path A) — works natively** |
| `video_urls` | list | ≤3, 2–15s combined | motion/camera transfer (optional) |
| `duration` | enum | **auto, 4–15s** | **15s per clip ✓** |
| `aspect_ratio` | enum | incl. **9:16** ✓ | vertical |
| `resolution` | enum | 480p/720p/**1080p**/4k (def 720p) | 720p→1080p |
| `generate_audio` | bool | default true | keep true so voice refs drive lip-sync |
| output | file | `video` url + `seed` | — |

**Multi-shot (the crux):** ByteDance's own tech report states Seedance "natively supports multi-shot video generation… shot-reverse-shot sequences, cut-ins, and match cuts while maintaining visual continuity across scene transitions, with characters staying consistent across different camera angles and time shifts." fal's `image-to-video` page phrases it as "natural cuts within a single generation, up to 15 seconds." **This is Seedance's headline strength, not a hoped-for edge case.**

**Alternative route** `bytedance/seedance-2.0/image-to-video` = classic keyframe anchoring (`image_url` + optional `end_image_url`, i.e. start/end frame) — but **only 2 images and NO voice-input parameter** ("audio generated automatically; no voice input parameter exists"). So it can't carry Path A voice refs. → **reference-to-video is the V3 endpoint; image-to-video is a fallback for silent/narrated cuts.**

## 3. Cost (the number idea #16 was waiting for)

fal Seedance 2.0 pricing (720p): **Standard $0.3024/s · Fast $0.2419/s**.

| Episode shape | Fast tier | Standard tier |
|---|---|---|
| 15s (1 clip) | $3.63 | $4.54 |
| **30s (2×15s)** | **$7.26** | **$9.07** |
| **45s (3×15s)** | **$10.89** | **$13.61** |

(1080p costs more — confirm multiplier at build.) Storyboard frames add ~$0.5–1.4/episode (see §6). Text pipeline stays ~$1.50. **So a 45s V3 episode ≈ $12–16 all-in** — the first real per-episode economics we've had. This is the data the roadmap wanted from M4; we now have an estimate *before* spending.

## 4. What this means for V3's generation architecture

The industry "keyframe-anchoring" pattern (already noted in `RESEARCH_video_generation.md` §3) now has a clean shape:

```
screenplay
  → STORYBOARD SKILL (image model): per-15s-segment keyframes,
      generated FROM char-ref + style-ref  → consistent frames
  → those storyboard frames ARE the Seedance @ImageN refs
  → Seedance 2.0 reference-to-video: 1 clip / 15s / multi-shot,
      bound to @Image(char, style, storyboard) + @Audio(voice)
  → 2–3 clips → assemble (subtitles) 
```

The storyboard isn't just a human review gate — its frames **double as the video model's visual anchors**. That's why the storyboard-model choice (§6) matters technically, not just for review.

## 5. Corrections this surfaced (ready to apply once V3 is greenlit to build)

**a) Canon `/tune` — `prompts/canon/prompting_guidelines_seedance.md`:**
- Title "Seedance 2.5" → **"Seedance 2.0"**.
- Ref table "Images ≤ 9 (v2.0) / ≤ 50 (v2.5)" → **≤ 9** (the ≤50 figure is unfounded; fal caps at 9).
- ✅ **Everything else is CONFIRMED correct by fal's own docs:** the `@ImageN`/`@AudioN`/`@VideoN` binding syntax, audio ≤3 & ≤15s, video ≤3 & ≤15s, the 3000-char cap. Our prompting model was right.

**b) Adapter fix — `pipeline/providers/video.py` (`FalVideoProvider`):**
- `MODEL` → `bytedance/seedance-2.0/reference-to-video` (confirm the exact `fal-ai/…` prefix from the model page's code sample at integration).
- `image_urls` and `audio_urls` arg names are **already correct** for this endpoint (the `⚠ confirm` flags resolve to ✓).
- Set `duration` to the clip length (15), add `generate_audio`, keep `resolution`/`aspect_ratio`.
- ~5-line change; no redesign needed.

## 6. Storyboard image model — options + recommendation

Criteria for us: (1) multi-reference **character** consistency (feed our sheets/portraits), (2) **style** consistency (match the locked style ref), (3) API-automatable (batch frames), (4) cheap/fast (storyboards are semi-disposable), (5) bonus: in-image text (annotations) and latent-transfer into Seedance.

| Model | Consistency | Refs | Storyboard fit | API / cost | Notes |
|---|---|---|---|---|---|
| **Nano Banana Pro** (Google, `gemini-3-pro-image-preview`) | Up to 5 people/scene; frame-to-frame identity | 14 ref objects; 4K | **Explicitly "ideal for storyboarding & pre-viz"**; accurate in-image text | fal **$0.15/img** (Kie.ai $0.09–0.12); fast 4–6s | Best storyboard-specific pick |
| **Seedream 4.x / 5.0 Lite** (ByteDance) | Multi-ref consistency; cinematic lighting | **≤6 images**; 4K; 2K in <2s | Strong; unified gen+edit | on fal + aggregators | **Same lab as Seedance → best latent-transfer bet into reference-to-video** |
| **GPT Image 2** (OpenAI) | SOTA general; edit-based | multi | Good, less storyboard-specific | OpenAI API | pricier/slower for batch |
| **FLUX.2 / Kontext** (BFL) | Strongest reference-heavy | multi | Good | fal/self-host | open-weights escape hatch |

**Recommendation (updated per Jayon 2026-07-22 — shortlist narrowed to two):** head-to-head **GPT Image 2** vs **Nano Banana Pro** on our actual character sheets + style ref. GPT Image 2 = SOTA general + strong iterative/edit-based consistency; Nano Banana Pro = storyboard-specific (frame-to-frame identity, in-image text, $0.15/img on fal). _(Seedream 4.x dropped from the running by Jayon; noted as the ByteDance same-family fallback if both underperform on latent-transfer into Seedance.)_ Decide on evidence, not vibes — a ~$1 test. The `anthropic-skills:ai-character-creation` skill (which names exactly these leaders) is the practical playbook for that head-to-head.

## 7. Residual risk — the one thing only a paid test closes

Seedance 2.0 **accepts** `audio_urls` and refers to them as `@Audio1`, but the docs don't prove it will **clone a German voice + lip-sync** to it (vs. just borrowing rhythm/SFX). Our canon §8 built Path A on this assumption. **This is the same "verify a real FAL_KEY Seedance call end-to-end" step already in the packet's next-3** — now with the correct endpoint + args in hand. Budget one 15s reference-to-video call (~$3.6) once a `FAL_KEY` exists. Fallback already speced (canon §8b: master audio as `@Video`).

Also still true: **Anthropic credits are exhausted** → the LLM stages (brainstorm/screenplay/prompt) can't run until topped up. The Seedance test is independent of that (needs only `FAL_KEY`).

## 8. Decisions for Jayon

1. **Duration default:** 45s (3×15s, ~$11–14 video) or 30s (2×15s, ~$7–9)? _(Recommend starting 30s to keep per-episode spend down during proving, allow 45s per-episode.)_
2. **Storyboard model:** approve the Nano Banana Pro vs Seedream head-to-head (~$1) as part of the build?
3. **Green-light the canon `/tune` + adapter fix** in §5 (factual corrections; apply now, or bundle into the V3 build)?
4. Next: shall I turn all this into the **V3 build plan** (phased, with the new storyboard skill + re-shaped skills 1–3 + studio UI increments)?

## 9. Sources

Seedance capability & multi-shot: [ByteDance Seed tech report](https://seed.bytedance.com/en/blog/tech-report-of-seedance-1-0-is-now-publicly-available), [Seedance paper (HF)](https://huggingface.co/papers/2506.09113), [VEED Seedance multi-shot](https://www.veed.io/ai-models/video/seedance-1.0), [Seedance landing](https://seed.bytedance.com/en/seedance). fal API schemas: [Seedance 2.0 reference-to-video API](https://fal.ai/models/bytedance/seedance-2.0/reference-to-video/api), [Seedance 2.0 image-to-video](https://fal.ai/models/bytedance/seedance-2.0/image-to-video), [fal Seedance 2.0 API repo](https://github.com/fal-ai/seedance-2.0-api), [i2v duration docs](https://fal.ai/docs/model-api-reference/video-generation-api/bytedance-seedance-2.0-image-to-video). Storyboard image models: [Nano Banana Pro on fal](https://fal.ai/models/fal-ai/nano-banana-pro/api), [Google Nano Banana Pro announce](https://blog.google/innovation-and-ai/products/nano-banana-pro/), [Seedream 4.0 API overview (CometAPI)](https://www.cometapi.com/seedream-4-0-api-architecture-benchmark-access/), [Seedream 4.5 (ByteDance)](https://seed.bytedance.com/en/seedream4_5), [Best AI for character consistency 2026 (ToonyStory)](https://toonystory.com/blog/best-ai-for-character-consistency-2026), [AI character consistency in storyboards (M Studio)](https://mstudio.ai/blog/storyboarding/ai-character-consistency-storyboards).

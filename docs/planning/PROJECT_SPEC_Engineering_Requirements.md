# Project Spec — Engineering Requirements

**Status:** COMPLETE DRAFT — all 10 components decided 2026-07-13 (#4/#5 deferred to prototyping by design); awaiting Jayon's final lock
**Date started:** 2026-07-13 · Supersedes `Project Spec Engineering Requirements.docx`
**Method:** for each component below → research options with proof → compare → Jayon decides → lock → next. Research details go into `RESEARCH_technical_requirements.md`; this doc holds only the locked decisions and why.

---

## The parent components this project needs (derived from the locked PRD)

Mapped to the pipeline: **words in → story → audio → video → assembly → app → runs daily**.

| # | Component | What it is / why we need it | Status |
|---|---|---|---|
| 1 | **Programming language** | The language the pipeline is written in — shapes every other choice and what Jayon learns. | ✅ Python |
| 2 | **Orchestration approach** | How the pipeline stages are chained and run: plain code vs a visual workflow tool (n8n) vs a job framework. Core of the "AI automation" learning goal. | ✅ n8n |
| 3 | **LLM (story/script generation)** | Turns 10 words into a coherent story + per-scene script with structured JSON output. | ✅ Claude Sonnet 5 |
| 4 | **TTS (audio)** | German narration per scene, slow/clear, SSML pause control. (May be absorbed by a video model with native audio — decided together with #5.) | ⏸ deferred → prototyping |
| 5 | **Video generation model + access layer** | The heart and biggest risk/cost. Model (Kling / Veo / Seedance / …) + aggregator (fal.ai / direct). Final style locked later via prototyping per PRD §6; here we choose the *candidate + access path*. | ⏸ deferred → prototyping |
| 6 | **Video assembly** | Stitch scenes + audio + (maybe) subtitles into the combined story video. FFmpeg vs API services (Creatomate/Shotstack). | ✅ Creatomate |
| 7 | **Backend / API** | Serves sessions to the app, triggers/monitors generation jobs. | ✅ none for MVP — Supabase auto-API (FastAPI = v1) |
| 8 | **Frontend (the simple app)** | The mobile-friendly session UI: word card → reveal → grade → video. | ✅ React + Vite PWA |
| 9 | **Database + object storage** | Word store, session/progress state, generated video files. | ✅ Supabase (Postgres + Storage) |
| 10 | **Hosting + daily scheduling** | Where it runs and what triggers the nightly generation job. | ✅ n8n in Docker on Mac (→ always-on later); app on Vercel |

**Decision order = above.** Rationale: language first (everything sits on it), orchestration second (shapes the pipeline's skeleton), then the AI stages in pipeline order (3→6), then the app around it (7→9), infra last (10) — matching the guide's advice to provision infra only once tools are chosen.

---

## Locked decisions

**#1 Programming language: Python** *(2026-07-13)* — AI-ecosystem default (first-class SDKs for Anthropic/fal.ai/ElevenLabs, FFmpeg wrappers, FastAPI), gentlest curve for learning pipeline concepts, already validated by the Comprehensible Engine research. Frontend language is a separate decision at #8.
*Learning foundation for Jayon:* Python basics if rusty — functions, dicts/JSON handling, `venv`/`uv` environments, calling an HTTP API with `requests`/`httpx`. That's 90% of what the pipeline code actually does.

**#2 Orchestration: n8n from day one** *(2026-07-13, Jayon's call — learning the automation tool IS a primary goal)* — the pipeline is built as n8n workflows: schedule trigger → LLM call → per-scene loop (TTS/video) → assembly → notify. Python (#1) remains the language for anything n8n can't express cleanly (e.g. local assembly scripts, future backend) — note n8n Code nodes are JavaScript-first, so we keep in-workflow code minimal and push logic into HTTP calls and small external scripts.
*Implications accepted:* needs a running n8n instance (self-hosted Docker on the Mac, or n8n cloud — finalized at #10); pipeline logic lives in workflow JSON (version-controlled by exporting to the repo).
*Learning foundation for Jayon:* n8n core concepts — nodes, triggers (Cron/Webhook), credentials, expressions, loops (Split In Batches), error workflows; Docker basics if self-hosting.

**#3 Story LLM: Claude Sonnet 5 (Anthropic API)** *(2026-07-13)* — top instruction-following + prose in July 2026 comparisons (BenchLM Elo 1508 for Claude family; highest prose scores in novel-writing tests), which maps to the two scarce skills here: "use exactly these 10 words correctly" and story coherence. *(Corrected 2026-07-13 during B2:)* Claude supports **native structured outputs** (`output_config.format` + JSON schema) — schema-valid JSON guaranteed at API level. The **validate → retry** loop therefore checks what schemas can't: semantic requirements (all 10 words genuinely used, German level). Native n8n Anthropic node; vendor swap stays cheap.
*Learning foundation for Jayon:* prompt engineering for structured output (few-shot examples, output priming), the validate-and-retry pattern, what a JSON schema is.

**#4+#5 Audio + Video generation: DEFERRED to Build-phase prototyping stage** *(2026-07-13, Jayon's call — will try candidates hands-on and decide there, consistent with PRD §6)*. Shortlist to prototype, with what each must prove:
1. **Gemini Omni (Google)** — Jayon's primary interest. Unified multimodal, 10s clips w/ native audio, conversational memory across generations (attacks scene-consistency directly). *Verify:* API availability (announced I/O May 2026, API "weeks away"), German audio quality, any narration-pacing control, cost.
2. **Kling 3.0 (Omni) via fal.ai + ElevenLabs TTS** — best-documented multi-shot consistency (~$0.029/s ⇒ ~$2.30/day for 10×8s); ElevenLabs German rated near-human, full slow-narration/pause control. The "full pedagogical control" option.
3. **Veo 3.1** — strongest native 48kHz synced dialogue + cinematic quality; weaker multi-shot consistency; pricing reports conflict — verify.
*Decision criterion (locked now so prototyping is honest):* cross-scene character/style consistency FIRST, German narration quality + pacing control SECOND, cost THIRD.
*Learning foundation for Jayon:* how video-gen APIs work (async job → poll → download), image-to-video reference anchoring for consistency, what SSML/pacing control means in TTS.
*Also on the prototyping radar (Jayon):* cheap open-source models (e.g. Wan) — accessible via fal.ai as plain API calls, include as cost-baseline candidates. **ComfyUI** (self-run open models on cloud GPUs) explicitly NOT for MVP — Mac can't run video diffusion locally, cloud-GPU ops is an orthogonal curriculum, and fal already serves the same models. Revisit trigger: prototyping shows we need custom consistency control (character LoRA) or daily cost becomes the binding constraint.

**#6 Assembly: Creatomate API** *(2026-07-13)* — JSON template in → rendered MP4 out; cleanest n8n integration (official tutorial exists); per-video fee verified at provisioning. FFmpeg earmarked as a deliberate v1 learning swap (one n8n node changes, fundamentals learned when a stall no longer threatens the MVP).
*Learning foundation for Jayon:* how template-based rendering works (composition JSON: tracks, clips, timing), video containers/codecs at a concept level.

**#7+#9 Data spine: Supabase** *(2026-07-13)* — Postgres (words table, sessions, per-word progress/grades) + Storage buckets (scene + story videos) + auto-generated API. n8n writes, the app reads via the Supabase JS client, grades write back. **No custom backend for MVP**; FastAPI becomes the v1 backend layer when AnkiConnect sync arrives.
*Learning foundation for Jayon:* relational basics (tables, rows, foreign keys), what an API key/row-level security is, object storage vs database.

**#8 Frontend: React + Vite, mobile-friendly PWA** *(2026-07-13)* — reuses Jayon's existing React foundations. Four screens: word card → reveal + self-grade → scene video → story finale. Deployed free on Vercel.
*Learning foundation for Jayon:* React state for the session flow, HTML5 video playback, what a PWA manifest is.

**#10 Hosting/scheduling: n8n self-hosted in Docker on the Mac** *(2026-07-13)* — free, teaches Docker; nightly generation runs while the Mac is awake (accepted MVP constraint). **Upgrade trigger:** when unattended daily reliability matters → cheap VPS (~€5/mo) or n8n Cloud. App hosting: Vercel free tier.
*Learning foundation for Jayon:* Docker run/compose basics, volumes (so n8n workflows survive restarts), cron expressions.

## Run context, ledger & memory (added 2026-07-18)

Stage-0 **Run Context Pack** (code-assembled: MISSION + bible + canon blocks + prompting guidelines distilled from Jayon's Seedance/Omni research in resources/ + series-memory digest + last-run state) injected into every LLM stage; **run ledger** (Supabase `runs`/`run_events`: per-stage artifacts, hashes, costs, gate decisions, canon versions) enables resume + traceability; **series memory** (`episodes` table) feeds the universe-growing digest. Change management via versioned canon files + /tune regression ritual. Authoritative spec: EXECUTION_PLAN_text_pipeline.md.

## Technical architecture (MVP)

```
           ON SESSION COMPLETION — event-driven (n8n, Docker on Mac)
  App writes "session complete" ─▶ n8n Webhook workflow
  Supabase ──"next 10 unseen words"──▶ (same workflow)
                                          │
                                          ▼
                             Claude Sonnet 5 (Anthropic API)
                             story + 10-scene script (JSON,
                             validate → retry loop)
                                          │
                              per scene (Split In Batches):
                                          ▼
                             video gen  [#5: Gemini Omni /
                             Kling+ElevenLabs / Veo — prototype]
                                          │
                                          ▼
                             Creatomate: assemble combined
                             story video (+ audio overlay if
                             separate TTS wins prototyping)
                                          │
                                          ▼
  Supabase ◀── scene videos + story video (Storage) + session row (DB)

                          DAYTIME (user session)
  React+Vite PWA (Vercel) ──reads session──▶ Supabase
    word card → recall → reveal → self-grade (written back to DB)
    → scene video → … → story finale
```

Key properties: **event-driven trigger** (Jayon's design, 2026-07-13) — completing a session fires generation of the next one, mirroring Anki's causality (today's outcomes precede tomorrow's queue); an optional periodic reconciliation check ("next session missing → generate") is the self-healing fallback, not the engine. The **word-source abstraction** is the Supabase words table + "next 10 unseen" query — AnkiConnect replaces that query at v1 without touching the pipeline or the trigger. Pipeline and app never talk to each other directly; Supabase is the single meeting point. Everything n8n does is exportable JSON, version-controlled in the repo.

**Estimated daily run cost (MVP, verify at provisioning):** LLM ~$0.01–0.05 · TTS ~$0.01 (if used) · video ~$2.30–3 (model-dependent) · assembly ~$0.05–0.10 → **≈ $2.50–3.20/day** while actively used.

## Provisioning checklist — JUST-IN-TIME (decided 2026-07-13)

**Policy:** nothing is provisioned up front. Each item below is created at the exact build step that first needs it, so every credential is learned in context. The checklist is the running record of what exists.

- [ ] Anthropic API key (Claude Sonnet 5)
- [ ] fal.ai account + key (video prototyping; also serves open-model baselines)
- [ ] Google AI access for Gemini Omni (verify API availability)
- [ ] ElevenLabs account (free tier first)
- [ ] Creatomate account (verify current pricing)
- [ ] Supabase project (free tier): words/sessions/progress tables + video bucket
- [ ] Docker Desktop on Mac + n8n container
- [ ] Vercel account (app deploy — can wait until frontend exists)
- [ ] Export of the 625-word deck (words + translations) → Supabase words table

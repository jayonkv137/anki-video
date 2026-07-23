# MVP ROADMAP — From Proven Text Pipeline to the Command Center

> **Created 2026-07-21 · Status: ACTIVE — this supersedes the E-plan as the forward roadmap** (EXECUTION_PLAN_text_pipeline.md is complete: E1–E6 done, E7 reframed into M-phases below).
> **Owner of vision: Jayon.** This document captures the full definition of the MVP end-state and every step to reach it.
>
> **⚠ 2026-07-22 — SUPERSEDED IN PART BY V3.** Jayon pulled the post-M6 redesign (idea #16) forward. Episode shape is now **2–3 Seedance multi-shot clips (30–45s)**, a serialized universe, a new storyboard stage, and the Command Center becomes a full co-creation studio. The M-phase **infrastructure still stands and is reused** (ledger, gates, providers, assembly, dashboard); the **episode shape + sequence** are now governed by **`VISION_v3_universe_and_studio.md`** + **`BUILD_PLAN_v3.md`**. §3's "parked until after M6" no longer applies to idea #16.

---

## 1. The vision (definition of MVP-done)

**The product is not a video generator. It is a human-in-the-loop content production OS**, proven on one niche (daily German-learning videos on Instagram):

- Humans supply what only humans should: **intent, ideas, taste, visual identity, approvals**.
- The system structures human intent through **locked templates**: words → story options → chosen story → screenplay → dual video prompts → video → assembly (subtitles + audio) → post.
- **Agents execute** every mechanical step; every behavior lives in a versioned, hash-verified canon file (`/tune` change management).
- A **Command Center** (web dashboard) gives the owner full observability and control: every run, every stage, every artifact, every cost — with human gates (choose the story, approve the video) and **idea injection** ("I have an idea for today" → director's note steering that day's episode).
- **Sellable framing:** a business owner (e.g. an Instagram page owner wanting daily content) watches and controls everything from one screen. Anti-slop positioning: *intentional, monitored, brand-controlled automation — not unsupervised AI output.*

**MVP is DONE when:** one episode has gone through the entire loop (words → posted video) AND the Command Center v1 shows and controls that loop end-to-end.

### Why this architecture already supports it
The Supabase ledger (`runs`, `run_events` with artifact paths/hashes/tokens/cost, `episodes`), the Gate A `awaiting_choice` state, and the `--note` director-input mechanism ARE the command center's data model. The dashboard is primarily a frontend over infrastructure that already exists.

---

## 2. Project brief — what exists today (2026-07-21)

| Layer | State |
|---|---|
| Word source | Supabase `words` (605-word A1/A2 deck), fetch by next-unseen / random / exact positions |
| Story chain | skill-1a (3 options for Gate A, DE+EN) → human choice → skill-1b (full story) — Sonnet 5 |
| Screenplay | skill-2 (10 scenes, dialogue-first, voice flavors) + code validators + skill-2q LLM quality judge (Haiku 4.5) with one-retry loop |
| Video prompts | skill-3 v3.0: dual Seedance 2.5 + Omni packages per scene; acts as virtual Director of Photography (per-scene lighting); canon substitution; per-scene JSON + refs_manifest |
| Visual identity | **canon_blocks v1.0 — photorealistic CGI live-action integration** (material laws: IOR/caustics, matte albedo, subsurface scattering, displacement/AO); Live-Action Integration Rule; multi-angle sheet + portrait dual identity refs |
| Governance | Hash-verified canon REGISTRY; versioned skills; `/tune` + regression ritual; full changelog |
| Ledger | Every run/stage/artifact/token/cost in Supabase; resumable; ~$1.50/episode text cost |
| Characters | 4 bibles (behavior) + character sheets + material-law char blocks; un-muted dialogue rule (v1.2) |
| Gates | Gate A (story choice, CLI) working; Gate 2 (pre-publish) designed, not built |
| Proven | Full text run end-to-end live (ep_22-499 "Müller, der Soldat"); visual pivot regression-verified |
| NOT yet built | Style-lock image · character voices/audio · actual video generation · assembly/subtitles · posting · n8n port · dashboard |

Repo state note: all recent work on branch `feat/e5-skills-v2` (merge to main = step M0).

---

## 3. The roadmap (M-phases, in order)

**Discipline rule for M1–M6: the episode needs to EXIST, not to be great.** Every quality observation goes to the parking lot, not into the critical path. Redesigns (10-words curriculum, 60s→30s duration, story structure — idea #16) happen AFTER M6 with real data.

### M0 — Housekeeping *(agent, minutes)*
Merge `feat/e5-skills-v2` → `main`. ✓ when main holds all E1–E6 + pivot work.

### M1 — Visual proof: material laws *(JAYON — critical path gate)*
Run the two manual Flashboard test prompts (Kati×Rolf pool, Bert×Kati pool; character sheets as refs, 720p, 9:16).
- Judge: Kati matte (not plastic)? Bert refracting light with caustics? Characters lit by the scene (not pasted-in)? Human scale (no miniature look)? Watch-item: Bert's felt hat vs AVOID-list "felt".
- Fail → `/tune` canon_blocks material laws to v1.1 with observed failures, retest.
- ✓ when: characters render photoreal and grounded in 2 independent generations. *(This also satisfies the C1 win-condition test.)*

### M2 — C1 close-out: style-lock *(Jayon creative + agent mechanical)*
Produce the **style reference image** (Lookbook method: curate live-action/VFX reference frames → reverse-engineer into technical vocabulary → generate the aesthetic anchor image). Register it as an asset; `refs_manifest` style ref goes `pending → resolved` (small resolver addition).
- ✓ when: every scene's manifest carries a real style-ref path. Then `/phase-gate` C1.

### M3 — Audio: the voices *(Jayon taste + agent wiring)*
Create 4 ElevenLabs voices using the bibles' "Customize Performance" texts (Müller's exists; write the other three from their voice sections). Generate the per-episode master dialogue track (chronological stitch of all scene lines). Wire: `audio-master` ref `pending → resolved`; store per-episode audio artifact.
- ✓ when: one episode's full German dialogue exists as a clean master track with per-character distinct voices.

### M4 — Video: generate one episode *(Jayon operates, agent supports)*
Regenerate cap-compliant prompts for the chosen episode (~$0.65). Generate all 10 scenes via Seedance/Flashboard **manually** (no automation wiring needed for proof). Use a lite version of the 5-10-1 protocol only if a scene fails repeatedly (parked #17 has the full protocol).
- Budget realistically: expect retries; track actual per-scene cost — this is the data that later decides 60s vs 30s (#16).
- ✓ when: 10 acceptable clips exist for one episode.

### M5 — Assembly: one video *(agent builds, script-based v1)*
Stitch 10 clips in order + burn **subtitles** (dialogue lines exist per-scene in screenplay.json with DE text — subtitle generation is mechanical) + lay the master audio (or per-scene native audio if M3 lands later). Tool: ffmpeg script v1 (Creatomate later at C5-full).
- ✓ when: one continuous 9:16 episode video file with subtitles plays end-to-end.

### M6 — POST IT: full-loop proof *(JAYON — the milestone)*
Post the episode (manual posting is fine — automation of posting is C6/C7). Screenshot for the portfolio.
- ✓ when: **the automation's output is live on Instagram.** This is the proof-of-technology milestone for job applications.

### M7 — Command Center v1 *(agent builds, Jayon designs the experience)*
The dashboard over the existing ledger. Build in three increments:
1. **v0 — Run viewer (read-only):** list runs; per-run timeline of stages with status/tokens/cost; artifact viewer (options, story, screenplay, prompts, clips, final video); series memory view. Backend = existing Supabase tables + output/ files. Stack suggestion: small React app (or even Supabase-connected Next.js) reading `runs`/`run_events`/`episodes` directly.
2. **v1 — Control:** Gate A in the UI (read 3 options, choose, add steering note); start-run button (word selection); Gate 2 approve/reject before posting; `/tune`-style canon version display.
3. **v2 — Idea injection & orchestration:** "today's idea" input feeding the director's-note mechanism; per-stage re-run buttons; cost dashboard; (later) live agent status when n8n port lands.
- ✓ when: one full episode can be run, gated, watched, and inspected entirely from the dashboard.

### M8 — Automation hardening *(agent; = old C4/C7)*
n8n port with webhook/Telegram gates (parked #15b), scheduled daily runs, posting automation (Instagram API/Buffer), failure alerts. The dashboard becomes the surveillance surface for a system that runs without being manually invoked.
- ✓ when: an episode runs on schedule with Jayon only touching the two gates. **= MVP COMPLETE.**

### M9 — Productization & market research *(joint; post-proof leverage phase)*
Research deliverable: where else does this system apply? (any business with recurring, template-shaped, quality-controlled content: real-estate listings→video tours, e-commerce product drops, restaurant weekly specials, course creators, local news recaps, multi-language brand channels, agency white-label…) Output: `RESEARCH_platform_applications.md` — industries, buyer profiles, pitch framing ("intentional automation, not slop"), competitor scan, pricing thinking + a portfolio case study of THIS project (architecture story: gates, ledger, versioned canon, tune ritual). Then: marketing/selling experiments.
- ✓ when: pitch-ready case study + target-market shortlist exist.

### Deliberately parked until after M6 (with real data)
Idea #16: curriculum redesign (10→5 words?), duration (60s→30s / 2×15s), story-structure changes, cost optimization. Idea #17: 5-10-1 protocol, upscale→LUT→grain post-chain, visual dubbing, ComfyUI/LoRA fallback. Jayon's noted design concerns on stories/prompt structure.

---

## 4. Sequencing summary

```
M0 merge → M1 VISUAL PROOF (Jayon) → M2 style-lock → M3 voices → M4 generate → M5 assemble → M6 POST ✦proof✦
                                                                                                  ↓
                                          M9 productization ← M8 automation (n8n) ← M7 COMMAND CENTER
```
(M7 can start in parallel after M6 — v0 run-viewer needs nothing from M2–M5.)

## 5. Cost picture (current knowledge)
- Text pipeline: ~$1.50/episode (Sonnet 5 + Haiku QC). Stage-7 prompts regen: ~$0.65.
- Video generation: UNKNOWN until M4 — the single most important number M4 produces. Budget expectation: 10 scenes × retries at Flashboard credit rates; drives the #16 duration/cost redesign decisions.
- Audio: ElevenLabs subscription tier (small).
- Dashboard/n8n: dev time, no meaningful run cost.

# Changelog

> Newest first. One entry per meaningful change/feature.

## 2026-07-21 — Fresh test run 51cc85bb + Flashboard prompt export (no-style, dual-ref)

- **Fresh end-to-end run** `51cc85bb` "Der fünfzigste Spieltag" (Müller×Rolf, heatwave garden matchday), ~$1.64. QC failed on dialogue-naturalness nits + proceeded per design; skill-3 emitted 4/10 Seedance prompts over the 3000-char cap (2-char scenes) — the standing skill-3 budget limitation on two-character scenes.
- **Flashboard export for Jayon's manual Seedance visual test** → `output/episodes/ep_54-564/flashboard.md`: all 10 prompts made paste-ready — trimmed the `@Audio1` sync line (no audio track for a silent look-test) and, per Jayon's request, **removed the style reference entirely** (no style image yet) and **rebound each character to TWO slots — main portrait + character sheet** (upload order: main then sheet). All 10 now ≤3000 chars. Per-scene upload guide reads the real slot assignments. Scenes 1–6 = Müller solo (@Image1/2); 7–10 = two-char (@Image1/2 Müller, @Image3/4 Rolf).
- Docs fully synced: project_status rewritten to current reality (machine half of MVP built + merged; M1 manual test is the critical path); phase checklist updated (C2 E1–E6, C3 provider system, C5 assembly, C6 caption+dashboard, M9 research all reflected).

## 2026-07-21 — Per-character VOICE references incorporated (Path A) + Path B vision

- **Path A built** (Jayon added a voice-identity .mp3 per character): each character now resolves to sheet + portrait + VOICE, attached to every scene automatically — the same pipeline the image sheets flow through, extended by one asset type. Changes: `.gitignore` un-ignores `resources/**/*.mp3` (the `*.mp3` generated-media rule was silently excluding the source voice assets); `_character_voice_path` resolver + `voice` role in `_resolve_binds`/`build_refs_manifest` (verified: all 4 voices resolve, umlaut-folded); skill-3 v3.1 emits per-character voice refs and writes `Use @AudioN as the voice of <Name>` bindings into the Seedance prompt; seedance canon §8 v2.1 (per-character voice references as the current method, merged-master documented as future) + omni §7 v1.2 (fixed per-character voice identity); REGISTRY v1.3 (verify_canon green); Fal provider now splits refs into images vs voice audio and passes both. Verified offline via a synthetic manifest test (live prompt regeneration blocked on an Anthropic credit top-up).
- **Path B vision documented** (`docs/planning/VOICE_REFS_INCORPORATION_PLAN.md`): the future upgrade where per-scene dialogue is synthesized in each character's ElevenLabs-cloned voice and handed to Seedance as a finished master track (tightest lip-sync + flawless German) — exact step-by-step workflow, the `providers/audio.py` + `stage_audio` build, and why/when to do it (= M3 audio).

## 2026-07-21 — M9 research: prior art + market applications (deep pass)

- **`docs/planning/RESEARCH_market_and_prior_art.md`**: the screenplay->prompts->video pipeline SHAPE is now common (ViMax, 11.3k★ academic project; Open-AI-Micro-Drama-Generator; Wireflow; multiple n8n templates) — none of them have a versioned/hash-verified prompt canon, a cost/token ledger, or a pre-spend human gate. That governance combination is the actual differentiator, not the AI pipeline itself. **Duolingo's 2026 AI-content TikTok/IG backlash** (deleted everything after follower revolt) is the single strongest validating data point for the anti-slop, human-gated pitch — paired with hard stats (78% consumer skepticism of AI content, 26% vs 60% preference collapse). Validated generalization targets ranked by fit: white-label content agencies (proven $1-10K/mo retainer economics) and course creators (same pipeline shape) first; real estate + e-commerce second tier; recruiting/local news explicitly a poor fit (those markets want zero human gates, opposite of our positioning). Generative-AI-content market: $21-24B (2026) -> $77B (2030).

## 2026-07-21 — M4 video generation: provider system (mock + real Seedance) + autopilot

- **Provider architecture** (`pipeline/providers/video.py`): one interface, two backends. `MockVideoProvider` renders real per-scene placeholder .mp4s locally (no key, no cost) so the WHOLE pipeline runs end-to-end today; `FalVideoProvider` calls real Seedance via fal.ai, activated by `FAL_KEY` in .env — one-key swap, no rewrite. Factory `get_video_provider(name)`.
- **`pipeline generate <run_id> --provider mock|fal`** (`stage_generate`): loops scenes, reads scene_NN.seedance.json + refs_manifest, writes clips/scene_NN.mp4, logs per-scene to ledger.
- **`pipeline autopilot <run_id>`**: full hands-off finish — generate → assemble (subtitles) → caption in one background run. **Proven end-to-end**: mock autopilot on ep_22-499 → 10 clips → stitched 69s 1080×1920 video with burned DE/EN subtitles (frame-verified) → caption. This is the automation working through to a postable video with zero manual steps.
- **Command Center: post studio v3** — ⚡ Autopilot panel (mock/real buttons), Generate-all buttons, per-scene clip status; all one-click. Browser-verified.
- **`docs/planning/REAL_API_CONNECTION.md`**: exactly how the real APIs connect (fal.ai Seedance, ElevenLabs, Instagram Graph), which keys you add, why n8n is optional, and the honesty note (real adapters are written to the standard SDK flow but unverified until keyed — first real call confirms exact schemas).

## 2026-07-21 — Caption generator (skill-4) + Command Center v2 (post studio)

- **Skill-4 caption writer + `pipeline caption <run_id>`** (`stage_caption`, CAPTION_SCHEMA): episode → Instagram post copy — scroll-stopping hook, story tease, all 10 words with correct articles + English, a comment-driving CTA using today's vocabulary, and normalized hashtags. Writes caption.json + caption.md. Verified on ep_22-499 (~$0.02). The missing "you can't post without a caption" piece for M6. (Minor: it emitted an off-brand `#germanpuppets` tag — captions are human-editable; a skill note can pin brand voice later.)
- **Command Center v2** (`dashboard/`): the loop is now fully drivable from the UI. New "post" tab = a 4-step studio: clip-upload grid (drop scene_NN.mp4 per scene, live 10/10 status) → Assemble button (spawns `pipeline assemble`) → in-page final video → post copy (Generate/Regenerate caption). New "caption" tab. Overview stats strip in header (runs/done/at-gate/total-cost). New endpoints: POST caption, POST assemble, multipart clip upload, GET stats. Browser-verified end-to-end (clips→assemble→video→caption all render, no console errors).

## 2026-07-21 — M5 Assembly + M7 Command Center v1 SHIPPED

- **M5 — `pipeline assemble <ep>`** (`pipeline/assemble.py`): scene clips → normalized (1080x1920@30, single audio track) → concat → subtitles burned from screenplay.json dialogue (DE + EN italic, distributed over real clip durations) → optional master-audio replacement → `final.mp4`. Verified with 10 dummy clips against the real ep_22-499 screenplay; frame-extract confirms burned subtitles. The moment real clips exist, the postable video is one command away.
- **M7 — Command Center v1** (`dashboard/app.py` FastAPI + `dashboard/static/index.html`): the control screen over the existing Supabase ledger. Live-verified in browser: runs sidebar with status chips/costs; per-run stage pipeline visual (incl. honest red ✗ on failed QC); artifact tabs (screenplay as scene cards with DE/EN dialogue, options, story, per-scene prompt JSONs, episode.md, **final video playing in-page**); **Gate A in the UI** (3 option cards + Choose buttons + steering note); **New Run dialog with "TODAY'S IDEA" director-note injection**. Choose endpoint guards to the latest awaiting run (CLI constraint). Launch: `.venv/bin/python -m uvicorn dashboard.app:app --port 8787` from repo root.
- Note: ledger costs stored before today's cost-fix display inflated (e.g. $13.59 shown vs true ~$1.86 for run 3baf6a40) — historical values; new runs record accurately.

## 2026-07-21 — MVP redefined + forward roadmap: the Command Center vision

- **New roadmap doc `docs/planning/MVP_ROADMAP_command_center.md`** (supersedes the completed E-plan as the forward plan). Jayon's MVP end-state: prove the full loop through actual POSTING, then a **Command Center dashboard** — full observability + control over every run/stage/artifact/cost, human gates in the UI, "today's idea" injection — built over the EXISTING Supabase ledger (the backend already exists). M-phases M0–M9 with owners and win conditions; strategy locked: prove-first, redesign-after (with real cost/quality data). M9 = productization research: the system generalizes as a human-in-the-loop content production OS for any recurring template-shaped content business (anti-slop positioning).

## 2026-07-21 — THE VISUAL PIVOT: puppet aesthetic → photorealistic CGI live-action integration

- **Canon overhaul (Jayon's CGI Integration research + Lookbook + Pipeline Design docs).** `canon_blocks.md` v1.0 (finally out of "interim"): STYLE_BLOCK rewritten to "high-end cinematic live-action cinematography with photorealistic CGI characters" (35mm anamorphic, locked-off camera, lens halation, full AVOID list banning cartoon/Pixar/plastic-skin/stop-motion/felt/clay/puppetry); all four CHAR_BLOCKs rewritten as VFX **material laws** — Bert: IOR + caustics + volumetric foam · Kati: strictly matte albedo, zero specular · Rolf: subsurface scattering, embedded tattoos · Müller: displacement mapping + max ambient occlusion. Old canon literally commanded what the new AVOID list bans (felt/puppet/handcrafted).
- **Constants vs Variables split.** Hardcoded lighting (3200K/5600K, high-key) and DoF REMOVED from the permanent style block (they fought outdoor scenes → "pasted-in" look). skill-3 v3.0 is now the **virtual Director of Photography**: writes per-scene Environment & Lighting in technical vocabulary derived from the screenplay's setting, consistent across the episode's single location.
- **Live-Action Integration Rule** added to seedance guidelines v2.0 (+new DON'T), omni guidelines v1.1, and skill-3's pitfalls: never puppet/claymation/needle-felt/stop-motion/miniature/toy vocabulary anywhere; scenes are live-action VFX integration at human scale. Character bible v1.3: "puppet" framing scrubbed.
- **Identity refs: sheet-first dual resolution.** `_character_ref_paths` now resolves each character to TWO images — multi-angle character sheet (primary; structural map preventing back/side dissolution on turns) + main portrait (close-up anchor) — both listed per scene in refs_manifest with `variant` labels. (Old resolver preferred portrait, backwards vs research.)
- **Regression run** (stage-7 regen on "Müller, der Soldat", ~$0.64): pivot verified — material laws in bindings, scene-derived fluorescent rehearsal-room lighting written by skill-3, zero puppet vocabulary. **Caught: substituted Seedance prompts exceeded the 3000-char cap** (3,766) — the CGI char blocks are ~3× longer. Fixed: skill-3 character-budget rule (~900 chars own text on 2-char scenes) + code-side over-cap warning logged to ledger. Old puppet-era prompts preserved at `output/episodes/ep_22-499/prompts_v0_puppet/`.
- REGISTRY v1.2: all four touched canon hashes updated; `verify_canon` green.
- Out of scope (parked, C3/C5): audio-first ElevenLabs chain, 5-10-1 generation protocol, upscale→LUT→grain post-production, visual dubbing remediation, ComfyUI/LoRA fallback.

## 2026-07-21 — E6: first full pipeline run completes end-to-end (Gate A → episode.md)

- **Live proof run** (`3baf6a40`, words 22-499, chose option 3 "Müller, der Soldat"): `pipeline run` → Gate A → `choose 3` → expand → screenplay (1 retry) → quality check (Haiku 4.5, still failing after the 1 allowed retry — proceeded per design, verdicts recorded) → dual Seedance/Omni prompts → finalize. Full artifact set produced: `story.json`, `screenplay.json`, `prompts.json`, `prompts/scene_NN.{seedance,omni}.json` ×10, `prompts/refs_manifest.json`, `episode.md`. Character refs resolved to real `resources/` images (Müller via umlaut-fold); style/audio refs correctly `pending` (C1/C3 not built yet).
- **Fix: skill-3 prompts truncated (`json.JSONDecodeError`, unterminated string).** `stage_prompts` used the default `max_tokens=24000`; the new dual-package output for 10 scenes needs far more room. Bumped to `max_tokens=64000` (within Sonnet 5's 128K streaming ceiling) — the exact "16k+ max_tokens" lesson this project hit before, recurring at the new output shape.
- **Fix: `ledger.add_cost` was 10x too high.** Formula divided by 100 instead of 1000 (`$3/M in` → `0.0003 cents/token`, not `0.003`). This run's ledger showed **1296 cents ($12.96)**; true cost was **122 cents ($1.22)**. Also fixed: cost was always priced at Sonnet rates even for Haiku 4.5 QC calls — `add_cost` now takes `model` and uses a per-tier rate table (`claude-sonnet-5` $3/$15, `claude-haiku-4-5` $1/$5 per M).
- **Fix: `choose`/`resume` reloaded the WRONG words for `--random` runs.** `fetch_words(start=positions[0])` did a sequential `gte+limit` re-fetch instead of the run's exact positions. New `fetch_words_by_positions()` (`in.()` filter, count-asserted); `stage_words` also gained an optional `positions` arg + `pipeline run --positions <list>` for golden-batch/regression runs (used for this proof).
- E6 ✓ condition met: full run with a real Gate A choice completes; artifacts + refs_manifest correct; ledger shows accurate hashes/tokens/cost.

## 2026-07-21 — tune: Characters-Main-Sheet v1.2 + skill-2 v1.1 — un-mute the quiet characters

- **Observed pattern (live Gate A run `3fb14aae`):** every story option built Müller/Rolf around NOT speaking ("silent armored guard", "says only Nee") — bible brevity caps taken literally by LLMs kill a language-teaching show. Fix (Jayon's text): top-level **Dialogue rule** in all four bibles + main sheet ("character shapes HOW they speak, never HOW LITTLE"); Müller belief "spend them never"→"carefully", first bullet → full compact sentences ("Moin." = greeting habit, not vocabulary), "silence as dialogue" → "economy as style"; Rolf → full dry sentences, two-sentence cap deleted. Synced the two enforcement echoes that would have fought the fix: skill-2 v1.1 (word budgets → voice flavors + no-mute-characters self-check) and `validate_screenplay` (Müller ≤3-word code check removed). REGISTRY v1.1: main sheet hash+version updated. **Verified working** in the E6 proof run above — Müller spoke real dialogue in all 10 scenes.

## 2026-07-21 — E5 skills v2 shipped + E6 stage-7 rewiring

- **E5: Skills v2** (committed `491fd61`, branch `feat/e5-skills-v2`, not yet merged to main). Split monolithic skill-1 → `skill-1a-story-options` (Gate A: 3 scored premises, DE+EN) + `skill-1b-story-expand` (chosen premise → full 12–16-beat story); rewired the two story stages in `stages.py` and deleted the inline `OVERRIDE`/scaffolding strings; old `skill-1-story-selector` deprecated (kept for reference). New `skill-2q-quality-check`: `stage_quality_check` now runs the code validators **and** an LLM checklist on **Haiku 4.5** (`claude-haiku-4-5`) — a 7-item binary rubric returning `{passed, checks[], feedback}` — passing only if both pass; verdict logged to the ledger. `_call` parameterized (`model`/`max_tokens`); added `HAIKU` tier + `QC_SCHEMA`. Rewrote `skill-3-prompt-writer` → v2: dual **Seedance + Omni** packages per the E1 canon (Seedance first-30-words law + ref-mirroring; Omni stateful edit-turn plan; ref-role mapping `{slot,binds,role}`), placeholder discipline preserved. Version headers on all active skills (`/tune` governance).
- **E6 (in progress, uncommitted): stage-7 output rewiring.** New dual-package `PROMPTS_SCHEMA` + `REF_SCHEMA`; `stage_prompts` now writes `prompts.json` and splits `prompts/scene_NN.{seedance,omni}.json` + `refs_manifest.json`. New `build_refs_manifest` resolves character `binds` → real `resources/<Name>/` images (umlaut-folded name match; picks Main/Master/sheet) and records **style + audio refs as `pending`** (C1 style-lock and C3 per-run audio not yet produced — no assets fabricated). `substitute_canon` + `stage_finalize` updated for the new shape. Offline-verified: 20 checks against real `resources/` + `canon_blocks.md`. Remaining E6: QC-fail → one retry of stage 5 (cli.py), then the live end-to-end run (human-gated at Gate A).

## 2026-07-18 → 2026-07-20 — E1–E4 execution (Antigravity/Opus session)

- **E1: Canon distillation.** Distilled `resources/AI Prompting Consistency Research.md` + `resources/Seedance Gemini Omni German Dialogue.pdf` → `prompts/canon/prompting_guidelines_seedance.md` (88 lines) + `prompts/canon/prompting_guidelines_omni.md` (101 lines). All rules traceable to source sections. Jayon-approved.
- **E2: Mission + Registry.** `prompts/canon/MISSION.md` (29 lines, distilled from PROJECT_GOAL_AND_MILESTONES.md) + `prompts/canon/REGISTRY.md` (SHA-256 hash table for all 5 canon files). RCP builder verifies at run start.
- **E3: Ledger + series memory.** Three Supabase tables: `runs` (status/stage/cost/canon versions), `run_events` (per-stage artifacts+tokens+hashes), `episodes` (series memory — scenario/cast/verdict). SQL migration at `scripts/migrations/001_ledger_tables.sql`. Migrated `episode_log.json` → `episodes` table. Round-trip test passed.
- **E4: Pipeline package refactor.** `pipeline/` package: `rcp.py` (canon loader + hash verifier + series memory digest), `ledger.py` (Supabase CRUD for runs/events/episodes + cost tracking), `stages.py` (pure functions: words → 3 story options → expand → screenplay + validate → quality check → prompts + canon substitution → finalize), `cli.py` (run/choose/status/resume commands). Live test: `pipeline run --random` → Gate A pause verified; `pipeline status` shows ledger truth. Model: Claude Sonnet 5 for all creative stages.
- **Learning system** (Jayon parallel session): `/learn` skill added to CLAUDE.md, `.agents/skills/learn/SKILL.md`, `docs/learning_system/` (README, LEARNING_LEDGER.md, db_ledger_visualizer.html).

## 2026-07-18 — Text-pipeline v2 architecture locked + Antigravity execution plan

- EXECUTION_PLAN_text_pipeline.md: Stage-0 Run Context Pack (answering Jayon's initialization question — yes, first, code-assembled, injected per stage; stateless-with-shared-pack chosen over one long chat per context-rot research), run ledger + series memory (Supabase), 3-option story premises + Gate A choice, quality-check stage, skill-3 v2 dual Seedance/Omni packages with reference-role mapping (per Jayon's two prompting-research files in resources/), /tune change-management ritual (+ new /tune skill). Tasks E1–E7 for Antigravity (Opus), Jayon parts listed. Core docs synced with pointers.

## 2026-07-17 — C2 v1 SHIPPED: the three-skill text chain works end-to-end

- prompts/skills/: skill-1 story-selector (word audit → 3 scored scenario candidates → cast by belief-collision → beats w/ hook+human-beat), skill-2 screenplay-writer (10 subtitled filmable scenes, voice budgets, retention+CI rules), skill-3 prompt-writer (Veo/Flow + Seedance variants, canon placeholders substituted by code).
- prompts/canon/canon_blocks.md: INTERIM style block + 4 character visual blocks (mechanical injection — LLM never paraphrases canon).
- scripts/generate_episode.py: chained harness w/ schema-enforced structured outputs + streaming (two live failures fixed: 8k/16k max_tokens truncations), semantic validation (word coverage + Müller word budget), episode log as run context, artifacts + pretty episode.md per run.
- First auto-episode passed validation: "Kati und der Handtuch-Krieg" (Freibad towel war, Kati×Rolf). R-6 hook findings encoded in skill-2.

## 2026-07-17 — Google Flow research + first full pipeline map

- RESEARCH_google_flow.md: Flow capabilities (Ingredients/voices/SceneBuilder/Flow Agent, confirm-before-generating), NO public API (unofficial APIs = ban risk) → Flow is the manual creative cockpit; automation uses same models via Gemini API (separate billing). Competitors compared (LTX Studio closest; model APIs remain the automatable route). Episode-0 manual mockup protocol defined.
- PIPELINE_MVP.md: first end-to-end pipeline diagram (canon injection points, 8 stages, 2 gates, Flow side-cockpit, stage ownership/status table).

## 2026-07-15 — Canon names finalized + grammar-corrected

- FINAL: Rolf die Wurst · Bert das Bier · Kati die Kartoffel · Müller das Brot. Articles corrected to noun gender (das Bier; die Wurst sing.) per new language-accuracy principle: everything learner-facing must be grammatically correct. Folders/files/docs renamed and synced (Pam-*→Kati-*, ASCII filenames). Review blocker B1 closed; Kati's polished look ruled a character trait; Bert's identity core = glass+foam.

## 2026-07-14 — THE PIVOT: V1 learner app → V2 Instagram content pipeline

- Vision V2 (Jayon): "Stereotypical German" Instagram page — 4 original comic characters, art-directed world, daily 10-word stories; quality-over-slop positioning; two human approval gates (before spend, before publish); story→screenplay→prompt three-pass LLM chain; learner app PARKED.
- Docs re-cut: goal doc V2, build plan V2 (C1 Character/Art Bible → C2 screenplay chain → C3 video prototyping → C4 gated scene pipeline → C5 assembly → C6 publishing+gate → C7 daily ops). B0–B2 carry over unchanged.
- New: RISKS_AND_REALITY_CHECKS.md (10 named failure modes with early warnings). New system rules in CLAUDE.md: mandatory research step per decision; model-selection table (Haiku/Sonnet/Opus/Fable) required in every delegation.
- Instagram market research committed (RESEARCH_instagram_german_market.md): digging playbook + ~35 verified accounts + format taxonomy; gap confirmed = serialized animated CI stories.

## 2026-07-13 — B2 design: story strategy locked

- Research (TPRS, exposure frequency, bizarreness/humor, story grammar) → `docs/planning/RESEARCH_story_design.md`.
- Locked: fixed duo cast + consistent world; fixed episode template (setting→problem→attempts→resolution); LLM assigns words to scenes freely, session presents in story order (PRD §5 amended); memorably-quirky visual humor with plain language; NO forced repetition (each word genuinely used ≥1×); dialogue as escape hatch for abstract/meta words; deck example sentences fed as sense anchors.

## 2026-07-13 — B1: Word source ✅

- Supabase provisioned (project `anki-video`, keys in `.env`; RLS on, no policies — only the secret key reads for now).
- `words` table: position (unique), word_type, german, english, sentence_de/en, related_raw (stored unused), introduced_on. Deck export (`00 Deutsch 605 Wörter.txt`, 605 rows) parsed + validated + upserted by `scripts/import_words.py` (idempotent; 0 parse problems; 395 Nomen / 85 Verb / 72 Adjektiv / 36 Zahlwort / 10 Adverb / 7 Pronomen).
- Workflow **B1 Next Words** (`workflows/b1-next-words.json`, credential-refs included): Webhook → fetch 10 unseen (PostgREST `is.null` + `order` + `limit`) → PATCH `introduced_on` (executeOnce, cross-node expression) → Respond.
- **Win condition met:** run 1 returned positions 1–10, run 2 returned 11–20; test stamps reset to null afterward (test-data hygiene).

## 2026-07-13 — B0: Engine heartbeat ✅

- Docker Desktop installed; n8n running as a container (`docker.n8n.io/n8nio/n8n` v2.29.10) detached, port `5678:5678`, data on named volume `n8n_data` mounted at `/home/node/.n8n`.
- First workflow **B0 Heartbeat** (`workflows/b0-heartbeat.json`, repo = source of truth): Webhook (GET `/webhook/heartbeat`) → HTTP Request (fetch `api.github.com/zen`) → Respond to Webhook (JSON). Imported via `n8n import:workflow` CLI, activated, restart-registered.
- **Win condition met:** calling the webhook returns 200 with live-fetched data; workflow + data survive a full container stop/start (proves volume persistence).

## 2026-07-13

- Plan phase completed: goal & milestones locked, product requirements locked, engineering requirements complete (stack decided; video/audio model deferred to prototyping with shortlist + criteria). Efficacy/competitor research done. All docs in `docs/planning/`.
- Repo created (private, github.com/jayonkv137/anki-video), scaffolded: README, .gitignore, .env.example (just-in-time provisioning policy), CLAUDE.md, automated docs.

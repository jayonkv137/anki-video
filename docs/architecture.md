# Architecture

> Living doc — updated after every structural change. Full rationale: `planning/PROJECT_SPEC_Engineering_Requirements.md`.

## System overview (target, MVP)

- **Nightly pipeline (n8n, Docker on Mac):** Supabase "next 10 unseen words" → Claude Sonnet 5 (story + 10-scene script JSON, validate→retry) → per-scene video generation (model TBD via prototyping) → Creatomate assembly → videos to Supabase Storage, session row to Postgres.
- **Session app (React + Vite PWA, Vercel):** reads session from Supabase → word card → recall → reveal + self-grade (written back) → scene video → story finale.
- **Single meeting point:** pipeline and app never talk directly; Supabase is the interface. Word source is a DB query (AnkiConnect swaps in at v1).

## Current state

B0 + B1 complete (n8n webhook workflows on Docker; Supabase holds the 605-word deck with `introduced_on` tracking). **Text pipeline (C2) is live as the `pipeline/` package** — E1–E6 all done: hash-verified canon + RCP, Supabase run ledger + series memory, the 8 stages with Gate A, skills v2 (1a/1b/2/2q/3), dual-package prompts + refs_manifest, QC-retry wiring, and a first full live run completed end-to-end (Gate A → episode.md). Runs via `python -m pipeline run/choose/status/resume`.

## V3 reshape (in progress — 2026-07-22)

The pipeline is being reshaped from "10 one-per-word scenes" to a **stereotype-driven, human-co-created** shape (see `planning/BUILD_PLAN_v3.md`). New/changed structure:

- **Stereotypes library** — `resources/stereotypes_library.json` (100 micro-behaviors · 10 categories + per-item coverage), ingested from `resources/stereotypes_source.xlsx` by `scripts/ingest_stereotypes.py` (idempotent; preserves coverage on re-ingest). Read/write API: `pipeline/stereotypes.py` (`pick_options(3)` daily pick, `mark_covered`, `coverage_summary`). This is the daily-pick + "what's covered" backbone.
- **Co-creation (story) stage** *(BUILT — structure-verified; live runs need credits)* — replaces skill-1a/1b for V3. Flow: pick stereotype → human **seed** → **cast** (main required + optional side/guest/background) → **skill-1a-align** (location + BOTH-kind lesson options) → **skill-1b-diverge** (3–5 comedic angles, temp 1.0, + an oblique constraint) → **skill-1c-commit** (critique → **Story Brief**, temp 0.2). Stage fns `stage_align`/`stage_diverge`/`stage_commit` in `stages.py`; schemas + safeguards (`STORY_BRIEF_SCHEMA`, `ALIGN/DIVERGE/BRIEF_COMMIT_SCHEMA`, `validate_brief`, `find_forbidden_in_dialogue`, `OBLIQUE_STRATEGIES`); `_call` takes a per-stage `temperature`. Driven by CLI `brief-start` → `brief-diverge` → `brief-commit`; the Brief feeds **skill-2 v2.1**. See `planning/DESIGN_cocreation_stage.md`.
- **Screenplay stage (reshaped, v2.0)** — `SCREENPLAY_SCHEMA` is now `episode → segments → shots` (2–3 ~15s segments, each = one multi-shot Seedance clip). `validate_screenplay` enforces segment/shot shape + CEFR word/sentence caps + teaching metadata (no deck coverage). skill-2/skill-2q at **v2.0** (segment/shot; QC now checks the grammar target is actually taught + the stereotype is shown-not-explained). The **Story Brief is skill-2's input**.
- **Video adapter** — `providers/video.py` `MODEL` → `bytedance/seedance-2.0/reference-to-video` (many image refs + audio + ≤15s), duration clamped 4–15s, `generate_audio` on.
- **Canon** — Seedance guidelines at **v2.2** (naming 2.0, image cap ≤9); REGISTRY **v1.4**.
- **Storyboard + video-prompt (V3, BUILT):** `skill-2b-storyboard` + `stage_storyboard` + `providers/image.py` (mock + GPT Image 2 + Nano Banana Pro) → 9:16 panels per shot; `skill-3` **v4** = thin **per-15s-segment Seedance** compiler (Omni + canon look-blocks dropped, binds the panels + sheets + voices + style), with `PROMPTS_SCHEMA` / `stage_prompts` / `build_refs_manifest` reshaped per-segment. CLI: `pipeline storyboard`. Screenplay shot now carries the **director layer** + per-shot `duration_s` (the 15s time-split).
- **⚠ Downstream NOT yet reshaped:** `stage_generate`, `stage_finalize`, `assemble.py` still assume the old per-scene `scenes[]` — they move to the per-segment contract in Phase 6. So automated video isn't runnable yet, but the per-segment **Seedance prompts + storyboard panels ARE produced** (test manually elsewhere). Anthropic credits still exhausted for LLM stages; real image/video need `FAL_KEY`.

## Planned next (E7, see docs/planning/EXECUTION_PLAN_text_pipeline.md)

Two more Jayon-approved batches (on fresh word sets) = C2 win condition; fixes via the /tune loop as issues surface (skill-2q already flagged one stylistic issue in the first run's finale line — worth a look).

## Components

### n8n engine (B0)
- **Runtime:** Docker container `n8n` from `docker.n8n.io/n8nio/n8n`, detached, `-p 5678:5678`.
- **Persistence:** named volume `n8n_data` → `/home/node/.n8n` (SQLite DB + workflows + credentials). Survives container restart/recreate; this is why n8n data is not lost on `docker restart`.
- **Workflows as code:** exported to `workflows/*.json` in the repo (the repo, not the running instance, is the source of truth). Import: `docker cp` → `docker exec n8n n8n import:workflow --input=...`.
- **First workflow:** `workflows/b0-heartbeat.json` — Webhook → HTTP Request → Respond. Production webhook (active workflow) at `http://localhost:5678/webhook/heartbeat`.
- **Restart recipe (upgrade-safe):** `docker rm` the container, `docker run` a new one on the same `n8n_data` volume — workflows persist.

### Word source (B1)
- **Supabase** project `anki-video`: `words` table (605 rows, deck order in `position`, `introduced_on` null until served). RLS enabled, no policies — secret key only until the app needs a read policy (B6).
- **Import:** `scripts/import_words.py` — parse (split on 2+ spaces) → validate (refuses on problems) → idempotent upsert (`on_conflict=position`). Python venv at `.venv/` (requests, python-dotenv).
- **Workflow `B1 Next Words`** (`workflows/b1-next-words.json`): GET `/webhook/next-words` → HTTP GET PostgREST (`introduced_on=is.null&order=position.asc&limit=10`) → HTTP PATCH stamp (`executeOnce`, `position=in.(…)` built via cross-node expression) → respond with the 10 words. Supabase credential stored in n8n (`supabaseApi`), referenced by id in the JSON so imports auto-attach.

### Text pipeline (`pipeline/` package — C2)
- **Entry:** `python -m pipeline run [--start N|--random] [--note] · choose <1|2|3> [--note] · status · resume`. Deps in `.venv/` (anthropic, requests, python-dotenv).
- **RCP (`rcp.py`):** assembles the per-run "creator's mind" (MISSION + character bible + canon blocks + Seedance/Omni guidelines + series-memory digest) and hash-verifies every canon file against `REGISTRY.md` at run start (mismatch aborts).
- **Ledger (`ledger.py` + Supabase):** `runs` / `run_events` (per-stage artifact paths + SHA-256 + tokens) / `episodes` (series memory). Cost tracked per LLM call.
- **Stages (`stages.py`, pure fns):** words → 3 story options (skill-1a) → **Gate A pause** → expand (skill-1b) → screenplay + validate→retry (skill-2) → quality check (skill-2q: code validators + Haiku 4.5 LLM checklist) → prompts (skill-3: dual Seedance + Omni) + canon substitution → finalize (episode.md + series memory). Model tiers: Sonnet 5 creative, Haiku 4.5 QC.
- **Visual canon (v1.0, 2026-07-21 pivot):** photorealistic CGI live-action integration — `canon_blocks.md` holds the CONSTANTS (medium + camera law + per-character VFX material laws + AVOID list); lighting and DoF are per-scene VARIABLES written by skill-3 acting as virtual Director of Photography. Live-Action Integration Rule (no puppet/miniature vocabulary, ever) in both model guideline files + skill-3.
- **Stage-7 output:** `prompts.json` + per-scene `prompts/scene_NN.{seedance,omni}.json` + `refs_manifest.json` (scene → reference assets; each character resolves to TWO identity images — multi-angle sheet first, portrait second — via umlaut-folded match; style/audio `pending` until C1/C3). Code warns when a substituted Seedance prompt exceeds the 3000-char engine cap.
- **QC-fail retry:** on failure, `cli.py` re-runs stage 5 once with the judge's feedback, re-judges, then proceeds regardless (verdict always recorded — no thrashing).
- **Cost tracking:** `ledger.add_cost` uses a per-model-tier cents/token rate table (Sonnet 5 $3/$15, Haiku 4.5 $1/$5 per M) — priced at whichever model actually ran each call.
- **Governance:** every skill/canon file carries a `version:` header; the `/tune` ritual edits exactly one owning file + bumps its version.

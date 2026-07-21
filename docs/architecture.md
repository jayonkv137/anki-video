# Architecture

> Living doc — updated after every structural change. Full rationale: `planning/PROJECT_SPEC_Engineering_Requirements.md`.

## System overview (target, MVP)

- **Nightly pipeline (n8n, Docker on Mac):** Supabase "next 10 unseen words" → Claude Sonnet 5 (story + 10-scene script JSON, validate→retry) → per-scene video generation (model TBD via prototyping) → Creatomate assembly → videos to Supabase Storage, session row to Postgres.
- **Session app (React + Vite PWA, Vercel):** reads session from Supabase → word card → recall → reveal + self-grade (written back) → scene video → story finale.
- **Single meeting point:** pipeline and app never talk directly; Supabase is the interface. Word source is a DB query (AnkiConnect swaps in at v1).

## Current state

B0 + B1 complete (n8n webhook workflows on Docker; Supabase holds the 605-word deck with `introduced_on` tracking). **Text pipeline (C2) is live as the `pipeline/` package** — E1–E6 all done: hash-verified canon + RCP, Supabase run ledger + series memory, the 8 stages with Gate A, skills v2 (1a/1b/2/2q/3), dual-package prompts + refs_manifest, QC-retry wiring, and a first full live run completed end-to-end (Gate A → episode.md). Runs via `python -m pipeline run/choose/status/resume`.

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
- **Stage-7 output:** `prompts.json` + per-scene `prompts/scene_NN.{seedance,omni}.json` + `refs_manifest.json` (scene → reference assets; character `binds` resolve to `resources/<Name>/` images via umlaut-folded match, style/audio `pending` until C1/C3).
- **QC-fail retry:** on failure, `cli.py` re-runs stage 5 once with the judge's feedback, re-judges, then proceeds regardless (verdict always recorded — no thrashing).
- **Cost tracking:** `ledger.add_cost` uses a per-model-tier cents/token rate table (Sonnet 5 $3/$15, Haiku 4.5 $1/$5 per M) — priced at whichever model actually ran each call.
- **Governance:** every skill/canon file carries a `version:` header; the `/tune` ritual edits exactly one owning file + bumps its version.

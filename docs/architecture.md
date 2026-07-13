# Architecture

> Living doc — updated after every structural change. Full rationale: `planning/PROJECT_SPEC_Engineering_Requirements.md`.

## System overview (target, MVP)

- **Nightly pipeline (n8n, Docker on Mac):** Supabase "next 10 unseen words" → Claude Sonnet 5 (story + 10-scene script JSON, validate→retry) → per-scene video generation (model TBD via prototyping) → Creatomate assembly → videos to Supabase Storage, session row to Postgres.
- **Session app (React + Vite PWA, Vercel):** reads session from Supabase → word card → recall → reveal + self-grade (written back) → scene video → story finale.
- **Single meeting point:** pipeline and app never talk directly; Supabase is the interface. Word source is a DB query (AnkiConnect swaps in at v1).

## Current state

B0 + B1 complete — n8n (Docker, persistent) serves webhook workflows; Supabase holds the 605-word deck with `introduced_on` tracking; `B1 Next Words` workflow fetches-and-stamps the next 10 unseen words.

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

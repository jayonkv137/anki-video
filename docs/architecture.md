# Architecture

> Living doc — updated after every structural change. Full rationale: `planning/PROJECT_SPEC_Engineering_Requirements.md`.

## System overview (target, MVP)

- **Nightly pipeline (n8n, Docker on Mac):** Supabase "next 10 unseen words" → Claude Sonnet 5 (story + 10-scene script JSON, validate→retry) → per-scene video generation (model TBD via prototyping) → Creatomate assembly → videos to Supabase Storage, session row to Postgres.
- **Session app (React + Vite PWA, Vercel):** reads session from Supabase → word card → recall → reveal + self-grade (written back) → scene video → story finale.
- **Single meeting point:** pipeline and app never talk directly; Supabase is the interface. Word source is a DB query (AnkiConnect swaps in at v1).

## Current state

B0 (engine heartbeat) complete — n8n runs in Docker with persistent storage and serves a webhook-triggered workflow. Data layer (B1) not started.

## Components

### n8n engine (B0)
- **Runtime:** Docker container `n8n` from `docker.n8n.io/n8nio/n8n`, detached, `-p 5678:5678`.
- **Persistence:** named volume `n8n_data` → `/home/node/.n8n` (SQLite DB + workflows + credentials). Survives container restart/recreate; this is why n8n data is not lost on `docker restart`.
- **Workflows as code:** exported to `workflows/*.json` in the repo (the repo, not the running instance, is the source of truth). Import: `docker cp` → `docker exec n8n n8n import:workflow --input=...`.
- **First workflow:** `workflows/b0-heartbeat.json` — Webhook → HTTP Request → Respond. Production webhook (active workflow) at `http://localhost:5678/webhook/heartbeat`.
- **Restart recipe (upgrade-safe):** `docker rm` the container, `docker run` a new one on the same `n8n_data` volume — workflows persist.

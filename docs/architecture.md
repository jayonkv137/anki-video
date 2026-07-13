# Architecture

> Living doc — updated after every structural change. Full rationale: `planning/PROJECT_SPEC_Engineering_Requirements.md`.

## System overview (target, MVP)

- **Nightly pipeline (n8n, Docker on Mac):** Supabase "next 10 unseen words" → Claude Sonnet 5 (story + 10-scene script JSON, validate→retry) → per-scene video generation (model TBD via prototyping) → Creatomate assembly → videos to Supabase Storage, session row to Postgres.
- **Session app (React + Vite PWA, Vercel):** reads session from Supabase → word card → recall → reveal + self-grade (written back) → scene video → story finale.
- **Single meeting point:** pipeline and app never talk directly; Supabase is the interface. Word source is a DB query (AnkiConnect swaps in at v1).

## Current state

Nothing built yet — repo scaffolded 2026-07-13, Claude Code setup phase in progress.

## Components

*(filled in as they come into existence)*

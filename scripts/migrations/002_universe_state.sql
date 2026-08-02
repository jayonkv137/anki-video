-- 002 — UNIVERSE_STATE strata 2–4 (DESIGN_universe_state.md §5 · BUILD_PLAN_v4 §6)
-- Run once in the Supabase SQL Editor (Dashboard → SQL Editor → New query),
-- exactly like 001_ledger_tables.sql. Then: .venv/bin/python -m pipeline state-verify
--
-- Stratum 1 (immutable canon)  = files + git (REGISTRY-pinned) — no table.
-- Stratum 5 (the plan)         = resources/curriculum.json — no table;
--   its live status is DERIVED from universe_progression (kind='atom_taught'),
--   so there is exactly one source of truth for what has been taught.

-- Stratum 2 — mutable world state (characters, locations, relationships,
-- tonal modes, directions, canon facts). One row per entity, upserted.
create table if not exists universe_world (
  id          uuid primary key default gen_random_uuid(),
  entity_type text not null,   -- character | location | relationship | tonal_mode
                               -- | direction | canon_fact | world
  entity_key  text not null,   -- e.g. 'Rolf die Wurst', 'Rolf die Wurst|Müller das Brot',
                               -- 'supermarket', 'Supermarket Fluorescent', a slug
  data        jsonb not null default '{}'::jsonb,
  updated_at  timestamptz not null default now(),
  unique (entity_type, entity_key)
);

-- Stratum 3 — the progression log (append-only).
create table if not exists universe_progression (
  id          uuid primary key default gen_random_uuid(),
  episode_ref text,            -- ep_<run_id> directory name
  kind        text not null,   -- episode_made | atom_taught | appearance
                               -- | story_beat | stereotype_encounter | thread
  ref         text,            -- atom id / canonical name / stereotype id / thread slug
  detail      jsonb not null default '{}'::jsonb,
  created_at  timestamptz not null default now()
);
create index if not exists idx_uprog_kind_ref on universe_progression (kind, ref);
create index if not exists idx_uprog_episode on universe_progression (episode_ref);

-- Stratum 4 — decisions & constraints (approvals bind; rejections persist).
create table if not exists universe_decisions (
  id         uuid primary key default gen_random_uuid(),
  kind       text not null,             -- approval | rejection | taste
  scope      text not null default 'global',  -- global | character | location | stage
  scope_key  text,                      -- canonical name / location key / stage name
  rule       text not null,             -- the constraint, as an injectable sentence
  source     text,                      -- episode_ref or chat reference
  active     boolean not null default true,
  created_at timestamptz not null default now()
);
create index if not exists idx_udec_active_scope on universe_decisions (active, scope, scope_key);

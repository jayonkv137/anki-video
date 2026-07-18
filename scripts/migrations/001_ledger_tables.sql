-- E3: Ledger + Series Memory tables
-- Run this in Supabase SQL Editor or via the migration script.

-- 1. RUNS — one row per pipeline run
CREATE TABLE IF NOT EXISTS runs (
    id              uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    started_at      timestamptz NOT NULL DEFAULT now(),
    status          text NOT NULL DEFAULT 'init'
                    CHECK (status IN ('init','running','awaiting_choice','completed','failed','cancelled')),
    stage           text,                           -- current/last stage name
    word_positions  int[],                          -- the 10 word positions for this run
    canon_versions  jsonb DEFAULT '{}'::jsonb,       -- {"MISSION.md": "1.0", ...}
    chosen_option   int,                            -- 1/2/3 after Gate A choice
    choice_note     text,                           -- optional steering note from Jayon
    cost_cents      int DEFAULT 0,                  -- running total
    error_detail    text,
    completed_at    timestamptz
);

-- 2. RUN_EVENTS — one row per stage completion/attempt
CREATE TABLE IF NOT EXISTS run_events (
    id              bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    run_id          uuid NOT NULL REFERENCES runs(id) ON DELETE CASCADE,
    stage           text NOT NULL,                  -- 'init','words','story_options','gate_a','story_expand','screenplay','quality_check','prompts','finalize'
    status          text NOT NULL DEFAULT 'started'
                    CHECK (status IN ('started','completed','failed','retried')),
    artifact_path   text,                           -- relative path to output file
    artifact_sha256 text,                           -- hex digest
    tokens_in       int DEFAULT 0,
    tokens_out      int DEFAULT 0,
    detail          jsonb DEFAULT '{}'::jsonb,       -- stage-specific metadata
    created_at      timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_run_events_run_id ON run_events(run_id);

-- 3. EPISODES — series memory (one row per completed episode)
CREATE TABLE IF NOT EXISTS episodes (
    id              bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    run_id          uuid REFERENCES runs(id),       -- nullable for migrated legacy episodes
    title_de        text NOT NULL,
    scenario        text NOT NULL,
    environment     text,
    mains           text[] NOT NULL,                -- e.g. {"Kati die Kartoffel","Rolf die Wurst"}
    cameos          text[] DEFAULT '{}',
    word_positions  int[] NOT NULL,
    verdict         text DEFAULT 'pending'          -- 'approved','rejected','pending'
                    CHECK (verdict IN ('approved','rejected','pending')),
    created_at      timestamptz NOT NULL DEFAULT now()
);

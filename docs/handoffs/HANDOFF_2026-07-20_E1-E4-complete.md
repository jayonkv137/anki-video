# Handoff Packet — 2026-07-20 (E1–E4 Complete)

> **From:** Antigravity / Opus session
> **To:** Next session (Fable or any model)
> **Priority:** Continue E5–E7 from EXECUTION_PLAN_text_pipeline.md

---

## What was accomplished

Tasks E1–E4 of the execution plan are done and committed. The pipeline package is live.

| Task | Commit | What |
|---|---|---|
| E1 | `fd05ec0` | Distilled prompting canon: `prompting_guidelines_seedance.md` (88 lines) + `prompting_guidelines_omni.md` (101 lines). Jayon approved. |
| E2 | `c606463` | `MISSION.md` (project soul, 29 lines) + `REGISTRY.md` (SHA-256 hash verification for all 5 canon files). |
| E3 | `7242919` | Supabase tables: `runs`, `run_events`, `episodes`. SQL migration + round-trip test passed. `episode_log.json` migrated. |
| E4 | `cda8d69` | `pipeline/` package: `rcp.py`, `ledger.py`, `stages.py`, `cli.py`. Gate A pause verified live. |

## Repo state (verify these)

```
git log --oneline -6

cda8d69 feat: E4 — pipeline package refactor (rcp, ledger, stages, cli) with Gate A pause
7242919 feat: E3 — ledger + series memory tables (runs, run_events, episodes) + migration
c606463 feat: E2 — MISSION.md + canon REGISTRY with SHA-256 hash verification
fd05ec0 feat: E1 — distill prompting canon (Seedance 2.5 + Gemini Omni Flash guidelines)
747e551 docs: text-pipeline v2 execution plan (E1-E7 for Antigravity) + /tune skill + ...
ef55387 chore: context handoff 2026-07-17 — transfer packet + status pointer
```

## Key files created/modified

### New files (E1–E4)
- `prompts/canon/prompting_guidelines_seedance.md` — Seedance 2.5 rules (88 lines)
- `prompts/canon/prompting_guidelines_omni.md` — Gemini Omni Flash rules (101 lines)
- `prompts/canon/MISSION.md` — Project mission (29 lines)
- `prompts/canon/REGISTRY.md` — SHA-256 canon hash registry
- `scripts/migrations/001_ledger_tables.sql` — Supabase DDL for runs/run_events/episodes
- `scripts/migrations/run_migration.py` — Migration + round-trip test script
- `pipeline/__init__.py` — Package init
- `pipeline/__main__.py` — `python -m pipeline` entry point
- `pipeline/rcp.py` — Run Context Pack builder (canon loader + hash verifier + series memory)
- `pipeline/ledger.py` — Supabase CRUD for runs/events/episodes + cost tracking
- `pipeline/stages.py` — Pure stage functions (words → options → expand → screenplay → QC → prompts → finalize)
- `pipeline/cli.py` — CLI commands: run / choose / status / resume

### New files (Jayon's parallel session — learning system)
- `.agents/skills/learn/SKILL.md` — /learn skill definition
- `docs/learning_system/README.md`
- `docs/learning_system/LEARNING_LEDGER.md`
- `docs/learning_system/db_ledger_visualizer.html`
- `CLAUDE.md` — added `/learn` command

## Live state

- **Test run `e0c04e38`** paused at Gate A in Supabase `runs` table. Words: [27, 44, 62, 80, 189, 290, 394, 474, 495, 575]. `output/episodes/ep_27-575/options.md` has 3 story options. This can be continued with `python -m pipeline choose <1|2|3>` or ignored (it's a test run).
- **Supabase tables** (`runs`, `run_events`, `episodes`) are live. 1 episode in series memory ("Kati und der Handtuch-Krieg").

## What to do next: E5–E7

Source of truth: `docs/planning/EXECUTION_PLAN_text_pipeline.md`

### E5 — Skills v2
- Skill-1a (options writer) already works (tested in E4)
- Skill-1b (story expand from chosen premise) already works in stages.py — but the skill prompt needs formal splitting
- **Quality-check skill** — new, use Haiku 4.5 for cost efficiency
- **Skill-3 v2** — rewrite for dual Seedance/Omni prompt packages with reference-role mapping per the new canon guidelines

### E6 — Full end-to-end test
- `pipeline run` → choose → all stages → `episode.md` produced
- Verify all ledger entries, cost tracking, artifact hashes

### E7 — Three proof runs
- 3 full batches whose stories Jayon approves = text pipeline win condition

## Working agreement reminders

- "Success = Jayon's understanding, not shipped code."
- One step at a time, phases discussed and explicitly locked.
- Model tiers: Opus for architecture, Sonnet 5 for creative stages, Haiku 4.5 for chores/quality checks.
- `/pickup` ritual at session start: read newest handoff + verify.
- n8n port is C4 (after text pipeline is proven) — don't port yet.
- Original `scripts/generate_episode.py` is still there as the v1 reference — don't delete it.

## Cost model

Current pipeline cost per episode (text only, no video):
- `pipeline run` (3 story options): ~19k tokens → ~$0.15
- `pipeline choose` (expand + screenplay + prompts): ~3 more LLM calls → ~$0.30-0.50
- Total per episode: **~$0.50-0.70** in Anthropic API costs
- Model: Claude Sonnet 5 (claude-sonnet-5) at $3/M in, $15/M out

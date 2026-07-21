# Connecting the Real APIs — the "last mile"

> How the fully-automated end-to-end pipeline connects to real external services.
> **Design principle:** every external step has a `mock` provider (runs now, free, no keys)
> and a `real` provider behind the SAME interface — swapping is a one-key change, never a rewrite.
> The pipeline runs 100% automated TODAY on mock; each real API turns on when you add its key.

## The full automated chain (all commands are hands-off)

```
pipeline run --random            # words → 3 story options → GATE A pause   (real: Anthropic ✓)
pipeline choose 2 --note "…"     # expand → screenplay → QC → dual prompts   (real: Anthropic ✓)
pipeline autopilot <run_id>      # generate clips → assemble+subtitles → caption
```
`autopilot` = `generate` → `assemble` → `caption` in one background run. Dashboard has one-click buttons for all of it (New Run, Gate A choose, ⚡ Autopilot).

## Providers & the keys YOU add

| Step | Provider file | mock (now) | real | Key in `.env` | Notes |
|---|---|---|---|---|---|
| **LLM stages** (story/screenplay/QC/prompts/caption) | pipeline (Anthropic) | — | **live already** | `ANTHROPIC_API_KEY` | fully working |
| **Video generation** | `pipeline/providers/video.py` | placeholder clips w/ scene info | Seedance via **fal.ai** | `FAL_KEY` | `pip install fal-client`; ⚠ confirm the Seedance model slug + arg names against current fal.ai docs (these models are newer than the adapter) — set `FAL_SEEDANCE_MODEL` if different |
| **Audio (voices)** | *(M3, adapter next)* | silent / clip audio | ElevenLabs Multilingual | `ELEVENLABS_API_KEY` | per-character voices from the bibles' "Customize Performance" text |
| **Subtitles + editing** | `pipeline/assemble.py` | — | **live already** (ffmpeg, local) | — | burns DE+EN subs from screenplay, normalizes to 1080×1920@30, concats |
| **Posting** | *(M6, adapter next)* | writes caption.md | Instagram Graph API | `IG_USER_ID` + `IG_ACCESS_TOKEN` | needs an IG Business account + Meta app; you create the page |

## To see REAL Seedance video (step by step)

1. Create a fal.ai account → get an API key.
2. `echo 'FAL_KEY=xxxx' >> .env`  and  `.venv/bin/pip install fal-client`.
3. Confirm the current Seedance route on fal.ai; if it differs from the default in `video.py`,
   add `FAL_SEEDANCE_MODEL=fal-ai/…` to `.env`.
4. `pipeline generate <run_id> --provider fal`  (or the dashboard "real Seedance" button).
   → real clips land in `output/episodes/<ep>/clips/`, then `assemble` burns subtitles over them.
5. First real run is the moment we verify the exact fal schema together and fix any arg-name
   mismatch — that's the only unknown, and it's a 2-line change in `FalVideoProvider.generate`.

## Why not n8n?
n8n was the original orchestration engine (old phase C4). The Python `pipeline/` package + the
dashboard already do everything n8n would (chaining, gates, state, artifacts, cost). n8n's only
remaining value is a daily **scheduler** and a visual diagram — a thin cron (Python `schedule`
or the dashboard) covers scheduling. It's optional, not a missing piece.

## Honesty note
Real-API adapters are written against the standard SDK flow for each service but are **untested
until you add the key + credits** — the first real call is where we confirm exact schemas. Mock
mode is fully tested and proves the orchestration end-to-end.

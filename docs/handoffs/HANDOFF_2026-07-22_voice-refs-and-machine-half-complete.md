# Handoff Packet — 2026-07-22

## Objective / non-goals
Build the entire machine-executable half of the MVP (video gen → assembly → caption → dashboard) and incorporate per-character voice references — while deliberately NOT touching story/curriculum quality (parked, idea #16) until the full loop is proven end-to-end.

## Exact position
- **C2 (screenplay chain):** E1–E6 done. Multiple full live runs completed.
- **C3 (video):** provider system built (`pipeline/providers/video.py` — `mock` + `fal`, key-gated). Voice refs incorporated (Path A). **Real fal.ai call never executed — unverified.**
- **C5 (assembly):** `pipeline assemble` built, mock-proven end-to-end (69s subtitled video, frame-verified).
- **C6 (publish):** caption (skill-4) built. Command Center dashboard (M7) built + browser-verified. No real IG posting adapter yet.
- **M1 (Jayon's manual Seedance visual test):** IN PROGRESS — awaiting his results.

## Files touched this session (aggregate — see `git log --oneline` for full commit list, HEAD=`7ebe606`)
`pipeline/{stages,cli,ledger,assemble.py(new)}`, `pipeline/providers/` (new dir), `dashboard/` (new: app.py + static/index.html), `prompts/skills/skill-{1a,1b,2,2q,3,4}*`, `prompts/canon/{canon_blocks,prompting_guidelines_seedance,prompting_guidelines_omni,REGISTRY}.md`, `resources/*` (bibles + 4 new voice `.mp3`s, now git-tracked), `docs/planning/{MVP_ROADMAP_command_center,REAL_API_CONNECTION,RESEARCH_market_and_prior_art,VOICE_REFS_INCORPORATION_PLAN}.md` (all new).

## Decisions made + why
- **Prove full loop (→ posted video) before story-quality iteration** — Jayon's explicit call; see `MVP_ROADMAP_command_center.md` §1.
- **Puppet → photorealistic CGI visual pivot** (Jayon's 3 research docs) — `canon_blocks.md` v1.0, material laws per character, Constants-vs-Variables (lighting is per-scene, not canon).
- **Voice refs: Path A now** (image+voice direct to Seedance per scene), **Path B later** (per-scene ElevenLabs dialogue → master track) — see `VOICE_REFS_INCORPORATION_PLAN.md`. Jayon's explicit choice.
- **n8n deemed unnecessary** — the Python pipeline + dashboard already orchestrate; n8n would be a redundant wrapper (`REAL_API_CONNECTION.md`).

## UNVERIFIED assumptions (do not trust without re-checking)
- **skill-3 v3.1's voice-binding output was never LLM-generated live.** `flashboard_voice.md`'s 10 prompts were deterministically hand-transformed (regex) from OLDER pre-voice prompts, NOT natively produced by the updated skill. First live regen will prove/disprove the actual skill output shape.
- **`FalVideoProvider`'s model slug + arg names (`image_urls`, `audio_urls`) are unverified** against fal.ai's current API — written to the standard SDK pattern, flagged `⚠ CONFIRM` in the code itself.
- **Run `575d3158` / episode `ep_14-456`** exists completed in the ledger (canon versions 2.0/1.1 — between the visual pivot and voice-refs commits) with no clear recollection of creating it this session. Text artifacts exist, no clips/video. Origin unclear — don't assume its content was reviewed.
- Jayon's Flashboard visual-test results (M1) — **not yet reported back.**

## Commands run + real results
- `git log --oneline -20` → HEAD `7ebe606`, 22 commits ahead of `origin/main`, **nothing pushed this session**.
- `verify_canon()` → PASS, all 5 files (seedance 2.1, omni 1.2, canon_blocks 1.0, MISSION 1.0, main-sheet 1.3).
- Voice resolver test → all 4 characters resolved to real `.mp3` paths (umlaut-folded).
- Live Anthropic call for prompt regen → **FAILED**: `400 invalid_request_error: Your credit balance is too low to access the Anthropic API.` Hard blocker on ALL further LLM stages.
- Mock autopilot (earlier, ep_22-499) → 10 clips → 69.1s subtitled `final.mp4`, frame-verified.
- Fresh run `51cc85bb` (ep_54-564, "Der fünfzigste Spieltag") → completed, $1.64, QC failed twice and proceeded per design (no-thrash rule).

## Failures distilled
- Live voice-binding regen → failed: **Anthropic account out of credits.** Top up before any `run`/`choose`/regen/caption.
- 4/10 Seedance prompts exceeded 3000-char cap on 2-char scenes (CGI char blocks ~3× longer than old puppet blocks) → fixed with skill-3 budget rule + code warning, but this episode's exports still needed manual trim — a permanent skill-3 `/tune` for voice+dual-image scenes is still owed.
- `ledger.add_cost` was silently 10× wrong since E1–E4 (cents math ÷100 not ÷1000) → fixed.
- `choose`/`resume` reloaded wrong words for `--random` runs → fixed (`fetch_words_by_positions`).

## Open risks
- Haiku QC (skill-2q) keeps failing on dialogue-naturalness/voice-consistency nits across multiple runs and proceeding by design — accumulating signal that skill-2 itself needs a `/tune`, not just per-episode fixes.
- Bert's canon literally says "felt hat" while the AVOID list bans "felt" — untested collision.
- Real fal.ai schema drift risk (unverified adapter).

## Next 3 steps
1. **Jayon: report Flashboard results** from `output/episodes/ep_54-564/flashboard_voice.md` (10 voice+dual-image prompts, no style ref). Pass → continue; fail → `/tune canon_blocks` v1.1.
2. **Top up Anthropic credits**, then verify skill-3 v3.1 natively emits voice bindings (regen stage 7 on an existing screenplay — don't trust the hand-transformed file).
3. Once M1 passes: style-lock image (C1 close) → verify a real `FAL_KEY` Seedance call end-to-end → judge Path A quality vs escalate to Path B.

## Reread-first list
1. `docs/project_status.md` (Where we left off)
2. `docs/planning/MVP_ROADMAP_command_center.md`
3. `docs/planning/VOICE_REFS_INCORPORATION_PLAN.md`
4. `prompts/skills/skill-3-prompt-writer.md` (v3.1, just changed)
5. `output/episodes/ep_54-564/flashboard_voice.md` (artifact awaiting judgment)
6. `prompts/canon/REGISTRY.md` (verify_canon must stay green)

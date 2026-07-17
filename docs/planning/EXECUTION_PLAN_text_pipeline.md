# EXECUTION PLAN — Text Pipeline v2 (words → chosen story → screenplay → dual video-prompts)

**Date:** 2026-07-18 · **Status:** LOCKED scope for the next build push · **Executor:** Antigravity (Claude Opus 4.6) + Jayon, guided by this document. **Single source of truth for this build** — other docs point here.
**Scope ends at prompt packages.** Video generation (C3) starts only after this pipeline reliably produces stories Jayon approves.

---

## 1. Architecture decisions (Jayon's questions, answered)

**A. Does the run need a "purpose/initialization"? YES — and it is Stage 0, BEFORE word collection.** Every run begins by assembling the **Run Context Pack (RCP)** — the same "creator's mind" injected into *every* LLM stage of that run:

```
RCP = MISSION.md (what this automation is: objective, values, standards, vision)
    + Characters-Main-Sheet.md (behavior bible)
    + canon_blocks.md (style + visual identity)
    + prompting guidelines (distilled from Jayon's two research files)
    + SERIES MEMORY digest (last 5 episode summaries + aggregates: scenarios used,
      character-intro state, running gags, known-weak patterns)
    + LAST RUN status (from the run ledger: completed? where did it stop?)
```

**B. One sustained LLM conversation per run? NO — deliberately not**, and Jayon's own context-rot research is the reason: a single long thread accumulates dilution, distraction and poisoning across stages. Instead: **stateless stage calls that all receive the identical RCP**. Same awareness as "one human creator who knows everything from the get-go" — but fresh, undiluted attention per stage, reproducible, and testable in isolation. The RCP *is* the sustained context; the ledger *is* the long-term memory.

**C. Prior art (established patterns; Antigravity verifies details during build):** MemGPT/Letta memory hierarchies (working vs archival memory ≈ RCP vs ledger), the Cline/Cursor "Memory Bank" pattern (markdown canon read at every session start), LangGraph checkpointers (run state persisted per thread ≈ our ledger + resume), CrewAI shared crew memory. Our design is a disciplined composite of these, file-and-Supabase-based.

**D. History system — two layers, both verifiable:**
- **RUN LEDGER** (Supabase `runs` + `run_events`): every run, every stage: status, artifact paths + SHA-256 hashes, token cost, gate decisions, errors, timestamps. A run can be resumed at any stage (ledger says where it stopped).
- **SERIES MEMORY** (Supabase `episodes`): one row per completed episode (title, scenario, cast, word positions, Jayon's verdict). A digest builder compresses this into the RCP (never the full history — rot prevention).

## 2. The pipeline (stages, exactly)

```
0 INIT (code, no LLM): open run in ledger → assemble RCP → verify canon files exist (hash-check vs registry)
1 WORDS: next-10-unseen (existing B1 logic) → recorded in ledger
2 STORY OPTIONS (skill-1a · Sonnet 5): THREE premise options — each: title_de, scenario,
  environment, mains, hook_visual, human_beat, 4-beat sketch, word-fit notes, self-score.
3 ═ GATE A — JAYON CHOOSES ═ options written to output/…/options.md; pipeline PAUSES
  (state saved). Jayon: `pipeline choose <1|2|3> [--note "…"]` (note steers expansion).
  MVP = CLI/file gate; n8n-webhook/Telegram version later (C4).
4 STORY EXPAND (skill-1b · Sonnet 5): chosen premise + note → full 12–16 beats + word_plan
  (current skill-1 output shape).
5 SCREENPLAY (skill-2 · Sonnet 5): as built, PLUS per-scene `required_refs` field
  (which character refs this scene needs) — the format is designed FOR prompt generation.
6 QUALITY CHECK (skill-2q · Haiku 4.5 first, upgrade if rubber-stamping — risk R10):
  code validators (word coverage, Müller budget — existing) + LLM checklist: grammar
  flawless? sentences natural-everyday? voices unswappable? hook muted-readable? human beat?
  single environment? filmable actions? → PASS or feedback → ONE retry of stage 5.
7 PROMPT WRITER (skill-3 v2 · Sonnet 5): per scene, TWO separate packages:
  • SEEDANCE package — prompt ≤3000 chars; subject+core action inside the FIRST 20–30
    words; no adjective stacking; explicit reference-asset map with roles
    [{slot, file_path, role: identity|style|motion|audio}] — character refs + style ref
    ALWAYS mapped; obeys prompts/canon/prompting_guidelines_seedance.md.
  • OMNI package — base-generation prompt + ORDERED edit-turn plan (stateful Interactions
    API via previous_interaction_id: generate base → refinement commands), ref image list
    (≤10); obeys prompting_guidelines_omni.md.
  Output: output/episodes/<run_id>/prompts/scene_NN.seedance.json + scene_NN.omni.json
  + refs_manifest.json (scene → absolute file paths into resources/).
8 FINALIZE (code): ledger → complete; episode row → series memory; pretty episode.md;
  cost summary printed.
```

## 3. The change-management system (the /tune loop)

Every behavior lives in a **versioned file** (skills, canon, checklists, MISSION — each carries a `version:` header). When Jayon spots a pattern to change: `/tune "<observation>"` → locate the ONE owning file → edit + bump version + changelog line → **regression run**: re-run the pinned GOLDEN BATCH (fixed word set, seeded) and diff against `episodes/episode-01.md` standards + the previous golden output → Jayon approves → commit. No silent prompt edits, ever. Ledger records which canon versions each run used → any quality shift is traceable to a version change.

## 4. Antigravity execution tasks (do IN ORDER; one commit per task; verify before next)

**Session opening prompt for Antigravity:** *"Read CLAUDE.md, docs/handoffs/ (newest), and docs/planning/EXECUTION_PLAN_text_pipeline.md. Verify repo state per the handoff packet. Then execute task E1, and stop for review."* — Model: Claude Opus (Sonnet acceptable for E3/E4 mechanical parts).

- **E1 — Distill prompting canon.** Read `resources/AI Prompting Consistency Research.md` + `resources/Seedance Gemini Omni German Dialogue.pdf` → produce `prompts/canon/prompting_guidelines_seedance.md` and `prompts/canon/prompting_guidelines_omni.md` (≤80 lines each: only actionable rules — syntax, ordering, limits, ref-mapping, German-dialogue technique, DON'Ts). ✓ Done when: both files exist, every rule traceable to the source docs, Jayon skims and approves.
- **E2 — Mission + canon registry.** Create `prompts/canon/MISSION.md` (≤40 lines, distilled from PROJECT_GOAL_AND_MILESTONES.md §1–3: what this automation is, quality bar, values, universe vision) and `prompts/canon/REGISTRY.md` (list of all canon files + versions + hashes). ✓ RCP builder can load and hash-verify everything.
- **E3 — Ledger + memory tables.** Supabase SQL: `runs` (id, started_at, status, stage, canon_versions jsonb, cost_cents), `run_events` (run_id, stage, status, artifact_path, artifact_sha256, tokens_in, tokens_out, detail jsonb, at), `episodes` (run_id, title_de, scenario, environment, mains text[], cameos text[], positions int[], verdict, created_at). Migrate `output/episodes/episode_log.json` → `episodes`. ✓ Insert+select round-trip proven from Python.
- **E4 — Pipeline package refactor.** `scripts/generate_episode.py` → `pipeline/` package: `rcp.py` (pack builder + digest), `ledger.py`, `stages.py` (one function per stage, resumable), `cli.py` (`run [--start|--random|--note]`, `choose <n> [--note]`, `status`, `resume <run_id>`). Keep: structured-output schemas, streaming, validators, canon substitution (fuzzy match), 16k+ max_tokens lesson. ✓ `pipeline run` reaches Gate A and pauses; `status` shows ledger truth.
- **E5 — Skills v2.** Split skill-1 → `skill-1a-story-options.md` + `skill-1b-story-expand.md`; write `skill-2q-quality-check.md` (binary checklist, JSON verdict); rewrite `skill-3-prompt-writer.md` per E1 guidelines (dual packages, ref-role mapping, Seedance first-30-words law, Omni edit-turn planning). All keep the Naming Law + placeholder discipline (code injects canon). ✓ Each skill has version header; dry prompts read clean.
- **E6 — Gate A end-to-end.** `pipeline run` → options.md written, run paused (ledger: `awaiting_choice`); `pipeline choose 2 --note "..."` → resumes 4→8 automatically. ✓ Full run with a real choice completes; artifacts + refs_manifest correct; hashes in ledger.
- **E7 — Proof + doc sync.** Three full runs on different batches (Jayon judging at Gate A and the end). Fix what he flags via /tune loop. Update changelog, project_status, architecture.md (pipeline package section). ✓ = **C2 win condition: 3 batches whose stories Jayon approved.**

**Jayon's parts:** choose at every Gate A · judge episodes · approve E1 distillations · (parallel, unblocked) STYLE_SYSTEM sheet + humans-in-world decision + Flow Episode-01 shoot.

## 5. Risks specific to this build
Ledger/gate resume logic is the new complexity center — keep stages pure functions over (RCP, inputs)→artifact, so resume = re-dispatch by ledger state. Don't let Antigravity "improve" scope (no video calls, no n8n port yet — that's C4 with this exact structure). If any stage misbehaves twice → stop, record in handoff, don't thrash (context-rot rule).

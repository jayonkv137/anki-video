# DESIGN — Story-Ideation Mechanism + the Overseer Agent

> **Status: DESIGN (2026-07-23).** Fixes the core co-creation mechanism (Jayon: "this story-idea phase is the most important; the design needs to be well-designed") and lays out the always-present **overseer agent** vision. Basis: `RESEARCH_story_ideation_agent.md`, `RESEARCH_cocreation_system_design.md`, `DESIGN_v3_data_flow.md`.

## Part A — The story-idea mechanism (the fix, now)

**Problem today:** two forked co-creations — the governed skills (`skill-1a/1b/1c`) *and* a thin inline chat prompt in `dashboard/app.py`. The live chat bypasses the skills, so the **pedagogy + constraints are lost** and logic lives in two places.

**Fix:** ONE mechanism — the **Story Strategist** (`skill-1-story-strategist.md`). A Socratic creative partner that:
- carries the **full context** every turn (cast, stereotype, seed, CEFR, teaching intent, series memory) — *server-injected, invisible in the chat bubbles* (context isolation);
- **enforces our constraints** via Elenchus (2–3×15s segments · ≤2 speakers · CEFR caps · stereotype-shown-not-explained · lesson-emerges-naturally);
- **draws out the human's ideas** (Maieutics) and offers **generative option-widgets** (Dialectic) — the current chat's widget pattern, kept + strengthened;
- moves through a **soft phase spine** (Hook → Arc → Beats → Verify) with a "just draft it" escape hatch;
- **exits deterministically**: only on explicit human approval (`ready_to_commit`), the app runs the commit/extract step → the existing **`STORY_BRIEF_SCHEMA`** → locks the idea → hands to the screenplay writer.

This **unifies** `skill-1a-align`/`1b-diverge`/`1c-commit` into the Strategist (the chat) + a commit/extract that still yields the Story Brief. The Brief schema and everything downstream are unchanged.

**Handoff choice (safer than the research's model tool-call):** keep the human-clicked **"Lock Brief"** → a `/commit` endpoint that extracts the `STORY_BRIEF` from the locked conversation. The human decides when to lock (reflective friction), and extraction is deterministic — more reliable than a model-initiated tool-call, and it fits our FastAPI+Gemini stack.

**Wiring note:** the mechanism (the skill) is independent of persistence and can be fixed now. To make the commit *stick* (write `brief.json`, create a run, `mark_covered`), the chat endpoint must call the real stage/commit + ledger — that's the UI↔pipeline connection (deferred, but required before the overseer).

## Part B — The Overseer Agent (the always-present editor)

**The vision (Jayon):** one full-context agent, present at *every* stage, that the human can talk to at any point to make a change that lands in the *right place* — e.g. after the screenplay, "change this shot" → the agent edits the screenplay shot and re-runs just the affected storyboard panel + Seedance prompt.

**Is it feasible? YES — and our architecture is what makes it possible.** The overseer is only tractable because we built the **lock + compiler** design: the screenplay is the single source of truth, and everything downstream (storyboard, prompts) is a *deterministic compile* from it. So a change has a **well-defined downstream recompile set** — the dependency graph:

```
Story Brief ──▶ Screenplay (the LOCK) ──▶ Storyboard panels ──▶ Seedance prompts
     edit brief → rebuild screenplay → rebuild affected panels → rebuild affected segment prompts
```

Without this design, "change any part, propagate everywhere" would be impossible. With it, the overseer is just: **edit an artifact → mark its downstream stale → recompile only the affected pieces.**

**Design:**
- **State = the run's persisted artifacts** (`brief.json`, `screenplay.json`, `storyboard.json`, `prompts.json`) + the ledger. (⇒ the overseer *requires* the pipeline to be persisted per run — the "disconnect is fine for now" stops being fine here.)
- **Tools (typed, not free-form file edits)** mapped to the dependency graph, e.g.:
  `edit_screenplay_shot(seg,shot,{fields})` · `regen_panel(seg,shot,note)` · `rewrite_segment(seg,note)` · `change_lesson(...)` · `edit_brief(...)` · `rerun_from(stage)`.
  Each tool: updates the artifact → marks downstream stale → triggers the *targeted* recompile → logs to the ledger (for undo).
- **System prompt** = the pipeline map + the dependency graph + the current run's state + the same pedagogy/constraints the Strategist uses.
- **UI** = a persistent "Director" chat panel available on every stage screen.
- **Guardrails:** typed tools only (no arbitrary writes); every edit is a ledger event (undo/audit); show the human the *diff + the affected downstream* and confirm before applying destructive recompiles.

**Stack:** a plain **Gemini/Anthropic function-calling loop** — our pipeline is a simple linear DAG, so we do NOT need LangGraph's cyclic-graph machinery. (LangGraph/`interrupt()` becomes worth it only if we later want durable, resumable multi-step edit sessions.) Gemini already does function-calling + structured output, which is all the overseer needs.

## Sequencing
1. **Now:** lock the Story Strategist mechanism (skill done) — the core the user feels.
2. **Then (connection):** wire the studio chat to the Strategist skill + a real `/commit` that writes `brief.json`, creates the run, and `mark_covered` — this persistence is the prerequisite for the overseer and for coverage/audit/resume.
3. **Then (overseer):** build the typed edit/regen tools over the persisted artifacts + the dependency graph + the always-on Director panel.

## Critical risks (design against them)
- **Socratic rigidity** — phases must be a *soft* spine (allow jumping + the "just draft it" escape), or the chat feels controlling/slow. Keep it fun and generative, not an interrogation.
- **Pedagogy drift** — the Strategist's system prompt MUST carry CEFR + shown-not-explained + lesson-emerges, or the chat produces charming-but-unteachable ideas (today's failure).
- **Overseer blast radius** — an agent that can edit anything can corrupt state; bound it to typed tools + ledger undo + confirm-with-diff, and let the dependency graph (not the model's guess) decide what recompiles.
- **Stack sprawl** — don't adopt Vercel/LangGraph just because the research uses them; adapt the *pattern* into our Python/Gemini studio. Reassess only if we want the polished streaming UX.

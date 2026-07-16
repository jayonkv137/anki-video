# The MVP Pipeline — full end-to-end map (first drawn 2026-07-17)

The complete automated flow as currently planned, words → published Instagram episode. n8n orchestrates everything; Supabase is the single state store; canon files in this repo are injected verbatim (never paraphrased) at the marked points. Two human gates. Flow (Google) is a MANUAL cockpit beside the pipeline, not a node in it (no API — see RESEARCH_google_flow.md).

```
                        ┌─────────────────────────────────────────────┐
                        │  CANON (this repo, versioned)               │
                        │  characters bible · per-char blocks ·       │
                        │  STYLE_SYSTEM block · episode template ·    │
                        │  reference images                           │
                        └──────┬───────────────┬──────────────┬───────┘
                        verbatim│        verbatim│      ref images│
                                ▼               ▼                ▼
┌──────────┐   ┌───────────────────┐   ┌──────────────────┐   ┌──────────────────────┐
│ TRIGGER   │   │ 1. WORDS          │   │ 2. STORY LLM     │   │ 3. SCREENPLAY LLM    │
│ daily /   ├──▶│ Supabase: next 10 ├──▶│ Claude Sonnet 5: │──▶│ Claude Sonnet 5:     │
│ manual    │   │ unseen (n8n,      │   │ belief-collision │   │ 10 scenes, dialogue, │
│ webhook   │   │ B1 workflow ✅)   │   │ episode, 2 chars,│   │ word placement, model│
└──────────┘   └───────────────────┘   │ A1/A2, word rules│   │ limits, shot notes   │
                                        └──────────────────┘   └──────────┬───────────┘
                                          ▲ validate→retry ▲              │
                                          └─── checklists ──┘             ▼
                                                               ┌──────────────────────┐
                                                               │ 4. PROMPT-WRITER     │
                                                               │ LLM writes ONLY       │
                                                               │ action+setting; code  │
                                                               │ concatenates canon    │
                                                               │ style+char blocks     │
                                                               └──────────┬───────────┘
                                                                          ▼
                                                          ╔═══════════════════════════╗
                                                          ║ GATE 1 — JAYON APPROVES   ║
                                                          ║ story + screenplay +      ║
                                                          ║ 10 prompts + cost estimate║
                                                          ║ (n8n Wait → approve link) ║
                                                          ╚═══════════╤═══════════════╝
                                                                      ▼ approved
┌─────────────────────────────────────────────────────────────────────────────────────┐
│ 5. SCENE GENERATION (n8n loop, per scene)                                            │
│ Gemini API: Veo 3.1 + reference images (API twin of Flow Ingredients)                │
│ — or C3 winner (LTX-2.3 / Kling / Omni-API-when-available) —                         │
│ submit → poll → download → auto-checks (duration/format) → Supabase Storage          │
└──────────────────────────────────────────┬──────────────────────────────────────────┘
                                           ▼
                          ┌────────────────────────────────┐      ┌───────────────────┐
                          │ 6. ASSEMBLY (Creatomate)       │      │ [SIDE COCKPIT]    │
                          │ subtitles/word-cards per format│      │ GOOGLE FLOW       │
                          │ → per-scene 9:16 cuts          │      │ manual mockups,   │
                          │ → combined episode             │      │ C3 style tests,   │
                          └───────────────┬────────────────┘      │ character assets, │
                                          ▼                       │ emergency retakes │
                          ╔═══════════════════════════════╗       └───────────────────┘
                          ║ GATE 2 — JAYON APPROVES       ║
                          ║ final videos + caption +      ║
                          ║ hashtags (batchable)          ║
                          ╚═══════════╤═══════════════════╝
                                      ▼ approved
                          ┌────────────────────────────────┐
                          │ 7. PUBLISH (Meta Graph API or  │
                          │ scheduler) → Instagram Reels,  │
                          │ scheduled slots                │
                          └───────────────┬────────────────┘
                                          ▼
                          ┌────────────────────────────────┐
                          │ 8. LOG + MEMORY                │
                          │ Supabase: episode row, per-    │
                          │ scene costs, gate decisions,   │
                          │ retake counts → cost telemetry │
                          └────────────────────────────────┘
```

## Stage ownership & status

| # | Stage | Tool | Status |
|---|---|---|---|
| 1 | Words | Supabase + n8n | ✅ built (B1) |
| 2 | Story | Claude Sonnet 5, structured output + semantic validation | ✅ built (B2) — needs V2 canon rewrite (C2) |
| 3 | Screenplay | Claude Sonnet 5, second pass + checklist evaluator | C2 |
| 4 | Prompt-writer | Claude + mechanical canon concatenation | C2 |
| G1 | Gate 1 | n8n Wait-node + approval webhook/link | C4 |
| 5 | Scene gen | Gemini API Veo 3.1 w/ refs (or C3 winner) | C3 decides → C4 builds |
| 6 | Assembly | Creatomate templates | C5 |
| G2 | Gate 2 | n8n Wait-node | C6 |
| 7 | Publish | Meta Graph API / scheduler (research in C6) | C6 |
| 8 | Log | Supabase | C7 |

**Key invariants:** no video spend before G1 · no publish before G2 · canon injected by CODE not LLM · every stage idempotent (safe re-runs) · every episode logged with costs. Flow sits beside the pipeline as cockpit; if Flow ever ships an API, stage 5 gains a candidate — nothing else changes.

# DESIGN — UNIVERSE_STATE (the project-context layer) · what we take from the research

> **Status: DECISIONS DRAFTED (2026-07-29), not built.** Derived from `RESEARCH_context_agent_architecture.md` (deep-research return on invideo AI's Agent Context + cross-domain memory patterns). This doc is the **filter**: what the research validates, what it fills, what we reject as over-engineering at our scale, and the resulting shape of `UNIVERSE_STATE` for the V4 universe platform. Companions: `CURRICULUM_v1_universe.md` · `DESIGN_story_ideation_and_overseer.md` · `architecture.md`.

## 1 · Headline
The research's central recommendation — **replace fragile semantic/vector retrieval with a deterministic, relational "Production State" + typed dependency resolution** — is the architecture we already chose for the *within-episode* pipeline (screenplay = lock; storyboard/prompts = compilers; Overseer resolves the recompile set from a typed graph). Its retrieval comparison rates typed dependency graphs **>95% accuracy** vs semantic vector **low-to-moderate** (attention dilution, lost-in-the-middle). **So: extend the same pattern across episodes.** `UNIVERSE_STATE` is the cross-run half of what we already do within a run.

## 2 · What it VALIDATES (already built — keep, don't rebuild)
| Ours | Research equivalent |
|---|---|
| Lock + compiler + Overseer's typed recompile set | Typed dependency graphs / screenplay→dependency-graph compilation |
| Overseer **propose → confirm → apply** | **Transactional promotion protocol** + "always ask" creator gate |
| Character sheet + portrait as identity refs (no fine-tuning) | **Asset pinning** via multi-angle turnaround sheets — invideo ships 70s films with no LoRA |
| Sheet method (one generation per segment) | Consistency via single-context generation + reference re-injection |
| Hash-pinned canon files | Immutable "source canon" stratum |
| Supabase ledger (`runs`/`run_events`/`episodes`) | Chronological progression log |
| Showrunner design (one brain, specialists downstream) | **"Creative Producer Agent" holds the vision; sub-agents inherit its parameters** |

## 3 · What it FILLS (our real gaps — the value)
Verified in code 2026-07-29: cross-run memory is only `rcp._fetch_series_memory(limit=5)`; **decision/rejection memory does not exist anywhere.**
1. **A persistent project state at all.** Five strata (adapted below) instead of "last 5 episodes".
2. **Decisions as first-class objects** — approvals become binding, rejections become persistent negative constraints injected into later generations ("settled stays settled; nothing gets reopened forty shots later"). We have `banned_terms` and canon AVOID lists, but nothing that *remembers what Jayon rejected*.
3. **Contradiction check before write** — a continuity-supervisor pass comparing a proposed state update against established canon; halt + quarantine + ask on conflict. We currently write story facts with zero validation.
4. **Visual verification before spending credits** — DINOv2 dense-feature cosine similarity vs the canonical turnaround, threshold **≥0.85**, blocking downstream renders on drift. Directly relevant the moment `FAL_KEY` goes live.
5. **Surgical source correction** — fix the *source reference asset in the context layer*, never the downstream clip. Pairs exactly with our dependency-graph recompile.
6. **Per-stage context budgets** — different token budgets + different memory slices per stage. Today we inline the whole RCP everywhere.
7. **Compaction into state cards** — raw history → high-density structured cards (their example: 75k tokens → 450). Our naive last-5 digest breaks well before episode 164.
8. **Relationship matrix as evolving state** — our bible's cast-dynamics matrix is *static*; the series premise is literally four strangers discovering each other, so relationships must be tracked as they change.
9. **Read-only global registry + per-agent workspaces** — how to add specialist agents without letting them corrupt canon.
10. **Continuity audit** of a finished cut against the shot list.

## 4 · What we REJECT / DEFER (honest scale check)
- **Vector DB / embeddings (LanceDB, cosine style retrieval): NOT NEEDED.** The research itself scopes vectors to "loose aesthetic mood boards" — we have ONE locked style, 4 characters, 164 atoms, ~30 modules. Deterministic lookup covers ~100% of our retrieval. Skip entirely; revisit only if a large freeform reference library appears.
- **SQLite as a new store: NO — we already run Postgres (Supabase).** Adopt the *schema*, not a third database. Immutable canon stays in **versioned files** (git already gives provenance + diffs + our hash-pinning).
- **A `shot_list` table: NO.** That duplicates `screenplay.json`, which is the lock. The DB tracks episode-level and decision-level records that *reference* the artifact; the artifact stays the source of truth for shots.
- **Ebbinghaus decay formula:** over-engineered. Use a flag: `canonical` (permanent) vs `episodic` (compacted after N episodes).
- **OpenTimelineIO / NLE interop:** irrelevant — we ship 30s vertical reels assembled by ffmpeg, not a DaVinci conform.
- **`location_audio_profiles` (ambient/reverb design):** defer; we have per-character voice clips and no ambient design.
- **DINOv2 verification:** adopt, but **phase 2** — it needs a local torch model, and it only pays once we're actually burning generation credits.

## 5 · The resulting shape of `UNIVERSE_STATE` (5 strata, adapted)
| Stratum | Content (ours) | Storage |
|---|---|---|
| **1. Immutable canon** | character sheets/portraits/voice clips, `canon_blocks` STYLE_BLOCK + material laws, character bible, the locked curriculum | **files + git** (hash-pinned; already exists) |
| **2. Mutable world state** | per-character: location, situation, wardrobe deltas, goals · **relationship matrix** (evolving) · established world facts | **Postgres** |
| **3. Progression log** | episodes made, blocks→atoms taught (`taught_in`), story beats, spiral recycling history, stereotype encounters used | **Postgres** (extends `episodes`) |
| **4. Decisions & constraints** | approvals (binding), rejections (persistent negatives), taste notes — scoped `global \| character \| location \| stage` | **Postgres** ← *entirely new* |
| **5. Goal/curriculum plan** | modules, 164 atoms, status `planned\|taught`, current position, guardrails per level | **`curriculum.json` + Postgres status** |

**Context assembly (per stage, deterministic):** resolve the episode's entities → pull each entity's canon refs + current mutable state → add active constraints (global + entity-scoped) → add the compacted story-so-far card + curriculum position → format to that stage's budget. No semantic search anywhere in the path.

**Write policy:** stratum 1 = human-only. Strata 2–3 = written by the finalize step, contradiction-checked first. Stratum 4 = written on explicit human approve/reject. All writes ledger-logged; the Overseer's confirm-with-diff is already the gate.

## 6 · Build order (after the curriculum lock)
1. **Postgres tables + `UNIVERSE_STATE` read/write module** (strata 2–4) + curriculum status.
2. **Decisions/constraints** wired into prompt assembly (cheapest high-value win: rejections stop recurring).
3. **Showrunner** reads the whole state; per-stage context contracts replace the blanket RCP inject.
4. **Contradiction check** before state writes.
5. **Compaction** into story-so-far cards (needed by ~episode 20–30).
6. *(Phase 2)* DINOv2 identity verification gate; continuity audit of finished cuts.

## 7 · Open questions
Where the relationship matrix is *authored* (Showrunner-proposed vs human) · whether `curriculum.json` status duplicates Postgres or Postgres is authoritative · how block-plans are persisted (new artifact vs part of the brief).

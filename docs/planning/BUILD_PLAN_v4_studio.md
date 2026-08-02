# BUILD PLAN V4 — The Studio (full-system review · contradiction audit · execution plan)

> **Status: GOVERNING BUILD DOC — APPROVED 2026-08-02 (Jayon: D1–D7 all as recommended). Phase 0 EXECUTED same day** (curriculum locked → `curriculum.json` v1.0 · nanobanana canon v1.0 · TREATMENT 1.2 / PIPELINE 1.2 / SHOW_BIBLE 1.2 / MISSION 2.1 · REGISTRY 1.14 · **NBP native-API test PASSED** — gemini-3-pro-image live on the existing GOOGLE_API_KEY, thoughtSignature returned; risk R2 cleared, images need no FAL_KEY). Written after a complete read of every document, resource, skill, and code module in this repo plus the four deep-research reports. This is the answer to: *do we have full clarity, what contradicts what, what survives from the old build, what the UI actually is, and in what order we build.*
> Companions: `docs/architecture.md` (the machine + why) · `prompts/canon/PIPELINE.md` §2.1 (the studio layer) · `DESIGN_studio_ux.md` · `DESIGN_universe_state.md` · `DESIGN_board_iteration.md` · `CURRICULUM_v1_universe.md` (v2.1 draft).
> Supersedes `BUILD_PLAN_v3.md` (historical) for all forward work.

---

## 1 · What we are building (the one-page restatement)

**Product:** a serialized German-learning series — four food characters torn from their bubble-worlds into an ordinary Germany that won't explain itself, carrying a learner A1→B1 across ~170 × 30-second vertical episodes. Load-bearing conceit: **fluent but foreign** (perfect German, zero understanding of the world; comedy = cultural decoding, never grammar failure).

**Platform:** a co-creation studio. One creator + four agents across five phases in **one continuous conversation per episode** that never resets:

| Phase | Agent | Produces (artifact) | Gate |
|---|---|---|---|
| **Idea** | Showrunner | module framing → `brief.json` | brief lock |
| **Script** | Writer | `screenplay.json` — THE LOCK | screenplay confirm |
| **Vision** | Director | sheet prompts → generated sheets → panels | sheet approval |
| **Shoot** | Director | Seedance prompts + refs manifest → clips | clip acceptance |
| **Post** | Editor | joined cut → `subtitles.json` → `final.mp4` | export |

QC never speaks (chips under the artifact). There is **no separate overseer window** — the propose→confirm→apply mechanism with graph-computed recompile sets *is the chat's change protocol*, available at every phase.

**Engineering thesis (unchanged):** consistency at scale is the whole problem. Lock+compiler · hash-pinned canon · reference images not fine-tuning · one sheet per segment.

## 2 · Sources of truth — what governs, what is history

**GOVERNING (agents/build read these):**
`prompts/canon/` — MISSION 2.0 · SHOW_BIBLE 1.1 · STORY_SYSTEM 1.0 · PEDAGOGY 1.0 · TREATMENT 1.1 · PIPELINE 1.1 · seedance 2.2 · *(new)* nanobanana · *(new)* `resources/curriculum.json`.
Design intents: `DESIGN_studio_ux` · `DESIGN_universe_state` · `DESIGN_board_iteration` · `DESIGN_stereotype_integration` · `CURRICULUM_v1_universe` (until the JSON lock, then the JSON governs).
Research feeding the build: `resources/Production Prompting Manual for Gemini 3 Pro.md` (→ becomes the nanobanana canon) · `resources/Production Engineering Guide Architectural Patterns.md` (agent runtime) · `resources/Creative AI Agents Research Report.md` (failure modes) · `resources/Cloud Infrastructure Cost Optimization Report.md` (sourcing only; treat first-party pricing as real, proxies as a ToS/custody decision, not a default).

**SUPERSEDED (must not leak into the new build):**
`Characters-Main-Sheet.md` + the four per-character bibles (→ SHOW_BIBLE §6) · `canon_blocks.md` (→ TREATMENT §10) · `prompting_guidelines_omni.md` (dead) · all 13 current skills (V3 stereotype-first) · the 7-step wizard UI · V2 code paths (`assemble.py`, `stage_finalize`, `stage_generate`, `substitute_canon`, word-deck stages) · `BUILD_PLAN_v3.md` · the five-typology table · `wardrobe_overrides` (feature removed in `7764af7`; skill-3 line is a dangling ref).

**Leak-prevention strategy:** the new studio is built as **new modules beside the old** (`pipeline/studio.py`, `pipeline/context.py`, `pipeline/universe_state.py`, new UI page). The old wizard is archived on a branch, then deleted from `main` once the new shell reaches parity. Old skills are moved to `prompts/skills/_retired/` at Phase 1 so nothing can load them by accident. The RCP stops injecting superseded documents at Phase 0 (registry surgery).

## 3 · THE CONTRADICTION AUDIT

Every document read against every other. **HARD = blocks building; SOFT = fix during the relevant phase.**

### HARD — must be resolved at Phase 0 (most need Jayon's call)

**C1 · The curriculum's word budgets contradict PEDAGOGY (and the code).**
`CURRICULUM` §1/§4: A1 ~40–75 spoken words · A2 ~60–95 · B1 ~75–110. `PEDAGOGY` §2 (hash-pinned canon): A1 ≤30 · A2 ≤55 · B1 ≤80. Code `CEFR_CAPS` agrees with PEDAGOGY.
The math sides with PEDAGOGY: at A1 pace (~80 WPM) with PEDAGOGY §3's ⅓-silence architecture, 30 seconds holds ~27 words. 75 words in 30s is ~150 WPM — native newsreader pace, impossible at A1. The curriculum's 40–75 came from generic reel guidance, not the level-adjusted numbers.
→ **Resolution: PEDAGOGY wins.** CURRICULUM v2.2 harmonizes §1 + §4 (word budgets AND the WPM rows: A2 ~100, B1 ~120–130) before the JSON lock. *Jayon confirms.*

**C2 · CURRICULUM §7 still lists the subtitle policy as open.** PEDAGOGY §5.2 locked it (static colour-coded clauses). → strike from §7 at v2.2. *No decision needed.*

**C3 · The registry pins a superseded bible, and the RCP injects it.** `REGISTRY` still pins `Characters-Main-Sheet.md` v1.3; `rcp.py` injects it (plus `canon_blocks`) into every story/screenplay call — while SHOW_BIBLE §6 explicitly supersedes it, speech constraints and all. `verify_canon()` is green *because* the wrong file is pinned. This is the MISSION-rot pattern, live right now. → Registry surgery at Phase 0: unpin Characters-Main-Sheet + canon_blocks + omni; the new context layer injects SHOW_BIBLE et al. per PIPELINE §3's read-lists. *No decision needed.*

**C4 · Two different things are named "Director".** PIPELINE §2.1: the Vision/Shoot phase agent is "Director". PIPELINE §3.9: "THE DIRECTOR (overseer)" is the edit-router. The old UI's floating window was also branded "Director". This is why the overseer keeps "appearing" in conversations — it's a naming collision, not a design ghost. `DESIGN_studio_ux` §3 already dissolved the overseer *window*; the *mechanism* (propose → show recompile set → confirm → deterministic apply) survives as the chat's change protocol.
→ **Resolution: the phase agent keeps "Director"; PIPELINE §3.9 is retitled "THE CHANGE PROTOCOL" and described as a capability of the conversation, not an agent.** `overseer.py`'s plan/apply/graph code survives as that protocol's engine. *Jayon confirms naming.*

**C5 · TREATMENT §9's reference budget and order are contradicted by NBP's real mechanics.** The manual: 14 refs split **5 human / 6 object / 3 style**; attention biased to the earliest indices; **characters must occupy indices 0–3, style refs go LAST**. TREATMENT §9.2 puts the style plate FIRST and §9.3 budgets "two characters × 3 images" = 6 human refs — over the 5-slot ceiling.
→ **Resolution (TREATMENT v1.2, a /tune):** order = Character A (sheet→portrait) · Character B (sheet→portrait) [4 human ≤5 ✓] · close-up only when ≤1 character needs reinforcing · location plate (object slot) · previous-segment sheet + style plate at the END (style slots ≤3 ✓). A rare third cameo character gets portrait only. *Jayon confirms.*

**C6 · The naming law collides with NBP identity binding.** Canon mandates `Rolf die Wurst` in every prompt; the manual mandates **distinct hyphenated tokens** and warns that common nouns pull generic training data into the render — and "die Wurst" *is* the German word for sausage (likewise Bier/Brot/Kartoffel).
→ **Recommendation:** in **image-model prompts only**, bind identities as `Character-Rolf`, `Character-Bert`, `Character-Kati`, `Character-Mueller`; full canonical names everywhere else (screenplay, subtitles, UI, video prompts). Recorded in the nanobanana canon + a one-line exception in TREATMENT §19/SHOW_BIBLE §13. *Jayon decides — this touches Tier-1 naming law.*

**C7 · The layout law exceeds NBP's tested panel capacity.** skill-2b/`sheet_grid` allow 2×2, 2×3, 3×3 grids for any shot count; the manual: **3 panels optimal, 4 marginal, 5+ unstable** (gutter collapse) at 2K, and multi-row grids are untested territory.
→ **Resolution: shot count stays story-driven; the SHEET splits, not the story.** ≤3 shots = one 1×3 sheet (16:9 @ 2K) · 4 = one sheet, flagged marginal (or 21:9/4K) · ≥5 = **two chained sheets** for the same segment (sheet 2 attaches sheet 1 as continuity ref). `sheet_grid` rewritten accordingly. *Jayon confirms.*

**C8 · skill-2b's prompt language actively harms NBP output.** (a) "Avoid double limbs, mutated hands, blurred faces…" — NBP has no negative-prompt channel; naming artifacts *causes* them. Replace with the manual's **Constraints-block** (positive phrasing: "exactly five fingers…"). (b) "thin neutral gray gutters" → must be **solid 20px white non-diegetic gutters** (the slicing math depends on it). (c) "Print the shot number in the gutter" → **dropped** — it risks text-in-frame, and blind slicing would smear it into panels; panel order is positional anyway. TREATMENT §14's negative list gets a note: it applies to the **video** model; the image stage uses the constraints-block transform. *No decision needed — dies with the skill rewrite.*

**C9 · The slicer cuts through gutters and the resolution is wrong.** `slice_sheet` does blind equal division (682px cells on a 2048 canvas); the manual's correct offsets with 20px gutters: (0–656) · (676–1332) · (1352–2008). And `image.py` never sets `resolution` → NBP defaults to **1K** → ~341px faces → below the 512px face-morph threshold. → exact-offset slicing + `resolution: "2K"` at Phase 3.3. *No decision needed.*

**C10 · Season-0 / Synthese blocks vs the QC audit.** PEDAGOGY check #3 blocks an episode whose atoms don't appear — but Season-0 intros are language-load ≈ 0 by design, and Synthese blocks teach zero *new* atoms (they recycle). → episode carries `format: lesson | synthese | season_zero`; the audit reads `atoms[]` + `recycles[]` and applies the right ruleset. *No decision needed; schema detail.*

### SOFT — fixed inside the relevant build phase

- **Phase names drift:** PIPELINE §2.1 `Idea·Script·Vision·Shoot·Post` vs DESIGN_studio_ux `Idea·Script·Boards·Shoot·Cut`. PIPELINE is canon → **Vision/Post win** unless Jayon prefers otherwise.
- **skill-2's five-typology table with fixed pairings** violates SHOW_BIBLE §5.2 ("no character owns a grammar point") — dies with the Writer rewrite.
- **`lighting_mood`** (shot schema + overseer fields) violates TREATMENT §5 (named source + ratio, never moods) → replaced by `light_source` + `light_ratio` in the v4 screenplay schema, plus the three missing fields (negative prompt, revision prompt) and **props as a first-class field** (TREATMENT §13 sound behaviour).
- **Subtitles:** `\k` karaoke + `#22C55E` vs PEDAGOGY §5.2/§5.3 (static clauses, `das` = `#10B981`) → Phase 3.5.
- **Gemini structured output is decorative:** `_call_gemini` accepts a schema and never passes it (`response_schema` unset) → Phase 1.3.
- **~185 lines of hardcoded creative fallbacks in `app.py`** (invented locations/lessons/target lines on LLM failure) violate PIPELINE §3.3 ("extracts; it does not invent") → deleted; failures become loud.
- **Cost ledger lies:** logs `gemini-2.5-flash` while running `gemini-3.6-flash`; `CEFR_CAPS` allows A2=40s vs the 30s block law → Phase 1.
- **TREATMENT §9.5/§16.5 still carry the withdrawn Rolf-asset note** (PLAN_production_canon §7) → removed in the same v1.2 edit as C5.
- **Stereotype library has zero tags** (verified) — the 6-field tagging pass (`DESIGN_stereotype_integration` §4) is a Phase 3.1 prerequisite for the Showrunner's filter.
- **skill-3's Wardrobe Override Rule** references a field that no longer exists → dies with the Shoot rewrite.

## 4 · What each research report changes (the learnings, applied)

**Production Prompting Manual (NBP) →** becomes `prompts/canon/prompting_guidelines_nanobanana.md` (same shape as seedance): identity-binding formula + token rule · 5/6/3 slot budget + ordering law · sheet geometry (16:9 @ 2K, 20px white gutters, exact slice offsets) · Lock-Change-Constraint editing + the edit-vs-regenerate metric `M = E_p/N_p + C_i + S_d ≥ 0.66` (this + `thoughtSignature` answers everything `DESIGN_board_iteration` §6 parked as "needs research") · temperature stays 1.0 · constraints-block instead of negatives · photocopy-degradation cap (≤3 chained generations grounded in raw refs) · parameter table + safety_tolerance escalation for false blocks.
**Critical unlock:** `thoughtSignature` (stateful edits) and `media_resolution` are **native Google API only** — fal hides them. We already hold a `GOOGLE_API_KEY` and already run `google-genai`. → **new NativeNanoBanana provider calling Google directly: real storyboard generation may be possible TODAY, without a FAL_KEY** (which is only needed for Seedance video). Verify with one ~$0.13 test call at Phase 0. This also unblocks the style plate + C1 identity validation *now*.

**Production Engineering Guide →** the agent runtime: single thread + **dynamic role-based views** (keep every human turn · keep the acting agent's own turns · re-project other phases' outputs as `[APPROVED SCREENPLAY]:`-style declarations) — the concrete anti-role-bleed mechanism `DESIGN_studio_ux` described but didn't specify · **tool-suppression law** (never tools + response_format in one call; schema only on the packaging turn) · three-tier context (canon hot / working window / compacted archive — our RCP is tier 1; tiers 2–3 don't exist yet) · anti-sycophancy as mechanics (critique-before-proposal, statement debiasing, apology prohibition, banned filler phrases) · single-question gate (structural ambiguity halts; stylistic ambiguity defaults) · propose-confirm-apply with idempotency guard + human modify-before-confirm (both get added to the change protocol) · golden-dataset regression + pointwise LLM judge (the measurement half `/tune` never had — finally answers the standing "QC keeps failing skill-2 on naturalness" signal) · prompt versioning as static git assets (validates our system; adds schema-version declaration per prompt).
**Framework verdict (both reports independently): raw SDK + custom orchestration.** No LangGraph, no CrewAI. Closed.

**Creative AI Agents Report →** the failure-mode table (role bleed / verbosity / over-asking / format drift) folded into skill templates; confirms everything above at lower resolution.

**Cloud Cost Report →** first-party prices are the planning numbers (NBP ~$0.13–0.15/sheet @2K → ~$0.30–0.60 per episode of boards; Vertex ≈ fal for images). Grey-market proxies are a deliberate ToS/key-custody decision for later, never a default.

## 5 · Keep / rewrite / delete

**KEEP (proven, V4-compatible):** `subtitles.py` (2 edits) · `overseer.py`'s plan/apply/graph engine (rehomed as the chat's change protocol) · `ledger.py` · hash-verification in `rcp.py` · `sheet_grid`/`slice_sheet` (upgraded per C7/C9) · fal Seedance video adapter · stereotype library + `stereotypes.py` · all canon docs + assets · the Assembly Studio UI pane (ported) · colour tokens, character cards, option-widget pattern.

**REWRITE:** all skills (4 agent skills + QC audit + compilers) · `STORY_BRIEF_SCHEMA`/`SCREENPLAY_SCHEMA` → v4 (lesson-first: `module_id`, `block_no`, `atom_ids[]`, `format`; director layer gains `light_source`/`light_ratio`/`negative_prompt`/`revision_prompt`/`props[]`; drops `global_aesthetic_rules`, typology; stereotype becomes an optional `encounter` field) · context assembly (`pipeline/context.py` replaces the blanket RCP inject with per-phase contracts from PIPELINE §3's read-lists) · `_call_gemini` (real `response_schema`, loud failures) · the UI shell.

**DELETE:** `assemble.py` · `stage_finalize`/`stage_generate`/`substitute_canon` + word-deck stages · skills 1a/1b/1c + story-selector/options/expand · every hardcoded creative fallback in `app.py` · `prompting_guidelines_omni.md` (file) · `canon_blocks.md` (after folding) · the 7-step wizard (after parity).

## 6 · Architecture of the new build

**The thread.** One `thread.json` per episode directory (artifact-consistent, offline-safe, git-diffable; Supabase mirroring optional later). Message = `{id, ts, role, sender: human|showrunner|writer|director|editor|system, phase, content, meta}`. The phase router selects the system prompt; the **view compiler** builds each call's context: human turns (always) + acting agent's own turns + other phases' locked artifacts as `[APPROVED …]` system declarations + this phase's canon slice. On phase lock, that phase's conversation is compacted to a few lines (the artifact carries the detail).

**Context contracts (per phase, from PIPELINE §3):** Idea = MISSION+SHOW_BIBLE+STORY_SYSTEM+PEDAGOGY(frame)+curriculum+state+stereotypes · Script = MISSION+SHOW_BIBLE(voices)+STORY_SYSTEM+PEDAGOGY(ceilings)+TREATMENT(filmability)+brief+state · Vision = TREATMENT+nanobanana+SHOW_BIBLE(presence)+screenplay · Shoot = TREATMENT+seedance+screenplay+panels · Post = PEDAGOGY(subtitles)+TREATMENT(safe zone)+screenplay+clips. Token-measured; warn at 60% budget (the guide's threshold — prompt-stage canon is already 10.4k chars before the studio adds more).

**UNIVERSE_STATE** (per `DESIGN_universe_state` §5, unchanged): stratum 1 = files+git (canon, curriculum.json) · strata 2–4 = Supabase (world state + relationship matrix · progression incl. `atoms_taught` · decisions/approvals/rejections as persistent constraints) · stratum 5 = curriculum.json (immutable plan) + Supabase status (`taught`/`taught_in`). Writes at gates only; contradiction check v1 = exact-fact comparison + halt-and-ask; DINOv2 verification deferred to phase 2 as designed.

**LLM layer:** one caller · `response_schema` enforced · tools and schema never in the same call · no silent fallbacks · correct model id in cost logs · per-stage temperature (1.0 fixed for NBP).

**The change protocol** (ex-overseer): same typed ops + graph-computed recompile set, now rendered as **proposal cards in the chat** (diff + blast radius + Confirm/Modify/Cancel), plus the guide's two additions: idempotency guard on apply, and human modify-before-confirm.

**Providers:** images = **native Google API** (new; thoughtSignature + media_resolution + possibly usable today) with fal-NBP kept as fallback · video = fal Seedance (unchanged, FAL_KEY-gated) · mocks stay for plumbing tests.

## 7 · The UI — and the Figma question

**Answer: no Figma needed.** This is a single-user professional tool whose hard problems are *interaction* problems (one chat driving five phases; proposal cards; artifact editing), not visual-identity problems — and those are cheapest to solve in the real medium. Process instead:
1. **I build a clickable greyscale HTML wireframe** (3 screens, fake data) → you click through it → we correct the nuances there (½ session).
2. The wireframe **becomes** the shell; the working UI is iterated live in the browser.
3. A visual-identity pass (yours or mine) comes later, on top of a working tool, if wanted. The old UI's tokens (dark studio palette, der/die/das colours) carry over meanwhile.

**Screen 1 — Home:** Continue-episode card · "Next lesson" card (Showrunner's door: module, atoms, lead recommendation) · the **series map** (curriculum grid, 164 atoms coloured by status — the progress view `DESIGN_studio_ux` §8 asked where to put; answer: here) · Directions notebook (SHOW_BIBLE §10's living window) · recent episodes.

**Screen 2 — Episode workspace (the one screen):**
- **Phase rail** (top): `Idea · Script · Vision · Shoot · Post`, states (locked ✓ / active / pending), clickable back — going back shows the recompile blast radius *before* reopening.
- **The stage** (main): the current phase's artifact, editable in place — brief card · screenplay (segments→shots, director layer, dialogue) · sheet cards with upload + **slice-preview overlay showing the exact gutter cut-lines** · prompt cards with copy buttons + refs checklist · the Assembly Studio (ported as-is).
- **The chat** (right, permanent): agent-labelled turns · phase-handoff dividers · option widgets · **proposal cards** (the change protocol: summary, diff, recompile set, Confirm/Modify/Cancel) · single-question gates rendered as choice chips.
- **QC chips** under the artifact: green/amber/red, each naming the check + line; BLOCKs disable the gate button, FLAGs don't.

**Interaction nuances already decided by canon** (the "nuances" you asked about — most were already answered in your own documents, which is why the wireframe can be fast): artifacts lock at gates and re-opening is explicit + shows blast radius · board objections route through A/B/C/D diagnosis (`DESIGN_board_iteration`) as a chat proposal, never a direct image edit · rejected generations are kept with reasons (evidence) · the hook/panel/subtitle safe-zones are drawn on previews · every agent reply that proposes something must show what it costs (recompiles, credits) before a confirm button.

## 8 · Execution plan

**Phase 0 — RECONCILE & LOCK** *(docs + registry only; 1–2 sessions)*
0.1 Jayon decides D1–D7 (below) → CURRICULUM v2.2 (C1/C2/C3 harmonized).
0.2 **Build `resources/curriculum.json`** + validator (`python -m pipeline curriculum verify`: 61/56/47 counts, id uniqueness, recycles-targets exist) + REGISTRY pin. No status field — status lives in state.
0.3 Write `prompting_guidelines_nanobanana.md` from the manual → canon + pin.
0.4 Canon surgery, one /tune each: TREATMENT v1.2 (C5 rebudget/order · §9.5+§16.5 Rolf note out · §14 video-only note · fold canon_blocks §10-verbatim check) · PIPELINE v1.2 (C4 change-protocol rename · phase names) · REGISTRY (unpin Characters-Main-Sheet/canon_blocks/omni · pin SHOW_BIBLE/nanobanana/curriculum.json) · SHOW_BIBLE §13/§14 (C6 token exception, if approved).
0.5 **One native-API NBP test call** (~$0.13) — verifies whether GOOGLE_API_KEY reaches gemini-3-pro-image. If yes: real boards, style plate, and C1 validation are unblocked *today*.

**Phase 1 — THE SPINE** *(backend, new modules beside old; 2–3 sessions)*
1.1 `pipeline/llm.py` — schema-enforced Gemini caller, loud failures, honest cost logging.
1.2 `pipeline/context.py` — per-phase context contracts + three-tier assembly + token accounting.
1.3 `pipeline/universe_state.py` + Supabase migration (strata 2–5) + curriculum status + decisions/constraints wired into context (the guide's cheapest high-value win: rejections stop recurring).
1.4 v4 schemas (brief/screenplay per §5) + validators updated to PEDAGOGY numbers.
1.5 Quarantine: retire old skills to `_retired/`, delete dead V2 code + app.py fallbacks, archive branch for the old wizard.

**Phase 1.6 — THE SCREENPLAY DOCUMENT** ✅ *(done 2026-08-02; inserted after Jayon caught that the AI-screenplay format was uncovered — and that the source material had been supplied and never fully read)*
1.6.1 Absorbed the four unread invideo guides (*Script Breakdown · Shot Planning · Diegetic Sound · Micro-Drama*).
1.6.2 **TREATMENT v1.3** — §3.1 DOF per shot · §6.5 tonal mode per segment · §8.1 atmosphere layers · §8.2 fused-sheet + mock-blocking reference duties · §8.3 density stress-test ("argue with the page") · §9.5 turnaround hygiene · §13 sound anchored to the beat · §15 as the complete brief. Closes the "12 parameters, we cover ~7" gap logged 2026-07-29.
1.6.3 `SCREENPLAY_V4` + validators extended to enforce it (11 blocks caught in self-test).
1.6.4 **`DESIGN_screenplay_document.md`** — the DRAFT view vs **the SHEET** (the full locked document), shot-block layout, completeness contract, inline-vs-change-protocol editing, the shot-by-shot procedure. Derives from TREATMENT §15 + the schema; restates neither.
*Correction folded in the same day: the Writer had been given a section-sliced TREATMENT on a token-budget rationale — reverted, since a metric must never scope canon (`context.py` DOC_SECTIONS is now empty and documents why).*

**Phase 2 — THE SHELL** *(2 sessions)*
2.1 `pipeline/studio.py` — thread store, phase router, view compiler, compaction-on-lock, change-protocol engine (rehomed overseer + idempotency + modify hook).
2.2 ✅ Clickable greyscale wireframe → **Jayon reviewed → REJECTED the design** (dense, flat, no hierarchy, no design system; it rendered the data model instead of designing a screen). Structure/IA confirmed correct; presentation to be rebuilt.
2.3a ✅ **Backend first, layout-agnostic** — `dashboard/studio_api.py` at `/api/studio/*`. Built ahead of the UI precisely because the API surface does not change with the layout, so design and wiring proceed in parallel.
2.3b **The UI rebuild, screen by screen, with Jayon leading** — a screen brief per screen (its one job · the decision it supports · primary/secondary/on-demand · every state), then a real **design system** (`claude.ai/design` project + a local component library synced with `DesignSync`), then variants. Research prompt: `DEEP_RESEARCH_PROMPT_design_system_workflow.md`.
2.3 The real shell: Home + Workspace (rail/stage/chat/chips), proposal cards, salvaged panes. Old wizard still runnable until 3.5.
2.4 **Two working modes** (`DESIGN_autopilot.md` v2) — per-phase Co-create/Draft toggle on the rail · the four gate actions (approve · edit-then-approve · reject-with-note · switch to Co-create) · decision-journal cards · cost shown *before* every generate click. **Every gate stays human in both modes**; no canon change required.

**Phase 3 — THE AGENTS, one vertical slice each, live-tested before the next** *(4–6 sessions)*
3.1 **Idea/Showrunner** — *(each phase agent ships BOTH entry points: the conversational one and `draft()`, which decides everything itself and emits a decision journal + attached assumptions.)*  curriculum front door, module framing, lead rec + rotation, 2–3 scenario directions, block plan; stereotype filter (3.1b: the one-time AI tagging pass over the 100 + a review screen for Jayon); brief extraction (never invents, fails loudly). Anti-sycophancy pack in every skill from here on.
3.2 **Script/Writer** — reverse-scenario method + acceptance test + load-balance law + voices + ceilings + filmability; QC = PEDAGOGY's 12-point audit as chips; the lock gate.
3.3 **Vision/Director** — sheet compiler per nanobanana canon (binding formula, 2K, white gutters, constraints block, C7 split rule) · exact-offset slicer · native-API provider · board iteration via A/B/C/D chat routing + the M-metric edit-vs-regenerate rule.
3.4 **Shoot/Director** — video prompt compiler (skill-3 core survives; C5 ref order; wardrobe rule out), refs manifest, Seedance adapter unchanged.
3.5 **Post/Editor** — subtitle fixes (static clauses, `#10B981`), assembly port, export; finalize writes state (atoms→taught, appearances, candidate facts → contradiction check → Jayon confirms → Canon Facts). Old wizard deleted.

**Phase 4 — HARDEN + FIRST PRODUCTION** *(ongoing)*
4.1 `pipeline tune-canon` helper (recompute hash + registry + changelog scaffold — kills the manual ritual that caused MISSION rot).
4.2 Golden dataset (start 10–15 scenarios incl. the recurring naturalness failures) + pointwise judge on the PEDAGOGY rubric; run on every skill change.
4.3 Visual identity: Jayon collects 15–25 style frames → extraction → style plate runs (native API) → **C1 win-condition test** (same character, two independent generations, two environments).
4.4 **Module A1.1 "Ankunft" produced end-to-end** — the real proof. Everything before this is scaffolding.

**Division of labour:** Jayon = the 7 decisions, wireframe review, style frames, generation approvals, gates, taste. Claude = everything else. **The single riskiest unknown** is NBP sheet behaviour with our cast (identity through 2K sheets, split-sheet chaining) — which is why 0.5 front-loads a real API test.

## 9 · Decisions needed from Jayon (D1–D7)

| # | Decision | Recommendation |
|---|---|---|
| D1 | Word budgets (C1) | PEDAGOGY's numbers win; CURRICULUM v2.2 harmonized |
| D2 | Image-prompt binding tokens (C6) | `Character-Rolf` etc. in NBP prompts only; canonical names everywhere else |
| D3 | Reference order/budget (C5) | chars first (sheet+portrait), style/continuity last, cameo = portrait only |
| D4 | Sheet split rule (C7) | ≤3 ideal · 4 marginal · ≥5 = two chained sheets; shot count stays story-driven |
| D5 | "Director" collision (C4) | phase agent keeps Director; §3.9 → "the change protocol" |
| D6 | Phase names | Idea · Script · Vision · Shoot · Post (PIPELINE canon) |
| D7 | Agent display names | keep Showrunner/Writer/Director/Editor for now; house voice later |

## 10 · Risk register (honest)

1. **NBP multi-panel behaviour with OUR characters is unverified** — everything image-side is documented-but-untested until 0.5/3.3. The manual marks grid stability >4 panels as unstable; our split rule works around it but chained-sheet continuity quality is unknown.
2. **GOOGLE_API_KEY may not reach gemini-3-pro-image** (key format unverified for image models) → then images stay fal/FAL_KEY-gated like video.
3. **Gemini `response_schema` on the deep screenplay schema** may degrade output quality vs free JSON — test at 1.1; the guide's fallback is validate→retry.
4. **Seedance German voice cloning** remains the residual unknown from V3 (one paid call decides).
5. **Curriculum lock freezes teaching order** — mitigated: exemplars stay rewritable seeds; atoms/order are the only locked surface; /tune path exists.
6. **Scope**: five phases × agent quality tuning is the long pole; the golden dataset (4.2) is what keeps tuning from being vibes.

---
*Next action once D1–D7 are answered: Phase 0.1 → CURRICULUM v2.2 → `curriculum.json` lock.*

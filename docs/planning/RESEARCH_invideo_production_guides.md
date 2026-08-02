# RESEARCH — The invideo production guides: absorption ledger (all 12)

> **Status: COMPLETE (2026-08-02).** Every PDF in `resources/Invideo Docs/` read, with what we took, what we rejected, and where it landed. **This ledger exists because of a real failure:** the folder was supplied ~2026-07-29, three guides were read, nine were not, no record was kept of which — and the cost (the "12 parameters per shot, we cover ~7" gap) sat unactioned for four days until Jayon asked. **Any future research drop gets a row here on arrival.**
> Companions: `TREATMENT.md` (where most of this landed) · `DESIGN_screenplay_document.md` · `BUILD_PLAN_v4_studio.md`.

---

## 1 · The ledger

| # | Guide | Read | What we took | Landed in |
|---|---|---|---|---|
| 1 | **The Treatment Document** | 07-29 | The 14-section rule-system shape; "write rules, not descriptions" | `TREATMENT` v1.0 |
| 2 | **How to Write a Screenplay (Treatment-First Method)** | 07-29 | Treatment as the controlling document, above the screenplay | `TREATMENT` v1.0 · `PIPELINE` §1 |
| 3 | **Showrunner + Director Agent Hierarchy** | 07-29 | Two-tier crew; locked scripts = execution mode; agents inherit context | `DESIGN_agent_crew_and_treatment` · `PIPELINE` §2.1 |
| 4 | **AI Script Breakdown** | 08-02 | The 12 parameters; full-script-for-context vs act-by-act generation; **the agent argues with the page** (18 cuts in 15s flagged pre-spend) | `TREATMENT` §8.3, §15 · `DESIGN_screenplay_document` |
| 5 | **AI Shot Planning** | 08-02 | **Fused sheet for contact shots** · mock blocking reference for POV · turnaround hygiene · shot order = context order · 4–7 candidates per 15s generation · ~25% keep rate | `TREATMENT` §8.2, §9.5 · §2 below |
| 6 | **Diegetic Sound Cues** | 08-02 | Four-slot sound order (already canon); **sound anchored to the visual beat**; per-scene audio architecture | `TREATMENT` §13 |
| 7 | **AI Micro-Drama** | 08-02 | Format grammar (vertical, one beat per episode, hook every 60–120s, long seasons) — confirms our 30s block + button | confirmatory only |
| 8 | **Episode-to-Episode Style Transfer** | 08-02 | **The finished graded episode is a better style reference than any text brief or plate.** Carries camera angles, movement, environment logic, tonal feel — **not** identity | `TREATMENT` §16.3 · §2 below |
| 9 | **AI Video Analysis** | 08-02 | Upload a cut → shot-completion map + prop/grade continuity flags + style signals. **Analyse during production, not after** | `BUILD_PLAN` Post phase · §2 below |
| 10 | **Test Style Guide Internalization** | 08-02 | **The five-test internalization suite** — a better eval design than the one we specced | `BUILD_PLAN` §4.2 · §3 below |
| 11 | **Directorial Style Systems** | 08-02 | Ratios not moods (already canon); the **cinematography challenge pass**; gate frames against the treatment *before returning them* | `TREATMENT` §11 note · confirmatory |
| 12 | **Turn a Novel or Webnovel** | 08-02 | Only the dense-chapter-splits / thin-chapter-merges ratio, which our atom-packing law already expresses. **Nothing adopted** — we are curriculum-driven and original, not adapting a source text | rejected, deliberately |

## 2 · The three findings that change something

### 2.1 Style transfer: the plate bootstraps, the episode supersedes it
We designed one static **style plate** (a locked Nano Banana Pro frame, `TREATMENT` §16.3) as the global look anchor. Guide #8 says the stronger reference is **the finished, graded episode itself** — because a text description of a look is a lossy translation of footage, while the footage is lossless. It carries camera angles, camera movement, environment logic and tonal feel; it explicitly does **not** carry character identity, which stays with the character sheets. That split is exactly our architecture, which is why this slots in rather than replacing anything.

**What it means for us — and the slot we already had and never used:** `prompting_guidelines_seedance.md` §4 documents a **video reference slot — `@VideoN`, ≤3 clips, ≤15s total — for "motion trajectory, camera transfer."** We have never attached one. Episode-to-episode style transfer *is* that slot's purpose.

**The strategy, in our shape:** an episode is 30s = 2 × 15s segments, so a whole episode overruns the ≤15s video budget. The reference is therefore **one representative graded segment**, not the episode. Sequence:
- **Episodes 1–n (bootstrap):** the style plate + `TREATMENT` prose carry the look, as designed.
- **Once a graded episode exists:** its strongest segment is promoted to **the series style reference**, stored in `UNIVERSE_STATE` (stratum 2, a `tonal_mode`-adjacent entity), and attached as `@Video1` on later generations.
- **It must be the final graded cut** — "an ungraded rough cut transfers an ungraded look."
- ⚠ **Unverified for our stack:** whether Seedance 2.0 `reference-to-video` accepts `audio_urls` + `image_urls` + video refs together, and how a video ref weighs against 8–9 image refs. **One paid test decides it.** Until then this is designed, not built.

### 2.2 Continuity audit: read the cut, don't scrub it
Guide #9 makes footage analysis a **read operation**: upload a cut, get back structured production data — shot-completion map against the shot list, prop continuity breaks, per-shot colour-grade drift, plus the four style signals. Run it **during** production ("the value of every signal decays the later you receive it"), at every assembly milestone.

For us this is unusually cheap: **we are already on Gemini, which reads video natively.** After `concat_clips` produces `joined.mp4`, one call with the screenplay attached returns: which shots landed, which props drifted, which segment's grade broke from its declared tonal mode. `DESIGN_universe_state.md` §3.10 listed "continuity audit of a finished cut" as a research finding and §6 deferred it to phase 2 — this is its mechanism, and it is no longer expensive enough to defer.

### 2.3 Overgeneration is a budget line, not a surprise
Documented productions kept **~25% of generated clips**, and 17 final shots in one episode were "Frankenstein shots" stitched from multiple generations of the same prompt: *"MOST SHOTS AREN'T ONE SHOT. Prompt → 8 tries → Frankenstein the keepers."* Also: **one 15-second generation typically contains 4–7 usable shot candidates**, so the plan should mark *which beat inside the chunk is the keeper*.

This directly contradicts an assumption baked into our Shoot phase, which treats one segment prompt → one accepted clip. It does not change the architecture, but it changes **expectations, budget, and the UI**: the Shoot phase needs to hold multiple takes per segment with one marked as the keeper, and rejects kept with reasons (`DESIGN_board_iteration` §5 already says keep the rejects). Recorded here; to be designed with the Shoot phase in Phase 3.4.

## 3 · The internalization suite (replaces our thinner eval spec)

Guide #10 gives five tests to run **before production**, on the canon itself, not on prompts. They are better than the golden-dataset-only plan in `BUILD_PLAN` §4.2, because they test whether the agent *absorbed the grammar* rather than whether it matched a stored answer:

1. **Cross-genre stress test.** Ask for a scene type the show has never done. Internalized grammar produces coherent output in unfamiliar territory; surface mimicry collapses. *Ours: ask the Writer for a scene type absent from all 164 atoms — a funeral, a hospital corridor — and check whether the named laws (separation rule, one legible environment, hook readable muted) still hold.*
2. **Does it ask before it generates?** An agent that produces instantly, with no question about a gap the documents don't cover, is pattern-matching. *This is the same behaviour PEDAGOGY and the change protocol demand — the single-question gate.*
3. **Unprompted citation of named rules.** Give it a scene the documents never address and see whether it cites canon back at you unasked. *"Page-level rule citation you didn't request is the strongest internalization signal there is."*
4. **Challenge its technical claims.** Push back on a lens, a ratio, a light source. An agent that **corrects itself with source-accurate specifics** has absorbed the material; one that folds to any pushback, or doubles down on a wrong spec, has not. *This is the anti-sycophancy test, and it converges exactly with the Production Engineering Guide's mandatory-critique mechanics.*
5. **The minimal continuation prompt.** With canon loaded, ask for a continuation using only **"Everything should match"** and audit character, lighting, lens grammar, spatial logic and pacing. If three words sustain consistency, **the document is carrying the style, not the prompting** — which is the state required before production.

**The governing rule: if an agent fails any of these, fix the DOCUMENT, not the prompt.** The suite's own remedies validate three TREATMENT design choices we already made — a quick-reference card (§18), a never-do list (§14), and exceptions fenced into their own section (§11) so general rules are not misapplied to outliers.

## 4 · What we deliberately did NOT take

- **Model routing across Veo/Kling/Runway.** We are Seedance-only by canon; routing is invideo's product surface, not our architecture.
- **Their economics** ($315–$750/finished minute, $950/episode, ~400 generations per 90s short). Different scale and different format — our unit is a 30-second block. Kept as an order-of-magnitude sanity check only.
- **Act-by-act chunking.** Their answer to long-form context loss. Our equivalent already exists and is finer-grained: the **module → block plan → one 30s block per episode**. Nothing to add.
- **Novel/webnovel adaptation** (#12) — we generate from a curriculum, not a source text.
- **"Upload the full screenplay first for context."** Correct for a feature film; meaningless for us, where one episode *is* 30 seconds. The equivalent — the Showrunner holding the module and the story so far — is `UNIVERSE_STATE`.

# HANDOFF — 2026-07-17 — C2 v1 shipped + context operating system installed

## Objective + non-goals
Building the "Stereotypical German" MVP: automated pipeline words → story → screenplay → prompts → [Gate 1] → scenes → assembly → [Gate 2] → Instagram. NON-goals right now: learner app (parked), parallel series, monetization, anything in IDEAS_PARKING_LOT.md.

## Exact position
- **C1 (Character & Art Bible): ~80% done.** Cast canon-named + reviewed; Flow versions exist with voices. OPEN: Jayon's STYLE_SYSTEM sheet (spec: RESEARCH_art_style_system.md §2), image text fixes (umlaut tattoo, B2 in C1_character_review.md), win-condition run (2× identical regeneration).
- **C2 (three-skill text chain): v1 BUILT & PROVEN, iteration open.** prompts/skills/skill-{1,2,3}*.md + prompts/canon/canon_blocks.md (INTERIM) + scripts/generate_episode.py. One full episode passed validation ("Kati und der Handtuch-Krieg", output/episodes/ep_87-559/). Win condition = 3 batches pass Jayon; 0/3 so far.
- Episode-01 handcrafted gold standard: episodes/episode-01.md — Jayon to shoot manually in Flow (protocol: RESEARCH_google_flow.md §4).

## Files touched this session (from git log)
prompts/skills/*, prompts/canon/canon_blocks.md, scripts/generate_episode.py, episodes/episode-01.md, docs/planning/{RESEARCH_google_flow, PIPELINE_MVP, CONTENT_STRATEGY_instagram, RESEARCH_BACKLOG, RESEARCH_art_style_system, C1_character_review, IDEAS_PARKING_LOT, VISION_HISTORY}.md, .claude/commands/{pickup,context-handoff,idea,phase-gate}.md, resources/* (renames + new sheets), CLAUDE.md.

## Decisions + why (each recorded in the linked doc)
- Canon names grammar-corrected: Rolf die Wurst · Bert das Bier · Kati die Kartoffel · Müller das Brot (C1_character_review B1) — language-accuracy principle.
- Flow = manual cockpit, NO API; automation via Gemini API; useapi.net parked as ToS risk (RESEARCH_google_flow).
- Triptych posting structure = leading candidate, decided at C6 after R-7 (CONTENT_STRATEGY).
- Scenario-first story selection, one-environment default, subtitles + scene-1 hook = hard requirements (CONTENT_STRATEGY §4–5, encoded in skills).
- Canon blocks injected by CODE, never paraphrased by LLM (skill-3 + harness).

## UNVERIFIED assumptions
- Veo 3.1 API reference-images consistency is good enough for our puppets (test in C3).
- Interim style/char blocks produce acceptable video (they're written from hero images, not validated in any video model).
- German audio quality of shortlist models (R4 risk) — untested.
- Kati's Flow voice + all Flow character voices unreviewed by us.
- **World-design question OPEN for Jayon: humans in the world (Ted-style) or puppet-only?** Current interim style block says no humans; first generated episode wanted a human crowd.

## Commands run + results
- `generate_episode.py --random` × 3: run1 fail (8192-token truncation), run2 fail (16k truncation at skill-3), run3 ✓ full pass after structured-outputs+streaming fix. Cost ≈ $0.30–0.60/episode text.
- `generate_story.py` (B2-era) worked ×3 earlier; superseded by generate_episode.py.

## Failures distilled
- Tried plain max_tokens bumps for big JSON → still truncated → fixed with output_config json_schema + streaming (KEEP this pattern).
- LLM wrote `CHAR_BLOCK:Kati` (short name) → substitution failed → fixed: fuzzy matcher + Naming Law section in all skills.
- (Historical) German -eln/-ern verbs broke stem validator; Sonnet thinking eats max_tokens budget.

## Open risks
R1 character drift (top), R2 10-scene coherence (watch in Flow shoot), R3 cost overshoot, R4 German audio — docs/planning/RISKS_AND_REALITY_CHECKS.md.

## Next 3 steps
1. Jayon: run `generate_episode.py` on several batches, judge; report weaknesses → iterate skills (C2 win: 3 passes).
2. Jayon: shoot Episode-01 in Flow (rename Flow chars to canon first!); log credits/retakes per scene.
3. Jayon: STYLE_SYSTEM sheet + answer the humans-in-world question → canon_blocks.md updated → then C3 prototyping.

## Reread first (next session)
CLAUDE.md (auto) · this packet · docs/project_status.md · docs/planning/BUILD_PLAN_MVP.md · docs/planning/CONTENT_STRATEGY_instagram.md · prompts/skills/ (if touching the chain)

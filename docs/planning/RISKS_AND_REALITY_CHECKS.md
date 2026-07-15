# Risks & Reality Checks — the anti-delusion register

**Purpose (Jayon, 2026-07-14):** name the ways this can fail BEFORE they happen, so nothing surprises us and no risk is discovered mid-spend. Living doc — update whenever a risk materializes, resolves, or a new one appears. Each risk: what breaks · how likely/costly · what we do about it · early-warning sign.

---

## R1 — Character consistency may just not work well enough 🔴 highest risk
AI video models drift: same prompt + same reference ≠ same character, especially across 10 scenes/day forever. Four characters multiplies the problem.
**Mitigations:** C1 designs characters FOR reproducibility (simple silhouettes, fixed color anchors, one signature prop each — an object-headed/mascot-style design is far more stable than realistic humans); reference-image anchoring + i2v; accept small drift as part of the AI-slop-aware aesthetic. **Early warning:** C1 win condition (bible → identical character twice) fails after serious iteration → redesign characters simpler, or narrow to 2 characters.

## R2 — 10 coherent scenes/day may exceed what models deliver 🔴
A story forced through 10 word-owning scenes can come out as 10 disconnected clips; viewers feel it instantly.
**Mitigations:** the two-pass screenplay stage exists exactly for this; combined-video quality is judged at Gate 1 (script) and Gate 2 (video); posting format can hide seams (post best scenes as singles + combined as the "episode"). **Early warning:** C2 win (scripts read well) passes but C3/C4 videos feel disjointed → shorten to 5-scene episodes (5 words/day) — the deck doesn't care.

## R3 — Cost balloons past the estimate 🟡
$2.40/day (LTX-2.3 Fast) assumes one clean generation per scene. Reality: retries, rejected takes, style tests. 3–5× overshoot is normal in AI video work → $7–12/day during learning months.
**Mitigations:** Gate 1 blocks weak scripts from spending; per-episode cost log (C7) makes drift visible; regenerate single scenes, never whole episodes; ComfyUI/self-host escape hatch documented (RESEARCH_video_generation.md §2) if sustained >$5/day. **Early warning:** cost log shows >4 generations/scene average.

## R4 — German audio quality unverified on the cheap models 🟡
LTX-2's German speech is untested by us; bad German in a LANGUAGE-TEACHING page is fatal to credibility.
**Mitigations:** C3 tests German FIRST; the narration fallback (silent video + ElevenLabs German TTS, verified near-human) always exists and even gives more pedagogical control. **Early warning:** native-speaker check (Jayon B1 + a native friend) flags pronunciation in C3 samples.

## R5 — Nobody watches / growth is slow 🟡 (business, not tech)
AI content saturation is real; German-learning is a niche; algorithm luck matters. 6–12 months to meaningful audience is normal; zero traction is possible.
**Mitigations:** primary goal remains learning (the pipeline is the win); quality positioning targets exactly the gap found in RESEARCH_instagram_german_market.md §C; posting-format experiments in v1; portfolio value exists at ANY follower count. **Early warning:** 30 posts with near-zero saves/shares (not just views) → format pivot, not abandonment.

## R6 — The word-driven story constraint fights entertainment 🟡
10 arbitrary deck words/story is a strong creative straitjacket; forced words read as forced.
**Mitigations:** already softened (no repetition quota); LLM assigns words to scenes freely; dialogue escape hatch; if needed, relax to "8 words on-screen, 2 in captions" or 5-word episodes. **Early warning:** Gate 1 rejections consistently cite the same 2–3 shoehorned scenes.

## R7 — Instagram platform risk 🟢 accepted
API/publishing rules for automated content tighten periodically; AI-content labeling policies evolve; reach is rented, never owned.
**Mitigations:** Gate 2 keeps a human in the loop (also policy-friendlier); scheduler-tool fallback if Graph API access is painful; cross-posting (TikTok/YouTube Shorts) trivial later since content is platform-agnostic.

## R8 — Solo-operator burnout 🟢→🟡
Daily gates + daily posting + studies + job = grind. The pipeline automates production, not judgment.
**Mitigations:** batch gates (approve 3–5 episodes in one sitting); pre-generate buffers; posting cadence is OURS to set — 3×/week is fine to start.

## R9 — Scope creep from the world-building dream 🟡 meta-risk
Four characters, podcast series, news-roasts, an app later… the vision is big and Jayon generates ideas fast. The V1→V2 pivot itself burned some B3-era work (React app plans, recall-first rules).
**Mitigations:** the phase system + locked docs exist for this; new ideas go to a PARKING LOT section in project_status.md, not into the current phase; one series until C7 is done. **Early warning:** any sentence starting "we could also…" during C1–C7.

## R10 — LLM quality loops can rubber-stamp 🟢
Evaluator LLMs often approve mediocre work (sycophancy) — the "loop engineering" may give false confidence.
**Mitigations:** checklists with binary, checkable criteria (not "is it good?"); Jayon's Gate 1 remains the real filter until evaluator agreement with Jayon's judgments is measured (log gate decisions vs evaluator scores — a v1 task).

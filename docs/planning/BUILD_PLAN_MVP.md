# Build Plan — V2 (Instagram content pipeline)

**Status:** V2 DRAFT (re-cut 2026-07-14 after the pivot; V1 in git history). B0–B2 completed under V1 and carry over unchanged.
**Rules:** one phase at a time; done = win condition demonstrated; every phase begins with its RESEARCH step; each phase names Jayon's learning objective and just-in-time provisioning.

---

## ✅ Done (V1 phases, fully reusable)

- **B0 — n8n engine** (Docker, persistent volume, webhook workflows)
- **B1 — Word source** (Supabase, 605 words, next-10-unseen workflow)
- **B2 — Story stage** (Claude Sonnet 5, structured output + semantic validate→retry; 3 stories passed; prompt gets a V2 revision in C1/C2)

## C1 — Character & Art Bible ⭐ (Jayon's creative step)

Jayon defines the four stereotypical-German characters (names, trait sheets, speech quirks, relationships, visual descriptions) + the art style (look, palette, rendering feel). Research step: character-design-for-AI-consistency practices; style-reference techniques of AI animation creators. Output: `docs/planning/CHARACTER_ART_BIBLE.md` + canonical reference images (generated with Jayon in the loop until he says "that's them").
- **Win:** reference images of all 4 characters + 1 style board Jayon signs off; regenerating a character from the bible text + refs produces a recognizably identical character twice in a row.
- **Learn:** image-model prompting, reference/seed techniques, what makes a character AI-reproducible (simple silhouettes, fixed color anchors, distinctive props).
- **Provision:** image-model credits (fal.ai covers Nano-Banana-class models) — small budget.

## C2 — Text pipeline v2 (NOW GOVERNED BY docs/planning/EXECUTION_PLAN_text_pipeline.md — tasks E1–E7, executed in Antigravity)

*(Original C2 sketch below; the execution plan supersedes details: adds Stage-0 Run Context Pack init, run ledger + series memory, 3-option story premises with Gate A choice, quality-check stage, dual Seedance/Omni prompt packages with reference mapping, /tune change management.)*

### C2 original sketch (superseded)

Split B2's single pass into V2's design: SCENARIO pass (scenario-first selection per CONTENT_STRATEGY §5.1, one-environment default, optional Jayon input param) → STORY pass (trait-faithful, practical everyday German, hook in scene 1) → SCREENPLAY pass (scene dissection, dialogue, CI checks, video-model limits) → PROMPT-WRITER pass (bible + scene → strict video prompt). Includes the quality-checklist evaluation between passes (loop engineering v0: validate → feedback → retry, extended from B2).
- **Win:** for 3 different word-batches, pipeline emits 10 scene-prompts each that pass the checklist AND read well to Jayon — before any video money is spent.
- **Learn:** multi-stage LLM chaining, evaluator prompts, checklist design.
- **Provision:** nothing new.

## C3 — Video prototyping (the deferred model decision + style lock)

The B3 shortlist survives (LTX-2.3 Fast / Gemini Omni / Kling 3.0 / Veo-Lite+TTS — RESEARCH_video_generation.md §5) but is now judged WITH the bible: which model best holds OUR art style + characters? Test consistency techniques: reference-image anchoring, last-frame chaining. Jayon drives manually (his stated wish: foresee every generation while learning the craft).
- **Win:** 2 consecutive scenes with the same character, same style, acceptable German audio (or narration route chosen), at a cost Jayon accepts. Model + technique LOCKED and recorded in the engineering spec.
- **Learn:** video-model prompting, i2v vs t2v, consistency techniques, cost control.
- **Provision:** fal.ai key + ~€10–20 experiment budget (+ Google AI key if testing Omni).

## C4 — Scene pipeline (semi-automated with Gate 1)

n8n: words → C2 three-pass chain → **Gate 1 (approval: Jayon sees story/screenplay/prompts + estimated cost, approves)** → generate 10 scenes via locked model → store in Supabase.
- **Win:** one full episode's 10 scenes generated hands-off after a single approval click.
- **Learn:** n8n wait/approve patterns (Wait node/webhook resume), async job polling, storage.

## C5 — Assembly

Creatomate (locked): stitch 10 scenes + BRANDED SUBTITLES (hard requirement, style from design step) → combined episode (9:16) + optional per-scene cuts. Stage 6b (pending MVP-scope decision): word-card generator for triptych carousels (template-based, pixel-accurate text).
- **Win:** watchable combined episode + individual scene clips, correct format, from one trigger.
- **Learn:** template rendering, aspect/format handling.

## C6 — Publishing stage with Gate 2

Instagram posting via API (research R-10) + posting-format decision (triptych vs reel-only, research R-7) + launch sequence (character intros, CONTENT_STRATEGY §2). **Gate 2:** Jayon approves final videos + caption before anything goes public. Posting format experiment plan (which cut structure to post) designed here.
- **Win:** one episode published to the page through the gate, scheduled, with caption + hashtags from the pipeline.
- **Learn:** Meta API/scheduling ecosystem, approval-gated automation.
- **Provision:** Instagram Business account + Meta app (or scheduler account).

## C7 — Daily operation (= MVP done)

Event/schedule-driven daily run of the full chain with both gates, failure notifications, idempotent re-runs, cost logging per episode.
- **Win:** **3 consecutive daily episodes published end-to-end** with Jayon touching only the two gates.
- **Learn:** error workflows, idempotency, monitoring, cost telemetry.

---

**Sequencing logic:** creative foundation (C1) → text chain hardened cheaply (C2) → spend money only when scripts are worthy (C3) → automate generation behind a gate (C4) → package (C5) → publish behind a gate (C6) → run daily (C7). Cheap stages absorb iteration; expensive stages stay gated.

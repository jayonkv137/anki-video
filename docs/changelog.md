# Changelog

> Newest first. One entry per meaningful change/feature.

## 2026-07-17 — Google Flow research + first full pipeline map

- RESEARCH_google_flow.md: Flow capabilities (Ingredients/voices/SceneBuilder/Flow Agent, confirm-before-generating), NO public API (unofficial APIs = ban risk) → Flow is the manual creative cockpit; automation uses same models via Gemini API (separate billing). Competitors compared (LTX Studio closest; model APIs remain the automatable route). Episode-0 manual mockup protocol defined.
- PIPELINE_MVP.md: first end-to-end pipeline diagram (canon injection points, 8 stages, 2 gates, Flow side-cockpit, stage ownership/status table).

## 2026-07-15 — Canon names finalized + grammar-corrected

- FINAL: Rolf die Wurst · Bert das Bier · Kati die Kartoffel · Müller das Brot. Articles corrected to noun gender (das Bier; die Wurst sing.) per new language-accuracy principle: everything learner-facing must be grammatically correct. Folders/files/docs renamed and synced (Pam-*→Kati-*, ASCII filenames). Review blocker B1 closed; Kati's polished look ruled a character trait; Bert's identity core = glass+foam.

## 2026-07-14 — THE PIVOT: V1 learner app → V2 Instagram content pipeline

- Vision V2 (Jayon): "Stereotypical German" Instagram page — 4 original comic characters, art-directed world, daily 10-word stories; quality-over-slop positioning; two human approval gates (before spend, before publish); story→screenplay→prompt three-pass LLM chain; learner app PARKED.
- Docs re-cut: goal doc V2, build plan V2 (C1 Character/Art Bible → C2 screenplay chain → C3 video prototyping → C4 gated scene pipeline → C5 assembly → C6 publishing+gate → C7 daily ops). B0–B2 carry over unchanged.
- New: RISKS_AND_REALITY_CHECKS.md (10 named failure modes with early warnings). New system rules in CLAUDE.md: mandatory research step per decision; model-selection table (Haiku/Sonnet/Opus/Fable) required in every delegation.
- Instagram market research committed (RESEARCH_instagram_german_market.md): digging playbook + ~35 verified accounts + format taxonomy; gap confirmed = serialized animated CI stories.

## 2026-07-13 — B2 design: story strategy locked

- Research (TPRS, exposure frequency, bizarreness/humor, story grammar) → `docs/planning/RESEARCH_story_design.md`.
- Locked: fixed duo cast + consistent world; fixed episode template (setting→problem→attempts→resolution); LLM assigns words to scenes freely, session presents in story order (PRD §5 amended); memorably-quirky visual humor with plain language; NO forced repetition (each word genuinely used ≥1×); dialogue as escape hatch for abstract/meta words; deck example sentences fed as sense anchors.

## 2026-07-13 — B1: Word source ✅

- Supabase provisioned (project `anki-video`, keys in `.env`; RLS on, no policies — only the secret key reads for now).
- `words` table: position (unique), word_type, german, english, sentence_de/en, related_raw (stored unused), introduced_on. Deck export (`00 Deutsch 605 Wörter.txt`, 605 rows) parsed + validated + upserted by `scripts/import_words.py` (idempotent; 0 parse problems; 395 Nomen / 85 Verb / 72 Adjektiv / 36 Zahlwort / 10 Adverb / 7 Pronomen).
- Workflow **B1 Next Words** (`workflows/b1-next-words.json`, credential-refs included): Webhook → fetch 10 unseen (PostgREST `is.null` + `order` + `limit`) → PATCH `introduced_on` (executeOnce, cross-node expression) → Respond.
- **Win condition met:** run 1 returned positions 1–10, run 2 returned 11–20; test stamps reset to null afterward (test-data hygiene).

## 2026-07-13 — B0: Engine heartbeat ✅

- Docker Desktop installed; n8n running as a container (`docker.n8n.io/n8nio/n8n` v2.29.10) detached, port `5678:5678`, data on named volume `n8n_data` mounted at `/home/node/.n8n`.
- First workflow **B0 Heartbeat** (`workflows/b0-heartbeat.json`, repo = source of truth): Webhook (GET `/webhook/heartbeat`) → HTTP Request (fetch `api.github.com/zen`) → Respond to Webhook (JSON). Imported via `n8n import:workflow` CLI, activated, restart-registered.
- **Win condition met:** calling the webhook returns 200 with live-fetched data; workflow + data survive a full container stop/start (proves volume persistence).

## 2026-07-13

- Plan phase completed: goal & milestones locked, product requirements locked, engineering requirements complete (stack decided; video/audio model deferred to prototyping with shortlist + criteria). Efficacy/competitor research done. All docs in `docs/planning/`.
- Repo created (private, github.com/jayonkv137/anki-video), scaffolded: README, .gitignore, .env.example (just-in-time provisioning policy), CLAUDE.md, automated docs.

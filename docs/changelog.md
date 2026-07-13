# Changelog

> Newest first. One entry per meaningful change/feature.

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

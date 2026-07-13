# Changelog

> Newest first. One entry per meaningful change/feature.

## 2026-07-13 — B0: Engine heartbeat ✅

- Docker Desktop installed; n8n running as a container (`docker.n8n.io/n8nio/n8n` v2.29.10) detached, port `5678:5678`, data on named volume `n8n_data` mounted at `/home/node/.n8n`.
- First workflow **B0 Heartbeat** (`workflows/b0-heartbeat.json`, repo = source of truth): Webhook (GET `/webhook/heartbeat`) → HTTP Request (fetch `api.github.com/zen`) → Respond to Webhook (JSON). Imported via `n8n import:workflow` CLI, activated, restart-registered.
- **Win condition met:** calling the webhook returns 200 with live-fetched data; workflow + data survive a full container stop/start (proves volume persistence).

## 2026-07-13

- Plan phase completed: goal & milestones locked, product requirements locked, engineering requirements complete (stack decided; video/audio model deferred to prototyping with shortlist + criteria). Efficacy/competitor research done. All docs in `docs/planning/`.
- Repo created (private, github.com/jayonkv137/anki-video), scaffolded: README, .gitignore, .env.example (just-in-time provisioning policy), CLAUDE.md, automated docs.

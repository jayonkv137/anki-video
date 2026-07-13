# CLAUDE.md

Daily comprehensible-input story videos for Anki vocabulary learning (German, Fluent Forever 625 deck). Nightly n8n pipeline: 10 words → Claude story → per-scene video → assembled story video → Supabase. React PWA serves the session: recall → grade → scene video → story finale.

## Working agreement (overrides default behavior)

This is Jayon's **learning-by-doing** project. Success = his understanding, not shipped code.

- Never build ahead of the current phase or dump complete solutions. One step at a time; each phase is discussed and explicitly agreed ("locked") before moving on.
- Actively teach: when a step involves a concept Jayon hasn't used, explain it and point to what to learn before implementing.
- Big decisions are researched with proof, presented as options, and **Jayon decides**.
- All project context lives in files (docs below), never only in chat — Antigravity IDE and future sessions must be able to pick up cold.

## Source of truth (read before planning any work)

- `docs/planning/PROJECT_GOAL_AND_MILESTONES.md` — locked goals, milestones, phase checklist
- `docs/planning/PROJECT_SPEC_Product_Requirements.md` — locked product spec, exact user flow
- `docs/planning/PROJECT_SPEC_Engineering_Requirements.md` — locked stack decisions, architecture, just-in-time provisioning checklist
- `docs/architecture.md` · `docs/changelog.md` · `docs/project_status.md` — living docs, update after every meaningful change
- `docs/reference/` — deep dives on specific features as they get built

## Hard constraints

- **Recall-first is load-bearing:** the video must never appear before the user's recall attempt (see research doc §2c). Never "simplify" this away.
- Secrets only in `.env` (git-ignored); `.env.example` lists placeholders. Provisioning is just-in-time — never create accounts/keys ahead of need.
- Video/audio model choice (#4/#5) is deliberately undecided until the prototyping stage — don't hardcode a model choice into pipeline design.
- n8n workflows are exported as JSON into the repo whenever changed — the instance is not the source of truth, the repo is.

## Conventions

- Branch per feature; PR or merge to `main` when working. Never commit generated media.
- Commit style: `type: summary` (feat/fix/chore/docs).
- After finishing a feature: update `docs/changelog.md` + `docs/project_status.md` (and `docs/architecture.md` if structure changed).

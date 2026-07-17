---
description: End-of-context ritual — write a verified transfer packet, sync all docs, commit, and prepare the next session's pickup
---

The user says "handoff" when this session's context is nearly full. Execute ALL steps — this is a ritual, not a suggestion. Principle (from our context-management research): **hand off STATE with EVIDENCE, never a prose recap of the transcript.** If this session has already degraded (repeated corrections, circular debugging), trust FILES over your own memory and mark memory-derived claims as UNVERIFIED.

1. **Write the transfer packet** to `docs/handoffs/HANDOFF_<YYYY-MM-DD>_<short-slug>.md` (≤80 lines):
   - **Objective + non-goals** of the current work (1–3 lines)
   - **Exact position**: phase, what's done vs in-flight (point to build-plan items)
   - **Files touched this session** — derive from `git log --oneline` + `git status`, not memory
   - **Decisions made + why** — one line each, link the doc where each is recorded
   - **UNVERIFIED assumptions** — things believed but not tested (explicit list; empty is suspicious)
   - **Commands/tests run + real results** (copy actual output lines, not summaries)
   - **Failures distilled**: "tried X → failed because Y" one-liners (these are gold; never omit)
   - **Open risks** (reference RISKS doc IDs where applicable)
   - **Next 3 steps**, concrete
   - **Reread-first list**: the 3–6 files the next session must read BEFORE acting
2. **Sync the living docs**: `docs/project_status.md` (Where we left off → points at the packet), `docs/changelog.md` if work landed, `IDEAS_PARKING_LOT.md` + `VISION_HISTORY.md` if this session produced unfiled ideas/pivots.
3. **Update auto-memory** (the persistent memory file for this project) with the new state.
4. **Commit and push everything** (`chore: context handoff <date>`).
5. **Print** the packet path and tell the user: next session → open in this repo and run `/pickup`.

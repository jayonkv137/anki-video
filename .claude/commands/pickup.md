---
description: Session-start ritual — load the latest handoff packet, VERIFY it against ground truth, then propose the next step
---

First job of a fresh session: ORIENT, don't guess — and never blindly "continue". (Research: a handoff without verification just compresses one chat's errors into the next chat's starting context.)

1. Read the NEWEST `docs/handoffs/HANDOFF_*.md` + `docs/project_status.md` + the packet's reread-first list.
2. **Verify the packet against reality**: `git log --oneline -8`, `git status`, existence/state of files the packet claims were touched, and any cheap ground-truth checks it mentions (tests, table counts, workflow list). Mark each packet claim ✓ confirmed / ⚠ stale / ✗ contradicted.
3. Re-check the packet's UNVERIFIED assumptions list — can any be cheaply verified now? Do it.
4. Report in ≤10 lines: where we are, what changed since the packet, discrepancies found.
5. Propose the single next step (from the packet's next-3 unless reality disagrees) and wait for the user's go — unless they already gave a task, then proceed on it with this grounding.

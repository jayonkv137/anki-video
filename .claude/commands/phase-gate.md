---
description: Close a phase — verify win condition with evidence, lock it, run the parking-lot + backlog review ritual
---

Phase to close: $ARGUMENTS (else infer the current phase from docs/project_status.md)

1. **Win condition check**: quote the phase's win condition from `docs/planning/BUILD_PLAN_MVP.md` and list the EVIDENCE it was met (outputs, runs, user confirmation). If evidence is missing: say what's missing and STOP — no ceremonial closes.
2. Mark the phase done in build plan + status; write the changelog entry; append `VISION_HISTORY.md` if the phase changed direction; note new learnings in the status learning-log.
3. **Review ritual** (the agreed system): walk `IDEAS_PARKING_LOT.md` — for each idea whose trigger fired or is near, present it in one line for promote / keep parked / kill. Then walk `RESEARCH_BACKLOG.md` open items relevant to the NEXT phase and confirm which research runs first.
4. State the next phase, its win condition, its research step, and Jayon's vs Claude's first moves. Commit everything (`docs: phase <X> closed`).

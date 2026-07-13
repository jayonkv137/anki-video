---
description: Generate a self-contained prompt for doing a task in Antigravity IDE (or another tool)
---

Task to hand off: $ARGUMENTS

Write a single self-contained prompt I can paste into Antigravity IDE. It must include:

1. One-paragraph project context (what anki-video is, current phase).
2. Instruction to read `CLAUDE.md` and `docs/project_status.md` first — and which planning docs matter for this task.
3. The task itself, precisely scoped: definition of done, what NOT to touch, and the working-agreement rules that apply (no building ahead, recall-first constraint, secrets in .env only).
4. Instruction to update `docs/changelog.md` + `docs/project_status.md` and commit on a feature branch when done.

Output only the prompt in a single code block, ready to copy.

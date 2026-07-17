---
description: Change-management ritual — turn an observed quality pattern into a versioned, regression-tested canon/skill change
---

Observation to act on: $ARGUMENTS

1. Locate the ONE file that owns this behavior (prompts/skills/*, prompts/canon/*, checklist, MISSION). Name it and quote the current relevant lines.
2. Propose the minimal edit; apply after user agreement. Bump the file's `version:` header; add a one-line docs/changelog.md entry ("tune: <file> vN — <why>").
3. REGRESSION: re-run the golden batch (`pipeline run --start 1` or current golden command), diff the output against the previous golden output + episodes/episode-01.md standards. Present the diff to the user.
4. On approval: commit (`tune: <file> vN`). On regression failure: revert, record the failed attempt as a one-line lesson in the changelog.
Never edit prompt/canon files outside this ritual.

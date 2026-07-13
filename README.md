# anki-video

Daily comprehensible-input story videos for Anki vocabulary learning.

Every day, for the day's 10 new German words: recall each word first (Anki-style), then watch an AI-generated story scene showing the word in action — each scene part of one continuous story, with the full combined story video as the session finale. Tomorrow's story is generated overnight, ready when you return.

**Stack:** n8n (orchestration) · Claude Sonnet 5 (story) · video model TBD via prototyping (Gemini Omni / Kling / Veo) · Creatomate (assembly) · Supabase (data + video storage) · React + Vite PWA.

**Planning docs** (source of truth): `docs/planning/` — locked goals & milestones, product spec, engineering spec, and the two research docs. Living docs (`architecture`, `changelog`, `project_status`) in `docs/`.

This is a learning-by-doing project: the primary success criterion is that Jayon understands every part of what gets built.

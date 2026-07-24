# DESIGN — Subtitle Engine + Assembly Studio (the light path)

> **Status: BUILT & verified live (2026-07-24).** The final stage of the pipeline: assemble the segment clips, auto-generate word-level colour-coded German subtitles, edit them in a live preview (and via the Director), and burn the final vertical video.

## The decision (light path, not Remotion)
Jayon supplied deep research recommending a **React + @remotion/player + Remotion Pro Timeline ($300) + Remotion Lambda (AWS) + Vercel AI SDK + WhisperX-on-GPU + Cloudflare R2** stack. Our studio is **none of those** — it's FastAPI + one vanilla-JS file + **ffmpeg** + Gemini, manual-upload — and `pipeline/assemble.py` **already burns subtitles via ffmpeg/libass**. So adopting Remotion meant discarding working code for a heavy toolchain + recurring cloud cost, to serve **one 30–45s video per episode** (no scale need).

**Chosen: the light path.** It delivers every requirement at **~$0**, reuses working code, and fits the system. We **adopt all the research's good IDEAS**, realised in our stack:
| Research idea | Our realisation |
|---|---|
| Frame-based declarative JSON state (single source of truth) | `subtitles.json` (30fps, 1080×1920) — drives BOTH preview and burn |
| Word-level kinetic timing | `words[]` with `startFrame/endFrame`, screenplay-derived (free) |
| Layout/colour rules (single-line L2, safe zone, box, der/die/das/grammar) | baked into `subtitles.py` + the ASS renderer |
| Decoupled subtitles → instant preview (no re-render) | HTML5 `<video>` + a synced DOM overlay reading the JSON |
| Tool-calling chat edits | the **Overseer** we already built (Gemini structured output) |
| ffmpeg/libass burn | `ass=` filter with per-word `\c` colour + `\k` karaoke + `\pos` |
**Rejected for this project:** Remotion/React rewrite, Lambda/AWS, Pro Timeline licence, Vercel AI SDK, WebCodecs workers — over-engineered for 1 low-volume video/episode.

## The state (`subtitles.json`) — the single source of truth
`{ composition{fps,width,height,durationInFrames}, layout{safeX:540,safeY:1150,fontSize:64,maxLineChars:24,maxCueSeconds:6}, colors{der,die,das,grammar,default}, subtitles:[{id,text,speaker,segment,shot,startFrame,endFrame,words:[{word,startFrame,endFrame,colorLabel}]}] }`
- **Colour-coding is computed from OUR data, not guessed:** `target_vocab[].gender` → der=blue/die=red/das=green (the noun carries the gender); grammar_target tokens → yellow (best-effort, editable). See `subtitles.color_map`.
- **Timing (free default):** distribute each shot's known German words across its known time window (scaled to the real clip duration). Chunked to ≤24 chars/line (the research's 42 overflows 1080px at 64pt). Human/Director adjustable. Optional **Deepgram Nova-3** (~$0.002/video) precision-align to the real audio is the future upgrade.

## Pipeline (Python, `pipeline/subtitles.py`)
`concat_clips` (normalise → concat demuxer → `assembly/joined.mp4`) → `build_subtitle_state` (→ `subtitles.json`) → `render_ass` (per-word `\c` colour + `\k` karaoke + `\pos(540,1150)` + BorderStyle=3 box) → `burn` (ffmpeg `ass=` → `assembly/final.mp4`). `mock_clip` synthesises test clips (no FAL_KEY). Non-destructive: `subtitles.json` is the editable truth; export re-burns.

## API (`dashboard/app.py`)
`POST /assemble` (concat + build subs) · `GET/POST /subtitles` (load/save state) · `POST /export` (burn) · `GET /video/{joined|final}` (serve) · `POST /mock-clips` (dev).

## UI (Step 07 assembly studio, `index.html`)
Expanded Step 07 into: **Video** (prompts + clip upload) → **Assembly & Subtitles** (HTML5 video + **live colour overlay** + a cue editor: editable text, ±frame nudge, click-a-word to recolour) → **Export** (burn + download). The overlay reads `subtitles.json` and updates instantly on every edit — the "instant preview without re-render" the research wanted, in vanilla JS.

## Director integration (`pipeline/overseer.py` + `skill-5-overseer.md`)
New leaf ops (no recompile): `recolor_word` ("make 'der Hund' blue"), `edit_subtitle` (retext a cue), `shift_subtitles` (nudge a segment's captions). Same propose→confirm→apply flow; subtitles.json returned in the apply artifacts so the UI refreshes.

## Verified live (2026-07-24)
Colour map (Radweg→der, Radwegnutzungspflicht→die, Badezimmer→das) ✓ · state builder (cues chunked ≤24 chars, word frames) ✓ · ASS burn (frame-extract: "Radweg" blue, box, safe-zone) ✓ · full assemble→subs→**live overlay in the UI** ("Radwegnutzungspflicht!" red on the video) ✓ · cue editor renders ✓ · **export → final.mp4 download** ✓ · Director `recolor_word` (Radweg der→die) ✓.

## Open / follow-ups
- Deepgram precision timing (one-key upgrade; free timing works now).
- Clip **trim** ops (the state can carry `trimBefore/After`; concat would apply them) — deferred; editing is minimal per the segment-based design.
- Real clips need a `FAL_KEY` (mock clips prove the whole chain today).
- Later: IG/Reels publish adapter (Gate 2).

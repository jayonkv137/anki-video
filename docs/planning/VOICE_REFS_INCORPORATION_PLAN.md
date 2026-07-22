# Plan — Incorporate per-character Voice References into the whole system

> Created 2026-07-21. You added one voice-identity `.mp3` per character in `resources/<Char>/`.
> Goal: every time a character appears, their voice reference is automatically attached — exactly
> like the image sheet is today. This document maps WHAT changes and WHERE, before we build.

## 0. What these files are (and are NOT)

| Concept | What it is | Lifecycle | In our system |
|---|---|---|---|
| **Voice-identity reference** (what you added) | 8–14s sample of how each character SOUNDS (timbre, accent) | **Constant** — one per character, reused every episode | Should resolve like the image sheet: a per-character asset |
| **Per-episode dialogue master** (`audio-master`, currently `pending`) | The actual German lines spoken THIS episode | **Per-run** — generated fresh each episode | Stays pending until the audio-gen step (M3) exists |

**These are different things.** The voice-identity reference is the persistent character asset; it is the *source* that the per-episode dialogue is generated FROM. Today the pipeline resolves each character to identity IMAGES (sheet + portrait). **This plan adds a third resolved asset type — VOICE — flowing through the exact same path the images already flow through.** The architecture already has the pattern; we extend it by one asset type.

## 1. The ONE decision to make first (drives scope)

How does the voice reference actually get "used" when a character speaks? Two mechanisms, not mutually exclusive:

- **Path B — ElevenLabs voice-clone source (RECOMMENDED, matches our canon).** The voice ref defines the character's voice in ElevenLabs; each episode's German lines are generated in that voice, merged into the `@Audio1` master, and passed to Seedance (the existing Audio-First workflow the canon already prescribes). The voice ref is the persistent identity that seeds the clone. This is the reliable path — our own Seedance canon §8 says native German TTS is unreliable ("confused-tourist effect") and to pre-generate audio externally.
- **Path A — Seedance direct audio-identity ref (experimental).** Pass the voice `.mp3` straight to Seedance as a per-character `@AudioN` reference in the prompt, letting Seedance voice the character. Simplest to wire, but quality is unproven for short timbre samples + German.

**Recommendation:** build the system so the voice ref is a **persistent per-character asset attached to every scene** (true regardless of path), then let each provider decide how to use it — ElevenLabs as the primary consumer (B), with the option to also hand it to Seedance directly (A) for experiments. The storage/attachment layer is identical either way, so we build that first and defer the A-vs-B usage question to the provider layer.

This split gives a clean **MINIMUM scope** (attach voice refs everywhere — code only, no canon change) and an **OPTIONAL scope** (make the Seedance/Omni *prompt text* bind voices directly — canon + skill change via `/tune`).

## 2. Impact map — every place this touches

### A. MINIMUM scope — make "voice attached to every character, every scene" true (code only)

| # | File / layer | Change | Why |
|---|---|---|---|
| 1 | **`.gitignore`** | Un-ignore voice refs: add `!resources/**/*.mp3` after the `*.mp3` line (or narrow the `*.mp3` rule to `output/**/*.mp3`) | The `*.mp3` rule (for generated media) is currently excluding your source voice assets — they'd never be committed, unlike the `.png` sheets |
| 2 | **`pipeline/stages.py` → `_character_ref_paths`** (or a new `_character_voice_path`) | Add resolution of each character's voice `.mp3` (glob `*.mp3` in the char folder, umlaut-folded match — same logic as the sheet resolver) | Single source of truth for "this character's voice file" |
| 3 | **`pipeline/stages.py` → `build_refs_manifest`** | For every character present in a scene (via its identity ref), **auto-inject a `voice` role ref** resolved to the mp3. Code-injected, not LLM-emitted — voice is mechanical, every speaking character always needs it | Guarantees voice is attached without depending on the LLM to remember it |
| 4 | **`refs_manifest.json`** (output artifact) | Now carries, per scene, a `{binds:<char>, role:"voice", path:.../X.mp3, status:"resolved"}` row per character, alongside the existing identity/style/audio rows | This is the machine-readable contract every downstream consumer (audio-gen, video providers) reads |
| 5 | **`pipeline/providers/video.py` → `FalVideoProvider`** | When building the real Seedance call, also collect `voice`-role refs and pass them as audio inputs (fal's audio arg — separate from `image_urls`). MockVideoProvider: no-op (or note the voice file in the card). | So a real generation actually receives the voices |
| 6 | **`dashboard`** (optional, small) | Show/▶play each character's voice ref in the refs view or a "Cast" panel; surface voice-resolved status in the post studio | Command-center visibility — "every character's voice is wired," audible proof |

**After the minimum scope:** the manifest and every provider KNOW each character's voice and attach it automatically every episode. This satisfies your literal ask ("every time these characters are used, their voice reference is also used") at the system-of-record level — no canon edit required.

### B. OPTIONAL scope — make the Seedance/Omni PROMPT bind voices directly (Path A; canon + skill via `/tune`)

Only needed if you want the generated **prompt text** to explicitly reference each character's voice (vs. the ElevenLabs master-audio path). Touches versioned canon → must go through the `/tune` ritual (version bump + regression + REGISTRY hash update):

| # | File | Change |
|---|---|---|
| 7 | **`prompts/canon/prompting_guidelines_seedance.md` §8** (→ v2.1) | Add a "per-character voice-identity reference" subsection: distinguish the persistent per-character `@Audio` voice ref from the per-episode merged `@Audio1` master; give the binding syntax (`Use @AudioN as the voice identity for <Character>`) |
| 8 | **`prompts/canon/prompting_guidelines_omni.md` §7** (→ v1.2) | Map the voice ref to Omni's voice-profile assignment (which TTS voice each speaker uses) |
| 9 | **`prompts/skills/skill-3-prompt-writer.md`** (→ v3.1) | Teach it to emit a `voice`-role reference per character AND write the `@AudioN` voice binding into the Seedance package; note the char-budget cost (voice refs add a line — watch the 3000-char cap) |
| 10 | **`prompts/canon/REGISTRY.md`** (→ v1.3) | New hashes/versions for the two guideline files (skills aren't hash-registered) |

### C. The bridge to M3 (audio generation) — where voice refs pay off most

The voice ref is the **input to the future ElevenLabs audio adapter** (`pipeline/providers/audio.py`, not yet built):
- New `stage_audio(run_id, sp, ep_dir, provider)`: for each character, use its voice ref to select/clone an ElevenLabs voice → generate that episode's German lines per scene → merge into the `@Audio1` master → resolve `audio-master` from `pending` to a real file.
- This is M3 in the roadmap; the voice refs you just added are exactly the missing ingredient that unblocks it. Same mock/real provider pattern as video (a `mock` audio provider can even TTS locally so the loop stays runnable without a key).

## 3. Sequenced build order (when you say go)

1. **#1 .gitignore fix** + commit the 4 voice refs (so they're safe in the repo). *(2 min)*
2. **#2–#4** resolver + manifest auto-injection → voice attached in `refs_manifest` for every character/scene. **Verifiable now offline** (regenerate manifest for an existing run, confirm voice rows resolve to the real mp3s). *(core change)*
3. **#5** Fal provider passes voice refs (built, key-gated, verified when you run real).
4. **#6** dashboard cast/voice panel (optional polish).
5. **(decision) OPTIONAL #7–#10** canon+skill `/tune` if you want prompt-level voice binding — with a regression run.
6. **(later, M3)** ElevenLabs audio adapter consuming the voice refs → real per-episode dialogue.

## 4. What's verifiable immediately vs. needs keys
- **Now, no keys:** #1–#4 + #6 — voice refs resolve, land in the manifest, show in the dashboard. I can prove it by regenerating a run's manifest and showing the voice rows.
- **Needs FAL_KEY + credits:** #5 real Seedance-with-voice generation.
- **Needs ELEVENLABS_API_KEY:** the M3 audio adapter (real per-episode dialogue).

---

# DECISION MADE (2026-07-21) — Path A is now BUILT

**Chosen:** Path A. For each scene, the pipeline provides Seedance/Omni the character IMAGE(s) + the character VOICE clip; Seedance uses both to make the scene's video **and** audio (it generates the German speech in that voice via the transcript trick).

**What shipped:** `.gitignore` fix (voice mp3s now tracked) · `_character_voice_path` resolver · `voice` role in `_resolve_binds`/`refs_manifest` (each character → sheet + portrait + voice, verified) · skill-3 v3.1 (emits per-character voice refs + writes `Use @AudioN as the voice of <Name>` bindings) · seedance canon §8 v2.1 (per-character voice references) · omni canon §7 v1.2 (fixed voice identity) · REGISTRY v1.3 · Fal provider passes voice audio. Live prompt-regeneration to see the bindings in generated output is pending Anthropic credit top-up.

---

# FUTURE UPGRADE — Path B: per-scene ElevenLabs dialogue (the exact vision, elaborated)

**The core idea in one line:** instead of letting Seedance *invent* the German speech, we generate the EXACT dialogue audio ourselves — in each character's real voice — and hand Seedance a finished soundtrack per scene, so it only has to make the mouth match audio it's given. Tightest lip-sync, flawless German, full control.

### Why upgrade (Path A vs Path B)
| | Path A (now) | Path B (future) |
|---|---|---|
| Who generates the German speech? | Seedance, from voice clip + text transcript | **ElevenLabs**, in the character's cloned voice |
| German pronunciation | Model's best guess (risk: "confused-tourist" accent) | Pristine — ElevenLabs is built for it |
| Lip-sync | Seedance approximates | Seedance locks mouth to a REAL waveform (tightest) |
| Control over delivery (emotion, pacing) | Low | High — tags, retries, exact timing |
| Complexity / cost | Simple, one step | Adds an audio-generation step + ElevenLabs cost |

### The exact Path-B workflow (step by step)
```
After the screenplay is locked (we know every scene's exact German lines):

STEP 1 — Voice setup (once):  each character's voice-identity clip → ElevenLabs
         voice clone/design → a saved "voice ID" per character.
         (The voice refs you just added are exactly this input.)

STEP 2 — Per-scene dialogue synthesis (new stage_audio):
         for each scene:
           for each dialogue line {speaker, german}:
             ElevenLabs.generate(text=german, voice=speaker's voice ID,
                                 [emotion/pacing tags]) → line_audio.mp3
           sequence the scene's lines with correct gaps/timing
             → scene_NN.master.mp3   (the scene's finished dialogue track)

STEP 3 — Feed Seedance the finished audio (not a transcript to voice):
         scene package = character images (@Image)  +  scene_NN.master.mp3 (@Audio1)
         prompt: "Use @Audio1 as the absolute rhythmic foundation.
                  Synchronize all lip movements to its timing."
         → Seedance renders video whose mouths match the real German audio.

STEP 4 — Assemble (unchanged): stitch scenes, burn subtitles, done.
```

### What we'd build to enable Path B
1. **`pipeline/providers/audio.py`** — mirror of the video provider: `MockAudioProvider` (local TTS/silence so the loop still runs keyless) + `ElevenLabsAudioProvider` (real, gated behind `ELEVENLABS_API_KEY`). Interface: `generate_line(text, character) -> audio_path`.
2. **`stage_audio(run_id, sp, ep_dir, provider)`** — runs STEP 2, writes `output/…/audio/scene_NN.master.mp3` per scene, resolves the manifest's `audio-master` from `pending` → the real file.
3. **A canon toggle** — the seedance §8 already documents both methods (8a Path A / 8b Path B); a per-run flag (`--audio path-a|path-b`) tells skill-3 / stage_generate which to wire (per-character voice refs vs the merged master).
4. **Voice-ID mapping** — a small `resources/voices.json` mapping each character → its ElevenLabs voice ID (created once in STEP 1).
5. **Autopilot extension** — `generate` becomes `audio → generate → assemble → caption` when Path B is on.

### When to do it
After Path A produces a first watchable video and you've judged whether Seedance's native German is "good enough." If the accent/lip-sync disappoints, Path B is the fix — and the voice refs + the §8b canon are already in place, so it's mostly building `providers/audio.py` + `stage_audio`. This is the natural evolution of **M3 (audio)** in the MVP roadmap.

---

## 5. Open questions for you (Path A is done; these are for later)
1. **Scope:** Minimum (A: attach everywhere, code-only) now, and defer the canon prompt-binding (B) — or do both in one pass?
2. **Path A vs B priority:** confirm ElevenLabs-master (B) is the primary intended voice path, with Seedance-direct (A) as experimental — or do you specifically want Seedance to consume the voice mp3s directly first?
3. Any characters that should share/deliberately NOT have a voice ref? (Right now all four have one.)

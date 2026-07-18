# Prompting Guidelines — Seedance 2.5

> version: 1.0 · canon file

## 1. Prompt structure (strict order)

`[Ref Assignments] → [Shot Structure] → [Camera & Spatial] → [Environment & Lighting] → [Style] → [Audio] → [Constraints]`

## 2. First-30-words law

Engine weights **first 20–30 words** heaviest. Lock **primary subject + core action** in this window before any style, camera, or environment text.

## 3. Limits

- **≤ 3 000 characters** hard cap. Prune ruthlessly.
- One precise adjective per quality — never stack ("beautiful, stunning, gorgeous" → pick ONE). Stacking dilutes the attention mechanism.

## 4. Reference-asset mapping

| Slot | Limit | Syntax | Role |
|---|---|---|---|
| Images | ≤ 9 (v2.0) / ≤ 50 (v2.5) | `@ImageN` | Identity lock, style anchor |
| Videos | ≤ 3 (≤ 15 s total) | `@VideoN` | Motion trajectory, camera transfer |
| Audio  | ≤ 3 (total ≤ clip length) | `@AudioN` | Rhythm, phoneme lip-sync |

**Hierarchy:** audio > video > image (audio dictates rhythm, video dictates motion, image dictates look).

### Binding syntax

Bind every character at prompt start:
```
Define the [description] in @ImageN as [CharacterName].
```

Declare style refs separately:
```
Use @ImageX and @ImageY as the global stylistic reference for lighting, color palette, and cinematic atmosphere.
```

Use the bound name **character-for-character identically** in every shot — this is called **prompt mirroring**. Even "dark jacket" → "dark jacket, slightly open" signals permission to alter the character's latent representation, causing visual drift.

## 5. One-action rule & shot syntax

One atomic visual beat per shot. If the screenplay says "walks to table, picks up glass, turns, waves" → **split into separate shots** or distill to the single most important beat. Multi-action in one shot causes temporal morphing.

Shot format:
```
Shot 1: 0-5s. [subject + single action + camera].
Shot 2: 5-10s. [subject + single action + camera].
```

For transformations, use an escalation arc: Calm → Threat → Transform → Aftermath, each in a separate numbered shot.

## 6. Camera syntax

Formula: `Camera: [move] + [speed] + [stability]`

| Intent | Syntax |
|---|---|
| Intimacy / revelation | `slow dolly in, smooth gimbal, steady motion, tight focus` |
| Action / pursuit | `tracking shot following [Subject], handheld documentary style, subtle shake` |
| Establishing reveal | `slow pan left to right, tripod stable, wide angle lens feel` |
| Scale / dominance | `low angle shot, smooth tracking, looking up at subject` |

**Zoom creep warning:** Seedance frequently confuses physical dolly movements with optical focal-length shifts, warping backgrounds. When using tracking or panning, always append `no zoom, maintain subject size in frame`.

## 7. German dialogue — Audio-First workflow

Native text-to-German audio generation is unreliable — the model was primarily trained on English/Mandarin, producing the "confused tourist" effect: distorted pronunciation, unnatural cadence, and drifting lip-sync.

**Mandatory workflow:**
1. Pre-generate pristine German audio externally (ElevenLabs / Seed-Audio 1.0) with distinct per-character voice profiles.
2. For 4+ characters: merge all dialogue tracks into **one master audio file** (Seedance accepts max 3 audio slots). Upload as `@Audio1`.
3. Declare audio role: `Use @Audio1 as the absolute rhythmic foundation. Synchronize all character lip movements and camera transitions to the timing of @Audio1.`
4. **Transcript Trick:** write the exact spoken German words in `{}` in the prompt alongside the `@Audio` reference — this locks phoneme-level lip-sync. State: `says in German {exact transcript}`.
5. **Fallback** if audio attention fails: convert the German audio to a black-screen MP4 and upload as `@VideoN` instead (Seedance grips video timing more aggressively than standalone audio).
6. Always append: `Audio Constraints: No background music, purely spoken dialogue` — prevents the model from hallucinating a musical score over your reference track.

## 8. DON'Ts

- ❌ **Adjective stacking** — dilutes attention, wastes characters
- ❌ **Omitting camera direction** — defaults to static medium shot, causes localized hallucinations
- ❌ **Changing character description wording between shots** — causes identity drift
- ❌ **Multi-action in a single shot** — causes temporal morphing
- ❌ **Leaving zoom unconstrained on tracking/panning** — causes zoom creep
- ❌ **Exceeding 3 000 characters** — hard engine cap
- ❌ **Text-only German dialogue** (no reference audio) — lip-sync will be poor
- ❌ **Omitting "No background music" constraint** when using dialogue audio

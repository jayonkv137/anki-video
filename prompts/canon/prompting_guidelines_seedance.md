# Prompting Guidelines — Seedance 2.5

> version: 2.1 · canon file · v2.1 (2026-07-21): per-character voice-identity references (Path A)

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

## 5. The Live-Action Integration Rule

- **Never** use terminology related to puppets, claymation, needle-felt, stop-motion, miniatures, or toys — these terms poison the latent space toward visible seams, stepped framerates, and tilt-shift miniature depth of field.
- All generated scenes must be treated as **live-action visual effects integration**. The characters are physically real entities interacting with human-scale, real-world environments.

## 6. One-action rule & shot syntax

One atomic visual beat per shot. If the screenplay says "walks to table, picks up glass, turns, waves" → **split into separate shots** or distill to the single most important beat. Multi-action in one shot causes temporal morphing.

Shot format:
```
Shot 1: 0-5s. [subject + single action + camera].
Shot 2: 5-10s. [subject + single action + camera].
```

For transformations, use an escalation arc: Calm → Threat → Transform → Aftermath, each in a separate numbered shot.

## 7. Camera syntax

Formula: `Camera: [move] + [speed] + [stability]`

| Intent | Syntax |
|---|---|
| Intimacy / revelation | `slow dolly in, smooth gimbal, steady motion, tight focus` |
| Action / pursuit | `tracking shot following [Subject], handheld documentary style, subtle shake` |
| Establishing reveal | `slow pan left to right, tripod stable, wide angle lens feel` |
| Scale / dominance | `low angle shot, smooth tracking, looking up at subject` |

**Zoom creep warning:** Seedance frequently confuses physical dolly movements with optical focal-length shifts, warping backgrounds. When using tracking or panning, always append `no zoom, maintain subject size in frame`.

## 8. German dialogue — voice references + Audio-First

Native text-to-German audio generation is unreliable — the model was trained mostly on English/Mandarin, producing the "confused tourist" effect: distorted pronunciation, unnatural cadence, drifting lip-sync. We counter this by giving Seedance each character's **voice-identity reference**.

### 8a. Per-character voice references — CURRENT method (Path A)
Every character carries a persistent **voice-identity clip** (a short sample of how they sound), stored beside their image sheet. It is attached to EVERY scene the character appears in, exactly like the image sheet.
1. Bind each character's voice at the top, right after their image binding: `Use @AudioN as the voice of <CharacterName>.`
2. **Transcript Trick:** write the exact spoken German in `{}` so the model locks phoneme-level lip-sync in that voice: `<CharacterName> says in German {exact transcript}.`
3. State once: `Synchronize each character's lip movements to their spoken line; treat each @Audio as that character's voice identity.`
4. **Max 3 audio slots** — so max 3 speaking characters per scene (our episodes cap at 2 mains, so this holds).
5. Always append: `Audio Constraints: No background music, purely spoken dialogue.`

### 8b. Merged master audio — FUTURE method (Path B, per-scene ElevenLabs dialogue)
When we generate exact per-scene dialogue externally (ElevenLabs in each character's cloned voice), merge the scene's lines into **one master track**, upload as `@Audio1`, and declare: `Use @Audio1 as the absolute rhythmic foundation. Synchronize all lip movements and camera transitions to the timing of @Audio1.` This gives the tightest lip-sync but requires the audio-generation step to exist first. **Fallback** if audio attention fails: convert the master to a black-screen MP4 and upload as `@VideoN` (Seedance grips video timing more aggressively than standalone audio).

## 9. DON'Ts

- ❌ **Puppet/miniature vocabulary** — puppets, claymation, felt-craft, stop-motion, miniatures, toys (see rule 5)
- ❌ **Adjective stacking** — dilutes attention, wastes characters
- ❌ **Omitting camera direction** — defaults to static medium shot, causes localized hallucinations
- ❌ **Changing character description wording between shots** — causes identity drift
- ❌ **Multi-action in a single shot** — causes temporal morphing
- ❌ **Leaving zoom unconstrained on tracking/panning** — causes zoom creep
- ❌ **Exceeding 3 000 characters** — hard engine cap
- ❌ **Text-only German dialogue** (no reference audio) — lip-sync will be poor
- ❌ **Omitting "No background music" constraint** when using dialogue audio

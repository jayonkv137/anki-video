# PEDAGOGY — the teaching floor and the check

> version: 1.1 · canon file · 2026-08-02
> v1.1: **§2.1 the narrative episode** — which of these rules still bind when an episode teaches nothing new (Season 0 intros; story episodes inside a lesson). Design: `DESIGN_narrative_episodes.md`.
> **What this is:** the smallest set of numbers and principles that keep an episode *teachable*, plus the checklist used to audit one. **What this is not:** a specification for how to write. Most of it is advisory and fires **after** the writing, not during it.
> **Read by:** the QC agent (primary — this is its checklist) · the screenplay agent (as a ceiling it stays under) · the Showrunner (when framing a lesson) · the subtitle engine (colour and placement).
> Companions: `STORY_SYSTEM.md` (how a scene is built — craft lives there, not here) · `CURRICULUM` (what is taught, in what order) · `TREATMENT.md` (rendering) · `SHOW_BIBLE.md` (who).

---

## 1 · THE ONE PRINCIPLE
**Language is acquired when the message is understood.** Everything below exists to keep meaning gettable while the language sits just beyond what the viewer already owns (*i+1*).

Two consequences that outrank every number in this document:
- **If the viewer cannot work out what is happening, no amount of correct grammar teaches anything.**
- **Meaning must be visible before or as it is spoken.** The situation, the action and the objects on screen carry the meaning; the German rides on top of it. (How to build that is `STORY_SYSTEM.md` §5 — not repeated here.)

## 2 · LEVEL CEILINGS — **HARD**
The one place this document blocks rather than advises. A block that exceeds its level's ceiling is not level-appropriate, whatever else is true of it.

| | **A1** | **A2** | **B1** |
|---|---|---|---|
| Spoken words per block | ≤ 30 | ≤ 55 | ≤ 80 |
| Max sentence length | 8 words | 12 words | 15 words |
| Core tenses | Präsens only | + Perfekt (haben/sein) | + Präteritum (aux/modals), Futur I, Passiv, Konjunktiv II |
| Syntax | main clauses, W-questions | coordinating conjunctions (und, aber, oder, denn); *weil*/*dass* subclauses | subordination, relative clauses, infinitive + zu |
| New active words | ≤ 5 | ≤ 6 | ≤ 8 |
| Structures not yet introduced | — | — | — |

**The prohibition rule:** a block may not use a structure the curriculum has not yet introduced, *except* as a deliberate unanalysed chunk where the curriculum says so (e.g. *"Ich hätte gern…"* at A2 long before Konjunktiv II is taught at B1). The curriculum is the authority on what is available; this table is the authority on how much.

### 2.1 · The narrative episode — what still binds when nothing is taught
Some episodes exist to move the story, not to teach: the Season-0 portal intros, and occasionally one episode inside a lesson (`format: narrative | season_zero`). They carry **no new atoms**. What changes, and what does not:

- **The word ceiling still binds — and should be spent far under it.** It is a ceiling on *comprehensibility*, not on teaching: a viewer at A1 cannot parse sixty words whether or not we are teaching them. Season 0 targets **near-zero dialogue**; a narrative episode that talks more is less watchable, not more cinematic.
- **Not applicable:** the target structure appearing twice · new-word budgets · "the block's atoms actually appear" (there are none).
- **Binds harder:** *meaning must be visible on screen* (§1). With less language, the image carries everything, and a narrative episode whose story cannot be followed muted has failed completely rather than partly.
- **Unchanged:** no character explains language · no translation line · no text in frame · the prohibition rule (a narrative episode may not sneak in an unintroduced structure just because it is "not teaching").
- **The audit (§8) branches on format:** checks 1, 4, 5 and 6 still apply; checks 2, 3, 7 and 10 do not; the rest are read as story questions.

**The rule underneath:** relaxing what an episode *teaches* never relaxes what a viewer can *understand*.

## 3 · PACING AND PAUSES — *soft*
German runs ~130–150 WPM natively; learners need less. With a syllable-to-word ratio of ≈ 1.7 (German compounds), the target rate is:

> **WPM = (syllables per second ÷ 1.7) × 60**

| Level | Target rate | Feel |
|---|---|---|
| A1 | ~80 WPM | deliberate, unhurried |
| A2 | ~100 WPM | relaxed conversational |
| B1 | ~120–130 WPM | natural conversational |

**Pauses are structure, not dead air.** A 30-second A1 block is roughly two-thirds speech and one-third silence, and the silence is placed deliberately: **before a separable prefix · around a subordinate clause · at every turn-taking switch.** These are the boundaries where a learner's parser needs a moment, and pausing there is what makes fast-sounding German followable.

## 4 · EXPOSURE — how often, and what actually counts
- **The useful window is roughly 3–7 encounters** with a form; the largest gains come in the first few, and returns fall off sharply after.
- **Informative context beats raw repetition.** Three occurrences in genuinely different situations teach more than eight identical echoes. Never pad a block by repeating a line.
- **The target structure should appear more than once per block**, in different mouths or different moments.
- **Spacing is the curriculum's job, not the block's.** A single episode does not need to exhaust a structure — the spiral (`CURRICULUM`) brings it back later in a new form. This is why blocks may stay light.

## 5 · SUBTITLES
### 5.1 The finding
Eye-tracking is unambiguous, and it decides our format:

| Mode | Gaze | Load | Vocabulary retention | Grammar acquisition |
|---|---|---|---|---|
| Dual (L1 + L2 stacked) | **70 % on the L1 line**, 25 % L2, 5 % scene | high | moderate | **low** |
| L2 only | 60 % L2, 40 % scene | moderate | high | moderate |
| **L2 + colour key** | **80 % L2**, 20 % scene | controlled | **very high** | **very high** |

**Dual subtitles are the trap:** given a translation, the eye takes it, and the viewer processes the episode in their own language while the German washes past. **We never show an L1 translation line.**

### 5.2 The decision — static clauses, colour-coded
Two of our sources disagreed and the disagreement resolves cleanly, because they are about two separable things:
- **Colour-coding is the win.** It is the "input enhancement" that produced the 80 % gaze figure and the highest grammar acquisition — the eye is drawn to the structural feature without anyone explaining a rule. **Keep it.**
- **Word-by-word reveal is a cost.** Animated karaoke captions destroy the *perceptual span* — the reader's natural forward preview — force reading at exactly the speaker's pace, and spend attention on tracking motion. **Drop it.**

> **Format: single-line German, shown as a complete clause, statically, colour-coded.** No translation line. No word-by-word reveal.

### 5.3 The colour key
| Meaning | Colour | Hex |
|---|---|---|
| Masculine noun (*der*) | blue | `#3B82F6` |
| Feminine noun (*die*) | red | `#EF4444` |
| Neuter noun (*das*) | green | `#10B981` |
| The block's target structure | yellow | `#F59E0B` |
Colour marks **gender and the target feature only.** Everything else stays white — if most of the line is coloured, nothing is highlighted.

### 5.4 Placement
Single line, centred, in the safe band (`TREATMENT.md` §7) — clear of the platform UI at the top and bottom of frame, and never over a face. Spatial proximity to the speaker aids attribution.

## 6 · HIGH-YIELD STRUCTURES FOR THIS FORMAT — *soft*
Thirty seconds is bad at overviews and excellent at structures whose meaning is *physically demonstrable*. When the curriculum offers a choice of emphasis, prefer:
- **Modal verbs** — obligation and permission can be shown: physically block someone and you have taught *nicht dürfen*.
- **Separable verbs** — the prefix's journey to the end of the clause is visible in the action itself.
- **Conversational particles** — carried by tone, face and timing rather than translation.
Structures that need a paradigm explained (full declension tables, tense systems in the abstract) belong to the spiral across many episodes, never to one block.

## 7 · WHAT BREAKS THE TEACHING
| Failure | Why it's fatal |
|---|---|
| **A character explains the language** | turns the episode into an instructional ad; the viewer switches from acquiring to studying, and the fiction dies. **Never.** |
| **A translation line on screen** | the eye takes the L1 and the German becomes background noise (§5.1) |
| **Meaning not visible** | a line whose sense can't be inferred from the screen teaches nothing, however correct it is |
| **Padding by repetition** | identical echoes add exposure count without adding learning (§4) |
| **Two objectives in one block** | neither lands; working memory is not divisible |
| **Text rendered inside the frame** | forbidden for visual reasons too (`TREATMENT.md` §14) |

## 8 · THE CHECK — the QC audit
Run **after** a block is written. Each item is either **BLOCK** (must be fixed) or **FLAG** (reported, Jayon decides).

| # | Check | Level |
|---|---|---|
| 1 | Within the level's word, sentence-length, tense and syntax ceilings (§2) | **BLOCK** |
| 2 | Uses no structure the curriculum hasn't introduced (except sanctioned chunks) | **BLOCK** |
| 3 | The block's atoms actually appear, and are used rather than mentioned | **BLOCK** |
| 4 | No character explains language, grammar, or the lesson | **BLOCK** |
| 5 | No text rendered in frame | **BLOCK** |
| 6 | The meaning of each line is inferable from what is on screen | FLAG |
| 7 | The target structure appears more than once, in different contexts | FLAG |
| 8 | Word count sits near the level's pacing target for the duration | FLAG |
| 9 | Pauses fall at clause boundaries and turn switches | FLAG |
| 10 | New-word count within budget | FLAG |
| 11 | One clear objective; the block stands alone for a first-time viewer | FLAG |
| 12 | German is natural — what a real person would actually say here | FLAG |

**A flag is information, never a veto.** Blocks stop the pipeline; flags are reported with the specific line at fault and a suggested fix.

## 9 · HARD vs SOFT
**HARD:** §2 level ceilings · the prohibition rule · no character explains the language · no translation line · no text in frame · the block's atoms are genuinely used.
**SOFT (everything else):** pacing targets, pause placement, exposure counts, structure preferences, and every craft note. These exist so QC can **report and suggest** — not so a writer can be told no.

## 10 · ⧖ OPEN
- **Precision subtitle timing.** Timing is currently derived from the screenplay. Aligning to the real generated audio (a forced-alignment pass) is a designed, unbuilt upgrade — worth it only once real audio exists.
- **The pacing numbers are targets, not measurements.** Once real episodes exist, measure actual delivered WPM and correct this table from evidence.

## 11 · MAINTENANCE
Tier 1 canon: changed only by deliberate human decision via the `/tune` ritual (`SHOW_BIBLE.md` §15.2). Agents may propose; they never write. **When real episodes contradict a number here, the number is wrong — correct it from evidence rather than defending it.**

### Revision history
- **v1.1 — 2026-08-02.** Added §2.1, the narrative episode: the level ceilings are about comprehensibility rather than teaching load, so they still bind (and should be spent far under) when an episode carries no atoms; the audit branches on format. Per Jayon: Season 0 and occasional in-lesson story episodes take their liberty **visually**, never linguistically.
- **v1.0 — 2026-07-29.** Created. Level ceilings, pacing formula and pause architecture, exposure window, the subtitle finding and format decision, high-yield structures, failure modes, and the 12-point QC audit. Per Jayon: written as a floor and a check rather than a writing specification, with only six HARD items. Subtitle format resolved to **static colour-coded clauses** — keeping the colour key (the source of the retention gain) and dropping the word-by-word reveal (which costs the perceptual span). Requires a change to `pipeline/subtitles.py`, which currently renders word-by-word karaoke and uses `#22C55E` for *das* rather than the sourced `#10B981`.

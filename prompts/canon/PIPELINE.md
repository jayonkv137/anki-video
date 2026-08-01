# PIPELINE — the stations, their contracts, and the handoffs

> version: 1.1 · canon file · 2026-07-29
> **What each station is, what it receives, what it produces, and — most importantly — what it must NOT decide because a later station owns that.** This is the map that keeps a pipeline of specialists from turning into four agents all writing the same episode badly.
> **Agents read their own row and their immediate neighbours — never the whole document.** Knowing too much is a failure mode here (§7).
> Contracts are stable and live here. **Current build status is not canon** and lives in `docs/architecture.md`.

---

## 1 · THE ONE PRINCIPLE — the lock and the compilers
> **The screenplay is the LOCK. Everything after it is a COMPILER.**

Every creative and pedagogical decision is made once — during ideation and screenplay. From that point on, each station **translates** the locked screenplay into another form, attaching established assets. A compiler never re-decides. That single rule is what makes the whole system tractable: an edit has a **knowable recompile set** (§6), consistency is enforced by construction rather than hope, and no station can quietly change the show.

**The corollary:** if a station finds itself inventing something creative, it is either doing another station's job, or the lock is incomplete and should be fixed **upstream** rather than patched locally.

## 2 · THE FLOW
```
curriculum ─▶ SHOWRUNNER ─▶ STRATEGIST (with the creator) ─▶ COMMIT ─▶ STORY BRIEF
                                                                          │
                                                    ┌─────────────────────┘
                                                    ▼
                                            SCREENPLAY  ◀── THE LOCK
                                                    │
                                          ┌─────────┴─────────┐
                                          ▼                   ▼
                                   QUALITY CHECK       STORYBOARD SHEETS ─▶ [human generates] ─▶ panels
                                                                                                    │
                                                                              VIDEO PROMPTS ◀───────┘
                                                                                    │
                                                                    [human generates clips]
                                                                                    │
                                                              ASSEMBLY ─▶ SUBTITLES ─▶ EXPORT ─▶ publish

  UNIVERSE_STATE is read by every station and written at the gates
```

## 2.1 · THE STUDIO LAYER — five phases, four agents
The stations above are the **internal** contracts. The creator never sees nine of anything. They move through **five phases**, talking to **four agents**, in **one continuous conversation** that never resets — the phase decides which system prompt answers, and the whole history stays visible to whoever is speaking.

| Phase | Agent | Stations it covers | The creator's question |
|---|---|---|---|
| **Idea** | **Showrunner** | §3.1 | *What are we making today?* |
| **Script** | **Writer** | §3.2 · §3.3 · §3.4 | *Write it.* |
| **Vision** | **Director** | §3.6 | *Show me what it looks like.* |
| **Shoot** | **Director** *(same agent)* | §3.7 | *Make the video.* |
| **Post** | **Editor** | §3.8 | *Finish it.* |

- **Quality check (§3.5) is never a speaker.** It runs automatically and surfaces as notes attached to the artifact — a linter, not a participant.
- **There is no separate overseer window.** The always-present conversation *is* the Director of §3.9: any instruction, at any phase, is proposed → shown with its recompile set → confirmed → applied.
- **Agent boundaries collapse; the seams do not.** Every artifact in §3 remains separate and separately gated — `brief.json` is still its own artifact even though the Writer produces both it and the screenplay. **The lock is a property of the artifact, not of who wrote it**, and each phase still loads only the canon its stations need (§7).

## 3 · THE STATIONS

### 3.1 SHOWRUNNER
- **Role.** Opens a module: presents what must be taught, where the story stands, who should lead, and what situations could work.
- **Reads.** `MISSION` · `SHOW_BIBLE` · `STORY_SYSTEM` · `PEDAGOGY` · curriculum · `UNIVERSE_STATE` · the stereotype library.
- **Receives.** The next module (or the creator's choice of one).
- **Produces.** A framing of the lesson · the story so far · a recommended lead with reasons · 2–3 scenario directions · 0–3 fitting stereotype options · the **block plan** (how atoms pack into 30-second blocks).
- **Decides.** What to *propose*, and in what order.
- **MUST NOT decide.** The scenario itself (the creator does, in conversation) · dialogue · shots, framing or visuals · anything already locked in canon. **It proposes; it never authors.**
- **Consumed by.** The creator, and then the Strategist conversation.
- **Failure.** No good stereotype match → say so plainly. Curriculum and story pulling apart → surface the conflict, don't resolve it silently.

### 3.2 STRATEGIST (the co-creation conversation)
- **Role.** Draws the creator's idea out and shapes it into a workable scenario.
- **Reads.** `MISSION` · `SHOW_BIBLE` · `STORY_SYSTEM` · `PEDAGOGY` · the Showrunner's framing · `UNIVERSE_STATE`.
- **Receives.** The creator, talking.
- **Produces.** An agreed scenario and block plan, held in the conversation.
- **Decides.** Which question to ask next; when the concept is ready to lock.
- **MUST NOT decide.** The story (**the creator's ideas come first — it asks before it offers**) · the final structured brief (§3.3 owns that) · anything downstream.
- **Failure.** Constraint conflict → name it gently and offer a fix, never silently comply.

### 3.3 COMMIT → the STORY BRIEF
- **Role.** Turns an agreed conversation into one structured artifact.
- **Receives.** The conversation.
- **Produces.** `brief.json` — lesson atoms, cast, location, premise, beats, target line, banned terms, director notes, the block plan.
- **Decides.** Nothing creative. **It extracts; it does not invent.** Anything not agreed in conversation must not appear in the brief.
- **Consumed by.** The screenplay writer.
- **Failure.** Missing information → ask, or record it as unresolved. Never fill a gap with a plausible guess.

### 3.4 SCREENPLAY WRITER — **the LOCK**
- **Role.** Turns the brief into the finished, filmable episode: segments → shots, each with the director layer and the German dialogue.
- **Reads.** `MISSION` · `SHOW_BIBLE` (voices) · `STORY_SYSTEM` (method + craft) · `PEDAGOGY` (ceilings) · `TREATMENT` (what is filmable) · the brief · `UNIVERSE_STATE`.
- **Produces.** `screenplay.json` — **the single source of truth for everything downstream.**
- **Decides.** All framing, blocking, action, gaze, expression, camera movement, timing, and every German line. **If a creative decision is going to be made anywhere, it is made here.**
- **MUST NOT decide.** Prompt syntax or `@Image` bindings · the style clause, colour, lens or grade (`TREATMENT` owns those) · anything rendered as on-screen text · which model runs.
- **Failure.** Cannot satisfy an atom within the level ceiling → flag the conflict rather than exceeding the ceiling or dropping the atom.

### 3.5 QUALITY CHECK
- **Role.** Judges the locked screenplay. **A judge, not a writer.**
- **Reads.** `PEDAGOGY` (the audit) · `STORY_SYSTEM` (craft checks) · `SHOW_BIBLE` (voice + canon facts) · curriculum · the screenplay.
- **Produces.** A verdict: blocking failures, advisory flags, each naming the specific line at fault.
- **MUST NOT.** Rewrite anything. Resolve a contradiction between the episode and canon — it **reports**; the human decides (`SHOW_BIBLE` §15.4).
- **Failure.** Uncertain whether something passes → **fail it and say why.** A false alarm is cheap; a bad episode is not.

### 3.6 STORYBOARD SHEET COMPILER
- **Role.** Compiles each segment into ONE image prompt that renders all its shots as panels in a single generation.
- **Reads.** `TREATMENT` (medium, camera, lens, colour, reference-attachment order, negatives) · `SHOW_BIBLE` (who is present) · the screenplay.
- **Produces.** One sheet prompt per segment + the reference list and attachment order.
- **Decides.** How the screenplay's shot fields translate into image language; panel layout.
- **MUST NOT decide.** New framing, blocking, action or story — **it compiles what the screenplay already decided** · the style clause (assembled mechanically from `TREATMENT`, never improvised) · anything about video or audio.
- **Consumed by.** The creator (who generates the sheet), then the slicer, then the video-prompt compiler.
- **Failure.** A shot's fields are too thin to compile → flag it upstream rather than inventing the missing detail.
- **Iterating on a generated sheet — the routing rule.** The panel is not the final product; it is a **reference fed to the video model**, and it is only useful while it *agrees* with the screenplay. Therefore: **anything the screenplay describes must be changed in the screenplay; anything it does not describe may be fixed in the image.** The station's job when the creator objects to a panel is **diagnosis** — classify the change and route it: the screenplay was wrong (edit the lock, recompile) · the prompt lost something the screenplay had (re-run the compilation; if it recurs, fix the skill) · the model simply failed (regenerate, or edit that panel only — the *only* case where direct image editing is legitimate) · or it is a new idea, which belongs to the screenplay if it carries meaning and to the location layer if it is set dressing. **A detail that lives only in a panel vanishes when the video is generated.** Full reasoning: `DESIGN_board_iteration.md`.

### 3.7 VIDEO PROMPT COMPILER
- **Role.** Compiles each segment into one multi-shot generation prompt with its references.
- **Reads.** `TREATMENT` (assembly order, camera syntax, sound, negatives, budgets) · seedance guidelines · the screenplay · the sliced panels.
- **Produces.** One prompt per segment + a resolved reference manifest.
- **Decides.** Reference bindings and slot order; how camera and timing are phrased for the engine.
- **MUST NOT decide.** How characters or the style *look* — the attached images carry that, and re-describing them causes drift · any change to the German dialogue, which is the lesson and is reproduced exactly · any new action.
- **Failure.** Over the character cap or the reference budget → report it; never silently drop a reference.

### 3.8 ASSEMBLY · SUBTITLES · EXPORT
- **Role.** Joins the generated clips, builds the subtitle state, burns and exports.
- **Reads.** `PEDAGOGY` (subtitle format, colour key) · `TREATMENT` (safe zone, format) · screenplay + clips.
- **Produces.** the joined cut · `subtitles.json` (the editable truth) · the final file.
- **Decides.** Timing derivation, colour assignment, rendering.
- **MUST NOT decide.** The German — it renders what the screenplay locked · the colour scheme, which `PEDAGOGY` owns.
- **Failure.** Clip durations disagree with the screenplay → use the real clip durations and flag the drift.

### 3.9 THE DIRECTOR (overseer)
- **Role.** Present at every station; takes an instruction at any point and lands it in the right place.
- **Reads.** All canon · every artifact of the run · `UNIVERSE_STATE`.
- **Produces.** A proposed, typed edit plan + the recompile set → on confirmation, the applied edits.
- **Decides.** *Where* an edit belongs (which layer owns it) and *what* it affects.
- **MUST NOT.** Edit a downstream artifact to fix an upstream problem — **it edits the lock and recompiles** · apply anything without confirmation · write Tier-1 canon (it proposes).
- **Failure.** Ambiguous instruction → ask one clarifying question rather than guess.

## 4 · THE HANDOFF LAW
**The artifact is the contract.** A station reads the artifact it is given, plus canon — never the internal reasoning, chat history or intermediate working of the station before it. If a downstream station needs something, that thing belongs *in the artifact*, not in a conversation it can't see.
**Every artifact is written to disk before the next station runs.** No station holds state for another.

## 5 · THE GATES (where a human decides)
| Gate | What is being approved | Why it exists |
|---|---|---|
| **Brief lock** | the concept | before any generation effort is spent |
| **Screenplay confirm** | the episode itself | this is the lock; everything downstream inherits it |
| **Sheet approval** | the visual interpretation | before video credits are spent |
| **Clip acceptance** | the generated footage | the only place output quality can be judged |
| **Export** | the finished episode | last look before it exists |
| **Any Director edit** | the diff + its recompile set | nothing changes without being seen |
**Gates are features.** A station that waits is doing its job.

## 6 · THE DEPENDENCY GRAPH — what recompiles when something changes
```
brief ──▶ screenplay ──┬──▶ storyboard sheet (per segment) ──▶ panels
                       └──▶ video prompt   (per segment)
screenplay ──▶ subtitle timing        clips ──▶ assembly ──▶ export
```
| Change | Recompiles |
|---|---|
| a **shot** in segment K | segment K's sheet prompt + segment K's video prompt **only** |
| a whole **segment** | the same, for that segment |
| the **brief** | the screenplay → **all** sheets and **all** prompts |
| a **subtitle** (text, timing, colour) | nothing — it is a leaf; re-export only |
| a **clip** re-generated | assembly → export |
**The graph decides the recompile set — never a model's judgement.** Anything outside the set is left untouched, and the set is shown to the human before it runs.

## 7 · CONTEXT SCOPING — what each station is *not* given
A station is given its own contract, its inputs, and the canon it needs. It is **not** given the full pipeline map, other stations' skills, or downstream concerns. This is deliberate: an agent that knows about video prompts starts writing video-shaped screenplays; one that knows the curriculum starts teaching inside the storyboard. **Separation is what makes each station good at its own job.**

## 8 · ⧖ OPEN
- **Publishing** — no station exists yet; the pipeline currently ends at export.
- **`UNIVERSE_STATE`** — read by every station and written at the gates; designed, not yet built.
- **Generation is manual** — images and video are generated by the creator outside the pipeline and uploaded back. The contracts above are unaffected by that becoming automatic.

## 9 · MAINTENANCE
Tier 1 canon: changed only by deliberate human decision via the `/tune` ritual (`SHOW_BIBLE.md` §15.2). **A new station, or a change to any station's "MUST NOT decide" list, is a Tier-1 edit** — those lists are the seams that hold the pipeline apart.

### Revision history
- **v1.1 — 2026-07-29.** Added §2.1 (the studio layer: five phases — Idea · Script · Vision · Shoot · Post — mapped onto the nine stations, four agents, one continuous chat; QC never speaks; no separate overseer window). Added the **board-iteration routing rule** to §3.6. Station contracts unchanged.
- **v1.0 — 2026-07-29.** Created. The lock-and-compiler principle, the flow, nine station contracts (each with an explicit *must not decide*), the handoff law, the human gates, the dependency graph (previously implicit in code), and the context-scoping rule.

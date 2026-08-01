# DESIGN — The studio: four agents, five phases, one chat

> **Status: PROPOSAL for Jayon's confirmation (2026-07-29).** Rethinks the agent structure and the interface after Jayon's critique: *too many agents, the split is an artifact of the old design, and the UI feels like a gauntlet.* Basis: invideo's two-tier crew, real TV production roles, and the KISS principle applied to the creator's actual experience. Companion: `PIPELINE.md` (station contracts — still valid, see §6).

---

## 1 · The diagnosis
The nine stations in `PIPELINE.md` are **engineering** stations, not **user-facing roles**. The creator never experiences "commit" as a thing — it is simply the moment an idea becomes real. That split leaked from implementation into UX, and it is why the studio feels like a queue of forms.

**Two references solve it the same way.** invideo runs **two tiers**: one showrunner holding the bible, one director per episode executing everything. Real TV production has roughly four roles a creator actually talks to. Neither has nine.

## 2 · The collapse — four agents, five phases
| Phase | Agent | Absorbs (old stations) | The creator's question |
|---|---|---|---|
| **Idea** | **Showrunner** | Showrunner | *What are we making today?* |
| **Script** | **Writer** | Strategist + Commit + Screenplay writer | *Write it.* |
| **Boards** | **Director** | Storyboard sheet compiler | *Show me what it looks like.* |
| **Shoot** | **Director** *(same)* | Video prompt compiler | *Make the video.* |
| **Cut** | **Editor** | Assembly + Subtitles + Export | *Finish it.* |

**Why these groupings:**
- **Writer** — ideation, locking the concept, and writing the script are one continuous act of authorship. Splitting them made the creator hand off their own idea to a stranger mid-thought.
- **Director** spans Boards and Shoot because both are *visual translation of the same locked script*, and in AI production the boards feed the prompts directly. Two phases, one head.
- **Editor** owns Cut because the creator experiences assembly, subtitles and export as one task: *finish it.* (Two activities inside it — burning and cue-editing — but one person.)
- **Quality check is not an agent.** Nobody wants to talk to QC. It becomes **inline chips under the artifact**, like a linter: green when clear, amber when it has a note. It never speaks.

## 3 · The Director/overseer dissolves
The floating "Director" window existed because the chat only lived in one step. **Once the chat is continuous and always carries full context, "an agent you can talk to at any time to change anything" is simply the chat.** So the separate overseer concept is removed — one fewer thing to learn, with no capability lost. Its mechanism survives intact: any change is still *proposed → shown with its recompile set → confirmed → applied*, but it now happens as a reply in the conversation rather than in a second window.

## 4 · One chat, many agents — how it works
**Yes, this is straightforward.** A chat is a message array; an "agent" is just which system prompt is loaded for a turn.

- **One `messages[]` per episode**, persisted for the life of the episode. It never resets.
- **Each turn:** `system = MISSION + the canon this phase needs + this phase's skill` · `messages = the full conversation so far`.
- The **phase decides the system prompt**; the conversation carries everything else.
- The UI shows a light label (*"Writer is answering"*) and a divider at each handoff, so the change of voice is legible without being ceremonial.

**Why this is better than separate chats:** the Director at Boards can see *why* the Writer chose a beat two hours earlier. Intent stops evaporating at every boundary — which is exactly the loss the old wizard forced.

**Keeping it affordable as it grows:** artifacts are the compression. Once a phase's artifact is locked, its conversation is summarised into a few lines and the artifact carries the detail. The chat stays readable and the context stays bounded.

## 5 · The interface
**One workspace. Two panes and a rail** — not seven screens.
- **Phase rail** across the top: `Idea · Script · Boards · Shoot · Cut`, showing progress, always clickable to go back.
- **The stage** (main pane): the artifact of the current phase — the brief, the script, the boards, the prompts, the cut. Editable in place.
- **The chat** (side pane): always present, never resets, labelled with whoever is answering.
- **Quality notes**: chips beneath the artifact, never messages.
- **Home**: continue the current episode · start the next lesson · browse what's been made. Nothing else.

Everything a phase needs is on one screen, and the only navigation is *back to an earlier phase*.

## 6 · What this means for `PIPELINE.md`
**The station contracts stay valid and unchanged.** The screenplay is still the lock; the compilers still compile; every "must not decide" line still holds. What changes is **presentation, not architecture**:
- **Artifacts stay separate** — `brief.json` remains a distinct artifact and a distinct gate, even though the same agent produces both it and the screenplay. The lock is a property of the artifact, not of who wrote it.
- **Agent boundaries collapse; seams do not.** The anti-role-bleed rules survive because each phase still loads only the canon it needs and still writes only its own artifact.
- `PIPELINE.md` gains a small section mapping the four agents onto the nine stations — added at implementation time, not before.

## 7 · What this removes
The separate overseer window · four wizard steps · QC as a conversational participant · the mid-thought handoff between ideation and writing · and the need for the creator to know that "commit" exists at all.

## 8 · Open
- Names — *Showrunner / Writer / Director / Editor* are placeholders; a house voice may suit better.
- Whether **Boards** and **Shoot** should be one phase with two actions rather than two phases.
- Where the **series-level** view lives (progress across all ~170 episodes, the curriculum map, the Directions section) — probably home, not the episode workspace.

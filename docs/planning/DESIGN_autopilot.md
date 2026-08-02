# DESIGN — The two working modes: Co-create and Draft

> **Status: PROPOSAL for Jayon's confirmation (2026-08-02, v2).**
> **v2 supersedes v1 entirely on Jayon's correction.** v1 proposed a trust ladder ending in full autopilot (agents signing gates, generating images and video unattended). **Rejected, correctly:** unattended generation spends money on work nobody has seen. v2 keeps **every gate human, always** — what becomes optional is the *conversation*, never the *approval*.
> Companions: `PIPELINE.md` §5 (the gates — unchanged) · `MISSION.md` §5 (unchanged, and that is the point) · `DESIGN_studio_ux.md` · `DESIGN_screenplay_document.md`.

---

## 1 · The axis

The studio has always had two separable things at each phase, and v1 confused them:

| | What it is | Who does it |
|---|---|---|
| **The work** | arriving at the artifact — the ideas, the choices, the writing | **this is what has a mode** |
| **The gate** | approving that artifact so the next phase may start | **always Jayon. Both modes. No exceptions.** |

So there is exactly one question per phase — *how does the artifact get proposed?* — and two answers:

- **CO-CREATE** *(the default, and the point of the product)* — the agent asks, offers options, pushes back, draws Jayon's ideas out, and converges through conversation. His creativity is the input; the artifact is the residue of a dialogue.
- **DRAFT** *(the fast track)* — no conversation. The agent makes every decision itself from canon + curriculum + `UNIVERSE_STATE` + the seed bank, and presents a finished artifact. Jayon reviews it at the same gate he would have reached anyway.

**Both roads end at the identical gate, with the identical artifact schema, the identical QC chips, and the identical change protocol.** Draft mode is not a different pipeline. It is the same pipeline with the conversation skipped.

## 2 · Money can never be spent on the far side of a decision Jayon didn't make

This is the hard rule the whole document exists to protect, and it is why v1 was wrong.

- **Every paid generation is downstream of an explicit human approval.** Approving a sheet prompt authorises *that* sheet. Approving a video prompt authorises *that* clip. Nothing generates because an agent felt ready.
- **A re-roll is a human action too.** A bad board is looked at, and Jayon decides to re-roll it. There is no loop that keeps paying until something passes.
- **One bounded exception, opt-in, default OFF:** `TREATMENT` §16.6 already requires generated frames to be gated against canon *before being shown*. If that gate catches a hard technical failure (gutter collapse, a panel rendered as text, a blank frame), the agent may auto-re-roll **at most N times** (`auto_reroll_on_technical_failure`, default **0**, recommended **1**). It fires only on **objective render faults, never on taste**, it is disclosed in the journal, and at `0` the failure is simply shown to Jayon. This is the only autonomous spend in the system, and Jayon can switch it off entirely.
- **Publishing is never automated.** Unchanged, permanent.

## 3 · Mode is per phase, and switchable mid-episode

Not a per-episode setting — a per-phase one, because the phases have genuinely different creative weight:

| Phase | Creative weight | Sensible default |
|---|---|---|
| **Idea** | high, but highly *derivable*: the curriculum says what's next, rotation says who leads, the stereotype library offers situations | either |
| **Script** | **the highest.** This is the episode | **Co-create** |
| **Vision** | ~none. `PIPELINE` §3.6 forbids it from inventing — it *compiles* what the screenplay decided | **Draft** |
| **Shoot** | ~none. Same — a translator, not an author | **Draft** |
| **Post** | mechanical (timing, colour, burn) | **Draft** |

**A realisation worth stating plainly: three of the five phases are already draft-by-nature.** Their station contracts explicitly forbid creative invention, so there is nothing to co-create there — the human's job at Vision/Shoot/Post has always been *approve the output*, not *discuss the input*. The mode selector therefore only really matters at **Idea** and **Script**, which is exactly where Jayon's creativity belongs.

Consequences:
- **Mixed by default is the normal shape:** co-create the Idea and Script, draft the rest. That is the product working as intended, not a compromise.
- **"Today, just do it"** = set Idea and Script to Draft too. Four gates of review instead of four gates plus two conversations.
- **Switchable at any gate, in both directions.** Reject a drafted screenplay with *"start over, but the button should land on Müller"* → it redrafts. Or switch that phase to Co-create and start talking. Nothing is locked by the mode you began with.

## 4 · What happens at a gate (identical in both modes)

Four actions, always available:

1. **Approve** → the phase locks, the next begins.
2. **Edit, then approve** → inline for leaf fields (a German line, a gaze, a prop's sound note); through the change protocol for anything that changes the recompile set — which is *shown before* the edit, never after.
3. **Reject with a note** → the agent redrafts that artifact only, with the note as a constraint. Bounded (default 2 redrafts, then it asks rather than looping).
4. **Switch to Co-create** → stop reviewing, start talking. The drafted artifact becomes the conversation's starting point rather than being thrown away.

## 5 · The decision journal — how a drafted artifact stays legible

In Co-create mode, Jayon knows why everything is the way it is: he was there. **In Draft mode, that context has to be reconstructable, or approving is rubber-stamping.**

So every decision an agent makes in Draft mode emits the **same proposal card the change protocol already produces** — what was chosen, what else was considered, why, and what it affects:

> **Lead: Müller das Brot** — coldest in rotation (last led A1.5); the Pfand situation fits his established thrift.
> *Considered:* Rolf die Wurst — rejected, led A1.8.2 two episodes ago.

Which means:
- A drafted episode's thread **reads like a co-created one**. Scroll it and every fork is visible.
- **Disagreeing is cheap:** reopening a journal entry *is* the change protocol. Nothing needed designing twice.
- **Uncertainty is surfaced, not hidden.** Where a Co-create agent would ask a clarifying question, a Draft agent proceeds with its best answer **and attaches the question to the gate**: *"I assumed the bakery is the one from A1.6 — confirm or correct."* A human is arriving anyway, so there is no need to park the episode; the question simply rides along with the artifact.
- **QC flags never launder.** Advisory flags accumulate on the artifact and are shown at the gate exactly as in Co-create mode.

## 6 · The honest risk in Draft mode, and the two levers against it

`STORY_SYSTEM` §9.1 is blunt: Jayon's own seed is the **most reliable** anti-slop disruptor, and *"an agent's unprompted invention is the least."* Draft mode removes the per-episode seed. Two mitigations, both cheap because the machinery exists:

1. **The seed bank.** Jayon drops ideas, overheard moments and observations in bulk whenever he has them — into Directions (`SHOW_BIBLE` §10 / `UNIVERSE_STATE` stratum 2). Draft mode **draws one and marks it consumed.** His creative DNA reaches episodes he wasn't present for. An empty bank is worth a warning at the Idea gate, not a block.
2. **The correction flywheel — already built and tested.** Every rejection Jayon makes becomes a stratum-4 constraint injected into every later run (`universe_state.constraints_block`, proven in the spine suite). **Co-create sessions train Draft mode.** The manual episodes are not the slow path; they are the calibration.

And the structural guard: Draft mode's output faces the *same* hard validators and the same 12-point audit. It cannot ship anything Co-create couldn't.

## 7 · Canon impact — none

This is worth stating because v1 got it wrong. `MISSION` §5 — *"The human decides; agents propose… they never make the creative call"* and *"Human gates are features, not gaps"* — is **satisfied exactly as written**. Every gate is human in both modes; agents propose harder in one of them. `PIPELINE` §5 (the six gates) and §3.9 (the change protocol) are unchanged. **No `/tune`, no version bump, no Tier-1 edit.**

The only canon-adjacent addition is documentation: `PIPELINE` §2.1 may gain one sentence noting that a phase's artifact may be reached by conversation or by draft, and that the gate is identical either way. That is a clarification, not a rule change.

## 8 · What gets built

Small, because the pipeline is untouched:

- **`episode.phase_modes`** — `{idea: co_create|draft, script: …, vision: …, …}` on the episode record, defaulted per §3, editable at any gate.
- **A `draft()` entry point per phase agent**, beside the existing conversational one: same system prompt and canon contract, different task framing — *"decide everything yourself, emit the artifact plus a decision journal, and attach any assumption you had to make."* One extra structured-output field (`decisions[]`), not a second agent.
- **Journal rendering** — free; it is the existing proposal card.
- **Redraft-with-note** — the reject path, bounded.
- **Seed bank** — `direction` entities tagged `seed` with drawn/consumed marks. The state layer exists.
- **`auto_reroll_on_technical_failure`** (default 0) wired into the §16.6 pre-return gate.
- **UI (Phase 2 wireframe):** a per-phase mode toggle on the phase rail · the four gate actions · journal cards in the chat · a spend line on every generate action (*"this will generate 1 sheet · ~$0.13"*) so cost is visible **before** the click, never after.

**No new tables. No new agents. No new gates. Nothing about the five phases, the artifacts, the canon contracts, or the recompile graph changes.**

## 9 · Failure modes

| Failure | Guard |
|---|---|
| Drafted work is technically valid but creatively flat | the seed bank · the correction flywheel · QC flags ride to the gate · Co-create is the default where it matters (Script) |
| Rubber-stamping a drafted artifact because it looks finished | the decision journal makes the *choices* reviewable, not just the output; attached assumptions are surfaced at the gate |
| Redraft looping | bounded (default 2), then the agent asks instead of retrying |
| Surprise spend | every generation is downstream of an approval; the one exception is opt-in, capped, journaled, default OFF; cost shown before the click |
| Draft mode quietly becoming the default everywhere | it is per phase and visible on the rail; Script defaults to Co-create every episode |

## 10 · Decision for Jayon (D8, revised)

1. Confirm the axis (§1) and the money rule (§2).
2. Confirm the per-phase defaults (§3) — **Script defaults to Co-create; Vision/Shoot/Post default to Draft**, since their contracts already forbid invention.
3. Set `auto_reroll_on_technical_failure`: **0** (nothing generates twice without you) or **1** (one silent re-roll on an objective render fault only). Recommend starting at 0 and revisiting once real generation costs are known.

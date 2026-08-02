# DESIGN — Autopilot: delegated gates, the decision journal, and the trust ladder

> **Status: PROPOSAL for Jayon's confirmation (2026-08-02).** Jayon's direction, responding to the outside review's D3 ("850 approval moments; the studio will be abandoned by episode 50"): the studio must ALSO be able to produce an episode with **no human in the loop** — agents choosing the lesson, the story, the cast, the shots, "just like a human would creatively and very deliberately" — while the human can drop in at any moment, understand everything that was decided, and change it.
> **The verdict this doc argues:** incorporate it NOW at the architecture level (it is cheap there), enable it in stages by evidence (that part cannot be rushed), and do it without external deep research — the mechanism patterns are already in our two agent-engineering reports and the invideo guides; the only missing knowledge is calibration evidence that can only come from our own episodes.
> Companions: `PIPELINE.md` §5 (gates) · `MISSION.md` §5 (the philosophy this amends) · `DESIGN_studio_ux.md` · `DESIGN_screenplay_document.md` · `BUILD_PLAN_v4_studio.md`.

---

## 1 · The reframe that makes this compatible with everything we built

The studio's gates were designed as **decision points** — places where a choice becomes binding and downstream work inherits it. Nothing about a decision point requires that a *human* operates it; it requires that the decision is **made once, recorded, and reversible at a known cost** (the recompile graph).

> **Autopilot does not remove gates. It changes who signs them. The signature is always logged.**

So: every gate gets a **policy** — `manual` (wait for Jayon) or `auto` (self-approve under conditions, §3). An episode runs with a policy set chosen at start. The pipeline, the artifacts, the proposal cards, the QC chips: all identical in both modes. The ONLY difference is where the confirmation comes from.

This is why the feature is cheap **for us specifically**: the expensive parts of safe autonomy — deterministic hard validators, a non-speaking QC, typed proposals with recompile sets, append-only state, artifacts-on-disk, standing constraints — are already built and tested (52-assertion spine suite). Most systems bolt autonomy onto vibes. Ours bolts it onto gates that already know exactly what "passing" means.

## 2 · What has to be true before ANY gate self-approves

An `auto` gate approves only when ALL of:
1. **Zero hard blocks.** Every deterministic validator passes (`validate_*_v4`, the canon closed sets, ceilings, banned vocabulary). Already built.
2. **QC blocks empty.** The 12-point audit's BLOCK items clear. FLAG items don't stop autopilot — they are **recorded on the episode for the review** (§6).
3. **No high-impact ambiguity.** The single-question gate inverts: where the agent would ask a structural question, autopilot does NOT guess — low-impact ambiguity resolves from documented defaults (canon → standing constraints → state), high-impact ambiguity **parks the episode** (§5). Parking is the autopilot version of asking.
4. **Budget intact.** The governor (§4) has headroom.

If any fails after bounded retries → **park, never push through**. MISSION §6: "if it feels like slop, it is" — autopilot's version is "if it can't pass the checks, it stops."

## 3 · The trust ladder — four levels, enabled by evidence, never by optimism

| Level | Name | Auto gates | Manual gates | Enabled when |
|---|---|---|---|---|
| **L0** | Co-pilot | none | all | today |
| **L1** | Drafting | brief lock · screenplay confirm | sheet · clips · export | the golden-dataset judge runs and agrees with Jayon's own verdicts on ~10 episodes |
| **L2** | Production | + sheet approval · clip acceptance (budget-capped) | export | C1 identity test passed · real Seedance voice test passed · per-clip price known |
| **L3** | Full autopilot | all five | **publish only** | ≥N L2 episodes where the export review changed nothing material |
| — | Publish | **never auto** | always | permanent. Posting is outward-facing and reputational; it is the one gate that stays human forever. |

Two properties of the ladder:
- **It follows the risk gradient.** Text artifacts are ~free to regenerate → delegate early. Paid generations are bounded by the governor → delegate second. Publishing is unbounded (reputation) → never.
- **L2/L3 are gated on exactly the validations the outside review demanded** (C1, voice, price). Autopilot doesn't compete with the ten-day list — it *depends* on it.

**Batch mode is the actual speed win:** "produce the next 3 episodes at L3 overnight" → a queue; each episode either reaches the export review or parks with a stated reason. The morning view is a **review queue**: finished episodes, each with its decision journal, its accumulated flags, and its takes.

## 4 · The budget governor

An unattended loop with a credit card needs a governor. Per-episode, configurable, park-on-breach:
- max **2** QC rewrite loops per artifact · max **2** sheet regenerations per segment · max **3** clip takes per segment (the ~25% keep-rate reality, bounded) · max **$X** total spend per episode · max wall-clock per episode.
- Every spend is ledgered per stage (already built); the governor reads the same ledger.

## 5 · Parking — how autopilot asks questions

A parked episode is a first-class state, not a failure: `parked(reason, at_gate, artifacts_so_far)`. It appears in the Home queue with the exact question the agent would have asked. Jayon answers it (one tap or one sentence) → the episode resumes from that gate with everything upstream intact. High-impact ambiguity, canon contradiction (`SHOW_BIBLE` §15.4), budget breach, and repeated QC failure all park. **Autopilot never resolves a canon contradiction and never writes a Tier-1/Tier-3 fact** — candidate canon facts queue for batch human confirmation even at L3 (mechanical writes — atoms taught, appearances, coverage — stay automatic; they are objective).

## 6 · The decision journal — "come by and understand"

Every decision an agent makes at an auto gate is emitted as the SAME proposal card the change protocol already produces — options considered, choice, reasons, recompile set — just confirmed by policy. Consequences:
- An autopiloted episode's thread **reads like a co-piloted session**. Scroll it and you see every fork: *"Lead: Müller das Brot — rotation coldest + Pfand situation fit; considered Rolf, rejected: led A1.8.2."*
- **Chip-in is retroactive and cheap:** reopening any journal entry IS the change protocol — propose → recompile set → confirm → apply. Nothing about intervention had to be designed twice.
- **Pause/take-over:** episodes are sequential state on disk; a running episode can be paused at the next gate boundary and continued manually from exactly there.
- Accumulated FLAGs ride on the episode into the export review — autopilot never launders a warning.

## 7 · The honest hard part: unattended creativity (not the mechanism)

`STORY_SYSTEM` §9.1 is blunt: the human seed is the **most reliable** anti-slop disruptor, and "an agent's unprompted invention is the least." Autopilot removes the per-episode seed. Mitigations, in order of strength:
1. **The seed bank.** Jayon drops ideas, observations, overheard scenes in bulk into Directions/UNIVERSE_STATE whenever he has them (the `/idea` reflex, aimed at the show). Autopilot **draws one seed per episode** and marks it consumed. The human's creative DNA stays in every episode without the human being present at any gate. *An empty seed bank is a legitimate parking reason at strict settings.*
2. **The flywheel already built:** every manual correction in co-pilot mode becomes a stratum-4 rejection/approval, injected into every later run (`constraints_block` — built, tested). **Co-pilot sessions train autopilot.** L0 episodes are not the slow path; they are the calibration data.
3. The existing variety engine: rotation, coverage log, oblique constraints, banned-cliché lists — all deterministic, all already designed.
4. The LLM judge (BUILD_PLAN 4.2) becomes load-bearing at L1+: it is the taste-check that runs when Jayon isn't looking, and the internalization suite (`RESEARCH_invideo_production_guides` §3) is its pre-flight.

## 8 · Canon impact — the one philosophical edit (Jayon's call, D8)

`MISSION` §5 currently: *"The human decides; agents propose… they never make the creative call."* and *"Human gates are features, not gaps."* `PIPELINE` §3.9: the change protocol must not *"apply anything without confirmation."* Autopilot, as designed, amends rather than contradicts:

> **Proposed MISSION v2.2 language:** "The human decides — at the gate, or in advance by policy. Delegation is explicit, bounded by budget and hard checks, journaled decision-by-decision, and reversible at the known recompile cost. Publishing is never delegated."

`PIPELINE` v1.3: §5 gains the policy column + parking; §3.9 "without confirmation" → "without a confirmation, which policy may supply." QC's contract is unchanged (it never speaks; its blocks simply become binding when nobody is watching). **These are Tier-1 edits and run through the /tune ritual on Jayon's explicit confirmation.**

## 9 · What gets BUILT (small, because the architecture pays off)

- `episode.run_policy` (per-gate policy + level preset + budget) on the episode record; chosen at start, changeable mid-flight.
- The **gate executor** in `studio.py` (Phase 2): at each gate, read policy → wait / evaluate §2 conditions → sign + journal, or park. ~100 lines, because validators/QC/proposal cards all exist.
- **Parking** state + Home queue + resume.
- **Seed bank** = `direction`-type entities with a `seed` tag + drawn/consumed marks (state layer exists; trivial).
- UI (Phase 2 wireframe): mode selector at episode start ("this one together" / "draft it, I'll review" / "full auto") · the review queue · journal rendering (free — it's the chat) · pause/take-over · budget meter.
- No new tables, no new agents, no framework. **Nothing about the five phases, the artifacts, or the canon contracts changes.**

## 10 · Do we need deep research? — No, and here is the honest reasoning

- **The mechanism** (HITL delegation, approval policies, bounded autonomy, always-ask vs autonomous modes) is covered by material we already hold: the Production Engineering Guide (propose-confirm-apply, idempotency, ambiguity split), the Creative AI Agents report, and the invideo guides ("always-ask mode… the approval gate is where the shot plan earns its keep" — theirs is our L0; their agents' autonomous mode is our L2/3).
- **The unknown is not researchable from outside:** whether OUR agents' unattended output meets OUR bar, on OUR cast, in German. That evidence comes only from co-pilot episodes + the judge — which the ladder already requires before anything unlocks.
- One narrow research prompt MAY be worth it later (LLM-judge calibration for subjective creative quality at L1), but we hold the Booking.com-style method already; write it only if the judge disagrees with Jayon in practice.

## 11 · Failure modes

| Failure | Guard |
|---|---|
| **Silent mediocrity** (technically valid, creatively flat) | the judge at L1+ · flags accumulate, never vanish · spot-check ratio (fully review 1 in N even at L3) · the seed bank |
| **Drift compounding across unattended episodes** | canon facts never auto-written · continuity audit on the cut (Gemini reads video) · C1-style identity checks at the sheet gate |
| **Runaway spend** | the governor; park-on-breach |
| **Autopilot guessing on structure** | the inverted question gate: parks, never guesses |
| **Trust jumped ahead of evidence** | the ladder's unlock criteria are written down; `canon-audit` can check the current level against the evidence flags |
| **The journal becoming noise** | journal entries are the same compact proposal cards as manual mode; the review queue shows per-episode summaries first |

## 12 · Decision for Jayon (D8)

1. Approve the reframe (§1) + ladder (§3) + publish-stays-manual — then MISSION v2.2 + PIPELINE v1.3 go through /tune.
2. Approve parking as the ask-mechanism (§5) and the seed bank (§7.1).
3. Set the L3 spot-check ratio (recommend: fully review 1 in 5 at first) and a default per-episode budget cap once the real clip price is known.

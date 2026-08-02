# DESIGN — The UI design system: method, tokens, and the Claude Design round-trip

> **Status: METHOD LOCKED (2026-08-02), nothing built yet.** Distilled from the two design-research reports Jayon commissioned (`resources/AI Design Tooling Workflow Guide.md` · `resources/AI-Powered Interfaces Research Report.md`) into the decisions that actually bind our build. **This is the how-to for the UI rebuild; `DESIGN_screen_home.md` is the what-to-build for screen 01.**
> Governing principle, Jayon's words: **KISS — keep it stupid simple.**

---

## 1 · The diagnosis both reports independently give

They converge on the same failure, and it is exactly what our 2.2 wireframe was:

> **"The AI-generated admin panel"** — flat, dense, unprioritised; every field at equal visual weight; no progressive disclosure; a sterile, generic aesthetic.

And on the same root cause: **an AI cannot invent an interaction paradigm.** It averages what it has seen, which is SaaS dashboards. If we do not supply the spatial architecture, we get a dashboard — from Claude Design, from Figma Make, from me. The structure must be decided *before* any tool is opened.

## 2 · What we are building, in their vocabulary

Not a dashboard. A **professional studio tool**, used for hours, daily, by an expert — closer to DaVinci Resolve or Ableton than to a web app. That analogy is load-bearing and gives us three structural rules:

1. **Fixed functional zones, not scrolling pages.** A canvas (the artifact under work), a **ledger** (the conversation — our thread already is this), and an **inspector** that changes content by selection rather than adding new panels.
2. **Phases are workspace configurations, not wizard steps.** Resolve switches Media/Cut/Edit/Fusion/Color/Deliver because each is a different cognitive mode. Our Plan/Idea/Script/Vision/Shoot/Post are the same thing — the window *rearranges*, it does not merely advance.
3. **Productive density beats airy whitespace** — but density is earned through typographic discipline, not by cramming.

## 3 · The token architecture (binds every future UI commit)

Vanilla CSS, no build step, so the system lives in native custom properties at `:root`, in **three tiers**:

| Tier | What | Example |
|---|---|---|
| **Primitive** | raw values, no meaning | `--gray-900: #161616` · `--space-base: 4px` |
| **Semantic** | purpose, referencing primitives | `--surface-background: var(--gray-900)` |
| **Component** | scoped, referencing semantic | `--inspector-bg: var(--surface-background)` |

**The rule that makes it real: if it is not a token, it does not ship.** No hardcoded hex, no inline styles, no arbitrary spacing. This is the same discipline as our hash-pinned canon, applied to CSS — and like canon, it needs a detector rather than a promise (§7).

**Starting decisions for a dense professional tool** (from both reports, adapted):
- **Type:** base 13–14px, a constrained scale — **four sizes maximum** in the operational UI. Micro-tracking (~0.16px at 14px) so dense text stays legible.
- **Spacing:** 4px base grid. Tight (4–8px) *inside* a group, loose (16–24px) *between* groups. **Whitespace groups and separates — it is the primary hierarchy tool.**
- **Elevation: borders and background steps, not shadows.** A 1px border and a slightly different surface, never a drop shadow.
- **Radius: 0–4px maximum.** Larger radii read as consumer toy, not instrument.
- **Colour:** a neutral ground with **one** accent for primary action, plus warning and error. Everything else is neutral.
- **Explicitly banned** (the AI-cliché list): purple-blue gradients · glassmorphism · floating cards · soft oversized shadows · decorative icons without labels · centred-everything.

## 4 · Designing STATE — our hardest problem, and where generic kits are useless

Both reports single this out, and it is the part of our product no UI kit covers. Our states are real and numerous: a gate is open/blocked/locked; an artifact is drafting/generating/ready/**stale**; a job has 3 takes and 1 keeper; a button **costs money**.

The principle: **an AI-generated artifact must never look like a human-approved one.** Undifferentiated states are how trust erodes.

| State | What it must communicate | How |
|---|---|---|
| **Provisional / generating** | work in progress, will change | dashed border · muted opacity · skeleton, never a blank |
| **Locked (approved)** | finished, immutable | solid high-contrast border · edit actions removed from view |
| **Stale** | upstream changed, needs attention | warning accent · an explicit reason, not just a badge |
| **Blocked (QC)** | cannot proceed, and why | the failing check named at the point of failure |
| **Failed** | dignity + a way out | the specific error *plus* the manual override, never a dead end |
| **Costs money** | before the click, never after | the price on the button (`~$0.27`), and "unknown" when we truly do not know |

Two named concepts worth adopting verbatim: **Confidence Visibility** (a drafted decision should not look like a confirmed one) and **Failure State Dignity** (a failure explains itself and offers a path, never a blank screen).

## 5 · Progressive disclosure — the fix for "every field is visible"

**The inspector is the mechanism.** One fixed zone whose *content* changes with selection replaces dozens of always-visible fields. Click a shot → the shot's fields. Click a take → the take's. Same space.

- **Core vs periphery:** on screen permanently = the minimum needed to judge the current state. Everything else — parameters, prompts, negative prompts, settings — lives in the inspector.
- **Hover/focus reveal** for secondary actions (edit, duplicate, delete).
- **Inline truncation** for long agent reasoning: two lines, expand on demand.
- **Keyboard primacy** for high-frequency actions; a command palette for the rare ones. For an expert tool, the mouse is the slow path.

## 6 · The tool decision — settled

| Job | Tool | Why |
|---|---|---|
| **The design system + real screens** | **Claude Design + Claude Code** | Our components *are* HTML/CSS. `/design-sync` is bidirectional and incremental — one component at a time, never a wholesale replace. Code tokens stay the source of truth. |
| **Spatial exploration, visual identity** | **Figma / Figma Make** | A sketchpad. Its React/Tailwind output is unusable in our stack, so we take the *idea*, not the code. |
| **Stateful screens** | **code, always** | A Figma frame shows one state. Our design problem *is* the states — they must be clickable. |

**Order that matters:** create the design system project **first**, publish it, then generate screens against it. Prompting for screens before the system exists is how you get a dashboard.

## 7 · Keeping it coherent — the detector, not the promise

Design drift is the same class of failure as canon drift, and we already know the answer: **build the detector**. A future `ui-audit` (alongside `canon-audit`) scanning the HTML/CSS for hardcoded colours, inline styles, off-scale spacing, and off-token radii. *If it is not a token, it does not ship* — enforced by a command, not by memory.

## 8 · Prompting for design (the playbook, condensed)

Vague adjectives ("clean", "modern", "sleek") produce the average of the training data. What actually works:
1. **State the spatial rule explicitly** — "a single-column chronological ledger left, a contextual inspector right; do not use a multi-column grid for the ledger."
2. **Enforce the tokens by name** — "use `--text-primary`, `--space-2`; introduce no new values."
3. **Ban the clichés explicitly** — "no box-shadows for elevation; borders and background steps only; radius ≤4px; no gradients."
4. **Demand the states** — "show the provisional card mid-generation *and* the locked card, side by side."
5. **Feed real data** — our actual German lines, real lesson titles, a real screenplay. Lorem produces layouts that break on contact with reality.
6. **Vary ONE parameter per variant.** "Three variants" of one prompt returns three of the same thing; changing the layout axis or the density per prompt forces genuine difference.

## 9 · The critique checklist (run on every generated screen, in this order)

1. **Squint test.** Blur it. If it reads as one uniform grey block, there is no hierarchy.
2. **Remove all borders mentally.** If the layout collapses, whitespace is not doing its job — borders are propping it up.
3. **What catches the eye first?** Is that actually the most important thing? AI routinely emphasises the wrong element.
4. **Spacing rhythm.** If every gap is identical, there is no rhythm — tight inside groups, loose between them.
5. **Token integrity.** Read the markup: any hardcoded hex, inline style, or off-scale value is a regression.
6. **Edge states.** Empty, loading, error, stale, very long content, missing image. AI designs the happy path only.
7. **Icons.** Does each one *mean* something, and is it labelled? Decorative icons out.
8. **Real content.** Placeholder text hides layout failures.

## 10 · The workflow, in order

1. **Screen brief** — its one job, the decision it supports, primary/secondary/on-demand, every state. *(Home's is written.)*
2. **Spatial zones** — sketch the fixed regions before any styling.
3. **The design system** — tokens in `:root`, then the component library; publish to Claude Design.
4. **Screens against the system**, one variant axis at a time.
5. **Critique (§9), then iterate.**
6. **Wire to `/api/studio/*`** — already built and layout-agnostic.

## 11 · The honest failure modes to watch

- **The Dashboard Fallacy** — treating a stateful studio as a data dashboard. This is what we already did once.
- **Token override drift** — one inline style to fix one bug, repeated for months.
- **Skipping fundamentals** — AI tooling *exposes* a missing design system rather than substituting for one.
- **Accepting the first output** — it is a draft. The critique loop is the work.

# Deep-Research Prompt — Designing a serious interface with AI tooling (Claude Design + Claude Code + Figma)

> **Purpose:** paste the block below into a deep-research tool. We have a working system, a settled information architecture, and a wireframe that is structurally right and **visually and experientially wrong**. This research answers: *what is the actual 2026 workflow for taking a functioning prototype to a properly designed product with a real design system, using AI design tooling — and what does that tooling not do?*
> **Created:** 2026-08-02. Feeds the UI rebuild (BUILD_PLAN Phase 2.3b).
> **Note for the researcher:** we are NOT asking "how do I make an app look nice." We are asking how a solo builder runs a rigorous design process when the implementation partner is an AI.

---

## THE PROMPT (copy from here) ⬇

You are a senior product designer who has shipped interfaces at a company known for craft, and who has spent 2026 working with AI design tooling in real production. Write a **practical workflow guide**, not a tool review.

### My situation
- I am one person building a **professional creative tool** — a studio where a human and a crew of AI agents make short video episodes together. It is used daily, for hours, by an expert (me). It is not a consumer app and not a landing page.
- **The system already works.** The data model, the state machine, the agent contracts and the API are built and tested. The information architecture is settled: five phases, one continuous conversation, human approval gates, artifacts that lock.
- **The interface is the problem.** My current screens are dense, flat, badly prioritised, and read as "AI-generated admin panel". Every field is visible at once, nothing is progressively disclosed, there is no type scale, no spacing system, no visual hierarchy — no design system at all.
- **Stack: plain HTML/CSS/vanilla JS served by a Python backend.** No React, no Tailwind, no build step. This is deliberate and I want to keep it.
- **Tools available:** Claude Code (agentic coding in my repo), **Claude Design** (`claude.ai/design` — design-system projects with a synced local component library), Figma + Figma Make.

### Answer these

**1 · The process, before any tool.** What are the actual steps a serious designer takes between "the system works" and "the interface is designed"? Screen briefs, job stories, information hierarchy, state inventories, flow diagrams — what is genuinely load-bearing versus ceremony a solo builder can skip? Where in that sequence does a design system get created — before the screens, extracted from them, or in parallel?

**2 · Building a design system that is not generic.** How do you arrive at a visual language with a point of view, rather than the shadcn/Linear/Vercel default that AI tools converge on? Concretely: how do you choose a type scale, a spacing rhythm, a colour system, density, borders and elevation for a **professional tool** (dense, keyboard-driven, long sessions) rather than a marketing site? What are the specific decisions that make an interface read as *designed* rather than *assembled*? Name real reference products for dense creative tools — DAWs, NLEs, 3D software, terminals, Linear, Figma itself — and what each does structurally that is worth stealing.

**3 · Claude Design specifically.** How is `claude.ai/design` actually used in a real project? What is the round-trip with a local component library and the `/design-sync` workflow — what lives locally, what lives in the project, how do component preview cards work, how do you iterate on one component without breaking others? Where does it fit against Figma? Give a concrete worked sequence for someone who already has code and needs a design system, not the reverse. **If public documentation is thin, say so plainly** and construct the workflow from what is documented plus general design-system practice, marking which parts are inferred.

**4 · Figma and Figma Make in this workflow.** Given a non-React codebase, what is Figma genuinely worth here? Is it for exploring visual identity only, or is there a real path from Figma to hand-written HTML/CSS that doesn't waste the design work? What does Figma Make actually produce, and what happens to it when your stack doesn't match its output? When is Figma the wrong tool for a stateful, dense tool interface — because a frame shows one state and a real UI has dozens?

**5 · Designing STATE, not screens.** My interface is mostly states: a gate that is open/blocked/locked, an artifact that is drafting/generating/ready/stale, a job with 3 takes and one keeper, warnings that are advisory versus blocking. How do good designers enumerate, design and document state? What patterns exist for showing "this is provisional", "this is locked", "this costs money if you click it", "this is stale because you changed something upstream"? This is the hardest part of my product and every generic UI kit ignores it.

**6 · Progressive disclosure for expert tools.** How do you decide what is on screen, one click away, or hidden? What are the real patterns for an interface with a lot of true complexity that must not feel complex — and how does that differ for an expert daily user versus a newcomer? Where do inspectors, panels, drawers, inline expansion and command palettes each actually belong?

**7 · Reviewing AI-generated UI like a designer.** When an AI produces a screen, what do you look at, in what order, to judge it? Give me a repeatable critique checklist that catches the specific ways AI-generated interfaces fail — uniform spacing with no rhythm, no hierarchy, everything the same weight, decorative borders, meaningless icons, centered-everything, no empty states, no loading states, no error states.

**8 · Prompting for design quality.** What actually changes an AI's design output? Is it reference products, constraints, a design system passed as tokens, critique loops, or asking for variants? What is measurably useless? How do you get genuinely *different* options rather than three versions of the same layout?

**9 · Keeping it coherent over months.** How does a design system stay real once code is being written fast — tokens as the single source, component inventories, drift detection, a review ritual? What rots first?

**10 · The honest failure modes** of designing this way, and what you would do differently.

### Deliver
A **workflow I can start on Monday**: the ordered process · a design-system starting kit for a dense professional tool (what to decide, in what order, with the reasoning) · the Claude Design round-trip explained concretely · a critique checklist · a prompting playbook · and a clear statement of which tool to use for which job, and which to skip.

Prefer 2026 practitioner sources — real teams' write-ups, design-system documentation, and hands-on accounts of Claude Design / Figma Make in production — over vendor marketing and listicles. **Where a tool's behaviour is undocumented or changing, say so explicitly** rather than guessing. Optimise every recommendation for **one person who can write code, has taste but not formal design training, and is building one tool they will use every day for years.**

## ⬆ (copy to here)

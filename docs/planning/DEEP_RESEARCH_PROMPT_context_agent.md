# Deep-Research Prompt — The Project-Context Agent (persistent memory for creative AI systems)

> **Purpose:** paste the block below into a deep-research tool. Goal: understand how creative-AI products give their agents a persistent, project-wide memory (invideo AI's Agent "context" is the trigger case), and come back with an architecture we can build.
> **Created:** 2026-07-29 (v2 — rewritten open; v1 was over-specified and would have just validated our current design). Our pipeline and stack are **explicitly open to change**, so the prompt does not describe them.
> **Consumer:** the output goes to the Claude session that builds the platform — so it must end in concrete mechanisms and a build order, not just prose.
> **Leads:** invideo.io · OpenAI's invideo case study (indicates o3 as planner/orchestrator, GPT-4.1 for script) · launch video `https://www.youtube.com/watch?v=o1kH71QKxmA` (transcript is NOT machine-fetchable — must be opened directly) · arXiv *EM-Vid*, *PermaVid* (multi-shot / cross-edit consistency via entity memory).

---

## THE PROMPT (copy from here) ⬇

You are a senior AI systems architect. Research and report on: **how AI creative tools give their agents a persistent, project-wide memory — a "context" layer that holds everything about a production so that what the AI generates stays consistent with what came before, without the user re-explaining the project every time.**

**The trigger case: invideo AI's "Agent context."** They claim their agent ingests your source material, saves what you build (characters, locations, look), remembers every approval and rejection so settled things stay settled, learns from your corrective notes, and — the interesting part — **works out what each new shot depends on and brings that memory in automatically** before generating. It also supports user-defined sub-agents (cinematographer, colorist, sound designer, etc.) sharing that same context. Start here: their site/blog/docs, the OpenAI case study on invideo, engineering talks and interviews, and their launch video (https://www.youtube.com/watch?v=o1kH71QKxmA — open it and use the actual transcript). Reconstruct how it actually works. **Their internals are proprietary: label each claim as documented fact or your inference, and say plainly when something is unknown.**

**Then go wide.** Don't stop at one vendor. Find whoever solves this well — other AI video/creative tools, agent-memory frameworks, coding agents with project memory, character/persona systems, established VFX and game-production asset pipelines, relevant research. Bring back the *pattern*, and anything good I wouldn't have thought to ask about.

### What I'm building (deliberately brief — I want your best design, not validation of mine)
A **serialized, character-driven short-video series** made mostly by AI, produced by one person over months:
- a **fixed recurring cast** whose look, voice and personality must never drift;
- a **continuous story world** that accumulates facts, places and relationships as episodes are made;
- a **fixed curriculum/goal** the series has to progress through, tracked over hundreds of episodes;
- a **multi-stage generation chain** (idea → script → images → video → edit), where each stage needs the right slice of established knowledge;
- an **overarching agent** that holds the whole picture and coordinates the specialist stages.

**My pipeline and tech stack are open and changeable** — recommend what is actually right, including a different architecture, if that's the honest answer. Optimize for a solo creator running a long project, not an enterprise team.

### What I need to understand
1. **The concept** — what this layer is, what it's called in the field, and what its parts are.
2. **What gets remembered, and how it's structured** — what kinds of knowledge need different treatment (things that must never change vs. things that evolve vs. history vs. decisions vs. raw uploaded material), and how each should be stored.
3. **How the right memory reaches each generation** — the hardest problem. How does a system determine what a given shot/scene depends on? Compare the real approaches (typed relationships and dependency resolution, semantic/vector retrieval, letting the model request what it needs, hybrids) and say when each wins and where each fails.
4. **How memory gets written** — what triggers a save, automatic extraction vs. explicit confirmation, how contradictions with established facts are detected and resolved, who's allowed to overwrite what.
5. **Decisions as memory** — how approvals become binding constraints and rejections stay rejected, and how taste/feedback is captured so it generalizes without over-fitting.
6. **Enforcing consistency, not just prompting for it** — binding reference assets to identities, validating a generation request against established canon before spending money on it, verifying output afterwards, and detecting drift across a long series.
7. **Many agents, one memory** — how a shared project memory is scoped per specialist agent, how they write back, how conflicts resolve, and where a human gate belongs.
8. **Scale and cost** — keeping context bounded as the project grows to hundreds of episodes (summarization, compaction, caching, what to inline vs. fetch).
9. **How it fails** — the real failure modes (stale or contradictory memory, retrieving the wrong thing, drowning the prompt, silent drift, memory the user can't see or correct) with detection signals and mitigations.
10. **Anything important I haven't asked about.**

### Deliver
An executive summary and architecture diagram; the invideo teardown (fact vs. inference); a comparison of how the best systems do it; the mechanisms explained concretely enough to implement (data models, rules, pseudo-code where it helps); **a recommended architecture for my case**, including what to build first, what to defer, and what would be over-engineering at my scale; a failure-modes table; and an annotated source list.

Prefer primary sources and current (2026) specifics over generic overviews. Be concrete and honest about uncertainty.

## ⬆ (copy to here)

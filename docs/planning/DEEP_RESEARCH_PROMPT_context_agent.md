# Deep-Research Prompt — The Project-Context Agent (persistent memory for creative AI production systems)

> **Purpose:** paste the block below into a deep-research tool (Gemini Deep Research / ChatGPT Deep Research / Claude Research). It researches **how creative-AI products give their agents a persistent, project-wide "world model"** — invideo AI's Agent "context" system as the primary case study, plus comparable products and the academic mechanisms — and returns an **implementable architecture** we can build for our own universe-building platform.
> **Created:** 2026-07-29, for Jayon. Feeds the Showrunner / `UNIVERSE_STATE` layer of the V4 pivot (`CURRICULUM_v1_universe.md` §6, `DESIGN_story_ideation_and_overseer.md`).
> **Consumer of the output:** the resulting document is handed to the Claude session that builds our platform — so it must contain schemas, retrieval/update rules, pseudo-code and a phased plan, not just prose.
> **Leads found while drafting (give these to the researcher):** invideo's own site + blog (invideo.io) · the OpenAI case study on invideo (openai.com/index/invideo-ai) — states a multi-agent design with **o3 as planner/orchestrator** and **GPT-4.1 for script/narrative** · the launch video `https://www.youtube.com/watch?v=o1kH71QKxmA` (transcript NOT machine-fetchable — the researcher must open/caption it) · arXiv: *EM-Vid* (training-free entity-centric memory for multi-shot consistency), *PermaVid* (consistent video across edits via disentangled context memory), *AI Hippocampus* memory survey.

---

## THE PROMPT (copy from here) ⬇

You are a senior AI systems architect. Produce a **comprehensive, citation-backed, implementation-ready report** on one specific thing: **how modern creative-AI production tools give their agents a persistent, project-wide memory ("context") so that generated output stays consistent with everything the user has established — and how to build such a system myself.**

### Why I'm asking (the system I'm building)
I run a small, self-hosted pipeline that produces a **serialized, character-driven German-learning video series** for Instagram. Relevant facts:
- **Fixed cast of 4 recurring characters** with locked visual identities (reference images: multi-angle character sheet + portrait + voice clip each) and locked personalities/speech patterns (a written "character bible").
- A **locked A1→B1 curriculum**: 30 modules containing 164 "teaching atoms" (each = one German pattern + exemplar sentence). Atoms get packed into **universal 30-second episodes**.
- A **growing serialized narrative** (a story universe that accumulates plot facts, relationships, locations, running gags) plus a **library of 100 cultural stereotypes** used as optional scene ingredients.
- A **linear compile pipeline**, already built: idea chat → **story brief** → **screenplay (the LOCK)** → storyboard sheet-prompts (one multi-panel image generation per ~15s segment) → video prompts (multi-reference video model) → assembly → subtitles → publish. Downstream stages are **deterministic compilers** of the screenplay, so any edit has a well-defined recompile set.
- **Stack:** Python + FastAPI backend, vanilla-JS single-page frontend, LLM = Gemini (structured JSON output), artifacts persisted as JSON files per run, a Postgres/Supabase event ledger, hash-pinned "canon" files, and an existing overseer agent that plans typed edit-operations which the human confirms before deterministic application.
- **What I lack:** a single **overarching "everything agent"** that holds the whole project (goal, curriculum progress, story-so-far, cast, style rules, past decisions, what's been taught, what's been approved/rejected) and **automatically supplies the right subset of that knowledge to every stage and every sub-agent**, so nothing drifts and I never re-explain my project.
- **Design constraint (important):** I want the *ideas*, adapted to a **small, single-developer, mostly-file-and-Postgres stack**. Recommend the simplest mechanism that achieves each goal; explicitly flag anything that is enterprise over-engineering for my scale.

### Primary case study: invideo AI's Agent "context"
invideo AI markets a project-context system with these claimed behaviors (my paraphrase of their marketing — verify, correct, and go deeper):
1. **Ingests source material** (script, treatment, brief, deck, brand guidelines, references) and "saves what it learns to context."
2. **Saves what you build** as you build it — characters, locations, look — so they don't change as the project grows.
3. **Remembers every decision** — approvals and rejections; "settled stays settled, nothing gets reopened forty shots later."
4. **Learns from corrective notes** — user feedback updates what it knows.
5. **Knowledge compounds** — return after a week and it still knows the project.
6. **Brings the right memory to every shot** — "works out what this shot depends on and brings it in" (this character's approved look, this location's light, the rule set for this beat, a reference pointed at weeks ago).
7. **Owns consistency/continuity** as a system responsibility rather than the user's.
8. Ships alongside **user-definable sub-agents** (e.g. scriptwriter, cinematographer, sound designer, colorist, editor), a **storyboard view**, a **timeline editor**, and **real-time multiplayer**.

**Research questions on invideo specifically:** What is publicly documented about the actual implementation? Cover: their multi-agent architecture (public sources indicate **o3 as planner/orchestrator** and **GPT-4.1** for script/narrative — confirm, and map which model does what); how "context" is represented and stored; whether it is retrieval-based (vector/semantic), structured-state-based (typed entities), or a hybrid; how references/images are bound to entity identities; how approvals/rejections are represented and enforced downstream; how context is scoped to sub-agents; how they handle context-window limits, compaction and staleness; multiplayer/shared-state implications. Use: their site/blog/docs/changelog, the OpenAI case study, engineering talks and podcast/YouTube interviews (**including `https://www.youtube.com/watch?v=o1kH71QKxmA` — open it and use the actual transcript/captions**), job postings (they reveal stack choices), patents, and hands-on reviews. **Where internals are not public, say so and label your reconstruction as inference.**

### Comparative landscape (do not skip — I need the pattern, not one vendor)
Analyze how these solve the same problem, and what each does *better* than invideo: **LTX Studio** (character/asset consistency across shots), **Runway** (references/presets), **Luma**, **Adobe Firefly Services / GenStudio** (brand kits, content credentials), **Showrunner / Fable**, **Character.ai / Inworld** (persona + long-term memory), **coding agents with project memory** (Cursor rules & memories, Claude Code CLAUDE.md/memory, Windsurf, Devin's knowledge), **doc/work tools** (Notion AI, Linear), and **game-dev / VFX pipelines** (story bibles, asset databases, shot-dependency graphs in Shotgun/ftrack, USD asset resolution). Also cover **agent-memory frameworks**: MemGPT/Letta, Mem0, Zep/Graphiti, LangGraph checkpointers + store, CrewAI/AutoGen memory, LlamaIndex/RAG patterns, and knowledge-graph memory. For each: memory model, retrieval strategy, write policy, and what a solo developer should copy or avoid.

### The mechanism playbook (the core of what I need)
Explain each with concrete data models + rules, not generalities:
1. **Memory taxonomy.** Distinguish and define the useful tiers: *immutable canon* (locked identities, style laws) · *evolving world state* (story facts, progress, relationships) · *episodic history* (what was made when) · *decisions* (approvals/rejections/preferences) · *raw source material* (uploads/references). What belongs in each, and what the write rules are for each tier.
2. **Storage.** When plain versioned files beat a DB; when a relational schema is required; when vectors are actually needed vs harmful (semantic search retrieving *near-miss* facts is a known failure); when a graph/entity model earns its complexity. Give a recommended concrete schema (tables/JSON) for a project of my kind.
3. **Retrieval / context assembly — the hardest part.** How does a system "work out what this shot depends on"? Compare: (a) **deterministic dependency resolution** from typed relations (this shot → these characters → their approved looks; this beat → this location → its lighting), (b) **semantic retrieval** over an embedded memory store, (c) **agent-driven tool-call retrieval** (the model asks for what it needs), (d) hybrids. Give selection criteria, and a concrete **context-assembly algorithm** (with pseudo-code) including ordering, token budgeting, and what gets inlined vs summarized vs linked.
4. **Write policy / memory formation.** What triggers a save; automatic extraction vs explicit human confirmation; deduplication; contradiction detection and resolution (new fact vs established canon); who is allowed to overwrite canon; provenance and timestamps; forgetting/archival.
5. **Decisions as first-class objects.** How approvals become *binding positive constraints* and rejections become *persistent negative constraints* injected into later generations; how to prevent "rejected idea returns 40 shots later"; how to represent taste/preference feedback so it generalizes without over-fitting.
6. **Consistency enforcement.** Beyond prompting: reference-image binding to entity IDs, style/look locks, pre-generation validation ("does this prompt contradict established canon?"), post-generation verification (automated identity/style checks, human gates), and drift detection over long series. Include what the multi-shot-consistency literature contributes (e.g. entity-centric memory approaches such as *EM-Vid*, and edit-consistency approaches such as *PermaVid*) and what is practically usable today with commercial image/video APIs.
7. **Multi-agent context scoping.** How a shared project memory is projected into role-specific views for sub-agents (writer vs cinematographer vs continuity checker), so each gets what it needs and not the whole store; how sub-agents write back; how conflicts between agents are resolved; orchestration patterns (planner/orchestrator + specialists) and where a **human confirmation gate** should sit.
8. **Context-window economics.** Hierarchical summarization, rolling series "story-so-far" digests, compaction cadence, caching, and how to keep per-call cost bounded as a series grows to hundreds of episodes.
9. **Evaluation & observability.** How to measure that the memory is *working*: consistency/drift metrics, "did it use the right context" traces, regression tests for canon adherence, and what to log.

### Failure modes (be specific and unsentimental)
Document the known ways these systems fail and the mitigations: context poisoning/contradiction accumulation, stale facts, over-retrieval (drowning the prompt), under-retrieval (silent drift), semantic-search near-misses, memory bloat and cost creep, over-fitting to one rejection, canon corruption by an agent write, hallucinated "remembered" facts, and the UX failure of a memory the user cannot see or correct. For each: detection signal + mitigation.

### Apply it to my system (required section — this is what gets implemented)
Given everything above and my stack/constraints, deliver a **concrete architecture**:
- The **memory schema** for my project: what entities exist (project goal, curriculum atom, module, character, location, style rule, story fact, decision, reference asset, episode) and their fields/relations — as JSON/SQL.
- **Where each lives** (files vs Postgres vs neither) and why, at my scale.
- The **context-assembly contract per pipeline stage** — i.e. exactly which slices of memory the story-ideation agent, screenplay writer, storyboard-prompt compiler, video-prompt compiler, and continuity checker each receive, and in what order/format.
- The **write-back rules**: which stage updates which memory, at what moment, with what human confirmation.
- How the **"overarching agent"** (my Showrunner) should be defined: its responsibilities, its tools, what it decides vs proposes, and its prompt/context contract.
- A **phased implementation plan** (what to build first for immediate value, what to defer), plus an explicit **"do NOT build this yet"** list for my scale.
- Migration notes: I already have per-run JSON artifacts, an event ledger, hash-pinned canon files, and a typed-edit overseer — reuse them wherever possible rather than replacing them.

### Deliverable format
(a) Executive summary + a diagram of the recommended architecture; (b) the concept explained precisely (with the vocabulary used in the field); (c) **invideo teardown** with an explicit *documented fact vs. reasoned inference* label on every claim, plus a confidence rating; (d) comparative matrix across the products/frameworks listed; (e) the **mechanism playbook** with schemas, rules and pseudo-code; (f) the **applied architecture for my system** as specified above; (g) failure modes + mitigations table; (h) phased build plan; (i) annotated source list.

**Ground rules:** prioritize **specific, current (2026), implementable** detail over generic overviews. Prefer primary sources (vendor docs, engineering talks, papers, patents, job posts) over listicles. Where something is proprietary or unknown, say so plainly rather than guessing silently — and then give the best-practice equivalent I could build myself. Optimize every recommendation for a **solo developer maintaining a long-running serialized production**, not an enterprise team.

## ⬆ (copy to here)

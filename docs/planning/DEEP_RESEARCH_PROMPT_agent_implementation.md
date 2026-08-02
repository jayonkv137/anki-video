# Deep-Research Prompt — How to actually build the agents

> **Purpose:** paste the block below into a deep-research tool. We have finished designing *what* our agents must know (six canon documents) and *what each must do* (`PIPELINE.md`). This research answers the remaining question: **how are agents like this actually built, tested and maintained in practice?**
> **Created:** 2026-07-29. Feeds the build of four phase-agents (Showrunner · Writer · Director · Editor) sharing one continuous conversation.

---

## THE PROMPT (copy from here) ⬇

You are a senior engineer who has shipped production AI agents. Write a **practical, implementation-level guide** to building a small crew of specialised creative agents that a person works *with* — not a survey of frameworks, and not agent theory.

### What I am building
A studio where one creator and a few agents make a short video episode together, start to finish:
- **Four agents across five phases** — one that helps decide what the episode is, one that writes it, one that turns it into images and video prompts, one that finishes the cut.
- **They share one continuous conversation** that never resets for the whole episode. The phase decides which agent answers; the full history stays visible to whoever is speaking.
- Each agent reads a set of **written rule documents** (a show bible, a story method, a teaching standard, a visual treatment, a pipeline contract) and produces a **structured artifact** that the next stage compiles.
- **The human decides everything creative.** Agents propose, explain, check and execute — they never make the call.
- Stack is deliberately small: Python, a single LLM provider with structured output, files and a database. No agent framework yet, and I want an honest opinion on whether I need one.

### Answer these
1. **What an agent actually is at the code level.** Strip away the marketing: a system prompt, a context assembly step, optional tools, a loop, and a place to write. What are the real moving parts, what does a minimal but *good* implementation look like, and what do people needlessly add?
2. **Writing the role.** How do you write a system prompt that produces a genuine collaborator rather than a generic helpful assistant? What actually changes behaviour — persona, explicit refusals, worked examples, output contracts, ordering? What is measurably useless? How do you stop an agent being sycophantic, over-eager, or verbose?
3. **Many agents, one conversation.** Practical patterns for switching the acting agent mid-thread while keeping history: how to handle the handoff, whether the new agent should see everything or a summary, how to stop role bleed, and how to keep the conversation coherent so it reads as one team rather than several strangers.
4. **Context assembly.** How production systems decide what goes into each call — ordering, what to inline vs summarise vs fetch, how to keep long sessions affordable, and when to compact. What breaks first as conversations grow.
5. **Tools vs structured output.** When should an agent *call a tool* rather than simply return structured data the application acts on? Principles for designing tools an agent uses correctly, and the failure modes of giving an agent too many.
6. **Asking rather than guessing.** Techniques that reliably make an agent ask one good clarifying question instead of inventing an answer — and the reverse failure, agents that ask too much and stall the work.
7. **Proposing changes safely.** Patterns for propose → show the consequences → confirm → apply, where the agent plans and deterministic code executes. How do real systems present a change and its blast radius so a human can approve it quickly?
8. **Good agent vs bad agent.** Concretely, in creative-assistant work: what separates one that a user keeps using from one they abandon? Name the specific behaviours.
9. **Testing and tuning.** How do you test an agent whose output is subjective? Evals, golden examples, regression suites, LLM-as-judge and its traps. What does a healthy tune-and-measure loop look like when you cannot unit-test taste, and how do you know a prompt change made things better rather than differently bad?
10. **Maintenance over time.** Versioning prompts, keeping them aligned with changing rule documents, detecting drift, and what rots first.
11. **Frameworks — do I need one?** An honest assessment of LangGraph, CrewAI, Vercel AI SDK, Letta/MemGPT, plain provider SDKs and similar, *for a solo developer building four cooperating agents over a small stack.* What each genuinely buys, what it costs, and when raw is the right answer.
12. **Anything important I have not asked about.**

### Deliver
An implementation guide with **concrete artifacts**: an annotated system-prompt template that works · a context-assembly pattern with pseudo-code · the handoff pattern for multiple agents in one thread · a propose/confirm/apply pattern · an eval and tuning workflow · a failure-mode table with fixes · and a clear framework recommendation for my case.

Prefer engineering write-ups, production post-mortems, provider documentation and open-source agent implementations you can point to over vendor marketing. Where something is genuinely unsettled or contested, say so. Optimise every recommendation for **a solo developer maintaining this for years**, not a team shipping a demo.

## ⬆ (copy to here)

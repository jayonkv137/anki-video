# RESEARCH — Interactive Story-Ideation Agent (Socratic Story Strategist)

> **Source:** Deep-research brief supplied by Jayon (2026-07-23), "Technical Architecture for an Interactive Story Ideation Agent." Faithful archive (citation noise stripped).
> **Status:** Evidence library — the blueprint for **fixing the co-creation (Align & Diverge / story-idea) mechanism** into a disciplined Socratic partner, and for the **overseer agent** vision. Adapted to our stack in `DESIGN_story_ideation_and_overseer.md`.
> **Key adaptation:** the doc's stack is Vercel AI SDK (TS/Next.js). Our stack is **Python/FastAPI + Gemini + the existing studio UI** — we take the *pattern*, not the framework (see design doc §Stack).

---

## 1. Orchestration options (how to run the interactive chat)

| | LangGraph | OpenAI Assistants/Responses | Gemini/Vertex | Vercel AI SDK |
|---|---|---|---|---|
| State | explicit DB checkpointers | opaque server threads | Google-backend sessions | client + pluggable persistence |
| Streaming | needs custom adapters | polling (higher latency) | GCP-optimized | native sub-second edge |
| Human-in-loop | native `interrupt()` / `Command(resume)` | manual tool-output loops | predefined review gates | client tool loops + confirm hooks |
| Stability | open-source, stable | **legacy Assistants shuts down Aug 2026** | enterprise, GCP-tied | de-facto TS standard |
| Portability | provider-agnostic | OpenAI-locked | Gemini-locked | dozens of providers |
| Complexity | high (cyclic graphs) | low–med | med (GCP config) | low (ergonomic hooks) |

Doc's pick: **Vercel AI SDK** for a UI-embedded creative chat (streaming + tool-calls + context isolation). _(For us: adapt the pattern into FastAPI+Gemini; a heavy graph framework is overkill for a linear pipeline — see design doc.)_

## 2. The Socratic "Story Strategist" system-prompt framework

Turn the LLM into a **cognitive sandbox**, not a script generator:
- **Maieutics** ("intellectual midwife") — ask questions that make the *user* articulate the conflict/motivations, rather than dictating the plot.
- **Elenchus** (cross-examination) — test each user idea against the pipeline constraints; gently expose contradictions (too many locations, over-length, pacing).
- **Dialectic** — offer opposing branches / options to sharpen focus without breaking structure.

**Behavioral guidelines:** NEVER output the full screenplay/beat-list in chat · keep replies concise · end **every** turn with exactly ONE targeted question · build incrementally · politely refuse "just write the whole script."

**Four collaboration phases** (don't advance until the user approves the current one):
1. **High-Level Hook** — the central premise; how the fixed cast clashes for an instant visual hook.
2. **Narrative Arc & Tension** — lock the peak conflict + the payoff, inside the runtime budget.
3. **Segment Breakdown** — the sequence of visual beats (Setup → Escalation → Climax → Payoff); get feedback on the sequence.
4. **Verification & Handoff** — review; on explicit user approval, call the handoff tool.

## 3. The structured exit (handoff) — the critical state boundary

Ideation is fluid; the handoff must be **deterministic + schema-valid** so downstream compiles. The doc uses a tool-call `submit_final_story_concept` bound to a strict Zod schema:
- `finalizedStory`: `storyTitle · genre · corePremise · beats[3–6] · totalDurationSeconds(20–40)`, `.strict()` (no extra fields), with a `.refine()` that the **sum of beat durations == total**.
- `storyBeat`: `beatNumber · title · visualDescription · audioDescription · estimatedDurationSeconds(≤15) · activeCharacters[1–4]`.
- Handoff mechanics: tool registered → model emits structured tool-call **only after Phase-4 approval** → backend commits payload in a **DB transaction** + sets session `LOCKED` → client intercepts (`onToolCall`), blocks input, animates, routes to the Screenplay panel.

## 4. Context isolation (keep config out of the chat, in the model's head)

Pipeline params (cast, stereotypes, duration, teaching intent) must be **invisible in the chat bubbles** but **present at every inference turn**:
- **Server-side system-prompt reconstruction** — client sends only the clean visual message history; the backend reads session state and **injects the constraints into the system prompt on every call**.
- **Runtime context** — pass session/permissions/params through the generation + tool loop without putting them in the visible array.
- Security: `allowSystemInMessages:false` (stop user text masquerading as system); keep secrets in runtime context, not prompts; avoid Zod `.transform()` (won't map to JSON Schema).

## 5. Production hardening
- **Transaction-safe handoff** — persist the story payload + lock the session in ONE transaction; roll back together (no "UI locked but backend didn't commit").
- **Prompt-injection mitigation** — system-in-messages off; runtime-context isolation.
- **Observability** — OpenTelemetry → Langfuse/Sentry for step latency, token cost, tool-failure; scrub PII/proprietary story details before export.

## 6. Sources (key)
Vercel AI SDK (streamText, useChat, tool-use, system prompts, runtime/tool context, message persistence); LangGraph interrupts/human-in-the-loop; OpenAI Assistants→Responses migration (Aug 2026 shutdown); Socratic-method prompting (ResearchGate 369020456); Zod↔JSON Schema; agent-framework comparisons (2026); Langfuse/Sentry OTel for the AI SDK.

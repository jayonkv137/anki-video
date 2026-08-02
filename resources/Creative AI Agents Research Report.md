# Building a Multi-Agent Creative Studio

**Overview:** In code, an LLM *agent* is really just a loop that assembles a prompt (with a system instruction and context), calls the model, and optionally invokes tools on its behalf.  For example, a simple agent loop might be: “user sends a message; agent adds it to the conversation context; agent sends system prompt + context to the LLM; the model decides on the next action (possibly calling a tool); if a tool call is needed, the agent runs that function and feeds the result back; the loop continues until the model yields a final answer”.  In practice an agent can be implemented as a Python class or function that holds: a system prompt (instructions/persona), code to build the context (conversation history and any retrieved or summarized info), an LLM API call, and a handler for structured tool calls.  Beyond this minimal loop, teams often *over-engineer* by adding heavy orchestration, elaborate logging systems, or complex event buses. For a small solo project, you can often skip those and stick to the essentials: a simple while-loop that calls the LLM with the assembled prompt, checks for any “tool call” outputs, runs those tools, and continues. 

```python
# Pseudo-code for a minimal agent loop
context = []                # conversation history (list of strings or message objects)
system_prompt = agent.prompt # the fixed system instruction for this agent

while not done:
    # Build the prompt: system message + full conversation
    messages = [{"role": "system", "content": system_prompt}]
    for msg in context:
        messages.append(msg)
    # Call the model
    response = llm.chat_completion(messages)
    # If the model requested a tool call, run it
    if response.get("tool_call"):
        tool_name = response.tool_call.name
        args = response.tool_call.arguments
        result = run_tool(tool_name, args)
        # Append tool result as a message for further reasoning
        context.append({"role": "tool", "content": result})
        continue
    # Otherwise this is a final assistant message
    answer = response.content
    context.append({"role": "assistant", "content": answer})
    # Check stopping condition (task done, user approval, etc.)
    if is_finished(answer):
        break
```

*Minimal moving parts:* Just a system prompt, a context builder, optional tools, and the LLM loop.  In code this can be a few dozen lines. People often add unnecessary bells and whistles (complex message routing, custom memory caches, etc.) early on. A solid minimal agent simply uses the conversation history and user instructions as context for each model call, and any needed external functionality is exposed as a simple function (tool) called by name. 

## System Prompt Design (Defining the Agent’s Role)

The system prompt *is* the agent’s “job description.”  For production quality, it should be clear, structured, and prescriptive.  Follow best practices like the **Field Guide to AI’s** six-layer template.  For example:

- **Identity/Role:** Start with a specific persona. E.g. _“You are Ava, the creative director for [Show Name], specializing in short animated episodes.”_  A narrow, well-defined role anchors the model’s decisions.
- **Primary Objective:** Explicitly state the goal. E.g. _“Your goal is to help brainstorm and script a single episode according to the show bible.”_  This guides conflicting rules.
- **Instruction Hierarchy:** If you have multiple rules, list a priority order. E.g. _“1) Follow the tone guidelines of the show bible. 2) Always align with the educational standard.”_  Without this, the model will guess which rule is most important.
- **Behavioral Rules:** Use clear bullet points. E.g. “_Rules:_ – Only output creative ideas if they fit the story method. – Do not suggest anything outside the permitted theme. – Always ask before making changes to the creator’s ideas.”  Group related rules with tags or headers.
- **Output Format:** Constrain style and structure. E.g. “_Output Format:_  
  - For story ideas, use a numbered list of brief phrases.  
  - For script drafts, write concise dialogue with character names.  
  - Limit responses to 200 words.”  Including a concrete example response is extremely helpful.
- **Edge Cases/Guardrails:** Preempt off-script scenarios. E.g. “_If asked about something outside your scope, say: “I specialize in X. For Y please see [resource].”_  “_If unsure, respond: “Let me check that.”_”  These “defensive patterns” catch user attempts to derail the agent. 

Each part of the system prompt is separated by tags or headers so the model can parse them easily.  For instance:

```
<role>
You are Ava, a creative director and content writer for the “Space Explorers” cartoon series.
</role>
<objective>
Your goal is to help outline and script a short educational episode about space science.
</objective>
<rules>
- Always follow the Show Bible’s character profiles and world rules.
- Never violate the educational standard: focus on age-appropriate facts.
- If a request conflicts with these, ask for clarification or say it’s not allowed.
</rules>
<format>
- Episode outline: numbered bullet list.
- Script: dialogue lines with character names in **bold**.
- Keep each character’s voice distinct and concise.
</format>
<edge cases>
- If something is out-of-scope, answer: “I specialize in [domain], sorry.”  
- If you don’t know, say: “I’m not sure; let’s find out together.”
</edge cases>
```

Each section should be succinct (a few sentences or bullets). Research shows that specifying *what not to do first* (constraint-first design) yields more consistent behavior. For example: “**Do not** hallucinate facts; if unsure, say so.”  We also found that simply adding a generic persona (“You are X”) does *not* automatically improve performance on factual tasks – its benefit is mostly situational. More important are the concrete rules, objective, and format. 

Finally, counter common LLM tendencies: explicitly forbid sycophancy and verbosity if needed. For instance, you might add “Do not simply agree or flatter; give honest feedback.” or “Be concise and precise; avoid unnecessary flattery.”  At least one study noted that adding a persona like “helpful assistant” has negligible effect on accuracy, so focus on actionable instructions instead of vague niceties. In short, treat the system prompt like code: make it **clear, structured, and testable**, then *version-control* and refine it.

## Multi-Agent Conversation Flow

We want all agents (writer, artist, editor, etc.) to share one continuous chat history, with the human creator guiding them. Concretely, this means managing a single conversation thread but swapping out *which agent is “speaking”*. One practical pattern is:

- **Shared history:** Maintain a global `history` list of messages (content and speaker label). Every time an agent replies, append its response to `history`.
- **System prompt per agent:** When invoking an agent, send its own system prompt as the current turn’s instructions. Include the full `history` (except internal system prompts) as prior messages so the new agent sees everything said so far.
- **Speaker labeling:** To avoid confusion, have each assistant message include the agent’s name or role. For example, store messages as `{"role": "assistant", "content": "<WriterAgent>: (what it said)"}`. When Agent A passes to Agent B, Agent B will see Agent A’s contributions as part of the conversation.
- **Deciding who speaks:** An external controller (your code) determines which agent goes next, usually by phase. For example, after brainstorming, you might switch from the “Idea Agent” to the “Writer Agent.” Each switch is handled in code by changing the system prompt.
- **Handoff marker (optional):** Some systems insert a “transfer” message to mark the change. For instance: `{"role": "assistant", "content": "=== NOW HAND OFF TO IMAGE AGENT ==="}`. This clarifies transitions, but it’s optional if you manage turns in code.

Crucially, you *explicitly decide* what context each agent sees. LangChain’s docs warn that if you use sub-agents, you must manually pass relevant messages between them. In our case we can simply forward the full chat. In pseudo-code:

```python
history = []  # list of {"role": "assistant" or "user", "content": ...}
phase = "brainstorm"

while not done:
    if phase == "brainstorm":
        system_prompt = writer_agent.prompt
    elif phase == "sketch":
        system_prompt = artist_agent.prompt
    # ... etc for each phase
    
    # Build conversation (user messages can be inserted here if needed)
    messages = [{"role": "system", "content": system_prompt}] + history
    
    # Call the chosen agent
    response = llm.chat_completion(messages)
    history.append({"role": "assistant", "content": f"{response.content}"})
    
    # Optionally: trigger phase change based on content
    phase = next_phase(history)
```

Each agent sees all prior outputs as context, but treats them under its own role instructions. This maintains coherence (they all know what’s been decided) but avoids *role bleed* because the new agent only sees the old messages as generic content, not as a previous system prompt. If the history grows long, you may selectively summarize older parts (see next section) so that each agent still gets a concise context. Overall, handle handoffs in code by swapping the system prompt and continuing the conversation thread.

## Context Assembly and Memory

As the conversation grows, you can’t blindly shove the entire transcript into every call. Instead use a layered memory strategy. For each API call, gather context by:

- **Recent history (sliding window):** Always include the last few exchanges explicitly so the agent has immediate continuity.
- **Summaries for older content:** Periodically collapse earlier dialogue or outputs into a short summary. For example, after the writer finishes an outline, you could summarize it into a single paragraph and store that. The agent’s prompt can then include the summary instead of the full original text. Anthropic and Oracle blogs recommend exactly this: “Keep the latest turns available as recent context. Summarize older dialogue so the model does not need the full transcript every time”. 
- **Retrieval memory (if needed):** If a user later references something said far back, you can retrieve it by search. A vector index or a simple keyword lookup can help recall facts from past conversation without including them every turn.
- **Structured memory:** You can separately store key artifacts (like the final script draft, character definitions from the show bible, etc.) and only reference them by name in context.  

For example, code-wise you might do:
```python
context_messages = []
recent = history[-5:]  # keep last 5 messages
context_messages.extend(recent)

if len(history) > 20:
    summary = summarize(history[:-5])  # call LLM to summarize older parts
    context_messages.insert(0, {"role": "assistant", "content": summary})
```
This hybrid approach “keeps the latest turns in memory” and compresses earlier turns.  The summary itself can be maintained and updated as part of the agent state. (If you find tools for auto-summarization, they fit here.)

The key is to *design a memory manager*: decide which messages to inline, which to compress, and what to fetch. For a short project (one episode), you may never exceed the token limit. But if it grows, summarization is your friend. In all cases, avoid passing irrelevant or duplicate text; tailor the context to what the agent needs now. 

## Tools vs Structured Output

Agents often need to perform specific actions (like generating an image prompt or editing a file). You have two approaches: have the agent *call a tool* (via function calling) or have it *output structured data* (JSON/Markdown) that your code interprets. The guideline is:

- **Use tools for actions or multi-step workflows.** If the agent needs to fetch data, call an API, generate an image, or perform any side-effect, define that as a tool. For example, you might register a `generate_image(prompt, style)` function. In the system prompt describe each tool and its schema. When the model outputs a tool call request (function name + args), your code executes it and returns results. This is essential if the task cannot be done by the LLM alone (e.g. “Find stock photo of this character”).
- **Use structured outputs for deterministic transformations.** If you simply want the agent to produce data in a known format (like a JSON outline, or a list of captions), you can have it output JSON or a fixed template. This uses a single LLM call and avoids the overhead of a function round-trip. For example, for a **single-step extraction or formatting task** (parse the meeting notes into a JSON object), structured output is ideal. It also simplifies validation: many APIs (OpenAI’s `response_format`, Anthropic’s `tool_use`) will enforce the schema for you.
- **Batch vs interactive:** If you’re processing many independent items (e.g. batch-generating 100 image prompts from a list of scenes), structured-output calls are more efficient (one model call per item). But if the workflow is interactive and depends on prior steps, tool-calling fits better.

**Principles for tools:**  
• *Single responsibility:* Each tool should do one thing clearly. Give it a precise name and description so the agent knows when to use it.  
• *Well-defined schema:* Provide strict JSON schemas (or Pydantic models) for tool inputs and outputs. This lets the LLM generate exact calls, and your code can safely parse them. Modern LLM APIs retry or error on malformed JSON.  
• *Failure modes:* If you give an agent *too many* tools, it can get confused or default to always picking one. Also, if a needed action could have been handled by the model directly, a tool call adds unnecessary latency and cost (every tool call is another API round-trip). Conversely, if you rely only on structured outputs for a multi-step task, the model may hallucinate intermediate steps. In short, **tools for dynamic actions/multi-step work, structured output for static formatting or extraction**.

In code, tools are just Python functions. For example, to avoid allowing the agent to invent facts, you might disable any “external knowledge” tool unless needed. Always keep your tool descriptions in the prompt so the model cannot surprise you by calling an unknown function. If a tool is called incorrectly, handle that gracefully (return an error message to the agent so it can try something else).

## Clarifying Questions vs Guessing

Agents often face ambiguity. A good agent should *ask* a question if needed, not just guess an answer. You can encourage this by including **interaction rules** in the prompt: e.g. `“If any essential information is missing, ask exactly one clarifying question before proceeding.”` The PromptQuorum guide suggests listing rules like “Ask clarifying questions” or “Admit uncertainty” in your system prompt. For instance:

> **Instruction:** If a user request is ambiguous, the agent should ask one specific follow-up question and stop. Do not try to answer without clarification.

In practice, you might have the agent output something like `{"clarification": "What style should the scene be drawn in?"}` and treat that as a question to the human user. Or simply the agent can output a normal question sentence. The key is that you **pause the loop** to get the user’s input before continuing. 

Be careful not to let this loop stall the project. Limit to one question at a time: after the user answers, proceed with the final answer. (You can re-enter the clarification step if the answer is still incomplete.) If an agent is asking *too many* questions, tighten the prompt (e.g. “If you have already asked, proceed with your best answer” or adjust temperature). Some systems even provide a “tool” called `ask_user(question)` to standardize this. 

**Fail-safes:** Have a maximum number of clarification rounds. If after asking once the agent is still uncertain, it should state uncertainty and move on. Conversely, don’t let an agent guess a missing fact that’s crucial to correctness. Balancing this often requires iteration. At minimum, explicitly instruct the agent to ask before guessing, as a rule. 

## Propose–Confirm–Apply Pattern

When the agent needs to **make changes to some artifact** (a document, a script, project files, etc.), adopt a “maker–checker” workflow: **Plan → Preview → Approve → Execute**. In practice:

1. **Plan:** The agent generates a *proposal* describing what it will change. For example, it might output a JSON list of edits or a bullet list of modifications.
2. **Preview:** Your code translates this proposal into an actual *diff* or *effect summary*. This could be a unified diff of a text file, or a textual summary like “This will add 150 words to scene 2 and remove 20 words from scene 3.” Show this to the user.
3. **Confirm:** Ask the user to approve or reject. For instance: “Agent proposes the above changes. Reply **YES** to apply them, or **NO** to cancel.” 
4. **Apply:** If approved, your programmatically apply the changes deterministically (e.g. patch the file, update the database). The agent itself does **not** directly edit the file – the code does so based on its plan. This avoids nondeterminism and makes changes auditable.

You should **explain the consequences** clearly. For example, the KLA governance guide suggests giving the reviewer (user) a concise narrative of the action, including targets and expected effect. In our context, that means summarizing the “blast radius” of the edit. A concrete implementation could be:

```python
# Pseudo-code for propose/confirm/apply
proposal = agent.generate_plan(current_script)  # e.g. JSON with edits
diff = compute_diff(current_script, proposal)   # your code computes actual changes
print("Proposed Changes:\n", diff)
user_input = input("Apply these changes? (yes/no) ")
if user_input.lower().startswith("y"):
    current_script = apply_patch(current_script, proposal)
    print("Changes applied.")
else:
    print("Operation cancelled.")
```

By structuring it this way, the user always sees exactly what will happen *before* it happens. This pattern prevents inadvertent errors: the agent only *proposed*, and your code then *deterministically executes* the approved plan. In production, you might log each proposal and its approval (as KLA suggests, with an “evidence schema” of decisions), but for a small studio you can keep it simple. 

## Good Agent vs Bad Agent (User Retention)

In creative assistance, the difference between a helpful agent and one that’s “thrown away” is concrete behavior. A **good agent** consistently adds value: it adheres to the style guide, suggests novel ideas, and follows instructions precisely. It is concise when needed, provides useful alternatives, and corrects itself when it errs. In other words, it behaves *like a junior collaborator* rather than a subservient yes-man. By contrast, a **bad agent** often gets off-topic, repeats itself, or displays behavior that frustrates the user. Examples of bad behaviors: 

- **Over-verbosity** (“Let me elaborate” paragraphs of filler).  
- **Sycophancy** (“Yes boss, that’s a great idea!”) without real input.  
- **Robotic refusal/hedging** (“As I stated before, I cannot do that”).  
- **Ignoring instructions or style rules.**  
- **Asking endless questions** or **dithering** instead of delivering.  

A user will quickly abandon an agent that feels like a generic chatbot rather than a creative partner. As the Field Guide notes, “A well-designed system prompt is the difference between an AI product that users trust and one they abandon after three interactions”. In practice, **specific behaviors** matter: helpful agents follow the format rules and deadlines, bad agents either violate them or become repetitive. For example, if the system says “bullet list of ideas”, a good agent will output bullets; a bad agent might ramble in paragraphs. Watch for users getting annoyed at repetition or irrelevant chatter – those are signs to tighten the prompt or give more examples. 

In summary, focus on *helpful, consistent, on-brand* behavior. Reinforce it in the system prompt (e.g. “Always follow these rules closely”) and monitor for common pitfalls like fluff or conflict. Good agents yield trust and continued use; bad ones break it quickly.

## Testing and Tuning Workflow

Because creative output is subjective, you can’t write simple unit tests. Instead, build an **evaluation suite** and use continuous feedback. Industry teams combine these approaches: 

- **Golden examples:** Collect a set of representative prompts and *expected outputs* (or at least desired properties). For instance, a few example episodes or scripts that meet all criteria. These form your regression suite.  
- **Automated scoring:** Use an LLM or programmatic “judge” to compare agent output against criteria. For example, check if required sections are present, or measure content length. Anthropic notes that real-world agents use multi-criteria grading (factuality, style, etc.) and often start with *static checks* before moving to LLM judges. You might implement simple checks (e.g. “Did the script include the main character’s name?”) or leverage OpenAI Evals and scoring tools. Be aware that LLM-judges can be inconsistent, so calibrate them with some human-reviewed examples. 
- **A/B testing:** Whenever you tweak a prompt or change a model, run A/B comparisons on your test inputs. For instance, run the old and new prompts side-by-side and compare scores or have a human rate which output is better. Braintrust’s guide emphasizes that prompt changes have unpredictable effects: an example you add might help one case but break another. A/B testing catches regressions early. (Tools like the Braintrust Playground or custom scripts can do this; see Braintrust’s tips.)
- **Iteration loop:** Change one prompt fragment at a time. After each change, re-run your eval suite to see if overall metrics improve. Track both quantitative scores (via your graders or LLM judges) and qualitative checks (sampling outputs). This is how teams “verify improvements with real quality scores before deployment”. If something got worse, revert or adjust the prompt. 
- **Monitoring drift:** Even after deployment, watch for “drift” in outputs. If you update the base model or the show rules change, outputs may slip. Keep the eval suite running periodically (e.g. on CI). The Chanl blog notes that frameworks may handle monitoring, but as a solo dev you should at least eyeball critical examples after any change.

In short, you’re looking for *relative improvement*, not absolute perfection. Use your “golden” episodes to catch regressions and guide tuning. And remember: an LLM judge is only as good as its instructions and examples – always double-check major changes manually. The goal is a **stable tune-and-measure** loop, not one-off tinkering.  

## Maintenance Over Time

Treat your prompts and code as living artifacts. **Version-control** everything (prompts, system messages, agent code) and tag releases. As the story bible or teaching standards evolve, update the relevant sections of the system prompt and then re-run your tests. The Field Guide explicitly says to treat prompts like code — “version them, test them, and iterate based on real-world behavior”. Over time, prompts may become stale: for example, if a character’s role in the show bible changes, the agent’s persona prompt must be updated. 

Watch for the first things to “rot”: typically, hard-coded rules or cultural references. Style guidelines might shift, new episodes may introduce exceptions, or the model’s knowledge cutoff may become an issue. Also monitor the underlying LLM’s updates. A model upgrade can subtly change tone or verbosity, so retest your prompts afterwards. If outputs start to drift, you may need to tweak the prompt (often just adding or removing one instruction can fix it). Logging key outputs or using a simple metrics monitor (even counting lengths or key terms) can give an early warning that something’s gone off the rails. 

In practice, we recommend at least a yearly or per-major-version review of all agent prompts and rules. Keep the “source of truth” documents (show bible, pipeline contract, etc.) under revision control too, so you know when requirements changed. Because a small team can’t manage huge frameworks, simplicity here pays off: clear, auditable prompts and a small set of structured tests will last longer than a complex hidden memory system.

## Failure Modes & Fixes

| Failure Mode                  | Symptoms                                 | Fixes/Workarounds                                                  |
|-------------------------------|------------------------------------------|--------------------------------------------------------------------|
| **Incoherent team voice:** Agents write as strangers (varying tone). | Script feels inconsistent; style slips between turns. | Reinforce persona in each agent’s system prompt; include example of desired style; possibly share a short “thread summary” in context so new agent recalls tone. |
| **Role bleed:** New agent uses previous agent’s instructions. | Agent incorrectly adopts another’s perspective or rules. | When switching agents, ensure you supply *only the conversation content* (no old system message). Explicitly label turns (e.g. prefix with agent name). |
| **Too much context:** Prompt exceeds token limit, or model runs out of memory. | Errors or cut-off responses, loss of earlier details. | Summarize older parts of the dialogue as needed. Use retrieval or a memory tool (e.g. vector DB) for long-term facts. |
| **Agent is too verbose:** Unnecessary filler or repeats. | Wandering answers; low engagement. | Add brevity constraints in the prompt (“be concise, limit to N lines”); adjust temperature or top-p for sharper focus; use an output format checklist. |
| **Agent refuses creatively:** Overly safe or literal answers. | Agent constantly says “I can’t”, or only agrees without adding ideas. | Loosen constraints in the prompt; remove overly-strict refusals. Encourage creativity (“feel free to suggest alternatives”). Possibly raise temperature. |
| **Agent hallucinations:** Inventing facts or images. | Factually incorrect statements; inconsistent story facts. | Add explicit “do not hallucinate” rule; supply necessary facts explicitly in context; use verification tools (e.g. knowledge API). |
| **Agent doesn’t ask when needed:** Answers even when missing info. | Implausible assumptions or outputs. | Instruct agent to ask clarifying questions if unsure. Lower temperature to make it cautious, or add a penalty for confident incorrect outputs. |
| **Agent asks too much:** “Stalling”. | Conversations get bogged down in endless Q&A. | Limit to one clarification per ambiguous point. Add in-system rule: “After one question, if still unclear, give the best answer you can.” or set a max turn count. |
| **Broken output format:** JSON or structure is invalid. | Parser errors or misinterpreted output. | Use API-enforced response_format (e.g. OpenAI’s Pydantic parsing). Provide clear schema and example, so the model’s JSON is valid. |
| **Proposal miscommunication:** User doesn’t understand planned changes. | User hesitates to approve; confusion about diff. | Present changes as a diff or annotated list. Use clear language (e.g. “add”, “remove”). Limit each proposal to one atomic change when possible. |
| **Prompt regressions:** A tweak broke something. | Previously good behaviors degraded suddenly. | Re-run your regression suite (A/B test). Compare outputs side-by-side to spot what changed. Revert or refine the last change. |
| **Drift over time:** Agent gradually deviates from style or rules. | Subtle style changes across episodes; rule violations slowly creep in. | Schedule periodic reviews. Use monitoring (e.g. track certain keywords or compliance rates). If drift is detected, adjust prompt or retrain memory (if any). |

Each of these is a common trap. For example, **context bloating** is best addressed by summarization. **Format issues** are often solved by stricter prompt contracts or using the API’s schema validation. The table above enumerates several failure modes seen in production, with practical fixes.

## Frameworks: Yay or Nay?

You asked whether to use a framework like LangGraph, CrewAI, Vercel AI SDK, Letta/MemGPT, etc. Here’s a candid assessment:

- **LangGraph:** Powerful but heavy. It gives fine-grained control (explicit state machines, checkpoints, observability), but has a steep learning curve. For one developer and four agents, it may be overkill. Use it if your workflow is very complex or long-running. Otherwise a simple loop in raw Python might suffice.
- **CrewAI:** Designed for multi-agent teams (it calls them “crews”). Very user-friendly (role-based, built-in memory, LangChain-compatible tools). It can rapidly prototype a specialized crew. However, it adds another dependency and its own style of abstractions. It might be useful if you want out-of-the-box collaboration features, but it’s not strictly necessary for a small project.
- **Vercel AI SDK:** This is mainly a **TypeScript/Next.js** framework for web apps. It has nice agent abstractions for UI streaming, but if you’re coding in Python or not using a web frontend, it isn’t relevant. Even as a concept, it’s not needed if you’re running a backend script.
- **Letta (MemGPT):** Letta provides advanced memory (tiered memory, agentic recollection). But it’s effectively its own “agent OS” – adopting Letta means running your agents *inside* its platform. For a short video episode, you probably don’t need persistent memory beyond the single session. A lighter memory approach (even none, or Mem0 vector store) is likely enough. Letta would be overkill here.
- **Raw provider SDKs (OpenAI/Anthropic API):** Often the simplest choice. You have full control, minimal magic, and no extra abstraction layers. For a solo dev, this is appealing. You can build exactly what you need (system prompt loops, context assembly) without wrestling with a framework’s patterns. The downside is writing more boilerplate for state and retries, but it keeps things transparent.
- **OpenAI Agents SDK / Claude SDK:** These newer SDKs provide a thin layer over the basic API, adding support for tools and memory. They are fairly lightweight. For example, the OpenAI Agents SDK gives primitives for agents, handoffs, and guardrails, but remains quite “unopinionated”. If you want some help with structure but without committing to a heavy framework, these can be a middle ground.
- **Pydantic AI, AutoGen, etc.:** Niche. Pydantic AI enforces type-checking (useful but requires writing schemas). AutoGen (now part of Microsoft) is for multi-agent debates and research; not needed for a straightforward pipeline.

In summary, for **one creator + four specialized agents**, a full agent framework is optional. Use CrewAI or the new OpenAI/Claude Agents SDK if you want shortcuts for multi-agent wiring. Otherwise, plain Python + LLM calls + a few custom tools is perfectly viable. The community consensus is: *“LangGraph remains the default for very complex workflows”* but *“CrewAI is the most approachable way to build role-based multi-agent teams”*. Since your workflow is fairly linear (idea → script → visuals → edit), you might not need the complexity of LangGraph. A minimal stack (Python + OpenAI SDK + a simple database or files for memory) will be easy to maintain for years. You can always integrate a heavier framework later if a need arises.

**Recommendation:** Start raw or with very light tooling. Keep your code modular (e.g. each agent as a Python class). If you find yourself repeating orchestration code, then evaluate a framework. But don’t let framework overhead slow you down at first. For example, you could use LangGraph’s graph if you wanted visual orchestration, but you can achieve the same with a handful of `if`/`else` and function calls in a script. CrewAI could speed up startup, but our research shows it mainly provides a nice developer UI and team metaphor rather than new capabilities. In short: **don’t use a heavy framework unless you’re sure you need its features**.

## Extra Tips

- **Logging:** Have each agent log its reasoning and tool calls (either to console or a file). This makes debugging easier.   
- **Use temperature judiciously:** A lower temperature (0.2–0.4) often yields more consistent planning; you can bump it when creativity is desired (e.g. in brainstorming).  
- **Error handling:** If the model ever fails (timeout, invalid JSON), retry or have a fallback. Never assume every API call will succeed.  
- **Persona naming:** Sometimes it helps to explicitly *mention* the agent’s name at each turn, e.g. “Ava (Writer): …” in the output, so the conversation reads as a coherent team.  
- **Human in the loop:** Remember that “the human decides everything creative.” The agents should present options, not finalize anything important. Make sure your prompts remind them to defer to the human if they’re unsure.  

Building this “creative studio” is an iterative process. Start small, test each component, and grow complexity only as needed. The sources above show that systematic prompt design and evaluation practices (prompt structure, A/B testing, regression suites) separate a working agent from an abandoned one. By following these patterns, you’ll end up with a robust pipeline of specialized agents that genuinely assist (but never override) the human creator.  

**Sources:** Engineering blogs and guides were used extensively: Anthropic’s context engineering and evaluation articles, the Field Guide to AI on prompt design, and various framework comparisons. These provided concrete code patterns and best practices which have been distilled into the advice above. Where controversies exist (e.g. persona effects), we’ve noted the uncertainty. Every recommendation here is optimized for a **solo developer in production**, prioritizing simplicity and long-term maintainability.
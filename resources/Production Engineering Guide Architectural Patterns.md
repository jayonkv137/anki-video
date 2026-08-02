# Production Engineering Guide: Architectural Patterns for Specialised Creative Agent Crews

# The Code-Level Anatomy of an Agent

To construct a resilient multi-agent system, a developer must strip away the marketing narratives surrounding autonomous artificial intelligence. At the execution level, an agent is not an independent entity possessing volition; it is a deterministic, stateful software harness wrapped around a stateless Large Language Model (LLM) inference call. The entire architecture can be decomposed into five concrete components: a system prompt defining the operational boundaries, a context assembly pipeline that prepares the input payload, a defined set of execution interfaces or tools, a localized deterministic execution loop, and a database layer to persist conversation history and state variables.

                    \+---------------------------------------+  
                     |        Deterministic App Host         |  
                     \+---------------------------------------+  
                                         |  
                                         v  
                         \+-------------------------------Base  
                         |   Context Assembly Pipeline   |  
                         \+-------------------------------Base  
                                         |  
                       \+-----------------+-----------------+  
                       |                                   |  
                       v                                   v  
             \+--------------------+              \+--------------------+  
             |   System Prompts   |              |  Unified History   |  
             |  & Core Rule Docs  |              |   & Phase State    |  
             \+--------------------+              \+--------------------+  
                                         |  
                                         v  
                         \+-------------------------------Base  
                         |      Stateless LLM Call       |  
                         \+-------------------------------Base  
                                         |  
                                         v  
                         \+-------------------------------Base  
                         |   Local Deterministic Loop    |  
                         \+-------------------------------Base  
                                         |  
                       \+-----------------+-----------------+  
                       |                                   |  
                       v                                   v  
             \+--------------------+              \+--------------------+  
             |  Tool Execution &  |              |   Terminal State   |  
             |   Parameter Check  |              |      Reached       |  
             \+--------------------+

The system behaves as a structured cognitive loop. The model provides the reasoning over the assembled context, whereas the surrounding application code controls the environment, enforces permissions, and executes deterministic actions.

## The Core Runtime Execution Loop

The following production-grade implementation demonstrates an agent runtime constructed strictly on top of raw provider SDKs, avoiding third-party framework layers. This implementation manages state transitions, tool invocation, and token boundaries:

```py
import json
import logging
import sys
from typing import Any, Callable, Dict, List, Optional
from pydantic import BaseModel, Field

logging.basicConfig(level=logging.INFO, stream=sys.stdout)
logger = logging.getLogger("AgentRuntime")

class ToolContract(BaseModel):
    name: str
    description: str
    parameters: Dict[str, Any]

class AgentRuntime:
    def __init__(self, client, model_name, system_prompt, tools=None, tool_registry=None, max_turns=8):
        self.client = client
        self.model_name = model_name
        self.system_prompt = system_prompt
        self.tools = tools or []
        self.tool_registry = tool_registry or {}
        self.max_turns = max_turns

    def _compile_tool_schemas(self):
        return [{"type": "function", "function": {"name": t.name, "description": t.description, "parameters": t.parameters}} for t in self.tools]

    def execute(self, history):
        payload = [{"role": "system", "content": self.system_prompt}] + history
        current_turn = 0
        while current_turn < self.max_turns:
            response = self.client.chat.completions.create(model=self.model_name, messages=payload, tools=self._compile_tool_schemas())
            res_msg = response.choices[0].message
            payload.append(res_msg)
            if not res_msg.tool_calls: return payload[1:]
            for tc in res_msg.tool_calls:
                # ... tool execution logic ...
                pass
            current_turn += 1
```

## Unnecessary Architectural Additions

Industry implementations frequently fail by introducing unnecessary layers of abstraction that complicate long-term maintenance. Key areas of over-engineering include:

* **Complex State Graph Libraries for Sequential Pipelines**: Utilizing heavy DAG orchestration packages to manage linear step-by-step tasks that are more reliably handled by native code control structures \[cite: 6, 7\].  
* **Vector Databases for Short-Term Message History**: Implementing semantic retrieval mechanisms to fetch recent dialogue turns, which disrupts chronological tracking and introduces retrieval noise \[cite: 8\].  
* **Distributed State Synchronization Abstractions**: Designing state coordination systems to update prompts globally at runtime, when static versioned code files represent a cleaner, immutable source of truth \[cite: 9, 10\].

---

# System Prompt Engineering for Creative Collaborators

## Engineering Behavioral Drivers and Mitigating Sycophancy

To transform an agent from an overly agreeable, conversational assistant into an authentic creative collaborator, system prompts must rely on rigid behavioral constraints rather than expressive adjectives \[cite: 11, 12\].  
The primary failure mode of creative agents is sycophancy—the tendency to validate every human premise, regardless of quality \[cite: 11, 13\]. Research shows that when users express high epistemic certainty or frame statements in the first person, LLM sycophancy rates spike significantly \[cite: 13\]. To mitigate this, system prompts must implement explicit behavioral rules \[cite: 11, 12\]:

| Behavioral Malady | Prompt Mechanism | Technical Implementation |
| ----- | ----- | ----- |
| **Sycophancy & Affirmation Loops** | **Mandatory Critique** | Force the agent to construct a strong critique of the human's direction before offering suggestions. |
| **Input Framing Contamination** | **1-Step Question Reframing** | Instruct the agent to internally convert user statements into neutral questions before parsing, reducing framing bias by up to 24%. |
| **Verbosity & Filler Dialogue** | **Negative Constraints** | Prohibit pleasantries (e.g., "I'm excited to help with...") and mandate direct, declarative syntax. |
| **Creative Vagueness** | **Structured Contrast Output** | Force the agent to present choices in binary, distinct variants rather than ambiguous continuums. |

## Complete Production System Prompt Template

The following system-prompt template demonstrates the structural elements required to enforce a highly focused, professional creative collaborator persona, designed to read and respect the project's core rule documents:  
**ROLE AND SPECIFIC GOAL DEFINITION**  
The agent acts as the Lead Visual Director for the episode production. The single objective of this agent is to construct visual treatments and scene-by-scene asset instructions based on the provided screenplay. The agent is strictly prohibited from writing script dialogue or altering narrative pacing.  
**SOURCE MATERIAL RULE DOCUMENTS**  
The agent must validate every proposed asset against the following master documents:

1. SHOW BIBLE: Defines the narrative universe limits, canonical character descriptions, and thematic boundaries.  
2. STORY METHOD: Mandates the exact scene-by-scene structural arc and narrative progression mechanics.  
3. TEACHING STANDARD: Sets the core educational criteria and information delivery guidelines.  
4. VISUAL TREATMENT: Sets the artistic direction, color palette limits, lighting models, and camera framing restrictions.  
5. PIPELINE CONTRACT: Establishes the folder directories, strict file naming rules, and image/video prompt schemas.

**ANTI-SYCOPHANCY & COLLABORATION SAFEGUARDS**

1. STATEMENT DEBIASING: Upon receiving any creative direction or evaluation from the human collaborator, the agent must internally rephrase the input as a neutral question before processing. Do not assume the human's aesthetic premise is correct \[cite: 13\].  
2. CRITICAL STEEL-MANNING: Before proposing any alternative visual direction, the agent must write exactly one sentence articulating the strongest visual justification for the human's original proposal \[cite: 12\].  
3. DIRECT REFUSAL PROTOCOL: If the human proposes an aesthetic choice that violates the Visual Treatment or the Show Bible, the agent must reject the direction. The rejection must cite the specific section of the violated document and state the resulting visual conflict \[cite: 11, 12\].  
4. APOLOGY PROHIBITION: If corrected, do not apologize. Acknowledge the parameter update and present the adjusted visual proposal immediately \[cite: 12\].  
5. BANNED PHRASES: Do not use the following conversational filler phrases:  
   * "That is a great idea\!"  
   * "I would be happy to help you with that."  
   * "You are absolutely right."  
   * "As an AI, I do not have personal tastes, but..." \[cite: 12\]

**OUTPUT SCHEMA CONTRACT**  
Every response must strictly follow this visual markdown layout. Do not add conversational text outside of these blocks:  
**CRITIQUE AND DEBIASING**  
\[Provide a direct critique of the current direction. Identify visual conflicts, cliches, or narrative inconsistencies. Limit to exactly 2 paragraphs.\]  
**VISUAL PROPOSAL**

* **Shot ID**: \[e.g., EP1\_S04\]  
* **Framing**: \[Strict composition classification\]  
* **Visual Description**: \[Dense sensory details, lighting vectors, and focal length\]  
* **Render Engine Prompt**: \[Synthesized, raw prompt containing stylistic keywords from the Visual Treatment\]

**CLARIFYING QUESTION**  
\[If information is missing, ask exactly one targeted question. If context is sufficient, output: "CONTEXT COMPLIANT \- READY FOR PIPELINE CONTROLLERS."\]  
---

# Unified Message History and Dynamic Agent Orchestration

## The Multi-Agent Unified Thread Architecture

For a team of specialized agents working on a single episode, the user must experience a single, unbroken stream of conversation \[cite: 14, 15\]. However, simply passing a massive, growing chat transcript to every agent is a critical failure path \[cite: 8\]. It causes:

* **Role Bleed**: Agents read previous turns generated by other agents and adopt their system instructions, voice, or tool parameters \[cite: 8\].  
* **Token Bloat**: The context window expands exponentially, driving up inference latency and API costs \[cite: 8\].  
* **Lost-in-the-Middle Effects**: The model's attention is diluted across hundreds of historical turns, causing it to ignore the show bible or the immediate human instruction \[cite: 8\].

The design pattern to resolve this is a **Single Thread with Dynamic Role-Based View Generation** \[cite: 2, 8\].

┌────────────────────────────────────────────────────────────────────────┐  
│                        UNIFIED SYSTEM THREAD                           │  
│ (PostgreSQL: Message Table with Role, Content, AgentID, Phase columns) │  
└───────────────────────────────────┬────────────────────────────────────┘  
                                    │  
               ┌────────────────────┼────────────────────┐  
               ▼                    ▼                    ▼  
     \[Phase: DECISION\]       \[Phase: WRITING\]     \[Phase: VISUALS\]  
     Retrieve:               Retrieve:            Retrieve:  
     \- Global Rule Docs      \- Global Rule Docs   \- Global Rule Docs  
     \- Phase 1 History Only  \- Script Turns Only  \- Shot List History  
     \- User Input            \- Current Script     \- Image Prompt Out  
At the application level, a single master thread is maintained in a database \[cite: 2\]. When the human progresses the production from the *Decision Phase* to the *Writing Phase*, the system switches the active agent. The orchestrator then dynamically filters the history of the unified thread, presenting the incoming agent with a tailored, contextual view of the conversation \[cite: 8\].

## Production Thread Routing and Speaker Selection

The orchestration engine determines the active agent based on the phase of the production pipeline, passing only relevant messages to prevent role bleed \[cite: 8\]. The following implementation demonstrates thread storage, stateful transitions across five phases (Decision, Writing, Visuals, Finishing, Compilation), and dynamic history assembly:  
import uuid  
from datetime import datetime  
from enum import Enum  
from typing import Dict, List, Optional  
from pydantic import BaseModel, Field

class ProductionPhase(str, Enum):  
    DECISION \= "decision"  
    WRITING \= "writing"  
    VISUALS \= "visuals"  
    FINISHING \= "finishing"  
    COMPILATION \= "compilation"

class DbMessage(BaseModel):  
    message\_id: str \= Field(default\_factory=lambda: str(uuid.uuid4()))  
    timestamp: datetime \= Field(default\_factory=datetime.utcnow)  
    role: str  \# "user", "assistant", "tool"  
    sender\_id: str  \# "human", "decision\_agent", "writing\_agent", "visual\_agent", "finishing\_agent", "system"  
    phase: ProductionPhase  
    content: str  
    metadata: Optional\[Dict\[str, Any\]\] \= None

class DynamicOrchestrator:  
    def \_\_init\_\_(self, datastore: List\[DbMessage\]):  
        self.datastore \= datastore  
        self.phase\_agents \= {  
            ProductionPhase.DECISION: "decision\_agent",  
            ProductionPhase.WRITING: "writing\_agent",  
            ProductionPhase.VISUALS: "visual\_agent",  
            ProductionPhase.FINISHING: "finishing\_agent"  
        }

    def write\_message(  
        self,   
        role: str,   
        sender\_id: str,   
        phase: ProductionPhase,   
        content: str,   
        metadata: Optional\[Dict\[str, Any\]\] \= None  
    ) \-\> DbMessage:  
        msg \= DbMessage(role=role, sender\_id=sender\_id, phase=phase, content=content, metadata=metadata)  
        self.datastore.append(msg)  
        return msg

    def compile\_history\_for\_agent(self, target\_agent: str, current\_phase: ProductionPhase) \-\> List\[Dict\[str, str\]\]:  
        """  
        Dynamically generates a specialized context view \[cite: 8\].  
        Filters out low-level intermediate conversations from prior phases,   
        while preserving key artifacts and human instructions to prevent role bleed \[cite: 8\].  
        """  
        agent\_view: List\[Dict\[str, str\]\] \= \[\]  
          
        for msg in self.datastore:  
            \# Rule 1: Always retain human instructions and corrections \[cite: 8\]  
            if msg.sender\_id \== "human":  
                agent\_view.append({  
                    "role": "user",   
                    "content": f"Human Operator: {msg.content}"  
                })  
                continue  
              
            \# Rule 2: Preserve target agent's own historical outputs for phase continuity \[cite: 8\]  
            if msg.sender\_id \== target\_agent:  
                agent\_view.append({  
                    "role": "assistant",   
                    "content": msg.content  
                })  
                continue  
                  
            \# Rule 3: Synthesize major transition points from previous phases as system declarations \[cite: 8, 14\]  
            if current\_phase \== ProductionPhase.WRITING and msg.sender\_id \== "decision\_agent":  
                agent\_view.append({  
                    "role": "system",   
                    "content": f"\[APPROVED CONCEPT\]: {msg.content}"  
                })  
                  
            elif current\_phase \== ProductionPhase.VISUALS and msg.sender\_id \== "writing\_agent":  
                agent\_view.append({  
                    "role": "system",   
                    "content": f"\[APPROVED SCREENPLAY SCRIPT\]: {msg.content}"  
                })  
                  
            elif current\_phase \== ProductionPhase.FINISHING and msg.sender\_id \== "visual\_agent":  
                agent\_view.append({  
                    "role": "system",   
                    "content": f"\[APPROVED VISUAL SHOT LIST\]: {msg.content}"  
                })

        return agent\_view

---

# Context Assembly and Token Optimization Patterns

## Designing a Three-Tier Context Engine

As a production episode progresses, the token count can quickly overwhelm standard model context windows or lead to significant API costs \[cite: 1, 8\]. The system must treat context as a managed resource rather than an open-ended buffer \[cite: 8, 16\]. This is achieved using a **Three-Tier Context Architecture** \[cite: 8\]:  
                    CONTEXT CAPACITY CAP (e.g., 32,000 Tokens)  
┌────────────────────────────────────────────────────────────────────────┐  
│ Tier 1: Hot Global Context (Always Inlined \- System Prompt, Rule Docs) │  
├────────────────────────────────────────────────────────────────────────┤  
│ Tier 2: Warm Working Context (Sliding Window of Last 5-10 Turns)       │  
├────────────────────────────────────────────────────────────────────────┤  
│ Tier 3: Cold Summarized Archive (Compacted Historical Milestones)      │  
└────────────────────────────────────────────────────────────────────────┘

1. **Tier 1: Hot Global Context (Always Inlined)**: Ingests the baseline rules that dictate structural correctness \[cite: 8\]:  
   * The System Prompt.  
   * Core Rule Documents (Show Bible, Visual Treatment, Pipeline Contract) read directly from disk.  
   * The active production state vector (e.g., `active_phase`, `completed_assets`).  
2. **Tier 2: Warm Working Context (Sliding Window)**: Contains the full, unsummarized text of the last 5 to 10 dialogue turns between the human and the current agent \[cite: 8\]. This ensures local dialogue coherence, logical flow, and natural phrasing.  
3. **Tier 3: Cold Summarized Archive (Compacted)**: Conversational turns older than the sliding window threshold are processed, summarized, and appended as a single historical digest block \[cite: 8, 14\]. This is critical to prevent the "lost in the middle" phenomenon \[cite: 8\].

## Token Tracking and Automatic Compaction Engine

The following implementation calculates token boundaries using the `tiktoken` library, automatically compressing older segments of conversation when context limits are reached \[cite: 8, 14, 17\]:  
import tiktoken

class TokenContextAssembler:  
    def \_\_init\_\_(self, client, model\_name: str, max\_allowed\_tokens: int \= 14000):  
        self.client \= client  
        self.model\_name \= model\_name  
        self.max\_tokens \= max\_allowed\_tokens  
        \# Set tokenizer encoding profile  
        try:  
            self.tokenizer \= tiktoken.encoding\_for\_model(model\_name)  
        except KeyError:  
            self.tokenizer \= tiktoken.get\_encoding("cl100k\_base")

    def measure\_tokens(self, text: str) \-\> int:  
        return len(self.tokenizer.encode(text))

    def assemble\_payload(  
        self,   
        system\_prompt: str,   
        rule\_documents: Dict\[str, str\],   
        conversation\_history: List\[Dict\[str, str\]\],   
        window\_size: int \= 6  
    ) \-\> List\[Dict\[str, str\]\]:  
        """  
        Assembles a prioritized context payload \[cite: 8, 16\].  
        Compacts the oldest messages using an auxiliary model if the token count exceeds limits \[cite: 8, 14\].  
        """  
        \# Formulate Tier 1: Hot Context  
        rules\_payload \= "\\n\\n".join(\[f"\#\#\# {k.upper()}\\n{v}" for k, v in rule\_documents.items()\])  
        compiled\_system \= f"{system\_prompt}\\n\\n\# INCORPORATED RULE DOCUMENTS\\n{rules\_payload}"  
          
        system\_token\_cost \= self.measure\_tokens(compiled\_system)  
          
        if system\_token\_cost \> self.max\_tokens \* 0.6:  
            logger.warning("System rules exceed 60% of total token allocation. Compaction threshold compressed.")

        \# Separate history into Warm (unaltered) and Cold (compressible) categories  
        if len(conversation\_history) \<= window\_size:  
            warm\_history \= conversation\_history  
            cold\_history \= \[\]  
        else:  
            warm\_history \= conversation\_history\[-window\_size:\]  
            cold\_history \= conversation\_history\[:-window\_size\]

        \# Calculate total current footprint  
        serialized\_warm \= "".join(\[m\["content"\] for m in warm\_history\])  
        warm\_token\_cost \= self.measure\_tokens(serialized\_warm)

        if system\_token\_cost \+ warm\_token\_cost \< self.max\_tokens:  
            \# Limit is respected; return combined history  
            return \[{"role": "system", "content": compiled\_system}\] \+ conversation\_history

        \# Limit exceeded: Initiate summarization pass on Cold Context \[cite: 8, 14\]  
        logger.info(f"Context payload size ({system\_token\_cost \+ warm\_token\_cost} tokens) exceeds limit. Summarizing history.")  
          
        cold\_text \= "\\n".join(\[f"{msg\['role'\].upper()}: {msg\['content'\]}" for msg in cold\_history\])  
        summary\_instruction \= (  
            "Summarize the following video production dialogue. "  
            "Identify and extract all finalized narrative premises, screenplay segments, "  
            "visual prompt variables, and cutting cues. Remove all pleasantries and rejected proposals."  
        )

        try:  
            summary\_response \= self.client.chat.completions.create(  
                model="gpt-4o-mini",  \# Cost-effective, high-throughput utility model \[cite: 13\]  
                messages=\[  
                    {"role": "system", "content": "The system is an elite technical summarize assistant."},  
                    {"role": "user", "content": f"{summary\_instruction}\\n\\nText to summarize:\\n{cold\_text}"}  
                \],  
                temperature=0.0  
            )  
            compacted\_block \= summary\_response.choices\[0\].message.content  
        except Exception as err:  
            logger.error(f"Automatic context compaction failed: {str(err)}")  
            \# Fallback: Truncate the oldest historical elements to protect model availability \[cite: 8, 14\]  
            return \[{"role": "system", "content": compiled\_system}\] \+ warm\_history

        compacted\_message \= {  
            "role": "system",  
            "content": f"\[COMPACTED ARCHIVE SUMMARY OF PRIOR DECISIONS\]:\\n{compacted\_block}"  
        }

        return \[{"role": "system", "content": compiled\_system}, compacted\_message\] \+ warm\_history

## Prompt Caching Architecture

Static reference files (such as Show Bibles, Visual Treatments, and Pipeline Contracts) represent high-volume, repetitive text \[cite: 18\]. Passing these documents to the API on every message turn causes substantial token overhead and high latency \[cite: 8, 18\].  
Modern production systems leverage **Prompt Caching** (supported natively by frontier APIs like Anthropic and OpenAI) \[cite: 10, 17\]. By structuring the payload so that the static System Prompts and Rule Documents are placed at the very beginning of the message list, model providers cache these parsed tokens \[cite: 10, 17\].  
This ensures that subsequent turns only charge for processing the newly appended, dynamic conversation tokens, reducing input costs by up to 90% and cutting latency down to a fraction of uncached calls.  
---

# Tool Design versus Structured Output Constraints

## The Tool Suppression Trap

A highly critical system-design trap in multi-agent orchestration is **Tool Suppression** (also called "tool-call struggle") \[cite: 19, 20\]. This occurs when a developer activates both Native Tool Calling (Function Calling) and Strict Structured Outputs (`response_format` with JSON Schema) in the exact same LLM API invocation \[cite: 19, 20\].  
              ┌──────────────────────────────────────────────┐  
               │              LLM API CALL                    │  
               │ (Tools defined AND response\_format enforced) │  
               └──────────────────────┬───────────────────────┘  
                                      │  
                   ┌──────────────────┴──────────────────┐  
                   ▼                                     ▼  
          \[Native Tool Calls\]                  \[Strict JSON Output Schema\]  
     "Model must output raw JSON           "Model must output JSON conforming  
     representing tool parameters"         to response\_format exactly"  
                   │                                     │  
                   └──────────────────┬──────────────────┘  
                                      │  
                                      ▼  
                      CRITICAL SYSTEM CONFLICT\!  
       Model skips tool execution entirely to comply with response schema.

When these features are run concurrently, the LLM is forced to output a JSON object matching the *response format* on its very first output token \[cite: 20\]. However, to call a tool, the model must output a specific tool-call sequence instead \[cite: 20, 21\]. This architectural conflict causes the model to bypass the tool call entirely and produce a blank or hallucinated response to satisfy the response schema \[cite: 19, 20\].  
**The Engineering Standard**: Clear, logical sequencing \[cite: 20, 21\].

* During conversational and iterative agent cycles, use **only tool-calling configurations** \[cite: 20, 21, 22\]. Let the model invoke tools, process returned values, and iterate freely without enforcing a final response schema format \[cite: 5, 20\].  
* On the **final turn of the workflow phase**, when the agent is ready to package its completed artifacts, disable all tool definitions and enforce the strict, parsed Pydantic schema using **Structured Outputs (**response\_format**)** \[cite: 20, 22\].

## Principles of Predictable Tool Engineering

When exposing tools to agents, the boundary of execution must be highly secure and deterministic \[cite: 3, 23\]. The agent should only output intentions (structured parameters), while the application layer evaluates safety, validates directories, and coordinates execution \[cite: 3, 5, 23\].  
import os  
from pydantic import BaseModel, Field, ValidationError

class ShotAssetSchema(BaseModel):  
    shot\_id: str \= Field(..., description="Target shot identifier matching format 'EP\[0-9\]+\_S\[0-9\]+'")  
    prompt\_text: str \= Field(..., description="Stylized visual description containing no formatting punctuation.")  
    aspect\_ratio: str \= Field("16:9", description="Target render composition aspect ratio.")

    @validator("shot\_id")  
    def validate\_id(cls, v):  
        import re  
        if not re.match(r"^EP\\d+\_S\\d+$", v):  
            raise ValueError("Shot ID must strictly follow 'EP\[number\]\_S\[number\]' format.")  
        return v

class SecureAssetTool:  
    def \_\_init\_\_(self, output\_root: str):  
        self.output\_root \= os.path.realpath(output\_root)

    def write\_asset\_metadata(self, shot\_id: str, prompt\_text: str, aspect\_ratio: str) \-\> Dict\[str, Any\]:  
        """  
        Tool used by the visual agent to record image generation payloads safely.  
        """  
        \# Step 1: Force strict schema validation on model inputs at runtime \[cite: 21, 23\]  
        try:  
            validated \= ShotAssetSchema(shot\_id=shot\_id, prompt\_text=prompt\_text, aspect\_ratio=aspect\_ratio)  
        except ValidationError as err:  
            return {"status": "error", "message": f"Parameter validation failed: {str(err)}"}

        \# Step 2: Prevent directory traversal attacks \[cite: 3\]  
        target\_path \= os.path.realpath(os.path.join(self.output\_root, f"{validated.shot\_id}.json"))  
        if not target\_path.startswith(self.output\_root):  
            return {"status": "error", "message": "Access Denied: Path traversal detected."}

        \# Step 3: Run deterministic writing operation \[cite: 24\]  
        try:  
            with open(target\_path, "w") as f:  
                f.write(validated.json(indent=2))  
            return {"status": "success", "file\_written": target\_path}  
        except Exception as exc:  
            return {"status": "error", "message": f"Hardware write error: {str(exc)}"}

---

# Interactive Clarification Loops: Asking vs. Guessing

## The Single-Question Gate

To prevent agents from making unverified assumptions when processing ambiguous creative requests, system architectures must implement a **Single-Question Gate** \[cite: 12, 25\]. This pattern forces the model to stop execution and ask a targeted, multiple-choice clarifying question, rather than hallucinating critical pipeline parameters \[cite: 12, 25\].  
However, to prevent the agent from asking too many questions and stalling the workflow, the system must distinguish between **structural ambiguities** (which halt execution) and **stylistic nuances** (which are resolved using default parameters derived from the rule documents) \[cite: 24, 25\].  
                 ┌─────────────────────────────────────┐  
                  │      AMBIGUITY ENCOUNTERED          │  
                  │ (Is the parameter/detail missing?)  │  
                  └──────────────────┬──────────────────┘  
                                     │  
                  ┌──────────────────┴──────────────────┐  
                  ▼                                     ▼  
        \[High-Impact Ambiguity\]                \[Low-Impact Ambiguity\]  
     \- Structural script changes           \- Tone nuances, minor wording  
     \- Rendering ratios / tech specs        \- Color hue variants  
                  │                                     │  
                  ▼                                     ▼  
      Stop & Ask Human \[cite: 25\]           Suggest & Propose \[cite: 24\]

**Implementation of the Intercept Gate**  
The following implementation demonstrates how an agent can request clarification using a specific structural gate, and how the application intercepts this request to pause execution:  
class AgentResponseSchema(BaseModel):  
    requires\_clarification: bool \= Field(  
        ...,   
        description="True ONLY if a structural parameter (aspect ratio, asset directory, scene structure) is missing."  
    )  
    clarifying\_question: Optional\[str\] \= Field(  
        None,   
        description="A single, multiple-choice question resolving the ambiguity. None if requires\_clarification is False."  
    )  
    suggested\_options: Optional\[List\[str\]\] \= Field(  
        None,   
        description="Exactly 3 distinct options for the operator to select from."  
    )  
    payload\_proposal: Optional\[str\] \= Field(  
        None,   
        description="The structured output proposal. Must be empty if requires\_clarification is True."  
    )

class DialogueManager:  
    @staticmethod  
    def process\_agent\_turn(parsed\_response: AgentResponseSchema) \-\> Dict\[str, Any\]:  
        """  
        Evaluates agent response. If a structural question is triggered,   
        it pauses execution and presents the options to the user \[cite: 25, 26\].  
        """  
        if parsed\_response.requires\_clarification:  
            logger.info("Structural clarification triggered. Halting pipeline execution.")  
            return {  
                "execution\_status": "paused",  
                "ui\_action\_required": "render\_question\_modal",  
                "question": parsed\_response.clarifying\_question,  
                "options": parsed\_response.suggested\_options  
            }  
          
        logger.info("Response verified. Proceeding to proposal evaluation.")  
        return {  
            "execution\_status": "ready",  
            "ui\_action\_required": "none",  
            "proposal": parsed\_response.payload\_proposal  
        }

---

# The Propose-Confirm-Apply Transaction Pattern

## Protecting Project State

AI agents must never be granted direct, unsupervised write access to production directories or database tables \[cite: 23, 24\]. Instead, systems must adopt a **Propose-Confirm-Apply Transaction Pattern** \[cite: 23, 24, 26\]. Under this design, the agent acts solely as a proposal engine, while the surrounding application structures the proposal, calculates the downstream blast radius, presents an approval interface to the operator, and executes the final change deterministically \[cite: 23, 24, 26\].  
The proposal payload must include a detailed **blast-radius assessment** to give the operator complete context before making a decision \[cite: 24\]. For example, if the script is modified, the system should flag which visual prompts must be regenerated, estimated rendering costs, and downstream scene impact annotations \[cite: 23, 24\].  
                    PROPOSE-CONFIRM-APPLY TRANSACTION FLOW  
 ┌─────────────────────────────────────────────────────────────────────────┐  
 | 1\. Agent Generates Proposal (Pydantic payload, blast-radius calculation) |  
 └───────────────────────────────────┬─────────────────────────────────────┘  
                                     │  
                                     ▼  
 ┌─────────────────────────────────────────────────────────────────────────┐  
 | 2\. Pending Transaction Database Record Created (State set to 'PENDING')  |  
 └───────────────────────────────────┬─────────────────────────────────────┘  
                                     │  
                                     ▼  
 ┌─────────────────────────────────────────────────────────────────────────┐  
 | 3\. Human Operator UI Verification (Human can APPROVE, REJECT, or MODIFY) |  
 └───────────────────────────────────┬─────────────────────────────────────┘  
                                     │ (On APPROVED)  
                                     ▼  
 ┌─────────────────────────────────────────────────────────────────────────┐  
 | 4\. Deterministic Execution Runner (Runs safely with idempotency checks)  |  
 └─────────────────────────────────────────────────────────────────────────┘

## Structured Proposal Engine with Modification Hook

The following code implements the transaction pattern, tracking proposals in a database and exposing a human modification hook before executing deterministic runs \[cite: 23, 24, 26\]:  
class ScriptProposal(BaseModel):  
    transaction\_id: str \= Field(default\_factory=lambda: str(uuid.uuid4()))  
    scene\_id: str  
    proposed\_dialogue: str  
    scene\_heading: str  
    affected\_files: List\[str\] \= Field(  
        ...,   
        description="Explicit list of downstream asset files that must be regenerated if approved."  
    )  
    estimated\_rendering\_cost\_usd: float

class ProposalLedger:  
    def \_\_init\_\_(self):  
        self.ledger: Dict\[str, Dict\[str, Any\]\] \= {}

    def register\_proposal(self, proposal: ScriptProposal) \-\> str:  
        """  
        Stores the proposal with a 'PENDING' status inside a secure database layer \[cite: 23, 24\].  
        """  
        self.ledger\[proposal.transaction\_id\] \= {  
            "proposal\_data": proposal.dict(),  
            "status": "pending",  
            "registered\_at": datetime.utcnow().isoformat()  
        }  
        return proposal.transaction\_id

    def modify\_proposal\_by\_human(self, transaction\_id: str, human\_modifications: Dict\[str, Any\]):  
        """  
        Allows the human operator to manually edit parameters before confirming \[cite: 26\].  
        """  
        if transaction\_id not in self.ledger:  
            raise KeyError("Transaction not found.")  
        if self.ledger\[transaction\_id\]\["status"\] \!= "pending":  
            raise ValueError("Only pending proposals can be modified.")  
          
        \# Merge human adjustments directly into the stored proposal data  
        self.ledger\[transaction\_id\]\["proposal\_data"\].update(human\_modifications)  
        logger.info(f"Human modification applied to transaction: {transaction\_id}")

    def apply\_transaction(self, transaction\_id: str, runner\_executable: Callable\[\[Dict\[str, Any\]\], bool\]) \-\> bool:  
        """  
        Executes the verified proposal. Implements an idempotency guard \[cite: 23, 24\].  
        """  
        if transaction\_id not in self.ledger:  
            raise KeyError("Transaction not found.")  
          
        record \= self.ledger\[transaction\_id\]  
        if record\["status"\] \== "applied":  
            logger.warning(f"Idempotency Guard Active: Transaction {transaction\_id} already executed.")  
            return True  
              
        \# Update state to prevent double-execution concurrency races \[cite: 23, 24\]  
        record\["status"\] \= "applied"  
          
        \# Execute the deterministic run  
        success \= runner\_executable(record\["proposal\_data"\])  
        if not success:  
            record\["status"\] \= "failed"  
            logger.error(f"Execution failed for transaction {transaction\_id}")  
            return False  
              
        logger.info(f"Transaction {transaction\_id} successfully applied to production.")  
        return True

---

# Qualitative Distinctions: High-Retention vs. Abandoned Agents

The separation between an agent that remains an essential component of a production workflow and one that is quickly discarded lies in subtle, behavioral design decisions \[cite: 11, 12, 25\]. Creative operators abandon tools that introduce friction, behave defensively, or generate inconsistent visual styles \[cite: 11, 12\].  
The following table contrasts the concrete qualitative patterns of successful production-grade agents against abandoned designs \[cite: 11, 12, 24, 25\]:

| Operational Attribute | High-Retention Behavior (The Professional) | Low-Retention Behavior (The Abandoned Chatbot) |
| ----- | ----- | ----- |
| **Response Syntax** | Direct, declarative outputs. Begins with structured actions or immediate suggestions, skipping introductory filler. | Conversational and verbose. Begins with greetings, transitions with explanations of its own logic, and adds polite closing remarks. |
| **Validation & Correction** | Identifies and rejects proposals that violate Show Bible constraints, citing the document and offering alternative solutions. | Agreeably validates conflicting instructions, creating inconsistent aesthetics and corrupted folder hierarchies. |
| **Ambiguity Management** | Detects missing structural variables and halts execution, presenting a single targeted multiple-choice question. | Attempts to guess complex values or make arbitrary assumptions, which propagates errors downstream. |

---

# Subjective Quality Tuning and Regression Testing

## Designing an Analytic Subjective Rubric

Traditional evaluation metrics (such as cosine similarity, BLEU, or toxicity scores) fail when grading highly subjective creative outputs like character voice, visual rhythm, and script compliance \[cite: 29, 30\]. To maintain high standards, development teams must construct a formal evaluation suite using an **Analytic Rubric** with 3-tier ordinal scales \[cite: 29, 31\]. This approach evaluates outputs based on observable text features rather than vague quality ratings \[cite: 31\].  
Rubric Metric: Visual Harmony

* **High (Score 3\)**: The visual output strictly respects all rule constraints in the Visual Treatment. The camera focal lengths and lighting models map cleanly to the scene instructions. No banned visual elements are present.  
* **Medium (Score 2\)**: The output is formatted correctly and is stylistically coherent, but uses visual cliches or contains descriptions that conflict with the Show Bible's timeline.  
* **Low (Score 1\)**: The output directly violates the Visual Treatment or the Story Method. It ignores explicit negative constraints or fails to address the user's immediate instruction \[cite: 11, 12\].

## Overcoming the Traps of LLM-as-Judge

When deploying a powerful model as an automated judge to grade subjective outputs, developers must mitigate three primary biases \[cite: 10, 32\]:

* **Verbosity Bias**: LLM judges tend to assign higher scores to longer, wordier outputs, regardless of actual quality \[cite: 10, 32\]. To counter this, the evaluation prompt must instruct the judge to penalize responses that exceed strict word counts.  
* **Self-Preference Bias**: Models consistently score outputs generated by their own architecture higher than those from other providers \[cite: 10, 32\]. To eliminate this bias, all model identifiers and metadata must be stripped from outputs before evaluation.  
* **Scoring Inconsistency**: Because models are probabilistic, a judge may assign different scores to the same output when run twice \[cite: 32\]. To resolve this, evaluations must use a zero-temperature configuration, run pointwise checks against static reference examples, and average scores from multiple evaluations \[cite: 32, 33\].

Pointwise judges are best suited for continuous production monitoring, as they assign absolute scores to individual responses \[cite: 34\]. Comparative judges (which evaluate two variants of a prompt side-by-side) are ideal for regression testing during prompt engineering phases, as they provide a clearer signal of relative quality \[cite: 34\].

## Automated Golden Dataset Regression Harness

The following testing suite runs prompt changes against a "Golden Dataset" of 50 challenging prompt scenarios, calculating the percentage shift in rubric compliance to ensure updates make the system better rather than differently bad \[cite: 10, 29, 35\]:  
from typing import List, Dict, Any  
from pydantic import BaseModel, Field

class EvaluationResult(BaseModel):  
    score: int \= Field(..., description="Absolute rubric score: 1 (Low), 2 (Medium), or 3 (High).")  
    justification: str \= Field(..., description="Concise explanation citing specific evidence in the text.")

class RegressionHarness:  
    def \_\_init\_\_(self, client, evaluator\_model: str \= "gpt-4o"):  
        self.client \= client  
        self.evaluator\_model \= evaluator\_model

    def evaluate\_output(self, output: str, prompt: str, rubric\_details: str) \-\> EvaluationResult:  
        """  
        Uses an independent LLM as a judge to evaluate agent performance \[cite: 10, 29, 34\].  
        Instructs the model to ignore length and self-preference biases \[cite: 10, 32\].  
        """  
        judge\_system\_prompt \= (  
            "You are an objective QA quality control judge. Grade the agent's output "  
            "strictly against the provided 3-tier rubric rules. Ignore output length. "  
            "Do not favor specific writing styles unless explicitly requested \[cite: 10, 31\]."  
        )  
          
        user\_eval\_prompt \= (  
            f"RUBRIC SPECIFICATIONS:\\n{rubric\_details}\\n\\n"  
            f"ORIGINAL OPERATOR PROMPT:\\n{prompt}\\n\\n"  
            f"AGENT OUTPUT TO EVALUATE:\\n{output}\\n\\n"  
            "Evaluate the output against the rubric rules. Generate a Pydantic response format."  
        )

        response \= self.client.beta.chat.completions.parse(  
            model=self.evaluator\_model,  
            messages=\[  
                {"role": "system", "content": judge\_system\_prompt},  
                {"role": "user", "content": user\_eval\_prompt}  
            \],  
            response\_format=EvaluationResult,  
            temperature=0.0  \# Force maximum deterministic output for testing consistency \[cite: 32\]  
        )  
        return response.choices\[0\].message.parsed

    def run\_regression\_suite(  
        self,   
        golden\_dataset: List\[Dict\[str, str\]\],   
        agent\_runner: Callable\[\[str\], str\],   
        rubric\_details: str  
    ) \-\> Dict\[str, Any\]:  
        """  
        Runs the regression suite across 50 challenging prompt scenarios \[cite: 10, 29, 35\].  
        """  
        total\_score \= 0  
        passed\_cases \= 0  
        failures \= \[\]

        for index, test\_case in enumerate(golden\_dataset):  
            prompt \= test\_case\["prompt"\]  
            expected\_behavior \= test\_case\["expected\_behavior"\]

            \# Run the candidate prompt setup to generate output  
            generated\_output \= agent\_runner(prompt)

            \# Evaluate the output using the pointwise judge  
            result \= self.evaluate\_output(generated\_output, prompt, rubric\_details)  
            total\_score \+= result.score

            if result.score \>= 2:  \# Score of 2 or 3 meets baseline requirements  
                passed\_cases \+= 1  
            else:  
                failures.append({  
                    "case\_index": index,  
                    "prompt": prompt,  
                    "expected\_behavior": expected\_behavior,  
                    "generated\_output": generated\_output,  
                    "justification": result.justification  
                })

        pass\_rate \= (passed\_cases / len(golden\_dataset)) \* 100  
        average\_score \= total\_score / len(golden\_dataset)

        return {  
            "pass\_rate\_percentage": pass\_rate,  
            "average\_rubric\_score": average\_score,  
            "failed\_cases\_log": failures  
        }

---

# Operational Maintenance, Prompt Versioning, and Drift Mitigation

## Controlling Long-Term Behavioral Decay

In production Multi-Agent Systems, prompts behave like compiled code dependencies \[cite: 10\]. However, unlike traditional code, they are highly vulnerable to behavioral drift \[cite: 36\]. Prompt drift is the gradual change in an agent's output behavior over time, occurring even when the prompt itself remains unchanged \[cite: 36, 37\]. It typically stems from two main sources:  
                         SOURCES OF PROMPT DRIFT  
┌────────────────────────────────────────────────────────────────────────┐  
│ 1\. Silent Model Updates                                                │  
│    Providers update API weights or safety filters without changing     │  
│    endpoint names, altering instruction adherence \[cite: 28, 36\].      │  
├────────────────────────────────────────────────────────────────────────┤  
│ 2\. Schema Evolution                                                    │  
│    Database modifications or API updates change parameters, causing    │  
│    older system prompts to request deprecated data formats \[cite: 9\]. │  
└────────────────────────────────────────────────────────────────────────┘

This drift can cause sudden regressions, leading to incorrect tool calls, loss of persona focus, or corrupted output formats \[cite: 9, 37\]. To counter these issues, production multi-agent systems must implement strict maintenance practices \[cite: 10\]:

* **Semantic Schema Locking**: Store system prompts as versioned static assets in git (e.g., `prompts/visual_agent/v1_4_2.txt`), rather than dynamically building them inside the database or code at runtime \[cite: 9, 10\].  
* **Explicit Schema-Version Mapping**: Every system prompt should explicitly declare the database and tool schemas it expects to interact with \[cite: 9\]. If a database migration updates a schema field, the application must block execution of older agents until their prompts are updated to match the new schema \[cite: 9\].  
* **Daily Regression Testing**: Run automated checks against a set of representative prompts every day \[cite: 29, 35\]. If average evaluation scores on the golden dataset drop below a defined threshold (e.g., 90% accuracy), it indicates silent model drift, and the engineering team is instantly alerted to update the prompt \[cite: 10, 29, 35\].

---

# Strategic Framework Evaluation

## Framework Trade-offs for Solo Developers

For a solo developer building and maintaining a specialized creative agent pipeline (4 agents across 5 phases) over multiple years, framework selection is a critical decision \[cite: 7, 38\]. Choosing the wrong abstraction layer can lead to unnecessary development overhead and technical debt \[cite: 7, 39\].

| Agent Framework | Core Model | Learning Curve | Maint. Costs |
| ----- | ----- | ----- | ----- |
| **LangGraph** | Directed Graphs. | Steep (1-2 Weeks). | Deterministic. |
| **CrewAI** | Role-playing. | Gentle (2-4 Hours). | High token cost. |

# Definitive Recommendation

For a solo developer building this specific video production studio, **writing a custom orchestration layer directly on top of the raw provider SDKs** is the most sustainable approach \[cite: 1, 6\].  
The project has highly specific state-transition requirements: 4 agents operating sequentially through 5 distinct phases over a single, continuous message thread \[cite: 8, 14\].

* High-level multi-agent frameworks like **CrewAI** introduce significant token overhead and obscure tool interactions, making it difficult to debug reasoning errors or control precise behavioral outputs \[cite: 38, 39\].  
* Heavy frameworks like **LangGraph** are built to handle complex, cyclic graphs and distributed, multi-user environments \[cite: 7, 39\]. For a single developer, this introduces unnecessary boilerplate, steep learning curves, and complex deployment requirements for a workflow that can be managed with standard Python functions \[cite: 6, 7, 38\].

By writing a minimal, custom Python loop, the developer retains complete control over context compilation, anti-sycophancy rules, and tool execution boundaries \[cite: 1\]. This ensures the entire system remains clean, easy to debug, and simple to maintain over years of updates \[cite: 1, 2\].  
---

# Operational Failures and Mitigation Strategies

The following table serves as an operational reference manual to diagnose and resolve systemic failures in multi-agent creative environments:

| Operational Symptom | Primary Diagnostic Root Cause | Target Correction Mechanism |
| ----- | ----- | ----- |
| **Tool Suppression**: Agent skips tool execution and returns a conversational response \[cite: 19, 20\]. | Conflicting constraints: Tools and strict structured outputs (`response_format`) are activated in the same API call \[cite: 19, 20\]. | **Decouple execution**: Allow the agent to call tools freely, then apply the response schema format only on the final turn \[cite: 20\]. |
| **Role Bleed**: Agent B adopts Agent A's system instructions or voice \[cite: 8\]. | Context pollution: The entire, unedited chat history is passed directly to the model \[cite: 8\]. | **Implement history filtering**: Dynamically filter out previous agent system prompts, passing only human messages and final phase output artifacts \[cite: 8\]. |
| **Lost-in-the-Middle**: Model ignores show bible rules after 10-15 turns of dialogue \[cite: 8\]. | Attention degradation: Important instructions get buried under thousands of tokens of chat logs \[cite: 8\]. | **Apply a Three-Tier Context Engine**: Use a sliding window to compress conversation turns older than 6 turns into a single summary block \[cite: 8, 14\]. |
| **Sycophancy Loop**: Agent repeatedly validates weak or contradictory human suggestions \[cite: 11, 13\]. | Affirmation bias: Model defaults to pleasing the user, reinforced by first-person statement framing \[cite: 11, 13\]. | **Apply behavioral rules**: Force the model to steel-man the human's idea, rephrase inputs as neutral questions, and explicitly forbid pleasantries in the system prompt \[cite: 12, 13\]. |
| **Corrupted Files**: An approved asset is written to disk multiple times, corrupting project data \[cite: 24\]. | Missing Idempotency Controls: Network retries cause the agent's tool execution block to run twice \[cite: 23, 24\]. | **Implement the Propose-Confirm-Apply pattern**: Generate a deterministic payload with a unique transaction ID, write it as a pending record, and check against applied keys before running \[cite: 23, 24\]. |
| **Regression Failure**: Modifying a system prompt fixes one error but breaks three others \[cite: 10\]. | Ad-hoc quality checking: Evaluating prompt variations manually instead of using a formal testing suite \[cite: 10, 29\]. | **Deploy a Pointwise Evaluator**: Establish a golden dataset of 50 challenging, real-world scenarios and use a powerful evaluator model to score outputs against a strict, numeric rubric \[cite: 10, 29, 34\]. |

---

# References

1. Building AI Agents from Scratch in Python (2026) \- OfoxAI, [https://ofox.ai/blog/ai-agent-development-python-guide-2026/](https://ofox.ai/blog/ai-agent-development-python-guide-2026/)  
2. Single-User vs Multi-User AI Agents: Why Architecture Changes Everything at Scale, [https://www.mindstudio.ai/blog/single-user-vs-multi-user-ai-agents-architecture](https://www.mindstudio.ai/blog/single-user-vs-multi-user-ai-agents-architecture)  
3. How to Build AI Agents Using Python: A Step-by-Step Guide \- Ema AI, [https://www.ema.ai/additional-blogs/addition-blogs/building-ai-agents-python-guide](https://www.ema.ai/additional-blogs/addition-blogs/building-ai-agents-python-guide)  
4. Beyond Static Interrupts: Context-Aware Human-in-the-Loop as a Cognitive Process for Trustworthy LLM Agents \- TechRxiv, [https://www.techrxiv.org/doi/pdf/10.36227/techrxiv.176857875.58164328](https://www.techrxiv.org/doi/pdf/10.36227/techrxiv.176857875.58164328)  
5. Chapter 29: Structured Outputs and Function/Tool Calling | AI Agents: Zero to Hero, [https://www.textorch.com/chapters/chapter-29-structured-outputs-and-functiontool-calling](https://www.textorch.com/chapters/chapter-29-structured-outputs-and-functiontool-calling)  
6. Choosing an agent framework: LangChain vs LangGraph vs CrewAI vs PydanticAI vs Mastra vs Vercel AI SDK \- Speakeasy, [https://www.speakeasy.com/blog/ai-agent-framework-comparison/](https://www.speakeasy.com/blog/ai-agent-framework-comparison/)  
7. LangGraph vs CrewAI vs OpenAI Agents SDK: 2026 Comparison \- Particula Tech, [https://particula.tech/blog/langgraph-vs-crewai-vs-openai-agents-sdk-2026](https://particula.tech/blog/langgraph-vs-crewai-vs-openai-agents-sdk-2026)  
8. The Complete Guide to Managing Conversation History in Multi-Agent AI Systems \- Medium, [https://medium.com/@\_Ankit\_Malviya/the-complete-guide-to-managing-conversation-history-in-multi-agent-ai-systems-0e0d3cca6423](https://medium.com/@_Ankit_Malviya/the-complete-guide-to-managing-conversation-history-in-multi-agent-ai-systems-0e0d3cca6423)  
9. Three Ways LLM Pipelines Fail in Production That Staging Will Not Catch \- Techstrong.ai, [https://techstrong.ai/contributed-content/three-ways-llm-pipelines-fail-in-production-that-staging-will-not-catch/](https://techstrong.ai/contributed-content/three-ways-llm-pipelines-fail-in-production-that-staging-will-not-catch/)  
10. The LLM Application Lifecycle: From Prompt to Production \- Applied AI, [https://www.applied-ai.com/briefings/llm-application-lifecycle/](https://www.applied-ai.com/briefings/llm-application-lifecycle/)  
11. How to Prevent AI Sycophancy in Your Workflows: The Multi-Persona Council Method, [https://www.mindstudio.ai/blog/how-to-prevent-ai-sycophancy-multi-persona-council-method](https://www.mindstudio.ai/blog/how-to-prevent-ai-sycophancy-multi-persona-council-method)  
12. Just Use System Prompt to Curtail Sycophancy\! : r/LocalLLaMA \- Reddit, [https://www.reddit.com/r/LocalLLaMA/comments/1nf45xw/just\_use\_system\_prompt\_to\_curtail\_sycophancy/](https://www.reddit.com/r/LocalLLaMA/comments/1nf45xw/just_use_system_prompt_to_curtail_sycophancy/)  
13. Ask Don't Tell: Reducing Sycophancy in Large Language Models | AISI Work, [https://www.aisi.gov.uk/blog/ask-dont-tell-reducing-sycophancy-in-large-language-models-2](https://www.aisi.gov.uk/blog/ask-dont-tell-reducing-sycophancy-in-large-language-models-2)  
14. AG2: Multi-Agent Systems, and Agentic Design Patterns | by Shekharsomani | Medium, [https://medium.com/@shekharsomani98/ag2-multi-agent-systems-and-agentic-design-patterns-52db65596321](https://medium.com/@shekharsomani98/ag2-multi-agent-systems-and-agentic-design-patterns-52db65596321)  
15. ai-agents-for-beginners/08-multi-agent/README.md at main \- GitHub, [https://github.com/microsoft/ai-agents-for-beginners/blob/main/08-multi-agent/README.md](https://github.com/microsoft/ai-agents-for-beginners/blob/main/08-multi-agent/README.md)  
16. AI Agent Architecture Patterns on the Microsoft Stack \- The Cave, [https://www.thepowerplatformcave.com/agent-architecture-patterns-microsoft-foundry-fabric/](https://www.thepowerplatformcave.com/agent-architecture-patterns-microsoft-foundry-fabric/)  
17. Claude Agent SDK in Python: First Agent to Workflows | Augment Code, [https://www.augmentcode.com/guides/claude-agent-sdk-python](https://www.augmentcode.com/guides/claude-agent-sdk-python)  
18. Function Calling vs Tool Use in AI Agents \- Propelius Technologies, [https://propelius.ai/blogs/function-calling-vs-tool-use-ai-agents/](https://propelius.ai/blogs/function-calling-vs-tool-use-ai-agents/)  
19. Constraint Tax in Open-Weight LLMs: An Empirical Study of Tool Calling Suppression Under Structured Output Constraints \- arXiv, [https://arxiv.org/html/2606.25605](https://arxiv.org/html/2606.25605)  
20. Can you use tool calling AND structured output together in LangChain/LangGraph? \- Reddit, [https://www.reddit.com/r/LangChain/comments/1rnaxzt/can\_you\_use\_tool\_calling\_and\_structured\_output/](https://www.reddit.com/r/LangChain/comments/1rnaxzt/can_you_use_tool_calling_and_structured_output/)  
21. Function Calling vs Structured Outputs: Safe Tool Use Guide \- Services Ground, [https://servicesground.com/blog/function-calling-structured-outputs/](https://servicesground.com/blog/function-calling-structured-outputs/)  
22. Structured model outputs | OpenAI API, [https://developers.openai.com/api/docs/guides/structured-outputs](https://developers.openai.com/api/docs/guides/structured-outputs)  
23. Laravel AI Agent: Human-in-the-Loop Approval \- Origin Main, [https://origin-main.com/ai-agents/laravel-ai-agent-human-in-the-loop-approval/](https://origin-main.com/ai-agents/laravel-ai-agent-human-in-the-loop-approval/)  
24. Human-in-the-Loop AI Agents: How to Design Approval Workflows for Safe and Scalable Automation \- StackAI, [https://www.stackai.com/insights/human-in-the-loop-ai-agents-how-to-design-approval-workflows-for-safe-and-scalable-automation](https://www.stackai.com/insights/human-in-the-loop-ai-agents-how-to-design-approval-workflows-for-safe-and-scalable-automation)  
25. Reframing LLM Agent Security as an Agent–Human Interaction Problem \- arXiv, [https://arxiv.org/html/2605.24309v1](https://arxiv.org/html/2605.24309v1)  
26. Approval Human In The Loop Node (HITL) (\#20652) · Epic · gitlab-org, [https://gitlab.com/groups/gitlab-org/-/epics/20652](https://gitlab.com/groups/gitlab-org/-/epics/20652)  
27. Prompt Drift & Chaining \- HumanFirst | AI, [https://www.humanfirst.ai/blog/prompt-drift-chaining](https://www.humanfirst.ai/blog/prompt-drift-chaining)  
28. LLM Drift, Prompt Drift & Cascading \- Kore.ai, [https://www.kore.ai/blog/llm-drift-prompt-drift-cascading](https://www.kore.ai/blog/llm-drift-prompt-drift-cascading)  
29. LLM Evaluation: Practical Tips at Booking.com \- MLOps Community, [https://mlops.community/llm-evaluation-practical-tips-at-booking-com](https://mlops.community/llm-evaluation-practical-tips-at-booking-com)  
30. Evaluating large language model applications with LLM-augmented feedback \- dataroots, [https://dataroots.io/blog/evaluating-llm](https://dataroots.io/blog/evaluating-llm)  
31. Rubric-Based Evaluations & LLM-as-a-Judge — Methodologies, Biases, and Empirical Validation in Domain-Specific Contexts. | by Adnan Masood, PhD. | Medium, [https://medium.com/@adnanmasood/rubric-based-evals-llm-as-a-judge-methodologies-and-empirical-validation-in-domain-context-71936b989e80](https://medium.com/@adnanmasood/rubric-based-evals-llm-as-a-judge-methodologies-and-empirical-validation-in-domain-context-71936b989e80)  
32. How to Evaluate AI that's Smarter than Us \- ACM Queue, [https://queue.acm.org/detail.cfm?id=3722043](https://queue.acm.org/detail.cfm?id=3722043)  
33. Human-in-the-Loop Evals at Scale: Golden Sets, Review Queues & Drift Watch \- Kinde, [https://kinde.com/learn/ai-for-software-engineering/ai-devops/human-in-the-loop-evals-at-scale-golden-sets-review-queues-drift-watch/](https://kinde.com/learn/ai-for-software-engineering/ai-devops/human-in-the-loop-evals-at-scale-golden-sets-review-queues-drift-watch/)  
34. Booking.com: LLM-as-a-Judge Framework for Automated LLM Evaluation at Scale \- ZenML, [https://www.zenml.io/llmops-database/llm-as-a-judge-framework-for-automated-llm-evaluation-at-scale](https://www.zenml.io/llmops-database/llm-as-a-judge-framework-for-automated-llm-evaluation-at-scale)  
35. Prompt Evaluation Explained: Random Sampling vs. Golden Datasets \- Helicone, [https://www.helicone.ai/blog/prompt-evaluation-for-llms](https://www.helicone.ai/blog/prompt-evaluation-for-llms)  
36. Prompt Drift: What It Is and How to Detect It \- Agenta-AI, [https://agenta.ai/blog/prompt-drift](https://agenta.ai/blog/prompt-drift)  
37. Prompt Drift: The Hidden Failure Mode Undermining Agentic Systems, [https://www.comet.com/site/blog/prompt-drift/](https://www.comet.com/site/blog/prompt-drift/)  
38. AI Agent Frameworks Compared: LangGraph vs CrewAI vs AutoGen (2026) \- PE Collective, [https://pecollective.com/blog/ai-agent-frameworks-compared/](https://pecollective.com/blog/ai-agent-frameworks-compared/)  
39. Agentic AI Frameworks 2026: Production Comparison | Uvik Software, [https://uvik.net/blog/agentic-ai-frameworks/](https://uvik.net/blog/agentic-ai-frameworks/)  
40. The 9 Best AI Agent Frameworks in 2026 (We Tested Every Single One) | AgentMail, [https://www.agentmail.to/blog/best-ai-agent-frameworks-2026](https://www.agentmail.to/blog/best-ai-agent-frameworks-2026)


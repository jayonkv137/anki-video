# The Universal Learning System

> "You have a vision, but you must fundamentally understand the lines of code that make that vision a reality."

## 1. The Core Philosophy
When a creator uses AI to build complex codebases, a dangerous disconnect forms. You know *what* the software does, but you lose the fundamental understanding of *how* it works under the hood. 

The Universal Learning System is designed to bridge this gap. It is an agentic tutoring framework built directly into your project. It does not teach you generic coding concepts; it teaches you **your exact codebase** by mapping abstract concepts to the actual lines of code running in your project.

## 2. The 4 Pillars of Learning
Whenever you trigger the learning system, the AI must adhere to these pillars:

1. **Medium Agnosticism (Unconstrained Creativity)**: The AI is not restricted to text or terminal scripts. It must invent the absolute best medium to teach the specific concept—whether that is an interactive HTML visualizer, a logic puzzle, a roleplay game, or a physical real-world analogy.
2. **The Glass Box (Code-Concept Bridging)**: The interactivity must not be a black-box toy. Every action you take in a micro-world must expose the engine. If you click a button in a visualizer, the UI must show you the exact `python` or `SQL` snippet from your project that handles that logic.
3. **Foundational Logical Thinking**: The activity must force your brain to engage with foundational coding logic (if/then branching, state management, loops, relational mapping). 
4. **The "What-If" Breakage Loop**: You must be able to safely break the system (e.g., triggering a cascade delete, or violating an API constraint) to visually learn *why* the guardrails exist.

## 3. How to Use It
Because this system is registered in your `.agents/skills/learn/SKILL.md` and global `CLAUDE.md`, it is permanently available in both **Antigravity** and **Claude Code**.

To trigger it, simply type:
```bash
/learn [Phase or Concept]
```
*(e.g., `/learn E3` or `/learn how the ledger module connects to Supabase`)*

The AI will then:
1. Generate an **Explainer Artifact** (Background, Intuition, Literate Walkthrough).
2. Pitch you interactive **Glass-Box Micro-worlds** using the best possible medium.
3. Evaluate your understanding with a tricky, interactive **Verification Quiz**.
4. Log your passing score (80%+) as permanent evidence in the `LEARNING_LEDGER.md`.

## 4. The "Quota Fallback" Workflow
The primary utility of the Universal Learning System is to ensure momentum never stops. 

When you hit an API quota/credit limit while coding (e.g., Opus 4.6 runs out), do not stop working. Instead:
1. Switch to a lower-cost or unlimited model (e.g., Gemini 3.5 Flash).
2. Trigger `/learn [Topic]` to spend the downtime mastering the architecture of what you just built.

**The Antigravity "Rewind & Graft" Maneuver:**
If you want to `/learn` but preserve your exact chat history for when the quota resets:
1. Copy the `docs/learning_system/` and `.agents/` folders to your Desktop.
2. **Rewind** the Antigravity chat back to the moment before you started learning.
3. Paste the folders back into the workspace.
4. Send a prompt to the AI telling it to read the learning files and resume building. You keep your chat context, but safely inject the new learning progress!

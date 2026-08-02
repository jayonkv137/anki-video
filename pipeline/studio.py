"""Studio — the episode thread, the phase router, the view compiler, the gates.

This is the shell every V4 agent runs inside. It owns four things and no creative
logic whatsoever:

  1. THE THREAD — one continuous conversation per episode, persisted as
     `thread.json` beside the artifacts. It never resets across the five phases.
  2. THE PHASE ROUTER — which agent answers, and which canon it is given
     (`context.py` per PIPELINE §3 read-lists).
  3. THE VIEW COMPILER — the anti-role-bleed mechanism. An agent NEVER sees the
     raw transcript; it sees a filtered projection (§ "Dynamic role-based views"
     in the agent-engineering research): every human turn, its OWN prior turns,
     and other phases' locked artifacts re-projected as `[APPROVED …]` system
     declarations. Another agent's chatter is not context; it is contamination.
  4. THE GATES — six human approvals (PIPELINE §5). Both working modes end here.

Modes (DESIGN_autopilot.md v2, approved 2026-08-02):
  co_create — the agent converses; Jayon's ideas are the input.
  draft     — no conversation; the agent decides and presents a finished artifact
              plus a DECISION JOURNAL, so approving is reviewing rather than
              rubber-stamping.
**The gate is human in BOTH modes.** Nothing here can approve anything, and
nothing here spends money — generation is always downstream of a human approval.
"""

import json
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from . import context as ctx
from .rcp import REPO

EPISODES = REPO / "output" / "episodes"

# The five phases, in order (PIPELINE §2.1). "qc" is not here: QC never speaks.
PHASE_ORDER = ["idea", "script", "vision", "shoot", "post"]

PHASE_AGENT = {"idea": "showrunner", "script": "writer",
               "vision": "director", "shoot": "director", "post": "editor"}

# The artifact each phase locks, and the gate's human-facing name (PIPELINE §5).
PHASE_ARTIFACT = {"idea": "brief.json", "script": "screenplay.json",
                  "vision": "storyboard.json", "shoot": "prompts.json",
                  "post": "subtitles.json"}
GATE_NAME = {"idea": "brief lock", "script": "screenplay confirm",
             "vision": "sheet approval", "shoot": "clip acceptance", "post": "export"}

CO_CREATE, DRAFT = "co_create", "draft"
# Approved defaults (D8): Vision/Shoot/Post are draft-BY-NATURE — their station
# contracts forbid creative invention, so there is nothing to co-create there.
DEFAULT_MODES = {"idea": CO_CREATE, "script": CO_CREATE,
                 "vision": DRAFT, "shoot": DRAFT, "post": DRAFT}
DEFAULT_SETTINGS = {
    "auto_reroll_on_technical_failure": 0,   # D8: nothing generates twice without a human
    "max_redrafts": 2,                       # then the agent asks instead of looping
}

# Message kinds. `proposal` and `journal` render as the same card — the only
# difference is who asked for it (a change request vs. a draft-mode decision).
KINDS = ("chat", "proposal", "journal", "gate", "qc", "handoff", "note")


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


class StudioError(RuntimeError):
    """An illegal studio operation — a bad phase, a gate out of order, a
    locked artifact edited without reopening it."""


# ── The thread ───────────────────────────────────────────────────

@dataclass
class Thread:
    episode_id: str
    path: Path
    data: dict

    # -- lifecycle -------------------------------------------------
    @classmethod
    def create(cls, episode_id: str, *, modes: dict | None = None,
               settings: dict | None = None) -> "Thread":
        ep = EPISODES / episode_id
        ep.mkdir(parents=True, exist_ok=True)
        data = {
            "episode_id": episode_id,
            "created_at": _now(),
            "phase": PHASE_ORDER[0],
            "phase_modes": {**DEFAULT_MODES, **(modes or {})},
            "settings": {**DEFAULT_SETTINGS, **(settings or {})},
            "gates": {p: {"state": "open", "locked_at": None, "redrafts": 0}
                      for p in PHASE_ORDER},
            "messages": [],
        }
        t = cls(episode_id, ep / "thread.json", data)
        t.save()
        t.append("system", "system", kind="handoff",
                 content=f"Episode {episode_id} opened at phase '{PHASE_ORDER[0]}' "
                         f"({data['phase_modes'][PHASE_ORDER[0]]}).")
        return t

    @classmethod
    def load(cls, episode_id: str) -> "Thread":
        p = EPISODES / episode_id / "thread.json"
        if not p.exists():
            raise StudioError(f"no thread for episode '{episode_id}' — create it first")
        return cls(episode_id, p, json.loads(p.read_text(encoding="utf-8")))

    def save(self) -> None:
        self.path.write_text(json.dumps(self.data, ensure_ascii=False, indent=2),
                             encoding="utf-8")

    # -- accessors -------------------------------------------------
    @property
    def phase(self) -> str:
        return self.data["phase"]

    @property
    def messages(self) -> list:
        return self.data["messages"]

    def mode(self, phase: str | None = None) -> str:
        return self.data["phase_modes"][phase or self.phase]

    def set_mode(self, phase: str, mode: str) -> None:
        if phase not in PHASE_ORDER:
            raise StudioError(f"unknown phase '{phase}'")
        if mode not in (CO_CREATE, DRAFT):
            raise StudioError(f"unknown mode '{mode}'")
        self.data["phase_modes"][phase] = mode
        self.append("system", "system", phase=phase, kind="handoff",
                    content=f"{phase} switched to {mode}.")

    def gate(self, phase: str | None = None) -> dict:
        return self.data["gates"][phase or self.phase]

    def artifact_path(self, phase: str | None = None) -> Path:
        return EPISODES / self.episode_id / PHASE_ARTIFACT[phase or self.phase]

    # -- writing ---------------------------------------------------
    def append(self, role: str, sender: str, *, content: str = "",
               kind: str = "chat", phase: str | None = None,
               meta: dict | None = None) -> dict:
        if kind not in KINDS:
            raise StudioError(f"unknown message kind '{kind}'")
        msg = {"id": uuid.uuid4().hex[:12], "ts": _now(), "role": role,
               "sender": sender, "phase": phase or self.phase, "kind": kind,
               "content": content, "meta": meta or {}}
        self.messages.append(msg)
        self.save()
        return msg

    def human(self, content: str) -> dict:
        return self.append("user", "human", content=content)

    def agent(self, content: str, *, kind: str = "chat", meta: dict | None = None) -> dict:
        return self.append("assistant", PHASE_AGENT[self.phase],
                           content=content, kind=kind, meta=meta)

    def journal(self, decision: str, why: str, *,
                considered: list | None = None, assumption: str = "") -> dict:
        """A draft-mode decision, rendered as the same card the change protocol
        emits. This is what makes approving a drafted artifact a review rather
        than a rubber stamp (DESIGN_autopilot §5)."""
        return self.append("assistant", PHASE_AGENT[self.phase], kind="journal",
                           content=decision,
                           meta={"why": why, "considered": considered or [],
                                 "assumption": assumption})

    def qc(self, blocks: list, flags: list) -> dict:
        """QC never speaks (PIPELINE §3.5) — it attaches to the artifact as chips."""
        verdict = "blocked" if blocks else ("flagged" if flags else "clear")
        return self.append("system", "system", kind="qc",
                           content=f"QC {verdict}: {len(blocks)} block(s), {len(flags)} flag(s)",
                           meta={"blocks": blocks, "flags": flags, "verdict": verdict})

    def open_questions(self) -> list:
        """Assumptions a draft-mode agent had to make, still unanswered at this
        phase — surfaced AT the gate rather than parking the episode, because a
        human is arriving anyway (DESIGN_autopilot §5)."""
        return [m for m in self.messages
                if m["kind"] == "journal" and m["phase"] == self.phase
                and (m["meta"] or {}).get("assumption")]


# ── The gates ────────────────────────────────────────────────────

def gate_status(t: Thread) -> dict:
    """Everything the UI needs to render the gate. `can_approve` is advisory —
    it reports whether QC is clear, it does NOT approve anything."""
    g = t.gate()
    latest_qc = next((m for m in reversed(t.messages)
                      if m["kind"] == "qc" and m["phase"] == t.phase), None)
    blocks = (latest_qc or {}).get("meta", {}).get("blocks", [])
    flags = (latest_qc or {}).get("meta", {}).get("flags", [])
    return {
        "phase": t.phase, "gate": GATE_NAME[t.phase], "agent": PHASE_AGENT[t.phase],
        "mode": t.mode(), "state": g["state"],
        "artifact": PHASE_ARTIFACT[t.phase],
        "artifact_exists": t.artifact_path().exists(),
        "blocks": blocks, "flags": flags,
        "open_questions": [m["meta"]["assumption"] for m in t.open_questions()],
        "redrafts": g["redrafts"],
        "can_approve": t.artifact_path().exists() and not blocks,
    }


def approve(t: Thread, note: str = "") -> dict:
    """THE human action. Locks the phase, compacts its conversation, advances.
    There is deliberately no programmatic caller for this other than a person:
    both modes end here (DESIGN_autopilot §1)."""
    st = gate_status(t)
    if st["state"] == "locked":
        raise StudioError(f"phase '{t.phase}' is already locked")
    if not st["artifact_exists"]:
        raise StudioError(f"nothing to approve — {st['artifact']} does not exist yet")
    if st["blocks"]:
        raise StudioError(f"cannot approve: {len(st['blocks'])} hard block(s) — "
                          f"first is: {st['blocks'][0]}")

    phase = t.phase
    t.gate()["state"] = "locked"
    t.gate()["locked_at"] = _now()
    t.append("user", "human", kind="gate",
             content=f"APPROVED — {GATE_NAME[phase]}" + (f": {note}" if note else ""),
             meta={"action": "approve", "note": note, "flags_carried": st["flags"]})
    _compact(t, phase)

    nxt = next_phase(phase)
    if nxt:
        t.data["phase"] = nxt
        t.append("system", "system", phase=nxt, kind="handoff",
                 content=f"— {PHASE_AGENT[nxt].upper()} takes over · {nxt} "
                         f"({t.mode(nxt)}) —")
    t.save()
    return {"locked": phase, "now": t.data["phase"], "flags_carried": st["flags"]}


def reject(t: Thread, note: str) -> dict:
    """Send the artifact back for a redraft with the note as a constraint.
    Bounded: after `max_redrafts` the agent must ask rather than loop."""
    if not note.strip():
        raise StudioError("a rejection needs a note — 'no' is not a constraint")
    g = t.gate()
    g["redrafts"] += 1
    exhausted = g["redrafts"] > t.data["settings"]["max_redrafts"]
    t.append("user", "human", kind="gate", content=f"REJECTED — {note}",
             meta={"action": "reject", "note": note,
                   "redraft": g["redrafts"], "budget_exhausted": exhausted})
    t.save()
    return {"redraft": g["redrafts"], "must_ask_instead": exhausted}


def reopen(t: Thread, phase: str, reason: str = "") -> dict:
    """Unlock a locked phase. Everything downstream of it becomes stale — the
    caller must show that recompile set BEFORE calling this (PIPELINE §6)."""
    if phase not in PHASE_ORDER:
        raise StudioError(f"unknown phase '{phase}'")
    if t.data["gates"][phase]["state"] != "locked":
        raise StudioError(f"phase '{phase}' is not locked")
    downstream = PHASE_ORDER[PHASE_ORDER.index(phase) + 1:]
    stale = [p for p in downstream if t.data["gates"][p]["state"] == "locked"]
    for p in [phase] + stale:
        t.data["gates"][p]["state"] = "open"
        t.data["gates"][p]["locked_at"] = None
    t.data["phase"] = phase
    t.append("user", "human", phase=phase, kind="gate",
             content=f"REOPENED {phase}" + (f" — {reason}" if reason else ""),
             meta={"action": "reopen", "reason": reason, "invalidated": stale})
    t.save()
    return {"reopened": phase, "invalidated": stale}


def next_phase(phase: str) -> str | None:
    i = PHASE_ORDER.index(phase)
    return PHASE_ORDER[i + 1] if i + 1 < len(PHASE_ORDER) else None


def recompile_set(phase: str) -> list:
    """What reopening `phase` invalidates. The GRAPH decides this, never a model
    (PIPELINE §6) — the UI must show it before the reopen, not after."""
    return PHASE_ORDER[PHASE_ORDER.index(phase) + 1:]


# ── Compaction (Tier 3) ──────────────────────────────────────────

def _compact(t: Thread, phase: str) -> None:
    """On lock, a phase's conversation collapses to one digest line. The ARTIFACT
    carries the detail — so the thread stays readable at episode 170 and the
    context stays bounded (three-tier architecture, Tier 3)."""
    turns = [m for m in t.messages
             if m["phase"] == phase and m["kind"] in ("chat", "journal")]
    if not turns:
        return
    human_turns = sum(1 for m in turns if m["sender"] == "human")
    decisions = [m["content"] for m in turns if m["kind"] == "journal"]
    digest = (f"[{phase.upper()} LOCKED · {t.mode(phase)}] "
              f"{len(turns)} turns ({human_turns} from the creator)"
              + (f" · decisions: {'; '.join(decisions[:6])}" if decisions else "")
              + f" · detail lives in {PHASE_ARTIFACT[phase]}")
    for m in turns:
        m["meta"]["compacted"] = True
    t.append("system", "system", phase=phase, kind="handoff", content=digest,
             meta={"compaction": True, "turns": len(turns)})


# ── The view compiler (anti-role-bleed) ──────────────────────────

def compile_view(t: Thread, *, phase: str | None = None,
                 window: int = 10) -> list[dict]:
    """Project the thread into what THIS phase's agent may see.

    Rules (the dynamic role-based view from the agent-engineering research):
      1. every HUMAN turn survives — corrections are never dropped;
      2. the acting agent's OWN prior turns survive (phase continuity);
      3. another agent's conversational turns are DROPPED — reading them is how
         an agent adopts a neighbour's voice and starts doing its job;
      4. a locked phase survives as a single `[APPROVED …]` system declaration,
         not as its transcript — the artifact is the contract (PIPELINE §4);
      5. compacted turns are replaced by their digest;
      6. only the last `window` conversational turns are kept verbatim (Tier 2).
    """
    phase = phase or t.phase
    agent = PHASE_AGENT[phase]
    out: list[dict] = []

    for m in t.messages:
        kind, sender, mphase = m["kind"], m["sender"], m["phase"]

        if kind == "handoff" and m["meta"].get("compaction"):
            out.append({"role": "system", "content": m["content"]})
            continue
        if m["meta"].get("compacted"):
            continue                                   # rule 5
        if kind == "qc":
            if mphase == phase:                        # only your own linter
                out.append({"role": "system", "content": m["content"]})
            continue
        if kind == "gate":
            if m["meta"].get("action") == "approve" and mphase != phase:
                # The creator's note on approval is a HUMAN instruction — rule 1
                # applies to it, so it rides forward with the declaration. Dropping
                # it would silently lose guidance like "ship it, but tighter next time".
                note = (m["meta"].get("note") or "").strip()
                decl = (f"[APPROVED {mphase.upper()}] {PHASE_ARTIFACT[mphase]} is locked "
                        f"and is now a fixed input. Do not re-decide it.")
                if note:
                    decl += f'\nThe creator said on approving it: "{note}"'
                out.append({"role": "system", "content": decl})
            elif mphase == phase:
                out.append({"role": "user", "content": f"Creator: {m['content']}"})
            continue
        if kind == "handoff":
            continue
        if sender == "human":                          # rule 1
            out.append({"role": "user", "content": f"Creator: {m['content']}"})
            continue
        if sender == agent and mphase == phase:        # rule 2
            out.append({"role": "assistant", "content": m["content"]})
            continue
        # rule 3 — another agent's chatter is contamination, not context.

    # rule 6 — keep system declarations, trim the conversational tail
    convo = [i for i, msg in enumerate(out) if msg["role"] in ("user", "assistant")]
    if len(convo) > window:
        drop = set(convo[:-window])
        out = [msg for i, msg in enumerate(out) if i not in drop]
    return out


def system_prompt(t: Thread, skill_text: str, *, phase: str | None = None,
                  data_blocks: dict | None = None) -> str:
    """Tier 1: the phase's canon + station contract + live data + its skill.

    `data_blocks` carries the non-canon inputs the caller resolved — curriculum
    slice, UNIVERSE_STATE story-so-far, standing constraints, the drawn seed,
    the upstream artifacts. They are DATA, appended after canon, never mixed in.
    """
    phase = phase or t.phase
    parts = [ctx.canon_context(phase)]
    for name, block in (data_blocks or {}).items():
        if block:
            parts.append(f"# {name.upper()}\n\n{block}")
    mode = t.mode(phase)
    parts.append(
        f"# YOUR WORKING MODE — {mode.upper()}\n\n"
        + ("Converse. Draw the creator's ideas out, offer options, push back when "
           "canon requires it, and ask ONE targeted question when a structural "
           "detail is genuinely missing. The artifact is the residue of the "
           "dialogue — do not write it alone."
           if mode == CO_CREATE else
           "No conversation. Decide everything yourself from the canon, the "
           "curriculum, the state and the seed, and produce the finished artifact.\n"
           "For every significant choice, emit a JOURNAL entry: what you chose, "
           "what else you considered, and why — the creator reviews your reasoning "
           "at the gate, so an unexplained choice is an unreviewable one.\n"
           "Where you would have asked a question, proceed with your best answer "
           "and record it as an ASSUMPTION on that entry. Never invent a fact you "
           "could have derived; never silently paper over a gap.")
        + "\n\n**The creator approves this phase either way. You never approve it.**")
    parts.append(skill_text)
    return "\n\n---\n\n".join(parts)


# ── Episode overview (Home) ──────────────────────────────────────

def overview(t: Thread) -> dict:
    return {
        "episode_id": t.episode_id,
        "phase": t.phase,
        "modes": t.data["phase_modes"],
        "settings": t.data["settings"],
        "gates": {p: {"state": t.data["gates"][p]["state"],
                      "gate": GATE_NAME[p],
                      "artifact": PHASE_ARTIFACT[p],
                      "exists": (EPISODES / t.episode_id / PHASE_ARTIFACT[p]).exists()}
                  for p in PHASE_ORDER},
        "messages": len(t.messages),
        "status": gate_status(t),
    }


def list_episodes() -> list[dict]:
    out = []
    if not EPISODES.exists():
        return out
    for d in sorted(EPISODES.iterdir(), key=lambda p: p.stat().st_mtime, reverse=True):
        if (d / "thread.json").exists():
            try:
                out.append(overview(Thread.load(d.name)))
            except Exception:
                continue
    return out

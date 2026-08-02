"""Studio API — the V4 backend, deliberately layout-agnostic.

Phase 2.3a. Every endpoint here is a thin, honest wrapper over `pipeline.studio`
and the state layer. **Nothing in this module knows what a screen looks like**,
which is the point: the UI is being redesigned from scratch, and whatever it
becomes will consume exactly these endpoints.

Design rules held here:
  · The gate is human. There is no endpoint that approves anything on its own.
  · Money is never spent on the far side of a decision the human didn't make.
    `/cost-preview` exists so a UI can show the price BEFORE the click.
  · Reopening shows its blast radius first — `/recompile/{phase}` is a read.
  · Failures are loud. No endpoint invents a fallback artifact.

Mounted at /api/studio/* beside the legacy V3 wizard, which is untouched and
dies at Phase 3.5.
"""

import json
from pathlib import Path

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from pipeline import context as ctx
from pipeline import lessons as L
from pipeline import studio as S
from pipeline import universe_state as st

router = APIRouter(prefix="/api/studio", tags=["studio"])

# Indicative unit costs, first-party (Cloud Infrastructure report, 2026-08).
# Video is UNVERIFIED until one real Seedance call — the UI must say so rather
# than show a confident number we made up.
COST = {"sheet_2k_usd": 0.134, "clip_15s_usd": None}


def _thread(episode_id: str) -> S.Thread:
    try:
        return S.Thread.load(episode_id)
    except S.StudioError as e:
        raise HTTPException(404, str(e))


def _guard(fn):
    """StudioError is a 409 — an illegal transition, not a server fault."""
    try:
        return fn()
    except S.StudioError as e:
        raise HTTPException(409, str(e))
    except st.StateError as e:
        raise HTTPException(500, f"state write failed: {e}")


# ── Episodes ─────────────────────────────────────────────────────

class NewEpisode(BaseModel):
    episode_id: str | None = None
    module_id: str | None = None
    modes: dict | None = None
    settings: dict | None = None


@router.get("/episodes")
def list_episodes():
    return S.list_episodes()


@router.post("/episodes")
def create_episode(body: NewEpisode):
    eid = body.episode_id
    if not eid:
        mod = body.module_id or (st.curriculum_status()["next_module"] or "x")
        n = sum(1 for e in S.list_episodes() if e["episode_id"].startswith(f"ep_{mod}"))
        eid = f"ep_{mod.replace('.', '-')}_{n + 1}"
    if (S.EPISODES / eid / "thread.json").exists():
        raise HTTPException(409, f"episode '{eid}' already exists")
    t = S.Thread.create(eid, modes=body.modes, settings=body.settings)
    return S.overview(t)


@router.get("/episodes/{episode_id}")
def get_episode(episode_id: str):
    return S.overview(_thread(episode_id))


@router.get("/episodes/{episode_id}/thread")
def get_thread(episode_id: str, phase: str | None = None):
    """The full conversation for rendering. Journal and proposal messages carry
    their card data in `meta` — the UI renders them, it does not re-derive them."""
    t = _thread(episode_id)
    msgs = [m for m in t.messages if not phase or m["phase"] == phase]
    return {"episode_id": episode_id, "phase": t.phase, "messages": msgs}


@router.get("/episodes/{episode_id}/view")
def get_view(episode_id: str, phase: str | None = None, window: int = 10):
    """The compiled agent view — what the acting agent will actually see.
    Exposed because anti-role-bleed is invisible in output; being able to LOOK
    at the projection is the only way to trust it."""
    t = _thread(episode_id)
    return {"phase": phase or t.phase,
            "view": S.compile_view(t, phase=phase, window=window)}


@router.get("/episodes/{episode_id}/artifact/{phase}")
def get_artifact(episode_id: str, phase: str):
    t = _thread(episode_id)
    if phase not in S.PHASE_ORDER:
        raise HTTPException(404, f"unknown phase '{phase}'")
    p = t.artifact_path(phase)
    if not p.exists():
        return {"phase": phase, "artifact": S.PHASE_ARTIFACT[phase], "data": None}
    return {"phase": phase, "artifact": S.PHASE_ARTIFACT[phase],
            "data": json.loads(p.read_text(encoding="utf-8"))}


# ── The conversation ─────────────────────────────────────────────

class Message(BaseModel):
    content: str


@router.post("/episodes/{episode_id}/message")
def post_message(episode_id: str, body: Message):
    """Record a human turn. Running the agent is Phase 3 — this is the shell."""
    t = _thread(episode_id)
    if not body.content.strip():
        raise HTTPException(400, "empty message")
    return t.human(body.content.strip())


# ── Modes ────────────────────────────────────────────────────────

class ModeChange(BaseModel):
    phase: str
    mode: str


@router.post("/episodes/{episode_id}/mode")
def set_mode(episode_id: str, body: ModeChange):
    t = _thread(episode_id)
    _guard(lambda: t.set_mode(body.phase, body.mode))
    return S.overview(t)


# ── The gate (always human) ──────────────────────────────────────

class GateAction(BaseModel):
    note: str = ""


@router.get("/episodes/{episode_id}/gate")
def gate(episode_id: str):
    return S.gate_status(_thread(episode_id))


@router.post("/episodes/{episode_id}/approve")
def approve(episode_id: str, body: GateAction):
    t = _thread(episode_id)
    res = _guard(lambda: S.approve(t, body.note))
    return {**res, "overview": S.overview(t)}


@router.post("/episodes/{episode_id}/reject")
def reject(episode_id: str, body: GateAction):
    t = _thread(episode_id)
    res = _guard(lambda: S.reject(t, body.note))
    return {**res, "gate": S.gate_status(t)}


class Reopen(BaseModel):
    phase: str
    reason: str = ""


@router.get("/episodes/{episode_id}/recompile/{phase}")
def recompile_preview(episode_id: str, phase: str):
    """The blast radius, as a READ. The UI shows this BEFORE offering the reopen —
    the creator should never learn the cost of an edit after making it."""
    t = _thread(episode_id)
    if phase not in S.PHASE_ORDER:
        raise HTTPException(404, f"unknown phase '{phase}'")
    downstream = S.recompile_set(phase)
    stale = [p for p in downstream if t.data["gates"][p]["state"] == "locked"]
    ep = S.EPISODES / episode_id
    sheets = len(list((ep / "storyboard").glob("sheet_*.png"))) if (ep / "storyboard").exists() else 0
    clips = len(list((ep / "clips").glob("*.mp4"))) if (ep / "clips").exists() else 0
    return {
        "phase": phase,
        "invalidates": stale,
        "artifacts_rebuilt": [S.PHASE_ARTIFACT[p] for p in stale],
        "generated_discarded": {"sheets": sheets, "clips": clips},
        "spend_at_risk_usd": round(sheets * COST["sheet_2k_usd"], 2),
        "spend_note": ("clip cost unverified — no real Seedance call has run"
                       if clips else ""),
    }


@router.post("/episodes/{episode_id}/reopen")
def reopen(episode_id: str, body: Reopen):
    t = _thread(episode_id)
    res = _guard(lambda: S.reopen(t, body.phase, body.reason))
    return {**res, "overview": S.overview(t)}


# ── Cost preview (the money rule, made visible) ──────────────────

@router.get("/episodes/{episode_id}/cost-preview")
def cost_preview(episode_id: str):
    """What approving THIS gate will spend. Returned so a UI can show it before
    the click. `verified: false` means we are guessing and must say so."""
    t = _thread(episode_id)
    phase = t.phase
    if phase == "vision":
        sp = t.artifact_path("script")
        n = 0
        if sp.exists():
            n = len(json.loads(sp.read_text(encoding="utf-8")).get("segments", []))
        n = n or 2
        return {"phase": phase, "units": n, "unit": "storyboard sheet (2K)",
                "estimate_usd": round(n * COST["sheet_2k_usd"], 2), "verified": True}
    if phase == "shoot":
        return {"phase": phase, "units": 2, "unit": "Seedance clip (15s)",
                "estimate_usd": None, "verified": False,
                "note": "per-clip price is unknown — no real Seedance call has ever run"}
    return {"phase": phase, "units": 0, "unit": None, "estimate_usd": 0.0,
            "verified": True}


# ── The Showrunner's front door ──────────────────────────────────

@router.get("/next-lesson")
def next_lesson():
    """Everything the Idea phase opens with: the next module, its untaught atoms,
    the rotation-derived lead recommendation, and the level's ceilings."""
    nb = st.next_module_brief()
    if not nb:
        return {"complete": True}
    rot = st.rotation_report()
    return {
        "complete": False,
        "module": {k: nb["module"][k] for k in ("id", "level", "title",
                                               "grammar_cluster", "functions")},
        "untaught_atoms": nb["untaught_atoms"],
        "taught_atoms": [a["id"] for a in nb["taught_atoms"]],
        "guardrails": nb["guardrails"],
        "lead_recommendation": {
            "character": rot["least_recent_first"][0] if rot["least_recent_first"] else None,
            "reason": "coldest in rotation",
            "appearances": rot["counts"],
        },
    }


@router.get("/curriculum")
def curriculum():
    """The series map: every atom with its taught state, for the Home screen."""
    cur = ctx.curriculum()
    taught = st.taught_atoms()
    status = st.curriculum_status()
    return {
        "totals": cur["meta"]["totals"],
        "taught_count": status["taught_atoms"],
        "next_module": status["next_module"],
        "modules": [
            {"id": m["id"], "level": m["level"], "title": m["title"],
             "atoms": [{"id": a["id"], "title": a["title"], "synthese": a["synthese"],
                        "taught": a["id"] in taught} for a in m["atoms"]]}
            for m in cur["modules"]
        ],
    }


# ── Seed bank (the anti-slop lever for Draft mode) ───────────────

class Seed(BaseModel):
    text: str


@router.get("/seeds")
def list_seeds():
    rows = st.list_entities("direction")
    seeds = [r for r in rows if (r.get("data") or {}).get("kind") == "seed"]
    return [{"key": r["entity_key"], "text": r["data"].get("text", ""),
             "used_by": r["data"].get("used_by"), "used": bool(r["data"].get("used_by"))}
            for r in seeds]


@router.post("/seeds")
def add_seed(body: Seed):
    if not body.text.strip():
        raise HTTPException(400, "a seed needs text")
    import uuid
    key = f"seed_{uuid.uuid4().hex[:8]}"
    st.put_entity("direction", key, {"kind": "seed", "text": body.text.strip(),
                                     "used_by": None})
    return {"key": key, "text": body.text.strip()}


@router.post("/seeds/{key}/consume")
def consume_seed(key: str, episode_id: str):
    row = st.get_entity("direction", key)
    if not row:
        raise HTTPException(404, "no such seed")
    data = {**row["data"], "used_by": episode_id}
    st.put_entity("direction", key, data)
    return {"key": key, "used_by": episode_id}


# ── Lessons — the layer above episodes (PIPELINE §3.0) ───────────

class NewPlan(BaseModel):
    module_id: str


class SavePlan(BaseModel):
    lesson: dict


class Replan(BaseModel):
    blocks: list
    deferred_atoms: list | None = None
    deferred_reason: str = ""
    confirmed: bool = False


def _lguard(fn):
    try:
        return fn()
    except L.LessonError as e:
        raise HTTPException(409, str(e))


@router.get("/lessons")
def list_lessons():
    return L.list_plans()


@router.post("/lessons")
def create_lesson(body: NewPlan):
    """Scaffold a plan from the curriculum. Deliberately INVALID until planned —
    it cannot be approved before anyone has decided anything."""
    return _lguard(lambda: L.create(body.module_id))


@router.get("/lessons/{module_id}")
def get_lesson(module_id: str):
    lesson = _lguard(lambda: L.load(module_id))
    return {"lesson": lesson, "validation": L.validate(lesson),
            "progress": L.progress(module_id)}


@router.put("/lessons/{module_id}")
def save_lesson(module_id: str, body: SavePlan):
    if body.lesson.get("module_id") != module_id:
        raise HTTPException(400, "module_id mismatch")
    L.save(body.lesson)
    return {"validation": L.validate(body.lesson), "progress": L.progress(module_id)}


@router.post("/lessons/{module_id}/approve")
def approve_lesson_plan(module_id: str):
    """The Plan gate. Blocks on the coverage invariant — nothing is silently lost."""
    return _lguard(lambda: L.approve_plan(module_id))


@router.get("/lessons/{module_id}/progress")
def lesson_progress(module_id: str):
    """'2 of 3 episodes' — the number that did not exist before the lesson layer."""
    return _lguard(lambda: L.progress(module_id))


@router.post("/lessons/{module_id}/replan-preview")
def replan_preview(module_id: str, body: Replan):
    """A READ. Shows the blast radius BEFORE the change — including that a made
    episode is never deleted or overwritten by a re-plan."""
    return _lguard(lambda: L.replan_preview(
        module_id, body.blocks, deferred_atoms=body.deferred_atoms,
        deferred_reason=body.deferred_reason or None))


@router.post("/lessons/{module_id}/replan")
def replan(module_id: str, body: Replan):
    if not body.confirmed:
        raise HTTPException(409, "a re-plan must be confirmed after seeing the preview")
    return _lguard(lambda: L.replan(module_id, body.blocks,
                                    deferred_atoms=body.deferred_atoms,
                                    deferred_reason=body.deferred_reason, confirmed=True))


@router.get("/lessons/{module_id}/context")
def lesson_context(module_id: str, episode_no: int = 0):
    """What an episode's agents actually receive from the lesson: the plan, and
    sibling episodes as summaries (never transcripts)."""
    def _sp(episode_id: str):
        p = S.EPISODES / episode_id / "screenplay.json"
        return json.loads(p.read_text(encoding="utf-8")) if p.exists() else None
    plan = _lguard(lambda: L.plan_block(module_id))
    sibs = L.siblings_block(module_id, episode_no, _sp) if episode_no else ""
    return {"plan_block": plan, "siblings_block": sibs}


# ── Health ───────────────────────────────────────────────────────

@router.get("/health")
def health():
    """One call the UI can use to know what is actually wired."""
    tables = st.tables_ready()
    return {
        "canon_files": len(ctx._canon()),
        "curriculum_atoms": ctx.curriculum()["meta"]["totals"]["atoms"],
        "state_tables": tables,
        "state_ready": all(tables.values()),
        "phases": S.PHASE_ORDER,
        "modes": [S.CO_CREATE, S.DRAFT],
        "lessons_planned": len(L.list_plans()),
        "agents_built": False,   # Phase 3
        "fal_key": bool(__import__("os").environ.get("FAL_KEY")),
    }

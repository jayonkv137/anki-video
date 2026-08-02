"""Command Center (M7) — dashboard + control API over the pipeline ledger.

Run:  .venv/bin/python -m uvicorn dashboard.app:app --port 8787 --app-dir <repo>
The Supabase ledger IS the backend; this app is a thin read/control layer:
  - runs list + per-run stage timeline (tokens/cost/status)
  - artifact viewer (options/story/screenplay/prompts/episode/final video)
  - Gate A in the UI: read the 3 options, choose with a steering note
  - New Run with word selection + "today's idea" director note (idea injection)
"""

import json
import os
import subprocess
import sys
from pathlib import Path

from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, HTMLResponse
from pydantic import BaseModel

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from pipeline import ledger  # noqa: E402  (loads .env itself)
from pipeline import stereotypes  # noqa: E402

app = FastAPI(title="Stereotypical German — Command Center")
STATIC = Path(__file__).resolve().parent / "static"
PYTHON = str(REPO / ".venv" / "bin" / "python")
LOGS = REPO / "dashboard" / "logs"
LOGS.mkdir(parents=True, exist_ok=True)
RESOURCES = REPO / "resources"
app.mount("/resources", StaticFiles(directory=RESOURCES), name="resources")


def _ep_dir(run: dict) -> Path | None:
    pos = run.get("word_positions") or []
    if not pos:
        return None
    return REPO / "output" / "episodes" / f"ep_{pos[0]}-{pos[-1]}"


def _spawn(args: list[str], tag: str):
    """Fire-and-forget pipeline subprocess; ledger is the progress channel."""
    log = open(LOGS / f"{tag}.log", "ab")
    subprocess.Popen([PYTHON, "-m", "pipeline", *args], cwd=REPO,
                     stdout=log, stderr=subprocess.STDOUT)


# ── Stereotype API ────────────────────────────────────────────────

@app.get("/api/stereotypes/options")
def get_stereotype_options(n: int = 3, category: str | None = None):
    return stereotypes.pick_options(n=n, category=category)


@app.get("/api/stereotypes/all")
def get_all_stereotypes():
    return stereotypes.all_stereotypes()


@app.get("/api/stereotypes/summary")
def get_stereotype_summary():
    return stereotypes.coverage_summary()


# ── Removed 2026-08-02 (Phase 1 quarantine) ─────────────────────────────
# `/api/co-creation/align` and `/api/co-creation/diverge` are deleted. They were
# dead (index.html never called them) and each carried ~80 lines of HARDCODED
# creative content — invented locations, lessons and target lines returned
# silently whenever the model call failed. That violates PIPELINE §3.3 ("it
# extracts; it does not invent") and could put fabricated pedagogy into a brief.
# Recover with: git show v3-wizard-archive:dashboard/app.py

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatReq(BaseModel):
    messages: list[ChatMessage]
    stereotype: dict
    cast: dict
    seed: str = ""
    cefr: str = "A1"

@app.post("/api/co-creation/chat")
def api_chat(req: ChatReq):
    """The co-creation chat — now driven by **skill-1-story-strategist** (the disciplined Socratic
    partner) instead of the old thin inline 'Co-Director' prompt. Full context (mission, stereotype,
    cast, bible, seed, CEFR, series memory) is server-injected each turn (invisible in the bubbles);
    the skill enforces the pipeline constraints + pedagogy, moves through the Hook→Arc→Beats→Verify
    phase spine, and signals `ready_to_commit`. The human's 'Lock Brief' click still runs
    /api/v3/commit (the deterministic extraction). See DESIGN_story_ideation_and_overseer.md Part A."""
    google_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
    _empty_widget = {"type": "none", "title": "", "options": []}
    if not google_key:
        return {"reply_text": "API Key missing for Live Chat.", "phase": "hook",
                "ready_to_commit": False, "widget": _empty_widget}
    try:
        from pipeline.stages import _call_gemini, _load_skill, _schema, _arr, STR, BOOL
        rcp = _get_rcp()

        OPTION_ITEM_SCHEMA = _schema(id=STR, label=STR, title=STR, desc=STR)
        WIDGET_SCHEMA = _schema(type=STR, title=STR, options=_arr(OPTION_ITEM_SCHEMA))
        CHAT_RESPONSE_SCHEMA = _schema(reply_text=STR, phase=STR, ready_to_commit=BOOL,
                                       widget=WIDGET_SCHEMA)

        skill = _load_skill("skill-1-story-strategist.md")
        skill = (skill
                 .replace("{{STEREOTYPE_JSON}}", json.dumps(req.stereotype, ensure_ascii=False))
                 .replace("{{CAST_JSON}}", json.dumps(req.cast, ensure_ascii=False))
                 .replace("{{CHARACTER_BIBLE}}", rcp.character_bible)
                 .replace("{{SEED}}", req.seed or "(none yet — draw the spark out of the human)")
                 .replace("{{CEFR_LEVEL}}", req.cefr)
                 .replace("{{EPISODE_LOG}}", rcp.series_digest or "(no prior episodes)"))
        system = rcp.for_story_stage() + "\n\n" + skill

        if not req.messages:
            user_prompt = ("Open the co-creation session: warmly set the creative frame for this "
                           "stereotype + cast, then start the HOOK phase — end with your one "
                           "targeted question (offer an option-widget if it helps).")
        else:
            user_prompt = "\n".join(
                f"{'Human' if m.role == 'user' else 'Strategist'}: {m.content}" for m in req.messages)

        parsed, _, _ = _call_gemini(system, user_prompt, CHAT_RESPONSE_SCHEMA, temperature=0.8)
        parsed.setdefault("phase", "hook")
        parsed.setdefault("ready_to_commit", False)
        parsed.setdefault("widget", _empty_widget)
        return parsed
    except Exception as e:
        return {"reply_text": f"⚠️ Error: {e}", "phase": "hook",
                "ready_to_commit": False, "widget": _empty_widget}

class ChatExtractReq(BaseModel):
    messages: list[ChatMessage]
    stereotype: dict
    cast: dict

@app.post("/api/co-creation/chat/extract")
def api_chat_extract(req: ChatExtractReq):
    google_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
    if not google_key:
        raise HTTPException(500, "API key missing")

    try:
        from pipeline.stages import _call_gemini, _schema, LOCATION_OPTION, LESSON_OPTION, ANGLE_SCHEMA
        EXTRACT_SCHEMA = _schema(
            location=LOCATION_OPTION,
            lesson=LESSON_OPTION,
            angle=ANGLE_SCHEMA
        )
        
        system = "You are a precise JSON extractor. Read the chat history and extract the finalized Location, Lesson, and Comedic Angle that the user and AI agreed upon. YOU MUST USE THE PROVIDED JSON SCHEMA."
        user = json.dumps([{"role": m.role, "content": m.content} for m in req.messages])
        
        parsed, _, _ = _call_gemini(system, f"Extract the decisions into JSON from this chat:\\n{user}", EXTRACT_SCHEMA, temperature=0.1)
        return parsed
    except Exception as e:
        raise HTTPException(500, f"Failed to extract decisions: {e}")


# ── Read API ─────────────────────────────────────────────────────

@app.get("/api/runs")
def list_runs():
    return ledger._get("runs", {"select": "*", "order": "started_at.desc", "limit": "50"})


@app.get("/api/runs/{run_id}")
def get_run(run_id: str):
    run = ledger.get_run(run_id)
    if not run:
        raise HTTPException(404, "run not found")
    run["events"] = ledger.get_events(run_id)
    ep = _ep_dir(run)
    run["episode_dir"] = ep.name if ep else None
    return run


@app.get("/api/runs/{run_id}/artifacts")
def get_artifacts(run_id: str):
    run = ledger.get_run(run_id)
    if not run:
        raise HTTPException(404, "run not found")
    ep = _ep_dir(run)
    out: dict = {"episode_dir": ep.name if ep else None}
    if not ep or not ep.exists():
        return out

    def read(name, as_json=False):
        p = ep / name
        if not p.exists():
            return None
        try:
            t = p.read_text(encoding="utf-8")
            return json.loads(t) if as_json else t
        except Exception:
            return None

    out["options_md"] = read("options.md")
    out["options"] = read("options.json", as_json=True)
    out["align"] = read("align.json", as_json=True)
    out["diverge"] = read("diverge.json", as_json=True)
    out["brief"] = read("brief.json", as_json=True)
    out["story"] = read("story.json", as_json=True)
    out["screenplay"] = read("screenplay.json", as_json=True)
    out["storyboard"] = read("storyboard.json", as_json=True)
    out["episode_md"] = read("episode.md")
    out["caption_md"] = read("caption.md")
    pdir = ep / "prompts"
    out["prompt_files"] = sorted(p.name for p in pdir.glob("*.json")) if pdir.exists() else []
    out["refs_manifest"] = (json.loads((pdir / "refs_manifest.json").read_text(encoding="utf-8"))
                            if (pdir / "refs_manifest.json").exists() else None)
    clips = ep / "clips"
    out["clips"] = sorted(c.name for c in clips.glob("*.mp4")) if clips.exists() else []
    out["final_video"] = (ep / "final.mp4").exists()

    return out


@app.get("/api/runs/{run_id}/prompt/{fname}")
def get_prompt_file(run_id: str, fname: str):
    run = ledger.get_run(run_id)
    ep = _ep_dir(run) if run else None
    if not ep:
        raise HTTPException(404, "run not found")
    p = (ep / "prompts" / fname).resolve()
    if not str(p).startswith(str(ep.resolve())) or not p.exists():
        raise HTTPException(404, "no such prompt file")
    return json.loads(p.read_text(encoding="utf-8"))


@app.get("/api/runs/{run_id}/video")
def get_video(run_id: str):
    run = ledger.get_run(run_id)
    ep = _ep_dir(run) if run else None
    f = (ep / "final.mp4") if ep else None
    if not f or not f.exists():
        raise HTTPException(404, "no final video yet")
    return FileResponse(f, media_type="video/mp4")


@app.get("/api/episodes")
def list_episodes():
    return ledger._get("episodes", {"select": "*", "order": "created_at.desc", "limit": "50"})


@app.get("/api/stats")
def stats():
    runs = ledger._get("runs", {"select": "status,cost_cents", "limit": "500"})
    return {
        "runs": len(runs),
        "completed": sum(1 for r in runs if r.get("status") == "completed"),
        "awaiting": sum(1 for r in runs if r.get("status") == "awaiting_choice"),
        "cost_cents": sum(r.get("cost_cents") or 0 for r in runs),
    }


# ── Control API ──────────────────────────────────────────────────

class NewRun(BaseModel):
    mode: str = "random"          # random | start | positions
    start: int | None = None
    positions: str | None = None  # comma-separated
    note: str = ""                # "today's idea" — director note


@app.post("/api/runs")
def start_run(body: NewRun):
    args = ["run"]
    if body.mode == "random":
        args.append("--random")
    elif body.mode == "start" and body.start:
        args += ["--start", str(body.start)]
    elif body.mode == "positions" and body.positions:
        args += ["--positions", body.positions]
    else:
        raise HTTPException(400, "invalid mode/params")
    if body.note.strip():
        args += ["--note", body.note.strip()]
    _spawn(args, "run")
    return {"status": "started", "args": args}


class Choice(BaseModel):
    choice: int
    note: str = ""


@app.post("/api/runs/{run_id}/choose")
def choose(run_id: str, body: Choice):
    latest = ledger.get_latest_run()
    if not latest or latest["id"] != run_id:
        raise HTTPException(409, "this run is not the latest — CLI choose targets the latest run")
    if latest.get("status") != "awaiting_choice":
        raise HTTPException(409, f"run is '{latest.get('status')}', not awaiting_choice")
    if body.choice not in (1, 2, 3):
        raise HTTPException(400, "choice must be 1..3")
    args = ["choose", str(body.choice)]
    if body.note.strip():
        args += ["--note", body.note.strip()]
    _spawn(args, "choose")
    return {"status": "started", "choice": body.choice}


@app.post("/api/runs/{run_id}/caption")
def gen_caption(run_id: str):
    run = ledger.get_run(run_id)
    if not run:
        raise HTTPException(404, "run not found")
    ep = _ep_dir(run)
    if not ep or not (ep / "story.json").exists():
        raise HTTPException(409, "no story yet — pass Gate A first")
    _spawn(["caption", run_id], "caption")
    return {"status": "started"}


class Gen(BaseModel):
    provider: str = "mock"


@app.post("/api/runs/{run_id}/generate")
def generate_clips(run_id: str, body: Gen):
    run = ledger.get_run(run_id)
    ep = _ep_dir(run) if run else None
    if not ep or not (ep / "screenplay.json").exists():
        raise HTTPException(409, "no screenplay yet")
    _spawn(["generate", run_id, "--provider", body.provider], "generate")
    return {"status": "started", "provider": body.provider}


@app.post("/api/runs/{run_id}/autopilot")
def autopilot(run_id: str, body: Gen):
    run = ledger.get_run(run_id)
    ep = _ep_dir(run) if run else None
    if not ep or not (ep / "screenplay.json").exists():
        raise HTTPException(409, "no screenplay yet")
    _spawn(["autopilot", run_id, "--provider", body.provider], "autopilot")
    return {"status": "started", "provider": body.provider}


@app.post("/api/runs/{run_id}/assemble")
def assemble(run_id: str):
    run = ledger.get_run(run_id)
    ep = _ep_dir(run) if run else None
    if not ep:
        raise HTTPException(404, "run not found")
    clips = ep / "clips"
    n = len(list(clips.glob("*.mp4"))) if clips.exists() else 0
    if n == 0:
        raise HTTPException(409, "no clips uploaded yet")
    _spawn(["assemble", ep.name], "assemble")
    return {"status": "started", "clips": n}


@app.post("/api/runs/{run_id}/clips/{scene}")
async def upload_clip(run_id: str, scene: int, file: UploadFile = File(...)):
    run = ledger.get_run(run_id)
    ep = _ep_dir(run) if run else None
    if not ep:
        raise HTTPException(404, "run not found")
    if not 1 <= scene <= 20:
        raise HTTPException(400, "scene out of range")
    clips = ep / "clips"
    clips.mkdir(parents=True, exist_ok=True)
    dest = clips / f"scene_{scene:02d}.mp4"
    dest.write_bytes(await file.read())
    return {"status": "saved", "file": dest.name}


# ── V3 pipeline API (co-creation → brief → screenplay → storyboard → video) ──
# Human-in-the-loop, manual-generation flow: each stage runs the real skill via Gemini,
# persists an artifact, and returns prompts; the human generates images/video externally
# and uploads them back. State carries by run_id (ep dir = ep_<run_id[:8]>).

_RCP_CACHE = None


def _get_rcp():
    global _RCP_CACHE
    if _RCP_CACHE is None:
        from pipeline.rcp import RunContextPack
        _RCP_CACHE = RunContextPack()
    return _RCP_CACHE


def _v3_ep(run_id: str) -> Path:
    return REPO / "output" / "episodes" / f"ep_{run_id[:8]}"


def _gemini_skill(skill_name: str, replacements: dict, schema: dict,
                  stage: str = "story", temperature=None) -> dict:
    """Run one skill through Gemini with the right RCP context (mirrors stages._call)."""
    from pipeline.stages import _call_gemini, _load_skill
    skill = _load_skill(skill_name)
    for k, v in replacements.items():
        skill = skill.replace(k, v)
    rcp = _get_rcp()
    ctx = {"story": rcp.for_story_stage, "screenplay": rcp.for_screenplay_stage,
           "prompt": rcp.for_prompt_stage}[stage]()
    parsed, _, _ = _call_gemini(ctx + "\n\n" + skill, "Produce the required JSON now.", schema, temperature)
    return parsed


class CommitReq(BaseModel):
    messages: list[ChatMessage]
    stereotype: dict
    cast: dict
    seed: str = ""
    cefr: str = "A1"
    run_id: str | None = None


@app.post("/api/v3/commit")
def v3_commit(req: CommitReq):
    """Lock the co-creation chat → full Story Brief → persist a run + brief.json + mark covered."""
    from pipeline.stages import _call_gemini, STORY_BRIEF_SCHEMA
    from pipeline import stereotypes as stlib
    rcp = _get_rcp()
    chat = "\n".join(f"{'User' if m.role == 'user' else 'Co-Director'}: {m.content}" for m in req.messages)
    
    st_title = req.stereotype.get("name_de", "Stereotype")
    main_char = req.cast.get("main", "Rolf die Wurst")
    side_char = req.cast.get("side", "")
    
    system = (
        rcp.for_story_stage() + "\n\n"
        "You are the COMMIT step of the co-creation. Read the CONTEXT and the CHAT and output the "
        "LOCKED Story Brief JSON — fill EVERY field faithfully from the discussion.\n\n"
        "CRITICAL FIELD INSTRUCTIONS:\n"
        f"- `title_de`: Set to '{st_title}'.\n"
        f"- `stereotype_id`: Set to '{req.stereotype.get('id', '')}'.\n"
        f"- `stereotype_name`: Set to '{st_title}'.\n"
        f"- `category`: Set to '{req.stereotype.get('category', 'General')}'.\n"
        f"- `cefr_level`: Set to '{req.cefr}'.\n"
        f"- `cast`: `main` MUST BE '{main_char}', `side` MUST BE '{side_char}'.\n"
        "- `location`: Set to the exact script location agreed upon in the chat (e.g. EXT. RED BICYCLE PATH - DAY).\n"
        "- `comedic_angle`: Set to the comedic angle discussed.\n"
        "- `lesson`: Fill `particle` or `structure`, `pragmatic_function`, and `pop_up_grammar`.\n"
        "- `target_line`: Fill `speaker` (the character), `german` (the sentence), `english`, and `why`.\n"
        "- `escalation_beats`: Ordered list of 4-5 visual beats (base reality → first unusual thing → escalation).\n"
        "- `button`: The final comedic payoff beat.\n"
        "- `banned_terms`: List of banned terms (stereotype name + synonyms + pedagogical words).\n\n"
        f"CONTEXT: stereotype={json.dumps(req.stereotype, ensure_ascii=False)} · "
        f"cast={json.dumps(req.cast, ensure_ascii=False)} · cefr={req.cefr} · seed={req.seed!r}\n\n"
        f"CHAT:\n{chat}"
    )
    brief, _, _ = _call_gemini(system, "Produce the locked Story Brief JSON now.",
                               STORY_BRIEF_SCHEMA, temperature=0.3)
    
    # No fabrication. A brief with invented fields is worse than no brief:
    # it looks locked, feeds the screenplay, and silently teaches the wrong
    # lesson. Missing essentials fail loudly instead (PIPELINE §3.3).
    missing = [f for f in ("title_de", "cefr_level", "location", "premise", "button")
               if not (brief.get(f) or "").strip()]
    if not isinstance(brief.get("cast"), dict) or not (brief["cast"].get("main") or "").strip():
        missing.append("cast.main")
    lesson = brief.get("lesson") if isinstance(brief.get("lesson"), dict) else {}
    if not ((lesson.get("particle") or "").strip() or (lesson.get("structure") or "").strip()):
        missing.append("lesson.particle|structure")
    tl = brief.get("target_line") if isinstance(brief.get("target_line"), dict) else {}
    if not (tl.get("german") or "").strip():
        missing.append("target_line.german")
    if missing:
        raise HTTPException(422, "The brief is incomplete — these came back empty: "
                            + ", ".join(missing)
                            + ". Nothing was invented to fill them; continue the chat "
                              "until they are decided, then lock again.")

    # Determine run_id (reuse provided run_id or search existing stereotype run to prevent duplicates)
    run_id = req.run_id
    if run_id and _v3_ep(run_id).exists():
        pass  # reuse exact run_id
    else:
        sid = req.stereotype.get("id") or st_title
        runs_dir = Path("output/episodes")
        existing_run_id = None
        if runs_dir.exists():
            for d in runs_dir.iterdir():
                if d.is_dir() and (d / "brief.json").exists():
                    try:
                        b = json.loads((d / "brief.json").read_text(encoding="utf-8"), strict=False)
                        if b.get("stereotype_name") == st_title or b.get("title_de") == st_title or (sid and b.get("stereotype_id") == sid):
                            existing_run_id = d.name.replace("ep_", "")
                            break
                    except Exception:
                        pass
        if existing_run_id:
            run_id = existing_run_id
        else:
            try:
                run = ledger.create_run(word_positions=[], canon_versions=rcp.canon_versions)
                run_id = run["id"]
            except Exception:
                import uuid
                run_id = str(uuid.uuid4())[:8]

    ep = _v3_ep(run_id)
    ep.mkdir(parents=True, exist_ok=True)
    (ep / "brief.json").write_text(json.dumps(brief, ensure_ascii=False, indent=2), encoding="utf-8")
    sid = req.stereotype.get("id")
    if sid:
        try:
            stlib.mark_covered(sid, ep.name)
        except Exception as e:
            print(f"[mark_covered failed: {e}]")
    try:
        ledger.update_run(run_id, stage="brief")
    except Exception as e:
        print(f"[ledger.update_run failed: {e}]")
        
    return {"run_id": run_id, "brief": brief}


@app.get("/api/v3/episodes")
def v3_list_episodes():
    episodes = []
    runs_dir = Path("output/episodes")
    if not runs_dir.exists():
        return []
    for d in sorted(runs_dir.iterdir(), key=lambda p: p.stat().st_mtime, reverse=True):
        if d.is_dir() and (d / "brief.json").exists():
            try:
                b = json.loads((d / "brief.json").read_text(encoding="utf-8"), strict=False)
                episodes.append({
                    "run_id": d.name.replace("ep_", ""),
                    "dir_name": d.name,
                    "title": b.get("title_de") or b.get("stereotype_name") or "Episode",
                    "stereotype": b.get("stereotype_name"),
                    "main_cast": b.get("cast", {}).get("main") if isinstance(b.get("cast"), dict) else "",
                    "has_screenplay": (d / "screenplay.json").exists(),
                    "has_storyboard": (d / "storyboard.json").exists(),
                })
            except Exception:
                pass
    return episodes


@app.get("/api/v3/runs/{run_id}")
def v3_get(run_id: str):
    ep = _v3_ep(run_id)

    def rd(name):
        p = ep / name
        return json.loads(p.read_text(encoding="utf-8")) if p.exists() else None

    sb, clips = ep / "storyboard", ep / "clips"
    return {
        "run_id": run_id,
        "brief": rd("brief.json"),
        "screenplay": rd("screenplay.json"),
        "storyboard": rd("storyboard.json"),
        "prompts": rd("prompts.json"),
        "refs_manifest": rd("prompts/refs_manifest.json"),
        "panels": sorted(p.name for p in sb.glob("*.png")) if sb.exists() else [],
        "clips": sorted(c.name for c in clips.glob("*.mp4")) if clips.exists() else [],
    }


@app.post("/api/v3/runs/{run_id}/screenplay")
def v3_screenplay(run_id: str):
    from pipeline.stages import SCREENPLAY_SCHEMA, validate_screenplay
    ep = _v3_ep(run_id)
    if not (ep / "brief.json").exists():
        raise HTTPException(409, "no brief yet — commit the co-creation first")
    brief = json.loads((ep / "brief.json").read_text(encoding="utf-8"))
    sp = _gemini_skill("skill-2-screenplay-writer.md",
                       {"{{CHARACTER_BIBLE}}": _get_rcp().character_bible,
                        "{{STORY_JSON}}": json.dumps(brief, ensure_ascii=False)},
                       SCREENPLAY_SCHEMA, stage="screenplay")
    (ep / "screenplay.json").write_text(json.dumps(sp, ensure_ascii=False, indent=2), encoding="utf-8")
    try:
        ledger.update_run(run_id, stage="screenplay")
    except Exception as e:
        print(f"[ledger.update_run failed: {e}]")
    return {"screenplay": sp, "problems": validate_screenplay(sp)}


@app.post("/api/v3/runs/{run_id}/storyboard-prompts")
def v3_storyboard(run_id: str):
    from pipeline.stages import STORYBOARD_SCHEMA
    ep = _v3_ep(run_id)
    if not (ep / "screenplay.json").exists():
        raise HTTPException(409, "no screenplay yet")
    sp = json.loads((ep / "screenplay.json").read_text(encoding="utf-8"))
    board = _gemini_skill("skill-2b-storyboard.md",
                          {"{{CHARACTER_BIBLE}}": _get_rcp().character_bible,
                           "{{SCREENPLAY_JSON}}": json.dumps(sp, ensure_ascii=False)},
                          STORYBOARD_SCHEMA, stage="prompt")
    (ep / "storyboard.json").write_text(json.dumps(board, ensure_ascii=False, indent=2), encoding="utf-8")
    try:
        ledger.update_run(run_id, stage="storyboard")
    except Exception as e:
        print(f"[ledger.update_run failed: {e}]")
    return {"storyboard": board}


@app.post("/api/v3/runs/{run_id}/sheet/{seg}")
async def v3_upload_sheet(run_id: str, seg: int, file: UploadFile = File(...)):
    """Human uploads ONE storyboard SHEET for a segment (the multi-panel image generated from
    the skill-2b sheet prompt); we save it and slice it into the per-shot
    panel_s<seg>_<shot>.png files the Seedance step resolves."""
    from pipeline.providers import image as _img
    ep = _v3_ep(run_id)
    sb = ep / "storyboard"
    sb.mkdir(parents=True, exist_ok=True)
    sheet_path = sb / f"sheet_s{seg:02d}.png"
    sheet_path.write_bytes(await file.read())

    # resolve this segment's shot list (storyboard.json first, else the screenplay)
    shot_numbers = []
    if (ep / "storyboard.json").exists():
        board = json.loads((ep / "storyboard.json").read_text(encoding="utf-8"))
        for s in board.get("sheets", []):
            if s.get("segment_number") == seg:
                shot_numbers = s.get("shot_numbers") or []
                break
    if not shot_numbers and (ep / "screenplay.json").exists():
        sp = json.loads((ep / "screenplay.json").read_text(encoding="utf-8"))
        for sg in sp.get("segments", []):
            if sg.get("segment_number") == seg:
                shot_numbers = [sh.get("shot_number") for sh in sg.get("shots", [])]
                break
    shot_numbers = shot_numbers or [1]
    rows, cols, _, _ = _img.sheet_grid(len(shot_numbers))
    panels = _img.slice_sheet(sheet_path, rows, cols, shot_numbers, sb, seg)
    return {"status": "saved", "sheet": sheet_path.name, "panels": [p.name for p in panels]}


@app.post("/api/v3/runs/{run_id}/panels/{seg}/{shot}")
async def v3_upload_panel(run_id: str, seg: int, shot: int, file: UploadFile = File(...)):
    ep = _v3_ep(run_id)
    sb = ep / "storyboard"
    sb.mkdir(parents=True, exist_ok=True)
    dest = sb / f"panel_s{seg:02d}_{shot:02d}.png"
    dest.write_bytes(await file.read())
    return {"status": "saved", "file": dest.name}


@app.post("/api/v3/runs/{run_id}/video-prompts")
def v3_video_prompts(run_id: str):
    from pipeline.stages import PROMPTS_SCHEMA, build_refs_manifest
    ep = _v3_ep(run_id)
    if not (ep / "screenplay.json").exists():
        raise HTTPException(409, "no screenplay yet")
    sp = json.loads((ep / "screenplay.json").read_text(encoding="utf-8"))
    prompts = _gemini_skill("skill-3-prompt-writer.md",
                            {"{{SCREENPLAY_JSON}}": json.dumps(sp, ensure_ascii=False)},
                            PROMPTS_SCHEMA, stage="prompt")
    (ep / "prompts.json").write_text(json.dumps(prompts, ensure_ascii=False, indent=2), encoding="utf-8")
    (ep / "prompts").mkdir(parents=True, exist_ok=True)
    manifest = build_refs_manifest(prompts, run_id, ep)
    (ep / "prompts" / "refs_manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    try:
        ledger.update_run(run_id, stage="prompts")
    except Exception as e:
        print(f"[ledger.update_run failed: {e}]")
    return {"prompts": prompts, "refs_manifest": manifest}


@app.post("/api/v3/runs/{run_id}/clips/{seg}")
async def v3_upload_clip(run_id: str, seg: int, file: UploadFile = File(...)):
    ep = _v3_ep(run_id)
    clips = ep / "clips"
    clips.mkdir(parents=True, exist_ok=True)
    dest = clips / f"segment_{seg:02d}.mp4"
    dest.write_bytes(await file.read())
    return {"status": "saved", "file": dest.name}


# ── Assembly & Subtitles (light path: ffmpeg concat + ASS burn) ──────────────

def _clip_paths(ep: Path) -> list:
    cdir = ep / "clips"
    return sorted(cdir.glob("segment_*.mp4")) if cdir.exists() else []


class SubtitlesSaveReq(BaseModel):
    state: dict


@app.post("/api/v3/runs/{run_id}/assemble")
def v3_assemble(run_id: str):
    """Concat the uploaded segment clips → assembly/joined.mp4, then build subtitles.json from the
    screenplay (word-level, colour-coded der/die/das/grammar) using the REAL clip durations."""
    from pipeline import subtitles as subs
    ep = _v3_ep(run_id)
    clips = _clip_paths(ep)
    if not clips:
        raise HTTPException(409, "no segment clips uploaded yet (upload them in the Video step)")
    if not (ep / "screenplay.json").exists():
        raise HTTPException(409, "no screenplay")
    sp = json.loads((ep / "screenplay.json").read_text(encoding="utf-8"))
    asm = ep / "assembly"
    asm.mkdir(parents=True, exist_ok=True)
    subs.concat_clips(clips, asm / "joined.mp4")
    durs = [subs.clip_duration(c) for c in clips]
    state = subs.build_subtitle_state(sp, durs)
    (ep / "subtitles.json").write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")
    try:
        ledger.update_run(run_id, stage="assemble")
    except Exception:
        pass
    return {"composition": state["composition"], "subtitles": state["subtitles"],
            "colors": state["colors"], "layout": state["layout"], "has_joined": True}


@app.get("/api/v3/runs/{run_id}/subtitles")
def v3_get_subtitles(run_id: str):
    ep = _v3_ep(run_id)
    p = ep / "subtitles.json"
    if not p.exists():
        raise HTTPException(404, "no subtitles yet — assemble first")
    return json.loads(p.read_text(encoding="utf-8"))


@app.post("/api/v3/runs/{run_id}/subtitles")
def v3_save_subtitles(run_id: str, req: SubtitlesSaveReq):
    """Persist the edited subtitle STATE (from the cue editor or the Director)."""
    ep = _v3_ep(run_id)
    (ep / "subtitles.json").write_text(json.dumps(req.state, ensure_ascii=False, indent=2), encoding="utf-8")
    return {"status": "saved", "cues": len(req.state.get("subtitles", []))}


@app.post("/api/v3/runs/{run_id}/export")
def v3_export(run_id: str):
    """Burn the current subtitles.json onto joined.mp4 → assembly/final.mp4 (libass)."""
    from pipeline import subtitles as subs
    ep = _v3_ep(run_id)
    joined = ep / "assembly" / "joined.mp4"
    if not joined.exists():
        raise HTTPException(409, "assemble first")
    state = json.loads((ep / "subtitles.json").read_text(encoding="utf-8"))
    subs.burn(joined, state, ep / "assembly" / "final.mp4")
    return {"status": "exported", "final": "final.mp4"}


@app.get("/api/v3/runs/{run_id}/video/{which}")
def v3_video(run_id: str, which: str):
    ep = _v3_ep(run_id)
    name = {"joined": "joined.mp4", "final": "final.mp4"}.get(which)
    if not name:
        raise HTTPException(404, "unknown video")
    f = ep / "assembly" / name
    if not f.exists():
        raise HTTPException(404, f"{name} not generated yet")
    return FileResponse(f, media_type="video/mp4")


@app.post("/api/v3/runs/{run_id}/mock-clips")
def v3_mock_clips(run_id: str):
    """Dev/demo: synthesize mock segment clips at the screenplay durations (no FAL_KEY) so the
    assembly → subtitles → export flow runs end-to-end. Overwrites existing clips."""
    from pipeline import subtitles as subs
    ep = _v3_ep(run_id)
    if not (ep / "screenplay.json").exists():
        raise HTTPException(409, "no screenplay")
    sp = json.loads((ep / "screenplay.json").read_text(encoding="utf-8"))
    cdir = ep / "clips"
    cdir.mkdir(parents=True, exist_ok=True)
    made = []
    for i, seg in enumerate(sp.get("segments", [])):
        n = int(seg.get("segment_number"))
        dur = seg.get("duration_s", 15) or 15
        subs.mock_clip(cdir / f"segment_{n:02d}.mp4", dur, f"SEGMENT {n}", idx=i)
        made.append(f"segment_{n:02d}.mp4")
    return {"status": "created", "clips": made}


# ── Overseer ("Director") — the always-present editor over a run's artifacts ──
# propose (plan) → human confirms → apply (deterministic edits + targeted recompiles).

class OverseerPlanReq(BaseModel):
    run_id: str
    instruction: str
    step: str = ""


class OverseerApplyReq(BaseModel):
    run_id: str
    operations: list[dict]


@app.post("/api/overseer/plan")
def overseer_plan(req: OverseerPlanReq):
    """Propose a typed edit plan (+ the recompile set) for the human to confirm. Applies nothing."""
    from pipeline import overseer
    if not _v3_ep(req.run_id).exists():
        raise HTTPException(404, "no such run — lock a brief first")
    try:
        return overseer.plan(req.run_id, req.instruction, req.step, _get_rcp())
    except Exception as e:
        return {"reply": f"⚠️ Director error: {e}", "operations": [],
                "needs_confirmation": False, "recompile": []}


@app.post("/api/overseer/apply")
def overseer_apply(req: OverseerApplyReq):
    """Execute the confirmed operations + run the targeted downstream recompiles."""
    from pipeline import overseer
    if not _v3_ep(req.run_id).exists():
        raise HTTPException(404, "no such run")
    return overseer.apply(req.run_id, req.operations, _get_rcp())


@app.get("/")
def index():
    return HTMLResponse((STATIC / "index.html").read_text(encoding="utf-8"))

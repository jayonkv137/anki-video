"""Command Center (M7) — dashboard + control API over the pipeline ledger.

Run:  .venv/bin/python -m uvicorn dashboard.app:app --port 8787 --app-dir <repo>
The Supabase ledger IS the backend; this app is a thin read/control layer:
  - runs list + per-run stage timeline (tokens/cost/status)
  - artifact viewer (options/story/screenplay/prompts/episode/final video)
  - Gate A in the UI: read the 3 options, choose with a steering note
  - New Run with word selection + "today's idea" director note (idea injection)
"""

import json
import subprocess
import sys
from pathlib import Path

from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.responses import FileResponse, HTMLResponse
from pydantic import BaseModel

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from pipeline import ledger  # noqa: E402  (loads .env itself)

app = FastAPI(title="Stereotypical German — Command Center")
STATIC = Path(__file__).resolve().parent / "static"
PYTHON = str(REPO / ".venv" / "bin" / "python")
LOGS = REPO / "dashboard" / "logs"
LOGS.mkdir(parents=True, exist_ok=True)


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
    out["story"] = read("story.json", as_json=True)
    out["screenplay"] = read("screenplay.json", as_json=True)
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


@app.get("/")
def index():
    return HTMLResponse((STATIC / "index.html").read_text(encoding="utf-8"))

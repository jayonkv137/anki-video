"""Assembly (M5) — stitch scene clips into one subtitled 9:16 episode video.

Convention: generated clips live at <ep_dir>/clips/scene_NN.mp4 (one per scene,
any codec/size — they get normalized). Subtitles are built from screenplay.json
dialogue (DE primary + EN italic) and distributed across each scene's real clip
duration. Optional master audio track replaces clip audio entirely.

Usage (via CLI):  python -m pipeline assemble ep_22-499 [--audio master.mp3] [--out final.mp4]
"""

import json
import subprocess
import tempfile
from pathlib import Path

from .rcp import REPO

W, H, FPS = 1080, 1920, 30

# Burned-in subtitle look (libass force_style): bottom-centered, readable on 9:16
SUB_STYLE = (
    "FontName=Helvetica,FontSize=13,PrimaryColour=&H00FFFFFF,OutlineColour=&H00000000,"
    "BorderStyle=1,Outline=1.2,Shadow=0.6,Alignment=2,MarginV=110,WrapStyle=0"
)


def _run(cmd: list[str]):
    p = subprocess.run(cmd, capture_output=True, text=True)
    if p.returncode != 0:
        raise RuntimeError(f"ffmpeg failed ({' '.join(cmd[:6])}…):\n{p.stderr[-1200:]}")
    return p


def clip_duration(path: Path) -> float:
    p = _run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
              "-of", "csv=p=0", str(path)])
    return float(p.stdout.strip())


def has_audio(path: Path) -> bool:
    p = _run(["ffprobe", "-v", "error", "-select_streams", "a",
              "-show_entries", "stream=index", "-of", "csv=p=0", str(path)])
    return bool(p.stdout.strip())


def _ts(sec: float) -> str:
    ms = int(round(sec * 1000))
    h, ms = divmod(ms, 3600_000)
    m, ms = divmod(ms, 60_000)
    s, ms = divmod(ms, 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def build_srt(screenplay: dict, durations: list[float]) -> str:
    """One SRT over the concatenated timeline: each scene's dialogue lines split
    its clip duration evenly. DE line + EN italic below."""
    entries, idx, t0 = [], 1, 0.0
    for sc, dur in zip(screenplay.get("scenes", []), durations):
        lines = sc.get("dialogue", [])
        if lines:
            pad = min(0.25, dur * 0.05)          # breathing room at scene edges
            usable = max(dur - 2 * pad, 0.5)
            per = usable / len(lines)
            for i, d in enumerate(lines):
                start = t0 + pad + i * per
                end = start + per - 0.05
                text = d.get("german", "").strip()
                en = d.get("english", "").strip()
                if en:
                    text += f"\n<i>{en}</i>"
                entries.append(f"{idx}\n{_ts(start)} --> {_ts(end)}\n{text}\n")
                idx += 1
        t0 += dur
    return "\n".join(entries)


def assemble_episode(ep_dir: Path, clips_dir: Path | None = None,
                     audio: Path | None = None, out: Path | None = None) -> Path:
    """Normalize clips → concat → burn subtitles → (optional) master audio."""
    clips_dir = clips_dir or (ep_dir / "clips")
    out = out or (ep_dir / "final.mp4")
    screenplay = json.loads((ep_dir / "screenplay.json").read_text(encoding="utf-8"))
    n_scenes = len(screenplay.get("scenes", []))

    clips = [clips_dir / f"scene_{i:02d}.mp4" for i in range(1, n_scenes + 1)]
    missing = [c.name for c in clips if not c.exists()]
    if missing:
        raise FileNotFoundError(
            f"{len(missing)} clip(s) missing in {clips_dir.relative_to(REPO)}: "
            + ", ".join(missing[:5]) + ("…" if len(missing) > 5 else ""))

    durations = [clip_duration(c) for c in clips]
    print(f"assemble: {n_scenes} clips, total {sum(durations):.1f}s")

    with tempfile.TemporaryDirectory() as td:
        tdir = Path(td)
        # 1. Normalize every clip (size/fps/codec + exactly ONE audio track —
        #    the clip's own if present, else generated silence)
        norm = []
        vf = (f"scale={W}:{H}:force_original_aspect_ratio=decrease,"
              f"pad={W}:{H}:(ow-iw)/2:(oh-ih)/2,fps={FPS},format=yuv420p")
        for i, c in enumerate(clips, 1):
            nf = tdir / f"n{i:02d}.mp4"
            if has_audio(c):
                _run(["ffmpeg", "-y", "-i", str(c), "-vf", vf,
                      "-map", "0:v", "-map", "0:a:0",
                      "-c:v", "libx264", "-preset", "fast", "-crf", "19",
                      "-c:a", "aac", "-ar", "48000", "-ac", "2", str(nf)])
            else:
                _run(["ffmpeg", "-y", "-i", str(c),
                      "-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo",
                      "-vf", vf, "-map", "0:v", "-map", "1:a",
                      "-c:v", "libx264", "-preset", "fast", "-crf", "19",
                      "-c:a", "aac", "-shortest", str(nf)])
            norm.append(nf)

        # 2. Concat
        listfile = tdir / "list.txt"
        listfile.write_text("".join(f"file '{f}'\n" for f in norm), encoding="utf-8")
        joined = tdir / "joined.mp4"
        _run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(listfile),
              "-c", "copy", str(joined)])

        # 3. Subtitles (burned)
        srt = tdir / "subs.srt"
        srt.write_text(build_srt(screenplay, durations), encoding="utf-8")
        subbed = tdir / "subbed.mp4"
        srt_escaped = str(srt).replace("'", r"\'")
        _run(["ffmpeg", "-y", "-i", str(joined),
              "-vf", f"subtitles='{srt_escaped}':force_style='{SUB_STYLE}'",
              "-c:v", "libx264", "-preset", "fast", "-crf", "19",
              "-c:a", "copy", str(subbed)])

        # 4. Optional master audio (replaces everything)
        if audio:
            _run(["ffmpeg", "-y", "-i", str(subbed), "-i", str(audio),
                  "-map", "0:v", "-map", "1:a", "-c:v", "copy",
                  "-c:a", "aac", "-shortest", str(out)])
        else:
            _run(["ffmpeg", "-y", "-i", str(subbed), "-c", "copy", str(out)])

    final_dur = clip_duration(out)
    print(f"✅ {out.relative_to(REPO)} — {final_dur:.1f}s, {W}x{H}@{FPS}fps, subtitles burned")
    return out

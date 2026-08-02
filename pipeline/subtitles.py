"""Subtitle engine — the declarative subtitle STATE + the ASS renderer.

Design (light path, chosen 2026-07-24): a **frame-based declarative JSON state** is the single
source of truth for both the live UI overlay preview AND the ffmpeg/libass burn — no Remotion,
no re-render to preview an edit. We KNOW the German (screenplay `dialogue`) and the gender of the
target nouns (`target_vocab`), so subtitles + colour-coding are computed from our own data, not
guessed. Word timing is screenplay-derived by default (distribute each shot's words across its
time window); an optional Deepgram pass can refine it to the real audio later.

Pedagogy rules baked in (from Jayon's research): single-line German (L2) only · ≤42 chars/line ·
≤6 s on screen · safe zone x540 y1150 in the 1080×1920 frame · bold 64 pt + rounded box ·
colour-coding der=blue / die=red / das=green / target-grammar=yellow.
"""

import json
import re
import subprocess
import tempfile
from pathlib import Path

FPS = 30
W, H = 1080, 1920
SAFE_X, SAFE_Y = 540, 1150          # centred safe zone (avoids IG/TikTok UI)
MAX_LINE_CHARS = 24                  # what actually fits 1080px at 64pt bold (the research's 42
                                    # overflows the frame) — shorter chunks also aid segmentation
MAX_CUE_SECONDS = 6
FONT_SIZE = 64

# colourLabel → (CSS hex for the UI overlay, ASS &HAABBGGRR for the burn).
# Values are PEDAGOGY §5.3 VERBATIM — `pipeline canon-audit` fails if they drift.
# (das and grammar were wrong here until 2026-08-02; the audit caught both.)
COLORS = {
    "der":     ("#3B82F6", "&H00F6823B"),   # masculine — blue
    "die":     ("#EF4444", "&H004444EF"),   # feminine  — red
    "das":     ("#10B981", "&H0081B910"),   # neuter    — green
    "grammar": ("#F59E0B", "&H000B9EF5"),   # target structure — yellow
    "":        ("#FFFFFF", "&H00FFFFFF"),   # default   — white
}


def _norm(w: str) -> str:
    """Fold a token for matching: lowercase, strip surrounding punctuation, keep umlauts/ß."""
    return re.sub(r"^[^\wäöüß]+|[^\wäöüß]+$", "", w.lower(), flags=re.UNICODE)


def color_map(screenplay: dict) -> dict:
    """normalized noun token → gender colourLabel, from target_vocab. The NOUN carries the gender
    (case-inflected articles are ambiguous), so we colour the noun tokens; nominative der/die/das
    articles are coloured too when they appear."""
    cmap = {}
    for v in screenplay.get("target_vocab", []):
        g = (v.get("gender") or "").strip()
        if g not in ("der", "die", "das"):
            continue
        for tok in (v.get("german") or "").split():
            n = _norm(tok)
            if n and n not in ("der", "die", "das"):   # the noun (+ any modifier) tokens
                cmap[n] = g
        cmap[g] = g                                     # the nominative article itself
    return cmap


def word_color_label(word: str, cmap: dict, grammar_tokens: set) -> str:
    n = _norm(word)
    if n in cmap:
        return cmap[n]
    if n in grammar_tokens:
        return "grammar"
    return ""


def _grammar_tokens(screenplay: dict) -> set:
    """Best-effort: literal German tokens named in grammar_target get the yellow highlight.
    grammar_target is often a description (English), so this is intentionally conservative —
    the editor / Director can recolour anything to yellow."""
    gt = screenplay.get("grammar_target") or ""
    return {_norm(t) for t in re.findall(r"[A-Za-zäöüßÄÖÜ]{3,}", gt)
            if _norm(t) not in {"konjunktiv", "imperative", "direct", "compound", "nouns",
                                "language", "escalation", "authority", "case", "present", "tense"}}


def _chunk_line(text: str) -> list[str]:
    """Greedy word-pack a dialogue line into ≤MAX_LINE_CHARS single-line cues."""
    words, lines, cur = text.split(), [], ""
    for w in words:
        if cur and len(cur) + 1 + len(w) > MAX_LINE_CHARS:
            lines.append(cur)
            cur = w
        else:
            cur = f"{cur} {w}".strip()
    if cur:
        lines.append(cur)
    return lines or [text]


def _distribute_words(words: list[str], start_f: int, end_f: int, cmap, gtok) -> list[dict]:
    """Split a cue's frame span across its words, proportional to token length (a decent proxy
    for spoken duration). Each word → {word, startFrame, endFrame, colorLabel}."""
    span = max(1, end_f - start_f)
    weights = [max(1, len(_norm(w))) for w in words]
    total = sum(weights)
    out, acc = [], 0
    for i, w in enumerate(words):
        ws = start_f + round(span * acc / total)
        acc += weights[i]
        we = start_f + round(span * acc / total)
        out.append({"word": w, "startFrame": ws, "endFrame": max(ws + 1, we),
                    "colorLabel": word_color_label(w, cmap, gtok)})
    return out


def build_subtitle_state(screenplay: dict, seg_durations: list[float] | None = None,
                         fps: int = FPS) -> dict:
    """Screenplay (+ actual per-segment clip durations, if known) → the declarative subtitle
    state. Falls back to the screenplay's segment `duration_s` when clip durations aren't in yet."""
    cmap = color_map(screenplay)
    gtok = _grammar_tokens(screenplay)
    segments = screenplay.get("segments", [])
    if not seg_durations:
        seg_durations = [seg.get("duration_s", 15) or 15 for seg in segments]

    cues, cue_i, seg_start = [], 0, 0.0
    for si, seg in enumerate(segments):
        seg_dur = float(seg_durations[si]) if si < len(seg_durations) else float(seg.get("duration_s", 15) or 15)
        shots = seg.get("shots", [])
        shot_sum = sum(int(sh.get("duration_s", 0) or 0) for sh in shots) or seg_dur
        factor = seg_dur / shot_sum                 # scale screenplay time → actual clip time
        shot_off = 0.0
        for sh in shots:
            sh_dur = int(sh.get("duration_s", 0) or 0) * factor
            lines = [d for d in sh.get("dialogue", []) if (d.get("german") or "").strip()]
            if lines:
                # split the shot window among its dialogue lines, then chunk each to ≤42 chars
                per = sh_dur / len(lines)
                for li, d in enumerate(lines):
                    line_start = seg_start + shot_off + li * per
                    chunks = _chunk_line(d["german"].strip())
                    cper = per / len(chunks)
                    for ci, chunk in enumerate(chunks):
                        s = line_start + ci * cper
                        e = min(s + cper, s + MAX_CUE_SECONDS)
                        sf, ef = round(s * fps), round(e * fps)
                        words = _distribute_words(chunk.split(), sf, ef, cmap, gtok)
                        cue_i += 1
                        cues.append({
                            "id": f"cue-{cue_i}", "text": chunk,
                            "speaker": d.get("speaker", ""),
                            "segment": seg.get("segment_number"), "shot": sh.get("shot_number"),
                            "startFrame": sf, "endFrame": ef, "words": words,
                        })
            shot_off += sh_dur
        seg_start += seg_dur

    total_frames = round(sum(float(x) for x in seg_durations) * fps) or 1
    return {
        "composition": {"id": screenplay.get("title_de", "episode"), "fps": fps,
                        "width": W, "height": H, "durationInFrames": total_frames},
        "layout": {"safeX": SAFE_X, "safeY": SAFE_Y, "fontSize": FONT_SIZE,
                   "maxLineChars": MAX_LINE_CHARS, "maxCueSeconds": MAX_CUE_SECONDS},
        "colors": {k: v[0] for k, v in COLORS.items()},
        "subtitles": cues,
    }


# ── ASS renderer (the burn format for ffmpeg/libass) ─────────────────

def _ass_ts(frame: int, fps: int) -> str:
    t = frame / fps
    h = int(t // 3600); m = int((t % 3600) // 60); s = t % 60
    return f"{h:d}:{m:02d}:{s:05.2f}"


def render_ass(state: dict) -> str:
    fps = state["composition"]["fps"]
    fs = state.get("layout", {}).get("fontSize", FONT_SIZE)
    head = [
        "[Script Info]", "ScriptType: v4.00+", f"PlayResX: {W}", f"PlayResY: {H}",
        "WrapStyle: 2", "ScaledBorderAndShadow: yes", "",
        "[V4+ Styles]",
        ("Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, "
         "BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, "
         "BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding"),
        # BorderStyle=3 → box (BackColour); Outline=16 = box padding; BackColour &H20000000 =
        # ~88% opaque black (ASS alpha is INVERTED: 00=opaque, FF=clear). Alignment=5 (we \pos it).
        (f"Style: DE,Arial,{fs},&H00FFFFFF,&H00FFFFFF,&H00000000,&H20000000,-1,0,0,0,100,100,0,0,"
         "3,16,0,5,40,40,40,1"),
        "", "[Events]",
        "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text",
    ]
    ev = []
    for cue in state.get("subtitles", []):
        start = _ass_ts(cue["startFrame"], fps)
        end = _ass_ts(cue["endFrame"], fps)
        # PEDAGOGY §5.2: the whole clause appears at once, colour-coded. The colour
        # key is the retention win and stays; the word-by-word reveal is dropped —
        # it destroys the reader's perceptual span (their natural forward preview)
        # and forces reading at exactly the speaker's pace. Per-word timing stays in
        # the STATE (the editor and the Director still address single words); it just
        # no longer drives the render.
        parts = [f"{{\\pos({SAFE_X},{SAFE_Y})}}"]
        for wd in cue["words"]:
            ass_color = COLORS.get(wd.get("colorLabel", ""), COLORS[""])[1]
            parts.append(f"{{\\c{ass_color}}}{wd['word']} ")
        ev.append(f"Dialogue: 0,{start},{end},DE,,0,0,0,,{''.join(parts).rstrip()}")
    return "\n".join(head + ev) + "\n"


# ── ffmpeg assembly + burn (the light-path renderer) ─────────────────

def _run(cmd: list) -> None:
    p = subprocess.run(cmd, capture_output=True, text=True)
    if p.returncode != 0:
        raise RuntimeError("ffmpeg/ffprobe failed:\n" + (p.stderr or "")[-1200:])


def clip_duration(path) -> float:
    p = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                        "-of", "csv=p=0", str(path)], capture_output=True, text=True)
    try:
        return float(p.stdout.strip())
    except ValueError:
        return 0.0


def concat_clips(clip_paths: list, out_path, fps: int = FPS) -> float:
    """Normalize each segment clip → concat (demuxer) → one joined 9:16 video. Returns duration."""
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        normd = []
        for i, c in enumerate(clip_paths):
            n = td / f"n{i:02d}.mp4"
            # simple, robust normalize (audio optional): keep video track + any audio, pad to 9:16
            vf = (f"scale={W}:{H}:force_original_aspect_ratio=decrease,"
                  f"pad={W}:{H}:(ow-iw)/2:(oh-ih)/2:color=black,fps={fps},format=yuv420p,setsar=1")
            _run(["ffmpeg", "-y", "-v", "error", "-i", str(c), "-vf", vf, "-r", str(fps),
                  "-c:v", "libx264", "-preset", "veryfast", "-crf", "20",
                  "-c:a", "aac", "-ar", "48000", "-ac", "2", str(n)])
            normd.append(n)
        listfile = td / "list.txt"
        listfile.write_text("".join(f"file '{n}'\n" for n in normd), encoding="utf-8")
        _run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", str(listfile),
              "-c", "copy", str(out_path)])
    return clip_duration(out_path)


def burn(video_path, state: dict, out_path) -> Path:
    """Burn the subtitle STATE onto a video via libass (render ASS → ffmpeg ass filter)."""
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as td:
        ass = Path(td) / "subs.ass"
        ass.write_text(render_ass(state), encoding="utf-8")
        esc = str(ass).replace("\\", "\\\\").replace(":", "\\:").replace("'", "\\'")
        _run(["ffmpeg", "-y", "-v", "error", "-i", str(video_path),
              "-vf", f"ass='{esc}'", "-c:v", "libx264", "-preset", "veryfast", "-crf", "20",
              "-c:a", "copy", str(out_path)])
    return out_path


def mock_clip(out_path, seconds: float, label: str, idx: int = 0, fps: int = FPS) -> Path:
    """Dev-only: synthesize a labelled 9:16 clip (no FAL_KEY needed) so assembly/preview/export
    run end-to-end. Mirrors the mock image provider."""
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    bg = ["0x1b2a4a", "0x3a1f2b", "0x1f3a2e", "0x3a301b", "0x2b1f3a"][idx % 5]
    font = "/System/Library/Fonts/Supplemental/Arial.ttf"
    with tempfile.TemporaryDirectory() as td:
        tf = Path(td) / "l.txt"
        tf.write_text(label, encoding="utf-8")
        _run(["ffmpeg", "-y", "-v", "error",
              "-f", "lavfi", "-i", f"color=c={bg}:s={W}x{H}:d={seconds}:r={fps}",
              "-f", "lavfi", "-t", str(seconds), "-i", "sine=frequency=220:sample_rate=48000",
              "-vf", (f"drawtext=fontfile={font}:textfile={tf}:fontcolor=white:fontsize=70:"
                      f"x=(w-text_w)/2:y=(h-text_h)/2:text_align=C"),
              "-c:v", "libx264", "-preset", "veryfast", "-pix_fmt", "yuv420p",
              "-c:a", "aac", "-ar", "48000", "-ac", "2", "-shortest", str(out_path)])
    return out_path

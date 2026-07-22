"""Video generation providers — turn a scene's Seedance prompt into a clip.

Interface (all providers):
    provider.generate(scene, seedance_pkg, refs, out_path) -> Path

- MockVideoProvider  : renders a real placeholder .mp4 locally (no key, no cost).
                       Lets the whole pipeline run end-to-end TODAY.
- FalVideoProvider   : calls the real Seedance model via fal.ai. Activated by
                       FAL_KEY in .env. Same interface — one-key swap.

Add other providers (Replicate, BytePlus/ModelArk, Gemini Omni) the same way.
"""

import os
import subprocess
import tempfile
import textwrap
import urllib.request
from pathlib import Path

FONT = "/System/Library/Fonts/Supplemental/Arial.ttf"
W, H = 720, 1280
# distinct card tints per scene so the assembled reel visibly changes shot-to-shot
PALETTE = ["0x1b2a4a", "0x3a1f2b", "0x1f3a2e", "0x3a301b", "0x2b1f3a",
           "0x1f2f3a", "0x3a2b1f", "0x2a1f2f", "0x1f3a3a", "0x2f2a1b"]


def _ff(cmd):
    p = subprocess.run(cmd, capture_output=True, text=True)
    if p.returncode != 0:
        raise RuntimeError("ffmpeg failed:\n" + p.stderr[-800:])


# ── Mock ─────────────────────────────────────────────────────────

class MockVideoProvider:
    name = "mock"

    def generate(self, scene: dict, seedance_pkg: dict, refs: list, out_path: Path) -> Path:
        n = scene.get("scene_number", 0)
        dur = max(int(scene.get("duration_s", 7) or 7), 2)
        word = scene.get("german_word", "")
        setting = scene.get("setting", "")
        speakers = " · ".join(dict.fromkeys(d.get("speaker", "") for d in scene.get("dialogue", [])))
        bg = PALETTE[(n - 1) % len(PALETTE)]

        card = (f"[ MOCK CLIP — no real video yet ]\n\nSCENE {n}\n{word}\n\n"
                f"{speakers}\n\n" + "\n".join(textwrap.wrap(setting, 34)))
        with tempfile.TemporaryDirectory() as td:
            tf = Path(td) / "card.txt"
            tf.write_text(card, encoding="utf-8")
            out_path.parent.mkdir(parents=True, exist_ok=True)
            _ff(["ffmpeg", "-y", "-v", "error",
                 "-f", "lavfi", "-i", f"color=c={bg}:s={W}x{H}:d={dur}",
                 "-f", "lavfi", "-i", f"sine=frequency={180 + n * 30}:duration={dur}",
                 "-vf",
                 f"drawgrid=w=72:h=72:c=0xffffff22,"
                 f"drawtext=fontfile={FONT}:textfile={tf}:fontcolor=white:fontsize=34:"
                 f"line_spacing=14:x=(w-text_w)/2:y=(h-text_h)/2:text_align=C",
                 "-c:v", "libx264", "-preset", "ultrafast", "-pix_fmt", "yuv420p",
                 "-c:a", "aac", "-shortest", str(out_path)])
        return out_path


# ── fal.ai (real Seedance) ───────────────────────────────────────

class FalVideoProvider:
    """Real Seedance via fal.ai. Requires: `pip install fal-client` + FAL_KEY in .env.

    ⚠ VERIFY BEFORE FIRST REAL RUN: `MODEL` is the fal.ai Seedance route and the
    `arguments` keys must match fal.ai's CURRENT Seedance schema (these models are
    newer than this code — confirm at https://fal.ai/models). Everything else
    (upload refs → subscribe → download) is the standard fal_client flow.
    """
    name = "fal"
    MODEL = os.environ.get("FAL_SEEDANCE_MODEL", "fal-ai/bytedance/seedance/v1/pro/text-to-video")

    def __init__(self):
        if not os.environ.get("FAL_KEY"):
            raise RuntimeError("FAL_KEY not set in environment/.env — get one at fal.ai, "
                               "add FAL_KEY=... to .env, then re-run with --provider fal.")
        try:
            import fal_client  # noqa
        except ImportError:
            raise RuntimeError("fal-client not installed — run: .venv/bin/pip install fal-client")

    def generate(self, scene: dict, seedance_pkg: dict, refs: list, out_path: Path) -> Path:
        import fal_client
        prompt = seedance_pkg.get("prompt", "")
        # Upload resolved refs (fal wants URLs); split character/style IMAGES from
        # per-character VOICE audio clips — Seedance uses images for identity, the
        # voice clips for how each character sounds (@Audio bindings in the prompt).
        image_urls, audio_urls = [], []
        for r in refs:
            p = r.get("path")
            if not (p and Path(p).exists()):
                continue
            url = fal_client.upload_file(p)
            if r.get("role") == "voice" or p.lower().endswith((".mp3", ".wav", ".m4a")):
                audio_urls.append(url)
            else:
                image_urls.append(url)

        args = {
            "prompt": prompt[:3000],
            "aspect_ratio": "9:16",
            "resolution": "720p",
            "duration": int(scene.get("duration_s", 7) or 7),
        }
        if image_urls:
            args["image_urls"] = image_urls  # ⚠ confirm key name in current fal schema
        if audio_urls:
            args["audio_urls"] = audio_urls  # ⚠ confirm key name in current fal schema

        result = fal_client.subscribe(self.MODEL, arguments=args, with_logs=False)
        url = (result.get("video") or {}).get("url") if isinstance(result.get("video"), dict) \
            else result.get("video_url") or result.get("url")
        if not url:
            raise RuntimeError(f"fal returned no video url. Raw keys: {list(result)}")
        out_path.parent.mkdir(parents=True, exist_ok=True)
        urllib.request.urlretrieve(url, out_path)
        return out_path


_PROVIDERS = {"mock": MockVideoProvider, "fal": FalVideoProvider}


def get_video_provider(name: str | None = None):
    name = (name or os.environ.get("PIPELINE_VIDEO_PROVIDER") or "mock").lower()
    if name not in _PROVIDERS:
        raise ValueError(f"unknown video provider '{name}' (have: {', '.join(_PROVIDERS)})")
    return _PROVIDERS[name]()

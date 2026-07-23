"""Image (storyboard panel) providers — turn a shot's image prompt into a 9:16 panel.

Interface (all providers):
    provider.generate(shot, image_prompt, refs, out_path) -> Path

- MockImageProvider     : renders a real placeholder .png locally (no key, no cost) — lets
                          the storyboard stage run end-to-end TODAY.
- FalGptImageProvider   : OpenAI GPT Image 2 via fal.ai (`openai/gpt-image-2/edit`).
- FalNanoBananaProvider : Google Nano Banana Pro via fal.ai (`fal-ai/nano-banana-pro`).

Both real providers are FAL_KEY-gated and SELECTABLE (Jayon: "have both, try either").
`refs` are IMAGE references only for the storyboard step: character sheets/portraits +
(later) the style plate. The panel this produces becomes a Seedance @Image ref downstream.

⚠ VERIFY BEFORE FIRST REAL RUN: the fal model slugs + `arguments` keys below are written to
the standard fal_client pattern but are unconfirmed against fal's CURRENT schema — confirm at
https://fal.ai/models (flagged `⚠ confirm` inline). Everything else is the standard flow.
"""

import os
import subprocess
import tempfile
import textwrap
import urllib.request
from pathlib import Path

FONT = "/System/Library/Fonts/Supplemental/Arial.ttf"
W, H = 720, 1280  # 9:16
PALETTE = ["0x1b2a4a", "0x3a1f2b", "0x1f3a2e", "0x3a301b", "0x2b1f3a", "0x1f2f3a"]


def _ff(cmd):
    p = subprocess.run(cmd, capture_output=True, text=True)
    if p.returncode != 0:
        raise RuntimeError("ffmpeg failed:\n" + p.stderr[-800:])


def _image_refs(refs: list) -> list:
    """Existing image files from the refs list (drop audio + unresolved)."""
    out = []
    for r in refs:
        p = r.get("path")
        if p and Path(p).exists() and not p.lower().endswith((".mp3", ".wav", ".m4a")):
            out.append(p)
    return out


# ── Mock ─────────────────────────────────────────────────────────

class MockImageProvider:
    name = "mock"

    def generate(self, shot: dict, image_prompt: str, refs: list, out_path: Path) -> Path:
        n = shot.get("shot_number", 0)
        size = shot.get("shot_size", "")
        angle = shot.get("camera_angle", "")
        action = shot.get("action", "")
        bg = PALETTE[(int(n) - 1) % len(PALETTE)]
        card = (f"[ MOCK PANEL — no real image yet ]\n\nSHOT {n}\n{size} · {angle}\n\n"
                + "\n".join(textwrap.wrap(action, 32)))
        with tempfile.TemporaryDirectory() as td:
            tf = Path(td) / "card.txt"
            tf.write_text(card, encoding="utf-8")
            out_path.parent.mkdir(parents=True, exist_ok=True)
            _ff(["ffmpeg", "-y", "-v", "error",
                 "-f", "lavfi", "-i", f"color=c={bg}:s={W}x{H}:d=1",
                 "-vf",
                 f"drawgrid=w=72:h=72:c=0xffffff22,"
                 f"drawtext=fontfile={FONT}:textfile={tf}:fontcolor=white:fontsize=32:"
                 f"line_spacing=14:x=(w-text_w)/2:y=(h-text_h)/2:text_align=C",
                 "-frames:v", "1", str(out_path)])
        return out_path


# ── fal.ai real providers ────────────────────────────────────────

class _FalImageBase:
    MODEL = None

    def __init__(self):
        if not os.environ.get("FAL_KEY"):
            raise RuntimeError("FAL_KEY not set — add FAL_KEY=... to .env, then re-run "
                               "with --image-provider gpt-image-2|nano-banana-pro.")
        try:
            import fal_client  # noqa
        except ImportError:
            raise RuntimeError("fal-client not installed — run: .venv/bin/pip install fal-client")

    def _run(self, args: dict, out_path: Path) -> Path:
        import fal_client
        result = fal_client.subscribe(self.MODEL, arguments=args, with_logs=False)
        imgs = result.get("images") or []
        url = (imgs[0].get("url") if imgs and isinstance(imgs[0], dict) else None) \
            or result.get("image", {}).get("url") if isinstance(result.get("image"), dict) else None
        if not url:
            raise RuntimeError(f"{self.name} returned no image url. Raw keys: {list(result)}")
        out_path.parent.mkdir(parents=True, exist_ok=True)
        urllib.request.urlretrieve(url, out_path)
        return out_path

    def _upload(self, refs: list) -> list:
        import fal_client
        return [fal_client.upload_file(p) for p in _image_refs(refs)]


class FalGptImageProvider(_FalImageBase):
    """OpenAI GPT Image 2 on fal — 99% text accuracy, neutral color, up to 16 edit refs."""
    name = "gpt-image-2"
    MODEL = os.environ.get("FAL_GPT_IMAGE_MODEL", "openai/gpt-image-2/edit")

    def generate(self, shot: dict, image_prompt: str, refs: list, out_path: Path) -> Path:
        args = {
            "prompt": image_prompt,
            "image_size": "portrait_16_9",   # ⚠ confirm 9:16 size token
            "quality": "high",
            "output_format": "png",
        }
        urls = self._upload(refs)
        if urls:
            args["image_urls"] = urls        # ⚠ confirm key name (edit endpoint)
        return self._run(args, out_path)


class FalNanoBananaProvider(_FalImageBase):
    """Google Nano Banana Pro (gemini-3-pro-image) on fal — up to 14 refs, native umlauts."""
    name = "nano-banana-pro"
    MODEL = os.environ.get("FAL_NANO_BANANA_MODEL", "fal-ai/nano-banana-pro")

    def generate(self, shot: dict, image_prompt: str, refs: list, out_path: Path) -> Path:
        args = {
            "prompt": image_prompt,
            "aspect_ratio": "9:16",           # ⚠ confirm arg name
            "num_images": 1,
        }
        urls = self._upload(refs)
        if urls:
            args["image_urls"] = urls         # ⚠ confirm key name
        return self._run(args, out_path)


_PROVIDERS = {
    "mock": MockImageProvider,
    "gpt-image-2": FalGptImageProvider,
    "nano-banana-pro": FalNanoBananaProvider,
}


def get_image_provider(name: str | None = None):
    name = (name or os.environ.get("PIPELINE_IMAGE_PROVIDER") or "mock").lower()
    if name not in _PROVIDERS:
        raise ValueError(f"unknown image provider '{name}' (have: {', '.join(_PROVIDERS)})")
    return _PROVIDERS[name]()

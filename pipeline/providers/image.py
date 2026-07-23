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
W, H = 720, 1280  # 9:16 — a single panel
SHEET_CW, SHEET_CH = 360, 640  # 9:16 — one cell of a mock sheet
PALETTE = ["0x1b2a4a", "0x3a1f2b", "0x1f3a2e", "0x3a301b", "0x2b1f3a", "0x1f2f3a"]


def _ff(cmd):
    p = subprocess.run(cmd, capture_output=True, text=True)
    if p.returncode != 0:
        raise RuntimeError("ffmpeg failed:\n" + p.stderr[-800:])


def _gcd(a, b):
    while b:
        a, b = b, a % b
    return a


def sheet_grid(n_shots: int) -> tuple[int, int, str, str]:
    """The layout law: shot count → (rows, cols, layout, sheet_aspect_ratio). **Story-driven —
    NO fixed shot cap.** Every CELL is 9:16; the SHEET's overall ratio is cols·9 : rows·16.
    ≤3 shots = a single-row filmstrip (1x2, 1x3); 4+ = a balanced grid with columns capped at
    3 so each panel stays large enough to slice cleanly (2x2, 2x3, 3x3, 3x4…). Scales to any N.
    See skill-2b-storyboard.md."""
    n = max(1, int(n_shots))
    if n <= 3:
        rows, cols = 1, n                 # filmstrip
    else:
        cols = 1
        while cols * cols < n:            # ceil(sqrt(n)) → a balanced grid
            cols += 1
        cols = min(3, cols)               # cap columns so panels stay large enough to slice
        rows = -(-n // cols)              # ceil(n / cols)
    w, h = cols * 9, rows * 16
    g = _gcd(w, h)
    return rows, cols, f"{rows}x{cols}", f"{w // g}:{h // g}"


def slice_sheet(sheet_path: Path, rows: int, cols: int, shot_numbers: list[int],
                out_dir: Path, seg_n: int) -> list[Path]:
    """Deterministic equal-division crop of a storyboard sheet into per-shot 9:16 panels.
    Each cell is cropped (iw/cols × ih/rows) in reading order, then centre-cropped + scaled to
    720×1280 so every panel is a clean 9:16 Seedance anchor. Writes panel_s<seg>_<shot>.png —
    the SAME filename contract the downstream skill-3 refs_manifest resolves."""
    out_dir.mkdir(parents=True, exist_ok=True)
    out = []
    for idx, shot_n in enumerate(shot_numbers):
        r, c = divmod(idx, cols)
        if r >= rows:
            break
        dest = out_dir / f"panel_s{int(seg_n):02d}_{int(shot_n):02d}.png"
        vf = (f"crop=iw/{cols}:ih/{rows}:iw/{cols}*{c}:ih/{rows}*{r},"
              f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H}")
        _ff(["ffmpeg", "-y", "-v", "error", "-i", str(sheet_path), "-vf", vf,
             "-frames:v", "1", str(dest)])
        out.append(dest)
    return out


def _fal_ratio(sheet_aspect_ratio: str, layout: str) -> str:
    """Map a sheet's ideal ratio to the nearest aspect_ratio token fal's image models accept.
    ⚠ confirm the exact supported tokens against fal's CURRENT nano-banana-pro / gpt-image-2
    schema; the layout is ALSO stated in the prompt text, which is what actually drives the
    panel arrangement — this only sets the output canvas shape."""
    supported = {"9:16": 9 / 16, "3:4": 3 / 4, "1:1": 1.0, "4:3": 4 / 3, "16:9": 16 / 9}
    try:
        w, h = sheet_aspect_ratio.split(":")
        target = int(w) / int(h)
    except Exception:
        return "9:16"
    return min(supported, key=lambda k: abs(supported[k] - target))


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

    def generate_sheet(self, sheet: dict, sheet_prompt: str, refs: list, out_path: Path) -> Path:
        """Render a real multi-panel storyboard sheet (rows×cols of 9:16 cells) locally, so the
        sheet→slice→panels plumbing runs end-to-end with no key/cost. Cells are exact 9:16, so
        slicing is pixel-perfect."""
        shots = sheet.get("shot_numbers") or [1]
        rows, cols, _, _ = sheet_grid(len(shots))
        seg = sheet.get("segment_number", 0)
        cw, ch = SHEET_CW, SHEET_CH
        sw, sh = cols * cw, rows * ch
        bg = PALETTE[(int(seg) - 1) % len(PALETTE)]
        with tempfile.TemporaryDirectory() as td:
            # per-cell label textfiles, chained as drawtext filters at cell origins
            draws = [f"drawgrid=w={cw}:h={ch}:t=3:c=0xffffffaa"]
            for idx, shot_n in enumerate(shots):
                r, c = divmod(idx, cols)
                if r >= rows:
                    break
                tf = Path(td) / f"c{idx}.txt"
                tf.write_text(f"[ MOCK SHEET ]\nSEG {seg}\nPanel {idx + 1}\nShot {shot_n}",
                              encoding="utf-8")
                draws.append(
                    f"drawtext=fontfile={FONT}:textfile={tf}:fontcolor=white:fontsize=30:"
                    f"line_spacing=10:x={c * cw}+({cw}-text_w)/2:y={r * ch}+({ch}-text_h)/2:text_align=C")
            out_path.parent.mkdir(parents=True, exist_ok=True)
            _ff(["ffmpeg", "-y", "-v", "error",
                 "-f", "lavfi", "-i", f"color=c={bg}:s={sw}x{sh}:d=1",
                 "-vf", ",".join(draws), "-frames:v", "1", str(out_path)])
        return out_path

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

    def generate_sheet(self, sheet: dict, sheet_prompt: str, refs: list, out_path: Path) -> Path:
        ratio = _fal_ratio(sheet.get("sheet_aspect_ratio", ""), sheet.get("layout", ""))
        size = {"9:16": "portrait_16_9", "3:4": "portrait_16_9", "1:1": "square",
                "4:3": "landscape_16_9", "16:9": "landscape_16_9"}.get(ratio, "landscape_16_9")
        args = {"prompt": sheet_prompt, "image_size": size,  # ⚠ confirm size tokens
                "quality": "high", "output_format": "png"}
        urls = self._upload(refs)              # incl. char sheets + prev-segment sheet (chaining)
        if urls:
            args["image_urls"] = urls
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

    def generate_sheet(self, sheet: dict, sheet_prompt: str, refs: list, out_path: Path) -> Path:
        """Primary storyboard path (Jayon's choice). One generation → the whole multi-panel
        sheet. The layout is stated in sheet_prompt; aspect_ratio sets the canvas shape. refs
        carry char sheets/portraits + the prev-segment sheet (cross-segment chaining) — Nano
        Banana Pro takes up to 14."""
        args = {
            "prompt": sheet_prompt,
            "aspect_ratio": _fal_ratio(sheet.get("sheet_aspect_ratio", ""), sheet.get("layout", "")),
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

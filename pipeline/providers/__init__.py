"""External-service provider adapters (video generation, audio, posting).

Each provider has a real implementation gated behind an API key, plus a `mock`
implementation so the FULL pipeline runs end-to-end locally with no keys/credits.
Swap provider by name (env PIPELINE_VIDEO_PROVIDER or --provider) — the interface
is identical, so real APIs are a one-key change, never a rewrite.
"""

from .video import get_video_provider  # noqa: F401

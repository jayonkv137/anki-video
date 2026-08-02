"""LLM — the V4 studio's single model gateway (Gemini, schema-ENFORCED, loud failures).

Rules (BUILD_PLAN_v4 §6 · the agent-engineering research):
- **Structured output is enforced**, twice: `response_schema` is passed to the API
  (sanitized to Gemini's OpenAPI subset), and the parsed result is locally validated
  against the ORIGINAL schema (required keys, types, closed-world where
  `additionalProperties: false`). One correction retry, then a loud error.
- **Tools and response schemas are never combined in one call** (tool suppression:
  the model skips the tool to satisfy the schema). Tool-calling gets its own entry
  point when Phase 3 needs it — never add a schema to it.
- **Failures are loud.** No silent fallback to another provider, no invented output,
  no plausible defaults. A failed call raises `LLMError` with the real cause.
- **Cost honesty:** this module returns real usage and the real model id; it does
  not write cost records (callers own their ledger semantics).

Legacy note: `stages._call_gemini` (schema-unenforced) remains only for the V3
wizard and dies with it in Phase 3.5. All V4 studio code calls THIS module.
"""

import json
import os
import re
import time

from dotenv import load_dotenv

from .rcp import REPO

load_dotenv(REPO / ".env")

DEFAULT_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.6-flash")
_CLIENT = None


class LLMError(RuntimeError):
    """A model call failed for real. Nothing was invented in its place."""

    def __init__(self, message: str, *, label: str = "", problems: list | None = None):
        super().__init__(message)
        self.label = label
        self.problems = problems or []


def _client():
    global _CLIENT
    if _CLIENT is None:
        from google import genai
        key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
        if not key:
            raise LLMError("GOOGLE_API_KEY/GEMINI_API_KEY not set — the studio cannot call its model.")
        _CLIENT = genai.Client(api_key=key)
    return _CLIENT


# ── Schema handling ──────────────────────────────────────────────

_UNSUPPORTED_KEYS = {"additionalProperties"}  # not in Gemini's OpenAPI subset


def _sanitize(schema):
    """Deep-copy a JSON schema, dropping keys Gemini's response_schema rejects.
    Enforcement of the dropped constraints happens locally in _check()."""
    if isinstance(schema, dict):
        return {k: _sanitize(v) for k, v in schema.items() if k not in _UNSUPPORTED_KEYS}
    if isinstance(schema, list):
        return [_sanitize(v) for v in schema]
    return schema


_TYPE_MAP = {
    "object": dict, "array": list, "string": str,
    "integer": int, "number": (int, float), "boolean": bool,
}


def _check(data, schema, path="$") -> list[str]:
    """Local validation against the ORIGINAL schema: required keys, basic types,
    closed world where additionalProperties is false. Returns a list of problems."""
    problems = []
    t = schema.get("type")
    expected = _TYPE_MAP.get(t)
    if expected and not isinstance(data, expected):
        return [f"{path}: expected {t}, got {type(data).__name__}"]
    if t == "object":
        props = schema.get("properties", {})
        for key in schema.get("required", []):
            if key not in data:
                problems.append(f"{path}.{key}: missing required field")
        if schema.get("additionalProperties") is False:
            for key in data:
                if key not in props:
                    problems.append(f"{path}.{key}: unexpected field")
        for key, sub in props.items():
            if key in data:
                problems.extend(_check(data[key], sub, f"{path}.{key}"))
    elif t == "array":
        item_schema = schema.get("items")
        if item_schema:
            for i, item in enumerate(data):
                problems.extend(_check(item, item_schema, f"{path}[{i}]"))
    return problems


def _parse_json(text: str):
    try:
        return json.loads(text, strict=False)
    except json.JSONDecodeError:
        sanitized = re.sub(r"[\x00-\x1f\x7f-\x9f]",
                           lambda m: "\\n" if m.group(0) == "\n" else "", text)
        return json.loads(sanitized, strict=False)


# ── The one structured call ──────────────────────────────────────

_RETRYABLE = ("429", "503", "UNAVAILABLE", "RESOURCE_EXHAUSTED", "DEADLINE")


def call_json(system: str, user: str, schema: dict, *,
              label: str = "", model: str | None = None,
              temperature: float | None = None,
              validate=None) -> tuple[dict, dict]:
    """One schema-enforced JSON call. Returns (data, usage).

    usage = {"model", "tokens_in", "tokens_out"}.
    `validate` (optional) is a callable data -> list[str] of HARD problems only —
    soft/advisory checks belong to the caller, after this returns.
    On schema or validation failure: ONE correction retry with the problems named,
    then LLMError. Never returns invented or partial data.
    """
    from google.genai import types

    model = model or DEFAULT_MODEL
    config_kwargs = dict(
        system_instruction=system,
        response_mime_type="application/json",
        response_schema=_sanitize(schema),
    )
    if temperature is not None:
        config_kwargs["temperature"] = temperature
    config = types.GenerateContentConfig(**config_kwargs)

    def _once(user_msg: str):
        last = None
        for attempt in range(3):
            try:
                resp = _client().models.generate_content(
                    model=model, contents=user_msg, config=config)
                data = _parse_json(resp.text)
                um = resp.usage_metadata
                usage = {"model": model,
                         "tokens_in": (um.prompt_token_count or 0) if um else 0,
                         "tokens_out": (um.candidates_token_count or 0) if um else 0}
                return data, usage
            except Exception as e:  # transport-level retry only
                last = e
                if any(tok in str(e) for tok in _RETRYABLE) and attempt < 2:
                    time.sleep(1.5 * (attempt + 1))
                    continue
                raise LLMError(f"[{label or model}] model call failed: {e}",
                               label=label) from e
        raise LLMError(f"[{label or model}] model call failed after retries: {last}",
                       label=label)

    data, usage = _once(user)
    problems = _check(data, schema) + (validate(data) if validate else [])
    if problems:
        correction = (user + "\n\nYour previous answer FAILED validation:\n- "
                      + "\n- ".join(problems[:25])
                      + "\nFix every problem and return the corrected JSON now.")
        data, usage2 = _once(correction)
        usage = {"model": model,
                 "tokens_in": usage["tokens_in"] + usage2["tokens_in"],
                 "tokens_out": usage["tokens_out"] + usage2["tokens_out"]}
        problems = _check(data, schema) + (validate(data) if validate else [])
        if problems:
            raise LLMError(
                f"[{label or model}] output failed validation after one retry "
                f"({len(problems)} problems): " + " · ".join(problems[:8]),
                label=label, problems=problems)
    if label:
        print(f"[{label} ({model}): {usage['tokens_in']} in / {usage['tokens_out']} out]")
    return data, usage

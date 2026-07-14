"""B2 story-stage test harness: 10 words -> story JSON, validated.

Usage:
  python scripts/generate_story.py                # words at positions 1-10
  python scripts/generate_story.py --start 41     # words 41-50
  python scripts/generate_story.py --random       # 10 random unseen words

Reads words from Supabase (read-only — nothing is stamped), calls Claude
Sonnet 5 with a schema-enforced structured output, then runs SEMANTIC
validation (the part schemas can't do): every target word genuinely present
in its owning scene. On failure: one retry with explicit feedback.
"""

import argparse
import json
import os
import random
import sys
from pathlib import Path

import requests
from anthropic import Anthropic
from dotenv import load_dotenv

REPO = Path(__file__).parent.parent
SYSTEM_PROMPT = (REPO / "prompts" / "story_system_prompt.md").read_text(encoding="utf-8").split("---\n", 1)[1]

STORY_SCHEMA = {
    "type": "object",
    "properties": {
        "title": {"type": "string", "description": "Short episode title in simple German"},
        "scenes": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "scene_number": {"type": "integer"},
                    "position": {"type": "integer", "description": "the deck position of the word this scene owns"},
                    "german_word": {"type": "string"},
                    "narration_de": {"type": "string", "description": "1-3 short German sentences, spoken in 6-8s"},
                    "visual_description_en": {"type": "string"},
                },
                "required": ["scene_number", "position", "german_word", "narration_de", "visual_description_en"],
                "additionalProperties": False,
            },
        },
    },
    "required": ["title", "scenes"],
    "additionalProperties": False,
}

ARTICLES = ("der ", "die ", "das ")


def fetch_words(start: int | None, randomize: bool) -> list[dict]:
    url = os.environ["SUPABASE_URL"].rstrip("/") + "/rest/v1/words"
    headers = {
        "apikey": os.environ["SUPABASE_SECRET_KEY"],
        "Authorization": f"Bearer {os.environ['SUPABASE_SECRET_KEY']}",
    }
    if randomize:
        pos = sorted(random.sample(range(1, 606), 10))
        params = {"position": f"in.({','.join(map(str, pos))})", "order": "position.asc",
                  "select": "position,german,english,sentence_de,sentence_en,word_type"}
    else:
        s = start or 1
        params = {"position": f"gte.{s}", "order": "position.asc", "limit": "10",
                  "select": "position,german,english,sentence_de,sentence_en,word_type"}
    resp = requests.get(url, headers=headers, params=params, timeout=15)
    resp.raise_for_status()
    words = resp.json()
    assert len(words) == 10, f"expected 10 words, got {len(words)}"
    return words


def word_stem(german: str) -> str:
    """Bare word for matching: drop article; for verbs drop -en/-n ending."""
    w = german.lower()
    for a in ARTICLES:
        if w.startswith(a):
            return w[len(a):]
    if (w.endswith("eln") or w.endswith("ern")) and len(w) > 4:
        return w[:-1]  # schütteln -> schüttel, matches schüttelt
    if w.endswith("en") and len(w) > 4:
        return w[:-2]  # arbeiten -> arbeit, matches arbeitet/arbeite
    return w


def validate(story: dict, words: list[dict]) -> list[str]:
    problems = []
    scenes = story.get("scenes", [])
    if len(scenes) != 10:
        problems.append(f"expected 10 scenes, got {len(scenes)}")
    by_pos = {w["position"]: w for w in words}
    seen_pos = set()
    for sc in scenes:
        pos = sc.get("position")
        if pos not in by_pos:
            problems.append(f"scene {sc.get('scene_number')}: unknown position {pos}")
            continue
        if pos in seen_pos:
            problems.append(f"position {pos} used by more than one scene")
        seen_pos.add(pos)
        stem = word_stem(by_pos[pos]["german"])
        if stem not in sc.get("narration_de", "").lower():
            problems.append(
                f"scene {sc.get('scene_number')}: word '{by_pos[pos]['german']}' (stem '{stem}') "
                f"not found in its narration: {sc.get('narration_de')!r}"
            )
    missing = set(by_pos) - seen_pos
    if missing:
        problems.append(f"words never assigned a scene: {sorted(missing)}")
    return problems


def generate(client: Anthropic, words: list[dict], feedback: str | None = None) -> dict:
    word_list = "\n".join(
        f"- position {w['position']}: {w['german']} = {w['english']} ({w['word_type']}) — "
        f"example: {w['sentence_de']} / {w['sentence_en']}"
        for w in words
    )
    user = f"Today's 10 target words:\n\n{word_list}\n\nWrite today's episode."
    if feedback:
        user += f"\n\nIMPORTANT — your previous attempt failed validation:\n{feedback}\nFix these issues."
    resp = client.messages.create(
        model="claude-sonnet-5",
        max_tokens=8192,
        system=SYSTEM_PROMPT,
        output_config={"format": {"type": "json_schema", "schema": STORY_SCHEMA}},
        messages=[{"role": "user", "content": user}],
    )
    usage = resp.usage
    print(f"[tokens: {usage.input_tokens} in / {usage.output_tokens} out]")
    text = next(b.text for b in resp.content if b.type == "text")
    return json.loads(text)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--start", type=int, default=None)
    ap.add_argument("--random", action="store_true")
    args = ap.parse_args()

    load_dotenv(REPO / ".env")
    if not os.environ.get("ANTHROPIC_API_KEY"):
        sys.exit("ANTHROPIC_API_KEY missing from .env — create one at console.anthropic.com")

    client = Anthropic()
    words = fetch_words(args.start, args.random)
    print("words:", ", ".join(f"{w['position']}:{w['german']}" for w in words), "\n")

    story = generate(client, words)
    problems = validate(story, words)
    if problems:  # the validate -> retry pattern: one retry with explicit feedback
        print("\n! validation failed, retrying with feedback:")
        for p in problems:
            print("  -", p)
        story = generate(client, words, feedback="\n".join(problems))
        problems = validate(story, words)

    print(f"\n{'=' * 60}\n  {story['title']}\n{'=' * 60}")
    for sc in sorted(story["scenes"], key=lambda s: s["scene_number"]):
        print(f"\nScene {sc['scene_number']} — {sc['german_word']} (pos {sc['position']})")
        print(f"  DE: {sc['narration_de']}")
        print(f"  Visual: {sc['visual_description_en']}")
    if problems:
        print(f"\n⚠ STILL FAILING after retry ({len(problems)} problems):")
        for p in problems:
            print("  -", p)
    else:
        print("\n✓ semantic validation passed (all 10 words present in their scenes)")

    out = REPO / "output" / "stories"
    out.mkdir(parents=True, exist_ok=True)
    fname = out / f"story_{words[0]['position']}-{words[-1]['position']}.json"
    fname.write_text(json.dumps(story, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"saved: {fname.relative_to(REPO)}")


if __name__ == "__main__":
    main()

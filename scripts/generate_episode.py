"""C2 test harness: 10 words -> Skill 1 (story) -> Skill 2 (screenplay) -> Skill 3 (prompts).

Usage:
  python scripts/generate_episode.py                     # next words at positions 1-10
  python scripts/generate_episode.py --start 41          # words 41-50
  python scripts/generate_episode.py --random            # 10 random words
  python scripts/generate_episode.py --note "im Biergarten bitte"   # director note

Read-only on Supabase. Saves all artifacts to output/episodes/ep_<pos>-<pos>/
(story.json, screenplay.json, prompts.json, episode.md) and prints the episode.
Canon blocks from prompts/canon/canon_blocks.md are substituted into final prompts.
"""

import argparse
import json
import os
import random
import re
import sys
from pathlib import Path

import requests
from anthropic import Anthropic
from dotenv import load_dotenv

REPO = Path(__file__).parent.parent
SKILLS = REPO / "prompts" / "skills"
MODEL = "claude-sonnet-5"

ARTICLES = ("der ", "die ", "das ")


def load_skill(name: str) -> str:
    return (SKILLS / name).read_text(encoding="utf-8")


def fetch_words(start, randomize):
    url = os.environ["SUPABASE_URL"].rstrip("/") + "/rest/v1/words"
    h = {"apikey": os.environ["SUPABASE_SECRET_KEY"],
         "Authorization": f"Bearer {os.environ['SUPABASE_SECRET_KEY']}"}
    sel = "position,german,english,sentence_de,sentence_en,word_type"
    if randomize:
        pos = sorted(random.sample(range(1, 606), 10))
        params = {"position": f"in.({','.join(map(str, pos))})", "order": "position.asc", "select": sel}
    else:
        params = {"position": f"gte.{start or 1}", "order": "position.asc", "limit": "10", "select": sel}
    r = requests.get(url, headers=h, params=params, timeout=15)
    r.raise_for_status()
    words = r.json()
    assert len(words) == 10, f"expected 10 words, got {len(words)}"
    return words


def _s(**props):
    req = list(props)
    return {"type": "object", "properties": props, "required": req, "additionalProperties": False}

def _arr(item):
    return {"type": "array", "items": item}

STR = {"type": "string"}
INT = {"type": "integer"}

STORY_SCHEMA = _s(title_de=STR, scenario=STR, environment=STR, mains=_arr(STR), cameos=_arr(STR),
    belief_challenged=_s(character=STR, belief=STR, how=STR), hook_visual=STR, human_beat=STR,
    beats=_arr(STR), word_plan=_arr(_s(position=INT, german=STR, beat_index=INT, how_used=STR, sense_note=STR)))

SCREENPLAY_SCHEMA = _s(title_de=STR, environment=STR,
    scenes=_arr(_s(scene_number=INT, position=INT, german_word=STR, duration_s=INT, setting=STR,
                   action_en=STR, dialogue=_arr(_s(speaker=STR, german=STR, english=STR)),
                   target_word_emphasis=STR, continuity_notes=STR, learning_check=STR)))

PROMPTS_SCHEMA = _s(scenes=_arr(_s(scene_number=INT, characters_in_frame=_arr(STR), veo_flow_prompt=STR,
    seedance_prompt=STR, avoid_list=STR, continuity=_s(use_last_frame={"type": "boolean"}, reason=STR),
    reference_images=_arr(STR), dialogue_check=_arr(_s(speaker=STR, german=STR)))))


def call(client, system, user, label, schema):
    with client.messages.stream(model=MODEL, max_tokens=24000, system=system,
                                output_config={"format": {"type": "json_schema", "schema": schema}},
                                messages=[{"role": "user", "content": user}]) as stream:
        resp = stream.get_final_message()
    print(f"[{label}: {resp.usage.input_tokens} in / {resp.usage.output_tokens} out]")
    text = next(b.text for b in resp.content if b.type == "text")
    return json.loads(text)


def word_stem(g):
    w = g.lower()
    for a in ARTICLES:
        if w.startswith(a):
            return w[len(a):]
    if (w.endswith("eln") or w.endswith("ern")) and len(w) > 4:
        return w[:-1]
    if w.endswith("en") and len(w) > 4:
        return w[:-2]
    return w


def validate_screenplay(sp, words):
    problems = []
    scenes = sp.get("scenes", [])
    if len(scenes) != 10:
        problems.append(f"expected 10 scenes, got {len(scenes)}")
    by_pos = {w["position"]: w for w in words}
    seen = set()
    for sc in scenes:
        pos = sc.get("position")
        if pos not in by_pos:
            problems.append(f"scene {sc.get('scene_number')}: unknown position {pos}")
            continue
        seen.add(pos)
        text = " ".join(d.get("german", "") for d in sc.get("dialogue", [])).lower()
        if word_stem(by_pos[pos]["german"]) not in text:
            problems.append(f"scene {sc.get('scene_number')}: '{by_pos[pos]['german']}' not in its German dialogue")
        for d in sc.get("dialogue", []):
            if d.get("speaker", "").startswith("Müller") and len(d.get("german", "").split()) > 3:
                problems.append(f"scene {sc.get('scene_number')}: Müller exceeds word budget: {d['german']!r}")
    missing = set(by_pos) - seen
    if missing:
        problems.append(f"words without scenes: {sorted(missing)}")
    return problems


def substitute_canon(prompts):
    canon = (REPO / "prompts" / "canon" / "canon_blocks.md").read_text(encoding="utf-8")
    def block(header):
        m = re.search(rf"## {re.escape(header)}\n(.+?)(?=\n## |\Z)", canon, re.S)
        if not m:  # fuzzy: match by first name (e.g. "Kati" -> "Kati die Kartoffel")
            first = header.split(":")[-1].strip().split()[0]
            m = re.search(rf"## CHAR_BLOCK: {re.escape(first)}[^\n]*\n(.+?)(?=\n## |\Z)", canon, re.S)
        return m.group(1).strip() if m else f"[MISSING CANON: {header}]"
    style = block("STYLE_BLOCK")
    def sub(text):
        text = text.replace("{{STYLE_BLOCK}}", style)
        return re.sub(r"\{\{CHAR_BLOCK:([^}]+)\}\}", lambda m: block(f"CHAR_BLOCK: {m.group(1).strip()}"), text)
    for sc in prompts.get("scenes", []):
        sc["veo_flow_prompt"] = sub(sc.get("veo_flow_prompt", ""))
        sc["seedance_prompt"] = sub(sc.get("seedance_prompt", ""))
    return prompts


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--start", type=int)
    ap.add_argument("--random", action="store_true")
    ap.add_argument("--note", default="")
    args = ap.parse_args()

    load_dotenv(REPO / ".env")
    client = Anthropic()
    bible = (REPO / "resources" / "Characters-Main-Sheet.md").read_text(encoding="utf-8")
    words = fetch_words(args.start, args.random)
    print("words:", ", ".join(f"{w['position']}:{w['german']}" for w in words), "\n")

    ep_dir = REPO / "output" / "episodes" / f"ep_{words[0]['position']}-{words[-1]['position']}"
    ep_dir.mkdir(parents=True, exist_ok=True)
    log_file = REPO / "output" / "episodes" / "episode_log.json"
    ep_log = json.loads(log_file.read_text()) if log_file.exists() else []

    # SKILL 1 — story selector
    s1 = load_skill("skill-1-story-selector.md")
    s1 = (s1.replace("{{CHARACTER_BIBLE}}", bible)
            .replace("{{WORDS_JSON}}", json.dumps(words, ensure_ascii=False))
            .replace("{{EPISODE_LOG}}", json.dumps(ep_log[-5:], ensure_ascii=False))
            .replace("{{JAYON_DIRECTIVE}}", args.note or "(none)"))
    story = call(client, s1, "Produce the story decision JSON now.", "skill-1 story", STORY_SCHEMA)
    (ep_dir / "story.json").write_text(json.dumps(story, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"→ {story.get('title_de')} | {story.get('scenario')} | mains: {story.get('mains')}\n")

    # SKILL 2 — screenplay (validate → one retry)
    s2 = load_skill("skill-2-screenplay-writer.md")
    s2 = (s2.replace("{{CHARACTER_BIBLE}}", bible)
            .replace("{{WORDS_JSON}}", json.dumps(words, ensure_ascii=False))
            .replace("{{STORY_JSON}}", json.dumps(story, ensure_ascii=False)))
    sp = call(client, s2, "Produce the screenplay JSON now.", "skill-2 screenplay", SCREENPLAY_SCHEMA)
    problems = validate_screenplay(sp, words)
    if problems:
        print("! screenplay validation failed, retrying with feedback:")
        for p in problems:
            print("  -", p)
        sp = call(client, s2, "Your previous attempt failed validation:\n"
                  + "\n".join(problems) + "\nFix these issues. Produce the corrected screenplay JSON now.",
                  "skill-2 retry", SCREENPLAY_SCHEMA)
        problems = validate_screenplay(sp, words)
    (ep_dir / "screenplay.json").write_text(json.dumps(sp, ensure_ascii=False, indent=2), encoding="utf-8")

    # SKILL 3 — prompt writer + mechanical canon substitution
    s3 = load_skill("skill-3-prompt-writer.md")
    s3 = s3.replace("{{SCREENPLAY_JSON}}", json.dumps(sp, ensure_ascii=False))
    prompts = call(client, s3, "Produce the prompts JSON now.", "skill-3 prompts", PROMPTS_SCHEMA)
    prompts = substitute_canon(prompts)
    (ep_dir / "prompts.json").write_text(json.dumps(prompts, ensure_ascii=False, indent=2), encoding="utf-8")

    # pretty episode.md for Jayon's review
    md = [f"# {sp.get('title_de', story.get('title_de'))}\n",
          f"Scenario: {story.get('scenario')} · Environment: {sp.get('environment')}",
          f"Mains: {', '.join(story.get('mains', []))} · Cameos: {', '.join(story.get('cameos', []))}",
          f"Hook: {story.get('hook_visual')}\nHuman beat: {story.get('human_beat')}\n"]
    for sc in sp.get("scenes", []):
        md.append(f"\n## Scene {sc['scene_number']} — {sc['german_word']} ({sc['duration_s']}s)")
        md.append(f"*{sc['setting']}*\n\n{sc['action_en']}\n")
        for d in sc.get("dialogue", []):
            md.append(f"- **{d['speaker']}:** „{d['german']}“  *({d.get('english','')})*")
        md.append(f"\n> learns: {sc.get('learning_check','')}")
        pr = next((p for p in prompts.get("scenes", []) if p.get("scene_number") == sc["scene_number"]), {})
        if pr:
            md.append(f"\n<details><summary>Veo/Flow prompt</summary>\n\n```\n{pr.get('veo_flow_prompt','')}\n```\n</details>")
    (ep_dir / "episode.md").write_text("\n".join(md), encoding="utf-8")

    # episode log (context for future runs)
    ep_log.append({"positions": [w["position"] for w in words], "title": story.get("title_de"),
                   "scenario": story.get("scenario"), "mains": story.get("mains")})
    log_file.write_text(json.dumps(ep_log, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"\n{'='*60}\nSaved to {ep_dir.relative_to(REPO)}/ (story, screenplay, prompts, episode.md)")
    if problems:
        print(f"⚠ STILL FAILING after retry:")
        for p in problems:
            print("  -", p)
    else:
        print("✓ validation passed — read episode.md and judge the quality")


if __name__ == "__main__":
    main()

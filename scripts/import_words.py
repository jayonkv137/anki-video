"""Import the Anki deck export into the Supabase `words` table.

Usage:
  python scripts/import_words.py --dry-run   # parse + validate only, print report
  python scripts/import_words.py             # validate, then upsert into Supabase

Deck row format (tab-separated, 3 fields):
  front: "21   Adverb   zurück   rWeg   eRichtung ...   Ich komme morgen zurück."
  back:  "21   back (direction)        I'll come back tomorrow."
  tag:   "Adverb"
Parts inside a field are separated by runs of 2+ spaces; single spaces occur
inside values ("die Tasche", sentences), which is why we split on 2+ only.
"""

import os
import re
import sys
from pathlib import Path

import requests
from dotenv import load_dotenv

DECK_FILE = Path(__file__).parent.parent / "00 Deutsch 605 Wörter.txt"
BATCH_SIZE = 100

MULTISPACE = re.compile(r"\s{2,}")


def parse_row(line: str, line_no: int, problems: list[str]) -> dict | None:
    fields = line.split("\t")
    if len(fields) != 3:
        problems.append(f"line {line_no}: expected 3 tab-fields, got {len(fields)}")
        return None
    front, back, tag = fields

    f = MULTISPACE.split(front.strip())
    b = MULTISPACE.split(back.strip())

    # front: [position, word_type, german, *related..., sentence_de]
    if len(f) < 4:
        problems.append(f"line {line_no}: front too short: {f!r}")
        return None
    if not f[0].isdigit():
        problems.append(f"line {line_no}: front position not a number: {f[0]!r}")
        return None

    # back: [position, english, sentence_en]  (english may itself hold the middle)
    if len(b) < 2 or not b[0].isdigit():
        problems.append(f"line {line_no}: back malformed: {b!r}")
        return None

    row = {
        "position": int(f[0]),
        "word_type": f[1],
        "german": f[2],
        "related_raw": " | ".join(f[3:-1]) if len(f) > 4 else None,
        "sentence_de": f[-1] if len(f) > 3 else None,
        "english": " ".join(b[1:-1]) if len(b) > 2 else b[1],
        "sentence_en": b[-1] if len(b) > 2 else None,
    }

    if int(b[0]) != row["position"]:
        problems.append(f"line {line_no}: front/back position mismatch {f[0]} vs {b[0]}")
    if tag.strip() and tag.strip() != row["word_type"]:
        problems.append(f"line {line_no}: tag {tag.strip()!r} != type {row['word_type']!r} (keeping type)")

    return row


def parse_deck() -> tuple[list[dict], list[str]]:
    lines = DECK_FILE.read_text(encoding="utf-8").splitlines()
    problems: list[str] = []
    rows: list[dict] = []
    for i, line in enumerate(lines, start=1):
        if not line.strip() or line.startswith("#"):
            continue
        row = parse_row(line, i, problems)
        if row:
            rows.append(row)

    positions = [r["position"] for r in rows]
    dupes = {p for p in positions if positions.count(p) > 1}
    if dupes:
        problems.append(f"duplicate positions: {sorted(dupes)}")
    return rows, problems


def report(rows: list[dict], problems: list[str]) -> None:
    print(f"parsed rows : {len(rows)}")
    if rows:
        print(f"positions   : {min(r['position'] for r in rows)}..{max(r['position'] for r in rows)}")
        types: dict[str, int] = {}
        for r in rows:
            types[r["word_type"]] = types.get(r["word_type"], 0) + 1
        print(f"word types  : {types}")
        print("sample row  :", rows[20])
    print(f"problems    : {len(problems)}")
    for p in problems:
        print("  !", p)


def upsert(rows: list[dict]) -> None:
    load_dotenv()
    url = os.environ["SUPABASE_URL"].rstrip("/") + "/rest/v1/words"
    headers = {
        "apikey": os.environ["SUPABASE_SECRET_KEY"],
        "Authorization": f"Bearer {os.environ['SUPABASE_SECRET_KEY']}",
        "Content-Type": "application/json",
        # upsert: re-running the script updates rows instead of failing on duplicates
        "Prefer": "resolution=merge-duplicates,return=minimal",
    }
    for i in range(0, len(rows), BATCH_SIZE):
        batch = rows[i : i + BATCH_SIZE]
        resp = requests.post(url + "?on_conflict=position", json=batch, headers=headers, timeout=30)
        if resp.status_code >= 300:
            sys.exit(f"batch {i // BATCH_SIZE + 1} failed: {resp.status_code} {resp.text}")
        print(f"batch {i // BATCH_SIZE + 1}: {len(batch)} rows ok")
    print(f"done — {len(rows)} words in Supabase")


if __name__ == "__main__":
    rows, problems = parse_deck()
    report(rows, problems)
    if "--dry-run" in sys.argv:
        sys.exit(0)
    if problems:
        sys.exit("fix problems first (or re-run with --dry-run to inspect)")
    upsert(rows)

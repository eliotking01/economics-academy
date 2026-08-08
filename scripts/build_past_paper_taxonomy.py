#!/usr/bin/env python3
"""Generate past-paper-questions-data/taxonomy.json.

The past-paper question bank does not invent a topic taxonomy. It reuses the
one the site already publishes: the 166 topic records in questions-data/, grouped
by the UNITS dict in build_questions.py, under the names taken from the notes
index <h1>s.

Reusing those slugs verbatim means a past-paper topic URL is a pure function of
the matching notes URL, so the two can never drift and nothing has to be renamed
later.

Structure, mirroring how the rest of the site is organised:

    board (edexcel, aqa)
      group (Edexcel: Theme 1-4; AQA: Microeconomics, Macroeconomics)
        unit (1.1, 1.2, ...)
          topic

Boards are kept apart because the two specifications reuse each other's codes
for different things: 1.1.1 is "Economics as a Social Science" on Edexcel and
"Economic Methodology" on AQA, and 37 codes collide that way. Page URLs are
therefore /past-paper-questions/<board>/<slug>/, so a reader is never shown two
numbering systems at once.

Run:  python3 scripts/build_past_paper_taxonomy.py [--check]

Standard library only, in keeping with the rest of scripts/.
"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_questions import UNITS, spec_key, unit_of  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
QUESTIONS_DATA = ROOT / "questions-data"
OUT = ROOT / "past-paper-questions-data" / "taxonomy.json"

# Group names lifted from the <h1> of each notes index, so the question bank and
# the notes call everything exactly the same thing.
BOARDS = [
    {
        "board": "edexcel",
        "name": "Edexcel",
        "qualification": "A Level Economics A (9EC0)",
        "papersUrl": "/past-papers/edexcel/",
        "groups": [
            ("edexcel-theme-1", "theme-1", "Theme 1",
             "Introduction to Markets and Market Failure"),
            ("edexcel-theme-2", "theme-2", "Theme 2",
             "The UK Economy — Performance and Policies"),
            ("edexcel-theme-3", "theme-3", "Theme 3",
             "Business Behaviour and the Labour Market"),
            ("edexcel-theme-4", "theme-4", "Theme 4", "A Global Perspective"),
        ],
    },
    {
        "board": "aqa",
        "name": "AQA",
        "qualification": "A-level Economics (7136)",
        "papersUrl": "/past-papers/aqa/",
        "groups": [
            ("aqa-a2-micro", "microeconomics", "Microeconomics",
             "Individuals, Firms, Markets and Market Failure"),
            ("aqa-a2-macro", "macroeconomics", "Macroeconomics",
             "The National and International Economy"),
        ],
    },
]

EXPECTED = {"edexcel": 87, "aqa": 79}


def load_topics(board_dir):
    """Every topic record for one notes directory, in spec order."""
    src = QUESTIONS_DATA / board_dir
    if not src.is_dir():
        sys.exit(f"missing {src} - is this branch based on main?")

    topics = []
    for path in sorted(src.glob("*.json")):
        d = json.loads(path.read_text(encoding="utf-8"))
        notes_rel = f"revision-notes/{board_dir}/{d['slug']}.html"
        if not (ROOT / notes_rel).is_file():
            sys.exit(f"{path.name}: notes page {notes_rel} does not exist")
        topics.append(
            {
                "spec": d["spec"],
                "slug": d["slug"],
                "title": d["title"],
                "shortTitle": d["shortTitle"],
                "notesUrl": f"/{notes_rel}",
                "questionsUrl": f"/practice-questions/{board_dir}/{d['slug']}.html",
            }
        )
    topics.sort(key=lambda t: spec_key(t["spec"]))
    return topics


def build():
    boards = []
    seen = {}

    for spec in BOARDS:
        groups = []
        count = 0
        for board_dir, slug, label, name in spec["groups"]:
            topics = load_topics(board_dir)
            count += len(topics)

            for t in topics:
                key = (spec["board"], t["slug"])
                if key in seen:
                    sys.exit(f"duplicate slug {t['slug']} on {spec['board']}")
                seen[key] = True

            units = []
            for code in sorted({unit_of(t["spec"]) for t in topics}, key=spec_key):
                meta = UNITS.get((board_dir, code))
                if meta is None:
                    sys.exit(f"UNITS has no entry for ({board_dir}, {code})")
                units.append(
                    {
                        "unit": code,
                        "name": meta[0],
                        "topics": [t for t in topics if unit_of(t["spec"]) == code],
                    }
                )

            groups.append(
                {
                    "slug": slug,
                    "label": label,
                    "name": name,
                    "fullName": f"{spec['name']} {label}: {name}"
                    if label.startswith("Theme")
                    else f"{spec['name']} {label}",
                    "notesDir": board_dir,
                    "notesIndexUrl": f"/revision-notes/{board_dir}/",
                    "units": units,
                }
            )

        if count != EXPECTED[spec["board"]]:
            sys.exit(
                f"{spec['board']}: expected {EXPECTED[spec['board']]} topics, "
                f"found {count}"
            )

        boards.append(
            {
                "board": spec["board"],
                "slug": spec["board"],
                "name": spec["name"],
                "qualification": spec["qualification"],
                "papersUrl": spec["papersUrl"],
                "groups": groups,
            }
        )

    return {
        "source": (
            "Generated by scripts/build_past_paper_taxonomy.py from "
            "questions-data/*/*.json and the UNITS dict in "
            "scripts/build_questions.py. Do not hand-edit."
        ),
        "boards": boards,
    }


def summarise(data):
    total = 0
    for b in data["boards"]:
        n = sum(len(u["topics"]) for g in b["groups"] for u in g["units"])
        units = sum(len(g["units"]) for g in b["groups"])
        total += n
        print(f"  {b['name']}: {len(b['groups'])} groups, {units} units, {n} topics")
    print(f"  total: {total} topics")
    return total


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="validate, write nothing")
    args = ap.parse_args()

    data = build()
    total = summarise(data)
    if total != sum(EXPECTED.values()):
        sys.exit(f"expected {sum(EXPECTED.values())} topics, found {total}")

    if args.check:
        print("check only - nothing written")
        return

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(
        json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print(f"wrote {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()

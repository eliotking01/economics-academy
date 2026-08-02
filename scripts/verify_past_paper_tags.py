#!/usr/bin/env python3
"""Validate past-paper-questions-data/tags.json against the extraction and taxonomy.

tags.json is hand-written and the extraction is machine-written, so the two can
drift: a question id can be renamed, a topic slug mistyped, a new question added
and never tagged. This checks they still agree.

  python3 scripts/verify_past_paper_tags.py

Checks:
  1. Every extracted question has a tags entry.
  2. Every tags entry corresponds to a real extracted question.
  3. Every topic slug exists in taxonomy.json.
  4. Every question has at least one topic and one keyword.
  5. No duplicate topics within a question.

Also prints the topic coverage histogram, which is what decides how many topic
pages clear the volume gate in Phase 3.

Standard library only. Exit status is non-zero if any check fails.
"""

import collections
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = ROOT / "past-paper-questions-data"
GATE = 4  # questions a topic needs before it earns its own page in Phase 3


def main():
    taxonomy = json.loads((DATA / "taxonomy.json").read_text(encoding="utf-8"))
    valid = {
        t["slug"]: dict(t, board=b["board"], group=g["label"])
        for b in taxonomy["boards"]
        for g in b["groups"]
        for u in g["units"]
        for t in u["topics"]
    }

    questions = {}
    for board_dir in ("edexcel-a", "aqa"):
        for path in sorted((DATA / board_dir).glob("*.json")):
            for q in json.loads(path.read_text(encoding="utf-8"))["questions"]:
                questions[q["id"]] = q

    tags = json.loads((DATA / "tags.json").read_text(encoding="utf-8"))
    tags.pop("_comment", None)

    errors = []

    for qid in sorted(questions):
        if qid not in tags:
            errors.append(f"{qid}: no tags entry")

    for qid, entry in sorted(tags.items()):
        if qid not in questions:
            errors.append(f"{qid}: tagged but not in any extracted paper")
            continue
        topics = entry.get("topics", [])
        keywords = entry.get("keywords", [])
        if not topics:
            errors.append(f"{qid}: no topics")
        if not keywords:
            errors.append(f"{qid}: no keywords")
        if len(topics) != len(set(topics)):
            errors.append(f"{qid}: duplicate topic")
        for slug in topics:
            if slug not in valid:
                errors.append(f"{qid}: unknown topic slug {slug!r}")

    counts = collections.Counter(
        slug
        for qid, entry in tags.items()
        if qid in questions
        for slug in entry.get("topics", [])
    )

    print(f"{len(questions)} questions, {len(tags)} tagged")
    print(f"{len(counts)} of {len(valid)} topics have at least one question")
    print(f"{sum(1 for n in counts.values() if n >= GATE)} topics reach the "
          f"gate of {GATE} and would get a page in Phase 3")
    print()
    print("Topic coverage, most-tagged first:")
    for slug, n in counts.most_common():
        mark = "*" if n >= GATE else " "
        print(f"  {mark} {n:2}  {valid[slug]['board']:8} {valid[slug]['spec']:7} {valid[slug]['title']}")

    untagged = [s for s in valid if s not in counts]
    print(f"\n{len(untagged)} topics have no question yet.")

    if errors:
        print(f"\n{len(errors)} error(s):", file=sys.stderr)
        for e in errors:
            print(f"  {e}", file=sys.stderr)
        sys.exit(1)
    print("\nall tag checks passed")


if __name__ == "__main__":
    main()

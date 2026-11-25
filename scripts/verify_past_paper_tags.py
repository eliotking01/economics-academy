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
  6. Every topic belongs to the question's own board: an Edexcel B question
     tagged with an Edexcel A slug passes check 3 and is still wrong.

Every extracted board is checked, including one whose bank is not live yet
(Edexcel B, staged until Phase 4's launch): its tags are written before its
pages, and a bad slug is cheaper to catch now. Only live boards count towards
the gate, because only they get topic pages.

Also prints the topic coverage histogram, which is what decides how many topic
pages clear the volume gate (build_past_paper_questions.GATE).

Standard library only. Exit status is non-zero if any check fails.
"""

import collections
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = ROOT / "past-paper-questions-data"

# Imported, not restated. This file carried its own `GATE = 4` until
# 2026-08-24, when the gate moved to 2 and the copy here would have gone on
# reporting the old number - a verifier printing a stale figure is worse than
# one that prints none. The generator is the single declaration; a verifier
# importing a generator is the verify_boards.py pattern (the ban in
# scripts/CLAUDE.md runs the other way).
sys.path.insert(0, str(ROOT / "scripts"))
from build_past_paper_questions import BANK_DIRS, GATE  # noqa: E402
import board_data  # noqa: E402

# Every directory an extractor writes, live, staged or neither: all of
# BANK_DIRS, not build_past_paper_questions.paper_dirs(), which follows
# boards.json. This verifier must see a board's tags before the build reads
# them.
BOARD_DIRS = tuple(d for dirs in BANK_DIRS.values() for d in dirs)


def main():
    taxonomy = json.loads((DATA / "taxonomy.json").read_text(encoding="utf-8"))
    valid = {
        t["slug"]: dict(t, board=b["board"], group=g["label"])
        for b in taxonomy["boards"]
        for g in b["groups"]
        for u in g["units"]
        for t in u["topics"]
    }

    live = {b["slugs"]["taxonomy"] for b in board_data.load("pastPaperBank").values()}
    # Multiple-choice records (Phase 7) count towards a page only where the
    # board's pastPaperMcqs family is live; staged ones count as "would".
    mcq_live = {b["slugs"]["taxonomy"]
                for b in board_data.load("pastPaperMcqs").values()}

    questions = {}
    board_of = {}
    for board_dir in BOARD_DIRS:
        for path in sorted((DATA / board_dir).glob("*.json")):
            paper = json.loads(path.read_text(encoding="utf-8"))
            for q in paper["questions"]:
                questions[q["id"]] = q
                board_of[q["id"]] = paper["board"]

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
            elif valid[slug]["board"] != board_of[qid]:
                errors.append(f"{qid}: topic {slug!r} is {valid[slug]['board']}'s, "
                              f"not {board_of[qid]}'s")

    counts = collections.Counter(
        slug
        for qid, entry in tags.items()
        if qid in questions
        for slug in entry.get("topics", [])
    )
    # What the live build publishes: a board in the bank, and an MCQ only
    # once its board's MCQs are live.
    published = collections.Counter(
        slug
        for qid, entry in tags.items()
        if qid in questions and board_of[qid] in live
        and (questions[qid].get("type") != "mcq" or board_of[qid] in mcq_live)
        for slug in entry.get("topics", [])
    )

    print(f"{len(questions)} questions, {len(tags)} tagged")
    print(f"{len(counts)} of {len(valid)} topics have at least one question")
    print(f"{sum(1 for n in published.values() if n >= GATE)} "
          f"topics reach the gate of {GATE} and have their own page")
    staged_mcqs = sum(1 for qid, q in questions.items()
                      if q.get("type") == "mcq" and board_of[qid] not in mcq_live)
    if staged_mcqs:
        n = sum(1 for s, c in counts.items()
                if c >= GATE and published[s] < GATE and valid[s]["board"] in live)
        print(f"  {staged_mcqs} multiple-choice questions are staged: "
              f"{n} more topics would reach the gate once they launch")
    for board in sorted({valid[s]["board"] for s in counts} - live):
        n = sum(1 for s, c in counts.items() if c >= GATE and valid[s]["board"] == board)
        print(f"  {board} is not in the bank yet: {n} of its topics would reach the gate")
    print()
    print("Topic coverage, most-tagged first (* = has its own page, + = would, once launched):")
    for slug, n in counts.most_common():
        mark = " " if n < GATE else ("*" if published[slug] >= GATE else "+")
        print(f"  {mark} {n:2}  {valid[slug]['board']:9} {valid[slug]['spec']:7} {valid[slug]['title']}")

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

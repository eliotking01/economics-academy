#!/usr/bin/env python3
"""Hold the past-paper bank's payloads under a byte budget.

    python3 scripts/verify_payload_budget.py

WHY

Nothing capped any of these until 2026-11-27. The master `questions.json` went
from 877 KB to 1,526 KB across two November launches (Phases 7 and 9), and the
AQA board payload from 441 KB to 721 KB, each shipped as measured because no
check said a step had happened (PROGRESS "Still open - housekeeping"). The
November health check (`seo/23` §3 and §B2) mapped the weight, split the
section pages onto their own payloads, and Eliot chose a failing check over a
warning (2026-11-27).

WHAT IT CHECKS

Every file in each class, gzip-compressed (level 6, close to what GitHub Pages
serves; measured served bytes run ~4% above it), against one ceiling per class:

    master   past-paper-questions/questions.json
    board    past-paper-questions/<board>/questions.json
    section  past-paper-questions/<board>/<section>/questions.json
    topic    past-paper-questions/<board>/<topic>/questions.json
    section-html  past-paper-questions/<board>/<section>/index.html

A section is a directory under a board whose name does not start with a digit
(`theme-1`, `microeconomics`); a topic's does (`1-2-3-...`). Each ceiling was
set at roughly 1.5x the largest file in its class on 2026-11-27, so ordinary
growth passes and a step change fails.

A FAILURE IS A PROMPT TO DECIDE, NOT A BUG

It is the one verifier here that fails on growth rather than on a defect. When
it fails, either raise the ceiling below in the same commit, with a dated
line saying why, or split or trim the payload. Do not raise it silently.

Standard library only.
"""

from __future__ import annotations

import gzip
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
BANK = REPO / "past-paper-questions"

KB = 1024

# Ceilings in gzip bytes. Largest file on 2026-11-27 in the comment.
CEILINGS = {
    "master": 384 * KB,        # 251 KB
    "board": 192 * KB,         # 126 KB (aqa)
    "section": 112 * KB,       # 70 KB (aqa/microeconomics)
    "topic": 24 * KB,          # 11 KB (aqa/2-5-1-fiscal-policy)
    "section-html": 160 * KB,  # 112 KB (aqa/microeconomics)
}


def classify(rel: Path) -> str | None:
    """The budget class of a path relative to past-paper-questions/, or None."""
    parts = rel.parts
    if parts == ("questions.json",):
        return "master"
    if len(parts) == 2 and parts[1] == "questions.json":
        return "board"
    if len(parts) == 3 and parts[2] in ("questions.json", "index.html"):
        is_topic = parts[1][:1].isdigit()
        if parts[2] == "questions.json":
            return "topic" if is_topic else "section"
        return None if is_topic else "section-html"
    return None


def gzip_size(path: Path) -> int:
    return len(gzip.compress(path.read_bytes(), compresslevel=6, mtime=0))


def main() -> int:
    found: dict[str, list[tuple[int, Path]]] = {k: [] for k in CEILINGS}
    for path in sorted(BANK.rglob("*")):
        if not path.is_file():
            continue
        cls = classify(path.relative_to(BANK))
        if cls:
            found[cls].append((gzip_size(path), path))

    failures = 0
    for cls, ceiling in CEILINGS.items():
        files = found[cls]
        if not files:
            print(f"FAIL  {cls}: no files found - has the bank moved?")
            failures += 1
            continue
        largest, where = max(files)
        over = [(n, p) for n, p in files if n > ceiling]
        status = "FAIL" if over else "ok  "
        print(f"{status}  {cls:13} {len(files):4} file(s), largest "
              f"{largest / KB:6.1f} KB gz of {ceiling / KB:.0f} KB "
              f"({where.relative_to(REPO)})")
        for n, p in over:
            print(f"        over by {(n - ceiling) / KB:.1f} KB: {p.relative_to(REPO)}")
        failures += bool(over)

    if failures:
        print("\nPAYLOAD BUDGET EXCEEDED - raise the ceiling in this file with a "
              "dated reason, or split the payload. See the docstring.")
        return 1
    print("\npayload budget OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())

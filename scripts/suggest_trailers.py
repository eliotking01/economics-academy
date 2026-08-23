#!/usr/bin/env python3
"""Print the exact Text-Change:/Markup-Change: trailers a pending commit needs.

    python3 scripts/suggest_trailers.py            # staged changes vs HEAD
    python3 scripts/suggest_trailers.py --comment  # same, each line prefixed "# "

WHY THIS EXISTS
---------------
CI runs verify_text_integrity.py and verify_markup_integrity.py --strict
against the previous commit and fails on any visible-text or markup loss the
commit message did not declare with a trailer. Working out WHICH paths to
declare meant running both checks after committing, reading their diffs and
amending - and a trailer missed on a pushed commit cannot be fixed. This asks
the same two scripts the same question BEFORE the commit exists, over the
staged files only, and prints nothing but the trailer lines:

    Text-Change: about.html
    Markup-Change: revision-notes/edexcel-theme-1/1-2-2-demand.html

.githooks/prepare-commit-msg appends them to the commit template as comments
(with --comment), so they are a suggestion to uncomment, never a declaration
made on your behalf. An undeclared change still fails CI, which is the point.

Prints nothing and exits 0 when no trailer is needed. Always exits 0: this is
advice, not a gate.

Standard library only.
"""

from __future__ import annotations

import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent


def lines_from(script: str, *flags: str) -> list[str]:
    proc = subprocess.run(
        [sys.executable, f"scripts/{script}", "--staged", "--trailers", *flags],
        cwd=ROOT, capture_output=True, text=True,
    )
    if proc.returncode != 0:
        return []   # advisory: a broken check must not block a commit
    return [l for l in proc.stdout.splitlines() if l.strip()]


def suggestions() -> list[str]:
    out = lines_from("verify_text_integrity.py")
    # --strict, because that is what CI runs.
    out += lines_from("verify_markup_integrity.py", "--strict")
    return out


def main(argv) -> int:
    comment = "--comment" in argv
    for line in suggestions():
        print(("# " if comment else "") + line)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

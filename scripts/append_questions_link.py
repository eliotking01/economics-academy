#!/usr/bin/env python3
"""Add the 'Test yourself on this topic' block to a notes page.

Purely additive, and the only thing in this project that touches a
pre-existing notes page. The script inserts a fixed block of markup
immediately after the page's existing .notes-cta div and does nothing
else - it never parses, reflows or rewrites prose. Scripted paragraph
rebuilds have destroyed <a> tags in this repo before; see CLAUDE.md.

Idempotent: a page that already carries the block is left untouched, so
the script is safe to re-run over the whole site.

Verify afterwards, against the commit before the run:

    python3 scripts/verify_text_integrity.py <before-ref>
    python3 scripts/verify_markup_integrity.py <before-ref> --strict

Usage:
    python3 scripts/append_questions_link.py                    # every set
    python3 scripts/append_questions_link.py aqa-a2-micro/1-3-2.json
    python3 scripts/append_questions_link.py --dry-run
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "questions-data"
NOTES_DIR = ROOT / "revision-notes"

ANCHOR = '<div class="notes-cta">'
MARKER = '<div class="notes-questions-link">'


def find_close(text, start):
    """Index just past the </div> that closes the div opening at `start`."""
    depth = 0
    i = start
    while i < len(text):
        open_at = text.find("<div", i)
        close_at = text.find("</div>", i)
        if close_at == -1:
            return -1
        if open_at != -1 and open_at < close_at:
            depth += 1
            i = open_at + 4
            continue
        depth -= 1
        if depth == 0:
            return close_at + len("</div>")
        i = close_at + len("</div>")
    return -1


def block(topic, indent):
    pad = " " * indent
    href = f"/practice-questions/{topic['boardDir']}/{topic['slug']}.html"
    label = f"{topic['spec']} {topic['shortTitle']}"
    return (
        f"\n"
        f'{pad}<div class="notes-questions-link">\n'
        f"{pad}  <h2>Test yourself on this topic</h2>\n"
        f"{pad}  <p>{topic['notesTeaser']}</p>\n"
        f"{pad}  <a\n"
        f'{pad}    href="{href}"\n'
        f'{pad}    class="button primary"\n'
        f"{pad}    >Practice Questions: {label}</a\n"
        f"{pad}  >\n"
        f"{pad}</div>"
    )


def apply(topic, dry_run=False):
    page = NOTES_DIR / topic["boardDir"] / f"{topic['slug']}.html"
    rel = page.relative_to(ROOT)

    if not page.is_file():
        return f"MISSING  {rel}"

    text = page.read_text(encoding="utf-8")

    if MARKER in text:
        return f"skipped  {rel} (already linked)"

    start = text.find(ANCHOR)
    if start == -1:
        return f"NO ANCHOR  {rel} (no .notes-cta div)"
    if text.find(ANCHOR, start + 1) != -1:
        return f"AMBIGUOUS  {rel} (more than one .notes-cta)"

    end = find_close(text, start)
    if end == -1:
        return f"UNCLOSED  {rel} (.notes-cta never closes)"

    line_start = text.rfind("\n", 0, start) + 1
    indent = start - line_start

    updated = text[:end] + block(topic, indent) + text[end:]
    if not dry_run:
        page.write_text(updated, encoding="utf-8")
    return f"{'would add' if dry_run else 'added   '} {rel}"


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("sources", nargs="*", help="paths relative to questions-data/")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)

    paths = (
        [DATA_DIR / s for s in args.sources]
        if args.sources
        else sorted(DATA_DIR.glob("*/*.json"))
    )
    if not paths:
        print("no question sources found", file=sys.stderr)
        return 1

    problems = 0
    for path in paths:
        if not path.is_file():
            print(f"no such source: {path}", file=sys.stderr)
            problems += 1
            continue
        topic = json.loads(path.read_text(encoding="utf-8"))
        result = apply(topic, dry_run=args.dry_run)
        if result.split()[0].isupper():
            problems += 1
        print(result)

    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())

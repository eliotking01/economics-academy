#!/usr/bin/env python3
"""Add the 'Past paper questions on this topic' block to a notes page.

Purely additive, and modelled directly on scripts/append_questions_link.py,
which does the same job for the practice questions. The script inserts one
fixed block of markup after the page's existing linked block and does nothing
else - it never parses, reflows or rewrites prose. Scripted paragraph rebuilds
have destroyed <a> tags in this repo before; see CLAUDE.md.

The block reuses the .notes-questions-link class so it needs no new CSS in the
shared notes stylesheet. The extra .notes-past-papers-link class is a marker
only, used to detect a page that already carries the block.

Where a topic has its own generated page the link goes there. The topics with
questions but too few for a page link to the master search filtered to them,
via ?topic=<slug>, which js/components/question-search.js reads.

Idempotent: a page that already carries the block is left untouched, so the
script is safe to re-run over the whole site.

Verify afterwards, against the commit before the run:

    python3 scripts/verify_text_integrity.py <before-ref>
    python3 scripts/verify_markup_integrity.py <before-ref> --strict

Usage:
    python3 scripts/append_past_papers_link.py             # every tagged topic
    python3 scripts/append_past_papers_link.py --dry-run
    python3 scripts/append_past_papers_link.py 3-4-5-monopoly
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
INDEX = ROOT / "past-paper-questions" / "questions.json"
NOTES_DIR = ROOT / "revision-notes"

# Insert after the practice-questions block where there is one, so the two
# related links sit together; otherwise after the page's own CTA.
ANCHORS = ['<div class="notes-questions-link">', '<div class="notes-cta">']
MARKER = "notes-past-papers-link"


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


def year_span(index, questions):
    years = sorted({index["papers"][q["p"]]["year"] for q in questions})
    return str(years[0]) if years[0] == years[-1] else f"{years[0]}&ndash;{years[-1]}"


# The existing practice-questions block opens "Eight original multiple-choice
# questions...", so small numbers are spelled out here too.
WORDS = {
    1: "One", 2: "Two", 3: "Three", 4: "Four", 5: "Five", 6: "Six",
    7: "Seven", 8: "Eight", 9: "Nine", 10: "Ten", 11: "Eleven", 12: "Twelve",
}


def sentence(index, slug, topic, questions):
    n = len(questions)
    marks = sorted({q["marks"] for q in questions})
    span = year_span(index, questions)

    if n == 1:
        return (
            f"One question on {topic['title']} from the Edexcel A-Level papers, "
            f"{span}, worth {marks[0]} marks. It links straight to the page of "
            f"the official mark scheme where its answer begins."
        )

    if len(marks) == 1:
        tariff = f"{marks[0]} marks each"
    else:
        tariff = f"{marks[0]} to {marks[-1]} marks"
    return (
        f"{WORDS.get(n, n)} questions on {topic['title']} from the Edexcel "
        f"A-Level papers, {span}, {tariff}. Each one links straight to the page "
        f"of the official mark scheme where its answer begins."
    )


def block(index, slug, topic, questions, indent):
    pad = " " * indent
    if topic["hasPage"]:
        href = f"/past-paper-questions/{slug}/"
    else:
        href = f"/past-paper-questions/?topic={slug}"
    label = f"{topic['spec']} {topic['shortTitle']}"
    return (
        f"\n"
        f'{pad}<div class="notes-questions-link {MARKER}">\n'
        f"{pad}  <h2>Past paper questions on this topic</h2>\n"
        f"{pad}  <p>{sentence(index, slug, topic, questions)}</p>\n"
        f"{pad}  <a\n"
        f'{pad}    href="{href}"\n'
        f'{pad}    class="button primary"\n'
        f"{pad}    >Past Paper Questions: {label}</a\n"
        f"{pad}  >\n"
        f"{pad}</div>"
    )


def apply(index, slug, dry_run=False):
    topic = index["topics"][slug]
    rel_notes = topic["notesUrl"].lstrip("/")
    page = ROOT / rel_notes

    if not page.is_file():
        return f"MISSING  {rel_notes}"

    text = page.read_text(encoding="utf-8")
    questions = [q for q in index["questions"] if slug in q["topics"]]

    # A block that is already there is refreshed, not skipped. Both halves of it
    # go stale as the bank grows: the count and year span change, and a topic
    # that crosses the gate needs its link repointed from ?topic= to its own
    # page. Replacing in place keeps this a pure function of the data.
    if MARKER in text:
        block_start = text.rfind("<div", 0, text.index(MARKER))
        block_end = find_close(text, block_start)
        if block_end == -1:
            return f"UNCLOSED  {rel_notes} (existing block never closes)"
        line_start = text.rfind("\n", 0, block_start) + 1
        indent = block_start - line_start
        # The block template opens with a newline and the indent; the slice
        # being compared starts at "<div", so both are stripped off.
        fresh = block(index, slug, topic, questions, indent).lstrip("\n ")
        current = text[block_start:block_end]
        if current == fresh:
            return f"current  {rel_notes}"
        updated = text[:block_start] + fresh + text[block_end:]
        if not dry_run:
            page.write_text(updated, encoding="utf-8")
        return f"{'would refresh' if dry_run else 'refreshed'} {rel_notes}"

    start = -1
    for anchor in ANCHORS:
        found = text.find(anchor)
        if found == -1:
            continue
        if text.find(anchor, found + 1) != -1:
            return f"AMBIGUOUS  {rel_notes} (more than one {anchor})"
        start = found
        break
    if start == -1:
        return f"NO ANCHOR  {rel_notes} (no .notes-questions-link or .notes-cta)"

    end = find_close(text, start)
    if end == -1:
        return f"UNCLOSED  {rel_notes} (anchor div never closes)"

    line_start = text.rfind("\n", 0, start) + 1
    indent = start - line_start

    updated = text[:end] + block(index, slug, topic, questions, indent) + text[end:]
    if not dry_run:
        page.write_text(updated, encoding="utf-8")
    return f"{'would add' if dry_run else 'added   '} {rel_notes}"


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("slugs", nargs="*", help="topic slugs; default is all tagged")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)

    if not INDEX.is_file():
        sys.exit("run scripts/build_past_paper_questions.py first")
    index = json.loads(INDEX.read_text(encoding="utf-8"))

    slugs = args.slugs or sorted(
        index["topics"],
        key=lambda s: [int(p) for p in index["topics"][s]["spec"].split(".")],
    )

    problems = 0
    added = 0
    for slug in slugs:
        if slug not in index["topics"]:
            print(f"UNKNOWN  {slug}", file=sys.stderr)
            problems += 1
            continue
        result = apply(index, slug, args.dry_run)
        print(result)
        if result.split()[0].isupper():
            problems += 1
        elif result.startswith(("added", "would add", "refreshed", "would refresh")):
            added += 1

    print(f"\n{added} page(s) {'would be ' if args.dry_run else ''}written, "
          f"{problems} problem(s)")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())

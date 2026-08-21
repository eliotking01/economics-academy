#!/usr/bin/env python3
"""Prove the previous/next chain is complete and that the tree agrees with it.

    python3 scripts/verify_notes_sequence.py
    python3 scripts/verify_notes_sequence.py --verbose

The chain through the 166 topic pages is derived rather than stored - see
scripts/notes_sequence.py - which removes the risk of a stored copy drifting
and replaces it with a different one: the chain is only as good as the three
things it is derived from. This is what holds those three together.

Five assertions, each over the whole set rather than a sample:

  1  every notes directory has a place in exactly one chain, and every
     directory a chain names exists
  2  every topic page is in the sequence, and the sequence names no page that
     does not exist - the hub's links, the .json records and the .html slices
     must be the same set, per directory
  3  no duplicate hub links, and the hub's order is natural numeric order
  4  each chain's length is the board's own declared expectedTopics
  5  the committed tree agrees: exactly two topic-nav rows on each of the 166
     topic pages, with the hrefs the sequence computes, and none at all on any
     other published page

WHY 5 IS NOT REDUNDANT WITH verify_generated.py

That script proves the committed tree is what the generators produce. This one
proves the generators produce the right thing, which is a different question:
a bug in notes_sequence.py would give a wrong-but-consistent tree and
verify_generated.py would pass it. Assertion 5 also catches the leak the other
four cannot see - navigation appearing on a page that is out of scope, such as
a hub, the glossary or the diagram galleries.

Exit status is non-zero if any assertion fails. Standard library only.
"""

from __future__ import annotations

import argparse
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import notes_sequence  # noqa: E402

NOTES = ROOT / "revision-notes"

# One <nav> opening tag, and the href of each of its two links.
NAV_OPEN = re.compile(r'<nav\s+class="topic-nav topic-nav--(top|bottom)"')
NAV_BLOCK = re.compile(r"<nav\s+class=\"topic-nav\b.*?</nav>", re.S)
NAV_HREF = re.compile(r'class="topic-nav__link topic-nav__link--(prev|next)[^"]*"\s*\n\s*href="([^"]+)"')

failures: list[str] = []


def check(name: str, problems: list[str], verbose: bool = False) -> None:
    if problems:
        failures.append(name)
        print(f"FAIL  {name} - {len(problems)} problem(s)")
        for line in problems[:40]:
            print(f"        {line}")
        if len(problems) > 40:
            print(f"        ... and {len(problems) - 40} more")
    else:
        print(f"ok    {name}")


def a1_directories_are_placed(chains) -> list[str]:
    """Every notes directory in exactly one chain, and every chain dir real."""
    problems = []
    placed: dict[str, str] = {}
    for chain in chains:
        for notes_dir in chain.dirs:
            if notes_dir in placed:
                problems.append(
                    f"{notes_dir} is in both the {placed[notes_dir]} and "
                    f"{chain.board_key} chains")
            placed[notes_dir] = chain.board_key
            if not (notes_sequence.TOPICS / notes_dir).is_dir():
                problems.append(f"{chain.board_key} names {notes_dir}, which "
                                f"has no notes-data/topics/ directory")
            if not (notes_sequence.HUBS / f"{notes_dir}.html").is_file():
                problems.append(f"{chain.board_key} names {notes_dir}, which "
                                f"has no notes-data/hubs/ slice")
    for src in sorted(notes_sequence.TOPICS.iterdir()):
        if src.is_dir() and src.name not in placed:
            problems.append(
                f"notes-data/topics/{src.name}/ exists but no chain includes "
                f"it - add it to a board's groups[] in boards-data/boards.json "
                f"and to EXPECTED_NOTES_DIRS in scripts/board_data.py")
    return problems


def a2_every_topic_is_in_the_sequence(chains) -> list[str]:
    """Hub links, .json records and .html slices are the same set."""
    problems = []
    for chain in chains:
        for notes_dir in chain.dirs:
            hub = {slug for slug, _ in notes_sequence.hub_topics(notes_dir)}
            src = notes_sequence.TOPICS / notes_dir
            records = {p.stem for p in src.glob("*.json")}
            slices = {p.stem for p in src.glob("*.html")}
            for slug in sorted(records - hub):
                problems.append(
                    f"{notes_dir}/{slug} has a record but the hub does not "
                    f"link to it, so it has no place in the sequence")
            for slug in sorted(hub - records):
                problems.append(
                    f"{notes_dir}/{slug} is linked from the hub but has no "
                    f"notes-data record - the sequence names a page that does "
                    f"not exist")
            for slug in sorted(records ^ slices):
                problems.append(
                    f"{notes_dir}/{slug} has a .json without a .html or the "
                    f"other way round")
    return problems


def a3_order_is_numeric(chains) -> list[str]:
    """No duplicate hub links, and hub order is spec-code order."""
    problems = []
    for chain in chains:
        for notes_dir in chain.dirs:
            order = [slug for slug, _ in notes_sequence.hub_topics(notes_dir)]
            seen = set()
            for slug in order:
                if slug in seen:
                    problems.append(f"{notes_dir}/{slug} is linked twice from "
                                    f"its hub")
                seen.add(slug)
            expected = sorted(order, key=notes_sequence.natural_key)
            if order != expected:
                first = next(a for a, b in zip(order, expected) if a != b)
                problems.append(
                    f"{notes_dir}: the hub's link order is not spec-code "
                    f"order; first disagreement at {first}. A plain string "
                    f"sort would put 1-2-10 before 1-2-2, so these two "
                    f"orderings must not be allowed to diverge")
    return problems


def a4_chain_lengths(chains) -> list[str]:
    """Each chain is as long as its board says it is."""
    problems = []
    for chain in chains:
        if len(chain.entries) != chain.expected:
            problems.append(
                f"{chain.board_key}: chain has {len(chain.entries)} pages, "
                f"boards.json declares expectedTopics {chain.expected}")
    return problems


def a5_tree_agrees(chains, verbose: bool) -> list[str]:
    """The committed pages carry the rows the sequence computes, and only there."""
    problems = []
    expected_pages: dict[str, tuple[str, str]] = {}
    for chain in chains:
        for notes_dir, slug, _ in chain.entries:
            expected_pages[f"revision-notes/{notes_dir}/{slug}.html"] = \
                (notes_dir, slug)

    for page in sorted(NOTES.rglob("*.html")):
        rel = str(page.relative_to(ROOT))
        source = page.read_text(encoding="utf-8")
        positions = NAV_OPEN.findall(source)

        if rel not in expected_pages:
            if positions:
                problems.append(
                    f"{rel} carries topic navigation and is out of scope - "
                    f"only the 166 topic pages may have it")
            continue

        if positions != ["top", "bottom"]:
            problems.append(f"{rel} has topic-nav rows {positions or 'none'}, "
                            f"expected ['top', 'bottom']")
            continue

        notes_dir, slug = expected_pages[rel]
        top, bottom = notes_sequence.rows(notes_dir, slug)
        want = {kind: href for kind, href in NAV_HREF.findall(top)}
        if len(want) != 2:
            problems.append(f"{rel}: could not read both hrefs out of the "
                            f"generated row - the row's shape has changed and "
                            f"NAV_HREF in this script needs updating with it")
            continue
        for block in NAV_BLOCK.findall(source):
            got = {kind: href for kind, href in NAV_HREF.findall(block)}
            if got != want:
                problems.append(f"{rel}: page links {got}, sequence says {want}")
        if verbose:
            print(f"      {rel}: prev={want['prev']} next={want['next']}")
    return problems


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--verbose", action="store_true",
                    help="print every page's resolved neighbours")
    args = ap.parse_args(argv[1:])

    chains = notes_sequence.chains()

    check("1 every notes directory is placed in exactly one chain",
          a1_directories_are_placed(chains))
    check("2 every topic is in the sequence, and the sequence is all real",
          a2_every_topic_is_in_the_sequence(chains))
    check("3 hub order is spec-code order, with no duplicates",
          a3_order_is_numeric(chains))
    check("4 each chain is its board's declared length",
          a4_chain_lengths(chains))
    check("5 the committed tree carries the computed rows, and only there",
          a5_tree_agrees(chains, args.verbose))

    total = sum(len(c.entries) for c in chains)
    print(f"\n{len(chains)} chains, {total} topic pages, "
          f"{5 - len(failures)}/5 assertions passed")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))

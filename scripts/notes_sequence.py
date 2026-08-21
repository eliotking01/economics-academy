#!/usr/bin/env python3
"""The previous/next chain through the 166 topic pages, derived from data.

    python3 scripts/notes_sequence.py            # print both chains
    python3 scripts/notes_sequence.py --row edexcel-theme-1/1-1-2-positive-normative-statements

Imported by build_notes_pages.py, which injects the rows, and by
verify_notes_sequence.py, which proves the chain is complete and that the
committed tree agrees with it. One definition, two consumers.

NOTHING IS STORED. THE CHAIN IS DERIVED FROM WHAT ALREADY DECIDES IT
--------------------------------------------------------------------
A checked-in sequence file would be a fourth copy of an ordering that three
other things already state, and copies here drift invisibly - docs/HISTORY.md
is largely a record of exactly that. So each part comes from whatever already
owns it:

  which directories, in what order   boards-data/boards.json `groups[]`, via
                                     scripts/board_data.py, whose own guard
                                     already fails if that order moves
  which topics, in what order        the hub page's own link order, read from
                                     notes-data/hubs/<dir>.html
  the label for a topic              that hub link's own anchor text
  the label for a theme hub          the group's `practiceQuestionsLabel`
  how many topics a chain has        the board's `expectedTopics` (87 / 79)

Reusing the hub's anchor text is deliberate and is the reason this feature
writes no new economics wording: every topic label already exists as visible
text on the hub, curated in specification wording. See CLAUDE.md hard rule 2.
The only new words on the page are the three captions below.

TWO CHAINS, NEVER JOINED
------------------------
Edexcel A runs theme 1 -> 2 -> 3 -> 4 as one continuous chain of 87 pages, and
AQA runs micro -> macro as one continuous chain of 79. Links cross sub-theme
and theme boundaries inside a chain and never cross between chains: the two
boards are meant to rank for board-specific queries and a cross-board link
would undo that (DO-NOT-BREAK.md, "Board differentiation").

Slugs are NOT unique across boards - `2-1-1-...` exists in both
edexcel-theme-2 and aqa-a2-macro - so everything here is keyed on
(notes_dir, slug), never on slug or spec code alone. Same rule as
DO-NOT-BREAK.md's "Spec code is not a key".

Standard library only.
"""

from __future__ import annotations

import argparse
import html
import pathlib
import re
import sys
from html.parser import HTMLParser

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import board_data  # noqa: E402

DATA = ROOT / "notes-data"
HUBS = DATA / "hubs"
TOPICS = DATA / "topics"

# The three new visible strings this feature introduces, approved 2026-08-21.
# Not economics wording; kept here so all three are in one place rather than
# spelled out at each of the four call sites below.
CAPTION_PREV = "Previous topic"
CAPTION_NEXT = "Next topic"
CAPTION_HUB = "Topic list"

# Text arrows, never Font Awesome. css/fontawesome-all.min.css is a SUBSET and
# adding a glyph needs fonttools + brotli, which CI does not have; a missing
# glyph then renders as nothing at all, silently. The breadcrumb already sets
# the precedent with a bare `&rsaquo;`.
ARROW_PREV = "&larr;"
ARROW_NEXT = "&rarr;"

# A hub link on a notes hub page: /revision-notes/<dir>/<slug>.html
TOPIC_HREF = re.compile(r"^/revision-notes/([a-z0-9-]+)/([a-z0-9-]+)\.html$")

# Every topic slug opens with its spec code, e.g. 1-2-10-alternative-views.
# Checked across all 166 before this was relied on.
SPEC_PREFIX = re.compile(r"^(\d+)-(\d+)-(\d+)-")


def natural_key(slug: str) -> tuple[int, int, int]:
    """Sort key for a topic slug, by spec code and not as a string.

    A plain string sort puts `1-2-10-alternative-views` before `1-2-2-demand`,
    and AQA micro runs as far as 1-8-10, so the difference is real rather than
    theoretical. Nothing here sorts by this - the hub's own order is what is
    used - but verify_notes_sequence.py asserts the two agree, which is what
    stops them diverging later.
    """
    m = SPEC_PREFIX.match(slug)
    if not m:
        sys.exit(f"notes_sequence: slug {slug!r} does not open with a spec code")
    return tuple(int(part) for part in m.groups())


class _HubLinks(HTMLParser):
    """Topic links on a hub page, in document order."""

    def __init__(self, notes_dir: str):
        super().__init__(convert_charrefs=True)
        self.notes_dir = notes_dir
        self.links: list[tuple[str, list[str]]] = []
        self._depth = 0

    def handle_starttag(self, tag, attrs):
        if tag != "a":
            if self._depth:
                self._depth += 1
            return
        if self._depth:
            self._depth += 1
            return
        href = dict(attrs).get("href") or ""
        m = TOPIC_HREF.match(href)
        if m and m.group(1) == self.notes_dir:
            self.links.append((m.group(2), []))
            self._depth = 1

    def handle_endtag(self, tag):
        if self._depth:
            self._depth -= 1

    def handle_data(self, data):
        if self._depth:
            self.links[-1][1].append(data)

    def result(self) -> list[tuple[str, str]]:
        # convert_charrefs=True has already turned `&amp;` back into `&`, and
        # the hub wraps long labels across lines, so collapse the whitespace.
        return [(slug, re.sub(r"\s+", " ", "".join(parts)).strip())
                for slug, parts in self.links]


def hub_topics(notes_dir: str) -> list[tuple[str, str]]:
    """(slug, label) for one directory, in the hub's own link order."""
    path = HUBS / f"{notes_dir}.html"
    if not path.is_file():
        sys.exit(f"notes_sequence: missing {path.relative_to(ROOT)} - every "
                 f"notes directory needs a hub slice to take its order from")
    parser = _HubLinks(notes_dir)
    parser.feed(path.read_text(encoding="utf-8"))
    parser.close()
    links = parser.result()
    if not links:
        sys.exit(f"notes_sequence: {path.relative_to(ROOT)} links to no topic "
                 f"pages in its own directory")
    return links


def disk_topics(notes_dir: str) -> set[str]:
    """Slugs with a record in notes-data/topics/<dir>/."""
    src = TOPICS / notes_dir
    if not src.is_dir():
        sys.exit(f"notes_sequence: missing {src.relative_to(ROOT)}")
    return {p.stem for p in src.glob("*.json")}


class Chain:
    """One board's run of topic pages, front to back."""

    def __init__(self, board_key: str, board: dict):
        self.board_key = board_key
        self.expected = board["expectedTopics"]
        self.dirs = [g["notesDir"] for g in board["groups"]]
        # notes_dir -> the name to show when linking back to that hub. The
        # group already carries one, and it is the same string the hub's own
        # breadcrumb ends on ("Edexcel Theme 1", "AQA Microeconomics").
        self.hub_label = {g["notesDir"]: g["names"]["practiceQuestionsLabel"]
                          for g in board["groups"]}
        self.entries: list[tuple[str, str, str]] = [
            (notes_dir, slug, label)
            for notes_dir in self.dirs
            for slug, label in hub_topics(notes_dir)
        ]
        self.index = {(notes_dir, slug): i
                      for i, (notes_dir, slug, _) in enumerate(self.entries)}


def chains() -> list[Chain]:
    """Both chains, in the order boards.json lists the boards.

    board_data.load() fails first if boards.json's board order or group order
    has moved, so the sequence cannot be reordered by an undeclared edit.
    """
    return [Chain(key, board) for key, board in board_data.load().items()]


def _slot(kind: str, href: str, title: str, rel: str | None) -> str:
    """One half of a row. `kind` is "prev" or "next"."""
    caption = CAPTION_PREV if kind == "prev" else CAPTION_NEXT
    if rel is None:
        # A hub slot. `rel="prev"`/`rel="next"` means the previous or next
        # document in the sequence, and a theme hub is not that, so it gets
        # no rel at all.
        caption = CAPTION_HUB
        spoken = f"Back to the topic list: {title}"
    else:
        spoken = f"{caption}: {title}"
    arrow = ARROW_PREV if kind == "prev" else ARROW_NEXT
    inner = (f'<span aria-hidden="true">{arrow}</span> {caption}'
             if kind == "prev"
             else f'{caption} <span aria-hidden="true">{arrow}</span>')
    classes = f"topic-nav__link topic-nav__link--{kind}"
    if rel is None:
        classes += " topic-nav__link--hub"
    rel_attr = f'\n                rel="{rel}"' if rel else ""
    return (
        f'              <a\n'
        f'                class="{classes}"\n'
        f'                href="{html.escape(href, quote=True)}"{rel_attr}\n'
        f'                aria-label="{html.escape(spoken, quote=True)}"\n'
        f'              >\n'
        f'                <span class="topic-nav__caption">{inner}</span>\n'
        f'                <span class="topic-nav__title">'
        f'{html.escape(title, quote=False)}</span>\n'
        f'              </a>\n'
    )


def _row(position: str, prev_slot: str, next_slot: str) -> str:
    """A whole row. `position` is "top" or "bottom".

    The two rows carry DIFFERENT aria-labels on purpose. They are otherwise
    identical, and two <nav> landmarks with the same accessible name is an
    axe failure ("landmarks must be unique") as well as being useless in a
    screen reader's landmark list.
    """
    where = "before" if position == "top" else "after"
    return (
        f'            <nav\n'
        f'              class="topic-nav topic-nav--{position}"\n'
        f'              aria-label="Topic navigation, {where} the notes"\n'
        f'            >\n'
        f'{prev_slot}'
        f'{next_slot}'
        f'            </nav>\n'
    )


def rows(notes_dir: str, slug: str) -> tuple[str, str]:
    """(top row, bottom row) for one topic page. Both are always two-sided."""
    for chain in chains():
        i = chain.index.get((notes_dir, slug))
        if i is None:
            continue
        if i > 0:
            d, s, label = chain.entries[i - 1]
            prev_slot = _slot("prev", f"/revision-notes/{d}/{s}.html", label, "prev")
        else:
            prev_slot = _slot("prev", f"/revision-notes/{notes_dir}/",
                              chain.hub_label[notes_dir], None)
        if i < len(chain.entries) - 1:
            d, s, label = chain.entries[i + 1]
            next_slot = _slot("next", f"/revision-notes/{d}/{s}.html", label, "next")
        else:
            next_slot = _slot("next", f"/revision-notes/{notes_dir}/",
                              chain.hub_label[notes_dir], None)
        return (_row("top", prev_slot, next_slot),
                _row("bottom", prev_slot, next_slot))
    sys.exit(f"notes_sequence: {notes_dir}/{slug} has no place in any chain. "
             f"Every topic page must be linked from its hub - run "
             f"python3 scripts/verify_notes_sequence.py for the detail.")


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--row", metavar="DIR/SLUG",
                    help="print the rows for one page instead of the chains")
    args = ap.parse_args(argv[1:])

    if args.row:
        notes_dir, _, slug = args.row.partition("/")
        top, bottom = rows(notes_dir, slug.removesuffix(".html"))
        print(top + "\n" + bottom, end="")
        return 0

    for chain in chains():
        print(f"{chain.board_key}: {len(chain.entries)} pages "
              f"(expected {chain.expected}) across {len(chain.dirs)} directories")
        prev_dir = None
        for notes_dir, slug, label in chain.entries:
            mark = "  ->" if notes_dir != prev_dir and prev_dir else "    "
            print(f"{mark} {notes_dir}/{slug}  {label}")
            prev_dir = notes_dir
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))

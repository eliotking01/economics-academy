#!/usr/bin/env python3
"""The four blocks build_notes_pages.py wraps around a topic slice.

    python3 scripts/notes_extras.py edexcel-theme-1/1-2-2-demand

A spec sub-label under the H1, stable ids on every <h2>, a table of contents
where the page has four or more sections, and a related-topics block carrying
the twin on the other board. All four are GENERATED CHROME, in the same sense
as the previous/next rows: they live here, never in notes-data/, and the byte
slices stay byte slices. notes-data/CLAUDE.md and CLAUDE.md hard rule 6.

EVERY ANCHOR AND EVERY HEADING IS EXISTING WORDING
--------------------------------------------------
Related-topic and twin anchors are the hub's own link text with the spec-code
prefix removed; table-of-contents entries are the page's own <h2> text. So
this adds no economics wording. What it does add is seven chrome strings, and
they are listed here rather than scattered through the file:

    "Updated"                     "On this page"
    "Related topics"              "Studying AQA instead?"
    "Studying Edexcel instead?"   "covers this on AQA."
    "covers this on Edexcel."

THE FOUR ANCHORS WERE MEASURED BEFORE THEY WERE RELIED ON
---------------------------------------------------------
Across all 166 slices, on 2026-08-21:

    <header class="major"> / <h1> / </header>   the same three lines, 166/166
    the spec-alert closes and a <section> opens 166/166
    exactly one <div class="notes-cta">         166/166, always after </section>
    every <h2> open tag is bare, no attributes  1,159/1,159

That last one is what makes an id insertion safe rather than a rewrite: there
is no attribute to collide with and no case to get wrong. The 688 <h2>s
before the notes-cta are the content sections and the 471 after it are the
three resource cards - measured, 0 anomalies - which is why the contents list
can be taken positionally instead of by parsing the section tree.

A slice that stops matching any of these fails the build. Silently skipping
it would ship a page missing a block nobody would notice was gone.

Standard library only.
"""

from __future__ import annotations

import argparse
import html
import pathlib
import re
import sys
from datetime import date

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import notes_sequence  # noqa: E402
import notes_twins  # noqa: E402

BOARD_OF_DIR = {
    "edexcel-theme-1": ("Edexcel", "Theme 1"),
    "edexcel-theme-2": ("Edexcel", "Theme 2"),
    "edexcel-theme-3": ("Edexcel", "Theme 3"),
    "edexcel-theme-4": ("Edexcel", "Theme 4"),
    "aqa-a2-micro": ("AQA", "Microeconomics"),
    "aqa-a2-macro": ("AQA", "Macroeconomics"),
}

# EVERY page with at least one section gets a contents list, and the reason is
# not that a two-item list is useful.
#
# The rule this started at was "four or more sections", which 95 of the 166
# pages meet. Measured, that binary split took verify_page_shell.py check 6's
# content spine from 6 shapes to 12 and produced two pages with a shape of
# their own - 1-1-3-the-economic-problem and 1-2-6-price-determination - by
# cutting two already-rare trailing-block combinations in half. That check
# exists to catch a structurally malformed page and its declared singleton set
# is empty; loosening it to fit a design choice would spend a real safety net
# on a cosmetic preference.
#
# Emitting the block on all 166 keeps the spine at exactly its six shapes and
# their six counts. The cost is four pages whose contents list has one entry:
# 1-6-3 and 1-6-6 on AQA, 4-4-1 and 4-4-3 on Edexcel. All four are among the
# thinnest on the site and all four are on the content approval list for
# expansion, which is the fix that makes the list worth reading.
MIN_SECTIONS_FOR_CONTENTS = 1

# re.S, and the <h1> is captured WHOLE rather than by its inner text. Eight
# H1s are long enough that Prettier wrapped them across three lines, and
# re-emitting one from its inner text would reflow it - a byte change to a
# heading, which is the one thing this file must not make.
HEADER_RE = re.compile(
    r"( *)<header class=\"major\">\n( *<h1>.*?</h1>\n)( *)</header>\n", re.S)
SPEC_CLOSE_RE = re.compile(
    r"(<div class=\"spec-alert\">.*?</div>\n)(\n*)( *)(<section>)", re.S)
CTA_RE = re.compile(r"( *)<div class=\"notes-cta\">")
H2_RE = re.compile(r"<h2>(.*?)</h2>", re.S)
CODE_PREFIX_RE = re.compile(r"^\d+(?:\.\d+)+\s+")
TAG_RE = re.compile(r"<[^>]+>")

MONTHS = ("January", "February", "March", "April", "May", "June", "July",
          "August", "September", "October", "November", "December")


def fail(where: str, what: str) -> None:
    sys.exit(f"notes_extras: {where}: {what}")


def plain(fragment: str) -> str:
    return " ".join(html.unescape(TAG_RE.sub(" ", fragment)).split())


def slugify(text: str) -> str:
    s = re.sub(r"[^a-z0-9]+", "-", plain(text).lower()).strip("-")
    return s or "section"


def long_date(iso: str) -> str:
    """2026-08-13 -> 13 August 2026. UK order, no ordinal suffix."""
    y, m, d = (int(x) for x in iso.split("-"))
    return f"{d} {MONTHS[m - 1]} {date(y, m, d).year}"


def topic_name(label: str) -> str:
    """A hub link's anchor text with its spec-code prefix removed.

    The hub writes "1.2.2 Demand". The code is what students do not search -
    4 impressions in 28 days across the whole site - so an internal anchor
    spends its words on the name. The name itself is the hub's, unchanged.
    """
    return CODE_PREFIX_RE.sub("", label).strip()


def label_for(notes_dir: str, slug: str) -> str:
    for s, label in notes_sequence.hub_topics(notes_dir):
        if s == slug:
            return topic_name(label)
    fail(f"{notes_dir}/{slug}", "the hub does not link to it, so it has no label")


# ---------------------------------------------------------------- sub-label

def sub_label(slice_html: str, notes_dir: str, slug: str, code: str,
              modified: str) -> str:
    """Insert board / module / code and the update date under the <h1>.

    §6 of the brief: the code stays visible for a student checking they are on
    the right page, without spending title or heading weight on it. The
    separators are aria-hidden because "Edexcel middle dot Theme 1" is not
    what a screen reader should say.
    """
    m = HEADER_RE.search(slice_html)
    if not m:
        fail(f"{notes_dir}/{slug}", "no <header class=\"major\"> wrapping a "
                                    "single <h1>")
    board, module = BOARD_OF_DIR[notes_dir]
    pad = m.group(1)
    dot = '<span aria-hidden="true"> · </span>'
    block = (
        f'{pad}<header class="major">\n'
        f'{m.group(2)}'
        f'{pad}  <p class="topic-meta">\n'
        f'{pad}    <span class="topic-meta__spec"'
        f' aria-label="{board} {module}, unit {code}"\n'
        f'{pad}      >{board}{dot}{module}{dot}{code}</span\n'
        f'{pad}    >\n'
        f'{pad}    <span class="topic-meta__updated"\n'
        f'{pad}      >Updated <time datetime="{modified}">'
        f'{long_date(modified)}</time></span\n'
        f'{pad}    >\n'
        f'{pad}  </p>\n'
        f'{pad}</header>\n'
    )
    return slice_html[:m.start()] + block + slice_html[m.end():]


# ------------------------------------------------------- ids and a contents

def with_h2_ids(slice_html: str, notes_dir: str, slug: str) -> tuple[str, list]:
    """Give every <h2> an id, and return the content headings in order.

    The id is the heading's own slug, suffixed on a within-page collision so
    that two sections called "Evaluation" do not both answer to #evaluation.
    Ids are derived and not stored, so rewording a heading moves its anchor -
    which is the right trade while nothing external cites one, and is recorded
    here so a future session knows it is a choice.
    """
    cta = CTA_RE.search(slice_html)
    if not cta:
        fail(f"{notes_dir}/{slug}", "no <div class=\"notes-cta\">")
    boundary = cta.start()

    used: dict[str, int] = {}
    contents: list[tuple[str, str]] = []
    out, last = [], 0
    for m in re.finditer(r"<h2>", slice_html):
        close = slice_html.index("</h2>", m.end())
        text = slice_html[m.end():close]
        base = slugify(text)
        used[base] = used.get(base, 0) + 1
        ident = base if used[base] == 1 else f"{base}-{used[base]}"
        out.append(slice_html[last:m.start()])
        out.append(f'<h2 id="{ident}">')
        last = m.end()
        if m.start() < boundary:
            contents.append((ident, plain(text)))
    out.append(slice_html[last:])
    return "".join(out), contents


def contents_block(contents: list[tuple[str, str]], pad: str) -> str:
    items = "".join(
        f'{pad}    <li><a href="#{ident}">{html.escape(text, quote=False)}</a></li>\n'
        for ident, text in contents)
    return (
        f'{pad}<nav class="topic-contents" aria-labelledby="topic-contents-label">\n'
        f'{pad}  <p class="topic-contents__label" id="topic-contents-label">'
        f'On this page</p>\n'
        f'{pad}  <ol class="topic-contents__list">\n'
        f'{items}'
        f'{pad}  </ol>\n'
        f'{pad}</nav>\n'
    )


def with_contents(slice_html: str, notes_dir: str, slug: str,
                  contents: list[tuple[str, str]]) -> str:
    if len(contents) < MIN_SECTIONS_FOR_CONTENTS:
        return slice_html
    m = SPEC_CLOSE_RE.search(slice_html)
    if not m:
        fail(f"{notes_dir}/{slug}", "the spec-alert is not followed by a <section>")
    # The blank line between the spec-alert and the first section is kept
    # BELOW the contents block rather than above it, so the rendered page has
    # the same one-blank-line rhythm it had before.
    return (slice_html[:m.end(1)] + contents_block(contents, m.group(3))
            + slice_html[m.start(2):])


# ---------------------------------------------------------------- related

def related_slugs(notes_dir: str, slug: str, limit: int = 3) -> list[str]:
    """Up to `limit` sibling topics from the same sub-unit, nearest first.

    A sub-unit is the X.Y that a page's slug starts with, which is how both
    boards group their own topics and is the one grouping that cannot cross a
    board - the directory is part of the key. The two neighbours already
    carrying a previous/next link are skipped, because repeating them adds a
    link and no destination.
    """
    order = [s for s, _ in notes_sequence.hub_topics(notes_dir)]
    if slug not in order:
        return []
    here = order.index(slug)
    neighbours = {order[i] for i in (here - 1, here + 1) if 0 <= i < len(order)}
    def pick(candidates: list[str]) -> list[str]:
        out = [s for s in candidates if s != slug and s not in neighbours]
        out.sort(key=lambda s: abs(order.index(s) - here))
        return out[:limit]

    unit = "-".join(slug.split("-")[:2])
    siblings = pick([s for s in order
                     if "-".join(s.split("-")[:2]) == unit])
    if siblings:
        return siblings
    # Four topics are alone in their sub-unit once the two prev/next
    # neighbours are taken out - 3.6.1 and 3.6.2 are the whole of Edexcel
    # unit 3.6 between them. Falling back to the nearest topics anywhere in
    # the same DIRECTORY keeps the block on every page, which is what stops
    # it becoming a fifteenth content spine (verify_page_shell.py check 6),
    # and the directory is still one board so nothing can cross.
    return pick(order)


def related_block(notes_dir: str, slug: str, pad: str) -> str:
    board, _ = BOARD_OF_DIR[notes_dir]
    other = "AQA" if board == "Edexcel" else "Edexcel"
    siblings = related_slugs(notes_dir, slug)
    pair = notes_twins.twin(notes_dir, slug)
    if not siblings and not pair:
        return ""

    body = ""
    if siblings:
        items = "".join(
            f'{pad}    <li>\n'
            f'{pad}      <a href="/revision-notes/{notes_dir}/{s}.html"'
            f'>{html.escape(label_for(notes_dir, s), quote=False)}</a>\n'
            f'{pad}    </li>\n'
            for s in siblings)
        body += (f'{pad}  <ul class="topic-related__list">\n'
                 f'{items}'
                 f'{pad}  </ul>\n')
    if pair:
        tdir, tslug = pair
        name = html.escape(label_for(tdir, tslug), quote=False)
        body += (
            f'{pad}  <p class="topic-related__twin">\n'
            f'{pad}    Studying {other} instead?\n'
            f'{pad}    <a class="topic-related__twin-link"'
            f' href="/revision-notes/{tdir}/{tslug}.html">{name}</a>\n'
            f'{pad}    covers this on {other}.\n'
            f'{pad}  </p>\n')

    return (
        f'{pad}<nav class="topic-related" aria-label="Related topics">\n'
        f'{pad}  <p class="topic-related__label">Related topics</p>\n'
        f'{body}'
        f'{pad}</nav>\n'
    )


def with_related(slice_html: str, notes_dir: str, slug: str) -> str:
    m = CTA_RE.search(slice_html)
    if not m:
        fail(f"{notes_dir}/{slug}", "no <div class=\"notes-cta\">")
    block = related_block(notes_dir, slug, m.group(1))
    if not block:
        return slice_html
    return slice_html[:m.start()] + block + slice_html[m.start():]


# ------------------------------------------------------------------ entry

def apply_all(slice_html: str, notes_dir: str, slug: str, code: str,
              modified: str) -> str:
    """Every block, in the order they appear down the page."""
    out = sub_label(slice_html, notes_dir, slug, code, modified)
    out, contents = with_h2_ids(out, notes_dir, slug)
    out = with_contents(out, notes_dir, slug, contents)
    return with_related(out, notes_dir, slug)


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("page", help="<notes-dir>/<slug>")
    args = ap.parse_args(argv)
    notes_dir, slug = args.page.split("/")
    src = ROOT / "notes-data" / "topics" / notes_dir / f"{slug}.html"
    body = src.read_text(encoding="utf-8")
    code = re.search(r"unit\s+(\d+(?:\.\d+)+)", body).group(1)
    print(apply_all(body, notes_dir, slug, code, "2026-08-13"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

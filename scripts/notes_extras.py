#!/usr/bin/env python3
"""The blocks build_notes_pages.py wraps around a topic slice.

    python3 scripts/notes_extras.py edexcel-theme-1/1-2-2-demand

A spec sub-label and an author byline under the H1, stable ids on every <h2>,
a table of contents, and - after the last section - THE TAIL: a related-topics
block carrying the twin on the other board, the three free next steps as one
"Carry on with this topic" unit, an "About the author" rule and one services
sentence. Since the notes redesign (2026-08-25, D61) also two per-instance
attribute transforms: a class on each definition paragraph and the scrollable-
region attributes on each table container - see with_definition_cards() and
with_table_regions(). All of them are GENERATED CHROME, in the same sense as
the previous/next rows: they live here, never in notes-data/, and the byte
slices stay byte slices. notes-data/CLAUDE.md and CLAUDE.md hard rule 6.

THE TAIL IS DERIVED, NOT STORED (2026-08-23)
--------------------------------------------
Until the topic-tail redesign every slice ENDED with a "Ready to apply these
notes?" button box and two or three resource blocks - quiz, flashcards, past
paper questions - written into the slice by two one-off scripts
(append_questions_link.py, append_past_papers_link.py, both retired). The
past-paper block said how many questions the bank held and from which years,
and 24 of 139 were wrong by the time anyone looked, because the scripts wrote
into rendered pages the next build overwrote. So the tail is now a pure
function of the data that the linked pages are themselves built from:

    quiz            questions-data/<dir>/<spec>.json   count, notesTeaser,
                                                        spec + shortTitle
    flashcards      FLASHCARDS_OF_DIR below             the deck per directory
    past papers     past-paper-questions-data/          tags.json + every
                                                        extracted paper, the
                                                        same files the index is
                                                        built from; GATE too
    board hub       PAST_PAPERS_HUB below
    diagram gallery the slice's own <p class="notes-diagrams-link">, verbatim,
                    re-homed as the unit's last line (47 Edexcel pages)
    services        SERVICES below, Eliot's approved sentence

The legacy tail was stripped from all 166 slices in the same change, so a
slice now ends at its last </section> (plus that one optional paragraph) and
the container close. A slice carrying anything else there fails the build.

EVERY ANCHOR AND EVERY HEADING IS EXISTING WORDING
--------------------------------------------------
Related-topic and twin anchors are the hub's own link text with the spec-code
prefix removed; table-of-contents entries are the page's own <h2> text; the
quiz line is the topic's own notesTeaser. So this adds no economics wording.
What it does add is chrome, and it is listed here rather than scattered
through the file - every string below was approved by Eliot, the first nine
on 2026-08-21, the rest on 2026-08-23 with the tail redesign:

    "Updated"                     "On this page"
    "Related topics"              "Studying AQA instead?"
    "Studying Edexcel instead?"   "covers this on AQA."
    "covers this on Edexcel."     "Written by"
    "About the author"
    "Carry on with this topic"
    "Practice questions: <spec> <shortTitle>"
    "Flashcards: <spec> <shortTitle>"
    "The <deck> deck filtered to this topic - definitions, diagrams and
     chains of reasoning, with your progress saved on this device."
    "Past paper questions: <spec> <shortTitle>"
    the derived past-paper line - past_paper_note() - e.g. "Five questions
     from the Edexcel A-Level papers, 2017-2024, 4 to 25 marks, each linked
     to the page of the official mark scheme where its answer begins."
    "Whole papers and mark schemes: <Board> past papers."
    "<Board> past papers" / "Question papers and mark schemes for every
     <Board> A-Level and AS paper, by paper and year."  (no tagged questions)
    SERVICES - the one paid sentence, two links
    "Scrollable table" - an aria-label on each table container, added by
     with_table_regions() (2026-08-25, D61); an attribute, not visible text

plus the byline and the bio themselves, the AUTHOR_* constants below. Those
are Eliot's own words about himself - supplied and approved on 2026-08-22,
task 4 of seo/15-notes-seo-manual-todo-2026-08-21.md - and every claim in
them is already on about.html. They describe the author, not economics.

THE ANCHORS WERE MEASURED BEFORE THEY WERE RELIED ON
----------------------------------------------------
Across all 166 slices, on 2026-08-21 and again after the strip on 2026-08-23:

    <header class="major"> / <h1> / </header>   the same three lines, 166/166
    the spec-alert closes and a <section> opens 166/166
    the slice ends </section> [+ one diagrams  166/166
      paragraph] + the container close
    every <h2> open tag is bare, no attributes  688/688

That last one is what makes an id insertion safe rather than a rewrite: there
is no attribute to collide with and no case to get wrong. Every <h2> in a
slice is now a content heading (the 471 resource-card <h2>s went with the
legacy tail), so the contents list is simply every <h2>.

A slice that stops matching any of these fails the build. Silently skipping
it would ship a page missing a block nobody would notice was gone.

Standard library only, plus one import from scripts/build_past_paper_questions.py
for the bank's source files and its volume gate.
"""

from __future__ import annotations

import argparse
import functools
import html
import json
import pathlib
import re
import sys
import textwrap
from datetime import date

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import build_past_paper_questions as ppq  # noqa: E402
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

# The flashcard deck each notes directory's topics belong to: the URL the
# old per-page block linked (measured 166/166 before the strip, one deck per
# directory, always filtered with ?topic=<slug>) and the deck's name as the
# old block's sentence gave it ("the Theme 1 deck", "the AQA macroeconomics
# deck"). Build fails if the deck's index page is not in the tree.
FLASHCARDS_OF_DIR = {
    "edexcel-theme-1": ("/flashcards/edexcel-a/theme-1/", "Theme 1"),
    "edexcel-theme-2": ("/flashcards/edexcel-a/theme-2/", "Theme 2"),
    "edexcel-theme-3": ("/flashcards/edexcel-a/theme-3/", "Theme 3"),
    "edexcel-theme-4": ("/flashcards/edexcel-a/theme-4/", "Theme 4"),
    "aqa-a2-micro": ("/flashcards/aqa/micro/", "AQA microeconomics"),
    "aqa-a2-macro": ("/flashcards/aqa/macro/", "AQA macroeconomics"),
}

# The board's past-papers hub. This link is DO-NOT-BREAK: it was the first
# button of the old notes-cta and P5 measured the board-named notes-cta as
# load-bearing differentiation between the near-identical Edexcel/AQA pairs.
# It is still on every page, per page, naming the board - now as the last
# sentence of the past-paper panel (or the panel itself where the topic has
# no tagged questions yet).
PAST_PAPERS_HUB = {"Edexcel": "/past-papers/edexcel/", "AQA": "/past-papers/aqa/"}
BOARD_SLUG = {"Edexcel": "edexcel", "AQA": "aqa"}

# The one paid sentence, approved by Eliot on 2026-08-23. The two anchor
# phrases are the SEO point of the tail redesign - the money pages used to
# get only button copy ("Book a Free Intro Call") from 166 pages - and the
# "free 15-minute intro call" is tutoring.html's own description of it.
SERVICES = (
    'Stuck on this topic? Work through it with an\n'
    '{pad}  <a href="/tutoring.html">online A-Level Economics tutor</a> in a free\n'
    '{pad}  15-minute intro call, or send an essay on it for\n'
    '{pad}  <a href="/marking.html">A-Level Economics essay marking</a>.'
)

# The author. Eliot's own words, supplied and approved in chat on 2026-08-22
# (seo/15-notes-seo-manual-todo-2026-08-21.md task 4). This is the ONE place
# the byline and the bio live: seo/tools/rewrite_notes_meta.py imports
# AUTHOR_NAME, AUTHOR_URL and AUTHOR_JOB_TITLE for the LearningResource
# `author` node, and seo/tools/verify_seo.py assertion 20 fails if the page and
# its schema stop naming the same person.
#
# AUTHOR_URL is a real fragment - about.html carries id="eliot-king" on its
# profile section and verify_links.py resolves it - and it is also the @id
# that about.html, index.html, tutoring.html, marking.html and contact.html
# already give the Person node. So the byline, the bio and the schema all
# point at one identity, which is the whole point of a byline for search.
AUTHOR_NAME = "Eliot King"
AUTHOR_URL = "/about.html#eliot-king"
AUTHOR_JOB_TITLE = "A-Level Economics Tutor"
# The three credential items in the byline, in the order Eliot supplied them,
# joined with the same middle dot the sub-label uses. "BSc (Hons) Economics"
# is the order about.html's credentials list and its Person node already use.
AUTHOR_CREDENTIALS = (
    "First-Class BSc (Hons) Economics, University of Bath",
    "6+ years teaching A-Level Economics",
    "Edexcel A, Edexcel B, AQA and OCR",
)
# The bio, minus its opening "Eliot King", which the box renders as the link.
# Adapted from about.html's opening paragraph: third person, and the four
# boards named; nothing else is new. "Over six years" is the prose form of the
# byline's "6+ years", which is also how about.html puts it.
AUTHOR_BIO_TAIL = (
    "is a First-Class BSc (Hons) Economics graduate from the University of "
    "Bath and the founder of Economics Academy. Eliot has taught A-Level "
    "Economics for over six years across Edexcel A, Edexcel B, AQA and OCR, "
    "supporting over 100 students with a particular focus on the exam "
    "technique and essay structure that mark schemes reward."
)

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
H2_RE = re.compile(r"<h2>(.*?)</h2>", re.S)
# How every topic slice ends, measured 166/166: the container close, and
# before it either the last </section> or the one optional diagram-gallery
# paragraph. build_notes_pages.with_topic_nav() checks the same close.
CONTAINER_CLOSE = "\n          </div>"
DIAGRAMS_RE = re.compile(
    r'\n*( *)<p class="notes-diagrams-link">\n(.*?\n)\1</p>\n?$', re.S)
# The indent every tail block is emitted at: the slice's own <section> indent.
TAIL_PAD = "            "
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
    """Insert board / module / code, the update date and the byline under the <h1>.

    §6 of the brief: the code stays visible for a student checking they are on
    the right page, without spending title or heading weight on it. The
    separators are aria-hidden because "Edexcel middle dot Theme 1" is not
    what a screen reader should say.

    The byline is the third line of the heading group, after the sub-label:
    name linked to the about page, then the three credential items. Every
    site that outranks these pages on their own queries prints one - the
    brief §2 and §7 - and until 2026-08-22 these 166 did not.
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
        f'{pad}  <p class="topic-byline">\n'
        f'{pad}    Written by\n'
        f'{pad}    <a class="topic-byline__name" href="{AUTHOR_URL}"'
        f' rel="author">{AUTHOR_NAME}</a>\n'
        f'{pad}    <span class="topic-byline__credentials"\n'
        f'{pad}      >— {" · ".join(AUTHOR_CREDENTIALS)}</span\n'
        f'{pad}    >\n'
        f'{pad}  </p>\n'
        f'{pad}</header>\n'
    )
    return slice_html[:m.start()] + block + slice_html[m.end():]


# ------------------------------------------------------- ids and a contents

def with_h2_ids(slice_html: str, notes_dir: str, slug: str) -> tuple[str, list]:
    """Give every <h2> an id, and return the headings in order.

    Every <h2> in a slice is a content heading since the legacy tail went
    (2026-08-23); before that the three resource cards had to be cut off
    at the notes-cta. The id is the heading's own slug, suffixed on a within-page collision so
    that two sections called "Evaluation" do not both answer to #evaluation.
    Ids are derived and not stored, so rewording a heading moves its anchor -
    which is the right trade while nothing external cites one, and is recorded
    here so a future session knows it is a choice.
    """
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


# -------------------------------------------- definition cards and tables

# A paragraph whose FIRST content is a key-definition chip - the same "chip
# opens the block" reading extract_glossary.py uses to tell a definition from
# a mid-sentence highlight, so the card set and the glossary agree by
# construction. Measured across all 166 slices on 2026-08-25 (PLAN.md §2):
# 641 chips; 540 open a bare <p> and become cards; 0 chip-first paragraphs
# carry any attribute on the <p>; 22 open an <li> and 79 sit mid-sentence,
# and both of those stay inline highlights - a card inside a bullet list
# breaks the list's rhythm. Every chip is spelled exactly
# <span class="key-definition" (0 variants), so the lookahead is the anchor.
DEFINITION_P_RE = re.compile(r'<p>(?=\s*<span class="key-definition")')

# The scroll container every comparison table sits in, spelled exactly this
# way in all 122 instances (measured 2026-08-25, 0 with extra classes). The
# added attributes make the scrollable region reachable and named for
# keyboard users; the CSS edge fades are the visual cue.
TABLE_CONTAINER_OPEN = '<div class="table-container">'
TABLE_CONTAINER_REGION = ('<div class="table-container" tabindex="0" '
                          'role="region" aria-label="Scrollable table">')


def with_definition_cards(slice_html: str) -> str:
    """Class each chip-opening paragraph so the sheet can render it as a card.

    Tolerant by construction, not strict: a chip anywhere else - mid-sentence,
    in a list item, in a paragraph that already carries an attribute - simply
    keeps its inline colour treatment. There is nothing to fail; a hand edit
    cannot break this, only opt out of the card look.
    """
    return DEFINITION_P_RE.sub('<p class="topic-definition">', slice_html)


def with_table_regions(slice_html: str) -> str:
    """Make each table container a labelled, keyboard-focusable region.

    A container with an unexpected class list is left alone - it still
    renders and still scrolls, losing only the keyboard focus stop. A
    degradation, not a trap: the pattern here is exactly the snippet
    revision-notes/CLAUDE.md and docs/EDITING-NOTES.md say to paste.
    """
    return slice_html.replace(TABLE_CONTAINER_OPEN, TABLE_CONTAINER_REGION)


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


# ----------------------------------------------------------------- author

def author_block(pad: str) -> str:
    """The "About the author" block: the bio, with the name linked to about.html.

    An <aside>, because it is about the page rather than part of it, labelled
    by its own visible heading-like <p> in the same way .topic-contents and
    .topic-related are - a real <h2> here would be the 1,160th on the site
    and would land in the contents list and the heading counts for nothing.
    """
    bio = textwrap.fill(AUTHOR_BIO_TAIL, width=76,
                        initial_indent=f"{pad}    ",
                        subsequent_indent=f"{pad}    ")
    return (
        f'{pad}<aside class="topic-author" aria-labelledby="topic-author-label">\n'
        f'{pad}  <p class="topic-author__label" id="topic-author-label">'
        f'About the author</p>\n'
        f'{pad}  <p class="topic-author__bio">\n'
        f'{pad}    <a class="topic-author__name" href="{AUTHOR_URL}"'
        f' rel="author">{AUTHOR_NAME}</a>\n'
        f'{bio}\n'
        f'{pad}  </p>\n'
        f'{pad}</aside>\n'
    )


# ------------------------------------------------------------- next steps

WORDS = {1: "One", 2: "Two", 3: "Three", 4: "Four", 5: "Five", 6: "Six",
         7: "Seven", 8: "Eight", 9: "Nine", 10: "Ten", 11: "Eleven",
         12: "Twelve"}


@functools.lru_cache(maxsize=None)
def quiz_records(notes_dir: str) -> dict[str, dict]:
    """slug -> the topic's questions-data record, for one notes directory."""
    out = {}
    for path in sorted((ROOT / "questions-data" / notes_dir).glob("*.json")):
        rec = json.loads(path.read_text(encoding="utf-8"))
        out[rec["slug"]] = rec
    return out


def quiz_record(notes_dir: str, slug: str) -> dict:
    rec = quiz_records(notes_dir).get(slug)
    if rec is None:
        fail(f"{notes_dir}/{slug}", "no questions-data record for this slug - "
             "every topic page needs its practice questions (scripts/new_topic.py "
             "step 4) before it can be built")
    return rec


@functools.lru_cache(maxsize=None)
def past_paper_bank() -> dict[str, list[tuple[int, str, int]]]:
    """slug -> [(year, level, marks), ...] for every PUBLISHED tagged question.

    Read from the bank's source files through ppq.load_bank(), not from
    past-paper-questions/questions.json: that index is written by a generator
    that runs AFTER this one (site_layout.GENERATORS), so reading it would
    make the notes pages a function of the previous build. The two
    conditions for counting - tagged, and with a mark scheme - are the two
    under which build_past_paper_questions.build() publishes a question, and
    scripts/tests/test_notes_extras.py checks the counts agree with the
    committed index.
    """
    tags, papers = ppq.load_bank()
    out: dict[str, list[tuple[int, str, int]]] = {}
    for paper in papers:
        for q in paper["questions"]:
            tag = tags.get(q["id"])
            if tag is None or q["markScheme"] is None:
                continue
            for s in tag["topics"]:
                out.setdefault(s, []).append((paper["year"], paper["level"], q["marks"]))
    return out


def past_paper_note(board: str, qs: list[tuple[int, str, int]]) -> str:
    """The derived line under the past-paper link. Every number comes from
    the bank, so it cannot go stale; the topic name is left out because the
    link above it already carries it."""
    n = len(qs)
    years = sorted({y for y, _, _ in qs})
    levels = {lvl for _, lvl, _ in qs}
    marks = sorted({m for _, _, m in qs})
    if levels == {"a-level"}:
        papers = f"{board} A-Level papers"
    elif levels == {"as-level"}:
        papers = f"{board} AS papers"
    else:
        papers = f"{board} A-Level and AS papers"
    span = (str(years[0]) if years[0] == years[-1]
            else f"{years[0]}&ndash;{years[-1]}")
    if n == 1:
        return (f"One question from the {papers}, {span}, worth {marks[0]} marks, "
                f"linked to the page of the official mark scheme where its "
                f"answer begins.")
    tariff = (f"{marks[0]} marks each" if len(marks) == 1
              else f"{marks[0]} to {marks[-1]} marks")
    return (f"{WORDS.get(n, n)} questions from the {papers}, {span}, {tariff}, "
            f"each linked to the page of the official mark scheme where its "
            f"answer begins.")


def next_item(pad: str, href: str, label: str, note: str) -> str:
    """One panel. The note is one line, however long: wrapping it would put
    a line break inside the <a> some notes carry, which is legal HTML and
    exactly the kind of reflow this repo has learnt not to do to prose."""
    return (
        f'{pad}    <li class="topic-next__item">\n'
        f'{pad}      <a class="topic-next__link" href="{href}">{label}</a>\n'
        f'{pad}      <p class="topic-next__note">{note}</p>\n'
        f'{pad}    </li>\n'
    )


def next_steps_block(notes_dir: str, slug: str, pad: str, diagrams: str) -> str:
    """The three free next steps as one unit, then the diagram-gallery line.

    Quiz, flashcards, past-paper questions - in that order, one panel each,
    every count and label derived. The third panel is the topic's own
    past-paper questions where the bank has any (its page if it clears the
    gate, the master search filtered to it if not) and closes with the
    board's past-papers hub; a topic with no tagged questions gets the hub as
    the panel itself, so the board link is on every page either way.
    """
    board, _ = BOARD_OF_DIR[notes_dir]
    hub = PAST_PAPERS_HUB[board]
    quiz = quiz_record(notes_dir, slug)
    name = html.escape(f'{quiz["spec"]} {quiz["shortTitle"]}', quote=False)

    items = next_item(
        pad, f"/practice-questions/{notes_dir}/{slug}.html",
        f"Practice questions: {name}", html.escape(quiz["notesTeaser"], quote=False))

    deck_url, deck = FLASHCARDS_OF_DIR[notes_dir]
    if not (ROOT / deck_url.lstrip("/") / "index.html").is_file():
        fail(f"{notes_dir}/{slug}", f"flashcard deck {deck_url} is not in the tree")
    items += next_item(
        pad, f"{deck_url}?topic={slug}", f"Flashcards: {name}",
        f"The {deck} deck filtered to this topic \u2014 definitions, diagrams and "
        f"chains of reasoning, with your progress saved on this device.")

    qs = past_paper_bank().get(slug, [])
    if qs:
        if len(qs) >= ppq.GATE:
            href = f"/past-paper-questions/{BOARD_SLUG[board]}/{slug}/"
        else:
            href = (f"/past-paper-questions/?board={BOARD_SLUG[board]}"
                    f"&amp;topic={slug}")
        items += next_item(
            pad, href, f"Past paper questions: {name}",
            past_paper_note(board, qs)
            + f' Whole papers and mark schemes: <a href="{hub}">{board} past papers</a>.')
    else:
        items += next_item(
            pad, hub, f"{board} past papers",
            f"Question papers and mark schemes for every {board} A-Level and AS "
            f"paper, by paper and year.")

    if diagrams:
        # The slice's own paragraph, byte for byte, two spaces further in.
        diagrams = "".join(f"  {line}\n" if line.strip() else "\n"
                           for line in diagrams.rstrip("\n").split("\n"))
    return (
        f'{pad}<nav class="topic-next" aria-labelledby="topic-next-label">\n'
        f'{pad}  <p class="topic-next__label" id="topic-next-label">'
        f'Carry on with this topic</p>\n'
        f'{pad}  <ul class="topic-next__list">\n'
        f'{items}'
        f'{pad}  </ul>\n'
        f'{diagrams}'
        f'{pad}</nav>\n'
    )


# --------------------------------------------------------------- services

def services_block(pad: str) -> str:
    return (f'{pad}<p class="topic-services">\n'
            f'{pad}  ' + SERVICES.format(pad=pad) + '\n'
            f'{pad}</p>\n')


# ------------------------------------------------------------------- tail

def tail_blocks(notes_dir: str, slug: str, diagrams: str) -> str:
    """Everything between the last section and the bottom prev/next row."""
    pad = TAIL_PAD
    return (
        related_block(notes_dir, slug, pad)
        + "\n"
        + next_steps_block(notes_dir, slug, pad, diagrams)
        + "\n"
        + author_block(pad)
        + "\n"
        # Newsletter signup: when Eliot has settled a sending rhythm
        # (OWNER-TODO.md, "Newsletter, ongoing"), a one-field Kit form slots
        # in HERE - after the author, before the paid sentence - as another
        # block at this pad. Not built; nothing is promised on the page.
        + services_block(pad)
    )


def with_tail(slice_html: str, notes_dir: str, slug: str) -> str:
    """Insert the tail between the slice's last block and the container close.

    The slice must end with the container close, and before it either the
    last </section> or the one optional diagram-gallery paragraph, which is
    lifted out and re-homed as the last line of the next-steps unit.
    Anything else there is a slice still carrying the legacy tail, or a new
    kind of trailing block nobody has thought about: fail, do not guess.
    """
    where = f"{notes_dir}/{slug}"
    if not slice_html.endswith(CONTAINER_CLOSE):
        fail(where, f"the slice does not end with {CONTAINER_CLOSE!r}")
    body = slice_html[:-len(CONTAINER_CLOSE)]
    diagrams = ""
    m = DIAGRAMS_RE.search(body)
    if m:
        diagrams = body[m.start():].lstrip("\n")
        body = body[:m.start()]
    if not body.rstrip("\n").endswith("</section>"):
        fail(where, "the slice does not end at its last </section> (plus at "
                    "most one <p class=\"notes-diagrams-link\">) - a slice "
                    "still carrying the legacy tail? see the module docstring")
    return (body.rstrip("\n") + "\n\n"
            + tail_blocks(notes_dir, slug, diagrams)
            + CONTAINER_CLOSE.lstrip("\n"))


# ------------------------------------------------------------------ entry

def apply_all(slice_html: str, notes_dir: str, slug: str, code: str,
              modified: str) -> str:
    """Every block, in the order they appear down the page."""
    out = sub_label(slice_html, notes_dir, slug, code, modified)
    out, contents = with_h2_ids(out, notes_dir, slug)
    out = with_contents(out, notes_dir, slug, contents)
    out = with_definition_cards(out)
    out = with_table_regions(out)
    return with_tail(out, notes_dir, slug)


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

#!/usr/bin/env python3
"""Pin the shape of every page's shell, so drift has to declare itself.

    python3 scripts/verify_page_shell.py
    python3 scripts/verify_page_shell.py --show    # print the shapes, don't judge

WHY THIS EXISTS
---------------
463 pages carry the same ~2.5 KB of `<head>`, body wrapper and script tail, and
nothing compares them. Phase 6 measured what that costs: 18 pages disagree with
themselves on a `<head>` field they write twice, 28 load the identical MathJax
asset with different markup, 341 breadcrumbs lack an `aria-label` the newest
100 have. None of it is visible, none of it is caught, and all of it arrived
one hand-written page at a time.

This is Wave 2 Phase 1 - "harden in place" - and PH06 section 3 calls it **the
cheapest 80% of the value in that document, worth doing even if the migration
is rejected**. It does not template anything. It writes down what the shell
looks like today and fails if that changes without the table below changing in
the same commit.

THE EXPECTED TABLES ARE THE POINT
---------------------------------
Every count here is a literal, in the spirit of
`build_past_paper_taxonomy.py`'s `EXPECTED = {"edexcel": 87, "aqa": 79}`, which
DO-NOT-BREAK keeps precisely because it "makes adding a board fail loudly
rather than silently emit a short taxonomy".

So a count going DOWN fails too. An improvement is welcome and must be
declared: change the page and the number together, and the diff then says what
was improved. A verifier that quietly congratulates you is one that cannot tell
an improvement from an accident.

EVERY NUMBER BELOW WAS MEASURED ON 2026-08-11, NOT COPIED
---------------------------------------------------------
Seven of PH06's eight figures survived re-derivation unchanged. One did not,
and it is recorded at check 7, because acting on it as written would have made
the site worse.

Standard library only, and deliberately self-contained: `docs/audit/scripts/`
is audit material and is excluded from publishing, so a check the workflow runs
must not import from it. The tokeniser below is `page_anatomy.py`'s method,
reimplemented here for that reason.
"""

from __future__ import annotations

import argparse
import collections
import html as htmllib
import json
import pathlib
import re
import subprocess
import sys
from html.parser import HTMLParser

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import build_sitemap  # noqa: E402  - for its _config.yml exclude parser

RUNTIME_PARTIALS = {"templates/header.html", "templates/footer.html"}


# --------------------------------------------------------------------------
# Families, as Phase 0 defined them in 00-INVENTORY.md section 4
# --------------------------------------------------------------------------

def family_of(path: str) -> str:
    if path.startswith("revision-notes/glossary/"):
        return "glossary"
    if path.startswith("revision-notes/"):
        rest = path[len("revision-notes/"):]
        if rest.endswith("/index.html") and rest.count("/") == 1:
            return "notes-hub"
        if "/" not in rest:
            return "notes-other"
        return "notes-topic"
    if path.startswith("practice-questions/"):
        return "mcq-hub" if path.endswith("/index.html") else "mcq-topic"
    if path.startswith("past-paper-questions/"):
        return "ppq"
    if path.startswith("past-papers/"):
        return "past-papers"
    if path.startswith("flashcards/"):
        return "flashcards"
    return "root"


# Families no generator writes. notes-topic and notes-hub left this list in
# Wave 2 Phases 5 and 3 - build_notes_pages.py renders all 173 of them from
# notes-data/ - and the header line below went on printing "190 of them
# hand-written" for every run afterwards. It is 17: the 9 root pages, the 5
# past-papers/ hubs and the 3 revision-notes/ non-topic pages. scripts/
# bake_templates.py owns exactly this set.
HAND_WRITTEN = ("root", "notes-other", "past-papers")

# ---- check 1 -------------------------------------------------------------
# pages, distinct <head> skeletons, body shells, script tails, stylesheet sets.
# "Distinct" means: strip every word of text, keep tag + id + class, and count
# how many different strings come out. Two pages with one skeleton differ only
# in words.
#
# notes-topic's 4 and root's 9/9/3/9 are PH06 section 1.2's table, re-derived
# here and unchanged. root SHOULD be 9 different pages - they are nine
# different pages, not a family.
EXPECTED_FAMILIES = {
    # family:        (pages, heads, shells, tails, css sets)
    "root":          (9, 9, 9, 3, 9),
    # 4 head shapes until 2026-08-13, then 3 when PH08-039's MathJax
    # convergence removed the "without id" markup, then 2 when PH08-042's
    # <style> block left 1-5-1-market-structures. 166 pages, one <head>
    # shape between them except for which of the two MathJax states they are
    # in. Declared here as well as at check 5 ON PURPOSE - the two counts are
    # measured by different code (this one tokenises the whole <head>, check
    # 5 classifies by MathJax markup), so a change moving only one of them
    # would be a real disagreement rather than a missed edit.
    "notes-topic":   (166, 2, 1, 1, 1),
    "notes-hub":     (7, 2, 2, 1, 2),
    "notes-other":   (3, 2, 3, 1, 2),
    "past-papers":   (5, 2, 2, 1, 2),
    "mcq-topic":     (166, 1, 1, 1, 1),
    "mcq-hub":       (7, 2, 2, 1, 1),
    "ppq":           (90, 1, 3, 1, 1),
    "flashcards":    (7, 2, 2, 1, 2),
    "glossary":      (3, 2, 2, 1, 2),
}

# ---- check 2 -------------------------------------------------------------
# Measured: it is not merely one tail per family, it is the same scripts in the
# same order as the FIRST scripts on all 463 pages, with six families appending
# their own. That is the stronger statement, so it is the one asserted.
#
# Wave 4.10 took this from seven to four. jquery.min.js, jquery.dropotron.min.js
# and util.js are deleted from the repo; inject-templates.js became nav.js, the
# rename D35 declined in Phase 7 because it edited 463 pages to gain a filename
# and which cost nothing here, where the tail was being rewritten on all 463
# anyway. **This is what proved the change reached every page**: 463 of 463
# carry the new tail and 0 carry any of the three removed scripts.
#
# Wave 4.11 took it from four to two: browser.min.js had zero call sites
# anywhere on the site and breakpoints.min.js had one, js/main.js's config
# call, which named four widths no listener ever read back.
#
# Restated here as a literal ON PURPOSE. It is not imported from
# page_shell.SCRIPT_TAIL, though that is now where the generators get it: a
# check that reads the value it is checking agrees with any value, including a
# wrong one. Changing the tail has to change both, in the same commit - the
# build_past_paper_taxonomy.py EXPECTED pattern.
SCRIPT_TAIL = (
    "/js/components/nav.js",
    "/js/main.js",
)

# Scripts this check must never see again. A page that kept one would still
# pass the ordering test above, because that filters to tail members and these
# are not members any more - so it is asserted separately rather than assumed.
REMOVED_SCRIPTS = (
    "/js/jquery.min.js",
    "/js/jquery.dropotron.min.js",
    "/js/util.js",
    "/js/components/inject-templates.js",
    "/js/browser.min.js",
    "/js/breakpoints.min.js",
)

#
# What a page may load after the four, and how many pages may do so.
#
# EXPECTED_INTERLEAVED was ["index.html"] until Wave 4.10 and is now empty,
# which is an improvement declared rather than absorbed. index.html put
# reviews.js and reviews-render.js between util.js and main.js; util.js is
# deleted, and bake_templates.sync_script_tail() re-emits the tail first and a
# page's own scripts after it, so the two review scripts now follow main.js.
# Nothing depends on the old position: reviews-render.js waits for
# DOMContentLoaded and reads `reviews` from js/data/reviews.js, which still
# precedes it. This check is what noticed.
EXPECTED_INTERLEAVED = []

EXPECTED_EXTRA_SCRIPTS = {
    "/js/components/quiz.js": 173,
    "/js/components/question-search.js": 90,
    "/js/components/flashcards.js": 7,
    "/js/components/glossary-filter.js": 3,
    "/js/data/reviews.js": 1,
    "/js/components/reviews-render.js": 1,
    "https://assets.calendly.com/assets/external/widget.js": 1,
}

# ---- check 3 -------------------------------------------------------------
# Fields a page writes twice must agree with themselves. PH06-029 found 18 that
# do not, all hand-written, none generated - a generator cannot disagree with
# itself. Each is a deliberately shortened social variant, so each is named
# rather than counted, and the field is named too: seventeen are og:description
# and exactly one is twitter:description.
#
# PH06 section 1.1's prose enumerates only 15 of these 18 - contact.html,
# faq.html and marking.html are missing from its list. The count 18 was right;
# the list was short. This is the list.
KNOWN_SELF_DISAGREEMENT = {
    "about.html": ("og:description", "shortened social variant"),
    "contact.html": ("og:description", "shortened social variant"),
    "faq.html": ("og:description", "shortened social variant"),
    "index.html": ("og:description", "shortened social variant"),
    "marking.html": ("og:description", "shortened social variant"),
    "tutoring.html": ("og:description", "shortened social variant"),
    "past-papers/index.html": ("og:description", "shortened social variant"),
    "past-papers/aqa/index.html": ("og:description", "shortened social variant"),
    "past-papers/edexcel/index.html": ("og:description", "shortened social variant"),
    "past-papers/edexcel-b/index.html": ("og:description", "shortened social variant"),
    "past-papers/ocr/index.html": ("og:description", "shortened social variant"),
    "revision-notes/index.html": ("og:description", "shortened social variant"),
    "revision-notes/aqa-a2-macro/index.html": ("og:description", "shortened social variant"),
    "revision-notes/aqa-a2-micro/index.html": ("og:description", "shortened social variant"),
    "revision-notes/edexcel-theme-2/index.html": ("og:description", "shortened social variant"),
    "revision-notes/edexcel-theme-3/index.html": ("og:description", "shortened social variant"),
    "revision-notes/edexcel-theme-4/index.html": ("og:description", "shortened social variant"),
    "revision-notes/macro-application/index.html": (
        "twitter:description",
        "the only one of the 18 that is twitter: rather than og:",
    ),
}

# ---- check 4 -------------------------------------------------------------
# CLAUDE.md's "a new page needs" list, as a census rather than a rule, because
# the rule is not true of every page and pretending otherwise ships a red
# check. 404.html and confirmation.html are noindex utility pages and carry
# almost none of the social furniture, correctly.
HEAD_REQUIREMENTS = {
    "gtag": r"googletagmanager\.com/gtag/js\?id=G-YVCNRW4QH6",
    "lang=en-GB": r'<html[^>]+lang="en-GB"',
    "title": r"<title[^>]*>.+?</title>",
    "meta description": r'<meta[^>]+name="description"[^>]+content="[^"]+"',
    "canonical": r'<link[^>]+rel="canonical"[^>]+href="https://economicsacademy\.co\.uk',
    "og:title": r'property="og:title"',
    "og:description": r'property="og:description"',
    "og:url": r'property="og:url"',
    "og:image": r'property="og:image"',
    "twitter:card": r'name="twitter:card"',
    "twitter:title": r'name="twitter:title"',
    "twitter:description": r'name="twitter:description"',
    "favicon": r'rel="icon"[^>]+href="/favicon\.ico"',
    "manifest": r'rel="manifest"',
    "/css/main.css": r'<link rel="stylesheet" href="/css/main\.css"',
    "a page stylesheet": r'<link rel="stylesheet" href="/css/pages/[^"]+\.css"',
    "JSON-LD": r'type="application/ld\+json"',
}

# Pages permitted to be missing each, named. Anything not named here fails.
HEAD_EXEMPT = {
    "canonical": {"404.html", "confirmation.html"},
    "og:title": {"404.html", "confirmation.html"},
    "og:description": {"404.html", "confirmation.html"},
    "og:url": {"404.html", "confirmation.html"},
    "og:image": {"404.html", "confirmation.html", "privacy.html"},
    "twitter:card": {"404.html", "confirmation.html"},
    "JSON-LD": {"404.html", "confirmation.html"},
    # WAS {"404.html"} until 2026-08-13 and is now EMPTY - a count going down,
    # declared here in the commit that moved it. 404.html was the one
    # published page with no page stylesheet, which is why wave-norm item (f)
    # had nowhere to put its 15 inline styles; css/pages/404.css now exists
    # and every one of the 463 pages carries a sheet of its own. Kept as an
    # empty set rather than deleted, so a page LOSING its stylesheet is
    # reported here rather than silently tolerated.
    "a page stylesheet": set(),
    # The 21 older hand-written pages that never gained a twitter: title or
    # description. twitter:card is present on 19 of them and Twitter falls back
    # to the og: tags, so nothing is broken - but a generated <head> that
    # ADDED them would be a change to what 21 pages emit, and that has to be a
    # decision rather than a side effect.
    "twitter:title": {
        "404.html", "about.html", "confirmation.html", "contact.html",
        "faq.html", "index.html", "marking.html", "privacy.html",
        "tutoring.html",
        "past-papers/index.html", "past-papers/aqa/index.html",
        "past-papers/edexcel/index.html", "past-papers/edexcel-b/index.html",
        "past-papers/ocr/index.html",
        "revision-notes/index.html",
        "revision-notes/aqa-a2-macro/index.html",
        "revision-notes/aqa-a2-micro/index.html",
        "revision-notes/edexcel-theme-1/index.html",
        "revision-notes/edexcel-theme-2/index.html",
        "revision-notes/edexcel-theme-3/index.html",
        "revision-notes/edexcel-theme-4/index.html",
    },
}
HEAD_EXEMPT["twitter:description"] = HEAD_EXEMPT["twitter:title"]

# ---- checks 5 and 6 ------------------------------------------------------
# The <head> shapes among the 166 notes pages, and what tells them apart.
#
# WAS FOUR SHAPES, 97 / 40 / 28 / 1, which was PH06 section 1.2's split
# re-derived unchanged. It is THREE from 2026-08-13, and the count going down
# is an improvement declared here rather than absorbed: PH08-039's MathJax
# convergence removed the "without id" shape entirely, so its 28 pages joined
# the 97 and made 125.
#
# AND TWO from later the same day, which the paragraph above predicted in
# as many words: PH08-042's 30-line <style> block left
# 1-5-1-market-structures for css/pages/revision-notes-textbook.css, so its
# page stopped being a shape of its own and joined the 125. The label is kept
# in the table with a 0 rather than deleted, because a <style> block coming
# BACK to a notes page is exactly what this check should catch.
EXPECTED_NOTES_HEAD_SHAPES = {
    "mathjax with id": 126,
    "no mathjax": 40,
    "mathjax with id + a <style> block": 0,
}

# The content spine is the ordered list of direct children of
# div.notes-container, with runs of identical siblings collapsed - because
# "six sections here and four there" is content length, not structural drift.
# 6 shapes across 166 pages, and every one of them is the same page with a
# different set of optional trailing blocks. There are no singletons.
#
# Reseeded 2026-08-14, Wave 5.4, from 9 shapes (95, 29, 15, 11, 7, 6, 1, 1, 1).
# The three ones were PH06-031's three malformed pages; each has been repaired
# and has merged into the shape it always should have had - 95 -> 97 took the
# two pages whose </section> closed early, and 15 -> 16 took the page whose
# <h2> sat above the spec-alert. DO-NOT-BREAK: these tables fail on a count
# going DOWN as well as up, and an improvement is DECLARED by changing the page
# and the number in the same commit, so the diff records what improved.
EXPECTED_NOTES_SPINES = 6
EXPECTED_SPINE_COUNTS = (97, 29, 16, 11, 7, 6)

# PH06-031, CLOSED 2026-08-14 by Wave 5.4, approved per page by Eliot - D18 had
# explicitly excluded these three because the fixes sit inside prose regions.
#
# THE EMPTY DICT IS KEPT, NOT DELETED, and it is doing more work empty than it
# did full. The check below asserts that the set of one-page spines EQUALS this
# set, so at zero it now says "no notes page has a shape of its own" - any new
# malformed page fails, where before a fourth could only be told apart from the
# three. Same argument as KNOWN_BREADCRUMB_DISAGREEMENT being kept empty in
# check 8: the structure is where a future deliberate exception gets declared,
# and the comparison is what catches an accidental one.
MALFORMED_NOTES_PAGES: dict[str, str] = {}

# ---- check 7 -------------------------------------------------------------
# THE ONE NUMBER PH06 AND PH11 GET WRONG, and the reason this check asserts a
# convention rather than a count.
#
# PH11 section 2's Wave 2 table lists 'loading="lazy"' as a normalisation over
# "33 pages / 94 images", sourced from seo/09-web-vitals-baseline.md item 4.
# Measured 2026-08-11 across all 463 pages:
#
#     104 pages carry an <img>; 309 images; 213 already lazy
#     96 images lack loading=, spread over 96 pages - ONE EACH
#     on all 96, the one that lacks it is the FIRST image on the page
#     0 pages depart from that pattern
#
# So "33 pages" is wrong - it is 96 (94 notes-topic + 2 root photographs). More
# importantly the item's premise is wrong: this is not drift with 94 stragglers,
# it is a convention applied 96 times out of 96. Commit d7bba50 added
# loading="lazy" to the SECOND image of a two-image page and deliberately left
# the first, which is the standard rule - a lazy first image delays the LCP
# candidate. "Adding loading=lazy to the 94 images lacking it" would reverse it
# on 96 pages.
#
# The 8 pages where every image is lazy are the two diagram galleries and the
# six flashcard decks, where the first image is not a plausible LCP element.
EXPECTED_IMAGE_PAGES = 104
EXPECTED_IMAGES = 309
EXPECTED_FIRST_EAGER = 96
EXPECTED_ALL_LAZY = 8

# ---- check 8 -------------------------------------------------------------
# Every page with a breadcrumb writes it twice, visible <nav> and JSON-LD
# BreadcrumbList. 440 of 441 agree, by hand, with nothing checking. PH06-030.
#
# "with aria-label" WAS 100 and is 441 from 2026-08-13 - a count going UP,
# declared here in the same commit that moved it. The 100 were the three
# newest generated families and the 341 were everything older, which PH06-030
# calls "the clean picture of how this repo drifts: a convention improved, and
# only the pages behind a generator received the improvement". There is no
# longer an older half.
#
# `agree` stays at 440 deliberately. The aria-label lives on the <nav> opening
# tag and check 8 reads that separately from the crumb list, so it cannot
# affect agreement - and the one disagreeing page is PH06-030's, listed in
# KNOWN_BREADCRUMB_DISAGREEMENT below, which is a different normalisation.
# `visible` WAS 441 and is 460 from 2026-08-13: PH04-053's 19 pages declared a
# BreadcrumbList in JSON-LD and rendered no trail at all, which is markup
# describing content that is not on the page - and, more to the point, left
# /past-papers/ocr/ and /past-papers/edexcel-b/ with no way back up. They earn
# 291 clicks and 21,131 impressions between them on ONE inbound link each
# (PH03-049), so they are the least affordable pages on the site to strand.
#
# Each trail was BUILT FROM THAT PAGE'S OWN BreadcrumbList, names copied
# verbatim, so `agree` rose by the same 19 as `visible` - 440 -> 459 - and the
# one page still disagreeing is PH06-030's, declared below.
#
# `agree` IS 460 OF 460 FROM 2026-08-13 and the exception below is empty.
# macro-application's visible trail opened at "Revision Notes" while its
# JSON-LD opened at "Home" - PH06-030's other half, found by P6 comparing
# extracted names and again by P4 parsing the JSON-LD, and carried here as a
# declared exception ever since. One line in its notes-data slice closed it.
EXPECTED_BREADCRUMB = {"visible": 460, "with aria-label": 460, "agree": 460}

# EMPTY, AND KEPT. The loop below still runs over it, so re-declaring a page
# here is how a future deliberate mismatch would be recorded - and the
# per-page comparison above is what fails when an accidental one appears. An
# empty dict is the strongest state this can be in, not a dead variable.
KNOWN_BREADCRUMB_DISAGREEMENT: dict[str, str] = {}


# ---- check 9 -------------------------------------------------------------
# Wave 2 Phase 7. The header and footer are baked into the page at build time
# rather than fetched by inject-templates.js, so templates/header.html is now
# copied into 463 files instead of being read once by the browser.
#
# That trade is only safe while the 463 copies are provably the same file.
# This is what makes it provable: lift the block back out of every page,
# remove the uniform indent and the one class="current" the page adds, and
# require what is left to be templates/header.html byte for byte. A nav edit
# that reaches 462 pages fails here rather than shipping.
#
# It is deliberately byte-exact rather than tolerant. page_shell.bake() emits
# the template verbatim and never reformats it - that is why the four
# generators that run Prettier bake AFTER it - so there is no legitimate
# reason for a single byte to differ, and a check that forgave whitespace
# would forgive a Prettier run that had quietly rewrapped a nav label.
BAKED_TEMPLATES = ("templates/header.html", "templates/footer.html")
EXPECTED_BAKED = 463

# The one thing a page is allowed to add: setActivePage() used to do this at
# runtime and the build does it now. Ten variants across 463 pages - nine nav
# items plus the four pages that highlight nothing.
CURRENT_CLASS = re.compile(r'(<li data-page="[^"]+") class="current">')


# --------------------------------------------------------------------------
# Tokeniser - page_anatomy.py's method, reimplemented so that a workflow check
# does not import from docs/audit/, which is excluded from publishing and is a
# record rather than a dependency.
# --------------------------------------------------------------------------

VOID = {"meta", "link", "br", "hr", "img", "input", "source", "col", "area"}


class Shell(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.head: list[str] = []
        self.body: list[tuple[int, str]] = []
        self.scripts: list[str] = []
        self.in_head = self.in_body = False
        self.depth = 0
        self.head_style_blocks = 0
        self.imgs: list[bool] = []          # True if the tag carries loading=

    @staticmethod
    def _tok(tag, attrs):
        d = dict(attrs)
        bits = [tag]
        if d.get("id"):
            bits.append("#" + d["id"])
        if d.get("class"):
            bits.append("." + ".".join(sorted(d["class"].split())))
        if tag == "meta":
            bits.append("[" + (d.get("name") or d.get("property")
                               or ("charset" if "charset" in d else "?")) + "]")
        elif tag == "link":
            bits.append("[" + (d.get("rel") or "?") + "]")
            if d.get("rel") == "stylesheet":
                bits.append("=" + (d.get("href") or ""))
        elif tag == "script":
            if d.get("src"):
                bits.append("=" + d["src"] + (" defer" if "defer" in d else ""))
            elif d.get("type") == "application/ld+json":
                bits.append("[ld+json]")
            else:
                bits.append("[inline]")
        return "".join(bits)

    def handle_starttag(self, tag, attrs):
        d = dict(attrs)
        if tag == "head":
            self.in_head = True
            return
        if tag == "body":
            self.in_body, self.in_head, self.depth = True, False, 0
            return
        if self.in_head:
            self.head.append(self._tok(tag, attrs))
            if tag == "style":
                self.head_style_blocks += 1
            return
        if not self.in_body:
            return
        self.body.append((self.depth, self._tok(tag, attrs)))
        if tag == "script" and d.get("src"):
            self.scripts.append(d["src"])
        if tag == "img":
            self.imgs.append("loading" in d)
        if tag not in VOID:
            self.depth += 1

    def handle_endtag(self, tag):
        if tag == "head":
            self.in_head = False
            return
        if self.in_body and tag not in VOID:
            self.depth = max(0, self.depth - 1)

    # -- derived shapes
    def head_shape(self) -> str:
        return "|".join(self.head)

    def body_shell(self) -> str:
        return "|".join(t for d, t in self.body if d <= 3)

    def script_tail(self) -> str:
        return "|".join(t for d, t in self.body
                        if t.startswith("script=") and d <= 2)

    def css_set(self) -> str:
        return "|".join(t for t in self.head if t.startswith("link[stylesheet]"))

    def spine(self, needle: str) -> list[str] | None:
        start = base = None
        for i, (d, t) in enumerate(self.body):
            if needle in t:
                start, base = i, d
                break
        if start is None:
            return None
        out = []
        for d, t in self.body[start + 1:]:
            if d <= base:
                break
            if d == base + 1:
                out.append(t)
        return out


def collapse(spine: list[str]) -> str:
    """Collapse runs of identical siblings.

    Six <section>s and four <section>s are the same shape carrying different
    amounts of prose. Without this the 166 notes pages have 38 spines and the
    number measures how long each page is, which is not drift.
    """
    out = []
    for t in spine:
        if not out or out[-1] != t:
            out.append(t)
    return "|".join(out)


# --------------------------------------------------------------------------
# Field extraction for check 3
# --------------------------------------------------------------------------

META = re.compile(r"<meta\b([^>]*?)/?>", re.I)
ATTR = re.compile(r'([\w:.-]+)\s*=\s*"([^"]*)"')
TITLE = re.compile(r"<title[^>]*>(.*?)</title>", re.S | re.I)

# Trios a page writes the same value into more than once. PH06 section 1.1:
# <title> == og:title == twitter:title on 463/463, and description ==
# og:description == twitter:description on 445.
TRIOS = [
    ("title", ["og:title", "twitter:title"]),
    ("description", ["og:description", "twitter:description"]),
]


def head_values(source: str) -> dict[str, str]:
    out: dict[str, str] = {}
    m = TITLE.search(source)
    if m:
        out["title"] = " ".join(m.group(1).split())
    for raw in META.findall(source):
        a = {k.lower(): v for k, v in ATTR.findall(raw)}
        key = (a.get("name") or a.get("property") or "").lower()
        if key:
            out.setdefault(key, " ".join(a.get("content", "").split()))
    return out


# --------------------------------------------------------------------------
# Reporting
# --------------------------------------------------------------------------

class Report:
    def __init__(self):
        self.problems: list[str] = []
        self.lines: list[str] = []

    def ok(self, line: str) -> None:
        self.lines.append(f"  ok    {line}")

    def bad(self, line: str, *detail: str) -> None:
        self.lines.append(f"  FAIL  {line}")
        for d in detail:
            self.lines.append(f"          {d}")
        self.problems.append(line)

    def section(self, heading: str | None) -> None:
        """Drain the pending results, then open the next check's heading.

        Collecting every line and printing at the end put all eight headings
        above all forty results, which is unreadable at exactly the moment it
        matters.
        """
        for line in self.lines:
            print(line)
        self.lines = []
        if heading:
            print(heading)

def pages() -> list[str]:
    ex = build_sitemap.excludes()
    out = subprocess.run(["git", "ls-files", "*.html"], cwd=ROOT,
                         capture_output=True, text=True, check=True).stdout.split()
    return sorted(f for f in out
                  if build_sitemap.published(f, ex) and f not in RUNTIME_PARTIALS)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--show", action="store_true",
                    help="print the measured shapes and exit 0, for reseeding "
                         "the tables after a deliberate change")
    args = ap.parse_args()

    paths = pages()
    src = {p: (ROOT / p).read_text(encoding="utf-8", errors="replace")
           for p in paths}
    parsed: dict[str, Shell] = {}
    for p in paths:
        s = Shell()
        s.feed(src[p])
        s.close()
        parsed[p] = s

    fam = collections.defaultdict(list)
    for p in paths:
        fam[family_of(p)].append(p)

    r = Report()
    print(f"{len(paths)} published pages, "
          f"{sum(len(fam[f]) for f in HAND_WRITTEN)} of them hand-written\n")

    # ---------------------------------------------------------- check 1
    r.section("=== 1. One shell per family ===")
    measured = {}
    for f, ps in sorted(fam.items()):
        heads = {parsed[p].head_shape() for p in ps}
        shells = {parsed[p].body_shell() for p in ps}
        tails = {parsed[p].script_tail() for p in ps}
        csss = {parsed[p].css_set() for p in ps}
        measured[f] = (len(ps), len(heads), len(shells), len(tails), len(csss))
    if args.show:
        for f, v in sorted(measured.items()):
            print(f'    "{f}": {v},')
    unknown = sorted(set(measured) - set(EXPECTED_FAMILIES))
    if unknown:
        r.bad(f"{len(unknown)} unknown page family/families: {', '.join(unknown)}",
              "Add it to EXPECTED_FAMILIES with its measured shape counts.")
    for f, want in sorted(EXPECTED_FAMILIES.items()):
        got = measured.get(f)
        if got is None:
            r.bad(f"{f}: family has vanished")
        elif got != want:
            names = ("pages", "head shapes", "body shells", "script tails",
                     "stylesheet sets")
            diff = ", ".join(f"{n} {a}->{b}" for n, a, b in zip(names, want, got)
                             if a != b)
            r.bad(f"{f}: {diff}",
                  "If that is an improvement, change EXPECTED_FAMILIES in the "
                  "same commit so the diff records it.")
        else:
            r.ok(f"{f:12} {got[0]:4} pages, {got[1]} head / {got[2]} shell / "
                 f"{got[3]} tail / {got[4]} css")

    # ---------------------------------------------------------- check 2
    n = len(SCRIPT_TAIL)
    r.section(f"\n=== 2. The {n}-script tail ===")
    wrong_order, interleaved, kept_removed = [], [], collections.Counter()
    extra = collections.Counter()
    for p in paths:
        seq = parsed[p].scripts
        if tuple(s for s in seq if s in SCRIPT_TAIL) != SCRIPT_TAIL:
            wrong_order.append(p)
        if tuple(seq[:n]) != SCRIPT_TAIL:
            interleaved.append(p)
        for s in seq:
            if s not in SCRIPT_TAIL:
                extra[s] += 1
            if s in REMOVED_SCRIPTS:
                kept_removed[s] += 1
    if args.show:
        print("   ", dict(extra), "interleaved:", interleaved)
    if wrong_order:
        r.bad(f"{len(wrong_order)} page(s) do not carry the {n} scripts once "
              f"each, in order", *wrong_order[:6])
    else:
        r.ok(f"the same {n} scripts, in the same order, on all "
             f"{len(paths)} pages")
    # Wave 4.10. Asserted separately because the ordering test above filters to
    # tail members, and these are not members any more - a page that still
    # loaded jQuery would sail through it.
    #
    # The message counts REMOVED_SCRIPTS rather than naming them, because
    # 4.11 added two to the list and the sentence that named four went stale
    # the moment it did.
    if kept_removed:
        r.bad(f"{sum(kept_removed.values())} page(s) still load a script that "
              f"has been removed from the tail: {dict(kept_removed)}")
    else:
        r.ok(f"0 of {len(paths)} pages load any of the "
             f"{len(REMOVED_SCRIPTS)} removed scripts")
    # index.html puts its two review scripts before main.js rather than after.
    # Nothing else does. Named rather than tolerated, so a second page adopting
    # the habit fails.
    if interleaved != EXPECTED_INTERLEAVED:
        r.bad(f"pages inserting a script inside the tail: "
              f"{EXPECTED_INTERLEAVED} -> {interleaved}")
    else:
        r.ok(f"{len(interleaved)} pages insert a script inside the tail")
    if dict(extra) != EXPECTED_EXTRA_SCRIPTS:
        for k in sorted(set(extra) | set(EXPECTED_EXTRA_SCRIPTS)):
            a, b = EXPECTED_EXTRA_SCRIPTS.get(k, 0), extra.get(k, 0)
            if a != b:
                r.bad(f"page-specific script {k}: {a} -> {b} pages")
    else:
        r.ok(f"{len(extra)} page-specific scripts beyond the tail, all "
             f"expected")

    # ---------------------------------------------------------- check 3
    r.section("\n=== 3. A <head> field written twice agrees with itself ===")
    disagree = {}
    for p in paths:
        v = head_values(src[p])
        for base, others in TRIOS:
            if base not in v:
                continue
            for o in others:
                if o in v and v[o] != v[base]:
                    disagree.setdefault(p, set()).add(o)
    for p in sorted(disagree):
        fields = sorted(disagree[p])
        known = KNOWN_SELF_DISAGREEMENT.get(p)
        if known and [known[0]] == fields:
            continue
        r.bad(f"{p} disagrees with itself on {', '.join(fields)}",
              "Every duplicated <head> field is meant to agree. If this one is "
              "a deliberate social variant, add it to "
              "KNOWN_SELF_DISAGREEMENT with the reason.")
    for p, (field, why) in sorted(KNOWN_SELF_DISAGREEMENT.items()):
        if field not in disagree.get(p, set()):
            r.bad(f"{p} no longer disagrees on {field}",
                  "Good - now delete its entry from KNOWN_SELF_DISAGREEMENT "
                  "in the same commit.")
    r.ok(f"{len(disagree)} pages disagree with themselves, all "
         f"{len(KNOWN_SELF_DISAGREEMENT)} declared "
         f"({sum(1 for f, _ in KNOWN_SELF_DISAGREEMENT.values() if f.startswith('og:'))} "
         f"og:description, "
         f"{sum(1 for f, _ in KNOWN_SELF_DISAGREEMENT.values() if f.startswith('twitter:'))} "
         f"twitter:description)")

    # ---------------------------------------------------------- check 4
    r.section("\n=== 4. The <head> furniture CLAUDE.md requires ===")
    for name, pattern in HEAD_REQUIREMENTS.items():
        rx = re.compile(pattern, re.S)
        missing = {p for p in paths if not rx.search(src[p])}
        exempt = HEAD_EXEMPT.get(name, set())
        undeclared = sorted(missing - exempt)
        gained = sorted(exempt - missing)
        if undeclared:
            r.bad(f"{name}: missing from {len(undeclared)} undeclared page(s)",
                  *undeclared[:8])
        elif gained:
            r.bad(f"{name}: {len(gained)} page(s) now carry it that were "
                  f"exempt", *gained[:8],
                  "Delete them from HEAD_EXEMPT in the same commit.")
        else:
            r.ok(f"{name:22} {len(paths) - len(missing):4}/{len(paths)}"
                 + (f"   ({len(exempt)} declared exempt)" if exempt else ""))

    # ---------------------------------------------------------- check 5
    r.section("\n=== 5. notes-topic: the four <head> shapes ===")
    nt = sorted(fam["notes-topic"])
    labels = collections.Counter()
    for p in nt:
        s = parsed[p]
        has_mj = any("mathjax" in t.lower() for t in s.head)
        with_id = any("mathjax" in t.lower() and "#MathJax-script" in t
                      for t in s.head)
        if not has_mj:
            labels["no mathjax"] += 1
        elif not with_id:
            labels["mathjax without id"] += 1
        elif s.head_style_blocks:
            labels["mathjax with id + a <style> block"] += 1
        else:
            labels["mathjax with id"] += 1
    if args.show:
        print("   ", dict(labels))
    shapes = {parsed[p].head_shape() for p in nt}
    # Against the labels EXPECTED still gives pages to, not the number of
    # labels. A label held at 0 is a tripwire for a shape coming BACK - the
    # <style> block is the live example - and counting it here would demand a
    # shape that is meant not to exist.
    want_shapes = sum(1 for n in EXPECTED_NOTES_HEAD_SHAPES.values() if n)
    if len(shapes) != want_shapes:
        r.bad(f"notes-topic has {len(shapes)} <head> shapes, expected "
              f"{want_shapes}")
    for label, want in EXPECTED_NOTES_HEAD_SHAPES.items():
        got = labels.get(label, 0)
        if got != want:
            r.bad(f"notes-topic '{label}': {want} -> {got} pages")
        else:
            r.ok(f"{label:36} {got:4} pages")

    # ---------------------------------------------------------- check 6
    r.section("\n=== 6. notes-topic: the content spine ===")
    spines = collections.Counter()
    by_spine = collections.defaultdict(list)
    for p in nt:
        sp = parsed[p].spine("notes-container")
        if sp is None:
            r.bad(f"{p} has no div.notes-container",
                  "The content region is what a template slices between. It is "
                  "present exactly once on 166/166 today.")
            continue
        k = collapse(sp)
        spines[k] += 1
        by_spine[k].append(p)
    counts = tuple(n for _, n in spines.most_common())
    if args.show:
        for k, n in spines.most_common():
            print(f"    {n:4}  {k}")
    if len(spines) != EXPECTED_NOTES_SPINES or counts != EXPECTED_SPINE_COUNTS:
        r.bad(f"notes-topic spines: {EXPECTED_NOTES_SPINES} shapes "
              f"{EXPECTED_SPINE_COUNTS} -> {len(spines)} shapes {counts}")
    else:
        r.ok(f"{EXPECTED_NOTES_SPINES} spine shapes over {len(nt)} pages, "
             f"{counts}")
    # The three singletons must be exactly the three known malformed pages.
    singles = {by_spine[k][0] for k, n in spines.items() if n == 1}
    if singles != set(MALFORMED_NOTES_PAGES):
        r.bad("the set of one-page spines is not the declared one",
              f"declared: {', '.join(sorted(MALFORMED_NOTES_PAGES)) or '(none)'}",
              f"measured: {', '.join(sorted(singles)) or '(none)'}",
              "A notes page with a shape of its own is a structural defect. "
              "PH06-031's three were repaired in Wave 5.4 and the declared set "
              "is now empty, so any new one fails here. A deliberate exception "
              "goes in MALFORMED_NOTES_PAGES with a reason.")
    elif singles:
        r.ok(f"the {len(singles)} one-page spines are the declared ones, "
             f"and no others")
    else:
        r.ok("no notes page has a spine shape of its own")

    # ---------------------------------------------------------- check 7
    r.section("\n=== 7. The image loading convention ===")
    with_imgs = [p for p in paths if parsed[p].imgs]
    total = sum(len(parsed[p].imgs) for p in with_imgs)
    first_eager, all_lazy, odd = 0, 0, []
    for p in with_imgs:
        lz = parsed[p].imgs
        if all(lz):
            all_lazy += 1
        elif not lz[0] and all(lz[1:]):
            first_eager += 1
        else:
            odd.append(p)
    if odd:
        r.bad(f"{len(odd)} page(s) break the loading= convention", *odd[:8],
              "Every page is either all-lazy or first-eager-rest-lazy. A lazy "
              "first image delays the LCP candidate, which is why d7bba50 "
              "left it off.")
    else:
        r.ok(f"{len(with_imgs)} pages, {total} images: {first_eager} "
             f"first-eager-rest-lazy, {all_lazy} all-lazy, 0 exceptions")
    for label, got, want in (("pages with images", len(with_imgs), EXPECTED_IMAGE_PAGES),
                             ("images", total, EXPECTED_IMAGES),
                             ("first-eager pages", first_eager, EXPECTED_FIRST_EAGER),
                             ("all-lazy pages", all_lazy, EXPECTED_ALL_LAZY)):
        if got != want:
            r.bad(f"{label}: {want} -> {got}")

    # ---------------------------------------------------------- check 8
    r.section("\n=== 8. Both breadcrumb copies stay in step ===")
    # Two groups: the opening tag's attributes, then the inner HTML. One group
    # spanning both leaks aria-label="Breadcrumb" into the crumb list, which
    # took the agreement count from 440 to 0 and looked like a site problem.
    NAV = re.compile(
        r'<nav\b([^>]*\bclass="[^"]*\bbreadcrumb\b[^"]*"[^>]*)>(.*?)</nav>',
        re.S | re.I)
    LD = re.compile(r'<script[^>]+application/ld\+json[^>]*>(.*?)</script>',
                    re.S | re.I)
    SEPARATOR = re.compile(r'<span class="separator">[^<]*</span>')
    visible = aria = agree = 0
    mismatched = {}
    for p in paths:
        m = NAV.search(src[p])
        if not m:
            continue
        visible += 1
        if 'aria-label="Breadcrumb"' in m.group(1):
            aria += 1
        # Split on the separator span and strip tags from each crumb, which is
        # notes_drift.py's method - a crumb can be a bare word or a whole
        # <a><span>, and pulling text nodes out instead gets 161 of 441 right.
        seen = [" ".join(htmllib.unescape(re.sub(r"<[^>]+>", " ", chunk)).split())
                for chunk in SEPARATOR.split(m.group(2))]
        seen = [x for x in seen if x]
        want = None
        for block in LD.findall(src[p]):
            try:
                data = json.loads(block)
            except ValueError:
                continue
            for node in (data if isinstance(data, list) else [data]):
                if isinstance(node, dict) and node.get("@type") == "BreadcrumbList":
                    want = [i.get("name") for i in node.get("itemListElement", [])]
        if want is None:
            continue
        if [x for x in seen if x] == want:
            agree += 1
        else:
            mismatched[p] = (seen, want)
    for p in sorted(mismatched):
        if p in KNOWN_BREADCRUMB_DISAGREEMENT:
            continue
        r.bad(f"{p}: the two breadcrumb copies disagree",
              f"visible: {mismatched[p][0]}", f"json-ld: {mismatched[p][1]}")
    for p in KNOWN_BREADCRUMB_DISAGREEMENT:
        if p not in mismatched:
            r.bad(f"{p} breadcrumbs now agree",
                  "Good - delete its entry from "
                  "KNOWN_BREADCRUMB_DISAGREEMENT in the same commit.")
    got = {"visible": visible, "with aria-label": aria, "agree": agree}
    if got != EXPECTED_BREADCRUMB:
        r.bad(f"breadcrumb census {EXPECTED_BREADCRUMB} -> {got}")
    else:
        r.ok(f"{visible} visible breadcrumbs, {aria} with aria-label, "
             f"{agree} agree with their JSON-LD, "
             f"{len(KNOWN_BREADCRUMB_DISAGREEMENT)} known exception")

    # ---------------------------------------------------------- check 9
    r.section("=== 9. The baked header and footer are the template, exactly ===")
    for name in BAKED_TEMPLATES:
        want = (ROOT / name).read_text(encoding="utf-8")
        begin, end = f"<!-- BEGIN {name} ", f"<!-- END {name} -->"
        baked, wrong, missing = 0, [], []
        for p in paths:
            text = src[p]
            b = text.find(begin)
            if b == -1:
                missing.append(p)
                continue
            e = text.find(end, b)
            if e == -1:
                wrong.append(f"{p}: {begin.strip()} with no closing marker")
                continue
            line_start = text.rfind("\n", 0, b) + 1
            pad = text[line_start:b]
            inner = text[text.index("\n", b) + 1: text.rfind("\n", b, e) + 1]
            got = "\n".join(
                ln[len(pad):] if ln.startswith(pad) else ln
                for ln in inner.rstrip("\n").split("\n")) + "\n"
            got = CURRENT_CLASS.sub(r"\1>", got)
            baked += 1
            if got != want:
                wrong.append(p)
        if missing:
            r.bad(f"{len(missing)} page(s) do not carry {name}", *missing[:6])
        if wrong:
            r.bad(f"{len(wrong)} page(s) carry a {name} that is not the "
                  f"template", *wrong[:6])
        if baked != EXPECTED_BAKED:
            r.bad(f"{name} baked into {baked} pages, expected "
                  f"{EXPECTED_BAKED}")
        elif not wrong and not missing:
            r.ok(f"{name} is byte-identical on all {baked} pages")

    # Nothing may go back to fetching it at runtime, on any page.
    left = [p for p in paths if 'id="header-placeholder"' in src[p]
            or 'id="footer-placeholder"' in src[p]]
    if left:
        r.bad(f"{len(left)} published page(s) still carry a runtime "
              f"placeholder", *left[:6])
    else:
        r.ok(f"0 published pages still fetch a template at runtime")

    # ---------------------------------------------------------- report
    r.section(None)
    print()
    sys.stdout.flush()
    if args.show:
        print("--show: tables printed, nothing judged")
        return 0
    if r.problems:
        print(f"FAIL: {len(r.problems)} problem(s) with the page shell:",
              file=sys.stderr)
        for p in r.problems:
            print(f"  {p}", file=sys.stderr)
        return 1
    print(f"page shell is as recorded: {len(paths)} pages, "
          f"{len(EXPECTED_FAMILIES)} families, 9 checks")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

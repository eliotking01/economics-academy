#!/usr/bin/env python3
"""Pin the shape of every page's shell, so drift has to declare itself.

    python3 scripts/verify_page_shell.py
    python3 scripts/verify_page_shell.py --show    # print the shapes, don't judge
    python3 scripts/verify_page_shell.py --reseed  # rewrite the pinned shape
                                                   # tables from the tree, show diff

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

INVARIANTS ARE PINNED; CARDINALITIES ARE DERIVED
------------------------------------------------
Until 2026-08-23 every number here was a literal, including the ones that
change whenever a topic is added - page counts per family, how many pages
load quiz.js, how many carry a breadcrumb, how many images there are. Adding
one notes topic meant bumping literals in this file, boards.json,
verify_boards.py and bake_templates.py by hand, and the image-count and
spine-count pins had already steered a product decision (PROGRESS.md: the
contents list went on all 166 pages partly so that check 6's tuple would not
move). So the checks are now split in two:

  INVARIANTS - the point of this file, still pinned as literals, and a change
  to one still has to change this file in the same commit: how many distinct
  <head> / body-shell / script-tail / stylesheet-set SHAPES each family has;
  the script tail and its order; the declared exception sets (which pages
  disagree with themselves, which are exempt from which head field, which
  carry no breadcrumb); that no notes page has a spine of its own; that the
  baked header is byte-identical on EVERY page; the image-loading convention;
  the zero-tripwires (no <style> in a notes head, no MathJax-without-id).
  `--reseed` rewrites the pinned shape tables from the measured tree and
  prints the diff, so a deliberate change is one command plus a read.

  CARDINALITIES - how many pages, breadcrumbs, images, extra scripts - are
  DERIVED: topic counts from boards.json's expectedTopics (the one place a
  count is declared), hub/deck/glossary counts from the data directories, and
  "every page" from the page list itself. They are printed, and where a
  relation holds (every mcq page loads quiz.js and nothing else does; every
  page but the three declared carries a breadcrumb) the RELATION is asserted,
  count-free. The three hand-written families and ppq keep a pinned page
  count because nothing in boards.json declares them; reseedable.

A count going DOWN on a pinned invariant still fails: an improvement is
welcome and must be declared. A verifier that quietly congratulates you is one
that cannot tell an improvement from an accident.

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
import board_data  # noqa: E402  - expectedTopics, groups: the declared counts
import reseed_util  # noqa: E402
import site_layout  # noqa: E402

# The families, the hand-written set and the page list are site_layout's
# since 2026-08-23 (they were defined here and page_shell.py - a generator -
# imported this verifier to reach them). Re-exported under their old names
# so nothing that still says verify_page_shell.family_of() breaks.
family_of = site_layout.family_of
HAND_WRITTEN = site_layout.HAND_WRITTEN
RUNTIME_PARTIALS = site_layout.RUNTIME_PARTIALS
pages = site_layout.pages

# ---- check 1 -------------------------------------------------------------
# Per family: distinct <head> skeletons, body shells, script tails, stylesheet
# sets. "Distinct" means: strip every word of text, keep tag + id + class, and
# count how many different strings come out. Two pages with one skeleton
# differ only in words.
#
# THE SHAPE COUNTS ARE THE INVARIANT and stay pinned. The PAGE count per family
# is a cardinality and is derived - see expected_page_counts() - except for
# the three hand-written families and ppq, which nothing in boards.json
# declares; those four keep a pinned page count as a shrink guard, in
# PINNED_PAGE_COUNTS below, and `--reseed` rewrites both tables.
#
# History the numbers carry (the comments used to sit inside the literal; a
# reseed rewrites the literal wholesale, so they live here now):
#   root: nine one-off pages, so 9 heads / 9 shells / 9 css sets is correct.
#     Script tails 3 -> 2 on 2026-08-14, the home-page revamp; 2 -> 1 on
#     2026-08-23 when tutoring.html's Calendly <script src> became an inline
#     lazy loader, so every root page now ends in the plain two-script tail.
#   notes-topic: 4 head shapes until 2026-08-13, 3 after PH08-039's MathJax
#     convergence, 2 after PH08-042 moved 1-5-1's <style> block out. Declared
#     here AND at check 5 on purpose - measured by different code.
#   mcq-hub: 2 head shapes until 2026-08-23, 1 after the hub redesign removed
#     the <noscript><style> block from the six board index pages.
#
# family: (heads, shells, tails, css sets). No comments inside the literal -
# --reseed rewrites it wholesale.
EXPECTED_SHAPES = {
    "root":          (9, 9, 1, 9),
    "notes-topic":   (2, 1, 1, 1),
    "notes-hub":     (2, 2, 1, 2),
    "notes-other":   (2, 3, 1, 2),
    "past-papers":   (2, 2, 1, 2),
    "mcq-topic":     (1, 1, 1, 1),
    "mcq-hub":       (1, 2, 1, 1),
    "ppq":           (1, 3, 1, 1),
    "flashcards":    (2, 2, 1, 2),
    "glossary":      (2, 2, 1, 2),
}

# The families whose page count is not a function of boards.json: the 17
# hand-written pages (bake_templates.EXPECTED is the same set, counted once)
# and the past-paper question bank, whose page set follows which topics have
# questions. A pin against an undeclared page appearing or vanishing; a
# deliberate change is `--reseed` in the same commit. No comments inside.
PINNED_PAGE_COUNTS = {
    "root":          9,
    "past-papers":   5,
    "notes-other":   3,
    "ppq":           90,
}


def expected_page_counts() -> dict[str, int]:
    """How many pages each family SHOULD have, derived from the declarations.

    boards.json's expectedTopics is the one place a topic count is declared
    (build_past_paper_taxonomy.py and verify_notes_sequence.py hold the data
    to it); hubs, decks and glossary pages follow the group and board lists
    and the data directories. Adding a topic is a boards.json bump and new
    data, and this table moves with it - no literal here to chase.
    """
    boards = board_data.load()
    topics = sum(b["expectedTopics"] for b in boards.values())
    groups = sum(len(b["groups"]) for b in boards.values())
    out = {
        "notes-topic": topics,
        "mcq-topic": topics,
        # one hub per group plus macro-application, which is a content page
        # that classifies as a hub - so count the hub RECORDS, not the groups
        "notes-hub": len(list((ROOT / "notes-data" / "hubs").glob("*.json"))),
        "mcq-hub": groups + 1,            # one per group plus /practice-questions/
        "flashcards": len(list((ROOT / "flashcards-data").glob("*/*.json"))) + 1,
        "glossary": len(boards) + 1,      # one per board plus the combined page
    }
    out.update(PINNED_PAGE_COUNTS)
    return out


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
# 2026-08-22 took it from two to three: js/components/track.js, the GA4
# conversion events, added after nav.js. 463 of 463 carry it.
#
# 2026-08-23 took it from three to four: js/components/consent.js, the
# analytics consent bar, after track.js and before main.js. It is the only
# thing that turns analytics on, so it is on every page.
#
# Restated here as a literal ON PURPOSE. It is not imported from
# page_shell.SCRIPT_TAIL, though that is now where the generators get it: a
# check that reads the value it is checking agrees with any value, including a
# wrong one. Changing the tail has to change both, in the same commit - the
# build_past_paper_taxonomy.py EXPECTED pattern.
SCRIPT_TAIL = (
    "/js/components/nav.js",
    "/js/components/track.js",
    "/js/components/consent.js",
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
# What a page may load after the tail, and how many pages may do so.
#
# EXPECTED_INTERLEAVED was ["index.html"] until Wave 4.10 and is now empty,
# which is an improvement declared rather than absorbed. index.html put
# reviews.js and reviews-render.js between util.js and main.js; util.js is
# deleted, and bake_templates.sync_script_tail() re-emits the tail first and a
# page's own scripts after it, so the two review scripts now follow main.js.
# Nothing depends on the old position: reviews-render.js waits for
# DOMContentLoaded and reads `reviews` from js/data/reviews.js, which still
# precedes it. This check is what noticed.
#
# Both review scripts were deleted outright in the 2026-08-14 home-page
# revamp - the testimonials are static HTML now - so index.html's tail is
# the plain two-script tail like everything else's.
EXPECTED_INTERLEAVED = []

# Which families load which component script after the tail, as a RELATION
# rather than a count: every page of the family carries it, and no page
# outside the family does. (Until 2026-08-23 this was a dict of counts -
# quiz.js 173 and so on - that had to be bumped by hand for every new topic
# and asserted nothing about WHICH pages.) Pages loading something else are
# named one by one in EXTRA_SCRIPT_PAGES.
FAMILY_SCRIPT = {
    "mcq-topic": "/js/components/quiz.js",
    "mcq-hub": "/js/components/quiz.js",
    "ppq": "/js/components/question-search.js",
    "flashcards": "/js/components/flashcards.js",
    "glossary": "/js/components/glossary-filter.js",
}
# tutoring.html's Calendly widget.js was the one entry here until 2026-08-23,
# when the performance pass made it lazy: an inline script at the foot of the
# page injects widget.js (and its widget.css, formerly a render-blocking
# <link> in the <head>) when the booking section nears the viewport. Nothing
# third-party is a <script src> on any page now; the table stays so the next
# one has somewhere to be declared.
EXTRA_SCRIPT_PAGES = {}

# ---- check 3 -------------------------------------------------------------
# Fields a page writes twice must agree with themselves. PH06-029 found 18 that
# do not, all hand-written, none generated - a generator cannot disagree with
# itself. Each is a deliberately shortened social variant, so each is named
# rather than counted, and the field is named too: all but one are
# og:description and exactly one is twitter:description.
#
# PH06 section 1.1's prose enumerates only 15 of these 18 - contact.html,
# faq.html and marking.html are missing from its list. The count 18 was right;
# the list was short. This is the list.
#
# tutoring.html left the list on 2026-08-14: the tutoring rework gave it one
# description used for both fields, so it no longer disagrees with itself.
# index.html left the same day, in the home-page revamp, for the same reason.
#
# SIX MORE LEFT ON 2026-08-21, in the notes on-page SEO pass, and for the same
# reason again. The five board hubs and macro-application had a shortened
# social variant because their meta descriptions ran 211 to 247 characters and
# a social card cannot show that much. Rewriting them to the 145-158 band -
# seo/14-notes-keyword-brief.md §5 - removed the thing the shortening existed
# for, so og:description is now the description on all six and a second string
# is no longer written. 10 remain.
#
# revision-notes/index.html STAYS. Its head is frozen - DECISIONS.md D50 -
# and was not touched by that pass.
KNOWN_SELF_DISAGREEMENT = {
    "about.html": ("og:description", "shortened social variant"),
    "contact.html": ("og:description", "shortened social variant"),
    "faq.html": ("og:description", "shortened social variant"),
    "marking.html": ("og:description", "shortened social variant"),
    "past-papers/index.html": ("og:description", "shortened social variant"),
    "past-papers/aqa/index.html": ("og:description", "shortened social variant"),
    "past-papers/edexcel/index.html": ("og:description", "shortened social variant"),
    "past-papers/edexcel-b/index.html": ("og:description", "shortened social variant"),
    "past-papers/ocr/index.html": ("og:description", "shortened social variant"),
    "revision-notes/index.html": ("og:description", "shortened social variant"),
}

# ---- check 4 -------------------------------------------------------------
# CLAUDE.md's "a new page needs" list, as a census rather than a rule, because
# the rule is not true of every page and pretending otherwise ships a red
# check. 404.html and confirmation.html are noindex utility pages and carry
# almost none of the social furniture, correctly.
HEAD_REQUIREMENTS = {
    # WAS the external gtag.js tag until 2026-08-23. Analytics is now behind
    # a hard consent gate: the head carries an inline loader that reads
    # localStorage["ea-consent"] and injects gtag.js only on "yes"
    # (page_shell.GTAG). Asserted by the read and the measurement ID
    # together; the tripwire that no page still loads gtag.js UNCONDITIONALLY
    # is UNGATED_GTAG below.
    "consent-gated gtag": r"googletagmanager\.com/gtag/js\?id=G-YVCNRW4QH6"
                          r'.{0,300}localStorage\.getItem\("ea-consent"\)',
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

# Zero tripwire, 2026-08-23. A `<script ... src="https://www.googletagmanager
# .com/gtag/js...">` TAG in the markup is gtag.js loading before anyone has
# been asked - the thing the consent gate exists to stop. The loader builds
# its tag in JS, so the only way this matches is a page that kept, or
# regained, the old unconditional snippet. Must be 0 of 463.
UNGATED_GTAG = re.compile(
    r'<script[^>]+src="https://www\.googletagmanager\.com/gtag/js', re.I)

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
# The two live labels are a cardinality - a new topic lands in one or the
# other - so they are not pinned: the check asserts that the two together
# account for every notes-topic page (their total is derived from boards.json)
# and prints the split. The ZERO labels are invariants, tripwires for a shape
# coming back: the <style> block (the live example above) and MathJax without
# an id (PH08-039). Either going above 0 fails.
NOTES_HEAD_LABELS_LIVE = ("mathjax with id", "no mathjax")
NOTES_HEAD_LABELS_ZERO = ("mathjax with id + a <style> block",
                          "mathjax without id")

# Since the performance pass of 2026-08-23 the split between the two live
# labels is not a free cardinality either: build_notes_pages.py loads MathJax
# if and only if the body contains one of the three delimiters the config
# typesets, and this is the independent restatement of that rule. The
# pattern is written out here rather than imported from the generator for the
# same reason check 2 restates the script tail - a check that imports the
# thing it is checking agrees with any value. A page loading MathJax with no
# maths wastes ~300 KB of third-party script; a page with maths and no
# MathJax shows raw TeX. Both fail. The preconnect to the CDN goes with the
# script: present on exactly the pages that load it.
MATHS_DELIMITER = re.compile(r"\\\(|\\\[|\$\$")
MATHJAX_ORIGIN = "https://cdn.jsdelivr.net"

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
# The NUMBER of spine shapes is the invariant and stays pinned (reseedable).
# The per-shape COUNTS - (97, 29, 16, 11, 7, 6) until 2026-08-23 - were a
# cardinality that moved with every added topic and had already shaped a
# product decision (PROGRESS.md, "contents list on all 166"): DELETED, not
# demoted to a warning, because a warning that fires on every legitimate
# addition is noise that trains people to skip the output. The counts are
# still printed. What check 6 actually protects - no notes page has a shape
# of its own - is the singleton assertion below, which is untouched.
EXPECTED_NOTES_SPINES = 6

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
# The 10 pages where every image is lazy are the two diagram galleries, the six
# flashcard decks, index.html - from the 2026-08-14 home-page revamp, whose one
# image is the below-the-fold tutor photo - and marking.html, which gained its
# two marked-work preview images on 2026-08-16. Both of marking.html's sit deep
# in the page, well below "What You Actually Get". On none of these pages is the
# first image a plausible LCP element.
# The CONVENTION - every page is all-lazy or first-eager-rest-lazy, 0
# exceptions - is the invariant and is asserted. The four counts that sat here
# until 2026-08-23 (106 pages, 312 images, 96 first-eager, 10 all-lazy) were
# cardinalities that moved with every diagram Eliot adds; they are measured
# and printed, not pinned.

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
# The relation, not the number: every published page carries a breadcrumb
# except the three named here, every breadcrumb has its aria-label, and every
# one agrees with its JSON-LD. (Was a census of three literals, all 460, that
# moved with every new page.) 404 and confirmation are noindex utility pages;
# the home page is the root of every trail and has nothing to climb to.
NO_BREADCRUMB = {"404.html", "confirmation.html", "index.html"}

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
# Baked into EVERY published page - the relation is the invariant. The literal
# 463 that sat here until 2026-08-23 restated len(pages()) and moved with it.

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

def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--show", action="store_true",
                    help="print the measured shapes and exit 0, for reading "
                         "the tables after a deliberate change")
    ap.add_argument("--reseed", action="store_true",
                    help="rewrite the pinned tables (EXPECTED_SHAPES, "
                         "PINNED_PAGE_COUNTS, EXPECTED_NOTES_SPINES) from the "
                         "measured tree, print the diff and exit 0. For a "
                         "DELIBERATE change, in the same commit; read the diff.")
    args = ap.parse_args()
    if args.reseed:
        args.show = True

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
    shapes, counts = {}, {}
    for f, ps in sorted(fam.items()):
        heads = {parsed[p].head_shape() for p in ps}
        shells = {parsed[p].body_shell() for p in ps}
        tails = {parsed[p].script_tail() for p in ps}
        csss = {parsed[p].css_set() for p in ps}
        shapes[f] = (len(heads), len(shells), len(tails), len(csss))
        counts[f] = len(ps)
    want_counts = expected_page_counts()
    if args.show:
        print("    EXPECTED_SHAPES (heads, shells, tails, css sets):")
        for f, v in shapes.items():
            print(f'      "{f}": {v},')
        print("    page counts, measured (derived expectation in brackets):")
        for f, n in counts.items():
            print(f'      "{f}": {n}   [{want_counts.get(f, "?")}]')
    unknown = sorted(set(shapes) - set(EXPECTED_SHAPES))
    if unknown:
        r.bad(f"{len(unknown)} unknown page family/families: {', '.join(unknown)}",
              "Add it to EXPECTED_SHAPES with its measured shape counts (and "
              "to expected_page_counts() or PINNED_PAGE_COUNTS).")
    names = ("head shapes", "body shells", "script tails", "stylesheet sets")
    for f, want in EXPECTED_SHAPES.items():
        got = shapes.get(f)
        if got is None:
            r.bad(f"{f}: family has vanished")
            continue
        problems = []
        if got != want:
            problems.append(", ".join(f"{n} {a}->{b}"
                                      for n, a, b in zip(names, want, got) if a != b))
        n_want = want_counts.get(f)
        if n_want is not None and counts[f] != n_want:
            source = ("PINNED_PAGE_COUNTS (--reseed)" if f in PINNED_PAGE_COUNTS
                      else "boards.json / the data directories")
            problems.append(f"pages {n_want}->{counts[f]} (expected from {source})")
        if problems:
            r.bad(f"{f}: {'; '.join(problems)}",
                  "A deliberate shape change: `--reseed` rewrites the pinned "
                  "tables, commit the diff with the pages. A page-count "
                  "disagreement: the declaration and the tree differ - note "
                  "pages() lists TRACKED files, so `git add` a new page first.")
        else:
            r.ok(f"{f:12} {counts[f]:4} pages, {got[0]} head / {got[1]} shell / "
                 f"{got[2]} tail / {got[3]} css")

    # ---------------------------------------------------------- check 2
    n = len(SCRIPT_TAIL)
    r.section(f"\n=== 2. The {n}-script tail ===")
    wrong_order, interleaved, kept_removed = [], [], collections.Counter()
    extra = collections.Counter()
    extra_pages: dict[str, set] = collections.defaultdict(set)
    for p in paths:
        seq = parsed[p].scripts
        if tuple(s for s in seq if s in SCRIPT_TAIL) != SCRIPT_TAIL:
            wrong_order.append(p)
        if tuple(seq[:n]) != SCRIPT_TAIL:
            interleaved.append(p)
        for s in seq:
            if s not in SCRIPT_TAIL:
                extra[s] += 1
                extra_pages[s].add(p)
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
    # The relation: every page of a family carries its script, no page
    # outside the family does, and every other extra script is on exactly
    # the pages declared for it.
    script_ok = True
    for f, script in FAMILY_SCRIPT.items():
        missing = [p for p in fam[f] if script not in parsed[p].scripts]
        if missing:
            script_ok = False
            r.bad(f"{len(missing)} {f} page(s) do not load {script}",
                  *missing[:6])
    allowed_for: dict[str, set] = collections.defaultdict(set)
    for f, script in FAMILY_SCRIPT.items():
        allowed_for[script].update(fam[f])
    for script, ps in EXTRA_SCRIPT_PAGES.items():
        allowed_for[script].update(ps)
    for script, ps in sorted(extra_pages.items()):
        stray = sorted(ps - allowed_for.get(script, set()))
        if stray:
            script_ok = False
            r.bad(f"{script} is loaded by {len(stray)} page(s) outside its "
                  f"family/declared set", *stray[:6],
                  "Name the page in EXTRA_SCRIPT_PAGES or the family in "
                  "FAMILY_SCRIPT if it is deliberate.")
    for script, ps in EXTRA_SCRIPT_PAGES.items():
        gone = sorted(ps - extra_pages.get(script, set()))
        if gone:
            script_ok = False
            r.bad(f"{script} is declared on {gone} but no longer loaded there",
                  "Delete the entry from EXTRA_SCRIPT_PAGES in the same commit.")
    if script_ok:
        r.ok(f"{len(extra)} page-specific scripts beyond the tail, each on "
             f"exactly its family's pages: "
             + ", ".join(f"{k.rsplit('/', 1)[-1]} x{v}"
                         for k, v in sorted(extra.items())))

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
    ungated = sorted(p for p in paths if UNGATED_GTAG.search(src[p]))
    if ungated:
        r.bad(f"{len(ungated)} page(s) load gtag.js unconditionally, before "
              f"consent", *ungated[:8],
              "Rebuild (python3 scripts/build.py) - the head comes from "
              "page_shell.GTAG and bake_templates.sync_gtag().")
    else:
        r.ok(f"{'ungated gtag.js tag':22} {0:4}/{len(paths)}   (analytics "
             f"loads only after consent)")

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
    # The zero labels are tripwires for a shape coming BACK - the <style>
    # block is the live example. The live labels are a cardinality: a new
    # topic lands in one or the other, so the check is that the two together
    # are every notes-topic page (the total comes from boards.json) and the
    # split is printed, not pinned.
    for label in NOTES_HEAD_LABELS_ZERO:
        got = labels.get(label, 0)
        if got:
            r.bad(f"notes-topic '{label}': 0 -> {got} pages",
                  "A shape that was deliberately removed has come back.")
        else:
            r.ok(f"{label:36} {got:4} pages")
    live_total = sum(labels.get(l, 0) for l in NOTES_HEAD_LABELS_LIVE)
    want_total = want_counts["notes-topic"]
    if live_total != len(nt) or len(nt) != want_total:
        r.bad(f"notes-topic live <head> labels account for {live_total} of "
              f"{len(nt)} pages (boards.json declares {want_total})")
    else:
        split = ", ".join(f"{labels.get(l, 0)} {l}" for l in NOTES_HEAD_LABELS_LIVE)
        r.ok(f"{'live labels':36} {live_total:4} pages = all of them ({split})")

    # MathJax if and only if the body has maths, and the CDN preconnect if and
    # only if MathJax. Decided from the SOURCE, head against body, not from the
    # parsed token lists: the delimiters are text, which the tokens drop.
    unneeded, missing, pc_bad = [], [], []
    for p in nt:
        head_src, body_src = src[p].split("</head>", 1)
        has_mj = "mathjax" in head_src.lower()
        has_maths = bool(MATHS_DELIMITER.search(body_src))
        has_pc = f'rel="preconnect" href="{MATHJAX_ORIGIN}"' in head_src
        if has_mj and not has_maths:
            unneeded.append(p)
        elif has_maths and not has_mj:
            missing.append(p)
        if has_pc != has_mj:
            pc_bad.append(p)
    if unneeded:
        r.bad(f"{len(unneeded)} notes-topic page(s) load MathJax with no maths "
              f"in the body", *unneeded[:8],
              "build_notes_pages.py decides from the body; rebuild.")
    if missing:
        r.bad(f"{len(missing)} notes-topic page(s) contain maths and do not "
              f"load MathJax", *missing[:8],
              "build_notes_pages.py decides from the body; rebuild.")
    if pc_bad:
        r.bad(f"{len(pc_bad)} notes-topic page(s) have the cdn.jsdelivr.net "
              f"preconnect without MathJax, or MathJax without it", *pc_bad[:8])
    if not (unneeded or missing or pc_bad):
        n_mj = sum(1 for p in nt if "mathjax" in src[p].split("</head>", 1)[0].lower())
        r.ok(f"{'mathjax iff maths in body':36} {n_mj:4} pages load it, "
             f"{len(nt) - n_mj} do not, 0 mismatches; CDN preconnect on the {n_mj}")

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
    spine_counts = tuple(n for _, n in spines.most_common())
    if args.show:
        for k, n in spines.most_common():
            print(f"    {n:4}  {k}")
    if len(spines) != EXPECTED_NOTES_SPINES:
        r.bad(f"notes-topic spines: {EXPECTED_NOTES_SPINES} shapes -> "
              f"{len(spines)} shapes {spine_counts}",
              "A deliberate change: `--reseed`, commit the diff with the pages.")
    else:
        # The per-shape counts are printed, not judged - see the note above
        # EXPECTED_NOTES_SPINES.
        r.ok(f"{EXPECTED_NOTES_SPINES} spine shapes over {len(nt)} pages, "
             f"{spine_counts}")
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
        # Measured, printed, not pinned - the convention is the invariant.
        r.ok(f"{len(with_imgs)} pages, {total} images: {first_eager} "
             f"first-eager-rest-lazy, {all_lazy} all-lazy, 0 exceptions")

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
    without = []
    for p in paths:
        m = NAV.search(src[p])
        if not m:
            without.append(p)
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
    # The relation: breadcrumbs on every page but the declared three, every
    # one with its aria-label, every one in agreement. No census literal.
    undeclared = sorted(set(without) - NO_BREADCRUMB)
    regained = sorted(NO_BREADCRUMB - set(without))
    if undeclared:
        r.bad(f"{len(undeclared)} page(s) carry no breadcrumb and are not "
              f"declared in NO_BREADCRUMB", *undeclared[:6])
    if regained:
        r.bad(f"{len(regained)} page(s) in NO_BREADCRUMB now carry one",
              *regained, "Delete them from NO_BREADCRUMB in the same commit.")
    if aria != visible:
        r.bad(f"{visible - aria} breadcrumb(s) lack aria-label=\"Breadcrumb\"")
    if agree + len(mismatched) != visible:
        r.bad(f"{visible - agree - len(mismatched)} breadcrumb(s) have no "
              f"BreadcrumbList JSON-LD to agree with")
    if not (undeclared or regained or aria != visible
            or agree + len(mismatched) != visible):
        r.ok(f"{visible} of {len(paths)} pages carry a breadcrumb "
             f"({len(NO_BREADCRUMB)} declared without), all {aria} with "
             f"aria-label, all {agree} agree with their JSON-LD, "
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
        if baked != len(paths):
            r.bad(f"{name} baked into {baked} of {len(paths)} pages")
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
    if args.reseed:
        print("--reseed: rewriting the pinned tables from the measured tree")
        reseed_util.rewrite(__file__, "EXPECTED_SHAPES",
                            reseed_util.format_tuple_dict(
                                {f: shapes[f] for f in EXPECTED_SHAPES if f in shapes}
                                | {f: shapes[f] for f in shapes if f not in EXPECTED_SHAPES}))
        reseed_util.rewrite(__file__, "PINNED_PAGE_COUNTS",
                            reseed_util.format_tuple_dict(
                                {f: counts[f] for f in PINNED_PAGE_COUNTS if f in counts}))
        reseed_util.rewrite(__file__, "EXPECTED_NOTES_SPINES", repr(len(spines)))
        print("Now re-run without --reseed, read the diff, and commit it with "
              "the pages that moved.")
        return 0
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
          f"{len(EXPECTED_SHAPES)} families, 9 checks")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

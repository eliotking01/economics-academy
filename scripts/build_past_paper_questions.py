#!/usr/bin/env python3
"""Build the past-paper question bank's client-side search index.

Joins the three data sources into the single JSON file the search component
fetches:

    past-paper-questions-data/edexcel-a/*.json   machine-extracted questions
    past-paper-questions-data/tags.json          hand-written topics + keywords
    past-paper-questions-data/taxonomy.json      themes, units, topics

    -> past-paper-questions/questions.json

Run:  python3 scripts/build_past_paper_questions.py [--check]

--check validates and reports without writing.

In Phase 3 this script also grows the theme and topic page generation. For now
it produces the index and reports which topics clear the volume gate.

PERFORMANCE PASS, 2026-08-23 (Phase 3)
--------------------------------------
The two board hubs were the heaviest pages on the site - edexcel/ 799 KB of
HTML with every one of its 304 questions baked in as a card, aqa/ 620 KB -
and then question-search.js fetched the full 424 KB index before a single
filter worked. Two changes, both below:

- A board hub bakes only the HUB_CARDS most recent questions as HTML (the
  same set, in the same order, the component renders first), followed by a
  static note inside the results container saying so and pointing at the
  section and topic lists further down the page, which between them list
  every question with no script at all. The component replaces the
  container's contents when it initialises, so the note is gone the moment
  the live list takes over, and the error path leaves the page as served.
  Section and topic pages still bake every card: they ARE the no-JS list.
- Every board and section page fetches a per-board payload,
  past-paper-questions/<board>/questions.json - board_payload() - instead of
  the master index. It carries every topic on the board, which is what their
  live Topic filter lists (DO-NOT-BREAK, PH08-046), and roughly half the
  bytes. The master index is unchanged and still what the master page and
  build_questions.py read.

Standard library only, in keeping with the rest of scripts/.
"""

import argparse
import collections
import datetime
import html
import json
import re
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import board_data  # noqa: E402
# Wave 2 Phase 6. page_shell.py owns the <head> for every family now.
import page_shell as shell  # noqa: E402
import prettier_util  # noqa: E402
DATA = ROOT / "past-paper-questions-data"
PAGE_DIR = ROOT / "past-paper-questions"
OUT = PAGE_DIR / "questions.json"
INDEX = PAGE_DIR / "index.html"

SITE = "https://economicsacademy.co.uk"
GTAG = "G-YVCNRW4QH6"

# A topic earns its own generated page at this many questions. Re-evaluated on
# every run, so topics rise above the gate as the bank grows and pages appear
# without anyone having to remember to add them.
#
# 4 -> 2 on 2026-08-24. At 4, 70 of the 151 topics that have a question had no
# page - monopsony, public goods and the trade cycle among them - while the 81
# that did were the best-built pages on the site: server-rendered, breadcrumbed,
# schema'd and in the sitemap. Dropping to 2 published 46 more (aqa 26, edexcel
# 20) and left the 24 one-question topics out, on the judgement that two real
# questions with mark-scheme links plus a notes link is a page worth landing on
# and one is not.
#
# THIS NUMBER IS DECLARED HERE AND NOWHERE ELSE. notes_extras.py,
# build_search_index.py and verify_past_paper_tags.py all import it; nothing
# restates it. A published URL is permanent, so raising it again would strand
# every page it removes - the gate may fall, never rise.
GATE = 2

# How many cards a BOARD hub bakes as HTML. Equal to question-search.js's
# PAGE_SIZE on purpose: the component's first render is the same 20 in the
# same order (newest first, question number within a year), so enabling the
# script swaps like for like. scripts/test_question_search.js holds the two
# numbers together.
HUB_CARDS = 20


# The extraction directories. Two extractors write here: the Swift/PDFKit one
# for Edexcel and the pdfplumber one for AQA. Both emit the same record shape,
# so from this point on the board is just a field.
#
# Edexcel spans two qualifications in two directories - 9EC0 and 8EC0 each
# have a Paper 1 in the same series, so one directory would mean colliding
# filenames. They share a board, and their questions mix freely from here on:
# the qualification is a field and a badge, not a separate namespace. Edexcel
# B is the same shape: 9EB0 and 8EB0.
#
# Keyed by boards.json key. Which of them the bank READS is boards.json's
# business, not this table's: paper_dirs() asks board_data for the boards with
# pastPaperBank, so a board's papers reach the build only once its bank is
# live (or staged, for validation). Boards are read in boards.json order and
# each board's directories in the order below, which keeps the paper table -
# and so every q.p index in the published payloads - stable as a board joins:
# a new board's papers append after the existing ones.
#
# AQA's AS papers (7135) joined by D71 (2026-11-25): Section A's MCQs only,
# in aqa-as/. Their records reach a page only once tagged, which is the gate
# that holds them back until launch - no family of their own. They read after
# aqa/, so in the master payload every Edexcel B paper's q.p moves up by the
# number of AS papers; each payload is self-consistent, so nothing breaks.
BANK_DIRS = {
    "edexcel-a": ("edexcel-a", "edexcel-a-as"),
    "aqa": ("aqa", "aqa-as"),
    "edexcel-b": ("edexcel-b", "edexcel-b-as"),
}

# A note printed on every card of these papers, under the question. Edexcel B
# Paper 3 is set on a context Pearson pre-releases, so a student meeting a
# Paper 3 question cold should know the paper's candidates had met its
# context, if not its extracts. Wording approved by Eliot, 2026-11-16
# (review/phase-4-extraction.md Q5), from the 9EB0 specification. Keyed
# (board, level, paper); carried in the paper table as `note` only where it
# applies, so no other paper's payload gains a byte.
PAPER_NOTES = {
    ("edexcel-b", "a-level", 3): (
        "Paper 3 is set on a broad context that Pearson pre-released the "
        "November before the exam. The extracts in the paper were unseen on "
        "the day."
    ),
}


def paper_dirs(*, staged=False):
    """The extraction directories of the bank's boards, live ones only
    unless staged=True. A board with the family and no BANK_DIRS row fails
    here rather than building a bank that silently lacks its papers."""
    out = []
    for key in board_data.load("pastPaperBank", staged=staged):
        if key not in BANK_DIRS:
            sys.exit(f"build_past_paper_questions: {key} has pastPaperBank in "
                     f"boards.json but no BANK_DIRS row - name its "
                     f"past-paper-questions-data/ directories")
        out.extend(BANK_DIRS[key])
    return tuple(out)


def load_bank(*, staged=False):
    """(tags, papers): the hand-written tags and every extracted paper of
    the bank's live boards (staged=True: and of its staged ones).

    Split out of load() on 2026-08-23 so that scripts/notes_extras.py can
    count a topic's tagged questions from the SAME source files this index is
    built from - without reading taxonomy.json, which is itself generated,
    or questions.json, which this script writes AFTER the notes pages are
    built (site_layout.GENERATORS). A question counts there under exactly
    the two conditions it is published here: it carries a tag, and it has a
    mark scheme - see the loop in build().
    """
    tags = json.loads((DATA / "tags.json").read_text(encoding="utf-8"))
    tags.pop("_comment", None)
    mcq_boards = {key: BANK_DIRS.get(key, ())
                  for key in board_data.load("pastPaperMcqs", staged=staged)}
    mcq_dirs = {d for dirs in mcq_boards.values() for d in dirs}
    papers = []
    for board_dir in paper_dirs(staged=staged):
        for path in sorted((DATA / board_dir).glob("*.json")):
            paper = json.loads(path.read_text(encoding="utf-8"))
            # A board's multiple-choice records (Phase 7) reach the bank only
            # once it has the pastPaperMcqs family - live, or staged when
            # validating. Dropped here, at the one door every reader comes
            # through (this index, the notes tail's counts), and question by
            # question rather than paper by paper: the paper itself stays in
            # the list, so the paper table and every q.p index into it are
            # the same with the MCQs on or off.
            if board_dir not in mcq_dirs:
                paper["questions"] = [q for q in paper["questions"]
                                      if q.get("type") != "mcq"]
            papers.append(paper)
    return tags, papers


def load(*, staged=False):
    taxonomy = json.loads((DATA / "taxonomy.json").read_text(encoding="utf-8"))
    # The bank's boards only. taxonomy.json can hold a board for its glossary
    # alone (board_data.TAXONOMY_READERS); reaching this index it would join the
    # master search's board list with no questions behind it.
    bank = {b["slugs"]["taxonomy"]: b["names"]["display"]
            for b in board_data.load("pastPaperBank", staged=staged).values()}
    taxonomy["boards"] = [b for b in taxonomy["boards"] if b["board"] in bank]
    # The bank names a board by its display name ("Edexcel A"), not the
    # taxonomy's short one ("Edexcel"): with Edexcel B in the bank, a bare
    # "Edexcel" beside it was ambiguous. Eliot, 2026-11-17 (B bank launch,
    # review/launch-pastPaperBank.md L7). Set here, once, for the board
    # records and for each paper's boardName (the card badge), because the
    # extracted paper files carry the short name and are never hand-edited.
    # load_bank() is untouched, so the notes tail, which reads it, is too.
    for b in taxonomy["boards"]:
        b["name"] = bank[b["board"]]
    tags, papers = load_bank(staged=staged)
    for p in papers:
        p["boardName"] = bank[p["board"]]
    return taxonomy, tags, papers


def topic_lookup(taxonomy):
    """slug -> everything the UI needs to render a topic chip or link.

    Keyed by slug alone, which is safe because no slug is shared between the two
    boards. The spec CODES are shared - 37 of them mean different things on
    Edexcel and AQA - which is why every page URL carries the board and why the
    board travels with each topic here.
    """
    out = {}
    for board in taxonomy["boards"]:
        for group in board["groups"]:
            for unit in group["units"]:
                for t in unit["topics"]:
                    if t["slug"] in out:
                        raise SystemExit(f"slug {t['slug']} used by two boards")
                    out[t["slug"]] = {
                        "spec": t["spec"],
                        "title": t["title"],
                        "shortTitle": t["shortTitle"],
                        "board": board["board"],
                        "boardName": board["name"],
                        "group": group["slug"],
                        "groupLabel": group["label"],
                        "groupName": group["name"],
                        "unit": unit["unit"],
                        "unitName": unit["name"],
                        "notesUrl": t["notesUrl"],
                        "questionsUrl": t["questionsUrl"],
                        "url": f"/past-paper-questions/{board['board']}/{t['slug']}/",
                    }
    return out


def build(taxonomy, tags, papers):
    topics = topic_lookup(taxonomy)
    errors = []
    untagged = []
    questions = []

    # Papers are held once in their own table and referenced by index. Inlining
    # them would repeat two ~110-character PDF URLs on every question, which is
    # most of the payload for a file the browser fetches before it can search.
    paper_table = [
        {
            "paper": p["paper"],
            "paperName": p["paperName"],
            "year": p["year"],
            "series": p["series"],
            "seriesSlug": p["seriesSlug"],
            "board": p["board"],
            "boardName": p["boardName"],
            "qualification": p["qualification"],
            "level": p["level"],
            # Short form for the card badge. The full qualification string is
            # too long to sit in a row of chips on a phone.
            "levelLabel": "AS Level" if p["level"] == "as-level" else "A Level",
            "questionPaperUrl": p["questionPaperUrl"],
            "markSchemeUrl": p["markSchemeUrl"],
            **({"note": PAPER_NOTES[(p["board"], p["level"], p["paper"])]}
               if (p["board"], p["level"], p["paper"]) in PAPER_NOTES else {}),
        }
        for p in papers
    ]
    # Keyed on board AND level: all three of Edexcel A Level, Edexcel AS and AQA
    # have a Paper 1 in the same series, so board alone is not unique.
    paper_index = {
        (p["board"], p["level"], p["paper"], p["seriesSlug"]): i
        for i, p in enumerate(paper_table)
    }

    for paper in papers:
        pi = paper_index[
            (paper["board"], paper["level"], paper["paper"], paper["seriesSlug"])
        ]
        for q in paper["questions"]:
            tag = tags.get(q["id"])
            if tag is None:
                # An extracted but untagged question is work in progress, not a
                # fault: it is counted and named in the summary, and simply not
                # published until someone has tagged it. A question with no
                # topic could not be filed on a topic page anyway.
                untagged.append(q["id"])
                continue

            slugs = tag["topics"]
            for slug in slugs:
                if slug not in topics:
                    errors.append(f"{q['id']}: unknown topic slug {slug!r}")

            known = [s for s in slugs if s in topics]
            groups = sorted({topics[s]["group"] for s in known})
            boards = sorted({topics[s]["board"] for s in known})
            if len(boards) > 1:
                errors.append(
                    f"{q['id']}: tagged across two boards ({', '.join(boards)})")

            if q["markScheme"] is None:
                errors.append(f"{q['id']}: no mark scheme recorded")
                continue

            mcq = {}
            if q.get("type") == "mcq":
                # Phase 7. The extraction verifier owns these checks; they
                # are restated here because this is the door to the payload,
                # and a key must never get through it (D67: search-only).
                if any(k in q for k in ("answer", "key", "correct")):
                    errors.append(f"{q['id']}: an MCQ record carries a key")
                opts = q.get("options")
                if opts is not None and [o["letter"] for o in opts] != list("ABCD"):
                    errors.append(f"{q['id']}: options are not A-D in order")
                if opts is None and not q.get("usesFigure"):
                    errors.append(f"{q['id']}: options not text, but no figure")
                # Options as a plain list: the letters are A-D in order, so
                # they are the list position, not 7 bytes each in the payload.
                mcq = {
                    "type": "mcq",
                    "options": [o["text"] for o in opts] if opts else None,
                    "usesFigure": bool(q.get("usesFigure")),
                }

            # Whitelist, not a copy. `sourceAttribution` is deliberately absent:
            # Pearson's citation for a Section C stimulus is provenance, not
            # question wording, so it stays in the extraction data and out of
            # the payload - which keeps it out of the card and out of the search
            # index without anything having to filter it later.
            entry = {
                "id": q["id"],
                "p": pi,
                "section": q["section"],
                "questionNumber": q["questionNumber"],
                "parentQuestion": q["parentQuestion"],
                "choiceGroup": q["choiceGroup"],
                "marks": q["marks"],
                "questionText": q["questionText"],
                "topics": slugs,
                "board": boards[0] if boards else paper["board"],
                "groups": groups,
                "keywords": tag["keywords"],
                "qpPage": q["questionPaper"]["page"],
                "msPage": q["markScheme"]["page"],
                # Page where this question's extract block starts, for the
                # "View the extract" link. Null for Section C, which has none.
                "ctxPage": q["context"]["page"] if q["context"] else None,
                "modelAnswer": q["modelAnswer"],
                # Edexcel A Papers 1-2 Section A (Phase 6): the link goes to
                # the page the question's stem is printed on, not an extract,
                # so it carries its own label - "Question 3 as printed",
                # approved by Eliot 2026-11-24. Emitted only for those
                # records, which leaves every other card's payload unchanged.
                **({"ctxLabel": q["context"]["label"]}
                   if q["context"] and q["context"].get("type") == "question"
                   else {}),
                # Multiple-choice cards only (Phase 7): a written card's
                # payload is unchanged by a byte, as ctxLabel's was.
                **mcq,
            }
            questions.append(entry)

    # Newest first, then paper, then question number: the order a student most
    # often wants, and the order the page shows before any sort is chosen.
    questions.sort(
        key=lambda q: (
            -paper_table[q["p"]]["year"],
            paper_table[q["p"]]["board"],
            paper_table[q["p"]]["seriesSlug"],
            paper_table[q["p"]]["paper"],
            int(re.sub(r"\D", "", q["questionNumber"]) or 0),
            q["questionNumber"],
        )
    )

    counts = collections.Counter(s for q in questions for s in q["topics"])
    gated = sorted(s for s, n in counts.items() if n >= GATE)

    # No build-date stamp. It made every rebuild produce a diff even when
    # nothing about the data had changed, so "re-run and check git diff is
    # empty" - the only cheap way to tell a real change from a no-op - did not
    # work. Nothing ever read the field. Same defect be3ec19 fixed for the
    # sitemap's <lastmod>; the JSON payloads were missed. PH09b-025.
    index = {
        "count": len(questions),
        "gate": GATE,
        "boards": [
            {
                "board": b["board"],
                "name": b["name"],
                "qualification": b["qualification"],
                "papersUrl": b["papersUrl"],
                "url": f"/past-paper-questions/{b['board']}/",
                "groups": [
                    {
                        "slug": g["slug"],
                        "label": g["label"],
                        "name": g["name"],
                        "fullName": g["fullName"],
                        "notesIndexUrl": g["notesIndexUrl"],
                        "url": f"/past-paper-questions/{b['board']}/{g['slug']}/",
                    }
                    for g in b["groups"]
                ],
            }
            for b in taxonomy["boards"]
        ],
        "papers": paper_table,
        # hasPage and gated are the same thing now that this script generates
        # the topic pages in the same run that writes this index. They are kept
        # as separate fields because the UI asks "can I link there?" while the
        # report asks "does this topic clear the gate?", and a future change
        # could make those differ again.
        "topics": {
            slug: dict(
                meta,
                count=counts.get(slug, 0),
                gated=slug in gated,
                hasPage=slug in gated,
            )
            for slug, meta in topics.items()
            if counts.get(slug, 0) > 0
        },
        "questions": questions,
    }
    return index, counts, gated, errors, untagged


# ---------------------------------------------------------------- master page

# The master page covers every board in the bank, so its title must not name
# one. Naming Edexcel here made it byte-identical to the Edexcel board page's
# generated title and gave the site its only pair of duplicate titles.
#
# How the master page names the boards, keyed by the set of bank boards with
# questions: (title phrase, prose phrase). Visible wording, so each is
# approved rather than derived - joining names with "and" gave "Edexcel and
# AQA and Edexcel B". The three-board pair follows the practice and
# flashcards hubs; approved by Eliot, 2026-11-17 (launch-pastPaperBank.md
# L1). A live set with no phrase stops the build rather than guess one.
BOARDS_PHRASE = {
    frozenset({"edexcel", "aqa"}): ("Edexcel & AQA", "Edexcel and AQA"),
    frozenset({"edexcel", "aqa", "edexcel-b"}): (
        "Edexcel A, Edexcel B & AQA", "Edexcel A, Edexcel B and AQA"),
}
TITLE = "A-Level Economics Past Paper Questions | {} | Economics Academy"

# How the bank names a board's qualification where boards.json's single
# A Level string would be wrong: the Edexcel A and Edexcel B banks hold AS
# cards as well (8EC0, 8EB0). Wording approved by Eliot, 2026-11-25
# (review/launch-section-a.md W2 A, W3). Three slots: the board hub's meta and
# JSON-LD description, its hero intro, and its heading on the master page.
# boards.json is left alone - the notes, practice and flashcard families read
# it too. A board not listed keeps that string everywhere. AQA joined with its
# AS Section A MCQs (7135), in the bank's form rather than AQA's own "AS":
# approved by Eliot, 2026-11-25 (D71, review/phase-9-aqa-as-mcqs.md W1-W3).
QUALIFICATION_PHRASE = {
    "edexcel": {
        "meta": "A Level 9EC0 and AS Level 8EC0",
        "intro": "A Level (9EC0) and AS Level (8EC0)",
        "heading": "A Level (9EC0) and AS Level (8EC0) Economics A",
    },
    "edexcel-b": {
        "meta": "A Level 9EB0 and AS Level 8EB0",
        "intro": "A Level (9EB0) and AS Level (8EB0)",
        "heading": "A Level (9EB0) and AS Level (8EB0) Economics B",
    },
    "aqa": {
        "meta": "A Level 7136 and AS Level 7135",
        "intro": "A Level (7136) and AS Level (7135)",
        "heading": "A Level (7136) and AS Level (7135) Economics",
    },
}


# The notes a multiple-choice card prints when the paper's figure or options
# cannot be shown (Phase 7). FIGURE_NOTE is W2, approved by Eliot 2026-11-25
# (review/phase-7-mcqs.md). OPTIONS_NOTE replaces it when the options
# themselves are not text - a table's rows, diagrams, fractions or bare
# letters on a figure - and is W3 as reworded in review/mcq-tags.md (T3 A,
# approved by Eliot 2026-11-25): one sentence true for every kind, since the
# record does not say which kind it is. Restated character for character in
# question-search.js;
# scripts/test_question_search.js holds the two together.
FIGURE_NOTE = ("Uses a table or diagram printed in the paper: open the "
               "question paper to see it.")
OPTIONS_NOTE = ("The four options are printed in the paper and are not shown "
                "here: open the question paper to see them.")
MCQ_BADGE = "Multiple choice"


def qualification_phrase(board, slot):
    """The board's qualification as the bank names it in `slot`."""
    return QUALIFICATION_PHRASE.get(board["board"], {}).get(slot, board["qualification"])

# The description is derived, not written down. The hard-coded one it replaced
# was authored before AQA and the Edexcel AS papers joined the bank and still
# claimed "every Edexcel (9EC0) question from 2017 to 2024" long after both had
# stopped being true. render_index() now builds it from the same values the hero
# prose uses, so adding a paper cannot make it stale again.


def e(s):
    """HTML-escape, matching escapeHtml() in question-search.js exactly.

    Not html.escape: that also turns an apostrophe into &#x27;, which the
    JavaScript does not, and the two renderers must agree character for
    character. Attribute values here are always double-quoted, so leaving the
    apostrophe alone is safe.
    """
    return (
        str(s)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def search_component(topic="", board="", group="", src="", hub=False,
                     mixed=None):
    """The search UI skeleton.

    Rendered identically on the master page, the board and section pages and the
    topic pages; only the pre-filter attributes and `data-src` differ.

    `src` overrides the payload the component fetches. A topic page has no use
    for the other 537 questions and fetching them cost it 413.7 KB, so it
    points at its own payload instead - a median of 9.6 KB. Since 2026-08-23
    the board and section pages point at their board's payload, which carries
    every topic on the board - what their Topic filter lists. Only the master
    page leaves it empty and gets the full index.

    `mixed` is the Question type filter (Phase 7): None leaves the field out
    of the page entirely - the state of every page while no MCQ is live, so
    staging them changed no byte - and otherwise it is present, and hidden
    in the served HTML unless the page's payload holds both types. Every
    Edexcel B page and every topic page with no MCQ keeps today's height
    (PH08-035). See type_mix().

    `hub` marks a board hub, which bakes HUB_CARDS cards rather than all of
    them, so its <noscript> note says where the rest are instead of claiming
    they are all below.

    The controls ship VISIBLE and disabled, and question-search.js enables them
    once questions.json has loaded. They used to ship `hidden` and be revealed
    by the script, which meant a padded, bordered, nine-field panel appeared
    after a 414 KB network round trip and pushed every result card down the
    page - a measured CLS of 0.253, against Google's 0.1 threshold, and the
    worst Core Web Vital on the site. PH08-035.

    Nothing in CSS could fix that: the component enforces
    `[hidden] { display: none !important }`, and a min-height on a display:none
    element reserves no space at all.

    Two things follow, and both matter for the layout to be stable:

    - The fields a pre-filtered page fixes are marked `hidden` HERE, in the
      served HTML, not by the script afterwards. Hiding them later would shrink
      the panel after first paint and simply move the shift rather than remove
      it.
    - A reader without JavaScript now sees the panel rather than nothing, so a
      <noscript> note says why it is inert. The question list below it is static
      HTML and works with scripting off exactly as before.
    """
    attr = ' data-src="' + e(src) + '"' if src else ""
    # A control is meaningless on a page already fixed to that value, so the
    # page ships without it. Mirrors what question-search.js used to do at
    # runtime; doing it here keeps the panel one fixed height from first paint.
    fixed = set()
    if topic:
        # A topic already implies its board and section.
        # `+=`, not `=`: this used to overwrite whatever attr already held,
        # which silently dropped data-src on exactly the pages that need it.
        attr += ' data-prefilter-topic="' + e(topic) + '"'
        fixed |= {"topic", "board", "group"}
    else:
        if board:
            attr += ' data-prefilter-board="' + e(board) + '"'
            fixed.add("board")
        if group:
            attr += ' data-prefilter-group="' + e(group) + '"'
            fixed.add("group")
    # "Section" here is the paper's section (A/B/C), distinct from the board's
    # section grouping, which is labelled Theme or Micro/Macroeconomics.
    fields = [
        ("board", "Board", "All boards"),
        # Defaults to showing both, per the owner's decision: an AS question is
        # still a real question on a Theme 1-2 topic, and hiding it by default
        # would make the Theme 1-2 pages look emptier than they are. The badge
        # does the disambiguating; this narrows.
        ("level", "Qualification", "AS and A Level"),
        ("group", "Theme / area", "All areas"),
        ("paper", "Paper", "All papers"),
        ("topic", "Topic", "All topics"),
        ("marks", "Marks", "All marks"),
        ("type", "Question type", "All types"),
        ("year", "Year", "All years"),
        ("section", "Paper section", "All sections"),
    ]
    if mixed is None:
        fields = [f for f in fields if f[0] != "type"]
    elif not mixed:
        fixed.add("type")
    field_html = "\n".join(
        f"""              <div class="ppq-field"{' hidden' if k in fixed else ''}>
                <label for="ppq-{k}">{lbl}</label>
                <select id="ppq-{k}" data-ppq-filter="{k}" data-ppq-all="{all_}" disabled></select>
              </div>"""
        for k, lbl, all_ in fields
    )

    if hub:
        noscript_note = (
            "                  These filters need JavaScript. The most recent\n"
            "                  questions are listed below, and every question is\n"
            "                  listed on its section and topic pages, linked further\n"
            "                  down. All the paper and mark scheme links work."
        )
    else:
        noscript_note = (
            "                  These filters need JavaScript. Every question is still listed\n"
            "                  below, grouped by topic, and all the paper and mark scheme\n"
            "                  links work."
        )

    return f"""          <div class="ppq-search" data-question-search{attr}>
            <form class="ppq-controls" data-ppq-controls aria-busy="true">
              <noscript>
                <p class="ppq-noscript">
{noscript_note}
                </p>
              </noscript>
              <div class="ppq-search-field">
                <label class="sr-only" for="ppq-query">Search past paper questions</label>
                <input
                  type="search"
                  id="ppq-query"
                  class="ppq-search-input"
                  data-ppq-query
                  placeholder="Search questions, topics or keywords&hellip;"
                  autocomplete="off"
                  spellcheck="false"
                  disabled
                />
              </div>
              <div class="ppq-fields">
{field_html}
                <div class="ppq-field">
                  <label for="ppq-sort">Sort</label>
                  <select id="ppq-sort" data-ppq-sort disabled>
                    <option value="relevance">Relevance</option>
                    <option value="newest">Newest first</option>
                    <option value="marks">Marks (high to low)</option>
                  </select>
                </div>
                <button type="button" class="ppq-clear" data-ppq-clear disabled>Clear all</button>
              </div>
            </form>

            <p class="ppq-error" data-ppq-error hidden>
              The question search could not load. Every question is still listed
              by topic below, and all the mark scheme links work.
            </p>

            <div class="ppq-status">
              <p class="ppq-count" data-ppq-count role="status" aria-live="polite"></p>
            </div>

            <div class="ppq-results" data-ppq-results></div>

            <div class="ppq-empty" data-ppq-empty hidden>
              <p><strong>No questions match that search.</strong></p>
              <p>
                Try a broader term &mdash; for example
                <em>monopoly</em>, <em>inflation</em>, <em>exchange rates</em>,
                <em>externalities</em> or <em>25 marks</em>.
              </p>
            </div>

            <button type="button" class="button ppq-more" data-ppq-more hidden>
              Show more
            </button>
          </div>"""


def type_mix(index, questions):
    """search_component()'s `mixed`: None while no MCQ is in the build, else
    whether `questions` - the page's payload - holds both types."""
    if not any(q.get("type") == "mcq" for q in index["questions"]):
        return None
    return len({q.get("type", "written") for q in questions}) > 1


def render_card(q, index):
    """Server-rendered question card.

    Must stay markup-identical to cardHtml() in js/components/question-search.js.
    Topic and theme pages ship their questions as real HTML so crawlers and
    readers without JavaScript get the content; the component then re-renders
    the same list from JSON. If the two drifted, enabling JavaScript would
    silently change the page. scripts/test_question_search.js compares the two
    renderers over all 112 questions and fails if they diverge.
    """
    paper = index["papers"][q["p"]]
    topics = index["topics"]

    # The qualification badge sits second, straight after the board, because an
    # A Level student who revises from an AS question without noticing gets a
    # distorted picture of the demand. It is on every card, in the static HTML,
    # not applied by script after load.
    badges = [
        f'<span class="ppq-badge ppq-badge-board">{e(paper["boardName"])}</span>',
        f'<span class="ppq-badge ppq-badge-level ppq-badge-level-{e(paper["level"])}">'
        f'{e(paper["levelLabel"])}</span>',
        f'<span class="ppq-badge ppq-badge-paper">Paper {paper["paper"]}</span>',
        f'<span class="ppq-badge">{e(paper["series"] + " " + str(paper["year"]))}</span>',
        # "1 mark", singular: Section A brought the bank's first 1-mark
        # cards (Eliot, 2026-11-25, review/launch-section-a.md W1). Kept
        # character-equal with cardHtml() in question-search.js.
        f'<span class="ppq-badge ppq-badge-marks">{q["marks"]} '
        f'{"mark" if q["marks"] == 1 else "marks"}</span>',
    ]
    # Phase 7: the type badge follows the marks, on multiple-choice cards
    # only. Neutral grey, so it does not compete with the qualification.
    if q.get("type") == "mcq":
        badges.append(f'<span class="ppq-badge ppq-badge-type">{MCQ_BADGE}</span>')
    # Keyed (board, slug): Edexcel A and Edexcel B both have a theme-1.
    groups = {(b["board"], g["slug"]): g
              for b in index["boards"] for g in b["groups"]}
    for slug in q["groups"]:
        g = groups.get((q["board"], slug))
        label = g["label"] if g else slug
        badges.append(f'<span class="ppq-badge ppq-badge-theme">{e(label)}</span>')

    links = []
    for slug in q["topics"]:
        t = topics.get(slug)
        if not t:
            continue
        label = e(t["spec"] + " " + t["shortTitle"])
        if t["hasPage"]:
            links.append(f'<a href="{e(t["url"])}">{label}</a>')
        else:
            links.append(f"<span>{label}</span>")
    topic_links = " &middot; ".join(links)

    # Question paper first: a student who wants to attempt this under exam
    # conditions needs the question as it was printed, before anything else.
    qp_url = e(paper["questionPaperUrl"] + "#page=" + str(q["qpPage"]))
    actions = [
        f'<a class="ppq-action" href="{qp_url}" target="_blank" '
        f'rel="noopener noreferrer">Question paper &mdash; p.{q["qpPage"]}</a>'
    ]
    if q["ctxPage"]:
        ctx = e(paper["questionPaperUrl"] + "#page=" + str(q["ctxPage"]))
        ctx_label = e(q["ctxLabel"]) if q.get("ctxLabel") else "View the extract"
        actions.append(
            f'<a class="ppq-action" href="{ctx}" target="_blank" '
            f'rel="noopener noreferrer">{ctx_label} &mdash; p.{q["ctxPage"]}</a>'
        )
    ms = e(paper["markSchemeUrl"] + "#page=" + str(q["msPage"]))
    actions.append(
        f'<a class="ppq-action" href="{ms}" target="_blank" '
        f'rel="noopener noreferrer">Mark scheme &mdash; p.{q["msPage"]}</a>'
    )
    first = topics.get(q["topics"][0]) if q["topics"] else None
    if first:
        actions.append(
            f'<a class="ppq-action" href="{e(first["notesUrl"])}">'
            f'Revision notes: {e(first["spec"])}</a>'
        )
    if q["modelAnswer"]:
        actions.append(
            f'<a class="ppq-action ppq-action-model" href="{e(q["modelAnswer"])}">'
            "Model answer</a>"
        )

    note = ""
    if paper.get("note"):
        note = f'<p class="ppq-note">{e(paper["note"])}</p>'

    # The options as printed, lettered as text, with nothing to click: there
    # is no answer to reveal (D67). When the options are not text, the list
    # is left out and OPTIONS_NOTE says where they are.
    options = ""
    figure = ""
    if q.get("type") == "mcq":
        if q["options"]:
            options = '<ol class="ppq-options">' + "".join(
                f'<li><span class="ppq-option-letter">{letter}</span> {e(text)}</li>'
                for letter, text in zip("ABCD", q["options"])) + "</ol>"
            if q["usesFigure"]:
                figure = f'<p class="ppq-figure">{e(FIGURE_NOTE)}</p>'
        else:
            figure = f'<p class="ppq-figure">{e(OPTIONS_NOTE)}</p>'

    choice = ""
    if q["choiceGroup"]:
        choice = (
            f'<p class="ppq-choice">One of two options in Section {e(q["section"])} '
            "&mdash; candidates answered this <em>or</em> the other.</p>"
        )

    return (
        f'<article class="ppq-card" id="{e(q["id"])}">'
        f'<div class="ppq-badges">{"".join(badges)}</div>'
        f'<p class="ppq-question">{e(q["questionText"])}</p>'
        f"{options}"
        f"{figure}"
        f"{note}"
        f"{choice}"
        + (f'<p class="ppq-topics">{topic_links}</p>' if topic_links else "")
        + f'<div class="ppq-actions">{"".join(actions)}</div>'
        "</article>"
    )


def json_ld(obj):
    """JSON-LD indented to sit inside the page's <script> block."""
    s = json.dumps(obj, indent=2)
    return "\n".join("      " + line for line in s.split("\n")).strip()


def visible_href(path):
    """Links are written in canonical form - the same URL the page canonicalises to.

    This used to return "/index.html" for the home link, because that was the
    site's convention. Both forms return 200 on GitHub Pages, so the convention
    was creating a duplicate URL for every hub page and splitting its ranking
    signals across the two.
    """
    return path


def breadcrumb_html(crumbs):
    """The crumbs joined inline, for the <nav> page_shell() writes. This
    family's trail is laid out differently from the flashcards/glossary one
    (page_shell.breadcrumb_html): the separator sits on its own line between
    crumbs at a fixed indent, and the href is run through visible_href() and
    e() - kept as it was, byte for byte."""
    sep = '\n            <span class="separator">&rsaquo;</span>\n            '
    parts = []
    for name, path in crumbs:
        if path:
            parts.append(f'<a href="{e(visible_href(path))}">{e(name)}</a>')
        else:
            parts.append(f"<span>{e(name)}</span>")
    return sep.join(parts)


def breadcrumb_ld(crumbs):
    return shell.breadcrumb_ld(crumbs)


def page_shell(title, desc, path, crumbs, body):
    """The head and body boilerplate every page in this section shares.

    Structured data is CollectionPage plus BreadcrumbList, matching the rest of
    the site. Deliberately NOT schema.org Quiz/Question: that markup expects an
    acceptedAnswer or suggestedAnswer, and this bank does not host answers by
    design - it links to Pearson's mark schemes. Declaring Question without an
    answer earns no rich result and misrepresents the page.

    2026-08-23: the skeleton and the og/twitter block come from page_shell.py;
    e() stays this family's own (it must match question-search.js's
    escapeHtml), which is why it is passed in.
    """
    url = SITE + path
    collection = {
        "@context": "https://schema.org",
        "@type": "CollectionPage",
        "name": title.split(" | ")[0],
        "description": desc,
        "url": url,
        "inLanguage": "en-GB",
        "isPartOf": {
            "@type": "WebSite",
            "name": "Economics Academy",
            "url": SITE,
        },
        "publisher": shell.ORGANISATION_REF,
    }
    values = shell.head_values(title, desc, url,
                               ["/css/pages/past-paper-questions.css"], esc=e)
    values.update({
        "jsonldBeforeIcons": [collection, breadcrumb_ld(crumbs)],
        # This family escapes non-ASCII in its JSON-LD where the notes pages
        # carry literal characters - 87 pages emit \u2014 for an em dash. Both
        # are valid and parse identically; the flag records which, so the swap
        # rewrites nothing.
        "jsonldAsciiEscaped": True,
    })
    inner = (
        f'          <nav class="breadcrumb" aria-label="Breadcrumb">\n'
        f"            {breadcrumb_html(crumbs)}\n"
        f"          </nav>\n"
        f"\n"
        f"{body}"
    )
    return shell.page(
        shell.render_head(values),
        shell.container(inner, "past-paper-questions-page"),
        ("/js/components/question-search.js",),
    )


CTA = """          <section class="ppq-cta">
            <h2>Practising past papers is only half of it</h2>
            <p>
              <strong
                >Past papers show you the question &mdash; feedback shows you the
                marks.</strong
              >
              Send an essay for examiner-style marking, or work through the
              topics you keep losing marks on with a specialist tutor.
            </p>
            <div class="ppq-cta-actions">
              <a href="/revision-notes/" class="button alt">Free Revision Notes</a>
              <a href="/marking.html" class="button alt">Get Your Essays Marked</a>
              <a href="/tutoring.html" class="button">Enquire About Tutoring</a>
            </div>
          </section>"""


def question_count_phrase(n):
    return "1 question" if n == 1 else f"{n} questions"


def year_span(index, questions):
    """The years phrase that follows a comma in every hero and description.

    A range keeps the en dash it has always had, so nothing that spans two or
    more years changes. A single year cannot use the same shape: ", 2018."
    lands as a stray date stamp in a slot the reader is expecting a span in.

    The gate change of 2026-08-24 made that reachable for the first time - no
    page with four or more questions has ever drawn them all from one year, but
    two of the 46 new two-question pages do (2.4.4 The Multiplier and 4.2.1
    Absolute and Relative Poverty, both 2018). "all set in 2018" says the same
    thing and reads correctly in all three slots that use this: the hub and
    section heroes, the topic hero, and the meta description of each.
    """
    years = sorted({index["papers"][q["p"]]["year"] for q in questions})
    if not years:
        return ""
    if years[0] != years[-1]:
        return f"{years[0]}&ndash;{years[-1]}"
    return f"set in {years[0]}" if len(questions) == 1 else f"all set in {years[0]}"


def level_phrase(index, questions):
    """Which qualifications' papers a set of questions came from, for the
    topic and section heroes: "A-Level", "AS" or "A-Level and AS". The same
    three readings as the notes tail (`notes_extras.past_paper_note()`).

    Both heroes said "A-Level" whatever they held, so an AS-only page named
    the wrong papers (launch-pastPaperMcqs.md N1, 2026-11-25). An A-Level-only
    page reads exactly as it always has."""
    levels = {index["papers"][q["p"]]["level"] for q in questions}
    if levels == {"as-level"}:
        return "AS"
    if "as-level" in levels:
        return "A-Level and AS"
    return "A-Level"


def static_cards(index, questions):
    """Questions as real HTML, so the page is complete before any script runs."""
    return "\n".join("            " + render_card(q, index) for q in questions)


def newest_first(index, questions):
    """The component's default order: year descending, then question number.

    question-search.js run() sorts by paper year descending and then by
    compareQuestionNumbers(): the number first, then the label as a string
    (Phase 7 - AQA's MCQs are Q1-Q30, and as strings "10" sorts before "2").
    This sorts the same way, so the hub's baked cards are the ones the live
    list shows first, in that order. Ties on all keys are left in index order.
    """
    return sorted(
        questions,
        key=lambda q: (-index["papers"][q["p"]]["year"],
                       int(re.sub(r"\D", "", q["questionNumber"]) or 0),
                       q["questionNumber"]),
    )


def hub_static_note(shown, total):
    """The sentence a board hub carries after its baked cards, inside the
    results container so the component's first render removes it."""
    return (
        f'            <p class="ppq-static-note">\n'
        f"              Showing the {shown} most recent of {total} questions. Every\n"
        f"              question is listed on its section and topic pages below, and\n"
        f"              the filters above search all {total}.\n"
        f"            </p>"
    )


def board_payload(index, board_slug):
    """The search payload for one board's hub and section pages.

    topic_payload()'s shape, narrowed to a board: its own board record, the
    papers it references (sparse, nulls kept - see topic_payload for why),
    every topic on the board (which is every topic any of its questions is
    tagged with, and is what the live Topic filter lists on these pages), and
    its questions. About half the master index; nobody filtering Edexcel
    downloads AQA.
    """
    questions = questions_for(index, board=board_slug)
    used_papers = {q["p"] for q in questions}
    used_topics = sorted({t for q in questions for t in q["topics"]})
    return {
        "count": len(questions),
        "gate": index["gate"],
        "boards": [b for b in index["boards"] if b["board"] == board_slug],
        "papers": [p if i in used_papers else None
                   for i, p in enumerate(index["papers"])],
        "topics": {t: index["topics"][t] for t in used_topics
                   if t in index["topics"]},
        "questions": questions,
    }


# ---------------------------------------------------------------- master page


def board_of(index, slug):
    return index["boards"][0] if not slug else next(
        b for b in index["boards"] if b["board"] == slug
    )


def group_of(index, board_slug, group_slug):
    b = board_of(index, board_slug)
    return next(g for g in b["groups"] if g["slug"] == group_slug)


def topics_in(index, *, board=None, group=None):
    """Topics that have questions, in spec order, optionally filtered."""
    out = [
        s
        for s, t in index["topics"].items()
        if (board is None or t["board"] == board)
        and (group is None or t["group"] == group)
    ]
    return sorted(out, key=lambda s: [int(p) for p in index["topics"][s]["spec"].split(".")])


def questions_for(index, *, board=None, group=None, topic=None):
    out = []
    for q in index["questions"]:
        if topic is not None and topic not in q["topics"]:
            continue
        if board is not None and q["board"] != board:
            continue
        if group is not None and group not in q["groups"]:
            continue
        out.append(q)
    return out


def topic_list_html(index, slugs, indent=16):
    pad = " " * indent
    rows = []
    for slug in slugs:
        t = index["topics"][slug]
        label = e(t["spec"] + " " + t["shortTitle"])
        link = f'<a href="{e(t["url"])}">{label}</a>' if t["hasPage"] else label
        rows.append(
            f'{pad}<li>{link} <span class="ppq-topic-count">'
            f'{question_count_phrase(t["count"])}</span></li>'
        )
    return "\n".join(rows)


# ---------------------------------------------------------------- master page


def render_index(index):
    years = sorted({p["year"] for p in index["papers"]})
    boards_with = [
        b for b in index["boards"] if questions_for(index, board=b["board"])
    ]
    live = frozenset(b["board"] for b in boards_with)
    if live not in BOARDS_PHRASE:
        sys.exit(
            f"build_past_paper_questions: BOARDS_PHRASE has no wording for "
            f"the bank boards {sorted(live)}. The master page's title, "
            f"description and intro name them, so add an approved phrase."
        )
    title_names, names = BOARDS_PHRASE[live]
    meta = (
        f'{index["count"]} questions &middot; {years[0]}&ndash;{years[-1]} '
        f'&middot; {len(index["topics"])} topics &middot; free, no sign-up'
    )
    desc = (
        f'{index["count"]} real {names} A-Level Economics past paper questions, '
        f"{years[0]} to {years[-1]}. Search by topic, paper, year or marks; "
        "each opens its mark scheme at the right page."
    )

    blocks = []
    for b in boards_with:
        rows = []
        for g in b["groups"]:
            n = len(questions_for(index, board=b["board"], group=g["slug"]))
            if not n:
                continue
            rows.append(
                f'                <li><a href="{e(g["url"])}">{e(g["label"])}: '
                f'{e(g["name"])}</a> <span class="ppq-topic-count">'
                f"{question_count_phrase(n)}</span></li>"
            )
        n_board = len(questions_for(index, board=b["board"]))
        blocks.append(
            f"""          <div class="ppq-theme-block">
            <h3><a href="{e(b["url"])}">{e(b["name"])}</a> &mdash; {e(qualification_phrase(b, "heading"))}</h3>
            <p>{question_count_phrase(n_board)} across {len(rows)} sections.</p>
            <ul class="ppq-topic-list">
{chr(10).join(rows)}
            </ul>
          </div>"""
        )

    body = f"""          <section class="ppq-hero">
            <h1 class="ppq-h1">A-Level Economics Past Paper Questions</h1>
            <p class="ppq-intro">
              Real exam questions from the <strong>{e(names)}</strong> A-Level
              Economics papers, {years[0]} to {years[-1]}, in one searchable
              place. Filter by topic, paper, year or mark tariff, and open the
              official mark scheme at the right page.
            </p>
            <p class="ppq-hero-meta">{meta}</p>
          </section>

{search_component(mixed=type_mix(index, index["questions"]))}

          <noscript>
            <p>
              The search above needs JavaScript. Every topic is listed below, and
              all the question papers and mark schemes are available from the
              <a href="/past-papers/">past papers</a> pages.
            </p>
          </noscript>

          <header class="major">
            <h2>Browse by specification</h2>
          </header>
          <p>
            The specifications number their topics differently, so each board
            keeps its own pages and its own codes. A question is never shown
            under another board's numbering.
          </p>

{chr(10).join(blocks)}

{CTA}"""

    return page_shell(
        TITLE.format(title_names),
        desc,
        "/past-paper-questions/",
        [("Home", "/"), ("Past Paper Questions", None)],
        body,
    )


# ------------------------------------------------------------------ board hub


def render_board_page(index, board):
    qs = questions_for(index, board=board["board"])
    path = board["url"]
    span = year_span(index, qs)
    slugs = topics_in(index, board=board["board"])

    title = (
        f'{board["name"]} A-Level Economics Past Paper Questions '
        f"| Economics Academy"
    )
    desc = (
        f'{len(qs)} {board["name"]} A-Level Economics past paper questions '
        f'({qualification_phrase(board, "meta")}), {span.replace("&ndash;", " to ")}. '
        "Each links straight to the right page of the official mark scheme."
    )

    group_rows = []
    for g in board["groups"]:
        n = len(questions_for(index, board=board["board"], group=g["slug"]))
        if not n:
            continue
        group_rows.append(
            f'                <li><a href="{e(g["url"])}">{e(g["label"])}: '
            f'{e(g["name"])}</a> <span class="ppq-topic-count">'
            f"{question_count_phrase(n)}</span></li>"
        )

    body = f"""          <section class="ppq-hero">
            <h1 class="ppq-h1">
              {e(board["name"])} A-Level Economics &mdash; Past Paper Questions
            </h1>
            <p class="ppq-intro">
              {question_count_phrase(len(qs))} from the {e(board["name"])}
              {e(qualification_phrase(board, "intro"))} papers, {span}. Every question links to
              the official mark scheme at the page its answer begins on.
            </p>
            <p class="ppq-hero-meta">
              <a href="{e(board["papersUrl"])}">{e(board["name"])} past papers</a>
              &middot;
              <a href="/past-paper-questions/">All past paper questions</a>
            </p>
          </section>

{search_component(board=board["board"], src=path + "questions.json", hub=True, mixed=type_mix(index, questions_for(index, board=board["board"])))}

          <header class="major">
            <h2>Browse by section</h2>
          </header>
          <div class="ppq-theme-block">
            <ul class="ppq-topic-list">
{chr(10).join(group_rows)}
            </ul>
          </div>

          <header class="major">
            <h2>All topics with questions</h2>
          </header>
          <div class="ppq-theme-block">
            <ul class="ppq-topic-list">
{topic_list_html(index, slugs)}
            </ul>
          </div>

{CTA}"""

    shown = newest_first(index, qs)[:HUB_CARDS]
    body = body.replace(
        '<div class="ppq-results" data-ppq-results></div>',
        '<div class="ppq-results" data-ppq-results>\n'
        + static_cards(index, shown)
        + "\n"
        + hub_static_note(len(shown), len(qs))
        + "\n          </div>",
    )

    crumbs = [
        ("Home", "/"),
        ("Past Paper Questions", "/past-paper-questions/"),
        (board["name"], None),
    ]
    return path, page_shell(title, desc, path, crumbs, body)


# ---------------------------------------------------------------- group pages


def render_group_page(index, board, group):
    qs = questions_for(index, board=board["board"], group=group["slug"])
    path = group["url"]
    span = year_span(index, qs)
    slugs = topics_in(index, board=board["board"], group=group["slug"])

    title = (
        f'{board["name"]} {group["label"]} Past Paper Questions '
        f"&mdash; A-Level Economics | Economics Academy"
    )
    title = html.unescape(title)
    desc = (
        f'{len(qs)} {board["name"]} A-Level Economics past paper questions on '
        f'{group["label"]}: {group["name"]}, '
        f'{span.replace("&ndash;", " to ")}. Each links straight to the right '
        "page of the official mark scheme."
    )
    if len(desc) > 300:
        desc = desc[:297] + "..."

    body = f"""          <section class="ppq-hero">
            <h1 class="ppq-h1">
              {e(board["name"])} {e(group["label"])}: {e(group["name"])}
              &mdash; Past Paper Questions
            </h1>
            <p class="ppq-intro">
              {question_count_phrase(len(qs))} from the {e(board["name"])}
              {level_phrase(index, qs)} Economics papers, {span}, covering
              {e(group["label"])}. Every question links to the official mark
              scheme at the page its answer begins on.
            </p>
            <p class="ppq-hero-meta">
              <a href="{e(group["notesIndexUrl"])}">{e(group["label"])} revision notes</a>
              &middot;
              <a href="{e(board["url"])}">All {e(board["name"])} questions</a>
              &middot;
              <a href="/past-paper-questions/">All past paper questions</a>
            </p>
          </section>

{search_component(board=board["board"], group=group["slug"], src=board["url"] + "questions.json", mixed=type_mix(index, questions_for(index, board=board["board"])))}

          <header class="major">
            <h2>Topics in {e(group["label"])}</h2>
          </header>
          <div class="ppq-theme-block">
            <ul class="ppq-topic-list">
{topic_list_html(index, slugs)}
            </ul>
          </div>

{CTA}"""

    body = body.replace(
        '<div class="ppq-results" data-ppq-results></div>',
        '<div class="ppq-results" data-ppq-results>\n'
        + static_cards(index, qs)
        + "\n          </div>",
    )

    crumbs = [
        ("Home", "/"),
        ("Past Paper Questions", "/past-paper-questions/"),
        (board["name"], board["url"]),
        (group["label"], None),
    ]
    return path, page_shell(title, desc, path, crumbs, body)


# ---------------------------------------------------------------- topic pages


def title_collisions(index):
    """(board, title) pairs that more than one PUBLISHED topic page shares.

    Edexcel has exactly one: "Balance of Payments" is both 2.1.4, the account
    itself in Theme 2, and 4.1.7, the global-economy treatment in Theme 4. Both
    cleared the gate on 2026-08-24 and would otherwise have shipped with an
    identical <title>, meta description and <h1> - which is a duplicate-title
    fault Google acts on, and which seo/tools/verify_seo.py check 6 catches.

    Computed rather than listed, so a second collision disambiguates itself the
    moment it appears instead of shipping and being spotted later. Nothing is
    appended when there is no clash, so the other 125 pages are untouched.
    """
    seen = collections.Counter(
        (t["board"], t["title"]) for t in index["topics"].values() if t["hasPage"]
    )
    return {pair for pair, n in seen.items() if n > 1}


def display_title(index, slug, collisions):
    """The topic's title, with its section appended only where it has to be.

    "Balance of Payments (Theme 2)" is the spelling revision-notes/ already
    uses for this pair - see verify_seo.py's KNOWN_H1_COLLISION - so the two
    families read as twins rather than as two different fixes for one problem.
    """
    t = index["topics"][slug]
    if (t["board"], t["title"]) not in collisions:
        return t["title"]
    return f'{t["title"]} ({t["groupLabel"]})'


def related_topics(index, slug):
    """Same unit first, then the rest of the group. Same board only."""
    me = index["topics"][slug]
    same_unit, same_group = [], []
    for other, t in index["topics"].items():
        if other == slug or not t["hasPage"]:
            continue
        if t["board"] != me["board"] or t["group"] != me["group"]:
            continue
        (same_unit if t["unit"] == me["unit"] else same_group).append(other)

    key = lambda s: [int(p) for p in index["topics"][s]["spec"].split(".")]
    return (sorted(same_unit, key=key) + sorted(same_group, key=key))[:6]


def topic_payload(index, slug):
    """The search payload for one topic page: same shape, a fraction of the size.

    The full index is 413.7 KB and every one of the 81 topic pages fetched it
    to use a median of 15 questions. This is the same object with three fields
    narrowed. PH08-046.

    `papers` stays a **sparse list**, with `None` in every slot the page does
    not reference, because `question-search.js` addresses it as `data.papers[q.p]`
    - `q.p` is an index into it, so re-packing the list would silently
    re-point every question at the wrong paper. Nulls cost about 300 bytes and
    keep the indexing exactly as it is. Verified: the component never iterates
    `papers`, only subscripts it (question-search.js:136 and :393).

    `topics` keeps every topic any included question is tagged with, not just
    this one, because the cards render a link per tag. The Topic filter, which
    is the other consumer of that field, is hidden on a topic page.

    One deliberate behaviour change: `populate()` builds the Paper, Year,
    Marks, Section and Qualification dropdowns from the payload, so they now
    offer only values that exist on the page. A topic page used to list all 9
    years when a mean of 4.9 have questions, and all 3 papers when a mean of
    1.7 do; picking one of the others returned nothing. Those options are gone.
    """
    questions = questions_for(index, topic=slug)
    used_papers = {q["p"] for q in questions}
    used_topics = sorted({t for q in questions for t in q["topics"]})
    return {
        "count": len(questions),
        "gate": index["gate"],
        "boards": index["boards"],
        "papers": [p if i in used_papers else None
                   for i, p in enumerate(index["papers"])],
        "topics": {t: index["topics"][t] for t in used_topics
                   if t in index["topics"]},
        "questions": questions,
    }


def render_topic_page(index, slug, collisions=frozenset()):
    t = index["topics"][slug]
    board = board_of(index, t["board"])
    group = group_of(index, t["board"], t["group"])
    qs = questions_for(index, topic=slug)
    path = t["url"]
    span = year_span(index, qs)
    name = display_title(index, slug, collisions)

    title = (
        f'{name} Past Paper Questions &mdash; {board["name"]} A-Level '
        f"Economics | Economics Academy"
    )
    title = html.unescape(title)
    desc = (
        f'{len(qs)} {board["name"]} A-Level Economics past paper questions on '
        f'{name} (spec {t["spec"]}), {span.replace("&ndash;", " to ")}. '
        "Each links straight to the right page of the official mark scheme."
    )
    if len(desc) > 300:
        desc = desc[:297] + "..."

    related = related_topics(index, slug)
    related_html = ""
    if related:
        related_html = f"""
          <header class="major">
            <h2>Related topics</h2>
          </header>
          <div class="ppq-theme-block">
            <ul class="ppq-topic-list">
{topic_list_html(index, related)}
            </ul>
          </div>
"""

    body = f"""          <section class="ppq-hero">
            <h1 class="ppq-h1">
              {e(name)} &mdash; {e(board["name"])} Past Paper Questions
            </h1>
            <p class="ppq-intro">
              {question_count_phrase(len(qs))} on <strong>{e(name)}</strong>
              ({e(board["name"])} specification {e(t["spec"])}) from the {level_phrase(index, qs)}
              Economics papers, {span}. Every question links to the official mark
              scheme at the page its answer begins on.
            </p>
            <p class="ppq-hero-meta">
              <a href="{e(t["notesUrl"])}">Revision notes: {e(t["spec"])} {e(t["shortTitle"])}</a>
              &middot;
              <a href="{e(t["questionsUrl"])}">Practice questions</a>
              &middot;
              <a href="{e(group["url"])}">{e(group["label"])}</a>
              &middot;
              <a href="{e(board["url"])}">All {e(board["name"])} questions</a>
            </p>
          </section>

{search_component(topic=slug, src=path + "questions.json", mixed=type_mix(index, questions_for(index, topic=slug)))}
{related_html}
{CTA}"""

    body = body.replace(
        '<div class="ppq-results" data-ppq-results></div>',
        '<div class="ppq-results" data-ppq-results>\n'
        + static_cards(index, qs)
        + "\n          </div>",
    )

    crumbs = [
        ("Home", "/"),
        ("Past Paper Questions", "/past-paper-questions/"),
        (board["name"], board["url"]),
        (group["label"], group["url"]),
        (t["shortTitle"], None),
    ]
    return path, page_shell(title, desc, path, crumbs, body)


# ---------------------------------------------------------------- sitemap


HUB_PAGE = ROOT / "past-papers" / "index.html"
HUB_COUNT_RE = re.compile(r"(<!-- ppq-count -->)\s*[\d,]+\s*(<!-- /ppq-count -->)")


def update_hub_count(index):
    """Refresh the question count in the past-papers hub's CTA.

    That page is hand-written; this rewrites only the digits between the
    ppq-count markers, so the copy around them stays the author's. Without it
    the number silently goes stale the first time the bank grows, and nothing
    would flag it.
    """
    if not HUB_PAGE.is_file():
        return None
    text = HUB_PAGE.read_text(encoding="utf-8")
    if not HUB_COUNT_RE.search(text):
        return None
    new = HUB_COUNT_RE.sub(rf"\g<1>{index['count']}\g<2>", text)
    if new == text:
        return False
    HUB_PAGE.write_text(new, encoding="utf-8")
    return True


SITEMAP_OPEN = "  <!-- Past Paper Questions -->"
SITEMAP_CLOSE = "  <!-- /Past Paper Questions -->"


def update_sitemap(index, paths):
    """UNUSED. scripts/build_sitemap.py owns the sitemap now: it enumerates pages from the filesystem and takes lastmod from git, so a generator stamping today's date into its own block would undo that.

    Kept for reference: it rewrote this section's block in sitemap.xml between
    HTML comment markers, stamping every entry with the date it ran.

    Same convention as the practice-questions block already in the file. The
    block is replaced wholesale, so removing a topic page removes its entry.
    Nothing outside the markers is touched.
    """
    sitemap = ROOT / "sitemap.xml"
    text = sitemap.read_text(encoding="utf-8")
    today = datetime.date.today().isoformat()

    lines = [SITEMAP_OPEN]
    for path in paths:
        depth = path.strip("/").count("/")
        priority = {0: "0.8", 1: "0.75", 2: "0.7"}.get(depth, "0.6")
        lines.append(
            f"  <url><loc>{SITE}{path}</loc><lastmod>{today}</lastmod>"
            f"<priority>{priority}</priority></url>"
        )
    lines.append(SITEMAP_CLOSE)
    block = "\n".join(lines)

    if SITEMAP_OPEN in text and SITEMAP_CLOSE in text:
        start = text.index(SITEMAP_OPEN)
        end = text.index(SITEMAP_CLOSE) + len(SITEMAP_CLOSE)
        new = text[:start] + block + text[end:]
    else:
        # First run: insert before </urlset> rather than guessing a position.
        marker = "</urlset>"
        idx = text.rindex(marker)
        new = text[:idx] + block + "\n" + text[idx:]

    if new != text:
        sitemap.write_text(new, encoding="utf-8")
        return True
    return False


def staged_boards():
    """Board keys whose bank is staged (D68): in the staged load, not the live."""
    return sorted(set(board_data.load("pastPaperBank", staged=True))
                  - set(board_data.load("pastPaperBank")))


def staged_mcq_boards():
    """Board keys whose multiple-choice questions are staged (Phase 7)."""
    return sorted(set(board_data.load("pastPaperMcqs", staged=True))
                  - set(board_data.load("pastPaperMcqs")))


def validate_staged(live_gated=()):
    """Build the bank WITH its staged boards and staged MCQs, in memory, and
    write nothing.

    Runs every check build() runs on live data - unknown or cross-board
    tags, a missing mark scheme, an MCQ's options - and renders every page
    the staged data would change, so a fault that would stop a launch stops
    this build instead. Exits 1 on any error. Returns the summary lines to
    print. `live_gated` is the live build's gated topics, so the report can
    name the topic pages the staged data would add: each is a permanent URL.
    """
    keys = staged_boards()
    mcq_keys = staged_mcq_boards()
    if not keys and not mcq_keys:
        return []
    taxonomy, tags, papers = load(staged=True)
    index, _counts, gated, errors, untagged = build(taxonomy, tags, papers)
    staged = board_data.load("pastPaperBank", staged=True)
    slugs = {staged[k]["slugs"]["taxonomy"] for k in keys}
    mcq_slugs = {staged[k]["slugs"]["taxonomy"] for k in mcq_keys}
    own = [u for u in untagged
           if any(u.startswith(s + "-") for s in slugs)]
    if own:
        errors.append(f"staged board has {len(own)} untagged question(s), "
                      f"e.g. {own[0]} - every question is tagged before launch")
    # load(staged=True) brought in the staged boards' MCQs and no others, so
    # any untagged MCQ here is one a launch would leave out.
    loose = [q["id"] for p in papers for q in p["questions"]
             if q.get("type") == "mcq" and q["id"] not in tags]
    if loose:
        errors.append(f"staged multiple-choice questions have {len(loose)} "
                      f"untagged, e.g. {loose[0]} - every MCQ is tagged first")
    if errors:
        for err in errors:
            print(f"ERROR (staged) {err}", file=sys.stderr)
        sys.exit(1)
    lines = []
    collisions = title_collisions(index)
    for board in index["boards"]:
        if board["board"] not in slugs | mcq_slugs:
            continue
        qs = questions_for(index, board=board["board"])
        pages = [render_board_page(index, board)]
        pages += [render_group_page(index, board, g) for g in board["groups"]
                  if questions_for(index, board=board["board"], group=g["slug"])]
        topics = [s for s in gated if index["topics"][s]["board"] == board["board"]]
        pages += [render_topic_page(index, s, collisions) for s in topics]
        if board["board"] in slugs:
            lines.append(
                f"  STAGED {board['board']}: {len(qs)} questions, "
                f"{len(pages) - 1 - len(topics)} section pages and "
                f"{len(topics)} topic pages at the gate of {GATE}, rendered "
                f"in memory - nothing written "
                f"(EA_PREVIEW={keys[0]}:pastPaperBank to preview)")
            continue
        mcqs = sum(1 for q in qs if q.get("type") == "mcq")
        new = [s for s in topics if s not in set(live_gated)]
        lines.append(
            f"  STAGED {board['board']} multiple choice: {mcqs} questions, "
            f"{len(new)} new topic page(s) at the gate of {GATE}, rendered "
            f"in memory - nothing written")
        lines += [f"    new page: {index['topics'][s]['url']}" for s in new]
    if mcq_keys:
        lines.append("  preview: EA_PREVIEW="
                     + ",".join(f"{k}:pastPaperMcqs" for k in mcq_keys))
    return lines


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--check",
        action="store_true",
        help="validate the INPUTS and write nothing. This does not check that committed output is current - use scripts/verify_generated.py for that",
    )
    args = ap.parse_args()

    taxonomy, tags, papers = load()
    index, counts, gated, errors, untagged = build(taxonomy, tags, papers)

    if errors:
        for e in errors:
            print(f"ERROR {e}", file=sys.stderr)
        sys.exit(1)
    staged_report = validate_staged(gated)

    years = sorted({p["year"] for p in index["papers"]})
    marks = sorted({q["marks"] for q in index["questions"]})
    print(f"{index['count']} questions from {len(papers)} papers")
    if untagged:
        by_board = collections.Counter(u.split("-")[0] for u in untagged)
        detail = ", ".join(f"{n} {b}" for b, n in sorted(by_board.items()))
        print(f"  NOT YET PUBLISHED: {len(untagged)} extracted but untagged "
              f"({detail})")
    print(f"  years  {years[0]}-{years[-1]}")
    print(f"  marks  {', '.join(str(m) for m in marks)}")
    print(f"  topics {len(counts)} with questions, {len(gated)} at or above the "
          f"gate of {GATE}")
    for line in staged_report:
        print(line)

    if args.check:
        print("check only - nothing written")
        return

    OUT.parent.mkdir(parents=True, exist_ok=True)
    # Minified: this is a build artefact the browser fetches before it can
    # search, not a file anyone reads or edits. Re-run the script to inspect it.
    OUT.write_text(
        json.dumps(index, ensure_ascii=False, separators=(",", ":")) + "\n",
        encoding="utf-8",
    )
    size = OUT.stat().st_size
    print(f"wrote {OUT.relative_to(ROOT)} ({size / 1024:.0f} KB)")

    written = [INDEX]
    payloads = []
    board_payloads = []
    paths = ["/past-paper-questions/"]

    INDEX.write_text(render_index(index), encoding="utf-8")

    def emit(path, page):
        # "/past-paper-questions/edexcel/theme-1/" -> edexcel/theme-1/index.html
        rel = path.strip("/").split("/")[1:]
        dest = PAGE_DIR.joinpath(*rel, "index.html")
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(page, encoding="utf-8")
        written.append(dest)
        paths.append(path)

    for board in index["boards"]:
        if not questions_for(index, board=board["board"]):
            continue
        emit(*render_board_page(index, board))
        # The board's payload, beside its hub, fetched by the hub and by its
        # section pages. Minified like the others.
        rel = board["url"].strip("/").split("/")[1:]
        dest = PAGE_DIR.joinpath(*rel, "questions.json")
        dest.write_text(
            json.dumps(board_payload(index, board["board"]), ensure_ascii=False,
                       separators=(",", ":")) + "\n",
            encoding="utf-8",
        )
        board_payloads.append(dest)
        print(f"wrote {dest.relative_to(ROOT)} ({dest.stat().st_size / 1024:.0f} KB)")
        for group in board["groups"]:
            if not questions_for(index, board=board["board"], group=group["slug"]):
                continue
            emit(*render_group_page(index, board, group))

    payload_bytes = 0
    collisions = title_collisions(index)
    for slug in sorted(
        gated, key=lambda s: [int(p) for p in index["topics"][s]["spec"].split(".")]
    ):
        path, page = render_topic_page(index, slug, collisions)
        emit(path, page)
        # Written beside the page it serves, minified for the same reason the
        # master payload is: nobody reads it, the browser fetches it.
        rel = path.strip("/").split("/")[1:]
        dest = PAGE_DIR.joinpath(*rel, "questions.json")
        dest.write_text(
            json.dumps(topic_payload(index, slug), ensure_ascii=False,
                       separators=(",", ":")) + "\n",
            encoding="utf-8",
        )
        payloads.append(dest)
        payload_bytes += dest.stat().st_size

    # Anything under past-paper-questions/ that this run did not write is a page
    # for a topic that has since dropped below the gate or been retagged. The
    # output is meant to be a pure function of the data, so it goes.
    keep = {p.parent for p in written}
    removed = 0
    for child in sorted(PAGE_DIR.rglob("index.html"), reverse=True):
        if child.parent in keep or child.parent == PAGE_DIR:
            continue
        child.unlink()
        removed += 1
    # Per-topic payloads go the same way, and by the same rule. The guard on
    # PAGE_DIR is what keeps the master past-paper-questions/questions.json,
    # which is not one of these and must stay published - it is what the
    # master, board and section pages fetch.
    kept_payloads = set(payloads) | set(board_payloads)
    for child in sorted(PAGE_DIR.rglob("questions.json"), reverse=True):
        if child in kept_payloads or child.parent == PAGE_DIR:
            continue
        child.unlink()
        removed += 1
    for d in sorted(PAGE_DIR.rglob("*"), reverse=True):
        if d.is_dir() and not any(d.iterdir()):
            d.rmdir()

    boards = sum(1 for p in paths if p.count("/") == 3)
    groups = sum(1 for p in paths if p.count("/") == 4 and "/theme-" in p or
                 p.count("/") == 4 and p.rstrip("/").split("/")[-1] in
                 {"microeconomics", "macroeconomics"})
    topics = len(paths) - 1 - boards - groups
    print(f"wrote {boards} board pages, {groups} section pages, {topics} topic pages")
    if payloads:
        sizes = sorted(p.stat().st_size for p in payloads)
        print(f"wrote {len(payloads)} per-topic payloads, "
              f"{payload_bytes / 1024:.0f} KB total, "
              f"median {sizes[len(sizes) // 2] / 1024:.1f} KB, "
              f"largest {sizes[-1] / 1024:.1f} KB "
              f"(each replaces a {size / 1024:.0f} KB fetch)")
    if removed:
        print(f"removed {removed} stale page(s)")

    # scripts/prettier_util.py: one call site, one pinned version, and it
    # STOPS the build if npx is missing rather than writing unformatted pages
    # and warning. Generating and formatting are one step so that re-running
    # is idempotent.
    print(f"formatted {prettier_util.format_files(written)} pages")

    # Wave 2 Phase 7. After Prettier, never before - see shell.bake_files().
    print(f"baked the header and footer into "
          f"{shell.bake_files(written)} page(s)")

    hub = update_hub_count(index)
    if hub is None:
        print("WARNING: ppq-count markers not found in past-papers/index.html")
    elif hub:
        print(f"updated the count in past-papers/index.html to {index['count']}")

    # The sitemap is built separately - see the note on update_sitemap().
    print(f"{len(paths)} page URLs; run scripts/build_sitemap.py to refresh the sitemap")


if __name__ == "__main__":
    main()

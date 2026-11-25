#!/usr/bin/env python3
"""Extract AQA A-level (7136) and AS (7135) Economics questions into JSON, one
file per paper.

    .venv/bin/python scripts/extract_aqa_questions.py [question-paper.pdf ...]

Writes past-paper-questions-data/aqa/<paper>-<series>.json for A-level and
past-paper-questions-data/aqa-as/<paper>-<series>.json for AS. With no
arguments it reads every A-level June paper and every non-specimen AS paper.

Why this is not the Swift extractor
-----------------------------------
Edexcel's papers read correctly through PDFKit. AQA's do not: each question
number sits in a boxed cell in the left margin, and PDFKit returns those boxes
detached from the questions they label - sometimes clumped together ("0 5 0 6"),
sometimes flushed after the text they belong to. Six rounds of reading-order
heuristics never got the boundaries right on more than one paper in sixteen.

Nothing in these PDFs is unreadable: the mark tariffs and the question numbers
both come out complete and correctly ordered, and the wording is intact. It was
only ever a segmentation problem. pdfplumber solves it by geometry rather than
guesswork - AQA prints the number cells at a fixed x, and each cell's vertical
position is exactly where its question starts, so cropping the body column
between one number and the next returns clean, correctly bounded text.

Structure, confirmed against all 24 papers
------------------------------------------
Papers 1 and 2   Section A  Context 1: Q1 (2), Q2 (4), Q3 (9), Q4 (25)
                            Context 2: Q5 (2), Q6 (4), Q7 (9), Q8 (25)
                 Section B  three essays, each 15 + 25:
                            Q9/Q10, Q11/Q12, Q13/Q14
Paper 3          Section A  Q1-Q30 multiple choice, 1 mark each (Phase 7)
                 Section B  Q31 (10), Q32 (15), Q33 (25)

The tariff sequence is fixed, so it doubles as the acceptance test: a paper whose
extracted tariffs do not match exactly is reported and written with low
confidence rather than passed off as correct.

AS (7135), confirmed against all 18 non-specimen papers (D71, 2026-11-25)
-------------------------------------------------------------------------
Papers 1 and 2   Section A  Q1-Q20 multiple choice, 1 mark each
                 Section B  two data-response contexts, choose one:
                            Q21-Q26 or Q27-Q32, each 3, 4, 4, 4, 10, 25

Only Section A is extracted; Section B and the specimens are out of scope
(D71). The whole-paper tariff check does not apply: the hosted AS PDFs bundle
the Insert inconsistently - before the paper, after it, both, or not at all -
and the Insert reprints the Section B questions with their tariffs. An AS
paper is accepted on its own Section A instead: number cells 1-20 in order,
each question closed by "[1 mark]", and the mark scheme's key-list page.
Every qpPage is the PDF's page index, so a link lands on the right page
whatever is bundled in front of the paper.

Paper 3 Section A is read by extract_mcqs(), at the level of characters rather
than words, because its stems print subscripts (SRAS1, E2) as 7pt glyphs set
below the line, which a word crop scatters onto lines of their own. The record
shape - type "mcq", options A-D as printed, usesFigure, and no answer key - was
approved by Eliot on 2026-11-25 (review/phase-7-mcqs.md).

This script NEVER invents, paraphrases or reconstructs question text.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

try:
    import pdfplumber
except ImportError:
    sys.exit(
        "pdfplumber is not installed.\n"
        "  python3 -m venv .venv\n"
        "  .venv/bin/pip install -r requirements.txt\n"
        "  .venv/bin/python scripts/extract_aqa_questions.py"
    )

ROOT = Path(__file__).resolve().parent.parent
PAPERS = ROOT / "past-papers" / "aqa" / "a-level"
OUT_DIR = ROOT / "past-paper-questions-data" / "aqa"
AS_PAPERS = ROOT / "past-papers" / "aqa" / "as-level"
AS_OUT_DIR = ROOT / "past-paper-questions-data" / "aqa-as"

PAPER_NAMES = {
    1: "Markets and Market Failure",
    2: "The National and International Economy",
    3: "Economic Principles and Issues",
}
# As printed on the 2025 covers. The 2016 covers set the same titles in
# sentence case; title case matches PAPER_NAMES above.
AS_PAPER_NAMES = {
    1: "The Operation of Markets and Market Failure",
    2: "The National Economy in a Global Context",
}
QUALIFICATION = {
    "a-level": "A-level Economics (7136)",
    "as-level": "AS Economics (7135)",
}

# The tariff for every question, in order. Also the acceptance test.
EXPECTED = {
    1: [2, 4, 9, 25, 2, 4, 9, 25, 15, 25, 15, 25, 15, 25],
    2: [2, 4, 9, 25, 2, 4, 9, 25, 15, 25, 15, 25, 15, 25],
    3: [10, 15, 25],
}
FIRST_Q = {1: 1, 2: 1, 3: 31}

# The number cells sit in a gutter whose x position is fixed within a paper but
# NOT across papers: 2019 onwards uses x=52.7/72.5, the 2018 papers x=68.3/85.2.
# So the gutter is measured per document rather than hard-coded, and the body
# column is taken to start a little to the right of whatever it turns out to be.
GUTTER_SEARCH_X = 110.0
GUTTER_ROW_TOLERANCE = 2.5  # pt; paired digits are not always on the same baseline
BODY_GAP = 8.0

# "Do not write outside the box" is set in the right margin. Its glyphs are
# upright, so orientation cannot separate them, and they interleave into the
# body word by word - "a manufacturer outsbidoex should consider". A fixed right
# edge does not work either: a data value in one Paper 3 table reaches x=571.9,
# further right than the strip starts. The strip is identified by its signature
# instead - one of these words, set in 7pt where the body is 11pt, at the far
# right - which no body text matches.
# Identified by position and type size rather than by the words themselves:
# on some pages pdfplumber merges the strip into single tokens like
# "outsbidoex", which no word list would match. Measured over all 24 papers,
# this removes the 279 instances of each of the six words and nothing else
# except a few chart axis year labels, none of which is question wording.
MARGIN_MAX_HEIGHT = 8.5
MARGIN_MIN_X = 520.0
# The strip is also excluded geometrically. Cropping to the page edge lets
# pdfplumber re-tokenise its fragments into single words like "outsbidoex",
# which then carry the leftmost fragment's x and slip past the filter above.
# Question wording never reaches this far right; only figures and tables do,
# and those are not inside a question's crop.
BODY_RIGHT_EDGE = 545.0
# Words within this many points of each other vertically are one visual line.
LINE_TOLERANCE = 3.0

SOURCE_RE = re.compile(r"^\s*Sources?:", re.M)
TARIFF_RE = re.compile(r"\[(\d{1,2})\s+marks?\]")
# The closing bracket of a tariff can sit beyond the body crop's right edge, so
# the copy used to cut a question short tolerates its absence.
TARIFF_CUT_RE = re.compile(r"\[\s*\d{1,2}\s+marks?\s*\]?")
FURNITURE_RE = re.compile(
    r"(?m)^\s*(?:Turn over.*|IB/M/\S+.*|Do not write outside the box|"
    r"END OF QUESTIONS|Section [AB]|\d{1,3})\s*$"
)


def parse_meta(path: Path):
    m = re.search(r"paper-(\d)-([a-z]+)-(\d{4})-question-paper\.pdf$", path.name)
    if not m:
        return None
    paper, series, year = int(m.group(1)), m.group(2), int(m.group(3))
    level = "as-level" if path.name.startswith("aqa-as-level-") else "a-level"
    names = AS_PAPER_NAMES if level == "as-level" else PAPER_NAMES
    if paper not in names:
        return None
    return {
        "level": level,
        "qualification": QUALIFICATION[level],
        "outDir": AS_OUT_DIR if level == "as-level" else OUT_DIR,
        "paper": paper,
        "paperName": names[paper],
        "year": year,
        "series": series.capitalize(),
        "seriesSlug": f"{series}-{year}",
        "qpPath": path,
        "msPath": Path(str(path).replace("-question-paper.pdf", "-mark-scheme.pdf")),
        "idStem": f"aqa{'-as' if level == 'as-level' else ''}-p{paper}-{year}-{series[:3]}",
    }


def number_cells(page):
    """Question-number cells on one page: (top, number, right_edge).

    AQA prints the number as two digit glyphs side by side in a gutter box. A
    row is a cell only when exactly two of them sit at the same height, which
    rejects the stray single digits that line numbers and figures leave in the
    same column. The two are not always on the identical baseline - some are
    0.6pt apart - so rows are clustered with a small tolerance rather than
    keyed on an exact value.
    """
    digits = [
        w
        for w in page.extract_words()
        if w["x0"] <= GUTTER_SEARCH_X and w["text"].isdigit() and len(w["text"]) == 1
    ]
    digits.sort(key=lambda w: (w["top"], w["x0"]))

    rows = []
    for w in digits:
        if rows and abs(rows[-1][0]["top"] - w["top"]) <= GUTTER_ROW_TOLERANCE:
            rows[-1].append(w)
        else:
            rows.append([w])

    cells = []
    for ws in rows:
        if len(ws) != 2:
            continue
        ws.sort(key=lambda w: w["x0"])
        # The pair is one boxed cell, so the digits sit close together.
        if not 8 <= ws[1]["x0"] - ws[0]["x0"] <= 30:
            continue
        cells.append((ws[0]["top"], int(ws[0]["text"] + ws[1]["text"]), ws[1]["x1"]))
    return sorted(cells)


def body_left_edge(pdf):
    """Where the body column starts, derived from the gutter this paper uses."""
    edges = [c[2] for p in pdf.pages for c in number_cells(p)]
    if not edges:
        return GUTTER_SEARCH_X
    return max(edges) + BODY_GAP


def is_margin_word(w) -> bool:
    return (
        w["x0"] > MARGIN_MIN_X and (w["bottom"] - w["top"]) < MARGIN_MAX_HEIGHT
    )


def crop_text(crop) -> str:
    """Text of a crop with the right-margin warning dropped.

    Rebuilt from words rather than taken from extract_text, so the margin strip
    can be removed before the line is assembled. Lines are preserved because the
    Source-attribution trim downstream needs them.
    """
    words = [w for w in crop.extract_words() if not is_margin_word(w)]
    if not words:
        return ""

    # Group into visual lines BEFORE sorting left to right. Sorting on top first
    # scrambles a line whose runs sit fractionally apart: a bold "Extract C" set
    # 0.4pt above its neighbours sorts ahead of them and lands mid-sentence
    # ("the cost of student Extract C accommodation").
    words.sort(key=lambda w: w["top"])
    lines = []
    for w in words:
        if lines and abs(lines[-1][0]["top"] - w["top"]) <= LINE_TOLERANCE:
            lines[-1].append(w)
        else:
            lines.append([w])

    return "\n".join(
        " ".join(w["text"] for w in sorted(line, key=lambda w: w["x0"]))
        for line in lines
    )


# A hyphenated word broken across a line break: joining the lines leaves the
# hyphen with a space after it ("self- correcting"). Both sides must be
# lower-case letters, which rules out a dash between clauses and a hyphen before
# a capitalised proper noun.
HYPHEN_BREAK_RE = re.compile(r"(?<=[a-z])-\s+(?=[a-z])")
# ...except the suspended-hyphen construction, where the space is correct and
# the word really has been left hanging: "short- and long-run", "pre- or
# post-tax". Joining those would corrupt real wording, so they are excepted by
# the conjunction that follows.
SUSPENDED_HYPHEN_RE = re.compile(r"(?<=[a-z])-\s+(?=(?:and|or|to)\b)")


def rejoin_hyphenation(text: str) -> str:
    """Repair a word the PDF broke across a line, leaving the suspended
    hyphen alone.

    One occurrence in the 248 AQA questions extracted so far - "self-
    correcting" in aqa-p2-2018-jun-q3. Fixed here rather than in the JSON
    because the data has to stay a pure function of the extractor.
    """
    keep = {m.start() for m in SUSPENDED_HYPHEN_RE.finditer(text)}
    out = []
    cursor = 0
    for m in HYPHEN_BREAK_RE.finditer(text):
        if m.start() in keep:
            continue
        out.append(text[cursor : m.start()])
        out.append("-")
        cursor = m.end()
    out.append(text[cursor:])
    return "".join(out)


def clean(text: str) -> str:
    text = FURNITURE_RE.sub(" ", text or "")
    # Anything before the last source attribution is stimulus, not question
    # wording; an extract's last line always carries one.
    hits = list(SOURCE_RE.finditer(text))
    if hits:
        nl = text.find("\n", hits[-1].end())
        text = text[nl + 1 :] if nl != -1 else ""
    # A question ends at its tariff. Cropping to the next number cell is not
    # enough on its own: pdfplumber keeps a word that merely straddles the crop
    # boundary, so the next question's first line leaks in. The tariff is the
    # paper's own end-of-question marker and cuts exactly.
    tariff = TARIFF_CUT_RE.search(text)
    if tariff:
        text = text[: tariff.start()]
    text = re.sub(r"\s+", " ", text).strip()
    return rejoin_hyphenation(text)


def extract_questions(pdf, first_q: int, expected: list[int]):
    """Walk the whole paper, cropping the body column between number cells."""
    found = {}
    order = []
    pending = None  # (number, page_index, top)
    body_x = body_left_edge(pdf)

    for pi, page in enumerate(pdf.pages):
        cells = number_cells(page)
        for top, num, _right in cells:
            if pending is not None:
                # Close the previous question: it ran to this cell if they share
                # a page, otherwise to the bottom of its own page.
                p_num, p_pi, p_top = pending
                bottom = top if p_pi == pi else pdf.pages[p_pi].height
                prev = pdf.pages[p_pi]
                crop = prev.crop(
                    (body_x, max(0, p_top - 3), min(prev.width, BODY_RIGHT_EDGE), bottom)
                )
                body = clean(crop_text(crop))
                if p_num not in found or len(body) > len(found[p_num]["text"]):
                    found[p_num] = {"text": body, "page": p_pi + 1}
                    if p_num not in order:
                        order.append(p_num)
            pending = (num, pi, top)

        # A question whose cell is the last on its page continues below it.
        if pending is not None and pending[1] == pi:
            p_num, p_pi, p_top = pending
            crop = page.crop(
                (
                    body_x,
                    max(0, p_top - 3),
                    min(page.width, BODY_RIGHT_EDGE),
                    page.height,
                )
            )
            body = clean(crop_text(crop))
            if p_num not in found or len(body) > len(found[p_num]["text"]):
                found[p_num] = {"text": body, "page": p_pi + 1}
                if p_num not in order:
                    order.append(p_num)
            pending = None

    wanted = list(range(first_q, first_q + len(expected)))
    return [(n, found.get(n)) for n in wanted]


def context_pages(pdf, paper: int):
    """Where the stimulus each question depends on begins.

    Papers 1 and 2: Context 1 carries Q1-Q4 and Context 2 carries Q5-Q8, both
    with extracts. Section B is three free-standing essays with no stimulus, so
    Q9-Q14 get nothing. Paper 3: Section A is multiple choice, whose data is
    printed with each question (extract_mcqs gives it no context), and
    Section B is a case study, so Q31-Q33 all point at where it starts.

    The cover lists "Context 1" and "Section B" in its bulleted instructions, so
    headings are matched at the start of a line, which those bullets are not.
    Only the cover itself is skipped: Context 1 opens on page 2.
    """
    out = {}
    if paper == 3:
        for i, page in enumerate(pdf.pages):
            if i < 1:
                continue
            text = page.extract_text() or ""
            if re.search(r"(?m)^\s*Section B\b", text):
                out.update({n: i + 1 for n in (31, 32, 33)})
                break
        return out

    found = {}
    for i, page in enumerate(pdf.pages):
        if i < 1:
            continue
        text = page.extract_text() or ""
        for n in (1, 2):
            if n not in found and re.search(rf"(?m)^\s*Context {n}\b", text):
                found[n] = i + 1
    for n in range(1, 5):
        if 1 in found:
            out[n] = found[1]
    for n in range(5, 9):
        if 2 in found:
            out[n] = found[2]
    return out


# ---------------------------------------------------------------- Paper 3 MCQs

# Section A's length: Paper 3 sets thirty, each AS paper twenty.
MCQ_COUNT = 30
AS_MCQ_COUNT = 20
OPTION_LETTERS = "ABCD"
# Body text is 11pt. A glyph this small inside the body column is either a
# subscript or superscript (SRAS1, E2) or a label inside a figure.
SCRIPT_MAX_SIZE = 9.5
# A sub/superscript is set flush against the glyph it belongs to: its left edge
# meets that glyph's right edge, and it sits within half a line of its baseline.
SCRIPT_X_GAP = 1.0
SCRIPT_Y_RANGE = 8.0
# Wrapped option text is indented past the option letter by about 14pt; a
# line that opens with "£" starts up to 18.3pt in, because of the glyph's
# side bearing (AS P1 June 2017 Q16: "B Exactly 50% ... higher than /
# £32 100").
CONTINUATION_INDENT = (10.0, 19.0)
# A wrapped line sits one line below the line it continues: about 13pt.
WRAP_LINE_GAP = 16.0
ALIGN_TOLERANCE = 2.0
STEM_TOLERANCE = 5.0
CELL_GAP = 15.0
WORD_GAP = 0.2
# How far inside an inked glyph a space must start to be discarded: well past
# the rounding (~0.05pt) by which a real word space can overlap the glyph
# before it.
SPACE_OVERLAP = 1.0
MCQ_TARIFF_RE = re.compile(r"^\[1 mark\]$")
# The AS papers of 2016-2019 close Section A over two lines, where Paper 3 and
# later AS papers print "END OF SECTION A". The break falls in either place:
# "QUESTION 20 IS THE LAST" / "QUESTION IN SECTION A" (2016; P2 2017 ends
# "A."), or "QUESTION 20 IS THE" / "LAST QUESTION IN SECTION A" (P1 2017-2019,
# P2 2018-2019). Unmatched, the two lines read as figure text and set a false
# usesFigure on Q20 (Phase 9 dry run, AS Paper 1 June 2016; P1 June 2018).
MCQ_FURNITURE_RE = re.compile(
    r"^(?:Turn over for (?:the next question|Section B)|Turn over ►?|Do not write outside the box|"
    r"END OF SECTION A|QUESTION \d+ IS THE(?: LAST)?|(?:LAST )?QUESTION IN SECTION A\.?|"
    r"Section [AB]|\d{1,3}|\*.*|IB/[A-Z]/\S+)$"
)


def _is_bold(ch) -> bool:
    return "Bold" in ch.get("fontname", "")


def _lines_from_chars(chars):
    """Visual lines from characters, sub/superscripts moved onto their base line.

    Each small glyph is attached to the full-size glyph whose right edge it
    touches and whose baseline it sits within half a line of: "SRAS" + "1".
    The digit is kept as printed, set flush against its base, the way PDFKit
    returns Edexcel's "P1" - no Unicode subscript is invented. A script of
    several glyphs ("OW" + "min", 2017 Q19) chains: each further glyph touches
    the one before it on the same small baseline. A small glyph with no such
    neighbour is figure text and keeps its own line.
    """
    full = [c for c in chars if c["size"] > SCRIPT_MAX_SIZE and c["text"].strip()]
    line_of = {}
    attached = []
    # Spaces are included: the space after a subscript is set at the
    # subscript's size and height ("(D1 and D2)", 2017 Q10), and would
    # otherwise be lost. A space only ever chains; it never starts a script.
    small = sorted(
        (c for c in chars if c["size"] <= SCRIPT_MAX_SIZE),
        key=lambda c: c["x0"],
    )
    for c in small:
        base = [
            b
            for b in full
            if c["text"].strip()
            and abs(b["x1"] - c["x0"]) <= SCRIPT_X_GAP
            and abs(b["top"] - c["top"]) <= SCRIPT_Y_RANGE
        ]
        if base:
            line_of[id(c)] = min(base, key=lambda b: abs(b["x1"] - c["x0"]))["top"]
            attached.append(c)
            continue
        prev = [
            a
            for a in attached
            if abs(a["x1"] - c["x0"]) <= SCRIPT_X_GAP and abs(a["top"] - c["top"]) <= 2.0
        ]
        if prev:
            line_of[id(c)] = line_of[id(prev[-1])]
            attached.append(c)

    keyed = sorted(chars, key=lambda c: line_of.get(id(c), c["top"]))
    lines = []
    for c in keyed:
        top = line_of.get(id(c), c["top"])
        if lines and abs(lines[-1]["top"] - top) <= LINE_TOLERANCE:
            lines[-1]["chars"].append(c)
        else:
            lines.append({"top": top, "chars": [c]})

    out = []
    for ln in lines:
        cs = sorted(ln["chars"], key=lambda c: c["x0"])
        # A space glyph that starts inside an inked glyph is not a word break.
        # The AS papers from 2022 set a run of spaces from the number cell
        # whose last one starts 0.4pt right of the F of "Figure" - sorted by
        # x it lands between F and i, and the text read "F igure 1" (Phase 9
        # dry run, AS Paper 2 June 2025 Q4). A real word space starts where
        # the glyph before it ends.
        inked_spans = [(c["x0"], c["x1"]) for c in cs if c["text"].strip()]
        cs = [
            c
            for c in cs
            if c["text"].strip()
            or not any(a < c["x0"] < b - SPACE_OVERLAP for a, b in inked_spans)
        ]
        # A word break the PDF prints as a gap with no space glyph (2018 Q2,
        # "financial year the") gets its space, as pdfplumber's own text
        # extraction gives it: a gap wider than a fifth of the type size.
        parts = []
        for k, c in enumerate(cs):
            if k and c["text"].strip() and cs[k - 1]["text"].strip():
                gap = c["x0"] - cs[k - 1]["x1"]
                if gap > WORD_GAP * max(c["size"], cs[k - 1]["size"]):
                    parts.append(" ")
            parts.append(c["text"])
        text = re.sub(r"\s+", " ", "".join(parts)).strip()
        if not text:
            continue
        first = next(c for c in cs if c["text"].strip())
        inked = [c for c in cs if c["text"].strip()]
        widest = max(
            (b["x0"] - a["x1"] for a, b in zip(inked, inked[1:])), default=0.0
        )
        out.append(
            {
                "top": ln["top"],
                "x0": first["x0"],
                "bold": _is_bold(first),
                "text": text,
                "scripts": sum(1 for c in cs if id(c) in line_of and c["text"].strip()),
                "small": all(c["size"] <= SCRIPT_MAX_SIZE for c in cs if c["text"].strip()),
                # The widest space between two inked glyphs. Prose is set
                # ragged right with ordinary word spaces; a gap this wide is
                # the space between two cells of a table row.
                "cells": widest > CELL_GAP,
            }
        )
    return out


def _option_rows(lines):
    """The four option lines - bold, lettered A-D in order, at one x - or []."""
    cands = [ln for ln in lines if ln["bold"] and re.match(r"^[A-D](?: |$)", ln["text"])]
    for a in (c for c in cands if c["text"][0] == "A"):
        rows = [a]
        for letter in OPTION_LETTERS[1:]:
            nxt = next(
                (
                    c
                    for c in cands
                    if c["text"][0] == letter
                    and c["top"] > rows[-1]["top"]
                    and abs(c["x0"] - a["x0"]) <= ALIGN_TOLERANCE
                ),
                None,
            )
            if nxt is None:
                break
            rows.append(nxt)
        if len(rows) == 4:
            return rows
    return []


def _rejoin_option_letters(lines):
    out = [dict(ln) for ln in lines]
    used = set()
    for i, ln in enumerate(out):
        if not (ln["bold"] and re.fullmatch(r"[A-D]", ln["text"])):
            continue
        beside = [
            j
            for j, o in enumerate(out)
            if j != i
            and j not in used
            and CONTINUATION_INDENT[0] <= o["x0"] - ln["x0"] <= CONTINUATION_INDENT[1]
            and abs(o["top"] - ln["top"]) <= 4.5
        ]
        if len(beside) == 1:
            j = beside[0]
            used.add(j)
            ln["text"] = ln["text"] + " " + out[j]["text"]
            ln["scripts"] += out[j]["scripts"]
    return [ln for j, ln in enumerate(out) if j not in used]


def _region_lines(page, top, bottom, body_x):
    chars = [
        c
        for c in page.chars
        if c["top"] >= top
        and c["bottom"] <= bottom + 1
        and c["x0"] >= body_x
        and c["x0"] < BODY_RIGHT_EDGE
        and not (c["x0"] > MARGIN_MIN_X and c["size"] < MARGIN_MAX_HEIGHT)
    ]
    return _lines_from_chars(chars)


def _images_in(page, top, bottom):
    return [
        im
        for im in page.images
        if im["bottom"] > top and im["top"] < bottom and (im["x1"] - im["x0"]) > 40
    ]


def extract_mcqs(pdf, count=MCQ_COUNT):
    """Section A, Q1-Q<count>: stem and options A-D, as printed. Thirty on
    Paper 3, twenty on each AS paper.

    Each question is the body column between its number cell and the next (or
    the foot of the page). Its lines are read by position:

      - the options are four bold lines lettered A-D, in order, at one x;
      - a line indented ~14pt past them continues the option above it;
      - a line at the text column above option A is the stem;
      - a line anywhere else is figure or table text - a data table's rows, a
        diagram's labels - and is dropped and counted, never reproduced;
      - "[1 mark]" must be present, but where it falls says nothing: it
        follows option D up to 2021 and sits above option A from 2022.

    usesFigure is true when anything was dropped, when an image is printed in
    the question, or when the options are bare letters under diagrams or the
    rows of a table (then options is null). Nothing is rewritten: lines are
    kept whole or not at all, and the only repair is rejoin_hyphenation's, as
    for every AQA question.
    """
    body_x = body_left_edge(pdf)
    cells = [
        (pi, top, n)
        for pi, p in enumerate(pdf.pages)
        for top, n, _r in number_cells(p)
        if 1 <= n <= count
    ]
    problems = []
    seen = [n for _pi, _t, n in cells]
    if seen != list(range(1, count + 1)):
        problems.append(f"Section A number cells read {seen}, expected 1-{count}")
    all_cells = sorted(
        (pi, top) for pi, p in enumerate(pdf.pages) for top, _n, _r in number_cells(p)
    )

    out = []
    for pi, top, n in cells:
        page = pdf.pages[pi]
        later = [t for p2, t in all_cells if p2 == pi and t > top + 1]
        bottom = min(later) if later else page.height
        lines = _region_lines(page, top - 3, bottom - 1, body_x)
        images = _images_in(page, top - 3, bottom)
        notes = []

        first = next((ln for ln in lines if abs(ln["top"] - top) <= 4), None)
        if first is None:
            problems.append(f"Q{n}: no stem line beside the number cell")
            continue

        # An option letter can sit a few points off its own text's baseline
        # (2022 Q28: "B" at 691.8, its text at 688.7), so the two land on
        # separate lines - and the text, read first, would join the option
        # above. A bare bold letter takes the one line set beside it.
        lines = _rejoin_option_letters(lines)

        # The option rows: four bold lines lettered A-D, in order, at one x.
        rows = _option_rows(lines)
        # The stem's column. Its first line can start a few points left of
        # the rest (2020 Q22: 88.0, then 91.5), and the option letters a few
        # points right of it (2019 Q18: 95.8 against 92.6). Options within
        # STEM_TOLERANCE of the first line are the question's own; a stem
        # line must then sit within ALIGN_TOLERANCE of the first line or of
        # the option letters - a table's row labels can start 4pt in (2024
        # Q5: "Original", "Disposable" at 96.8 against 92.6).
        col = first["x0"]
        # Rows that are a table's (cells set apart on the line, 2020 Q3 "A
        # -2%   0%   +2%") are table options wherever their letters sit.
        text_options = (
            bool(rows)
            and abs(rows[0]["x0"] - col) <= STEM_TOLERANCE
            and not any(r["cells"] for r in rows)
        )
        stem_xs = [col]
        if text_options:
            col = rows[0]["x0"]
            stem_xs.append(col)
        row_ids = {id(r) for r in rows} if text_options else set()
        start_top = rows[0]["top"] if rows else None

        stem, options, order, dropped, trailing, closed = [], {}, [], [], [], False
        current, last_top = None, None
        for ln in lines:
            t = ln["text"]
            if MCQ_FURNITURE_RE.match(t):
                continue
            # The tariff follows the options up to 2021 and the stem from 2022
            # (it sits above option A), so it marks nothing; the question runs
            # to the next number cell or the foot of the page.
            if MCQ_TARIFF_RE.match(t):
                closed = True
                continue
            near = (
                min(abs(ln["x0"] - x) for x in stem_xs) <= ALIGN_TOLERANCE
                and not ln["small"]
                and not ln["cells"]
            )
            if id(ln) in row_ids:
                current = t[0]
                order.append(current)
                options[current] = [t[2:]] if len(t) > 2 else []
                last_top = ln["top"]
            elif (
                current
                and CONTINUATION_INDENT[0] <= ln["x0"] - col <= CONTINUATION_INDENT[1]
                and not ln["small"]
                and not ln["cells"]
            ):
                options[current].append(t)
                last_top = ln["top"]
            elif ln is first or (near and (start_top is None or ln["top"] < start_top)):
                stem.append(t)
            elif (
                current
                and near
                and not ln["bold"]
                and ln["top"] - last_top <= WRAP_LINE_GAP
                and any(r["top"] > ln["top"] for r in rows)
            ):
                # An option wrapped back to the letter column rather than to
                # the indent (AS P2 June 2016 Q4: "B More government spending
                # on training and a higher / exchange rate"). Only between two
                # option rows and directly under the line above; after D it is
                # still reported below.
                options[current].append(t)
                last_top = ln["top"]
            elif current and near:
                # Prose at the text column after the options: nothing should
                # be printed there, so it is reported rather than guessed at.
                trailing.append(t)
            else:
                dropped.append(t)

        if not closed:
            problems.append(f"Q{n}: no [1 mark] tariff before the next question")
        if trailing:
            problems.append(f"Q{n}: text at the column after option D: {trailing}")
        # Options printed as the rows of a table (2017 Q20: "A Increase
        # Increase Increases" under three column headings) start at the
        # table's own left edge, well right of the stem, or set their cells
        # apart on the line, so the pass above read them as table text. The letter may share a line with the first cell
        # or stand alone in its own cell (2017 Q22, 2020 Q11, 2021 Q18). The
        # cells mean nothing without their headings, so the options are not
        # reproduced: options is null, as for diagrams.
        table_options = bool(rows) and not text_options
        # Four diagrams printed as one image, letters and all, so the text
        # layer holds no option letter (2022 Q15). Accepted only when the
        # image sits below the stem.
        image_options = False
        if not rows and images and stem:
            stem_bottom = max(ln["top"] for ln in lines if ln["text"] in stem)
            image_options = any(im["top"] > stem_bottom for im in images)
        if table_options or image_options:
            order = list(OPTION_LETTERS)
            options = {L: [] for L in OPTION_LETTERS}
        if order != list(OPTION_LETTERS):
            problems.append(f"Q{n}: options read {''.join(order)}, expected ABCD")
            continue

        bare = [L for L in OPTION_LETTERS if not options[L]]
        if bare and len(bare) != 4:
            problems.append(f"Q{n}: options {''.join(bare)} have no text but the others do")
            continue
        figure_options = len(bare) == 4

        text = rejoin_hyphenation(re.sub(r"\s+", " ", " ".join(stem)).strip())
        opts = (
            None
            if figure_options
            else [
                {
                    "letter": L,
                    "text": rejoin_hyphenation(" ".join(options[L]).strip()),
                }
                for L in OPTION_LETTERS
            ]
        )
        uses_figure = bool(dropped or images or figure_options)
        if dropped:
            notes.append(
                f"{len(dropped)} line(s) of figure or table text printed with the "
                "question are not reproduced; see the question paper"
            )
        if images:
            notes.append("the question prints a diagram or chart (an image)")
        if table_options:
            notes.append("the options are the rows of a table; not reproduced")
        elif image_options:
            notes.append("the options are diagrams printed as one image; the text layer has no option letters")
        elif figure_options and images:
            notes.append("the options are diagrams; only the letters are text")
        elif figure_options:
            # Bare letters and no image: the options are the rows of a table
            # whose letter column sits at the text column (2017 Q6), or
            # printed fractions (2022 Q25).
            notes.append("the options are a table or formulae beside bare letters; only the letters are text")
        scripts = sum(ln["scripts"] for ln in lines)
        if scripts:
            notes.append(f"{scripts} subscript or superscript glyph(s) set flush against their base")
        out.append(
            {
                "num": n,
                "text": text,
                "options": opts,
                "usesFigure": uses_figure,
                "page": pi + 1,
                "notes": notes,
            }
        )
    return out, problems


def mcq_key_page(ms_path: Path, count=MCQ_COUNT):
    """The mark-scheme page holding the Section A key list.

    Verified by content, not position: the page must say SECTION A and KEY
    LIST and print every question number 1-<count>. From 2021 the list reprints each
    answer's wording beside its letter, so a number and its letter are no
    longer neighbours in the text; only the numbers are required. The key
    itself is never read into the data - only the page number is kept, as for
    every card.
    """
    if not ms_path.is_file():
        return None
    with pdfplumber.open(ms_path) as ms:
        for i, p in enumerate(ms.pages):
            text = p.extract_text() or ""
            if "KEY LIST" not in text.upper() or "SECTION A" not in text.upper():
                continue
            numbers = {int(a) for a in re.findall(r"(?<![\d£.,%])\b(\d{1,2})\b(?![\d.,%])", text)}
            if set(range(1, count + 1)) <= numbers:
                return i + 1
    return None


def tariffs_in_order(pdf):
    text = "\n".join((p.extract_text() or "") for p in pdf.pages)
    return [int(m.group(1)) for m in TARIFF_RE.finditer(text)]


def mark_scheme_pages(ms_path: Path, numbers: list[int]):
    """First page whose heading names each question. Verified, not assumed.

    AQA's schemes head each answer with the same two-digit cell the question
    paper uses - "0 2", "1 1" - so the question number is matched in that exact
    form rather than as a bare integer, which would hit any stray figure.
    """
    out = {}
    if not ms_path.is_file():
        return out
    with pdfplumber.open(ms_path) as ms:
        pages = [(i + 1, (p.extract_text() or "")) for i, p in enumerate(ms.pages)]
    for n in numbers:
        spaced = f"{n:02d}"
        pat = re.compile(rf"(?<![0-9]){spaced[0]}\s+{spaced[1]}(?![0-9])")
        for pno, text in pages:
            if pno <= 2:
                continue
            if pat.search(text):
                out[n] = pno
                break
    return out


def mcq_records(meta, mcqs, key_page):
    """The Section A records, in the shape approved in review/phase-7-mcqs.md:
    no answer field, the key-list page as the mark-scheme link."""
    questions = []
    for m in mcqs:
        notes = list(m["notes"])
        confidence = "high"
        if key_page is None:
            confidence = "low"
            notes.append("mark scheme key list page could not be verified")
        if len(m["text"]) < 15:
            confidence = "low"
            notes.append(f"stem is only {len(m['text'])} characters")
        questions.append(
            {
                "id": f"{meta['idStem']}-q{m['num']}",
                "section": "A",
                "questionNumber": str(m["num"]),
                "parentQuestion": None,
                "choiceGroup": None,
                "marks": 1,
                "type": "mcq",
                "questionText": m["text"],
                "options": m["options"],
                "usesFigure": m["usesFigure"],
                # Section A has no extracts: the stem's own data is on the
                # question's page, which the question-paper link already opens.
                "contextPage": None,
                "qpPage": m["page"],
                "msPage": key_page,
                "confidence": confidence,
                "notes": notes,
            }
        )
    return questions


def extract_as_paper(meta):
    """An AS paper: Section A only (D71). See the module docstring for why
    the whole-paper tariff check does not apply."""
    with pdfplumber.open(meta["qpPath"]) as pdf:
        mcqs, problems = extract_mcqs(pdf, AS_MCQ_COUNT)
        page_count = len(pdf.pages)
    if len(mcqs) != AS_MCQ_COUNT:
        problems.append(f"read {len(mcqs)} Section A questions, expected {AS_MCQ_COUNT}")
    key_page = mcq_key_page(meta["msPath"], AS_MCQ_COUNT)
    return mcq_records(meta, mcqs, key_page), problems, page_count


def extract_paper(meta):
    if meta["level"] == "as-level":
        return extract_as_paper(meta)

    problems = []
    expected = EXPECTED[meta["paper"]]
    first = FIRST_Q[meta["paper"]]

    with pdfplumber.open(meta["qpPath"]) as pdf:
        pairs = extract_questions(pdf, first, expected)
        contexts = context_pages(pdf, meta["paper"])
        found_tariffs = tariffs_in_order(pdf)
        mcqs = []
        # Paper 3's 30 one-mark MCQs come first: Section A, read separately.
        if meta["paper"] == 3:
            ones = found_tariffs[:MCQ_COUNT]
            if ones != [1] * MCQ_COUNT:
                problems.append(f"Section A tariffs {ones} are not thirty 1-mark questions")
            found_tariffs = found_tariffs[MCQ_COUNT:]
            mcqs, mcq_problems = extract_mcqs(pdf)
            problems.extend(mcq_problems)
        page_count = len(pdf.pages)

    if found_tariffs != expected:
        problems.append(
            f"tariff sequence {found_tariffs} does not match expected {expected}"
        )

    ms_pages = mark_scheme_pages(meta["msPath"], [n for n, _ in pairs])

    key_page = mcq_key_page(meta["msPath"]) if mcqs else None
    questions = mcq_records(meta, mcqs, key_page)
    for i, (num, hit) in enumerate(pairs):
        marks = expected[i]
        notes = []
        confidence = "high"
        text = hit["text"] if hit else ""
        qp_page = hit["page"] if hit else 0

        if not hit:
            problems.append(f"Q{num}: no number cell found")
            continue
        if len(text) < 25:
            confidence = "low"
            notes.append(f"extracted text is only {len(text)} characters")
        if len(text) > 900:
            confidence = "low"
            notes.append("extracted text is unusually long; may include stimulus")

        ms_page = ms_pages.get(num)
        if ms_page is None:
            confidence = "low"
            notes.append(f"mark scheme page for Q{num} could not be verified")

        section = "A" if (meta["paper"] != 3 and i < 8) else "B"
        ctx = contexts.get(num)
        if ctx and ctx > qp_page:
            # Stimulus cannot start after the question that depends on it. The
            # same page is fine: Paper 3's case study opens on the page that
            # also carries its first question.
            ctx = None
            notes.append("context page after the question; dropped")
        if section == "A" and meta["paper"] != 3 and ctx is None:
            confidence = "low"
            notes.append("Section A question with no extract page found")
        if meta["paper"] == 3 and ctx is None:
            confidence = "low"
            notes.append("Paper 3 case study page not found")
        questions.append(
            {
                "id": f"{meta['idStem']}-q{num}",
                "section": section,
                "questionNumber": str(num),
                "parentQuestion": None,
                "choiceGroup": None,
                "marks": marks,
                "questionText": text,
                "contextPage": ctx,
                "qpPage": qp_page,
                "msPage": ms_page,
                "confidence": confidence,
                "notes": notes,
            }
        )

    return questions, problems, page_count


def url_for(path: Path) -> str:
    """Site path for a hosted PDF, whether the caller passed an absolute or a
    repo-relative path."""
    return "/" + str(path.resolve().relative_to(ROOT))


def emit(meta, questions, problems):
    qp_url = url_for(meta["qpPath"])
    ms_url = url_for(meta["msPath"])
    doc = {
        "qualification": meta["qualification"],
        "board": "aqa",
        "boardName": "AQA",
        "level": meta["level"],
        "paper": meta["paper"],
        "paperName": meta["paperName"],
        "year": meta["year"],
        "series": meta["series"],
        "seriesSlug": meta["seriesSlug"],
        "questionPaperUrl": qp_url,
        "markSchemeUrl": ms_url,
        "problems": problems,
        "questions": [
            {
                "id": q["id"],
                "section": q["section"],
                "questionNumber": q["questionNumber"],
                "parentQuestion": q["parentQuestion"],
                "choiceGroup": q["choiceGroup"],
                "marks": q["marks"],
                # Only an MCQ carries these three, so every written record keeps
                # the shape it already has on disk, byte for byte.
                **({"type": q["type"]} if "type" in q else {}),
                "questionText": q["questionText"],
                **(
                    {"options": q["options"], "usesFigure": q["usesFigure"]}
                    if "type" in q
                    else {}
                ),
                "context": (
                    {
                        "type": "extracts",
                        "label": f"Extracts for Question {q['questionNumber']}",
                        "pdfUrl": qp_url,
                        "page": q["contextPage"],
                    }
                    if q["contextPage"]
                    else None
                ),
                "questionPaper": {"pdfUrl": qp_url, "page": q["qpPage"]},
                "markScheme": (
                    {"pdfUrl": ms_url, "page": q["msPage"], "verified": True}
                    if q["msPage"]
                    else None
                ),
                "modelAnswer": None,
                "extractionConfidence": q["confidence"],
                "extractionNotes": q["notes"],
            }
            for q in questions
        ],
    }
    dest = meta["outDir"] / f"p{meta['paper']}-{meta['seriesSlug']}.json"
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(
        json.dumps(doc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    return dest


def main(argv):
    # AS: every series but the specimens, which are out of scope (D71).
    paths = [Path(a) for a in argv] if argv else sorted(
        PAPERS.glob("paper-*/aqa-a-level-economics-paper-*-june-*-question-paper.pdf")
    ) + sorted(
        p
        for p in AS_PAPERS.glob("paper-*/aqa-as-level-economics-paper-*-question-paper.pdf")
        if "-specimen-" not in p.name
    )
    if not paths:
        sys.exit("no AQA question papers found")

    status = 0
    for path in paths:
        meta = parse_meta(path)
        if meta is None:
            print(f"SKIP {path.name}", file=sys.stderr)
            continue
        questions, problems, _ = extract_paper(meta)
        dest = emit(meta, questions, problems)
        low = sum(1 for q in questions if q["confidence"] != "high")
        line = f"{dest.name}: {len(questions)} questions"
        if low:
            line += f", {low} low-confidence"
        if problems:
            line += f", PROBLEMS: {'; '.join(problems)}"
            status = 1
        if low:
            status = 1
        print(line)
    return status


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

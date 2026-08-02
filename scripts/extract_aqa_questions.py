#!/usr/bin/env python3
"""Extract AQA A-level Economics (7136) questions into JSON, one file per paper.

    .venv/bin/python scripts/extract_aqa_questions.py

Writes past-paper-questions-data/aqa/<paper>-<series>.json.

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
Paper 3          Section A  Q1-Q30 multiple choice - EXCLUDED, by instruction
                 Section B  Q31 (10), Q32 (15), Q33 (25)

The tariff sequence is fixed, so it doubles as the acceptance test: a paper whose
extracted tariffs do not match exactly is reported and written with low
confidence rather than passed off as correct.

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

PAPER_NAMES = {
    1: "Markets and Market Failure",
    2: "The National and International Economy",
    3: "Economic Principles and Issues",
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
    if paper not in PAPER_NAMES:
        return None
    return {
        "paper": paper,
        "paperName": PAPER_NAMES[paper],
        "year": year,
        "series": series.capitalize(),
        "seriesSlug": f"{series}-{year}",
        "qpPath": path,
        "msPath": Path(str(path).replace("-question-paper.pdf", "-mark-scheme.pdf")),
        "idStem": f"aqa-p{paper}-{year}-{series[:3]}",
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
    return re.sub(r"\s+", " ", text).strip()


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
    Q9-Q14 get nothing. Paper 3: Section A is multiple choice and excluded, and
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


def extract_paper(meta):
    problems = []
    expected = EXPECTED[meta["paper"]]
    first = FIRST_Q[meta["paper"]]

    with pdfplumber.open(meta["qpPath"]) as pdf:
        pairs = extract_questions(pdf, first, expected)
        contexts = context_pages(pdf, meta["paper"])
        found_tariffs = tariffs_in_order(pdf)
        # Paper 3's 30 one-mark MCQs come first and are excluded by instruction.
        if meta["paper"] == 3:
            found_tariffs = [t for t in found_tariffs if t != 1]
        page_count = len(pdf.pages)

    if found_tariffs != expected:
        problems.append(
            f"tariff sequence {found_tariffs} does not match expected {expected}"
        )

    ms_pages = mark_scheme_pages(meta["msPath"], [n for n, _ in pairs])

    questions = []
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
        "qualification": "A-level Economics (7136)",
        "board": "aqa",
        "boardName": "AQA",
        "level": "a-level",
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
                "questionText": q["questionText"],
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
    dest = OUT_DIR / f"p{meta['paper']}-{meta['seriesSlug']}.json"
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(
        json.dumps(doc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    return dest


def main(argv):
    paths = [Path(a) for a in argv] if argv else sorted(
        PAPERS.glob("paper-*/aqa-a-level-economics-paper-*-june-*-question-paper.pdf")
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

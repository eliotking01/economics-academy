#!/usr/bin/env python3
"""Build the static practice-question pages from their JSON sources.

One JSON file per topic under questions-data/ is the single source of truth
for both the visible HTML and the schema.org JSON-LD, so the two cannot
drift. The authoring standard the JSON is written to is QUESTIONS_GUIDE.md.

The script validates every set before writing anything. A set that fails
validation stops the whole run - no page is written from a bad source.

Generated pages are committed to the repo; hosting stays plain static.

Usage:
    python3 scripts/build_questions.py                 # build everything
    python3 scripts/build_questions.py --check         # validate only
    python3 scripts/build_questions.py --sitemap       # also refresh sitemap.xml
    python3 scripts/build_questions.py aqa-a2-micro/1-3-2.json   # one topic

Exit status is non-zero if any set fails validation.

Board index pages and the hub are built by a later phase; this script
currently emits topic pages and the sitemap block.
"""

from __future__ import annotations

import argparse
import datetime
import html
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "questions-data"
OUT_DIR = ROOT / "practice-questions"
NOTES_DIR = ROOT / "revision-notes"
SITEMAP = ROOT / "sitemap.xml"

SITE = "https://economicsacademy.co.uk"
GA_ID = "G-YVCNRW4QH6"
OG_IMAGE = f"{SITE}/og-image.png?v=1"

LETTERS = ("A", "B", "C", "D")
SKILLS = {"calculation", "data-table", "applied-reasoning", "definition-in-context"}
DIFFICULTIES = {"foundation", "standard", "stretch"}
SKILL_LABELS = {
    "calculation": "Calculation",
    "data-table": "Data interpretation",
    "applied-reasoning": "Applied reasoning",
    "definition-in-context": "Definition in context",
}

PAST_PAPERS = {
    "aqa": ("/past-papers/aqa/index.html", "AQA Past Papers"),
    "edexcel": ("/past-papers/edexcel/index.html", "Edexcel Past Papers"),
}
BOARD_LABELS = {"aqa": "AQA", "edexcel": "Edexcel"}

# Display order and copy for the hub and the board index pages. Mirrors the
# order the notes use in templates/header.html.
BOARDS = [
    (
        "edexcel-theme-1",
        "Edexcel Theme 1",
        "Introduction to Markets and Market Failure",
    ),
    ("edexcel-theme-2", "Edexcel Theme 2", "The UK Economy - Performance and Policies"),
    ("edexcel-theme-3", "Edexcel Theme 3", "Business Behaviour and the Labour Market"),
    ("edexcel-theme-4", "Edexcel Theme 4", "A Global Perspective"),
    (
        "aqa-a2-micro",
        "AQA Microeconomics",
        "Individuals, Firms, Markets and Market Failure",
    ),
    ("aqa-a2-macro", "AQA Macroeconomics", "The National and International Economy"),
]
BOARD_ORDER = {d: i for i, (d, _, _) in enumerate(BOARDS)}

# How revision-notes/index.html groups the boards on its hub: an exam-board
# section per board, split into year groups.
HUB_SECTIONS = [
    (
        "Edexcel Economics",
        [
            ("Year 1 (AS Level)", ["edexcel-theme-1", "edexcel-theme-2"], ""),
            ("Year 2 (A Level)", ["edexcel-theme-3", "edexcel-theme-4"], "alt "),
        ],
    ),
    (
        "AQA Economics",
        [
            ("Year 1 &amp; 2 (A Level)", ["aqa-a2-micro", "aqa-a2-macro"], "alt "),
        ],
    ),
]

# Button labels on the hub, matching the wording on revision-notes/index.html.
HUB_LABELS = {
    "edexcel-theme-1": "Theme 1: Introduction to Markets and Market Failure",
    "edexcel-theme-2": "Theme 2: The UK Economy",
    "edexcel-theme-3": "Theme 3: Business Behaviour and the Labour Market",
    "edexcel-theme-4": "Theme 4: A Global Perspective",
    "aqa-a2-micro": "Micro: Individuals, Firms, Markets and Market Failure",
    "aqa-a2-macro": "Macro: The National and International Economy",
}
BOARD_BLURB = {d: b for d, _, b in BOARDS}

# Unit groupings, lifted verbatim from the notes board index pages so the
# questions index mirrors them exactly. Keyed by (boardDir, unit code),
# where the unit code is a spec code's first two components: 1.3.2 -> 1.3.
UNITS = {
    # edexcel-theme-1
    ("edexcel-theme-1", "1.1"): (
        "Nature of Economics",
        "Economics as a social science, positive and normative statements, the economic problem, production possibility frontiers",
    ),
    ("edexcel-theme-1", "1.2"): (
        "How Markets Work",
        "Rational decision making, demand, price elasticity, supply, price determination, consumer surplus",
    ),
    ("edexcel-theme-1", "1.3"): (
        "Market Failure",
        "Types of market failure, externalities, public goods, information gaps",
    ),
    ("edexcel-theme-1", "1.4"): (
        "Government Intervention",
        "Government intervention in markets, government failure",
    ),
    # edexcel-theme-2
    ("edexcel-theme-2", "2.1"): (
        "Measures of Economic Performance",
        "Economic growth, inflation, employment/unemployment, balance of payments",
    ),
    ("edexcel-theme-2", "2.2"): (
        "Aggregate Demand (AD)",
        "Components of AD, AD curve, shifts in AD",
    ),
    ("edexcel-theme-2", "2.3"): (
        "Aggregate Supply",
        "Short-run AS, long-run AS, factors influencing AS",
    ),
    ("edexcel-theme-2", "2.4"): (
        "National Income",
        "Circular flow of income, equilibrium, multiplier effect",
    ),
    ("edexcel-theme-2", "2.5"): (
        "Economic Growth",
        "Causes, consequences, sustainability",
    ),
    ("edexcel-theme-2", "2.6"): (
        "Macroeconomic Objectives and Policies",
        "Policy conflicts, demand-side policies, supply-side policies",
    ),
    # edexcel-theme-3
    ("edexcel-theme-3", "3.1"): (
        "Business Growth",
        "Forms of growth, mergers and takeovers, constraints on growth",
    ),
    ("edexcel-theme-3", "3.2"): (
        "Business Objectives",
        "Profit maximisation, revenue maximisation, other objectives",
    ),
    ("edexcel-theme-3", "3.3"): (
        "Revenue, Costs and Profits",
        "Revenue, costs, economies of scale, normal/supernormal profits",
    ),
    ("edexcel-theme-3", "3.4"): (
        "Market Structures",
        "Perfect competition, monopolistic competition, oligopoly, monopoly",
    ),
    ("edexcel-theme-3", "3.5"): (
        "Labour Market",
        "Demand and supply of labour, wage determination, government intervention",
    ),
    ("edexcel-theme-3", "3.6"): (
        "Government Intervention",
        "Regulation, competition policy, public ownership, privatisation",
    ),
    # edexcel-theme-4
    ("edexcel-theme-4", "4.1"): (
        "International Economics",
        "Globalisation, trade, terms of trade, trading blocs, WTO",
    ),
    ("edexcel-theme-4", "4.2"): (
        "Poverty and Inequality",
        "Absolute/relative poverty, inequality measures, policies",
    ),
    ("edexcel-theme-4", "4.3"): (
        "Emerging and Developing Economies",
        "Characteristics, growth strategies, role of financial sector",
    ),
    ("edexcel-theme-4", "4.4"): (
        "The Financial Sector",
        "Role of financial markets, market failure, regulation",
    ),
    ("edexcel-theme-4", "4.5"): (
        "Role of the State in the Macroeconomy",
        "Public expenditure, taxation, macroeconomic policies",
    ),
    # aqa-a2-micro
    ("aqa-a2-micro", "1.1"): (
        "Economic Methodology and the Economic Problem",
        "Positive vs normative, economic models, assumptions",
    ),
    ("aqa-a2-micro", "1.2"): (
        "Individual Economic Decision Making",
        "Rationality, behavioural economics, demand theory",
    ),
    ("aqa-a2-micro", "1.3"): (
        "Price Determination in a Competitive Market",
        "Demand, supply, equilibrium, elasticities",
    ),
    ("aqa-a2-micro", "1.4"): (
        "Production, Costs and Revenue",
        "Costs, revenues, economies of scale, efficiency",
    ),
    ("aqa-a2-micro", "1.5"): (
        "Perfect Competition, Imperfectly Competitive Markets and Monopoly",
        "Perfect competition, monopoly, oligopoly, contestability",
    ),
    ("aqa-a2-micro", "1.6"): (
        "Labour Market",
        "Demand, supply, wage determination, discrimination",
    ),
    ("aqa-a2-micro", "1.7"): (
        "The Distribution of Income and Wealth: Poverty and Inequality",
        "Regulation, competition policy, public ownership",
    ),
    ("aqa-a2-micro", "1.8"): (
        "The Market Mechanism, Market Failure and Government Intervention in Markets",
        "Regulation, competition policy, public ownership",
    ),
    # aqa-a2-macro
    ("aqa-a2-macro", "2.1"): (
        "The Measurement of Macroeconomic Performance",
        "Growth, inflation, unemployment, balance of payments",
    ),
    ("aqa-a2-macro", "2.2"): (
        "How the Macroeconomy Works",
        "AD components, AS models, macroeconomic equilibrium",
    ),
    ("aqa-a2-macro", "2.3"): (
        "Economic Performance",
        "Fiscal, monetary, supply-side policies",
    ),
    ("aqa-a2-macro", "2.4"): (
        "Financial Markets and Monetary Policy",
        "Globalisation, trade, development",
    ),
    ("aqa-a2-macro", "2.5"): (
        "Fiscal Policy and Supply-Side Policies",
        "Money, banking, financial sector",
    ),
    ("aqa-a2-macro", "2.6"): (
        "The International Economy",
        "Taxation, public spending, fiscal policy",
    ),
}

# Inline markup an author may use inside a fragment. Anything else is a bug
# in the source, not something to silently pass through to the page.
ALLOWED_TAGS_RE = re.compile(r"</?(?:strong|em|sub|sup)>|<br />")
TAG_RE = re.compile(r"<[^>]*>")
ENTITY_RE = re.compile(r"&(?!(?:amp|lt|gt|quot|#\d+|#x[0-9a-fA-F]+);)")

BANNED_OPTION_RE = re.compile(
    r"\ball of the above\b|\bnone of the above\b|\bboth [a-d] and [a-d]\b"
    r"|\ball of these\b|\bnone of these\b",
    re.IGNORECASE,
)

# UK English is a house rule. Word boundaries keep "laboratory" and
# "programmer" out of it.
US_SPELLINGS = [
    "maximize", "maximized", "maximizing", "minimize", "minimized", "minimizing",
    "labor", "behavior", "behaviors", "specialization", "organization",
    "organizations", "center", "centers", "analyze", "analyzed", "favorable",
    "unfavorable", "utilize", "utilized", "defense", "license", "practise",
    "traveling", "modeling", "labeled", "fulfill", "installment",
]
US_SPELLING_RE = re.compile(r"\b(" + "|".join(US_SPELLINGS) + r")\b", re.IGNORECASE)

ID_RE = re.compile(r"^(aqa|edexcel)-\d+(?:-\d+)*-q\d+$")


NOSCRIPT_ACCORDION = """
    <noscript>
      <!-- The accordion collapses its panels in CSS and quiz.js reopens them.
           With scripting off nothing could open them, so the topic links would
           be unreachable. Show every panel instead, and drop the +/- affordance
           that would then be lying. -->
      <style>
        .practice-questions-page .subtopic-list {
          display: block;
        }
        .practice-questions-page .toggle-icon {
          display: none;
        }
        .practice-questions-page .topic-item {
          cursor: auto;
        }
      </style>
    </noscript>"""

SITEMAP_OPEN = "  <!-- Practice Questions -->"
SITEMAP_CLOSE = "  <!-- /Practice Questions -->"


class SetError(Exception):
    """A question set that must not be written to a page."""


# ---------------------------------------------------------------- validation


def _starts_capitalised(text):
    """First visible character is not a lower-case letter.

    Options are read as standalone sentences next to their A-D chip, not as
    a grammatical continuation of the stem, so they open with a capital.
    Numbers and symbols ('-2.0', '£30') are left alone.
    """
    stripped = TAG_RE.sub("", text).lstrip()
    return not (stripped and stripped[0].isalpha() and stripped[0].islower())


def _fragment_errors(where, text, capitalised=False):
    """Fragments are HTML, so they must be pre-escaped and use known tags."""
    errors = []
    if not isinstance(text, str) or not text.strip():
        return [f"{where}: empty or not a string"]
    if capitalised and not _starts_capitalised(text):
        errors.append(f"{where}: must start with a capital letter")
    stripped = ALLOWED_TAGS_RE.sub("", text)
    for bad in TAG_RE.findall(stripped):
        errors.append(f"{where}: disallowed markup {bad!r}")
    if ENTITY_RE.search(text):
        errors.append(f"{where}: bare '&' - write &amp;")
    if "<" in stripped:
        errors.append(f"{where}: bare '<' - write &lt;")
    hit = US_SPELLING_RE.search(TAG_RE.sub("", text))
    if hit:
        errors.append(f"{where}: US spelling {hit.group(1)!r}")
    return errors


def validate(topic, path, seen_ids):
    errors = []

    required = [
        "board", "boardDir", "boardName", "spec", "slug", "title",
        "shortTitle", "pageTitle", "metaDescription", "intro",
        "notesTeaser", "questions",
    ]
    for field in required:
        if not topic.get(field):
            errors.append(f"missing field {field!r}")
    if errors:
        raise SetError(f"{path.relative_to(ROOT)}:\n  " + "\n  ".join(errors))

    if topic["board"] not in BOARD_LABELS:
        errors.append(f"board must be one of {sorted(BOARD_LABELS)}")
    if topic["boardDir"] not in BOARD_ORDER:
        errors.append(f"boardDir must be one of {sorted(BOARD_ORDER)}")
    elif not topic["boardDir"].startswith(topic["board"].split("-")[0]):
        errors.append(f"boardDir {topic['boardDir']!r} does not match board "
                      f"{topic['board']!r}")

    notes_file = NOTES_DIR / topic["boardDir"] / f"{topic['slug']}.html"
    if not notes_file.is_file():
        errors.append(f"no notes page at {notes_file.relative_to(ROOT)}")

    desc = topic["metaDescription"]
    if not 120 <= len(desc) <= 165:
        errors.append(f"metaDescription is {len(desc)} chars, want 120-165")
    if not topic["pageTitle"].endswith("| Economics Academy"):
        errors.append("pageTitle must end '| Economics Academy'")

    for field in ("intro", "notesTeaser"):
        errors += _fragment_errors(field, topic[field], capitalised=True)

    questions = topic["questions"]
    if not 4 <= len(questions) <= 10:
        errors.append(f"{len(questions)} questions, want 4-10")

    tally = {letter: 0 for letter in LETTERS}

    for index, q in enumerate(questions, start=1):
        where = f"q{index}"

        qid = q.get("id", "")
        if not ID_RE.match(qid):
            errors.append(f"{where}: id {qid!r} does not match <board>-<spec>-q<n>")
        elif qid in seen_ids:
            errors.append(f"{where}: duplicate id {qid!r} (also in {seen_ids[qid]})")
        else:
            seen_ids[qid] = str(path.relative_to(ROOT))

        if q.get("skill") not in SKILLS:
            errors.append(f"{where}: skill must be one of {sorted(SKILLS)}")
        if q.get("difficulty") not in DIFFICULTIES:
            errors.append(f"{where}: difficulty must be one of {sorted(DIFFICULTIES)}")
        if not isinstance(q.get("sketch"), bool):
            errors.append(f"{where}: sketch must be true or false")

        errors += _fragment_errors(f"{where}.stem", q.get("stem", ""), capitalised=True)

        options = q.get("options") or {}
        if set(options) != set(LETTERS):
            errors.append(f"{where}: options must be exactly A, B, C, D")
        else:
            for letter in LETTERS:
                errors += _fragment_errors(
                    f"{where}.options.{letter}", options[letter], capitalised=True
                )
                if BANNED_OPTION_RE.search(TAG_RE.sub("", options[letter])):
                    errors.append(f"{where}.options.{letter}: banned option pattern")

        answer = q.get("answer")
        if answer not in LETTERS:
            errors.append(f"{where}: answer must be A, B, C or D")
        else:
            tally[answer] += 1

        model = q.get("model") or {}
        errors += _fragment_errors(
            f"{where}.model.working", model.get("working", ""), capitalised=True
        )

        distractors = model.get("distractors") or {}
        if answer in LETTERS:
            expected = {l for l in LETTERS if l != answer}
            if set(distractors) != expected:
                errors.append(
                    f"{where}: model.distractors must cover exactly "
                    f"{sorted(expected)}, got {sorted(distractors)}"
                )
            else:
                for letter in sorted(expected):
                    errors += _fragment_errors(
                        f"{where}.model.distractors.{letter}",
                        distractors[letter],
                        capitalised=True,
                    )

        table = q.get("table")
        if table is not None:
            head = table.get("head")
            rows = table.get("rows")
            if not table.get("caption"):
                errors.append(f"{where}.table: missing caption")
            if not isinstance(head, list) or not head:
                errors.append(f"{where}.table: head must be a non-empty list")
            elif not isinstance(rows, list) or not rows:
                errors.append(f"{where}.table: rows must be a non-empty list")
            else:
                for r, row in enumerate(rows):
                    if not isinstance(row, list) or len(row) != len(head):
                        errors.append(
                            f"{where}.table.rows[{r}]: expected {len(head)} cells"
                        )
                        continue
                    for c, cell in enumerate(row):
                        if cell != "":
                            errors += _fragment_errors(
                                f"{where}.table.rows[{r}][{c}]", cell
                            )

    # Roughly even letters, so the answer is never guessable from the pattern.
    if len(questions):
        even = len(questions) / 4
        for letter in LETTERS:
            if abs(tally[letter] - even) > 2:
                errors.append(
                    f"letter distribution: {letter} used {tally[letter]} times "
                    f"in a set of {len(questions)}"
                )

    if errors:
        raise SetError(f"{path.relative_to(ROOT)}:\n  " + "\n  ".join(errors))

    return tally


# ------------------------------------------------------------------ helpers


def plain(fragment):
    """Fragment -> plain text, for JSON-LD and meta content."""
    text = fragment.replace("<br />", " ")
    text = TAG_RE.sub("", text)
    return re.sub(r"\s+", " ", html.unescape(text)).strip()


def attr(text):
    return html.escape(text, quote=True)


def headline(fragment, limit=110):
    """A short label for schema.org `name`: the stem's first sentence.

    Splitting on '. ' rather than '.' leaves '£2.50' and '4.1' intact. Falls
    back to a word-boundary cut so the label never ends mid-word.
    """
    text = plain(fragment)
    first = text.split(". ")[0].rstrip(".")
    if len(first) <= limit:
        return first
    cut = first[:limit].rsplit(" ", 1)[0]
    return cut + "…"


def notes_url(topic):
    return f"/revision-notes/{topic['boardDir']}/{topic['slug']}.html"


def page_url(topic):
    return f"/practice-questions/{topic['boardDir']}/{topic['slug']}.html"


# ----------------------------------------------------------------- rendering


def render_table(table):
    head = table["head"]
    lines = [
        '          <div class="table-container">',
        '            <table class="quiz-data">',
        f"              <caption>{table['caption']}</caption>",
        "              <thead>",
        "                <tr>",
    ]
    for cell in head:
        lines.append(f'                  <th scope="col">{cell}</th>')
    lines += ["                </tr>", "              </thead>", "              <tbody>"]
    for row in table["rows"]:
        lines.append("                <tr>")
        # First cell labels the row, so it is a header cell, not data.
        lines.append(f'                  <th scope="row">{row[0]}</th>')
        for cell in row[1:]:
            lines.append(f"                  <td>{cell}</td>")
        lines.append("                </tr>")
    lines += ["              </tbody>", "            </table>", "          </div>"]
    return "\n".join(lines)


def render_question(q, number):
    qid = q["id"]
    answer = q["answer"]
    out = [
        '        <li',
        '          class="quiz-item"',
        f'          id="q{number}"',
        f'          data-qid="{qid}"',
        f'          data-board="{q["_board"]}"',
        f'          data-spec="{q["_spec"]}"',
        f'          data-skill="{q["skill"]}"',
        f'          data-difficulty="{q["difficulty"]}"',
        f'          data-sketch="{"true" if q["sketch"] else "false"}"',
        f'          data-answer="{answer}"',
        "        >",
        f'          <h2 class="quiz-stem">',
        f'            <span class="quiz-number">{number}.</span> {q["stem"]}',
        "          </h2>",
        '          <p class="quiz-tags">',
        f'            <span class="quiz-tag">{SKILL_LABELS[q["skill"]]}</span>',
    ]
    if q["sketch"]:
        out.append(
            '            <span class="quiz-tag quiz-tag-sketch">Sketch to solve</span>'
        )
    out.append("          </p>")

    if q.get("table"):
        out.append(render_table(q["table"]))

    out += [
        '          <fieldset class="quiz-options">',
        '            <legend class="quiz-options-legend">Select one answer</legend>',
    ]
    for letter in LETTERS:
        out += [
            '            <div class="quiz-option">',
            "              <input",
            '                type="radio"',
            f'                id="{qid}-{letter}"',
            f'                name="{qid}"',
            f'                value="{letter}"',
            "              />",
            f'              <label for="{qid}-{letter}">',
            f'                <span class="quiz-letter">{letter}</span>',
            f'                <span class="quiz-option-text">{q["options"][letter]}</span>',
            "              </label>",
            "            </div>",
        ]
    out.append("          </fieldset>")

    out += [
        '          <p class="quiz-feedback" data-quiz-feedback role="status" hidden></p>',
        '          <details class="quiz-model">',
        "            <summary>Show model answer</summary>",
        '            <div class="quiz-model-body">',
        "              <p>",
        f"                <strong>Answer: {answer} "
        f"({plain(q['options'][answer])}).</strong>",
        f"                {q['model']['working']}",
        "              </p>",
        '              <p class="quiz-why-wrong-heading">',
        "                <strong>Why the other options are wrong</strong>",
        "              </p>",
        '              <ul class="quiz-why-wrong">',
    ]
    for letter in LETTERS:
        if letter == answer:
            continue
        out += [
            "                <li>",
            f"                  <strong>{letter}</strong> &mdash; "
            f"{q['model']['distractors'][letter]}",
            "                </li>",
        ]
    out += [
        "              </ul>",
        "            </div>",
        "          </details>",
        "        </li>",
    ]
    return "\n".join(out)


def render_jsonld_quiz(topic):
    questions = []
    for q in topic["questions"]:
        answer = q["answer"]
        suggested = [
            {
                "@type": "Answer",
                "text": plain(q["options"][letter]),
                "comment": {
                    "@type": "Comment",
                    "text": plain(q["model"]["distractors"][letter]),
                },
            }
            for letter in LETTERS
            if letter != answer
        ]
        questions.append(
            {
                "@type": "Question",
                "eduQuestionType": "Multiple choice",
                "learningResourceType": "Practice problem",
                "name": headline(q["stem"]),
                "text": plain(q["stem"]),
                "acceptedAnswer": {
                    "@type": "Answer",
                    "text": plain(q["options"][answer]),
                    "comment": {
                        "@type": "Comment",
                        "text": plain(q["model"]["working"]),
                    },
                },
                "suggestedAnswer": suggested,
            }
        )

    board_label = BOARD_LABELS[topic["board"]]
    return {
        "@context": "https://schema.org",
        "@type": "Quiz",
        "name": f"{topic['title']} - {board_label} A-Level Economics practice questions",
        "url": SITE + page_url(topic),
        "about": {"@type": "Thing", "name": topic["title"]},
        "educationalLevel": "A-Level",
        "inLanguage": "en-GB",
        "educationalAlignment": {
            "@type": "AlignmentObject",
            "alignmentType": "educationalSubject",
            "targetName": f"{board_label} A-Level Economics {topic['spec']}",
        },
        "assesses": topic["title"],
        "provider": {
            "@type": "EducationalOrganization",
            "name": "Economics Academy",
            "url": SITE,
        },
        "hasPart": questions,
    }


def jsonld_block(data, indent):
    pad = " " * indent
    body = json.dumps(data, indent=2, ensure_ascii=False)
    body = "\n".join(pad + "  " + line for line in body.splitlines())
    return (
        f'{pad}<script type="application/ld+json">\n'
        f"{body}\n"
        f"{pad}</script>"
    )


def render_page(topic):
    url = SITE + page_url(topic)
    board_label = BOARD_LABELS[topic["board"]]
    papers_href, papers_label = PAST_PAPERS[topic["board"]]
    count = len(topic["questions"])
    notes = notes_url(topic)

    # render_question emits at 8 spaces; the <ol> sits at 12, so its children
    # belong at 14.
    items = "\n".join(
        "\n".join(
            ("      " + line if line else line)
            for line in render_question(q, n).splitlines()
        )
        for n, q in enumerate(topic["questions"], start=1)
    )

    body = f"""      <section id="main" class="quiz-page">
        <div class="container">
          <nav class="breadcrumb">
            <a href="/">Home</a>
            <span class="separator">&rsaquo;</span>
            <a href="/practice-questions/index.html">Practice Questions</a>
            <span class="separator">&rsaquo;</span>
            <a href="/practice-questions/{topic['boardDir']}/index.html"
              >{topic['boardName']}</a
            >
            <span class="separator">&rsaquo;</span>
            <span>{topic['spec']} {topic['title']}</span>
          </nav>

          <div class="quiz-container">
            <header class="major">
              <h1>{topic['spec']} {topic['shortTitle']} &mdash; Practice Questions</h1>
            </header>

            <p class="quiz-intro">{topic['intro']}</p>

            <p class="quiz-meta">
              <span>{count} questions</span>
              <span>{board_label} A-Level</span>
              <span>Multiple choice</span>
              <span>Model answers included</span>
            </p>

            <p class="quiz-notes-link">
              Not read the notes yet? Start with the
              <a href="{notes}">{topic['spec']} {topic['shortTitle']} revision notes</a>.
            </p>

            <div class="quiz-dashboard" data-quiz-dashboard>
              <p class="quiz-score" data-quiz-score>
                {count} questions in this set
              </p>
              <p class="quiz-best" data-quiz-best></p>
              <div class="quiz-progress-track">
                <div class="quiz-progress-bar" data-quiz-bar></div>
              </div>
              <button
                type="button"
                class="button alt small quiz-dashboard-reset"
                data-quiz-reset
              >
                Reset saved progress
              </button>
            </div>

            <ol class="quiz-list">
{items}
            </ol>

            <div class="quiz-summary" data-quiz-summary hidden>
              <h2 data-quiz-summary-heading>Your score</h2>
              <p data-quiz-summary-text></p>
              <div class="quiz-summary-actions">
                <button type="button" class="button primary" data-quiz-retry>
                  Try again
                </button>
                <a href="{notes}" class="button alt">Back to the notes</a>
              </div>
            </div>

            <div class="quiz-cta">
              <p>Ready to go further?</p>
              <a href="{notes}" class="button alt"
                >Revision Notes: {topic['shortTitle']}</a
              >
              <a href="{papers_href}" class="button alt">{papers_label}</a>
              <a href="/tutoring.html" class="button">Book a Free Intro Call</a>
            </div>
          </div>
        </div>
      </section>"""

    return shell(
        title=topic["pageTitle"],
        desc=topic["metaDescription"],
        url=url,
        css="/css/pages/quiz.css",
        jsonld=jsonld_block(render_jsonld_quiz(topic), 4),
        breadcrumb=breadcrumb_jsonld(
            [
                ("Home", "/"),
                ("Practice Questions", "/practice-questions/index.html"),
                (
                    topic["boardName"],
                    f"/practice-questions/{topic['boardDir']}/index.html",
                ),
                (f"{topic['spec']} {topic['title']}", None),
            ]
        ),
        body=body,
        scripts='\n    <script src="/js/components/quiz.js" defer></script>',
        og_type="article",
    )




def shell(
    *, title, desc, url, css, jsonld, breadcrumb, body, scripts="",
    og_type="website", head_extra="",
):
    """The common page skeleton. Same head order as a notes topic page."""
    return f"""<!doctype html>
<html lang="en-GB">
  <head>
    <!-- Google tag (gtag.js) -->
    <script
      async
      src="https://www.googletagmanager.com/gtag/js?id={GA_ID}"
    ></script>
    <script>
      window.dataLayer = window.dataLayer || [];
      function gtag() {{
        dataLayer.push(arguments);
      }}
      gtag("js", new Date());

      gtag("config", "{GA_ID}");
    </script>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <!-- css/main.css reaches the web fonts through an @import, so the browser
         cannot discover fonts.gstatic.com until main.css has parsed and the
         imported sheet has come back. Warming both origins here shortens that
         chain and cuts the font-swap layout shift. -->
    <link rel="preconnect" href="https://fonts.googleapis.com" />
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
    <title>{attr(title)}</title>
    <meta name="description" content="{attr(desc)}" />

    <link rel="canonical" href="{url}" />
    <meta property="og:type" content="{og_type}" />
    <meta property="og:site_name" content="Economics Academy" />
    <meta property="og:locale" content="en_GB" />
    <meta property="og:url" content="{url}" />
    <meta property="og:title" content="{attr(title)}" />
    <meta property="og:description" content="{attr(desc)}" />
    <meta property="og:image" content="{OG_IMAGE}" />
    <meta property="og:image:width" content="1200" />
    <meta property="og:image:height" content="1200" />
    <meta property="og:image:type" content="image/png" />
    <meta property="og:image:alt" content="Economics Academy logo" />
    <meta name="twitter:card" content="summary_large_image" />
    <meta name="twitter:title" content="{attr(title)}" />
    <meta name="twitter:description" content="{attr(desc)}" />
    <meta name="twitter:image" content="{OG_IMAGE}" />
{jsonld}
    <link rel="icon" href="/favicon.ico" sizes="any" />
    <link rel="apple-touch-icon" href="/apple-touch-icon.png" />
    <link rel="manifest" href="/site.webmanifest" />
    <link rel="stylesheet" href="/css/main.css" />

    <link rel="stylesheet" href="{css}" />{head_extra}
{breadcrumb}
  </head>
  <body class="is-preload">
    <div id="page-wrapper">
      <!-- Header -->
      <div id="header-placeholder"></div>

{body}

      <!-- Footer -->
      <div id="footer-placeholder"></div>
    </div>

    <!-- Scripts -->
    <script src="/js/jquery.min.js"></script>
    <script src="/js/jquery.dropotron.min.js"></script>
    <script src="/js/components/inject-templates.js"></script>
    <script src="/js/browser.min.js"></script>
    <script src="/js/breakpoints.min.js"></script>
    <script src="/js/util.js"></script>
    <script src="/js/main.js"></script>{scripts}
  </body>
</html>
"""


def breadcrumb_jsonld(trail):
    items = []
    for position, (name, href) in enumerate(trail, start=1):
        item = {"@type": "ListItem", "position": position, "name": name}
        if href:
            item["item"] = SITE + href
        items.append(item)
    return jsonld_block(
        {
            "@context": "https://schema.org",
            "@type": "BreadcrumbList",
            "itemListElement": items,
        },
        4,
    )


def unit_of(spec):
    """1.3.2 -> 1.3"""
    return ".".join(spec.split(".")[:2])


def render_cta_strip(text, actions):
    """The conversion strip from revision-notes/index.html."""
    buttons = "\n".join(
        f'              <a href="{href}" class="button{cls}">{label}</a>'
        for href, cls, label in actions
    )
    return f"""          <section class="pq-cta-strip">
            <p>{text}</p>
            <div class="pq-cta-actions">
{buttons}
            </div>
          </section>"""


def render_unit(board_dir, unit, topics, index):
    """One collapsible unit on a board index, matching the notes accordion."""
    title, blurb = UNITS.get(
        (board_dir, unit), (f"Unit {unit}", "")
    )
    count = sum(len(t["questions"]) for t in topics)
    items = "\n".join(
        f"""                  <li class="subtopic-item">
                    <a href="{page_url(t)}">
                      <span class="subtopic-name"
                        >{t['spec']} {t['shortTitle']}</span
                      >
                      <span class="subtopic-meta"
                        >{len(t['questions'])} questions</span
                      >
                      <span
                        class="subtopic-last"
                        data-quiz-last="{t['board']}:{t['spec']}"
                      ></span>
                    </a>
                  </li>"""
        for t in sorted(topics, key=lambda t: spec_key(t["spec"]))
    )
    return f"""              <li class="topic-item">
                <div class="topic-header">
                  <h2>
                    <button
                      type="button"
                      class="topic-toggle"
                      aria-expanded="false"
                      aria-controls="subtopic-{index}"
                    >
                      {unit} {title}
                    </button>
                  </h2>
                  <span class="toggle-icon" aria-hidden="true">+</span>
                </div>
                <p>{blurb} &middot; {count} questions</p>

                <ul class="subtopic-list" id="subtopic-{index}">
{items}
                </ul>
              </li>"""


def render_board_index(board_dir, topics):
    name = next(n for d, n, _ in BOARDS if d == board_dir)
    blurb = BOARD_BLURB[board_dir]
    board = topics[0]["board"]
    label = BOARD_LABELS[board]
    papers_href, papers_label = PAST_PAPERS[board]
    count = sum(len(t["questions"]) for t in topics)
    topic_word = "topic" if len(topics) == 1 else "topics"
    url = f"{SITE}/practice-questions/{board_dir}/index.html"

    title = f"{name} Practice Questions — {label} A-Level Economics | Economics Academy"
    desc = (
        f"Free {label} A-Level Economics multiple-choice questions on {blurb.lower()}. "
        f"{count} questions across {len(topics)} {topic_word}, each with a worked answer."
    )[:164]

    by_unit = {}
    for t in topics:
        by_unit.setdefault(unit_of(t["spec"]), []).append(t)
    units = "\n".join(
        render_unit(board_dir, u, by_unit[u], i)
        for i, u in enumerate(sorted(by_unit, key=spec_key), start=1)
    )

    body = f"""      <section id="main" class="practice-questions-page">
        <div class="container">
          <nav class="breadcrumb">
            <a href="/">Home</a>
            <span class="separator">&rsaquo;</span>
            <a href="/practice-questions/index.html">Practice Questions</a>
            <span class="separator">&rsaquo;</span>
            <span>{name}</span>
          </nav>

          <section class="pq-header">
            <header class="major">
              <h1>{name} Practice Questions</h1>
              <p>
                Free exam-style multiple-choice questions covering
                {blurb.lower()}, written to the style and difficulty of the real
                {label} papers. Every question carries a full worked answer.
                Click any unit to expand its topics.
              </p>
            </header>
          </section>

          <h2>Available Topics</h2>
          <p class="pq-note">
            Click any unit below to see its topics &middot; {count} questions across
            {len(topics)} {topic_word}, free and with no sign-up.
          </p>

          <ul class="topic-list">
{units}
          </ul>

{render_cta_strip(
    "<strong>Getting these wrong?</strong> Work through the topic with an expert "
    "tutor, or send an essay for detailed examiner-style marking.",
    [
        (f"/revision-notes/{board_dir}/index.html", " alt", "Read the Notes"),
        (papers_href, " alt", papers_label),
        ("/tutoring.html", "", "Book a Free Intro Call"),
    ],
)}
        </div>
      </section>"""

    return shell(
        title=title,
        desc=desc,
        url=url,
        css="/css/pages/practice-questions.css",
        jsonld=jsonld_block(
            {
                "@context": "https://schema.org",
                "@type": "CollectionPage",
                "name": f"{name} practice questions",
                "description": desc,
                "url": url,
                "inLanguage": "en-GB",
                "isPartOf": {
                    "@type": "WebSite",
                    "name": "Economics Academy",
                    "url": SITE,
                },
            },
            4,
        ),
        breadcrumb=breadcrumb_jsonld(
            [
                ("Home", "/"),
                ("Practice Questions", "/practice-questions/index.html"),
                (name, None),
            ]
        ),
        body=body,
        scripts='\n    <script src="/js/components/quiz.js" defer></script>',
        head_extra=NOSCRIPT_ACCORDION,
    )


def render_hub(by_board):
    total = sum(len(t["questions"]) for ts in by_board.values() for t in ts)
    topic_count = sum(len(ts) for ts in by_board.values())
    topic_word = "topic" if topic_count == 1 else "topics"
    url = f"{SITE}/practice-questions/index.html"

    title = (
        "A-Level Economics Practice Questions — AQA and Edexcel "
        "| Economics Academy"
    )
    desc = (
        f"Free A-Level Economics multiple-choice practice questions for AQA and "
        f"Edexcel. {total} questions across {topic_count} {topic_word}, each with a "
        f"full worked answer."
    )[:164]

    sections = []
    for heading, groups in HUB_SECTIONS:
        rows = []
        for group_name, dirs, cls in groups:
            live = [d for d in dirs if by_board.get(d)]
            if not live:
                continue
            buttons = []
            for d in live:
                n = sum(len(t["questions"]) for t in by_board[d])
                topics_n = len(by_board[d])
                buttons.append(
                    f"""                <a
                  href="/practice-questions/{d}/index.html"
                  class="button {cls}pq-board-button"
                >
                  {HUB_LABELS[d]}
                  <span class="pq-board-count"
                    >{topics_n} {'topic' if topics_n == 1 else 'topics'} &middot; {n} questions</span
                  >
                </a>"""
                )
            rows.append(
                f"""            <div class="pq-board-group">
              <h3>{group_name}</h3>
              <div class="pq-board-buttons">
{chr(10).join(buttons)}
              </div>
            </div>"""
            )
        if not rows:
            continue
        sections.append(
            f"""          <div class="pq-board-section">
            <header class="major">
              <h2>{heading}</h2>
            </header>

{chr(10).join(rows)}
          </div>"""
        )

    body = f"""      <section id="main" class="practice-questions-page">
        <div class="container">
          <section class="pq-hero">
            <h1 class="pq-h1">Free A-Level Economics Practice Questions</h1>
            <p class="pq-intro">
              Exam-style multiple-choice questions for
              <strong>Edexcel</strong> and <strong>AQA</strong>, written to the
              style and difficulty of the real papers. Answer one at a time for
              instant feedback, then read a full worked answer that explains the
              correct option and names the mistake behind each wrong one.
            </p>
            <p class="pq-hero-meta">
              {total} questions &middot; {topic_count} {topic_word} &middot; free, no sign-up
            </p>
          </section>

{chr(10).join(sections)}

{render_cta_strip(
    "<strong>Questions show you the gaps &mdash; essays are where the marks are.</strong> "
    "Send yours for examiner-style marking, or work through the tricky topics "
    "with a specialist tutor.",
    [
        ("/revision-notes/index.html", " alt", "Free Revision Notes"),
        ("/marking.html", " alt", "Get Your Essays Marked"),
        ("/tutoring.html", "", "Book a Free Intro Call"),
    ],
)}
        </div>
      </section>"""

    return shell(
        title=title,
        desc=desc,
        url=url,
        css="/css/pages/practice-questions.css",
        jsonld=jsonld_block(
            {
                "@context": "https://schema.org",
                "@type": "CollectionPage",
                "name": "A-Level Economics practice questions",
                "description": desc,
                "url": url,
                "inLanguage": "en-GB",
                "isPartOf": {
                    "@type": "WebSite",
                    "name": "Economics Academy",
                    "url": SITE,
                },
            },
            4,
        ),
        breadcrumb=breadcrumb_jsonld([("Home", "/"), ("Practice Questions", None)]),
        body=body,
        scripts='\n    <script src="/js/components/quiz.js" defer></script>',
    )


def spec_key(spec):
    return tuple(int(part) for part in spec.split("."))


# ------------------------------------------------------------------ sitemap


def update_sitemap(topics):
    """Insert or refresh the practice-questions block. Purely additive to
    every line outside the block's own markers."""
    today = datetime.date.today().isoformat()
    lines = [SITEMAP_OPEN]
    lines.append(
        f"  <url><loc>{SITE}/practice-questions/</loc>"
        f"<lastmod>{today}</lastmod><priority>0.9</priority></url>"
    )
    for board_dir in sorted({t["boardDir"] for t in topics}, key=BOARD_ORDER.get):
        lines.append(
            f"  <url><loc>{SITE}/practice-questions/{board_dir}/</loc>"
            f"<lastmod>{today}</lastmod><priority>0.8</priority></url>"
        )
    for topic in sorted(
        topics, key=lambda t: (BOARD_ORDER[t["boardDir"]], spec_key(t["spec"]))
    ):
        lines.append(
            f"  <url><loc>{SITE}{page_url(topic)}</loc>"
            f"<lastmod>{today}</lastmod><priority>0.7</priority></url>"
        )
    lines.append(SITEMAP_CLOSE)
    block = "\n".join(lines)

    text = SITEMAP.read_text(encoding="utf-8")
    if SITEMAP_OPEN in text and SITEMAP_CLOSE in text:
        start = text.index(SITEMAP_OPEN)
        end = text.index(SITEMAP_CLOSE) + len(SITEMAP_CLOSE)
        text = text[:start] + block + text[end:]
    else:
        text = text.replace("</urlset>", block + "\n\n</urlset>")
    SITEMAP.write_text(text, encoding="utf-8")


# --------------------------------------------------------------------- main


def load(paths):
    topics = []
    seen_ids = {}
    failures = []
    for path in paths:
        try:
            topic = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            failures.append(f"{path.relative_to(ROOT)}: invalid JSON - {exc}")
            continue
        try:
            validate(topic, path, seen_ids)
        except SetError as exc:
            failures.append(str(exc))
            continue
        for q in topic["questions"]:
            q["_board"] = topic["board"]
            q["_spec"] = topic["spec"]
        topics.append(topic)
    return topics, failures


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("sources", nargs="*", help="paths relative to questions-data/")
    parser.add_argument("--check", action="store_true", help="validate, write nothing")
    parser.add_argument("--sitemap", action="store_true", help="refresh sitemap.xml")
    args = parser.parse_args(argv)

    if args.sources:
        paths = [DATA_DIR / s for s in args.sources]
        missing = [p for p in paths if not p.is_file()]
        if missing:
            for p in missing:
                print(f"no such source: {p}", file=sys.stderr)
            return 2
    else:
        paths = sorted(DATA_DIR.glob("*/*.json"))

    if not paths:
        print("no question sources found", file=sys.stderr)
        return 1

    topics, failures = load(paths)

    if failures:
        print(f"{len(failures)} set(s) failed validation:\n", file=sys.stderr)
        for failure in failures:
            print(failure, file=sys.stderr)
        return 1

    total = sum(len(t["questions"]) for t in topics)
    if args.check:
        print(f"OK - {len(topics)} set(s), {total} questions, nothing written")
        return 0

    for topic in topics:
        out = OUT_DIR / topic["boardDir"] / f"{topic['slug']}.html"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(render_page(topic), encoding="utf-8")
        print(f"wrote {out.relative_to(ROOT)} ({len(topic['questions'])} questions)")

    # The hub and the board indexes list everything, so they can only be
    # rebuilt from a full run. A partial run leaves them as they were.
    if args.sources:
        print("\npartial build - hub, board indexes and sitemap left untouched")
        print(f"{len(topics)} set(s), {total} questions")
        return 0

    by_board = {}
    for topic in topics:
        by_board.setdefault(topic["boardDir"], []).append(topic)

    for board_dir, board_topics in by_board.items():
        out = OUT_DIR / board_dir / "index.html"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(render_board_index(board_dir, board_topics), encoding="utf-8")
        print(f"wrote {out.relative_to(ROOT)} ({len(board_topics)} topics)")

    hub = OUT_DIR / "index.html"
    hub.write_text(render_hub(by_board), encoding="utf-8")
    print(f"wrote {hub.relative_to(ROOT)}")

    if args.sitemap:
        update_sitemap(topics)
        print(f"updated {SITEMAP.relative_to(ROOT)}")

    print(f"\n{len(topics)} set(s), {total} questions")
    return 0


if __name__ == "__main__":
    sys.exit(main())

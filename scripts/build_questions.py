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
    python3 scripts/build_sitemap.py                   # the sitemap, separately
    python3 scripts/build_questions.py aqa-a2-micro/1-3-2.json   # one topic

Exit status is non-zero if any set fails validation.

This script emits the topic pages, the six board index pages and the hub. The
sitemap is built separately by scripts/build_sitemap.py.

URLs are written in canonical form: a directory page is linked and
canonicalised as /practice-questions/<board>/, never .../index.html. Both
forms return 200 on GitHub Pages, so linking the index.html variant creates a
duplicate URL that competes with the canonical one.
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
sys.path.insert(0, str(ROOT / "scripts"))
import board_data  # noqa: E402
# Wave 2 Phase 6, the last of the five. page_shell.py owns the <head>.
import page_shell as page_shell_mod  # noqa: E402
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

# All four structures below come from boards-data/boards.json - Wave 3.2,
# PH09-022. This file held five of them and was PH01-012's largest single count.
PAST_PAPERS = {
    b["slugs"]["pastPapers"]:
        (b["papersUrl"], f"{b['names']['short']} Past Papers")
    for b in board_data.load().values()
}
BOARD_LABELS = {b["slugs"]["pastPapers"]: b["names"]["short"]
                for b in board_data.load().values()}

# Cross-resource links per group - resource unification Phase 2. Each group's
# flashcards deck and question-finder board page, from the record: the slugs
# differ per family ("edexcel-theme-1" here, "edexcel-a/theme-1" in
# flashcards, "edexcel" in the question bank), which is exactly why they are
# read rather than derived. GROUP_LABELS is the short display label
# ("Theme 1", "Microeconomics") for the notes button on each board index.
FLASHCARDS_URLS = {
    group["notesDir"]:
        f"/flashcards/{board['slugs']['flashcards']}/{group['flashcardsSlug']}/"
    for _key, board, group in board_data.groups()
}
QB_URLS = {
    group["notesDir"]: f"/past-paper-questions/{board['slugs']['questionBank']}/"
    for _key, board, group in board_data.groups()
}
GROUP_LABELS = {group["notesDir"]: group["label"]
                for _key, _board, group in board_data.groups()}

# Display order and copy for the hub and the board index pages. Mirrors the
# order the notes use in templates/header.html.
#
# THE ORDER IS THE OUTPUT. BOARD_ORDER below is this list's index, and it sorts
# the topics on every board index page, so the record's group order reaches
# published pages directly. board_data.EXPECTED_NOTES_DIRS is what makes
# changing it a declared act rather than a silent reordering.
#
# `practiceQuestions` is the third of Theme 2's three spellings - the HYPHEN
# form, which this family shares with the flashcards decks and taxonomy.json
# does not.
BOARDS = [
    (group["notesDir"],
     group["names"]["practiceQuestionsLabel"],
     group["names"]["practiceQuestions"])
    for _key, _board, group in board_data.groups()
]
BOARD_ORDER = {d: i for i, (d, _, _) in enumerate(BOARDS)}

# How revision-notes/index.html groups the boards on its hub: an exam-board
# section per board, split into year groups.
HUB_SECTIONS = [
    (
        "Edexcel Economics",
        [
            ("Year 1 (AS Level)", ["edexcel-theme-1", "edexcel-theme-2"]),
            ("Year 2 (A Level)", ["edexcel-theme-3", "edexcel-theme-4"]),
        ],
    ),
    (
        "AQA Economics",
        [
            ("Year 1 &amp; 2 (A Level)", ["aqa-a2-micro", "aqa-a2-macro"]),
        ],
    ),
]

# Button labels on the hub, matching the wording on revision-notes/index.html.
# Theme 2's is "Theme 2: The UK Economy" - the SHORT form, and the reason
# boards.json records a group's name five times over rather than once.
HUB_LABELS = {group["notesDir"]: group["names"]["practiceQuestionsButton"]
              for _key, _board, group in board_data.groups()}
BOARD_BLURB = {d: b for d, _, b in BOARDS}

# HUB_SECTIONS is NOT in the record and is not meant to be: which themes are
# Year 1 and which are Year 2 is a teaching grouping, not board identity, and
# putting it in boards.json would mean inventing a field rather than recording
# one. But a board added to the record now reaches four structures on this page
# automatically and this one not at all, which would drop it off the hub with no
# error. So the two are reconciled here instead.
_hub_dirs = [d for _h, gs in HUB_SECTIONS for _label, ds in gs for d in ds]
_recorded = [g["notesDir"] for _k, _b, g in board_data.groups()]
if sorted(_hub_dirs) != sorted(_recorded):
    sys.exit(
        f"HUB_SECTIONS lists {sorted(_hub_dirs)} and boards.json records "
        f"{sorted(_recorded)}. Every board reaches the practice-questions hub "
        f"through HUB_SECTIONS, so a group missing here is a group missing "
        f"from the page - add it to the right year group."
    )

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
#
# Deliberately absent: "practise" and "license". Both are the correct UK
# *verb* forms ("to practise", "to license"), sitting alongside the UK nouns
# "practice" and "licence". Listing them flagged correct UK English.
US_SPELLINGS = [
    "maximize", "maximized", "maximizing", "minimize", "minimized", "minimizing",
    "labor", "behavior", "behaviors", "specialization", "organization",
    "organizations", "center", "centers", "analyze", "analyzed", "favorable",
    "unfavorable", "utilize", "utilized", "defense",
    "traveling", "modeling", "labeled", "fulfill", "installment",
]
US_SPELLING_RE = re.compile(r"\b(" + "|".join(US_SPELLINGS) + r")\b", re.IGNORECASE)

# A question ID is {board}-{spec}-q{n}, so its first component is a board slug.
# Longest first, for the reason extract_glossary.SPEC_ALERT_RE gives: `re`
# alternation is ordered, so a slug that is a prefix of another would shadow it.
ID_RE = re.compile(
    r"^("
    + "|".join(re.escape(s) for s in sorted(BOARD_LABELS, key=len, reverse=True))
    + r")-\d+(?:-\d+)*-q\d+$"
)


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
            # Same @id on every restatement of the organisation across the
            # site, so the 354 copies read as one entity rather than 354
            # lookalikes. See seo/08-structured-data.md.
            "@id": f"{SITE}/#organization",
            "name": "Economics Academy",
            "url": SITE,
        },
        "hasPart": questions,
    }


def jsonld_block(data, indent):
    """Kept as the identity on `data`.

    Wave 2 Phase 6: page_shell.ldjson() does the serialising now, and it
    produced byte-identical output to what this used to - json.dumps(indent=2)
    re-indented by six, inside script tags at four. The function survives so
    the three call sites read unchanged and the `indent` argument stays
    documented as having only ever been 4.
    """
    assert indent == 4, f"only indent=4 was ever used, got {indent}"
    return data


def render_page(topic, siblings=(), ppq=None):
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

    body = f"""      <main id="main" class="quiz-page">
        <div class="container">
          <nav class="breadcrumb" aria-label="Breadcrumb">
            <a href="/">Home</a>
            <span class="separator">&rsaquo;</span>
            <a href="/practice-questions/">Practice Questions</a>
            <span class="separator">&rsaquo;</span>
            <a href="/practice-questions/{topic['boardDir']}/"
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
                <a href="{notes}" class="button alt"
                  >Back to the {topic['spec']} {topic['shortTitle']} notes</a
                >
              </div>
            </div>

{render_related(topic, siblings, ppq)}            <div class="quiz-cta">
              <p>Ready to go further?</p>
              <a href="{notes}" class="button alt"
                >Revision Notes: {topic['shortTitle']}</a
              >
              <a href="{papers_href}" class="button alt">{papers_label}</a>
              <a href="/tutoring.html" class="button">Book a Free Intro Call</a>
            </div>
          </div>
        </div>
      </main>"""

    return shell(
        title=topic["pageTitle"],
        desc=topic["metaDescription"],
        url=url,
        css="/css/pages/quiz.css",
        jsonld=jsonld_block(render_jsonld_quiz(topic), 4),
        breadcrumb=breadcrumb_jsonld(
            [
                ("Home", "/"),
                ("Practice Questions", "/practice-questions/"),
                (
                    topic["boardName"],
                    f"/practice-questions/{topic['boardDir']}/",
                ),
                (f"{topic['spec']} {topic['title']}", None),
            ]
        ),
        body=body,
        scripts=("/js/components/quiz.js",),
        og_type="article",
    )




EARLY_PRECONNECT_COMMENT = """    <!-- The font stylesheet is linked in <head> below, so the preload scanner
         finds it immediately. gstatic is still a second origin, discovered only
         once that stylesheet parses, so warming both here still pays. -->"""


def shell(
    *, title, desc, url, css, jsonld, breadcrumb, body, scripts=(),
    og_type="website", head_extra="",
):
    """The common page skeleton. The <head> comes from scripts/page_shell.py.

    Wave 2 Phase 6. Two things about this family's <head> are its own and are
    passed as values rather than reworded: it puts the font preconnect before
    <title> under its own explanatory comment, and its six hub pages carry a
    <noscript> block that DO-NOT-BREAK protects - the accordion collapses in
    CSS and quiz.js reopens it, so with scripting off the topic links would be
    unreachable without it.
    """
    head = page_shell_mod.render_head({
        "title": attr(title),
        "description": attr(desc),
        "canonical": url,
        "preconnectEarly": True,
        "earlyPreconnectComment": EARLY_PRECONNECT_COMMENT,
        "og": {
            "type": og_type, "siteName": "Economics Academy",
            "locale": "en_GB", "url": url,
            "title": attr(title), "description": attr(desc),
            "image": OG_IMAGE, "image:width": "1200", "image:height": "1200",
            "image:type": "image/png", "image:alt": "Economics Academy logo",
        },
        "twitter": {
            "card": "summary_large_image", "title": attr(title),
            "description": attr(desc), "image": OG_IMAGE,
        },
        "jsonldBeforeIcons": [jsonld],
        "jsonldAfterStyles": [breadcrumb],
        "pageStylesheets": [css],
        "headNoscript": head_extra or None,
    })
    return f"""<!doctype html>
<html lang="en-GB">
  <head>
{head}
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
{page_shell_mod.script_tail(scripts)}
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


PPQ_INDEX = ROOT / "past-paper-questions" / "questions.json"


def load_pastpaper_topics():
    """practice-question page URL -> that topic's past-paper-questions record.

    Joined on questionsUrl, which is a full site path, so the match is exact
    and CANNOT cross an exam board. No topic code is ever compared: 37 codes
    exist on both boards and mean different topics - 1.1.1 is "Economics as a
    Social Science" on Edexcel and "Economic Methodology" on AQA. Matching on
    one would resolve to a real page, 404 nothing, and quietly send students to
    the wrong board.

    Absent index -> empty map -> no past-paper link is emitted anywhere. The
    build still succeeds, because this section is additive.
    """
    if not PPQ_INDEX.is_file():
        return {}
    data = json.loads(PPQ_INDEX.read_text(encoding="utf-8"))
    out = {}
    for slug, rec in data.get("topics", {}).items():
        if rec.get("questionsUrl"):
            out[rec["questionsUrl"]] = dict(rec, slug=slug)
    return out


def siblings_for(topic, by_unit, limit=4):
    """Up to `limit` other topics from the same unit on the SAME board.

    Keyed on (boardDir, unit), and boardDir carries the board, so a cross-board
    sibling is not representable. Never keyed on the unit code alone - "1.2" is
    a real unit on both boards.

    The window is centred on this topic so the list reads as neighbouring
    specification points rather than always the first four in the unit.
    """
    peers = by_unit.get((topic["boardDir"], unit_of(topic["spec"])), [])
    if len(peers) <= 1:
        return []
    peers = sorted(peers, key=lambda t: spec_key(t["spec"]))
    i = next(n for n, t in enumerate(peers) if t["slug"] == topic["slug"])
    lo, hi = i, i + 1
    picked = []
    while len(picked) < limit and (lo > 0 or hi < len(peers)):
        if lo > 0:
            lo -= 1
            picked.append(peers[lo])
        if len(picked) < limit and hi < len(peers):
            picked.append(peers[hi])
            hi += 1
    return sorted(picked, key=lambda t: spec_key(t["spec"]))[:limit]


def render_related(topic, siblings, ppq):
    """The 'keep going' block: past-paper questions, then sibling topics.

    Added because practice-questions was the one section with no lateral links
    at all - 0 of 166 pages linked to a sibling, against 53.6% in the notes and
    100% in past-paper-questions. See seo/07-link-graph.md.

    The past-paper anchor is deliberately a descriptive sentence rather than
    "{spec} {shortTitle}": the past-paper index pages already point at these
    topics with that exact string, up to 68 times each, and repeating it here
    would deepen an anchor-text monoculture rather than add anything.
    """
    if not ppq and not siblings:
        return ""

    parts = ['            <nav class="quiz-related" aria-labelledby="quiz-related-heading">',
             '              <h2 id="quiz-related-heading">Keep going on this topic</h2>']

    if ppq:
        if ppq["hasPage"]:
            href = ppq["url"]
        else:
            href = f"/past-paper-questions/?board={ppq['board']}&amp;topic={ppq['slug']}"
        n = ppq["count"]
        noun = "question" if n == 1 else "questions"
        parts += [
            '              <p class="quiz-related-papers">',
            f'                <a href="{href}"',
            f'                  >{n} real exam {noun} on {ppq["shortTitle"]}</a',
            "                >",
            "                from the past papers, each linked to the page of the mark",
            "                scheme where its answer begins.",
            "              </p>",
        ]

    if siblings:
        # UNITS is the same grouping the board index pages print, lifted from
        # the notes, so the heading here matches what the student saw there.
        unit = UNITS.get((topic["boardDir"], unit_of(topic["spec"])))
        lead = (f"Other topics in {unit[0]}:" if unit
                else "Other topics in this unit:")
        parts += [f'              <p class="quiz-related-lead">{lead}</p>',
                  '              <ul class="quiz-related-list">']
        for s in siblings:
            parts += [
                "                <li>",
                f'                  <a href="{page_url(s)}"',
                f'                    >{s["spec"]} {s["shortTitle"]}</a',
                "                  >",
                "                </li>",
            ]
        parts.append("              </ul>")

    parts.append("            </nav>")
    return "\n".join(parts) + "\n\n"


def render_cross_strip(links):
    """The free cross-resource strip - resource unification Phase 2.

    The component is .resource-cross in css/main.css, shared with the
    flashcards pages since Phase 1. Free links only: the paid services sit
    in .resource-services below, so a paid button never lands in a row a
    student reads as free (PH07-058).
    """
    buttons = "\n".join(
        f'            <a href="{href}" class="button">{label}</a>'
        for href, label in links
    )
    return f"""          <section class="resource-cross">
{buttons}
          </section>"""


def render_services(text, actions):
    """The paid-services panel, .resource-services in css/main.css."""
    buttons = "\n".join(
        f'            <a href="{href}" class="button{cls}">{label}</a>'
        for href, cls, label in actions
    )
    return f"""          <section class="resource-services">
            <p>{text}</p>
{buttons}
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
    url = f"{SITE}/practice-questions/{board_dir}/"

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

    body = f"""      <main id="main" class="practice-questions-page">
        <div class="container">
          <nav class="breadcrumb" aria-label="Breadcrumb">
            <a href="/">Home</a>
            <span class="separator">&rsaquo;</span>
            <a href="/practice-questions/">Practice Questions</a>
            <span class="separator">&rsaquo;</span>
            <span>{name}</span>
          </nav>

          <section class="resource-hero">
            <h1>{name} Practice Questions</h1>
            <p class="resource-intro">
              Free exam-style multiple-choice questions covering
              {blurb.lower()}, written to the style and difficulty of the real
              {label} papers. Every question carries a full worked answer.
            </p>
            <p class="resource-stats">
              {count} questions &middot; {len(topics)} {topic_word} &middot; free, no sign-up
            </p>
          </section>

          <h2>Available Topics</h2>
          <p class="pq-note">Click any unit below to see its topics.</p>

          <ul class="topic-list">
{units}
          </ul>

{render_cross_strip(
    # D45 line: the notes and past-papers buttons restyle links this page
    # already carried; the flashcards and question-finder buttons are new
    # edges into the NEW sections only, which Phases 1-2 may add freely.
    [
        (f"/revision-notes/{board_dir}/",
         f"Read the {GROUP_LABELS[board_dir]} notes"),
        (FLASHCARDS_URLS[board_dir], "Revise with the flashcards"),
        (QB_URLS[board_dir], f"Search {label} past paper questions"),
        (papers_href, papers_label),
    ],
)}
{render_services(
    "<strong>Getting these wrong?</strong> Work through the topic with an expert "
    "tutor, or send an essay for detailed examiner-style marking.",
    [
        ("/marking.html", " alt", "Get Your Essays Marked"),
        ("/tutoring.html", "", "Book a Free Intro Call"),
    ],
)}
        </div>
      </main>"""

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
                "publisher": page_shell_mod.ORGANISATION_REF,
            },
            4,
        ),
        breadcrumb=breadcrumb_jsonld(
            [
                ("Home", "/"),
                ("Practice Questions", "/practice-questions/"),
                (name, None),
            ]
        ),
        body=body,
        scripts=("/js/components/quiz.js",),
        head_extra=NOSCRIPT_ACCORDION,
    )


def render_hub(by_board):
    total = sum(len(t["questions"]) for ts in by_board.values() for t in ts)
    topic_count = sum(len(ts) for ts in by_board.values())
    topic_word = "topic" if topic_count == 1 else "topics"
    url = f"{SITE}/practice-questions/"

    # "Edexcel and AQA", not "AQA and Edexcel": boards.json's group order is
    # the display order everywhere else on the page, and the intro already
    # names Edexcel first - resource unification Phase 2.
    title = (
        "A-Level Economics Practice Questions — Edexcel and AQA "
        "| Economics Academy"
    )
    desc = (
        f"Free A-Level Economics multiple-choice practice questions for Edexcel "
        f"and AQA. {total} questions across {topic_count} {topic_word}, each with a "
        f"full worked answer."
    )[:164]

    sections = []
    for heading, groups in HUB_SECTIONS:
        rows = []
        for group_name, dirs in groups:
            live = [d for d in dirs if by_board.get(d)]
            if not live:
                continue
            cards = []
            for d in live:
                n = sum(len(t["questions"]) for t in by_board[d])
                topics_n = len(by_board[d])
                # The card heading is an h4, not the h3 the flashcards hub
                # uses, because the year-group label above it is already an
                # h3 - the shared .resource-card rules cover both levels.
                cards.append(
                    f"""                <article class="resource-card">
                  <h4>
                    <a href="/practice-questions/{d}/"
                      >{HUB_LABELS[d]}</a
                    >
                  </h4>
                  <p class="resource-card-meta">
                    {topics_n} {'topic' if topics_n == 1 else 'topics'} &middot; {n} questions
                  </p>
                </article>"""
                )
            rows.append(
                f"""            <div class="pq-board-group">
              <h3>{group_name}</h3>
              <div class="resource-cards">
{chr(10).join(cards)}
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

    body = f"""      <main id="main" class="practice-questions-page">
        <div class="container">
          <nav class="breadcrumb" aria-label="Breadcrumb">
            <a href="/">Home</a>
            <span class="separator">&rsaquo;</span>
            <span>Practice Questions</span>
          </nav>

          <section class="resource-hero">
            <h1>Free A-Level Economics Practice Questions</h1>
            <p class="resource-intro">
              Exam-style multiple-choice questions for
              <strong>Edexcel</strong> and <strong>AQA</strong>, written to the
              style and difficulty of the real papers. Answer one at a time for
              instant feedback, then read a full worked answer that explains the
              correct option and names the mistake behind each wrong one.
            </p>
            <p class="resource-stats">
              {total} questions &middot; {topic_count} {topic_word} &middot; free, no sign-up
            </p>
          </section>

{chr(10).join(sections)}

{render_cross_strip(
    # D45 line: the revision-notes button restyles a link this page already
    # carried; the flashcards and question-finder buttons are new edges into
    # the NEW sections only, which Phases 1-2 may add freely.
    [
        ("/revision-notes/", "Browse the revision notes"),
        ("/flashcards/", "Revise with the flashcards"),
        ("/past-paper-questions/", "Search real past paper questions"),
    ],
)}
{render_services(
    "<strong>Questions show you the gaps &mdash; essays are where the marks are.</strong> "
    "Send yours for examiner-style marking, or work through the tricky topics "
    "with a specialist tutor.",
    [
        ("/marking.html", " alt", "Get Your Essays Marked"),
        ("/tutoring.html", "", "Book a Free Intro Call"),
    ],
)}
        </div>
      </main>"""

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
                # hasPart names each board index, as the revision-notes hub
                # does for its theme pages and the flashcards hub for its
                # decks - the winner's pattern (resource unification Phase 2).
                # Names match each board page's own CollectionPage name.
                "hasPart": [
                    {
                        "@type": "WebPage",
                        "name": f"{n} practice questions",
                        "url": f"{SITE}/practice-questions/{d}/",
                    }
                    for d, n, _ in BOARDS
                    if by_board.get(d)
                ],
                "publisher": page_shell_mod.ORGANISATION_REF,
            },
            4,
        ),
        breadcrumb=breadcrumb_jsonld([("Home", "/"), ("Practice Questions", None)]),
        body=body,
        scripts=("/js/components/quiz.js",),
    )


def spec_key(spec):
    return tuple(int(part) for part in spec.split("."))


# ------------------------------------------------------------------ sitemap


def update_sitemap(topics):
    """UNUSED. scripts/build_sitemap.py owns the sitemap now: it enumerates pages from the filesystem and takes lastmod from git, so a generator stamping today's date into its own block would undo that."""
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
    parser.add_argument(
        "--check",
        action="store_true",
        help="validate the INPUTS and write nothing. This does not check that committed output is current - use scripts/verify_generated.py for that",
    )
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

    # Siblings are built from EVERY set on disk, not from `topics`, so a
    # partial run (`build_questions.py aqa-a2-micro/1-3-2.json`) still emits
    # the same related-topics list a full run would. Without this a partial
    # rebuild would silently drop links to sets it was not asked to write.
    all_topics, _ = load(sorted(DATA_DIR.glob("*/*.json")))
    by_unit = {}
    for t in all_topics:
        by_unit.setdefault((t["boardDir"], unit_of(t["spec"])), []).append(t)
    pastpapers = load_pastpaper_topics()

    written = []
    for topic in topics:
        out = OUT_DIR / topic["boardDir"] / f"{topic['slug']}.html"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(
            render_page(
                topic,
                siblings_for(topic, by_unit),
                pastpapers.get(page_url(topic)),
            ),
            encoding="utf-8",
        )
        written.append(out)
        print(f"wrote {out.relative_to(ROOT)} ({len(topic['questions'])} questions)")

    # The hub and the board indexes list everything, so they can only be
    # rebuilt from a full run. A partial run leaves them as they were.
    if args.sources:
        # Wave 2 Phase 7. This generator is the one that never ran Prettier,
        # so there is nothing to sequence after - but the partial-build path
        # writes pages too, and a page written without the header would be a
        # page with no navigation.
        print(f"baked the header and footer into "
              f"{page_shell_mod.bake_files(written)} page(s)")
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
        written.append(out)
        print(f"wrote {out.relative_to(ROOT)} ({len(board_topics)} topics)")

    hub = OUT_DIR / "index.html"
    hub.write_text(render_hub(by_board), encoding="utf-8")
    written.append(hub)
    print(f"wrote {hub.relative_to(ROOT)}")

    # Wave 2 Phase 7.
    print(f"baked the header and footer into "
          f"{page_shell_mod.bake_files(written)} page(s)")

    if args.sitemap:
        print("--sitemap is retired; run scripts/build_sitemap.py instead")

    print(f"\n{len(topics)} set(s), {total} questions")
    return 0


if __name__ == "__main__":
    sys.exit(main())

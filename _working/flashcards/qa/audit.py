#!/usr/bin/env python3
"""Audit flashcard card text for the four QA issues in this pass.

    python3 _working/flashcards/qa/audit.py            # summary counts
    python3 _working/flashcards/qa/audit.py --issue A  # full list for one
    python3 _working/flashcards/qa/audit.py --issue B --show

Reads the hand-authored sources in flashcards-data/ (the source of truth -
flashcards/data/*.json is generated from them). Issues:

  A  merged points on one line - several definitions, points or calculation
     steps sharing a single <p>/<li> that should be separate lines.
  B  exam board references in visible card text ("Edexcel", "AQA", "the
     specification", "the spec"). Board metadata is not card text and is
     never touched.
  C  cards testing more than one revision area, so the front cannot be
     answered with a single focus. Heuristic - every hit is read by hand.
  D  long inline comma/semicolon lists that should be bullets, capped at six.
"""

import argparse
import collections
import glob
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[3]

BLOCK = re.compile(r"<(p|li)>(.*?)</\1>", re.S)
TAG = re.compile(r"<[^>]+>")

# B: word-boundary so "specialisation" and specCode metadata never match.
BOARD = re.compile(r"\b(edexcel|aqa|ocr|specification|specifications|spec|"
                   r"exam board|the board)\b", re.I)

# A1: "<strong>Term</strong> - definition", twice or more in one block.
TERM_DASH = re.compile(r"<strong>[^<]+</strong>\s*(?:—|–|:)\s*")
# A2: a sentence after the first that opens with a bolded lead-in.
MID_STRONG = re.compile(r"(?<=[.;:!?])\s+<strong>")
# A3: two or more worked arithmetic steps sharing a block.
CALC_STEP = re.compile(r"=\s*(?:<strong>)?[-−£$]?\d")

VERBS = (r"define|defin(?:e|ing)|explain|evaluate|state|list|show|calculate|"
         r"describe|distinguish|compare|contrast|assess|analyse|outline|give|"
         r"name|draw|identify")
# C: two tasks joined, or a second revision area bolted on with "and".
C_PATTERNS = [
    re.compile(r",\s+and\s+(?:the|its|their|how|why|what|when)\b", re.I),
    re.compile(r"\b(?:%s)\b.{0,80}?\band\b.{0,40}?\b(?:%s)\b" % (VERBS, VERBS),
               re.I),
    re.compile(r"\band\s+(?:the\s+)?significance\s+of\b", re.I),
    re.compile(r"\band\s+(?:the\s+)?(?:effects?|impacts?|causes?|role)\s+of\b.*"
               r"\band\b", re.I),
]


def blocks(html):
    """Every <p>/<li> body in a card face, markup intact."""
    return [m.group(2) for m in BLOCK.finditer(html)]


def plain(html):
    return re.sub(r"\s+", " ", TAG.sub("", html)).strip()


def list_runs(text):
    """Genuine enumerations of four or more parallel items in one sentence.

    Splitting a sentence on commas counts clauses, not list items, which
    flags ordinary prose. So a run only counts when four or more CONSECUTIVE
    segments are short and parallel, and the run is classified:

      substantive - items average more than three words, i.e. each carries a
                    revision point (causes, impacts, evaluation points).
                    These are the ones Issue D asks to bullet.
      atomic      - a bare noun list ("land, labour, capital, enterprise")
                    sitting inside a sentence. Bulleting these would break
                    the sentence, so they are reported separately.
    """
    runs = []
    for sentence in re.split(r"(?<=[.!?])\s+", text):
        for sep in (";", ","):
            parts = [p.strip() for p in re.split(re.escape(sep), sentence)
                     if p.strip()]
            if len(parts) < 4:
                continue
            best = []
            run = []
            for part in parts:
                if len(part.split()) <= 14:
                    run.append(part)
                    if len(run) > len(best):
                        best = list(run)
                else:
                    run = []
            if len(best) < 4:
                continue
            words = sum(len(p.split()) for p in best) / len(best)
            kind = "substantive" if words > 3 else "atomic"
            runs.append((sep, len(best), kind, sentence))
            break
    return runs


def audit_card(card):
    """Return {issue: [detail, ...]} for one card."""
    found = collections.defaultdict(list)
    for side in ("front", "back"):
        html = card[side]

        for hit in BOARD.finditer(plain(html)):
            found["B"].append(f"{side}: '{hit.group(0)}'")

        for body in blocks(html):
            text = plain(body)
            if len(TERM_DASH.findall(body)) >= 2:
                found["A"].append(f"{side}: {len(TERM_DASH.findall(body))} "
                                  f"term-definitions in one block: {text[:90]}")
            elif MID_STRONG.search(body) and len(text) > 120:
                found["A"].append(f"{side}: bolded lead-in mid-block: "
                                  f"{text[:90]}")
            elif len(CALC_STEP.findall(body)) >= 2 and ";" in text:
                found["A"].append(f"{side}: {len(CALC_STEP.findall(body))} "
                                  f"calculation steps in one block: {text[:90]}")

            for sep, count, kind, sentence in list_runs(text):
                key = "D" if kind == "substantive" else "D-atomic"
                found[key].append(f"{side}: {count} items ('{sep}'): "
                                  f"{sentence[:110]}")

    front = plain(card["front"])
    for pattern in C_PATTERNS:
        if pattern.search(front):
            found["C"].append(f"front: {front}")
            break
    return found


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--issue", choices=["A", "B", "C", "D", "D-atomic"])
    ap.add_argument("--show", action="store_true",
                    help="print every detail line, not just ids")
    ap.add_argument("--deck")
    args = ap.parse_args()

    totals = collections.Counter()
    instances = collections.Counter()
    per_deck = collections.defaultdict(collections.Counter)
    listing = collections.defaultdict(list)
    cards = 0

    for path in sorted(glob.glob(str(ROOT / "flashcards-data" / "*" /
                                     "*.json"))):
        deck = json.loads(pathlib.Path(path).read_text(encoding="utf-8"))
        if args.deck and deck["deckId"] != args.deck:
            continue
        for card in deck["cards"]:
            cards += 1
            found = audit_card(card)
            for issue, details in found.items():
                totals[issue] += 1
                instances[issue] += len(details)
                per_deck[deck["deckId"]][issue] += 1
                listing[issue].append((deck["deckId"], card["id"], details))

    if args.issue:
        rows = listing[args.issue]
        for deck, cid, details in rows:
            print(f"{deck:20} {cid}")
            if args.show:
                for detail in details:
                    print(f"    {detail}")
        print(f"\nissue {args.issue}: {len(rows)} cards")
        return

    print(f"{cards} cards audited\n")
    print(f"{'issue':10} {'cards':>6} {'instances':>10}")
    for issue in ["A", "B", "C", "D", "D-atomic"]:
        print(f"{issue:10} {totals[issue]:>6} {instances[issue]:>10}")
    print(f"\n{'deck':22} " + " ".join(f"{i:>5}" for i in "ABCD"))
    for deck in sorted(per_deck):
        counts = per_deck[deck]
        print(f"{deck:22} " + " ".join(f"{counts[i]:>5}" for i in "ABCD"))


if __name__ == "__main__":
    sys.exit(main())

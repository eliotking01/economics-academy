#!/usr/bin/env python3
"""Prove boards-data/boards.json reproduces the four hardcoded board structures.

    python3 scripts/verify_boards.py

WHY THIS EXISTS
---------------
PH09-022: every generator that needs to know what a board is defines it again,
in a different shape, and no two agree on the identifier. `build_glossary.py`
even carries a field called `taxonomy` whose only job is to bridge its own
board key to another generator's - the need for a canonical identity is
already recognised in the codebase, just solved privately inside one file.

PH09's migration order starts: **add boards.json, change nothing, and add a
test asserting it reproduces all four existing structures exactly.** This is
that test. Nothing imports boards.json yet. When a generator is repointed at
it, this is what says the swap changed no output before the swap is made.

The direction matters: this compares the RECORD against the CODE, and the code
wins. boards.json is a transcription, so a disagreement means the
transcription is wrong, not that the generator is.

WHAT MEASURING IT TURNED UP
---------------------------
PH09's design made `slugs` a map because one board is spelled three ways across
three families and all three are correct - the URLs are frozen and GitHub Pages
issues no 301. Measured on 2026-08-11, **the same is true of group names, which
PH09 did not anticipate.** Theme 2 reaches published output as three different
strings:

    The UK Economy — Performance and Policies    taxonomy.json, notes hub <h1>
    The UK Economy - Performance and Policies    the flashcards decks
    The UK Economy                               practice-questions

A single canonical `name` would have silently rewritten visible text on a whole
page family, which needs explicit approval and a `Text-Change:` trailer, every
time. So names are recorded per consumer, exactly as slugs are, and this check
compares each against the consumer that uses it.

WHY THERE IS A SECOND COPY OF THE RECORD IN THIS FILE
-----------------------------------------------------
Wave 3.2 points the generators at boards.json. From that moment the four
comparisons below are circular for any generator that has been swapped: they
ask whether boards.json agrees with a structure boards.json just produced, and
the answer is yes for every value, including a wrong one. A check that cannot
fail protects nothing, and it protects nothing while still printing green.

So `PINNED` restates all 82 leaves of the record as an independent literal, in
a deliberately different shape - a flat dotted-path map against the file's
nested objects and arrays - and check 0 compares the two. This is
`verify_page_shell.SCRIPT_TAIL` and `build_past_paper_taxonomy.EXPECTED`, the
same pattern for the same reason: changing a board name or slug now has to
change two files in the same commit, so it cannot happen by accident. Do not
"remove the duplication" by deriving one from the other.

It was seeded from boards.json on 2026-08-12, when the 28 code comparisons
below were green on all four structures, so it is anchored to what the
generators said before any of them was touched. `--show` reprints it.

Standard library only.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
BOARDS_JSON = ROOT / "boards-data" / "boards.json"

# Every leaf of boards-data/boards.json, restated. See the docstring: this is
# the independent copy that keeps check 0 meaningful once the generators read
# the file instead of declaring their own structures. Keys are dotted paths;
# `_`-prefixed keys in the record are commentary and are not pinned.
#
# A slug is a live URL and GitHub Pages issues no 301. A name is visible text.
# Changing either here without changing boards-data/boards.json - or the other
# way round - is meant to fail.
PINNED = {
    "edexcel-a.names.short": "Edexcel",
    "edexcel-a.names.display": "Edexcel A",
    "edexcel-a.names.long": "Edexcel A-Level Economics A",
    "edexcel-a.names.qualification": "A Level Economics A (9EC0)",
    "edexcel-a.slugs.pastPapers": "edexcel",
    "edexcel-a.slugs.questionBank": "edexcel",
    "edexcel-a.slugs.taxonomy": "edexcel",
    "edexcel-a.slugs.glossary": "edexcel-a",
    "edexcel-a.slugs.flashcards": "edexcel-a",
    "edexcel-a.slugs.dataDir": "edexcel-a",
    "edexcel-a.papersUrl": "/past-papers/edexcel/",
    "edexcel-a.notesUrl": "/revision-notes/",
    "edexcel-a.specCodesAreReal": True,
    "edexcel-a.expectedTopics": 87,
    "edexcel-a.groups.0.notesDir": "edexcel-theme-1",
    "edexcel-a.groups.0.taxonomySlug": "theme-1",
    "edexcel-a.groups.0.flashcardsSlug": "theme-1",
    "edexcel-a.groups.0.label": "Theme 1",
    "edexcel-a.groups.0.names.taxonomy":
        "Introduction to Markets and Market Failure",
    "edexcel-a.groups.0.names.flashcards":
        "Introduction to Markets and Market Failure",
    "edexcel-a.groups.0.names.practiceQuestions":
        "Introduction to Markets and Market Failure",
    "edexcel-a.groups.0.names.practiceQuestionsLabel": "Edexcel Theme 1",
    "edexcel-a.groups.0.names.practiceQuestionsButton":
        "Theme 1: Introduction to Markets and Market Failure",
    "edexcel-a.groups.1.notesDir": "edexcel-theme-2",
    "edexcel-a.groups.1.taxonomySlug": "theme-2",
    "edexcel-a.groups.1.flashcardsSlug": "theme-2",
    "edexcel-a.groups.1.label": "Theme 2",
    # Theme 2 is the em-dash/hyphen/short-form case the docstring describes.
    # These three differ on purpose and must not be collapsed.
    "edexcel-a.groups.1.names.taxonomy":
        "The UK Economy — Performance and Policies",
    "edexcel-a.groups.1.names.flashcards":
        "The UK Economy - Performance and Policies",
    "edexcel-a.groups.1.names.practiceQuestions":
        "The UK Economy - Performance and Policies",
    "edexcel-a.groups.1.names.practiceQuestionsLabel": "Edexcel Theme 2",
    "edexcel-a.groups.1.names.practiceQuestionsButton":
        "Theme 2: The UK Economy",
    "edexcel-a.groups.2.notesDir": "edexcel-theme-3",
    "edexcel-a.groups.2.taxonomySlug": "theme-3",
    "edexcel-a.groups.2.flashcardsSlug": "theme-3",
    "edexcel-a.groups.2.label": "Theme 3",
    "edexcel-a.groups.2.names.taxonomy":
        "Business Behaviour and the Labour Market",
    "edexcel-a.groups.2.names.flashcards":
        "Business Behaviour and the Labour Market",
    "edexcel-a.groups.2.names.practiceQuestions":
        "Business Behaviour and the Labour Market",
    "edexcel-a.groups.2.names.practiceQuestionsLabel": "Edexcel Theme 3",
    "edexcel-a.groups.2.names.practiceQuestionsButton":
        "Theme 3: Business Behaviour and the Labour Market",
    "edexcel-a.groups.3.notesDir": "edexcel-theme-4",
    "edexcel-a.groups.3.taxonomySlug": "theme-4",
    "edexcel-a.groups.3.flashcardsSlug": "theme-4",
    "edexcel-a.groups.3.label": "Theme 4",
    "edexcel-a.groups.3.names.taxonomy": "A Global Perspective",
    "edexcel-a.groups.3.names.flashcards": "A Global Perspective",
    "edexcel-a.groups.3.names.practiceQuestions": "A Global Perspective",
    "edexcel-a.groups.3.names.practiceQuestionsLabel": "Edexcel Theme 4",
    "edexcel-a.groups.3.names.practiceQuestionsButton":
        "Theme 4: A Global Perspective",
    "aqa.names.short": "AQA",
    "aqa.names.display": "AQA",
    "aqa.names.long": "AQA A-Level Economics",
    "aqa.names.qualification": "A-level Economics (7136)",
    "aqa.slugs.pastPapers": "aqa",
    "aqa.slugs.questionBank": "aqa",
    "aqa.slugs.taxonomy": "aqa",
    "aqa.slugs.glossary": "aqa",
    "aqa.slugs.flashcards": "aqa",
    "aqa.slugs.dataDir": "aqa",
    "aqa.papersUrl": "/past-papers/aqa/",
    "aqa.notesUrl": "/revision-notes/",
    "aqa.specCodesAreReal": False,
    "aqa.expectedTopics": 79,
    "aqa.groups.0.notesDir": "aqa-a2-micro",
    "aqa.groups.0.taxonomySlug": "microeconomics",
    "aqa.groups.0.flashcardsSlug": "micro",
    "aqa.groups.0.label": "Microeconomics",
    "aqa.groups.0.names.taxonomy":
        "Individuals, Firms, Markets and Market Failure",
    "aqa.groups.0.names.flashcards":
        "Individuals, Firms, Markets and Market Failure",
    "aqa.groups.0.names.practiceQuestions":
        "Individuals, Firms, Markets and Market Failure",
    "aqa.groups.0.names.practiceQuestionsLabel": "AQA Microeconomics",
    "aqa.groups.0.names.practiceQuestionsButton":
        "Micro: Individuals, Firms, Markets and Market Failure",
    "aqa.groups.1.notesDir": "aqa-a2-macro",
    "aqa.groups.1.taxonomySlug": "macroeconomics",
    "aqa.groups.1.flashcardsSlug": "macro",
    "aqa.groups.1.label": "Macroeconomics",
    "aqa.groups.1.names.taxonomy": "The National and International Economy",
    "aqa.groups.1.names.flashcards": "The National and International Economy",
    "aqa.groups.1.names.practiceQuestions":
        "The National and International Economy",
    "aqa.groups.1.names.practiceQuestionsLabel": "AQA Macroeconomics",
    "aqa.groups.1.names.practiceQuestionsButton":
        "Macro: The National and International Economy",
}


def flatten(obj, prefix: str = "") -> dict:
    """Every leaf of the record as a dotted path, commentary keys dropped.

    Deliberately flat, where boards.json is nested: the pinned copy has to be
    a restatement rather than the same shape twice, or a wrong value could be
    pasted into both without looking wrong in either.
    """
    out: dict = {}
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k.startswith("_"):
                continue
            out.update(flatten(v, f"{prefix}.{k}" if prefix else k))
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            out.update(flatten(v, f"{prefix}.{i}"))
    else:
        out[prefix] = obj
    return out


def load_module(name: str):
    """Import a generator for its constants without running it.

    Every one of these guards its work behind `if __name__ == "__main__"`, so
    importing is side-effect free. Checked before relying on it.
    """
    path = ROOT / "scripts" / f"{name}.py"
    spec = importlib.util.spec_from_file_location(f"_boards_{name}", path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


class Check:
    def __init__(self):
        self.bad: list[str] = []

    def eq(self, label: str, record, code, right: str = "the code") -> None:
        if record == code:
            print(f"  ok    {label}")
        else:
            print(f"  FAIL  {label}")
            print(f"          boards.json: {record!r}")
            print(f"          {right:<11}: {code!r}")
            self.bad.append(label)


def show(flat: dict) -> None:
    """Reprint PINNED for reseeding, the verify_page_shell.py --show pattern."""
    print("PINNED = {")
    for k, v in flat.items():
        print(f"    {k!r}: {v!r},")
    print("}")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--show", action="store_true",
                    help="reprint PINNED from boards.json and exit")
    args = ap.parse_args()

    data = json.loads(BOARDS_JSON.read_text(encoding="utf-8"))["boards"]
    flat = flatten(data)
    if args.show:
        show(flat)
        return 0

    c = Check()

    # ------------------------------------------------- check 0: the pinned copy
    #
    # The only comparison here that stays meaningful after a generator reads
    # boards.json. Everything below it compares the record against code that
    # may now be deriving itself from the record.
    print("=== the pinned restatement in this file ===")
    missing = sorted(set(PINNED) - set(flat))
    extra = sorted(set(flat) - set(PINNED))
    for k in missing:
        c.bad.append(f"pinned but no longer in boards.json: {k}")
        print(f"  FAIL  pinned but no longer in boards.json: {k}")
    for k in extra:
        c.bad.append(f"in boards.json but not pinned: {k}")
        print(f"  FAIL  in boards.json but not pinned: {k}")
    if not missing and not extra:
        print(f"  ok    all {len(PINNED)} leaves are pinned, and only those")
        for k in PINNED:
            c.eq(f"pinned {k}", flat[k], PINNED[k], right="PINNED")

    print(f"\n{BOARDS_JSON.relative_to(ROOT)} vs the four hardcoded structures\n")

    # ---------------------------------------------------- build_glossary.py
    print("=== build_glossary.py BOARDS ===")
    gl = load_module("build_glossary").BOARDS
    c.eq("glossary board keys",
         sorted(b["slugs"]["glossary"] for b in data.values()), sorted(gl))
    for key, rec in sorted(data.items()):
        g = gl.get(rec["slugs"]["glossary"])
        if g is None:
            c.bad.append(f"glossary has no board {key}")
            continue
        c.eq(f"{key}: glossary slug", rec["slugs"]["glossary"], g["slug"])
        c.eq(f"{key}: glossary name", rec["names"]["display"], g["name"])
        c.eq(f"{key}: glossary long", rec["names"]["long"], g["long"])
        c.eq(f"{key}: glossary taxonomy bridge",
             rec["slugs"]["taxonomy"], g["taxonomy"])
        c.eq(f"{key}: notesUrl", rec["notesUrl"], g["notesUrl"])

    # -------------------------------------------- build_past_paper_taxonomy.py
    print("\n=== build_past_paper_taxonomy.py BOARDS + EXPECTED ===")
    tx = load_module("build_past_paper_taxonomy")
    by_slug = {b["board"]: b for b in tx.BOARDS}
    c.eq("taxonomy board slugs",
         sorted(b["slugs"]["taxonomy"] for b in data.values()), sorted(by_slug))
    for key, rec in sorted(data.items()):
        t = by_slug.get(rec["slugs"]["taxonomy"])
        if t is None:
            c.bad.append(f"taxonomy has no board {key}")
            continue
        c.eq(f"{key}: taxonomy short name", rec["names"]["short"], t["name"])
        c.eq(f"{key}: qualification",
             rec["names"]["qualification"], t["qualification"])
        c.eq(f"{key}: papersUrl", rec["papersUrl"], t["papersUrl"])
        c.eq(f"{key}: taxonomy groups",
             [(g["notesDir"], g["taxonomySlug"], g["label"],
               g["names"]["taxonomy"]) for g in rec["groups"]],
             [tuple(g) for g in t["groups"]])
    c.eq("EXPECTED topic counts",
         {b["slugs"]["taxonomy"]: b["expectedTopics"] for b in data.values()},
         tx.EXPECTED)

    # --------------------------------------------------- build_flashcards.py
    print("\n=== build_flashcards.py NOTES_DIRS ===")
    fc = load_module("build_flashcards").NOTES_DIRS
    c.eq("flashcards (board, theme) -> notes dir",
         {(b["slugs"]["flashcards"], g["flashcardsSlug"]): g["notesDir"]
          for b in data.values() for g in b["groups"]},
         fc)

    # ---------------------------------------------------- build_questions.py
    print("\n=== build_questions.py: five structures ===")
    q = load_module("build_questions")
    c.eq("PAST_PAPERS",
         {b["slugs"]["pastPapers"]:
          (b["papersUrl"], f"{b['names']['short']} Past Papers")
          for b in data.values()},
         q.PAST_PAPERS)
    c.eq("BOARD_LABELS",
         {b["slugs"]["pastPapers"]: b["names"]["short"] for b in data.values()},
         q.BOARD_LABELS)
    # BOARDS is display order, and the order is the one templates/header.html
    # uses. It is Edexcel themes 1-4 then AQA micro, macro - which is the order
    # boards.json lists them in, so the record carries it rather than a
    # separate index.
    c.eq("BOARDS (display order, label, blurb)",
         [(g["notesDir"], g["names"]["practiceQuestionsLabel"],
           g["names"]["practiceQuestions"])
          for b in data.values() for g in b["groups"]],
         [tuple(x) for x in q.BOARDS])
    c.eq("BOARD_ORDER",
         {g["notesDir"]: i for i, g in
          enumerate(g for b in data.values() for g in b["groups"])},
         q.BOARD_ORDER)
    c.eq("HUB_LABELS",
         {g["notesDir"]: g["names"]["practiceQuestionsButton"]
          for b in data.values() for g in b["groups"]},
         q.HUB_LABELS)
    c.eq("BOARD_BLURB",
         {g["notesDir"]: g["names"]["practiceQuestions"]
          for b in data.values() for g in b["groups"]},
         q.BOARD_BLURB)

    print()
    sys.stdout.flush()
    if c.bad:
        print(f"FAIL: {len(c.bad)} disagreement(s):", file=sys.stderr)
        for b in c.bad:
            print(f"  {b}", file=sys.stderr)
        if any(b.startswith("pinned") or "pinned" in b for b in c.bad):
            print("\nboards.json and this file's PINNED copy disagree. That is "
                  "the guard working: a board name or slug is meant to be "
                  "changed in both, in one commit, on purpose. If the change "
                  "was intended, update PINNED - `--show` reprints it - and "
                  "say in the commit message what moved and why. If it was "
                  "not intended, revert boards.json.", file=sys.stderr)
        print("\nboards.json is a transcription of what the generators already "
              "say, so a disagreement with the code means the transcription is "
              "wrong. Fix boards.json, not the generator - changing a slug "
              "changes a live URL and changing a name changes visible text.",
              file=sys.stderr)
        return 1
    print(f"boards.json matches its {len(PINNED)}-leaf pinned copy and "
          f"reproduces all four hardcoded structures exactly")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

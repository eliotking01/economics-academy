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

    def eq(self, label: str, record, code) -> None:
        if record == code:
            print(f"  ok    {label}")
        else:
            print(f"  FAIL  {label}")
            print(f"          boards.json: {record!r}")
            print(f"          the code   : {code!r}")
            self.bad.append(label)


def main() -> int:
    argparse.ArgumentParser(description=__doc__.splitlines()[0]).parse_args()

    data = json.loads(BOARDS_JSON.read_text(encoding="utf-8"))["boards"]
    c = Check()

    print(f"{BOARDS_JSON.relative_to(ROOT)} vs the four hardcoded structures\n")

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
        print(f"FAIL: boards.json disagrees with the code in "
              f"{len(c.bad)} place(s):", file=sys.stderr)
        for b in c.bad:
            print(f"  {b}", file=sys.stderr)
        print("\nboards.json is a transcription of what the generators already "
              "say, so a disagreement means the transcription is wrong. Fix "
              "boards.json, not the generator - changing a slug changes a live "
              "URL and changing a name changes visible text.", file=sys.stderr)
        return 1
    print("boards.json reproduces all four hardcoded structures exactly")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

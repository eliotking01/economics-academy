#!/usr/bin/env python3
"""Read boards-data/boards.json. The one place a generator learns what a board is.

    import board_data
    for key, board in board_data.load("flashcards").items(): ...
    for key, board, group in board_data.groups("practiceQuestions"): ...

WHY THIS EXISTS
---------------
PH09-022 and PH01-012: every generator that needed to know what a board is
defined it again, in a different shape, and no two agreed on the identifier.
build_glossary.py even carried a field called `taxonomy` whose only job was to
bridge its own board key to another generator's. Wave 3.1 wrote the record;
Wave 3.2 is the generators reading it, one commit each, with each generator's
output proved byte-unmoved.

WHAT THIS MODULE DELIBERATELY DOES NOT DO
-----------------------------------------
**It does not return one canonical shape, and it must never grow one.** Each
generator keeps building its own structure from the record, because the shapes
differ for real reasons that are recorded rather than tidied:

  - One board is spelled three ways across three families, and all three are
    correct. `slugs` is a map because the URLs are frozen and GitHub Pages
    issues no 301.
  - The same is true of GROUP NAMES. Theme 2 reaches published output as three
    different strings - em dash in taxonomy.json and the notes hub <h1>, hyphen
    in the flashcards decks, the short form in practice-questions. A helper
    here returning "the name of a group" would be the collapse DO-NOT-BREAK
    names as the single most likely way to get this wave wrong.

So the accessors below hand back the record and let the caller pick the field
it needs by name. A caller asking for `names.flashcards` is stating which
consumer it is, which is the whole point of the file.

ORDER IS PART OF THE RECORD. `json.loads` preserves object order, so
`load(family)` yields Edexcel A, AQA, then Edexcel B, and `groups(family)`
yields Themes 1-4, micro, macro, then B's Themes 1-4 (each filtered to the
boards with that family) - which is the display order build_questions.BOARDS uses and the
order templates/header.html puts the nav in. `_ordering_is_significant` asserts
it rather than trusting it.

`_`-prefixed keys in the record are commentary for a human reader and are left
in place; every caller accesses fields by name, so they are never iterated.

EVERY CALLER NAMES ITS FAMILY
-----------------------------
Each board's record carries a `features` list: which of FEATURES it has.
Edexcel A and AQA have all five; Edexcel B had notes alone from 2026-09-26
(D66, when this was a `notesOnly` flag) and gains the rest one family at a
time under D67, each added to its list only when complete for all four
themes. `load(family)` and `groups(family)` return ONLY the boards with that
family, because a board reaching a generator it has nothing for would mint
pages it does not have. There is deliberately no default: a new caller says
which family it is, in the call, and that is the whole guard.

`taxonomy` is the one family that is not a feature. It is the shared spine
`taxonomy.json` that the glossary and the past-paper bank read, so a board is
in it when it has either of those (TAXONOMY_READERS). Both readers also filter
taxonomy.json down to their own family, so a board in the taxonomy for its
glossary does not reach the bank, or the other way round.

`has_feature(notes_dir, family)` answers the same question per notes
directory, for the code that walks every notes page and decides what each
one links to (notes_extras' tail, build_search_index's quiz flag).

Standard library only, like everything the workflow runs.
"""

from __future__ import annotations

import copy
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
BOARDS_JSON = ROOT / "boards-data" / "boards.json"

_cache: dict | None = None

# The board keys and group notesDirs this file expects to find, in order.
# Same property as build_past_paper_taxonomy.EXPECTED and bake_templates.EXPECTED:
# adding a board must be a declared change that fails loudly here first, rather
# than a silent short build somewhere downstream. Update it in the same commit
# that adds the board.
EXPECTED_KEYS = ("edexcel-a", "aqa", "edexcel-b")
EXPECTED_NOTES_DIRS = (
    "edexcel-theme-1", "edexcel-theme-2", "edexcel-theme-3", "edexcel-theme-4",
    "aqa-a2-micro", "aqa-a2-macro",
    # Edexcel B (D66): one entry per OPEN theme, added as each theme's hub
    # left notes-data/hubs/drafts/. All four are open.
    "edexcel-b-theme-1", "edexcel-b-theme-2", "edexcel-b-theme-3",
    "edexcel-b-theme-4",
)


# The resource families a board can have, as boards.json spells them. Order
# is display order nowhere; it is only the order the record lists them in.
FEATURES = ("notes", "practiceQuestions", "flashcards", "glossary",
            "pastPaperBank")

# taxonomy.json is built for any board one of these reads it for. It is a
# family a caller can ask for, never a feature a record can list.
TAXONOMY_READERS = ("glossary", "pastPaperBank")
FAMILIES = FEATURES + ("taxonomy",)


def features(board: dict) -> tuple[str, ...]:
    """The families a board record has, the derived taxonomy included."""
    have = tuple(board["features"])
    if any(f in have for f in TAXONOMY_READERS):
        have += ("taxonomy",)
    return have


def load(family: str) -> dict:
    """{board key: record} for the boards that have `family`, in the order
    boards.json lists them. See the module docstring: the caller names the
    family it builds, and gets no board it has nothing to build for.
    """
    _known(family)
    return {k: b for k, b in _load_all().items() if family in features(b)}


def groups(family: str) -> list[tuple[str, dict, dict]]:
    """(board key, board record, group record) for every group of the boards
    that have `family`, in file order."""
    return [(key, board, group)
            for key, board in load(family).items()
            for group in board["groups"]]


def has_feature(notes_dir: str, family: str) -> bool:
    """True if the notes directory's board has `family`."""
    _known(family)
    for _key, board, group in groups("notes"):
        if group["notesDir"] == notes_dir:
            return family in features(board)
    sys.exit(f"board_data: {notes_dir!r} is not a notes directory in "
             f"boards-data/boards.json")


def _known(family: str) -> None:
    if family not in FAMILIES:
        sys.exit(f"board_data: {family!r} is not a family - one of "
                 f"{', '.join(FAMILIES)}")


def _load_all() -> dict:
    """{board key: record} for every board in the file.

    A deep copy every time: a generator that edited the record in place would
    otherwise change what the next generator in verify_generated.py's run sees,
    and the failure would depend on import order.
    """
    global _cache
    if _cache is None:
        try:
            raw = json.loads(BOARDS_JSON.read_text(encoding="utf-8"))
        except FileNotFoundError:
            sys.exit(f"missing {BOARDS_JSON.relative_to(ROOT)} - every "
                     f"generator reads it; is this branch based on main?")
        except json.JSONDecodeError as exc:
            sys.exit(f"{BOARDS_JSON.relative_to(ROOT)} is not valid JSON: {exc}")
        _cache = raw["boards"]
        _ordering_is_significant(_cache)
        _features_are_coherent(_cache)
    return copy.deepcopy(_cache)


def _features_are_coherent(data: dict) -> None:
    """Fail on a features list no generator could honour.

    Every board has notes: nothing else here is a board in this file's sense
    (OCR has past papers and no record, `_pastPapersOnly`). glossary and
    pastPaperBank read taxonomy.json, which build_past_paper_taxonomy.py builds
    from the board's questions-data/ topic records and which links each
    topic's practice page - so neither can be on while practiceQuestions is
    off, or the taxonomy would assert records that do not exist and publish
    links to pages that do not either.
    """
    for key, board in data.items():
        have = board.get("features")
        if not isinstance(have, list) or not have:
            sys.exit(f"boards.json: {key} has no features list - every board "
                     f"names the families it has (see _features)")
        unknown = [f for f in have if f not in FEATURES]
        if unknown:
            sys.exit(f"boards.json: {key} lists {unknown}, which are not "
                     f"features - one of {', '.join(FEATURES)}")
        if len(set(have)) != len(have):
            sys.exit(f"boards.json: {key} lists a feature twice: {have}")
        if "notes" not in have:
            sys.exit(f"boards.json: {key} has no notes. Every board in this "
                     f"file has notes; a past-papers-only board has no record")
        for reader in TAXONOMY_READERS:
            if reader in have and "practiceQuestions" not in have:
                sys.exit(f"boards.json: {key} has {reader} without "
                         f"practiceQuestions. taxonomy.json, which {reader} "
                         f"reads, is built from the questions-data/ topic "
                         f"records - switch practiceQuestions on first")


def _ordering_is_significant(data: dict) -> None:
    """Fail if the record's order has moved, because output depends on it.

    build_questions.BOARD_ORDER is `{notesDir: index}` taken straight from this
    order, and it decides the order boards appear on the practice-questions hub.
    A reordered boards.json would silently reorder a published page, which is
    exactly the class of change this wave promises not to make.
    """
    keys = tuple(data)
    if keys != EXPECTED_KEYS:
        sys.exit(f"boards.json lists {keys}, expected {EXPECTED_KEYS}. Adding "
                 f"or reordering a board changes published output - declare it "
                 f"by updating EXPECTED_KEYS in scripts/board_data.py.")
    dirs = tuple(g["notesDir"] for b in data.values() for g in b["groups"])
    if dirs != EXPECTED_NOTES_DIRS:
        sys.exit(f"boards.json lists groups {dirs}, expected "
                 f"{EXPECTED_NOTES_DIRS}. This order is the display order on "
                 f"the practice-questions hub - declare a change by updating "
                 f"EXPECTED_NOTES_DIRS in scripts/board_data.py.")


if __name__ == "__main__":
    for _key, _board in load("notes").items():
        _names = _board["names"]
        print(f"{_key}: {_names['display']} ({_names['qualification']}), "
              f"{len(_board['groups'])} groups, "
              f"{_board['expectedTopics']} topics; "
              + ", ".join(features(_board)))
        for _group in _board["groups"]:
            print(f"    {_group['notesDir']:<18} {_group['label']}")

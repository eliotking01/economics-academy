#!/usr/bin/env python3
"""Read boards-data/boards.json. The one place a generator learns what a board is.

    import board_data
    for key, board in board_data.load().items(): ...
    for key, board, group in board_data.groups(): ...

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
`load()` yields Edexcel A then AQA, and `groups()` yields Themes 1-4 then
micro, macro - which is the display order build_questions.BOARDS uses and the
order templates/header.html puts the nav in. `_ordering_is_significant` asserts
it rather than trusting it.

`_`-prefixed keys in the record are commentary for a human reader and are left
in place; every caller accesses fields by name, so they are never iterated.

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
EXPECTED_KEYS = ("edexcel-a", "aqa")
EXPECTED_NOTES_DIRS = (
    "edexcel-theme-1", "edexcel-theme-2", "edexcel-theme-3", "edexcel-theme-4",
    "aqa-a2-micro", "aqa-a2-macro",
)


def load() -> dict:
    """{board key: record}, in the order boards.json lists them.

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
    return copy.deepcopy(_cache)


def groups() -> list[tuple[str, dict, dict]]:
    """(board key, board record, group record) for all 6 groups, in file order."""
    return [(key, board, group)
            for key, board in load().items()
            for group in board["groups"]]


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
    for _key, _board in load().items():
        _names = _board["names"]
        print(f"{_key}: {_names['display']} ({_names['qualification']}), "
              f"{len(_board['groups'])} groups, "
              f"{_board['expectedTopics']} topics")
        for _group in _board["groups"]:
            print(f"    {_group['notesDir']:<16} {_group['label']}")

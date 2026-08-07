#!/usr/bin/env python3
"""Apply hand-authored card-text replacements, one field at a time, safely.

    python3 _working/flashcards/qa/apply.py _working/flashcards/qa/edits/batch-02.json

The edits file is a list of objects:

    [{"id": "...", "field": "back", "old": "...", "new": "..."}, ...]

`old` and `new` are the FULL field values. Nothing is generated: every `new`
string is written by hand, exactly as it would have been typed into the file.
CLAUDE.md's rule is that prose must never be *rebuilt* by a script - scripted
paragraph rebuilds have silently destroyed markup in this repo - and this tool
does not rebuild anything. What it adds over a plain editor is proof:

  * `old` must match the card's current value byte for byte, or the run aborts
    with nothing written;
  * after the substitution the file is re-parsed and compared card by card
    against the original, and any change to a card or field that was not named
    in the edits file aborts the run;
  * the file is never re-serialised, so formatting and key order survive.

Fields other than front/back are rejected outright.
"""

import copy
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
DATA = ROOT / "flashcards-data"
ALLOWED = {"front", "back"}


def encode(value):
    """The exact JSON text of a string value, as it appears in the file."""
    return json.dumps(value, ensure_ascii=False)


def main(path):
    edits = json.loads(pathlib.Path(path).read_text(encoding="utf-8"))
    for edit in edits:
        if edit["field"] not in ALLOWED:
            raise SystemExit(f"{edit['id']}: field {edit['field']} not allowed")

    by_deck = {}
    for deck_path in sorted(DATA.glob("*/*.json")):
        text = deck_path.read_text(encoding="utf-8")
        for edit in edits:
            if f'"id": "{edit["id"]}"' in text:
                by_deck.setdefault(deck_path, []).append(edit)

    missing = {e["id"] for e in edits} - {
        e["id"] for group in by_deck.values() for e in group}
    if missing:
        raise SystemExit(f"cards not found: {', '.join(sorted(missing))}")

    for deck_path, group in by_deck.items():
        original = deck_path.read_text(encoding="utf-8")
        before = json.loads(original)
        index = {c["id"]: c for c in before["cards"]}
        text = original

        for edit in group:
            card = index[edit["id"]]
            if card[edit["field"]] != edit["old"]:
                raise SystemExit(
                    f"{edit['id']}: 'old' does not match the file.\n"
                    f"  file: {card[edit['field']][:120]}\n"
                    f"  edit: {edit['old'][:120]}")
            needle = f'"{edit["field"]}": {encode(edit["old"])}'
            if text.count(needle) != 1:
                raise SystemExit(f"{edit['id']}: {edit['field']} value is not "
                                 f"unique in {deck_path.name} "
                                 f"({text.count(needle)} matches)")
            text = text.replace(
                needle, f'"{edit["field"]}": {encode(edit["new"])}', 1)

        after = json.loads(text)
        # Prove only the named fields on the named cards moved.
        probe = copy.deepcopy(after)
        probe_index = {c["id"]: c for c in probe["cards"]}
        for edit in group:
            probe_index[edit["id"]][edit["field"]] = index[edit["id"]][
                edit["field"]]
        if probe != before:
            raise SystemExit(f"{deck_path.name}: refused - something outside "
                             f"the named fields changed")

        deck_path.write_text(text, encoding="utf-8")
        print(f"{deck_path.name}: applied {len(group)} edit(s)")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit(__doc__)
    main(sys.argv[1])

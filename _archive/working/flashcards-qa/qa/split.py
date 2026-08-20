#!/usr/bin/env python3
"""Split one card into two, for Issue C.

    python3 _working/flashcards/qa/split.py _working/flashcards/qa/edits/splits.json

Each entry names the original card, the narrowed front/back it keeps, and the
new card's id plus the fields that differ from the original:

    {"id": "...", "front": "...", "back": "...",
     "new": {"id": "...", "front": "...", "back": "...", "cardType": "...",
             "tags": [...], "difficulty": "...", "source": {...}}}

The new card is built by **copying the original card's raw text** and replacing
named fields in it, rather than re-serialising a dict. That keeps the file's
formatting byte-for-byte consistent - Prettier keeps short arrays inline, which
json.dumps would not reproduce - and guarantees the new card inherits
specCode, topic, subtopic, premium and the rest unchanged.

Safety, same contract as apply.py: the original's current front/back are
asserted before anything is written, the new id must not already exist, and
afterwards the file is re-parsed and every card other than the pair is compared
field by field against the original file.
"""

import copy
import datetime as dt
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
DATA = ROOT / "flashcards-data"
TODAY = dt.date.today().isoformat()


def card_span(text, cid):
    marker = re.search(r'\{\s*"id": "%s"' % re.escape(cid), text)
    if not marker:
        raise SystemExit(f"{cid}: not found")
    start, depth, i = marker.start(), 0, marker.start()
    while i < len(text):
        if text[i] == "{":
            depth += 1
        elif text[i] == "}":
            depth -= 1
            if depth == 0:
                return start, i + 1
        i += 1
    raise SystemExit(f"{cid}: unbalanced braces")


def set_field(body, key, value):
    """Replace one top-level scalar/array/object field inside a card's text."""
    encoded = json.dumps(value, ensure_ascii=False)
    if isinstance(value, (dict, list)):
        # Match the existing value whatever its layout, up to the line that
        # begins the next field at the same indent.
        pattern = re.compile(r'("%s": )(\{.*?\n      \}|\[.*?\]|[^\n]*?)(,\n      "|\n    \})'
                             % re.escape(key), re.S)
    else:
        pattern = re.compile(r'("%s": )([^\n]*?)(,\n|\n)' % re.escape(key))
    match = pattern.search(body)
    if not match:
        raise SystemExit(f"field {key} not found in card body")
    if isinstance(value, (dict, list)):
        encoded = json.dumps(value, ensure_ascii=False)
        return body[:match.start(2)] + encoded + body[match.end(2):]
    return body[:match.start(2)] + encoded + body[match.end(2):]


def main(path):
    splits = json.loads(pathlib.Path(path).read_text(encoding="utf-8"))

    for deck_path in sorted(DATA.glob("*/*.json")):
        original = deck_path.read_text(encoding="utf-8")
        before = json.loads(original)
        index = {c["id"]: c for c in before["cards"]}
        mine = [s for s in splits if s["id"] in index]
        if not mine:
            continue
        text = original
        added = []

        for split in mine:
            card = index[split["id"]]
            for field in ("front", "back"):
                if split[field + "_old"] != card[field]:
                    raise SystemExit(
                        f"{split['id']}: {field} does not match the file.\n"
                        f"  file: {card[field][:130]}\n"
                        f"  spec: {split[field + '_old'][:130]}")
            if split["new"]["id"] in index:
                raise SystemExit(f"{split['new']['id']}: id already exists")

            start, end = card_span(text, split["id"])
            body = text[start:end]

            # The new card is a copy of the original with fields overridden.
            new_body = body
            for key, value in split["new"].items():
                new_body = set_field(new_body, key, value)
            new_body = set_field(new_body, "version", 1)
            new_body = set_field(new_body, "lastVerified", TODAY)

            # The original, narrowed.
            kept = set_field(body, "front", split["front"])
            kept = set_field(kept, "back", split["back"])
            kept = set_field(kept, "version", card["version"] + 1)
            kept = set_field(kept, "lastVerified", TODAY)

            text = text[:start] + kept + ",\n    " + new_body + text[end:]
            added.append(split["new"]["id"])

        after = json.loads(text)
        if len(after["cards"]) != len(before["cards"]) + len(mine):
            raise SystemExit(f"{deck_path.name}: card count wrong")

        # Everything except the split pairs must be untouched.
        touched = {s["id"] for s in mine} | set(added)
        old_rest = [c for c in before["cards"] if c["id"] not in touched]
        new_rest = [c for c in after["cards"] if c["id"] not in touched]
        if old_rest != new_rest:
            raise SystemExit(f"{deck_path.name}: refused - a card outside the "
                             f"split pairs changed")
        # The originals must differ only in front/back/version/lastVerified.
        idx_after = {c["id"]: c for c in after["cards"]}
        for split in mine:
            probe = copy.deepcopy(idx_after[split["id"]])
            source = index[split["id"]]
            for field in ("front", "back", "version", "lastVerified"):
                probe[field] = source[field]
            if probe != source:
                raise SystemExit(f"{split['id']}: refused - a field other than "
                                 f"front/back/version/lastVerified changed")

        deck_path.write_text(text, encoding="utf-8")
        print(f"{deck_path.name}: split {len(mine)} -> added "
              f"{', '.join(added)}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit(__doc__)
    main(sys.argv[1])

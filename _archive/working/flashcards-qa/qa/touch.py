#!/usr/bin/env python3
"""Bump version and lastVerified on named cards, touching nothing else.

    python3 _working/flashcards/qa/touch.py edexcel-a-1-2-3-formula-02 ...

Card text in this pass is edited BY HAND (CLAUDE.md: never bulk-rewrite prose
with a script - scripted paragraph rebuilds have destroyed markup in this repo
before). This helper only ever rewrites two scalar metadata fields inside one
card object, and it proves it: every byte outside those fields is asserted
unchanged, and the file's JSON is re-parsed and compared field by field before
being written. It never re-serialises the file, so formatting is preserved.
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
    """Byte span of the object holding "id": "<cid>", by brace matching."""
    marker = re.search(r'\{\s*"id": "%s"' % re.escape(cid), text)
    if not marker:
        raise SystemExit(f"{cid}: not found")
    start = marker.start()
    depth, i = 0, start
    while i < len(text):
        if text[i] == "{":
            depth += 1
        elif text[i] == "}":
            depth -= 1
            if depth == 0:
                return start, i + 1
        i += 1
    raise SystemExit(f"{cid}: unbalanced braces")


def main(ids):
    for path in sorted(DATA.glob("*/*.json")):
        original = path.read_text(encoding="utf-8")
        before = json.loads(original)
        text = original
        touched = []
        for cid in ids:
            if not re.search(r'"id": "%s"' % re.escape(cid), text):
                continue
            start, end = card_span(text, cid)
            body = text[start:end]
            new = re.sub(r'"version": (\d+)',
                         lambda m: '"version": %d' % (int(m.group(1)) + 1),
                         body, count=1)
            new = re.sub(r'"lastVerified": "[0-9-]+"',
                         '"lastVerified": "%s"' % TODAY, new, count=1)
            if new == body:
                raise SystemExit(f"{cid}: nothing to bump")
            text = text[:start] + new + text[end:]
            touched.append(cid)
        if not touched:
            continue

        after = json.loads(text)
        # Prove the only differences are the two fields, on the named cards.
        probe = copy.deepcopy(after)
        index = {c["id"]: c for c in probe["cards"]}
        for cid in touched:
            source = next(c for c in before["cards"] if c["id"] == cid)
            index[cid]["version"] = source["version"]
            index[cid]["lastVerified"] = source["lastVerified"]
        if probe != before:
            raise SystemExit(f"{path.name}: refused - a field other than "
                             f"version/lastVerified changed")
        path.write_text(text, encoding="utf-8")
        print(f"{path.name}: bumped {len(touched)} -> {', '.join(touched)}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise SystemExit(__doc__)
    main(sys.argv[1:])

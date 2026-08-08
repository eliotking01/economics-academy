#!/usr/bin/env python3
"""Re-point notes -> past-paper-questions links that still go to the hub.

scripts/append_past_papers_link.py writes a DIRECT link where a topic has its
own generated page, and a query-string link to the hub where it does not:

    /past-paper-questions/?board=edexcel&topic=1-2-2-demand

It is idempotent - it skips any page already carrying the block - which is
correct for what it does, but means a topic that later cleared the volume gate
and gained a real page never had its link upgraded. The notes page, which is
the ideal topical referrer, goes on pointing at the hub, and its signal lands
there instead of on the topic page.

Measured in seo/07-link-graph.md: 66 direct links against 73 to the hub, with
15 ppq topic pages receiving no direct link from their own notes page.

To be clear about severity, because I first overstated it: those pages are NOT
orphans. Each already carries 5-17 inbound links from inside its own section.
This moves the most topically relevant one to where it belongs; it does not
rescue anything from isolation.

WHAT THIS TOUCHES: the href value, and nothing else. Not the block, not the
sentence, not the anchor text, not one character of prose. The surrounding
markup is left byte-identical, so verify_markup_integrity must report 0 losses
and verify_text_integrity 0 differences.

BOARD SAFETY: the slug in the query string is looked up in questions.json,
which carries the board explicitly. The board in the query string, the board on
the record and the board segment of the destination URL must all agree or the
run aborts without writing. No topic code is compared - 37 codes exist on both
boards and mean different topics.

Idempotent: once re-pointed there is no query-string href left to match.

    python3 seo/tools/upgrade_pastpaper_links.py --dry-run
    python3 seo/tools/upgrade_pastpaper_links.py --dry-run --diff 3
    python3 seo/tools/upgrade_pastpaper_links.py
"""

from __future__ import annotations

import argparse
import difflib
import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
NOTES = REPO / "revision-notes"
INDEX = REPO / "past-paper-questions" / "questions.json"

HREF_RE = re.compile(
    r'href="/past-paper-questions/\?board=([a-z-]+)&amp;topic=([a-z0-9-]+)"'
)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--diff", type=int, default=0)
    args = ap.parse_args()

    topics = json.loads(INDEX.read_text())["topics"]

    changed: list[tuple[Path, str, str]] = []
    kept = 0
    errors: list[str] = []

    for page in sorted(NOTES.rglob("*.html")):
        text = page.read_text()
        if not HREF_RE.search(text):
            continue
        rel = page.relative_to(REPO)

        def swap(m: re.Match) -> str:
            nonlocal kept
            q_board, slug = m.group(1), m.group(2)
            rec = topics.get(slug)
            if rec is None:
                errors.append(f"{rel}: {slug!r} is not in questions.json")
                return m.group(0)
            if not rec.get("hasPage"):
                kept += 1                       # correct as-is: no page exists
                return m.group(0)
            url = rec["url"]
            # All three board statements must agree before anything is written.
            if rec["board"] != q_board:
                errors.append(f"{rel}: {slug!r} query board {q_board!r} != "
                              f"record board {rec['board']!r}")
                return m.group(0)
            if f"/past-paper-questions/{q_board}/" not in url:
                errors.append(f"{rel}: {slug!r} destination {url!r} is not "
                              f"under board {q_board!r}")
                return m.group(0)
            return f'href="{url}"'

        new = HREF_RE.sub(swap, text)
        if new != text:
            changed.append((page, text, new))

    print(f"pages to re-point        : {len(changed)}")
    print(f"hub links left alone     : {kept}  (topic has no page of its own)")
    print(f"board/lookup errors      : {len(errors)}")
    for e in errors[:10]:
        print(f"   {e}")

    for path, old, new in changed[: args.diff]:
        rel = path.relative_to(REPO)
        print(f"\n{'=' * 70}\n--- {rel}\n{'=' * 70}")
        for line in difflib.unified_diff(old.split("\n"), new.split("\n"),
                                         lineterm="", n=2,
                                         fromfile=str(rel), tofile=str(rel)):
            print(line)

    if errors:
        print("\nABORTED - nothing written. Resolve the errors above first.",
              file=sys.stderr)
        return 1
    if args.dry_run:
        print("\nDRY RUN - nothing written.")
        return 0

    for path, _, new in changed:
        path.write_text(new)
    print(f"\nWritten: {len(changed)} files.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

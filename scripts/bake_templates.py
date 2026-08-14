#!/usr/bin/env python3
"""Bake the header, footer and script tail into the pages no generator owns.

    python3 scripts/bake_templates.py            # dry run, writes nothing
    python3 scripts/bake_templates.py --apply
    python3 scripts/bake_templates.py --list

Wave 2 Phase 7. Five generators call page_shell.bake() on the 446 pages they
write. The other 17 published pages are hand-written and nothing rebuilds
them, so without this Phase 7 would half-land: two of those 17 are
/past-papers/edexcel-b/ and /past-papers/ocr/, which between them earn 291
clicks and 21,131 impressions - more than anything on the site outside the
homepage - and they would have kept a nav that needs JavaScript.

**Wave 4.10 added the script tail**, for exactly the same reason. The tail
went from seven scripts to four; the other 446 pages take it from
page_shell.SCRIPT_TAIL on a rebuild, and without this these 17 would have
gone on requesting a jQuery that is no longer in the repo. Same two pages,
same argument, same answer. Wave 4.11 took it from four to two the same way.

    root         9   index, tutoring, marking, about, faq, contact, privacy,
                     confirmation, 404. Permanently out of scope for the
                     <head> migration by D34, which is about nine one-off
                     <head> shapes and says nothing about the body.
    past-papers  5   the hub and the four board pages
    notes-other  3   revision-notes/index.html and the two diagram galleries

**This writes markup, never prose.** It replaces one byte-exact anchor -
`<div id="header-placeholder"></div>`, present exactly once on 463 of 463
pages - with the contents of templates/header.html, and the same for the
footer. It does not parse the page and it does not re-serialise it, so it
cannot do the thing CLAUDE.md records scripted rewrites doing here before:
destroy an <a> tag it did not understand. Everything above the anchor and
everything below it is copied through untouched.

**It is re-runnable, and that is the point.** page_shell.bake() accepts a
block it wrote earlier as readily as an untouched placeholder, so editing the
nav is: edit templates/header.html, run the generators, run this, commit. If
it could only run once, these 17 pages would drift away from the other 446
the first time the nav changed, silently.

Dry run by default, like the five seo/tools/ mutators and for the same
reason: a no-flag re-run must stay harmless.

Standard library only.
"""

from __future__ import annotations

import argparse
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import page_shell  # noqa: E402
import verify_page_shell as shell_check  # noqa: E402  - family_of(), pages()

# The families no generator writes. Everything else is rebuilt from source and
# picks the header up on the next run; see verify_page_shell.family_of().
UNGENERATED = ("root", "past-papers", "notes-other")

# Measured, and asserted rather than assumed: if a generator ever takes one of
# these over - or a new hand-written page appears - the count moves and this
# script says so instead of quietly doing different work.
EXPECTED = 17


# Scripts that used to be in the tail and are not any more. Declared, because
# the sync below has to be able to tell "a stale tail entry, delete it" from
# "this page's own script, leave it alone" - index.html carried reviews.js and
# reviews-render.js inside its tail until the 2026-08-14 home-page revamp made
# the testimonials static HTML. No page has own-tail scripts today; the
# distinction stays because the next one might.
#
# Wave 4.10 emptied this of jQuery, dropotron and util.js and renamed
# inject-templates.js to nav.js. Anything removed from page_shell.SCRIPT_TAIL
# in future belongs here in the same commit, or these 17 pages keep loading it
# after the other 446 have stopped.
#
# Wave 4.11 added browser.min.js and breakpoints.min.js, which is that rule
# being followed rather than restated: both files are deleted from the repo, so
# without these two lines /past-papers/edexcel-b/ and /past-papers/ocr/ would
# request two 404s on every page view.
LEGACY_TAIL = (
    "/js/jquery.min.js",
    "/js/jquery.dropotron.min.js",
    "/js/components/inject-templates.js",
    "/js/util.js",
    "/js/browser.min.js",
    "/js/breakpoints.min.js",
)

SCRIPT_RE = re.compile(r'^([ \t]*)<script src="([^"]+)"></script>$')


def sync_script_tail(text: str) -> str:
    """Rewrite the page's script tail from page_shell.SCRIPT_TAIL.

    The region runs from the first `<script src>` naming a current or former
    tail entry to the last. Inside it, current entries are re-emitted in
    SCRIPT_TAIL's order, former entries are dropped, and anything else is the
    page's own and is kept, in its original order, after them.

    Line-based and anchored on exact tags, so it cannot touch anything else on
    the page - the same property the header bake has, and for the same reason.
    """
    lines = text.split("\n")
    known = set(page_shell.SCRIPT_TAIL) | set(LEGACY_TAIL)

    hits = [i for i, ln in enumerate(lines)
            if (m := SCRIPT_RE.match(ln)) and m.group(2) in known]
    if not hits:
        return text
    first, last = hits[0], hits[-1]
    indent = SCRIPT_RE.match(lines[first]).group(1)

    # Everything in the region that is neither a current nor a former tail
    # entry: nothing today - the home-page revamp deleted index.html's two
    # review scripts. Kept for the next page that carries its own.
    theirs = [ln for ln in lines[first:last + 1]
              if not ((m := SCRIPT_RE.match(ln)) and m.group(2) in known)]

    rebuilt = [f'{indent}<script src="{s}"></script>'
               for s in page_shell.SCRIPT_TAIL] + theirs
    return "\n".join(lines[:first] + rebuilt + lines[last + 1:])


def targets() -> list[str]:
    return [p for p in shell_check.pages()
            if shell_check.family_of(p) in UNGENERATED]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--apply", action="store_true",
                    help="write the files (default: report and write nothing)")
    ap.add_argument("--list", action="store_true",
                    help="print the pages this owns and stop")
    args = ap.parse_args()

    paths = targets()
    if args.list:
        for p in paths:
            print(f"  {shell_check.family_of(p):12} {p}")
        print(f"{len(paths)} pages")
        return 0

    if len(paths) != EXPECTED:
        print(f"error: expected {EXPECTED} ungenerated published pages, "
              f"found {len(paths)}. If that is right, change EXPECTED in the "
              f"same commit that changes the page set.", file=sys.stderr)
        for p in paths:
            print(f"  {shell_check.family_of(p):12} {p}", file=sys.stderr)
        return 1

    changed, already = [], 0
    for rel in paths:
        path = ROOT / rel
        before = path.read_text(encoding="utf-8")
        after = sync_script_tail(page_shell.bake(before, rel))
        if after == before:
            already += 1
            continue
        changed.append(rel)
        if args.apply:
            path.write_text(after, encoding="utf-8")

    verb = "baked" if args.apply else "WOULD BAKE"
    for rel in changed:
        print(f"  {verb} {rel}")
    print(f"{len(paths)} pages: {len(changed)} {'changed' if args.apply else 'would change'}, "
          f"{already} already current")
    if not args.apply and changed:
        print("dry run - nothing written. Re-run with --apply.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

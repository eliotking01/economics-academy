#!/usr/bin/env python3
"""Slice the 7 notes-hub pages into notes-data/hubs/. One-off, dry run by default.

    python3 scripts/extract_notes_hubs.py            # report, write nothing
    python3 scripts/extract_notes_hubs.py --apply    # write notes-data/hubs/

Wave 2 Phase 3, the pilot. Pairs with scripts/build_notes_hubs.py, which
renders the pages back from what this writes.

THE ONE RULE THAT MATTERS
-------------------------
PH06 section 3: **the content is moved by slicing bytes out of the existing
file. It is never parsed and re-serialised. No HTML parser round trip. No prose
is regenerated.** That is what protects against the failure mode CLAUDE.md
records - "scripted paragraph rebuilds have silently destroyed <a> tags here
before". A byte slice cannot destroy an <a> tag, because it does not
understand what one is.

So this script finds two offsets and copies what is between them. Everything
it does understand - the <head> values, the wrapper's attributes, which
decorative comments a page carries - is lifted verbatim into a JSON file
beside the slice, never re-derived. The meta descriptions in particular are
bespoke per page, and rewriting one would be a content change.

WHY THE 7 HUBS ARE A GOOD PILOT, HAVING MEASURED THEM
------------------------------------------------------
They carry two body shapes, not one. Six use `<section id="main">` with
`<!-- Header -->`-style comments; `revision-notes/macro-application/index.html`
uses `<section id="main" class="revision-notes-content">`, closes its blocks
with `<!-- end #main -->` markers, and carries a completely different trailing
inline script. Six of the seven are also among PH06-029's 18 pages that
disagree with themselves on og:description, and one is PH06-030's single
breadcrumb mismatch. A pilot that did not meet those would prove less.

Standard library only.
"""

from __future__ import annotations

import argparse
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import page_shell  # noqa: E402
import verify_page_shell as shell_check  # noqa: E402

OUT = ROOT / "notes-data" / "hubs"

# <div class="container"> ... </div> </section>, with the optional end-marker
# comments macro-application carries. Two capture groups so those comments are
# lifted rather than dropped: migrate byte-identically first, tidy later.
OPEN = re.compile(
    r'\n      <section id="main"([^>]*)>\n        <div class="container">\n')
CLOSE = re.compile(
    r"\n        </div>(<!--[^>]*-->)?\n      </section>(<!--[^>]*-->)?\n")
BODY_OPEN = re.compile(r"</head>\n  <body class=\"is-preload\">\n")
SEVEN_START = '    <script src="/js/jquery.min.js"></script>\n'
SEVEN_END = '    <script src="/js/main.js"></script>\n'


def slug_of(path: str) -> str:
    """revision-notes/edexcel-theme-1/index.html -> edexcel-theme-1."""
    return path[len("revision-notes/"):-len("/index.html")]


def carve(path: str, source: str) -> dict:
    om, cm = OPEN.search(source), CLOSE.search(source)
    if not om or not cm:
        raise SystemExit(f"{path}: could not find the container boundaries. "
                         f"Extraction refuses to guess; handle this page by hand.")
    if len(OPEN.findall(source)) != 1 or len(CLOSE.findall(source)) != 1:
        raise SystemExit(f"{path}: the container boundary is not unique.")

    slice_html = source[om.end():cm.start()]
    bo = BODY_OPEN.search(source)
    if not bo:
        raise SystemExit(f"{path}: unexpected <body>.")

    between = source[bo.end():om.start() + 1]
    seven_at = source.index(SEVEN_START)
    tail_at = source.index(SEVEN_END) + len(SEVEN_END)

    return {
        "path": path,
        "head": page_shell.extract(source),
        "body": {
            # The full attribute string, so macro-application keeps its
            # .revision-notes-content wrapper - Wave 4.6 scoped the textbook
            # stylesheet under exactly that class on 169 pages.
            "mainAttrs": om.group(1),
            "endContainerComment": cm.group(1),
            "endMainComment": cm.group(2),
            # Everything between <body> and <section id="main">: the
            # page-wrapper, the header placeholder and whichever decorative
            # comments this page happens to carry.
            "beforeMain": between,
            # Between </section> and the script tail: the footer placeholder,
            # the page-wrapper close and whichever comments this page carries.
            "afterMain": source[cm.end() - 1:seven_at],
            # Everything after the seven-script tail, verbatim: each hub
            # carries its own inline script and they are not interchangeable.
            "afterScripts": source[tail_at:],
        },
        "slice": slice_html,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--apply", action="store_true", help="write the files")
    args = ap.parse_args()

    hubs = [p for p in shell_check.pages()
            if shell_check.family_of(p) == "notes-hub"]
    print(f"{len(hubs)} notes-hub pages\n")

    carved = []
    for p in hubs:
        src = (ROOT / p).read_text(encoding="utf-8")
        rec = carve(p, src)
        carved.append(rec)
        print(f"  {slug_of(p):20} slice {len(rec['slice']):6} bytes of "
              f"{len(src):6}  ({100 * len(rec['slice']) / len(src):.0f}%)")

    if not args.apply:
        print(f"\ndry run, nothing written. Re-run with --apply.")
        return 0

    OUT.mkdir(parents=True, exist_ok=True)
    for rec in carved:
        slug = slug_of(rec["path"])
        (OUT / f"{slug}.html").write_text(rec.pop("slice"), encoding="utf-8")
        (OUT / f"{slug}.json").write_text(
            json.dumps(rec, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8")
    print(f"\nwrote {2 * len(carved)} files to {OUT.relative_to(ROOT)}")
    print("notes-data/ must be in _config.yml's exclude in this same commit.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

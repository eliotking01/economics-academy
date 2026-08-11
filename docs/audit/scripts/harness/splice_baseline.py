#!/usr/bin/env python3
"""Build the OLD-spliced baseline the Phase 7 harness run compares against.

Baking the header and footer into the pages changes the visible text of the
source of all 463 pages, so `compare_trees.py` assertion 2 - and
`verify_text_integrity.py` - go red against OLD by design rather than by
mistake. Weakening either would be the wrong answer: assertion 2 is the
strongest thing the harness has.

So the comparison is re-pointed instead of relaxed. The right baseline is not
OLD, it is **OLD as the browser assembles it**: `inject-templates.js` does

    document.getElementById("header-placeholder").outerHTML = data

which is a literal replacement of the placeholder by the bytes of
`templates/header.html`, followed by `setActivePage()` adding `class="current"`
to one <li>. This script does exactly that, to a copy of OLD. Comparing NEW
against the result asks the only question that matters: **does the page the
reader gets still say and link the same things?** All ten assertions then
apply unchanged, at D33's criterion.

**This is deliberately a second implementation, and must stay one.**
`scripts/bake_templates.py` produces the committed output; this produces the
thing that output is judged against. If both were the same code, a bug in it
would cancel itself out and the harness would pass green on a broken site -
the "measurement that returns 0 and could never return anything else" trap
that PROGRESS.md records. So this one is naive on purpose: a literal
`str.replace`, no re-indentation, no BEGIN/END markers, no shared import. The
two outputs differ in whitespace and comments, which nine of the ten
assertions are blind to and the tenth (assertion 3, LaTeX) never sees.

The `current` mapping below is transcribed from the `pageMap` array in
`js/components/inject-templates.js`, in order, because that array is what
ships today. It is not imported from anywhere.

**The baseline must cover exactly what the commit bakes, and no more.**
Phase 7 lands a family at a time, so a baseline spliced over all 463 pages
would report the not-yet-baked ones as differing - a failure that means
"this commit did not do the next commit's work". Pass --only to scope it.
With no --only it splices every published page, which is the right baseline
once the last family has landed.

Usage:
    python3 splice_baseline.py <old-tree> <output-tree> [--only PREFIX ...]
"""

import pathlib
import re
import shutil
import subprocess
import sys

HEADER_PLACEHOLDER = '<div id="header-placeholder"></div>'
FOOTER_PLACEHOLDER = '<div id="footer-placeholder"></div>'

# js/components/inject-templates.js setActivePage(), pageMap, in its order.
PAGE_MAP = [
    (r"^/revision-notes(/|$)", "revision-notes"),
    (r"^/flashcards(/|$)", "flashcards"),
    (r"^/practice-questions(/|$)", "practice-questions"),
    (r"^/past-paper-questions(/|$)", "past-papers"),
    (r"^/past-papers(/|$)", "past-papers"),
    (r"^/tutoring\.html$", "tutoring"),
    (r"^/marking\.html$", "marking"),
    (r"^/about\.html$", "about"),
    (r"^/contact\.html$", "contact"),
    (r"^/(index\.html)?$", "home"),
]


def url_path(rel: str) -> str:
    """window.location.pathname for a page at this repo-relative path."""
    if rel == "index.html":
        return "/"
    if rel.endswith("/index.html"):
        return "/" + rel[: -len("index.html")]
    return "/" + rel


def active_page(rel: str) -> str:
    path = url_path(rel)
    for pattern, page in PAGE_MAP:
        if re.search(pattern, path):
            return page
    return ""


def main(argv) -> int:
    only = []
    while "--only" in argv:
        i = argv.index("--only")
        only.append(argv[i + 1])
        del argv[i:i + 2]
    if len(argv) != 2:
        print("usage: splice_baseline.py <old-tree> <output-tree> "
              "[--only PREFIX ...]")
        return 2
    old, out = pathlib.Path(argv[0]), pathlib.Path(argv[1])
    if out.exists():
        shutil.rmtree(out)
    shutil.copytree(old, out, symlinks=True)

    header = (out / "templates" / "header.html").read_text(encoding="utf-8")
    footer = (out / "templates" / "footer.html").read_text(encoding="utf-8")

    tracked = subprocess.run(
        ["git", "ls-files", "*.html"], cwd=old,
        capture_output=True, text=True, check=True,
    ).stdout.split()

    # Published pages only. 14 tracked .html under _working/flashcards/qa/
    # carry the placeholders too, and they are working files that the build
    # must not touch - splicing them here would make assertion 8 report 14
    # differing files outside every migrating family.
    sys.path.insert(0, str(old / "scripts"))
    import build_sitemap  # noqa: E402  - for its _config.yml exclude parser
    excludes = build_sitemap.excludes()

    done = 0
    skipped = []
    for rel in sorted(tracked):
        if rel.startswith("templates/"):
            continue
        if not build_sitemap.published(rel, excludes):
            continue
        if only and not any(rel.startswith(p) for p in only):
            continue
        f = out / rel
        src = f.read_text(encoding="utf-8")
        if HEADER_PLACEHOLDER not in src or FOOTER_PLACEHOLDER not in src:
            skipped.append(rel)
            continue
        page = active_page(rel)
        head = header
        if page:
            # classList.add("current") on the one <li data-page="..."> element.
            # Every one of the nine is written on a single line in the
            # template, so a literal replace is enough; if that ever stops
            # being true the count check at the end of this function fails.
            before = head
            head = head.replace(
                f'<li data-page="{page}">',
                f'<li data-page="{page}" class="current">',
                1,
            )
            if head == before:
                print(f"REFUSING: no <li data-page=\"{page}\"> in the header "
                      f"template, needed by {rel}")
                return 1
        src = src.replace(HEADER_PLACEHOLDER, head, 1)
        src = src.replace(FOOTER_PLACEHOLDER, footer, 1)
        f.write_text(src, encoding="utf-8")
        done += 1

    print(f"spliced {done} pages in {out}")
    if skipped:
        print(f"  {len(skipped)} tracked .html had no placeholder pair "
              f"(not published, or already baked): {skipped[:5]}")
    if done == 0:
        print("REFUSING: 0 pages spliced. A baseline that changed nothing "
              "would make every assertion pass for the wrong reason.")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

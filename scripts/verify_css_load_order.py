#!/usr/bin/env python3
"""The `<head>` stylesheet order every page depends on is still what it was.

    python3 scripts/verify_css_load_order.py

Pure stdlib. Exit code 1 if anything is flagged.

WHY THIS EXISTS

Wave 4.6 set out to scope the bare selectors in every `css/pages/*.css` so
that a page sheet beats `css/main.css` on **specificity** rather than on load
order. `revision-notes-textbook.css` was done: it was already winning every
argument, so raising its specificity changed nothing and it now wins for a
reason that survives a reordered `<head>`.

`contact.css` and `tutoring.css` could not be done, and the reason is
measured rather than assumed. On those two pages `css/main.css` is currently
*winning* - 9 property conflicts on contact.html, and the whole `#contactModal`
block on tutoring.html. Scoping them reverses those wins: the contact form
loses 120px of height and its select and textarea stop matching its text
inputs; the tutoring modal drops from `position: fixed` to `static` and the
enquiry form lands inline on the page. So the bare selectors stay, and what
keeps those two pages correct is **load order alone**.

That makes the order an invariant rather than an accident, and nothing was
checking it. This script does. It is the thing that has to stay green before
Wave 2's page_shell.py starts generating `<head>` blocks, because a template
that emits the same links in a different order breaks two commercial pages
silently - no console error, no failed request, just a different design.

THE THREE CHECKS

1. Every page that loads a `css/pages/*.css` loads `css/main.css` first.
   462 of 462 today. This is the one the 4.6 decline rests on.

2. The order is fontawesome -> the Google Fonts stylesheet -> `css/main.css`.
   `4db232c` hoisted the first two out of two `@import` rules in main.css and
   into every `<head>` in exactly that order, to remove a render-blocking
   chain; DO-NOT-BREAK.md records that it must not be reversed, and until now
   only the *presence* of those links was checked, never their order.

3. Exactly one page loads two `css/pages/*.css` sheets, and it is
   `revision-notes/macro-application/index.html`. PH08-038's finding that
   unscoped page sheets are safe depends on this: two of them on one page
   would fight each other, and load order would decide that too. A second
   such page fails here rather than being discovered by eye. Deliberately a
   named path rather than a count, in the spirit of
   `EXPECTED = {"edexcel": 87, "aqa": 79}` in build_past_paper_taxonomy.py.
"""

from __future__ import annotations

import pathlib
import re
import subprocess
import sys

REPO = pathlib.Path(__file__).resolve().parent.parent

# Sibling in scripts/. Imported for its _config.yml `exclude` parser and its
# publish rule, the same way verify_liquid.py does, so this checker and the
# sitemap agree on what Jekyll actually builds. Without it the _working/
# flashcard QA harnesses are checked, and they are not pages.
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import build_sitemap  # noqa: E402

LINK = re.compile(r"<link\b[^>]*>", re.I)
HREF = re.compile(r'href="([^"]+)"', re.I)
REL = re.compile(r'rel="([^"]+)"', re.I)

FONTAWESOME = "fontawesome-all.min.css"
GOOGLE_FONTS = "fonts.googleapis.com"
MAIN = "/css/main.css"
PAGE_DIR = "/css/pages/"

# Check 3. Two page sheets on one page is a collision the scoping house rule
# exists to prevent; this is the one place it happens and it is deliberate.
TWO_SHEET_PAGES = {"revision-notes/macro-application/index.html"}


def tracked(*globs: str) -> list[pathlib.Path]:
    out = subprocess.run(
        ["git", "ls-files", *globs], cwd=REPO, capture_output=True, text=True, check=True
    )
    return [REPO / line for line in out.stdout.split()]


def stylesheets(text: str) -> list[str]:
    """Every rel=stylesheet href, in document order."""
    out = []
    for tag in LINK.findall(text):
        rel, href = REL.search(tag), HREF.search(tag)
        if rel and "stylesheet" in rel.group(1).lower() and href:
            out.append(href.group(1))
    return out


def first(sheets: list[str], predicate) -> int | None:
    for i, s in enumerate(sheets):
        if predicate(s):
            return i
    return None


def main() -> int:
    problems: list[str] = []
    checked = 0
    two_sheet: set[str] = set()
    ex = build_sitemap.excludes()

    for path in tracked("*.html"):
        rel = path.relative_to(REPO).as_posix()
        if not build_sitemap.published(rel, ex):
            continue
        sheets = stylesheets(path.read_text(encoding="utf-8", errors="ignore"))
        page_idx = [i for i, s in enumerate(sheets) if PAGE_DIR in s]
        if not page_idx:
            continue
        checked += 1
        if len(page_idx) > 1:
            two_sheet.add(rel)

        i_main = first(sheets, lambda s: s.endswith(MAIN))
        i_fa = first(sheets, lambda s: s.endswith(FONTAWESOME))
        i_gf = first(sheets, lambda s: GOOGLE_FONTS in s)

        # 1. main.css first, then the page sheet
        if i_main is None:
            problems.append(f"{rel}: loads a page stylesheet but not {MAIN}")
        elif i_main > page_idx[0]:
            problems.append(
                f"{rel}: {MAIN} is loaded AFTER {sheets[page_idx[0]]} — the page "
                "sheet's bare selectors no longer win"
            )

        # 2. the 4db232c order
        if i_fa is None:
            problems.append(f"{rel}: no direct <link> to {FONTAWESOME} (4db232c)")
        if i_gf is None:
            problems.append(f"{rel}: no direct <link> to the Google Fonts stylesheet")
        if None not in (i_fa, i_gf, i_main) and not i_fa < i_gf < i_main:
            problems.append(
                f"{rel}: stylesheet order is not fontawesome < fonts.googleapis "
                f"< main.css (indices {i_fa}, {i_gf}, {i_main}) — 4db232c reversed"
            )

    # 3. the page-sheet pairing
    for rel in sorted(two_sheet - TWO_SHEET_PAGES):
        problems.append(
            f"{rel}: loads two css/pages sheets. Only "
            f"{', '.join(sorted(TWO_SHEET_PAGES))} may — two unscoped page sheets "
            "on one page are decided by load order too (PH08-038)"
        )
    for rel in sorted(TWO_SHEET_PAGES - two_sheet):
        problems.append(
            f"{rel}: expected to load two css/pages sheets and no longer does — "
            "update TWO_SHEET_PAGES if that is intended"
        )

    print(f"{checked} pages load a css/pages stylesheet; {len(two_sheet)} load two")

    if problems:
        print(f"\n{len(problems)} problem(s):")
        for p in problems:
            print(f"  {p}")
        return 1

    print("main.css precedes every page stylesheet, and 4db232c's order holds")
    return 0


if __name__ == "__main__":
    sys.exit(main())

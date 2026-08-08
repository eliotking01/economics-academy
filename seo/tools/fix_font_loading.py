#!/usr/bin/env python3
"""Hoist the two @import rules out of css/main.css into every page's <head>.

The problem, measured in seo/09-web-vitals-baseline.md:

    css/main.css opened with
        @import url("fontawesome-all.min.css");
        @import url("https://fonts.googleapis.com/css2?...");

    An @import inside a render-blocking stylesheet is invisible to the preload
    scanner. The browser cannot learn those two requests exist until main.css
    has downloaded and parsed, which produced a 4-deep critical request chain
    on all 463 pages:

        HTML -> main.css -> fonts.googleapis.com -> fonts.gstatic.com/*.woff2

    Lighthouse measured that Google Fonts stylesheet as the single largest
    render-blocking resource on 6 of 6 sampled pages - 2.9 KB costing 782-834
    ms - purely because of when it was discovered. The LCP element is text on
    every one of those pages, so this gates LCP directly.

What this does, per page: inserts the two stylesheet <link>s immediately before
the existing /css/main.css link, plus the two font preconnects on the 190 pages
that lack them.

THE ORDER IS THE WHOLE SAFETY ARGUMENT. @import rules are applied where they
appear, so the old cascade was:

    fontawesome -> google fonts -> main.css's own rules -> page stylesheet

Inserting both links immediately before the main.css link, fontawesome first,
reproduces that exactly. Nothing else about the cascade changes, and no rule is
added, removed or reordered.

This is a <head> edit only. It never touches <body>, so no prose is at risk -
but verify anyway, against the commit before the run:

    python3 scripts/verify_text_integrity.py <before-ref>
    python3 scripts/verify_markup_integrity.py <before-ref> --strict

Idempotent: a page already carrying the fontawesome link is skipped, so this is
safe to re-run over the whole site. The four generators in scripts/ emit the
same block, so regenerating a section produces no diff.

    python3 seo/tools/fix_font_loading.py --dry-run
    python3 seo/tools/fix_font_loading.py --dry-run --diff 3
    python3 seo/tools/fix_font_loading.py
"""

from __future__ import annotations

import argparse
import difflib
import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
MAIN_CSS = REPO / "css" / "main.css"

FONTS_URL = (
    "https://fonts.googleapis.com/css2?family=Merriweather:ital,wght@0,400;0,700;1,400"
    "&amp;family=Open+Sans:wght@400;600;700"
    "&amp;family=Source+Sans+Pro:ital,wght@0,300;0,400;0,700;0,900;1,300"
    "&amp;display=swap"
)

ANCHOR_RE = re.compile(
    r'^([ \t]*)<link rel="stylesheet" href="/css/main\.css"\s*/?>[ \t]*$', re.M
)

# Marker for "this page is already done". Chosen because no page linked
# fontawesome directly before this script existed - verified, 0 of 463.
DONE_MARKER = 'href="/css/fontawesome-all.min.css"'
PRECONNECT_MARKER = 'rel="preconnect" href="https://fonts.gstatic.com"'

COMMENT = """<!-- Linked here rather than @imported from main.css: an @import inside a
         render-blocking stylesheet is invisible to the preload scanner, so
         neither request could start until main.css had parsed. The order below
         matches the old @import order, so the cascade is unchanged.
         See seo/09-web-vitals-baseline.md. -->"""

PRECONNECTS = """<link rel="preconnect" href="https://fonts.googleapis.com" />
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />"""

# Wrapped exactly as prettier@3.9.6 formats it, so a future Prettier run over
# these files is a no-op on the block this script inserts.
STYLESHEETS = f"""<link rel="stylesheet" href="/css/fontawesome-all.min.css" />
    <link
      rel="stylesheet"
      href="{FONTS_URL}"
    />"""


def block_for(text: str) -> str:
    parts = [COMMENT]
    if PRECONNECT_MARKER not in text:
        parts.append(PRECONNECTS)
    parts.append(STYLESHEETS)
    return "\n    ".join(parts)


def patch_page(text: str) -> str | None:
    """Return the patched page, or None if it needs no change."""
    if DONE_MARKER in text:
        return None
    m = ANCHOR_RE.search(text)
    if not m:
        return None
    block = block_for(text)
    return text[: m.start()] + f"{m.group(1)}{block}\n" + text[m.start():]


CSS_DONE_MARKER = "Do not put them back."


def patch_main_css(text: str) -> str | None:
    # Guard on the note, not on "@import": once the imports are gone the file
    # has no @import to test for, and an earlier version of this function
    # re-prepended the note on every run.
    if CSS_DONE_MARKER in text or "@import" not in text:
        return None
    lines = text.split("\n")
    kept = [ln for ln in lines if not ln.startswith("@import ")]
    note = (
        "/* The two @import rules that used to open this file - fontawesome and\n"
        "   the Google Fonts stylesheet - are now <link> tags in every page's\n"
        "   <head>, immediately before this file, in the same order. An @import\n"
        "   here is invisible to the preload scanner and cost 782-834 ms of\n"
        "   render-blocking time on every page measured. Do not put them back.\n"
        "   See seo/09-web-vitals-baseline.md and seo/tools/fix_font_loading.py. */"
    )
    return note + "\n" + "\n".join(kept).lstrip("\n")


def tracked_pages() -> list[Path]:
    out = subprocess.run(
        ["git", "-C", str(REPO), "ls-files", "*.html"],
        capture_output=True, text=True, check=True,
    ).stdout.split("\n")
    skip = ("templates/", "_working/", "old-logos-archive/")
    return [REPO / p for p in out if p and not p.startswith(skip)]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--diff", type=int, default=0, help="show N sample diffs")
    args = ap.parse_args()

    changed: list[tuple[Path, str, str]] = []
    skipped = no_anchor = 0
    added_preconnect = 0

    css_text = MAIN_CSS.read_text()
    css_new = patch_main_css(css_text)
    if css_new:
        changed.append((MAIN_CSS, css_text, css_new))

    for p in tracked_pages():
        text = p.read_text()
        new = patch_page(text)
        if new is None:
            if DONE_MARKER in text:
                skipped += 1
            else:
                no_anchor += 1
            continue
        if PRECONNECT_MARKER not in text:
            added_preconnect += 1
        changed.append((p, text, new))

    html_changed = [c for c in changed if c[0] != MAIN_CSS]
    print(f"css/main.css @imports removed : {'yes' if css_new else 'no (already done)'}")
    print(f"pages to change               : {len(html_changed)}")
    print(f"  ...of which gain preconnect : {added_preconnect}")
    print(f"pages already done            : {skipped}")
    print(f"pages without the anchor      : {no_anchor}")

    for path, old, new in changed[: args.diff]:
        rel = path.relative_to(REPO)
        print(f"\n{'=' * 70}\n--- {rel}\n{'=' * 70}")
        diff = difflib.unified_diff(
            old.split("\n"), new.split("\n"), lineterm="", n=2,
            fromfile=str(rel), tofile=str(rel),
        )
        for line in diff:
            print(line)

    if args.dry_run:
        print("\nDRY RUN - nothing written.")
        return 0

    for path, _, new in changed:
        path.write_text(new)
    print(f"\nWritten: {len(changed)} files.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

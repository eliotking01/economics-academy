#!/usr/bin/env python3
"""Assert that nothing unexpected is published on the live site.

    python3 scripts/verify_published_surface.py

WHY THIS EXISTS
---------------
`revision-notes/macro-application/macro-application-uk-sa.md` - 429 lines of
source markdown - was tracked, not excluded, and served live at its own URL for
the entire eleven-phase audit. It survived because **every enumeration tool in
this repo globs `*.html`**: `lib.published_html()`, `lib.pages()`,
`build_sitemap.py` and `verify_links.py` all do. So `is_published()` returned
True and `published_html()` returned False for the same file, and every count
was right while none of them included it.

`_config.yml`'s `exclude` list is maintained by DIRECTORY. It catches every
directory that is entirely source, and it cannot catch a source file that lives
inside a content directory. Nothing else looked.

This check closes the class rather than the instance: it enumerates ALL tracked
files, not just HTML, and asserts every published one is either a known web
asset type or a file we have decided to serve.

The sharper risk it guards is a deploy failure, not a stray URL. Liquid runs over
every published markdown file before Markdown, and one stray `{%` fails the whole
GitHub Pages build - not the page, the deploy. A markdown file inside a published
content directory is exactly where that would be least expected.

PH10-060. Standard library only.
"""

from __future__ import annotations

import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import build_sitemap  # noqa: E402  - for its _config.yml exclude parser

# Everything a browser is meant to fetch. Deliberately a whitelist: the point is
# that an unrecognised type is a question, not something to quietly permit.
ALLOWED_SUFFIXES = {
    ".html", ".pdf",
    ".css", ".js", ".json", ".xml",
    ".png", ".jpg", ".jpeg", ".svg", ".webp", ".gif", ".ico",
    ".woff", ".woff2", ".ttf", ".eot",
    ".txt", ".webmanifest",
}

# Extensionless or odd files we serve on purpose.
ALLOWED_NAMES = {
    "CNAME",        # GitHub Pages custom-domain config
    "robots.txt",
    "LICENSE.txt",
}

# Known and accepted exceptions, each with the reason and where it is tracked.
# Printed on EVERY run rather than passing silently - a suppressed exception
# that nobody sees is how PH10-060 lasted eleven phases in the first place.
#
# Currently empty, and worth keeping that way. Its one entry - PH10-060's
# macro-application-uk-sa.md - was resolved by moving the file to _archive/raw-notes/
# rather than by leaving it listed here, which is what the RESOLVED branch below
# exists to push for.
KNOWN: dict[str, str] = {}


def published_files():
    """Every tracked file GitHub Pages actually serves.

    build_sitemap.published() applies _config.yml's exclude list and Jekyll's
    underscore rule. Jekyll ALSO skips any path segment beginning with a dot,
    which that function does not model - it never needs to, because it is only
    ever handed .html and .pdf paths. Verified live: /.gitignore returns 404
    while /CNAME, /robots.txt and /LICENSE.txt all return 200.
    """
    ex = build_sitemap.excludes()
    out = subprocess.run(["git", "ls-files"], cwd=ROOT,
                         capture_output=True, text=True, check=True).stdout
    files = [f for f in out.splitlines() if f]
    return [
        f for f in files
        if build_sitemap.published(f, ex)
        and not any(seg.startswith(".") for seg in f.split("/"))
    ]


def main() -> int:
    published = published_files()
    unexpected = []
    for f in published:
        p = pathlib.PurePosixPath(f)
        if p.name in ALLOWED_NAMES or p.suffix.lower() in ALLOWED_SUFFIXES:
            continue
        unexpected.append(f)

    accepted = [f for f in unexpected if f in KNOWN]
    problems = [f for f in unexpected if f not in KNOWN]

    print(f"{len(published)} tracked files are published")

    for f in accepted:
        print(f"  KNOWN  {f}\n         {KNOWN[f]}")

    stale = [f for f in KNOWN if f not in unexpected]
    for f in stale:
        print(f"  RESOLVED  {f} is no longer published - "
              f"delete its entry from KNOWN in this script.")

    sys.stdout.flush()
    if problems:
        print(f"\nFAIL: {len(problems)} unexpected file(s) on the published "
              f"surface:", file=sys.stderr)
        for f in problems:
            print(f"  {f}", file=sys.stderr)
        print("\nEither add it to _config.yml's exclude list, move it out of a "
              "published directory, or - if it is genuinely meant to be served "
              "- add its type to ALLOWED_SUFFIXES in this script.\n"
              "If it is markdown, note that Liquid runs over it before Markdown "
              "and a stray '{%' fails the whole deploy.", file=sys.stderr)
        return 1

    print(f"no unexpected file types published"
          f"{f' ({len(accepted)} known exception(s))' if accepted else ''}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

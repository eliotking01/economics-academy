#!/usr/bin/env python3
"""Catch Liquid syntax errors before they break the Pages deploy.

    python3 scripts/verify_liquid.py

GitHub Pages builds this repo with Jekyll, and Jekyll runs **Liquid over every
markdown file before Markdown**. A stray `{%` therefore opens a Liquid tag that
is never closed, and the whole deploy fails - not the one page, the deploy.

Backticks do not help. Liquid runs first and has no idea what a code span is.
This is how it failed once, in REVIEW-NOTES.md, on a line documenting a LaTeX
bug:

    `\\text{% Change in Real GDP} = ...`

    Liquid syntax error (line 1513): Tag '{%' was not properly terminated

The fix is to wrap the offending text in `{% raw %}` ... `{% endraw %}`.

Only markdown is at risk. The site's HTML has no front matter, so Jekyll copies
it verbatim without rendering. Directories beginning with `_` are excluded from
the build entirely, which is why `_working/` is skipped here too.

Standard library only. This reimplements enough of Liquid 4's tokeniser to
reproduce the failure; it was checked against the real Liquid 4.0.4, the version
github-pages v232 ships, on both the broken file and the fixed one.
"""

from __future__ import annotations

import pathlib
import re
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent

# Liquid::TemplateParser - non-greedy, so each opener takes the nearest closer.
TOKEN = re.compile(r"(\{%-?.*?-?%\}|\{\{-?.*?-?\}\})", re.S)
TAG_NAME = re.compile(r"\A\{%-?\s*(\w+)")
STRAY = re.compile(r"\{%|\{\{")

# Liquid::Raw::FullTokenPossiblyInvalid. Inside a raw block Liquid re-scans each
# token with a GREEDY leading .*, so it matches the LAST tag in the token rather
# than the first. That is what lets `{% raw %}\text{% ... %}{% endraw %}` close
# correctly even though the non-greedy tokeniser above swallowed the endraw into
# one oversized token. Reimplementing this faithfully matters: without it this
# checker reports a false failure on text that Liquid accepts.
RAW_CLOSE = re.compile(r"\A(.*)\{%-?\s*(\w+)\s*(.*?)-?%\}\Z", re.S)


def rendered_files():
    """Every markdown file GitHub Pages will run Liquid over."""
    out = subprocess.run(["git", "ls-files", "*.md"], cwd=ROOT,
                         capture_output=True, text=True, check=True).stdout
    return [ROOT / f for f in out.split()
            if not any(part.startswith("_") for part in pathlib.Path(f).parts)]


def check(path: pathlib.Path):
    """Return a list of (line, message) for one file."""
    text = path.read_text(encoding="utf-8")
    problems = []
    raw_depth = 0
    pos = 0
    for part in TOKEN.split(text):
        if not part:
            continue
        is_tag = bool(TOKEN.fullmatch(part))
        name = ""
        if is_tag:
            m = TAG_NAME.match(part)
            name = m.group(1) if m else ""

        if raw_depth:
            # Inside raw, only endraw is honoured; everything else is literal.
            # Match Liquid's own greedy re-scan, so an endraw that the tokeniser
            # swallowed into a larger token is still found.
            m = RAW_CLOSE.match(part)
            if m and m.group(2) == "endraw":
                raw_depth -= 1
        elif is_tag and name == "raw":
            raw_depth += 1
        elif not is_tag:
            # Text that still holds an opener means the tokeniser could not
            # terminate it - exactly the error Liquid reports.
            m = STRAY.search(part)
            if m:
                line = text.count("\n", 0, pos + m.start()) + 1
                snippet = text.splitlines()[line - 1].strip()[:90]
                problems.append(
                    (line, f"unterminated {m.group(0)!r} - wrap it in "
                            f"{{% raw %}} ... {{% endraw %}}\n      {snippet}"))
        pos += len(part)

    if raw_depth:
        problems.append((0, "'{% raw %}' is never closed with '{% endraw %}'"))
    return problems


def main():
    files = rendered_files()
    bad = 0
    for path in files:
        for line, msg in check(path):
            bad += 1
            where = f"{path.relative_to(ROOT)}:{line}" if line else \
                    str(path.relative_to(ROOT))
            print(f"  {where}: {msg}", file=sys.stderr)
    print(f"\n{len(files)} markdown files checked, {bad} problem(s)")
    if bad:
        print("A Liquid error fails the whole GitHub Pages deploy, not just the "
              "page it is on.", file=sys.stderr)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())

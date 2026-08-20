#!/usr/bin/env python3
"""Catch Liquid syntax errors before they break the Pages deploy.

    python3 scripts/verify_liquid.py

GitHub Pages builds this repo with Jekyll, and Jekyll runs **Liquid over every
markdown file before Markdown**. A stray `{%` therefore opens a Liquid tag that
is never closed, and the whole deploy fails - not the one page, the deploy.

Backticks do not help. Liquid runs first and has no idea what a code span is.
This is how it failed once, in docs/REVIEW-NOTES.md, on a line documenting a LaTeX
bug:

    `\\text{% Change in Real GDP} = ...`

    Liquid syntax error (line 1513): Tag '{%' was not properly terminated

The fix is to wrap the offending text in `{% raw %}` ... `{% endraw %}`.

Only markdown is at risk. The site's HTML has no front matter, so Jekyll copies
it verbatim without rendering.

And only markdown Jekyll actually *reads* is at risk. Anything in `_config.yml`'s
`exclude` list is never opened by the build, so its contents cannot fail a deploy
however malformed they are. This script consults that list rather than keeping a
skip list of its own - it did keep one once, knowing only Jekyll's `_`-prefix
rule, and the result was PH00-011: `seo/05-verification.md` reported as a deploy
risk for months while being excluded from the build, on a line that was itself
documenting this checker. A guard that cries wolf gets ignored, and then it is
not a guard.

The exclude list is parsed by `build_sitemap.py` and imported here rather than
restated. Two copies of the list would drift; two callers of one parser cannot.

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

# Sibling in scripts/. Imported for its _config.yml `exclude` parser and its
# publish rule, so this checker and the sitemap agree on what Jekyll builds.
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import build_sitemap  # noqa: E402

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
    """Every markdown file GitHub Pages will run Liquid over.

    Returns (rendered, skipped). `build_sitemap.published()` applies both rules
    that matter - Jekyll's `_`-prefix rule and `_config.yml`'s `exclude` - so
    there is one definition of "published" in the repo rather than two.

    splitlines() rather than split(): this repo has had Finder duplicates named
    "notes 2.md" appear on disk, and a whitespace split would tear one filename
    into two nonexistent ones.
    """
    ex = build_sitemap.excludes()
    out = subprocess.run(["git", "ls-files", "*.md"], cwd=ROOT,
                         capture_output=True, text=True, check=True).stdout
    tracked = [f for f in out.splitlines() if f]
    rendered = [f for f in tracked if build_sitemap.published(f, ex)]
    return [ROOT / f for f in rendered], len(tracked) - len(rendered)


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
    files, skipped = rendered_files()
    bad = 0
    for path in files:
        for line, msg in check(path):
            bad += 1
            where = f"{path.relative_to(ROOT)}:{line}" if line else \
                    str(path.relative_to(ROOT))
            print(f"  {where}: {msg}", file=sys.stderr)

    for path in files:
        print(f"  checked  {path.relative_to(ROOT)}")
    print(f"\n{len(files)} markdown file(s) checked, {bad} problem(s)"
          f"  [{skipped} excluded from the Jekyll build, not at risk]")

    if bad:
        print("A Liquid error fails the whole GitHub Pages deploy, not just the "
              "page it is on.", file=sys.stderr)
        return 1

    # The empty set is now the CORRECT state, and is asserted elsewhere.
    #
    # This used to fail when there was nothing to check, on the grounds that a
    # checker which checks nothing passes for the wrong reason (D31). That was
    # right while nothing else watched the published surface. It stopped being
    # right when scripts/verify_published_surface.py landed: `.md` is not in its
    # ALLOWED_SUFFIXES, so any markdown file appearing in a published directory
    # fails THAT check, by name, before it can ever reach Jekyll.
    #
    # So the guarantee moved rather than disappeared, and this script is now a
    # latent guard: dormant while the published surface has no markdown on it,
    # and immediately useful the moment a deliberate exception puts one there.
    # Deleting it would throw away the only thing that then checks its syntax.
    if not files:
        print("Nothing to check: no markdown reaches the Jekyll build. That is "
              "asserted by scripts/verify_published_surface.py, which fails on "
              "any .md inside a published directory - so this is a real pass, "
              "not an empty one.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

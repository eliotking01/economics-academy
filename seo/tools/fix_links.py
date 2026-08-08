#!/usr/bin/env python3
"""Rewrite internal links to canonical URL form. Dry-run by default.

    href="/index.html"            ->  href="/"
    href="/<path>/index.html"     ->  href="/<path>/"
    href="https://economicsacademy.co.uk/<path>/index.html"  -> .../<path>/

CLAUDE.md is explicit that scripted prose rebuilds have silently destroyed <a>
tags in this repo before. This is not that. It never parses, re-serialises or
reflows anything: it matches the literal byte sequence `href="..."` with a
regex, replaces only the characters between the quotes, and writes the file back
otherwise untouched. Everything outside an href attribute value - all prose,
whitespace, entities, attribute order, line wrapping - is provably unchanged,
because those bytes are never in the match.

Two safety properties are asserted per file before anything is written:

  1. Removing every href="..." value from old and new must leave two identical
     strings. If it does not, something outside an href moved, and the file is
     skipped and reported.
  2. The count of `href=` occurrences must be unchanged. A dropped or added
     link fails the run.

Usage:
    python3 seo/tools/fix_links.py                  # dry run, summary only
    python3 seo/tools/fix_links.py --diff N         # dry run + N sample diffs
    python3 seo/tools/fix_links.py --apply          # write
    python3 seo/tools/fix_links.py --apply --scripts  # also rewrite generators
"""

from __future__ import annotations

import argparse
import difflib
import re
import subprocess
import sys
from collections import Counter
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
SITE = "https://economicsacademy.co.uk"

HREF_RE = re.compile(r'href="([^"]*)"')
ANY_HREF = re.compile(r"href=")


def canonicalise(value: str) -> str:
    """Return the canonical form of one href value, or it unchanged."""
    v = value
    prefix = ""
    for p in (SITE, "http://economicsacademy.co.uk", "https://www.economicsacademy.co.uk"):
        if v.startswith(p):
            prefix, v = SITE, v[len(p):]
            break
    if not v.startswith("/"):
        return value
    path, sep, tail = v.partition("#")
    path, qsep, query = path.partition("?")
    if path == "/index.html":
        path = "/"
    elif path.endswith("/index.html"):
        path = path[: -len("index.html")]
    else:
        return value
    return f"{prefix}{path}{qsep}{query}{sep}{tail}"


def rewrite(text: str) -> tuple[str, int]:
    n = 0

    def sub(m: re.Match) -> str:
        nonlocal n
        old = m.group(1)
        new = canonicalise(old)
        if new != old:
            n += 1
            return f'href="{new}"'
        return m.group(0)

    return HREF_RE.sub(sub, text), n


def strip_hrefs(text: str) -> str:
    """Everything except href values - the invariant that must not change."""
    return HREF_RE.sub('href=""', text)


def targets(include_scripts: bool) -> list[Path]:
    out = subprocess.run(["git", "-C", str(REPO), "ls-files"],
                         capture_output=True, text=True, check=True).stdout.splitlines()
    files = [REPO / p for p in out
             if p.endswith(".html") and not p.startswith("_working/")]
    if include_scripts:
        files += [REPO / p for p in out if p.startswith("scripts/") and p.endswith(".py")]
    return files


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--diff", type=int, default=0, help="show N sample diffs")
    ap.add_argument("--scripts", action="store_true", help="include scripts/*.py")
    args = ap.parse_args()

    changed, failed, samples = [], [], []
    total = 0
    by_section = Counter()

    for f in sorted(targets(args.scripts)):
        old = f.read_text(encoding="utf-8")
        new, n = rewrite(old)
        if n == 0:
            continue
        rel = f.relative_to(REPO).as_posix()

        # invariant 1: nothing outside an href value moved
        if strip_hrefs(old) != strip_hrefs(new):
            failed.append((rel, "content outside href changed"))
            continue
        # invariant 2: no link gained or lost
        if len(ANY_HREF.findall(old)) != len(ANY_HREF.findall(new)):
            failed.append((rel, "href count changed"))
            continue

        changed.append((rel, n))
        total += n
        by_section[rel.split("/")[0] if "/" in rel else "ROOT"] += n
        if len(samples) < args.diff:
            samples.append((rel, old, new))
        if args.apply:
            f.write_text(new, encoding="utf-8")

    mode = "APPLIED" if args.apply else "DRY RUN"
    print(f"== {mode} ==")
    print(f"files to change      : {len(changed)}")
    print(f"link rewrites        : {total}")
    print(f"files failing checks : {len(failed)}")
    for rel, why in failed:
        print(f"    SKIPPED {rel}: {why}")
    print("\nby section:")
    for k, v in by_section.most_common():
        print(f"  {v:>5}  {k}")

    for rel, old, new in samples:
        print(f"\n--- diff: {rel} " + "-" * (60 - len(rel)))
        diff = difflib.unified_diff(old.splitlines(), new.splitlines(),
                                    fromfile=f"a/{rel}", tofile=f"b/{rel}",
                                    lineterm="", n=1)
        for line in list(diff)[:40]:
            print(line)

    if failed:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

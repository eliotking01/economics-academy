#!/usr/bin/env python3
"""No published page carries an authored inline `style=` attribute.

    python3 scripts/verify_inline_styles.py
    python3 scripts/verify_inline_styles.py --show   # print, don't judge

Pure stdlib. Exit 1 if anything is flagged.

WHY THIS EXISTS
---------------
D18's Q20 item 6 approved moving the site's authored inline styles into CSS
classes, and wave-norm item (f) did it: 322 attributes across 44 files, ending
at 0 on 2026-08-13. Nothing was checking, which is how 322 accumulated one
hand-written page at a time in the first place.

A half-swept item is one no verifier can ever hold at zero, and a zero that
nothing asserts drifts back. That is the argument that decided the hardest
part of (f) - the 96 <th> column widths, where a class genuinely buys nothing
except this check being able to exist. So this is what that trade bought, and
it has to stay in the workflow for the trade to have been worth making.

THE KATEX COUNT IS THE OTHER HALF, AND IT IS THE DANGEROUS ONE
--------------------------------------------------------------
1,187 of the site's inline styles are KaTeX build output - the top, height,
margin-right and vertical-align offsets it emits to position glyphs, on the
two glossary pages and five flashcard decks. DO-NOT-BREAK names them as one of
the four entries hardest to resist undoing, because a sweep for inline styles
hits them first and removing any one breaks a formula silently.

So they are asserted, not merely skipped. EXPECTED_KATEX_PAGES pins the exact
7 paths and their counts. A sweep that "tidied" them turns this red, and so
does a KaTeX upgrade that changes what it emits - the second is a legitimate
change that must be declared here, in the same commit, exactly as
verify_page_shell.py's tables work.

Classification is BY CONSTRUCTION: an attribute is KaTeX output if it sits
anywhere inside an element whose class list holds a token beginning "katex".
Never by page path, never by a hand-maintained list of offsets.
"""

from __future__ import annotations

import argparse
import pathlib
import subprocess
import sys
from html.parser import HTMLParser

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import build_sitemap  # noqa: E402  - for its _config.yml exclude parser

# The seven pages KaTeX writes into, and how many offsets it emits on each.
# Named paths with counts rather than a total, in the spirit of
# build_past_paper_taxonomy.py's EXPECTED = {"edexcel": 87, "aqa": 79}: a total
# alone would let one page lose 20 while another gained 20.
EXPECTED_KATEX_PAGES = {
    "revision-notes/glossary/aqa/index.html": 609,
    "revision-notes/glossary/edexcel-a/index.html": 488,
    "flashcards/edexcel-a/theme-2/index.html": 22,
    "flashcards/edexcel-a/theme-3/index.html": 21,
    "flashcards/aqa/micro/index.html": 19,
    "flashcards/aqa/macro/index.html": 15,
    "flashcards/edexcel-a/theme-1/index.html": 13,
}

# Authored inline styles. 322 across 44 files until 2026-08-13; 0 since.
#
# NOT a dict of allowed pages, deliberately. There is no legitimate authored
# inline style on this site - CLAUDE.md's CSS conventions say "No inline
# `style` attributes - extract a class" without exception - so the right shape
# for this is a bare zero. If one is ever genuinely needed, that is a decision
# to record in DECISIONS.md and a named exception to add here with its reason,
# not a number to nudge.
EXPECTED_AUTHORED = 0

VOID = {"meta", "link", "br", "hr", "img", "input", "source", "col", "area",
        "base", "embed", "param", "track", "wbr"}


class Census(HTMLParser):
    """Every style= attribute, split into KaTeX-descended and authored."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack: list[tuple[str, bool]] = []
        self.katex_depth = 0
        self.katex: list[str] = []
        self.authored: list[tuple[int, str, str]] = []

    def _see(self, tag, attrs, self_closing):
        d = {}
        for k, v in attrs:
            d.setdefault(k.lower(), v)
        opens_katex = any(c.startswith("katex")
                          for c in (d.get("class") or "").split())
        style = d.get("style")
        if style is not None:
            if self.katex_depth or opens_katex:
                self.katex.append(style)
            else:
                self.authored.append((self.getpos()[0], tag, style))
        if not self_closing and tag not in VOID:
            self.stack.append((tag, opens_katex))
            if opens_katex:
                self.katex_depth += 1

    def handle_starttag(self, tag, attrs):
        self._see(tag, attrs, False)

    def handle_startendtag(self, tag, attrs):
        self._see(tag, attrs, True)

    def handle_endtag(self, tag):
        # Walk back to the matching open tag. The site's HTML is well-formed -
        # verify_html.py is the workflow's first step - but an unclosed inline
        # tag must not strand katex_depth above 0 and silence the whole check.
        for i in range(len(self.stack) - 1, -1, -1):
            if self.stack[i][0] == tag:
                for _, was_katex in self.stack[i:]:
                    if was_katex:
                        self.katex_depth -= 1
                del self.stack[i:]
                return


def published_pages() -> list[str]:
    ex = build_sitemap.excludes()
    out = subprocess.run(["git", "ls-files", "*.html"], cwd=ROOT,
                         capture_output=True, text=True, check=True).stdout.split()
    return sorted(f for f in out if build_sitemap.published(f, ex))


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--show", action="store_true",
                    help="print the measured counts and exit 0, for reseeding "
                         "EXPECTED_KATEX_PAGES after a deliberate change")
    args = ap.parse_args()

    problems: list[str] = []
    authored: dict[str, list[tuple[int, str, str]]] = {}
    katex: dict[str, int] = {}

    paths = published_pages()
    for rel in paths:
        c = Census()
        c.feed((ROOT / rel).read_text(encoding="utf-8", errors="replace"))
        c.close()
        if c.authored:
            authored[rel] = c.authored
        if c.katex:
            katex[rel] = len(c.katex)

    total_authored = sum(len(v) for v in authored.values())
    total_katex = sum(katex.values())
    print(f"{len(paths)} published pages; "
          f"{total_authored + total_katex} inline style= attributes: "
          f"{total_katex} KaTeX output, {total_authored} authored")

    if args.show:
        print("\nEXPECTED_KATEX_PAGES = {")
        for rel, n in sorted(katex.items(), key=lambda kv: -kv[1]):
            print(f'    "{rel}": {n},')
        print("}")
        for rel, rows in sorted(authored.items()):
            print(f"\n{rel}: {len(rows)} authored")
            for line, tag, style in rows:
                print(f"    :{line} <{tag} style={style!r}>")
        print("\n--show: counts printed, nothing judged")
        return 0

    # ---- authored: must be none
    if total_authored != EXPECTED_AUTHORED:
        problems.append(
            f"{total_authored} authored inline style= attribute(s) on "
            f"{len(authored)} page(s), expected {EXPECTED_AUTHORED}")
        for rel, rows in sorted(authored.items()):
            for line, tag, style in rows[:4]:
                problems.append(f"    {rel}:{line}  <{tag} style=\"{style}\">")
            if len(rows) > 4:
                problems.append(f"    {rel}: ... and {len(rows) - 4} more")
        problems.append(
            "    CLAUDE.md: no inline style attributes - extract a class, "
            "scoped under the page's wrapper. AND CHECK THE CASCADE: an "
            "inline style outranks every class selector, so the class can "
            "lose to a rule the attribute was beating. Two of wave-norm "
            "item (f)'s last 35 did exactly that. "
            "docs/audit/scripts/harness/computed_style_diff.py measures it.")

    # ---- KaTeX: must be exactly what it was, page by page
    for rel in sorted(set(katex) | set(EXPECTED_KATEX_PAGES)):
        want = EXPECTED_KATEX_PAGES.get(rel, 0)
        got = katex.get(rel, 0)
        if got == want:
            continue
        if want and not got:
            problems.append(
                f"{rel}: {want} KaTeX inline styles -> 0. Every formula on "
                f"this page has lost its glyph positioning. This is "
                f"DO-NOT-BREAK's 'build output, not tidiness' entry.")
        elif not want:
            problems.append(
                f"{rel}: KaTeX output has appeared on a page that had none "
                f"({got}). If a new page pre-renders formulae, add it to "
                f"EXPECTED_KATEX_PAGES in the same commit.")
        else:
            problems.append(
                f"{rel}: KaTeX inline styles {want} -> {got}. If KaTeX or the "
                f"formulae changed on purpose, reseed with --show in the same "
                f"commit.")

    if problems:
        print(f"\nFAIL: {len(problems)} problem(s):", file=sys.stderr)
        for p in problems:
            print(f"  {p}", file=sys.stderr)
        return 1

    print(f"0 authored inline styles; {total_katex} KaTeX offsets across "
          f"{len(EXPECTED_KATEX_PAGES)} pages, all as recorded")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

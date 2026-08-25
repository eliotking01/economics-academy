#!/usr/bin/env python3
"""Gate 1 proof: the mock's content region is the live page's, byte for byte
in text terms.

    python3 _working/notes-redesign/check_content_identity.py

Compares revision-notes/edexcel-theme-1/1-2-2-demand.html (the live generated
page) against _working/notes-redesign/1-2-2-demand.html (the mock) over the
CONTENT REGION - the <h1>, the spec-alert and every top-level <section>, in
order:

  1. tag-stripped, whitespace-squashed text: must be identical;
  2. the <img> src and alt lists, in order: must be identical.

Chrome (meta line, byline, contents list, tail, prev/next) is deliberately
outside the comparison: it is generated furniture, and the redesign changes
it on purpose with every string listed in PROPOSAL.md. Standard library only.
"""

from __future__ import annotations

import difflib
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
LIVE = ROOT / "revision-notes/edexcel-theme-1/1-2-2-demand.html"
MOCK = ROOT / "_working/notes-redesign/1-2-2-demand.html"

TAG = re.compile(r"<[^>]+>")
SECTION = re.compile(r"<section>.*?</section>", re.S)
H1 = re.compile(r"<h1>(.*?)</h1>", re.S)
SPEC = re.compile(r'<div class="spec-alert">.*?</div>', re.S)
IMG = re.compile(r"<img\b[^>]*>", re.S)
ATTR = {name: re.compile(rf'{name}="([^"]*)"') for name in ("src", "alt")}


def squash(html: str) -> str:
    return " ".join(TAG.sub(" ", html).split())


def content(page: str) -> tuple[str, list[tuple[str, str]]]:
    # Cut to the notes container first: the baked header above it mentions
    # literal tag names inside comments, which the section regex would match.
    start = page.index('<div class="notes-container">')
    page = page[start:page.index("</main>", start)]
    h1 = H1.search(page)
    spec = SPEC.search(page)
    sections = SECTION.findall(page)
    if not (h1 and spec and sections):
        sys.exit("could not find h1 / spec-alert / sections - page shape moved?")
    text = " ".join([squash(h1.group(1)), squash(spec.group(0))]
                    + [squash(s) for s in sections])
    images = []
    for m in IMG.finditer("".join(sections)):
        tag = m.group(0)
        src = ATTR["src"].search(tag)
        alt = ATTR["alt"].search(tag)
        images.append((src.group(1) if src else "?", alt.group(1) if alt else "?"))
    return text, images


live_text, live_imgs = content(LIVE.read_text(encoding="utf-8"))
mock_text, mock_imgs = content(MOCK.read_text(encoding="utf-8"))

ok = True
if live_text != mock_text:
    ok = False
    print("TEXT DIFFERS:")
    for line in difflib.unified_diff(
            live_text.split(". "), mock_text.split(". "),
            "live", "mock", lineterm=""):
        print("  " + line)
else:
    print(f"text identical: {len(live_text)} characters, "
          f"{len(live_text.split())} words")

if live_imgs != mock_imgs:
    ok = False
    print("IMAGES DIFFER:")
    print(f"  live: {live_imgs}")
    print(f"  mock: {mock_imgs}")
else:
    print(f"images identical: {len(live_imgs)} (src, alt) pairs, same order")

print("CONTENT IDENTITY " + ("OK" if ok else "FAILED"))
sys.exit(0 if ok else 1)

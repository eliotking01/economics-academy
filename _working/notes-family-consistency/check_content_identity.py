#!/usr/bin/env python3
"""Prove the three redesigned pages carry identical economics content.

    python3 _working/notes-family-consistency/check_content_identity.py [BASE]

For each page, takes the version at BASE (default: the merge base with main,
i.e. the pre-redesign page) and the working-tree version, cuts the content
region, removes the navigation chrome that changed by design (the old
Contents jump-list / new "On this page" rail, and the old notes-cta / new
Carry-on-revising tail - every one of those strings is declared in the
commit's Text-Change trailers and listed in PROPOSAL.md), strips tags,
normalises whitespace and diffs. Also compares the (src, alt) pair of every
<img>, in order. Zero differences or a non-zero exit.

The same method as _working/notes-redesign/check_content_identity.py, which
proved the topic-page redesign at Gates 1 and 3.
"""
import difflib
import html as htmllib
import pathlib
import re
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]

PAGES = [
    "revision-notes/microeconomics-diagrams.html",
    "revision-notes/macroeconomics-diagrams.html",
    "revision-notes/macro-application/index.html",
]

# The navigation chrome each version carries, removed before comparing. The
# patterns are anchored on the block's opening tag and its own closing tag.
CHROME = [
    # old: the Contents jump-list section (galleries)
    re.compile(r'<section>\s*<h2>Contents</h2>.*?</section>', re.S),
    # new: the contents list / rail (all three)
    re.compile(r'<nav class="topic-contents".*?</nav>', re.S),
    # old: the notes-cta button box (all three)
    re.compile(r'<div class="notes-cta">.*?</div>', re.S),
    # new: the Carry on revising unit and the services sentence (all three)
    re.compile(r'<nav class="topic-next".*?</nav>', re.S),
    re.compile(r'<p class="topic-services">.*?</p>', re.S),
    # new: the filter bar's two country group labels (macro-application) -
    # the chips themselves are NOT stripped, so their text is still compared
    re.compile(r'<span class="filter-topic-group__label">.*?</span>', re.S),
]

TAG = re.compile(r"<[^>]+>")
IMG = re.compile(r"<img\b[^>]*?>", re.S)
ATTR = re.compile(r'(src|alt)="([^"]*)"')


def region(text: str) -> str:
    start = text.index('<div class="notes-container">')
    end = text.rindex("</main>")
    cut = text[start:end]
    for rx in CHROME:
        cut = rx.sub(" ", cut)
    # script content is not visible text
    cut = re.sub(r"<script\b.*?</script>", " ", cut, flags=re.S)
    return cut


def words(cut: str) -> list[str]:
    return htmllib.unescape(TAG.sub(" ", cut)).split()

def images(cut: str) -> list[tuple[str, str]]:
    out = []
    for m in IMG.finditer(cut):
        d = dict(ATTR.findall(m.group(0)))
        out.append((d.get("src", ""), d.get("alt", "")))
    return out


def main() -> int:
    base = sys.argv[1] if len(sys.argv) > 1 else subprocess.run(
        ["git", "merge-base", "main", "HEAD"], cwd=ROOT,
        capture_output=True, text=True, check=True).stdout.strip()
    failed = False
    for page in PAGES:
        old = subprocess.run(["git", "show", f"{base}:{page}"], cwd=ROOT,
                             capture_output=True, text=True, check=True).stdout
        new = (ROOT / page).read_text(encoding="utf-8")
        ow, nw = words(region(old)), words(region(new))
        oi, ni = images(region(old)), images(region(new))
        if ow != nw:
            failed = True
            print(f"{page}: TEXT DIFFERS")
            for line in list(difflib.unified_diff(ow, nw, lineterm=""))[:40]:
                print("   ", line)
        else:
            print(f"{page}:")
            print(f"  text identical: {len(' '.join(nw))} characters, "
                  f"{len(nw)} words")
        if oi != ni:
            failed = True
            print(f"{page}: IMAGES DIFFER {len(oi)} -> {len(ni)}")
            for a, b in zip(oi, ni):
                if a != b:
                    print("   ", a, "->", b)
        else:
            print(f"  images identical: {len(ni)} (src, alt) pairs, same order")
    print("CONTENT IDENTITY OK" if not failed else "CONTENT IDENTITY FAILED")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())

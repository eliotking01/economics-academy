#!/usr/bin/env python3
"""Link the Edexcel notes pages back to the diagram gallery that features them.

The two galleries earn 4,083 impressions between them on ONE inbound link each,
and that link is the runtime-injected header - so a crawler that does not
execute JavaScript sees none at all. Meanwhile they link OUT to 47 notes pages
and not one of those links back. See seo/07-link-graph.md.

EDEXCEL ONLY, and that is not an oversight. Both galleries say so in their own
intro - "A complete collection of Microeconomics diagrams from Edexcel Theme 1
and Theme 3 revision notes" - and all 47 of their notes links go to
/revision-notes/edexcel-theme-*/. Linking an AQA notes page to them would be a
cross-board link of exactly the kind that resolves fine, 404s nothing, passes
every assertion, and sends a student to the wrong board's content.

    micro gallery  <- Edexcel Theme 1 and Theme 3
    macro gallery  <- Edexcel Theme 2 and Theme 4

WHICH PAGES: only the ones a gallery already links to. That is what makes the
link honest - the page's own diagram is in the gallery being linked, so this is
a reciprocal link rather than a directory entry. Pages the galleries do not
feature get nothing.

WORDING: the sentence never claims the page has a diagram of its own. One of
the 47, 3-4-6-monopsony.html, is featured by the micro gallery but has no <img>
on it, and a sentence opening "This diagram..." would have been false there.

Anchor text varies by theme so neither gallery collects 26 identically-anchored
inbound links.

Idempotent: a page already carrying the marker class is skipped.

    python3 seo/tools/add_diagram_gallery_links.py --dry-run
    python3 seo/tools/add_diagram_gallery_links.py --dry-run --diff 3
    python3 seo/tools/add_diagram_gallery_links.py
"""

from __future__ import annotations

import argparse
import difflib
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
NOTES = REPO / "revision-notes"
MARKER = "notes-diagrams-link"

GALLERIES = {
    "micro": "/revision-notes/microeconomics-diagrams.html",
    "macro": "/revision-notes/macroeconomics-diagrams.html",
}

# theme directory -> (gallery, the sentence). Two wordings per gallery so the
# 26 micro links do not all read identically; each is factual on its own and
# neither asserts anything about the individual page.
SENTENCES = {
    "edexcel-theme-1": ("micro",
        'Every Theme 1 and Theme 3 diagram in one place: '
        '<a href="{href}">Microeconomics Diagrams</a>.'),
    "edexcel-theme-3": ("micro",
        'The full Theme 1 and Theme 3 set is collected in '
        '<a href="{href}">all the Microeconomics diagrams</a>.'),
    "edexcel-theme-2": ("macro",
        'Every Theme 2 and Theme 4 diagram in one place: '
        '<a href="{href}">Macroeconomics Diagrams</a>.'),
    "edexcel-theme-4": ("macro",
        'The full Theme 2 and Theme 4 set is collected in '
        '<a href="{href}">all the Macroeconomics diagrams</a>.'),
}

# Insert after the last of these, so the line closes the block stack rather
# than interrupting it. Same anchoring approach as
# scripts/append_past_papers_link.py.
ANCHORS = ['<div class="notes-questions-link', '<div class="notes-cta"']


def find_close(text: str, start: int) -> int:
    """Index just past the </div> closing the div that opens at `start`."""
    depth = 0
    i = start
    while i < len(text):
        open_at = text.find("<div", i)
        close_at = text.find("</div>", i)
        if close_at == -1:
            return -1
        if open_at != -1 and open_at < close_at:
            depth += 1
            i = open_at + 4
            continue
        depth -= 1
        if depth == 0:
            return close_at + len("</div>")
        i = close_at + len("</div>")
    return -1


def featured_pages() -> dict[str, str]:
    """notes page (repo-relative) -> gallery key, read FROM the galleries."""
    out: dict[str, str] = {}
    for key, href in GALLERIES.items():
        text = (REPO / href.lstrip("/")).read_text()
        for m in re.findall(r'href="(/revision-notes/edexcel-theme-\d/[^"]+\.html)"',
                            text):
            out[m.lstrip("/")] = key
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--diff", type=int, default=0)
    args = ap.parse_args()

    featured = featured_pages()
    changed: list[tuple[Path, str, str]] = []
    problems: list[str] = []
    skipped = 0

    for rel, gallery in sorted(featured.items()):
        page = REPO / rel
        if not page.is_file():
            problems.append(f"{rel}: featured by the {gallery} gallery but not on disk")
            continue
        theme = Path(rel).parts[1]
        entry = SENTENCES.get(theme)
        if entry is None:
            problems.append(f"{rel}: theme {theme!r} has no gallery mapping")
            continue
        want_gallery, template = entry
        # The gallery that features the page and the gallery its theme maps to
        # must be the same, or the mapping above is wrong for this page.
        if want_gallery != gallery:
            problems.append(f"{rel}: featured by {gallery!r} but theme "
                            f"{theme!r} maps to {want_gallery!r}")
            continue

        text = page.read_text()
        if MARKER in text:
            skipped += 1
            continue

        found = [text.rfind(a) for a in ANCHORS if text.rfind(a) != -1]
        start = max(found) if found else -1
        if start == -1:
            problems.append(f"{rel}: no notes-questions-link or notes-cta to anchor to")
            continue
        end = find_close(text, start)
        if end == -1:
            problems.append(f"{rel}: could not find the closing </div>")
            continue

        # Indent from notes-cta, not from the insertion point. The past-paper
        # block that append_past_papers_link.py writes sits at 48 spaces on
        # some pages, and inheriting that would carry the oddity forward.
        cta = text.find('<div class="notes-cta"')
        ref = cta if cta != -1 else start
        indent = " " * (ref - text.rfind("\n", 0, ref) - 1)
        sentence = template.format(href=GALLERIES[gallery])
        block = (f'\n{indent}<p class="{MARKER}">\n'
                 f"{indent}  {sentence}\n"
                 f"{indent}</p>")
        changed.append((page, text, text[:end] + block + text[end:]))

    print(f"pages featured by a gallery : {len(featured)}")
    print(f"pages to change             : {len(changed)}")
    print(f"already done                : {skipped}")
    print(f"problems                    : {len(problems)}")
    for p in problems[:10]:
        print(f"   {p}")

    for path, old, new in changed[: args.diff]:
        r = path.relative_to(REPO)
        print(f"\n{'=' * 70}\n--- {r}\n{'=' * 70}")
        for line in difflib.unified_diff(old.split("\n"), new.split("\n"),
                                         lineterm="", n=3,
                                         fromfile=str(r), tofile=str(r)):
            print(line)

    if problems:
        print("\nABORTED - nothing written.", file=sys.stderr)
        return 1
    if args.dry_run:
        print("\nDRY RUN - nothing written.")
        return 0

    for path, _, new in changed:
        path.write_text(new)
    print(f"\nWritten: {len(changed)} files.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

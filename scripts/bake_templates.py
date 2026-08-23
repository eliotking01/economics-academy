#!/usr/bin/env python3
"""Bake the header, footer, script tail and analytics loader into the pages no generator owns.

    python3 scripts/bake_templates.py            # dry run, writes nothing
    python3 scripts/bake_templates.py --apply
    python3 scripts/bake_templates.py --list
    python3 scripts/bake_templates.py --prettierignore > .prettierignore

Wave 2 Phase 7. Five generators call page_shell.bake() on the 446 pages they
write. The other 17 published pages are hand-written and nothing rebuilds
them, so without this Phase 7 would half-land: two of those 17 are
/past-papers/edexcel-b/ and /past-papers/ocr/, which between them earn 291
clicks and 21,131 impressions - more than anything on the site outside the
homepage - and they would have kept a nav that needs JavaScript.

**Wave 4.10 added the script tail**, for exactly the same reason. The tail
went from seven scripts to four; the other 446 pages take it from
page_shell.SCRIPT_TAIL on a rebuild, and without this these 17 would have
gone on requesting a jQuery that is no longer in the repo. Same two pages,
same argument, same answer. Wave 4.11 took it from four to two the same way.

**2026-08-23 added the analytics block in the <head>** (page_shell.GTAG), for
the third time the same reason: the unconditional gtag snippet became a
consent-gated loader on the 446 generated pages, and without sync_gtag() these
17 - index.html among them - would have gone on setting GA4 cookies before
anyone was asked.

**Later the same day, the stylesheet block** (page_shell.stylesheet_block()):
the performance pass self-hosted the fonts, so the 446 generated heads lost
the Google Fonts preconnect pair and stylesheet and gained a preload of the
body face. sync_fonts() does the same to these 17, anchored on the 4db232c
hoist comment at one end and the main.css link at the other. A page's own
stylesheets after main.css are outside the region and untouched.

    root         9   index, tutoring, marking, about, faq, contact, privacy,
                     confirmation, 404. Permanently out of scope for the
                     <head> migration by D34, which is about nine one-off
                     <head> shapes and says nothing about the body.
    past-papers  5   the hub and the four board pages
    notes-other  3   revision-notes/index.html and the two diagram galleries

**This writes markup, never prose.** It replaces one byte-exact anchor -
`<div id="header-placeholder"></div>`, present exactly once on 463 of 463
pages - with the contents of templates/header.html, and the same for the
footer. It does not parse the page and it does not re-serialise it, so it
cannot do the thing CLAUDE.md records scripted rewrites doing here before:
destroy an <a> tag it did not understand. Everything above the anchor and
everything below it is copied through untouched.

**It is re-runnable, and that is the point.** page_shell.bake() accepts a
block it wrote earlier as readily as an untouched placeholder, so editing the
nav is: edit templates/header.html, run the generators, run this, commit. If
it could only run once, these 17 pages would drift away from the other 446
the first time the nav changed, silently.

Dry run by default, like the five seo/tools/ mutators and for the same
reason: a no-flag re-run must stay harmless.

Standard library only.
"""

from __future__ import annotations

import argparse
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import page_shell  # noqa: E402
import reseed_util  # noqa: E402
import site_layout as shell_check  # noqa: E402  - family_of(), pages()

# The families no generator writes. Everything else is rebuilt from source and
# picks the header up on the next run; see site_layout.family_of().
UNGENERATED = ("root", "past-papers", "notes-other")

# Measured, and asserted rather than assumed: if a generator ever takes one of
# these over - or a new hand-written page appears - the count moves and this
# script says so instead of quietly doing different work. It is a pin against
# an UNDECLARED change, not a count anyone should remember: a deliberate change
# is `--reseed`, which rewrites this line from the measured set and prints the
# diff. Two other things are derived from this set and must move with it -
# .prettierignore (`--prettierignore`) and HAND_WRITTEN in
# .claude/hooks/block-generated.py - which is why the change must be declared.
EXPECTED = 17


# Scripts that used to be in the tail and are not any more. Declared, because
# the sync below has to be able to tell "a stale tail entry, delete it" from
# "this page's own script, leave it alone" - index.html carried reviews.js and
# reviews-render.js inside its tail until the 2026-08-14 home-page revamp made
# the testimonials static HTML. No page has own-tail scripts today; the
# distinction stays because the next one might.
#
# Wave 4.10 emptied this of jQuery, dropotron and util.js and renamed
# inject-templates.js to nav.js. Anything removed from page_shell.SCRIPT_TAIL
# in future belongs here in the same commit, or these 17 pages keep loading it
# after the other 446 have stopped.
#
# Wave 4.11 added browser.min.js and breakpoints.min.js, which is that rule
# being followed rather than restated: both files are deleted from the repo, so
# without these two lines /past-papers/edexcel-b/ and /past-papers/ocr/ would
# request two 404s on every page view.
LEGACY_TAIL = (
    "/js/jquery.min.js",
    "/js/jquery.dropotron.min.js",
    "/js/components/inject-templates.js",
    "/js/util.js",
    "/js/browser.min.js",
    "/js/breakpoints.min.js",
)

SCRIPT_RE = re.compile(r'^([ \t]*)<script src="([^"]+)"></script>$')


def sync_script_tail(text: str) -> str:
    """Rewrite the page's script tail from page_shell.SCRIPT_TAIL.

    The region runs from the first `<script src>` naming a current or former
    tail entry to the last. Inside it, current entries are re-emitted in
    SCRIPT_TAIL's order, former entries are dropped, and anything else is the
    page's own and is kept, in its original order, after them.

    Line-based and anchored on exact tags, so it cannot touch anything else on
    the page - the same property the header bake has, and for the same reason.
    """
    lines = text.split("\n")
    known = set(page_shell.SCRIPT_TAIL) | set(LEGACY_TAIL)

    hits = [i for i, ln in enumerate(lines)
            if (m := SCRIPT_RE.match(ln)) and m.group(2) in known]
    if not hits:
        return text
    first, last = hits[0], hits[-1]
    indent = SCRIPT_RE.match(lines[first]).group(1)

    # Everything in the region that is neither a current nor a former tail
    # entry: nothing today - the home-page revamp deleted index.html's two
    # review scripts. Kept for the next page that carries its own.
    theirs = [ln for ln in lines[first:last + 1]
              if not ((m := SCRIPT_RE.match(ln)) and m.group(2) in known)]

    rebuilt = [f'{indent}<script src="{s}"></script>'
               for s in page_shell.SCRIPT_TAIL] + theirs
    return "\n".join(lines[:first] + rebuilt + lines[last + 1:])


# The <head> analytics block, the one region this script rewrites ABOVE the
# header. Both the block it replaces and the block it writes begin with a
# `<!-- Google ...` comment line and contain the single `gtag("config", ...)`
# call followed, some lines later, by the `</script>` that closes the block:
# the old pair (an external <script async src=gtag.js> then an inline
# snippet) and the new loader (one inline <script>) alike. The region is
# located by those two anchors, which is what makes the sync re-runnable -
# an already-current page matches itself and is rewritten to itself.
#
# The old pair had one byte-level variant - four root pages carried it without
# the blank line before gtag("config") - which is why this is anchored on
# lines rather than on a literal of the old block.
GTAG_START = re.compile(r'^[ \t]*<!-- Google (?:tag \(gtag\.js\)|Analytics) ', re.M)
GTAG_CONFIG = re.compile(r'gtag\("config", "' + re.escape(page_shell.GA_ID) + r'"\);')
GTAG_END = re.compile(r'[ \t]*</script>[ \t]*\n')


FONTS_START = "    <!-- Linked here rather than @imported from main.css"
FONTS_END = '<link rel="stylesheet" href="/css/main.css" />'


def sync_fonts(text: str) -> str:
    """Rewrite the page's stylesheet block from page_shell.stylesheet_block().

    The region runs from the 4db232c hoist comment to the main.css link,
    inclusive - exactly the lines page_shell.render_head() emits between the
    favicons and a page's own stylesheets: the comment, any extra preconnect,
    the body-face preload, fontawesome, main.css. Same anchoring discipline
    as sync_gtag(): exact markers, no parsing, nothing outside touched, and a
    page without both markers is returned unchanged for verify_page_shell.py
    and verify_css_load_order.py to report.

    Extra preconnects inside the region are kept: tutoring.html's Calendly
    pair sits elsewhere in its head today, but the shell honours
    `extraPreconnects` on generated pages and this keeps the same promise.
    """
    head_end = text.find("</head>")
    if head_end < 0:
        return text
    a = text.find(FONTS_START, 0, head_end)
    if a < 0:
        return text
    b = text.find(FONTS_END, a, head_end)
    if b < 0:
        return text
    b += len(FONTS_END)
    region = text[a:b]
    extra = re.findall(r'<link rel="preconnect" href="([^"]+)"', region)
    extra = [h for h in extra
             if h not in ("https://fonts.googleapis.com", "https://fonts.gstatic.com")]
    return text[:a] + page_shell.stylesheet_block(extra) + text[b:]


def sync_gtag(text: str) -> str:
    """Rewrite the page's <head> analytics block from page_shell.GTAG.

    Anchored on exact markers, never parsed, and it touches nothing outside
    the region - the same property sync_script_tail() has. A page with no
    recognisable block is returned unchanged rather than given one: a missing
    block is verify_page_shell.py check 4's job to report, not this script's
    job to guess at.
    """
    head_end = text.find("</head>")
    if head_end < 0:
        return text
    start = GTAG_START.search(text, 0, head_end)
    if not start:
        return text
    config = GTAG_CONFIG.search(text, start.start(), head_end)
    if not config:
        return text
    end = GTAG_END.search(text, config.end(), head_end)
    if not end:
        return text
    return text[:start.start()] + page_shell.GTAG + "\n" + text[end.end():]


def targets() -> list[str]:
    return [p for p in shell_check.pages()
            if shell_check.family_of(p) in UNGENERATED]


def prettierignore(paths: list[str]) -> str:
    """The body of the repo's .prettierignore, derived rather than typed.

    Two traps, both recorded in docs/HISTORY.md and DO-NOT-BREAK: Prettier
    reformats the baked header inside the hand-written pages (so bake_templates
    must run AFTER it), and it must never touch revision-notes/index.html,
    whose head is GSC-frozen (D50). Listing the pages here means a stray
    `npx prettier --write .` skips them instead of silently rewrapping the
    nav on 17 pages. The generated notes pages are listed for the same reason
    DO-NOT-BREAK gives for their generator running no Prettier at all: a
    reflow can move a line break across an inline tag and turn
    `<strong>word</strong>s` into "word s".
    """
    L = [
        "# GENERATED by: python3 scripts/bake_templates.py --prettierignore > .prettierignore",
        "# Do not edit by hand; re-run that command when the hand-written page set",
        "# changes (it is bake_templates.py's own list, so the two cannot drift).",
        "#",
        "# What Prettier must never touch, and why (docs/HISTORY.md, DO-NOT-BREAK):",
        "#  - the hand-written pages: Prettier rewraps the baked header/footer",
        "#    block inside them, which verify_page_shell.py check 9 then rejects.",
        "#    revision-notes/index.html is additionally GSC-frozen (D50).",
        "#  - the generated notes pages: build_notes_pages.py deliberately runs no",
        "#    Prettier over a prose slice - a reflow can move a line break across",
        "#    an inline tag boundary. The glossary pages are NOT listed: their",
        "#    generator formats them on purpose.",
        "#",
        "# The three generators that DO run Prettier (glossary, flashcards,",
        "# past-paper-questions) are unaffected: none of their output is here.",
        "",
        "# Every pattern is anchored with a leading slash. gitignore syntax, which",
        "# this file uses, matches an unanchored `index.html` at ANY depth - and",
        "# an unanchored version of this list made the generators skip their own",
        "# flashcards/index.html and 90 past-paper-questions pages. Measured.",
        "",
        "# The hand-written pages, from bake_templates.py:",
    ]
    L += ["/" + p for p in paths]
    L += [
        "",
        "# The generated notes pages (everything under revision-notes/ except the",
        "# glossary, which is the one notes family its generator formats):",
        "/revision-notes/**",
        "!/revision-notes/glossary/",
        "!/revision-notes/glossary/**",
    ]
    return "\n".join(L) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--apply", action="store_true",
                    help="write the files (default: report and write nothing)")
    ap.add_argument("--list", action="store_true",
                    help="print the pages this owns and stop")
    ap.add_argument("--prettierignore", action="store_true",
                    help="print the body of .prettierignore - these pages "
                         "plus what must never be formatted - and stop")
    ap.add_argument("--reseed", action="store_true",
                    help="rewrite EXPECTED in this file from the measured page "
                         "set, print the diff and stop. For a DELIBERATE new "
                         "or removed hand-written page, in the same commit - "
                         "then regenerate .prettierignore and update "
                         ".claude/hooks/block-generated.py's HAND_WRITTEN.")
    args = ap.parse_args()

    paths = targets()
    if args.list:
        for p in paths:
            print(f"  {shell_check.family_of(p):12} {p}")
        print(f"{len(paths)} pages")
        return 0
    if args.prettierignore:
        print(prettierignore(paths), end="")
        return 0
    if args.reseed:
        reseed_util.rewrite(__file__, "EXPECTED", repr(len(paths)))
        print("Now: python3 scripts/bake_templates.py --prettierignore > "
              ".prettierignore, and update HAND_WRITTEN in "
              ".claude/hooks/block-generated.py.")
        return 0

    if len(paths) != EXPECTED:
        print(f"error: expected {EXPECTED} ungenerated published pages, "
              f"found {len(paths)}. If that is right, change EXPECTED in the "
              f"same commit that changes the page set.", file=sys.stderr)
        for p in paths:
            print(f"  {shell_check.family_of(p):12} {p}", file=sys.stderr)
        return 1

    changed, already = [], 0
    for rel in paths:
        path = ROOT / rel
        before = path.read_text(encoding="utf-8")
        after = sync_fonts(sync_gtag(sync_script_tail(page_shell.bake(before, rel))))
        if after == before:
            already += 1
            continue
        changed.append(rel)
        if args.apply:
            path.write_text(after, encoding="utf-8")

    verb = "baked" if args.apply else "WOULD BAKE"
    for rel in changed:
        print(f"  {verb} {rel}")
    print(f"{len(paths)} pages: {len(changed)} {'changed' if args.apply else 'would change'}, "
          f"{already} already current")
    if not args.apply and changed:
        print("dry run - nothing written. Re-run with --apply.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

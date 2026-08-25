#!/usr/bin/env python3
"""Render the migrated notes pages from notes-data/. Wave 2 Phases 3 and 5.

    python3 scripts/build_notes_pages.py
    python3 scripts/build_notes_pages.py --check    # compare, write nothing
    python3 scripts/build_notes_pages.py --out DIR  # build somewhere else

The <head> comes from scripts/page_shell.py, which is the point of the whole
wave: changing the header on every migrated page becomes one edit. The page
body is the byte slice the extractor took, emitted verbatim.

Every family lives under notes-data/ and is found by globbing rather than by
being listed, so adding a board directory is an extraction and a rebuild, with
no edit here. Each record carries its own `path`, so this file needs no
knowledge of where a family lives.

THE EXCEPTIONS TO "EMITTED UNCHANGED", ADDED 2026-08-21
-------------------------------------------------------
The 166 TOPIC slices - not the hubs, not macro-application - are spliced with
a previous/next navigation row at each end of .notes-container. See
with_topic_nav() for why that happens here rather than in the 166 source
files, and scripts/notes_sequence.py for where the chain comes from.

Later the same day the notes SEO pass added four more, all of them from
scripts/notes_extras.py and all for the same reason: a spec sub-label and an
update date under the <h1>, a stable id on every <h2>, a table of contents
where a page has four or more sections, and a related-topics block carrying
the twin on the other board. On 2026-08-22 two more joined them from the same
module, once Eliot had supplied the wording: an author byline under the
sub-label and an "About the author" box.

On 2026-08-23 the topic-tail redesign made the WHOLE tail generated: the
three free next steps (quiz, flashcards, past-paper questions - counts and
labels derived from questions-data/ and the past-paper bank's source files)
and the one services sentence now come from notes_extras.with_tail(), and
the legacy button box and resource blocks were stripped out of the 166
slices in the same change. A slice ends at its last </section> (plus, on 47
Edexcel pages, one diagram-gallery paragraph that the tail re-homes).

The slices on disk are still verbatim byte slices and are still never written
to by any generator; what changes is only what this generator wraps around
them. Every one of these blocks fails the build rather than degrading if its
anchor stops matching - notes_extras.fail().

DIAGRAMS ARE OFFERED AS WEBP FIRST (2026-08-23)
-----------------------------------------------
Every `<img src="/images/diagrams/X.png">` in a slice is emitted inside a
`<picture>` whose `<source type="image/webp">` points at the lossless twin
`images/diagrams/X.webp` that scripts/build_diagram_webp.py writes (32%
smaller across the set). The `<img>` bytes are untouched - the wrapper goes
around them at render time, exactly as the previous/next rows go around the
container - so the PNG stays the fallback at its URL and the slice on disk
stays a verbatim slice. A PNG with no twin is emitted bare; verify_image_
dimensions.py is what insists every PNG has one of the same size.

Since the notes redesign (2026-08-25, D61) the TOPIC pages - not the hubs -
get two more things from the same transform: each diagram is wrapped in an
`<a class="diagram-zoom">` pointing at the PNG (tap-to-enlarge that works
with JavaScript off; js/components/notes.js upgrades it to a <dialog>
lightbox), and the FIRST diagram on a page gains `fetchpriority="high"` -
unless it already carries `loading="lazy"`, because promoting a lazy image
is a contradiction the browser resolves unpredictably (one page today:
aqa-a2-macro/2-6-2-trade, logged in docs/REVIEW-NOTES.md). The topic pages
also load notes.js as their family's extra script, the same per-family
mechanism as quiz.js and flashcards.js.

MATHJAX IS DECIDED FROM THE BODY, NOT FROM THE RECORD (2026-08-23)
------------------------------------------------------------------
Until the performance pass every record carried a stored `head.mathjax`
value inherited from the hand-written page it was lifted from, and 126 of
166 topic pages loaded MathJax 3 from jsDelivr - 67 of them with no maths
anywhere in the body. The flag is now derived: a page loads MathJax if and
only if its rendered body contains one of the three delimiters the config
declares (backslash-paren, backslash-bracket, double dollar - see
page_shell.MATHJAX_CONFIG_BODY), and the
same page gets a preconnect to cdn.jsdelivr.net so the script's connection
opens early. The stored fields were removed from the records; no page needs
an override. verify_page_shell.py check 5 asserts the iff independently.

WHAT THIS DELIBERATELY DOES NOT DO
----------------------------------
**It does not run Prettier**, and that is a departure from PH06 section 3
step 5, made on measurement. Prettier is a parse-and-re-serialise, and the one
rule of this migration is that the content is never parsed and re-serialised.
Running it over a slice containing prose risks moving a line break across an
inline tag boundary, which turns `<strong>word</strong>s` into `word s`. The
harness's assertion 2 would catch that - but not creating the hazard beats
catching it, and the output is deterministic without it, which is all that
--check and verify_generated.py need.

The consequence, accepted with Eliot on 2026-08-11: the generated page is not
byte-identical to the page it replaces, because the committed pages were never
Prettier-formatted either and their <head> whitespace is inconsistent. The
agreed criterion is instead that the page has the same tags, in the same
order, with the same values - which is what compare_trees.py's ten assertions
check, and what a reader or a crawler can actually observe.

Standard library only.
"""

from __future__ import annotations

import argparse
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import notes_extras  # noqa: E402
import notes_sequence  # noqa: E402
import page_shell  # noqa: E402

DATA = ROOT / "notes-data"

# Wave 4.10: the tail is page_shell.SCRIPT_TAIL now, declared once for all
# five generators. Since 2026-08-25 the topic pages append their own
# component script after it (defer), through the same `extra` mechanism
# quiz.js and flashcards.js use; the hubs keep the plain tail.
# verify_page_shell.py's FAMILY_SCRIPT holds the relation.
NOTES_JS = ("/js/components/notes.js",)

# The one hub that loads the family script too. macro-application is a hub
# by location (notes-data/hubs/, so topic_key() rightly gives it no topic
# chrome) and a notes-family content page by design: since the family
# consistency pass (2026-08-25, D62) its contents-rail scrollspy and the
# no-JS filter upgrade live in notes.js, which replaced the inline filter
# script its record used to carry in afterScripts. The six board hubs are
# index pages and keep the plain tail. verify_page_shell.py names the same
# page in EXTRA_SCRIPT_PAGES.
EXTRA_SCRIPT_PAGES = {"revision-notes/macro-application/index.html": NOTES_JS}

# The two anchors the previous/next rows are spliced against. Both were
# measured across all 166 topic slices before being relied on: every one opens
# its content with this exact line, at this exact indent, once, and every one
# ends with this exact string.
CONTAINER_OPEN = '          <div class="notes-container">\n'
# The close is declared in notes_extras, which splices the tail against it
# first; restating it here would be a second copy of the same anchor.
CONTAINER_CLOSE = notes_extras.CONTAINER_CLOSE

# The three delimiters page_shell.MATHJAX_CONFIG_BODY tells MathJax to typeset.
# Anything else - a lone `$`, a `\frac` outside delimiters - is not maths to
# MathJax either, so it is not maths to this test. verify_page_shell.py
# restates the pattern rather than importing it, on purpose.
MATHS_DELIMITER = re.compile(r"\\\(|\\\[|\$\$")
MATHJAX_ORIGIN = "https://cdn.jsdelivr.net"


# A diagram <img> in a slice: its own line, indented, self-closing, src under
# /images/diagrams/. The lookahead pins the src; the tag body never contains
# a ">" (alt text is entity-escaped), which is what lets [^>] span the lines.
DIAGRAM_IMG = re.compile(
    r'^([ \t]*)<img\b(?=[^>]*\bsrc="(/images/diagrams/[\w\-]+)\.png")[^>]*?/>',
    re.M | re.S)


# How every diagram <img> tag closes, measured 208/208 across the 93 topic
# slices that carry one (2026-08-25): the `/>` on its own line at the tag's
# indent, attributes two spaces further in. That is where the promoted
# attribute goes, as its own line, so the tag keeps its one-attribute-per-
# line shape.
IMG_CLOSE_RE = re.compile(r"\n([ \t]*)/>$")


def with_webp_pictures(html: str, zoom: bool = False) -> str:
    """Wrap each diagram <img> in a <picture> offering its WebP twin first.

    The <img> is re-emitted byte for byte; only the wrapper lines are new,
    at the tag's own indent. A PNG whose .webp is not in the tree is left
    bare rather than pointed at a 404 - and verify_image_dimensions.py fails
    the build for the missing twin, so that cannot ship quietly.

    With `zoom` (the topic pages; hubs never pass it) each diagram is also
    wrapped in an `<a class="diagram-zoom">` to its PNG - a working
    open-full-size link with JavaScript off, upgraded to a lightbox by
    notes.js - and the first diagram on the page gains
    `fetchpriority="high"`, the one attribute this transform writes INTO the
    <img> tag, unless that first diagram carries `loading="lazy"` (a lazy
    image must not be promoted; it is left exactly as written).
    """
    state = {"first": zoom}

    def wrap(m: re.Match) -> str:
        indent, stem = m.group(1), m.group(2)
        img = m.group(0)
        if state["first"]:
            state["first"] = False
            if 'loading="lazy"' not in img:
                img = IMG_CLOSE_RE.sub(
                    lambda c: (f'\n{c.group(1)}  fetchpriority="high"'
                               f'\n{c.group(1)}/>'), img)
        if (ROOT / stem.lstrip("/")).with_suffix(".webp").exists():
            body = (f"{indent}<picture>\n"
                    f'{indent}<source type="image/webp" srcset="{stem}.webp" />\n'
                    f"{img}\n"
                    f"{indent}</picture>")
        else:
            body = img
        if zoom:
            body = (f'{indent}<a class="diagram-zoom" href="{stem}.png">\n'
                    f"{body}\n"
                    f"{indent}</a>")
        return body
    return DIAGRAM_IMG.sub(wrap, html)


def head_for(rec: dict, body_html: str) -> dict:
    """The page's head values, with MathJax decided by the body it will carry.

    `body_html` is the final body - slice, extras and previous/next rows - so
    the decision is about what the page actually contains. A page with maths
    loads MathJax (the one canonical form, `id="MathJax-script" async`, the
    `<!-- MathJax Configuration -->` comment above the config) and preconnects
    to its CDN; a page without does neither. The record's own `extraPreconnects`
    are kept and the CDN appended, so a future record can still name one.
    """
    head = dict(rec["head"])
    has_maths = bool(MATHS_DELIMITER.search(body_html))
    head["mathjax"] = "with-id" if has_maths else None
    head["mathjaxComment"] = has_maths
    extra = [h for h in head.get("extraPreconnects", []) if h != MATHJAX_ORIGIN]
    head["extraPreconnects"] = extra + [MATHJAX_ORIGIN] if has_maths else extra
    return head


def topic_key(meta: pathlib.Path) -> tuple[str, str] | None:
    """(notes_dir, slug) for a topic record, or None for a hub.

    Keyed on where the record LIVES, not on its `path`. A hub's path is
    revision-notes/<dir>/index.html and a topic's is
    revision-notes/<dir>/<slug>.html, so a path test would work today and
    would quietly start injecting navigation into a hub the day one is named
    differently. notes-data/topics/ versus notes-data/hubs/ is the actual
    distinction and it cannot drift.
    """
    try:
        rel = meta.relative_to(DATA / "topics")
    except ValueError:
        return None
    if len(rel.parts) != 2:
        return None
    return rel.parts[0], meta.stem


def date_modified(rec: dict) -> str:
    """The page's own dateModified, from its record.

    Read from the JSON rather than from `git log` on purpose. This generator
    has to be a pure function of notes-data/: verify_generated.py re-runs all
    eight generators inside a throwaway worktree and diffs the result against
    the committed tree, and a generator that shelled out to git would answer
    differently there and fail a correct commit. The date is put into the
    record by seo/tools/rewrite_notes_meta.py, which is where the git reading
    happens, once.
    """
    for block in rec["head"].get("jsonldBeforeIcons", []):
        if block.get("@type") == "LearningResource" and block.get("dateModified"):
            return block["dateModified"]
    sys.exit(f"{rec['path']}: no dateModified in its LearningResource - run "
             f"python3 seo/tools/rewrite_notes_meta.py --apply")


SPEC_UNIT_RE = re.compile(r"unit\s+(\d+(?:\.\d+)+)")


def with_topic_nav(slice_html: str, key: tuple[str, str]) -> str:
    """Splice the previous/next rows into a topic slice.

    THE SLICE ON DISK IS NEVER TOUCHED. notes-data/topics/*.html is a verbatim
    byte slice of the page's content and stays one - the rows are chrome this
    generator wraps around it, in the same way it already wraps the <head>,
    the <main> and the script tail. Editing 166 source files instead would be
    exactly the scripted bulk edit CLAUDE.md hard rule 6 forbids, and which
    has silently destroyed <a> tags in this repo before.

    Both rows go INSIDE .notes-container, which is `max-width: 1200px` with
    `padding: 3em` while the breadcrumb's .container is 70em - so inside is
    the only placement that lines the row up with the notes body rather than
    the page. It also puts both rows inside the region
    verify_markup_integrity.py profiles, which cuts at this same anchor.

    A slice that does not match both anchors fails the build rather than
    being silently mangled.
    """
    notes_dir, slug = key
    where = f"notes-data/topics/{notes_dir}/{slug}.html"
    if slice_html.count(CONTAINER_OPEN) != 1:
        sys.exit(f"{where}: expected exactly one {CONTAINER_OPEN.strip()!r} "
                 f"line at ten spaces of indent, found "
                 f"{slice_html.count(CONTAINER_OPEN)}")
    if not slice_html.endswith(CONTAINER_CLOSE):
        sys.exit(f"{where}: expected the slice to end with "
                 f"{CONTAINER_CLOSE!r}")

    top, bottom = notes_sequence.rows(notes_dir, slug)
    cut = slice_html.index(CONTAINER_OPEN) + len(CONTAINER_OPEN)
    body = slice_html[cut:-len(CONTAINER_CLOSE)]
    return (slice_html[:cut] + top + "\n"
            + body + "\n\n" + bottom
            + CONTAINER_CLOSE.lstrip("\n"))


def render(rec: dict, slice_html: str, extra_scripts: tuple = ()) -> str:
    b = rec["body"]
    end_container = b.get("endContainerComment") or ""
    end_main = b.get("endMainComment") or ""
    # Wave 2 Phase 7 bakes the header and footer in. This is the one generator
    # with nothing to sequence the bake after, because it deliberately does not
    # run Prettier (see above), so it happens here rather than post-write - and
    # --check keeps comparing like with like as a result.
    return page_shell.bake(
        "<!doctype html>\n"
        '<html lang="en-GB">\n'
        "  <head>\n"
        f"{page_shell.render_head(head_for(rec, slice_html))}\n"
        "  </head>\n"
        '  <body class="is-preload">\n'
        f"{b['beforeMain']}"
        f'      <main id="main"{b["mainAttrs"]}>\n'
        '        <div class="container">\n'
        f"{slice_html}"
        f"\n        </div>{end_container}\n"
        f"      </main>{end_main}"
        f"{b['afterMain']}"
        f"{page_shell.script_tail(extra_scripts)}\n"
        f"{b['afterScripts']}",
        rec["path"],
    )


def build() -> dict[str, str]:
    """Every page this generator owns, path -> rendered bytes."""
    pages: dict[str, str] = {}
    for meta in sorted(DATA.rglob("*.json")):
        rec = json.loads(meta.read_text(encoding="utf-8"))
        slice_html = meta.with_suffix(".html").read_text(encoding="utf-8")
        key = topic_key(meta)
        if key is not None:
            notes_dir, slug = key
            unit = SPEC_UNIT_RE.search(slice_html)
            if not unit:
                sys.exit(f"notes-data/topics/{notes_dir}/{slug}.html: no "
                         f"'unit X.Y.Z' in its spec-alert")
            slice_html = notes_extras.apply_all(
                slice_html, notes_dir, slug, unit.group(1), date_modified(rec))
            slice_html = with_topic_nav(slice_html, key)
        slice_html = with_webp_pictures(slice_html, zoom=key is not None)
        pages[rec["path"]] = render(
            rec, slice_html,
            NOTES_JS if key is not None
            else EXTRA_SCRIPT_PAGES.get(rec["path"], ()))
    return pages


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--check", action="store_true",
                    help="compare against what is on disk and write nothing; "
                         "exits non-zero on any difference")
    ap.add_argument("--out", default=str(ROOT),
                    help="tree to write into (default: the repo)")
    args = ap.parse_args()

    out_root = pathlib.Path(args.out).resolve()
    pages = build()

    if args.check:
        # PH09b-026: a --check that does not compare rendered output against
        # the file on disk is a false pass. build_sitemap.py:252 is the model.
        changed = [p for p, body in pages.items()
                   if not (out_root / p).exists()
                   or (out_root / p).read_text(encoding="utf-8") != body]
        for p in changed:
            print(f"  WOULD CHANGE {p}")
        print(f"{len(pages)} pages checked, {len(changed)} would change")
        return 1 if changed else 0

    for p, body in pages.items():
        dest = out_root / p
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(body, encoding="utf-8")
    print(f"wrote {len(pages)} notes pages into {out_root}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

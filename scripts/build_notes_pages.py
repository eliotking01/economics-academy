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
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import page_shell  # noqa: E402

DATA = ROOT / "notes-data"

SEVEN_SCRIPTS = "\n".join(
    f'    <script src="{s}"></script>' for s in (
        "/js/jquery.min.js",
        "/js/jquery.dropotron.min.js",
        "/js/components/inject-templates.js",
        "/js/browser.min.js",
        "/js/breakpoints.min.js",
        "/js/util.js",
        "/js/main.js",
    )
)


def render(rec: dict, slice_html: str) -> str:
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
        f"{page_shell.render_head(rec['head'])}\n"
        "  </head>\n"
        '  <body class="is-preload">\n'
        f"{b['beforeMain']}"
        f'      <section id="main"{b["mainAttrs"]}>\n'
        '        <div class="container">\n'
        f"{slice_html}"
        f"\n        </div>{end_container}\n"
        f"      </section>{end_main}"
        f"{b['afterMain']}"
        f"{SEVEN_SCRIPTS}\n"
        f"{b['afterScripts']}",
        rec["path"],
    )


def build() -> dict[str, str]:
    """Every page this generator owns, path -> rendered bytes."""
    pages: dict[str, str] = {}
    for meta in sorted(DATA.rglob("*.json")):
        rec = json.loads(meta.read_text(encoding="utf-8"))
        slice_html = meta.with_suffix(".html").read_text(encoding="utf-8")
        pages[rec["path"]] = render(rec, slice_html)
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

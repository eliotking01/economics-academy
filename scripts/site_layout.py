#!/usr/bin/env python3
"""What the site is made of, declared once: the generators, in order.

    from site_layout import GENERATORS    # from inside scripts/
    python3 scripts/site_layout.py        # print the list

NOT `site.py`. That was the planned name, and it cannot work: `site` is a
Python standard-library module that the interpreter imports at start-up, so
`import site` always returns the stdlib one and a scripts/site.py is silently
unreachable. Found by trying it.

This module exists so that the generator sequence is written down in exactly
ONE place. Until 2026-08-23 it was hand-copied into at least four - the root
CLAUDE.md (five generators), .claude/commands/rebuild-nav.md (five),
notes-data/CLAUDE.md (a three-step variant) and scripts/verify_generated.py
(eight) - and the copies disagreed. `scripts/build.py` runs this list and
`scripts/verify_generated.py` re-runs it in a throwaway worktree; both import
it from here, and nothing restates it.

Import direction: generators and verifiers may import this module. It imports
neither. (Phase 5 of the maintainability work moves the shared page
enumeration - `family_of`, `pages`, the publish rules - in here as well, for
the same reason: so a generator never has to import a verifier to find out
what the site contains.)

Standard library only.
"""

from __future__ import annotations

import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent

# The generators that write CONTENT, in the order they must run. Order
# matters: the taxonomy feeds the question bank, and extract_glossary.py must
# run before build_glossary.py or the glossary is rendered from a stale
# extraction.
#
# build_notes_pages.py goes first because nothing depends on it and everything
# that enumerates the filesystem afterwards has to see what it wrote. It globs
# notes-data/, so a new board directory needs no edit here.
CONTENT_GENERATORS = (
    "build_notes_pages.py",
    "build_past_paper_taxonomy.py",
    "build_past_paper_questions.py",
    "build_questions.py",
    "extract_glossary.py",
    "build_glossary.py",
    "build_flashcards.py",
)

# The sitemap is a generator too, and it is LAST - it enumerates the filesystem
# and takes every <lastmod> from `git log`, so it can only be right once every
# page exists AND has been committed. That is why build.py runs it only under
# --sitemap, after the content commit, while verify_generated.py (which checks
# a committed tree) runs it with the rest.
SITEMAP_GENERATOR = "build_sitemap.py"

# Every generator, in order. This is the list verify_generated.py proves the
# committed tree against. If you are adding a generator, add it here and
# nowhere else; build.py, verify_generated.py and the docs all read this.
GENERATORS = CONTENT_GENERATORS + (SITEMAP_GENERATOR,)


def main() -> int:
    for i, name in enumerate(GENERATORS, 1):
        note = "   (after the content commit)" if name == SITEMAP_GENERATOR else ""
        print(f"  {i}. scripts/{name}{note}")
    print(f"{len(GENERATORS)} generators")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

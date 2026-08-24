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

It also holds the shared ENUMERATION of the site - the publish rules that
mirror GitHub Pages' default Jekyll build (`excludes()`, `published()`), the
page families (`family_of()`, `HAND_WRITTEN`) and the published page list
(`pages()`). Until 2026-08-23 those lived in build_sitemap.py and
verify_page_shell.py, and page_shell.py - a generator - imported a VERIFIER to
get at them. The rule now: generators and verifiers may both import this
module; verifiers may import generators; a generator never imports a
verifier. This module imports neither.

Standard library only.
"""

from __future__ import annotations

import pathlib
import re
import subprocess

ROOT = pathlib.Path(__file__).resolve().parent.parent

# The generators that write CONTENT, in the order they must run. Order
# matters: the taxonomy feeds the question bank, and extract_glossary.py must
# run before build_glossary.py or the glossary is rendered from a stale
# extraction.
#
# build_notes_pages.py goes first because nothing depends on it and everything
# that enumerates the filesystem afterwards has to see what it wrote. It globs
# notes-data/, so a new board directory needs no edit here.
# build_search_index.py is LAST of the content generators for the mirror
# reason: it reads titles from pages the generators before it write.
CONTENT_GENERATORS = (
    "build_notes_pages.py",
    "build_past_paper_taxonomy.py",
    "build_past_paper_questions.py",
    "build_questions.py",
    "extract_glossary.py",
    "build_glossary.py",
    "build_flashcards.py",
    "build_search_index.py",
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


# --------------------------------------------------------------------------
# What is published. Mirrors the GitHub Pages default Jekyll build: anything
# under a path segment starting with "_" is skipped, as is anything in
# _config.yml's `exclude` list. The list is PARSED from _config.yml rather
# than restated - DO-NOT-BREAK's rule, after a restated copy in
# docs/audit/scripts/lib.py went stale for two waves.
# --------------------------------------------------------------------------

def excludes() -> list[str]:
    """The entries of _config.yml's `exclude:` list, in order."""
    cfg = (ROOT / "_config.yml").read_text(encoding="utf-8")
    out, inside = [], False
    for line in cfg.splitlines():
        if re.match(r"^exclude:\s*$", line):
            inside = True
            continue
        if inside:
            if re.match(r"^\S", line):
                break
            m = re.match(r"^\s+-\s+(\S+)", line)
            if m:
                out.append(m.group(1))
    return out


def published(path: str, ex: list[str]) -> bool:
    """Does GitHub Pages serve this repo-relative path? `ex` is excludes()."""
    if any(seg.startswith("_") for seg in path.split("/")):
        return False
    for e in ex:
        if e.endswith("/") and path.startswith(e):
            return False
        if path == e:
            return False
    return True


# Not pages: read at build time, excluded since 2026-08-20. Kept as a filter so
# that a future un-excluding could not put them in a page list by accident.
RUNTIME_PARTIALS = {"templates/header.html", "templates/footer.html"}


# --------------------------------------------------------------------------
# Page families, as Phase 0 defined them in 00-INVENTORY.md section 4.
# --------------------------------------------------------------------------

def family_of(path: str) -> str:
    if path.startswith("revision-notes/glossary/"):
        return "glossary"
    if path.startswith("revision-notes/"):
        rest = path[len("revision-notes/"):]
        if rest.endswith("/index.html") and rest.count("/") == 1:
            return "notes-hub"
        if "/" not in rest:
            return "notes-other"
        return "notes-topic"
    if path.startswith("practice-questions/"):
        return "mcq-hub" if path.endswith("/index.html") else "mcq-topic"
    if path.startswith("past-paper-questions/"):
        return "ppq"
    if path.startswith("past-papers/"):
        return "past-papers"
    if path.startswith("flashcards/"):
        return "flashcards"
    return "root"


# Families no generator writes: the 9 root pages, the 5 past-papers/ hubs and
# the 3 revision-notes/ non-topic pages. scripts/bake_templates.py owns
# exactly this set (and prints it); notes-topic and notes-hub left this list in
# Wave 2 Phases 5 and 3 when build_notes_pages.py took them over.
HAND_WRITTEN = ("root", "notes-other", "past-papers")


def pages() -> list[str]:
    """Every published .html page, repo-relative, sorted. Tracked files only
    (`git ls-files`), so a new page is listed once it is added."""
    ex = excludes()
    out = subprocess.run(["git", "ls-files", "*.html"], cwd=ROOT,
                         capture_output=True, text=True, check=True).stdout.split()
    return sorted(f for f in out
                  if published(f, ex) and f not in RUNTIME_PARTIALS)


def main() -> int:
    for i, name in enumerate(GENERATORS, 1):
        note = "   (after the content commit)" if name == SITEMAP_GENERATOR else ""
        print(f"  {i}. scripts/{name}{note}")
    print(f"{len(GENERATORS)} generators")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

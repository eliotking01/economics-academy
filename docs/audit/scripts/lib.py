"""Shared read-only helpers for the organisation audit.

READ-ONLY. Nothing in docs/audit/scripts/ may open a site file for writing. Every
script here takes its file list from `git ls-files` rather than the filesystem,
so untracked local cruft (the Finder " 2.py" duplicates, .DS_Store, .venv)
cannot contaminate a count.

Site vs published vs served:
  tracked     every file git knows about
  published   tracked, minus what _config.yml excludes and minus _-prefixed
              directories (Jekyll's own rule)
  page        published .html that is a page in its own right - excludes
              templates/, which is fetched at runtime and has no URL a user
              visits
"""

import pathlib
import posixpath
import re
import subprocess
from functools import lru_cache

SITE = "https://economicsacademy.co.uk"

# docs/audit/scripts/lib.py -> the repo root.
REPO = pathlib.Path(__file__).resolve().parents[3]

# Mirrors the `exclude:` list in _config.yml.
#
# THIS WENT STALE AND NOTHING NOTICED - found 2026-08-13, during item (f)'s
# measurement. `boards-data/` and `notes-data/` were added to _config.yml by
# Waves 2 and 3.2 and never added here, so `published_html()` returned 638
# where the real published surface is 465, and `pages()` returned 636 rather
# than 463. `link_graph.py` printed "published pages: 636" and listed 173
# phantom orphans; `metadata_census.py`, `asset_census.py`, `structured_data.py`
# and `link_depth.py` all read through the same function, and four of them back
# DO-NOT-BREAK's "Numbers that must not regress" table. None is in CI, which is
# why it survived.
#
# The comment here claimed "verify_matches_config() below fails loudly if it
# drifts". THAT FUNCTION WAS NEVER WRITTEN. It is written now, and every
# consumer calls it on import, so the list cannot silently disagree again.
#
# The right fix is not to re-transcribe the list. `scripts/build_sitemap.py`
# PARSES _config.yml - DO-NOT-BREAK's rule is "copy that pattern rather than
# adding skip lists" - but docs/audit/scripts/ is deliberately standalone and
# read-only, so the literal stays and is CHECKED against the file instead.
EXCLUDED_PREFIXES = (
    "scripts/",
    "boards-data/",
    "notes-data/",
    "glossary-data/",
    "questions-data/",
    "past-paper-questions-data/",
    "flashcards-data/",
    "raw-notes/",
    "docs/",
    "seo/",
    "_",  # Jekyll skips any path starting with underscore
)

EXCLUDED_FILES = {
    "CLAUDE.md",
    "NEW-CONTENT-LOG.md",
    "PAST-PAPERS-PROGRESS.md",
    "PROJECT-LOG.md",
    "QUESTIONS_GUIDE.md",
    "QUESTIONS_PROGRESS.md",
    "README.md",
    "README.txt",
    "REVIEW-NOTES.md",
    "ROADMAP.md",
    "extraction-qa-report.md",
    "requirements.txt",
}


def tracked(pattern="*"):
    out = subprocess.check_output(["git", "ls-files", pattern], text=True)
    return [line for line in out.splitlines() if line]


def verify_matches_config():
    """Fail loudly if the two lists above have drifted from `_config.yml`.

    The comment on EXCLUDED_PREFIXES promised this function for months and it
    did not exist, which is exactly how the list came to be two entries short
    of the real thing while eight scripts read through it. It is called on
    import, below, so no consumer can opt out by forgetting.

    Only entries that could change a publish decision are compared. Jekyll's
    restated defaults (Gemfile, node_modules, vendor/) are in `_config.yml`
    and not here because nothing tracked matches them; they are ignored rather
    than being a permanent false alarm.
    """
    cfg = REPO / "_config.yml"
    if not cfg.exists():                      # pragma: no cover
        raise SystemExit(f"lib.py: cannot find {cfg}")

    listed, in_exclude = [], False
    for raw in cfg.read_text(encoding="utf-8").splitlines():
        if raw.startswith("exclude:"):
            in_exclude = True
            continue
        if in_exclude:
            if raw[:1] not in (" ", "-", "", "#") and not raw.startswith("  "):
                break                          # a new top-level key
            s = raw.strip()
            if s.startswith("- "):
                listed.append(s[2:].strip())

    ignore = {"Gemfile", "Gemfile.lock", "node_modules", "vendor/", ".github/"}
    want_prefixes = {e for e in listed if e.endswith("/")} - ignore
    want_files = {e for e in listed if not e.endswith("/")} - ignore

    have_prefixes = {p for p in EXCLUDED_PREFIXES if p != "_"}
    # "_working/" is covered by the bare "_" rule rather than being listed.
    have_prefixes |= {p for p in want_prefixes if p.startswith("_")}

    missing = want_prefixes - have_prefixes
    extra = have_prefixes - want_prefixes
    missing_f = want_files - EXCLUDED_FILES
    extra_f = EXCLUDED_FILES - want_files
    if missing or extra or missing_f or extra_f:
        lines = ["docs/audit/scripts/lib.py disagrees with _config.yml:"]
        for label, s in (("in _config.yml, not in lib.py", missing | missing_f),
                         ("in lib.py, not in _config.yml", extra | extra_f)):
            if s:
                lines.append(f"  {label}: {', '.join(sorted(s))}")
        lines.append("  `exclude` is the only thing keeping working files off "
                     "the site, so a disagreement here means every count this "
                     "module produces is measuring the wrong file set.")
        raise SystemExit("\n".join(lines))


def is_published(path):
    if path in EXCLUDED_FILES:
        return False
    return not path.startswith(EXCLUDED_PREFIXES)


def published_html():
    """Every .html file GitHub Pages serves, templates/ included."""
    return [f for f in tracked("*.html") if is_published(f)]


def pages():
    """Published .html that is a real page. templates/ excluded."""
    return [f for f in published_html() if not f.startswith("templates/")]


def canonical_url(path):
    """The URL form the SEO pass settled on: directories, never /index.html."""
    if path == "index.html":
        return SITE + "/"
    if path.endswith("/index.html"):
        return SITE + "/" + path[: -len("index.html")]
    return SITE + "/" + path


def url_variants(path):
    """Both forms a page can be requested at, for link resolution."""
    out = {"/" + path}
    if path == "index.html":
        out.add("/")
    elif path.endswith("/index.html"):
        out.add("/" + path[: -len("index.html")])
    return out


@lru_cache(maxsize=None)
def read(path):
    with open(path, encoding="utf-8", errors="replace") as fh:
        return fh.read()


# Anchors only. A bare href="..." also matches <link rel="stylesheet">,
# <link rel="canonical"> and <link rel="icon">, which are not navigation and
# must never enter the link graph - counting them made /css/main.css look like
# a page with 463 inbound links.
ANCHOR = re.compile(r"<a\b[^>]*?\shref=\"([^\"]+)\"", re.I | re.S)
HREF = re.compile(r'href="([^"]+)"')
SRC = re.compile(r'\bsrc="([^"]+)"')


def resolve(href, from_path):
    """Normalise one href to a root-absolute site path, or None if off-site.

    Query strings and fragments are stripped: the past-paper-questions hub takes
    ?topic= filters, and for link-graph purposes /past-paper-questions/?topic=x
    and /past-paper-questions/ are the same destination page.
    """
    if href.startswith(("http://", "https://", "mailto:", "tel:", "#", "javascript:")):
        return None
    href = href.split("#")[0].split("?")[0]
    if not href:
        return None
    if not href.startswith("/"):
        href = posixpath.normpath(posixpath.join("/" + posixpath.dirname(from_path), href))
    return href


def links_from(path):
    """Unique internal <a href> targets in one file's raw source.

    Unique per page on purpose: three links from one page to another page are
    one editorial decision, not three, and counting them three times inflates
    every hub.
    """
    out = set()
    for href in ANCHOR.findall(read(path)):
        target = resolve(href, path)
        if target:
            out.add(target)
    return out


# Called on import, so that no consumer can opt out by forgetting. The whole
# point of the check is that it fires for the eight scripts that read through
# this module, not only for whoever remembers to ask.
verify_matches_config()

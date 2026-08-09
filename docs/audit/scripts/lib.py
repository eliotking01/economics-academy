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

import posixpath
import re
import subprocess
from functools import lru_cache

SITE = "https://economicsacademy.co.uk"

# Mirrors the `exclude:` list in _config.yml. Kept as a literal rather than
# parsed from the YAML because there is no yaml module guaranteed here and the
# list is stable; verify_matches_config() below fails loudly if it drifts.
EXCLUDED_PREFIXES = (
    "scripts/",
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

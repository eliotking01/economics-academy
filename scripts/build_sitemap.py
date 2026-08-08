#!/usr/bin/env python3
"""Build sitemap.xml as a sitemap index, plus one sitemap per section.

Replaces the previous arrangement, where three generators each rewrote their own
block of a single flat sitemap.xml between HTML comment markers. That had two
problems:

  1. Every generator stamped <lastmod> with the date it ran. 440 of 461 entries
     carried one of three build dates, so a page untouched since May was
     advertised as modified today and Google had no reason to trust the field.
  2. Coverage in Search Console was reported for the whole site at once, which
     makes it impossible to see that (say) practice-questions is not being
     indexed while revision-notes is.

This script owns the sitemap outright. It enumerates pages from the filesystem
rather than being told about them, so a new page cannot be forgotten, and it
takes <lastmod> from git - the date the file was last actually committed.

Publish status mirrors the GitHub Pages default Jekyll build: anything under a
path segment starting with "_" is skipped, as is anything in _config.yml's
`exclude` list. Pages carrying a noindex meta tag are left out, because a
sitemap that advertises a page you have told Google not to index is a
contradiction.

    sitemap.xml                       the index
    sitemaps/core.xml                 root pages
    sitemaps/revision-notes.xml
    sitemaps/practice-questions.xml
    sitemaps/past-paper-questions.xml
    sitemaps/past-papers.xml
    sitemaps/flashcards.xml
    sitemaps/pdfs.xml                 the past papers themselves

Standard library only, in keeping with the rest of scripts/.

Usage:
    python3 scripts/build_sitemap.py
    python3 scripts/build_sitemap.py --check     # verify, write nothing
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE = "https://economicsacademy.co.uk"
SITEMAP_DIR = ROOT / "sitemaps"

# Sections, in the order they appear in the index. The prefix is matched against
# the repo-relative path; "" catches everything left over at the root.
SECTIONS = [
    ("core", ""),
    ("revision-notes", "revision-notes/"),
    ("practice-questions", "practice-questions/"),
    ("past-paper-questions", "past-paper-questions/"),
    ("past-papers", "past-papers/"),
    ("flashcards", "flashcards/"),
]

# Served, but fetched at runtime by js/components/inject-templates.js rather
# than being pages anyone can land on.
RUNTIME_PARTIALS = {"templates/header.html", "templates/footer.html"}

PRIORITY = [
    ("", 1.0),                                  # the homepage
    ("tutoring.html", 0.9),
    ("marking.html", 0.9),
    ("revision-notes/", 0.9),
    ("practice-questions/", 0.8),
    ("past-paper-questions/", 0.8),
    ("past-papers/", 0.8),
    ("flashcards/", 0.8),
    ("about.html", 0.7),
    ("contact.html", 0.6),
    ("faq.html", 0.5),
    ("privacy.html", 0.3),
]

NOINDEX_RE = re.compile(r'<meta[^>]+name=["\']robots["\'][^>]*noindex', re.I)


def git_files() -> list[str]:
    out = subprocess.run(["git", "-C", str(ROOT), "ls-files"],
                         capture_output=True, text=True, check=True).stdout
    return [p for p in out.splitlines() if p]


def excludes() -> list[str]:
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
    if any(seg.startswith("_") for seg in path.split("/")):
        return False
    for e in ex:
        if e.endswith("/") and path.startswith(e):
            return False
        if path == e:
            return False
    return True


def url_for(path: str) -> str:
    """The canonical URL for a page, matching its own rel=canonical."""
    if path == "index.html":
        return f"{SITE}/"
    if path.endswith("/index.html"):
        return f"{SITE}/{path[: -len('index.html')]}"
    return f"{SITE}/{path}"


def lastmod(paths: list[str]) -> str:
    """Last commit date across one or more files, YYYY-MM-DD.

    A directory page's freshness is really its own file's; taking the max over
    a list lets a caller widen that if it ever needs to.
    """
    best = ""
    for p in paths:
        out = subprocess.run(
            ["git", "-C", str(ROOT), "log", "-1", "--format=%cs", "--", p],
            capture_output=True, text=True,
        ).stdout.strip()
        if out > best:
            best = out
    return best


def priority_for(url_path: str) -> str:
    for prefix, value in PRIORITY:
        if url_path == prefix:
            return f"{value:.1f}"
    for prefix, value in PRIORITY:
        if prefix and url_path.startswith(prefix):
            # one step down from the section hub
            return f"{max(value - 0.1, 0.1):.1f}"
    return "0.5"


def section_of(path: str) -> str:
    for name, prefix in SECTIONS:
        if prefix and path.startswith(prefix):
            return name
    return "core"


def xml_escape(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def urlset(entries: list[tuple[str, str, str]]) -> str:
    lines = ['<?xml version="1.0" encoding="UTF-8"?>',
             '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for loc, mod, pri in entries:
        lines.append(
            f"  <url><loc>{xml_escape(loc)}</loc>"
            f"<lastmod>{mod}</lastmod>"
            f"<priority>{pri}</priority></url>"
        )
    lines.append("</urlset>")
    return "\n".join(lines) + "\n"


def sitemapindex(names: list[tuple[str, str]]) -> str:
    lines = ['<?xml version="1.0" encoding="UTF-8"?>',
             '<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for name, mod in names:
        lines.append(
            f"  <sitemap><loc>{SITE}/sitemaps/{name}.xml</loc>"
            f"<lastmod>{mod}</lastmod></sitemap>"
        )
    lines.append("</sitemapindex>")
    return "\n".join(lines) + "\n"


def collect() -> tuple[dict[str, list], list, list[str]]:
    ex = excludes()
    tracked = git_files()
    by_section: dict[str, list] = {name: [] for name, _ in SECTIONS}
    pdfs = []
    skipped_noindex = []

    for path in sorted(tracked):
        if not published(path, ex):
            continue
        if path.lower().endswith(".pdf"):
            pdfs.append((f"{SITE}/{path}", lastmod([path]), "0.4"))
            continue
        if not path.endswith(".html") or path in RUNTIME_PARTIALS:
            continue
        text = (ROOT / path).read_text(encoding="utf-8", errors="replace")
        if NOINDEX_RE.search(text):
            skipped_noindex.append(path)
            continue
        loc = url_for(path)
        by_section[section_of(path)].append(
            (loc, lastmod([path]), priority_for(loc[len(SITE) + 1:]))
        )
    return by_section, pdfs, skipped_noindex


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="report, write nothing")
    args = ap.parse_args()

    by_section, pdfs, skipped = collect()

    files: dict[Path, str] = {}
    index: list[tuple[str, str]] = []

    for name, _ in SECTIONS:
        entries = sorted(by_section[name])
        if not entries:
            continue
        files[SITEMAP_DIR / f"{name}.xml"] = urlset(entries)
        index.append((name, max(e[1] for e in entries)))

    if pdfs:
        files[SITEMAP_DIR / "pdfs.xml"] = urlset(sorted(pdfs))
        index.append(("pdfs", max(e[1] for e in pdfs)))

    files[ROOT / "sitemap.xml"] = sitemapindex(index)

    total = sum(len(by_section[n]) for n, _ in SECTIONS)
    for name, _ in SECTIONS:
        if by_section[name]:
            print(f"  {len(by_section[name]):>4}  sitemaps/{name}.xml")
    print(f"  {len(pdfs):>4}  sitemaps/pdfs.xml")
    print(f"  {total} pages + {len(pdfs)} PDFs across {len(index)} sitemaps")
    if skipped:
        print(f"  excluded (noindex): {', '.join(skipped)}")

    if args.check:
        changed = [p for p, body in files.items()
                   if not p.exists() or p.read_text(encoding="utf-8") != body]
        for p in changed:
            print(f"  WOULD CHANGE {p.relative_to(ROOT)}")
        print("nothing written")
        return 1 if changed else 0

    SITEMAP_DIR.mkdir(exist_ok=True)
    for p, body in files.items():
        p.write_text(body, encoding="utf-8")
    print(f"wrote sitemap.xml and {len(files) - 1} section sitemaps")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

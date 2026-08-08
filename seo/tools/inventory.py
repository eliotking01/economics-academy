#!/usr/bin/env python3
"""Phase 0 ground truth: what exists, what is published, what Google knows.

Reads only. Produces the four-way reconciliation behind seo/00-inventory.md:

    repo files  vs  sitemap URLs  vs  GSC-known URLs  vs  live-crawlable URLs

Nothing here trusts a filename or an assumption. Publish status is derived from
_config.yml's `exclude` list plus Jekyll's own "_" rule; URL mapping follows the
project URL policy (directory pages canonical without index.html, root .html
pages keep their extension).

Case matters: GitHub Pages is case-sensitive and macOS APFS is not, so every
path check resolves against `git ls-files` rather than the filesystem.

Usage:
    python3 seo/tools/inventory.py            # human-readable summary
    python3 seo/tools/inventory.py --json     # machine-readable, for later phases
"""

from __future__ import annotations

import csv
import json
import re
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
SITE = "https://economicsacademy.co.uk"
SITEMAP_NS = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}

# Pages that carry a deliberate noindex and so are not candidates for the index.
DELIBERATE_NOINDEX = {"404.html", "confirmation.html"}

# Served, but partials fetched at runtime by js/components/inject-templates.js,
# not pages. _config.yml deliberately keeps them public; see CLAUDE.md.
RUNTIME_PARTIALS = {"templates/header.html", "templates/footer.html"}


def git_files() -> list[str]:
    """Every tracked path, case-exact. git is the only case-sensitive oracle here."""
    out = subprocess.run(
        ["git", "-C", str(REPO), "ls-files"],
        capture_output=True, text=True, check=True,
    ).stdout
    return [line for line in out.splitlines() if line]


def jekyll_excludes() -> list[str]:
    """The `exclude:` entries from _config.yml, read as text.

    No PyYAML in this repo (stdlib only, per scripts/verify_*.py), and the list
    is a flat sequence of scalars, so a line scan is exact rather than a guess.
    """
    cfg = (REPO / "_config.yml").read_text(encoding="utf-8")
    out, in_exclude = [], False
    for line in cfg.splitlines():
        if re.match(r"^exclude:\s*$", line):
            in_exclude = True
            continue
        if in_exclude:
            if re.match(r"^\S", line):          # next top-level key ends the block
                break
            m = re.match(r"^\s+-\s+(\S+)", line)
            if m:
                out.append(m.group(1))
    return out


def is_published(path: str, excludes: list[str]) -> tuple[bool, str]:
    """Would GitHub Pages' default Jekyll build publish this path?"""
    parts = path.split("/")
    if any(p.startswith("_") for p in parts):
        return False, "Jekyll '_' rule"
    for ex in excludes:
        if ex.endswith("/"):
            if path.startswith(ex):
                return False, f"_config.yml exclude: {ex}"
        elif path == ex:
            return False, f"_config.yml exclude: {ex}"
    return True, ""


def url_for(path: str) -> str:
    """Live URL for a published HTML file, under the project URL policy."""
    if path == "index.html":
        return f"{SITE}/"
    if path.endswith("/index.html"):
        return f"{SITE}/{path[: -len('index.html')]}"
    return f"{SITE}/{path}"


def read_sitemap() -> dict:
    root = ET.parse(REPO / "sitemap.xml").getroot()
    urls = []
    for u in root.findall("sm:url", SITEMAP_NS):
        loc = u.findtext("sm:loc", default="", namespaces=SITEMAP_NS).strip()
        lastmod = u.findtext("sm:lastmod", default="", namespaces=SITEMAP_NS).strip()
        urls.append({"loc": loc, "lastmod": lastmod})
    return {
        "count": len(urls),
        "urls": urls,
        "with_lastmod": sum(1 for u in urls if u["lastmod"]),
        "index_html_variants": [u["loc"] for u in urls if u["loc"].endswith("index.html")],
        "non_https": [u["loc"] for u in urls if not u["loc"].startswith("https://")],
        "is_index": root.tag.endswith("sitemapindex"),
    }


def read_gsc() -> list[dict]:
    """Normalise every GSC export to url | gsc_reason | last_crawled.

    Encoding and delimiter are detected, not assumed: GSC hands out UTF-16/TSV
    in some flows and UTF-8/CSV in others. Finder's " 2.csv" duplicates are
    skipped so rows are not double-counted.
    """
    rows = []
    d = REPO / "seo" / "gsc-exports"
    for f in sorted(d.glob("*.csv")):
        if re.search(r" \d+\.csv$", f.name):
            continue
        raw = f.read_bytes()
        if raw.startswith((b"\xff\xfe", b"\xfe\xff")):
            text, enc = raw.decode("utf-16"), "utf-16"
        else:
            text, enc = raw.decode("utf-8-sig"), "utf-8"
        sample = text[:2048]
        delim = "\t" if sample.count("\t") > sample.count(",") else ","
        reader = csv.reader(text.splitlines(), delimiter=delim)
        header = next(reader, None)
        for row in reader:
            if not row or not row[0].strip():
                continue
            rows.append({
                "url": row[0].strip(),
                "gsc_reason": f.stem,
                "last_crawled": row[1].strip() if len(row) > 1 else "",
                "source_file": f.name,
                "encoding": enc,
                "delimiter": "tab" if delim == "\t" else "comma",
                "header": header,
            })
    return rows


def build() -> dict:
    excludes = jekyll_excludes()
    tracked = git_files()

    html = [p for p in tracked if p.endswith(".html")]
    pdfs = [p for p in tracked if p.lower().endswith(".pdf")]

    published_html, unpublished_html = [], []
    for p in html:
        ok, why = is_published(p, excludes)
        (published_html if ok else unpublished_html).append((p, why))

    pages = [p for p, _ in published_html if p not in RUNTIME_PARTIALS]
    indexable = [p for p in pages if p not in DELIBERATE_NOINDEX]

    published_pdfs = [p for p in pdfs if is_published(p, excludes)[0]]

    sitemap = read_sitemap()
    gsc = read_gsc()

    expected = {url_for(p) for p in indexable}
    in_sitemap = {u["loc"] for u in sitemap["urls"]}
    gsc_urls = {r["url"] for r in gsc}

    return {
        "html_total": len(html),
        "html_unpublished": unpublished_html,
        "html_published": len(published_html),
        "runtime_partials": sorted(RUNTIME_PARTIALS),
        "pages": sorted(pages),
        "deliberate_noindex": sorted(DELIBERATE_NOINDEX),
        "indexable": sorted(indexable),
        "pdfs_total": len(pdfs),
        "pdfs_published": len(published_pdfs),
        "pdf_paths": sorted(published_pdfs),
        "sitemap": sitemap,
        "gsc": gsc,
        "expected_urls": sorted(expected),
        "sitemap_urls": sorted(in_sitemap),
        "gsc_urls": sorted(gsc_urls),
        "missing_from_sitemap": sorted(expected - in_sitemap),
        "sitemap_orphans": sorted(in_sitemap - expected),
        "excludes": excludes,
    }


def main() -> int:
    d = build()
    if "--json" in sys.argv:
        json.dump(d, sys.stdout, indent=2, default=str)
        return 0

    print(f"HTML files tracked ............ {d['html_total']}")
    print(f"  not published ............... {len(d['html_unpublished'])}")
    for why in sorted({w for _, w in d['html_unpublished']}):
        n = sum(1 for _, w in d['html_unpublished'] if w == why)
        print(f"      {n:>4}  {why}")
    print(f"  published ................... {d['html_published']}")
    print(f"    runtime partials .......... {len(d['runtime_partials'])}")
    print(f"    real pages ................ {len(d['pages'])}")
    print(f"      deliberate noindex ...... {len(d['deliberate_noindex'])}")
    print(f"      INDEXABLE ............... {len(d['indexable'])}")
    print()
    print(f"PDFs tracked / published ...... {d['pdfs_total']} / {d['pdfs_published']}")
    print()
    sm = d["sitemap"]
    print(f"sitemap.xml ................... {sm['count']} <loc>, "
          f"{sm['with_lastmod']} with <lastmod>, "
          f"index-format={sm['is_index']}")
    print(f"  index.html variants ......... {len(sm['index_html_variants'])}")
    print(f"  non-https ................... {len(sm['non_https'])}")
    print(f"  in sitemap, no file ......... {len(d['sitemap_orphans'])}")
    print(f"  file exists, not in sitemap . {len(d['missing_from_sitemap'])}")
    print()
    reasons: dict[str, int] = {}
    for r in d["gsc"]:
        reasons[r["gsc_reason"]] = reasons.get(r["gsc_reason"], 0) + 1
    print(f"GSC export rows ............... {len(d['gsc'])} "
          f"({len(d['gsc_urls'])} distinct URLs)")
    for k, v in sorted(reasons.items(), key=lambda kv: -kv[1]):
        print(f"      {v:>4}  {k}")
    encs = {(r["encoding"], r["delimiter"]) for r in d["gsc"]}
    print(f"  detected encodings/delims ... {sorted(encs)}")
    pdf_rows = sum(1 for u in d["gsc_urls"] if u.lower().endswith(".pdf"))
    print(f"  of which PDF / non-PDF ...... {pdf_rows} / {len(d['gsc_urls']) - pdf_rows}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

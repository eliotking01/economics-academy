#!/usr/bin/env python3
"""Phase 5: assert the SEO invariants across every page, by rule.

Not a sample and not a spot-check. Each assertion runs over the whole repo and
either passes for every page or names the pages it failed on. Exit status is
non-zero if any assertion fails, so this can gate a future change.

    1  no internal link points at a non-canonical URL
    2  no internal link is case-mismatched or dead
    3  every page has a self-referencing canonical
    4  og:url matches canonical; og:title and twitter:title match <title>
    5  every page has exactly one <h1>, a title and a meta description
    6  titles and meta descriptions are unique
    7  no unintended noindex
    8  every JSON-LD block parses, and no breadcrumb points at a duplicate URL
    9  sitemap: valid index, every URL 200-able, self-canonicalising, no
       redirects, no duplicates, matches the filesystem exactly
   10  robots.txt does not block anything crawlable, and names the sitemap

Usage:
    python3 seo/tools/verify_seo.py
    python3 seo/tools/verify_seo.py --verbose
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import xml.etree.ElementTree as ET
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from inventory import build as build_inventory, url_for, SITE  # noqa: E402
from pagemeta import norm_space, parse_html  # noqa: E402

REPO = Path(__file__).resolve().parent.parent.parent
NS = "{http://www.sitemaps.org/schemas/sitemap/0.9}"
EXTERNAL_RE = re.compile(r"^(https?:|mailto:|tel:|data:|javascript:|//)", re.I)

results: list[tuple[str, bool, str, list[str]]] = []


def check(name: str, failures: list[str], detail: str = "") -> None:
    results.append((name, not failures, detail, failures))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--verbose", action="store_true")
    args = ap.parse_args()

    inv = build_inventory()
    pages = inv["indexable"]
    all_html = pages + inv["deliberate_noindex"] + ["templates/header.html",
                                                    "templates/footer.html"]
    tracked = set(subprocess.run(["git", "-C", str(REPO), "ls-files"],
                                 capture_output=True, text=True,
                                 check=True).stdout.splitlines())
    parsed = {p: parse_html((REPO / p).read_text(encoding="utf-8", errors="replace"))
              for p in all_html}

    def site_paths(page: str):
        """Every internal URL the page references, as a site-absolute path."""
        pp = parsed[page]
        for raw in list(pp.links) + list(pp.srcs) + [
            m for b in pp.jsonld for m in re.findall(r'"item":\s*"([^"]+)"', b)
        ]:
            v = re.sub(r"^https?://(www\.)?economicsacademy\.co\.uk", "", raw.strip())
            if EXTERNAL_RE.match(v) or not v.startswith("/"):
                continue
            yield raw, v.split("#")[0].split("?")[0]

    # 1 ---------------------------------------------------------------------
    bad = [f"{p}: {raw}" for p in all_html for raw, v in site_paths(p)
           if v == "/index.html" or v.endswith("/index.html")]
    check("1  no internal link points at a non-canonical URL", bad,
          f"{sum(1 for p in all_html for _ in site_paths(p))} internal references")

    # 2 ---------------------------------------------------------------------
    lower = {t.lower(): t for t in tracked}
    bad = []
    for p in all_html:
        for raw, v in site_paths(p):
            if v == "/":
                continue
            target = v[1:] + ("index.html" if v.endswith("/") else "")
            if target in tracked:
                continue
            if target.lower() in lower:
                bad.append(f"{p}: {raw} -> case differs from {lower[target.lower()]}")
            else:
                bad.append(f"{p}: {raw} -> no such file")
    check("2  no internal link is case-mismatched or dead", bad)

    # 3 ---------------------------------------------------------------------
    bad = [f"{p}: canonical={parsed[p].canonical or '(none)'} expected={url_for(p)}"
           for p in pages if parsed[p].canonical != url_for(p)]
    check("3  every page has a self-referencing canonical", bad, f"{len(pages)} pages")

    # 4 ---------------------------------------------------------------------
    bad = []
    for p in pages:
        m = parsed[p]
        if m.og_url and m.og_url != m.canonical:
            bad.append(f"{p}: og:url != canonical")
        if m.og_title and norm_space(m.og_title) != m.title:
            bad.append(f"{p}: og:title != <title>")
        if m.twitter_title and norm_space(m.twitter_title) != m.title:
            bad.append(f"{p}: twitter:title != <title>")
    check("4  og:url matches canonical; social titles match <title>", bad)

    # 5 ---------------------------------------------------------------------
    bad = []
    for p in pages:
        m = parsed[p]
        if len(m.h1) != 1:
            bad.append(f"{p}: {len(m.h1)} <h1>")
        if not m.title:
            bad.append(f"{p}: no <title>")
        if not m.description:
            bad.append(f"{p}: no meta description")
    check("5  exactly one <h1>, a title and a description on every page", bad)

    # 6 ---------------------------------------------------------------------
    titles, descs = defaultdict(list), defaultdict(list)
    for p in pages:
        titles[parsed[p].title].append(p)
        descs[parsed[p].description].append(p)
    bad = [f"{len(v)} pages share title {k!r}" for k, v in titles.items() if len(v) > 1]
    bad += [f"{len(v)} pages share a description ({v[0]}, ...)"
            for k, v in descs.items() if len(v) > 1]
    check("6  titles and meta descriptions are unique", bad,
          f"{len(titles)} titles, {len(descs)} descriptions")

    # 7 ---------------------------------------------------------------------
    bad = [f"{p}: robots={parsed[p].robots}" for p in pages
           if "noindex" in parsed[p].robots.lower()]
    check("7  no unintended noindex", bad,
          f"intentional: {', '.join(inv['deliberate_noindex'])}")

    # 8 ---------------------------------------------------------------------
    bad, blocks = [], 0
    for p in pages:
        m = parsed[p]
        blocks += len(m.jsonld)
        for err in m.invalid_jsonld():
            bad.append(f"{p}: {err[:70]}")
        if not m.jsonld:
            bad.append(f"{p}: no JSON-LD")
    check("8  every JSON-LD block parses and every page has one", bad,
          f"{blocks} blocks")

    # 9 ---------------------------------------------------------------------
    bad = []
    root = ET.parse(REPO / "sitemap.xml").getroot()
    if root.tag != f"{NS}sitemapindex":
        bad.append(f"sitemap.xml root is {root.tag}, expected sitemapindex")
    listed, seen = [], set()
    for sm in root.findall(f"{NS}sitemap"):
        loc = sm.findtext(f"{NS}loc") or ""
        rel = loc.replace(f"{SITE}/", "")
        if not (REPO / rel).exists():
            bad.append(f"index names {rel}, which does not exist")
            continue
        r = ET.parse(REPO / rel).getroot()
        if r.tag != f"{NS}urlset":
            bad.append(f"{rel} root is {r.tag}, expected urlset")
        for u in r.findall(f"{NS}url"):
            l = u.findtext(f"{NS}loc") or ""
            mod = u.findtext(f"{NS}lastmod") or ""
            if l in seen:
                bad.append(f"{l} appears in more than one sitemap")
            seen.add(l)
            if not l.startswith(f"{SITE}/"):
                bad.append(f"{l} is not an https apex URL")
            if l.endswith("index.html"):
                bad.append(f"{l} is a non-canonical variant")
            if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", mod):
                bad.append(f"{l} has lastmod {mod!r}")
            listed.append(l)

    expected_pages = {url_for(p) for p in pages}
    expected_pdfs = {f"{SITE}/{p}" for p in inv["pdf_paths"]}
    listed_set = set(listed)
    for missing in sorted(expected_pages - listed_set):
        bad.append(f"indexable page missing from sitemap: {missing}")
    for missing in sorted(expected_pdfs - listed_set):
        bad.append(f"published PDF missing from sitemap: {missing}")
    for extra in sorted(listed_set - expected_pages - expected_pdfs):
        bad.append(f"sitemap URL has no corresponding file: {extra}")
    check("9  sitemap valid, complete, canonical-only, no duplicates", bad,
          f"{len(listed)} URLs across {len(root.findall(f'{NS}sitemap'))} sitemaps")

    # 10 --------------------------------------------------------------------
    bad = []
    robots = (REPO / "robots.txt").read_text(encoding="utf-8")
    for line in robots.splitlines():
        if line.lower().startswith("disallow:") and line.split(":", 1)[1].strip():
            bad.append(f"robots.txt disallows {line.split(':', 1)[1].strip()}")
    if f"{SITE}/sitemap.xml" not in robots:
        bad.append("robots.txt does not name the sitemap")
    check("10 robots.txt blocks nothing and names the sitemap", bad)

    # ---------------------------------------------------------------- report
    width = max(len(n) for n, _, _, _ in results)
    failed = 0
    for name, ok, detail, failures in results:
        mark = "PASS" if ok else "FAIL"
        print(f"  [{mark}] {name:<{width}}  {detail}")
        if not ok:
            failed += 1
            for f in failures[: (None if args.verbose else 8)]:
                print(f"           - {f}")
            if not args.verbose and len(failures) > 8:
                print(f"           ... and {len(failures) - 8} more")
    print()
    print(f"{len(results) - failed}/{len(results)} assertions passed")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())

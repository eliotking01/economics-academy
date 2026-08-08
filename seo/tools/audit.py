#!/usr/bin/env python3
"""Phase 2: run every defect rule against every page in the repo.

The GSC exports cover 132 URLs. The site has 461 indexable pages and Google
stopped crawling most sections months ago, so those exports describe a subset of
a subset. A page absent from them is unobserved, not clean. Every rule here is
mechanical and runs over the whole repo; GSC is used only to label a finding as
reported or unreported, never to decide what to look at.

Each finding carries the source file responsible - a template, a generator
script, or the page itself - because a defect on 200 pages is one bug in one
generator, not 200 bugs.

Offline: reads the working tree only, so it can be re-run after a fix without
touching the network. The live-only facts (which URL variants return 200) come
from seo/01-variants.csv, produced by crawl.py.

Usage:
    python3 seo/tools/audit.py                  # summary to stdout
    python3 seo/tools/audit.py --json out.json  # full findings
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from inventory import build as build_inventory, url_for, SITE  # noqa: E402
from pagemeta import jaccard, norm_space, parse_html, shingles  # noqa: E402

REPO = Path(__file__).resolve().parent.parent.parent

# Generators that write HTML. A link defect inside one of these reappears on the
# next build, so the fix belongs here rather than in the emitted page.
GENERATORS = {
    "past-paper-questions/": "scripts/build_past_paper_questions.py",
    "practice-questions/": "scripts/build_questions.py",
    "revision-notes/glossary/": "scripts/build_glossary.py",
    "flashcards/": "scripts/build_flashcards.py",
}
RUNTIME_TEMPLATES = ("templates/header.html", "templates/footer.html")

EXTERNAL_RE = re.compile(r"^(https?:|mailto:|tel:|data:|javascript:|//)", re.I)
ASSET_RE = re.compile(r"\.(css|js|png|jpe?g|gif|svg|ico|webmanifest|woff2?|ttf|xml|json|txt)$", re.I)

# Google truncates around these; outside is a warning, not a defect.
TITLE_MAX = 60
DESC_MIN, DESC_MAX = 70, 160
THIN_WORDS = 300


def source_for(page: str) -> str:
    """Which file must change to fix a defect on this page."""
    for prefix, script in GENERATORS.items():
        if page.startswith(prefix):
            return script
    return page


def git_lastmod(path: str) -> str:
    out = subprocess.run(
        ["git", "-C", str(REPO), "log", "-1", "--format=%cI", "--", path],
        capture_output=True, text=True,
    ).stdout.strip()
    return out[:10] if out else ""


class Audit:
    def __init__(self):
        self.inv = build_inventory()
        self.pages = self.inv["indexable"]
        self.all_html = self.pages + self.inv["deliberate_noindex"] + list(RUNTIME_TEMPLATES)
        self.tracked = set(
            subprocess.run(["git", "-C", str(REPO), "ls-files"],
                           capture_output=True, text=True, check=True).stdout.splitlines()
        )
        self.gsc = {r["url"] for r in self.inv["gsc"]}
        self.parsed: dict[str, object] = {}
        self.findings: list[dict] = []
        self.perf = self._perf()

        for p in self.all_html:
            self.parsed[p] = parse_html((REPO / p).read_text(encoding="utf-8", errors="replace"))

    # ------------------------------------------------------------------ util
    def _perf(self) -> dict[str, tuple[int, int]]:
        f = REPO / "seo" / "performance-pages.csv"
        if not f.exists():
            return {}
        out = {}
        for r in csv.DictReader(f.open(encoding="utf-8-sig")):
            try:
                out[r["Top pages"]] = (int(r["Clicks"]), int(r["Impressions"]))
            except (KeyError, ValueError):
                continue
        return out

    def reported(self, page: str) -> bool:
        """Is any URL form of this page present in the GSC exports?"""
        u = url_for(page)
        forms = {u, u.rstrip("/"), u + "index.html" if u.endswith("/") else u}
        if u.endswith("/"):
            forms.add(u + "index.html")
        if u.endswith(".html"):
            forms.add(u[: -len(".html")])
        return bool(forms & self.gsc)

    def add(self, cls: str, page: str, detail: str, **extra):
        self.findings.append({
            "defect_class": cls,
            "page": page,
            "url": url_for(page) if page in self.pages else f"{SITE}/{page}",
            "detail": detail,
            "source_file": source_for(page),
            "gsc_reported": self.reported(page) if page in self.pages else False,
            **extra,
        })

    # ----------------------------------------------------------------- rules
    def rule_noncanonical_links(self):
        """Internal links pointing at a URL that is not the target's canonical."""
        for page in self.all_html:
            p = self.parsed[page]
            for href in p.links:
                if EXTERNAL_RE.match(href) and "economicsacademy.co.uk" not in href:
                    continue
                h = href.split("#")[0].split("?")[0]
                h = re.sub(r"^https?://(www\.)?economicsacademy\.co\.uk", "", h)
                if not h.startswith("/"):
                    continue
                if h == "/index.html":
                    self.add("link-noncanonical", page,
                             'href="/index.html" should be href="/"', target=h)
                elif h.endswith("/index.html"):
                    self.add("link-noncanonical", page,
                             f'href="{h}" should be href="{h[:-len("index.html")]}"',
                             target=h)

    def rule_parameterised_links(self):
        """Internal links carrying a query string.

        Not a duplication defect - the target page's hardcoded canonical points
        at the clean URL, so Google consolidates correctly. It is a crawl-budget
        cost: each distinct ?topic= value is a separate URL Googlebot must fetch
        before discarding, and that competes with the pages it has never seen.
        """
        for page in self.all_html:
            for href in self.parsed[page].links:
                h = re.sub(r"^https?://(www\.)?economicsacademy\.co\.uk", "", href)
                if not h.startswith("/") or "?" not in h:
                    continue
                self.add("link-parameterised", page,
                         f'href="{h}" adds a crawlable URL for {h.split("?")[0]}',
                         target=h.split("?")[0])

    def rule_link_targets(self):
        """Dead or case-mismatched internal targets, resolved case-sensitively.

        git ls-files is the oracle, not the filesystem: macOS APFS is
        case-insensitive so os.path.exists() cannot see /Revision-Notes/, which
        404s on GitHub Pages.
        """
        for page in self.all_html:
            p = self.parsed[page]
            for href in list(p.links) + list(p.srcs):
                if EXTERNAL_RE.match(href) and "economicsacademy.co.uk" not in href:
                    continue
                h = href.split("#")[0].split("?")[0]
                h = re.sub(r"^https?://(www\.)?economicsacademy\.co\.uk", "", h)
                if not h.startswith("/") or h == "/":
                    continue
                target = h[1:] + ("index.html" if h.endswith("/") else "")
                if target in self.tracked:
                    continue
                lower = {t.lower(): t for t in self.tracked}
                if target.lower() in lower:
                    self.add("link-case-mismatch", page,
                             f'href="{href}" -> repo has "{lower[target.lower()]}"',
                             target=h)
                else:
                    self.add("link-dead", page, f'href="{href}" resolves to nothing',
                             target=h)

    def rule_canonical(self):
        for page in self.pages:
            p = self.parsed[page]
            want = url_for(page)
            if not p.canonical:
                self.add("canonical-missing", page, "no rel=canonical")
            elif p.canonical != want:
                self.add("canonical-wrong", page,
                         f"canonical={p.canonical} but page is served at {want}",
                         expected=want, actual=p.canonical)
            if p.og_url and p.canonical and p.og_url != p.canonical:
                self.add("ogurl-mismatch", page,
                         f"og:url={p.og_url} != canonical={p.canonical}")

    def rule_head_tags(self):
        for page in self.pages:
            p = self.parsed[page]
            if not p.title:
                self.add("title-missing", page, "no <title>")
            elif len(p.title) > TITLE_MAX:
                self.add("title-long", page, f"{len(p.title)} chars (>{TITLE_MAX})")
            if not p.description:
                self.add("description-missing", page, "no meta description")
            elif not (DESC_MIN <= len(p.description) <= DESC_MAX):
                self.add("description-length", page,
                         f"{len(p.description)} chars (target {DESC_MIN}-{DESC_MAX})")
            if not p.h1:
                self.add("h1-missing", page, "no <h1>")
            elif len(p.h1) > 1:
                self.add("h1-multiple", page, f"{len(p.h1)} <h1> elements")
            if p.og_title and p.title and norm_space(p.og_title) != p.title:
                self.add("ogtitle-mismatch", page,
                         f"og:title={p.og_title!r} != <title>={p.title!r}")
            if p.twitter_title and p.title and norm_space(p.twitter_title) != p.title:
                self.add("twittertitle-mismatch", page,
                         f"twitter:title={p.twitter_title!r} != <title>={p.title!r}")
            if not p.lang:
                self.add("lang-missing", page, "<html> has no lang attribute")
            elif p.lang != "en-GB":
                self.add("lang-wrong", page, f'lang="{p.lang}" (house standard is en-GB)')

    def rule_robots(self):
        for page in self.pages:
            r = self.parsed[page].robots.lower()
            if "noindex" in r:
                self.add("noindex-accidental", page,
                         f'meta robots="{self.parsed[page].robots}" on an indexable page')

    def rule_jsonld(self):
        for page in self.pages:
            p = self.parsed[page]
            for err in p.invalid_jsonld():
                self.add("jsonld-invalid", page, err)
            if not p.jsonld:
                self.add("jsonld-missing", page, "no JSON-LD block")

    def rule_duplicates(self):
        titles, descs = defaultdict(list), defaultdict(list)
        for page in self.pages:
            p = self.parsed[page]
            if p.title:
                titles[p.title].append(page)
            if p.description:
                descs[p.description].append(page)
        for t, pages in titles.items():
            if len(pages) > 1:
                for page in pages:
                    self.add("title-duplicate", page,
                             f"{len(pages)} pages share this title: {t!r}",
                             shared_with=[x for x in pages if x != page])
        for d, pages in descs.items():
            if len(pages) > 1:
                for page in pages:
                    self.add("description-duplicate", page,
                             f"{len(pages)} pages share this description",
                             shared_with=[x for x in pages if x != page])

    def rule_thin(self):
        for page in self.pages:
            w = self.parsed[page].words
            if w < THIN_WORDS:
                self.add("thin-content", page, f"{w} words (<{THIN_WORDS})", words=w)

    def rule_near_duplicates(self):
        """Near-duplicate clusters, within a section only.

        Cross-section comparison is meaningless here: a notes page and its
        practice-questions twin share a topic but not a template. Comparison is
        O(n^2) inside each section, which is fine at this size.
        """
        by_section = defaultdict(list)
        for page in self.pages:
            by_section[page.split("/")[0] if "/" in page else "ROOT"].append(page)
        for section, pages in by_section.items():
            sh = {p: shingles(self.parsed[p].text) for p in pages}
            for i, a in enumerate(pages):
                for b in pages[i + 1:]:
                    j = jaccard(sh[a], sh[b])
                    if j >= 0.80:
                        self.add("near-duplicate", a,
                                 f"{j:.0%} shingle overlap with {b}",
                                 other=b, similarity=round(j, 3))

    def rule_sitemap(self):
        in_sitemap = set(self.inv["sitemap_urls"])
        for page in self.pages:
            if url_for(page) not in in_sitemap:
                self.add("sitemap-missing", page, "indexable page absent from sitemap.xml")
        # PDFs are in the sitemap by decision; they are not HTML pages, so they
        # would otherwise all read as stale entries here.
        expected = {url_for(p) for p in self.pages}
        expected |= {f"{SITE}/{p}" for p in self.inv["pdf_paths"]}
        for u in in_sitemap - expected:
            self.findings.append({
                "defect_class": "sitemap-stale", "page": "", "url": u,
                "detail": "sitemap URL has no corresponding indexable page",
                "source_file": "sitemap.xml", "gsc_reported": u in self.gsc,
            })

    def rule_orphans(self):
        """Pages with no inbound link from any other page's static HTML.

        Links from templates/header.html and footer.html do not count: they are
        injected at runtime by JavaScript, so a crawler that does not render
        never sees them.
        """
        inbound = Counter()
        for page in self.all_html:
            if page in RUNTIME_TEMPLATES:
                continue
            for href in self.parsed[page].links:
                h = href.split("#")[0].split("?")[0]
                h = re.sub(r"^https?://(www\.)?economicsacademy\.co\.uk", "", h)
                if not h.startswith("/"):
                    continue
                h = re.sub(r"index\.html$", "", h)
                inbound[h] += 1
        for page in self.pages:
            u = url_for(page).replace(SITE, "")
            if inbound.get(u, 0) == 0:
                self.add("orphan", page, "no inbound internal link outside the runtime nav")

    def rule_variants(self):
        """Duplicate URL variants both returning 200, from the live probe.

        Reads seo/01-variants.csv, produced by seo/tools/probe_variants.py. That
        file records a status per variant kind but not the URL it probed, so the
        URL is reconstructed here from the same rule the prober used.
        """
        f = REPO / "seo" / "01-variants.csv"
        if not f.exists():
            return
        from probe_variants import variants_for  # local: needs no network

        for r in csv.DictReader(f.open(encoding="utf-8")):
            page = r["page"]
            live = [k for k in ("dir", "dir_index", "html", "extensionless")
                    if str(r.get(f"{k}_status", "")) == "200"]
            if len(live) < 2:
                continue
            canonical_kind = "dir" if page.endswith("index.html") else "html"
            vs = variants_for(page)
            for k in live:
                if k == canonical_kind or k not in vs:
                    continue
                scheme, host, path = vs[k]
                self.add("duplicate-url-variant", page,
                         f"{scheme}://{host}{path} also returns 200 "
                         f"alongside {url_for(page)}",
                         variant_kind=k, variant_url=f"{scheme}://{host}{path}")

    # ------------------------------------------------------------------- run
    def run(self):
        for name in dir(self):
            if name.startswith("rule_"):
                getattr(self, name)()
        return self.findings


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", default="")
    args = ap.parse_args()

    a = Audit()
    findings = a.run()

    by_class = defaultdict(lambda: {"reported": 0, "unreported": 0, "pages": set(),
                                    "sources": Counter()})
    for f in findings:
        d = by_class[f["defect_class"]]
        d["reported" if f["gsc_reported"] else "unreported"] += 1
        if f["page"]:
            d["pages"].add(f["page"])
        d["sources"][f["source_file"]] += 1

    print(f"{'defect class':<26}{'reported':>9}{'unreported':>12}{'total':>8}{'pages':>8}  top source")
    print("-" * 100)
    for cls in sorted(by_class, key=lambda c: -(by_class[c]["reported"] + by_class[c]["unreported"])):
        d = by_class[cls]
        tot = d["reported"] + d["unreported"]
        top = d["sources"].most_common(1)[0]
        src = top[0] if top[1] < tot else f"{top[0]} ({top[1]}/{tot})"
        print(f"{cls:<26}{d['reported']:>9}{d['unreported']:>12}{tot:>8}{len(d['pages']):>8}  {src[:44]}")
    print("-" * 100)
    print(f"{'TOTAL':<26}"
          f"{sum(d['reported'] for d in by_class.values()):>9}"
          f"{sum(d['unreported'] for d in by_class.values()):>12}"
          f"{len(findings):>8}")

    if args.json:
        Path(args.json).write_text(json.dumps(findings, indent=2, default=list), encoding="utf-8")
        print(f"\nwrote {args.json} ({len(findings)} findings)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

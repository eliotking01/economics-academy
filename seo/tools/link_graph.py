#!/usr/bin/env python3
"""Task A1: the internal link graph, and the cross-section topic map.

Read only. Writes nothing but its three reports.

This is about CRAWL PRIORITY DISTRIBUTION, not link hygiene - hygiene is
already asserted by seo/tools/verify_seo.py and is green. The question here is
which pages the link structure tells Google to care about, and whether that
matches which pages deserve it.

TWO GRAPHS, ALWAYS REPORTED TOGETHER
------------------------------------
The site's header and footer are not in any page's HTML. They are fetched at
runtime by js/components/inject-templates.js and injected into placeholder
divs. So there are two different true answers to "how deep is this page":

    static   - only links written in the page itself. What a crawler that does
               not execute JavaScript sees.
    rendered - static plus the 38 header/footer links, applied from every page.
               What Googlebot sees after rendering.

Reporting one number would be misleading in whichever direction it was picked,
so every depth and orphan figure below is given both ways.

THE CROSS-BOARD HAZARD
----------------------
Edexcel uses official spec codes; AQA uses the site owner's own scheme. They
share the X.Y.Z format and 37 bare codes collide outright - 1.1.1 is
"Economics as a Social Science" on Edexcel and "Economic Methodology" on AQA.
Matching on a bare topic code would mis-link 37 topics, resolve to real pages,
404 nothing and pass every existing assertion. The only symptom would be
students sent to the wrong board.

So the topic map is keyed on (section, board directory, filename) and is built
from two independent sources that must agree before a row is called "high":

    structural  - the board directory in the URL path, plus the filename slug
    declared    - past-paper-questions-data/taxonomy.json, which carries an
                  explicit board on every topic record, plus the <h1> of the
                  target page

    python3 seo/tools/link_graph.py
    python3 seo/tools/link_graph.py --write     # emit the three reports
"""

from __future__ import annotations

import argparse
import collections
import csv
import html
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from inventory import build as build_inventory, url_for, SITE  # noqa: E402

REPO = Path(__file__).resolve().parent.parent.parent
TEMPLATES = ["templates/header.html", "templates/footer.html"]
EXTERNAL_RE = re.compile(r"^(https?:|mailto:|tel:|data:|javascript:|//)", re.I)
# Prettier wraps a long anchor so the closing tag is split - "</a" on one line
# and ">" on the next. Matching a literal "</a>" silently found only 4 of the
# 18 links on a typical notes page and made every cross-section figure read 0%.
ANCHOR_RE = re.compile(r"<a\b([^>]*)>(.*?)</a\s*>", re.I | re.S)
HREF_RE = re.compile(r'href="([^"]*)"', re.I)
TAG_RE = re.compile(r"<[^>]+>")
H1_RE = re.compile(r"<h1[^>]*>(.*?)</h1>", re.I | re.S)
SPEC_RE = re.compile(r'class="spec-alert"[^>]*>(.*?)</div>', re.I | re.S)
SPEC_FIELDS_RE = re.compile(r"Specification Coverage:\s*([A-Za-z ]+?)\s+unit\s+"
                            r"(\d+(?:\.\d+)+)", re.I)
# Board as the spec-alert writes it -> the board key the graph compares on.
BOARD_NAMES = {"edexcel": "edexcel", "aqa": "aqa"}

# Anchors that carry no topical signal. Judged, not guessed: each is a phrase
# that would read identically on any page of the site.
GENERIC = {
    "click here", "here", "read more", "more", "learn more", "find out more",
    "view", "view all", "see more", "next", "previous", "back", "home",
    "this page", "link", "download", "start", "go", "continue",
}

# Board directory -> (board key, human label). The board key is what the
# cross-board assertion compares. A directory not listed here is board-agnostic.
BOARD_OF_DIR = {
    "edexcel-theme-1": ("edexcel", "Edexcel Theme 1"),
    "edexcel-theme-2": ("edexcel", "Edexcel Theme 2"),
    "edexcel-theme-3": ("edexcel", "Edexcel Theme 3"),
    "edexcel-theme-4": ("edexcel", "Edexcel Theme 4"),
    "aqa-a2-micro": ("aqa", "AQA Microeconomics"),
    "aqa-a2-macro": ("aqa", "AQA Macroeconomics"),
    "edexcel-a": ("edexcel", "Edexcel A"),
    "edexcel": ("edexcel", "Edexcel"),
    "edexcel-b": ("edexcel-b", "Edexcel B"),
    "aqa": ("aqa", "AQA"),
    "ocr": ("ocr", "OCR"),
}


def text_of(fragment: str) -> str:
    return re.sub(r"\s+", " ", html.unescape(TAG_RE.sub(" ", fragment))).strip()


def board_of(page: str) -> str | None:
    """Exam board a page belongs to, or None if it is board-agnostic."""
    for part in Path(page).parts:
        if part in BOARD_OF_DIR:
            return BOARD_OF_DIR[part][0]
    return None


class Graph:
    def __init__(self) -> None:
        inv = build_inventory()
        self.pages: list[str] = list(inv["indexable"])
        self.all_html = self.pages + inv["deliberate_noindex"]
        self.pdfs = set(inv["pdf_paths"])
        self.text = {p: (REPO / p).read_text(errors="replace")
                     for p in self.all_html + TEMPLATES}

        # canonical site path -> repo file, so a link can be resolved to a node
        self.by_url: dict[str, str] = {}
        for p in self.all_html:
            self.by_url[url_for(p).replace(SITE, "") or "/"] = p
        for p in self.pdfs:
            self.by_url["/" + p] = p

        self.out: dict[str, list[tuple[str, str]]] = {}   # page -> [(target, anchor)]
        self.pdf_links: dict[str, list[str]] = {}
        for p in self.all_html + TEMPLATES:
            self.out[p], self.pdf_links[p] = self._edges(p)

        self.tmpl_targets = sorted({t for tp in TEMPLATES for t, _ in self.out[tp]})

    def _edges(self, page: str) -> tuple[list[tuple[str, str]], list[str]]:
        edges, pdfs = [], []
        for m in ANCHOR_RE.finditer(self.text[page]):
            href = HREF_RE.search(m.group(1))
            if not href:
                continue
            v = re.sub(r"^https?://(www\.)?economicsacademy\.co\.uk", "",
                       href.group(1).strip())
            if EXTERNAL_RE.match(v) or not v.startswith("/"):
                continue
            v = v.split("#")[0].split("?")[0]
            target = self.by_url.get(v)
            if target is None:
                continue
            if target in self.pdfs:
                pdfs.append(target)
            elif target != page:
                edges.append((target, text_of(m.group(2))))
        return edges, pdfs

    def adjacency(self, rendered: bool) -> dict[str, set[str]]:
        adj = {p: {t for t, _ in self.out[p]} for p in self.all_html}
        if rendered:
            extra = set(self.tmpl_targets)
            for p in adj:
                adj[p] |= extra - {p}
        return adj

    def depths(self, rendered: bool) -> dict[str, int]:
        adj = self.adjacency(rendered)
        seen = {"index.html": 0}
        frontier = ["index.html"]
        d = 0
        while frontier:
            d += 1
            nxt = []
            for p in frontier:
                for t in adj.get(p, ()):
                    if t not in seen:
                        seen[t] = d
                        nxt.append(t)
            frontier = nxt
        return seen

    def inbound(self, rendered: bool) -> collections.Counter:
        c = collections.Counter()
        for p in self.all_html:
            for t in {t for t, _ in self.out[p]}:
                c[t] += 1
        if rendered:
            for t in self.tmpl_targets:
                c[t] += len(self.all_html) - 1
        for p in self.pages:
            c.setdefault(p, 0)
        return c


# ---------------------------------------------------------------- topic map

def topic_rows(g: Graph) -> list[dict]:
    """One row per (board, topic) with whatever exists in each section."""
    notes: dict[tuple[str, str], str] = {}
    prac: dict[tuple[str, str], str] = {}
    for p in g.pages:
        parts = Path(p).parts
        if len(parts) < 3 or parts[-1] == "index.html":
            continue
        d, fn = parts[1], parts[-1]
        if d not in BOARD_OF_DIR:
            continue
        m = re.match(r"^(\d+(?:-\d+)+)-(.*)\.html$", fn)
        if not m:
            continue
        key = (d, m.group(1))
        if parts[0] == "revision-notes":
            notes[key] = p
        elif parts[0] == "practice-questions":
            prac[key] = p

    tax = json.loads((REPO / "past-paper-questions-data" / "taxonomy.json").read_text())
    # declared: ppq topic slug -> board, from the file that carries board
    # explicitly. Nesting is boards -> groups -> units -> topics; each group
    # also names the notes directory it belongs to, which is a second
    # board-safe anchor and is recorded as declared_dir.
    declared: dict[str, str] = {}
    declared_dir: dict[str, str] = {}
    for b in tax["boards"]:
        for grp in b.get("groups", []):
            nd = (grp.get("notesDir") or "").strip("/").split("/")[-1]
            for unit in grp.get("units", []):
                for t in unit.get("topics", []):
                    declared[t["slug"]] = b["board"]
                    declared_dir[t["slug"]] = nd

    ppq_pages = {}
    for p in g.pages:
        parts = Path(p).parts
        if parts[0] == "past-paper-questions" and parts[-1] == "index.html" and len(parts) == 4:
            ppq_pages[parts[2]] = (p, BOARD_OF_DIR.get(parts[1], (None,))[0])

    fc = {}
    for p in g.pages:
        parts = Path(p).parts
        if parts[0] == "flashcards" and parts[-1] == "index.html" and len(parts) >= 3:
            fc[(BOARD_OF_DIR.get(parts[1], (None,))[0], parts[2])] = p

    rows = []
    for (d, code), notes_path in sorted(notes.items()):
        board = BOARD_OF_DIR[d][0]
        slug = re.match(r"^\d+(?:-\d+)+-(.*)\.html$", Path(notes_path).name).group(1)
        prac_path = prac.get((d, code), "")

        # ppq: match by the full "<code>-<slug>" directory name, then REQUIRE the
        # declared board in taxonomy.json to agree with the structural board.
        ppq_slug = f"{code}-{slug}"
        ppq_path, ppq_conf, ev = "", "", []
        hit = ppq_pages.get(ppq_slug)
        if hit:
            path, struct_board = hit
            decl_board = declared.get(ppq_slug)
            decl_dir = declared_dir.get(ppq_slug)
            if struct_board == board and decl_board == board and decl_dir == d:
                ppq_path, ppq_conf = path, "high"
                ev.append("ppq: dir+taxonomy+notesDir agree")
            elif struct_board == board and decl_board == board:
                ppq_path, ppq_conf = path, "medium"
                ev.append(f"ppq: notesDir says {decl_dir!r}, page is in {d!r}")
            elif struct_board == board:
                ppq_path, ppq_conf = path, "medium"
                ev.append(f"ppq: taxonomy says {decl_board!r}, dir says {struct_board!r}")
            else:
                ppq_conf = "low"
                ev.append(f"ppq: BOARD MISMATCH dir={struct_board} decl={decl_board}")

        # slug agreement between notes and practice is the structural evidence
        slug_ok = bool(prac_path) and Path(prac_path).name == Path(notes_path).name
        if prac_path:
            ev.append("practice: identical filename" if slug_ok
                      else "practice: SLUG DIFFERS")

        # The second source has to be DECLARED IN THE PAGE and has to name the
        # board, or it cannot rule out the cross-board hazard. Titles do not
        # qualify: the notes say "2.1.1 The Objectives of Government Economic
        # Policy" where the practice page says "2.1.1 Objectives of Government
        # Policy", and the Edexcel notes h1 carries no code at all. Two things
        # do qualify, and both are on 166 of 166 pages:
        #
        #   notes    - the spec-alert, "Specification Coverage: {Board} unit X.Y.Z"
        #   practice - data-board and data-spec on every question <li>
        #
        # Each states the board in the page's own content, so agreement with
        # the directory is real evidence and not a restatement of the URL.
        want = code.replace("-", ".")
        declared_ok = True

        m = SPEC_RE.search(g.text[notes_path])
        got = SPEC_FIELDS_RE.search(text_of(m.group(1))) if m else None
        if got and BOARD_NAMES.get(got.group(1).lower()) == board and got.group(2) == want:
            ev.append(f"notes spec-alert declares {got.group(1)} unit {got.group(2)}")
        else:
            declared_ok = False
            ev.append(f"notes spec-alert MISMATCH: {got.groups() if got else 'absent'}"
                      f" vs ({board}, {want})")

        if prac_path:
            b = set(re.findall(r'data-board="([^"]+)"', g.text[prac_path]))
            c = set(re.findall(r'data-spec="([^"]+)"', g.text[prac_path]))
            if b == {board} and c == {want}:
                ev.append(f"practice declares data-board={board} data-spec={want}")
            else:
                declared_ok = False
                ev.append(f"practice data-* MISMATCH: board={b or '-'} spec={c or '-'}")

        codes_ok = declared_ok

        conf = "high" if (slug_ok and codes_ok) else ("medium" if prac_path else "low")
        if ppq_conf == "low":
            conf = "low"

        rows.append({
            "board": board,
            "module": BOARD_OF_DIR[d][1],
            "topic_code": code.replace("-", "."),
            "notes_url": url_for(notes_path).replace(SITE, ""),
            "practice_url": url_for(prac_path).replace(SITE, "") if prac_path else "",
            "pastpaper_url": url_for(ppq_path).replace(SITE, "") if ppq_path else "",
            "flashcard_url": next(
                (url_for(v).replace(SITE, "") for (fb, _), v in fc.items() if fb == board
                 and _ in (d.replace("edexcel-theme-", "theme-"),
                           d.replace("aqa-a2-", ""))), ""),
            "confidence": conf,
            "evidence": "; ".join(ev),
        })
    return rows


# ------------------------------------------------------------------ report

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args()

    g = Graph()
    out = []
    P = out.append

    P(f"pages (nodes): {len(g.pages)}   PDFs (not nodes): {len(g.pdfs)}")
    P(f"template links applied in the rendered graph: {len(g.tmpl_targets)}")

    for rendered in (False, True):
        name = "rendered" if rendered else "static"
        d = g.depths(rendered)
        hist = collections.Counter(d.values())
        unreach = [p for p in g.pages if p not in d]
        P(f"\n=== {name} graph ===")
        P("  depth histogram: " + ", ".join(f"{k}:{hist[k]}" for k in sorted(hist)))
        P(f"  unreachable from homepage: {len(unreach)}")
        deep = sorted(p for p in g.pages if p in d and d[p] >= 4)
        P(f"  pages at depth >=4: {len(deep)}")
        for p in deep[:15]:
            P(f"      d{d[p]}  {p}")
        if unreach:
            P(f"  unreachable examples: {unreach[:6]}")
        inb = g.inbound(rendered)
        low = [p for p in g.pages if inb[p] < 3]
        P(f"  pages with <3 inbound links: {len(low)}")

    inb = g.inbound(False)
    P("\n=== inbound (static), bottom 25 ===")
    for p, n in sorted(((p, inb[p]) for p in g.pages), key=lambda x: (x[1], x[0]))[:25]:
        P(f"   {n:3d}  {p}")
    P("\n=== inbound (static), top 10 ===")
    for p, n in sorted(((p, inb[p]) for p in g.pages), key=lambda x: -x[1])[:10]:
        P(f"   {n:4d}  {p}")

    # cross-section coverage, by board
    # A link to a section's HUB is not topic coverage. The notes link to
    # /past-paper-questions/?board=..&topic=.. wherever the topic has no page
    # of its own, and that query string strips to the hub - so counting any
    # link into the section reads 84% where direct topic-page coverage is 40%.
    # Both are reported; the second is the one that matters for crawl priority.
    P("\n=== cross-section coverage by board (static) ===")
    P("   'any' = any link into the section, hub included")
    P("   'topic' = a link to a specific topic page in that section")
    sections = ("revision-notes", "practice-questions", "past-paper-questions")

    def is_topic_page(t: str) -> bool:
        parts = Path(t).parts
        if parts[-1] == "index.html":
            return len(parts) == 4      # /section/board/topic-slug/index.html
        return len(parts) == 3          # /section/board/topic.html

    for src in sections:
        for dst in sections:
            if src == dst:
                continue
            for bk in ("edexcel", "aqa"):
                srcs = [p for p in g.pages if Path(p).parts[0] == src
                        and board_of(p) == bk and Path(p).name != "index.html"]
                if not srcs:
                    continue
                any_ = sum(1 for p in srcs
                           if any(Path(t).parts[0] == dst for t, _ in g.out[p]))
                top = sum(1 for p in srcs
                          if any(Path(t).parts[0] == dst and is_topic_page(t)
                                 for t, _ in g.out[p]))
                P(f"   {src:20}->{dst:20} {bk:8}"
                  f"  any {any_:3d}/{len(srcs):3d} {any_/len(srcs)*100:5.1f}%"
                  f"   topic {top:3d}/{len(srcs):3d} {top/len(srcs)*100:5.1f}%")

    # generic anchors
    P("\n=== anchor text ===")
    anchors: dict[str, collections.Counter] = collections.defaultdict(collections.Counter)
    for p in g.all_html:
        for t, a in g.out[p]:
            anchors[t][a.lower()] += 1
    gen = [(t, c) for t, c in anchors.items()
           if sum(v for k, v in c.items() if k in GENERIC) > 0]
    P(f"  targets receiving >=1 generic anchor: {len(gen)}")
    dom = [(t, c.most_common(1)[0]) for t, c in anchors.items()
           if sum(c.values()) >= 5 and c.most_common(1)[0][1] / sum(c.values()) > 0.9]
    P(f"  targets whose inbound anchors are >90% one identical string: {len(dom)}")
    for t, (a, n) in sorted(dom, key=lambda x: -x[1][1])[:10]:
        P(f"      {n:4d}x  {a[:52]!r:56} -> {t}")

    # reciprocity: does a topic page link to any SIBLING topic page, or only
    # up to its hub? Pure hub-and-spoke gives a crawler one path in and one
    # path out and concentrates every signal on the index page.
    P("\n=== reciprocity: lateral sibling links (static) ===")
    for sec in ("revision-notes", "practice-questions", "past-paper-questions"):
        topics = [p for p in g.pages if Path(p).parts[0] == sec
                  and Path(p).name != "index.html" or
                  (Path(p).parts[0] == sec and Path(p).name == "index.html"
                   and len(Path(p).parts) == 4)]
        topics = [p for p in topics if board_of(p)]
        if not topics:
            continue
        lateral = 0
        for p in topics:
            sibs = {t for t, _ in g.out[p]
                    if t != p and Path(t).parts[0] == sec and board_of(t) == board_of(p)
                    and Path(t).name != "index.html"}
            lateral += bool(sibs)
        P(f"   {sec:22} {lateral:3d}/{len(topics):3d} pages link to a sibling"
          f"  {lateral/len(topics)*100:5.1f}%")

    # link-starved pages that already earn impressions - the top priority
    P("\n=== pages earning impressions, ranked by how few inbound links they have ===")
    perf = REPO / "seo" / "performance-pages.csv"
    if perf.exists():
        rows_p = list(csv.DictReader(perf.open()))
        seen = []
        for r in rows_p:
            u = r["Top pages"].replace(SITE, "") or "/"
            pg = g.by_url.get(u.split("?")[0])
            if pg and pg in inb:
                seen.append((inb[pg], int(r["Impressions"]), int(r["Clicks"]), pg))
        for n, imp, clk, pg in sorted(seen)[:12]:
            P(f"   inbound {n:3d}  impressions {imp:5d}  clicks {clk:4d}  {pg}")

    # sitemap-only pages
    d_static, d_rend = g.depths(False), g.depths(True)
    only = [p for p in g.pages if inb[p] == 0]
    P(f"\n=== reachable only from the sitemap (0 static inbound): {len(only)} ===")
    for p in only[:20]:
        P(f"   rendered-depth {d_rend.get(p, '-')}  {p}")

    # PDFs
    linkers = {p for p in g.all_html if g.pdf_links[p]}
    P(f"\n=== PDFs: {len(g.pdfs)} files, linked from {len(linkers)} pages ===")

    rows = topic_rows(g)
    conf = collections.Counter(r["confidence"] for r in rows)
    P(f"\n=== topic map: {len(rows)} rows, confidence {dict(conf)} ===")
    P(f"  with practice_url : {sum(1 for r in rows if r['practice_url'])}")
    P(f"  with pastpaper_url: {sum(1 for r in rows if r['pastpaper_url'])}")
    P(f"  with flashcard_url: {sum(1 for r in rows if r['flashcard_url'])}")

    report = "\n".join(out)
    print(report)

    if args.write:
        csv_path = REPO / "seo" / "07a-topic-map.csv"
        with csv_path.open("w", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=[
                "board", "module", "topic_code", "notes_url", "practice_url",
                "pastpaper_url", "flashcard_url", "confidence", "evidence"])
            w.writeheader()
            w.writerows(rows)
        print(f"\nwrote {csv_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

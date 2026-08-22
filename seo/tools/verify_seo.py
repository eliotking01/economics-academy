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
   11  every page is within 3 clicks of the homepage on the rendered graph
   12  every page has 3 or more inbound internal links
   13  no link crosses an exam board except a declared twin-board pair
   14  every indexable page below the homepage has a BreadcrumbList
   15  every notes topic title matches the brief's formula and fits 65 chars
   16  every notes topic description is page-specific and 145-158 characters
   17  every notes topic carries dateModified and a visible update date
   18  every notes topic with a declared twin links to it, once, both ways
   19  no two notes pages share an <h1>
   20  every notes topic names its author on the page, and the schema agrees

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

    # ------------------------------------------------- 11-14: architecture
    # Added by the seo/architecture-pass work. These lock in what Task A and
    # Task B established so a future edit cannot quietly undo it.
    #
    # The link graph is built by seo/tools/link_graph.py, which is the single
    # definition of an edge, a board and a topic page. Restating any of that
    # here would let the two drift apart.
    from link_graph import Graph, board_of  # noqa: E402

    g = Graph()

    # 11 --------------------------------------------------------------------
    # Depth is measured on the RENDERED graph, because the header and footer
    # are fetched at runtime and Googlebot renders. The static graph bottoms
    # out at 4 and always will while the nav is injected.
    depths = g.depths(rendered=True)
    bad = [f"{p} at depth {depths[p]}" for p in g.pages
           if p in depths and depths[p] > 3]
    bad += [f"{p} unreachable from the homepage" for p in g.pages
            if p not in depths]
    check("11 every page within 3 clicks of the homepage (rendered)", bad,
          f"max depth {max(depths.values())}")

    # 12 --------------------------------------------------------------------
    # Three pages sit below the bar for reasons that are correct, so they are
    # named rather than the bar being lowered to 2:
    #   3-2-1-business-objectives is the only topic alone in its unit, so it
    #     has no siblings to link it;
    #   the two glossary board pages are reached from the glossary hub and
    #     from each other, which is the whole of their intended entry path.
    THIN_BY_DESIGN = {
        "practice-questions/edexcel-theme-3/3-2-1-business-objectives.html",
        "revision-notes/glossary/aqa/index.html",
        "revision-notes/glossary/edexcel-a/index.html",
    }
    inbound = g.inbound(rendered=True)
    bad = [f"{p} has {inbound[p]} inbound" for p in g.pages
           if inbound[p] < 3 and p not in THIN_BY_DESIGN]
    check("12 every page has 3+ inbound internal links (rendered)", bad,
          f"{len(THIN_BY_DESIGN)} allowed exceptions")

    # 13 --------------------------------------------------------------------
    # The highest-risk failure mode in the whole architecture pass. Edexcel
    # and AQA share the X.Y.Z topic-code format and 37 bare codes collide
    # outright - 1.1.1 is "Economics as a Social Science" on Edexcel and
    # "Economic Methodology" on AQA. A cross-board link resolves to a real
    # page, 404s nothing and passes every other assertion here; the only
    # symptom is a student sent to the wrong board's content.
    #
    # The two allowed pairs are the glossary's own board selector, which is
    # the one place on the site where crossing boards is the point.
    #
    # Links inside the baked header and footer are not this check's subject.
    # The nav offers every board from every page and always has - before
    # Wave 2 Phase 7 it was injected at runtime, so it was invisible here, and
    # baking it in put 3,887 menu entries in front of an assertion written
    # about content links. Excluding the chrome keeps the assertion at full
    # strength for the thing it was written to catch: a page's own prose
    # linking a student to the other board's version of a topic.
    BOARD_SWITCHER = {
        ("revision-notes/glossary/aqa/index.html",
         "revision-notes/glossary/edexcel-a/index.html"),
        ("revision-notes/glossary/edexcel-a/index.html",
         "revision-notes/glossary/aqa/index.html"),
    }

    # AMENDED 2026-08-21 by the notes on-page SEO pass, and deliberately not
    # weakened. The 166 topic pages now each carry a link to the page covering
    # the same topic on the other board, because a student searching "monopoly
    # a level economics" without naming a board should not land on the wrong
    # one with no way across - seo/14-notes-keyword-brief.md §8.
    #
    # The exemption is NOT "anything inside the twin block". It is the exact
    # (source, target) pair appearing in scripts/notes_twins.TWINS, which is
    # a written-down, hand-verified table with its evidence recorded per row.
    # So this assertion still fails on a cross-board link that the table does
    # not name - including one inside the twin block, if the generator ever
    # started deriving the target instead of reading it - which is the failure
    # it was written to catch: a student sent to the wrong board's content.
    sys.path.insert(0, str(REPO / "scripts"))
    import notes_twins  # noqa: E402

    def twin_pair(page: str, target: str) -> bool:
        def key(p: str):
            parts = Path(p).parts
            return (parts[1], Path(p).stem) if len(parts) == 3 else None
        a, b = key(page), key(target)
        return bool(a and b and notes_twins.TWINS.get(a) == b)

    bad = []
    for page in g.pages:
        src = board_of(page)
        if not src:
            continue
        chrome = g.chrome.get(page, set())
        for target, anchor in g.out[page]:
            if (target, anchor) in chrome:
                continue
            dst = board_of(target)
            if not dst or dst == src:
                continue
            if (page, target) in BOARD_SWITCHER or twin_pair(page, target):
                continue
            bad.append(f"{page} -> {target} ({src} -> {dst}) {anchor!r}")
    check("13 no link crosses an exam board except a declared twin", bad,
          f"{len(notes_twins.TWINS)} declared twin pairs, "
          f"{len(BOARD_SWITCHER)} glossary, plus the site nav")

    # 14 --------------------------------------------------------------------
    # Assertion 8 already proves every JSON-LD block parses. This proves the
    # one type that still earns a rich result is actually present. The
    # homepage is excluded because a homepage is the root of the trail.
    bad = []
    for page in pages:
        if page == "index.html":
            continue
        blocks = parsed[page].jsonld
        if not any("BreadcrumbList" in b for b in blocks):
            bad.append(page)
    check("14 every indexable page below the homepage has a BreadcrumbList",
          bad, f"{len(pages) - 1} pages")

    # ------------------------------------------- 15-19: the notes on-page pass
    # Added 2026-08-21 by the revision-notes on-page SEO audit. Each locks in
    # one thing that pass established, so a later edit cannot quietly undo it
    # - which is the only reason any of this is in CI rather than in a report.
    #
    # The formulas are imported from seo/tools/notes_titles.py rather than
    # restated. A check that restates the rule it is checking passes when both
    # copies are wrong together, and the whole point of putting these here is
    # to catch the case where the generator and the intention drift apart.
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import notes_titles as formulas  # noqa: E402

    NOTES_DIRS = ("edexcel-theme-1", "edexcel-theme-2", "edexcel-theme-3",
                  "edexcel-theme-4", "aqa-a2-micro", "aqa-a2-macro")
    topics = [p for p in pages
              if len(Path(p).parts) == 3
              and Path(p).parts[0] == "revision-notes"
              and Path(p).parts[1] in NOTES_DIRS
              and Path(p).name != "index.html"]

    def board_label(page: str) -> str:
        return "AQA" if Path(page).parts[1].startswith("aqa") else "Edexcel"

    # 15 --------------------------------------------------------------------
    # The title formula, §4. Two things are asserted and the second matters
    # more than the first: that every title is one of the three shapes for
    # its board, and that the topic name comes FIRST in it. 166 of 166 titles
    # used to end with the topic name, behind a board and a spec code, and
    # the code was earning 4 impressions in 28 days.
    #
    # No title on EITHER board may carry a spec code. AQA's are site-local
    # and misleading (settled 2026-08-21); Edexcel's are real but earn
    # nothing, and Eliot removed them on 2026-08-22 - DECISIONS.md D54. The
    # two Balance of Payments pages carry "(Theme 2)" / "(Theme 4)" labels
    # instead, which this regex deliberately does not match.
    SPEC_IN_TITLE = re.compile(r"\d+\.\d+(\.\d+)?")
    bad = []
    for p in topics:
        title = parsed[p].title
        board = board_label(p)
        shapes = (formulas.EDEXCEL_VARIANTS if board == "Edexcel"
                  else formulas.AQA_VARIANTS)
        tails = [v.split("{topic}", 1)[1].replace("({code})", "") .strip()
                 for v in shapes]
        if len(title) > formulas.HARD_MAX:
            bad.append(f"{p}: title is {len(title)} chars, over "
                       f"{formulas.HARD_MAX}")
        if not any(title.endswith(t) for t in tails):
            bad.append(f"{p}: title is not one of the §4 shapes: {title!r}")
        elif title.startswith(board) or title.startswith("A-Level"):
            bad.append(f"{p}: title does not lead with the topic: {title!r}")
        if SPEC_IN_TITLE.search(title):
            bad.append(f"{p}: title carries a spec code: {title!r}")
    lengths = sorted(len(parsed[p].title) for p in topics)
    check("15 notes titles match the §4 formula, topic name first", bad,
          f"{len(topics)} pages, {lengths[0]}-{lengths[-1]} chars")

    # 16 --------------------------------------------------------------------
    # The description band, §5. 145-158 is where Google shows the whole thing;
    # a hard floor and ceiling either side of it catches a description that
    # has drifted far enough to be truncated or to be wasting the space.
    #
    # The tolerance is not symmetric and is not a fudge. 20 descriptions run
    # 159-168 because their sub-concept list cannot be shortened by a script
    # without mangling it - seo/tools/notes_titles.py records the 25 that a
    # scripted attempt broke - so the ceiling here is 170, and the count of
    # pages outside the target band is asserted so it cannot silently grow.
    OUT_OF_BAND_ALLOWED = 21
    bad, out_of_band = [], []
    for p in topics:
        d = parsed[p].description
        if not (formulas.DESC_MIN <= len(d) <= formulas.DESC_MAX):
            out_of_band.append(p)
        if len(d) < 130 or len(d) > 170:
            bad.append(f"{p}: description is {len(d)} chars")
        topic_first = d.split(" for ")[0].split(" — ")[0]
        if len(topic_first) > 80:
            bad.append(f"{p}: description does not front-load a topic name")
    if len(out_of_band) > OUT_OF_BAND_ALLOWED:
        bad.append(f"{len(out_of_band)} descriptions outside "
                   f"{formulas.DESC_MIN}-{formulas.DESC_MAX}, "
                   f"was {OUT_OF_BAND_ALLOWED}")
    check("16 notes descriptions are front-loaded and in band", bad,
          f"{len(topics) - len(out_of_band)}/{len(topics)} in "
          f"{formulas.DESC_MIN}-{formulas.DESC_MAX}")

    # 17 --------------------------------------------------------------------
    # dateModified in the LearningResource and the same date visible on the
    # page. Freshness is a signal Google can only read if it is stated, and a
    # schema date that disagrees with the page is worse than no date at all -
    # so this asserts the two agree rather than merely that both exist.
    bad = []
    for p in topics:
        src = (REPO / p).read_text(encoding="utf-8", errors="replace")
        schema = re.search(r'"dateModified":\s*"(\d{4}-\d{2}-\d{2})"', src)
        visible = re.search(r'<time datetime="(\d{4}-\d{2}-\d{2})">', src)
        if not schema:
            bad.append(f"{p}: no dateModified in its LearningResource")
        elif not visible:
            bad.append(f"{p}: no visible <time> update date")
        elif schema.group(1) != visible.group(1):
            bad.append(f"{p}: schema says {schema.group(1)}, page shows "
                       f"{visible.group(1)}")
    check("17 every notes topic states when it was last updated", bad,
          f"{len(topics)} pages")

    # 18 --------------------------------------------------------------------
    # The twin link exists where the table says it should, exactly once, and
    # the reverse direction resolves too. Assertion 13 proves no UNDECLARED
    # cross-board link ships; this proves the declared ones actually did.
    # Without it, a generator change that dropped the block would leave 13
    # passing on an empty set and nobody any the wiser.
    bad = []
    for p in topics:
        key = (Path(p).parts[1], Path(p).stem)
        pair = notes_twins.TWINS.get(key)
        if not pair:
            continue
        want = f"/revision-notes/{pair[0]}/{pair[1]}.html"
        src = (REPO / p).read_text(encoding="utf-8", errors="replace")
        n = src.count(f'class="topic-related__twin-link" href="{want}"')
        if n != 1:
            bad.append(f"{p}: {n} twin links to {want}, expected 1")
    check("18 every notes topic with a declared twin links to it", bad,
          f"{len(notes_twins.TWINS)} pairs")

    # 19 --------------------------------------------------------------------
    # One <h1> per page is assertion 5; this is that no two notes pages ON THE
    # SAME BOARD share the same one. Two pages under one board answering to
    # the same heading is the shape of a duplicate.
    #
    # ACROSS boards it is not, and scoping this per board is the whole point.
    # Eleven topics are called the same thing on Edexcel and AQA - "Perfect
    # Competition", "Globalisation", "Supply-Side Policies" - and both are
    # meant to rank, for board-specific queries, which DECISIONS.md D4 settles
    # by refusing a cross-board canonical. A site-wide version of this check
    # would report all eleven as duplicates and would report more, not fewer,
    # if the AQA code prefixes are ever stripped from the AQA <h1>s.
    #
    # The one real collision is Edexcel's, and it is named so that a SECOND
    # one fails here rather than joining a tolerated set: "Balance of
    # Payments" is Theme 2's 2.1.4, as a measure of macroeconomic performance,
    # and Theme 4's 4.1.7, as international economics.
    KNOWN_H1_COLLISION = {("Edexcel", "Balance of Payments")}
    seen = defaultdict(list)
    for p in topics:
        h1 = parsed[p].h1[0] if parsed[p].h1 else ""
        seen[(board_label(p), h1)].append(p)
    bad = [f"{len(v)} {k[0]} pages share the <h1> {k[1]!r}: {', '.join(v)}"
           for k, v in seen.items()
           if len(v) > 1 and k not in KNOWN_H1_COLLISION]
    check("19 no two same-board notes pages share an <h1>", bad,
          f"{len(seen)} board/heading pairs over {len(topics)} pages, "
          f"{len(KNOWN_H1_COLLISION)} declared collision")

    # 20 --------------------------------------------------------------------
    # Added 2026-08-22, when Eliot supplied the byline and bio (manual to-do
    # task 4). Like 17 this asserts AGREEMENT, not presence: the byline under
    # the <h1>, the author box above the notes-cta and the LearningResource
    # `author` must all name the person scripts/notes_extras.py names, by the
    # @id about.html gives its Person node - and that @id must be a real
    # fragment on about.html, because the byline links to it. A schema author
    # the page does not show, or a byline the schema contradicts, is worse
    # than neither.
    import notes_extras  # noqa: E402  (scripts/ went on sys.path for 13)
    person_id = SITE + notes_extras.AUTHOR_URL
    # The byline and the box are pinned SEPARATELY, each as the exact anchor
    # the generator writes. Asking only that the name appear somewhere let a
    # byline naming someone else pass on the strength of the box below it -
    # found by breaking 1-2-2-demand on 2026-08-22, before this shipped.
    byline = (f'class="topic-byline__name" href="{notes_extras.AUTHOR_URL}"'
              f' rel="author">{notes_extras.AUTHOR_NAME}</a>')
    box = (f'class="topic-author__name" href="{notes_extras.AUTHOR_URL}"'
           f' rel="author">{notes_extras.AUTHOR_NAME}</a>')
    bad = []
    for p in topics:
        src = (REPO / p).read_text(encoding="utf-8", errors="replace")
        if src.count('class="topic-byline"') != 1:
            bad.append(f"{p}: no byline under the <h1>")
        if src.count('class="topic-author"') != 1:
            bad.append(f"{p}: no author box")
        if src.count(byline) != 1:
            bad.append(f"{p}: the byline does not link {notes_extras.AUTHOR_NAME} "
                       f"to {notes_extras.AUTHOR_URL}, exactly once")
        if src.count(box) != 1:
            bad.append(f"{p}: the author box does not link {notes_extras.AUTHOR_NAME} "
                       f"to {notes_extras.AUTHOR_URL}, exactly once")
        author = None
        for b in parsed[p].jsonld:
            data = json.loads(b)
            for node in (data if isinstance(data, list) else [data]):
                if node.get("@type") == "LearningResource":
                    author = node.get("author")
        if (not isinstance(author, dict)
                or author.get("@type") != "Person"
                or author.get("@id") != person_id
                or author.get("name") != notes_extras.AUTHOR_NAME):
            bad.append(f"{p}: LearningResource author is not the Person the "
                       f"byline names ({author!r})")
    about = (REPO / "about.html").read_text(encoding="utf-8", errors="replace")
    if f'id="{notes_extras.AUTHOR_URL.split("#", 1)[1]}"' not in about:
        bad.append(f"about.html: no id for {notes_extras.AUTHOR_URL} to land on")
    check("20 every notes topic names its author, and the schema agrees", bad,
          f"{len(topics)} pages, author {notes_extras.AUTHOR_NAME!r}")

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

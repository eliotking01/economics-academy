"""Phase 6 — structural drift inside the hand-written page families.

READ-ONLY. Every figure quoted in docs/audit/findings/PH06-html-architecture.md
comes from here or from page_anatomy.py. Run both to reproduce the phase.

    python3 docs/audit/scripts/page_anatomy.py
    python3 docs/audit/scripts/notes_drift.py
"""

import html
import itertools
import json
import os
import re
import sys
from collections import Counter, defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lib                                        # noqa: E402
from page_anatomy import family_of, parse, spine, GENERATED  # noqa: E402


def norm(s):
    return " ".join(html.unescape(re.sub("<[^>]+>", "", s)).split())


def notes_topic():
    return [p for p in lib.pages() if family_of(p) == "notes-topic"]


# --------------------------------------------------------------- 1. spines

def spine_shapes():
    """Distinct content shapes, with runs of identical siblings collapsed.

    Collapsing is the whole point: 'this page has 6 <section>s and that one
    has 4' is content length, not structural drift. What survives collapsing
    is real - a block present on one page and absent on another.
    """
    pages = notes_topic()
    shapes, ex, per_board = Counter(), {}, defaultdict(Counter)
    for p in pages:
        sp = spine(parse(p), "notes-container")
        key = "|".join(k for k, _ in itertools.groupby(sp))
        shapes[key] += 1
        ex.setdefault(key, p)
        per_board[p.split("/")[1]][key] += 1

    print(f"=== 1. Content spine: {len(shapes)} shapes across {len(pages)} pages ===")
    for i, (k, n) in enumerate(shapes.most_common(), 1):
        print(f"[{i}] {n:4}  {k}")
        print(f"        e.g. {ex[k]}")
    print("\n-- shapes per board directory --")
    for d in sorted(per_board):
        print(f"  {d:18} {len(per_board[d])} shapes over {sum(per_board[d].values()):3} pages")

    print("\n-- optional trailing blocks, by board --")
    per = defaultdict(Counter)
    for p in pages:
        d, src = p.split("/")[1], lib.read(p)
        per[d]["pages"] += 1
        for b in ("notes-past-papers-link", "notes-diagrams-link"):
            if b in src:
                per[d][b] += 1
    for d in sorted(per):
        r = per[d]
        print(f"  {d:18} pages={r['pages']:3}  past-papers={r['notes-past-papers-link']:3}"
              f"  diagrams={r['notes-diagrams-link']:3}")


# ----------------------------------------------- 2. teaser vs questions-data

def teaser_provenance():
    """Is the notes page's MCQ teaser paragraph a copy of JSON that already exists?"""
    c, sample = Counter(), []
    for p in notes_topic():
        bd, fn = p.split("/")[1], p.split("/")[2]
        m = re.match(r"(\d+-\d+-\d+)", fn)
        j = f"questions-data/{bd}/{m.group(1)}.json" if m else None
        if not j or not os.path.exists(j):
            c["no matching JSON"] += 1
            continue
        teaser = " ".join((json.load(open(j)).get("notesTeaser") or "").split())
        src = lib.read(p)
        i = src.find('<div class="notes-questions-link">')
        mm = re.search(r"<p>(.*?)</p>", src[i:i + 1500], re.S)
        onpage = norm(mm.group(1)) if mm else None
        if not teaser:
            c["JSON has no notesTeaser"] += 1
        elif onpage == teaser:
            c["identical to questions-data"] += 1
        else:
            c["DIFFERS"] += 1
            if len(sample) < 3:
                sample.append((p, teaser, onpage))
    print("\n=== 2. Notes-page MCQ teaser vs questions-data notesTeaser ===")
    for k, v in c.items():
        print(f"  {k:34} {v}")
    for p, t, o in sample:
        print(f"\n  {p}\n    json: {t[:110]}\n    page: {(o or '')[:110]}")


# ------------------------------------------------------- 3. metadata drift

def metadata_drift():
    def attr(src, pat):
        m = re.search(pat, src, re.S)
        return html.unescape(" ".join(m.group(1).split())) if m else None

    rows, byfam = [], Counter()
    for p in lib.pages():
        s = lib.read(p)
        d = attr(s, r'name="description"\s+content="(.*?)"')
        og = attr(s, r'property="og:description"\s+content="(.*?)"')
        tw = attr(s, r'name="twitter:description"\s+content="(.*?)"')
        t = attr(s, r"<title>(.*?)</title>")
        ogt = attr(s, r'property="og:title"\s+content="(.*?)"')
        twt = attr(s, r'name="twitter:title"\s+content="(.*?)"')
        bad = []
        if ogt and ogt != t:
            bad.append("og:title")
        if twt and twt != t:
            bad.append("twitter:title")
        if og and og != d:
            bad.append("og:description")
        if tw and tw != d:
            bad.append("twitter:description")
        if bad:
            byfam[family_of(p)] += 1
            rows.append((p, ",".join(bad)))
    print("\n=== 3. <head> fields that repeat the same value - do they agree? ===")
    print(f"  pages where a duplicate field disagrees: {len(rows)} of {len(lib.pages())}")
    print(f"  by family: {dict(byfam)}")
    gen = sum(1 for p, _ in rows if family_of(p) in GENERATED)
    print(f"  of those, generated: {gen}   hand-written: {len(rows) - gen}")
    for p, b in rows:
        print(f"    {p:46} {b}")


# ------------------------------------------------------ 4. breadcrumb drift

def breadcrumb_drift():
    aria, agree, ex = Counter(), Counter(), []
    for p in lib.pages():
        s = lib.read(p)
        m = re.search(r'<nav class="breadcrumb"([^>]*)>(.*?)</nav>', s, re.S)
        if not m:
            aria["no visible breadcrumb"] += 1
            continue
        aria["with aria-label" if "aria-label" in m.group(1) else "without aria-label"] += 1
        vis = [v for v in (norm(x) for x in
               re.split(r'<span class="separator">[^<]*</span>', m.group(2))) if v]
        j = re.search(r'"@type":\s*"BreadcrumbList".*?"itemListElement":\s*(\[.*?\])\s*\}', s, re.S)
        if not j:
            agree["no JSON-LD breadcrumb"] += 1
            continue
        try:
            names = [" ".join(i["name"].split()) for i in json.loads(j.group(1))]
        except Exception:
            agree["JSON-LD unparseable"] += 1
            continue
        if names == vis:
            agree["agree"] += 1
        else:
            agree["DISAGREE"] += 1
            ex.append((p, vis, names))
    print("\n=== 4. Breadcrumbs: written twice per page, in two languages ===")
    for k, v in aria.items():
        print(f"  {k:26} {v}")
    for k, v in agree.items():
        print(f"  {k:26} {v}")
    for p, v, n in ex:
        print(f"    {p}\n      visible: {v}\n      json-ld: {n}")


# ------------------------------------------------- 5. the stale notes template

def stale_template():
    src = open("scripts/convert_raw_notes.py", encoding="utf-8").read()
    i = src.find('return f"""<!doctype html>')
    tpl = src[i:src.find("def resolve_paths")]
    live = lib.read("revision-notes/edexcel-theme-1/1-1-1-economics-as-a-social-science.html")
    print("\n=== 5. scripts/convert_raw_notes.py already contains a full page template ===")
    print(f"  template found at scripts/convert_raw_notes.py:{src[:i].count(chr(10)) + 1}, "
          f"{len(tpl)} bytes")
    print(f"  {'feature':32} {'template':>9} {'live page':>10}")
    for label, needle in [
        ('lang="en-GB"', 'lang="en-GB"'),
        ("canonical", 'rel="canonical"'),
        ("og: tags", "og:"),
        ("twitter: tags", "twitter:"),
        ("JSON-LD blocks", "ld+json"),
        ("LearningResource", "LearningResource"),
        ("BreadcrumbList", "BreadcrumbList"),
        ("hoisted font/fontawesome css", "fontawesome-all.min.css"),
        ("preconnect", 'rel="preconnect"'),
        ("notes-cta", 'class="notes-cta"'),
        ("notes-questions-link", "notes-questions-link"),
    ]:
        print(f"  {label:32} {tpl.count(needle):>9} {live.count(needle):>10}")


# ------------------------------------------------------ 6. cost of a change

def change_cost():
    pages = lib.pages()
    hand = [p for p in pages if family_of(p) not in GENERATED]
    notes = notes_topic()

    def count(pred, pool=pages):
        return sum(1 for p in pool if pred(lib.read(p)))

    print("\n=== 6. What one global change costs today ===")
    jobs = [
        ("add or change one nav item",
         1, "templates/header.html - already solved by runtime injection"),
        ("add one <meta> to every page",
         len(pages), f"{len(pages) - len(hand)} via 4 generators, {len(hand)} by hand"),
        ("add aria-label to every breadcrumb",
         count(lambda s: '<nav class="breadcrumb">' in s),
         "the pages that lack it; the 100 newest already have it"),
        ('add loading="lazy" to every note image',
         count(lambda s: "<img" in s and 'loading=' not in s, notes),
         "notes-topic pages carrying at least one un-lazy image"),
        ("change the notes CTA wording",
         len(notes), "all hand-written"),
        ("add a board-switcher link to every note",
         len(notes), "all hand-written"),
        ("change the script tail",
         len(pages), "every page"),
    ]
    for label, n, note in jobs:
        print(f"  {label:44} {n:5} files   ({note})")

    print("\n  historical evidence - files touched by past sitewide changes:")
    for ref, what in [("4db232c", "hoist 2 @imports into every <head>"),
                      ("befb061", "rewrite remaining internal links to canonical form"),
                      ("17571f3", "past-paper + sibling links on practice pages"),
                      ("d1e7a3a", "link 47 notes pages to their diagram gallery")]:
        import subprocess
        out = subprocess.run(["git", "show", "--stat", "--format=", ref],
                             capture_output=True, text=True).stdout.strip().splitlines()
        n = out[-1].split()[0] if out else "?"
        print(f"    {ref}  {n:>4} files   {what}")


if __name__ == "__main__":
    spine_shapes()
    teaser_provenance()
    metadata_drift()
    breadcrumb_drift()
    stale_template()
    change_cost()

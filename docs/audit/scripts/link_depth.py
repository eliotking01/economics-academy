"""Phase 3 - internal linking, crawl depth and anchor text.

READ-ONLY. Reuses the graph from link_graph.py rather than rebuilding it.

Sections:
  1  BFS click depth from / on the raw graph, and again on the injected graph
  2  Anchor-text distribution: which strings are reused, and how often
  3  Hub/spoke integrity: does every hub link to all its children, and back
  4  Fragment targets: every #anchor resolves
  5  PH00-001 quantified: what the injection-dependent URLs would lose

Run:  python3 docs/audit/scripts/link_depth.py [section-number ...]
"""

import collections
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lib  # noqa: E402

# Repo root: walk up until the directory holding .git, rather than counting
# levels. Depth-independent on purpose - the fixed three-level version broke
# silently when _audit/scripts/ became docs/audit/scripts/ (D30), chdir-ing
# into docs/ where git ls-files finds no site HTML at all.
ROOT = os.path.dirname(os.path.abspath(__file__))
while ROOT != os.path.dirname(ROOT) and not os.path.isdir(os.path.join(ROOT, ".git")):
    ROOT = os.path.dirname(ROOT)
os.chdir(ROOT)

TEMPLATES = ["templates/header.html", "templates/footer.html"]
PAGES = lib.pages()

# url -> canonical page path, for both the /dir/ and /dir/index.html forms
URL_TO_PAGE = {}
for _p in PAGES:
    for _v in lib.url_variants(_p):
        URL_TO_PAGE[_v] = _p

TEMPLATE_TARGETS = set()
for _t in TEMPLATES:
    TEMPLATE_TARGETS |= lib.links_from(_t)


def out_edges(page, injected):
    """Pages this page links to. `injected` adds the runtime header/footer."""
    targets = set(lib.links_from(page))
    if injected:
        targets |= TEMPLATE_TARGETS
    return {URL_TO_PAGE[t] for t in targets if t in URL_TO_PAGE}


def bfs(injected):
    start = "index.html"
    depth = {start: 0}
    queue = collections.deque([start])
    while queue:
        cur = queue.popleft()
        for nxt in out_edges(cur, injected):
            if nxt not in depth:
                depth[nxt] = depth[cur] + 1
                queue.append(nxt)
    return depth


# ================================================================= section 1


def s1_depth():
    print("=== 1. Click depth from / ===\n")
    for injected in (False, True):
        label = "INJECTED (header/footer counted)" if injected else "RAW (no JavaScript)"
        depth = bfs(injected)
        hist = collections.Counter(depth.values())
        unreached = [p for p in PAGES if p not in depth]
        print(f"-- {label} --")
        print(f"   reached: {len(depth)} of {len(PAGES)}")
        for d in sorted(hist):
            print(f"   depth {d}: {hist[d]:>4} pages")
        print(f"   UNREACHED: {len(unreached)}  {unreached[:6]}")
        if not injected:
            deep = sorted(p for p, d in depth.items() if d >= 4)
            print(f"   pages at depth >= 4: {len(deep)}")
            for p in deep[:25]:
                print(f"      {depth[p]}  {p}")
            if len(deep) > 25:
                print(f"      ... and {len(deep)-25} more")
            fam = collections.Counter()
            for p, d in depth.items():
                fam[d] = fam[d]
            # depth by family
            import asset_census as ac
            byfam = collections.defaultdict(list)
            for p, d in depth.items():
                byfam[ac.FAMILY[p]].append(d)
            print("\n   depth by family (min / median / max):")
            for f in ac.FAM_ORDER:
                if f not in byfam:
                    continue
                v = sorted(byfam[f])
                print(f"      {f:<14} {v[0]} / {v[len(v)//2]} / {v[-1]}   ({len(v)} pages)")
        print()


# ================================================================= section 2

A_TAG = re.compile(r"<a\b([^>]*)>(.*?)</a>", re.I | re.S)
TAGS = re.compile(r"<[^>]+>")


def anchor_rows(include_templates=False):
    rows = []
    files = list(PAGES) + (TEMPLATES if include_templates else [])
    for p in files:
        for attrs, inner in A_TAG.findall(lib.read(p)):
            m = re.search(r'href="([^"]+)"', attrs)
            if not m:
                continue
            target = lib.resolve(m.group(1), p)
            if not target or target not in URL_TO_PAGE:
                continue
            text = re.sub(r"\s+", " ", TAGS.sub(" ", inner)).strip()
            rows.append((p, URL_TO_PAGE[target], text))
    return rows


def s2_anchors():
    print("=== 2. Anchor-text distribution ===\n")
    rows = anchor_rows()
    texts = collections.Counter(t for _, _, t in rows)
    print(f"internal <a> occurrences (page-body links only, templates excluded): {len(rows)}")
    print(f"distinct anchor strings: {len(texts)}\n")
    print("-- strings used more than 50 times (P3's stated threshold) --")
    over = [(t, n) for t, n in texts.most_common() if n > 50]
    if not over:
        print("   none")
    for t, n in over:
        print(f"   {n:>5}  {t[:88]!r}")
    print(f"\n   {len(over)} string(s) over the threshold")

    print("\n-- top 25 anchor strings --")
    for t, n in texts.most_common(25):
        print(f"   {n:>5}  {t[:82]!r}")

    print("\n-- anchor-text diversity per destination (worst 15 by monoculture) --")
    per_target = collections.defaultdict(collections.Counter)
    for _, tgt, txt in rows:
        per_target[tgt][txt] += 1
    worst = []
    for tgt, c in per_target.items():
        total = sum(c.values())
        if total < 10:
            continue
        top, topn = c.most_common(1)[0]
        worst.append((topn / total, total, len(c), top, tgt))
    worst.sort(key=lambda r: (-r[1] * r[0]))
    print(f"   {'inbound':>7} {'distinct':>8} {'top%':>6}  destination")
    for share, total, distinct, top, tgt in worst[:15]:
        print(f"   {total:>7} {distinct:>8} {share*100:>5.0f}%  {tgt}")
        print(f"            top string: {top[:74]!r}")

    print("\n-- empty or image-only anchor text on internal links --")
    empt = [(p, t) for p, t, txt in rows if not txt]
    print(f"   {len(empt)}")
    for p, t in empt[:10]:
        print(f"      {p} -> {t}")


# ================================================================= section 3


def s3_hubs():
    print("=== 3. Hub / spoke integrity ===\n")
    import asset_census as ac
    hubs = {
        "revision-notes": ("revision-notes/{}/index.html", "notes-topic"),
        "practice-questions": ("practice-questions/{}/index.html", "mcq-topic"),
    }
    del hubs
    # a hub is <dir>/index.html; its spokes are the other pages in that dir
    bydir = collections.defaultdict(list)
    for p in PAGES:
        d = os.path.dirname(p)
        if d:
            bydir[d].append(p)
    print(f"{'directory':<40} {'spokes':>6} {'hub->spoke':>11} {'spoke->hub':>11} {'gaps':>5}")
    total_missing_down = total_missing_up = 0
    detail = []
    for d in sorted(bydir):
        hub = f"{d}/index.html"
        if hub not in URL_TO_PAGE.values() and hub not in PAGES:
            continue
        spokes = [p for p in bydir[d] if p != hub]
        if not spokes:
            continue
        hub_out = out_edges(hub, False)
        down = sum(1 for s in spokes if s in hub_out)
        up = sum(1 for s in spokes if hub in out_edges(s, False))
        md, mu = len(spokes) - down, len(spokes) - up
        total_missing_down += md
        total_missing_up += mu
        print(f"{d:<40} {len(spokes):>6} {down:>11} {up:>11} {md+mu:>5}")
        if md:
            detail.append((d, "hub does not link to", [s for s in spokes if s not in hub_out]))
        if mu:
            detail.append((d, "does not link back to hub", [s for s in spokes if hub not in out_edges(s, False)]))
    print(f"\n   missing hub->spoke: {total_missing_down}   missing spoke->hub: {total_missing_up}")
    for d, what, items in detail:
        print(f"\n   {d}: {what} ({len(items)})")
        for i in items[:8]:
            print(f"      {i}")
        if len(items) > 8:
            print(f"      ... and {len(items)-8} more")

    # cross-family: does every notes topic page link to its MCQ twin and back
    print("\n-- notes-topic <-> mcq-topic pairing --")
    pairs = 0
    n2m = m2n = 0
    for p in PAGES:
        if ac.FAMILY[p] != "notes-topic":
            continue
        twin = p.replace("revision-notes/", "practice-questions/", 1)
        if twin not in PAGES:
            continue
        pairs += 1
        if twin in out_edges(p, False):
            n2m += 1
        if p in out_edges(twin, False):
            m2n += 1
    print(f"   pairs: {pairs}   notes->mcq: {n2m}   mcq->notes: {m2n}")


# ================================================================= section 4


def s4_fragments():
    print("=== 4. Fragment targets ===\n")
    bad = []
    total = 0
    for p in PAGES:
        text = lib.read(p)
        ids = set(re.findall(r'\sid="([^"]+)"', text)) | set(
            re.findall(r'\sname="([^"]+)"', text)
        )
        for href in lib.ANCHOR.findall(text):
            if "#" not in href:
                continue
            base, frag = href.split("#", 1)
            if not frag:
                continue
            total += 1
            if base in ("", "#"):
                target_page, target_ids = p, ids
            else:
                resolved = lib.resolve(base, p)
                target_page = URL_TO_PAGE.get(resolved)
                if not target_page:
                    continue
                t = lib.read(target_page)
                target_ids = set(re.findall(r'\sid="([^"]+)"', t)) | set(
                    re.findall(r'\sname="([^"]+)"', t)
                )
            if frag not in target_ids:
                bad.append((p, href, target_page))
    print(f"internal links carrying a #fragment: {total}")
    print(f"fragments that do not resolve      : {len(bad)}")
    for p, href, tp in bad[:20]:
        print(f"   {p}  ->  {href}   (target page {tp})")


# ================================================================= section 5


def s5_injection():
    print("=== 5. PH00-001 quantified: what the injection-dependent URLs lose ===\n")
    raw_depth = bfs(False)
    inj_depth = bfs(True)
    rows = []
    for t in sorted(TEMPLATE_TARGETS):
        page = URL_TO_PAGE.get(t)
        if not page:
            continue
        raw_in = sum(1 for p in PAGES if page in out_edges(p, False))
        rows.append((raw_in, raw_depth.get(page), inj_depth.get(page), page))
    rows.sort()
    print(f"{'raw in':>7} {'raw depth':>10} {'inj depth':>10}  page")
    for raw_in, rd, idp, page in rows:
        flag = "  <-- unreachable without JS" if rd is None else ""
        print(f"{raw_in:>7} {str(rd):>10} {str(idp):>10}  {page}{flag}")


SECTIONS = {
    "1": s1_depth,
    "2": s2_anchors,
    "3": s3_hubs,
    "4": s4_fragments,
    "5": s5_injection,
}

if __name__ == "__main__":
    for key in sys.argv[1:] or sorted(SECTIONS):
        SECTIONS[key]()
        print("\n" + "=" * 78 + "\n")

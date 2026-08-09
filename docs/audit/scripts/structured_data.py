"""Phase 4 - structured data validity.

READ-ONLY. Parses every JSON-LD block on every published page.

Sections:
  1  Parse: does every <script type="application/ld+json"> block parse
  2  Required properties per @type, against schema.org / Google's requirements
  3  Family coverage: which families emit which types, and the ragged edges
  4  BreadcrumbList: JSON-LD vs the visible trail, item URLs, position sequence
  5  @type choices: every type in use, with a page count and a sample
  6  Cross-checks: URLs resolve, dates parse, no placeholder values

Run:  python3 docs/audit/scripts/structured_data.py [section-number ...]
"""

import collections
import html
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lib  # noqa: E402
import asset_census as ac  # noqa: E402

# Repo root: walk up until the directory holding .git, rather than counting
# levels. Depth-independent on purpose - the fixed three-level version broke
# silently when _audit/scripts/ became docs/audit/scripts/ (D30), chdir-ing
# into docs/ where git ls-files finds no site HTML at all.
ROOT = os.path.dirname(os.path.abspath(__file__))
while ROOT != os.path.dirname(ROOT) and not os.path.isdir(os.path.join(ROOT, ".git")):
    ROOT = os.path.dirname(ROOT)
os.chdir(ROOT)

PAGES = lib.pages()
LD = re.compile(
    r'<script[^>]*type="application/ld\+json"[^>]*>(.*?)</script>', re.I | re.S
)

RESOLVABLE = set()
for _p in PAGES:
    RESOLVABLE |= lib.url_variants(_p)
for _p in lib.tracked("*.pdf"):
    if lib.is_published(_p):
        RESOLVABLE.add("/" + _p)


def blocks(page):
    """(index, raw, parsed-or-None, error-or-None) per JSON-LD block."""
    out = []
    for i, raw in enumerate(LD.findall(lib.read(page))):
        try:
            out.append((i, raw, json.loads(raw), None))
        except json.JSONDecodeError as e:
            out.append((i, raw, None, str(e)))
    return out


def nodes(obj, _seen=None):
    """Every dict carrying an @type, recursively, including @graph members."""
    if isinstance(obj, list):
        for x in obj:
            yield from nodes(x)
    elif isinstance(obj, dict):
        if "@type" in obj:
            yield obj
        for v in obj.values():
            if isinstance(v, (dict, list)):
                yield from nodes(v)


def types_of(node):
    t = node.get("@type")
    return t if isinstance(t, list) else [t]


# ================================================================= section 1


def s1_parse():
    print("=== 1. Does every JSON-LD block parse? ===\n")
    total = bad = 0
    pages_with = 0
    per_page = collections.Counter()
    for p in PAGES:
        bs = blocks(p)
        if bs:
            pages_with += 1
        per_page[len(bs)] += 1
        for i, raw, parsed, err in bs:
            total += 1
            if err:
                bad += 1
                print(f"  PARSE ERROR  {p}  block {i}: {err}")
    print(f"pages with >=1 JSON-LD block : {pages_with} of {len(PAGES)}")
    print(f"blocks total                 : {total}")
    print(f"blocks that fail to parse    : {bad}")
    print(f"\nblocks per page: {dict(sorted(per_page.items()))}")
    noldjson = [p for p in PAGES if not blocks(p)]
    print(f"\npages with NO JSON-LD: {len(noldjson)}  {noldjson}")

    # @context present and correct
    ctx = collections.Counter()
    missing_ctx = []
    for p in PAGES:
        for i, raw, parsed, err in blocks(p):
            if err:
                continue
            c = parsed.get("@context") if isinstance(parsed, dict) else None
            if c is None:
                missing_ctx.append((p, i))
            ctx[str(c)] += 1
    print(f"\n@context values: {dict(ctx)}")
    print(f"top-level blocks with no @context: {len(missing_ctx)}  {missing_ctx[:5]}")


# ================================================================= section 2

# Required / strongly-recommended properties. Sources: schema.org type
# definitions and Google's structured-data documentation for the types that
# have rich-result requirements. Types with no Google requirement are checked
# against schema.org's own required set only, which for most types is empty -
# those are marked "advisory".
REQUIRED = {
    "BreadcrumbList": (["itemListElement"], []),
    "ListItem": (["position", "name"], ["item"]),
    "Course": (["name", "description"], ["provider", "hasCourseInstance"]),
    "LearningResource": (["name"], ["description", "educationalLevel", "learningResourceType"]),
    "Quiz": (["name"], ["hasPart", "about"]),
    "Question": (["name"], ["acceptedAnswer", "eduQuestionType"]),
    "Answer": (["text"], []),
    "FAQPage": (["mainEntity"], []),
    "EducationalOrganization": (["name"], ["url", "logo"]),
    "WebSite": (["name", "url"], ["potentialAction"]),
    "CollectionPage": (["name"], ["description", "url"]),
    "DefinedTermSet": (["name"], ["hasDefinedTerm"]),
    "DefinedTerm": (["name", "description"], ["inDefinedTermSet"]),
    "Person": (["name"], ["url"]),
    "Service": (["name"], ["provider", "areaServed"]),
    "Offer": (["price", "priceCurrency"], ["availability"]),
    "WebPage": (["name"], ["description"]),
}


def s2_required():
    print("=== 2. Required and recommended properties ===\n")
    missing_req = collections.Counter()
    missing_rec = collections.Counter()
    examples = {}
    counts = collections.Counter()
    for p in PAGES:
        for i, raw, parsed, err in blocks(p):
            if err:
                continue
            for node in nodes(parsed):
                for t in types_of(node):
                    if t not in REQUIRED:
                        continue
                    counts[t] += 1
                    req, rec = REQUIRED[t]
                    for k in req:
                        if k not in node:
                            missing_req[(t, k)] += 1
                            examples.setdefault((t, k), p)
                    for k in rec:
                        if k not in node:
                            missing_rec[(t, k)] += 1
                            examples.setdefault((t, k), p)
    print("-- REQUIRED property missing --")
    if not missing_req:
        print("   none")
    for (t, k), n in missing_req.most_common():
        print(f"   {n:>5} of {counts[t]:>5}  {t}.{k}   e.g. {examples[(t,k)]}")
    print("\n-- recommended property absent (advisory, not an error) --")
    for (t, k), n in missing_rec.most_common():
        print(f"   {n:>5} of {counts[t]:>5}  {t}.{k}   e.g. {examples[(t,k)]}")


# ================================================================= section 3


def s3_coverage():
    print("=== 3. Type coverage per family, and the ragged edges ===\n")
    fam_pages = collections.Counter()
    fam_type = collections.defaultdict(collections.Counter)
    page_types = {}
    for p in PAGES:
        f = ac.FAMILY[p]
        fam_pages[f] += 1
        seen = set()
        for i, raw, parsed, err in blocks(p):
            if err:
                continue
            for node in nodes(parsed):
                seen.update(t for t in types_of(node) if t)
        page_types[p] = seen
        for t in seen:
            fam_type[f][t] += 1

    all_types = sorted({t for c in fam_type.values() for t in c})
    print("legend:  ALL = every page in the family;  n/m = ragged\n")
    for f in ac.FAM_ORDER:
        if f not in fam_pages:
            continue
        n = fam_pages[f]
        parts = []
        for t in all_types:
            c = fam_type[f].get(t, 0)
            if not c:
                continue
            parts.append(f"{t}={'ALL' if c == n else f'{c}/{n}'}")
        print(f"{f:<14} ({n:>3} pages)  {'  '.join(parts)}")

    print("\n-- ragged edges: the odd page out, per family and type --")
    for f in ac.FAM_ORDER:
        if f not in fam_pages:
            continue
        n = fam_pages[f]
        for t, c in sorted(fam_type[f].items()):
            if c == n or c == 0:
                continue
            gap = n - c
            if gap > 4:
                continue  # a whole-family absence, not a ragged edge
            odd = [p for p in PAGES if ac.FAMILY[p] == f and t not in page_types[p]]
            print(f"   {f}: {t} on {c}/{n} — missing from {odd}")


# ================================================================= section 4


def s4_breadcrumbs():
    print("=== 4. BreadcrumbList integrity ===\n")
    bad_pos, bad_url, mismatch, no_visible = [], [], [], []
    total = 0
    for p in PAGES:
        text = lib.read(p)
        crumbs = None
        for i, raw, parsed, err in blocks(p):
            if err:
                continue
            for node in nodes(parsed):
                if "BreadcrumbList" in types_of(node):
                    crumbs = node
        if not crumbs:
            continue
        total += 1
        items = crumbs.get("itemListElement", [])
        positions = [it.get("position") for it in items if isinstance(it, dict)]
        if positions != list(range(1, len(items) + 1)):
            bad_pos.append((p, positions))
        for it in items:
            if not isinstance(it, dict):
                continue
            url = it.get("item")
            if isinstance(url, dict):
                url = url.get("@id")
            if not url:
                continue
            path = re.sub(r"^https?://[^/]+", "", url)
            if path not in RESOLVABLE and path != "/":
                bad_url.append((p, url))
        # visible trail
        m = re.search(r'<nav[^>]*class="[^"]*breadcrumb[^"]*"[^>]*>(.*?)</nav>', text, re.I | re.S)
        if not m:
            m = re.search(r'<(?:div|p|ol|ul)[^>]*class="[^"]*breadcrumb[^"]*"[^>]*>(.*?)</(?:div|p|ol|ul)>', text, re.I | re.S)
        if not m:
            no_visible.append(p)
            continue
        # The visible trail is HTML; the JSON-LD is a JSON string. Decode
        # entities before comparing, or every "&amp;" reads as a disagreement.
        vis = [html.unescape(x).strip() for x in re.split(r"<[^>]+>", m.group(1)) if x.strip()]
        vis = [re.sub(r"\s+", " ", v) for v in vis if v not in ("›", "»", "/", "|", "›")]
        names = [it.get("name") for it in items if isinstance(it, dict)]
        if [v for v in vis if v] != [n for n in names if n]:
            mismatch.append((p, names, vis))

    print(f"pages carrying a BreadcrumbList : {total}")
    print(f"position sequence not 1..n      : {len(bad_pos)}  {bad_pos[:5]}")
    print(f"item URLs that do not resolve   : {len(bad_url)}")
    for p, u in bad_url[:10]:
        print(f"     {p} -> {u}")
    print(f"\nBreadcrumbList with NO visible trail : {len(no_visible)}")
    print("   ", ac.fam_counts(no_visible))
    for p in sorted(no_visible):
        print(f"     {p}")
    print(f"\nvisible trail disagrees with JSON-LD : {len(mismatch)}")
    for p, names, vis in mismatch[:12]:
        print(f"     {p}")
        print(f"        json-ld: {names}")
        print(f"        visible: {vis}")


# ================================================================= section 5


def s5_types():
    print("=== 5. Every @type in use ===\n")
    counts = collections.Counter()
    pagecount = collections.defaultdict(set)
    sample = {}
    for p in PAGES:
        for i, raw, parsed, err in blocks(p):
            if err:
                continue
            for node in nodes(parsed):
                for t in types_of(node):
                    if not t:
                        continue
                    counts[t] += 1
                    pagecount[t].add(p)
                    sample.setdefault(t, (p, sorted(k for k in node if not k.startswith("@"))))
    print(f"{'nodes':>7} {'pages':>6}  @type")
    for t, n in counts.most_common():
        print(f"{n:>7} {len(pagecount[t]):>6}  {t}")
    print("\n-- properties used, per type (from the first instance seen) --")
    for t, _ in counts.most_common():
        p, keys = sample[t]
        print(f"  {t:<32} {', '.join(keys)[:120]}")


# ================================================================= section 6


def s6_crosschecks():
    print("=== 6. Cross-checks ===\n")
    bad_url, placeholders, bad_date = [], [], []
    URLKEYS = {"url", "@id", "sameAs", "logo", "image", "target", "item", "mainEntityOfPage"}
    for p in PAGES:
        for i, raw, parsed, err in blocks(p):
            if err:
                continue
            for node in nodes(parsed):
                for k, v in node.items():
                    vals = v if isinstance(v, list) else [v]
                    for val in vals:
                        if isinstance(val, dict):
                            val = val.get("@id") or val.get("url")
                        if not isinstance(val, str):
                            continue
                        if k in URLKEYS and val.startswith("https://economicsacademy.co.uk"):
                            path = val[len("https://economicsacademy.co.uk"):] or "/"
                            path = path.split("#")[0].split("?")[0]
                            if path not in RESOLVABLE and path != "/" and not path.endswith((".png", ".jpg", ".ico", ".svg")):
                                bad_url.append((p, k, val))
                        if re.search(r"\b(lorem|TODO|FIXME|xxx|placeholder|example\.com)\b", val, re.I):
                            placeholders.append((p, k, val[:60]))
                        if k in ("datePublished", "dateModified", "startDate", "endDate"):
                            if not re.match(r"^\d{4}-\d{2}-\d{2}", val):
                                bad_date.append((p, k, val))
    print(f"on-site URLs in JSON-LD that do not resolve : {len(bad_url)}")
    for p, k, v in bad_url[:15]:
        print(f"     {p}  {k}={v}")
    print(f"\nplaceholder-looking values : {len(placeholders)}  {placeholders[:5]}")
    print(f"non-ISO dates              : {len(bad_date)}  {bad_date[:5]}")

    # canonical vs JSON-LD url/@id agreement
    print("\n-- page-level url/@id vs the page's own canonical --")
    dis = []
    for p in PAGES:
        m = re.search(r'<link[^>]*rel="canonical"[^>]*href="([^"]+)"', lib.read(p))
        if not m:
            continue
        canon = m.group(1)
        for i, raw, parsed, err in blocks(p):
            if err or not isinstance(parsed, dict):
                continue
            for t in types_of(parsed):
                if t in ("LearningResource", "Course", "CollectionPage", "WebPage", "Quiz", "FAQPage"):
                    u = parsed.get("url") or parsed.get("@id")
                    if isinstance(u, str) and u.rstrip("/") != canon.rstrip("/"):
                        dis.append((p, t, u, canon))
    print(f"   disagreements: {len(dis)}")
    for p, t, u, c in dis[:10]:
        print(f"     {p}  {t}.url={u}  canonical={c}")


SECTIONS = {
    "1": s1_parse,
    "2": s2_required,
    "3": s3_coverage,
    "4": s4_breadcrumbs,
    "5": s5_types,
    "6": s6_crosschecks,
}

if __name__ == "__main__":
    for key in sys.argv[1:] or sorted(SECTIONS):
        SECTIONS[key]()
        print("\n" + "=" * 78 + "\n")

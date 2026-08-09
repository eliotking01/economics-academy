"""Phase 8 - front-end assets, semantics and accessibility.

READ-ONLY. Opens site files for reading only, never for writing.

Sections:
  1  Stylesheet inventory: which page loads which sheet; unreferenced sheets
  2  Scoping convention: is every rule nested under the page's wrapper class
  3  Selector reach: class selectors that match nothing in any HTML or JS
  4  Script inventory: load order, defer/async, unreferenced JS
  5  Render-blocking chain: what is in the <head> and in what order
  6  Images: format, bytes, dimensions, loading, unreferenced files
  7  Fonts: what is fetched, from where, and what is self-hosted
  8  ARIA and semantics beyond what Phase 6 already measured
  9  GA4 and third-party consistency

Run:  python3 docs/audit/scripts/asset_census.py [section-number ...]
"""

import os
import re
import sys
from collections import Counter, defaultdict

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

PAGES = lib.pages()
PUBLISHED_HTML = lib.published_html()

# ---------------------------------------------------------------- family map
# Same buckets Phase 6 used, so the two phases' tables line up.


def family(path):
    if path.startswith("templates/"):
        return "templates"
    if path.startswith("revision-notes/glossary/"):
        return "glossary"
    if path.startswith("revision-notes/"):
        rest = path[len("revision-notes/") :]
        if rest == "index.html":
            return "notes-other"
        if rest.endswith("/index.html"):
            return "notes-hub"
        if "/" not in rest:
            return "notes-other"
        if rest.startswith("macro-application/"):
            return "notes-other"
        return "notes-topic"
    if path.startswith("practice-questions/"):
        return "mcq-hub" if path.endswith("/index.html") else "mcq-topic"
    if path.startswith("past-paper-questions/"):
        return "ppq"
    if path.startswith("past-papers/"):
        return "past-papers"
    if path.startswith("flashcards/"):
        return "flashcards"
    return "root"


FAMILY = {p: family(p) for p in PUBLISHED_HTML}
FAM_ORDER = [
    "root",
    "notes-topic",
    "notes-hub",
    "notes-other",
    "glossary",
    "mcq-topic",
    "mcq-hub",
    "ppq",
    "past-papers",
    "flashcards",
    "templates",
]


def fam_counts(paths):
    c = Counter(FAMILY[p] for p in paths)
    return ", ".join(f"{f} {c[f]}" for f in FAM_ORDER if c[f])


# ---------------------------------------------------------------- CSS parsing

COMMENT = re.compile(r"/\*.*?\*/", re.S)


def strip_comments(text):
    return COMMENT.sub("", text)


def top_level_rules(css):
    """Yield (selector, body) for every rule at brace depth 0.

    @media / @supports blocks are recursed into, so a rule inside one is
    reported with its own selector rather than the at-rule's condition. That
    matters here: the scoping convention has to hold inside media queries too.
    """
    css = strip_comments(css)
    i, n = 0, len(css)
    buf = []
    while i < n:
        ch = css[i]
        if ch == "{":
            selector = "".join(buf).strip()
            depth, j = 1, i + 1
            while j < n and depth:
                if css[j] == "{":
                    depth += 1
                elif css[j] == "}":
                    depth -= 1
                j += 1
            body = css[i + 1 : j - 1]
            if selector.startswith("@") and re.match(
                r"@(media|supports|layer|container)\b", selector
            ):
                yield from top_level_rules(body)
            else:
                yield selector, body
            buf = []
            i = j
            continue
        buf.append(ch)
        i += 1


CLASS_IN_SELECTOR = re.compile(r"\.(-?[_a-zA-Z][\w-]*)")


def selector_list(selector):
    """Split a comma-separated selector group, ignoring commas inside :not() etc."""
    out, depth, buf = [], 0, []
    for ch in selector:
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
        if ch == "," and depth == 0:
            out.append("".join(buf).strip())
            buf = []
        else:
            buf.append(ch)
    if "".join(buf).strip():
        out.append("".join(buf).strip())
    return out


# ---------------------------------------------------------------- HTML assets

LINK_CSS = re.compile(r'<link\b[^>]*rel="stylesheet"[^>]*>', re.I)
SCRIPT_TAG = re.compile(r"<script\b([^>]*)>", re.I)
ATTR = re.compile(r'([a-zA-Z:-]+)\s*=\s*"([^"]*)"')
HEAD_BLOCK = re.compile(r"<head\b[^>]*>(.*?)</head>", re.I | re.S)
IMG_TAG = re.compile(r"<img\b([^>]*)>", re.I)


def attrs(fragment):
    return {k.lower(): v for k, v in ATTR.findall(fragment)}


def head_of(text):
    m = HEAD_BLOCK.search(text)
    return m.group(1) if m else ""


def stylesheets_of(text):
    out = []
    for tag in LINK_CSS.findall(text):
        a = attrs(tag)
        if a.get("href"):
            out.append(a["href"])
    return out


def scripts_of(text):
    out = []
    for m in SCRIPT_TAG.finditer(text):
        a = attrs(m.group(1))
        out.append(
            {
                "src": a.get("src"),
                "defer": "defer" in m.group(1).lower(),
                "async": "async" in m.group(1).lower(),
                "type": a.get("type"),
                "id": a.get("id"),
                "pos": m.start(),
            }
        )
    return out


def local_asset(url):
    """Root-absolute local path for an asset URL, or None if remote."""
    if url.startswith(("http://", "https://", "//", "data:")):
        return None
    return url.split("?")[0].split("#")[0].lstrip("/")


# ================================================================= section 1


def s1_stylesheets():
    print("=== 1. Stylesheet inventory ===\n")
    tracked_css = [f for f in lib.tracked("*.css") if lib.is_published(f)]
    refs = defaultdict(list)  # css path -> pages
    remote = Counter()
    missing = defaultdict(list)
    per_page = {}
    for p in PUBLISHED_HTML:
        sheets = stylesheets_of(lib.read(p))
        per_page[p] = sheets
        for href in sheets:
            asset = local_asset(href)
            if asset is None:
                remote[href.split("?")[0]] += 1
                continue
            if not os.path.exists(asset):
                missing[href].append(p)
            refs[asset].append(p)

    print(f"tracked published .css files: {len(tracked_css)}")
    print(f"pages scanned: {len(PUBLISHED_HTML)} (templates/ included)\n")
    print(f"{'pages':>5}  {'css file':<44} families")
    for f in sorted(tracked_css):
        n = len(refs.get(f, []))
        flag = "" if n else "   <-- UNREFERENCED"
        print(f"{n:>5}  {f:<44} {fam_counts(refs.get(f, []))}{flag}")

    print("\n-- remote stylesheets --")
    for url, n in remote.most_common():
        print(f"{n:>5}  {url}")

    print("\n-- stylesheet hrefs that do not resolve to a file --")
    print(f"  {len(missing)} distinct" if missing else "  none")
    for href, pgs in missing.items():
        print(f"  {href}  on {len(pgs)} page(s), e.g. {pgs[0]}")

    print("\n-- sheets loaded per page, by family --")
    combos = defaultdict(Counter)
    for p, sheets in per_page.items():
        local = tuple(local_asset(s) or "REMOTE:" + s.split("?")[0] for s in sheets)
        combos[FAMILY[p]][local] += 1
    for f in FAM_ORDER:
        if f not in combos:
            continue
        print(f"\n  {f}  ({len(combos[f])} distinct combination(s))")
        for combo, n in combos[f].most_common():
            names = [c.replace("css/pages/", "pages/") for c in combo]
            print(f"    {n:>4}x  {' | '.join(names)}")

    # css/pages sheet used by more than one family
    print("\n-- css/pages sheets loaded by more than one family --")
    hits = 0
    for f in sorted(tracked_css):
        if not f.startswith("css/pages/"):
            continue
        fams = sorted({FAMILY[p] for p in refs.get(f, [])})
        if len(fams) > 1:
            hits += 1
            print(f"  {f:<44} {', '.join(fams)}")
    if not hits:
        print("  none")


# ================================================================= section 2


def s2_scoping():
    print("=== 2. Scoping convention in css/pages/*.css ===\n")
    print("House rule (CLAUDE.md): put a wrapper class on the page's")
    print("<section id=\"main\"> and nest every rule under it.\n")

    sheets = sorted(f for f in lib.tracked("css/pages/*.css"))
    # wrapper classes actually present on section#main / main#main
    wrapper_re = re.compile(r'<(?:section|main)\b[^>]*id="main"[^>]*>', re.I)
    page_wrappers = {}
    for p in PUBLISHED_HTML:
        m = wrapper_re.search(lib.read(p))
        page_wrappers[p] = attrs(m.group(0)).get("class", "").split() if m else []

    # map sheet -> wrapper classes seen on pages that load it
    sheet_pages = defaultdict(list)
    for p in PUBLISHED_HTML:
        for href in stylesheets_of(lib.read(p)):
            a = local_asset(href)
            if a and a.startswith("css/pages/"):
                sheet_pages[a].append(p)

    rows = []
    unscoped_detail = {}
    for sheet in sheets:
        css = lib.read(sheet)
        wrappers = Counter()
        for p in sheet_pages.get(sheet, []):
            for w in page_wrappers[p]:
                wrappers[w] += 1
        total = scoped = 0
        unscoped = []
        candidates = [w for w, _ in wrappers.most_common()]
        for selector, _body in top_level_rules(css):
            if selector.startswith("@") or not selector:
                continue
            for one in selector_list(selector):
                total += 1
                if any("." + w in one for w in candidates):
                    scoped += 1
                elif one.split()[0].lstrip() in (":root", "html", "body", "*"):
                    scoped += 1  # legitimately global
                else:
                    unscoped.append(one)
        rows.append(
            (
                sheet,
                len(sheet_pages.get(sheet, [])),
                candidates[0] if candidates else "(none)",
                total,
                len(unscoped),
            )
        )
        unscoped_detail[sheet] = unscoped

    print(f"{'sheet':<44} {'pages':>5} {'wrapper':<28} {'sels':>5} {'unscoped':>8}")
    for sheet, npages, wrapper, total, nun in rows:
        print(f"{sheet:<44} {npages:>5} {wrapper:<28} {total:>5} {nun:>8}")

    print("\n-- unscoped selectors, first 12 per sheet --")
    for sheet, _n, _w, _t, nun in rows:
        if not nun:
            continue
        print(f"\n  {sheet}  ({nun})")
        for sel in unscoped_detail[sheet][:12]:
            print(f"      {sel[:110]}")

    # cross-file bare class collisions
    print("\n-- class names defined in more than one css/pages sheet --")
    defined = defaultdict(set)
    for sheet in sheets:
        for selector, _body in top_level_rules(lib.read(sheet)):
            if selector.startswith("@"):
                continue
            for cls in CLASS_IN_SELECTOR.findall(selector):
                defined[cls].add(sheet)
    shared = {c: s for c, s in defined.items() if len(s) > 1}
    print(f"  {len(shared)} class name(s) appear in 2+ sheets")
    for cls, s in sorted(shared.items(), key=lambda kv: (-len(kv[1]), kv[0]))[:40]:
        print(f"    .{cls:<34} {', '.join(sorted(x.replace('css/pages/', '') for x in s))}")


# ================================================================= section 3


def s3_selector_reach():
    print("=== 3. Selector reach: class selectors that match nothing ===\n")
    print("A class counts as used if it appears in any published .html, any")
    print("tracked .js, or any generator in scripts/ (which writes the html).\n")

    used = set()
    CLASS_ATTR = re.compile(r'class="([^"]*)"')
    for p in PUBLISHED_HTML:
        for chunk in CLASS_ATTR.findall(lib.read(p)):
            used.update(chunk.split())
    # JS may add classes at runtime
    js_text = "\n".join(lib.read(f) for f in lib.tracked("*.js"))
    py_text = "\n".join(lib.read(f) for f in lib.tracked("scripts/*.py"))
    dynamic = js_text + "\n" + py_text

    for sheet in sorted(lib.tracked("css/pages/*.css")) + ["css/main.css"]:
        css = lib.read(sheet)
        classes = set()
        for selector, _body in top_level_rules(css):
            if selector.startswith("@"):
                continue
            classes.update(CLASS_IN_SELECTOR.findall(selector))
        dead = []
        for c in sorted(classes):
            if c in used:
                continue
            if re.search(r"[\"'`\s.](" + re.escape(c) + r")[\"'`\s.]", dynamic):
                continue
            dead.append(c)
        pct = 100.0 * len(dead) / len(classes) if classes else 0
        print(f"{sheet:<44} {len(classes):>4} classes, {len(dead):>4} unmatched ({pct:4.1f}%)")
        if dead:
            print("      " + ", ".join("." + d for d in dead[:25]))
            if len(dead) > 25:
                print(f"      ... and {len(dead) - 25} more")


# ================================================================= section 4


def s4_scripts():
    print("=== 4. Script inventory and load order ===\n")
    refs = defaultdict(list)
    remote = Counter()
    missing = defaultdict(list)
    orders = defaultdict(Counter)
    defer_async = Counter()
    inline_blocks = Counter()
    in_head = Counter()

    for p in PUBLISHED_HTML:
        text = lib.read(p)
        head = head_of(text)
        head_end = text.lower().find("</head>")
        seq = []
        for s in scripts_of(text):
            if not s["src"]:
                inline_blocks[p] += 1
                continue
            a = local_asset(s["src"])
            if a is None:
                remote[s["src"].split("?")[0]] += 1
            else:
                if not os.path.exists(a):
                    missing[s["src"]].append(p)
                refs[a].append(p)
            seq.append(a or "REMOTE:" + s["src"].split("?")[0])
            if s["defer"]:
                defer_async["defer"] += 1
            if s["async"]:
                defer_async["async"] += 1
            if head_end >= 0 and s["pos"] < head_end:
                in_head[a or "REMOTE"] += 1
        orders[FAMILY[p]][tuple(seq)] += 1
        del head

    tracked_js = [f for f in lib.tracked("*.js") if lib.is_published(f)]
    print(f"{'pages':>5}  {'js file':<40} families")
    for f in sorted(tracked_js):
        n = len(refs.get(f, []))
        flag = "" if n else "   <-- UNREFERENCED by any page"
        print(f"{n:>5}  {f:<40} {fam_counts(refs.get(f, []))}{flag}")

    print("\n-- remote scripts --")
    for url, n in remote.most_common():
        print(f"{n:>5}  {url}")

    print("\n-- script srcs that do not resolve to a file --")
    print(f"  {len(missing)} distinct" if missing else "  none")
    for href, pgs in missing.items():
        print(f"  {href}  on {len(pgs)} page(s), e.g. {pgs[0]}")

    print(f"\n-- defer / async usage across all pages: {dict(defer_async) or 'none'}")
    print(f"-- scripts placed inside <head>: {sum(in_head.values())}")
    for k, v in in_head.most_common():
        print(f"     {v:>5}  {k}")

    print("\n-- distinct script sequences per family --")
    for f in FAM_ORDER:
        if f not in orders:
            continue
        print(f"\n  {f}  ({len(orders[f])} distinct)")
        for seq, n in orders[f].most_common(4):
            short = [s.replace("js/components/", "c/").replace("js/", "") for s in seq]
            print(f"    {n:>4}x  {' > '.join(short)}")

    print("\n-- inline <script> blocks per page (count of pages by n) --")
    print("  ", dict(Counter(inline_blocks.values())), " (pages with 0 not shown)")


# ================================================================= section 5


def s5_head_order():
    print("=== 5. <head> resource order (render-blocking chain) ===\n")
    RESOURCE = re.compile(
        r'<(link|script|style)\b([^>]*)>', re.I
    )
    shapes = Counter()
    examples = {}
    for p in PUBLISHED_HTML:
        head = head_of(lib.read(p))
        seq = []
        for kind, rest in RESOURCE.findall(head):
            a = attrs(rest)
            kind = kind.lower()
            if kind == "link":
                rel = a.get("rel", "")
                if rel in ("stylesheet", "preconnect", "preload", "dns-prefetch"):
                    href = a.get("href", "")
                    host = ""
                    if href.startswith("http"):
                        host = re.sub(r"^https?://([^/]+).*", r"\1", href)
                    seq.append(f"{rel}:{host or local_asset(href)}")
            elif kind == "script":
                src = a.get("src")
                seq.append("script:" + (re.sub(r"^https?://([^/]+).*", r"\1", src) if src and src.startswith("http") else (local_asset(src) if src else "INLINE")))
            elif kind == "style":
                seq.append("STYLE-BLOCK")
        shapes[tuple(seq)] += 1
        examples.setdefault(tuple(seq), p)

    print(f"{len(shapes)} distinct <head> resource orders across {len(PUBLISHED_HTML)} pages\n")
    for seq, n in shapes.most_common():
        print(f"  {n:>4} pages   e.g. {examples[seq]}")
        for step in seq:
            print(f"          {step}")
        print()


# ================================================================= section 6


def s6_images():
    print("=== 6. Images ===\n")
    tracked_img = [
        f
        for f in lib.tracked("*")
        if lib.is_published(f)
        and f.lower().endswith((".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp", ".avif", ".ico"))
    ]
    by_ext = Counter(os.path.splitext(f)[1].lower() for f in tracked_img)
    total_bytes = sum(os.path.getsize(f) for f in tracked_img if os.path.exists(f))
    print(f"tracked published image files: {len(tracked_img)}, {total_bytes/1024/1024:.1f} MB")
    print("  by extension:", dict(by_ext.most_common()))

    # referenced from html/css/js/json
    referenced = set()
    scan = (
        PUBLISHED_HTML
        + [f for f in lib.tracked("*.css")]
        + [f for f in lib.tracked("*.js")]
        + [f for f in lib.tracked("*.json") if lib.is_published(f)]
        + lib.tracked("*.webmanifest")
        + lib.tracked("*.xml")
    )
    pat = re.compile(r"[\"'(]([^\"'()\s]+\.(?:png|jpe?g|gif|svg|webp|avif|ico))", re.I)

    def norm(hit):
        # og:image and JSON-LD write absolute URLs; CSS writes ../ relative ones.
        hit = hit.split("?")[0].split("#")[0]
        hit = re.sub(r"^https?://(www\.)?economicsacademy\.co\.uk/?", "", hit)
        hit = re.sub(r"^(\.\./)+", "", hit)
        return hit.lstrip("/")

    for f in scan + lib.tracked("flashcards-data/*/*.json"):
        if not os.path.exists(f):
            continue
        for hit in pat.findall(lib.read(f)):
            referenced.add(norm(hit))
            # a css url() is relative to the sheet, not to the site root
            base = os.path.dirname(f)
            rel = os.path.normpath(os.path.join(base, hit.split("?")[0].split("#")[0]))
            referenced.add(rel)

    unref = [f for f in tracked_img if f not in referenced]
    unref_bytes = sum(os.path.getsize(f) for f in unref if os.path.exists(f))
    print(f"\n-- images referenced by nothing: {len(unref)}, {unref_bytes/1024:.0f} KB")
    for f in sorted(unref):
        size = os.path.getsize(f) / 1024 if os.path.exists(f) else 0
        print(f"    {size:>8.0f} KB  {f}")

    # <img> attribute census
    print("\n-- <img> tags in published HTML --")
    rows = defaultdict(lambda: Counter())
    biggest = []
    srcs = Counter()
    for p in PUBLISHED_HTML:
        for tag in IMG_TAG.findall(lib.read(p)):
            a = attrs(tag)
            f = FAMILY[p]
            rows[f]["imgs"] += 1
            if not a.get("alt", "").strip():
                rows[f]["no-alt"] += 1
            if not (a.get("width") and a.get("height")):
                rows[f]["no-dims"] += 1
            if not a.get("loading"):
                rows[f]["no-loading"] += 1
            elif a["loading"] == "lazy":
                rows[f]["lazy"] += 1
            if not a.get("decoding"):
                rows[f]["no-decoding"] += 1
            src = local_asset(a.get("src", ""))
            if src:
                srcs[src] += 1
    print(f"{'family':<14} {'imgs':>5} {'no-alt':>7} {'no-dims':>8} {'no-loading':>11} {'lazy':>5} {'no-decoding':>12}")
    for f in FAM_ORDER:
        if f not in rows:
            continue
        r = rows[f]
        print(
            f"{f:<14} {r['imgs']:>5} {r['no-alt']:>7} {r['no-dims']:>8} "
            f"{r['no-loading']:>11} {r['lazy']:>5} {r['no-decoding']:>12}"
        )

    # heaviest images actually used
    print("\n-- 20 heaviest referenced images --")
    used = [(os.path.getsize(f), f) for f in tracked_img if f in referenced and os.path.exists(f)]
    for size, f in sorted(used, reverse=True)[:20]:
        print(f"    {size/1024:>8.0f} KB  {f}  (used on {srcs.get(f,0)} <img>)")

    # format opportunity
    png = [f for f in tracked_img if f.lower().endswith(".png")]
    png_bytes = sum(os.path.getsize(f) for f in png if os.path.exists(f))
    webp = [f for f in tracked_img if f.lower().endswith((".webp", ".avif"))]
    print(f"\n-- PNG: {len(png)} files, {png_bytes/1024/1024:.1f} MB. WebP/AVIF: {len(webp)}")
    del biggest


# ================================================================= section 7


def s7_fonts():
    print("=== 7. Fonts ===\n")
    fonts = [f for f in lib.tracked("*") if f.lower().endswith((".woff2", ".woff", ".ttf", ".otf", ".eot"))]
    pub = [f for f in fonts if lib.is_published(f)]
    print(f"tracked font files: {len(fonts)} ({len(pub)} published)")
    by_dir = Counter(os.path.dirname(f) for f in fonts)
    for d, n in by_dir.most_common():
        b = sum(os.path.getsize(f) for f in fonts if os.path.dirname(f) == d and os.path.exists(f))
        print(f"  {n:>4} files, {b/1024:>7.0f} KB  {d}/")

    print("\n-- remote font/stylesheet origins referenced from <head> --")
    origins = Counter()
    preconnects = Counter()
    preloads = Counter()
    for p in PUBLISHED_HTML:
        head = head_of(lib.read(p))
        for tag in re.findall(r"<link\b[^>]*>", head, re.I):
            a = attrs(tag)
            rel, href = a.get("rel", ""), a.get("href", "")
            if href.startswith("http"):
                host = re.sub(r"^https?://([^/]+).*", r"\1", href)
                if rel == "preconnect":
                    preconnects[host] += 1
                elif rel == "stylesheet":
                    origins[host] += 1
                elif rel == "preload":
                    preloads[host] += 1
            elif rel == "preload":
                preloads[local_asset(href) or href] += 1
    print("  stylesheet origins:", dict(origins))
    print("  preconnect:        ", dict(preconnects))
    print("  preload:           ", dict(preloads) or "none")

    print("\n-- @font-face and font-display in local CSS --")
    for f in lib.tracked("*.css"):
        css = lib.read(f)
        faces = len(re.findall(r"@font-face", css, re.I))
        if not faces:
            continue
        disp = Counter(re.findall(r"font-display\s*:\s*([a-z-]+)", css, re.I))
        print(f"  {f:<44} {faces:>3} @font-face, font-display: {dict(disp) or 'ABSENT'}")

    print("\n-- fonts referenced by url() in CSS but not tracked --")
    missing = set()
    for f in lib.tracked("*.css"):
        base = os.path.dirname(f)
        for u in re.findall(r"url\(\s*['\"]?([^'\")]+)['\"]?\s*\)", lib.read(f)):
            if u.startswith(("http", "data:")):
                continue
            path = os.path.normpath(os.path.join(base, u.split("?")[0].split("#")[0]))
            if not os.path.exists(path):
                missing.add((f, u))
    print(f"  {len(missing)}")
    for f, u in sorted(missing)[:20]:
        print(f"    {f}: {u}")


# ================================================================= section 8


def s8_semantics():
    print("=== 8. ARIA and semantics ===\n")

    checks = defaultdict(Counter)
    noscript_pages = []
    button_no_type = []
    aria_controls_missing = []
    dup_ids = []
    for p in PUBLISHED_HTML:
        text = lib.read(p)
        f = FAMILY[p]
        checks[f]["pages"] += 1
        if "<noscript" in text.lower():
            checks[f]["noscript"] += 1
            noscript_pages.append(p)
        if re.search(r"<main\b", text, re.I):
            checks[f]["main"] += 1
        if re.search(r"<nav\b", text, re.I):
            checks[f]["nav"] += 1
        if re.search(r"<header\b", text, re.I):
            checks[f]["header"] += 1
        if re.search(r"<footer\b", text, re.I):
            checks[f]["footer"] += 1
        if re.search(r"<article\b", text, re.I):
            checks[f]["article"] += 1
        if re.search(r"<aside\b", text, re.I):
            checks[f]["aside"] += 1
        checks[f]["buttons"] += len(re.findall(r"<button\b", text, re.I))
        checks[f]["aria-expanded"] += len(re.findall(r"aria-expanded", text, re.I))
        checks[f]["aria-controls"] += len(re.findall(r"aria-controls", text, re.I))
        checks[f]["aria-label"] += len(re.findall(r"aria-label=", text, re.I))
        checks[f]["aria-hidden"] += len(re.findall(r"aria-hidden", text, re.I))
        checks[f]["role="] += len(re.findall(r"\brole=", text, re.I))
        checks[f]["tabindex"] += len(re.findall(r"tabindex=", text, re.I))
        # <button> without type= defaults to submit inside a form
        for tag in re.findall(r"<button\b([^>]*)>", text, re.I):
            if "type=" not in tag.lower():
                button_no_type.append(p)
                break
        # aria-controls pointing at an id that is not in the page
        ids = set(re.findall(r'\sid="([^"]+)"', text))
        for target in re.findall(r'aria-controls="([^"]+)"', text):
            for t in target.split():
                if t not in ids:
                    aria_controls_missing.append((p, t))
        seen = Counter(re.findall(r'\sid="([^"]+)"', text))
        for k, v in seen.items():
            if v > 1:
                dup_ids.append((p, k, v))

    print(f"{'family':<14} {'pages':>5} {'main':>5} {'nav':>4} {'hdr':>4} {'ftr':>4} {'art':>4} {'noscr':>6} {'btns':>5} {'a-exp':>6} {'a-ctl':>6} {'a-lbl':>6} {'role':>5}")
    for f in FAM_ORDER:
        if f not in checks:
            continue
        c = checks[f]
        print(
            f"{f:<14} {c['pages']:>5} {c['main']:>5} {c['nav']:>4} {c['header']:>4} "
            f"{c['footer']:>4} {c['article']:>4} {c['noscript']:>6} {c['buttons']:>5} "
            f"{c['aria-expanded']:>6} {c['aria-controls']:>6} {c['aria-label']:>6} {c['role=']:>5}"
        )

    print(f"\n-- pages with a <noscript>: {len(noscript_pages)}")
    for p in noscript_pages[:10]:
        print(f"    {p}")

    print(f"\n-- pages with at least one <button> lacking type=: {len(button_no_type)}")
    print("   ", fam_counts(button_no_type) or "none")
    for p in button_no_type[:6]:
        print(f"    {p}")

    print(f"\n-- aria-controls targets not present in the same page: {len(aria_controls_missing)}")
    for p, t in aria_controls_missing[:12]:
        print(f"    {p}  -> #{t}")

    print(f"\n-- duplicate id= within one page: {len(dup_ids)}")
    for p, k, v in dup_ids[:12]:
        print(f"    {p}  id={k} x{v}")

    # link text quality
    print("\n-- non-descriptive link text --")
    bad = Counter()
    A_TEXT = re.compile(r"<a\b[^>]*>(.*?)</a>", re.I | re.S)
    TAGS = re.compile(r"<[^>]+>")
    for p in PUBLISHED_HTML:
        for inner in A_TEXT.findall(lib.read(p)):
            txt = re.sub(r"\s+", " ", TAGS.sub("", inner)).strip().lower()
            if txt in ("click here", "here", "read more", "more", "link", "this", "learn more", ""):
                bad[txt or "(empty)"] += 1
    print("  ", dict(bad.most_common()) or "none")

    # target=_blank without rel=noopener
    print("\n-- target=\"_blank\" without rel containing noopener --")
    blank = []
    for p in PUBLISHED_HTML:
        for tag in re.findall(r"<a\b[^>]*>", lib.read(p), re.I):
            a = attrs(tag)
            if a.get("target") == "_blank" and "noopener" not in a.get("rel", ""):
                blank.append((p, a.get("href", "")))
    print(f"  {len(blank)}")
    for p, h in blank[:10]:
        print(f"    {p}  -> {h}")

    # skip link target
    print("\n-- skip link --")
    tpl = lib.read("templates/header.html")
    m = re.search(r'<a\b[^>]*class="[^"]*skip[^"]*"[^>]*>', tpl, re.I)
    print("  templates/header.html:", m.group(0) if m else "NOT FOUND")
    no_main_anchor = [p for p in PAGES if not re.search(r'id="main"', lib.read(p))]
    print(f"  pages with no id=\"main\" anchor: {len(no_main_anchor)}  {no_main_anchor[:5]}")


# ================================================================= section 9


def s9_third_party():
    print("=== 9. GA4 and third-party consistency ===\n")
    GA_ID = re.compile(r"G-[A-Z0-9]{8,}")
    ids = defaultdict(list)
    no_ga = []
    gtag_variants = Counter()
    for p in PAGES:
        text = lib.read(p)
        found = set(GA_ID.findall(text))
        if not found:
            no_ga.append(p)
        for i in found:
            ids[i].append(p)
        m = re.search(r"<script[^>]*googletagmanager[^>]*>.*?</script>\s*<script>(.*?)</script>", text, re.S | re.I)
        if m:
            gtag_variants[re.sub(r"\s+", " ", m.group(1)).strip()] += 1
    print("GA4 measurement IDs found:")
    for i, pgs in ids.items():
        print(f"  {i}  on {len(pgs)} of {len(PAGES)} pages")
    print(f"pages with no GA4 id: {len(no_ga)}  {no_ga[:5]}")
    print(f"\ndistinct gtag init snippets: {len(gtag_variants)}")
    for snippet, n in gtag_variants.most_common():
        print(f"  {n:>4}x  {snippet[:150]}")

    print("\n-- third-party hosts referenced from any published HTML --")
    hosts = Counter()
    host_pages = defaultdict(set)
    for p in PUBLISHED_HTML:
        for url in re.findall(r'(?:src|href)="(https?://[^"]+)"', lib.read(p)):
            h = re.sub(r"^https?://([^/]+).*", r"\1", url)
            if "economicsacademy.co.uk" in h:
                continue
            hosts[h] += 1
            host_pages[h].add(p)
    for h, n in hosts.most_common():
        print(f"  {n:>5} refs on {len(host_pages[h]):>4} pages   {h}")


SECTIONS = {
    "1": s1_stylesheets,
    "2": s2_scoping,
    "3": s3_selector_reach,
    "4": s4_scripts,
    "5": s5_head_order,
    "6": s6_images,
    "7": s7_fonts,
    "8": s8_semantics,
    "9": s9_third_party,
}

if __name__ == "__main__":
    wanted = sys.argv[1:] or sorted(SECTIONS)
    for key in wanted:
        SECTIONS[key]()
        print("\n" + "=" * 78 + "\n")

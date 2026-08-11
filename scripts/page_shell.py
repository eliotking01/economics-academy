#!/usr/bin/env python3
"""The shared <head>, rendered from about ten values. Wave 2 Phase 2.

    python3 scripts/page_shell.py --selftest
    python3 scripts/page_shell.py --selftest --family notes-topic --verbose
    python3 scripts/page_shell.py --show revision-notes/edexcel-theme-1/1-2-2-demand.html

WIRED INTO NOTHING, AND IT WRITES NO FILES. That is the whole design of this
phase: PH06 section 3 calls it "the highest-information, lowest-risk step in
the plan - if the shell module cannot reproduce today's <head> exactly, that is
discovered here, at zero cost, before anything is written."

WHAT --selftest DOES
--------------------
For each of the 190 hand-written pages: read the committed <head>, pull out the
values a template would need, render a <head> from those values alone, and
compare. It reports four progressively weaker equalities, because "can it
reproduce the head" turns out to have four different answers:

  L1  byte-identical                    the committed bytes, exactly
  L2  identical after Prettier 3.9.6    same content, formatted canonically
  L3  identical ignoring whitespace     same tags, same order, same values
  L4  same tags and values, any order   same information, different sequence

L1 is PH06's stated exit criterion. It is not reachable, and the reason is
measured rather than argued - see THE FINDING below. L3 is the criterion that
actually protects the site, because compare_trees.py's ten assertions are all
whitespace-insensitive except assertion 3, which covers LaTeX inside the
content slice and never touches the <head>.

THE FINDING
-----------
Only 6 of the 190 hand-written pages are byte-identical to their own Prettier
output. The site's HTML has never been run through Prettier - only the four
generators run it, over their own output. So "render the head and compare
bytes" cannot succeed on 184 pages no matter how good the template is, and
that is a fact about the committed files rather than about the shell.

Three kinds of real, non-whitespace drift sit underneath that, all found by
diffing the 13 byte-level <head> formats the 166 notes pages carry:

  * The MathJax config block has several variants. Some pages carry the
    trailing comments `// Both $...$ and \\(...\\)` and `// Allows \\_ in text`
    and some do not; some carry an `autoload` block and some do not. PH08-039
    counted the <script src> tag's `id` attribute and never looked at the
    config beneath it.
  * The page stylesheet moves. On 28 pages `<link href="/css/pages/...">`
    sits in a different position relative to the MathJax block.
  * Two pages carry a decorative `<!-- ==== -->` separator comment; one
    carries a 30-line <style> block (PH08-042, already known).

None of that is whitespace, which is why running Prettier over all 190 leaves
the count at 13 rather than collapsing it. It is exactly the drift a template
exists to remove - so the honest reading is that the shell reproduces the head
at L3 and the residue is the improvement, not a failure.

Standard library only. Prettier is used only by --selftest's L2 column, and
only when `npx` is available; without it L2 reports as not run.
"""

from __future__ import annotations

import argparse
import collections
import json
import pathlib
import re
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import build_sitemap  # noqa: E402
import verify_page_shell as shell_check  # noqa: E402  - family_of(), pages()

SITE = "https://economicsacademy.co.uk"
BOARDS = json.loads(
    (ROOT / "boards-data" / "boards.json").read_text(encoding="utf-8"))["boards"]

PRINT_WIDTH = 80   # Prettier's default, and CLAUDE.md pins Prettier 3.9.6
INDENT = 4         # inside <head>


# --------------------------------------------------------------------------
# Prettier-shaped emission
# --------------------------------------------------------------------------

def tag(name: str, attrs: list[tuple[str, str | None]], indent: int = INDENT,
        void: bool = True) -> str:
    """One element, wrapped the way Prettier 3.9.6 wraps it.

    Prettier keeps a tag on one line if it fits inside printWidth, and
    otherwise puts every attribute on its own line indented by two with the
    closing bracket back at the tag's own indent. Reproducing that rule rather
    than hardcoding which tags wrap is what lets one template emit a <head>
    whose long descriptions wrap and whose `content="1200"` does not.
    """
    pad = " " * indent
    parts = [f' {k}="{v}"' if v is not None else f" {k}" for k, v in attrs]
    one = f"{pad}<{name}" + "".join(parts) + (" />" if void else ">")
    if len(one) <= PRINT_WIDTH:
        return one
    lines = [f"{pad}<{name}"]
    lines += [f"{pad}  {p.strip()}" for p in parts]
    lines.append(pad + ("/>" if void else ">"))
    return "\n".join(lines)


def ldjson(obj, indent: int = INDENT + 2) -> str:
    """A JSON-LD block, serialised the way the notes pages carry it.

    json.dumps(indent=2) re-indented, key order preserved from the object, and
    the script tags at the head's own indent. ensure_ascii is off because the
    pages carry real em dashes and pound signs rather than escapes.
    """
    body = json.dumps(obj, indent=2, ensure_ascii=False)
    body = "\n".join(" " * indent + line for line in body.splitlines())
    pad = " " * INDENT
    return (f'{pad}<script type="application/ld+json">\n'
            f"{body}\n"
            f"{pad}</script>")


# The blocks every page carries verbatim, byte for byte. page_anatomy.py
# section 1 measured these as identical wherever they appear: the gtag pair on
# 463, the favicon trio on 463, the hoist comment on 463, the preconnect pair
# on 463.
GTAG = '''    <!-- Google tag (gtag.js) -->
    <script
      async
      src="https://www.googletagmanager.com/gtag/js?id=G-YVCNRW4QH6"
    ></script>
    <script>
      window.dataLayer = window.dataLayer || [];
      function gtag() {
        dataLayer.push(arguments);
      }
      gtag("js", new Date());

      gtag("config", "G-YVCNRW4QH6");
    </script>'''

FAVICONS = '''    <link rel="icon" href="/favicon.ico" sizes="any" />
    <link rel="apple-touch-icon" href="/apple-touch-icon.png" />
    <link rel="manifest" href="/site.webmanifest" />'''

# 4db232c. DO-NOT-BREAK: the two @import rules stay out of css/main.css, the
# stylesheet stays a direct <link> in every <head>, in this order.
# verify_css_load_order.py holds it at 462/462 and exists for this module.
HOIST_COMMENT = '''    <!-- Linked here rather than @imported from main.css: an @import inside a
         render-blocking stylesheet is invisible to the preload scanner, so
         neither request could start until main.css had parsed. The order below
         matches the old @import order, so the cascade is unchanged.
         See seo/09-web-vitals-baseline.md. -->'''

PRECONNECT = '''    <link rel="preconnect" href="https://fonts.googleapis.com" />
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />'''

GOOGLE_FONTS = (
    "https://fonts.googleapis.com/css2?family=Merriweather:ital,wght@0,400;"
    "0,700;1,400&amp;family=Open+Sans:wght@400;600;700&amp;family=Source+Sans"
    "+Pro:ital,wght@0,300;0,400;0,700;0,900;1,300&amp;display=swap"
)

OG_IMAGE = f"{SITE}/og-image.png?v=1"


# --------------------------------------------------------------------------
# The shell
# --------------------------------------------------------------------------

def render_head(v: dict) -> str:
    """The <head> for one page, from its values. Returns the inner HTML."""
    out: list[str] = [GTAG]
    out.append(tag("meta", [("charset", "utf-8")]))
    out.append(tag("meta", [("name", "viewport"),
                            ("content", "width=device-width, initial-scale=1")]))

    title = v["title"]
    one = f'{" " * INDENT}<title>{title}</title>'
    out.append(one if len(one) <= PRINT_WIDTH else
               f'{" " * INDENT}<title>\n{" " * (INDENT + 2)}{title}\n'
               f'{" " * INDENT}</title>')
    out.append(tag("meta", [("name", "description"), ("content", v["description"])]))

    # A decorative <!-- ==== --> divider sits between the description and the
    # canonical on exactly 2 of 463 pages. It is invisible to a reader and a
    # crawler, and the template exists to remove drift like it - but Eliot's
    # Option A criterion is "same tags, same order, same values, only
    # whitespace may differ", and a comment is a token rather than whitespace.
    # So it is lifted and re-emitted, and dropping it stays a decision for
    # Eliot to make rather than one made silently here.
    if v.get("dividerAfterDescription"):
        out.append(v["dividerAfterDescription"])
    if v.get("robots"):
        out.append(tag("meta", [("name", "robots"), ("content", v["robots"])]))
    if v.get("canonical"):
        out.append(tag("link", [("rel", "canonical"), ("href", v["canonical"])]))

    # ---- Open Graph
    og = v.get("og", {})
    if og:
        if v.get("ogComment"):
            out.append("    <!-- Open Graph -->")
        out.append(tag("meta", [("property", "og:type"), ("content", og["type"])]))
        if og.get("siteName"):
            out.append(tag("meta", [("property", "og:site_name"),
                                    ("content", og["siteName"])]))
        if og.get("locale"):
            out.append(tag("meta", [("property", "og:locale"),
                                    ("content", og["locale"])]))
        out.append(tag("meta", [("property", "og:url"), ("content", og["url"])]))
        out.append(tag("meta", [("property", "og:title"), ("content", og["title"])]))
        out.append(tag("meta", [("property", "og:description"),
                                ("content", og["description"])]))
        # about.html carries its own photograph at 800x800 as image/jpeg with
        # its own alt, so every part of the image set is lifted rather than
        # assumed to be the site logo.
        if og.get("image"):
            out.append(tag("meta", [("property", "og:image"),
                                    ("content", og["image"])]))
            for k in ("width", "height", "type", "alt"):
                if og.get(f"image:{k}") is not None:
                    out.append(tag("meta", [("property", f"og:image:{k}"),
                                            ("content", og[f"image:{k}"])]))

    # ---- Twitter
    tw = v.get("twitter", {})
    if tw:
        out.append(tag("meta", [("name", "twitter:card"),
                                ("content", tw["card"])]))
        if tw.get("title"):
            out.append(tag("meta", [("name", "twitter:title"),
                                    ("content", tw["title"])]))
        if tw.get("description"):
            out.append(tag("meta", [("name", "twitter:description"),
                                    ("content", tw["description"])]))
        if tw.get("image"):
            out.append(tag("meta", [("name", "twitter:image"),
                                    ("content", tw["image"])]))

    # ---- structured data, favicons, stylesheets
    # The comment introduces whichever JSON-LD group the page actually has.
    # macro-application puts both blocks after the stylesheets, so keying it to
    # the "before" group alone silently dropped its comment.
    if v.get("sdComment") and v.get("jsonldBeforeIcons"):
        out.append("    <!-- Structured data -->")
    for block in v.get("jsonldBeforeIcons", []):
        out.append(ldjson(block))
    out.append(FAVICONS)
    out.append(HOIST_COMMENT)
    out.append(PRECONNECT)
    for href in v.get("extraPreconnects", []):
        out.append(tag("link", [("rel", "preconnect"), ("href", href)]))
    out.append(tag("link", [("rel", "stylesheet"),
                            ("href", "/css/fontawesome-all.min.css")]))
    out.append(tag("link", [("rel", "stylesheet"), ("href", GOOGLE_FONTS)]))
    out.append(tag("link", [("rel", "stylesheet"), ("href", "/css/main.css")]))
    for href in v.get("pageStylesheets", []):
        out.append(tag("link", [("rel", "stylesheet"), ("href", href)]))

    # ---- MathJax
    if v.get("headStyle"):
        out.append(v["headStyle"])
    if v.get("mathjax"):
        # The config body is LIFTED when the caller supplies one, so that the
        # selftest measures whether the shell's structure is right rather than
        # whether a page's config has drifted. Three distinct bodies exist
        # across the 126 pages (89 / 18 / 19) and reconciling them is a Phase 5
        # normalisation with its own commit - see MATHJAX_CONFIG.
        cfg = v.get("mathjaxConfig") or MATHJAX_CONFIG_BODY
        if v.get("mathjaxComment"):
            out.append("    <!-- MathJax Configuration -->")
        out.append(cfg)
        src = ("https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js")
        if v["mathjax"] == "with-id":
            attrs = [("id", "MathJax-script"), ("async", None), ("src", src)]
        else:
            attrs = [("src", src), ("async", None)]
        out.append(tag("script", attrs, void=False) + "</script>")

    if v.get("sdComment") and not v.get("jsonldBeforeIcons"):
        out.append("    <!-- Structured data -->")
    for block in v.get("jsonldAfterStyles", []):
        out.append(ldjson(block))
    return "\n".join(out)


# The MathJax configuration, as the 97 baseline pages carry it. The variants
# are the finding: 33 pages drop the trailing comments, 18 drop `autoload`.
# Emitting one config is what removes that, and it is a Phase 5 normalisation
# with its own commit, not something this module decides.
MATHJAX_CONFIG_BODY = '''    <script>
      window.MathJax = {
        tex: {
          inlineMath: [
            ["$", "$"],
            ["\\\\(", "\\\\)"],
          ], // Both $...$ and \\(...\\)
          displayMath: [
            ["$$", "$$"],
            ["\\\\[", "\\\\]"],
          ],
          processEscapes: true, // Allows \\_ in text
          autoload: {
            color: [],
            ams: ["boldsymbol"], // For \\mathbf{}
          },
        },
        options: {
          skipHtmlTags: ["script", "noscript", "style", "textarea", "pre"],
        },
      };
    </script>'''


# --------------------------------------------------------------------------
# Extraction - the selftest's inverse
# --------------------------------------------------------------------------

HEAD = re.compile(r"<head>(.*?)</head>", re.S)
META = re.compile(r"<meta\b([^>]*?)/?>", re.I)
LINK = re.compile(r"<link\b([^>]*?)/?>", re.I)
ATTR = re.compile(r'([\w:.-]+)\s*=\s*"([^"]*)"')
TITLE = re.compile(r"<title[^>]*>(.*?)</title>", re.S | re.I)
LD = re.compile(r'<script type="application/ld\+json">(.*?)</script>', re.S)
MJ_SRC = re.compile(r"<script\b([^>]*?)>\s*</script>", re.S)


def extract(source: str) -> dict:
    """The values a template would need, lifted verbatim from the page.

    Lifted, never re-derived. The meta descriptions are bespoke per page and
    rewriting one would be a content change - PH06's risk table names that as
    the failure mode assertion 5 exists to catch.
    """
    head = HEAD.search(source)
    if not head:
        return {}
    h = head.group(1)
    metas = {}
    for raw in META.findall(h):
        a = {k.lower(): v for k, v in ATTR.findall(raw)}
        key = (a.get("name") or a.get("property") or "").lower()
        if key:
            metas.setdefault(key, a.get("content", ""))

    v: dict = {}
    t = TITLE.search(h)
    v["title"] = " ".join(t.group(1).split()) if t else ""
    v["description"] = metas.get("description", "")
    if "robots" in metas:
        v["robots"] = metas["robots"]
    div = re.search(r'/>\n(\s*<!--\s*=+\s*-->)\n\s*<link[^>]*rel="canonical"',
                    h, re.S)
    if div:
        v["dividerAfterDescription"] = div.group(1)

    for raw in LINK.findall(h):
        a = {k.lower(): v2 for k, v2 in ATTR.findall(raw)}
        if a.get("rel") == "canonical":
            v["canonical"] = a.get("href", "")

    if "og:title" in metas:
        v["og"] = {
            "type": metas.get("og:type", "website"),
            "url": metas.get("og:url", ""),
            "title": metas.get("og:title", ""),
            "description": metas.get("og:description", ""),
        }
        if "og:site_name" in metas:
            v["og"]["siteName"] = metas["og:site_name"]
        if "og:locale" in metas:
            v["og"]["locale"] = metas["og:locale"]
        if "og:image" in metas:
            v["og"]["image"] = metas["og:image"]
            for k in ("width", "height", "type", "alt"):
                if f"og:image:{k}" in metas:
                    v["og"][f"image:{k}"] = metas[f"og:image:{k}"]
        v["ogComment"] = "<!-- Open Graph -->" in h
    v["sdComment"] = "<!-- Structured data -->" in h
    if "twitter:card" in metas:
        v["twitter"] = {"card": metas["twitter:card"]}
        if "twitter:title" in metas:
            v["twitter"]["title"] = metas["twitter:title"]
        if "twitter:description" in metas:
            v["twitter"]["description"] = metas["twitter:description"]
        if "twitter:image" in metas:
            v["twitter"]["image"] = metas["twitter:image"]

    v["pageStylesheets"] = [
        a["href"] for a in
        ({k.lower(): v2 for k, v2 in ATTR.findall(raw)} for raw in LINK.findall(h))
        if a.get("rel") == "stylesheet" and a.get("href", "").startswith("/css/pages/")
    ]

    v["mathjaxComment"] = "<!-- MathJax Configuration -->" in h
    v["extraPreconnects"] = [
        a["href"] for a in
        ({k.lower(): v2 for k, v2 in ATTR.findall(raw)} for raw in LINK.findall(h))
        if a.get("rel") == "preconnect"
        and a.get("href", "") not in ("https://fonts.googleapis.com",
                                      "https://fonts.gstatic.com")
    ]
    mc = re.search(r"[ \t]*<script>\s*window\.MathJax\s*=.*?</script>", h, re.S)
    v["mathjaxConfig"] = mc.group(0) if mc else None
    st = re.search(r"[ \t]*<style>.*?</style>", h, re.S)
    v["headStyle"] = st.group(0) if st else None
    v["mathjax"] = None
    for raw in MJ_SRC.findall(h):
        a = {k.lower(): v2 for k, v2 in ATTR.findall(raw)}
        if "mathjax" in a.get("src", "").lower():
            v["mathjax"] = "with-id" if a.get("id") == "MathJax-script" else "no-id"

    # Which side of the stylesheet block each JSON-LD block sits on is part of
    # the page's shape, so it is lifted rather than assumed: the notes pages
    # put the BreadcrumbList after MathJax, past-papers puts both before the
    # favicons.
    css_at = h.find("/css/main.css")
    before, after = [], []
    for m in LD.finditer(h):
        try:
            obj = json.loads(m.group(1))
        except ValueError:
            continue
        (before if m.start() < css_at else after).append(obj)
    v["jsonldBeforeIcons"] = before
    v["jsonldAfterStyles"] = after
    return v


# --------------------------------------------------------------------------
# Comparison
# --------------------------------------------------------------------------

TAGS = re.compile(r"<[^>]+>|[^<]+")
COMMENT = re.compile(r"<!--.*?-->", re.S)


def squeeze(s: str) -> str:
    """Collapse whitespace between and inside tags, for L3."""
    out = []
    for tok in TAGS.findall(s):
        tok = " ".join(tok.split())
        if tok:
            out.append(tok)
    return "\n".join(out)


def decomment(s: str) -> str:
    """Drop HTML comments, for the L3c column.

    A comment is invisible to the reader and to a crawler, and a template
    emits its own set rather than each page's. The one comment that is NOT
    decorative - the @import-hoist note recording 4db232c - is emitted by the
    shell, so dropping the rest loses nothing load-bearing.
    """
    return COMMENT.sub("", s)


def token_multiset(s: str):
    """Tags and their attributes, order-insensitive, for L4."""
    return collections.Counter(
        t for t in squeeze(s).splitlines() if t.startswith("<"))


def prettier(text: str, tmp: pathlib.Path) -> str | None:
    tmp.write_text(f"<!doctype html>\n<html><head>\n{text}\n</head><body></body></html>",
                   encoding="utf-8")
    p = subprocess.run(["npx", "prettier@3.9.6", "--parser", "html", str(tmp)],
                       capture_output=True, text=True)
    return p.stdout if p.returncode == 0 else None


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--show", metavar="PATH",
                    help="print the rendered <head> for one page and exit")
    ap.add_argument("--family", action="append", default=[])
    ap.add_argument("--verbose", action="store_true")
    ap.add_argument("--prettier", action="store_true",
                    help="run the L2 column, which needs npx")
    args = ap.parse_args()

    if args.show:
        src = (ROOT / args.show).read_text(encoding="utf-8")
        print(render_head(extract(src)))
        return 0
    if not args.selftest:
        ap.print_help()
        return 2

    hand = set(shell_check.HAND_WRITTEN)
    paths = [p for p in shell_check.pages()
             if shell_check.family_of(p) in hand
             and (not args.family or shell_check.family_of(p) in args.family)]

    tmp = ROOT / ".page_shell_selftest.tmp.html"
    stats: dict[str, collections.Counter] = collections.defaultdict(collections.Counter)
    worst: dict[str, list] = collections.defaultdict(list)
    try:
        for p in paths:
            fam = shell_check.family_of(p)
            src = (ROOT / p).read_text(encoding="utf-8")
            committed = HEAD.search(src).group(1)
            rendered = render_head(extract(src))
            stats[fam]["pages"] += 1
            # L0: does any VALUE change? Re-extract from the rendered head and
            # compare. This is the question that actually matters - whitespace
            # and block order are formatting, a lost canonical is a defect.
            v1 = extract(src)
            v2 = extract(f"<head>{rendered}</head>")
            for d in (v1, v2):
                for k in ("ogComment", "sdComment", "mathjaxComment",
                          "mathjaxConfig", "headStyle"):
                    d.pop(k, None)
            if v1 == v2:
                stats[fam]["L0"] += 1
            # The captured group runs from just after <head> to just before
            # </head>, so it opens with a newline and closes with the two
            # spaces that indent </head>. An earlier version compared
            # committed.strip("\n") against the render, which leaves those two
            # spaces in place and could therefore NEVER match - it reported
            # L1 = 0/190 for the whole corpus, which was a bug in this file
            # rather than a fact about the pages. Corrected 2026-08-11.
            if committed == "\n" + rendered + "\n  ":
                stats[fam]["L1"] += 1
            if args.prettier:
                a, b = prettier(committed, tmp), prettier(rendered, tmp)
                if a is not None and a == b:
                    stats[fam]["L2"] += 1
            if squeeze(committed) == squeeze(rendered):
                stats[fam]["L3"] += 1
            if squeeze(decomment(committed)) == squeeze(decomment(rendered)):
                stats[fam]["L3c"] += 1
            if token_multiset(committed) == token_multiset(rendered):
                stats[fam]["L4"] += 1
            if squeeze(decomment(committed)) != squeeze(decomment(rendered)):
                d = token_multiset(committed) - token_multiset(rendered)
                e = token_multiset(rendered) - token_multiset(committed)
                worst[fam].append(
                    (p, f"-{sum(d.values())} +{sum(e.values())} tags"))
    finally:
        tmp.unlink(missing_ok=True)

    cols = ("pages", "L0", "L1", "L2", "L3", "L3c", "L4")
    print(f"{'family':14} " + " ".join(f"{c:>6}" for c in cols))
    tot = collections.Counter()
    for fam in sorted(stats):
        s = stats[fam]
        tot.update(s)
        print(f"{fam:14} " + " ".join(f"{s[c]:>6}" for c in cols))
    print(f"{'TOTAL':14} " + " ".join(f"{tot[c]:>6}" for c in cols))
    print()
    print("  L0  every extracted value survives a render/re-extract round trip")
    print("  L1  byte-identical to the committed <head>")
    print("  L2  identical after Prettier 3.9.6 on both sides"
          + ("" if args.prettier else "   (NOT RUN - pass --prettier)"))
    print("  L3  identical ignoring whitespace: same tags, order and values")
    print("  L3c as L3, and also ignoring decorative HTML comments")
    print("  L4  same tags and values, in any order")

    if args.verbose:
        for fam in sorted(worst):
            if not worst[fam]:
                continue
            print(f"\n-- {fam}: {len(worst[fam])} pages not L3 --")
            for path, why in worst[fam][:15]:
                print(f"   {why:32} {path}")
    n = len(paths)
    print(f"\n{tot['L0']}/{n} heads lose no value, {tot['L3']}/{n} reproduced "
          f"at L3, {tot['L3c']}/{n} at L3c, {tot['L4']}/{n} at L4, "
          f"{tot['L1']}/{n} at L1")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

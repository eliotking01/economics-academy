#!/usr/bin/env python3
"""Build the glossary pages from glossary-data/terms.json.

    python3 scripts/build_glossary.py            # build
    python3 scripts/build_glossary.py --check    # validate, write nothing

Writes revision-notes/glossary/index.html and one page per exam board, updates
the Glossary block in sitemap.xml, and runs Prettier over its own output so
generating twice is byte-identical.

Shape of the pages
------------------
The whole glossary is real HTML in the page - no fetch, no client-side render.
That follows the house precedent set by the past-paper bank, where bounded
indexable lists ship as markup and only the unbounded hub search fetches JSON,
and it is what makes the pages readable with JavaScript off.

A-Z is the primary order, because that is how a glossary is used. Theme is a
filter and a line of metadata on each entry rather than a second set of
headings: listing every term twice under two orderings would double the page
and give each term two anchors.

Formulae are pre-rendered with KaTeX at build time, so the published pages carry
no maths JavaScript. The notes pages still use MathJax, so the same formula
looks slightly different in the two places - recorded in ROADMAP.md.

Standard library only, plus node for KaTeX and npx for Prettier. Neither is
needed to view the site.
"""

from __future__ import annotations

import argparse
import datetime
import html
import json
import pathlib
import re
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = ROOT / "glossary-data" / "terms.json"
TAXONOMY = ROOT / "past-paper-questions-data" / "taxonomy.json"
OUT_DIR = ROOT / "revision-notes" / "glossary"
SITEMAP = ROOT / "sitemap.xml"
KATEX_JS = ROOT / "scripts" / "vendor" / "katex.min.js"

SITE = "https://economicsacademy.co.uk"
GTAG = "G-YVCNRW4QH6"
OG_IMAGE = f"{SITE}/og-image.png?v=1"

LETTERS = [chr(c) for c in range(ord("A"), ord("Z") + 1)]

# Inline markup a definition may carry. extract_glossary.py already narrows to
# this set; restated here so the generator fails loudly rather than emitting
# something unexpected into a page.
ALLOWED = re.compile(r"</?(?:strong|em|sub|sup)>|<br />|<a href=\"[^\"]*\">|</a>")
# A definition may be completed by the list that follows it in the notes.
ALLOWED_LIST = re.compile(r"</?(?:ul|li|strong|em|sub|sup)>|<a href=\"[^\"]*\">|</a>")

BOARDS = {
    "edexcel-a": {
        "slug": "edexcel-a",
        "name": "Edexcel A",
        "long": "Edexcel A-Level Economics A",
        "taxonomy": "edexcel",
        "notesUrl": "/revision-notes/index.html",
        "intro": (
            "Every key term and formula you need for <strong>Edexcel A-Level "
            "Economics A (9EC0)</strong>, covering Themes 1 to 4. Each "
            "definition is taken word for word from the revision notes on this "
            "site, and links back to the topic page it came from."
        ),
        "meta": (
            "Every key term and formula for Edexcel A-Level Economics (9EC0), "
            "taken word for word from our Theme 1-4 revision notes. Search, "
            "browse A-Z or print."
        ),
    },
    "aqa": {
        "slug": "aqa",
        "name": "AQA",
        "long": "AQA A-Level Economics",
        "taxonomy": "aqa",
        "notesUrl": "/revision-notes/index.html",
        "intro": (
            "Every key term and formula you need for <strong>AQA A-Level "
            "Economics (7136)</strong>, covering microeconomics and "
            "macroeconomics. Each definition is taken word for word from the "
            "revision notes on this site, and links back to the topic page it "
            "came from."
        ),
        "meta": (
            "Every key term and formula for AQA A-Level Economics (7136), taken "
            "word for word from our microeconomics and macroeconomics revision "
            "notes. Search or print."
        ),
    },
}

INLINE_TEX = re.compile(r"\\\((.+?)\\\)", re.S)

LANDING_META = (
    "Free A-Level Economics glossary. Choose your exam board for every "
    "definition and formula you need, taken word for word from our Edexcel and "
    "AQA revision notes."
)


class BuildError(Exception):
    pass


# ---------------------------------------------------------------- helpers

def e(s: str) -> str:
    """HTML-escape for attributes and text nodes."""
    return html.escape(s, quote=True)


def tex_to_text(s: str) -> str:
    """Reduce inline LaTeX to readable text. JSON-LD descriptions only.

    A schema.org description is a plain-text field, so `\\( AC = \\frac{TC}{Q}
    \\)` cannot go in it as written - a crawler would index the backslashes.
    This turns it into "AC = TC/Q".

    Scoped deliberately: the visible page always shows the real KaTeX, and this
    never touches it. It runs on the description field and nowhere else.
    """
    def one(m):
        t = m.group(1)
        t = re.sub(r"\\frac\{([^{}]*)\}\{([^{}]*)\}", r"\1/\2", t)
        t = re.sub(r"\\text\{([^{}]*)\}", r"\1", t)
        t = (t.replace(r"\times", "x").replace(r"\%", "%")
              .replace(r"\Delta", "change in").replace(r"\infty", "infinity"))
        t = re.sub(r"\\[a-zA-Z]+", " ", t)
        return re.sub(r"\s+", " ", t.replace("{", "").replace("}", "")).strip()
    return INLINE_TEX.sub(one, s)


def plain(fragment: str) -> str:
    """Fragment -> plain text, for JSON-LD and meta descriptions."""
    return re.sub(r"\s+", " ",
                  tex_to_text(re.sub(r"<[^>]+>", "", fragment))).strip()


def json_ld(obj, indent="      ") -> str:
    s = json.dumps(obj, indent=2, ensure_ascii=False)
    return "\n".join(indent + line for line in s.split("\n")).strip()


def katex(latex_list):
    """Pre-render every formula through KaTeX, in one node process.

    throwOnError is on: a formula that will not render is a build failure, not
    a page that silently ships broken maths. That is how the two unescaped `%`
    characters in the notes were found - `%` starts a comment in TeX, so those
    formulae do not render under MathJax on the notes pages either.

    The output mode is left at KaTeX's default, htmlAndMathml, and must stay
    there. output:"html" halves the markup but emits only the visual spans,
    which KaTeX marks aria-hidden - a screen reader would then find nothing at
    all where the formula is. The MathML is what assistive technology reads.
    """
    return _katex(latex_list, True)


def render_inline_maths(definition: str, inline_map) -> str:
    """Swap \\( ... \\) inside a definition for pre-rendered KaTeX.

    Fifteen definitions state their formula inline - "Average Cost (AC):
    \\( AC = \\frac{TC}{Q} \\)". The glossary pages carry no maths JavaScript,
    so without this those definitions display their LaTeX source to the reader.
    Display formulae are handled separately; only the inline form appears here.
    """
    return INLINE_TEX.sub(
        lambda m: inline_map[html.unescape(m.group(1)).strip()], definition)


def _katex(latex_list, display):
    if not latex_list:
        return []
    script = (
        'const katex=require(process.argv[1]);'
        'const display=process.argv[2]==="1";'
        'let s="";process.stdin.on("data",d=>s+=d).on("end",()=>{'
        'try{'
        'const out=JSON.parse(s).map(t=>katex.renderToString(t,'
        '{displayMode:display,throwOnError:true,strict:false}));'
        'process.stdout.write(JSON.stringify({ok:true,html:out}));'
        '}catch(err){'
        'process.stdout.write(JSON.stringify({ok:false,error:String(err.message||err)}));'
        '}});'
    )
    try:
        r = subprocess.run(
            ["node", "-e", script, str(KATEX_JS), "1" if display else "0"],
            input=json.dumps(latex_list), capture_output=True,
            text=True, check=True, cwd=ROOT,
        )
    except (OSError, subprocess.CalledProcessError) as exc:
        raise BuildError(
            f"could not run node to pre-render formulae: {exc}. "
            f"node is needed at build time only; see scripts/vendor/README.md"
        ) from None
    out = json.loads(r.stdout)
    if not out["ok"]:
        raise BuildError(f"KaTeX could not render a formula: {out['error']}")
    return out["html"]


def slug_ok(s: str) -> bool:
    return bool(re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", s))


# ---------------------------------------------------------------- validation

def validate(data, groups):
    """Collect every failure. Nothing is written if there is one."""
    errs = []
    seen = {}

    for t in data["terms"]:
        where = f"term '{t['term']}'"
        if not slug_ok(t["id"]):
            errs.append(f"{where}: id '{t['id']}' is not a clean slug")
        if t["id"] in seen:
            errs.append(f"{where}: id '{t['id']}' collides with '{seen[t['id']]}'")
        seen[t["id"]] = t["term"]
        if not t["sources"]:
            errs.append(f"{where}: no sources")
        for s in t["sources"]:
            if s["board"] not in BOARDS:
                errs.append(f"{where}: unknown board '{s['board']}'")
            if s["notesUrl"] and not (ROOT / s["notesUrl"].lstrip("/")).is_file():
                errs.append(f"{where}: notesUrl does not exist - {s['notesUrl']}")
            if s["group"] not in groups:
                errs.append(f"{where}: unknown group '{s['group']}'")
            if s.get("definitionListHtml"):
                lst = ALLOWED_LIST.sub("", s["definitionListHtml"])
                if "<" in lst or ">" in lst:
                    errs.append(f"{where}: continuation list carries markup "
                                f"that is not allowed - {lst[:80]}")
            stripped = ALLOWED.sub("", s["definitionHtml"])
            if "<" in stripped or ">" in stripped:
                errs.append(f"{where}: definition carries markup that is not "
                            f"allowed - {stripped[:80]}")
            if re.search(r"&(?!(?:amp|lt|gt|quot|#\d+|#x[0-9a-fA-F]+);)",
                         s["definitionHtml"]):
                errs.append(f"{where}: unescaped & in the definition")
        if t["boards"] != sorted({s["board"] for s in t["sources"]}):
            errs.append(f"{where}: boards do not match its sources")

    fseen = {}
    for f in data["formulae"]:
        where = f"formula '{f['label']}'"
        if f["id"] in fseen:
            errs.append(f"{where}: id '{f['id']}' collides with '{fseen[f['id']]}'")
        fseen[f["id"]] = f["label"]
        if not f["latex"].strip():
            errs.append(f"{where}: empty LaTeX")
        # % begins a comment in TeX. The notes escape it as \% in 39 places and
        # miss it in a couple; catch it here rather than shipping broken maths.
        if re.search(r"(?<!\\)%", f["latex"]):
            errs.append(f"{where}: unescaped % in the LaTeX, which TeX reads as "
                        f"a comment - it must be written \\%. Fix the notes page")

    for board, meta in BOARDS.items():
        if not 120 <= len(meta["meta"]) <= 165:
            errs.append(f"{board}: meta description is {len(meta['meta'])} "
                        f"characters, needs 120-165")
    if not 120 <= len(LANDING_META) <= 165:
        errs.append(f"landing: meta description is {len(LANDING_META)} "
                    f"characters, needs 120-165")
    return errs


# ---------------------------------------------------------------- page shell

def page_shell(*, title, desc, path, crumbs, body, jsonld, katex_css=False):
    """The common page skeleton, in the same head order as every other page."""
    url = f"{SITE}{path}"
    crumb_ld = json_ld({
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {k: v for k, v in
             {"@type": "ListItem", "position": i, "name": name,
              "item": f"{SITE}{href}" if href else None}.items() if v is not None}
            for i, (name, href) in enumerate(crumbs, 1)
        ],
    })
    katex_link = ('\n    <link rel="stylesheet" href="/css/vendor/katex/katex.min.css" />'
                  if katex_css else "")
    return f"""<!doctype html>
<html lang="en-GB">
  <head>
    <!-- Google tag (gtag.js) -->
    <script
      async
      src="https://www.googletagmanager.com/gtag/js?id={GTAG}"
    ></script>
    <script>
      window.dataLayer = window.dataLayer || [];
      function gtag() {{
        dataLayer.push(arguments);
      }}
      gtag("js", new Date());

      gtag("config", "{GTAG}");
    </script>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <link rel="preconnect" href="https://fonts.googleapis.com" />
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
    <title>{e(title)}</title>
    <meta name="description" content="{e(desc)}" />
    <link rel="canonical" href="{url}" />
    <link rel="icon" href="/favicon.ico" sizes="any" />
    <link rel="apple-touch-icon" href="/apple-touch-icon.png" />
    <link rel="manifest" href="/site.webmanifest" />

    <!-- Open Graph -->
    <meta property="og:type" content="website" />
    <meta property="og:site_name" content="Economics Academy" />
    <meta property="og:locale" content="en_GB" />
    <meta property="og:url" content="{url}" />
    <meta property="og:title" content="{e(title)}" />
    <meta property="og:description" content="{e(desc)}" />
    <meta property="og:image" content="{OG_IMAGE}" />
    <meta property="og:image:width" content="1200" />
    <meta property="og:image:height" content="1200" />
    <meta property="og:image:type" content="image/png" />
    <meta property="og:image:alt" content="Economics Academy logo" />
    <meta name="twitter:card" content="summary_large_image" />
    <meta name="twitter:title" content="{e(title)}" />
    <meta name="twitter:description" content="{e(desc)}" />
    <meta name="twitter:image" content="{OG_IMAGE}" />

    <!-- Structured data -->
    <script type="application/ld+json">
      {jsonld}
    </script>
    <script type="application/ld+json">
      {crumb_ld}
    </script>

    <link rel="stylesheet" href="/css/main.css" />
    <link rel="stylesheet" href="/css/pages/glossary.css" />{katex_link}
  </head>
  <body class="is-preload">
    <div id="page-wrapper">
      <!-- Header -->
      <div id="header-placeholder"></div>

      <section id="main" class="glossary-page">
        <div class="container">
{body}
        </div>
      </section>

      <!-- Footer -->
      <div id="footer-placeholder"></div>
    </div>

    <!-- Scripts -->
    <script src="/js/jquery.min.js"></script>
    <script src="/js/jquery.dropotron.min.js"></script>
    <script src="/js/components/inject-templates.js"></script>
    <script src="/js/browser.min.js"></script>
    <script src="/js/breakpoints.min.js"></script>
    <script src="/js/util.js"></script>
    <script src="/js/main.js"></script>
    <script src="/js/components/glossary-filter.js" defer></script>
  </body>
</html>
"""


def breadcrumb_html(crumbs, indent=10):
    pad = " " * indent
    parts = []
    for name, href in crumbs:
        if href:
            parts.append(f'{pad}  <a href="{href}">{e(name)}</a>')
        else:
            parts.append(f"{pad}  <span>{e(name)}</span>")
        parts.append(f'{pad}  <span class="separator">&rsaquo;</span>')
    parts.pop()
    inner = "\n".join(parts)
    return (f'{pad}<nav class="breadcrumb" aria-label="Breadcrumb">\n'
            f"{inner}\n{pad}</nav>")


# ---------------------------------------------------------------- board page

def source_for(term, board):
    """The wording this board shows.

    Sources arrive already ranked by extract_glossary.py - curated preference
    first, then board and spec - so the first source for the board is the one
    curation chose.
    """
    return next(s for s in term["sources"] if s["board"] == board)


def source_link(s):
    """The 'where this is taught' line.

    An authored entry for a concept no page covers yet has no notesUrl, and
    says so rather than linking somewhere that does not cover it.
    """
    group = f'<span class="gl-group">{e(s["groupLabel"])}</span>'
    if not s.get("notesUrl"):
        return (group + '\n                    <span class="gl-nopage"'
                '>Not yet covered in the revision notes</span>')
    return (group + f'\n                    <a href="{e(s["notesUrl"])}"'
            f'>{e(s["spec"])} {e(s["topic"])}</a>')


def entry_html(term, board, inline_map):
    s = source_for(term, board)
    # Five definitions end on a colon because the rest of them is the bulleted
    # list that follows on the notes page. The list is carried across so the
    # entry reads as a whole; it cannot sit inside the <p>.
    dlist = ""
    if s.get("definitionListHtml"):
        dlist = ('\n                  <div class="gl-def-list">'
                 + render_inline_maths(s["definitionListHtml"], inline_map)
                 + "</div>")
    groups = sorted({x["group"] for x in term["sources"] if x["board"] == board})
    others = [x for x in term["sources"]
              if x["board"] == board and x is not s]
    also = ""
    if others:
        links = ", ".join(
            f'<a href="{x["notesUrl"]}">{e(x["spec"])}</a>' for x in others)
        also = (f'\n                <p class="gl-also">Also covered in '
                f"{links}</p>")
    return f"""              <div
                class="gl-entry"
                id="{e(term['id'])}"
                data-term="{e(term['term'].lower())}"
                data-groups="{e(' '.join(groups))}"
                data-origin="{e(s.get('origin', 'notes'))}"
              >
                <dt class="gl-term">{e(term['term'])}</dt>
                <dd class="gl-def">
                  <p class="gl-text">{render_inline_maths(s['definitionHtml'], inline_map)}</p>{dlist}
                  <p class="gl-source">{source_link(s)}</p>{also}
                </dd>
              </div>"""


def formula_html(f, board, rendered, groups):
    srcs = [s for s in f["sources"] if s["board"] == board]
    s = srcs[0]
    slugs = sorted({x["group"] for x in srcs})
    return f"""            <div
              class="gl-formula"
              id="{e(f['id'])}"
              data-term="{e(f['label'].lower())}"
              data-groups="{e(' '.join(slugs))}"
            >
              <h3 class="gl-formula-name">{e(f['label'])}</h3>
              <!-- prettier-ignore -->
              <div class="gl-math">{rendered}</div>
              <p class="gl-source">
                <span class="gl-group">{e(groups[s['group']]['label'])}</span>
                <a href="{e(s['notesUrl'])}">{e(s['spec'])} {e(s['topic'])}</a>
              </p>
            </div>"""


def render_board(data, board, groups, rendered_map, inline_map):
    meta = BOARDS[board]
    terms = [t for t in data["terms"] if board in t["boards"]]
    formulae = [f for f in data["formulae"] if board in f["boards"]]
    # Sort on the canonical key so a leading article is ignored here too,
    # matching how letter_of() files them.
    terms.sort(key=lambda t: (t["key"], t["id"]))
    formulae.sort(key=lambda f: f["label"].lower())

    by_letter = {L: [t for t in terms if t["letter"] == L] for L in LETTERS}
    other = [t for t in terms if t["letter"] not in by_letter]

    # A-Z strip. Empty letters stay in place, disabled, so the strip does not
    # reflow between the two boards.
    az = []
    for L in LETTERS:
        if by_letter[L]:
            az.append(f'            <a href="#letter-{L.lower()}">{L}</a>')
        else:
            az.append(f'            <span aria-disabled="true">{L}</span>')
    az_html = "\n".join(az)

    board_groups = sorted(
        {g for t in terms for s in t["sources"] if s["board"] == board
         for g in [s["group"]]},
        key=lambda g: groups[g]["order"])
    options = "\n".join(
        f'                <option value="{e(g)}">{e(groups[g]["label"])}</option>'
        for g in board_groups)

    sections = []
    for L in LETTERS:
        if not by_letter[L]:
            continue
        entries = "\n".join(
                entry_html(t, board, inline_map) for t in by_letter[L])
        sections.append(f"""          <section class="gl-letter" id="letter-{L.lower()}">
            <h2 class="gl-letter-head">{L}</h2>
            <dl class="gl-list">
{entries}
            </dl>
          </section>""")
    if other:
        entries = "\n".join(entry_html(t, board, inline_map) for t in other)
        sections.append(f"""          <section class="gl-letter" id="letter-other">
            <h2 class="gl-letter-head">Other</h2>
            <dl class="gl-list">
{entries}
            </dl>
          </section>""")

    formula_block = ""
    if formulae:
        items = "\n".join(
            formula_html(f, board, rendered_map[f["latex"]], groups)
            for f in formulae)
        formula_block = f"""
          <section class="gl-formulae" id="formulae">
            <header class="major">
              <h2>Formulae</h2>
            </header>
            <p class="gl-formulae-intro">
              The {len(formulae)} formulae stated in the {e(meta['name'])} notes.
              Every one is rendered as it appears on its topic page.
            </p>
            <div class="gl-formula-grid">
{items}
            </div>
          </section>
"""

    other_board = "aqa" if board == "edexcel-a" else "edexcel-a"
    crumbs = [("Home", "/"), ("Revision Notes", "/revision-notes/index.html"),
              ("Glossary", "/revision-notes/glossary/"),
              (BOARDS[board]["name"], None)]

    body = f"""{breadcrumb_html(crumbs)}

          <header class="gl-hero">
            <h1>{e(meta['long'])} Glossary</h1>
            <p class="gl-intro">{meta['intro']}</p>
            <p class="gl-stats">
              <strong>{len(terms)}</strong> definitions and
              <strong>{len(formulae)}</strong> formulae.
              <a href="/revision-notes/glossary/{BOARDS[other_board]['slug']}/"
                >Switch to the {e(BOARDS[other_board]['name'])} glossary</a
              >
            </p>
          </header>

          <div class="gl-search" data-glossary-search>
            <form class="gl-controls" data-gl-controls hidden>
              <div class="gl-field">
                <label for="gl-query">Search this glossary</label>
                <input
                  type="search"
                  id="gl-query"
                  data-gl-query
                  placeholder="Try elasticity, or PED"
                  autocomplete="off"
                />
              </div>
              <div class="gl-field">
                <label for="gl-group">Filter by topic</label>
                <select id="gl-group" data-gl-filter>
                  <option value="">All topics</option>
{options}
                </select>
              </div>
              <button type="button" class="gl-clear" data-gl-clear>Clear</button>
            </form>
            <p class="gl-count" role="status" aria-live="polite" data-gl-count></p>

            <noscript>
              <p class="gl-noscript">
                Search needs JavaScript. The full glossary is below either way -
                use the A to Z, or your browser's find on this page.
              </p>
            </noscript>

            <nav class="gl-atoz" aria-label="Jump to a letter">
{az_html}
            </nav>

            <p class="gl-empty" data-gl-empty hidden>
              No entries match. Try a shorter search, or
              <button type="button" class="gl-clear-inline" data-gl-clear>
                clear the filters</button
              >.
            </p>
{formula_block}
{chr(10).join(sections)}
          </div>"""

    ld = json_ld({
        "@context": "https://schema.org",
        "@type": "DefinedTermSet",
        "@id": f"{SITE}/revision-notes/glossary/{meta['slug']}/#glossary",
        "name": f"{meta['long']} Glossary",
        "description": plain(meta["meta"]),
        "url": f"{SITE}/revision-notes/glossary/{meta['slug']}/",
        "inLanguage": "en-GB",
        "educationalLevel": "A-Level",
        "publisher": {"@type": "EducationalOrganization",
                      "name": "Economics Academy", "url": SITE},
        "hasDefinedTerm": [
            {
                "@type": "DefinedTerm",
                "@id": f"{SITE}/revision-notes/glossary/{meta['slug']}/#{t['id']}",
                "name": t["term"],
                "description": plain(source_for(t, board)["definitionHtml"]),
                "url": f"{SITE}/revision-notes/glossary/{meta['slug']}/#{t['id']}",
                "inDefinedTermSet":
                    f"{SITE}/revision-notes/glossary/{meta['slug']}/#glossary",
            }
            for t in terms
        ],
    })

    return page_shell(
        title=f"{meta['long']} Glossary — Key Terms & Formulae | Economics Academy",
        desc=meta["meta"],
        path=f"/revision-notes/glossary/{meta['slug']}/",
        crumbs=crumbs, body=body, jsonld=ld, katex_css=bool(formulae),
    )


# ---------------------------------------------------------------- landing

def render_landing(data):
    counts = {}
    for b in BOARDS:
        counts[b] = (
            sum(1 for t in data["terms"] if b in t["boards"]),
            sum(1 for f in data["formulae"] if b in f["boards"]),
        )
    crumbs = [("Home", "/"), ("Revision Notes", "/revision-notes/index.html"),
              ("Glossary", None)]

    cards = []
    for b, meta in BOARDS.items():
        n, nf = counts[b]
        cards.append(f"""            <div class="gl-card">
              <h2><a href="/revision-notes/glossary/{meta['slug']}/">{e(meta['long'])}</a></h2>
              <p class="gl-card-count">
                <strong>{n}</strong> definitions &middot; <strong>{nf}</strong> formulae
              </p>
              <p>{meta['intro']}</p>
              <a
                href="/revision-notes/glossary/{meta['slug']}/"
                class="button primary gl-card-button"
                >Open the {e(meta['name'])} glossary</a
              >
            </div>""")

    body = f"""{breadcrumb_html(crumbs)}

          <header class="gl-hero">
            <h1>A-Level Economics Glossary</h1>
            <p class="gl-intro">
              Every definition and formula you need, in one place. Pick your exam
              board - the two specifications share most of their vocabulary, but
              not all of it, and each glossary carries only what its own
              specification asks for.
            </p>
            <p class="gl-intro">
              Nothing here is written for the glossary. Every definition is taken
              word for word from the
              <a href="/revision-notes/index.html">revision notes</a> on this
              site, and links back to the topic page it came from.
            </p>
          </header>

          <div class="gl-cards">
{chr(10).join(cards)}
          </div>

          <section class="gl-more">
            <header class="major">
              <h2>While you are revising</h2>
            </header>
            <div class="gl-more-links">
              <a href="/practice-questions/index.html" class="button"
                >Practice Questions</a
              >
              <a href="/past-paper-questions/" class="button"
                >Search Past Paper Questions</a
              >
              <a href="/revision-notes/index.html" class="button"
                >Revision Notes</a
              >
            </div>
          </section>"""

    ld = json_ld({
        "@context": "https://schema.org",
        "@type": "CollectionPage",
        "name": "A-Level Economics Glossary",
        "description": LANDING_META,
        "url": f"{SITE}/revision-notes/glossary/",
        "inLanguage": "en-GB",
        "isPartOf": {"@type": "WebSite", "name": "Economics Academy", "url": SITE},
        "hasPart": [
            {"@type": "DefinedTermSet",
             "name": f"{m['long']} Glossary",
             "url": f"{SITE}/revision-notes/glossary/{m['slug']}/"}
            for m in BOARDS.values()
        ],
    })

    return page_shell(
        title="A-Level Economics Glossary — Key Terms & Formulae | Economics Academy",
        desc=LANDING_META,
        path="/revision-notes/glossary/",
        crumbs=crumbs, body=body, jsonld=ld,
    )


# ---------------------------------------------------------------- sitemap

SITEMAP_OPEN = "  <!-- Glossary -->"
SITEMAP_CLOSE = "  <!-- /Glossary -->"


def update_sitemap(paths):
    today = datetime.date.today().isoformat()
    lines = [SITEMAP_OPEN]
    for p in paths:
        priority = "0.8" if p.count("/") == 3 else "0.75"
        lines.append(f"  <url><loc>{SITE}{p}</loc><lastmod>{today}</lastmod>"
                     f"<priority>{priority}</priority></url>")
    lines.append(SITEMAP_CLOSE)
    block = "\n".join(lines)

    text = SITEMAP.read_text(encoding="utf-8")
    if SITEMAP_OPEN in text and SITEMAP_CLOSE in text:
        start = text.index(SITEMAP_OPEN)
        end = text.index(SITEMAP_CLOSE) + len(SITEMAP_CLOSE)
        new = text[:start] + block + text[end:]
    else:
        i = text.rindex("</urlset>")
        new = text[:i] + block + "\n\n" + text[i:]
    if new == text:
        return False
    SITEMAP.write_text(new, encoding="utf-8")
    return True


def prettify(paths):
    """Run the repo's Prettier over the generated HTML.

    Prettier is not installed here; the repo convention is `npx prettier@3.9.6`.
    The generator calls it so that generating and formatting are one step and
    re-running is idempotent - otherwise every run would undo the formatting and
    the files would churn in `git diff` forever.
    """
    try:
        subprocess.run(
            ["npx", "--yes", "prettier@3.9.6", "--write", "--log-level", "warn"]
            + [str(p) for p in paths],
            check=True, cwd=ROOT, capture_output=True,
        )
        return True
    except (OSError, subprocess.CalledProcessError):
        return False


# ---------------------------------------------------------------- main

def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--check", action="store_true",
                    help="validate and report, write nothing")
    args = ap.parse_args()

    data = json.loads(DATA.read_text(encoding="utf-8"))
    tax = json.loads(TAXONOMY.read_text(encoding="utf-8"))
    groups, order = {}, 0
    for b in tax["boards"]:
        for g in b["groups"]:
            groups[g["slug"]] = {"label": g["label"], "name": g["name"],
                                 "order": order}
            order += 1

    errs = validate(data, groups)
    if errs:
        print(f"{len(errs)} problem(s), nothing written:", file=sys.stderr)
        for x in errs:
            print(f"  - {x}", file=sys.stderr)
        return 1

    try:
        latex = [f["latex"] for f in data["formulae"]]
        rendered_map = dict(zip(latex, katex(latex)))
        inline = sorted({
            html.unescape(m).strip()
            for t in data["terms"] for s in t["sources"]
            for m in INLINE_TEX.findall(s["definitionHtml"])
        })
        inline_map = dict(zip(inline, _katex(inline, False)))
    except BuildError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    pages = {OUT_DIR / "index.html": render_landing(data)}
    for board in BOARDS:
        pages[OUT_DIR / BOARDS[board]["slug"] / "index.html"] = \
            render_board(data, board, groups, rendered_map, inline_map)

    for path, source in pages.items():
        leftover = re.search(r"\\\(|\\\[", source)
        if leftover:
            i = leftover.start()
            print(f"error: {path.name} still contains raw LaTeX at "
                  f"{source[i:i + 60]!r} - it was not pre-rendered",
                  file=sys.stderr)
            return 1

    for b in BOARDS:
        n = sum(1 for t in data["terms"] if b in t["boards"])
        nf = sum(1 for f in data["formulae"] if b in f["boards"])
        print(f"  {BOARDS[b]['name']:12} {n:4} definitions  {nf:3} formulae")

    if args.check:
        print("\n--check: nothing written")
        return 0

    for path, source in pages.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(source, encoding="utf-8")
        print(f"  wrote {path.relative_to(ROOT)}")

    urls = ["/revision-notes/glossary/"] + [
        f"/revision-notes/glossary/{BOARDS[b]['slug']}/" for b in BOARDS]
    print("  sitemap " + ("updated" if update_sitemap(urls) else "already current"))
    if not prettify(list(pages)):
        print("  WARNING: prettier unavailable, formatting differs from the repo")
    return 0


if __name__ == "__main__":
    sys.exit(main())

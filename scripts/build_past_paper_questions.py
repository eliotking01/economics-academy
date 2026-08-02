#!/usr/bin/env python3
"""Build the past-paper question bank's client-side search index.

Joins the three data sources into the single JSON file the search component
fetches:

    past-paper-questions-data/edexcel-a/*.json   machine-extracted questions
    past-paper-questions-data/tags.json          hand-written topics + keywords
    past-paper-questions-data/taxonomy.json      themes, units, topics

    -> past-paper-questions/questions.json

Run:  python3 scripts/build_past_paper_questions.py [--check]

--check validates and reports without writing.

In Phase 3 this script also grows the theme and topic page generation. For now
it produces the index and reports which topics clear the volume gate.

Standard library only, in keeping with the rest of scripts/.
"""

import argparse
import collections
import datetime
import html
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = ROOT / "past-paper-questions-data"
PAGE_DIR = ROOT / "past-paper-questions"
OUT = PAGE_DIR / "questions.json"
INDEX = PAGE_DIR / "index.html"

SITE = "https://economicsacademy.co.uk"
GTAG = "G-YVCNRW4QH6"

# A topic earns its own generated page at this many questions. Re-evaluated on
# every run, so topics rise above the gate as the bank grows and pages appear
# without anyone having to remember to add them.
GATE = 4


def load():
    taxonomy = json.loads((DATA / "taxonomy.json").read_text(encoding="utf-8"))
    tags = json.loads((DATA / "tags.json").read_text(encoding="utf-8"))
    tags.pop("_comment", None)

    papers = []
    for path in sorted((DATA / "edexcel-a").glob("*.json")):
        papers.append(json.loads(path.read_text(encoding="utf-8")))
    return taxonomy, tags, papers


def topic_lookup(taxonomy):
    """slug -> everything the UI needs to render a topic chip or link."""
    out = {}
    for theme in taxonomy["themes"]:
        for unit in theme["units"]:
            for t in unit["topics"]:
                out[t["slug"]] = {
                    "spec": t["spec"],
                    "title": t["title"],
                    "shortTitle": t["shortTitle"],
                    "theme": theme["theme"],
                    "themeName": theme["name"],
                    "unit": unit["unit"],
                    "unitName": unit["name"],
                    "notesUrl": t["notesUrl"],
                }
    return out


def build(taxonomy, tags, papers):
    topics = topic_lookup(taxonomy)
    errors = []
    questions = []

    # Papers are held once in their own table and referenced by index. Inlining
    # them would repeat two ~110-character PDF URLs on every question, which is
    # most of the payload for a file the browser fetches before it can search.
    paper_table = [
        {
            "paper": p["paper"],
            "paperName": p["paperName"],
            "year": p["year"],
            "series": p["series"],
            "seriesSlug": p["seriesSlug"],
            "board": p["boardName"],
            "qualification": p["qualification"],
            "questionPaperUrl": p["questionPaperUrl"],
            "markSchemeUrl": p["markSchemeUrl"],
        }
        for p in papers
    ]
    paper_index = {
        (p["paper"], p["seriesSlug"]): i for i, p in enumerate(paper_table)
    }

    for paper in papers:
        pi = paper_index[(paper["paper"], paper["seriesSlug"])]
        for q in paper["questions"]:
            tag = tags.get(q["id"])
            if tag is None:
                errors.append(f"{q['id']}: no tags entry")
                continue

            slugs = tag["topics"]
            for slug in slugs:
                if slug not in topics:
                    errors.append(f"{q['id']}: unknown topic slug {slug!r}")

            themes = sorted({topics[s]["theme"] for s in slugs if s in topics})

            if q["markScheme"] is None:
                errors.append(f"{q['id']}: no mark scheme recorded")
                continue

            entry = {
                "id": q["id"],
                "p": pi,
                "section": q["section"],
                "questionNumber": q["questionNumber"],
                "parentQuestion": q["parentQuestion"],
                "choiceGroup": q["choiceGroup"],
                "marks": q["marks"],
                "questionText": q["questionText"],
                "topics": slugs,
                "themes": themes,
                "keywords": tag["keywords"],
                "qpPage": q["questionPaper"]["page"],
                "msPage": q["markScheme"]["page"],
                # Page where this question's extract block starts, for the
                # "View the extract" link. Null for Section C, which has none.
                "ctxPage": q["context"]["page"] if q["context"] else None,
                "modelAnswer": q["modelAnswer"],
            }
            questions.append(entry)

    # Newest first, then paper, then question number: the order a student most
    # often wants, and the order the page shows before any sort is chosen.
    questions.sort(
        key=lambda q: (
            -paper_table[q["p"]]["year"],
            paper_table[q["p"]]["seriesSlug"],
            paper_table[q["p"]]["paper"],
            q["questionNumber"],
        )
    )

    counts = collections.Counter(s for q in questions for s in q["topics"])
    gated = sorted(s for s, n in counts.items() if n >= GATE)

    index = {
        "generated": datetime.date.today().isoformat(),
        "count": len(questions),
        "gate": GATE,
        "qualification": "A Level Economics A (9EC0)",
        "themes": [
            {
                "theme": t["theme"],
                "slug": t["slug"],
                "name": t["name"],
                "fullName": t["fullName"],
            }
            for t in taxonomy["themes"]
        ],
        "papers": paper_table,
        # hasPage is "a page exists on disk", not "a page is warranted". Nothing
        # links to a topic page until it has actually been generated, so the
        # master page can never ship a link to a Phase 3 page that is not there
        # yet. Phase 3 generates the pages before rebuilding this index, which
        # flips these to true without any flag to remember.
        "topics": {
            slug: dict(
                meta,
                count=counts.get(slug, 0),
                gated=slug in gated,
                hasPage=(PAGE_DIR / slug / "index.html").is_file(),
            )
            for slug, meta in topics.items()
            if counts.get(slug, 0) > 0
        },
        "questions": questions,
    }
    return index, counts, gated, errors


# ---------------------------------------------------------------- master page

TITLE = "Edexcel A-Level Economics Past Paper Questions | Economics Academy"
DESC = (
    "Search every Edexcel A-Level Economics (9EC0) Section B and Section C past "
    "paper question from 2017 to 2024. Filter by topic, paper, year and marks, "
    "with a direct link to the right page of each mark scheme."
)


def e(s):
    return html.escape(str(s), quote=True)


def search_component(prefilter=""):
    """The search UI skeleton.

    Rendered identically here and on every Phase 3 topic page; only
    data-prefilter-topic differs. The controls ship hidden and are revealed by
    js/components/question-search.js, so a reader without JavaScript is never
    shown a search box that cannot work.
    """
    attr = ' data-prefilter-topic="' + e(prefilter) + '"' if prefilter else ""
    fields = [
        ("paper", "Paper", "All papers"),
        ("theme", "Theme", "All themes"),
        ("topic", "Topic", "All topics"),
        ("marks", "Marks", "All marks"),
        ("year", "Year", "All years"),
        ("section", "Section", "All sections"),
    ]
    field_html = "\n".join(
        f"""              <div class="ppq-field">
                <label for="ppq-{k}">{lbl}</label>
                <select id="ppq-{k}" data-ppq-filter="{k}" data-ppq-all="{all_}"></select>
              </div>"""
        for k, lbl, all_ in fields
    )

    return f"""          <div class="ppq-search" data-question-search{attr}>
            <form class="ppq-controls" data-ppq-controls hidden>
              <div class="ppq-search-field">
                <label class="sr-only" for="ppq-query">Search past paper questions</label>
                <input
                  type="search"
                  id="ppq-query"
                  class="ppq-search-input"
                  data-ppq-query
                  placeholder="Search questions, topics or keywords&hellip;"
                  autocomplete="off"
                  spellcheck="false"
                />
              </div>
              <div class="ppq-fields">
{field_html}
                <div class="ppq-field">
                  <label for="ppq-sort">Sort</label>
                  <select id="ppq-sort" data-ppq-sort>
                    <option value="relevance">Relevance</option>
                    <option value="newest">Newest first</option>
                    <option value="marks">Marks (high to low)</option>
                  </select>
                </div>
                <button type="button" class="ppq-clear" data-ppq-clear>Clear all</button>
              </div>
            </form>

            <p class="ppq-error" data-ppq-error hidden>
              The question search could not load. Every question is still listed
              by topic below, and all the mark scheme links work.
            </p>

            <div class="ppq-status">
              <p class="ppq-count" data-ppq-count role="status" aria-live="polite"></p>
            </div>

            <div class="ppq-results" data-ppq-results></div>

            <div class="ppq-empty" data-ppq-empty hidden>
              <p><strong>No questions match that search.</strong></p>
              <p>
                Try a broader term &mdash; for example
                <em>monopoly</em>, <em>inflation</em>, <em>exchange rates</em>,
                <em>externalities</em> or <em>25 marks</em>.
              </p>
            </div>

            <button type="button" class="button ppq-more" data-ppq-more hidden>
              Show more
            </button>
          </div>"""


def topic_directory(index):
    """The crawlable fallback: every topic that has questions, grouped by theme.

    This is what a crawler and a no-JS reader see, since the results list above
    it is rendered by script on this page.
    """
    topics = index["topics"]
    blocks = []
    for theme in index["themes"]:
        rows = sorted(
            (s for s, t in topics.items() if t["theme"] == theme["theme"]),
            key=lambda s: [int(p) for p in topics[s]["spec"].split(".")],
        )
        if not rows:
            continue
        items = []
        for slug in rows:
            t = topics[slug]
            label = e(t["spec"] + " " + t["shortTitle"])
            n = t["count"]
            count = f'<span class="ppq-topic-count">{n} question{"" if n == 1 else "s"}</span>'
            if t["hasPage"]:
                link = f'<a href="/past-paper-questions/{e(slug)}/">{label}</a>'
            else:
                link = label
            items.append(f"                <li>{link} {count}</li>")
        blocks.append(
            "            <div class=\"ppq-theme-block\">\n"
            f'              <h3>Theme {theme["theme"]}: {e(theme["name"])}</h3>\n'
            '              <ul class="ppq-topic-list">\n'
            + "\n".join(items)
            + "\n              </ul>\n"
            "            </div>"
        )
    return "\n".join(blocks)


def render_index(index):
    url = f"{SITE}/past-paper-questions/"
    years = sorted({p["year"] for p in index["papers"]})
    n_topics = len(index["topics"])
    meta = (
        f'{index["count"]} questions &middot; {years[0]}&ndash;{years[-1]} '
        f"&middot; {n_topics} topics &middot; free, no sign-up"
    )

    ld_collection = json.dumps(
        {
            "@context": "https://schema.org",
            "@type": "CollectionPage",
            "name": "Edexcel A-Level Economics past paper questions",
            "description": DESC,
            "url": url,
            "inLanguage": "en-GB",
            "isPartOf": {
                "@type": "WebSite",
                "name": "Economics Academy",
                "url": SITE,
            },
        },
        indent=2,
    )
    ld_crumbs = json.dumps(
        {
            "@context": "https://schema.org",
            "@type": "BreadcrumbList",
            "itemListElement": [
                {
                    "@type": "ListItem",
                    "position": 1,
                    "name": "Home",
                    "item": f"{SITE}/",
                },
                {
                    "@type": "ListItem",
                    "position": 2,
                    "name": "Past Paper Questions",
                },
            ],
        },
        indent=2,
    )
    ld_collection = "\n".join("      " + l for l in ld_collection.split("\n")).strip()
    ld_crumbs = "\n".join("      " + l for l in ld_crumbs.split("\n")).strip()

    # Only promise topic pages once they exist, so this copy stays true whether
    # or not Phase 3 has run.
    linked = sum(1 for t in index["topics"].values() if t["hasPage"])
    if linked:
        directory_note = (
            "Questions are tagged against the Edexcel specification. Topics with "
            "their own page are linked; the rest are searchable above."
        )
    else:
        directory_note = (
            "Questions are tagged against the Edexcel specification. Use the "
            "search above to filter to any topic listed here."
        )

    return f"""<!doctype html>
<html lang="en-GB">
  <head>
    <!-- Google tag (gtag.js) -->
    <script async src="https://www.googletagmanager.com/gtag/js?id={GTAG}"></script>
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
    <title>{e(TITLE)}</title>
    <meta name="description" content="{e(DESC)}" />

    <link rel="canonical" href="{url}" />
    <meta property="og:type" content="website" />
    <meta property="og:site_name" content="Economics Academy" />
    <meta property="og:locale" content="en_GB" />
    <meta property="og:url" content="{url}" />
    <meta property="og:title" content="{e(TITLE)}" />
    <meta property="og:description" content="{e(DESC)}" />
    <meta property="og:image" content="{SITE}/og-image.png?v=1" />
    <meta property="og:image:width" content="1200" />
    <meta property="og:image:height" content="1200" />
    <meta property="og:image:type" content="image/png" />
    <meta property="og:image:alt" content="Economics Academy logo" />
    <meta name="twitter:card" content="summary_large_image" />
    <meta name="twitter:title" content="{e(TITLE)}" />
    <meta name="twitter:description" content="{e(DESC)}" />
    <meta name="twitter:image" content="{SITE}/og-image.png?v=1" />
    <script type="application/ld+json">
      {ld_collection}
    </script>
    <script type="application/ld+json">
      {ld_crumbs}
    </script>
    <link rel="icon" href="/favicon.ico" sizes="any" />
    <link rel="apple-touch-icon" href="/apple-touch-icon.png" />
    <link rel="manifest" href="/site.webmanifest" />
    <link rel="stylesheet" href="/css/main.css" />
    <link rel="stylesheet" href="/css/pages/past-paper-questions.css" />
  </head>
  <body class="is-preload">
    <div id="page-wrapper">
      <!-- Header -->
      <div id="header-placeholder"></div>

      <section id="main" class="past-paper-questions-page">
        <div class="container">
          <nav class="breadcrumb" aria-label="Breadcrumb">
            <a href="/index.html">Home</a>
            <span class="separator">&rsaquo;</span>
            <span>Past Paper Questions</span>
          </nav>

          <section class="ppq-hero">
            <h1 class="ppq-h1">Edexcel A-Level Economics Past Paper Questions</h1>
            <p class="ppq-intro">
              Every Section B and Section C question from the
              <strong>Edexcel A-Level Economics A (9EC0)</strong> papers, {years[0]}
              to {years[-1]}, in one searchable place. Filter by topic, paper, year
              or mark tariff, and open the official mark scheme at the right page.
            </p>
            <p class="ppq-hero-meta">{meta}</p>
          </section>

{search_component()}

          <noscript>
            <p>
              The search above needs JavaScript. Every topic is listed below, and
              all the question papers and mark schemes are available from the
              <a href="/past-papers/edexcel/index.html">Edexcel past papers</a>
              page.
            </p>
          </noscript>

          <header class="major">
            <h2>Browse by topic</h2>
          </header>
          <p>{directory_note}</p>

{topic_directory(index)}

          <section class="ppq-cta">
            <h2>Practising past papers is only half of it</h2>
            <p>
              <strong>Past papers show you the question &mdash; feedback shows you the
              marks.</strong> Send an essay for examiner-style marking, or work
              through the topics you keep losing marks on with a specialist tutor.
            </p>
            <div class="ppq-cta-actions">
              <a href="/revision-notes/index.html" class="button alt">Free Revision Notes</a>
              <a href="/marking.html" class="button alt">Get Your Essays Marked</a>
              <a href="/tutoring.html" class="button">Book a Free Intro Call</a>
            </div>
          </section>
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
    <script src="/js/components/question-search.js" defer></script>
  </body>
</html>
"""


def prettify(paths):
    """Run the repo's Prettier over generated HTML.

    Prettier is not installed here; the repo convention is `npx prettier@3.9.6`.
    The generator calls it so that generating and formatting are one step and
    re-running the generator is idempotent. Without this, every run would undo
    the formatting and the file would churn in `git diff` forever.

    If npx is unavailable or offline, the page is still valid HTML - it is just
    formatted differently from the rest of the repo, and the caller is told.
    """
    import subprocess

    try:
        subprocess.run(
            ["npx", "--yes", "prettier@3.9.6", "--write", "--log-level", "warn"]
            + [str(p) for p in paths],
            check=True,
            cwd=ROOT,
            capture_output=True,
        )
        return True
    except (OSError, subprocess.CalledProcessError):
        return False


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="validate, write nothing")
    args = ap.parse_args()

    taxonomy, tags, papers = load()
    index, counts, gated, errors = build(taxonomy, tags, papers)

    if errors:
        for e in errors:
            print(f"ERROR {e}", file=sys.stderr)
        sys.exit(1)

    years = sorted({p["year"] for p in index["papers"]})
    marks = sorted({q["marks"] for q in index["questions"]})
    print(f"{index['count']} questions from {len(papers)} papers")
    print(f"  years  {years[0]}-{years[-1]}")
    print(f"  marks  {', '.join(str(m) for m in marks)}")
    print(f"  topics {len(counts)} with questions, {len(gated)} at or above the "
          f"gate of {GATE}")

    if args.check:
        print("check only - nothing written")
        return

    OUT.parent.mkdir(parents=True, exist_ok=True)
    # Minified: this is a build artefact the browser fetches before it can
    # search, not a file anyone reads or edits. Re-run the script to inspect it.
    OUT.write_text(
        json.dumps(index, ensure_ascii=False, separators=(",", ":")) + "\n",
        encoding="utf-8",
    )
    size = OUT.stat().st_size
    print(f"wrote {OUT.relative_to(ROOT)} ({size / 1024:.0f} KB)")

    INDEX.write_text(render_index(index), encoding="utf-8")
    if prettify([INDEX]):
        print(f"wrote {INDEX.relative_to(ROOT)} (formatted)")
    else:
        print(
            f"wrote {INDEX.relative_to(ROOT)} "
            "(WARNING: prettier unavailable, formatting differs from the repo)"
        )


if __name__ == "__main__":
    main()

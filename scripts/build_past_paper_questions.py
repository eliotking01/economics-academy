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
                    "questionsUrl": t["questionsUrl"],
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
                "notesDir": t["notesDir"],
                "notesIndexUrl": t["notesIndexUrl"],
            }
            for t in taxonomy["themes"]
        ],
        "papers": paper_table,
        # hasPage and gated are the same thing now that this script generates
        # the topic pages in the same run that writes this index. They are kept
        # as separate fields because the UI asks "can I link there?" while the
        # report asks "does this topic clear the gate?", and a future change
        # could make those differ again.
        "topics": {
            slug: dict(
                meta,
                count=counts.get(slug, 0),
                gated=slug in gated,
                hasPage=slug in gated,
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


def search_component(topic="", theme=0):
    """The search UI skeleton.

    Rendered identically on the master page, the theme pages and the topic
    pages; only the pre-filter attribute differs. The controls ship hidden and
    are revealed by js/components/question-search.js, so a reader without
    JavaScript is never shown a search box that cannot work.
    """
    attr = ""
    if topic:
        attr = ' data-prefilter-topic="' + e(topic) + '"'
    elif theme:
        attr = ' data-prefilter-theme="' + e(theme) + '"'
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


def render_card(q, index):
    """Server-rendered question card.

    Must stay markup-identical to cardHtml() in js/components/question-search.js.
    Topic and theme pages ship their questions as real HTML so crawlers and
    readers without JavaScript get the content; the component then re-renders
    the same list from JSON. If the two drifted, enabling JavaScript would
    silently change the page. scripts/test_question_search.js compares the two
    renderers over all 112 questions and fails if they diverge.
    """
    paper = index["papers"][q["p"]]
    topics = index["topics"]

    badges = [
        f'<span class="ppq-badge ppq-badge-paper">Paper {paper["paper"]}</span>',
        f'<span class="ppq-badge">{e(paper["series"] + " " + str(paper["year"]))}</span>',
        f'<span class="ppq-badge ppq-badge-marks">{q["marks"]} marks</span>',
    ]
    for n in q["themes"]:
        badges.append(f'<span class="ppq-badge ppq-badge-theme">Theme {n}</span>')

    links = []
    for slug in q["topics"]:
        t = topics.get(slug)
        if not t:
            continue
        label = e(t["spec"] + " " + t["shortTitle"])
        if t["hasPage"]:
            links.append(f'<a href="/past-paper-questions/{e(slug)}/">{label}</a>')
        else:
            links.append(f"<span>{label}</span>")
    topic_links = " &middot; ".join(links)

    # Question paper first: a student who wants to attempt this under exam
    # conditions needs the question as it was printed, before anything else.
    qp_url = e(paper["questionPaperUrl"] + "#page=" + str(q["qpPage"]))
    actions = [
        f'<a class="ppq-action" href="{qp_url}" target="_blank" '
        f'rel="noopener noreferrer">Question paper &mdash; p.{q["qpPage"]}</a>'
    ]
    if q["ctxPage"]:
        ctx = e(paper["questionPaperUrl"] + "#page=" + str(q["ctxPage"]))
        actions.append(
            f'<a class="ppq-action" href="{ctx}" target="_blank" '
            f'rel="noopener noreferrer">View the extract &mdash; p.{q["ctxPage"]}</a>'
        )
    ms = e(paper["markSchemeUrl"] + "#page=" + str(q["msPage"]))
    actions.append(
        f'<a class="ppq-action" href="{ms}" target="_blank" '
        f'rel="noopener noreferrer">Mark scheme &mdash; p.{q["msPage"]}</a>'
    )
    first = topics.get(q["topics"][0]) if q["topics"] else None
    if first:
        actions.append(
            f'<a class="ppq-action" href="{e(first["notesUrl"])}">'
            f'Revision notes: {e(first["spec"])}</a>'
        )
    if q["modelAnswer"]:
        actions.append(
            f'<a class="ppq-action ppq-action-model" href="{e(q["modelAnswer"])}">'
            "Model answer</a>"
        )

    choice = ""
    if q["choiceGroup"]:
        choice = (
            f'<p class="ppq-choice">One of two options in Section {e(q["section"])} '
            "&mdash; candidates answered this <em>or</em> the other.</p>"
        )

    return (
        f'<article class="ppq-card" id="{e(q["id"])}">'
        f'<div class="ppq-badges">{"".join(badges)}</div>'
        f'<p class="ppq-question">{e(q["questionText"])}</p>'
        f"{choice}"
        + (f'<p class="ppq-topics">{topic_links}</p>' if topic_links else "")
        + f'<div class="ppq-actions">{"".join(actions)}</div>'
        "</article>"
    )


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


def json_ld(obj):
    """JSON-LD indented to sit inside the page's <script> block."""
    s = json.dumps(obj, indent=2)
    return "\n".join("      " + line for line in s.split("\n")).strip()


def visible_href(path):
    """The site writes the home link as /index.html but canonicalises it as /."""
    return "/index.html" if path == "/" else path


def breadcrumb_html(crumbs):
    sep = '\n            <span class="separator">&rsaquo;</span>\n            '
    parts = []
    for name, path in crumbs:
        if path:
            parts.append(f'<a href="{e(visible_href(path))}">{e(name)}</a>')
        else:
            parts.append(f"<span>{e(name)}</span>")
    return sep.join(parts)


def breadcrumb_ld(crumbs):
    items = []
    for i, (name, path) in enumerate(crumbs, start=1):
        item = {"@type": "ListItem", "position": i, "name": name}
        if path:
            item["item"] = SITE + path
        items.append(item)
    return json_ld(
        {
            "@context": "https://schema.org",
            "@type": "BreadcrumbList",
            "itemListElement": items,
        }
    )


def page_shell(title, desc, path, crumbs, body):
    """The head and body boilerplate every page in this section shares.

    Structured data is CollectionPage plus BreadcrumbList, matching the rest of
    the site. Deliberately NOT schema.org Quiz/Question: that markup expects an
    acceptedAnswer or suggestedAnswer, and this bank does not host answers by
    design - it links to Pearson's mark schemes. Declaring Question without an
    answer earns no rich result and misrepresents the page.
    """
    url = SITE + path
    collection = json_ld(
        {
            "@context": "https://schema.org",
            "@type": "CollectionPage",
            "name": title.split(" | ")[0],
            "description": desc,
            "url": url,
            "inLanguage": "en-GB",
            "isPartOf": {
                "@type": "WebSite",
                "name": "Economics Academy",
                "url": SITE,
            },
        }
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
    <title>{e(title)}</title>
    <meta name="description" content="{e(desc)}" />

    <link rel="canonical" href="{url}" />
    <meta property="og:type" content="website" />
    <meta property="og:site_name" content="Economics Academy" />
    <meta property="og:locale" content="en_GB" />
    <meta property="og:url" content="{url}" />
    <meta property="og:title" content="{e(title)}" />
    <meta property="og:description" content="{e(desc)}" />
    <meta property="og:image" content="{SITE}/og-image.png?v=1" />
    <meta property="og:image:width" content="1200" />
    <meta property="og:image:height" content="1200" />
    <meta property="og:image:type" content="image/png" />
    <meta property="og:image:alt" content="Economics Academy logo" />
    <meta name="twitter:card" content="summary_large_image" />
    <meta name="twitter:title" content="{e(title)}" />
    <meta name="twitter:description" content="{e(desc)}" />
    <meta name="twitter:image" content="{SITE}/og-image.png?v=1" />
    <script type="application/ld+json">
      {collection}
    </script>
    <script type="application/ld+json">
      {breadcrumb_ld(crumbs)}
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
            {breadcrumb_html(crumbs)}
          </nav>

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
    <script src="/js/components/question-search.js" defer></script>
  </body>
</html>
"""


CTA = """          <section class="ppq-cta">
            <h2>Practising past papers is only half of it</h2>
            <p>
              <strong
                >Past papers show you the question &mdash; feedback shows you the
                marks.</strong
              >
              Send an essay for examiner-style marking, or work through the
              topics you keep losing marks on with a specialist tutor.
            </p>
            <div class="ppq-cta-actions">
              <a href="/revision-notes/index.html" class="button alt">Free Revision Notes</a>
              <a href="/marking.html" class="button alt">Get Your Essays Marked</a>
              <a href="/tutoring.html" class="button">Book a Free Intro Call</a>
            </div>
          </section>"""


def question_count_phrase(n):
    return "1 question" if n == 1 else f"{n} questions"


def year_span(index, questions):
    years = sorted({index["papers"][q["p"]]["year"] for q in questions})
    if not years:
        return ""
    return str(years[0]) if years[0] == years[-1] else f"{years[0]}&ndash;{years[-1]}"


def static_cards(index, questions):
    """Questions as real HTML, so the page is complete before any script runs."""
    return "\n".join("            " + render_card(q, index) for q in questions)


# ---------------------------------------------------------------- master page


def theme_links(index):
    rows = []
    for theme in index["themes"]:
        n = sum(1 for q in index["questions"] if theme["theme"] in q["themes"])
        if not n:
            continue
        rows.append(
            f'                <li><a href="/past-paper-questions/{theme["slug"]}/">'
            f'Theme {theme["theme"]}: {e(theme["name"])}</a> '
            f'<span class="ppq-topic-count">{question_count_phrase(n)}</span></li>'
        )
    return "\n".join(rows)


def render_index(index):
    years = sorted({p["year"] for p in index["papers"]})
    meta = (
        f'{index["count"]} questions &middot; {years[0]}&ndash;{years[-1]} '
        f'&middot; {len(index["topics"])} topics &middot; free, no sign-up'
    )
    linked = sum(1 for t in index["topics"].values() if t["hasPage"])
    if linked:
        note = (
            "Questions are tagged against the Edexcel specification. Topics with "
            "their own page are linked; the rest are searchable above."
        )
    else:
        note = (
            "Questions are tagged against the Edexcel specification. Use the "
            "search above to filter to any topic listed here."
        )

    body = f"""          <section class="ppq-hero">
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
            <h2>Browse by theme</h2>
          </header>
          <div class="ppq-theme-block">
            <ul class="ppq-topic-list">
{theme_links(index)}
            </ul>
          </div>

          <header class="major">
            <h2>Browse by topic</h2>
          </header>
          <p>{note}</p>

{topic_directory(index)}

{CTA}"""

    return page_shell(
        TITLE,
        DESC,
        "/past-paper-questions/",
        [("Home", "/"), ("Past Paper Questions", None)],
        body,
    )


# ---------------------------------------------------------------- theme pages


def render_theme_page(index, theme):
    questions = [q for q in index["questions"] if theme["theme"] in q["themes"]]
    path = f'/past-paper-questions/{theme["slug"]}/'
    span = year_span(index, questions)
    n = len(questions)

    title = (
        f'Theme {theme["theme"]} Past Paper Questions '
        f"&mdash; Edexcel A-Level Economics | Economics Academy"
    )
    title = html.unescape(title)
    desc = (
        f'{n} Edexcel A-Level Economics past paper questions on Theme '
        f'{theme["theme"]}: {theme["name"]}, from {span.replace("&ndash;", " to ")}. '
        "Each links straight to the right page of the official mark scheme."
    )

    topics_in_theme = sorted(
        (s for s, t in index["topics"].items() if t["theme"] == theme["theme"]),
        key=lambda s: [int(p) for p in index["topics"][s]["spec"].split(".")],
    )
    rows = []
    for slug in topics_in_theme:
        t = index["topics"][slug]
        label = e(t["spec"] + " " + t["shortTitle"])
        link = (
            f'<a href="/past-paper-questions/{e(slug)}/">{label}</a>'
            if t["hasPage"]
            else label
        )
        rows.append(
            f'                <li>{link} <span class="ppq-topic-count">'
            f'{question_count_phrase(t["count"])}</span></li>'
        )

    body = f"""          <section class="ppq-hero">
            <h1 class="ppq-h1">
              Theme {theme["theme"]}: {e(theme["name"])} &mdash; Past Paper Questions
            </h1>
            <p class="ppq-intro">
              {question_count_phrase(n)} from the Edexcel A-Level Economics A
              (9EC0) papers, {span}, covering Theme {theme["theme"]}. Every
              question links to the official mark scheme at the page its answer
              begins on.
            </p>
            <p class="ppq-hero-meta">
              <a href="/revision-notes/{e(theme["notesDir"])}/index.html"
                >Theme {theme["theme"]} revision notes</a
              >
              &middot;
              <a href="/past-paper-questions/">All past paper questions</a>
            </p>
          </section>

{search_component(theme=theme["theme"])}

          <header class="major">
            <h2>Topics in Theme {theme["theme"]}</h2>
          </header>
          <div class="ppq-theme-block">
            <ul class="ppq-topic-list">
{chr(10).join(rows)}
            </ul>
          </div>

{CTA}"""

    # The component replaces the results container, so the static cards live
    # inside it and are what a crawler or a reader without JavaScript sees.
    body = body.replace(
        '<div class="ppq-results" data-ppq-results></div>',
        '<div class="ppq-results" data-ppq-results>\n'
        + static_cards(index, questions)
        + "\n          </div>",
    )

    crumbs = [
        ("Home", "/"),
        ("Past Paper Questions", "/past-paper-questions/"),
        (f'Theme {theme["theme"]}', None),
    ]
    return path, page_shell(title, desc, path, crumbs, body)


# ---------------------------------------------------------------- topic pages


def related_topics(index, slug):
    """Same unit first, then the rest of the theme. Only pages that exist."""
    me = index["topics"][slug]
    same_unit = []
    same_theme = []
    for other, t in index["topics"].items():
        if other == slug or not t["hasPage"]:
            continue
        if t["theme"] != me["theme"]:
            continue
        (same_unit if t["unit"] == me["unit"] else same_theme).append(other)

    key = lambda s: [int(p) for p in index["topics"][s]["spec"].split(".")]
    ordered = sorted(same_unit, key=key) + sorted(same_theme, key=key)
    return ordered[:6]


def render_topic_page(index, slug):
    t = index["topics"][slug]
    questions = [q for q in index["questions"] if slug in q["topics"]]
    path = f"/past-paper-questions/{slug}/"
    span = year_span(index, questions)
    n = len(questions)

    title = f'{t["title"]} Past Paper Questions &mdash; Edexcel A-Level Economics | Economics Academy'
    title = html.unescape(title)
    desc = (
        f'{n} Edexcel A-Level Economics past paper questions on {t["title"]} '
        f'(spec {t["spec"]}), {span.replace("&ndash;", " to ")}. Each links '
        "straight to the right page of the official mark scheme."
    )
    if len(desc) > 300:
        desc = desc[:297] + "..."

    related = related_topics(index, slug)
    related_html = ""
    if related:
        rows = "\n".join(
            f'                <li><a href="/past-paper-questions/{e(r)}/">'
            f'{e(index["topics"][r]["spec"] + " " + index["topics"][r]["shortTitle"])}</a> '
            f'<span class="ppq-topic-count">'
            f'{question_count_phrase(index["topics"][r]["count"])}</span></li>'
            for r in related
        )
        related_html = f"""
          <header class="major">
            <h2>Related topics</h2>
          </header>
          <div class="ppq-theme-block">
            <ul class="ppq-topic-list">
{rows}
            </ul>
          </div>
"""

    body = f"""          <section class="ppq-hero">
            <h1 class="ppq-h1">
              {e(t["title"])} &mdash; Past Paper Questions
            </h1>
            <p class="ppq-intro">
              {question_count_phrase(n)} on <strong>{e(t["title"])}</strong>
              (specification {e(t["spec"])}) from the Edexcel A-Level Economics A
              (9EC0) papers, {span}. Every question links to the official mark
              scheme at the page its answer begins on.
            </p>
            <p class="ppq-hero-meta">
              <a href="{e(t["notesUrl"])}">Revision notes: {e(t["spec"])} {e(t["shortTitle"])}</a>
              &middot;
              <a href="{e(t["questionsUrl"])}">Practice questions</a>
              &middot;
              <a href="/past-paper-questions/theme-{t["theme"]}/">Theme {t["theme"]}</a>
              &middot;
              <a href="/past-paper-questions/">All past paper questions</a>
            </p>
          </section>

{search_component(topic=slug)}
{related_html}
{CTA}"""

    body = body.replace(
        '<div class="ppq-results" data-ppq-results></div>',
        '<div class="ppq-results" data-ppq-results>\n'
        + static_cards(index, questions)
        + "\n          </div>",
    )

    crumbs = [
        ("Home", "/"),
        ("Past Paper Questions", "/past-paper-questions/"),
        (f'Theme {t["theme"]}', f'/past-paper-questions/theme-{t["theme"]}/'),
        (t["shortTitle"], None),
    ]
    return path, page_shell(title, desc, path, crumbs, body)


# ---------------------------------------------------------------- sitemap


SITEMAP_OPEN = "  <!-- Past Paper Questions -->"
SITEMAP_CLOSE = "  <!-- /Past Paper Questions -->"


def update_sitemap(index, paths):
    """Rewrite the section's block in sitemap.xml, between HTML comment markers.

    Same convention as the practice-questions block already in the file. The
    block is replaced wholesale, so removing a topic page removes its entry.
    Nothing outside the markers is touched.
    """
    sitemap = ROOT / "sitemap.xml"
    text = sitemap.read_text(encoding="utf-8")
    today = datetime.date.today().isoformat()

    lines = [SITEMAP_OPEN]
    for path in paths:
        if path == "/past-paper-questions/":
            priority = "0.8"
        elif "/theme-" in path:
            priority = "0.7"
        else:
            priority = "0.6"
        lines.append(
            f"  <url><loc>{SITE}{path}</loc><lastmod>{today}</lastmod>"
            f"<priority>{priority}</priority></url>"
        )
    lines.append(SITEMAP_CLOSE)
    block = "\n".join(lines)

    if SITEMAP_OPEN in text and SITEMAP_CLOSE in text:
        start = text.index(SITEMAP_OPEN)
        end = text.index(SITEMAP_CLOSE) + len(SITEMAP_CLOSE)
        new = text[:start] + block + text[end:]
    else:
        # First run: insert before </urlset> rather than guessing a position.
        marker = "</urlset>"
        idx = text.rindex(marker)
        new = text[:idx] + block + "\n" + text[idx:]

    if new != text:
        sitemap.write_text(new, encoding="utf-8")
        return True
    return False


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

    written = [INDEX]
    paths = ["/past-paper-questions/"]

    INDEX.write_text(render_index(index), encoding="utf-8")

    for theme in index["themes"]:
        if not any(theme["theme"] in q["themes"] for q in index["questions"]):
            continue
        path, page = render_theme_page(index, theme)
        dest = PAGE_DIR / theme["slug"] / "index.html"
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(page, encoding="utf-8")
        written.append(dest)
        paths.append(path)

    for slug in sorted(gated, key=lambda s: [int(p) for p in index["topics"][s]["spec"].split(".")]):
        path, page = render_topic_page(index, slug)
        dest = PAGE_DIR / slug / "index.html"
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(page, encoding="utf-8")
        written.append(dest)
        paths.append(path)

    # Anything under past-paper-questions/ that this run did not write is a page
    # for a topic that has since dropped below the gate or been retagged. The
    # output is meant to be a pure function of the data, so it goes.
    keep = {p.parent for p in written}
    removed = 0
    for child in sorted(PAGE_DIR.iterdir()):
        if child.is_dir() and child not in keep:
            for f in sorted(child.rglob("*")):
                f.unlink()
            child.rmdir()
            removed += 1

    theme_pages = sum(1 for p in paths if "/theme-" in p)
    topic_pages = len(paths) - theme_pages - 1
    print(f"wrote {theme_pages} theme pages and {topic_pages} topic pages")
    if removed:
        print(f"removed {removed} stale page(s)")

    if prettify(written):
        print(f"formatted {len(written)} pages")
    else:
        print("WARNING: prettier unavailable, formatting differs from the repo")

    if update_sitemap(index, paths):
        print(f"updated sitemap.xml ({len(paths)} URLs in the block)")
    else:
        print("sitemap.xml already up to date")


if __name__ == "__main__":
    main()

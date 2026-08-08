#!/usr/bin/env python3
"""Build the flashcards feature from flashcards-data/.

Reads one hand-authored deck file per board per theme from flashcards-data/,
validates every card, and emits:

    flashcards/index.html                      the hub (board -> theme picker)
    flashcards/<board>/<theme>/index.html      one landing page per deck
    flashcards/data/<deckId>.json              the public payload the player
                                               fetches at runtime

Do not hand-edit any of those outputs; re-run this script.

Rules enforced here rather than trusted:

  * Cards with "premium": true never enter the public payload or the sample
    cards - the builder is the gate, per the architectural note in CLAUDE.md.
  * A card whose source.origin is "notes-verbatim" must carry the exact text
    in source.verbatim, and that text must still appear on its notes page.
    The notes are the source of truth; a definition that reads badly is fixed
    in the notes and re-checked here, never edited on the card alone.
  * Diagram cards must reference an SVG that exists and carry alt text.
  * Formulae are LaTeX in the source data and KaTeX HTML in the outputs -
    the pages and payload carry no maths JavaScript.

Standard library only, plus node for KaTeX and npx for Prettier, exactly as
scripts/build_glossary.py does (the KaTeX and Prettier plumbing below is
copied from there - duplication over abstraction is the house idiom).
"""

from __future__ import annotations

import datetime as dt
import html
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "flashcards-data"
OUT_DIR = ROOT / "flashcards"
KATEX_JS = ROOT / "scripts" / "vendor" / "katex.min.js"

SITE = "https://economicsacademy.co.uk"
GTAG = "G-YVCNRW4QH6"
OG_IMAGE = f"{SITE}/og-image.png?v=1"

CARD_TYPES = {"definition", "formula", "calculation", "diagram", "chain",
              "evaluation", "application"}
DIFFICULTIES = {"foundation", "standard", "stretch"}
ORIGINS = {"notes-verbatim", "card-authored"}

# (board, theme) -> the revision-notes directory that teaches it. AQA decks,
# when they arrive, use the site-local 1.x.y / 2.x.y codes - see CLAUDE.md.
NOTES_DIRS = {
    ("edexcel-a", "theme-1"): "edexcel-theme-1",
    ("edexcel-a", "theme-2"): "edexcel-theme-2",
    ("edexcel-a", "theme-3"): "edexcel-theme-3",
    ("edexcel-a", "theme-4"): "edexcel-theme-4",
    ("aqa", "micro"): "aqa-a2-micro",
    ("aqa", "macro"): "aqa-a2-macro",
}

INLINE_TEX = re.compile(r"\\\((.+?)\\\)", re.S)


class BuildError(Exception):
    pass


def e(s: str) -> str:
    return html.escape(s, quote=True)


def json_ld(obj, indent="      ") -> str:
    s = json.dumps(obj, indent=2, ensure_ascii=False)
    return "\n".join(indent + line for line in s.split("\n")).strip()


def normalise(s: str) -> str:
    """Whitespace-normalise text for the verbatim comparison.

    Stripping tags leaves stray spaces where markup sat mid-sentence
    ("actually <strong>pay</strong>." becomes "pay ."), so spaces before
    closing punctuation and after an opening bracket are tightened on both
    sides of the comparison.
    """
    s = re.sub(r"\s+", " ", s).strip()
    s = re.sub(r"\s+([.,;:!?)\]])", r"\1", s)
    return re.sub(r"([(\[])\s+", r"\1", s)


def page_text(path: Path) -> str:
    """A notes page as normalised plain text, for the verbatim check."""
    text = path.read_text(encoding="utf-8")
    return normalise(html.unescape(re.sub(r"<[^>]+>", " ", text)))


def page_h1(path: Path) -> str:
    m = re.search(r"<h1>\s*(.*?)\s*</h1>", path.read_text(encoding="utf-8"),
                  re.S)
    if not m:
        raise BuildError(f"no <h1> found in {path}")
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", "", m.group(1))))


# ------------------------------------------------------------------- KaTeX
# Copied from scripts/build_glossary.py. throwOnError stays on: a formula
# that will not render is a build failure, not silently shipped LaTeX source.
# Output mode stays at KaTeX's default htmlAndMathml: the MathML half is what
# screen readers get, the HTML half is marked aria-hidden.

def katex(latex_list, display):
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


# -------------------------------------------------------------- validation

REQUIRED_DECK = ["board", "boardName", "theme", "themeName", "deckId",
                 "deckTitle", "metaDescription", "intro", "cards"]
REQUIRED_CARD = ["id", "specCode", "topic", "subtopic", "cardType", "front",
                 "back", "svgRef", "difficulty", "tags", "premium",
                 "acceptableAnswers", "version", "lastVerified", "source"]


def validate_deck(deck, path, errors):
    for key in REQUIRED_DECK:
        if key not in deck:
            errors.append(f"{path.name}: missing deck field '{key}'")
    if errors:
        return
    if (deck["board"], deck["theme"]) not in NOTES_DIRS:
        errors.append(f"{path.name}: unknown board/theme "
                      f"{deck['board']}/{deck['theme']}")
        return
    notes_dir = ROOT / "revision-notes" / NOTES_DIRS[(deck["board"],
                                                      deck["theme"])]
    seen_ids = set()
    page_cache = {}
    for card in deck["cards"]:
        cid = card.get("id", "<no id>")
        where = f"{path.name}: {cid}"
        for key in REQUIRED_CARD:
            if key not in card:
                errors.append(f"{where}: missing field '{key}'")
        if any(key not in card for key in REQUIRED_CARD):
            continue
        if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", card["id"]):
            errors.append(f"{where}: id is not a slug")
        if card["id"] in seen_ids:
            errors.append(f"{where}: duplicate id")
        seen_ids.add(card["id"])
        if not card["id"].startswith(deck["board"] + "-"):
            errors.append(f"{where}: id does not start with the board")
        if card["cardType"] not in CARD_TYPES:
            errors.append(f"{where}: bad cardType '{card['cardType']}'")
        if card["difficulty"] not in DIFFICULTIES:
            errors.append(f"{where}: bad difficulty '{card['difficulty']}'")
        if not re.fullmatch(r"\d+\.\d+\.\d+", card["specCode"]):
            errors.append(f"{where}: bad specCode '{card['specCode']}'")
        if not card["subtopic"].startswith(card["specCode"].replace(".", "-")):
            errors.append(f"{where}: subtopic does not match specCode")
        if not isinstance(card["premium"], bool):
            errors.append(f"{where}: premium must be a boolean")
        if not isinstance(card["version"], int):
            errors.append(f"{where}: version must be an integer")
        if not isinstance(card["tags"], list) or not isinstance(
                card["acceptableAnswers"], list):
            errors.append(f"{where}: tags and acceptableAnswers must be lists")
        try:
            dt.date.fromisoformat(card["lastVerified"])
        except (TypeError, ValueError):
            errors.append(f"{where}: lastVerified is not an ISO date")
        for field in ("front", "back"):
            if not (isinstance(card[field], str) and card[field].strip()):
                errors.append(f"{where}: empty {field}")

        notes_page = notes_dir / f"{card['subtopic']}.html"
        expected = (f"/revision-notes/{NOTES_DIRS[(deck['board'], deck['theme'])]}"
                    f"/{card['subtopic']}.html")
        if not notes_page.is_file():
            errors.append(f"{where}: no notes page {notes_page.name}")
        if card["source"].get("notesPage") != expected:
            errors.append(f"{where}: source.notesPage should be {expected}")
        origin = card["source"].get("origin")
        if origin not in ORIGINS:
            errors.append(f"{where}: bad source.origin '{origin}'")
        if origin == "notes-verbatim":
            verbatim = card["source"].get("verbatim", "")
            if not verbatim:
                errors.append(f"{where}: notes-verbatim card has no "
                              f"source.verbatim")
            elif notes_page.is_file():
                if notes_page not in page_cache:
                    page_cache[notes_page] = page_text(notes_page)
                needle = normalise(verbatim)
                if needle not in page_cache[notes_page]:
                    errors.append(f"{where}: verbatim text no longer appears "
                                  f"on {notes_page.name}")

        if card["cardType"] == "diagram":
            if not card["svgRef"]:
                errors.append(f"{where}: diagram card has no svgRef")
        if card["svgRef"]:
            if not (ROOT / card["svgRef"].lstrip("/")).is_file():
                errors.append(f"{where}: svgRef {card['svgRef']} not found")
            if not card.get("svgAlt"):
                errors.append(f"{where}: svgRef without svgAlt")
        if card.get("formula") and card["cardType"] not in ("formula",
                                                            "calculation"):
            errors.append(f"{where}: only formula/calculation cards may "
                          f"carry a formula")


# --------------------------------------------------------------- rendering

def render_maths(deck):
    """Pre-render the formula field and any inline \\( ... \\) maths."""
    display = sorted({c["formula"] for c in deck["cards"] if c.get("formula")})
    display_map = dict(zip(display, katex(display, True)))
    inline = sorted({html.unescape(m.group(1)).strip()
                     for c in deck["cards"]
                     for field in ("front", "back")
                     for m in INLINE_TEX.finditer(c[field])})
    inline_map = dict(zip(inline, katex(inline, False)))

    def swap_inline(text):
        return INLINE_TEX.sub(
            lambda m: inline_map[html.unescape(m.group(1)).strip()], text)

    return display_map, swap_inline


def public_cards(deck, display_map, swap_inline):
    notes_dir = NOTES_DIRS[(deck["board"], deck["theme"])]
    out = []
    for card in deck["cards"]:
        if card["premium"]:
            continue
        item = {
            "id": card["id"],
            "specCode": card["specCode"],
            "topic": card["topic"],
            "subtopic": card["subtopic"],
            "cardType": card["cardType"],
            "difficulty": card["difficulty"],
            "tags": card["tags"],
            "front": swap_inline(card["front"]),
            "back": swap_inline(card["back"]),
            "svgRef": card["svgRef"],
            "notesUrl": f"/revision-notes/{notes_dir}/{card['subtopic']}.html",
        }
        if card.get("formula"):
            item["formulaHtml"] = display_map[card["formula"]]
        if card["svgRef"]:
            item["svgAlt"] = card["svgAlt"]
        out.append(item)
    return out


def deck_topics(deck, cards):
    notes_dir = NOTES_DIRS[(deck["board"], deck["theme"])]
    topics = {}
    for card in cards:
        slug = card["subtopic"]
        if slug not in topics:
            page = ROOT / "revision-notes" / notes_dir / f"{slug}.html"
            topics[slug] = {
                "subtopic": slug,
                "specCode": card["specCode"],
                "title": page_h1(page),
                "notesUrl": card["notesUrl"],
                "count": 0,
            }
        topics[slug]["count"] += 1
    return list(topics.values())


# ------------------------------------------------------------- page shells

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
    <link rel="stylesheet" href="/css/pages/flashcards.css" />{katex_link}
  </head>
  <body class="is-preload">
    <div id="page-wrapper">
      <!-- Header -->
      <div id="header-placeholder"></div>

      <section id="main" class="flashcards-page">
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
    <script src="/js/components/flashcards.js" defer></script>
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


def sample_card_html(card):
    ignore = ("          <!-- prettier-ignore -->\n"
              if "formulaHtml" in card or "katex" in card["back"] else "")
    figure = ""
    if card["svgRef"]:
        figure = (f'\n            <img src="{card["svgRef"]}" '
                  f'alt="{e(card["svgAlt"])}" class="fc-sample-diagram" '
                  f'width="800" height="600" loading="lazy" />')
    formula = (f'\n            <div class="fc-formula">{card["formulaHtml"]}</div>'
               if "formulaHtml" in card else "")
    return f"""{ignore}          <article class="fc-sample">
            <div class="fc-sample-front">{card["front"]}</div>
            <div class="fc-sample-back">{formula}{figure}
              {card["back"]}
            </div>
          </article>"""


def pick_samples(cards):
    """First definition, first formula/calculation, first diagram - a stable,
    representative trio for the crawlable landing page."""
    samples = []
    for want in (("definition",), ("formula", "calculation"), ("diagram",)):
        for card in cards:
            if card["cardType"] in want and card not in samples:
                samples.append(card)
                break
    return samples


def deck_page(deck, cards, topics):
    board_seg = deck["board"]
    theme_seg = deck["theme"]
    path = f"/flashcards/{board_seg}/{theme_seg}/"
    crumbs = [("Home", "/"), ("Flashcards", "/flashcards/"),
              (f"{deck['boardName']} {deck['themeName'].split(':')[0]}", None)]
    notes_dir = NOTES_DIRS[(deck["board"], deck["theme"])]
    samples = "\n".join(sample_card_html(c) for c in pick_samples(cards))
    topic_items = "\n".join(
        f'            <li><a href="{t["notesUrl"]}">{e(t["title"])}</a>'
        f' <span class="fc-topic-count">{t["count"]} card'
        f'{"s" if t["count"] != 1 else ""}</span></li>'
        for t in topics)
    ld = json_ld({
        "@context": "https://schema.org",
        "@type": "LearningResource",
        "name": deck["deckTitle"],
        "description": deck["metaDescription"],
        "url": f"{SITE}{path}",
        "educationalLevel": "A-Level",
        "learningResourceType": "Flash cards",
        "inLanguage": "en-GB",
        "isPartOf": {
            "@type": "Course",
            "name": f"{deck['boardName']} A-Level Economics",
            "provider": {
                "@type": "EducationalOrganization",
                "name": "Economics Academy",
                "url": SITE,
            },
        },
    })
    body = f"""{breadcrumb_html(crumbs)}
          <header class="major">
            <h1>{e(deck["deckTitle"])}</h1>
          </header>
          <p class="fc-intro">{deck["intro"]}</p>
          <p class="fc-deck-stats">
            {len(cards)} cards &middot; {len(topics)} topics &middot;
            {e(deck["boardName"])} {e(deck["themeName"])}
          </p>

          <div
            class="fc-player"
            data-flashcards
            data-src="/flashcards/data/{deck["deckId"]}.json"
            data-board="{deck["board"]}"
            data-theme="{deck["theme"]}"
            data-deck-id="{deck["deckId"]}"
            data-deck-label="{e(deck["deckTitle"])}"
          >
            <noscript>
              <p class="fc-noscript">
                The interactive deck needs JavaScript. Without it, the sample
                cards below still work, and every definition on them comes
                from our
                <a href="/revision-notes/{notes_dir}/">{e(deck["themeName"])} revision notes</a>.
              </p>
            </noscript>
            <div class="fc-samples" data-fc-samples>
              <h2>Sample cards</h2>
{samples}
              <p class="fc-sample-note">
                These three are a taste of the deck. The full
                {len(cards)}-card deck loads right here — flip, rate and
                shuffle the cards, with your progress saved on this device.
              </p>
            </div>
            <div class="fc-mount" data-fc-mount></div>
          </div>

          <section class="fc-topics">
            <h2>What these flashcards cover</h2>
            <ul>
{topic_items}
            </ul>
          </section>

          <section class="fc-cta">
            <a href="/revision-notes/{notes_dir}/" class="button">
              Read the {e(deck["themeName"].split(":")[0])} notes
            </a>
            <a href="/practice-questions/{notes_dir}/" class="button">
              Try the practice questions
            </a>
          </section>"""
    return page_shell(
        title=deck["deckTitle"],
        desc=deck["metaDescription"],
        path=path,
        crumbs=[(n, h) for n, h in crumbs],
        body=body,
        jsonld=ld,
        katex_css=any("formulaHtml" in c for c in cards),
    ), path


def hub_page(decks):
    path = "/flashcards/"
    crumbs = [("Home", "/"), ("Flashcards", None)]
    ld = json_ld({
        "@context": "https://schema.org",
        "@type": "CollectionPage",
        "name": "A-Level Economics Flashcards",
        "description": "Free interactive A-Level Economics flashcards for "
                       "Edexcel A and AQA, with spaced repetition.",
        "url": f"{SITE}{path}",
        "inLanguage": "en-GB",
    })
    sections = []
    for board_name in sorted({d["deck"]["boardName"] for d in decks}):
        deck_cards = "\n".join(
            f"""            <article class="fc-deck-card">
              <h3>
                <a href="/flashcards/{d["deck"]["board"]}/{d["deck"]["theme"]}/">
                  {e(d["deck"]["themeName"])}
                </a>
              </h3>
              <p>{len(d["cards"])} cards &middot; {len(d["topics"])} topics</p>
            </article>"""
            for d in decks if d["deck"]["boardName"] == board_name)
        sections.append(f"""          <section class="fc-board">
            <h2>{e(board_name)}</h2>
{deck_cards}
          </section>""")
    body = f"""{breadcrumb_html(crumbs)}
          <header class="major">
            <h1>A-Level Economics Flashcards</h1>
          </header>
          <p class="fc-intro">
            Interactive flashcards for A-Level Economics — precise
            definitions, formulae, exam-standard diagrams, chains of
            reasoning and evaluation points, written to each board's own
            specification. Flip a card to check yourself and rate how well
            you knew it; the deck remembers and brings the hard ones back.
            More decks are added as they are written, and every card links
            to the revision notes page that teaches it.
          </p>
{chr(10).join(sections)}
          <section class="fc-cta">
            <a href="/revision-notes/" class="button">
              Browse the revision notes
            </a>
            <a href="/practice-questions/" class="button">
              Try the practice questions
            </a>
          </section>"""
    return page_shell(
        title="A-Level Economics Flashcards | Economics Academy",
        desc="Free interactive A-Level Economics flashcards for Edexcel A "
             "and AQA: definitions, formulae, diagrams and evaluation "
             "points with spaced repetition.",
        path=path,
        crumbs=crumbs,
        body=body,
        jsonld=ld,
    ), path


# ------------------------------------------------------------------ output

def run_prettier(paths):
    """Prettier is not installed here; the repo convention is
    `npx prettier@3.9.6` (see CLAUDE.md)."""
    try:
        subprocess.run(
            ["npx", "--yes", "prettier@3.9.6", "--write", "--log-level",
             "warn"] + [str(p) for p in paths],
            check=True, cwd=ROOT,
        )
        return True
    except (OSError, subprocess.CalledProcessError):
        return False


def main():
    deck_files = sorted(DATA_DIR.glob("*/*.json"))
    if not deck_files:
        print("no deck files under flashcards-data/", file=sys.stderr)
        return 1

    errors = []
    decks = []
    for path in deck_files:
        deck = json.loads(path.read_text(encoding="utf-8"))
        validate_deck(deck, path, errors)
        # Deck order is spec order, whatever order the cards were authored
        # in. The sort is stable, so cards sharing a spec code keep their
        # authored order.
        try:
            deck["cards"].sort(
                key=lambda c: tuple(int(p) for p in c["specCode"].split(".")))
        except (KeyError, ValueError):
            pass  # already reported by validation
        decks.append((path, deck))
    if errors:
        for err in errors:
            print(f"ERROR: {err}", file=sys.stderr)
        print(f"{len(errors)} error(s); nothing written", file=sys.stderr)
        return 1

    html_paths = []
    built = []
    (OUT_DIR / "data").mkdir(parents=True, exist_ok=True)
    for path, deck in decks:
        display_map, swap_inline = render_maths(deck)
        cards = public_cards(deck, display_map, swap_inline)
        topics = deck_topics(deck, cards)
        payload = {
            "generated": dt.date.today().isoformat(),
            "board": deck["board"],
            "boardName": deck["boardName"],
            "theme": deck["theme"],
            "themeName": deck["themeName"],
            "deckId": deck["deckId"],
            "deckTitle": deck["deckTitle"],
            "count": len(cards),
            "topics": topics,
            "cards": cards,
        }
        data_path = OUT_DIR / "data" / f"{deck['deckId']}.json"
        data_path.write_text(
            json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8")

        page, url_path = deck_page(deck, cards, topics)
        out = OUT_DIR / deck["board"] / deck["theme"] / "index.html"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(page, encoding="utf-8")
        html_paths.append(out)
        built.append({"deck": deck, "cards": cards, "topics": topics})
        hidden = len(deck["cards"]) - len(cards)
        print(f"built {url_path}: {len(cards)} cards, {len(topics)} topics"
              + (f" ({hidden} premium card(s) withheld)" if hidden else ""))

    page, _ = hub_page(built)
    hub_path = OUT_DIR / "index.html"
    hub_path.write_text(page, encoding="utf-8")
    html_paths.append(hub_path)
    print(f"built /flashcards/ hub with {len(built)} deck(s)")

    if not run_prettier(html_paths):
        print("  WARNING: prettier unavailable, formatting differs from "
              "the repo")
    return 0


if __name__ == "__main__":
    sys.exit(main())

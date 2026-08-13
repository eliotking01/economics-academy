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
sys.path.insert(0, str(ROOT / "scripts"))
# Wave 2 Phase 6. The <head> is no longer written here; page_shell.py owns it
# for every family, so a change to the social cards or the script tail is one
# edit rather than five. What stays local is everything below </head>.
import board_data  # noqa: E402
import page_shell as shell  # noqa: E402

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

# (board, theme) -> the revision-notes directory that teaches it, from
# boards-data/boards.json rather than restated here - Wave 3.2, PH09-022.
#
# The AQA decks use the site-local 1.x.y / 2.x.y codes, not the real 7136
# codes - ratified in CLAUDE.md, and `specCodesAreReal: false` in the record is
# where that now reads as data rather than prose.
#
# This generator takes NO NAME from the record. A deck's title is its own, in
# flashcards-data/<board>/<theme>.json, and Theme 2's is the HYPHEN spelling
# where taxonomy.json and the notes hub carry an em dash. boards.json records
# both, per consumer, and nothing here may reconcile them.
NOTES_DIRS = {
    (board["slugs"]["flashcards"], group["flashcardsSlug"]): group["notesDir"]
    for _key, board, group in board_data.groups()
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
    """The common page skeleton. The <head> comes from scripts/page_shell.py.

    Wave 2 Phase 6. Everything above </head> used to be a 65-line f-string
    here, duplicating what four other generators and 190 hand-written pages
    also carried. It is now one call, and the values below are the whole of
    what this family contributes to its own <head>.
    """
    url = f"{SITE}{path}"
    crumb_ld = {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {k: v for k, v in
             {"@type": "ListItem", "position": i, "name": name,
              "item": f"{SITE}{href}" if href else None}.items() if v is not None}
            for i, (name, href) in enumerate(crumbs, 1)
        ],
    }
    sheets = ["/css/pages/flashcards.css"]
    if katex_css:
        # Self-hosted KaTeX, for the formula cards. page_shell keeps every
        # stylesheet after main.css in order; an earlier version of it filtered
        # to /css/pages/ and would have dropped this one silently.
        sheets.append("/css/vendor/katex/katex.min.css")
    head = shell.render_head({
        "title": e(title),
        "description": e(desc),
        "canonical": url,
        # This family puts the font preconnect before <title> and the favicon
        # trio straight after the canonical. Both are recorded rather than
        # chosen: reconciling them with the hand-written pages is a separate
        # normalisation.
        "preconnectEarly": True,
        "faviconsAfterCanonical": True,
        "ogComment": True,
        "sdComment": True,
        "og": {
            "type": "website", "siteName": "Economics Academy",
            "locale": "en_GB", "url": url,
            "title": e(title), "description": e(desc),
            "image": OG_IMAGE, "image:width": "1200", "image:height": "1200",
            "image:type": "image/png", "image:alt": "Economics Academy logo",
        },
        "twitter": {
            "card": "summary_large_image", "title": e(title),
            "description": e(desc), "image": OG_IMAGE,
        },
        "jsonldBeforeIcons": [jsonld, crumb_ld],
        "pageStylesheets": sheets,
    })
    return f"""<!doctype html>
<html lang="en-GB">
  <head>
{head}
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
{shell.script_tail(("/js/components/flashcards.js",))}
  </body>
</html>
"""


# PH07-058, Wave 4.9. See the matching note in build_glossary.py: flashcards
# and the glossary were the only two families with no body link to a paid
# service, and the injected footer needs JavaScript. The anchor text is new on
# purpose - 444 of 455 links to tutoring.html already read "Book a Free Intro
# Call", and seo/07b-link-decisions.md §5 declines deepening exactly that.
SERVICES_CTA = """
          <section class="fc-services-cta">
            <p>Recall is the easy half — the marks are in the application.</p>
            <a href="/marking.html" class="button alt"
              >Have a practice paper marked</a
            >
            <a href="/tutoring.html" class="button">Book a tutoring session</a>
          </section>"""


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
    ld = {
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
                # Same @id everywhere the organisation is restated across the
                # site; see seo/08-structured-data.md.
                "@id": f"{SITE}/#organization",
                "name": "Economics Academy",
                "url": SITE,
            },
        },
    }
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
          </section>
{SERVICES_CTA}"""
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
    ld = {
        "@context": "https://schema.org",
        "@type": "CollectionPage",
        "name": "A-Level Economics Flashcards",
        "description": "Free interactive A-Level Economics flashcards for "
                       "Edexcel A and AQA, with spaced repetition.",
        "url": f"{SITE}{path}",
        "inLanguage": "en-GB",
        "publisher": shell.ORGANISATION_REF,
    }
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
          </section>
{SERVICES_CTA}"""
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
        # No build-date stamp - see PH09b-025 and the note in
        # build_past_paper_questions.py. It made every rebuild diff against a
        # clean tree while nothing read the value.
        payload = {
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
    # Wave 2 Phase 7. After Prettier, never before - see shell.bake_files().
    print(f"  baked the header and footer into "
          f"{shell.bake_files(html_paths)} page(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())

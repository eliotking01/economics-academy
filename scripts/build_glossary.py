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
looks slightly different in the two places - recorded in _archive/ROADMAP.md.

Standard library only, plus node for KaTeX and npx for Prettier. Neither is
needed to view the site.
"""

from __future__ import annotations

import argparse
import hashlib
import html
import json
import pathlib
import re
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import board_data  # noqa: E402
# Wave 2 Phase 6. page_shell.py owns the <head> for every family now.
import page_shell as shell  # noqa: E402
import prettier_util  # noqa: E402
DATA = ROOT / "glossary-data" / "terms.json"
TAXONOMY = ROOT / "past-paper-questions-data" / "taxonomy.json"
OUT_DIR = ROOT / "revision-notes" / "glossary"
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

# The hero paragraph and meta description for each board page. These are PAGE
# COPY, not board identity, and they stay here on purpose: boards.json records
# what a board is called and where it lives, not what a page says about it.
# Every other field below now comes from the record - Wave 3.2, PH09-022.
#
# The `taxonomy` key was PH09-022's own exhibit: a field whose only job was to
# bridge this generator's board key to another's, proving the need for a
# canonical identity while solving it privately where nothing else could reach.
# It is still here, and it is now a lookup rather than a translation.
BOARD_COPY = {
    "edexcel-a": {
        "intro": (
            "Every key term and formula you need for <strong>Edexcel A-Level "
            "Economics A (9EC0)</strong>, covering Themes 1 to 4. Each "
            "definition comes from the revision notes on this site, and links "
            "back to the topic page it came from."
        ),
        "meta": (
            "Every key term and formula for Edexcel A-Level Economics (9EC0), "
            "taken from our Theme 1-4 revision notes. Search, "
            "browse A-Z or print."
        ),
    },
    "aqa": {
        "intro": (
            "Every key term and formula you need for <strong>AQA A-Level "
            "Economics (7136)</strong>, covering microeconomics and "
            "macroeconomics. Each definition comes from the revision notes on "
            "this site, and links back to the topic page it came from."
        ),
        "meta": (
            "Every key term and formula for AQA A-Level Economics (7136), taken "
            "from our microeconomics and macroeconomics revision "
            "notes. Search or print."
        ),
    },
    # Phase 3: copied from Edexcel A's with B's name and code, approved by
    # Eliot on 2026-11-16 (review/glossary-b.md Q1). B is STAGED, so no page
    # prints this until /launch-feature.
    "edexcel-b": {
        "intro": (
            "Every key term and formula you need for <strong>Edexcel A-Level "
            "Economics B (9EB0)</strong>, covering Themes 1 to 4. Each "
            "definition comes from the revision notes on this site, and links "
            "back to the topic page it came from."
        ),
        "meta": (
            "Every key term and formula for Edexcel A-Level Economics B "
            "(9EB0), taken from our Theme 1-4 revision notes. Search, "
            "browse A-Z or print."
        ),
    },
}

def board_table(staged: bool = False) -> dict:
    """{glossary slug: page metadata} for the live glossary boards, or with
    staged=True the staged ones too (D68) - which build_glossary renders in
    memory to validate and never writes."""
    out = {}
    for b in board_data.load("glossary", staged=staged).values():
        slug = b["slugs"]["glossary"]
        if slug not in BOARD_COPY:
            sys.exit(f"boards.json records glossary board {slug!r} and "
                     f"BOARD_COPY has no intro or meta for it. A board page "
                     f"cannot be built without both - add the copy here, in "
                     f"this file.")
        out[slug] = {
            "slug": slug,
            "name": b["names"]["display"],
            "long": b["names"]["long"],
            "taxonomy": b["slugs"]["taxonomy"],
            "notesUrl": b["notesUrl"],
            **BOARD_COPY[slug],
        }
    return out


BOARDS = board_table()
STAGED_BOARDS = board_table(staged=True)

_orphaned = sorted(set(BOARD_COPY) - set(STAGED_BOARDS))
if _orphaned:
    sys.exit(f"BOARD_COPY has page copy for {_orphaned}, which boards.json "
             f"does not record as a glossary board. Delete it, or add the "
             f"board to the record.")

INLINE_TEX = re.compile(r"\\\((.+?)\\\)", re.S)
# Display maths INSIDE a definition. Edexcel B's notes (Phase 3) state a
# formula in the chip's own paragraph as \[ ... \] - "Average cost: the cost
# of producing one unit ...: \[ AC = ... \]" - where Edexcel A and AQA wrote
# it inline. It is part of the notes' own definition, so it is pre-rendered
# in display mode like a formula, not stripped. No live definition had one.
DISPLAY_TEX = re.compile(r"\\\[(.+?)\\\]", re.S)

# ------------------------------------------------------------ capitalisation
#
# The notes write a definition as the continuation of its chip - "Absolute
# advantage: a situation in which ..." - so lifted out and set under a heading
# it opens on a lower-case letter. Capitalising the first letter is a
# presentation change, and it is made HERE, at render time, for exactly that
# reason: glossary-data/terms.json stays byte-identical to the notes, so
# verify_glossary.py's verbatim check keeps meaning what it says.
#
# Which records get it is not a judgement this script makes. It reads the
# approved list from curation.json, where scripts/check_glossary_capitalisation.py
# put it. Definitions that need the term as their grammatical subject
# ("Globalisation is the increasing integration ...") are NOT on that list, and
# are fixed in the notes or not at all.

CURATION = DATA.parent / "curation.json"

# A definition record has no stable id - a term can carry several sources on one
# page - so approval is keyed on the wording itself. Reword the notes and the
# key changes, the approval lapses, and --check asks for it again. That is the
# intended behaviour, not a limitation.
FIRST_LETTER = re.compile(r"^(\s*(?:<[^>]+>\s*)*)([a-z])")


def cap_key(term_id: str, definition_html: str) -> str:
    digest = hashlib.sha1(definition_html.encode("utf-8")).hexdigest()[:8]
    return f"{term_id}:{digest}"


def approved_capitalisations() -> set:
    cur = json.loads(CURATION.read_text(encoding="utf-8"))
    return set(cur.get("capitalise", {}).get("apply", {}))


def capitalise(term_id: str, fragment: str, approved: set) -> str:
    """Upper-case the definition's first letter, if that record is approved.

    The first letter is not always the first character: a definition may open
    inside a <strong>, so the tags are stepped over rather than counted.
    """
    if cap_key(term_id, fragment) not in approved:
        return fragment
    return FIRST_LETTER.sub(lambda m: m.group(1) + m.group(2).upper(),
                            fragment, count=1)


# ---------------------------------------------------------------- rewrites
#
# THE ONE PLACE THE GLOSSARY DOES NOT SHOW THE NOTES' OWN WORDS.
#
# 46 definitions read as fragments because the notes made the term the subject
# of the sentence - "Globalisation is the increasing integration ...". Under a
# heading that leaves "is the increasing integration ...". Eliot asked on
# 2026-08-07 for these to read correctly in the glossary WITHOUT the notes being
# edited, which is a deliberate, instructed departure from the rule in CLAUDE.md
# that a badly-reading definition is fixed in the notes and re-extracted.
#
# It is kept as narrow as it can be:
#
#   - A rewrite replaces a LEADING SUBSTRING and nothing else. 39 of the 46 only
#     drop a lead-in and capitalise the next word, so no word is invented. The
#     seven that do not are marked "adds" or "not-a-definition" in curation.json.
#   - "from" must still be the start of the extracted definition. Change the
#     notes and the build stops, rather than quietly applying a rewrite to text
#     it was never reviewed against. That is the anti-drift property the
#     verbatim check gives everything else.
#   - terms.json is untouched, so check 1 keeps proving the EXTRACTION is
#     faithful. What it no longer proves is that the rendered page is - which is
#     what check 7 in verify_glossary.py exists to make visible.


def rewrites() -> dict:
    cur = json.loads(CURATION.read_text(encoding="utf-8"))
    return cur.get("rewrite", {}).get("entries", {})


def rewrite(term_id: str, fragment: str, table: dict) -> str:
    rule = table.get(cap_key(term_id, fragment))
    if not rule:
        return fragment
    if not fragment.startswith(rule["from"]):
        raise BuildError(
            f"rewrite for '{term_id}' no longer applies: the notes now open "
            f"{fragment[:60]!r}, not {rule['from']!r}. Re-review it in "
            f"glossary-data/curation.json, or delete the rule if the notes have "
            f"been fixed at source.")
    return rule["to"] + fragment[len(rule["from"]):]


# ---------------------------------------------------------------- senses
#
# One headword, two meanings. Edexcel B defines `risk` twice (1.4.2 business
# risk, 4.5.1 measurable risk) and `interdependence` twice (3.1.3 countries,
# 4.1.3 firms), and the wordings are different concepts rather than variants
# of one. Eliot decided on 2026-11-11 that the B glossary shows both, under
# one headword; the rendering was approved on 2026-11-16 (review/glossary-b.md
# Q10). curation.json `senses.entries` names, per term key and board, the
# sources to show as numbered senses, in order. Each is still a notes chip,
# word for word, with its own page link. Every other entry is unchanged.


def senses() -> dict:
    cur = json.loads(CURATION.read_text(encoding="utf-8"))
    return cur.get("senses", {}).get("entries", {})


def sense_sources(term, board, table):
    """The sources shown as numbered senses for this board, or []."""
    urls = table.get(term["key"], {}).get(board, [])
    mine = {x["notesUrl"]: x for x in term["sources"] if x["board"] == board}
    missing = [u for u in urls if u not in mine]
    if missing:
        raise BuildError(
            f"senses for '{term['term']}' ({board}) name {missing}, which are "
            f"not its {board} sources - fix glossary-data/curation.json")
    return [mine[u] for u in urls]


# The landing page's copy depends on which boards it lists, so it is keyed on
# them, in boards.json order. Edexcel A + AQA is what is live. The three-board
# entry was approved by Eliot on 2026-11-16 (Phase 3, review/glossary-b.md Q3)
# and is printed by no page until Edexcel B's glossary launches. Any other set
# of boards stops the build until it has copy here.
LANDING_COPY = {
    ("edexcel-a", "aqa"): {
        "meta": (
            "Free A-Level Economics glossary. Choose your exam board for every "
            "definition and formula you need, taken from our Edexcel and "
            "AQA revision notes."
        ),
        "intro": """Every definition and formula you need, in one place. Pick your exam
              board - the two specifications share most of their vocabulary, but
              not all of it, and each glossary carries only what its own
              specification asks for.""",
    },
    ("edexcel-a", "aqa", "edexcel-b"): {
        "meta": (
            "Free A-Level Economics glossary. Choose your exam board for every "
            "definition and formula you need, taken from our Edexcel A, "
            "Edexcel B and AQA revision notes."
        ),
        "intro": """Every definition and formula you need, in one place. Pick your exam
              board - the three specifications share most of their vocabulary,
              but not all of it, and each glossary carries only what its own
              specification asks for.""",
    },
}


def landing_copy(boards: dict) -> dict:
    key = tuple(boards)
    if key not in LANDING_COPY:
        sys.exit(f"the glossary landing page has no copy for the boards "
                 f"{key}. Add an entry to LANDING_COPY in this file.")
    return LANDING_COPY[key]


LANDING_META = landing_copy(BOARDS)["meta"]


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
    return DISPLAY_TEX.sub(one, INLINE_TEX.sub(one, s))


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


def render_inline_maths(definition: str, inline_map, display_map=None) -> str:
    """Swap \\( ... \\) inside a definition for pre-rendered KaTeX.

    Fifteen definitions state their formula inline - "Average Cost (AC):
    \\( AC = \\frac{TC}{Q} \\)". The glossary pages carry no maths JavaScript,
    so without this those definitions display their LaTeX source to the reader.
    Display formulae are handled separately; only the inline form appears here.
    """
    if display_map is not None:
        definition = DISPLAY_TEX.sub(
            lambda m: display_map[html.unescape(m.group(1)).strip()],
            definition)
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

def taxonomy_groups(tax, boards) -> dict:
    """{(glossary board, group slug): label, name, order} for `boards`.

    Keyed on the board as well as the slug since Phase 3: Edexcel A and
    Edexcel B both have groups `theme-1`..`theme-4`, and keyed on the slug
    alone the second board's would overwrite the first's (Phase 0 hazard 1).
    Glossary boards only: taxonomy.json can hold a board for the past-paper
    bank alone, or for a staged glossary (board_data.TAXONOMY_READERS).
    """
    of_taxonomy = {m["taxonomy"]: slug for slug, m in boards.items()}
    groups, order = {}, 0
    for b in tax["boards"]:
        if b["board"] not in of_taxonomy:
            continue
        for g in b["groups"]:
            groups[(of_taxonomy[b["board"]], g["slug"])] = {
                "label": g["label"], "name": g["name"], "order": order}
            order += 1
    return groups


def validate(data, groups, boards=None):
    """Collect every failure. Nothing is written if there is one."""
    boards = BOARDS if boards is None else boards
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
            if s["board"] not in boards:
                errs.append(f"{where}: unknown board '{s['board']}'")
            if s["notesUrl"] and not (ROOT / s["notesUrl"].lstrip("/")).is_file():
                errs.append(f"{where}: notesUrl does not exist - {s['notesUrl']}")
            if (s["board"], s["group"]) not in groups:
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

    for board, meta in boards.items():
        if not 120 <= len(meta["meta"]) <= 165:
            errs.append(f"{board}: meta description is {len(meta['meta'])} "
                        f"characters, needs 120-165")
    landing_meta = landing_copy(boards)["meta"]
    if not 120 <= len(landing_meta) <= 165:
        errs.append(f"landing: meta description is {len(landing_meta)} "
                    f"characters, needs 120-165")
    return errs


# ---------------------------------------------------------------- page shell

def page_shell(*, title, desc, path, crumbs, body, jsonld, katex_css=False):
    """The common page skeleton. The <head> comes from scripts/page_shell.py.

    Wave 2 Phase 6. This function's <head> was byte-identical to
    build_flashcards.py's bar the stylesheet name, which is the duplication
    the whole wave exists to remove. 2026-08-23: the skeleton, the og/twitter
    block and the BreadcrumbList builder moved into page_shell.py too; what is
    left here is the list of values this family contributes.
    """
    url = f"{SITE}{path}"
    sheets = ["/css/pages/glossary.css"]
    if katex_css:
        sheets.append("/css/vendor/katex/katex.min.css")
    values = shell.head_values(title, desc, url, sheets, esc=e)
    values.update({
        # This family puts the favicon trio straight after the canonical.
        # Recorded rather than chosen: reconciling it with the hand-written
        # pages is a separate normalisation. (It also put the font preconnect
        # before <title> until the fonts were self-hosted on 2026-08-23.)
        "faviconsAfterCanonical": True,
        "ogComment": True,
        "sdComment": True,
        "jsonldBeforeIcons": [jsonld, shell.breadcrumb_ld(crumbs)],
    })
    return shell.page(
        shell.render_head(values),
        shell.container(body, "glossary-page"),
        ("/js/components/glossary-filter.js",),
    )


# PH07-058, Wave 4.9. The glossary was one of two families with no body link
# to a paid service at all - the injected footer was the only route, and that
# needs JavaScript, so with scripting off these pages had none.
#
# The anchor text is deliberately NOT the notes pages' "Book a Free Intro
# Call" / "Get Essays Marked". seo/07b-link-decisions.md §5 declines more
# links to tutoring.html and marking.html, and its stated reason is that they
# are already the most-linked pages; the bullet after it declines reusing an
# anchor string because "adding more deepens a monoculture". Measured before
# writing this: 444 of 455 links to tutoring.html read "Book a Free Intro
# Call" - 97.6%, 8 distinct anchors across the whole site. Ten more of the
# same string would be exactly what §5's third bullet objects to. Two new
# anchors here, two more in build_flashcards.py, take tutoring to 10 distinct
# and marking to 9. Do not "harmonise" these with the notes CTA.
SERVICES_CTA = """
          <section class="gl-services-cta">
            <p>Ready to use these terms in an answer?</p>
            <a href="/marking.html" class="button alt">Have an essay marked</a>
            <a href="/tutoring.html" class="button">Book a 1-on-1 session</a>
          </section>"""


def breadcrumb_html(crumbs, indent=10):
    return shell.breadcrumb_html(crumbs, indent, esc=e)


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


def ld_description(term, board, rules, approved):
    """The DefinedTerm description: the same words the page shows.

    Where the list carries the meaning, "e.g. USMCA" on its own would be a
    useless description, so the list is folded in - as a sentence, since
    structured data takes plain text and cannot show bullets.

    An entry shown as numbered senses (senses()) carries them all, numbered
    as the page numbers them.
    """
    numbered = sense_sources(term, board, senses())
    if numbered:
        return " ".join(
            f"{i}. " + plain(capitalise(term["id"], rewrite(
                term["id"], x["definitionHtml"], rules), approved))
            for i, x in enumerate(numbered, 1))
    s = source_for(term, board)
    text = plain(capitalise(term["id"],
                            rewrite(term["id"], s["definitionHtml"], rules),
                            approved))
    if s.get("listIsDefinition") and s.get("definitionListHtml"):
        items = [plain(i) for i in
                 re.findall(r"<li>(.*?)</li>", s["definitionListHtml"], re.S)]
        if items:
            text = "; ".join(i.rstrip(".") for i in items) + f". {text}"
    return text


def senses_html(term, board, numbered, inline_map, approved, rules,
                display_map):
    """An entry whose meanings are listed as numbered senses (see senses())."""
    items = []
    for x in numbered:
        if x.get("definitionListHtml"):
            raise BuildError(f"'{term['term']}': a sense cannot carry a "
                             f"continuation list")
        d = capitalise(term["id"], rewrite(term["id"], x["definitionHtml"],
                                           rules), approved)
        items.append(
            "<li>\n"
            f'                      <p class="gl-text">'
            f"{render_inline_maths(d, inline_map, display_map)}</p>\n"
            f'                      <p class="gl-source">{source_link(x)}</p>\n'
            "                    </li>")
    groups = sorted({x["group"] for x in term["sources"] if x["board"] == board})
    others = [x for x in term["sources"]
              if x["board"] == board and x not in numbered]
    also = ""
    if others:
        links = ", ".join(
            f'<a href="{x["notesUrl"]}">{e(x["spec"])}</a>' for x in others)
        also = (f'\n                <p class="gl-also">Also covered in '
                f"{links}</p>")
    body = "\n                    ".join(items)
    return f"""              <div
                class="gl-entry"
                id="{e(term['id'])}"
                data-term="{e(term['term'].lower())}"
                data-groups="{e(' '.join(groups))}"
                data-origin="{e(numbered[0].get('origin', 'notes'))}"
              >
                <dt class="gl-term">{e(term['term'])}</dt>
                <dd class="gl-def">
                  <ol class="gl-senses">
                    {body}
                  </ol>{also}
                </dd>
              </div>"""


def entry_html(term, board, inline_map, approved, rules, display_map=None,
               sense_table=None):
    numbered = sense_sources(term, board, sense_table or {})
    if numbered:
        return senses_html(term, board, numbered, inline_map, approved, rules,
                           display_map)
    s = source_for(term, board)
    definition = rewrite(term["id"], s["definitionHtml"], rules)
    definition = capitalise(term["id"], definition, approved)
    # Some definitions end on a colon because the rest of them is the bulleted
    # list that follows on the notes page. The list is carried across so the
    # entry reads as a whole; it cannot sit inside the <p>.
    #
    # Order depends on which half is the definition. Normally the paragraph
    # opens the sentence and the list finishes it, so the paragraph leads. For
    # the five trading-bloc terms it is the other way round - the paragraph is
    # only "e.g. USMCA" and the list carries the meaning - so the list leads and
    # the example follows it.
    dlist = ""
    if s.get("definitionListHtml"):
        dlist = ('<div class="gl-def-list">'
                 + render_inline_maths(s["definitionListHtml"], inline_map,
                                       display_map)
                 + "</div>")
    text = (f'<p class="gl-text">'
            f'{render_inline_maths(definition, inline_map, display_map)}</p>')
    body = [dlist, text] if s.get("listIsDefinition") else [text, dlist]
    body_html = "\n                  ".join(p for p in body if p)
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
                  {body_html}
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
                <span class="gl-group">{e(groups[(board, s['group'])]['label'])}</span>
                <a href="{e(s['notesUrl'])}">{e(s['spec'])} {e(s['topic'])}</a>
              </p>
            </div>"""


def render_board(data, board, groups, rendered_map, inline_map, boards=None):
    boards = BOARDS if boards is None else boards
    meta = boards[board]
    approved = approved_capitalisations()
    rules = rewrites()
    sense_table = senses()
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
        key=lambda g: groups[(board, g)]["order"])
    options = "\n".join(
        f'                <option value="{e(g)}">{e(groups[(board, g)]["label"])}</option>'
        for g in board_groups)

    sections = []
    for L in LETTERS:
        if not by_letter[L]:
            continue
        entries = "\n".join(
                entry_html(t, board, inline_map, approved, rules, rendered_map,
                           sense_table)
                for t in by_letter[L])
        sections.append(f"""          <section class="gl-letter" id="letter-{L.lower()}">
            <h2 class="gl-letter-head">{L}</h2>
            <dl class="gl-list">
{entries}
            </dl>
          </section>""")
    if other:
        entries = "\n".join(entry_html(t, board, inline_map, approved, rules,
                                        rendered_map, sense_table)
                             for t in other)
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

    # PH01-012's exhibit: this was `"aqa" if board == "edexcel-a" else
    # "edexcel-a"`, which silently assumed there would only ever be two boards.
    # With two, the hero still renders the one "Switch to the ... glossary"
    # link it always has, byte for byte. With three (Edexcel B, Phase 3) it
    # names each other board - see switch_html().
    crumbs = [("Home", "/"), ("Revision Notes", "/revision-notes/"),
              ("Glossary", "/revision-notes/glossary/"),
              (boards[board]["name"], None)]
    switch = switch_html(board, boards)

    body = f"""{breadcrumb_html(crumbs)}

          <header class="gl-hero">
            <h1>{e(meta['long'])} Glossary</h1>
            <p class="gl-intro">{meta['intro']}</p>
            <p class="gl-stats">
              <strong>{len(terms)}</strong> definitions and
              <strong>{len(formulae)}</strong> formulae.
{switch}
            </p>
          </header>

          <div class="gl-search" data-glossary-search>
            <form class="gl-controls" data-gl-controls hidden>
              <div class="gl-field">
                <label for="gl-query">Search key terms</label>
                <input
                  type="search"
                  id="gl-query"
                  data-gl-query
                  placeholder="Search key terms - try elasticity, or PED"
                  autocomplete="off"
                  aria-describedby="gl-query-help"
                />
                <p class="gl-help" id="gl-query-help">
                  Searches term names, not definition text.
                </p>
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
              No key terms match <strong data-gl-echo></strong>. Search looks at
              term names only, not definition text - so a topic that is not
              itself a key term will not be found. Try a shorter term, jump to a
              letter above, or
              <button type="button" class="gl-clear-inline" data-gl-clear>
                clear the search</button
              >.
            </p>

            <section class="gl-results" data-gl-results hidden>
              <h2 class="gl-letter-head">Best matches</h2>
              <dl class="gl-list"></dl>
            </section>
{formula_block}
{chr(10).join(sections)}
          </div>
{SERVICES_CTA}"""

    ld = {
        "@context": "https://schema.org",
        "@type": "DefinedTermSet",
        "@id": f"{SITE}/revision-notes/glossary/{meta['slug']}/#glossary",
        "name": f"{meta['long']} Glossary",
        "description": plain(meta["meta"]),
        "url": f"{SITE}/revision-notes/glossary/{meta['slug']}/",
        "inLanguage": "en-GB",
        "educationalLevel": "A-Level",
        # The @id is the same on every restatement of the organisation across
        # the site; see seo/08-structured-data.md.
        "publisher": {"@type": "EducationalOrganization",
                      "@id": f"{SITE}/#organization",
                      "name": "Economics Academy", "url": SITE},
        "hasDefinedTerm": [
            {
                "@type": "DefinedTerm",
                "@id": f"{SITE}/revision-notes/glossary/{meta['slug']}/#{t['id']}",
                "name": t["term"],
                "description": ld_description(t, board, rules, approved),
                "url": f"{SITE}/revision-notes/glossary/{meta['slug']}/#{t['id']}",
                "inDefinedTermSet":
                    f"{SITE}/revision-notes/glossary/{meta['slug']}/#glossary",
            }
            for t in terms
        ],
    }

    return page_shell(
        title=f"{meta['long']} Glossary — Key Terms & Formulae | Economics Academy",
        desc=meta["meta"],
        path=f"/revision-notes/glossary/{meta['slug']}/",
        crumbs=crumbs, body=body, jsonld=ld, katex_css=bool(formulae),
    )


def switch_html(board, boards):
    """The hero's link to the other board's glossary - or, with more than one
    other board, to each of them.

    The two-board form is the markup the live pages have always carried, kept
    byte-identical. The three-board form was approved by Eliot on 2026-11-16
    (Phase 3, review/glossary-b.md Q2); no page prints it until Edexcel B's
    glossary launches.
    """
    others = [b for b in boards if b != board]
    if len(others) == 1:
        o = boards[others[0]]
        return (f'              <a href="/revision-notes/glossary/{o["slug"]}/"\n'
                f'                >Switch to the {e(o["name"])} glossary</a\n'
                f'              >')
    links = [f'<a href="/revision-notes/glossary/{boards[o]["slug"]}/"'
             f'>{e(boards[o]["name"])}</a>' for o in others]
    joined = ", ".join(links[:-1]) + " or " + links[-1]
    return f"              Switch to the {joined} glossary."


# ---------------------------------------------------------------- landing

def render_landing(data, boards=None):
    boards = BOARDS if boards is None else boards
    copy = landing_copy(boards)
    counts = {}
    for b in boards:
        counts[b] = (
            sum(1 for t in data["terms"] if b in t["boards"]),
            sum(1 for f in data["formulae"] if b in f["boards"]),
        )
    crumbs = [("Home", "/"), ("Revision Notes", "/revision-notes/"),
              ("Glossary", None)]

    cards = []
    for b, meta in boards.items():
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
              {copy["intro"]}
            </p>
            <p class="gl-intro">
              Every definition comes from the
              <a href="/revision-notes/">revision notes</a> on this
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
              <a href="/practice-questions/" class="button"
                >Practice Questions</a
              >
              <a href="/past-paper-questions/" class="button"
                >Search Past Paper Questions</a
              >
              <a href="/revision-notes/" class="button"
                >Revision Notes</a
              >
            </div>
          </section>
{SERVICES_CTA}"""

    ld = {
        "@context": "https://schema.org",
        "@type": "CollectionPage",
        "name": "A-Level Economics Glossary",
        "description": copy["meta"],
        "url": f"{SITE}/revision-notes/glossary/",
        "inLanguage": "en-GB",
        "isPartOf": {"@type": "WebSite", "name": "Economics Academy", "url": SITE},
        "publisher": shell.ORGANISATION_REF,
        "hasPart": [
            {"@type": "DefinedTermSet",
             "name": f"{m['long']} Glossary",
             "url": f"{SITE}/revision-notes/glossary/{m['slug']}/"}
            for m in boards.values()
        ],
    }

    return page_shell(
        title="A-Level Economics Glossary — Key Terms & Formulae | Economics Academy",
        desc=copy["meta"],
        path="/revision-notes/glossary/",
        crumbs=crumbs, body=body, jsonld=ld,
    )


# ---------------------------------------------------------------- main

# extract_glossary.py's staged run (D68). Read to validate, never published.
STAGED_TERMS = ROOT / "_working" / "glossary" / "staged" / "terms.json"


def render_all(data, tax, boards) -> dict:
    """{path: page source} for the landing page and each board's page.
    Raises BuildError on the first class of failure, writing nothing."""
    groups = taxonomy_groups(tax, boards)
    errs = validate(data, groups, boards)
    if errs:
        raise BuildError(f"{len(errs)} problem(s), nothing written:\n"
                         + "\n".join(f"  - {x}" for x in errs))

    # Display maths: every formula, plus any \[ \] inside a definition. The
    # second set is empty for Edexcel A and AQA, so their render is unchanged.
    latex = [f["latex"] for f in data["formulae"]]
    seen = set(latex)
    for t in data["terms"]:
        for s in t["sources"]:
            for m in DISPLAY_TEX.findall(s["definitionHtml"]
                                         + s.get("definitionListHtml", "")):
                m = html.unescape(m).strip()
                if m not in seen:
                    seen.add(m)
                    latex.append(m)
    rendered_map = dict(zip(latex, katex(latex)))
    inline = sorted({
        html.unescape(m).strip()
        for t in data["terms"] for s in t["sources"]
        for m in INLINE_TEX.findall(s["definitionHtml"]
                                    + s.get("definitionListHtml", ""))
    })
    inline_map = dict(zip(inline, _katex(inline, False)))

    pages = {OUT_DIR / "index.html": render_landing(data, boards)}
    for board in boards:
        pages[OUT_DIR / boards[board]["slug"] / "index.html"] = render_board(
            data, board, groups, rendered_map, inline_map, boards)

    for path, source in pages.items():
        leftover = re.search(r"\\\(|\\\[", source)
        if leftover:
            i = leftover.start()
            raise BuildError(f"{path.relative_to(ROOT)} still contains raw "
                             f"LaTeX at {source[i:i + 60]!r} - it was not "
                             f"pre-rendered")
    return pages


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--check",
        action="store_true",
        help="validate the INPUTS and write nothing. This does not check that "
             "committed output is current - use scripts/verify_generated.py "
             "for that",
    )
    args = ap.parse_args()

    data = json.loads(DATA.read_text(encoding="utf-8"))
    tax = json.loads(TAXONOMY.read_text(encoding="utf-8"))

    try:
        pages = render_all(data, tax, BOARDS)
    except BuildError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    # STAGED boards (D68): every page rendered again, in memory, from
    # extract_glossary.py's staged run, with every check above - and nothing
    # written. That includes the live boards' pages as they would be at
    # launch, so their three-board copy is validated too.
    staged = sorted(set(STAGED_BOARDS) - set(BOARDS))
    if staged:
        if not STAGED_TERMS.is_file():
            print(f"error: {', '.join(staged)} glossary is staged and "
                  f"{STAGED_TERMS.relative_to(ROOT)} is missing - run "
                  f"scripts/extract_glossary.py first", file=sys.stderr)
            return 1
        try:
            staged_pages = render_all(
                json.loads(STAGED_TERMS.read_text(encoding="utf-8")), tax,
                STAGED_BOARDS)
        except BuildError as exc:
            print(f"error (staged {', '.join(staged)}): {exc}", file=sys.stderr)
            return 1
        print(f"  validated the staged {', '.join(staged)} glossary: "
              f"{len(staged_pages)} pages rendered in memory, none written")

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
    print(f"  {len(urls)} page URLs; run scripts/build_sitemap.py for the sitemap")
    # scripts/prettier_util.py: one call site, one pinned version, and it
    # STOPS the build if npx is missing rather than writing unformatted pages
    # and warning. Generating and formatting are one step so that re-running
    # is idempotent - otherwise every run would undo the formatting and the
    # files would churn in `git diff` forever.
    print(f"  formatted {prettier_util.format_files(list(pages))} page(s)")
    # Wave 2 Phase 7. After Prettier, never before - see shell.bake_files().
    print(f"  baked the header and footer into "
          f"{shell.bake_files(list(pages))} page(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())

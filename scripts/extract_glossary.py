#!/usr/bin/env python3
"""Extract the glossary from the revision notes. Verbatim, never rewritten.

    python3 scripts/extract_glossary.py            # extract and write
    python3 scripts/extract_glossary.py --check    # validate, write nothing

Reads the 166 topic pages under revision-notes/ and writes
glossary-data/terms.json plus the human-readable _working/glossary/inventory.md.

The one rule this script exists to enforce: **a definition is whatever the notes
page already says.** Nothing here paraphrases, tidies or completes a definition.
A term that reads badly is fixed on the notes page and re-extracted; it is never
edited downstream. scripts/verify_glossary.py re-reads the notes afterwards and
fails if a shipped definition no longer appears in its source page.

Where the definitions actually are
----------------------------------
The notes mark a key term as <span class="key-definition">Term:</span> and then
let the definition run on as the rest of the enclosing <p> or <li>. The span
holds the term ONLY - no chip anywhere on the site exceeds six words. So the
definition is the block's remaining children, not the span's contents.

Why a real parser and not a regex
---------------------------------
Three of the twelve gotchas recorded in _working/glossary/PROGRESS.md are cases
where a regex quietly gets the wrong answer: Prettier splits `</span\n>` on 65
chips, the MathJax config block contains the literal strings "\\[" and "\\]" so
a naive formula grep hits all 125 MathJax pages, and a chip inside an <li> that
also contains a nested list has no non-greedy match that is correct. Building a
tree with html.parser costs about sixty lines and removes all three.

Standard library only, in keeping with the rest of scripts/. .venv exists solely
for the AQA PDF extractor and is not used here.
"""

from __future__ import annotations

import argparse
import collections
import hashlib
import html
import json
import pathlib
import re
import sys
import unicodedata
from html.parser import HTMLParser

ROOT = pathlib.Path(__file__).resolve().parent.parent
NOTES = ROOT / "revision-notes"
DATA = ROOT / "glossary-data"
TAXONOMY = ROOT / "past-paper-questions-data" / "taxonomy.json"
CURATION = DATA / "curation.json"
AUTHORED = DATA / "authored.json"
TERMS_OUT = DATA / "terms.json"
INVENTORY = ROOT / "_working" / "glossary" / "inventory.md"

SITE = "https://economicsacademy.co.uk"

# Inline markup kept inside a definition. Everything else is unwrapped to its
# text: the glossary reproduces the notes' words, not their layout.
KEEP = {"strong", "em", "sub", "sup", "a", "br"}
# Allowed only inside a captured continuation list, never in a paragraph.
LIST_KEEP = KEEP | {"li"}
VOID = {"br", "img", "hr", "input", "meta", "link", "source", "area", "base",
        "col", "embed", "param", "track", "wbr"}

SPEC_ALERT_RE = re.compile(
    r"Specification Coverage:\s*(AQA|Edexcel)\s+unit\s+([\d.]+)\s*"
    r"(?:[-–—]\s*)?(.*?)\.(?:\s|$)",
    re.S,
)
DISPLAY_TEX_RE = re.compile(r"\\\[(.+?)\\\]", re.S)
INLINE_TEX_RE = re.compile(r"\\\((.+?)\\\)", re.S)


# ---------------------------------------------------------------- tree

class Node:
    __slots__ = ("tag", "attrs", "children", "text", "parent")

    def __init__(self, tag=None, attrs=None, text=None, parent=None):
        self.tag = tag
        self.attrs = attrs or {}
        self.children = []
        self.text = text
        self.parent = parent

    def cls(self):
        return self.attrs.get("class", "")


class TreeBuilder(HTMLParser):
    """A minimal DOM. The notes parse cleanly - verify_html.py passes 176/176."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.root = Node("#root")
        self.cur = self.root
        self.skip = 0

    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style"):
            self.skip += 1
            return
        if self.skip or tag in VOID:
            if not self.skip and tag == "br":
                self.cur.children.append(Node("br", parent=self.cur))
            return
        node = Node(tag, dict(attrs), parent=self.cur)
        self.cur.children.append(node)
        self.cur = node

    def handle_endtag(self, tag):
        if tag in ("script", "style"):
            self.skip = max(0, self.skip - 1)
            return
        if self.skip or tag in VOID:
            return
        node = self.cur
        while node is not self.root and node.tag != tag:
            node = node.parent
        if node is not self.root:
            self.cur = node.parent

    def handle_data(self, data):
        if self.skip:
            return
        self.cur.children.append(Node(None, text=data, parent=self.cur))


def parse(source: str) -> Node:
    b = TreeBuilder()
    b.feed(source)
    b.close()
    return b.root


def text_of(node: Node) -> str:
    if node.tag is None:
        return node.text or ""
    if node.tag == "br":
        return " "
    return "".join(text_of(c) for c in node.children)


def squash(s: str) -> str:
    return re.sub(r"\s+", " ", s).strip()


def html_of(nodes) -> str:
    """Re-serialise, keeping only the inline tags a definition may carry."""
    out = []
    for n in nodes:
        if n.tag is None:
            out.append(html.escape(n.text or "", quote=False))
        elif n.tag == "br":
            out.append("<br />")
        elif n.tag in KEEP:
            if n.tag == "a" and "href" in n.attrs:
                href = html.escape(n.attrs["href"], quote=True)
                out.append(f'<a href="{href}">{html_of(n.children)}</a>')
            else:
                out.append(f"<{n.tag}>{html_of(n.children)}</{n.tag}>")
        else:
            out.append(html_of(n.children))
    return squash("".join(out))


def following_list(node: Node):
    """The <ul>/<ol> immediately after this block, if there is one.

    A handful of definitions end on a colon because the rest of them is the
    bulleted list that follows - "Quasi-public goods: goods that are either:".
    Read on its own the definition is a fragment, so the list is captured with
    it. Still the notes' own words; only the reach changes.
    """
    parent = node.parent
    if parent is None:
        return None
    kids = [c for c in parent.children if c.tag or squash(c.text or "")]
    try:
        i = kids.index(node)
    except ValueError:
        return None
    for nxt in kids[i + 1:]:
        if nxt.tag in ("ul", "ol"):
            return nxt
        if nxt.tag is None:
            continue
        return None
    return None


def list_html(node: Node) -> str:
    """Serialise a continuation list.

    Items are joined with a space, not butted together, so that the generator's
    output flattens to the same text as the file after Prettier has reformatted
    it. Without the space "…fossil fuels.Under-provision…" and
    "…fossil fuels. Under-provision…" differ, and verify_glossary reports the
    page as out of date on every run.
    """
    items = [f"<li>{html_of(c.children)}</li>"
             for c in node.children if c.tag == "li"]
    return f"<ul>{' '.join(items)}</ul>" if items else ""


def trim_dangling(definition: str) -> str:
    """Drop a trailing clause that only introduces content the glossary cannot
    show - "...with various market structures in between. The main market
    structures include:" loses the second sentence, and nothing else.

    Removal only. Nothing is added or reworded.
    """
    text = re.sub(r"<[^>]+>", "", definition)
    if not text.rstrip().endswith(":"):
        return definition
    cut = definition.rstrip()
    # Walk back to the end of the previous sentence.
    m = list(re.finditer(r"\.\s", cut))
    if not m:
        return definition
    return cut[: m[-1].end()].strip()


def walk(node: Node):
    for child in node.children:
        if child.tag:
            yield child
            yield from walk(child)


def find(node: Node, tag: str):
    for n in walk(node):
        if n.tag == tag:
            return n
    return None


def has_descendant(node: Node, tag: str) -> bool:
    return any(n.tag == tag for n in walk(node))


# ---------------------------------------------------------------- slugs

def slugify(s: str) -> str:
    s = unicodedata.normalize("NFKD", s)
    s = "".join(c for c in s if not unicodedata.combining(c))
    s = s.lower().replace("&", " and ")
    s = re.sub(r"[^a-z0-9]+", "-", s)
    return re.sub(r"-{2,}", "-", s).strip("-")


def canonical_key(term: str) -> str:
    """The key two pages must share for their definitions to be one entry."""
    t = squash(term).rstrip(":.").strip()
    t = re.sub(r"^(the|a|an)\s+", "", t, flags=re.I)
    return t.lower()


def letter_of(term: str) -> str:
    """Which A-Z section a term files under.

    Called with the canonical key, not the display name, so a leading article
    is ignored - "The Law of Demand" files under L and "A demerger" under D,
    the way any index or library catalogue treats them. The display name keeps
    its article.
    """
    for ch in term:
        if ch.isalpha():
            return ch.upper()
    return "#"


# ---------------------------------------------------------------- pages

def board_index():
    """notesDir -> board and group metadata, straight from taxonomy.json.

    The taxonomy already carries every name the glossary needs and is itself
    generated from the notes, so redeclaring any of it here would create a
    second source of truth that could drift.
    """
    tax = json.loads(TAXONOMY.read_text(encoding="utf-8"))
    out = {}
    for b in tax["boards"]:
        for g in b["groups"]:
            out[g["notesDir"]] = {
                "board": "edexcel-a" if b["slug"] == "edexcel" else b["slug"],
                "boardName": b["name"],
                "qualification": b.get("qualification", ""),
                "group": g["slug"],
                "groupLabel": g["label"],
                "groupName": g["name"],
            }
    return out


def page_meta(root: Node, path: pathlib.Path, meta, problems):
    """Board, spec code and topic title, taken from the spec-alert line.

    Not from the JSON-LD: its isPartOf names have about twenty inconsistent
    variants across the 166 pages, whereas 161 spec-alerts match this shape
    exactly and the five that do not differ only by a missing ' - ' separator,
    which the optional dash in the pattern absorbs.
    """
    alert = next((n for n in walk(root) if "spec-alert" in n.cls()), None)
    rel = path.relative_to(ROOT).as_posix()
    if alert is None:
        problems.append(f"{rel}: no spec-alert block")
        return None
    m = SPEC_ALERT_RE.search(squash(text_of(alert)))
    if not m:
        problems.append(f"{rel}: spec-alert does not parse")
        return None

    stated = "edexcel-a" if m.group(1) == "Edexcel" else "aqa"
    if stated != meta["board"]:
        problems.append(
            f"{rel}: spec-alert says {m.group(1)} but the file is in "
            f"{path.parent.name}"
        )

    h1 = find(root, "h1")
    return {
        **meta,
        "spec": m.group(2),
        "topic": squash(m.group(3)),
        "h1": squash(text_of(h1)) if h1 else "",
        "notesUrl": f"/{rel}",
        "sourceFile": rel,
    }


def chips_on(root: Node, ctx, stop, problems, attach=frozenset()):
    """Every term and definition on one page, plus what was deliberately skipped.

    `attach` is the set of canonical keys whose following list completes the
    definition even though the chip's text does not end on a colon - see the
    comment at the bottom of this function.
    """
    kept, skipped = [], []
    heading = ""

    for node in walk(root):
        if node.tag in ("h2", "h3"):
            heading = squash(text_of(node))
            continue
        if node.tag not in ("p", "li"):
            continue

        chip = next((c for c in node.children
                     if c.tag == "span" and "key-definition" in c.cls()), None)
        if chip is None:
            continue

        before = node.children[: node.children.index(chip)]
        after = node.children[node.children.index(chip) + 1:]

        # Gotcha 4: a chip that is not the first content in its block is an
        # inline highlight, and the definition wraps around it rather than
        # following it. There is no verbatim term/definition pair to take.
        if squash(html_of(before)):
            skipped.append(("mid-sentence highlight", squash(text_of(chip)), node))
            continue

        raw = squash(text_of(chip))
        term = raw.rstrip(":").strip()
        definition = html_of(after)

        # Gotcha 6: a generic "Definition:" chip names no term. The term is the
        # section heading it sits under - taken verbatim, not tidied. Headings
        # are written as prose ("What Is LRAS?", "The SRAS Curve: A Recap"), so
        # every one of these lands in the review file for a human to name. The
        # definition itself is untouched either way.
        from_heading = False
        if term.lower() in ("definition", "definitions") and heading:
            term, from_heading = heading, True

        if not definition:
            skipped.append(("chip with no definition text", term, node))
            continue
        if canonical_key(term) in stop:
            skipped.append(("stop-listed label", term, node))
            continue

        # A definition ending on a colon is a fragment. Take the list that
        # completes it where there is one; otherwise drop the dangling clause.
        #
        # Five trading-bloc chips need the same treatment for a different
        # reason: they give an example where a definition is expected - "Free
        # trade area: e.g. USMCA" - and the defining characteristics are the
        # bulleted list underneath. There is no punctuation that says so, so
        # curation names them in attachList and the list is taken exactly as a
        # trailing colon would take it. Still the notes' own words, and still
        # covered by the verbatim check, which reads the list too.
        definition_list = ""
        list_is_definition = False
        dangling = squash(re.sub(r"<[^>]+>", "", definition)).endswith(":")
        attached = canonical_key(term) in attach
        if dangling or attached:
            lst = following_list(node)
            if lst is not None:
                definition_list = list_html(lst)
                # For an attachList chip the list IS the definition and the
                # paragraph is only an example, so the page renders it first.
                # For a colon-ended one the paragraph opens the sentence the
                # list finishes, and the order has to stay as written.
                list_is_definition = attached and not dangling
            elif dangling:
                definition = trim_dangling(definition)

        kept.append({
            "term": term,
            "key": canonical_key(term),
            "definitionHtml": definition,
            "definitionListHtml": definition_list,
            "listIsDefinition": list_is_definition,
            # From the definition as kept, so a trim is reflected here too.
            "definitionText": squash(re.sub(r"<[^>]+>", "", definition)),
            "heading": heading,
            "origin": "chip",
            "fromHeading": from_heading,
            # The notes signal a definition with a trailing colon on the chip.
            # 483 chips have one. The 69 that do not are mostly still
            # definitions written as a sentence ("Globalisation is the
            # increasing integration..."), so they are kept - but flagged,
            # because a handful are the term used as a sentence subject rather
            # than defined. Deciding which is which is a judgement about
            # wording, so it goes to the review file, not into this script.
            "chipHasColon": raw.endswith(":"),
            **ctx,
        })

    return kept, skipped


DEF_COLUMN_WORDS = ("definition", "meaning", "what it means", "description")


def tables_on(root: Node, ctx):
    """concept-tables that carry a definition column, with their rows.

    A handful of terms are defined only in a comparison table - the factors of
    production, and the three efficiency types, whose chips elsewhere are Yes/No
    verdicts rather than definitions. Harvesting a table means choosing which
    column is the term and which is the definition, which is a judgement, so
    nothing here is used until it appears in curation["tables"]. Until then
    every candidate is listed in the review file with all of its rows.
    """
    out = []
    index = 0
    for node in walk(root):
        if node.tag != "table" or "concept-table" not in node.cls():
            continue
        this, index = index, index + 1
        head = find(node, "thead")
        if head is None:
            continue
        headers = [squash(text_of(th)) for th in walk(head) if th.tag == "th"]
        if not any(w in h.lower() for h in headers for w in DEF_COLUMN_WORDS):
            continue
        rows = []
        for tr in walk(node):
            if tr.tag != "tr":
                continue
            cells = [c for c in tr.children if c.tag in ("td", "th")]
            if cells and all(c.tag == "td" for c in cells):
                rows.append([html_of(c.children) for c in cells])
        out.append({"table": this, "headers": headers, "rows": rows, **ctx})
    return out


def harvest_tables(candidates, approved, stop):
    """Turn the approved (page, table, term column, definition column) into terms."""
    index = {(a["notesUrl"], a["table"]): a for a in approved}
    kept = []
    for c in candidates:
        a = index.get((c["notesUrl"], c["table"]))
        if a is None:
            continue
        for row in c["rows"]:
            if max(a["termColumn"], a["definitionColumn"]) >= len(row):
                continue
            term = squash(re.sub(r"<[^>]+>", "", row[a["termColumn"]]))
            definition = row[a["definitionColumn"]]
            if not term or not definition or canonical_key(term) in stop:
                continue
            kept.append({
                "term": term,
                "key": canonical_key(term),
                "definitionHtml": definition,
                "definitionText": squash(re.sub(r"<[^>]+>", "", definition)),
                "definitionListHtml": "",
                "heading": "",
                "origin": "table",
                "fromHeading": False,
                "chipHasColon": True,
                **{k: v for k, v in c.items()
                   if k not in ("table", "headers", "rows")},
            })
    return kept


def formulae_on(root: Node, ctx):
    """Display formulae only.

    The notes carry 219 display formulae and 375 inline ones, but the inline
    ones are overwhelmingly fragments inside a sentence - `MC = MR`, `P \\times
    Q` - rather than statements of a formula a student has to learn. Taking
    only display keeps the glossary's formula list to things that stand alone.
    The inline count is reported for the gap report.
    """
    out = []
    heading = ""
    for node in walk(root):
        if node.tag in ("h2", "h3"):
            heading = squash(text_of(node))
            continue
        # Gotcha 8: a formula-box is not 1:1 with a formula - it may hold a
        # label paragraph, a gloss and two equations. Scan the leaf blocks and
        # split per \[...\], so a box with two equations yields two records.
        if node.tag == "p":
            pass
        elif "formula-box" in node.cls() and not has_descendant(node, "p"):
            pass
        else:
            continue
        body = text_of(node)
        for m in DISPLAY_TEX_RE.finditer(body):
            latex = squash(m.group(1))
            out.append({
                "latex": latex,
                "key": squash(re.sub(r"\s+", " ", latex)),
                "label": heading,
                "origin": "notes",
                # Gotcha 7: two display formulae live in <p><strong>, outside
                # any formula-box. Recorded so the gap report can show them.
                "inFormulaBox": "formula-box" in (node.parent.cls() if node.parent else "")
                                or "formula-box" in node.cls(),
                **ctx,
            })
    return out


# ---------------------------------------------------------------- merge

def load_authored(page_ctx, problems):
    """The authored layer: definitions written for the glossary, not lifted.

    Everything else in this file reproduces the notes word for word. These do
    not - they cover concepts the notes teach without ever defining, and the
    specification requires. They are kept in their own file, tagged
    origin="authored" all the way through to the page, and excluded from the
    verbatim check in verify_glossary.py, because there is nothing in the notes
    for them to match.

    Each entry names the notes page that teaches the concept, and borrows that
    page's real board, unit and topic metadata, so an authored entry links and
    files exactly like an extracted one. The page must exist and must belong to
    the board claimed, or the build fails.

    The intent is that this file shrinks: once a definition is added to its
    notes page as a key-definition chip, the extractor picks it up and the
    entry here becomes a duplicate, which is reported as an error.
    """
    if not AUTHORED.is_file():
        return [], []
    data = json.loads(AUTHORED.read_text(encoding="utf-8"))
    terms, formulae = [], []

    # group slug -> a representative context, for entries with no page to cite
    by_group = {}
    for ctx in page_ctx.values():
        by_group.setdefault((ctx["board"], ctx["group"]), ctx)

    for entry in data.get("terms", []):
        for board in entry["boards"]:
            url = entry.get("notes", {}).get(board)
            if url:
                ctx = page_ctx.get(url)
                if ctx is None:
                    problems.append(f"authored '{entry['term']}': {url} is not a "
                                    f"topic page")
                    continue
                if ctx["board"] != board:
                    problems.append(f"authored '{entry['term']}': {url} is a "
                                    f"{ctx['board']} page, not {board}")
                    continue
            else:
                # No page teaches this yet - four quantitative-skills concepts
                # are in both specifications and on no page. Rather than link a
                # student to a page that does not cover it, the entry ships with
                # no source link and says so.
                group = entry.get("group", {}).get(board)
                base = by_group.get((board, group))
                if base is None:
                    problems.append(f"authored '{entry['term']}': needs either a "
                                    f"notes page or a valid group for {board}")
                    continue
                ctx = {**base, "spec": "", "topic": "", "notesUrl": "",
                       "sourceFile": "", "h1": ""}
            terms.append({
                "term": entry["term"],
                "key": canonical_key(entry["term"]),
                "definitionHtml": entry["definition"],
                "definitionText": re.sub(r"<[^>]+>", "", entry["definition"]),
                "definitionListHtml": "",
                "heading": "",
                "origin": "authored",
                "fromHeading": False,
                "chipHasColon": True,
                **ctx,
            })

    for entry in data.get("formulae", []):
        for board in entry["boards"]:
            url = entry["notes"].get(board)
            ctx = page_ctx.get(url) if url else None
            if ctx is None or ctx["board"] != board:
                problems.append(f"authored formula '{entry['label']}': bad notes "
                                f"page for {board} - {url}")
                continue
            formulae.append({
                "latex": entry["latex"],
                "key": squash(entry["latex"]),
                "label": entry["label"],
                "inFormulaBox": True,
                "origin": "authored",
                **ctx,
            })
    return terms, formulae


def merge(records):
    """Group per-page records into one entry per key, keeping every source."""
    grouped = {}
    for r in records:
        entry = grouped.setdefault(r["key"], {"key": r["key"], "sources": []})
        entry["sources"].append(r)
    return grouped


def build():
    problems, notes = [], []
    curation = json.loads(CURATION.read_text(encoding="utf-8"))
    stop = {canonical_key(s) for s in curation.get("stopTerms", [])}
    aliases = {canonical_key(k): v for k, v in curation.get("aliases", {}).items()}
    display = curation.get("display", {})
    # Some chips are not definitions of the term they label. The three
    # efficiency types are the clear case: on the market-structure pages the
    # chip introduces a Yes/No verdict about that structure ("No - the firm
    # does not produce where P = MC..."), not a definition. Curation can drop
    # those sources, and rank the ones that do define the term first.
    exclude_src = {canonical_key(k): set(v)
                   for k, v in curation.get("excludeSources", {}).items()}
    prefer_src = {canonical_key(k): list(v)
                  for k, v in curation.get("preferredSources", {}).items()}
    # Chips whose following list is the definition - see chips_on().
    attach = {canonical_key(k) for k in curation.get("attachList", [])}
    boards = board_index()

    term_records, formula_records, table_candidates = [], [], []
    page_ctx = {}
    skipped_all, inline_count, page_count = [], 0, 0

    for notes_dir in sorted(boards):
        for path in sorted((NOTES / notes_dir).glob("*.html"),
                           key=lambda p: [int(x) if x.isdigit() else x
                                          for x in re.split(r"(\d+)", p.name)]):
            if path.name == "index.html":
                continue
            page_count += 1
            root = parse(path.read_text(encoding="utf-8"))
            ctx = page_meta(root, path, boards[notes_dir], problems)
            if ctx is None:
                continue
            body = next((n for n in walk(root)
                         if "notes-container" in n.cls()), root)
            page_ctx[ctx["notesUrl"]] = ctx
            kept, skipped = chips_on(body, ctx, stop, problems, attach)
            term_records.extend(kept)
            skipped_all.extend((ctx["sourceFile"], why, t)
                               for why, t, _ in skipped)
            formula_records.extend(formulae_on(body, ctx))
            table_candidates.extend(tables_on(body, ctx))
            inline_count += len(INLINE_TEX_RE.findall(text_of(body)))

    term_records.extend(
        harvest_tables(table_candidates, curation.get("tables", []), stop))

    # Order matters here. Aliases first, so a merge is seen; then exclusions, so
    # a source curation has dropped is gone before anything else looks at it;
    # only then the authored layer, whose duplicate check must not fire against
    # a source that is no longer in play.
    for r in term_records:
        r["key"] = aliases.get(r["key"], r["key"])
    term_records = [r for r in term_records
                    if r["notesUrl"] not in exclude_src.get(r["key"], ())]

    authored, authored_formulae = load_authored(page_ctx, problems)
    for r in authored:
        r["key"] = aliases.get(r["key"], r["key"])
    extracted_keys = {(r["key"], r["board"]) for r in term_records}
    for r in authored:
        if (r["key"], r["board"]) in extracted_keys:
            problems.append(
                f"authored.json defines '{r['term']}' for {r['board']}, but the "
                f"notes now define it too. Remove it from authored.json - the "
                f"notes are the better source")
    term_records.extend(authored)
    formula_records.extend(authored_formulae)

    terms = []
    for key, entry in sorted(merge(term_records).items()):
        # Exclusions were applied before the authored layer was merged in, so
        # that an authored entry can deliberately replace an excluded chip on
        # the same page. Filtering again here would drop it.
        srcs = entry["sources"]
        rank = prefer_src.get(key, [])
        srcs.sort(key=lambda s: (rank.index(s["notesUrl"])
                                 if s["notesUrl"] in rank else len(rank),
                                 s["board"], s["spec"]))
        variants = {s["definitionHtml"] for s in srcs}
        pretty = display.get(key) or max((s["term"] for s in srcs), key=len)
        review = []
        if any(s["fromHeading"] for s in srcs):
            review.append("term taken from a section heading, needs naming")
        if not any(s["chipHasColon"] for s in srcs):
            review.append("chip has no colon - confirm this is a definition")
        if len(variants) > 1:
            review.append(f"{len(variants)} different wordings across its sources")
        if any(s["definitionText"].rstrip().endswith(":")
               and not s.get("definitionListHtml") for s in srcs):
            review.append("definition ends in a colon - it runs on into a list")

        terms.append({
            "id": slugify(pretty),
            "term": pretty,
            "key": key,
            "letter": letter_of(key),
            "boards": sorted({s["board"] for s in srcs}),
            "origin": sorted({s["origin"] for s in srcs}),
            "definitionVariants": len(variants),
            "review": review,
            "sources": [{
                "board": s["board"],
                "group": s["group"],
                "groupLabel": s["groupLabel"],
                "spec": s["spec"],
                "topic": s["topic"],
                "notesUrl": s["notesUrl"],
                "termAsWritten": s["term"],
                "origin": s["origin"],
                "definitionHtml": s["definitionHtml"],
                "definitionListHtml": s.get("definitionListHtml", ""),
                "listIsDefinition": s.get("listIsDefinition", False),
            } for s in srcs],   # already ranked: curated preference, then board
        })

    seen = {}
    for t in terms:
        if t["id"] in seen:
            problems.append(
                f"slug collision: '{t['term']}' and '{seen[t['id']]}' both give "
                f"id '{t['id']}' - add an alias or a display override to "
                f"glossary-data/curation.json"
            )
        seen[t["id"]] = t["term"]

    formulae = []
    f_exclude = set(curation.get("formulaExclude", []))
    f_label = curation.get("formulaLabel", {})
    for key, entry in sorted(merge(formula_records).items()):
        srcs = entry["sources"]
        formulae.append({
            "id": "f-" + slugify(srcs[0]["label"] or srcs[0]["topic"])[:60],
            "latex": srcs[0]["latex"],
            "label": srcs[0]["label"] or srcs[0]["topic"],
            "boards": sorted({s["board"] for s in srcs}),
            "outsideFormulaBox": not any(s["inFormulaBox"] for s in srcs),
            "sources": [{
                "board": s["board"],
                "group": s["group"],
                "spec": s["spec"],
                "topic": s["topic"],
                "notesUrl": s["notesUrl"],
            } for s in sorted(srcs, key=lambda s: (s["board"], s["spec"]))],
        })

    # Formula ids come from the section heading, and one heading often carries
    # several formulae, so they collide. Disambiguate with a short hash OF THE
    # FORMULA, never with a positional counter.
    #
    # A counter was the first attempt and it silently mislabelled two formulae.
    # Records are sorted by their LaTeX, so escaping a stray % - a one-character
    # correction on a notes page - moved one formula past another, the -2 suffix
    # landed on the wrong one, and the curated labels for "Real GDP Growth" and
    # "Real GDP per Capita" swapped. Hashing the LaTeX makes an id depend only
    # on the formula it names, so an unrelated edit cannot move it.
    base_count = collections.Counter(f["id"] for f in formulae)
    for f in formulae:
        if base_count[f["id"]] > 1:
            digest = hashlib.sha1(f["latex"].encode("utf-8")).hexdigest()[:4]
            f["id"] = f"{f['id']}-{digest}"
    for f in formulae:
        f["label"] = f_label.get(f["id"], f["label"])
    formulae = [f for f in formulae if f["id"] not in f_exclude]

    stats = {
        "pages": page_count,
        "authoredTerms": len({r["key"] for r in authored}),
        "authoredFormulae": len({f["key"] for f in authored_formulae}),
        "termsExtracted": len(term_records),
        "uniqueTerms": len(terms),
        "termsOnBothBoards": sum(1 for t in terms if len(t["boards"]) > 1),
        "termsWithVariantDefinitions": sum(1 for t in terms
                                           if t["definitionVariants"] > 1),
        "termsNeedingReview": sum(1 for t in terms if t["review"]),
        "displayFormulae": len(formula_records),
        "uniqueFormulae": len(formulae),
        "formulaeExcludedByCuration": len(f_exclude),
        "tableCandidates": len(table_candidates),
        "tablesApproved": len(curation.get("tables", [])),
        "termsFromTables": sum(1 for r in term_records if r["origin"] == "table"),
        "inlineFormulaeNotExtracted": inline_count,
        "chipsSkipped": len(skipped_all),
    }
    return terms, formulae, stats, skipped_all, problems, table_candidates, curation


# ---------------------------------------------------------------- output

def write_inventory(terms, formulae, stats, skipped):
    """The whole inventory, rewritten each run.

    Deliberately not appended incrementally: extraction over 166 pages takes a
    couple of seconds and is deterministic, so a complete rewrite is both safer
    than a partial append and always consistent with terms.json.
    """
    L = ["# Glossary inventory",
         "",
         "Generated by `scripts/extract_glossary.py`. Do not hand-edit — re-run it.",
         "Judgement belongs in `glossary-data/curation.json`, which this never touches.",
         "",
         "## Totals", "",
         "| Measure | Count |", "| --- | ---: |"]
    L += [f"| {k} | {v} |" for k, v in stats.items()]

    L += ["", "## Terms", "",
          "`T` numbers match this run only — they come from the sort order and "
          "shift as curation lands. `B` = boards defining it. `V` = distinct "
          "definition wordings across its sources; anything above 1 is a "
          "gap-report item.", "",
          "| # | Term | B | V | Sources |", "| ---: | --- | --- | ---: | --- |"]
    for i, t in enumerate(terms, 1):
        b = "".join("E" if s == "edexcel-a" else "A" for s in t["boards"])
        src = ", ".join(f"{s['groupLabel']} {s['spec']}" for s in t["sources"])
        L.append(f"| **T{i}** | {t['term']} | {b} | {t['definitionVariants']} | {src} |")

    L += ["", "## Display formulae", "",
          "`B` numbers match section B of `review-decisions.md`.", "",
          "| # | Label | LaTeX | Boards | In formula-box |",
          "| ---: | --- | --- | --- | --- |"]
    for i, f in enumerate(formulae, 1):
        tex = f["latex"].replace("|", "\\|")
        b = "".join("E" if s == "edexcel-a" else "A" for s in f["boards"])
        L.append(f"| **B{i}** | {f['label']} | `{tex}` | {b} | "
                 f"{'no' if f['outsideFormulaBox'] else 'yes'} |")

    L += ["", "## Chips deliberately not extracted", "",
          "None of these is a term/definition pair. Listed so the decision is "
          "auditable rather than silent.", "",
          "| # | Page | Reason | Chip |", "| ---: | --- | --- | --- |"]
    for i, (page, why, term) in enumerate(skipped, 1):
        L.append(f"| **X{i}** | {page} | {why} | {term} |")

    INVENTORY.write_text("\n".join(L) + "\n", encoding="utf-8")


def write_review(terms, formulae, tables, curation):
    """Everything the extractor refused to decide, in one reviewable file.

    Regenerated on every run, so it shrinks as decisions land in curation.json.
    An empty section means that class of question is settled.
    """
    approved = {(a["notesUrl"], a["table"]) for a in curation.get("tables", [])}

    def flagged(reason):
        # Substring, not prefix: the variant-count reason reads "3 different
        # wordings across its sources" and leads with the count.
        return [t for t in terms if any(reason in r for r in t["review"])]

    L = ["# Glossary — decisions needed",
         "",
         "Generated by `scripts/extract_glossary.py`. Every item here is a question "
         "about **which text is a definition**, never about what a definition should "
         "say. Record answers in `glossary-data/curation.json` and re-run; this file "
         "shrinks as they land.",
         "",
         "Sections A–B are additions. C–F are corrections. G is a confirmation.",
         "",
         "## How to reply",
         "",
         "Every row is numbered. Quote the numbers and nothing else — for example:",
         "",
         "```",
         "A: 6 and 9 yes, rest no",
         "B: exclude 6, 12, 15. Rename 1 to \"Aggregate Demand\"",
         "C: 2, 5, 11 -> stop-list. Rest fine",
         "D: all fine except 17",
         "E: 3, 8 -> use the Edexcel wording. 14 -> exclude the 1.5.4 source",
         "G: all confirmed except M7",
         "```",
         "",
         "**The numbers are for this round only.** They come from the current sort "
         "order, so they will shift once decisions land and the file regenerates. "
         "Answer against this version.",
         "",
         "---",
         "",
         f"## A. Table harvests — {len(tables) - len(approved)} of {len(tables)} still undecided",
         "",
         "These `concept-table`s carry a definition-style column. Some genuinely "
         "define terms; some are classification grids that only look like it. For "
         "each one to use, add the entry shown to `curation.tables`; for the rest, "
         "do nothing.",
         "",
         "| # | Page | Table | Headers | Rows | State |",
         "| ---: | --- | ---: | --- | ---: | --- |"]
    for i, c in enumerate(tables, 1):
        state = "APPROVED" if (c["notesUrl"], c["table"]) in approved else "undecided"
        L.append(f"| **A{i}** | {c['groupLabel']} {c['spec']} | {c['table']} | "
                 f"{' / '.join(c['headers'])} | {len(c['rows'])} | {state} |")
    L.append("")

    for i, c in enumerate(tables, 1):
        state = "APPROVED" if (c["notesUrl"], c["table"]) in approved else "undecided"
        L += [f"### A{i}. {c['groupLabel']} {c['spec']} — table {c['table']} — **{state}**",
              "",
              f"`{c['notesUrl']}`", "",
              "| " + " | ".join(f"{i}. {h}" for i, h in enumerate(c["headers"])) + " |",
              "| " + " | ".join("---" for _ in c["headers"]) + " |"]
        for row in c["rows"]:
            L.append("| " + " | ".join(x.replace("|", "\\|")[:120] for x in row) + " |")
        # Suggest the column whose own header says it holds definitions, rather
        # than assuming column 1 - on the efficiency tables that is column 2,
        # and column 1 holds the condition.
        def_col = next((i for i, h in enumerate(c["headers"]) if i > 0
                        and any(w in h.lower() for w in DEF_COLUMN_WORDS)), 1)
        L += ["", "```json",
              json.dumps({"notesUrl": c["notesUrl"], "table": c["table"],
                          "termColumn": 0, "definitionColumn": def_col}),
              "```", ""]

    L += ["---", "",
          f"## B. Formulae — {len(formulae)} extracted", "",
          "Every display formula in the notes. Some are worked arithmetic from an "
          "example rather than a formula to learn — add those ids to "
          "`curation.formulaExclude`. Labels come from the section heading the "
          "formula sits under, so most want renaming via `curation.formulaLabel`.",
          "",
          "| # | label | LaTeX | boards | in a formula-box | id |",
          "| ---: | --- | --- | --- | --- | --- |"]
    for i, f in enumerate(formulae, 1):
        b = "".join("E" if s == "edexcel-a" else "A" for s in f["boards"])
        L.append(f"| **B{i}** | {f['label']} | "
                 f"`{f['latex'].replace('|', chr(92) + '|')}` | {b} | "
                 f"{'no' if f['outsideFormulaBox'] else 'yes'} | `{f['id']}` |")

    sections = [
        ("C", "Terms named from a section heading",
         "term taken from a section heading",
         "The chip said only `Definition:`, so the term had to come from the "
         "heading above it — and headings are written as prose. The definition "
         "is untouched; only the name needs deciding. Fix by adding an entry to "
         "`curation.aliases` (to merge into an existing term) or "
         "`curation.display` (to rename it)."),
        ("D", "Chips without a colon",
         "chip has no colon",
         "The notes signal a definition with a trailing colon on the chip. These "
         "have none. Most are still definitions written as a sentence "
         "(\"Globalisation is the increasing integration…\") and are fine as they "
         "stand. A few are the term used as a sentence subject rather than "
         "defined — add those to `curation.stopTerms`."),
        ("E", "Terms worded differently across their sources",
         "different wordings",
         "The same term is defined more than once and the wordings differ. Either "
         "align them in the notes, or name the page whose wording is canonical in "
         "`curation.preferredSources`. Where a source is not a definition at all "
         "— the three efficiency types are labelled Yes/No against each market "
         "structure — put it in `curation.excludeSources` instead."),
        ("F", "Definitions that run on into a list",
         "definition ends in a colon",
         "The definition ends mid-thought because the rest of it is the bulleted "
         "list that follows, which the extractor does not take. Either reword the "
         "notes page so the definition is self-contained, or accept the short form."),
    ]
    for letter, title, reason, blurb in sections:
        rows = flagged(reason)
        L += ["", "---", "", f"## {letter}. {title} — {len(rows)}", "", blurb, "",
              "| # | Term | Boards | Source(s) | Definition as extracted |",
              "| ---: | --- | --- | --- | --- |"]
        for i, t in enumerate(rows, 1):
            b = "".join("E" if s == "edexcel-a" else "A" for s in t["boards"])
            src = "<br>".join(f"{s['groupLabel']} {s['spec']}" for s in t["sources"])
            if letter == "E":
                # One line per source, each separately numbered, so a reply can
                # name a single wording to keep or drop rather than the term.
                d = "<br>".join(
                    f"**{letter}{i}.{j}** *{s['groupLabel']} {s['spec']}* — "
                    f"{s['definitionHtml'][:150]}"
                    for j, s in enumerate(t["sources"], 1))
            else:
                d = t["sources"][0]["definitionHtml"][:220]
            L.append(f"| **{letter}{i}** | {t['term']} | {b} | {src} | "
                     f"{d.replace('|', chr(92) + '|')} |")

    L += ["", "---", "",
          "## G. Curation already applied — please confirm", "",
          "These were decided from the evidence and are live in "
          "`glossary-data/curation.json`. None of them changes a single word of "
          "any definition; they only decide what counts as a term and what it is "
          "called.", "",
          f"### Stop-listed as rhetorical labels, not terms ({len(curation['stopTerms'])})",
          "",
          "| # | Label | # | Label | # | Label |", "| ---: | --- | ---: | --- | ---: | --- |"]
    stops = curation["stopTerms"]
    for i in range(0, len(stops), 3):
        cells = []
        for j, s in enumerate(stops[i:i + 3]):
            cells += [f"**S{i + j + 1}**", f"`{s}`"]
        cells += ["", ""] * (3 - len(stops[i:i + 3]))
        L.append("| " + " | ".join(cells) + " |")
    L += ["", f"### Merged ({len(curation['aliases'])})", "",
          "| # | Variant | Merged into |", "| ---: | --- | --- |"]
    for i, (k, v) in enumerate(sorted(curation["aliases"].items()), 1):
        L.append(f"| **M{i}** | {k} | {v} |")
    L += ["", f"### Renamed for display ({len(curation['display'])})", "",
          "| # | Key | Shown as |", "| ---: | --- | --- |"]
    for i, (k, v) in enumerate(sorted(curation["display"].items()), 1):
        L.append(f"| **R{i}** | {k} | {v} |")

    (INVENTORY.parent / "review-decisions.md").write_text(
        "\n".join(L) + "\n", encoding="utf-8")


def write_authored_review(terms, formulae):
    """Every authored definition, for review of the economics.

    These are the only entries on the site that are not the notes' own words,
    so they are the only ones whose economics needs checking by a person.
    """
    # One row per authored SOURCE, not per term. A term can be authored for one
    # board and lifted from a chip on the other - only the authored half needs
    # its economics checked, and showing the term's first source would display
    # the chip instead.
    auth = [(t, s) for t in terms for s in t["sources"]
            if s.get("origin") == "authored"]
    af = [f for f in formulae if any(s.get("origin") == "authored"
                                     for s in f["sources"])]
    L = ["# Authored definitions — for review",
         "",
         "Generated by `scripts/extract_glossary.py` from "
         "`glossary-data/authored.json`.",
         "",
         f"**{len(auth)} definitions and {len(af)} formulae written for the "
         "glossary.** Everything else on the site is the revision notes' own "
         "wording, lifted verbatim. These are not: they cover concepts the "
         "notes teach without defining, or that a specification requires and no "
         "page covers.",
         "",
         "**This is the list whose economics needs checking.** Correct anything "
         "wrong in `glossary-data/authored.json` and re-run the extractor and "
         "the builder.",
         "",
         "Better still, move one into its notes page as a `key-definition` "
         "chip: the extractor then picks it up, the entry here becomes a "
         "duplicate, and the build tells you to delete it. That is the intended "
         "direction of travel.",
         "",
         "`B` = the board this wording is for. Entries marked **no page** are required by "
         "a specification but covered by no notes page, so they ship without a "
         "source link and say so on the page.",
         "",
         "| # | Term | B | Definition | Where it links |",
         "| ---: | --- | --- | --- | --- |"]
    for i, (t, src) in enumerate(
            sorted(auth, key=lambda x: (x[0]["term"].lower(), x[1]["board"])), 1):
        b = "E" if src["board"] == "edexcel-a" else "A"
        where = (f"{src['groupLabel']} {src['spec']}" if src["notesUrl"]
                 else "**no page**")
        other = [o for o in t["sources"] if o.get("origin") != "authored"]
        if other:
            where += (" · the other board defines this itself, so only this "
                      "wording is authored")
        d = src["definitionHtml"].replace("|", "\\|")
        L.append(f"| **W{i}** | {t['term']} | {b} | {d} | {where} |")

    if af:
        L += ["", "## Authored formulae", "",
              "| # | Label | LaTeX | B |", "| ---: | --- | --- | --- |"]
        for i, f in enumerate(sorted(af, key=lambda x: x["label"].lower()), 1):
            b = "".join("E" if s == "edexcel-a" else "A" for s in f["boards"])
            L.append(f"| **F{i}** | {f['label']} | "
                     f"`{f['latex'].replace('|', chr(92) + '|')}` | {b} |")

    (INVENTORY.parent / "authored-review.md").write_text(
        "\n".join(L) + "\n", encoding="utf-8")


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--check", action="store_true",
                    help="validate and report, write nothing")
    args = ap.parse_args()

    terms, formulae, stats, skipped, problems, tables, curation = build()

    for k, v in stats.items():
        print(f"  {k:32} {v}")
    if problems:
        print(f"\n{len(problems)} problem(s):", file=sys.stderr)
        for p in problems:
            print(f"  - {p}", file=sys.stderr)

    if args.check:
        print("\n--check: nothing written")
        return 1 if problems else 0

    DATA.mkdir(exist_ok=True)
    TERMS_OUT.write_text(json.dumps({
        "source": "Generated by scripts/extract_glossary.py from the revision "
                  "notes. Do not hand-edit; re-run it. Hand-written judgement "
                  "belongs in glossary-data/curation.json.",
        "site": SITE,
        "stats": stats,
        "terms": terms,
        "formulae": formulae,
    }, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    write_inventory(terms, formulae, stats, skipped)
    write_review(terms, formulae, tables, curation)
    write_authored_review(terms, formulae)
    print(f"\nwrote {TERMS_OUT.relative_to(ROOT)}")
    print(f"wrote {INVENTORY.relative_to(ROOT)}")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())

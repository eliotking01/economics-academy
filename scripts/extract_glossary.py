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
TERMS_OUT = DATA / "terms.json"
INVENTORY = ROOT / "_working" / "glossary" / "inventory.md"

SITE = "https://economicsacademy.co.uk"

# Inline markup kept inside a definition. Everything else is unwrapped to its
# text: the glossary reproduces the notes' words, not their layout.
KEEP = {"strong", "em", "sub", "sup", "a", "br"}
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


def chips_on(root: Node, ctx, stop, problems):
    """Every term and definition on one page, plus what was deliberately skipped."""
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

        kept.append({
            "term": term,
            "key": canonical_key(term),
            "definitionHtml": definition,
            "definitionText": squash("".join(text_of(c) for c in after)),
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
                # Gotcha 7: two display formulae live in <p><strong>, outside
                # any formula-box. Recorded so the gap report can show them.
                "inFormulaBox": "formula-box" in (node.parent.cls() if node.parent else "")
                                or "formula-box" in node.cls(),
                **ctx,
            })
    return out


# ---------------------------------------------------------------- merge

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
    boards = board_index()

    term_records, formula_records, table_candidates = [], [], []
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
            kept, skipped = chips_on(body, ctx, stop, problems)
            term_records.extend(kept)
            skipped_all.extend((ctx["sourceFile"], why, t)
                               for why, t, _ in skipped)
            formula_records.extend(formulae_on(body, ctx))
            table_candidates.extend(tables_on(body, ctx))
            inline_count += len(INLINE_TEX_RE.findall(text_of(body)))

    term_records.extend(
        harvest_tables(table_candidates, curation.get("tables", []), stop))

    # Apply alias merges before grouping, so a curated alias genuinely unifies.
    for r in term_records:
        r["key"] = aliases.get(r["key"], r["key"])

    terms = []
    for key, entry in sorted(merge(term_records).items()):
        srcs = [s for s in entry["sources"]
                if s["notesUrl"] not in exclude_src.get(key, ())]
        if not srcs:
            problems.append(f"every source for '{key}' is excluded by curation")
            continue
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
        if any(s["definitionText"].rstrip().endswith(":") for s in srcs):
            review.append("definition ends in a colon - it runs on into a list")

        terms.append({
            "id": slugify(pretty),
            "term": pretty,
            "key": key,
            "letter": letter_of(pretty),
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

    # Formula ids are derived from a heading and collide readily; make unique.
    used = {}
    for f in formulae:
        base = f["id"]
        used[base] = used.get(base, 0) + 1
        if used[base] > 1:
            f["id"] = f"{base}-{used[base]}"
    for f in formulae:
        f["label"] = f_label.get(f["id"], f["label"])
    formulae = [f for f in formulae if f["id"] not in f_exclude]

    stats = {
        "pages": page_count,
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
          "`B` = boards defining it. `V` = distinct definition wordings across "
          "its sources; anything above 1 is a gap-report item.", "",
          "| Term | B | V | Sources |", "| --- | --- | ---: | --- |"]
    for t in terms:
        b = "".join("E" if s == "edexcel-a" else "A" for s in t["boards"])
        src = ", ".join(f"{s['groupLabel']} {s['spec']}" for s in t["sources"])
        L.append(f"| {t['term']} | {b} | {t['definitionVariants']} | {src} |")

    L += ["", "## Display formulae", "", "| Label | LaTeX | Boards | In formula-box |",
          "| --- | --- | --- | --- |"]
    for f in formulae:
        tex = f["latex"].replace("|", "\\|")
        b = "".join("E" if s == "edexcel-a" else "A" for s in f["boards"])
        L.append(f"| {f['label']} | `{tex}` | {b} | "
                 f"{'no' if f['outsideFormulaBox'] else 'yes'} |")

    L += ["", "## Chips deliberately not extracted", "",
          "None of these is a term/definition pair. Listed so the decision is "
          "auditable rather than silent.", "",
          "| Page | Reason | Chip |", "| --- | --- | --- |"]
    for page, why, term in skipped:
        L.append(f"| {page} | {why} | {term} |")

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
         "---",
         "",
         f"## A. Table harvests — {len(tables) - len(approved)} of {len(tables)} still undecided",
         "",
         "These `concept-table`s carry a definition-style column. Some genuinely "
         "define terms; some are classification grids that only look like it. For "
         "each one to use, add the entry shown to `curation.tables`; for the rest, "
         "do nothing.",
         ""]

    for c in tables:
        state = "APPROVED" if (c["notesUrl"], c["table"]) in approved else "undecided"
        L += [f"### {c['groupLabel']} {c['spec']} — table {c['table']} — **{state}**",
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
          "| id | label | LaTeX | boards | in a formula-box |",
          "| --- | --- | --- | --- | --- |"]
    for f in formulae:
        b = "".join("E" if s == "edexcel-a" else "A" for s in f["boards"])
        L.append(f"| `{f['id']}` | {f['label']} | `{f['latex'].replace('|', chr(92)+'|')}` "
                 f"| {b} | {'no' if f['outsideFormulaBox'] else 'yes'} |")

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
              "| Term | Boards | Source(s) | Definition as extracted |",
              "| --- | --- | --- | --- |"]
        for t in rows:
            b = "".join("E" if s == "edexcel-a" else "A" for s in t["boards"])
            src = "<br>".join(f"{s['groupLabel']} {s['spec']}" for s in t["sources"])
            if letter == "E":
                d = "<br>".join(f"*{s['spec']}* — {s['definitionHtml'][:150]}"
                                for s in t["sources"])
            else:
                d = t["sources"][0]["definitionHtml"][:220]
            L.append(f"| **{t['term']}** | {b} | {src} | {d.replace('|', chr(92)+'|')} |")

    L += ["", "---", "",
          "## G. Curation already applied — please confirm", "",
          "These were decided from the evidence and are live in "
          "`glossary-data/curation.json`. None of them changes a single word of "
          "any definition; they only decide what counts as a term and what it is "
          "called.", "",
          f"### Stop-listed as rhetorical labels, not terms ({len(curation['stopTerms'])})",
          "", ", ".join(f"`{s}`" for s in curation["stopTerms"]), "",
          f"### Merged ({len(curation['aliases'])})", "",
          "| Variant | Merged into |", "| --- | --- |"]
    for k, v in sorted(curation["aliases"].items()):
        L.append(f"| {k} | {v} |")
    L += ["", f"### Renamed for display ({len(curation['display'])})", "",
          "| Key | Shown as |", "| --- | --- |"]
    for k, v in sorted(curation["display"].items()):
        L.append(f"| {k} | {v} |")

    (INVENTORY.parent / "review-decisions.md").write_text(
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
    print(f"\nwrote {TERMS_OUT.relative_to(ROOT)}")
    print(f"wrote {INVENTORY.relative_to(ROOT)}")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""Build /search-index.json - the one payload behind the site-wide search.

    python3 scripts/build_search_index.py            # write search-index.json
    python3 scripts/build_search_index.py --out X    # write elsewhere (mocks)

The overlay (js/components/site-search.js) fetches this file once, lazily,
the first time a reader opens the search. Nothing else reads it. It is
GENERATED - never hand-edit it; edit this script or the sources and re-run.

WHAT IS IN IT, AND WHERE EACH PIECE COMES FROM
----------------------------------------------
    topics     the 166 topics. Title, board, unit and spec from the topic's
               questions-data record (the same record notes_extras builds the
               tail from - a topic page cannot build without it); the extra
               match text is the page's own <h2> headings, read from the
               slice in notes-data/topics/. One record drives up to three
               result rows client-side: the notes page, the practice-question
               page, and - where the topic clears the past-paper bank's
               volume GATE, the same rule the tail applies - its
               question-bank page. Individual past-paper exam questions are
               deliberately NOT indexed: the bank has its own purpose-built
               finder (Eliot's call).
    glossary   every term and formula in glossary-data/terms.json. The
               definition text is build_glossary.ld_description() - the SAME
               words the glossary page shows (curation rewrites and approved
               capitalisations applied), which is also what its DefinedTerm
               structured data carries. Where a term sits on both boards the
               overlay shows the first board's wording and links to both
               anchors.
    decks      the 6 flashcard decks, deckTitle from flashcards-data/.
    pages      the hand-written and hub pages. Each title is the page's own
               <h1>, extracted at build time so it cannot go stale; the
               SYNONYMS table below is the one curated piece of this file -
               honest search words for pages whose body is not indexed. FAQ
               questions are extracted individually and link to their anchor.

THE SCHEMA IS COMPACT ON PURPOSE - the payload goes over the wire. Rows are
arrays, and everything derivable is derived client-side by site-search.js
(URLs from dir + slug, board metas from the dirs table, static group match
words). The two files state the same schema and must move together:

    dirs      [notesDir, boardName, moduleName, boardSlug] x6
    topics    [di, slug, spec, title, short, headings, ppq]
              di indexes dirs; short is "" when it equals title; ppq is 0/1
    glossary  [title, anchorId, boards, kind, definition]
              boards: 1 = Edexcel A, 2 = AQA, 3 = both; kind: 0 term,
              1 formula (definition is then the formula as plain text)
    decks     [deckTitle, url, di]
    pages     [title, url, metaLabel, synonyms]

ORDER IN THE BUILD. This generator runs LAST of the content generators
(site_layout.GENERATORS): it reads pages that build_notes_pages.py,
build_glossary.py and the rest write earlier in the same run - the same
"later generators see what earlier ones wrote" contract build_sitemap.py
relies on.

NO NEW WORDING. Every title is an existing page's own wording; definitions
are the glossary's own; headings are the notes' own. The only strings minted
here are the SYNONYMS (match text, never displayed), all listed for approval
in the site-search proposal and frozen here.

Standard library only. Deterministic: two runs give identical bytes.
"""

from __future__ import annotations

import argparse
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import build_glossary  # noqa: E402
import build_past_paper_questions as ppq  # noqa: E402
import notes_extras  # noqa: E402

OUT = ROOT / "search-index.json"

# ---------------------------------------------------------------- pages

# The curated half of the "pages" group: url -> (meta label, synonym match
# text). The title is NOT here - it is the page's own <h1>, read below, so a
# retitled page updates itself on the next build. Synonyms are search words a
# student would type for a page whose body is not indexed. Keep them honest:
# every phrase is something the page genuinely answers.
PAGES: dict[str, tuple[str, str]] = {
    "/": ("Economics Academy", "home start"),
    "/tutoring.html": (
        "Tutoring",
        "tutor tutoring lessons online one to one 1-to-1 group price cost "
        "book intro call free call"),
    "/marking.html": (
        "Marking",
        "marking marked essay feedback 25 marker paper marking service "
        "price cost send an essay"),
    "/contact.html": ("Contact", "contact email enquiry message get in touch"),
    "/about.html": ("About",
                    "about eliot king who tutor credentials dbs experience"),
    "/faq.html": ("FAQ", "faq questions answers help"),
    "/privacy.html": ("Privacy",
                      "privacy cookies analytics consent data policy"),
    "/revision-notes/": ("Revision notes", "revision notes free"),
    "/revision-notes/glossary/": (
        "Glossary", "glossary definitions formulae formulas key terms"),
    "/revision-notes/macro-application/": (
        "Revision notes", "macro application uk economy applied examples"),
    "/revision-notes/microeconomics-diagrams.html": (
        "Diagram gallery", "diagrams graphs curves micro microeconomics"),
    "/revision-notes/macroeconomics-diagrams.html": (
        "Diagram gallery", "diagrams graphs curves macro macroeconomics"),
    "/practice-questions/": (
        "Practice questions",
        "practice questions quiz mcq multiple choice test"),
    "/flashcards/": ("Flashcards",
                     "flashcards cards decks spaced repetition"),
    "/past-papers/": ("Past papers",
                      "past papers pdf question papers mark schemes"),
    "/past-papers/edexcel/": ("Past papers",
                              "edexcel past papers mark schemes 9ec0 8ec0"),
    "/past-papers/aqa/": ("Past papers", "aqa past papers mark schemes 7136"),
    "/past-papers/ocr/": ("Past papers", "ocr past papers mark schemes h460"),
    "/past-papers/edexcel-b/": ("Past papers",
                                "edexcel b past papers mark schemes 9eb0"),
    "/past-paper-questions/": (
        "Past paper questions",
        "past paper questions real exam questions search finder by topic"),
}

# The board hub pages join the "pages" group too, titles from their own <h1>s.
BOARD_HUBS = (
    "/revision-notes/edexcel-theme-1/", "/revision-notes/edexcel-theme-2/",
    "/revision-notes/edexcel-theme-3/", "/revision-notes/edexcel-theme-4/",
    "/revision-notes/aqa-a2-micro/", "/revision-notes/aqa-a2-macro/",
    "/practice-questions/edexcel-theme-1/", "/practice-questions/edexcel-theme-2/",
    "/practice-questions/edexcel-theme-3/", "/practice-questions/edexcel-theme-4/",
    "/practice-questions/aqa-a2-micro/", "/practice-questions/aqa-a2-macro/",
    "/revision-notes/glossary/edexcel-a/", "/revision-notes/glossary/aqa/",
)

H1_RE = re.compile(r"<h1[^>]*>(.*?)</h1>", re.S)
H2_RE = re.compile(r"<h2>(.*?)</h2>", re.S)
FAQ_ITEM_RE = re.compile(
    r'<div class="accordion-item" id="([^"]+)">\s*<button.*?>(.*?)</button>',
    re.S)
ICON_SPAN_RE = re.compile(r"<span[^>]*class=\"icon[^\"]*\".*?</span>", re.S)


def fail(what: str) -> None:
    sys.exit(f"build_search_index: {what}")


def page_file(url: str) -> pathlib.Path:
    rel = url.lstrip("/")
    if url.endswith("/"):
        rel += "index.html"
    return ROOT / (rel or "index.html")


def h1_of(url: str) -> str:
    path = page_file(url)
    if not path.is_file():
        fail(f"{url}: no file at {path.relative_to(ROOT)}")
    m = H1_RE.search(path.read_text(encoding="utf-8"))
    if not m:
        fail(f"{url}: no <h1> found")
    return notes_extras.plain(m.group(1))


def faq_rows() -> list[list]:
    text = (ROOT / "faq.html").read_text(encoding="utf-8")
    out = []
    for ident, button in FAQ_ITEM_RE.findall(text):
        question = notes_extras.plain(ICON_SPAN_RE.sub(" ", button))
        if not question:
            fail(f"faq.html #{ident}: empty question text")
        out.append([question, f"/faq.html#{ident}", "FAQ", "faq"])
    if len(out) < 20:
        fail(f"faq.html: only {len(out)} questions extracted - markup moved?")
    return out


def pages_rows() -> list[list]:
    out = [[h1_of(url), url, meta, synonyms]
           for url, (meta, synonyms) in PAGES.items()]
    for url in BOARD_HUBS:
        family = ("Practice questions" if url.startswith("/practice-questions/")
                  else "Glossary" if "/glossary/" in url
                  else "Revision notes")
        out.append([h1_of(url), url, family, ""])
    return out + faq_rows()


# ---------------------------------------------------------------- topics

# One row per notes directory, indexed into by every topic row:
# [notesDir, boardName, moduleName, boardSlug]. Order = notes_extras's, which
# is boards.json group order (Edexcel first).
def dirs_table() -> list[list[str]]:
    return [[d, board, module, notes_extras.BOARD_SLUG[board]]
            for d, (board, module) in notes_extras.BOARD_OF_DIR.items()]


def headings_of(notes_dir: str, slug: str) -> list[str]:
    path = ROOT / "notes-data" / "topics" / notes_dir / f"{slug}.html"
    if not path.is_file():
        fail(f"no slice at {path.relative_to(ROOT)}")
    return [notes_extras.plain(h)
            for h in H2_RE.findall(path.read_text(encoding="utf-8"))]


def topic_rows(dirs: list[list[str]]) -> list[list]:
    bank = notes_extras.past_paper_bank()
    out = []
    for di, (notes_dir, *_rest) in enumerate(dirs):
        recs = notes_extras.quiz_records(notes_dir)
        for slug in sorted(recs):
            rec = recs[slug]
            short = rec["shortTitle"] if rec["shortTitle"] != rec["title"] else ""
            has_page = len(bank.get(slug, [])) >= ppq.GATE
            out.append([di, slug, rec["spec"], rec["title"], short,
                        " ".join(headings_of(notes_dir, slug)),
                        1 if has_page else 0])
    if len(out) != 166:
        fail(f"expected 166 topic records, found {len(out)}")
    return out


# ------------------------------------------------------------- glossary

# boards bitmask, in boards.json group order: Edexcel first.
GLOSSARY_BOARDS = (("edexcel-a", 1), ("aqa", 2))


def glossary_rows() -> list[list]:
    data = json.loads((ROOT / "glossary-data" / "terms.json")
                      .read_text(encoding="utf-8"))
    rules = build_glossary.rewrites()
    approved = build_glossary.approved_capitalisations()

    out = []
    for term in sorted(data["terms"], key=lambda t: (t["key"], t["id"])):
        mask = sum(bit for b, bit in GLOSSARY_BOARDS if b in term["boards"])
        if not mask:
            fail(f"term {term['id']}: no known board in {term['boards']}")
        first = next(b for b, bit in GLOSSARY_BOARDS if mask & bit)
        out.append([term["term"], term["id"], mask, 0,
                    build_glossary.ld_description(term, first, rules, approved)])
    for f in sorted(data["formulae"], key=lambda f: f["label"].lower()):
        mask = sum(bit for b, bit in GLOSSARY_BOARDS if b in f["boards"])
        if not mask:
            fail(f"formula {f['id']}: no known board in {f['boards']}")
        out.append([f["label"], f["id"], mask, 1,
                    build_glossary.tex_to_text(f["latex"])])
    return out


# ---------------------------------------------------------------- decks

def deck_rows(dirs: list[list[str]]) -> list[list]:
    di_of = {row[0]: i for i, row in enumerate(dirs)}
    out = []
    for notes_dir, (url, _deck) in notes_extras.FLASHCARDS_OF_DIR.items():
        board_dir, theme = url.rstrip("/").split("/")[-2:]
        src = ROOT / "flashcards-data" / board_dir / f"{theme}.json"
        rec = json.loads(src.read_text(encoding="utf-8"))
        out.append([rec["deckTitle"], url, di_of[notes_dir]])
    return out


# ------------------------------------------------------------------ build

def build() -> dict:
    dirs = dirs_table()
    return {
        "_generated_by": "scripts/build_search_index.py - do not hand-edit",
        "v": 1,
        "dirs": dirs,
        "topics": topic_rows(dirs),
        "glossary": glossary_rows(),
        "decks": deck_rows(dirs),
        "pages": pages_rows(),
    }


def render(index: dict) -> str:
    # One row per line: reviewable diffs, deterministic bytes.
    out = [json.dumps({k: v for k, v in index.items()
                       if not isinstance(v, list)}, ensure_ascii=False)[:-1]]
    for key in ("dirs", "topics", "glossary", "decks", "pages"):
        rows = ",\n".join(
            json.dumps(r, ensure_ascii=False, separators=(",", ":"))
            for r in index[key])
        out.append(f',"{key}":[\n{rows}\n]')
    return "".join(out) + "}\n"


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--out", type=pathlib.Path, default=OUT,
                    help="write the index here instead (mocks and tests)")
    args = ap.parse_args(argv)
    index = build()
    text = render(index)
    n = sum(len(index[k]) for k in ("topics", "glossary", "decks", "pages"))
    args.out.write_text(text, encoding="utf-8")
    print(f"search-index: {n} records, {len(text.encode('utf-8')):,} bytes "
          f"-> {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

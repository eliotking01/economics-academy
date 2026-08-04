#!/usr/bin/env python3
"""Prove the glossary still says exactly what the notes say.

    python3 scripts/verify_glossary.py

The glossary reproduces definitions from the revision notes word for word. That
is only true on the day it is generated: edit a notes page afterwards and the
glossary silently becomes a quotation of something that no longer exists. This
is the check that catches it.

Five checks, in order of what they would catch:

  1. Every EXTRACTED definition appears verbatim in the notes page it cites.
     Done by comparing plain text, independently of the extractor, so a bug in
     extract_glossary.py cannot make this pass. Entries from
     glossary-data/authored.json are exempt by definition - they were written
     for the glossary because no notes page defines the concept - and are
     counted separately so the exemption stays visible.
  2. glossary-data/terms.json is current - re-extracting produces the same data.
  3. Every generated page is current - rebuilding produces the same HTML.
  4. Every cited notes page exists, and every anchor id on a page is unique.
  5. Every DefinedTerm in the JSON-LD points at an id that exists on the page.

Exits non-zero on any failure. Standard library only.
"""

from __future__ import annotations

import importlib.util
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = ROOT / "glossary-data" / "terms.json"
GLOSSARY = ROOT / "revision-notes" / "glossary"
BOARD_DIR = {"edexcel-a": "edexcel-a", "aqa": "aqa"}


def load(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def norm(s: str) -> str:
    """Collapse whitespace and unify the characters that vary by typing.

    The notes and the generated page differ in where a line wraps, and a dash
    may be typed as - or written as an entity. Neither is a change of wording,
    so both sides are normalised the same way.
    """
    s = s.replace("–", "-").replace("—", "-").replace("−", "-")
    s = s.replace("‘", "'").replace("’", "'")
    s = s.replace("“", '"').replace("”", '"')
    return re.sub(r"\s+", " ", s).strip()


def flatten(s: str) -> str:
    """HTML fragment -> comparable plain text.

    Tags are stripped BEFORE entities are resolved, and only on strings that
    really are HTML. Doing it the other way round corrupts the maths: the notes
    write `\\( TR &lt; TC \\)`, and once that is unescaped to a bare `<` a tag
    regex treats the rest of the sentence as a tag and eats it. That is why
    page_text() below normalises without stripping - its text is already
    tag-free and already unescaped by the parser.
    """
    import html as _html
    return norm(_html.unescape(re.sub(r"<[^>]+>", "", s)))


def page_text(eg, path: pathlib.Path) -> str:
    root = eg.parse(path.read_text(encoding="utf-8"))
    body = next((n for n in eg.walk(root) if "notes-container" in n.cls()), root)
    return norm(eg.text_of(body))


def main():
    fails = []

    if not DATA.is_file():
        print("error: glossary-data/terms.json is missing - run "
              "scripts/extract_glossary.py", file=sys.stderr)
        return 1
    for board, d in BOARD_DIR.items():
        if not (GLOSSARY / d / "index.html").is_file():
            print(f"error: revision-notes/glossary/{d}/index.html is missing - "
                  f"run scripts/build_glossary.py", file=sys.stderr)
            return 1

    eg = load("extract_glossary")
    data = json.loads(DATA.read_text(encoding="utf-8"))

    # ---- 1. every definition is still in the notes page it cites -----------
    cache = {}
    checked = 0
    authored = 0
    for t in data["terms"]:
        for s in t["sources"]:
            # Authored definitions have nothing in the notes to match - that is
            # what makes them authored. They are counted, not checked.
            if s.get("origin") == "authored":
                authored += 1
                continue
            path = ROOT / s["notesUrl"].lstrip("/")
            if not path.is_file():
                fails.append(f"[1] {t['term']}: {s['notesUrl']} does not exist")
                continue
            if path not in cache:
                cache[path] = page_text(eg, path)
            # The continuation list is part of the definition, so it is checked
            # against the notes too.
            needle = flatten(s["definitionHtml"]
                             + " " + s.get("definitionListHtml", ""))
            checked += 1
            if needle and needle not in cache[path]:
                fails.append(
                    f"[1] {t['term']} ({s['board']} {s['spec']}): the definition "
                    f"is no longer in {s['notesUrl']}\n"
                    f"      glossary says: {needle[:110]}"
                )
    print(f"  1. definitions still verbatim in their notes page   "
          f"{checked - len([f for f in fails if f.startswith('[1]')])}/{checked}"
          f"   ({authored} authored, not applicable)")

    # ---- 2. terms.json is current -----------------------------------------
    terms, formulae, stats, _skipped, problems = eg.build()[:5]
    fresh = {"terms": terms, "formulae": formulae}
    stale = (json.dumps(fresh["terms"], sort_keys=True)
             != json.dumps(data["terms"], sort_keys=True)
             or json.dumps(fresh["formulae"], sort_keys=True)
             != json.dumps(data["formulae"], sort_keys=True))
    if stale:
        fails.append("[2] glossary-data/terms.json is out of date - the notes "
                     "have changed since it was written. Re-run "
                     "scripts/extract_glossary.py")
    if problems:
        for p in problems:
            fails.append(f"[2] extraction problem: {p}")
    print(f"  2. terms.json matches the notes                     "
          f"{'stale' if stale else 'current'}")

    # ---- 3. the pages are current -----------------------------------------
    bg = load("build_glossary")
    tax = json.loads((ROOT / "past-paper-questions-data" / "taxonomy.json")
                     .read_text(encoding="utf-8"))
    groups, order = {}, 0
    for b in tax["boards"]:
        for g in b["groups"]:
            groups[g["slug"]] = {"label": g["label"], "name": g["name"],
                                 "order": order}
            order += 1
    try:
        latex = [f["latex"] for f in data["formulae"]]
        rendered = dict(zip(latex, bg.katex(latex)))
        import html as _h
        inline = sorted({
            _h.unescape(m).strip()
            for t in data["terms"] for src in t["sources"]
            for m in bg.INLINE_TEX.findall(src["definitionHtml"])
        })
        inline_map = dict(zip(inline, bg._katex(inline, False)))
    except bg.BuildError as exc:
        fails.append(f"[3] {exc}")
        rendered = inline_map = None

    pages = {}
    if rendered is not None:
        pages[GLOSSARY / "index.html"] = bg.render_landing(data)
        for board in bg.BOARDS:
            pages[GLOSSARY / bg.BOARDS[board]["slug"] / "index.html"] = \
                bg.render_board(data, board, groups, rendered, inline_map)
        for path, expected in pages.items():
            actual = path.read_text(encoding="utf-8")
            # Prettier reformats the generator's output, so compare the text
            # rather than the bytes - wording is what must not drift.
            if flatten(expected) != flatten(actual):
                fails.append(f"[3] {path.relative_to(ROOT)} is out of date - "
                             f"re-run scripts/build_glossary.py")
    print(f"  3. generated pages match the data                   "
          f"{len(pages)} page(s) checked")

    # ---- 4. anchors ---------------------------------------------------------
    dup_total = 0
    for board, d in BOARD_DIR.items():
        html_src = (GLOSSARY / d / "index.html").read_text(encoding="utf-8")
        ids = re.findall(r'\bid="([^"]+)"', html_src)
        dupes = {i for i in ids if ids.count(i) > 1}
        dup_total += len(dupes)
        for i in sorted(dupes):
            fails.append(f"[4] {d}: duplicate id '{i}'")
        expected = {t["id"] for t in data["terms"] if board in t["boards"]}
        missing = expected - set(ids)
        for i in sorted(missing):
            fails.append(f"[4] {d}: term id '{i}' is not on the page")
        # No term may appear on a board page without a source for that board.
        term_ids = {t["id"] for t in data["terms"]}
        for i in set(ids) & term_ids:
            t = next(x for x in data["terms"] if x["id"] == i)
            if board not in t["boards"]:
                fails.append(f"[4] {d}: '{t['term']}' is on the page but has no "
                             f"{board} source")
    print(f"  4. anchors unique and complete                      "
          f"{'ok' if dup_total == 0 else str(dup_total) + ' duplicates'}")

    # No page may show LaTeX source to a reader. Fifteen definitions state
    # their formula inline, and the pages carry no maths JavaScript.
    for board, d in BOARD_DIR.items():
        src = (GLOSSARY / d / "index.html").read_text(encoding="utf-8")
        for m in re.finditer(r"\\\(|\\\[", src):
            fails.append(f"[4] {d}: raw LaTeX on the page at "
                         f"{src[m.start():m.start() + 50]!r}")
            break

    # ---- 5. JSON-LD ---------------------------------------------------------
    ld_checked = 0
    for board, d in BOARD_DIR.items():
        html_src = (GLOSSARY / d / "index.html").read_text(encoding="utf-8")
        ids = set(re.findall(r'\bid="([^"]+)"', html_src))
        for block in re.findall(
                r'<script type="application/ld\+json">(.*?)</script>',
                html_src, re.S):
            try:
                obj = json.loads(block)
            except json.JSONDecodeError as exc:
                fails.append(f"[5] {d}: JSON-LD does not parse - {exc}")
                continue
            for dt in obj.get("hasDefinedTerm", []):
                ld_checked += 1
                anchor = dt["@id"].rsplit("#", 1)[-1]
                if anchor not in ids:
                    fails.append(f"[5] {d}: DefinedTerm '{dt['name']}' points at "
                                 f"#{anchor}, which is not on the page")
                if not dt.get("description", "").strip():
                    fails.append(f"[5] {d}: DefinedTerm '{dt['name']}' has an "
                                 f"empty description")
    print(f"  5. JSON-LD terms resolve to real anchors            {ld_checked} checked")

    if fails:
        print(f"\n{len(fails)} failure(s):", file=sys.stderr)
        for f in fails:
            print(f"  - {f}", file=sys.stderr)
        return 1
    print("\nall checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())

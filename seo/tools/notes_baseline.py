#!/usr/bin/env python3
"""Phase 0 of the revision-notes on-page audit: the before/after snapshot.

One row per in-scope page, written as CSV. Every claim in
`seo/17-notes-seo-audit-*.md` is meant to be traceable back to a column here,
so this script computes the numbers rather than restating them.

    python3 seo/tools/notes_baseline.py --out seo/17-notes-baseline-2026-08-21.csv
    python3 seo/tools/notes_baseline.py --summary        # to stdout, writes nothing

WHAT COUNTS AS IN SCOPE, AND THE ONE TRAP
-----------------------------------------
In scope: the 166 topic pages in the six board directories, the 7 hub
index.html pages under notes-data/hubs/, revision-notes/index.html, and the
two diagram gallery pages (metadata only).

The trap: `revision-notes/aqa-a2-micro/1-1-5-production-possibility-diagrams.html`
is a TOPIC page. A glob on `*-diagrams.html` matches it alongside the two real
galleries and misclassifies it. Classification here is by directory, never by
filename, which cannot make that mistake.

Standard library only.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from html import unescape
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from pagemeta import parse_html, norm_space  # noqa: E402

REPO = Path(__file__).resolve().parent.parent.parent
NOTES = REPO / "revision-notes"

# Board directory -> (board key, board label, module label). The module label
# is what the spec sub-label and the description formula name for AQA, where a
# site-local code must not be published as if it were a real 7136 code.
BOARD_DIRS = {
    "edexcel-theme-1": ("edexcel", "Edexcel", "Theme 1"),
    "edexcel-theme-2": ("edexcel", "Edexcel", "Theme 2"),
    "edexcel-theme-3": ("edexcel", "Edexcel", "Theme 3"),
    "edexcel-theme-4": ("edexcel", "Edexcel", "Theme 4"),
    "aqa-a2-micro": ("aqa", "AQA", "Microeconomics"),
    "aqa-a2-macro": ("aqa", "AQA", "Macroeconomics"),
}

MAIN_RE = re.compile(r"<main\b[^>]*>(.*?)</main\s*>", re.I | re.S)
IMG_RE = re.compile(r"<img\b", re.I)
SVG_RE = re.compile(r"<svg\b", re.I)
H_RE = re.compile(r"<(h[1-6])\b[^>]*>", re.I)
H2_ID_RE = re.compile(r"<h2\b([^>]*)>", re.I)
ID_ATTR_RE = re.compile(r'\bid="([^"]*)"', re.I)
A_RE = re.compile(r'<a\b[^>]*href="([^"]*)"', re.I)
SPEC_RE = re.compile(
    r"Specification Coverage:\s*</strong>\s*([A-Za-z][A-Za-z ]*?)\s+unit\s+"
    r"(\d+(?:\.\d+)+)", re.I | re.S)
CODE_PREFIX_RE = re.compile(r"^(\d+(?:\.\d+)+)\s+(.*)$")


def classify(rel: str) -> tuple[str, str, str]:
    """(kind, board, module) from the page's LOCATION, never its filename."""
    parts = Path(rel).parts
    if parts[0] != "revision-notes":
        return "out-of-scope", "", ""
    if len(parts) == 2:
        if parts[1] == "index.html":
            return "section-index", "", ""
        if parts[1] in ("macroeconomics-diagrams.html", "microeconomics-diagrams.html"):
            return "gallery", "", ""
        return "out-of-scope", "", ""
    d = parts[1]
    if d in BOARD_DIRS:
        board, label, module = BOARD_DIRS[d]
        return ("hub" if parts[-1] == "index.html" else "topic"), label, module
    if d == "macro-application" and parts[-1] == "index.html":
        return "hub", "", "Macro application"
    return "out-of-scope", "", ""


def in_scope() -> list[str]:
    out = []
    for p in sorted(NOTES.rglob("*.html")):
        rel = p.relative_to(REPO).as_posix()
        if classify(rel)[0] != "out-of-scope":
            out.append(rel)
    return out


def main_html(source: str) -> str:
    m = MAIN_RE.search(source)
    return m.group(1) if m else ""


def strip_tags_words(fragment: str) -> int:
    """Visible words in a fragment, by tag-strip.

    Deliberately a tag-strip and not pagemeta.parse_html's own counter. The
    two disagree by about 5% - the parser treats a run of data between two
    tags as one chunk, so `(<em>ceteris paribus</em>)` counts differently -
    and `seo/14-notes-keyword-brief.md` §3 was measured with a tag-strip.
    Matching it means the "17 pages under 500 words" figure in the brief and
    in this CSV are the same 17 pages, rather than two nearby numbers nobody
    can reconcile. Reproduced exactly: min 300, median 741, mean 859, max
    2,547, 17 under 500.
    """
    t = re.sub(r"<script.*?</script>", "", fragment, flags=re.S | re.I)
    t = re.sub(r"<style.*?</style>", "", t, flags=re.S | re.I)
    t = re.sub(r"<!--.*?-->", "", t, flags=re.S)
    t = unescape(re.sub(r"<[^>]+>", " ", t))
    return len(t.split())


def jsonld_of(page_source: str) -> list[dict]:
    out = []
    for block in parse_html(page_source).jsonld:
        try:
            d = json.loads(block)
        except Exception:  # noqa: BLE001
            continue
        out.extend(d if isinstance(d, list) else [d])
    return out


def learning_resource(blocks: list[dict]) -> dict | None:
    for b in blocks:
        t = b.get("@type")
        types = t if isinstance(t, list) else [t]
        if "LearningResource" in types:
            return b
    return None


def row_for(rel: str) -> dict:
    source = (REPO / rel).read_text(encoding="utf-8", errors="replace")
    meta = parse_html(source)
    kind, board, module = classify(rel)
    body = main_html(source)

    spec = ""
    ms = SPEC_RE.search(body)
    if ms:
        spec = ms.group(2)

    h1 = meta.h1[0] if meta.h1 else ""
    h1_code = ""
    h1_bare = h1
    cm = CODE_PREFIX_RE.match(h1)
    if cm:
        h1_code, h1_bare = cm.group(1), cm.group(2)

    levels = [m.group(1).lower() for m in H_RE.finditer(body)]
    skips = []
    prev = 0
    for lv in levels:
        n = int(lv[1])
        if prev and n > prev + 1:
            skips.append(f"h{prev}->h{n}")
        prev = n

    h2_tags = H2_ID_RE.findall(body)
    h2_with_id = sum(1 for a in h2_tags if ID_ATTR_RE.search(a))

    internal = 0
    for href in A_RE.findall(body):
        v = re.sub(r"^https?://(www\.)?economicsacademy\.co\.uk", "", href.strip())
        if v.startswith("/"):
            internal += 1

    blocks = jsonld_of(source)
    lr = learning_resource(blocks) or {}
    types = []
    for b in blocks:
        t = b.get("@type")
        types.extend(t if isinstance(t, list) else [t])

    return {
        "path": rel,
        "kind": kind,
        "board": board,
        "module": module,
        "spec_code": spec,
        "title": meta.title,
        "title_len": len(meta.title),
        "description": meta.description,
        "desc_len": len(meta.description),
        "h1": h1,
        "h1_code_prefix": h1_code,
        "h1_bare": h1_bare,
        "canonical": meta.canonical,
        "canonical_self": "yes" if meta.canonical.endswith("/" + rel)
                          or meta.canonical.endswith("/" + rel.replace("/index.html", "/"))
                          else "check",
        "h2_count": len(h2_tags),
        "h2_with_id": h2_with_id,
        "heading_skips": ";".join(skips),
        "words_main": strip_tags_words(body),
        "img_count": len(IMG_RE.findall(body)),
        "svg_count": len(SVG_RE.findall(body)),
        "internal_links_out": internal,
        "jsonld_types": ";".join(sorted(set(t for t in types if t))),
        "has_datePublished": "yes" if lr.get("datePublished") else "no",
        "has_dateModified": "yes" if lr.get("dateModified") else "no",
        "has_author": "yes" if lr.get("author") else "no",
        "og_title_matches": "yes" if norm_space(meta.og_title) == meta.title else "no",
        "twitter_title_matches": "yes" if norm_space(meta.twitter_title) == meta.title else "no",
        "og_desc_matches": "yes" if meta.og_description == meta.description else "no",
        "twitter_desc_matches": "yes" if meta.twitter_description == meta.description else "no",
    }


def build() -> list[dict]:
    return [row_for(rel) for rel in in_scope()]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--out", help="CSV to write")
    ap.add_argument("--summary", action="store_true", help="print a summary only")
    args = ap.parse_args()

    rows = build()
    fields = list(rows[0].keys())

    if args.out:
        dest = REPO / args.out if not Path(args.out).is_absolute() else Path(args.out)
        with dest.open("w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=fields)
            w.writeheader()
            w.writerows(rows)
        print(f"wrote {len(rows)} rows to {dest}")

    kinds = {}
    for r in rows:
        kinds[r["kind"]] = kinds.get(r["kind"], 0) + 1
    print("  by kind: " + ", ".join(f"{k}={v}" for k, v in sorted(kinds.items())))

    topics = [r for r in rows if r["kind"] == "topic"]
    tl = sorted(r["title_len"] for r in topics)
    dl = sorted(r["desc_len"] for r in topics)
    wc = sorted(r["words_main"] for r in topics)
    print(f"  topics: {len(topics)}  "
          f"edexcel={sum(1 for r in topics if r['board'] == 'Edexcel')} "
          f"aqa={sum(1 for r in topics if r['board'] == 'AQA')}")
    print(f"  title len   min {tl[0]} median {tl[len(tl)//2]} max {tl[-1]}  "
          f"over60={sum(1 for x in tl if x > 60)} over65={sum(1 for x in tl if x > 65)}")
    print(f"  desc len    min {dl[0]} median {dl[len(dl)//2]} max {dl[-1]}  "
          f"in145-158={sum(1 for x in dl if 145 <= x <= 158)}")
    print(f"  words main  min {wc[0]} median {wc[len(wc)//2]} max {wc[-1]}  "
          f"under500={sum(1 for x in wc if x < 500)}")
    print(f"  no image or svg: {sum(1 for r in topics if r['img_count'] == 0 and r['svg_count'] == 0)}")
    print(f"  h1 with code prefix: {sum(1 for r in topics if r['h1_code_prefix'])}")
    print(f"  h2s with a stable id: {sum(r['h2_with_id'] for r in topics)} "
          f"of {sum(r['h2_count'] for r in topics)}")
    print(f"  dateModified present: {sum(1 for r in topics if r['has_dateModified'] == 'yes')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Text similarity between Edexcel A and AQA revision-note topic pages.

Answers one question: where the two boards teach the same economics, how similar
is the prose, and are the pages differentiated enough that Google can tell them
apart and rank each for its own board's queries.

Three things make this harder than a naive diff, and each is handled explicitly:

  1. **Pages cannot be paired on spec code.** AQA notes use site-local codes
     1.x.y / 2.x.y, deliberately not the real 7136 codes, and they do not line up
     with Edexcel's 1.1.1-4.5.4. So every Edexcel page is compared against every
     AQA page and the best match is reported. Pairing is an output, not an input.

  2. **Boilerplate MASKS similarity here — it does not inflate it.** That is the
     opposite of the usual case and was measured, not assumed: with the
     breadcrumb, spec-alert, notes-cta and diagram-gallery line left in, pairs
     scoring >=0.80 fall from 26 to 6 and the median drops 0.368 -> 0.325. The
     furniture is itself board-specific - the spec-alert names the board and
     unit, the notes-cta links to that board's past papers - so including it
     rewards pages for differing in their template while their prose is
     identical. Stripping it is what exposes the real picture.
     --keep-boilerplate reproduces the masked numbers.

  3. **Jaccard on unigrams overstates.** Two economics pages share a large
     vocabulary whatever they say. Shingles (default 5-word) measure whether the
     same sentences appear, which is what duplicate-content risk actually is.

READ-ONLY. Run from the repo root:
    python3 docs/audit/scripts/board_similarity.py
    python3 docs/audit/scripts/board_similarity.py --shingle 8 --top 30
"""

import argparse
import collections
import html
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lib  # noqa: E402

EDEXCEL_DIRS = ("edexcel-theme-1", "edexcel-theme-2", "edexcel-theme-3", "edexcel-theme-4")
AQA_DIRS = ("aqa-a2-micro", "aqa-a2-macro")

# Blocks that are template furniture, not the page's own economics.
BOILERPLATE = [
    re.compile(r'<nav class="breadcrumb".*?</nav>', re.S | re.I),
    re.compile(r'<div class="spec-alert".*?</div>', re.S | re.I),
    re.compile(r'<div class="notes-cta".*?</div>\s*</div>', re.S | re.I),
    re.compile(r'<p class="notes-diagrams-link".*?</p>', re.S | re.I),
]
TAG = re.compile(r"<[^>]+>")
WS = re.compile(r"\s+")
SCRIPT_STYLE = re.compile(r"<(script|style)\b.*?</\1>", re.S | re.I)


def body_text(path, strip_boilerplate=True):
    """Visible prose of one topic page, lower-cased and whitespace-normalised."""
    s = lib.read(path)
    start = s.find('<section id="main"')
    end = s.find('footer-placeholder')
    if start == -1 or end == -1:
        return ""
    seg = s[start:end]
    seg = SCRIPT_STYLE.sub(" ", seg)
    if strip_boilerplate:
        for pat in BOILERPLATE:
            seg = pat.sub(" ", seg)
    seg = TAG.sub(" ", seg)
    return WS.sub(" ", html.unescape(seg)).strip().lower()


def shingles(text, n):
    words = text.split()
    if len(words) < n:
        return set()
    return {" ".join(words[i:i + n]) for i in range(len(words) - n + 1)}


def jaccard(a, b):
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def topic_pages():
    ed, aqa = [], []
    for f in lib.pages():
        if not f.startswith("revision-notes/"):
            continue
        if f.endswith("/index.html"):
            continue
        d = f.split("/")[1]
        if d in EDEXCEL_DIRS:
            ed.append(f)
        elif d in AQA_DIRS:
            aqa.append(f)
    return sorted(ed), sorted(aqa)


TITLE = re.compile(r"<title>(.*?)</title>", re.S)
H1 = re.compile(r"<h1[^>]*>(.*?)</h1>", re.S | re.I)
DESC = re.compile(r'<meta\s+name="description"\s+content="([^"]*)"', re.I)
SPEC = re.compile(r'<div class="spec-alert".*?</div>', re.S | re.I)


def meta(path):
    s = lib.read(path)
    def one(pat, default=""):
        m = pat.search(s)
        return WS.sub(" ", html.unescape(TAG.sub("", m.group(1)))).strip() if m else default
    return {
        "title": one(TITLE),
        "h1": one(H1),
        "desc": one(DESC),
        "spec": WS.sub(" ", html.unescape(TAG.sub(" ", SPEC.search(s).group(0)))).strip()
                if SPEC.search(s) else "(none)",
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--shingle", type=int, default=5)
    ap.add_argument("--top", type=int, default=25)
    ap.add_argument("--keep-boilerplate", action="store_true")
    args = ap.parse_args()

    ed, aqa = topic_pages()
    strip = not args.keep_boilerplate
    et = {f: shingles(body_text(f, strip), args.shingle) for f in ed}
    at = {f: shingles(body_text(f, strip), args.shingle) for f in aqa}

    empty = [f for f, s in list(et.items()) + list(at.items()) if not s]
    print(f"Edexcel topic pages: {len(ed)}   AQA topic pages: {len(aqa)}")
    print(f"shingle size: {args.shingle}   boilerplate: "
          f"{'KEPT' if args.keep_boilerplate else 'stripped'}")
    if empty:
        print(f"WARNING: {len(empty)} pages produced no text: {empty[:5]}")
    print(f"comparisons: {len(ed) * len(aqa)}")
    print()

    best = []
    for e in ed:
        top_a, top_s = None, 0.0
        for a in aqa:
            s = jaccard(et[e], at[a])
            if s > top_s:
                top_a, top_s = a, s
        best.append((top_s, e, top_a))
    best.sort(reverse=True)

    buckets = collections.Counter()
    for s, _, _ in best:
        buckets[min(int(s * 10) / 10, 0.9)] += 1
    print("=== distribution of each Edexcel page's BEST AQA match ===")
    for lo in sorted(buckets):
        bar = "#" * buckets[lo]
        print(f"  {lo:.1f}-{lo + 0.1:.1f}  {buckets[lo]:3d}  {bar}")
    over = [b for b in best if b[0] >= 0.80]
    mid = [b for b in best if 0.50 <= b[0] < 0.80]
    print(f"\n  >= 0.80 : {len(over)}")
    print(f"  0.50-0.79: {len(mid)}")
    print(f"  < 0.50   : {len(best) - len(over) - len(mid)}")
    print()

    print(f"=== top {args.top} pairs ===")
    for s, e, a in best[:args.top]:
        print(f"\n  {s:.3f}  {e.split('/', 1)[1]}")
        print(f"         {a.split('/', 1)[1] if a else '(none)'}")
        if s >= 0.50 and a:
            me, ma = meta(e), meta(a)
            for k in ("title", "h1", "desc"):
                same = "SAME" if me[k] == ma[k] else "diff"
                print(f"         {k:5s} [{same}] {me[k][:64]}")
                print(f"               {'':6s} {ma[k][:64]}")


if __name__ == "__main__":
    main()

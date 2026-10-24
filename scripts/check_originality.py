#!/usr/bin/env python3
"""Check practice questions for originality against the real exam papers.

    python3 scripts/check_originality.py corpus            # (re)build the corpora
    python3 scripts/check_originality.py check questions-data/edexcel-b-theme-1/1-6-2.json ...

WHY THIS EXISTS
---------------
Practice questions are sold, so every one must be 100% original (CLAUDE.md
rule 4). docs/QUESTIONS_PROGRESS.md sections 7-9 describe how originality was
checked on every batch: shingle each new set against the AQA and Edexcel A
past-paper corpora and against the rest of the bank, and compare numeric
option sets with the option blocks printed in the papers. The script that
did it, `orig.py`, lived in session scratchpads and was never committed. This
is that check, rebuilt from the record and extended to Edexcel B (D67, Phase 0).

THE CORPORA NEVER SHARE A DATA PATH WITH questions-data/
--------------------------------------------------------
`corpus` writes plain text extracted from every question paper (never a mark
scheme) to `_working/originality-corpus/<board>.txt`, which is gitignored and,
being under an underscore directory, never published. It is a reference to
check against and nothing reads it but this script. Rebuild it after new
papers arrive; extraction takes a couple of minutes (Swift + PDFKit,
scripts/pdf_text.swift).

WHAT `check` REPORTS, AND THE BAR
---------------------------------
For each question in the given sets, its stem, table and options against:

  1. every past-paper corpus - EXACT if the normalised stem appears verbatim
     and three or more of its options follow it in the paper; NEAR if a run
     of NEAR_PAPER (10) words is shared that fewer than STOCK_PAPER papers
     print. A phrase two papers share is the board's scaffolding ("which
     one of the following is most likely to be"), which section 7 says to
     leave alone; so is a stock stem with different options, printed as a
     note.
  2. every other question in questions-data/ - stems only, as section 8
     does: EXACT if a stem is identical; READ if NEAR_BANK (8) words are
     shared once the elasticity template and stock phrasing are filtered
     out (any run the papers print, or that STOCK_BANK or more bank stems
     share). A READ line is a prompt, not a verdict: section 8's rule is
     that shared runs inside the stem's own SCENARIO are a port and must
     be rewritten, while shared house phrasing ("using Table 1, the only
     change that shifts") is fine. Measured over the whole bank on
     2026-10-24, almost every READ is house phrasing - which is why it
     cannot be a mechanical bar.
  3. the numeric option blocks in the papers - REVIEW if three or more of
     a question's purely numeric options match one real block. A prompt to
     compare archetypes, never a verdict (section 7).

The bar is 0 EXACT and 0 NEAR, and every READ line read by hand; the exit
status is 1 on any EXACT or NEAR. Section 9's
concept-grep - two questions asking the same thing in different words - is
something no shingle can find, and stays a manual step.

Standard library only, apart from `swift` for `corpus`. Not in CI: the
corpora are local.
"""

from __future__ import annotations

import argparse
import html
import json
import pathlib
import re
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
QUESTIONS = ROOT / "questions-data"
CORPUS_DIR = ROOT / "_working" / "originality-corpus"

# board -> the hand-written past-papers directory its question papers sit in.
# Every *question-paper*.pdf under it, A Level and AS alike; mark schemes are
# never read. OCR is not here: no practice set is written to its spec.
CORPORA = {
    "aqa": ROOT / "past-papers" / "aqa",
    "edexcel-a": ROOT / "past-papers" / "edexcel",
    "edexcel-b": ROOT / "past-papers" / "edexcel-b",
}

NEAR_PAPER = 10
NOTE_PAPER = 8
NEAR_BANK = 8
STOCK_BANK = 3
STOCK_PAPER = 2

# Phrases every board's questions share on purpose (section 8): the
# elasticity precision instruction the guide requires. Removed from stems
# before the intra-bank comparison.
TEMPLATES = (
    "measuring each percentage change against its original value",
)

TAG_RE = re.compile(r"<[^>]+>")
WORD_RE = re.compile(r"[a-z0-9£%.]+")
NUM = r"[-−–]?£?\d[\d,]*(?:\.\d+)?%?"
OPTION_BLOCK_RE = re.compile(
    rf"\bA\s+({NUM})\s+B\s+({NUM})\s+C\s+({NUM})\s+D\s+({NUM})\b")


def words(text: str) -> list[str]:
    text = html.unescape(TAG_RE.sub(" ", text)).lower()
    text = text.replace("’", "'").replace("−", "-")
    return [w.strip(".") for w in WORD_RE.findall(text) if w.strip(".")]


def grams(ws: list[str], n: int) -> set[tuple[str, ...]]:
    return {tuple(ws[i:i + n]) for i in range(len(ws) - n + 1)}


def question_text(q: dict) -> str:
    parts = [q["stem"]]
    table = q.get("table")
    if table:
        parts.append(table.get("caption", ""))
        parts += [" ".join(map(str, table.get("head", [])))]
        parts += [" ".join(map(str, row)) for row in table.get("rows", [])]
    parts += list(q["options"].values())
    return " ".join(parts)


def stem_only(q: dict) -> list[str]:
    ws = " ".join(words(q["stem"]))
    for t in TEMPLATES:
        ws = ws.replace(t, " ")
    return ws.split()


def norm_num(v: str) -> str:
    return re.sub(r"[£,%]", "", v).replace("−", "-").replace("–", "-")


def numeric_options(q: dict) -> set[str]:
    """The options that are a number and nothing else ("£4.50", "-0.8").
    "1 and 2 only" is a statement choice, not a value, and is left out."""
    out = set()
    for text in q["options"].values():
        t = html.unescape(TAG_RE.sub("", text)).strip().rstrip(".")
        if re.fullmatch(NUM, t):
            out.add(norm_num(t))
    return out


# ------------------------------------------------------------------ corpus

def build_corpus() -> int:
    if CORPUS_DIR.resolve().is_relative_to(QUESTIONS.resolve()):
        sys.exit("refusing: the corpus must never share a path with questions-data/")
    CORPUS_DIR.mkdir(parents=True, exist_ok=True)
    for board, src in CORPORA.items():
        pdfs = sorted(src.rglob("*question-paper*.pdf"))
        if not pdfs:
            sys.exit(f"{board}: no question papers under {src.relative_to(ROOT)}")
        out = CORPUS_DIR / f"{board}.txt"
        print(f"{board}: extracting {len(pdfs)} question papers ...", flush=True)
        run = subprocess.run(
            ["swift", str(ROOT / "scripts" / "pdf_text.swift"), *map(str, pdfs)],
            capture_output=True, text=True)
        if run.returncode != 0:
            sys.exit(f"{board}: pdf_text.swift failed:\n{run.stderr}")
        files = run.stdout.count("@@@FILE ")
        if files != len(pdfs):
            sys.exit(f"{board}: {len(pdfs)} papers but {files} extracted:\n{run.stderr}")
        out.write_text(run.stdout, encoding="utf-8")
        print(f"  wrote {out.relative_to(ROOT)} ({len(run.stdout) / 1024:.0f} KB, "
              f"{len(OPTION_BLOCK_RE.findall(run.stdout))} numeric option blocks)")
    return 0


def load_corpora() -> dict[str, str]:
    out = {}
    for board in CORPORA:
        path = CORPUS_DIR / f"{board}.txt"
        if not path.is_file():
            sys.exit(f"no corpus at {path.relative_to(ROOT)} - run "
                     f"`python3 scripts/check_originality.py corpus` first")
        out[board] = path.read_text(encoding="utf-8")
    return out


# ------------------------------------------------------------------- check

def check(paths: list[pathlib.Path]) -> int:
    corpora = load_corpora()
    # One entry per paper, so a run can be counted across papers: a phrase
    # that STOCK_PAPER or more papers print is the board's own scaffolding.
    papers = [(b, words(chunk)) for b, t in corpora.items()
              for chunk in t.split("@@@FILE ")[1:]]
    in_papers: dict = {}
    for _b, ws in papers:
        for g in grams(ws, NEAR_PAPER):
            in_papers[g] = in_papers.get(g, 0) + 1
    stock_paper = {g for g, n in in_papers.items() if n >= STOCK_PAPER}
    paper_text = {b: " ".join(words(t)) for b, t in corpora.items()}
    paper_near = {b: set() for b in corpora}
    paper_note = {b: set() for b in corpora}
    for b, ws in papers:
        paper_near[b] |= grams(ws, NEAR_PAPER)
        paper_note[b] |= grams(ws, NOTE_PAPER)
    blocks = [(b, {norm_num(v) for v in m})
              for b, t in corpora.items() for m in OPTION_BLOCK_RE.findall(t)]
    any_paper = set().union(*paper_note.values())

    # The bank: every question, each compared with every OTHER one, so the
    # whole bank can be audited as well as a new set checked against it.
    bank = [(f"{f.parent.name}/{f.name} {q['id']}", q["id"], stem_only(q))
            for f in sorted(QUESTIONS.glob("*/*.json"))
            for q in json.loads(f.read_text(encoding="utf-8"))["questions"]]
    seen: dict = {}
    for _w, _i, ws in bank:
        for g in grams(ws, NEAR_BANK):
            seen[g] = seen.get(g, 0) + 1
    stock = any_paper | {g for g, n in seen.items() if n >= STOCK_BANK}
    bank_grams = [(w, i, grams(ws, NEAR_BANK) - stock, " ".join(ws))
                  for w, i, ws in bank]

    exact = near = read = review = checked = 0
    for path in paths:
        data = json.loads(path.read_text(encoding="utf-8"))
        for q in data["questions"]:
            checked += 1
            qid = q["id"]
            ws = words(question_text(q))
            stem = " ".join(words(q["stem"]))
            firsts = {w[0] for w in (words(o) for o in q["options"].values()) if w}
            for b in corpora:
                at = paper_text[b].find(stem) if len(stem.split()) >= 6 else -1
                if at >= 0:
                    after = set(paper_text[b][at + len(stem):].split()[:80])
                    if len(firsts & after) >= 3:
                        exact += 1
                        print(f"EXACT   {qid}: stem verbatim in the {b} papers, "
                              f"followed by {len(firsts & after)} of its options")
                    else:
                        print(f"note    {qid}: stock stem, verbatim in the {b} "
                              f"papers with different options")
                hits = (grams(ws, NEAR_PAPER) & paper_near[b]) - stock_paper
                if hits:
                    near += 1
                    print(f"NEAR    {qid}: {len(hits)} shared {NEAR_PAPER}-word run(s) "
                          f"with the {b} papers, e.g. \"{' '.join(min(hits))}\"")
            sw = stem_only(q)
            sg = grams(sw, NEAR_BANK) - stock
            for where, other_id, g, other in bank_grams:
                if other_id == qid:
                    continue
                if other and other == " ".join(sw):
                    exact += 1
                    print(f"EXACT   {qid}: same stem as {where}")
                elif sg & g:
                    read += 1
                    print(f"READ    {qid}: shares a {NEAR_BANK}-word stem run with "
                          f"{where}: \"{' '.join(min(sg & g))}\"")
            mine = numeric_options(q)
            for b, real in blocks:
                shared = mine & real
                if len(shared) >= 3:
                    review += 1
                    print(f"REVIEW  {qid}: options share {sorted(shared)} with a "
                          f"numeric option block in the {b} papers - compare archetypes")

    print(f"\n{checked} question(s) checked against {', '.join(corpora)} "
          f"({len(papers)} papers) and {len(bank)} bank question(s): {exact} exact, {near} near, "
          f"{read} bank run(s) to read, {review} option set(s) to review")
    return 1 if exact or near else 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("corpus", help="extract every question paper into the corpora")
    c = sub.add_parser("check", help="check question sets against the corpora and the bank")
    c.add_argument("sets", nargs="+", type=pathlib.Path)
    args = ap.parse_args()
    if args.cmd == "corpus":
        return build_corpus()
    return check([p if p.is_absolute() else pathlib.Path.cwd() / p for p in args.sets])


if __name__ == "__main__":
    sys.exit(main())

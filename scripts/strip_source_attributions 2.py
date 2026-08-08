#!/usr/bin/env python3
"""Move source attributions out of question text and into `sourceAttribution`.

Pearson prints a citation under the stimulus paragraph of every Section C
question - `(Source adapted from: https://...)`. The Swift extractor took the
whole block between the opener and the tariff line, so the citation came with it
and rendered inside the question. It is the paper's provenance note, not part of
what the candidate is asked to do.

This does not delete it. The matched text moves to a `sourceAttribution` field
on the question, which build_past_paper_questions.py deliberately does not emit
into `questions.json`, so it stays out of the rendered card and out of the
search index while remaining in the repo and reversible.

**The extractors are the real fix.** `stripAttribution()` in
extract_past_paper_questions.swift and `clean()` in extract_aqa_questions.py
both do this at source, so re-extraction cannot reintroduce a citation and
Section C questions added later never carry one. This script is the safety net
over data already on disk, and over any future extractor that is less tidy. Run
after an extraction: it should report 0 changes.

**Format-preserving on purpose.** It edits the JSON as text rather than
round-tripping it through `json.dumps`, because the two extractors hand-write
their output - raw UTF-8, and `context`/`questionPaper`/`markScheme` on a single
line each. A round-trip would reformat all 48 files and the next extractor run
would revert it, so `git diff` after regeneration would never be empty again.
`--verify` re-parses every file it touches, so the text editing cannot go
unnoticed if it ever goes wrong.

Re-runnable and idempotent: a question whose text no longer matches is left
exactly as it is.

    python3 scripts/strip_source_attributions.py            # dry run, the default
    python3 scripts/strip_source_attributions.py --apply    # write
"""

import argparse
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = ROOT / "past-paper-questions-data"

# A citation is a bracketed run that opens with Source/Sources and carries a
# URL. Requiring the URL is what keeps ordinary prose safe: the questions use
# the word freely ("a source of market failure", "sources in a market economy"),
# and none of those sit in brackets around a link. [^()]* rather than .* so a
# citation can never swallow a later bracket.
ATTRIBUTION = re.compile(r"\(\s*Sources?\b[^()]*https?://[^()]*\)")

# The extractors write one field per line. Capturing the indent keeps the
# inserted field aligned with whatever wrote the file.
FIELD = re.compile(r'^(?P<indent>\s*)"questionText": "(?P<value>.*)",?$')


def tidy(text):
    """Close the gap a removal leaves, without touching anything else."""
    # The citation sits between the stimulus and the question sentence, so
    # removing it leaves two spaces mid-string; at the end it leaves one.
    text = re.sub(r"[ \t]{2,}", " ", text)
    # An orphaned opener or closer, should a citation ever be split across one.
    text = re.sub(r"\(\s*\)", "", text)
    # Space pushed in front of its punctuation.
    text = re.sub(r"\s+([.,;:!?])", r"\1", text)
    # Doubled sentence punctuation left by a citation that ended one.
    text = re.sub(r"\.\s*\.", ".", text)
    return text.strip()


def json_string(s):
    """Encode as the extractors do: raw UTF-8, only the mandatory escapes."""
    return json.dumps(s, ensure_ascii=False)


def process_file(path):
    """Return (new_text, [(qid, before, after, attribution)]).

    Walks the file line by line so every byte it does not need to change is
    carried through untouched.
    """
    lines = path.read_text().split("\n")
    out = []
    changes = []
    current_id = None

    for line in lines:
        id_match = re.match(r'^\s*"id": "(?P<id>[^"]+)",?$', line)
        if id_match:
            current_id = id_match.group("id")

        # Never re-add a field that is already there.
        if re.match(r'^\s*"sourceAttribution":', line):
            out.append(line)
            continue

        m = FIELD.match(line)
        if not m:
            out.append(line)
            continue

        before = json.loads('"' + m.group("value") + '"')
        found = ATTRIBUTION.findall(before)
        if not found:
            out.append(line)
            continue

        after = tidy(ATTRIBUTION.sub(" ", before))
        attribution = " ".join(found)

        trailing = "," if line.rstrip().endswith(",") else ""
        indent = m.group("indent")
        out.append(f'{indent}"questionText": {json_string(after)},')
        out.append(f'{indent}"sourceAttribution": {json_string(attribution)}{trailing}')
        changes.append((current_id, before, after, attribution))

    return "\n".join(out), changes


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--apply", action="store_true", help="write the changes")
    ap.add_argument(
        "--verify",
        action="store_true",
        help="re-parse every file afterwards and check the field survived",
    )
    args = ap.parse_args()

    files = sorted(DATA.glob("*/*.json"))
    if not files:
        sys.exit(f"no extraction files under {DATA}")

    total = 0
    touched = 0
    already = 0

    for path in files:
        new_text, changes = process_file(path)

        existing = json.loads(path.read_text())
        already += sum(1 for q in existing["questions"] if q.get("sourceAttribution"))

        if not changes:
            continue

        touched += 1
        total += len(changes)

        for qid, before, after, attribution in changes:
            print("=" * 78)
            print(f"{qid}   ({path.relative_to(ROOT)})")
            print("-" * 78)
            print(f"  attribution : {attribution}")
            print(f"  before      : {before}")
            print(f"  after       : {after}")
            print()

        # Parsing the rewritten text before it reaches disk is what makes the
        # text editing safe.
        try:
            parsed = json.loads(new_text)
        except json.JSONDecodeError as exc:
            sys.exit(f"{path}: rewrite produced invalid JSON ({exc}) - nothing written")
        if len(parsed["questions"]) != len(existing["questions"]):
            sys.exit(f"{path}: question count changed - nothing written")

        if args.apply:
            path.write_text(new_text)

    verb = "changed" if args.apply else "would change"
    print("=" * 78)
    print(f"{verb} {total} questions across {touched} files")
    if already:
        print(f"{already} already carry a sourceAttribution and were left alone")

    if args.verify:
        bad = []
        for path in files:
            doc = json.loads(path.read_text())
            for q in doc["questions"]:
                if ATTRIBUTION.search(q["questionText"]):
                    bad.append((path.name, q["id"]))
        print(f"verify: {len(bad)} questions still contain an attribution")
        for b in bad[:10]:
            print("   ", b)

    if not args.apply:
        print("dry run - nothing written. Re-run with --apply.")


if __name__ == "__main__":
    main()

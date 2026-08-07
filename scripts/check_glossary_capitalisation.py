#!/usr/bin/env python3
"""Find glossary definitions that do not start with a capital letter.

    python3 scripts/check_glossary_capitalisation.py           # write the report
    python3 scripts/check_glossary_capitalisation.py --check   # validate only

The glossary reproduces the notes word for word, and the notes write a
definition as the continuation of its chip - "Absolute advantage: a situation
in which ...". Lifted out of that sentence and set under a heading, the
definition starts on a lower-case letter.

Most of those want nothing more than the first letter capitalised. Some do not:
where the notes wrote "Globalisation is the increasing integration ...", the
term is the sentence's subject and the extracted text is a fragment. Capitalising
that produces "Is the increasing integration ...". Those have to be fixed in the
notes, not here.

Two mechanical signals separate the two, and neither is a judgement about
wording:

  1. chipHasColon - did the notes punctuate it "Term: definition"? A colon means
     the author wrote the definition as a standalone phrase.
  2. the leading word - a determiner or noun ("a", "the", "an", "when") opens a
     phrase; a finite verb or pronoun ("is", "are", "occurs", "provide", "this")
     needs the term in front of it to parse.

Nothing here edits a definition. It classifies and reports; the capitalisation
itself is applied at render time by scripts/build_glossary.py, from the
allow-list in glossary-data/curation.json.

--check exits non-zero when a lower-case definition is not accounted for by
curation.json, so a newly written notes chip cannot reintroduce this silently.

Standard library only.
"""

from __future__ import annotations

import argparse
import html as _html
import importlib.util
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = ROOT / "glossary-data" / "terms.json"
CURATION = ROOT / "glossary-data" / "curation.json"
REPORT = ROOT / "_working" / "glossary" / "capitalisation-report.md"
SITE = "https://economicsacademy.co.uk"

# Leading words that open a noun phrase. A definition starting with one of
# these stands on its own once the term is a heading above it.
PHRASE_LEAD = {
    "a", "an", "the", "any", "all", "one", "each", "every", "no",
    "when", "where", "who", "whether",
    "goods", "natural", "spillover", "policies", "costs", "payments",
}

# Leading words that require the term as their grammatical subject. A
# definition starting with one of these is a fragment.
SUBJECT_LEAD = {
    "is", "are", "was", "were", "means", "occurs", "exists", "refers",
    "describes", "measures", "measure", "happens", "arises", "includes",
    "combine", "combines", "provide", "provides", "educate", "educates",
    "requiring", "bans", "ban", "limits", "limit",
    "this", "these", "it", "they",
}


def load(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def flatten(fragment: str) -> str:
    """HTML fragment -> plain text, for reading the first character."""
    return re.sub(r"\s+", " ", _html.unescape(re.sub(r"<[^>]+>", "", fragment))).strip()


def chip_colons(data) -> dict:
    """(notesUrl, term, definitionHtml) -> did the notes chip end on a colon?

    extract_glossary computes this per chip but does not carry it into
    terms.json, so it is recomputed here from the notes themselves.
    """
    eg = load("extract_glossary")
    urls = {s["notesUrl"] for t in data["terms"] for s in t["sources"]
            if s["origin"] == "chip"}
    out = {}
    for url in sorted(urls):
        path = ROOT / url.lstrip("/")
        if not path.is_file():
            continue
        root = eg.parse(path.read_text(encoding="utf-8"))
        for chip in eg.chips_on(root, {}, set(), [])[0]:
            out[(url, chip["term"], chip["definitionHtml"])] = chip["chipHasColon"]
    return out


def classify(data):
    """Every definition that does not open on a capital, sorted into buckets."""
    colons = chip_colons(data)
    rows = []
    for term in data["terms"]:
        for src in term["sources"]:
            text = flatten(src["definitionHtml"])
            if not text:
                continue
            first = text[0]
            if first.isupper():
                continue

            lead = text.split()[0].lower().strip(".,;:")
            if not first.isalpha():
                bucket, reason = "symbol", "opens on notation, not a word"
            elif src["origin"] == "authored":
                bucket, reason = "authored", "written for the glossary"
            elif lead in ("e.g", "eg", "i.e", "ie"):
                bucket, reason = "notdef", "an example, not a definition"
            elif not colons.get((src["notesUrl"], src["termAsWritten"],
                                 src["definitionHtml"]), True):
                bucket, reason = "fragment", "no colon: the term is the subject"
            elif lead in SUBJECT_LEAD:
                bucket, reason = "fragment", f'opens on "{lead}", which needs the term'
            elif lead in PHRASE_LEAD or lead.isalpha():
                bucket, reason = "clean", f'opens on "{lead}", a complete phrase'
            else:
                bucket, reason = "unknown", f'leading word "{lead}" not recognised'

            rows.append({
                "id": term["id"], "term": term["term"], "board": src["board"],
                "spec": src["spec"], "url": src["notesUrl"], "text": text,
                "bucket": bucket, "reason": reason, "lead": lead,
            })
    return rows


def group(rows):
    """Collapse the boards that share byte-identical wording into one row."""
    merged = {}
    for r in rows:
        key = (r["id"], r["text"])
        if key not in merged:
            merged[key] = dict(r, sources=[])
        merged[key]["sources"].append(r)
    return sorted(merged.values(), key=lambda r: (r["term"].lower(), r["text"]))


BUCKETS = [
    ("clean", "Clean — capitalise the first letter",
     "The notes wrote these as `Term: definition`, and the definition opens on a "
     "noun phrase. Capitalising the first letter changes nothing else and leaves "
     "a complete glossary entry. **These are the ones to approve.**"),
    ("fragment", "Fragment — needs fixing in the notes",
     "The definition needs the term in front of it to parse: the notes wrote "
     "`Globalisation is the increasing integration ...`, so the extracted text "
     "starts on a verb. Capitalising gives `Is the increasing integration ...`. "
     "**Do not capitalise these.** Each is fixed by rewording its notes chip and "
     "re-extracting — Eliot's call, not a scripted change."),
    ("notdef", "Not a definition",
     "These are examples that were chipped as if they were definitions. "
     "Capitalisation is not the problem with them."),
    ("symbol", "Intentional — leave alone",
     "These open on notation rather than a word. Nothing to change."),
    ("authored", "Authored entries",
     "From `glossary-data/authored.json`, which is hand-written — fix in place."),
    ("unknown", "Unclassified — needs a look",
     "The leading word did not match either list. Classify by hand."),
]


def write_report(rows) -> None:
    merged = group(rows)
    n = len(rows)
    out = [
        "# Glossary — definitions that do not start with a capital",
        "",
        "Generated by `python3 scripts/check_glossary_capitalisation.py`. "
        "Do not hand-edit; re-run it.",
        "",
        f"`{n}` of the `{sum(len(t['sources']) for t in json.loads(DATA.read_text())['terms'])}` "
        "definition records open on something other than a capital letter. "
        "Rows below merge the boards that share identical wording.",
        "",
        "| Bucket | Records | Entries |",
        "| --- | ---: | ---: |",
    ]
    for key, title, _ in BUCKETS:
        recs = [r for r in rows if r["bucket"] == key]
        ents = [r for r in merged if r["bucket"] == key]
        if recs:
            out.append(f"| {title.split(' — ')[0]} | {len(recs)} | {len(ents)} |")
    out.append("")

    for key, title, blurb in BUCKETS:
        ents = [r for r in merged if r["bucket"] == key]
        if not ents:
            continue
        out += ["", f"## {title}", "", blurb, ""]
        for r in ents:
            where = ", ".join(
                f"[{s['board']} {s['spec']}]({SITE}{s['url']})"
                for s in sorted(r["sources"], key=lambda s: s["board"])
            )
            proposed = r["text"][0].upper() + r["text"][1:]
            out.append(f"### {r['term']}")
            out.append("")
            out.append(f"- **id** `{r['id']}` · **notes** {where}")
            out.append(f"- **now** {r['text']}")
            if key == "clean":
                out.append(f"- **proposed** {proposed}")
            out.append(f"- **why** {r['reason']}")
            out.append("")

    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text("\n".join(out) + "\n", encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true",
                    help="validate only: fail on an unaccounted lower-case start")
    args = ap.parse_args()

    data = json.loads(DATA.read_text(encoding="utf-8"))
    rows = classify(data)

    if not args.check:
        write_report(rows)
        counts = {}
        for r in rows:
            counts[r["bucket"]] = counts.get(r["bucket"], 0) + 1
        print(f"wrote {REPORT.relative_to(ROOT)}")
        for key, title, _ in BUCKETS:
            if counts.get(key):
                print(f"  {counts[key]:>4}  {title}")
        return 0

    # --check: everything must be accounted for. A record is accounted for when
    # it is on the approved capitalisation list, or on the list of known
    # exceptions - which is what stops a new notes chip slipping through.
    cur = json.loads(CURATION.read_text(encoding="utf-8"))
    cap = cur.get("capitalise", {})
    approved = set(cap.get("apply", []))
    known = set(cap.get("leave", []))
    fails = []
    for r in rows:
        if r["id"] in approved or r["id"] in known:
            continue
        fails.append(f"{r['id']} ({r['board']} {r['spec']}): {r['bucket']} - "
                     f"{r['text'][:80]}")
    if fails:
        print(f"{len(fails)} definition(s) start lower-case and are not listed in "
              f"curation.json \"capitalise\":", file=sys.stderr)
        for f in sorted(fails):
            print(f"  - {f}", file=sys.stderr)
        print("\nRun without --check to regenerate the report.", file=sys.stderr)
        return 1
    print(f"capitalisation: {len(rows)} lower-case start(s), all accounted for")
    return 0


if __name__ == "__main__":
    sys.exit(main())

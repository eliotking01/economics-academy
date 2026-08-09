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
that produces "Is the increasing integration ...". Those instead get a rewrite
rule in curation.json, which replaces the lead-in when the page is generated -
see the "rewrite" block there and check 7 in verify_glossary.py.

Two mechanical signals separate the two, and neither is a judgement about
wording:

  1. chipHasColon - did the notes punctuate it "Term: definition"? A colon means
     the author wrote the definition as a standalone phrase.
  2. the leading word - a determiner or noun ("a", "the", "an", "when") opens a
     phrase; a finite verb or pronoun ("is", "are", "occurs", "provide", "this")
     needs the term in front of it to parse.

Nothing here edits a definition. It classifies and reports; the capitalisation
and the rewrites are both applied at render time by scripts/build_glossary.py,
from glossary-data/curation.json.

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
                # An example where a definition was expected. Resolved when the
                # notes' own list underneath has been attached to it.
                if src.get("definitionListHtml"):
                    bucket, reason = ("example",
                                      "an example, completed by the notes' list")
                else:
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
                "html": src["definitionHtml"],
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
    ("fragment", "Fragment — rewritten at render time",
     "The definition needs the term in front of it to parse: the notes wrote "
     "`Globalisation is the increasing integration ...`, so the extracted text "
     "starts on a verb and capitalising it would give `Is the increasing "
     "integration ...`.\n\n"
     "These are **not** capitalised. Each has a rule in `curation.json` under "
     "`rewrite` that replaces its lead-in when the page is generated, so the "
     "glossary reads correctly while the notes are left alone. 39 only drop a "
     "lead-in and capitalise the next word — no word is invented. The rest are "
     "marked `adds` or `not-a-definition` in that file and are the only new "
     "wording in the glossary outside `authored.json`.\n\n"
     "The `now` line below is what the **notes** say. What the page shows is "
     "the `to` value of the rule."),
    ("example", "Example plus the notes' own defining list — resolved",
     "The chip gives an example where a definition was expected — `Free trade "
     "area: e.g. USMCA` — and the defining characteristics are the bulleted "
     "list underneath it on the page. Those chips are named in "
     "`curation.json` → `attachList`, so the extractor takes the list as part "
     "of the definition, exactly as a trailing colon would make it. Still the "
     "notes' own words, and the verbatim check reads the list too. The "
     "lower-case `e.g.` is left alone deliberately."),
    ("notdef", "Not a definition",
     "These are examples that were chipped as if they were definitions, with "
     "nothing on the page to complete them. Capitalisation is not the problem "
     "with them."),
    ("symbol", "Intentional — leave alone",
     "These open on notation rather than a word. Nothing to change."),
    ("authored", "Authored entries",
     "From `glossary-data/authored.json`, which is hand-written — fix in place."),
    ("unknown", "Unclassified — needs a look",
     "The leading word did not match either list. Classify by hand."),
]


def write_report(rows) -> None:
    bg = load("build_glossary")
    rules = json.loads(CURATION.read_text(encoding="utf-8")) \
        .get("rewrite", {}).get("entries", {})
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
            if key == "fragment":
                rule = rules.get(bg.cap_key(r["id"], r["html"]))
                if rule:
                    out.append(f"- **shown** {rule['reads']}")
                    out.append(f"- **rule** `{rule['kind']}` — "
                               f"`{rule['from']}` → `{rule['to']}`")
                else:
                    out.append("- **shown** unchanged — no rewrite rule")
            out.append(f"- **why** {r['reason']}")
            out.append("")

    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text("\n".join(out) + "\n", encoding="utf-8")


def write_curation(rows) -> int:
    """Record the classification as the approved list in curation.json.

    Both lists are keyed on the wording, so a reworded notes chip drops off and
    has to be approved again. The value is the label a human reads - the key on
    its own says nothing.
    """
    bg = load("build_glossary")
    cur = json.loads(CURATION.read_text(encoding="utf-8"))
    # A record with a rewrite rule is accounted for by that rule; listing it
    # here as well would say it was left alone, which is no longer true.
    rules = cur.get("rewrite", {}).get("entries", {})
    apply_, leave = {}, {}
    for r in rows:
        key = bg.cap_key(r["id"], r["html"])
        if key in rules:
            continue
        label = f"{r['term']} - {r['text'][:60]}"
        (apply_ if r["bucket"] == "clean" else leave)[key] = label
    cur["capitalise"] = {
        "_comment": [
            "Which glossary definitions have their first letter capitalised at",
            "render time, by scripts/build_glossary.py. Nothing else about the",
            "wording changes, and glossary-data/terms.json is not touched - it",
            "stays byte-identical to the notes so the verbatim check still means",
            "what it says.",
            "",
            "apply  definitions the notes wrote as 'Term: definition'. Under a",
            "       heading they open on a noun phrase and read as complete.",
            "leave  definitions that need the term as their grammatical subject",
            "       ('Globalisation is the increasing integration ...'), plus",
            "       those opening on notation. Capitalising these would produce",
            "       'Is the increasing integration ...'. They are fixed in the",
            "       notes or not at all.",
            "",
            "Keyed on term id + a hash of the wording, so rewording the notes",
            "lapses the approval and --check asks for it again.",
            "",
            "Regenerate with: python3 scripts/check_glossary_capitalisation.py --approve",
        ],
        "apply": dict(sorted(apply_.items(), key=lambda kv: kv[1].lower())),
        "leave": dict(sorted(leave.items(), key=lambda kv: kv[1].lower())),
    }
    CURATION.write_text(json.dumps(cur, indent=2, ensure_ascii=False) + "\n",
                        encoding="utf-8")
    print(f"wrote {CURATION.relative_to(ROOT)}: "
          f"{len(apply_)} to capitalise, {len(leave)} left alone")
    return 0


def unclassified_exit(rows) -> int:
    """Non-zero while anything sits in the `unknown` bucket.

    This script used to exit 0 while reporting "2 Unclassified - needs a look",
    writing them into _working/glossary/capitalisation-report.md, which is
    unpublished and in nobody's path. They sat there from the day the glossary
    was built. A check that identifies work and then reports success cannot
    cause the work to happen - it is a queue nobody is subscribed to.

    Deliberately NOT given a suppression list, unlike
    verify_published_surface.py's KNOWN. There, the exception is a decision
    already taken with a scheduled fix. Here, the whole finding is that
    acknowledging these without acting on them is the failure mode, so the only
    way to make this exit 0 is to classify them. PH10-063.
    """
    unknown = [r for r in rows if r["bucket"] == "unknown"]
    if not unknown:
        return 0
    # stdout is block-buffered when piped, stderr is not: without this the
    # failure lands above the bucket counts it refers to.
    sys.stdout.flush()
    print(f"\nFAIL: {len(unknown)} definition(s) are unclassified and have been "
          f"waiting since the glossary was built:", file=sys.stderr)
    for r in sorted(unknown, key=lambda r: (r["id"], r["board"])):
        print(f"  - {r['id']} ({r['board']} {r['spec']}): {r['text'][:90]}",
              file=sys.stderr)
    print("\nClassify each one, then re-run. The routes, in the order the "
          "glossary's conventions prefer them: fix the wording in the notes page "
          "and re-extract; exclude the source in curation.json and add a "
          "`rewrite` rule; or author a definition in authored.json. Logged as G4 "
          "in REVIEW-NOTES.md. PH10-063.", file=sys.stderr)
    return 1


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true",
                    help="validate only: fail on an unaccounted lower-case start")
    ap.add_argument("--approve", action="store_true",
                    help="write the classification into curation.json")
    args = ap.parse_args()

    data = json.loads(DATA.read_text(encoding="utf-8"))
    rows = classify(data)

    if args.approve:
        return write_curation(rows)

    if not args.check:
        write_report(rows)
        counts = {}
        for r in rows:
            counts[r["bucket"]] = counts.get(r["bucket"], 0) + 1
        print(f"wrote {REPORT.relative_to(ROOT)}")
        for key, title, _ in BUCKETS:
            if counts.get(key):
                print(f"  {counts[key]:>4}  {title}")
        return unclassified_exit(rows)

    # --check: everything must be accounted for. A record is accounted for when
    # it is on the approved capitalisation list, or on the list of known
    # exceptions - which is what stops a new notes chip slipping through.
    bg = load("build_glossary")
    cur = json.loads(CURATION.read_text(encoding="utf-8"))
    cap = cur.get("capitalise", {})
    accounted = (set(cap.get("apply", {})) | set(cap.get("leave", {}))
                 | set(cur.get("rewrite", {}).get("entries", {})))
    fails = []
    for r in rows:
        if bg.cap_key(r["id"], r["html"]) in accounted:
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
    # "Accounted for" above means listed in curation.json. That is a different
    # question from "classified": the two Regulation definitions ARE listed, and
    # the classifier still cannot tell what to do with them because their
    # leading word matches neither list. Both have to hold. PH10-063.
    return unclassified_exit(rows)


if __name__ == "__main__":
    sys.exit(main())

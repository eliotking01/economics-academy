#!/usr/bin/env python3
"""Apply the brief's title, description and schema rules to notes-data/.

    python3 seo/tools/rewrite_notes_meta.py            # dry run, prints a diff
    python3 seo/tools/rewrite_notes_meta.py --apply    # write the JSON

Rewrites only the `head` block of notes-data/topics/**/*.json and
notes-data/hubs/*.json. It never opens a .html slice for writing: the slices
are verbatim byte records and the page's visible wording is not this script's
business. Metadata in JSON is scriptable; prose is not - CLAUDE.md hard rule 6.

Re-runnable and idempotent. Run it again after editing a page to refresh that
page's dateModified.

WHAT IS DELIBERATELY NOT TOUCHED
--------------------------------
revision-notes/index.html. Its <title>, H1, meta description and canonical are
on the frozen-head list - DECISIONS.md D50, "crown jewel" - and stay
byte-identical. It is not in notes-data/ at all, so this is a statement of
intent rather than a code path, but a future session extending this script to
the hand-written notes pages needs to know.

LearningResource.description is also left alone. It is a longer, differently
worded field from the meta description and always has been; the two are not
required to agree and rewriting it would put a second set of new sentences on
166 pages for no search gain.

THE DATES ARE STORED, NOT DERIVED AT BUILD TIME
-----------------------------------------------
build_notes_pages.py must stay a pure function of notes-data/, because
verify_generated.py re-runs every generator in a throwaway worktree and diffs
the result against the committed tree. A generator that read `git log` would
produce a different answer there and the check would go red on a correct
commit. So the dates are computed here, once, and written into the JSON as
data - the same way every other head field works.

datePublished is the EARLIER of the first commit touching the slice (with
--follow) and the first commit touching the rendered page. Seventeen slices
were created whole during the Wave 2 migration on 2026-08-11 and --follow
cannot see past that, but their pages existed months earlier; taking the
minimum recovers the real date, which for edexcel-theme-1/1-3-3-public-goods
is 2025-09-01 rather than 2026-08-11.

Standard library only.
"""

from __future__ import annotations

import argparse
import json
import pathlib
import re
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
sys.path.insert(0, str(ROOT / "scripts"))
import notes_extras  # noqa: E402
import notes_titles as nt  # noqa: E402

DATA = ROOT / "notes-data"
SITE = "https://economicsacademy.co.uk"
ORG = f"{SITE}/#organization"
# The Person node about.html defines, by the @id every root page already uses
# for it. Name and URL come from scripts/notes_extras.py, which is where the
# visible byline is written, so the schema cannot name a different person
# from the page.
PERSON = f"{SITE}{notes_extras.AUTHOR_URL}"
ABOUT = f"{SITE}/about.html"

BOARD_OF_DIR = {
    "edexcel-theme-1": ("Edexcel", "Theme 1"),
    "edexcel-theme-2": ("Edexcel", "Theme 2"),
    "edexcel-theme-3": ("Edexcel", "Theme 3"),
    "edexcel-theme-4": ("Edexcel", "Theme 4"),
    "aqa-a2-micro": ("AQA", "Microeconomics"),
    "aqa-a2-macro": ("AQA", "Macroeconomics"),
}

H1_RE = re.compile(r"<h1[^>]*>(.*?)</h1>", re.I | re.S)
SPEC_RE = re.compile(r"Specification Coverage:\s*</strong>\s*"
                     r"([A-Za-z][A-Za-z ]*?)\s+unit\s+(\d+(?:\.\d+)+)", re.I | re.S)
TAG_RE = re.compile(r"<[^>]+>")

# Hub titles. Seven pages, so the rule is written out rather than inferred:
# {Board} {Module} Revision Notes, the existing descriptor kept where the whole
# string stays inside 65 characters, and the " | Economics Academy" suffix
# dropped everywhere. The suffix is 22 characters that Google appends itself,
# and on three of these hubs it was the reason the descriptor could not fit.
#
# edexcel-theme-3 is the one that does not fit: its descriptor "Business
# Behaviour & Labour Market" lands the title on 66, one character over. The
# alternative was to drop the descriptor entirely, and that costs more - a
# bare "Edexcel Theme 3 Revision Notes" carries none of the words a student
# searching for business or labour-market notes would type. One word of
# Eliot's phrase goes instead, and the choice is on the approval list.
HUB_TITLES = {
    "edexcel-theme-1": "Edexcel Theme 1 Revision Notes | Markets & Market Failure",
    "edexcel-theme-2": "Edexcel Theme 2 Revision Notes | The UK Economy",
    "edexcel-theme-3": "Edexcel Theme 3 Revision Notes | Business & Labour Market",
    "edexcel-theme-4": "Edexcel Theme 4 Revision Notes | A Global Perspective",
    "aqa-a2-micro": "AQA A-Level Microeconomics Revision Notes",
    "aqa-a2-macro": "AQA A-Level Macroeconomics Revision Notes",
    "macro-application": "Macroeconomic Application | A-Level Economics Revision Notes",
}

# Hub descriptions, 145-158, front-loaded on the module. Each keeps the sub-
# concept list its own page already carried and drops the boilerplate closing
# sentence ("Every topic covered, with links to detailed notes on each
# subtopic"), which was 64 characters saying nothing a hub does not obviously
# do. No hub claims diagrams: a hub carries none, and §5 forbids naming a
# feature the page does not have even where the pages it links to do.
HUB_DESCRIPTIONS = {
    "edexcel-theme-1":
        "Theme 1 revision notes for Edexcel A-Level Economics: markets, "
        "market failure and government intervention. Free notes on every "
        "topic in the theme.",
    "edexcel-theme-2":
        "Theme 2 revision notes for Edexcel A-Level Economics: aggregate "
        "demand and supply, national income, economic growth and "
        "macroeconomic policy. Free.",
    "edexcel-theme-3":
        "Theme 3 revision notes for Edexcel A-Level Economics: business "
        "growth and objectives, costs, market structures and the labour "
        "market. Free, on every topic.",
    "edexcel-theme-4":
        "Theme 4 revision notes for Edexcel A-Level Economics: international "
        "economics, poverty and inequality, emerging economies and the role "
        "of the state. Free.",
    "aqa-a2-micro":
        "Microeconomics revision notes for AQA A-Level Economics: individual "
        "decision making, price determination, market structures and labour "
        "markets. Free.",
    "aqa-a2-macro":
        "Macroeconomics revision notes for AQA A-Level Economics: "
        "macroeconomic performance, AD and AS, financial markets, policy and "
        "the international economy.",
    "macro-application":
        "Real-world UK and South Africa macroeconomic data for A-Level "
        "Economics. Application points on growth, inflation, unemployment, "
        "trade, inequality and policy.",
}


def git_first(path: str, follow: bool) -> str:
    cmd = ["git", "-C", str(ROOT), "log", "--diff-filter=A",
           "--format=%ad", "--date=short", "-1"]
    if follow:
        cmd.append("--follow")
    out = subprocess.run(cmd + ["--", path], capture_output=True, text=True)
    return out.stdout.strip()


def git_last(path: str) -> str:
    out = subprocess.run(["git", "-C", str(ROOT), "log", "--format=%ad",
                          "--date=short", "-1", "--", path],
                         capture_output=True, text=True)
    return out.stdout.strip()


def text_of(fragment: str) -> str:
    return " ".join(TAG_RE.sub(" ", fragment).replace("&amp;", "&").split())


def set_if_present(block: dict, key: str, value: str) -> None:
    """Update a social tag only where the page already emits one.

    The six board hubs carry no twitter:title or twitter:description and are
    named in verify_page_shell.HEAD_EXEMPT for it, with a comment saying that
    a <head> which ADDED them "would be a change to what 21 pages emit, and
    that has to be a decision rather than a side effect". Twitter falls back
    to the og: tags, so the gain would be nil; this keeps that decision where
    it was made.
    """
    if key in block:
        block[key] = value


def for_head(value: str) -> str:
    """Store a string the way page_shell.render_head will emit it.

    render_head interpolates the title straight into <title> and the
    description straight into a content="" attribute - neither is escaped on
    the way out, which is why the six existing values containing an ampersand
    all carry "&amp;" in the JSON. Lengths are measured on the unescaped
    string, since that is what a reader and a SERP see; only the stored form
    is escaped. "&amp;" is the only entity in any title, description or H1 in
    notes-data/, so this is the whole of the conversion.
    """
    return value.replace("&", "&amp;")


def reading_minutes(words: int) -> int:
    """Whole minutes at 200 words a minute, never less than two.

    A revision page is read slowly and re-read, so this is a floor rather than
    a claim. Google has never used timeRequired for a rich result; it is here
    because §7 asks for it where a sensible figure can be computed, and one
    computed from the page's own word count is the only sensible kind.
    """
    return max(2, round(words / 200))


def enrich(lr: dict, *, name: str, board: str, module: str, code: str,
           words: int, published: str, modified: str) -> dict:
    """The §7 additions. Everything already present is left as it is."""
    lr["datePublished"] = published
    lr["dateModified"] = modified
    # A named Person author is the stronger signal and every competitor that
    # outranks this site has one. It needed Eliot's own words, which he
    # supplied on 2026-08-22 (task 4 of the manual to-do list); the byline and
    # bio are scripts/notes_extras.py's, and this node names the same person
    # by the same @id the Person node on about.html already carries, so the
    # page and its schema cannot disagree on who wrote it - verify_seo.py
    # assertion 20 fails if they do. The organisation stays as publisher,
    # which is what it is. The hubs keep the organisation as author too: they
    # carry no byline, and a schema claim the page does not make is the thing
    # 17 and 20 exist to stop.
    lr["author"] = {
        "@type": "Person",
        "@id": PERSON,
        "name": notes_extras.AUTHOR_NAME,
        "jobTitle": notes_extras.AUTHOR_JOB_TITLE,
        "url": ABOUT,
    }
    lr["publisher"] = {"@id": ORG}
    lr["audience"] = {"@type": "EducationalAudience", "educationalRole": "student"}
    lr["about"] = {"@type": "Thing", "name": name}
    # AQA gets the module and NOT the code. The 1.x.y / 2.x.y codes on this
    # site are site-local and deliberately not AQA's real 7136 codes; printing
    # one inside an educationalAlignment would assert it as a specification
    # reference, which is the one thing it is not.
    target = (f"{board} A-Level Economics {module}, unit {code}"
              if board == "Edexcel" else
              f"{board} A-Level Economics {module}")
    lr["educationalAlignment"] = {
        "@type": "AlignmentObject",
        "alignmentType": "educationalSubject",
        "targetName": target,
    }
    if words:
        lr["timeRequired"] = f"PT{reading_minutes(words)}M"
    return lr


def rewrite_topic(meta: pathlib.Path) -> dict:
    rec = json.loads(meta.read_text(encoding="utf-8"))
    head = rec["head"]
    slice_path = meta.with_suffix(".html")
    body = slice_path.read_text(encoding="utf-8")
    notes_dir, slug = meta.parent.name, meta.stem
    board, module = BOARD_OF_DIR[notes_dir]

    h1 = text_of(H1_RE.search(body).group(1))
    code = SPEC_RE.search(body).group(2)
    topic = nt.display_name(slug, h1)

    title, _ = nt.title_for(board, slug, h1, code)
    images = len(re.findall(r"<img\b", body)) + len(re.findall(r"<svg\b", body))
    kd = len(re.findall(r'class="key-definition"', body))
    evaluation = bool(re.search(r"<h[23]>[^<]*Evaluat", body))
    desc, _ = nt.description_for(
        topic, board, "macro" if module == "Macroeconomics" else "micro", code,
        head["description"].replace("&amp;", "&"), images=images,
        key_definitions=kd, evaluation=evaluation)

    head["title"] = for_head(title)
    head["description"] = for_head(desc)
    set_if_present(head["og"], "title", for_head(title))
    set_if_present(head["og"], "description", for_head(desc))
    set_if_present(head["twitter"], "title", for_head(title))
    set_if_present(head["twitter"], "description", for_head(desc))

    published = min(x for x in (git_first(str(slice_path.relative_to(ROOT)), True),
                                git_first(rec["path"], True)) if x)
    modified = git_last(str(slice_path.relative_to(ROOT))) or published
    words = len(text_of(body).split())
    for block in head.get("jsonldBeforeIcons", []):
        if block.get("@type") == "LearningResource":
            enrich(block, name=topic, board=board, module=module, code=code,
                   words=words, published=published, modified=modified)
    return rec


def rewrite_hub(meta: pathlib.Path) -> dict:
    rec = json.loads(meta.read_text(encoding="utf-8"))
    head = rec["head"]
    key = meta.stem
    title = HUB_TITLES[key]
    desc = HUB_DESCRIPTIONS[key]
    head["title"] = for_head(title)
    head["description"] = for_head(desc)
    set_if_present(head["og"], "title", for_head(title))
    set_if_present(head["og"], "description", for_head(desc))
    set_if_present(head["twitter"], "title", for_head(title))
    set_if_present(head["twitter"], "description", for_head(desc))

    slice_path = meta.with_suffix(".html")
    published = min(x for x in (git_first(str(slice_path.relative_to(ROOT)), True),
                                git_first(rec["path"], True)) if x)
    modified = git_last(str(slice_path.relative_to(ROOT))) or published
    board, module = ({"aqa-a2-micro": ("AQA", "Microeconomics"),
                      "aqa-a2-macro": ("AQA", "Macroeconomics")}
                     .get(key, ("Edexcel", key.replace("edexcel-theme-", "Theme "))))
    for block in head.get("jsonldBeforeIcons", []):
        if block.get("@type") == "LearningResource":
            block["datePublished"] = published
            block["dateModified"] = modified
            block["author"] = {"@id": ORG}
            block["publisher"] = {"@id": ORG}
            block["audience"] = {"@type": "EducationalAudience",
                                 "educationalRole": "student"}
            block["educationalAlignment"] = {
                "@type": "AlignmentObject",
                "alignmentType": "educationalSubject",
                "targetName": f"{board} A-Level Economics {module}",
            }
    return rec


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--apply", action="store_true", help="write the files")
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args()

    changed = 0
    for meta in sorted(DATA.rglob("*.json")):
        if meta.parent.name == "hubs":
            if meta.stem not in HUB_TITLES:
                continue
            new = rewrite_hub(meta)
        else:
            new = rewrite_topic(meta)
        old_text = meta.read_text(encoding="utf-8")
        new_text = json.dumps(new, indent=2, ensure_ascii=False) + "\n"
        if new_text == old_text:
            continue
        changed += 1
        if not args.quiet:
            old = json.loads(old_text)
            for field in ("title", "description"):
                if old["head"][field] != new["head"][field]:
                    print(f"  {new['path']}")
                    print(f"    - {old['head'][field]}")
                    print(f"    + {new['head'][field]}")
        if args.apply:
            meta.write_text(new_text, encoding="utf-8")

    print(f"{'wrote' if args.apply else 'would change'} {changed} records")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Task B4: the approved structured-data changes, on hand-written pages.

Three changes, all additive. The fourth approved change - removing
aggregateRating and the four Review objects from index.html - was a deletion
and was done by hand; see seo/08-structured-data.md for why it had to go.

  1. @id on every EducationalOrganization. The organisation is restated 354
     times across the site as publisher/provider/worksFor, always with an
     identical name and url. Giving every instance the same @id says they are
     one entity rather than 354 lookalikes.

     The nested blocks KEEP their name and url. Replacing them with a bare
     {"@id": ...} reference would be wrong: @id only merges nodes within a
     single page's graph, so a bare reference to a node defined on another
     page resolves to nothing and the information would simply be lost.

  2. @id on Eliot King's Person, so the copies inside Service on tutoring.html
     and marking.html, inside ContactPage, and inside founder on the homepage
     all point at the definition on about.html.

     Matched on "@type": "Person" IMMEDIATELY FOLLOWED BY "name": "Eliot King".
     The four Review author Persons on the homepage were also "@type": "Person"
     and must never have received Eliot's @id; they are now deleted, but the
     name guard is what makes this safe to re-run regardless.

  3. BreadcrumbList on the 17 indexable pages that have none. Every generated
     section already emits one - these are all hand-written. index.html is
     excluded on purpose: a homepage is the root of the trail, not a step in it.

Generated pages are NOT touched here. scripts/build_*.py emit the same @id, so
regenerating a section produces no diff. Run this, then rebuild, then confirm
the rebuild is clean.

Idempotent: every insertion is guarded on the value already being present.

    python3 seo/tools/fix_structured_data.py --dry-run
    python3 seo/tools/fix_structured_data.py --dry-run --diff 3
    python3 seo/tools/fix_structured_data.py
"""

from __future__ import annotations

import argparse
import difflib
import json
import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))
from inventory import build as build_inventory  # noqa: E402

SITE = "https://economicsacademy.co.uk"
ORG_ID = f"{SITE}/#organization"
PERSON_ID = f"{SITE}/about.html#eliot-king"

LD_RE = re.compile(r'(<script type="application/ld\+json">)(.*?)(</script>)', re.S)
ORG_RE = re.compile(r'^(\s*)"@type": "EducationalOrganization",$', re.M)
PERSON_RE = re.compile(
    r'^(\s*)"@type": "Person",\n(\s*)"name": "Eliot King",$', re.M)

# The trail for each page that has no BreadcrumbList. Written out rather than
# derived: these are 17 hand-written pages with four different shapes, and a
# derived trail would have had to guess the human label for each one.
TRAILS = {
    "about.html": [("Home", "/"), ("About", None)],
    "contact.html": [("Home", "/"), ("Contact", None)],
    "faq.html": [("Home", "/"), ("FAQ", None)],
    "marking.html": [("Home", "/"), ("Essay Marking", None)],
    "tutoring.html": [("Home", "/"), ("Tutoring", None)],
    "revision-notes/index.html": [("Home", "/"), ("Revision Notes", None)],
    "past-papers/index.html": [("Home", "/"), ("Past Papers", None)],
    "past-papers/aqa/index.html": [
        ("Home", "/"), ("Past Papers", "/past-papers/"), ("AQA", None)],
    "past-papers/edexcel/index.html": [
        ("Home", "/"), ("Past Papers", "/past-papers/"), ("Edexcel A", None)],
    "past-papers/edexcel-b/index.html": [
        ("Home", "/"), ("Past Papers", "/past-papers/"), ("Edexcel B", None)],
    "past-papers/ocr/index.html": [
        ("Home", "/"), ("Past Papers", "/past-papers/"), ("OCR", None)],
    "revision-notes/edexcel-theme-1/index.html": [
        ("Home", "/"), ("Revision Notes", "/revision-notes/"),
        ("Edexcel Theme 1", None)],
    "revision-notes/edexcel-theme-2/index.html": [
        ("Home", "/"), ("Revision Notes", "/revision-notes/"),
        ("Edexcel Theme 2", None)],
    "revision-notes/edexcel-theme-3/index.html": [
        ("Home", "/"), ("Revision Notes", "/revision-notes/"),
        ("Edexcel Theme 3", None)],
    "revision-notes/edexcel-theme-4/index.html": [
        ("Home", "/"), ("Revision Notes", "/revision-notes/"),
        ("Edexcel Theme 4", None)],
    "revision-notes/aqa-a2-micro/index.html": [
        ("Home", "/"), ("Revision Notes", "/revision-notes/"),
        ("AQA Microeconomics", None)],
    "revision-notes/aqa-a2-macro/index.html": [
        ("Home", "/"), ("Revision Notes", "/revision-notes/"),
        ("AQA Macroeconomics", None)],
}

GENERATED_ROOTS = ("practice-questions/", "past-paper-questions/", "flashcards/")


def is_generated(rel: str) -> bool:
    return rel.startswith(GENERATED_ROOTS) or "glossary" in rel


def breadcrumb_block(trail: list[tuple[str, str | None]], indent: str) -> str:
    items = []
    for n, (name, href) in enumerate(trail, start=1):
        item = {"@type": "ListItem", "position": n, "name": name}
        if href:
            item["item"] = SITE + href
        items.append(item)
    data = {"@context": "https://schema.org", "@type": "BreadcrumbList",
            "itemListElement": items}
    body = json.dumps(data, indent=2)
    body = "\n".join(indent + "  " + ln for ln in body.split("\n"))
    return (f'{indent}<script type="application/ld+json">\n'
            f"{body}\n{indent}</script>\n")


def patch(rel: str, text: str) -> str:
    out = text

    def add_org_id(m: re.Match) -> str:
        indent = m.group(1)
        return f'{indent}"@type": "EducationalOrganization",\n{indent}"@id": "{ORG_ID}",'

    def add_person_id(m: re.Match) -> str:
        i1, i2 = m.group(1), m.group(2)
        return (f'{i1}"@type": "Person",\n{i1}"@id": "{PERSON_ID}",\n'
                f'{i2}"name": "Eliot King",')

    # Only inside JSON-LD blocks, so nothing in the page body can be touched.
    def in_ld(m: re.Match) -> str:
        body = m.group(2)
        if f'"@id": "{ORG_ID}"' not in body:
            body = ORG_RE.sub(add_org_id, body)
        if f'"@id": "{PERSON_ID}"' not in body:
            body = PERSON_RE.sub(add_person_id, body)
        return m.group(1) + body + m.group(3)

    out = LD_RE.sub(in_ld, out)

    trail = TRAILS.get(rel)
    if trail and "BreadcrumbList" not in out:
        last = None
        for m in LD_RE.finditer(out):
            last = m
        if last is not None:
            indent = " " * (last.start() - out.rfind("\n", 0, last.start()) - 1)
            end = last.end()
            end += 1 if out[end:end + 1] == "\n" else 0
            out = out[:end] + breadcrumb_block(trail, indent) + out[end:]
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--diff", type=int, default=0)
    args = ap.parse_args()

    inv = build_inventory()
    pages = sorted(set(inv["indexable"]) | set(inv["deliberate_noindex"]))

    changed: list[tuple[Path, str, str]] = []
    skipped_generated = 0
    for rel in pages:
        if is_generated(rel):
            skipped_generated += 1
            continue
        path = REPO / rel
        text = path.read_text()
        new = patch(rel, text)
        if new != text:
            changed.append((path, text, new))

    # Every emitted block must parse, before anything is written.
    bad = []
    for path, _, new in changed:
        for m in LD_RE.finditer(new):
            try:
                json.loads(m.group(2))
            except json.JSONDecodeError as exc:
                bad.append(f"{path.relative_to(REPO)}: {exc}")

    print(f"hand-written pages to change : {len(changed)}")
    print(f"generated pages skipped      : {skipped_generated}")
    print(f"breadcrumb trails defined    : {len(TRAILS)}")
    print(f"JSON-LD parse failures       : {len(bad)}")
    for b in bad[:5]:
        print(f"   {b}")

    for path, old, new in changed[: args.diff]:
        r = path.relative_to(REPO)
        print(f"\n{'=' * 70}\n--- {r}\n{'=' * 70}")
        for line in difflib.unified_diff(old.split("\n"), new.split("\n"),
                                         lineterm="", n=2,
                                         fromfile=str(r), tofile=str(r)):
            print(line)

    if bad:
        print("\nABORTED - nothing written.", file=sys.stderr)
        return 1
    if args.dry_run:
        print("\nDRY RUN - nothing written.")
        return 0

    for path, _, new in changed:
        path.write_text(new)
    print(f"\nWritten: {len(changed)} files.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

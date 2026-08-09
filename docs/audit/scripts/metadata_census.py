#!/usr/bin/env python3
"""Per-page <head> and structured-data census across every published page.

Checks title/description uniqueness, canonical correctness, og:url agreement,
lang, meta robots, and which JSON-LD @types each page family emits. The SEO pass
of 2026-08-08 left all of these clean; this script is the regression detector,
not a discovery tool.

READ-ONLY. Run from the repo root:  python3 docs/audit/scripts/metadata_census.py
"""

import collections
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lib  # noqa: E402

TITLE = re.compile(r"<title>(.*?)</title>", re.S)
DESC = re.compile(r'<meta\s+name="description"\s+content="([^"]*)"', re.I)
CANON = re.compile(r'<link\s+rel="canonical"\s+href="([^"]*)"', re.I)
OGURL = re.compile(r'<meta\s+property="og:url"\s+content="([^"]*)"', re.I)
LANG = re.compile(r'<html[^>]*\blang="([^"]*)"', re.I)
ROBOTS = re.compile(r'<meta\s+name="robots"[^>]*content="([^"]*)"', re.I)
LDTYPE = re.compile(r'"@type"\s*:\s*"([^"]+)"')


def family(path):
    parts = path.split("/")
    if len(parts) == 1:
        return "(root)"
    if len(parts) == 2:
        return parts[0]
    return f"{parts[0]}/{parts[1]}"


def main():
    page_list = lib.pages()
    titles, descs = collections.Counter(), collections.Counter()
    langs, robots = collections.Counter(), collections.Counter()
    types = collections.Counter()
    types_by_family = collections.defaultdict(collections.Counter)
    family_size = collections.Counter()

    no_title, no_desc, no_canon, bad_canon, og_mismatch = [], [], [], [], []

    for p in page_list:
        s = lib.read(p)
        fam = family(p)
        family_size[fam] += 1

        m = TITLE.search(s)
        if m:
            titles[m.group(1).strip()] += 1
        else:
            no_title.append(p)

        m = DESC.search(s)
        if m:
            descs[m.group(1).strip()] += 1
        else:
            no_desc.append(p)

        m = CANON.search(s)
        canon = m.group(1) if m else None
        if not canon:
            no_canon.append(p)
        elif canon != lib.canonical_url(p):
            bad_canon.append((p, canon, lib.canonical_url(p)))

        m = OGURL.search(s)
        if m and canon and m.group(1) != canon:
            og_mismatch.append((p, m.group(1), canon))

        m = LANG.search(s)
        langs[m.group(1) if m else "MISSING"] += 1
        m = ROBOTS.search(s)
        robots[m.group(1) if m else "(none)"] += 1

        for t in set(LDTYPE.findall(s)):
            types[t] += 1
            types_by_family[t][fam] += 1

    print(f"pages: {len(page_list)}")
    print(f"missing <title>: {len(no_title)}  {no_title}")
    print(f"missing description: {len(no_desc)}  {no_desc}")
    print(f"missing canonical: {len(no_canon)}  {no_canon}")
    print(f"canonical != expected: {len(bad_canon)}")
    for row in bad_canon:
        print(f"   {row}")
    print(f"og:url != canonical: {len(og_mismatch)}")
    for row in og_mismatch:
        print(f"   {row}")
    print()
    dupt = {t: n for t, n in titles.items() if n > 1}
    dupd = {d: n for d, n in descs.items() if n > 1}
    print(f"duplicate titles: {len(dupt)} strings covering {sum(dupt.values())} pages")
    for t, n in sorted(dupt.items(), key=lambda x: -x[1])[:10]:
        print(f"   x{n}  {t[:88]}")
    print(f"duplicate descriptions: {len(dupd)} strings covering {sum(dupd.values())} pages")
    for d, n in sorted(dupd.items(), key=lambda x: -x[1])[:10]:
        print(f"   x{n}  {d[:88]}")
    print()
    print(f"lang: {dict(langs)}")
    print(f"meta robots: {dict(robots)}")
    print()
    print("=== JSON-LD @type coverage (pages emitting / pages in family) ===")
    for t, n in types.most_common():
        gaps = [f"{f} {types_by_family[t][f]}/{family_size[f]}"
                for f in sorted(family_size)
                if 0 < types_by_family[t][f] < family_size[f]]
        flag = "  PARTIAL: " + "; ".join(gaps) if gaps else ""
        print(f"  {n:4d}  {t}{flag}")


if __name__ == "__main__":
    main()

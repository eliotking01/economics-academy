#!/usr/bin/env python3
"""Internal link graph, computed TWICE: raw HTML, then plus JS-injected links.

The delta is the point. Header and footer are fetched at runtime by
js/components/inject-templates.js, so a non-rendering crawler sees neither. This
script quantifies exactly which URLs depend on that injection and by how much.

READ-ONLY. Run from the repo root:  python3 docs/audit/scripts/link_graph.py
"""

import collections
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lib  # noqa: E402

TEMPLATES = ["templates/header.html", "templates/footer.html"]


def build():
    page_list = lib.pages()

    resolvable = set()
    for p in page_list:
        resolvable |= lib.url_variants(p)
    for p in lib.tracked("*.pdf"):
        if lib.is_published(p):
            resolvable.add("/" + p)

    raw = collections.Counter()
    broken = collections.Counter()
    for p in page_list:
        for target in lib.links_from(p):
            raw[target] += 1
            if target not in resolvable:
                broken[target] += 1

    # Every page injects the same header and footer, so each template link is an
    # edge from all len(page_list) pages.
    injected = collections.Counter()
    for t in TEMPLATES:
        for target in lib.links_from(t):
            injected[target] += len(page_list)

    return page_list, raw, injected, broken, resolvable


def main():
    page_list, raw, injected, broken, resolvable = build()

    print(f"published pages: {len(page_list)}")
    print(f"raw internal edges: {sum(raw.values())}")
    print(f"injected edges: {sum(injected.values())}")
    print()

    print("=== BROKEN internal targets (raw HTML) ===")
    if not broken:
        print("  none")
    for target, n in broken.most_common():
        print(f"  {n:4d}  {target}")
    print()

    print("=== ORPHANS: published pages with zero raw inbound links ===")
    orphans = []
    for p in page_list:
        if not any(raw.get(v, 0) for v in lib.url_variants(p)):
            orphans.append(p)
    for p in orphans:
        print(f"  {p}")
    print(f"  ({len(orphans)} of {len(page_list)}; "
          f"{len(page_list) - len(orphans)} reachable without JavaScript)")
    print()

    print("=== INJECTION DEPENDENCY: every target the templates link to ===")
    print(f"{'raw':>6} {'injected':>9} {'total':>7} {'inj%':>7}  url")
    rows = sorted(((t, raw.get(t, 0), n) for t, n in injected.items()),
                  key=lambda r: r[1])
    for target, r, i in rows:
        print(f"{r:>6} {i:>9} {r + i:>7} {i / (r + i) * 100:6.1f}%  {target}")


if __name__ == "__main__":
    main()

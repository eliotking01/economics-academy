#!/usr/bin/env python3
"""Resolve every internal link and fragment in the revision notes.

The site has no build step and no link checker, so a removed section or a
mistyped href fails silently in production. This walks every note page,
collects hrefs and src attributes, and checks that each one resolves to a
file on disk and, where a fragment is given, to an id on the target page.

External links (http, mailto, tel) are reported but not fetched.

Usage:
    python3 scripts/verify_links.py [root ...]     # defaults to revision-notes/
Exit status is non-zero if anything fails to resolve.
"""

import pathlib
import re
import sys
from html.parser import HTMLParser

REPO = pathlib.Path(__file__).resolve().parent.parent
EXTERNAL = re.compile(r"^(https?:|mailto:|tel:|data:|//)")


class Collector(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.refs = []      # (attr_value, line)
        self.ids = set()

    def _scan(self, attrs):
        line = self.getpos()[0]
        for name, value in attrs:
            if not value:
                continue
            if name == "id":
                self.ids.add(value)
            elif name in ("href", "src"):
                self.refs.append((value, line))

    handle_starttag = lambda self, tag, attrs: self._scan(attrs)
    handle_startendtag = lambda self, tag, attrs: self._scan(attrs)


def collect(path):
    p = Collector()
    p.feed(path.read_text(encoding="utf-8"))
    p.close()
    return p


def resolve(ref, page):
    """Map an href to a path on disk. Root-relative hrefs are repo-relative.

    Cache-busting query strings (?v=2) are stripped before resolving.
    """
    target = ref.split("#", 1)[0].split("?", 1)[0]
    if not target:
        return page
    if target.startswith("/"):
        return REPO / target.lstrip("/")
    return (page.parent / target).resolve()


def main(argv):
    roots = [pathlib.Path(a) for a in argv[1:]] or [pathlib.Path("revision-notes")]
    pages = []
    for root in roots:
        pages.extend(sorted(root.rglob("*.html")) if root.is_dir() else [root])

    ids_cache = {}
    checked = external = 0
    broken_href = []
    broken_fragment = []

    for page in pages:
        info = collect(page)
        ids_cache[page.resolve()] = info.ids
        for ref, line in info.refs:
            if EXTERNAL.match(ref):
                external += 1
                continue
            checked += 1
            target = resolve(ref, page)
            if not target.exists():
                broken_href.append((page, line, ref))
                continue
            if "#" in ref:
                frag = ref.split("#", 1)[1]
                if not frag:
                    continue
                key = target.resolve()
                if key not in ids_cache:
                    if key.suffix != ".html":
                        continue
                    ids_cache[key] = collect(key).ids
                if frag not in ids_cache[key]:
                    broken_fragment.append((page, line, ref))

    for page, line, ref in broken_href:
        print(f"BROKEN HREF      {page}:{line}  ->  {ref}")
    for page, line, ref in broken_fragment:
        print(f"BROKEN FRAGMENT  {page}:{line}  ->  {ref}")

    print(f"\n{len(pages)} pages, {checked} internal refs checked "
          f"({external} external skipped)")
    print(f"  broken hrefs:     {len(broken_href)}")
    print(f"  broken fragments: {len(broken_fragment)}")
    return 1 if (broken_href or broken_fragment) else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))

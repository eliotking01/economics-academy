#!/usr/bin/env python3
"""Prove that a commit changed no visible wording.

Extracts the plain text of every note page at two commits, normalises
whitespace, and diffs. Used to gate the formatting and emphasis commits,
where the rule is that markup may change but not a single word.

Script, style and comment content is dropped, since none of it is visible
text. Everything else - including the contents of inline elements such as
<strong> and <em> - is kept, so moving a tag boundary across a word would
still be caught.

Usage:
    python3 scripts/verify_text_integrity.py <before-ref> [<after-ref>]

<after-ref> defaults to the working tree. Exit status is non-zero if any
file's visible text differs.
"""

import difflib
import pathlib
import re
import subprocess
import sys
from html.parser import HTMLParser

SKIP = {"script", "style"}


class TextExtractor(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts = []
        self.skip_depth = 0

    def handle_starttag(self, tag, attrs):
        if tag in SKIP:
            self.skip_depth += 1

    def handle_endtag(self, tag):
        if tag in SKIP and self.skip_depth:
            self.skip_depth -= 1

    def handle_data(self, data):
        if not self.skip_depth:
            self.parts.append(data)

    def text(self):
        return re.sub(r"\s+", " ", "".join(self.parts)).strip()


def extract(source):
    p = TextExtractor()
    p.feed(source)
    p.close()
    return p.text()


def read_at(ref, path):
    """File contents at a git ref, or from the working tree if ref is None."""
    if ref is None:
        return pathlib.Path(path).read_text(encoding="utf-8")
    result = subprocess.run(
        ["git", "show", f"{ref}:{path}"],
        capture_output=True, text=True,
    )
    return result.stdout if result.returncode == 0 else None


def list_files(ref):
    if ref is None:
        return sorted(str(p) for p in pathlib.Path("revision-notes").rglob("*.html"))
    out = subprocess.run(
        ["git", "ls-tree", "-r", "--name-only", ref, "revision-notes"],
        capture_output=True, text=True, check=True,
    ).stdout.split()
    return sorted(f for f in out if f.endswith(".html"))


def main(argv):
    if len(argv) < 2:
        print(__doc__)
        return 2
    before = argv[1]
    after = argv[2] if len(argv) > 2 else None

    files = list_files(before)
    differing = []
    missing = []

    for path in files:
        old = read_at(before, path)
        new = read_at(after, path)
        if new is None:
            missing.append(path)
            continue
        a, b = extract(old), extract(new)
        if a != b:
            differing.append((path, a, b))

    for path, a, b in differing:
        print(f"\n=== {path}")
        for line in list(difflib.unified_diff(
            a.split(" "), b.split(" "), lineterm="", n=6
        ))[:40]:
            print(f"  {line}")

    print(
        f"\n{len(files)} files compared between {before} and "
        f"{after or 'working tree'}"
    )
    print(f"  visible text differs: {len(differing)}")
    if missing:
        print(f"  absent from the later revision: {len(missing)}")
        for m in missing:
            print(f"    {m}")
    return 1 if differing else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))

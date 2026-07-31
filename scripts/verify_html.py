#!/usr/bin/env python3
"""Strict well-formedness check for the revision-notes HTML.

There is no build step on this site, so nothing else catches a broken tag.
Uses only the standard library: html.parser is available everywhere, bs4 and
lxml are not installed.

Reports, per file:
  - unclosed tags at EOF
  - mismatched closing tags
  - closing tags with no opener
  - duplicate id attributes

Usage:
    python3 scripts/verify_html.py [path ...]      # defaults to revision-notes/
Exit status is non-zero if any file has an error.
"""

import sys
import pathlib
from html.parser import HTMLParser

# Elements that never have a closing tag.
VOID = {
    "area", "base", "br", "col", "embed", "hr", "img", "input",
    "link", "meta", "param", "source", "track", "wbr",
}


class Checker(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack = []
        self.errors = []
        self.ids = {}

    def handle_starttag(self, tag, attrs):
        for name, value in attrs:
            if name == "id" and value:
                if value in self.ids:
                    self.errors.append(
                        f"line {self.getpos()[0]}: duplicate id {value!r} "
                        f"(first seen on line {self.ids[value]})"
                    )
                else:
                    self.ids[value] = self.getpos()[0]
        if tag not in VOID:
            self.stack.append((tag, self.getpos()[0]))

    def handle_startendtag(self, tag, attrs):
        # <img ... /> — self-closing, so only the id check applies.
        for name, value in attrs:
            if name == "id" and value:
                if value in self.ids:
                    self.errors.append(
                        f"line {self.getpos()[0]}: duplicate id {value!r} "
                        f"(first seen on line {self.ids[value]})"
                    )
                else:
                    self.ids[value] = self.getpos()[0]

    def handle_endtag(self, tag):
        if tag in VOID:
            return
        line = self.getpos()[0]
        if not self.stack:
            self.errors.append(f"line {line}: </{tag}> with no opening tag")
            return
        if self.stack[-1][0] == tag:
            self.stack.pop()
            return
        # Look for the opener further down the stack.
        for depth in range(len(self.stack) - 1, -1, -1):
            if self.stack[depth][0] == tag:
                unclosed = ", ".join(
                    f"<{t}> (line {ln})" for t, ln in self.stack[depth + 1:]
                )
                self.errors.append(
                    f"line {line}: </{tag}> closes an element opened on line "
                    f"{self.stack[depth][1]}, leaving unclosed: {unclosed}"
                )
                del self.stack[depth:]
                return
        self.errors.append(f"line {line}: </{tag}> with no opening tag")

    def finish(self):
        for tag, line in self.stack:
            self.errors.append(f"line {line}: <{tag}> is never closed")
        return self.errors


def check(path):
    parser = Checker()
    parser.feed(path.read_text(encoding="utf-8"))
    parser.close()
    return parser.finish()


def main(argv):
    roots = [pathlib.Path(a) for a in argv[1:]] or [pathlib.Path("revision-notes")]
    files = []
    for root in roots:
        files.extend(sorted(root.rglob("*.html")) if root.is_dir() else [root])

    failed = 0
    for path in files:
        errors = check(path)
        if errors:
            failed += 1
            print(f"\n{path}")
            for e in errors:
                print(f"  {e}")

    print(f"\n{len(files)} files parsed, {failed} with errors")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))

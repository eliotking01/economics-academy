#!/usr/bin/env python3
"""Prove that a commit destroyed no inline markup.

verify_text_integrity.py compares visible text, which is blind to a whole
class of damage: stripping an <a> or a key-definition span changes no text
at all, so the text check passes while a link silently disappears. This
script closes that gap by counting tags and link targets instead.

Reports, per file:
  - any element type whose count DROPPED (additions are counted but not
    flagged, since enrichment legitimately adds elements)
  - any href or src that was present before and is gone after

Structural tags that enrichment work legitimately adds (div, table, tr, td,
th, thead, tbody, p, h3, strong, em, section) are ignored by default, since
adding a worked example changes all of them. Pass --strict to compare those
too.

Usage:
    python3 scripts/verify_markup_integrity.py <before-ref> [<after-ref>] [--strict]
"""

import collections
import pathlib
import re
import subprocess
import sys

STRUCTURAL = {
    "div", "table", "thead", "tbody", "tr", "td", "th",
    "p", "h2", "h3", "strong", "em", "section", "ul", "ol", "li",
}

TAG = re.compile(r"<([a-zA-Z][a-zA-Z0-9]*)\b")
REF = re.compile(r'(?:href|src)="([^"]+)"')


def body_of(source):
    """Only the note body — head metadata is not what this is guarding."""
    return source.split('<div class="notes-container">', 1)[-1]


def read_at(ref, path):
    if ref is None:
        return pathlib.Path(path).read_text(encoding="utf-8")
    r = subprocess.run(["git", "show", f"{ref}:{path}"],
                       capture_output=True, text=True)
    return r.stdout if r.returncode == 0 else None


def list_files(ref):
    if ref is None:
        return sorted(str(p) for p in pathlib.Path("revision-notes").rglob("*.html"))
    out = subprocess.run(
        ["git", "ls-tree", "-r", "--name-only", ref, "revision-notes"],
        capture_output=True, text=True, check=True,
    ).stdout.split()
    return sorted(f for f in out if f.endswith(".html"))


def profile(source):
    body = body_of(source)
    counts = collections.Counter(TAG.findall(body))
    counts["span.key-definition"] = len(re.findall(r'class="key-definition"', body))
    refs = collections.Counter(REF.findall(body))
    return counts, refs


def main(argv):
    args = [a for a in argv[1:] if not a.startswith("--")]
    strict = "--strict" in argv
    if not args:
        print(__doc__)
        return 2
    before, after = args[0], (args[1] if len(args) > 1 else None)

    problems = 0
    gains = 0
    for path in list_files(before):
        old, new = read_at(before, path), read_at(after, path)
        if new is None:
            continue
        (oc, orefs), (nc, nrefs) = profile(old), profile(new)

        if not strict:
            for tag in STRUCTURAL:
                oc.pop(tag, None)
                nc.pop(tag, None)

        # Only a DROP is a problem. Enrichment legitimately adds elements, and
        # flagging those buries the losses that matter.
        for tag in sorted(set(oc) | set(nc)):
            was, now = oc.get(tag, 0), nc.get(tag, 0)
            if now < was:
                problems += 1
                print(f"TAG   {path}: <{tag}> {was} -> {now}")
            elif now > was:
                gains += 1

        for ref in sorted(orefs):
            if orefs[ref] > nrefs.get(ref, 0):
                problems += 1
                print(f"REF   {path}: lost {ref!r}")

    print(f"\ncompared {before} -> {after or 'working tree'}: "
          f"{problems} losses, {gains} additions (additions are not problems)")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))

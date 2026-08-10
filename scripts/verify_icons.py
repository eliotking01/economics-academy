#!/usr/bin/env python3
"""Every icon the site asks for is in the Font Awesome subset that ships.

    python3 scripts/verify_icons.py

Pure stdlib. Exit code 1 if anything is flagged.

WHY THIS EXISTS

`css/fontawesome-all.min.css` is a subset: 15 glyphs of 1,458, one face of
three, and `webfonts/fa-solid-900.woff2` is subsetted to match. A subset font
fails **silently** — a glyph that is not in it renders as nothing at all, no
console error, no tofu box on the pages checked.

That is not hypothetical. faq.html shipped 30 `class="icon fa-plus"` spans
that asked for weight 400, where `plus` is a solid-only glyph in Font Awesome
Free 5. Every one of them rendered nothing, the accordion had no open/close
indicator, and the JS spent its life toggling between two invisible states.
It took a pixel diff during Wave 4.2 to notice. This script is what stops the
next one taking as long.

THE THREE WAYS IT CAN GO WRONG, AND THE CHECK FOR EACH

1. A page uses an icon class with no rule in the stylesheet. Add
   `class="icon solid fa-rocket"` and nothing appears.
2. A stylesheet sets `content: "\\f135"` directly, the way css/main.css does
   for the mobile nav hamburger, for a codepoint the subset does not carry.
3. The stylesheet gained a rule but nobody re-ran
   `scripts/subset_fontawesome.py`, so the rule exists and the glyph does
   not. This is the one a CSS-only checker cannot see: reading a woff2 needs
   brotli, which is not stdlib. The subsetter writes
   `_working/fontawesome/subset-manifest.txt` recording what actually went
   into the font, and check 3 compares the two.
"""

from __future__ import annotations

import hashlib
import pathlib
import re
import subprocess
import sys

REPO = pathlib.Path(__file__).resolve().parent.parent
STYLESHEET = REPO / "css" / "fontawesome-all.min.css"
FONT = REPO / "webfonts" / "fa-solid-900.woff2"
MANIFEST = REPO / "_working" / "fontawesome" / "subset-manifest.txt"

CONTENT_RULE = re.compile(
    r'\.fa-([a-z0-9-]+):before\s*\{\s*content:\s*"\\([0-9a-f]{4})";\s*\}')
CLASS_ATTR = re.compile(r'class="([^"]*)"')
# The private use area Font Awesome lives in. Nothing else on this site sets
# a `content` in that range.
FA_CONTENT = re.compile(r'content:\s*"\\(f[0-9a-f]{3})"')


def tracked(*globs: str) -> list[pathlib.Path]:
    out = subprocess.run(["git", "ls-files", *globs], cwd=REPO,
                         capture_output=True, text=True, check=True)
    return [REPO / line for line in out.stdout.split()]


def main() -> int:
    if not STYLESHEET.is_file():
        sys.exit(f"missing {STYLESHEET.relative_to(REPO)}")

    rules = {name: int(code, 16)
             for name, code in CONTENT_RULE.findall(
                 STYLESHEET.read_text(encoding="utf-8"))}
    problems: list[str] = []

    # 1. every fa- class used in markup or in JS has a rule
    used: dict[str, set[str]] = {}
    for path in tracked("*.html", "*.js"):
        if path.parts[-2:] == ("css", "fontawesome-all.min.css"):
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        names = set()
        for value in CLASS_ATTR.findall(text):
            names |= {t for t in value.split() if t.startswith("fa-")}
        # JS builds class strings too — reviews-render.js does
        for value in re.findall(r'classList\.add\("(fa-[a-z0-9-]+)"\)', text):
            names.add(value)
        for name in names:
            used.setdefault(name, set()).add(
                str(path.relative_to(REPO)))

    for name, files in sorted(used.items()):
        if name[3:] not in rules:
            problems.append(
                f"{name} is used but has no rule in "
                f"{STYLESHEET.relative_to(REPO)} — it will render as "
                f"nothing. Used in: {', '.join(sorted(files)[:3])}")

    # 2. every direct content: "\fXXX" in the site's own CSS is carried
    codes = set(rules.values())
    from_css: set[int] = set()
    for path in tracked("css/*.css", "css/pages/*.css"):
        if path == STYLESHEET or "vendor" in path.parts:
            continue
        for code in FA_CONTENT.findall(
                path.read_text(encoding="utf-8", errors="ignore")):
            from_css.add(int(code, 16))
            if int(code, 16) not in codes:
                problems.append(
                    f'{path.relative_to(REPO)} sets content: "\\{code}", '
                    f"which the subset does not carry")

    # 3. the font on disk is the one the stylesheet describes
    if not MANIFEST.is_file():
        problems.append(
            f"missing {MANIFEST.relative_to(REPO)} — run "
            "scripts/subset_fontawesome.py --apply")
    else:
        lines = MANIFEST.read_text(encoding="utf-8").splitlines()
        recorded = {int(p[1], 16) for p in (line.split() for line in lines)
                    if p and p[0] == "glyph"}
        digest = next((p[1] for p in (line.split() for line in lines)
                       if p and p[0] == "sha256"), None)
        for name, code in sorted(rules.items(), key=lambda kv: kv[1]):
            if code not in recorded:
                problems.append(
                    f"fa-{name} (U+{code:04X}) has a rule but is not in the "
                    "shipped font — re-run scripts/subset_fontawesome.py "
                    "--apply")
        stale = recorded - codes
        if stale:
            problems.append(
                "the font carries glyphs the stylesheet no longer names: "
                + ", ".join(f"U+{c:04X}" for c in sorted(stale))
                + " — re-run scripts/subset_fontawesome.py --apply")
        if FONT.is_file() and digest:
            actual = hashlib.sha256(FONT.read_bytes()).hexdigest()
            if actual != digest:
                problems.append(
                    f"{FONT.relative_to(REPO)} does not match the manifest "
                    "— it was replaced without re-running the subsetter")

    print(f"{len(rules)} icon rules, {len(used)} classes used across "
          f"{len(set().union(*used.values())) if used else 0} files")
    # A rule reached only through a CSS `content` is used, just not as a
    # class — css/main.css's hamburger is the case. Do not call it spare.
    unused = sorted(n for n, code in rules.items()
                    if "fa-" + n not in used and code not in from_css)
    if unused:
        print("  spare rules, reached by no class and no CSS content "
              "(not a failure): " + ", ".join("fa-" + u for u in unused))

    if problems:
        print(f"\n{len(problems)} problem(s):")
        for p in problems:
            print(f"  {p}")
        return 1

    print("every icon the site uses is in the stylesheet and in the font")
    return 0


if __name__ == "__main__":
    sys.exit(main())

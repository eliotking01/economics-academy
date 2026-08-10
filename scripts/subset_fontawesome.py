#!/usr/bin/env python3
"""Subset the Font Awesome solid font to the glyphs css/fontawesome-all.min.css asks for.

A one-off conversion, not a build step and not part of the verification suite.
It needs fonttools and brotli, which along with Pillow are the only non-stdlib
packages this repo uses; everything CI runs is stdlib-only and stays that way.

    python3 scripts/subset_fontawesome.py            # dry run, writes nothing
    python3 scripts/subset_fontawesome.py --apply

Dry run by default, like the mutators in seo/tools/ and reencode_diagrams.py.

SOURCE AND OUTPUT

    _working/fontawesome/fa-solid-900.woff2   full Font Awesome Free 5.15.4
    webfonts/fa-solid-900.woff2               the subset, published

The full font stays in `_working/`, which Jekyll never publishes (both the
`_` prefix rule and line 64 of _config.yml). Keeping it means adding an icon
later is "add the rule, re-run this" rather than "recover the font from git
history first". Do not delete it and do not move it into webfonts/.

THE GLYPH LIST IS NOT IN THIS FILE

It is read from the `.fa-*:before { content: "\\fXXX" }` rules in
css/fontawesome-all.min.css, so the stylesheet and the font cannot disagree.
Add an icon by adding its rule there and re-running; there is no second list
to keep in step. `scripts/verify_icons.py` checks that every icon the site
actually uses has such a rule, which is the other half of the same guarantee.

WHY THIS NEEDS A GUARD AT ALL

A subset font fails silently: a glyph that is not in it renders as nothing,
which is exactly how faq.html's 30 accordion `+` icons went missing without
anyone noticing. verify_icons.py is in the CI workflow for that reason.
"""

from __future__ import annotations

import argparse
import hashlib
import pathlib
import re
import sys

try:
    from fontTools import subset
    from fontTools.ttLib import TTFont
except ModuleNotFoundError:
    sys.exit("fonttools and brotli are required: "
             "python3 -m pip install fonttools brotli")

REPO = pathlib.Path(__file__).resolve().parent.parent
SOURCE = REPO / "_working" / "fontawesome" / "fa-solid-900.woff2"
OUTPUT = REPO / "webfonts" / "fa-solid-900.woff2"
MANIFEST = REPO / "_working" / "fontawesome" / "subset-manifest.txt"
STYLESHEET = REPO / "css" / "fontawesome-all.min.css"

CONTENT_RULE = re.compile(
    r'\.fa-([a-z0-9-]+):before\s*\{\s*content:\s*"\\([0-9a-f]{4})";\s*\}')


def write_manifest(icons: dict[str, int], data: bytes) -> None:
    """Record what actually went into the font, for verify_icons.py.

    Without this, a stdlib checker can only prove the stylesheet is
    self-consistent. It cannot open a woff2 — that needs brotli. So editing
    the stylesheet and forgetting to re-run this script would reproduce the
    exact silent failure the subset is supposed to be guarded against: a rule
    exists, the glyph does not, the icon renders as nothing. The manifest is
    what lets the checker notice.
    """
    lines = [
        "# Written by scripts/subset_fontawesome.py. Do not hand-edit.",
        "# What is actually in webfonts/fa-solid-900.woff2, so that",
        "# scripts/verify_icons.py can check the stylesheet against it",
        "# without needing brotli to open the font.",
        f"sha256 {hashlib.sha256(data).hexdigest()}",
        f"bytes {len(data)}",
    ]
    lines += [f"glyph {code:04x} fa-{name}"
              for name, code in sorted(icons.items(), key=lambda kv: kv[1])]
    MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    MANIFEST.write_text("\n".join(lines) + "\n", encoding="utf-8")


def wanted_codepoints() -> dict[str, int]:
    css = STYLESHEET.read_text(encoding="utf-8")
    return {name: int(code, 16)
            for name, code in CONTENT_RULE.findall(css)}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true",
                    help="write the file; without it nothing is touched")
    args = ap.parse_args()

    if not SOURCE.is_file():
        sys.exit(f"missing source font: {SOURCE.relative_to(REPO)}\n"
                 "Recover it from git history — see the docstring.")

    icons = wanted_codepoints()
    if not icons:
        sys.exit(f"no .fa-*:before rules found in "
                 f"{STYLESHEET.relative_to(REPO)} — refusing to subset to "
                 "nothing")

    # recalcTimestamp belongs on the constructor, not on subset.Options: with
    # it left at the default, head.modified is stamped with the current time
    # and two runs a second apart produce different bytes. Caught by hashing
    # three consecutive runs, which is worth doing to any generator here.
    font = TTFont(SOURCE, recalcTimestamp=False)
    have = set()
    for table in font["cmap"].tables:
        have |= set(table.cmap)
    missing = {n: c for n, c in icons.items() if c not in have}
    if missing:
        print("PROBLEMS — the stylesheet asks for glyphs the source font "
              "does not have:")
        for name, code in sorted(missing.items()):
            print(f"  fa-{name}  U+{code:04X}")
        return 1

    options = subset.Options()
    options.flavor = "woff2"
    options.layout_features = []
    options.notdef_outline = False

    subsetter = subset.Subsetter(options=options)
    subsetter.populate(unicodes=sorted(icons.values()))
    subsetter.subset(font)

    import io
    buf = io.BytesIO()
    font.flavor = "woff2"
    font.save(buf)
    data = buf.getvalue()

    before = OUTPUT.stat().st_size if OUTPUT.is_file() else 0
    print(f"{len(icons)} glyphs from {STYLESHEET.relative_to(REPO)}: "
          + ", ".join(f"fa-{n}" for n in sorted(icons)))
    print(f"\n{SOURCE.stat().st_size / 1024:.1f} KB source -> "
          f"{len(data) / 1024:.1f} KB subset"
          f"   (on disk now: {before / 1024:.1f} KB)")

    if OUTPUT.is_file() and OUTPUT.read_bytes() == data:
        print("\nalready up to date; nothing to write.")
        return 0

    if not args.apply:
        print("\ndry run: nothing written. Re-run with --apply.")
        return 0

    OUTPUT.write_bytes(data)
    write_manifest(icons, data)
    print(f"\nwrote {OUTPUT.relative_to(REPO)}")
    print(f"wrote {MANIFEST.relative_to(REPO)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

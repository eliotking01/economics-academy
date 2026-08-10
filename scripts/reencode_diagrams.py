#!/usr/bin/env python3
"""Re-encode the notes diagram PNGs to a 64-colour palette, in place.

A one-off conversion, not a build step and not part of the verification suite.
It needs Pillow, which is the only non-stdlib dependency anywhere in this repo;
everything in `scripts/` that CI runs is stdlib-only and stays that way.

    python3 scripts/reencode_diagrams.py            # dry run, writes nothing
    python3 scripts/reencode_diagrams.py --apply

Dry run by default, like the five mutators in `seo/tools/`, so a no-flag re-run
after the conversion is harmless.

WHAT IT DOES NOT DO, AND WHY

**It does not resize.** The roadmap asked for 1600 px as well, and measurement
said no. The `width`/`height` attributes on all 293 `<img>` tags carry each
file's intrinsic pixel size, and browsers use them for the aspect ratio, so a
resize means editing every one of them or introducing layout shift where there
is none. What that would buy is 0.61 MiB across the whole site - the palette
does 79.4% and the resize adds 2.3 points - and it would cost sharpness: the
notes container is about 1088 CSS px wide, so 2176 device px on a 2x display,
and most of these files are 2200-3600 px today. Resampling to 2200 px measured
*larger* than not resizing at all, because Lanczos invents intermediate colours
that the palette then has to spend entries on.

**It does not use fast-octree**, which is smaller still at 4.48 MiB. Octree
maps the white background to (254,254,254) on all 112 images, so every diagram
would render as a faint grey rectangle against the page. Median cut keeps pure
white in the palette on 112 of 112. Fidelity beats 0.93 MiB.

**It does not dither.** Pillow ignores the flag for median cut anyway, and
these are flat-colour line drawings with no gradients to band.

**It skips anything already converted**, which is what makes a re-run a no-op.
Median cut is not idempotent: quantising an already-quantised image picks a
slightly different palette, and a second --apply rewrote 37 of the 112 files
to the same total size but different bytes. That is PH09b-025's failure mode
in a new place - a rebuild producing a spurious diff - so the skip is the fix,
not a shortcut.

QUALITY

64 colours against sources carrying 256-4,900 distinct colours, nearly all of
which are edge antialiasing. Mean error is 0.02-0.12 of 255 and the worst
window of the worst file is indistinguishable at 2x magnification. Every image
is checked for pure white in the output palette and the run aborts if one is
missing.
"""

from __future__ import annotations

import argparse
import pathlib
import sys

try:
    from PIL import Image, ImageChops, ImageStat
except ModuleNotFoundError:
    sys.exit("Pillow is required: python3 -m pip install Pillow")

REPO = pathlib.Path(__file__).resolve().parent.parent
DIAGRAMS = REPO / "images" / "diagrams"

COLOURS = 64
MIB = 1024 * 1024

# A run that breaches either of these is reporting a real change to what a
# reader sees, and stops rather than writing.
MAX_MEAN_ERROR = 0.20
MAX_PIXEL_ERROR = 80


def already_converted(path: pathlib.Path) -> bool:
    """True if this file is already a palette PNG of at most COLOURS entries.

    Median cut is not idempotent, so re-quantising a converted file rewrites
    it to different bytes for no gain. Nothing else in images/diagrams/ is
    mode P: all 112 sources were RGBA.
    """
    with Image.open(path) as im:
        return im.mode == "P" and len(im.getcolors() or [None] * 999) <= COLOURS


def reencode(path: pathlib.Path):
    """Return (palette image, mean error, max error, keeps_pure_white)."""
    original = Image.open(path).convert("RGB")
    palette = original.quantize(colors=COLOURS, method=Image.Quantize.MEDIANCUT)

    delta = ImageChops.difference(original, palette.convert("RGB"))
    stat = ImageStat.Stat(delta)
    mean = sum(stat.mean) / 3
    worst = max(stat.extrema[i][1] for i in range(3))

    raw = palette.getpalette()
    used = len(palette.getcolors())
    entries = [tuple(raw[i:i + 3]) for i in range(0, used * 3, 3)]
    return palette, mean, worst, (255, 255, 255) in entries


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true",
                    help="write the files; without it nothing is touched")
    args = ap.parse_args()

    pngs = sorted(DIAGRAMS.glob("*.png"))
    if not pngs:
        sys.exit(f"no PNGs under {DIAGRAMS}")

    before = after = 0
    problems = []
    results = []
    skipped = []

    for path in pngs:
        original_size = path.stat().st_size
        if already_converted(path):
            skipped.append(path)
            continue
        palette, mean, worst, white = reencode(path)

        # Sizing the result means encoding it, so encode once and keep the
        # bytes - re-encoding on the write pass could produce a different file
        # from the one that was measured.
        import io
        buf = io.BytesIO()
        palette.save(buf, "PNG", optimize=True)
        data = buf.getvalue()

        before += original_size
        after += len(data)
        results.append((path, original_size, data, mean, worst))

        if not white:
            problems.append(f"{path.name}: pure white is not in the palette")
        if mean > MAX_MEAN_ERROR:
            problems.append(f"{path.name}: mean error {mean:.3f} over "
                            f"{MAX_MEAN_ERROR}")
        if worst > MAX_PIXEL_ERROR:
            problems.append(f"{path.name}: worst pixel {worst} over "
                            f"{MAX_PIXEL_ERROR}")

    if skipped:
        print(f"{len(skipped)} already converted, skipped")
    if not results:
        print("nothing to convert.")
        return 0

    width = max(len(p.name) for p in pngs)
    for path, original_size, data, mean, worst in sorted(
            results, key=lambda r: r[1] - len(r[2]), reverse=True)[:10]:
        print(f"  {path.name:{width}} {original_size / 1024:7.0f} KB -> "
              f"{len(data) / 1024:6.0f} KB   mean {mean:.3f}  max {worst}")
    if len(results) > 10:
        print(f"  ... {len(results) - 10} more")

    print(f"\n{len(results)} PNGs   {before / MIB:.2f} MiB -> "
          f"{after / MIB:.2f} MiB   ({100 * (1 - after / before):.1f}% smaller)")

    if problems:
        print("\nPROBLEMS — nothing written:")
        for p in problems:
            print(f"  {p}")
        return 1

    if not args.apply:
        print("\ndry run: nothing written. Re-run with --apply.")
        return 0

    for path, _, data, _, _ in results:
        path.write_bytes(data)
    print(f"\nwrote {len(results)} files in place")
    return 0


if __name__ == "__main__":
    sys.exit(main())

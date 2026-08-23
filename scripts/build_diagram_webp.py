#!/usr/bin/env python3
"""Write a lossless WebP twin beside every notes diagram PNG.

A conversion, not a build step and not part of the verification suite. Like
`reencode_diagrams.py` it needs Pillow, which keeps it out of CI; everything
CI runs is stdlib-only. The `.webp` files it writes are committed artefacts,
in the way `webfonts/fa-solid-900.woff2` is - generated here, checked by
`scripts/verify_image_dimensions.py` (stdlib, in CI), served as-is.

    python3 scripts/build_diagram_webp.py            # dry run, writes nothing
    python3 scripts/build_diagram_webp.py --apply

WHY (performance pass, 2026-08-23)

A sample of 10 of the 106 diagram PNGs re-encoded as LOSSLESS WebP came out
29.8% smaller (616 KB -> 432 KB), above the 25% bar set for rolling it out.
Lossless, so the pixels are identical to the PNG - these are 64-colour line
drawings and lossy WebP would soften every edge. The PNGs stay published at
their existing URLs and remain the `<img src>`; the WebP is offered first
through a `<picture><source type="image/webp">` wrapper that
`build_notes_pages.py` puts around each diagram `<img>` at build time, and
that the two diagram galleries carry directly. A browser that cannot decode
WebP (none in current use) takes the PNG.

IDEMPOTENT: a PNG whose twin already exists and decodes to the same pixels
is skipped, so a re-run after the conversion is a no-op and a rebuild cannot
produce a spurious diff. A PNG that has CHANGED (different pixels from its
twin) is re-encoded. The four PNGs no page references get twins too: the
rule is "every PNG has one", which is what the verifier can check.
"""

from __future__ import annotations

import argparse
import io
import pathlib
import sys

try:
    from PIL import Image, ImageChops
except ModuleNotFoundError:
    sys.exit("Pillow is required: python3 -m pip install Pillow")

REPO = pathlib.Path(__file__).resolve().parent.parent
DIAGRAMS = REPO / "images" / "diagrams"


def encode(png: pathlib.Path) -> bytes:
    im = Image.open(png)
    buf = io.BytesIO()
    # method=6 is the slowest, smallest encoder setting; lossless so
    # quality only steers effort. RGBA/P both round-trip exactly.
    im.save(buf, "WEBP", lossless=True, quality=100, method=6)
    return buf.getvalue()


def same_pixels(png: pathlib.Path, webp: pathlib.Path) -> bool:
    a = Image.open(png).convert("RGBA")
    b = Image.open(webp).convert("RGBA")
    return a.size == b.size and ImageChops.difference(a, b).getbbox() is None


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--apply", action="store_true",
                    help="write the files (default: report and write nothing)")
    args = ap.parse_args()

    pngs = sorted(DIAGRAMS.glob("*.png"))
    if not pngs:
        sys.exit(f"no PNGs under {DIAGRAMS}")

    todo, current, png_bytes, webp_bytes = [], 0, 0, 0
    for png in pngs:
        webp = png.with_suffix(".webp")
        png_bytes += png.stat().st_size
        if webp.exists() and same_pixels(png, webp):
            current += 1
            webp_bytes += webp.stat().st_size
            continue
        todo.append(png)

    for png in todo:
        data = encode(png)
        webp = png.with_suffix(".webp")
        webp_bytes += len(data)
        saving = 100 * (png.stat().st_size - len(data)) / png.stat().st_size
        print(f"  {'wrote' if args.apply else 'WOULD WRITE'} {webp.relative_to(REPO)}"
              f"  {png.stat().st_size / 1024:6.1f} KB -> {len(data) / 1024:6.1f} KB"
              f"  ({saving:4.1f}% smaller)")
        if args.apply:
            webp.write_bytes(data)
            if not same_pixels(png, webp):
                sys.exit(f"{webp}: decoded pixels differ from the PNG - aborting")

    print(f"{len(pngs)} PNGs: {len(todo)} {'written' if args.apply else 'would be written'}, "
          f"{current} already current")
    if len(todo) + current == len(pngs):
        print(f"PNG total {png_bytes / 1024:.0f} KB, WebP total {webp_bytes / 1024:.0f} KB "
              f"({100 * (png_bytes - webp_bytes) / png_bytes:.1f}% smaller)")
    if not args.apply and todo:
        print("dry run - nothing written. Re-run with --apply.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

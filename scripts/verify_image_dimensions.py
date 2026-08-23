#!/usr/bin/env python3
"""Every <img> width/height matches the file's real intrinsic size.

    python3 scripts/verify_image_dimensions.py

Pure stdlib — it reads the headers itself rather than importing Pillow, so it
can live in the CI workflow, which has no non-stdlib dependencies.

WHY

Every image on the site is `max-width: 100%`, so the browser uses the declared
`width` and `height` only for the aspect ratio: it reserves a box of that
shape before the bytes arrive. Get the ratio wrong and the page moves when the
image lands, which is layout shift with no visible cause in the CSS.

`revision-notes/macroeconomics-diagrams.html` declared `1667x593` for a file
that is `3030x1454` — a box 35% too short — and it survived every check in the
repo, because nothing compared the two. Found by hand during Wave 4.1. This is
that comparison, so the next one fails a build instead.

It is also the guard on re-encoding: `scripts/reencode_diagrams.py` deliberately
does not resize, and if a future run ever does, this fails on all 293 tags at
once rather than shipping a site-wide shift.

WHAT IT CHECKS

  * every local <img> that declares both width and height must declare the
    file's true intrinsic size;
  * every local <img> must declare both, because one alone gives no ratio;
  * the src must resolve to a tracked file, case-sensitively — macOS will
    happily open `Foo.PNG` as `foo.png`, GitHub Pages will not.

SVG is measured from `width`/`height` when both are absolute, and otherwise
from `viewBox`, which is what a browser does.

SINCE THE PERFORMANCE PASS (2026-08-23) it also checks the `<picture>`
variants, which are new files a browser may pick instead of the `<img>`:

  * every local candidate in a `<source srcset>` is a tracked file;
  * a candidate with a `Nw` descriptor really is N pixels wide, and every
    candidate has the SAME aspect ratio (to 1%) as its sibling `<img>`'s
    declared box - the box is reserved from the <img>, whichever file lands;
  * every `images/diagrams/*.png` has a `.webp` twin of identical pixel size
    (scripts/build_diagram_webp.py writes them, lossless), so the
    `<picture>` wrapper build_notes_pages.py puts around each diagram never
    points at a 404 and never changes the box.
"""

from __future__ import annotations

import pathlib
import re
import struct
import subprocess
import sys
import xml.etree.ElementTree as ET

REPO = pathlib.Path(__file__).resolve().parent.parent

IMG_TAG = re.compile(r"<img\b[^>]*?>", re.S)
PICTURE = re.compile(r"<picture\b[^>]*>(.*?)</picture>", re.S)
SOURCE_TAG = re.compile(r"<source\b[^>]*?>", re.S)
ATTR = lambda tag, name: (  # noqa: E731
    m.group(1) if (m := re.search(rf'\s{name}="([^"]*)"', tag)) else None)
LENGTH = re.compile(r"^\s*([0-9.]+)\s*(px)?\s*$")


def png_size(data: bytes):
    if data[:8] != b"\x89PNG\r\n\x1a\n" or data[12:16] != b"IHDR":
        return None
    return struct.unpack(">II", data[16:24])


def gif_size(data: bytes):
    if data[:6] not in (b"GIF87a", b"GIF89a"):
        return None
    return struct.unpack("<HH", data[6:10])


def jpeg_size(data: bytes):
    if data[:2] != b"\xff\xd8":
        return None
    i = 2
    while i < len(data) - 9:
        if data[i] != 0xFF:
            i += 1
            continue
        marker = data[i + 1]
        # Standalone markers carry no length.
        if marker in (0xD8, 0xD9) or 0xD0 <= marker <= 0xD7:
            i += 2
            continue
        length = struct.unpack(">H", data[i + 2:i + 4])[0]
        # SOF0..SOF15, excluding the DHT/JPG/DAC markers interleaved with them.
        if 0xC0 <= marker <= 0xCF and marker not in (0xC4, 0xC8, 0xCC):
            height, width = struct.unpack(">HH", data[i + 5:i + 9])
            return width, height
        i += 2 + length
    return None


def webp_size(data: bytes):
    if data[:4] != b"RIFF" or data[8:12] != b"WEBP":
        return None
    chunk = data[12:16]
    if chunk == b"VP8X":
        w = int.from_bytes(data[24:27], "little") + 1
        h = int.from_bytes(data[27:30], "little") + 1
        return w, h
    if chunk == b"VP8L":
        bits = int.from_bytes(data[21:25], "little")
        return (bits & 0x3FFF) + 1, ((bits >> 14) & 0x3FFF) + 1
    if chunk == b"VP8 ":
        return struct.unpack("<HH", data[26:30])
    return None


def svg_size(data: bytes):
    try:
        root = ET.fromstring(data)
    except ET.ParseError:
        return None
    w, h = root.get("width"), root.get("height")
    if w and h and (mw := LENGTH.match(w)) and (mh := LENGTH.match(h)):
        return float(mw.group(1)), float(mh.group(1))
    box = root.get("viewBox")
    if box:
        parts = re.split(r"[\s,]+", box.strip())
        if len(parts) == 4:
            try:
                return float(parts[2]), float(parts[3])
            except ValueError:
                return None
    return None


READERS = {
    ".png": png_size, ".gif": gif_size, ".webp": webp_size,
    ".jpg": jpeg_size, ".jpeg": jpeg_size, ".svg": svg_size,
}


def intrinsic(path: pathlib.Path):
    reader = READERS.get(path.suffix.lower())
    if reader is None:
        return None
    return reader(path.read_bytes())


def main() -> int:
    listing = subprocess.run(["git", "ls-files"], cwd=REPO,
                             capture_output=True, text=True, check=True)
    tracked = set(listing.stdout.split())
    pages = [f for f in tracked if f.endswith(".html")]

    problems: list[str] = []
    checked = missing_attrs = 0
    cache: dict[str, object] = {}

    for page in sorted(pages):
        text = (REPO / page).read_text(encoding="utf-8", errors="ignore")
        for tag in IMG_TAG.findall(text):
            src = ATTR(tag, "src")
            if not src or src.startswith(("http://", "https://", "data:")):
                continue
            rel = src.split("?")[0].split("#")[0].lstrip("/")
            if rel not in tracked:
                problems.append(f"{page}: src=\"{src}\" is not a tracked file")
                continue

            width, height = ATTR(tag, "width"), ATTR(tag, "height")
            if not (width and height):
                missing_attrs += 1
                problems.append(
                    f"{page}: <img src=\"{src}\"> declares "
                    f"{'width only' if width else 'height only' if height else 'neither width nor height'}"
                    " — one alone gives the browser no aspect ratio")
                continue
            if not (width.isdigit() and height.isdigit()):
                problems.append(
                    f'{page}: <img src="{src}"> has non-integer '
                    f'width="{width}" height="{height}"')
                continue

            if rel not in cache:
                cache[rel] = intrinsic(REPO / rel)
            size = cache[rel]
            if size is None:
                problems.append(
                    f"{page}: cannot read the intrinsic size of {rel} "
                    "— unsupported or malformed image")
                continue

            checked += 1
            # SVG dimensions can be fractional; a declared integer within half
            # a pixel is the same box.
            if abs(size[0] - int(width)) > 0.5 or abs(size[1] - int(height)) > 0.5:
                declared = int(width) / int(height)
                real = size[0] / size[1]
                problems.append(
                    f'{page}: <img src="{src}"> declares '
                    f'{width}x{height} (ratio {declared:.4f}) but the file is '
                    f"{size[0]:g}x{size[1]:g} (ratio {real:.4f})"
                    + ("" if abs(declared - real) < 0.001 else
                       " — the reserved box is the wrong SHAPE, so the page "
                       "will move when the image loads"))

    # ---- <picture> variants -------------------------------------------
    candidates = 0
    for page in sorted(pages):
        text = (REPO / page).read_text(encoding="utf-8", errors="ignore")
        for pic in PICTURE.findall(text):
            imgs = IMG_TAG.findall(pic)
            if len(imgs) != 1:
                problems.append(f"{page}: a <picture> holds {len(imgs)} <img> tags, not 1")
                continue
            w, h = ATTR(imgs[0], "width"), ATTR(imgs[0], "height")
            if not (w and h and w.isdigit() and h.isdigit()):
                continue  # already reported above
            ratio = int(w) / int(h)
            for src_tag in SOURCE_TAG.findall(pic):
                srcset = ATTR(src_tag, "srcset") or ""
                for cand in srcset.split(","):
                    parts = cand.split()
                    if not parts:
                        continue
                    url, desc = parts[0], (parts[1] if len(parts) > 1 else None)
                    if url.startswith(("http://", "https://", "data:")):
                        continue
                    rel = url.split("?")[0].split("#")[0].lstrip("/")
                    if rel not in tracked:
                        problems.append(f"{page}: <source srcset> {url} is not a tracked file")
                        continue
                    if rel not in cache:
                        cache[rel] = intrinsic(REPO / rel)
                    size = cache[rel]
                    if size is None:
                        problems.append(f"{page}: cannot read the intrinsic size of {rel}")
                        continue
                    candidates += 1
                    if desc and desc.endswith("w") and desc[:-1].isdigit() \
                            and int(desc[:-1]) != size[0]:
                        problems.append(f"{page}: {url} is declared {desc} but is "
                                        f"{size[0]:g} px wide")
                    if abs(size[0] / size[1] - ratio) / ratio > 0.01:
                        problems.append(
                            f"{page}: {url} ({size[0]:g}x{size[1]:g}) does not have the "
                            f"shape of its <img> ({w}x{h}) - the reserved box is wrong "
                            "when this candidate is chosen")

    # ---- every diagram PNG has a same-size lossless WebP twin ------------
    twins = 0
    for rel in sorted(tracked):
        if not (rel.startswith("images/diagrams/") and rel.endswith(".png")):
            continue
        webp = rel[:-4] + ".webp"
        if webp not in tracked:
            problems.append(f"{rel}: no .webp twin - run "
                            "python3 scripts/build_diagram_webp.py --apply and commit it")
            continue
        a, b = intrinsic(REPO / rel), intrinsic(REPO / webp)
        if a != b:
            problems.append(f"{webp}: {b} but its PNG is {a} - re-run build_diagram_webp.py")
        twins += 1

    print(f"{checked} <img> tags checked against {len(cache)} image files; "
          f"{candidates} <picture> candidates; {twins} diagram PNG/WebP twins")
    if problems:
        print(f"\n{len(problems)} problem(s):")
        for p in problems:
            print(f"  {p}")
        return 1
    print("every declared width/height matches its file")
    return 0


if __name__ == "__main__":
    sys.exit(main())

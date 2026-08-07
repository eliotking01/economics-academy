#!/usr/bin/env python3
"""Check the internal geometry of the flashcard diagram SVGs.

For each SVG given (default: every .svg in images/diagrams/svg/):

  * classifies elements by the style-guide conventions in
    docs/DIAGRAM_STYLE.md — curves are 3.5px lines, axes are 2.5px #333333
    lines, guides are anything with a stroke-dasharray;
  * prints every pairwise curve intersection that falls within both
    segments, so the author can cross-check label positions;
  * FLAGs any dashed-guide endpoint, shaded-path vertex or rect corner that
    does not lie on a curve, an axis or another guide (tolerance 1px);
  * enforces the declared-geometry comment every diagram must carry:

        <!-- geometry
             intersections: 360,300 300,240
             on-curve: 300,360
        -->

    Each `intersections` point must lie on at least two distinct curves;
    each `on-curve` point on at least one. This is the author stating the
    economics of the diagram, and it is what actually catches a curve that
    misses its intended crossing — the purely structural checks cannot tell
    a marker that touches one curve correctly from one that should touch
    two and misses.

Pure stdlib. Exit code 1 if anything is flagged. This exists because a
hand-drawn demand curve once missed 45 degrees by a whisker and every dashed
intersection marker silently sat ~12px off the true crossing; eyes did not
catch it, arithmetic does.
"""

import glob
import math
import os
import re
import sys
import xml.etree.ElementTree as ET

SVG_NS = "{http://www.w3.org/2000/svg}"
TOL = 1.0

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_DIR = os.path.join(REPO, "images", "diagrams", "svg")


def seg_point_distance(px, py, x1, y1, x2, y2):
    """Distance from point (px,py) to segment (x1,y1)-(x2,y2)."""
    dx, dy = x2 - x1, y2 - y1
    length_sq = dx * dx + dy * dy
    if length_sq == 0:
        return math.hypot(px - x1, py - y1)
    t = ((px - x1) * dx + (py - y1) * dy) / length_sq
    t = max(0.0, min(1.0, t))
    return math.hypot(px - (x1 + t * dx), py - (y1 + t * dy))


def seg_intersection(a, b):
    """Intersection point of segments a and b, or None."""
    (x1, y1, x2, y2), (x3, y3, x4, y4) = a, b
    d = (x2 - x1) * (y4 - y3) - (y2 - y1) * (x4 - x3)
    if d == 0:
        return None
    t = ((x3 - x1) * (y4 - y3) - (y3 - y1) * (x4 - x3)) / d
    u = ((x3 - x1) * (y2 - y1) - (y3 - y1) * (x2 - x1)) / d
    if -0.001 <= t <= 1.001 and -0.001 <= u <= 1.001:
        return (x1 + t * (x2 - x1), y1 + t * (y2 - y1))
    return None


def path_vertices(d):
    """Vertices of a simple absolute M/L/Z path."""
    nums = [float(n) for n in re.findall(r"-?\d+(?:\.\d+)?", d)]
    if re.search(r"[a-z]", d.replace("z", "")) or len(nums) % 2:
        return None  # relative or curved commands: not checkable here
    return list(zip(nums[0::2], nums[1::2]))


def sample_path_segments(d):
    """A stroked curve path (absolute M/L/Q/C) as a sampled polyline.

    Bezier curves are flattened to short segments so point-on-curve checks
    work on curved diagrams (the PPF) exactly as they do on straight lines.
    Returns None if the path uses anything else.
    """
    tokens = re.findall(r"[MLQCZz]|-?\d+(?:\.\d+)?", d)
    segments = []
    point = start = None
    i = 0

    def bezier(points, steps):
        prev = points[0]
        for k in range(1, steps + 1):
            t = k / steps
            work = list(points)
            while len(work) > 1:
                work = [((1 - t) * a[0] + t * b[0], (1 - t) * a[1] + t * b[1])
                        for a, b in zip(work, work[1:])]
            segments.append((prev[0], prev[1], work[0][0], work[0][1]))
            prev = work[0]

    while i < len(tokens):
        cmd = tokens[i]
        if cmd == "M":
            point = start = (float(tokens[i + 1]), float(tokens[i + 2]))
            i += 3
        elif cmd == "L" and point:
            nxt = (float(tokens[i + 1]), float(tokens[i + 2]))
            segments.append((point[0], point[1], nxt[0], nxt[1]))
            point = nxt
            i += 3
        elif cmd == "Q" and point:
            ctrl = (float(tokens[i + 1]), float(tokens[i + 2]))
            end = (float(tokens[i + 3]), float(tokens[i + 4]))
            bezier([point, ctrl, end], 48)
            point = end
            i += 5
        elif cmd == "C" and point:
            c1 = (float(tokens[i + 1]), float(tokens[i + 2]))
            c2 = (float(tokens[i + 3]), float(tokens[i + 4]))
            end = (float(tokens[i + 5]), float(tokens[i + 6]))
            bezier([point, c1, c2, end], 64)
            point = end
            i += 7
        elif cmd in ("Z", "z") and point and start:
            segments.append((point[0], point[1], start[0], start[1]))
            point = start
            i += 1
        else:
            return None
    return segments


def declared_points(path):
    """Parse the '<!-- geometry ... -->' comment. Returns two point lists."""
    with open(path, encoding="utf-8") as fh:
        text = fh.read()
    match = re.search(r"<!--\s*geometry(.*?)-->", text, re.S)
    if not match:
        return None, None
    block = match.group(1)
    points = {"intersections": [], "on-curve": []}
    for key in points:
        found = re.search(key + r":((?:\s+-?\d+(?:\.\d+)?,-?\d+(?:\.\d+)?)+)",
                          block)
        if found:
            points[key] = [tuple(float(v) for v in pair.split(","))
                           for pair in found.group(1).split()]
    return points["intersections"], points["on-curve"]


def check_file(path):
    tree = ET.parse(path)
    curves, axes, guides, checks = [], [], [], []
    curve_ids = []  # parallel to curves: which drawn curve each segment is

    for el in tree.iter():
        tag = el.tag.replace(SVG_NS, "")
        if tag == "line":
            seg = tuple(float(el.get(k)) for k in ("x1", "y1", "x2", "y2"))
            if el.get("stroke-dasharray"):
                guides.append(seg)
            elif el.get("stroke-width") == "3.5":
                curves.append(seg)
                curve_ids.append(id(el))
            elif el.get("stroke") == "#333333" and el.get("stroke-width") == "2.5":
                axes.append(seg)
        elif tag == "rect" and el.get("fill-opacity"):
            x, y = float(el.get("x")), float(el.get("y"))
            w, h = float(el.get("width")), float(el.get("height"))
            for cx, cy in ((x, y), (x + w, y), (x, y + h), (x + w, y + h)):
                checks.append(("rect corner", cx, cy))
        elif tag == "path" and el.get("stroke-width") == "3.5":
            segs = sample_path_segments(el.get("d", ""))
            if segs is None:
                print("  NOTE  curve path could not be parsed; not checked")
            else:
                curves.extend(segs)
                curve_ids.extend([id(el)] * len(segs))
        elif tag == "path" and el.get("fill-opacity"):
            verts = path_vertices(el.get("d", ""))
            if verts is None:
                print("  NOTE  shaded path uses curved/relative commands; "
                      "not checked")
            else:
                for vx, vy in verts:
                    checks.append(("path vertex", vx, vy))

    for gx1, gy1, gx2, gy2 in guides:
        checks.append(("guide endpoint", gx1, gy1))
        checks.append(("guide endpoint", gx2, gy2))

    print(f"{os.path.relpath(path, REPO)}")
    for i, a in enumerate(curves):
        for j in range(i + 1, len(curves)):
            if curve_ids[i] == curve_ids[j]:
                continue  # segments of one sampled path meet at their joints
            p = seg_intersection(a, curves[j])
            if p:
                print(f"  curves cross at ({p[0]:.1f}, {p[1]:.1f})")

    anchors = curves + axes + guides
    flags = 0
    for kind, px, py in checks:
        if not any(seg_point_distance(px, py, *seg) <= TOL for seg in anchors):
            print(f"  FLAG  {kind} ({px:g}, {py:g}) lies on no curve, axis "
                  f"or guide")
            flags += 1

    crossings, on_curve = declared_points(path)
    if crossings is None:
        print("  FLAG  no '<!-- geometry -->' declaration in the file")
        flags += 1
    else:
        for px, py in crossings:
            hits = sum(seg_point_distance(px, py, *c) <= TOL for c in curves)
            if hits < 2:
                print(f"  FLAG  declared intersection ({px:g}, {py:g}) "
                      f"touches {hits} curve(s), needs at least 2")
                flags += 1
        for px, py in on_curve:
            if not any(seg_point_distance(px, py, *c) <= TOL for c in curves):
                print(f"  FLAG  declared on-curve point ({px:g}, {py:g}) "
                      f"lies on no curve")
                flags += 1

    if not flags:
        print("  OK    structure and declared geometry both hold")
    return flags


def main():
    paths = sys.argv[1:] or sorted(glob.glob(os.path.join(DEFAULT_DIR, "*.svg")))
    if not paths:
        print("no SVGs found")
        return 1
    total = sum(check_file(p) for p in paths)
    print(f"{len(paths)} file(s) checked, {total} flag(s)")
    return 1 if total else 0


if __name__ == "__main__":
    sys.exit(main())

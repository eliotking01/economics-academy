#!/usr/bin/env python3
"""Build a before/after page for every SVG changed since a given ref.

WHY

Wave 5.1 turned up 21 diagrams needing repair, and DIAGRAM_STYLE.md's self-QA
loop ends "only then present for approval, in batches". Screenshots in a chat
transcript are not reviewable - they are one fixed size and Eliot cannot zoom
them. This writes a page instead, so he sees the real SVGs at whatever size he
wants, in a browser, exactly as a student would.

The BEFORE copy is inlined from git (`git show <ref>:<path>`) rather than
written to disk, so reviewing costs no extra files in the repo. The AFTER is a
plain `<img>` at the live path, so re-rendering after a further edit is a page
refresh rather than a rebuild.

USAGE

    python3 _working/diagram-review/batch.py [ref]        # default HEAD

Open through Live Server, not file://: the image paths are root-absolute, like
the site's own.
"""

from __future__ import annotations

import html
import pathlib
import re
import subprocess
import sys

REPO = pathlib.Path(__file__).resolve().parents[2]
OUT = REPO / "_working" / "diagram-review" / "batch.html"
SVG_DIR = "images/diagrams/svg"

# Eliot's verdicts, 2026-08-14, verbatim. Keyed by stem so each row can state
# what it is meant to have fixed - a before/after with no claim attached is
# just two pictures.
NOTES = {
    "overconsumption": "Welfare loss should point to the shaded region, not the corner of the triangle.",
    "overproduction": "Welfare loss should point to the shaded region, not the corner of the triangle.",
    "underconsumption": "Welfare loss should point to the shaded region, not the corner of the triangle.",
    "underproduction": "Welfare loss should point to the shaded region, not the corner of the triangle.",
    "efficiency-perfect-competition": '"Productive" should read "Productive efficiency" and "Allocative" should read "Allocative efficiency"',
    "efficiency-imperfect-competition": '"Productive" and "Allocative" need the say "Productive efficiency" and "allocative efficiency" respectively. Also need a label to show dynamic efficiency as the shaded area.',
    "collusion": 'The MC curve should rise more on the left hand side to make it look more like a "hockey stick"',
    "economies-of-scale": "Text needs to be moved left slightly - currently overlapping the curve.",
    "kinked-demand-curve": "MC curve should be extended further on the right hand side",
    "nationalisation-privatisation": "All curves need to be shifted left - currently they are all on the far right of the diagram space, not centered.",
    "short-run-costs": "AFC should curve upwards more on the left tail, and the AC and AVC curves could be higher up as they arae squashed at the bottom.",
    "j-curve": 'Surplus and Deficit are the wrong side of the Y axis - should be on the left. "Depreciation occurs" should be above the left hand dotted line',
    "laffer-curve": "Curve should be a smooth, upside down U shape",
    "normal-profit-imperfect-competition": "The AC curve has two requirements: it needs its lowest point to be where it intersects MC, and it needs to be touching the point/tangential where P,C meet AR (which it currently does).",
    "perfect-competition-market-price": "The Revenue/Quantity Diagram needs its horizontal line extended to cover the width of the axis.",
    "trade-union-monopsony": "There should also be a red line extending from the intersection of W(TU) and S=AC up along the S=AC curve",
}


def changed_svgs(ref: str) -> list[str]:
    out = subprocess.run(
        ["git", "diff", "--name-only", ref, "--", SVG_DIR],
        cwd=REPO, capture_output=True, text=True, check=True,
    ).stdout.split()
    return sorted(p for p in out if p.endswith(".svg"))


def at_ref(ref: str, path: str) -> str | None:
    r = subprocess.run(["git", "show", f"{ref}:{path}"], cwd=REPO,
                       capture_output=True, text=True)
    return r.stdout if r.returncode == 0 else None


def inline(svg_text: str, uid: str) -> str:
    """Make an SVG safe to inline beside others: scope its ids and drop the XML
    declaration. Two SVGs on one page sharing `id="t"` would otherwise make
    every aria-labelledby ambiguous."""
    svg_text = re.sub(r"<\?xml[^>]*\?>", "", svg_text).strip()
    for attr in ('id="t"', 'id="d"'):
        svg_text = svg_text.replace(attr, attr[:-1] + f'-{uid}"')
    svg_text = svg_text.replace('aria-labelledby="t d"', f'aria-labelledby="t-{uid} d-{uid}"')
    return svg_text


CSS = """
:root{--ink:#1a202c;--mute:#5a6572;--line:#e2e8f0;--bg:#f7f8fa;--card:#fff;--accent:#d52349}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);
     font:16px/1.55 "Source Sans Pro",-apple-system,BlinkMacSystemFont,"Segoe UI",Helvetica,Arial,sans-serif}
header.sheet{position:sticky;top:0;z-index:20;background:var(--card);
     border-bottom:1px solid var(--line);padding:14px 22px;box-shadow:0 1px 6px rgba(0,0,0,.06)}
header.sheet h1{margin:0 0 4px;font-size:19px}
header.sheet p{margin:0;font-size:13.5px;color:var(--mute);max-width:80ch}
main{padding:22px;max-width:1500px;margin:0 auto}
.row{background:var(--card);border:1px solid var(--line);border-radius:10px;
     padding:16px 18px;margin-bottom:18px}
.rowhead{display:flex;align-items:baseline;gap:10px;flex-wrap:wrap}
.rowhead h2{margin:0;font-size:17px;font-family:ui-monospace,SFMono-Regular,Menlo,monospace}
.rowhead .n{font-size:12px;color:var(--mute)}
.ask{font-size:14px;margin:6px 0 12px;padding-left:11px;border-left:3px solid var(--accent)}
.ask b{color:var(--accent)}
.pair{display:grid;grid-template-columns:1fr 1fr;gap:16px}
.pane h3{margin:0 0 6px;font-size:12px;text-transform:uppercase;letter-spacing:.05em;color:var(--mute)}
.box{background:#fff;border:1px solid var(--line);border-radius:8px;padding:8px}
.box svg,.box img{width:100%;height:auto;display:block}
@media (max-width:900px){.pair{grid-template-columns:1fr}}
"""


def main() -> int:
    ref = sys.argv[1] if len(sys.argv) > 1 else "HEAD"
    paths = changed_svgs(ref)
    if not paths:
        print(f"no SVG changed since {ref} — nothing to review")
        return 0

    parts = []
    for i, path in enumerate(paths, 1):
        stem = pathlib.PurePosixPath(path).stem
        before = at_ref(ref, path)
        before_html = (
            f'<div class="box">{inline(before, "b%d" % i)}</div>'
            if before else
            '<div class="box"><em>New file — nothing at this ref.</em></div>'
        )
        ask = NOTES.get(stem, "")
        parts.append(f"""
<section class="row">
  <div class="rowhead"><span class="n">{i} / {len(paths)}</span><h2>{html.escape(stem)}</h2></div>
  {f'<p class="ask"><b>You asked:</b> {html.escape(ask)}</p>' if ask else ''}
  <div class="pair">
    <div class="pane"><h3>Before</h3>{before_html}</div>
    <div class="pane"><h3>After</h3>
      <div class="box"><img src="/{SVG_DIR}/{stem}.svg" alt=""></div></div>
  </div>
</section>""")

    OUT.write_text(f"""<!doctype html>
<html lang="en-GB">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex, nofollow">
<title>Diagram repairs — before and after</title>
<style>{CSS}</style>
</head>
<body>
<header class="sheet">
  <h1>Diagram repairs — before and after</h1>
  <p>{len(paths)} SVG{'s' if len(paths) != 1 else ''} changed since <code>{html.escape(ref)}</code>.
     Before is the committed version, inlined from git; after is the live file, so a refresh
     picks up any further edit. Both scale with the window — widen it to inspect closely.</p>
</header>
<main>{''.join(parts)}</main>
</body>
</html>
""", encoding="utf-8")

    print(f"{len(paths)} diagram(s) written to {OUT.relative_to(REPO)}")
    for p in paths:
        print("   ", p)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

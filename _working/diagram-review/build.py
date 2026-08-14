#!/usr/bin/env python3
"""Build the Wave 5.1 SVG/PNG review sheet.

WHY

Wave 5.1 asks whether each hand-drawn SVG in `images/diagrams/svg/` teaches the
same economics as the PNG it would replace in the notes. That question cannot be
answered mechanically: PH08-047 found `perfect-competition-short-run-supernormal
-profit` is a two-panel figure as a PNG and a one-panel drawing as an SVG, and
aspect ratio does not predict which pairs are like that (a 2.446 pair is
faithful, a 2.766 pair is not). CLAUDE.md standing rule 4 says every diagram is
visually inspected, never trusted by filename.

So this writes a page that puts the two images side by side with every caption
the diagram carries on the live site, and lets Eliot record a verdict per pair.
It is a review tool, not a build step: nothing it writes is published, and it
reads the site rather than changing it.

OUTPUT

`_working/diagram-review/index.html`. `_working/` is `_`-prefixed, so Jekyll
excludes it by its own rule - see DO-NOT-BREAK. Open it through Live Server
(not file://) because the image paths are root-absolute, like the site's.

WHAT A ROW SHOWS

  * the SVG and the PNG at matched height, so panel structure is comparable;
  * every DISTINCT `<figcaption>` the diagram carries, with the pages that use
    it - 70 of the 74 twinned diagrams that appear in a `<figure>` are captioned
    more than one way, because the Edexcel and AQA twins word them differently;
  * every distinct `alt`, which is what a screen reader gets;
  * the PNG's true pixel size and aspect, against the SVG's 800x600 viewBox.

PAIRING

Two kinds. 78 pairs share a filename stem. 5 more do not, and they are the ones
PROGRESS.md's HANDOVER calls "SVGs with no ground-truth PNG": each is one panel
of a wider PNG under a different name, recorded in docs/FLASHCARDS_PROGRESS.md.
They are declared in CROSS_NAME below rather than guessed at run time.
"""

from __future__ import annotations

import html
import json
import pathlib
import re
import struct
import sys

REPO = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "docs" / "audit" / "scripts"))
import lib  # noqa: E402

OUT = REPO / "_working" / "diagram-review" / "index.html"

# SVGs whose ground truth is one panel of a differently-named PNG. Each is
# sourced to the entry in docs/FLASHCARDS_PROGRESS.md that records the split.
CROSS_NAME = {
    "exchange-rate-appreciation": (
        "exchange-rates",
        "Left/right panel of the two-panel exchange-rates.png. Split ratified by "
        "Eliot 2026-08-06 (FLASHCARDS_PROGRESS): follows the figure's P1/P2 "
        "labels, not the caption's E1/E2/E3 - CONTENT_ISSUES #28.",
    ),
    "exchange-rate-depreciation": (
        "exchange-rates",
        "The other panel of the same two-panel PNG. Same ratification.",
    ),
    "lras-shift-keynesian": (
        "lras-shift",
        "Keynesian panel of the two-panel lras-shift.png. Eliot chose to ship "
        "both variants, 2026-08-05. NOTE: the log records lras-shift.svg as "
        "drawing only the CLASSICAL panel with the decision 'pending Eliot', "
        "and no entry closes it.",
    ),
    "indirect-tax-elastic-demand": (
        "Indirect-tax-incidence-elastic-inelastic",
        "Elastic panel of the two-panel PNG. Inferred from the SVG <title> and "
        "the PNG's 2.191 aspect - NOT found in FLASHCARDS_PROGRESS, so the "
        "pairing itself needs your eye as well as the content.",
    ),
    "indirect-tax-inelastic-demand": (
        "Indirect-tax-incidence-elastic-inelastic",
        "Inelastic panel of the same PNG. Same caveat.",
    ),
}

# Diagrams where the PNG is NOT ground truth, because a content error was found
# in it and you approved the SVG as the replacement. Recorded in
# docs/CONTENT_ISSUES.md; both SVGs are already live in the notes.
KNOWN_PNG_WRONG = {
    "game-theory": "CONTENT_ISSUES #9, approved 2026-08-05. The PNG's Low/High "
    "price headers are swapped, which inverts the dominant strategy. The SVG is "
    "authoritative and is ALREADY LIVE on 3-4-4-oligopoly and the micro gallery. "
    "Nothing to decide - check only that the SVG is right.",
    "comparative-advantage": "CONTENT_ISSUES #23/#25, approved 2026-08-06. The "
    "PNG carries the superseded numbers with the impossible specialisation "
    "total. The SVG is authoritative and is ALREADY LIVE on 4-1-2, 2-6-2 and the "
    "macro gallery. Nothing to decide - check only that the SVG is right.",
}


def png_size(path: pathlib.Path) -> tuple[int, int]:
    data = path.open("rb").read(33)
    if data[:8] != b"\x89PNG\r\n\x1a\n" or data[12:16] != b"IHDR":
        raise SystemExit(f"not a PNG: {path}")
    return struct.unpack(">II", data[16:24])


def svg_viewbox(path: pathlib.Path) -> tuple[float, float]:
    head = path.read_text(encoding="utf-8")[:2000]
    m = re.search(r'viewBox="([\d.\s-]+)"', head)
    if not m:
        raise SystemExit(f"no viewBox: {path}")
    parts = [float(x) for x in m.group(1).split()]
    return parts[2], parts[3]


def svg_title(path: pathlib.Path) -> str:
    m = re.search(r"<title[^>]*>(.*?)</title>", path.read_text(encoding="utf-8"), re.S)
    return " ".join(m.group(1).split()) if m else ""


FIGURE = re.compile(r"<figure\b.*?</figure>", re.S | re.I)
SRC = re.compile(r'src="(/images/diagrams/[^"]+)"')
ALT = re.compile(r'alt="([^"]*)"')
CAPTION = re.compile(r"<figcaption[^>]*>(.*?)</figcaption>", re.S | re.I)


def strip_tags(fragment: str) -> str:
    return " ".join(re.sub(r"<[^>]+>", " ", fragment).split())


def collect_usage() -> dict[str, dict]:
    """Walk the published surface for every <figure> showing a diagram.

    Keyed on the filename stem, so a page that has already been swapped to the
    SVG lands under the same key as the pages still showing the PNG - which is
    how game-theory and comparative-advantage keep their captions.
    """
    usage: dict[str, dict] = {}
    for page in lib.published_html():
        text = pathlib.Path(REPO / page).read_text(encoding="utf-8")
        for figure in FIGURE.findall(text):
            src = SRC.search(figure)
            if not src:
                continue
            stem = pathlib.PurePosixPath(src.group(1)).stem
            record = usage.setdefault(stem, {"captions": {}, "alts": {}, "pages": []})
            record["pages"].append(str(page))
            caption = CAPTION.search(figure)
            if caption:
                record["captions"].setdefault(strip_tags(caption.group(1)), []).append(
                    str(page)
                )
            alt = ALT.search(figure)
            if alt:
                record["alts"].setdefault(strip_tags(alt.group(1)), []).append(str(page))
    return usage


def build_rows() -> list[dict]:
    svg_dir = REPO / "images" / "diagrams" / "svg"
    png_dir = REPO / "images" / "diagrams"
    svgs = {p.stem: p for p in svg_dir.glob("*.svg")}
    pngs = {p.stem: p for p in png_dir.glob("*.png")}
    usage = collect_usage()

    rows = []
    for stem, svg_path in svgs.items():
        if stem in pngs:
            png_stem, note = stem, ""
        elif stem in CROSS_NAME:
            png_stem, note = CROSS_NAME[stem]
        else:
            raise SystemExit(f"SVG with no ground truth and no CROSS_NAME entry: {stem}")

        png_path = pngs[png_stem]
        pw, ph = png_size(png_path)
        vw, vh = svg_viewbox(svg_path)
        seen = usage.get(png_stem, {"captions": {}, "alts": {}, "pages": []})

        rows.append(
            {
                "stem": stem,
                "svg": f"/images/diagrams/svg/{stem}.svg",
                "png": f"/images/diagrams/{png_stem}.png",
                "png_stem": png_stem,
                "cross": stem in CROSS_NAME,
                "note": note,
                "png_wrong": KNOWN_PNG_WRONG.get(png_stem, ""),
                "title": svg_title(svg_path),
                "png_dims": f"{pw}x{ph}",
                "png_w": pw,
                "png_h": ph,
                "svg_w": int(vw),
                "svg_h": int(vh),
                "png_ar": round(pw / ph, 3),
                "svg_ar": round(vw / vh, 3),
                "wide": pw / ph >= 1.9,
                "captions": [
                    {"text": t, "pages": sorted(set(p))}
                    for t, p in sorted(seen["captions"].items())
                ],
                "alts": [
                    {"text": t, "pages": sorted(set(p))}
                    for t, p in sorted(seen["alts"].items())
                ],
                "tags": len(seen["pages"]),
                "pages": sorted(set(seen["pages"])),
            }
        )

    # Risky first: the wide PNGs and the cross-name splits are where every known
    # panel-drop lives, so they front-load the answer. Then alphabetical.
    rows.sort(key=lambda r: (not (r["wide"] or r["cross"]), r["stem"]))
    return rows


CSS = """
:root{--ink:#1a202c;--mute:#5a6572;--line:#e2e8f0;--bg:#f7f8fa;--card:#fff;
      --accent:#d52349;--ok:#0f7b6c;--warn:#b45309}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);
     font:16px/1.55 "Source Sans Pro",-apple-system,BlinkMacSystemFont,"Segoe UI",Helvetica,Arial,sans-serif}
header.sheet{position:sticky;top:0;z-index:20;background:var(--card);
     border-bottom:1px solid var(--line);padding:14px 22px;
     box-shadow:0 1px 6px rgba(0,0,0,.06)}
header.sheet h1{margin:0 0 4px;font-size:19px;letter-spacing:-.01em}
header.sheet p{margin:0;font-size:13.5px;color:var(--mute)}
.bar{display:flex;gap:10px;align-items:center;flex-wrap:wrap;margin-top:10px}
.bar button{font:inherit;font-size:13px;padding:6px 12px;border:1px solid var(--line);
     background:#fff;border-radius:6px;cursor:pointer}
.bar button:hover{border-color:var(--mute)}
#tally{font-size:13px;color:var(--mute);margin-left:auto;font-variant-numeric:tabular-nums}
main{padding:22px;max-width:1500px;margin:0 auto}
.row{background:var(--card);border:1px solid var(--line);border-radius:10px;
     padding:16px 18px;margin-bottom:18px;scroll-margin-top:130px}
.row.done-yes{border-left:5px solid var(--ok)}
.row.done-no{border-left:5px solid var(--accent)}
.row.done-maybe{border-left:5px solid var(--warn)}
.rowhead{display:flex;align-items:baseline;gap:10px;flex-wrap:wrap;margin-bottom:4px}
.rowhead .n{font-size:12px;color:var(--mute);font-variant-numeric:tabular-nums}
.rowhead h2{margin:0;font-size:17px;font-family:ui-monospace,SFMono-Regular,Menlo,monospace}
.chip{font-size:11px;padding:2px 8px;border-radius:99px;border:1px solid var(--line);color:var(--mute)}
.chip.wide{background:#fff7ed;border-color:#fdba74;color:#9a3412}
.chip.cross{background:#eef2ff;border-color:#a5b4fc;color:#3730a3}
.chip.settled{background:#ecfdf5;border-color:#6ee7b7;color:#065f46}
.title{font-size:14px;color:var(--mute);margin:0 0 10px}
.note{font-size:13.5px;background:#fffbeb;border:1px solid #fde68a;border-radius:7px;
      padding:9px 12px;margin:0 0 12px}
.note.settled{background:#ecfdf5;border-color:#a7f3d0}
.pair{display:grid;grid-template-columns:1fr 1fr;gap:16px;align-items:start}
.pane{min-width:0}
.pane h3{margin:0 0 6px;font-size:12px;text-transform:uppercase;letter-spacing:.05em;color:var(--mute)}
.pane .meta{font-size:12px;color:var(--mute);margin:0 0 8px;font-variant-numeric:tabular-nums}
.imgwrap{background:#fff;border:1px solid var(--line);border-radius:8px;padding:8px;
     display:flex;align-items:center;justify-content:center;min-height:120px;cursor:zoom-in}
.imgwrap img{max-width:100%;max-height:360px;height:auto;display:block}
body.big .imgwrap img{max-height:none;width:100%}
.caps{margin-top:14px;border-top:1px dashed var(--line);padding-top:11px}
.caps h3{margin:0 0 7px;font-size:12px;text-transform:uppercase;letter-spacing:.05em;color:var(--mute)}
.cap{font-size:14px;margin:0 0 9px;padding-left:11px;border-left:3px solid var(--line)}
.cap .where{display:block;font-size:11.5px;color:var(--mute);margin-top:2px;
     font-family:ui-monospace,SFMono-Regular,Menlo,monospace}
.alts{margin-top:6px}
.alts summary{font-size:12px;color:var(--mute);cursor:pointer}
.alts .cap{font-size:13px;color:var(--mute)}
.verdict{margin-top:13px;border-top:1px dashed var(--line);padding-top:11px;
     display:flex;gap:8px;align-items:center;flex-wrap:wrap}
.verdict label{font-size:14px;display:inline-flex;align-items:center;gap:5px;
     padding:5px 11px;border:1px solid var(--line);border-radius:99px;cursor:pointer}
.verdict label:hover{border-color:var(--mute)}
.verdict input{margin:0}
.verdict textarea{flex:1 1 320px;min-width:220px;font:inherit;font-size:13.5px;
     padding:6px 9px;border:1px solid var(--line);border-radius:6px;resize:vertical}
dialog{border:none;border-radius:10px;padding:0;max-width:96vw;max-height:96vh;
     box-shadow:0 20px 60px rgba(0,0,0,.35)}
dialog::backdrop{background:rgba(0,0,0,.65)}
dialog img{display:block;max-width:96vw;max-height:92vh}
dialog .close{position:absolute;top:8px;right:12px;font-size:22px;background:#fff;
     border:1px solid var(--line);border-radius:6px;cursor:pointer;padding:2px 10px}
#exportbox{width:100%;height:230px;font:12.5px/1.4 ui-monospace,SFMono-Regular,Menlo,monospace;
     padding:10px;border:1px solid var(--line);border-radius:8px}
@media (max-width:900px){.pair{grid-template-columns:1fr}}
"""

JS = """
const KEY='wave51-diagram-review';
const state=JSON.parse(localStorage.getItem(KEY)||'{}');
function paint(stem){
  const el=document.querySelector('[data-stem="'+stem+'"]');
  if(!el)return;
  el.classList.remove('done-yes','done-no','done-maybe');
  const v=state[stem]&&state[stem].v;
  if(v==='faithful')el.classList.add('done-yes');
  else if(v==='differs')el.classList.add('done-no');
  else if(v==='unsure')el.classList.add('done-maybe');
}
function tally(){
  let y=0,n=0,m=0;
  for(const k in state){const v=state[k].v;if(v==='faithful')y++;else if(v==='differs')n++;else if(v==='unsure')m++;}
  document.getElementById('tally').textContent=
    y+' faithful \\u00b7 '+n+' differs \\u00b7 '+m+' unsure \\u00b7 '+(TOTAL-y-n-m)+' left of '+TOTAL;
}
function save(){localStorage.setItem(KEY,JSON.stringify(state));tally();}
document.addEventListener('change',e=>{
  const r=e.target.closest('[data-stem]');if(!r)return;
  const stem=r.dataset.stem;
  state[stem]=state[stem]||{};
  if(e.target.type==='radio')state[stem].v=e.target.value;
  paint(stem);save();
});
document.addEventListener('input',e=>{
  if(e.target.tagName!=='TEXTAREA')return;
  const r=e.target.closest('[data-stem]');if(!r)return;
  state[r.dataset.stem]=state[r.dataset.stem]||{};
  state[r.dataset.stem].note=e.target.value;save();
});
document.addEventListener('click',e=>{
  const w=e.target.closest('.imgwrap');
  if(w){const d=document.getElementById('zoom');
    d.querySelector('img').src=w.querySelector('img').getAttribute('src');d.showModal();}
});
function restore(){
  for(const stem in state){
    const r=document.querySelector('[data-stem="'+stem+'"]');if(!r)continue;
    const s=state[stem];
    if(s.v){const i=r.querySelector('input[value="'+s.v+'"]');if(i)i.checked=true;}
    if(s.note){const t=r.querySelector('textarea');if(t)t.value=s.note;}
    paint(stem);
  }
  tally();
}
function exportAll(){
  const lines=['# Wave 5.1 verdicts','',
    '# stem | verdict | note'];
  document.querySelectorAll('[data-stem]').forEach(r=>{
    const stem=r.dataset.stem,s=state[stem]||{};
    lines.push(stem+' | '+(s.v||'NOT REVIEWED')+' | '+((s.note||'').replace(/\\n/g,' ')));
  });
  const d=document.getElementById('exportdlg');
  d.querySelector('textarea').value=lines.join('\\n');
  d.showModal();d.querySelector('textarea').select();
}
function jumpNext(){
  const rows=[...document.querySelectorAll('[data-stem]')];
  const next=rows.find(r=>!(state[r.dataset.stem]&&state[r.dataset.stem].v));
  if(next)next.scrollIntoView({behavior:'smooth',block:'start'});
}
document.addEventListener('DOMContentLoaded',()=>{
  restore();
  document.getElementById('big').addEventListener('click',()=>document.body.classList.toggle('big'));
  document.getElementById('export').addEventListener('click',exportAll);
  document.getElementById('next').addEventListener('click',jumpNext);
  document.querySelectorAll('dialog .close').forEach(b=>
    b.addEventListener('click',()=>b.closest('dialog').close()));
});
"""


def render(rows: list[dict]) -> str:
    e = html.escape
    parts: list[str] = []
    for i, r in enumerate(rows, 1):
        chips = []
        if r["cross"]:
            chips.append('<span class="chip cross">panel split &mdash; different filename</span>')
        if r["wide"]:
            chips.append(f'<span class="chip wide">wide PNG {r["png_ar"]} &mdash; check panel count</span>')
        if r["png_wrong"]:
            chips.append('<span class="chip settled">already settled</span>')
        chips.append(f'<span class="chip">{r["tags"]} live tag{"s" if r["tags"] != 1 else ""}</span>')

        notes = ""
        if r["png_wrong"]:
            notes += f'<p class="note settled"><strong>PNG is known-incorrect.</strong> {e(r["png_wrong"])}</p>'
        if r["note"]:
            notes += f'<p class="note"><strong>Pairing:</strong> {e(r["note"])}</p>'
        if not r["captions"] and not r["png_wrong"]:
            notes += (
                '<p class="note"><strong>Replaces nothing in the notes.</strong> This '
                "PNG appears in no <code>&lt;figure&gt;</code> on any published page, so "
                "the swap question does not arise for it &mdash; it is kept only as the "
                "ground truth for a flashcard SVG (D38). Judge it as a flashcard "
                "diagram, not as a replacement.</p>"
            )

        caps = "".join(
            f'<p class="cap">{e(c["text"])}<span class="where">{e(", ".join(c["pages"]))}</span></p>'
            for c in r["captions"]
        ) or '<p class="cap"><em>No figure on any published page.</em></p>'

        alts = "".join(
            f'<p class="cap">{e(a["text"])}<span class="where">{e(", ".join(a["pages"]))}</span></p>'
            for a in r["alts"]
        ) or '<p class="cap"><em>none</em></p>'

        parts.append(f"""
<section class="row" data-stem="{e(r['stem'])}" id="row-{e(r['stem'])}">
  <div class="rowhead">
    <span class="n">{i} / {len(rows)}</span>
    <h2>{e(r['stem'])}</h2>
    {''.join(chips)}
  </div>
  <p class="title">{e(r['title'])}</p>
  {notes}
  <div class="pair">
    <div class="pane">
      <h3>SVG &mdash; the candidate</h3>
      <p class="meta">viewBox 800&times;600 &middot; aspect {r['svg_ar']}</p>
      <div class="imgwrap"><img src="{e(r['svg'])}" alt=""
           width="{r['svg_w']}" height="{r['svg_h']}"></div>
    </div>
    <div class="pane">
      <h3>PNG &mdash; ground truth ({e(r['png_stem'])})</h3>
      <p class="meta">{e(r['png_dims'])} &middot; aspect {r['png_ar']}</p>
      <div class="imgwrap"><img src="{e(r['png'])}" alt=""
           width="{r['png_w']}" height="{r['png_h']}"></div>
    </div>
  </div>
  <div class="caps">
    <h3>Captions the notes carry for this diagram</h3>
    {caps}
    <details class="alts"><summary>alt text ({len(r['alts'])} distinct)</summary>{alts}</details>
  </div>
  <div class="verdict">
    <label><input type="radio" name="v-{e(r['stem'])}" value="faithful"> Faithful</label>
    <label><input type="radio" name="v-{e(r['stem'])}" value="differs"> Differs</label>
    <label><input type="radio" name="v-{e(r['stem'])}" value="unsure"> Unsure</label>
    <textarea rows="1" placeholder="what differs, if anything"></textarea>
  </div>
</section>""")

    return f"""<!doctype html>
<html lang="en-GB">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex, nofollow">
<title>Wave 5.1 &mdash; SVG / PNG diagram review</title>
<style>{CSS}</style>
</head>
<body>
<header class="sheet">
  <h1>Wave 5.1 &mdash; do the SVGs teach the same economics as the PNGs?</h1>
  <p>The SVGs are 4:3 redraws, so none looks identical &mdash; that is by design and is not the question.
     The question is <strong>same panels, same curves, same labels, same shaded areas</strong>, and whether the
     captions underneath stay true. Risky pairs are first: wide PNGs and panel splits.</p>
  <div class="bar">
    <button id="next">Jump to next unreviewed</button>
    <button id="big">Toggle large images</button>
    <button id="export">Export verdicts</button>
    <span id="tally"></span>
  </div>
</header>
<main>
{''.join(parts)}
</main>
<dialog id="zoom"><button class="close">&times;</button><img src="" alt=""></dialog>
<dialog id="exportdlg"><button class="close">&times;</button>
  <div style="padding:34px 18px 18px">
    <p style="margin:0 0 8px;font-size:14px">Copy this and paste it back into the chat.</p>
    <textarea id="exportbox"></textarea>
  </div>
</dialog>
<script>const TOTAL={len(rows)};{JS}</script>
</body>
</html>
"""


def main() -> int:
    rows = build_rows()
    OUT.write_text(render(rows), encoding="utf-8")

    wide = sum(1 for r in rows if r["wide"])
    cross = sum(1 for r in rows if r["cross"])
    settled = sum(1 for r in rows if r["png_wrong"])
    caps = sum(len(r["captions"]) for r in rows)
    nofig = sum(1 for r in rows if not r["captions"])

    print(f"{len(rows)} rows written to {OUT.relative_to(REPO)}")
    print(f"  {cross} paired across filenames, {len(rows) - cross} by shared stem")
    print(f"  {wide} carry a PNG at aspect >= 1.9 (check the panel count)")
    print(f"  {settled} already settled - the PNG is the known-incorrect one")
    print(f"  {caps} distinct captions shown; {nofig} rows have no figure on any page")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

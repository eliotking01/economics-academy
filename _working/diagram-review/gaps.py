#!/usr/bin/env python3
"""Build the Wave 5.2 sheet: which of the 28 untwinned diagram PNGs still need drawing.

WHY

The roadmap says 5.2 is "28 missing diagrams". That number is the arithmetic
`106 PNGs - 78 same-name pairs`, not a measurement of what is missing: several
of the 28 are already drawn under a DIFFERENT filename, because a wide PNG was
split into one SVG per panel (`exchange-rates.png` is `exchange-rate-
appreciation.svg` + `-depreciation.svg`, ratified in D46). Others have a
same-prefix SVG that draws a DIFFERENT diagram entirely - `demand-curve-shift`
is not `demand-curve-movement`, one being a shift and the other a movement
along.

Telling those two cases apart is the whole question, and it cannot be done from
filenames. So this puts the PNG beside every SVG that might already cover it,
at matched size, with every caption the PNG carries on the live site, and lets
Eliot settle it per row. Same tool as Wave 5.1's `build.py`, aimed at the
complement of that set.

WHAT IT ALSO MEASURES, AND WHY IT MATTERS MORE THAN THE PAIRING

The cost of drawing one of these is set by its PANEL COUNT, not its file size,
and **aspect ratio does not predict panel count here**. Three of the narrowest
PNGs on the list are multi-panel grids:

    price-elasticity-demand-ranges   1.559 aspect   FIVE panels
    price-elasticity-supply-ranges   1.146 aspect   FOUR panels
    shifts-in-equilibrium            1.202 aspect   FOUR panels

Wave 5.1 established that a wide PNG (>= 1.9) predicts the panel-drop class,
which is true of the 83 pairs it looked at. It is NOT true of these 28. A size
quoted off the 17 wide files would have missed the three most expensive rows on
the list. The `panels` figure below is counted by eye, per file, and the sheet
shows the render so it can be checked rather than believed.

OUTPUT

`_working/diagram-review/gaps.html`. `_working/` is `_`-prefixed so Jekyll
excludes it - see DO-NOT-BREAK. Open it through Live Server, not file://,
because the image paths are root-absolute like the site's.

EVERY <img> CARRIES width AND height. `verify_image_dimensions.py` enumerates
through `git ls-files`, so a file under `_working/` is checked exactly like a
published page; the Wave 5.1 sheet turned the workflow's 7th step red by
omitting them on 166 tags. PNGs take their true pixel size, read from the IHDR
header here rather than trusted; SVGs take their viewBox, which is what that
checker reads for an SVG with no absolute width.

Writes one file and is idempotent: no timestamps, no dict-order dependence.
"""

from __future__ import annotations

import html
import pathlib
import re
import struct
import sys

REPO = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "docs" / "audit" / "scripts"))
import lib  # noqa: E402

OUT = REPO / "_working" / "diagram-review" / "gaps.html"

# ---------------------------------------------------------------------------
# The proposal. Every row is a CLAIM to be confirmed or overturned on the sheet.
#
#   covered   - the PNG's economics is already drawn, panel for panel, under
#               other filenames. Nothing to draw.
#   superset  - an existing SVG teaches this and more. A judgement call.
#   gap       - nothing drawn covers it. Needs drawing.
#
# `panels` is counted by eye from the render, per file. `seen` records whether
# I looked at that render myself while building this, or inferred the count
# from its twin - stated rather than hidden, because an inferred count is the
# kind of number this project has been caught on before.
# ---------------------------------------------------------------------------
ROWS = [
    # -- already drawn under other names ------------------------------------
    ("exchange-rates", "covered", 2, True,
     ["exchange-rate-appreciation", "exchange-rate-depreciation"],
     "Eliot named which panel each SVG takes in the 5.1 review: appreciation is "
     "the right-hand panel, depreciation the left. Both passed as faithful "
     "(PH08-047 rows 19 and 20)."),
    ("Indirect-tax-incidence-elastic-inelastic", "covered", 2, True,
     ["indirect-tax-elastic-demand", "indirect-tax-inelastic-demand"],
     "Both panels drawn, both passed as faithful in 5.1 (rows 22 and 25)."),
    ("trade-union", "covered", 2, True,
     ["trade-union-competitive", "trade-union-monopsony"],
     "Both panels drawn. The monopsony one was a 5.1 `differs` and has been "
     "repaired. Note the two single-panel PNGs are the ground truth DO-NOT-BREAK "
     "protects from deletion."),
    ("ad-shift-right-classical-keynesian", "covered", 2, True,
     ["keynesian-ad-shift-right", "classical-ad-shift-right"],
     "Checked panel by panel while building this sheet. Left panel is Keynesian, "
     "right is classical; both SVGs carry the same PL1/PL2, Y1/Y2/Yfe, AD1/AD2 "
     "and LRAS1 labels as the panel they draw."),
    ("long-run-growth-ad-lras", "covered", 2, True,
     ["classical-lras-shift-right", "keynesian-lras-shift-right"],
     "Checked panel by panel. Both draw LRAS1 to LRAS2 against a fixed AD, "
     "classical and Keynesian. The Keynesian SVG labels the outputs Y1/Y2 where "
     "the PNG says Yfe1/Yfe2 - a label difference, not a different diagram. "
     "This is also the PNG whose declared size Wave 4.1 found wrong."),
    ("sras-ad-shift-right", "covered", 1, True,
     ["ad-shift-right"],
     "Single-panel PNG and the SVG is the same diagram: SRAS fixed, AD1 to AD2, "
     "PL1 to PL2, Y1 to Y2. The filenames disagree and the economics does not."),

    # -- drawn, but not exactly this ----------------------------------------
    ("ppf-long-run-growth", "superset", 1, True,
     ["ppf-growth-decline"],
     "The SVG draws PPF1 outward to PPF2 AND inward to PPF3. It contains this "
     "diagram and adds the decline case. Your call whether the notes' figure, "
     "whose caption is only about the outward shift, is served by a drawing "
     "that also shows a contraction."),

    # -- genuine gaps, multi-panel grids ------------------------------------
    ("price-elasticity-demand-ranges", "gap", 5, True, [],
     "FIVE panels: perfectly inelastic, relatively inelastic, unitary, "
     "perfectly elastic, relatively elastic. On a 1.559 aspect - the width "
     "screen would have called this cheap. D46 measured three panels on the "
     "locked 800x600 canvas at 205px each and rejected it for "
     "price-discrimination; five is not drawable there at all."),
    ("price-elasticity-supply-ranges", "gap", 4, True, [],
     "FOUR panels in a 2x2 grid, on the NARROWEST aspect of all 28 (1.146). "
     "Same canvas problem as the row above."),
    ("shifts-in-equilibrium", "gap", 4, True, [],
     "FOUR panels in a 2x2 grid: demand rises, demand falls, supply rises, "
     "supply falls. 1.202 aspect. The caption calls it a practice template."),

    # -- genuine gaps, two-panel --------------------------------------------
    ("ad-lras-equilibrium", "gap", 2, True,
     ["lras-classical", "lras-keynesian"],
     "The two candidate SVGs draw the LRAS CURVE ALONE - no AD curve and no "
     "equilibrium. The PNG's whole point is where AD meets LRAS at PL1. Not "
     "covered; checked by eye."),
    ("perfect-competition-profit-to-longrun", "gap", 2, True,
     ["perfect-competition-short-run-supernormal-profit"],
     "The candidate draws the SHORT run - supernormal profit shaded. This PNG "
     "draws the ADJUSTMENT to long run: entry shifts market supply S1 to S2, "
     "price falls to P2, and the firm ends at P2,C2 with AC minimum on MC. "
     "Different economics. Checked by eye."),
    ("perfect-competition-loss-to-longrun", "gap", 2, True,
     ["perfect-competition-short-run-loss"],
     "Same relationship as the row above, the other way: exit shifts supply "
     "left, price rises to P2, losses are eliminated. Checked by eye."),
    ("consumer-producer-surplus-competitive-monopoly", "gap", 2, True,
     ["consumer-producer-surplus-equilibrium"],
     "Two panels comparing the surplus split under competition and under "
     "monopoly, with MR and Qm/Qc. The candidate is the plain equilibrium "
     "diagram with no monopoly panel. Checked by eye."),
    ("consumer-producer-surplus-price-discrimination-after", "gap", 2, True, [],
     "Two panels, one per sub-market, with the surplus transferred to the "
     "producer. Checked by eye. Related to the new "
     "`price-discrimination-combined-market.svg`, which D46 says is yours to "
     "place - flagged, not proposed."),
    ("surplus-demand-increase", "gap", 2, True, [],
     "Panels 3a and 3b: the same demand shift with consumer surplus shaded in "
     "one and producer surplus in the other. Lettered points A-G. Checked by eye."),
    ("surplus-supply-increase", "gap", 2, False, [],
     "Panels 2a and 2b, the supply-side twin of the row above. Panel count "
     "inferred from that twin and from the caption's '2a & 2b', not viewed."),
    ("joint-demand", "gap", 2, True, [],
     "Two panels, Cars and Petrol, with a titled header. One of five figures on "
     "a single AQA page. Checked by eye."),
    ("composite-demand", "gap", 2, True, [],
     "Two panels, Cheese and Butter. Checked by eye."),
    ("joint-supply", "gap", 2, False, [],
     "Panel count inferred from the four other figures on the same page, not "
     "viewed."),
    ("derived-demand", "gap", 2, False, [],
     "Panel count inferred from its four page-mates, not viewed."),
    ("competitive-demand", "gap", 2, False, [],
     "Panel count inferred from its four page-mates, not viewed."),

    # -- genuine gaps, single panel -----------------------------------------
    ("demand-curve-movement", "gap", 1, True,
     ["demand-curve-shift"],
     "The candidate draws a SHIFT, D1 to D2. This PNG draws a MOVEMENT ALONG a "
     "single curve, points A and B, extension and contraction. Different "
     "concept, and the one students most often confuse. Checked by eye."),
    ("supply-curve-movement", "gap", 1, False,
     ["supply-curve-shift"],
     "Same relationship as the row above, on the supply side. Inferred from "
     "that twin and from the caption's 'Extension in QS'."),
    ("demand-increase", "gap", 1, True,
     ["demand-curve-shift"],
     "The candidate has no supply curve and no equilibrium: it shows D1 to D2 "
     "at one price. This PNG shows the shift meeting S and moving equilibrium "
     "from P1,Q1 to P2,Q2. Checked by eye."),
    ("supply-increase", "gap", 1, False,
     ["supply-curve-shift"],
     "Supply-side twin of the row above. Inferred, not viewed."),
    ("consumer-producer-surplus-price-discrimination-before", "gap", 1, True, [],
     "One panel despite its 1.504 aspect - the drawing sits left with the "
     "MC=AC=S line running out to the right. Checked by eye."),
    ("net-welfare-loss-monopoly", "gap", 1, True, [],
     "One panel, one shaded triangle between Qm and Qc. The cheapest row on the "
     "list. Checked by eye."),
]


def png_size(path: pathlib.Path) -> tuple[int, int]:
    data = path.open("rb").read(33)
    if data[:8] != b"\x89PNG\r\n\x1a\n" or data[12:16] != b"IHDR":
        raise SystemExit(f"not a PNG: {path}")
    return struct.unpack(">II", data[16:24])


def svg_viewbox(path: pathlib.Path) -> tuple[int, int]:
    m = re.search(r'viewBox="([\d.\s-]+)"', path.read_text(encoding="utf-8")[:2000])
    if not m:
        raise SystemExit(f"no viewBox: {path}")
    parts = [float(x) for x in m.group(1).split()]
    return int(parts[2]), int(parts[3])


FIGURE = re.compile(r"<figure\b.*?</figure>", re.S | re.I)
SRC = re.compile(r'src="(/images/diagrams/[^"]+)"')
CAPTION = re.compile(r"<figcaption[^>]*>(.*?)</figcaption>", re.S | re.I)


def strip_tags(fragment: str) -> str:
    return " ".join(re.sub(r"<[^>]+>", " ", fragment).split())


def collect_usage() -> dict:
    usage: dict = {}
    for page in lib.published_html():
        text = (REPO / page).read_text(encoding="utf-8")
        for figure in FIGURE.findall(text):
            src = SRC.search(figure)
            if not src:
                continue
            stem = pathlib.PurePosixPath(src.group(1)).stem
            record = usage.setdefault(stem, {"captions": {}, "pages": []})
            record["pages"].append(str(page))
            caption = CAPTION.search(figure)
            if caption:
                record["captions"].setdefault(strip_tags(caption.group(1)), []).append(
                    str(page))
    return usage


def guard() -> None:
    """The 28 in ROWS must BE the 28 on disk. A drifted list is a wrong sheet."""
    pngs = {p.stem for p in (REPO / "images" / "diagrams").glob("*.png")}
    svgs = {p.stem for p in (REPO / "images" / "diagrams" / "svg").glob("*.svg")}
    untwinned = pngs - svgs
    listed = {r[0] for r in ROWS}
    if listed != untwinned:
        raise SystemExit(
            f"ROWS has drifted from disk.\n"
            f"  listed not on disk: {sorted(listed - untwinned)}\n"
            f"  on disk not listed: {sorted(untwinned - listed)}")
    for row in ROWS:
        for candidate in row[4]:
            if candidate not in svgs:
                raise SystemExit(f"{row[0]}: candidate SVG does not exist: {candidate}")


CSS = """
:root{--ink:#1a202c;--mute:#5a6572;--line:#e2e8f0;--bg:#f7f8fa;--card:#fff;
      --accent:#d52349;--ok:#0f7b6c;--warn:#b45309}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);
     font:16px/1.55 "Source Sans Pro",-apple-system,BlinkMacSystemFont,"Segoe UI",Helvetica,Arial,sans-serif}
header.sheet{position:sticky;top:0;z-index:20;background:var(--card);
     border-bottom:1px solid var(--line);padding:14px 22px;box-shadow:0 1px 6px rgba(0,0,0,.06)}
header.sheet h1{margin:0 0 4px;font-size:19px;letter-spacing:-.01em}
header.sheet p{margin:0;font-size:13.5px;color:var(--mute);max-width:110ch}
.bar{display:flex;gap:10px;align-items:center;flex-wrap:wrap;margin-top:10px}
.bar button{font:inherit;font-size:13px;padding:6px 12px;border:1px solid var(--line);
     background:#fff;border-radius:6px;cursor:pointer}
.bar button:hover{border-color:var(--mute)}
#tally{font-size:13px;color:var(--mute);margin-left:auto;font-variant-numeric:tabular-nums}
main{padding:22px;max-width:1500px;margin:0 auto}
h2.group{font-size:15px;text-transform:uppercase;letter-spacing:.06em;color:var(--mute);
     margin:30px 0 12px;padding-bottom:6px;border-bottom:1px solid var(--line)}
h2.group:first-child{margin-top:0}
.row{background:var(--card);border:1px solid var(--line);border-radius:10px;
     padding:16px 18px;margin-bottom:18px;scroll-margin-top:150px}
.row.done-draw{border-left:5px solid var(--accent)}
.row.done-skip{border-left:5px solid var(--ok)}
.row.done-later{border-left:5px solid var(--warn)}
.rowhead{display:flex;align-items:baseline;gap:10px;flex-wrap:wrap;margin-bottom:8px}
.rowhead .n{font-size:12px;color:var(--mute);font-variant-numeric:tabular-nums}
.rowhead h3{margin:0;font-size:17px;font-family:ui-monospace,SFMono-Regular,Menlo,monospace}
.chip{font-size:11px;padding:2px 8px;border-radius:99px;border:1px solid var(--line);color:var(--mute)}
.chip.panels{background:#fff7ed;border-color:#fdba74;color:#9a3412}
.chip.p1{background:#f0fdf4;border-color:#86efac;color:#166534}
.chip.covered{background:#ecfdf5;border-color:#6ee7b7;color:#065f46}
.chip.inferred{background:#fef2f2;border-color:#fca5a5;color:#991b1b}
.note{font-size:13.5px;background:#fffbeb;border:1px solid #fde68a;border-radius:7px;
      padding:9px 12px;margin:0 0 12px}
.note.covered{background:#ecfdf5;border-color:#a7f3d0}
.pair{display:grid;grid-template-columns:1fr 1fr;gap:16px;align-items:start}
.pane{min-width:0}
.pane h4{margin:0 0 6px;font-size:12px;text-transform:uppercase;letter-spacing:.05em;color:var(--mute)}
.pane .meta{font-size:12px;color:var(--mute);margin:0 0 8px;font-variant-numeric:tabular-nums}
.imgwrap{background:#fff;border:1px solid var(--line);border-radius:8px;padding:8px;
     display:flex;align-items:center;justify-content:center;min-height:120px;cursor:zoom-in}
.imgwrap img{max-width:100%;max-height:340px;height:auto;display:block}
body.big .imgwrap img{max-height:none;width:100%}
.stack{display:flex;flex-direction:column;gap:10px}
.caps{margin-top:14px;border-top:1px dashed var(--line);padding-top:11px}
.caps h4{margin:0 0 7px;font-size:12px;text-transform:uppercase;letter-spacing:.05em;color:var(--mute)}
.cap{font-size:14px;margin:0 0 9px;padding-left:11px;border-left:3px solid var(--line)}
.cap .where{display:block;font-size:11.5px;color:var(--mute);margin-top:2px;
     font-family:ui-monospace,SFMono-Regular,Menlo,monospace}
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
#exportbox{width:100%;height:260px;font:12.5px/1.4 ui-monospace,SFMono-Regular,Menlo,monospace;
     padding:10px;border:1px solid var(--line);border-radius:8px}
@media (max-width:900px){.pair{grid-template-columns:1fr}}
"""

JS = """
const KEY='wave52-diagram-gaps';
const state=JSON.parse(localStorage.getItem(KEY)||'{}');
function paint(stem){
  const el=document.querySelector('[data-stem="'+stem+'"]');
  if(!el)return;
  el.classList.remove('done-draw','done-skip','done-later');
  const v=state[stem]&&state[stem].v;
  if(v==='draw')el.classList.add('done-draw');
  else if(v==='skip')el.classList.add('done-skip');
  else if(v==='later')el.classList.add('done-later');
}
function tally(){
  let d=0,s=0,l=0;
  for(const k in state){const v=state[k].v;if(v==='draw')d++;else if(v==='skip')s++;else if(v==='later')l++;}
  document.getElementById('tally').textContent=
    d+' draw \\u00b7 '+s+' already covered \\u00b7 '+l+' later \\u00b7 '+(TOTAL-d-s-l)+' left of '+TOTAL;
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
  const lines=['# Wave 5.2 verdicts','','# stem | verdict | note'];
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

GROUPS = [
    ("covered", "Already drawn under other filenames &mdash; nothing to draw (proposal)"),
    ("superset", "Drawn, but the SVG teaches more than the PNG &mdash; your call"),
    ("gap", "Nothing drawn covers this &mdash; needs drawing (proposal)"),
]


def render() -> str:
    e = html.escape
    usage = collect_usage()
    index = {r[0]: i for i, r in enumerate(ROWS)}
    body: list[str] = []
    n = 0

    for kind, heading in GROUPS:
        rows = [r for r in ROWS if r[1] == kind]
        if not rows:
            continue
        rows.sort(key=lambda r: (-r[2], index[r[0]]))
        body.append(f'<h2 class="group">{heading} &mdash; {len(rows)}</h2>')

        for stem, _kind, panels, seen, candidates, note in rows:
            n += 1
            pw, ph = png_size(REPO / "images" / "diagrams" / f"{stem}.png")
            record = usage.get(stem, {"captions": {}, "pages": []})

            chips = [
                f'<span class="chip {"panels" if panels > 1 else "p1"}">'
                f'{panels} panel{"s" if panels != 1 else ""}</span>',
                f'<span class="chip">aspect {pw / ph:.3f}</span>',
                f'<span class="chip">{len(set(record["pages"]))} page'
                f'{"s" if len(set(record["pages"])) != 1 else ""}</span>',
            ]
            if kind == "covered":
                chips.insert(0, '<span class="chip covered">proposed: covered</span>')
            if not seen:
                chips.append('<span class="chip inferred">panel count INFERRED, '
                             'not viewed</span>')

            if candidates:
                svg_panes = "".join(
                    f'<div><p class="meta">{e(c)}.svg &mdash; viewBox '
                    f'{svg_viewbox(REPO / "images" / "diagrams" / "svg" / f"{c}.svg")[0]}'
                    f'&times;'
                    f'{svg_viewbox(REPO / "images" / "diagrams" / "svg" / f"{c}.svg")[1]}'
                    f'</p><div class="imgwrap">'
                    f'<img src="/images/diagrams/svg/{e(c)}.svg" width="800" '
                    f'height="600" alt="{e(c)} SVG" loading="lazy"></div></div>'
                    for c in candidates)
                right_head = ("Already drawn" if kind != "gap"
                              else "Nearest drawn SVG &mdash; is it the same diagram?")
            else:
                svg_panes = ('<div class="imgwrap"><p class="meta">'
                             'No SVG on the site is a candidate for this figure.'
                             '</p></div>')
                right_head = "Nearest drawn SVG"

            caps = "".join(
                f'<p class="cap">{e(text)}<span class="where">'
                f'{e(", ".join(sorted(set(pages))))}</span></p>'
                for text, pages in sorted(record["captions"].items())
            ) or '<p class="cap"><em>No figure caption on any published page.</em></p>'

            body.append(f"""
<section class="row" data-stem="{e(stem)}">
  <div class="rowhead">
    <span class="n">{n:02d} / {len(ROWS)}</span>
    <h3>{e(stem)}.png</h3>
    {"".join(chips)}
  </div>
  <p class="note{' covered' if kind != 'gap' else ''}">{note}</p>
  <div class="pair">
    <div class="pane">
      <h4>The PNG in the notes today</h4>
      <p class="meta">{pw}&times;{ph}</p>
      <div class="imgwrap"><img src="/images/diagrams/{e(stem)}.png"
        width="{pw}" height="{ph}" alt="{e(stem)}" loading="lazy"></div>
    </div>
    <div class="pane">
      <h4>{right_head}</h4>
      <div class="stack">{svg_panes}</div>
    </div>
  </div>
  <div class="caps">
    <h4>How the notes caption it</h4>
    {caps}
  </div>
  <div class="verdict">
    <label><input type="radio" name="v-{e(stem)}" value="draw"> Needs drawing</label>
    <label><input type="radio" name="v-{e(stem)}" value="skip"> Already covered</label>
    <label><input type="radio" name="v-{e(stem)}" value="later"> Not now</label>
    <textarea rows="1" placeholder="Note (optional)"></textarea>
  </div>
</section>""")

    counts = {k: sum(1 for r in ROWS if r[1] == k) for k, _ in GROUPS}
    return f"""<!doctype html>
<html lang="en-GB">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Wave 5.2 &mdash; which diagrams are actually missing</title>
<style>{CSS}</style>
</head>
<body>
<header class="sheet">
  <h1>Wave 5.2 &mdash; the {len(ROWS)} diagram PNGs with no same-named SVG</h1>
  <p>The roadmap calls these &ldquo;28 missing diagrams&rdquo;. My proposal is that
     <strong>{counts['covered']} are already drawn</strong> under different filenames,
     <strong>{counts['superset']} is drawn as part of something larger</strong>, and
     <strong>{counts['gap']} are real gaps</strong>. Every row is a claim to confirm or
     overturn. The cost driver is the <strong>panel count</strong>, not the file width:
     three of the narrowest files here are four- and five-panel grids.</p>
  <div class="bar">
    <button id="big" type="button">Toggle full size</button>
    <button id="next" type="button">Next undecided</button>
    <button id="export" type="button">Export verdicts</button>
    <span id="tally"></span>
  </div>
</header>
<main>
{"".join(body)}
</main>
<dialog id="zoom"><button class="close" type="button">&times;</button><img alt=""></dialog>
<dialog id="exportdlg"><button class="close" type="button">&times;</button>
  <textarea id="exportbox" readonly></textarea></dialog>
<script>const TOTAL={len(ROWS)};{JS}</script>
</body>
</html>
"""


def main() -> None:
    guard()
    OUT.write_text(render(), encoding="utf-8")
    print(f"wrote {OUT.relative_to(REPO)} — {len(ROWS)} rows")
    for kind, _ in GROUPS:
        rows = [r for r in ROWS if r[1] == kind]
        print(f"  {kind:9} {len(rows):2}  panels: "
              f"{sorted((r[2] for r in rows), reverse=True)}")
    inferred = [r[0] for r in ROWS if not r[3]]
    print(f"  panel count inferred rather than viewed: {len(inferred)} — "
          f"{', '.join(inferred)}")


if __name__ == "__main__":
    main()

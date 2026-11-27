"""Pre-render TeX with the vendored KaTeX, and read the TeX back out again.

Imported by the generators that write formulae (build_glossary.py since
2026-08-09, build_notes_pages.py since 2026-11-27) and by everything that
has to see through the rendered output to the TeX it came from
(extract_glossary.py, verify_glossary.py, verify_text_integrity.py).

render() shells out to `node` once per call with scripts/vendor/katex.min.js
(see scripts/vendor/README.md for why it is vendored). The options are the
glossary's, unchanged: `throwOnError: true` so a formula KaTeX cannot typeset
stops the build instead of shipping red error text, `strict: false`, and the
default `htmlAndMathml` output - the HTML half is aria-hidden, so the MathML
half is what a screen reader reads, and it carries the source TeX in an
`<annotation encoding="application/x-tex">`.

to_tex() is that annotation's use: it replaces every rendered formula in a
page with `\\(TeX\\)` (inline) or `\\[TeX\\]` (display), which is exactly the
form the notes are written in - the notes use no `$$` (2026-11-27: the only
`$$` on the site was inside MathJax's own config). A reader that worked on
the TeX before the notes were pre-rendered therefore sees the same thing
after, and verify_text_integrity can prove a conversion moved no wording.

Standard library only, plus node at build time.
"""

from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
KATEX_JS = ROOT / "scripts" / "vendor" / "katex.min.js"
KATEX_CSS = "/css/vendor/katex/katex.min.css"


class KatexError(RuntimeError):
    """node could not be run, or KaTeX could not typeset a formula."""


_SCRIPT = (
    'const katex=require(process.argv[1]);'
    'let s="";process.stdin.on("data",d=>s+=d).on("end",()=>{'
    'try{'
    'const out=JSON.parse(s).map(([t,d])=>katex.renderToString(t,'
    '{displayMode:d,throwOnError:true,strict:false}));'
    'process.stdout.write(JSON.stringify({ok:true,html:out}));'
    '}catch(err){'
    'process.stdout.write(JSON.stringify({ok:false,error:String(err.message||err)}));'
    '}});'
)


def render(items: list[tuple[str, bool]]) -> list[str]:
    """[(tex, display), ...] -> [html, ...], in one node process."""
    if not items:
        return []
    try:
        r = subprocess.run(
            ["node", "-e", _SCRIPT, str(KATEX_JS)],
            input=json.dumps([[t, bool(d)] for t, d in items]),
            capture_output=True, text=True, check=True, cwd=ROOT,
        )
    except (OSError, subprocess.CalledProcessError) as exc:
        raise KatexError(
            f"could not run node to pre-render formulae: {exc}. "
            f"node is needed at build time only; see scripts/vendor/README.md"
        ) from None
    out = json.loads(r.stdout)
    if not out["ok"]:
        raise KatexError(f"KaTeX could not render a formula: {out['error']}")
    return out["html"]


# The opening tag of a rendered formula: a display wrapper, or a bare inline
# .katex span. `class="katex"` exactly - the inner spans are katex-mathml,
# katex-html, and never match.
_OPEN = re.compile(r'<span class="katex-display">|<span class="katex">')
_SPAN_TAG = re.compile(r"<span\b|</span>")
_ANNOTATION = re.compile(
    r'<annotation encoding="application/x-tex">(.*?)</annotation>', re.S)


def to_tex(html: str) -> str:
    """Every rendered formula in `html` back to its delimited TeX source.

    The TeX is the annotation's text exactly as KaTeX escaped it, so an HTML
    parser reading the result decodes it to the same characters it decoded
    from the original source.
    """
    out = []
    pos = 0
    for m in _OPEN.finditer(html):
        if m.start() < pos:
            continue  # inside a formula already consumed
        depth = 0
        end = None
        for t in _SPAN_TAG.finditer(html, m.start()):
            depth += 1 if t.group() == "<span" else -1
            if depth == 0:
                end = t.end()
                break
        if end is None:
            raise ValueError(f"unclosed KaTeX span at offset {m.start()}")
        block = html[m.start():end]
        ann = _ANNOTATION.search(block)
        if not ann:
            raise ValueError(f"KaTeX span with no TeX annotation at offset {m.start()}")
        display = m.group() == '<span class="katex-display">'
        out.append(html[pos:m.start()])
        out.append(("\\[" if display else "\\(") + ann.group(1)
                   + ("\\]" if display else "\\)"))
        pos = end
    out.append(html[pos:])
    return "".join(out)

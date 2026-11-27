"""katex_render.to_tex(): rendered KaTeX back to the TeX it was written in."""

import shutil
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import katex_render as kr  # noqa: E402

# The shape KaTeX emits, trimmed: nested spans and the TeX annotation.
INLINE = ('<span class="katex"><span class="katex-mathml"><math><semantics>'
          '<mrow></mrow><annotation encoding="application/x-tex">a &lt; b</annotation>'
          '</semantics></math></span><span class="katex-html" aria-hidden="true">'
          '<span class="base"><span class="mord">a</span></span></span></span>')
DISPLAY = '<span class="katex-display">' + INLINE.replace("a &lt; b", "\\frac{1}{2}") + "</span>"


class ToTexTest(unittest.TestCase):
    def test_inline_and_display(self):
        html = f"<p>So {INLINE} and</p><div>{DISPLAY}</div>"
        self.assertEqual(kr.to_tex(html),
                         "<p>So \\(a &lt; b\\) and</p><div>\\[\\frac{1}{2}\\]</div>")

    def test_no_maths_is_unchanged(self):
        html = '<p class="katex-free">plain <span class="katexish">x</span></p>'
        self.assertEqual(kr.to_tex(html), html)

    def test_unclosed_span_fails_loudly(self):
        with self.assertRaises(ValueError):
            kr.to_tex('<span class="katex"><span>')

    @unittest.skipUnless(shutil.which("node"), "node renders; CI has it")
    def test_round_trip_through_render(self):
        items = [("PED = \\frac{\\%\\Delta Q_d}{\\%\\Delta P}", True),
                 ("1 - 0.4 = 0.6", False)]
        html = "|".join(kr.render(items))
        self.assertEqual(
            kr.to_tex(html),
            "\\[PED = \\frac{\\%\\Delta Q_d}{\\%\\Delta P}\\]|\\(1 - 0.4 = 0.6\\)")


if __name__ == "__main__":
    unittest.main()

"""verify_liquid.py - the Liquid-detection rules.

A stray `{%` in a published markdown file fails the WHOLE GitHub Pages deploy,
and the checker reimplements Liquid's own tokeniser - including the greedy
re-scan inside a raw block - to say exactly what Jekyll would reject. These
pin that behaviour on synthetic files: what passes, what fails, and the raw
block edge case the module docstring calls out.

    python3 -m unittest discover scripts/tests
"""
import pathlib
import sys
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
import verify_liquid as vl  # noqa: E402


def problems(text: str):
    with tempfile.TemporaryDirectory() as d:
        p = pathlib.Path(d) / "f.md"
        p.write_text(text, encoding="utf-8")
        return vl.check(p)


class LiquidRules(unittest.TestCase):
    def test_plain_markdown_passes(self):
        self.assertEqual(problems("# Title\n\nSome prose with {braces} and 50% done.\n"), [])

    def test_balanced_tags_pass(self):
        self.assertEqual(problems("{% if x %}a{% endif %} and {{ y }}\n"), [])

    def test_unterminated_tag_opener_is_reported_with_its_line(self):
        out = problems("line one\nA stray {% here\n")
        self.assertEqual(len(out), 1)
        line, msg = out[0]
        self.assertEqual(line, 2)
        self.assertIn("unterminated '{%'", msg)

    def test_unterminated_output_opener(self):
        out = problems("text {{ never closed\n")
        self.assertEqual(out[0][1].split(" - ")[0], "unterminated '{{'")

    def test_backticks_do_not_protect(self):
        # The docstring's warning, pinned: Liquid runs before Markdown.
        self.assertEqual(len(problems("`{%` in code\n")), 1)

    def test_raw_block_protects_its_contents(self):
        self.assertEqual(problems("{% raw %} a {% b {{ c {% endraw %}\n"), [])

    def test_raw_block_greedy_rescan_edge_case(self):
        # Liquid's FullTokenPossiblyInvalid matches the LAST tag in a token, so
        # this closes correctly even though the non-greedy tokeniser swallowed
        # the endraw into one token. A checker without the re-scan reports a
        # false failure here.
        self.assertEqual(problems("{% raw %}\\text{% ... %}{% endraw %}\n"), [])

    def test_unclosed_raw_is_reported(self):
        out = problems("{% raw %} never closed\n")
        self.assertEqual(out, [(0, "'{% raw %}' is never closed with '{% endraw %}'")])

    def test_inner_raw_is_literal(self):
        # Inside a raw block only endraw is honoured, so a second {% raw %} does
        # not nest: the first endraw closes the block and the text after it is
        # ordinary again.
        self.assertEqual(problems("{% raw %}{% raw %}x{% endraw %}\n"), [])
        self.assertEqual(len(problems("{% raw %}{% raw %}x{% endraw %} {{ open\n")), 1)


if __name__ == "__main__":
    unittest.main()

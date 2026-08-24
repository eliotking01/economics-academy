"""Tests for scripts/build_search_index.py - the site-search payload.

What matters here is that no search result can dangle: every URL a row can
produce must resolve to a real file or a real anchor, the schema the client
reconstructs from must hold, and two runs must give identical bytes. The
matcher itself is covered by scripts/test_site_search.js.
"""

import json
import pathlib
import re
import sys
import unittest

SCRIPTS = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SCRIPTS))

import build_search_index as bsi  # noqa: E402

ROOT = SCRIPTS.parent


class TestSearchIndex(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.index = bsi.build()

    def test_shape_and_counts(self):
        idx = self.index
        self.assertEqual(len(idx["dirs"]), 6)
        self.assertEqual(len(idx["topics"]), 166)
        self.assertEqual(len(idx["decks"]), 6)
        data = json.loads((ROOT / "glossary-data" / "terms.json")
                          .read_text(encoding="utf-8"))
        self.assertEqual(len(idx["glossary"]),
                         len(data["terms"]) + len(data["formulae"]))
        # 20 curated pages + 14 board hubs + the FAQ questions.
        self.assertGreaterEqual(len(idx["pages"]), 50)

    def test_deterministic(self):
        self.assertEqual(bsi.render(self.index), bsi.render(bsi.build()))

    def test_size_budget(self):
        raw = bsi.render(self.index).encode("utf-8")
        self.assertLess(len(raw), 150_000,
                        "the index has outgrown its budget - trim before "
                        "shipping, do not just raise this number")

    def test_topic_rows_resolve(self):
        """Every URL the client can build from a topic row is a real page."""
        for di, slug, spec, title, short, headings, ppq in self.index["topics"]:
            notes_dir, board, module, board_slug = self.index["dirs"][di]
            self.assertTrue(spec and title and headings, msg=slug)
            for rel in ([f"revision-notes/{notes_dir}/{slug}.html",
                         f"practice-questions/{notes_dir}/{slug}.html"]
                        + ([f"past-paper-questions/{board_slug}/{slug}/index.html"]
                           if ppq else [])):
                self.assertTrue((ROOT / rel).is_file(), msg=rel)

    def test_deck_rows_resolve(self):
        for title, url, di in self.index["decks"]:
            self.assertTrue((ROOT / url.lstrip("/") / "index.html").is_file(),
                            msg=url)
            self.assertTrue(0 <= di < len(self.index["dirs"]), msg=title)

    def test_glossary_anchors_resolve(self):
        """Every board a term claims carries its anchor on that board's page."""
        pages = {
            1: (ROOT / "revision-notes/glossary/edexcel-a/index.html")
                .read_text(encoding="utf-8"),
            2: (ROOT / "revision-notes/glossary/aqa/index.html")
                .read_text(encoding="utf-8"),
        }
        for title, ident, mask, kind, definition in self.index["glossary"]:
            self.assertTrue(definition, msg=title)
            self.assertIn(kind, (0, 1), msg=title)
            for bit, text in pages.items():
                if mask & bit:
                    self.assertIn(f'id="{ident}"', text,
                                  msg=f"{title}: no anchor on board {bit}")

    def test_page_rows_resolve(self):
        for title, url, meta, match in self.index["pages"]:
            self.assertTrue(title, msg=url)
            path, _, frag = url.partition("#")
            self.assertTrue(bsi.page_file(path).is_file(), msg=url)
            if frag:
                text = bsi.page_file(path).read_text(encoding="utf-8")
                self.assertIn(f'id="{frag}"', text, msg=url)

    def test_ppq_flag_matches_the_tail_gate(self):
        """The rows that link a question-bank page are exactly the topics the
        notes tail links one for - same bank, same gate."""
        import notes_extras
        import build_past_paper_questions as ppq_mod
        bank = notes_extras.past_paper_bank()
        for row in self.index["topics"]:
            slug, flag = row[1], row[6]
            expected = 1 if len(bank.get(slug, [])) >= ppq_mod.GATE else 0
            self.assertEqual(flag, expected, msg=slug)


if __name__ == "__main__":
    unittest.main()

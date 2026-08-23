"""notes_sequence.py - the derived previous/next chain.

The chain is derived from boards.json, the hub slices and the topic records,
so the tests use the real data (it is the fixture) and pin the properties
verify_notes_sequence.py relies on: natural ordering, hub parsing, chain
lengths equal to expectedTopics, two-sided rows with hub slots at the ends.

    python3 -m unittest discover scripts/tests
"""
import pathlib
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
import board_data  # noqa: E402
import notes_sequence as ns  # noqa: E402


class NaturalKeyTests(unittest.TestCase):
    def test_numeric_not_lexical(self):
        slugs = ["1-2-10-alternative-views", "1-2-2-demand", "1-10-1-x", "1-2-1-rational"]
        self.assertEqual(sorted(slugs, key=ns.natural_key),
                         ["1-2-1-rational", "1-2-2-demand", "1-2-10-alternative-views", "1-10-1-x"])

    def test_slug_without_a_spec_code_exits(self):
        with self.assertRaises(SystemExit):
            ns.natural_key("demand")


class HubParsingTests(unittest.TestCase):
    def test_hub_links_parser_collapses_whitespace_and_ignores_foreign_links(self):
        p = ns._HubLinks("edexcel-theme-1")
        p.feed('<a href="/revision-notes/edexcel-theme-1/1-2-2-demand.html">'
               '<span>1.2.2</span>\n   <span>Demand</span></a>'
               '<a href="/revision-notes/aqa-a2-micro/1-1-1-x.html">Other board</a>'
               '<a href="/practice-questions/">Not a topic</a>')
        p.close()
        self.assertEqual(p.result(), [("1-2-2-demand", "1.2.2 Demand")])

    def test_every_hub_is_in_spec_order_with_no_duplicates(self):
        for _key, _board, group in board_data.groups():
            links = ns.hub_topics(group["notesDir"])
            slugs = [s for s, _ in links]
            self.assertEqual(len(slugs), len(set(slugs)), group["notesDir"])
            self.assertEqual(slugs, sorted(slugs, key=ns.natural_key), group["notesDir"])


class ChainTests(unittest.TestCase):
    def setUp(self):
        self.chains = ns.chains()

    def test_one_chain_per_board_in_boards_json_order(self):
        self.assertEqual([c.board_key for c in self.chains], list(board_data.load()))

    def test_each_chain_is_its_declared_length(self):
        for c in self.chains:
            self.assertEqual(len(c.entries), c.expected, c.board_key)

    def test_chains_never_join(self):
        seen = set()
        for c in self.chains:
            dirs = set(c.dirs)
            self.assertFalse(dirs & seen, "a directory is in two chains")
            seen |= dirs

    def test_rows_at_the_ends_point_back_to_the_hub(self):
        c = self.chains[0]
        first_dir, first_slug, _ = c.entries[0]
        last_dir, last_slug, _ = c.entries[-1]
        top, bottom = ns.rows(first_dir, first_slug)
        self.assertIn(f'href="/revision-notes/{first_dir}/"', top)      # prev = hub
        self.assertIn('rel="next"', top)
        self.assertNotIn('rel="prev"', top)
        top, _ = ns.rows(last_dir, last_slug)
        self.assertIn(f'href="/revision-notes/{last_dir}/"', top)       # next = hub
        self.assertIn('rel="prev"', top)
        self.assertNotIn('rel="next"', top)
        # two rows, two different positions, same links
        self.assertIn('topic-nav--top', top)
        self.assertIn('topic-nav--bottom', bottom)

    def test_middle_rows_are_two_sided_and_label_from_the_hub(self):
        c = self.chains[0]
        d, s, label = c.entries[1]
        top, _ = ns.rows(d, s)
        prev_d, prev_s, prev_label = c.entries[0]
        next_d, next_s, next_label = c.entries[2]
        self.assertIn(f'href="/revision-notes/{prev_d}/{prev_s}.html"', top)
        self.assertIn(f'href="/revision-notes/{next_d}/{next_s}.html"', top)
        self.assertIn(ns.CAPTION_PREV, top)
        self.assertIn(ns.CAPTION_NEXT, top)

    def test_unknown_topic_exits(self):
        with self.assertRaises(SystemExit):
            ns.rows("edexcel-theme-1", "9-9-9-nowhere")


if __name__ == "__main__":
    unittest.main()

"""notes_extras.py - the generated tail of every topic page.

The tail is derived from questions-data/ and the past-paper bank's source
files, so the tests use the real data as the fixture and pin the properties
the redesign of 2026-08-23 rests on: the counts the notes pages print agree
with the index the past-paper generator writes; every destination the old
hand-placed tail carried is still emitted exactly once; the derived sentence
says what the data says.

    python3 -m unittest discover scripts/tests
"""
import json
import pathlib
import re
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
import notes_extras as ne  # noqa: E402

INDEX = ROOT / "past-paper-questions" / "questions.json"


class PastPaperNoteTests(unittest.TestCase):
    def test_one_question(self):
        self.assertEqual(
            ne.past_paper_note("AQA", [(2019, "a-level", 25)]),
            "One question from the AQA A-Level papers, 2019, worth 25 marks, "
            "linked to the page of the official mark scheme where its answer "
            "begins.")

    def test_several_same_tariff_and_as_only(self):
        note = ne.past_paper_note("Edexcel", [(2018, "as-level", 4),
                                              (2020, "as-level", 4)])
        self.assertTrue(note.startswith(
            "Two questions from the Edexcel AS papers, 2018&ndash;2020, "
            "4 marks each, each linked"))

    def test_mixed_levels_and_tariffs(self):
        note = ne.past_paper_note("Edexcel", [(2017, "a-level", 25),
                                              (2024, "as-level", 4),
                                              (2019, "a-level", 8)])
        self.assertTrue(note.startswith(
            "Three questions from the Edexcel A-Level and AS papers, "
            "2017&ndash;2024, 4 to 25 marks, each linked"))

    def test_large_counts_use_digits(self):
        qs = [(2020, "a-level", 25)] * 14
        self.assertTrue(ne.past_paper_note("AQA", qs).startswith("14 questions"))


@unittest.skipUnless(INDEX.is_file(), "questions.json not built")
class BankAgreesWithIndexTests(unittest.TestCase):
    """The notes pages count from the SOURCE files (tags + papers); the
    search index is built from the same files by a later generator. If the
    two ever disagree, one of them has changed its publishing rule."""

    def test_counts_match_the_committed_index(self):
        index = json.loads(INDEX.read_text(encoding="utf-8"))
        bank = ne.past_paper_bank()
        for slug, topic in index["topics"].items():
            self.assertEqual(len(bank.get(slug, [])), topic["count"], slug)
        # and nothing counted here that the index does not publish
        self.assertEqual(set(bank) - set(index["topics"]), set())

    def test_gate_decides_the_link(self):
        index = json.loads(INDEX.read_text(encoding="utf-8"))
        self.assertEqual(ne.ppq.GATE, index["gate"])


class TailShapeTests(unittest.TestCase):
    """One Edexcel page with a diagram-gallery line, one AQA page without."""

    def tail_of(self, notes_dir, slug):
        src = ROOT / "notes-data" / "topics" / notes_dir / f"{slug}.html"
        body = src.read_text(encoding="utf-8")
        code = re.search(r"unit\s+(\d+(?:\.\d+)+)", body).group(1)
        return ne.apply_all(body, notes_dir, slug, code, "2026-08-13")

    def test_every_destination_once(self):
        out = self.tail_of("edexcel-theme-1", "1-2-2-demand")
        for href in (
            "/practice-questions/edexcel-theme-1/1-2-2-demand.html",
            "/flashcards/edexcel-a/theme-1/?topic=1-2-2-demand",
            "/past-paper-questions/edexcel/1-2-2-demand/",
            "/past-papers/edexcel/",
            "/revision-notes/microeconomics-diagrams.html",
            "/tutoring.html",
            "/marking.html",
        ):
            self.assertEqual(out.count(f'href="{href}"'), 1, href)
        # the author: byline under the <h1> and the box in the tail, no more
        self.assertEqual(out.count(f'href="{ne.AUTHOR_URL}"'), 2)
        # the gallery line is inside the next-steps unit, not a sibling of it
        nav = out[out.index('<nav class="topic-next"'):]
        nav = nav[:nav.index("</nav>")]
        self.assertIn('class="notes-diagrams-link"', nav)
        # order: related, next, author, services
        idx = [out.index(s) for s in ('class="topic-related"', 'class="topic-next"',
                                      'class="topic-author"', 'class="topic-services"')]
        self.assertEqual(idx, sorted(idx))
        self.assertNotIn("notes-cta", out)

    def test_untagged_topic_gets_the_hub_panel(self):
        # AQA 1.1.1 has no tagged past-paper questions (as of 2026-08-23),
        # and no AQA page carries a diagram-gallery line.
        out = self.tail_of("aqa-a2-micro", "1-1-1-economic-methodology")
        self.assertEqual(out.count('href="/past-papers/aqa/"'), 1)
        self.assertNotIn("/past-paper-questions/", out)
        self.assertNotIn("notes-diagrams-link", out)

    def test_a_slice_with_a_legacy_tail_fails(self):
        src = ROOT / "notes-data" / "topics" / "aqa-a2-micro" / \
            "1-6-6-the-national-minimum-wage.html"
        body = src.read_text(encoding="utf-8")
        bad = body.replace("\n          </div>",
                           '\n            <div class="notes-cta"></div>\n          </div>')
        with self.assertRaises(SystemExit):
            ne.with_tail(bad, "aqa-a2-micro", "1-6-6-the-national-minimum-wage")


if __name__ == "__main__":
    unittest.main()

"""build_past_paper_questions.py - the copy that varies with a topic's size.

The gate fell from 4 to 2 on 2026-08-24 and published 46 topic pages carrying
two or three questions. Sentences that had only ever been rendered over a long
list suddenly had to be grammatical over a short one, and two of the new pages
draw every question from a single year - a case no page had ever hit before.

These pin the three pure functions that decide that copy, and the property the
gate change rests on: that a small page is a real page, not a stretched one.

    python3 -m unittest discover scripts/tests
"""
import json
import pathlib
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
import build_past_paper_questions as ppq  # noqa: E402

INDEX = ROOT / "past-paper-questions" / "questions.json"


def index():
    return json.loads(INDEX.read_text(encoding="utf-8"))


class GateTests(unittest.TestCase):
    """The gate is one number, declared once, and it may fall but not rise."""

    def test_gate_matches_the_published_index(self):
        self.assertEqual(ppq.GATE, index()["gate"])

    def test_every_topic_at_or_above_the_gate_has_a_page(self):
        idx = index()
        for slug, t in idx["topics"].items():
            self.assertEqual(
                t["hasPage"], t["count"] >= ppq.GATE,
                f"{slug}: {t['count']} question(s), hasPage={t['hasPage']}")

    def test_a_page_exists_on_disk_for_every_gated_topic(self):
        idx = index()
        for slug, t in idx["topics"].items():
            page = ROOT / t["url"].strip("/") / "index.html"
            self.assertEqual(page.is_file(), t["hasPage"], t["url"])


class YearSpanTests(unittest.TestCase):
    """year_span() fills a slot that always follows a comma.

    A range keeps the en dash it has always had - changing that would rewrite
    the hero of all 127 pages. A single year cannot use the same shape: ", 2018."
    reads as a stray date stamp where the reader expects a span.
    """

    def span(self, years):
        idx = {"papers": [{"year": y} for y in years]}
        qs = [{"p": i} for i in range(len(years))]
        return ppq.year_span(idx, qs)

    def test_a_range_is_unchanged(self):
        self.assertEqual(self.span([2016, 2020, 2024]), "2016&ndash;2024")

    def test_two_questions_from_one_year(self):
        self.assertEqual(self.span([2018, 2018]), "all set in 2018")

    def test_three_questions_from_one_year(self):
        self.assertEqual(self.span([2019, 2019, 2019]), "all set in 2019")

    def test_a_single_question_does_not_say_all(self):
        self.assertEqual(self.span([2018]), "set in 2018")

    def test_no_questions_is_empty(self):
        self.assertEqual(self.span([]), "")

    def test_the_range_survives_the_description_rewrite(self):
        # Three call sites render the description with this substitution.
        self.assertEqual(
            self.span([2016, 2024]).replace("&ndash;", " to "), "2016 to 2024")
        self.assertEqual(
            self.span([2018, 2018]).replace("&ndash;", " to "), "all set in 2018")


class TitleCollisionTests(unittest.TestCase):
    """Two Edexcel topics are called "Balance of Payments" - 2.1.4 and 4.1.7.

    Both cleared the gate at 2, so both got a page. Without disambiguation they
    would share a <title>, a description and an <h1>; verify_seo.py check 6
    fails on exactly that.
    """

    def test_the_known_collision_is_detected(self):
        self.assertIn(("edexcel", "Balance of Payments"), ppq.title_collisions(index()))

    def test_a_colliding_title_gains_its_section(self):
        idx = index()
        cols = ppq.title_collisions(idx)
        self.assertEqual(
            ppq.display_title(idx, "2-1-4-balance-of-payments", cols),
            "Balance of Payments (Theme 2)")
        self.assertEqual(
            ppq.display_title(idx, "4-1-7-balance-of-payments", cols),
            "Balance of Payments (Theme 4)")

    def test_an_uncontested_title_is_left_alone(self):
        idx = index()
        cols = ppq.title_collisions(idx)
        self.assertEqual(
            ppq.display_title(idx, "3-4-6-monopsony", cols), "Monopsony")

    def test_only_published_topics_can_collide(self):
        # A pageless topic has no <title> to clash with, so it must not drag a
        # bracketed section onto a page that does not need one.
        idx = index()
        for t in idx["topics"].values():
            t["hasPage"] = False
        self.assertEqual(ppq.title_collisions(idx), set())


class CountPhraseTests(unittest.TestCase):
    def test_singular_and_plural(self):
        self.assertEqual(ppq.question_count_phrase(1), "1 question")
        self.assertEqual(ppq.question_count_phrase(2), "2 questions")
        self.assertEqual(ppq.question_count_phrase(3), "3 questions")


class SmallPageTests(unittest.TestCase):
    """A two-question page gets everything a twenty-three-question page gets.

    Rendered from the real index, so this fails if the template ever grows a
    block that only fills in on a long list.
    """

    def rendered(self, slug):
        idx = index()
        _, page = ppq.render_topic_page(idx, slug, ppq.title_collisions(idx))
        return page

    def test_the_smallest_pages_carry_the_full_furniture(self):
        idx = index()
        smallest = sorted(
            (t["count"], s) for s, t in idx["topics"].items() if t["hasPage"])[:8]
        self.assertEqual(smallest[0][0], ppq.GATE, "no page sits at the gate")
        for count, slug in smallest:
            page = self.rendered(slug)
            t = idx["topics"][slug]
            with self.subTest(slug=slug, count=count):
                self.assertIn('class="ppq-intro"', page)
                self.assertIn("BreadcrumbList", page)
                self.assertIn("CollectionPage", page)
                self.assertIn("<h2>Related topics</h2>", page)
                self.assertIn(t["notesUrl"], page)
                self.assertIn(t["questionsUrl"], page)
                self.assertIn(ppq.question_count_phrase(count), page)

    def test_a_small_page_bakes_every_one_of_its_questions(self):
        # The static cards ARE the no-JS list on a topic page.
        idx = index()
        for slug, t in idx["topics"].items():
            if not t["hasPage"] or t["count"] > 3:
                continue
            page = self.rendered(slug)
            with self.subTest(slug=slug):
                self.assertEqual(page.count('class="ppq-card"'), t["count"])


if __name__ == "__main__":
    unittest.main()

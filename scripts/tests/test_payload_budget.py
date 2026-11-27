"""verify_payload_budget.classify(): which budget each bank path falls under."""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import verify_payload_budget as vpb  # noqa: E402


class ClassifyTest(unittest.TestCase):
    def test_classes(self):
        cases = {
            "questions.json": "master",
            "aqa/questions.json": "board",
            "aqa/microeconomics/questions.json": "section",
            "edexcel-b/theme-3/questions.json": "section",
            "aqa/1-2-3-some-topic/questions.json": "topic",
            "aqa/microeconomics/index.html": "section-html",
            "edexcel/theme-1/index.html": "section-html",
        }
        for rel, want in cases.items():
            self.assertEqual(vpb.classify(Path(rel)), want, rel)

    def test_unbudgeted(self):
        # Topic pages, board hubs and the master page HTML carry no ceiling.
        for rel in ("aqa/1-2-3-some-topic/index.html", "aqa/index.html",
                    "index.html", "aqa/theme-1/extra/questions.json"):
            self.assertIsNone(vpb.classify(Path(rel)), rel)

    def test_every_class_has_a_ceiling(self):
        self.assertEqual(set(vpb.CEILINGS),
                         {"master", "board", "section", "topic", "section-html"})


if __name__ == "__main__":
    unittest.main()

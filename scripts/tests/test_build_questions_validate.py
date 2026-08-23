"""build_questions.validate() - the ~140 lines of authoring rules.

Each test takes a set that passes today (a real one from questions-data/,
deep-copied), breaks exactly one rule, and asserts validate() names it. The
real file is the cheapest complete valid fixture there is; if it ever moves,
BASE below is the one line to change.

    python3 -m unittest discover scripts/tests
"""
import json
import pathlib
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
import build_questions as bq  # noqa: E402

BASE = ROOT / "questions-data" / "edexcel-theme-1" / "1-2-2.json"


def load():
    return json.loads(BASE.read_text(encoding="utf-8"))


def errors_for(topic):
    """The error text validate() raises, or "" if it passes."""
    try:
        bq.validate(topic, BASE, {})
    except bq.SetError as e:
        return str(e)
    return ""


class ValidateTests(unittest.TestCase):
    def setUp(self):
        self.topic = load()

    def test_the_real_set_passes(self):
        self.assertEqual(errors_for(self.topic), "")
        tally = bq.validate(self.topic, BASE, {})
        self.assertEqual(sum(tally.values()), len(self.topic["questions"]))

    def test_missing_required_field(self):
        del self.topic["notesTeaser"]
        self.assertIn("missing field 'notesTeaser'", errors_for(self.topic))

    def test_board_dir_must_match_board(self):
        self.topic["boardDir"] = "aqa-a2-micro"
        self.assertIn("does not match board", errors_for(self.topic))

    def test_unknown_board_dir(self):
        self.topic["boardDir"] = "edexcel-theme-9"
        self.assertIn("boardDir must be one of", errors_for(self.topic))

    def test_notes_page_must_exist(self):
        self.topic["slug"] = "1-2-2-no-such-page"
        self.assertIn("no notes page at", errors_for(self.topic))

    def test_meta_description_length_band(self):
        self.topic["metaDescription"] = "Too short."
        self.assertIn("metaDescription is 10 chars, want 120-165",
                      errors_for(self.topic))

    def test_page_title_suffix(self):
        self.topic["pageTitle"] = "Demand questions"
        self.assertIn("pageTitle must end '| Economics Academy'",
                      errors_for(self.topic))

    def test_question_count_band(self):
        self.topic["questions"] = self.topic["questions"][:3]
        self.assertIn("3 questions, want 4-10", errors_for(self.topic))

    def test_question_id_shape(self):
        self.topic["questions"][0]["id"] = "bad id"
        self.assertIn("does not match <board>-<spec>-q<n>", errors_for(self.topic))

    def test_duplicate_id_across_sets(self):
        qid = self.topic["questions"][0]["id"]
        with self.assertRaises(bq.SetError) as cm:
            bq.validate(self.topic, BASE, {qid: "some/other.json"})
        self.assertIn(f"duplicate id {qid!r}", str(cm.exception))

    def test_skill_and_difficulty_vocabulary(self):
        self.topic["questions"][0]["skill"] = "guessing"
        self.topic["questions"][1]["difficulty"] = "impossible"
        out = errors_for(self.topic)
        self.assertIn("q1: skill must be one of", out)
        self.assertIn("q2: difficulty must be one of", out)

    def test_sketch_is_boolean(self):
        self.topic["questions"][0]["sketch"] = "no"
        self.assertIn("q1: sketch must be true or false", errors_for(self.topic))

    def test_options_are_exactly_abcd(self):
        del self.topic["questions"][0]["options"]["D"]
        self.assertIn("q1: options must be exactly A, B, C, D", errors_for(self.topic))

    def test_banned_option_pattern(self):
        self.topic["questions"][0]["options"]["A"] = "All of the above."
        self.assertIn("q1.options.A: banned option pattern", errors_for(self.topic))

    def test_answer_letter(self):
        self.topic["questions"][0]["answer"] = "E"
        self.assertIn("q1: answer must be A, B, C or D", errors_for(self.topic))

    def test_distractors_cover_the_other_three(self):
        q = self.topic["questions"][0]
        q["model"]["distractors"].pop(next(iter(q["model"]["distractors"])))
        self.assertIn("model.distractors must cover exactly", errors_for(self.topic))

    def test_disallowed_markup_in_a_fragment(self):
        self.topic["questions"][0]["stem"] = "<script>alert(1)</script> What is demand?"
        out = errors_for(self.topic)
        self.assertIn("q1.stem", out)

    def test_us_spelling_is_rejected(self):
        self.topic["questions"][0]["stem"] = (
            "A firm's behavior changes when the price of a substitute rises. "
            "What happens to demand?")
        self.assertIn("q1.stem", errors_for(self.topic))

    def test_letter_distribution(self):
        for q in self.topic["questions"]:
            q["answer"] = "A"
            q["model"]["distractors"] = {l: "Wrong, because of the reasoning above."
                                         for l in "BCD"}
        self.assertIn("letter distribution: A used", errors_for(self.topic))

    def test_table_shape(self):
        self.topic["questions"][0]["table"] = {
            "caption": "", "head": ["Year", "Price"], "rows": [["2020"]]}
        out = errors_for(self.topic)
        self.assertIn("q1.table: missing caption", out)
        self.assertIn("q1.table.rows[0]: expected 2 cells", out)


if __name__ == "__main__":
    unittest.main()

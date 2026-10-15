"""new_topic.py - the hub edits and the notes-only board filter.

The hub edits are pure string functions, so they are tested on a small
hand-written hub. The board filter is tested on the real boards.json, which
is the fixture: load() must never return a notes-only board, because the
practice-questions, flashcards, glossary and taxonomy generators iterate it.

    python3 -m unittest discover scripts/tests
"""
import pathlib
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
import board_data  # noqa: E402
import new_topic  # noqa: E402

HUB = """            <p class="resource-stats">1 topic &middot; free, no sign-up</p>
            <div class="resource-index">
              <section class="resource-index-unit" id="unit-1-1">
                <div class="resource-index-unit-head">
                  <h3>1.1 First Unit</h3>
                  <span class="resource-index-count">1 topic</span>
                </div>
                <p>Blurb.</p>
                <ul class="resource-index-topics">
                  <li>
                    <a href="/revision-notes/x-theme-1/1-1-1-one.html"
                      ><span class="resource-index-code">1.1.1</span>
                      <span class="resource-index-title">One</span></a
                    >
                  </li>
                </ul>
              </section>
              <section class="resource-index-unit" id="unit-1-2">
                <div class="resource-index-unit-head">
                  <h3>1.2 Second Unit</h3>
                  <span class="resource-index-count">0 topics</span>
                </div>
                <p>Blurb.</p>
                <ul class="resource-index-topics">
                </ul>
              </section>
            </div>
"""


def add(hub, spec, title):
    slug = f"{spec.replace('.', '-')}-{new_topic.kebab(title)}"
    return new_topic.hub_with_link(hub, notes_dir="x-theme-1", spec=spec,
                                   title=title, slug=slug)


class HubEditTests(unittest.TestCase):
    def test_topics_word_is_singular_for_one(self):
        self.assertEqual(new_topic.topics_word(1), "1 topic")
        self.assertEqual(new_topic.topics_word(0), "0 topics")
        self.assertEqual(new_topic.topics_word(2), "2 topics")

    def test_first_link_goes_into_an_empty_panel(self):
        out = add(HUB, "1.2.1", "Two Point One")
        unit = out[out.index('id="unit-1-2"'):]
        self.assertIn('<span class="resource-index-count">1 topic</span>', unit)
        self.assertIn("/revision-notes/x-theme-1/1-2-1-two-point-one.html", unit)
        # the <li> sits inside the list, two spaces in from the <ul>
        self.assertIn('<ul class="resource-index-topics">\n'
                      '                  <li>\n', unit)
        self.assertIn('<p class="resource-stats">2 topics &middot;', out)
        # unit 1.1 is untouched
        self.assertEqual(out[:out.index('id="unit-1-2"')].count("<li>"), 1)

    def test_link_into_a_populated_panel_bumps_both_counts(self):
        out = add(HUB, "1.1.2", "One Point Two")
        head = out[:out.index('id="unit-1-2"')]
        self.assertIn('<span class="resource-index-count">2 topics</span>', head)
        self.assertLess(head.index("1-1-1-one"), head.index("1-1-2-one-point-two"))
        self.assertIn('<p class="resource-stats">2 topics &middot;', out)

    def test_a_unit_with_no_panel_is_refused(self):
        with self.assertRaises(SystemExit):
            add(HUB, "1.3.1", "No Panel")

    def test_a_linked_page_is_refused_twice(self):
        with self.assertRaises(SystemExit):
            add(HUB, "1.1.1", "One")


class NotesOnlyFilterTests(unittest.TestCase):
    def test_load_never_returns_a_notes_only_board(self):
        self.assertFalse(any(b.get("notesOnly") for b in board_data.load().values()))
        self.assertFalse(any(b.get("notesOnly") for _k, b, _g in board_data.groups()))

    def test_load_notes_is_load_plus_the_notes_only_boards(self):
        full = board_data.load()
        notes = board_data.load_notes()
        self.assertEqual({k for k, b in notes.items() if not b.get("notesOnly")},
                         set(full))
        self.assertEqual(tuple(notes), board_data.EXPECTED_KEYS)


if __name__ == "__main__":
    unittest.main()

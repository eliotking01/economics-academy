"""site_layout.py - the one generator list, the publish rules, the families,
and the import direction the module exists to enforce.

    python3 -m unittest discover scripts/tests
"""
import ast
import pathlib
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))
import site_layout as sl  # noqa: E402


class GeneratorListTests(unittest.TestCase):
    def test_every_generator_exists_and_sitemap_is_last(self):
        for name in sl.GENERATORS:
            self.assertTrue((SCRIPTS / name).is_file(), name)
        self.assertEqual(sl.GENERATORS[-1], sl.SITEMAP_GENERATOR)
        self.assertEqual(sl.GENERATORS, sl.CONTENT_GENERATORS + (sl.SITEMAP_GENERATOR,))

    def test_order_constraints(self):
        g = list(sl.GENERATORS)
        self.assertLess(g.index("build_past_paper_taxonomy.py"),
                        g.index("build_past_paper_questions.py"))
        self.assertLess(g.index("extract_glossary.py"), g.index("build_glossary.py"))
        self.assertEqual(g[0], "build_notes_pages.py")

    def test_verify_generated_and_build_import_the_list(self):
        # exactly ONE list: the two consumers must read it from here
        for name in ("verify_generated.py", "build.py"):
            src = (SCRIPTS / name).read_text(encoding="utf-8")
            self.assertIn("site_layout", src, name)
            self.assertNotIn('"build_flashcards.py",\n    "build_sitemap.py"', src, name)


class PublishRuleTests(unittest.TestCase):
    def test_excludes_parses_config(self):
        ex = sl.excludes()
        for must in ("scripts/", "docs/", "notes-data/", "templates/", "package.json", "CLAUDE.md"):
            self.assertIn(must, ex)

    def test_published(self):
        ex = sl.excludes()
        self.assertTrue(sl.published("index.html", ex))
        self.assertTrue(sl.published("revision-notes/edexcel-theme-1/1-2-2-demand.html", ex))
        self.assertFalse(sl.published("scripts/build.py", ex))
        self.assertFalse(sl.published("_archive/x.md", ex))
        self.assertFalse(sl.published("a/_b/c.html", ex))
        self.assertFalse(sl.published("CLAUDE.md", ex))
        self.assertFalse(sl.published("package.json", ex))
        self.assertFalse(sl.published("templates/header.html", ex))

    def test_pages_are_published_html_only(self):
        pages = sl.pages()
        self.assertGreater(len(pages), 400)
        self.assertTrue(all(p.endswith(".html") for p in pages))
        self.assertNotIn("templates/header.html", pages)
        self.assertEqual(pages, sorted(pages))


class FamilyTests(unittest.TestCase):
    def test_family_of(self):
        cases = {
            "index.html": "root",
            "past-papers/ocr/index.html": "past-papers",
            "revision-notes/index.html": "notes-other",
            "revision-notes/microeconomics-diagrams.html": "notes-other",
            "revision-notes/edexcel-theme-1/index.html": "notes-hub",
            "revision-notes/macro-application/index.html": "notes-hub",
            "revision-notes/edexcel-theme-1/1-2-2-demand.html": "notes-topic",
            "revision-notes/glossary/index.html": "glossary",
            "revision-notes/glossary/aqa/index.html": "glossary",
            "practice-questions/index.html": "mcq-hub",
            "practice-questions/edexcel-theme-1/1-2-2-demand.html": "mcq-topic",
            "past-paper-questions/edexcel/1-2-2-demand/index.html": "ppq",
            "flashcards/aqa/micro/index.html": "flashcards",
        }
        for path, fam in cases.items():
            self.assertEqual(sl.family_of(path), fam, path)

    def test_hand_written_families(self):
        self.assertEqual(set(sl.HAND_WRITTEN), {"root", "notes-other", "past-papers"})


class ImportDirectionTests(unittest.TestCase):
    """Verifiers may import generators; generators never import a verifier.
    page_shell.py imported verify_page_shell until 2026-08-23."""

    GENERATOR_LIKE = [
        "build.py", "page_shell.py", "bake_templates.py", "board_data.py",
        "notes_sequence.py", "notes_extras.py", "prettier_util.py",
        "site_layout.py", "reseed_util.py", "new_topic.py",
    ]

    @staticmethod
    def imports_of(path):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for a in node.names:
                    yield a.name
            elif isinstance(node, ast.ImportFrom) and node.module:
                yield node.module

    def test_no_generator_imports_a_verifier(self):
        names = list(self.GENERATOR_LIKE) + list(sl.GENERATORS)
        for name in names:
            path = SCRIPTS / name
            bad = [m for m in self.imports_of(path) if m.startswith("verify_")]
            self.assertEqual(bad, [], f"{name} imports a verifier: {bad}")

    def test_site_layout_imports_no_sibling(self):
        siblings = {p.stem for p in SCRIPTS.glob("*.py")} - {"site_layout"}
        bad = [m for m in self.imports_of(SCRIPTS / "site_layout.py") if m in siblings]
        self.assertEqual(bad, [])


if __name__ == "__main__":
    unittest.main()

"""page_shell.py - the shared shell helpers the four generators call.

These are the pieces that moved out of build_questions.py, build_flashcards.py,
build_glossary.py and build_past_paper_questions.py on 2026-08-23. Each
migration was proved byte-identical by verify_generated.py; these tests pin
the helpers' contracts so a later "tidy" cannot quietly move a byte.

    python3 -m unittest discover scripts/tests
"""
import json
import pathlib
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
import page_shell as ps  # noqa: E402

CRUMBS = [("Home", "/"), ("Flashcards", "/flashcards/"), ("Theme 1 & 2", None)]


class BreadcrumbTests(unittest.TestCase):
    def test_ld_shape_and_key_order(self):
        ld = ps.breadcrumb_ld(CRUMBS)
        self.assertEqual(ld["@type"], "BreadcrumbList")
        items = ld["itemListElement"]
        self.assertEqual([i["position"] for i in items], [1, 2, 3])
        # item only when there is an href, and key order is serialised
        self.assertEqual(list(items[0]), ["@type", "position", "name", "item"])
        self.assertEqual(list(items[2]), ["@type", "position", "name"])
        self.assertEqual(items[1]["item"], "https://economicsacademy.co.uk/flashcards/")

    def test_html_form(self):
        html = ps.breadcrumb_html(CRUMBS, indent=4)
        self.assertTrue(html.startswith('    <nav class="breadcrumb" aria-label="Breadcrumb">\n'))
        self.assertTrue(html.endswith("\n    </nav>"))
        # n crumbs -> n-1 separators; the last crumb is a span; & is escaped
        self.assertEqual(html.count('<span class="separator">&rsaquo;</span>'), 2)
        self.assertIn("<span>Theme 1 &amp; 2</span>", html)
        self.assertIn('<a href="/flashcards/">Flashcards</a>', html)

    def test_html_and_ld_agree_on_names(self):
        # verify_page_shell.py check 8 compares the two on every page
        names_ld = [i["name"] for i in ps.breadcrumb_ld(CRUMBS)["itemListElement"]]
        self.assertEqual(names_ld, [n for n, _ in CRUMBS])

    def test_href_hook_and_custom_escape(self):
        html = ps.breadcrumb_html([("A", "/x/index.html")], esc=lambda s: s.upper(),
                                  href=lambda h: h.replace("index.html", ""))
        self.assertIn('<a href="/x/">A</a>', html)


class SkeletonTests(unittest.TestCase):
    def test_page_is_the_canonical_skeleton(self):
        out = ps.page("HEAD", "BODY", ("/js/x.js",))
        self.assertTrue(out.startswith('<!doctype html>\n<html lang="en-GB">\n  <head>\nHEAD\n  </head>\n'))
        self.assertIn('  <body class="is-preload">\n    <div id="page-wrapper">\n', out)
        self.assertIn(ps.HEADER_PLACEHOLDER, out)
        self.assertIn(ps.FOOTER_PLACEHOLDER, out)
        self.assertIn("\nBODY\n\n      <!-- Footer -->", out)
        for s in ps.SCRIPT_TAIL:
            self.assertIn(f'<script src="{s}"></script>', out)
        self.assertIn('<script src="/js/x.js" defer></script>', out)
        self.assertTrue(out.endswith("  </body>\n</html>\n"))
        # the family script comes after the tail, never before
        self.assertLess(out.index(ps.SCRIPT_TAIL[-1]), out.index("/js/x.js"))

    def test_container(self):
        out = ps.container("INNER", "glossary-page")
        self.assertEqual(out, '      <main id="main" class="glossary-page">\n'
                              '        <div class="container">\n'
                              'INNER\n'
                              '        </div>\n'
                              '      </main>')

    def test_bake_fills_both_placeholders_and_is_rerunnable(self):
        baked = ps.bake(ps.page("H", "B"), "about.html")
        self.assertNotIn(ps.HEADER_PLACEHOLDER, baked)
        self.assertNotIn(ps.FOOTER_PLACEHOLDER, baked)
        self.assertIn('<li data-page="about" class="current">', baked)
        self.assertEqual(ps.bake(baked, "about.html"), baked)   # idempotent


class HeadValueTests(unittest.TestCase):
    def test_social_and_head_values(self):
        v = ps.head_values('A "quoted" title', "Desc & more", "https://x/", ["/css/a.css"],
                           og_type="article")
        self.assertEqual(v["title"], "A &quot;quoted&quot; title")
        self.assertEqual(v["og"]["type"], "article")
        self.assertEqual(v["og"]["description"], "Desc &amp; more")
        self.assertEqual(v["twitter"]["card"], "summary_large_image")
        self.assertEqual(v["og"]["image"], ps.OG_IMAGE)
        self.assertEqual(v["pageStylesheets"], ["/css/a.css"])
        self.assertEqual(v["canonical"], "https://x/")

    def test_custom_escape_is_honoured(self):
        v = ps.head_values("It's", "x", "u", [], esc=lambda s: s)
        self.assertEqual(v["title"], "It's")

    def test_render_head_self_hosts_the_fonts(self):
        # Performance pass, 2026-08-23: no Google Fonts origin anywhere, the
        # body face preloaded before the stylesheets, FontAwesome before
        # main.css (4db232c), and a page's extra preconnect still honoured.
        base = ps.head_values("T", "D", "https://economicsacademy.co.uk/p/", ["/css/p.css"])
        head = ps.render_head({**base, "extraPreconnects": ["https://cdn.example"]})
        self.assertNotIn("fonts.googleapis.com", head)
        self.assertNotIn("fonts.gstatic.com", head)
        self.assertIn('rel="preload"', head)
        self.assertIn(ps.BODY_FONT, head)
        self.assertLess(head.index(ps.BODY_FONT), head.index("fontawesome-all"))
        self.assertLess(head.index("fontawesome-all"), head.index("/css/main.css"))
        self.assertLess(head.index("https://cdn.example"), head.index(ps.BODY_FONT))

    def test_tag_wraps_at_print_width(self):
        short = ps.tag("meta", [("name", "x"), ("content", "y")])
        self.assertEqual(short, '    <meta name="x" content="y" />')
        long_ = ps.tag("meta", [("name", "description"), ("content", "z" * 100)])
        self.assertEqual(long_.splitlines()[0], "    <meta")
        self.assertEqual(long_.splitlines()[-1], "    />")

    def test_ldjson_escaping_is_a_value(self):
        obj = {"name": "em — dash"}
        self.assertIn("—", ps.ldjson(obj))
        self.assertIn("\\u2014", ps.ldjson(obj, ascii_escape=True))
        self.assertEqual(json.loads(ps.ldjson(obj).split(">", 1)[1].rsplit("<", 1)[0]), obj)


class NavTests(unittest.TestCase):
    def test_url_path_and_active_page(self):
        self.assertEqual(ps.url_path("index.html"), "/")
        self.assertEqual(ps.url_path("flashcards/index.html"), "/flashcards/")
        self.assertEqual(ps.url_path("about.html"), "/about.html")
        self.assertEqual(ps.active_page("revision-notes/glossary/index.html"), "revision-notes")
        self.assertEqual(ps.active_page("past-paper-questions/index.html"), "past-papers")
        self.assertEqual(ps.active_page("past-papers/ocr/index.html"), "past-papers")
        self.assertEqual(ps.active_page("index.html"), "home")
        self.assertEqual(ps.active_page("privacy.html"), "")


if __name__ == "__main__":
    unittest.main()

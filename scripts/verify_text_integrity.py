#!/usr/bin/env python3
"""Prove that a commit changed no visible wording.

Extracts the plain text of every hand-written published page at two commits,
normalises whitespace, and diffs. Used to gate the formatting and emphasis
commits, where the rule is that markup may change but not a single word.

Script, style and comment content is dropped, since none of it is visible
text. Everything else - including the contents of inline elements such as
<strong> and <em> - is kept, so moving a tag boundary across a word would
still be caught.

WHAT IS COMPARED, AND WHY IT IS NOT SIMPLY revision-notes/

Until Wave 4.9 this walked `revision-notes/` and nothing else. That was wrong
in both directions, and the two errors hid each other:

  * 14 hand-written published pages were never compared - the 9 root pages
    (index, tutoring, marking, about, faq, contact, privacy, confirmation,
    404) and the 5 past-papers/ hub pages. The root pages are the commercial
    surface, so the wording most worth protecting was the wording nobody was
    checking. templates/header.html and footer.html were out too, and every
    nav label on all 463 pages comes from them.

  * The 3 generated glossary pages WERE compared, and they are the one place
    where a legitimate change routinely shows up: regenerate, and the diff is
    the generator's output rather than anybody's edit. Their wording already
    has a stronger guarantee than this script can give - verify_glossary.py
    check 1 re-reads the notes and fails if a shipped definition is no longer
    in its source page, and verify_generated.py proves the committed output is
    exactly what the source produces. A third, weaker check over the same
    files buys nothing and goes red on a correct commit.

So: every published page EXCEPT the four generated families. Coverage goes
from 179 files (3 of them generated) to 192 hand-written ones. If a generated
page's wording is wrong, the two checks named above are what catch it.

DELIBERATE CHANGES DECLARE THEMSELVES

A wording change that was approved is not the failure this exists to catch;
an accidental one is. A commit whose visible text changes on purpose names
the pages it changes:

    Text-Change: revision-notes/macro-application/index.html

one line per path, reason in the commit body. See declared() for why that is
a declaration rather than an off switch. A commit that declares one page and
changes the wording of another still fails.

THE HEADER AND FOOTER COUNT AS THE PAGE'S OWN TEXT

A page carrying <div id="header-placeholder"></div> displays the header's
words - inject-templates.js replaces that div with templates/header.html
before the reader sees anything. So the honest comparison has always been
"page text plus header text plus footer text", and reading the source alone
understated it by the whole of the nav on all 463 pages.

That never mattered while every page was the same shape. Wave 2 Phase 7 bakes
both templates into the source, which changes what the source says on every
page while changing nothing a reader sees - so comparing raw source text
across that commit would report 463 changed pages, all of them false. Rather
than declare 463 paths and turn the check off for the one commit it most
needs to be on for, visible() splices the templates in wherever a placeholder
is found. Both sides of the diff then say what the reader gets, which is the
question this script is asking.

Once no page carries a placeholder the branch stops firing. It is left in
because it remains the correct description of any page that has one.

Usage:
    python3 scripts/verify_text_integrity.py <before-ref> [<after-ref>]

<after-ref> defaults to the working tree. Exit status is non-zero if any
file's visible text differs without being declared. Note that a run against
uncommitted work has no commit message to read, so declare-then-commit is
the order; a red run before committing is expected.
"""

import difflib
import pathlib
import re
import subprocess
import sys
from html.parser import HTMLParser

ROOT = pathlib.Path(__file__).resolve().parent.parent

# Sibling in scripts/, for its _config.yml `exclude` parser and publish rule -
# the same import verify_liquid.py and verify_css_load_order.py use, so all
# three agree with the sitemap about what Jekyll actually builds.
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import build_sitemap  # noqa: E402

SKIP = {"script", "style"}

# Generated families. Fix the source or the generator and re-run; their text is
# guaranteed by verify_generated.py, and the glossary's additionally by
# verify_glossary.py check 1. See the module docstring.
GENERATED = (
    "revision-notes/glossary/",
    "practice-questions/",
    "past-paper-questions/",
    "flashcards/",
)


class TextExtractor(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts = []
        self.skip_depth = 0

    def handle_starttag(self, tag, attrs):
        if tag in SKIP:
            self.skip_depth += 1

    def handle_endtag(self, tag):
        if tag in SKIP and self.skip_depth:
            self.skip_depth -= 1

    def handle_data(self, data):
        if not self.skip_depth:
            self.parts.append(data)

    def text(self):
        return re.sub(r"\s+", " ", "".join(self.parts)).strip()


def extract(source):
    p = TextExtractor()
    p.feed(source)
    p.close()
    return p.text()


PLACEHOLDERS = (
    ('<div id="header-placeholder"></div>', "templates/header.html"),
    ('<div id="footer-placeholder"></div>', "templates/footer.html"),
)


def visible(source, templates):
    """A page's text as the reader gets it, placeholders resolved.

    `templates` maps template path -> its source AT THE SAME REF. Reading them
    from the working tree instead would be a trap: reword the nav and every
    one of the 190 pages would report a text change, burying the one real
    diff - templates/header.html's own - in 190 false ones.
    """
    for placeholder, path in PLACEHOLDERS:
        if placeholder in source:
            source = source.replace(placeholder, templates.get(path) or "", 1)
    return extract(source)


def read_at(ref, path):
    """File contents at a git ref, or from the working tree if ref is None."""
    if ref is None:
        return pathlib.Path(path).read_text(encoding="utf-8")
    result = subprocess.run(
        ["git", "show", f"{ref}:{path}"],
        capture_output=True, text=True,
    )
    return result.stdout if result.returncode == 0 else None


def list_files(ref):
    """Every hand-written published .html at `ref`, or in the working tree.

    The publish rule is read from today's _config.yml on both sides on
    purpose: this compares two revisions of the same site, so the question is
    what is published now, not what a past exclude list said.
    """
    if ref is None:
        out = subprocess.run(
            ["git", "ls-files", "*.html"], cwd=ROOT,
            capture_output=True, text=True, check=True,
        ).stdout.split()
    else:
        out = subprocess.run(
            ["git", "ls-tree", "-r", "--name-only", ref],
            capture_output=True, text=True, check=True,
        ).stdout.split()
    ex = build_sitemap.excludes()
    return sorted(
        f for f in out
        if f.endswith(".html")
        and build_sitemap.published(f, ex)
        and not f.startswith(GENERATED)
    )


TRAILER = re.compile(r"^Text-Change:\s*(\S+)", re.M)


def declared(before, after):
    """Paths declared by a `Text-Change:` trailer in the range's commits.

    A deliberate wording change is not the failure this script exists to
    catch - accidental ones are. Wave 5 is nothing but approved content
    changes, Wave 3's relabelling is another, and 4.9 added CTA copy to
    eleven pages; with no way to say so, the step goes red on correct work
    and is ignored within a week. So a commit may declare the files whose
    visible text it means to change:

        Text-Change: revision-notes/macro-application/index.html

    one line per path, with the reason in the commit body where it belongs.

    Three properties make this a declaration rather than a switch:

      * It lives in a commit message, so it applies to exactly that commit
        and cannot be left on by accident. There is no file to forget to
        revert.
      * It is per PATH. A commit that declares one page and changes the
        wording of another still fails, which is the accident being guarded
        against.
      * It is visible in `git log` forever, so the record of every
        deliberate wording change is the history itself.

    Trailers are collected across the whole range, so a merge commit is
    covered by the declarations of the commits it merges - which is the case
    that matters, since CI compares a merge against main's previous tip.
    """
    rng = f"{before}..{after or 'HEAD'}"
    out = subprocess.run(
        ["git", "log", "--format=%B", rng], cwd=ROOT,
        capture_output=True, text=True,
    )
    if out.returncode != 0:
        return set()
    return set(TRAILER.findall(out.stdout))


def main(argv):
    if len(argv) < 2:
        print(__doc__)
        return 2
    before = argv[1]
    after = argv[2] if len(argv) > 2 else None

    allowed = declared(before, after)
    files = list_files(before)
    differing = []
    missing = []

    # One read each, per side, rather than per page.
    old_templates = {p: read_at(before, p) for _, p in PLACEHOLDERS}
    new_templates = {p: read_at(after, p) for _, p in PLACEHOLDERS}

    for path in files:
        old = read_at(before, path)
        new = read_at(after, path)
        if new is None:
            missing.append(path)
            continue
        a = visible(old, old_templates)
        b = visible(new, new_templates)
        if a != b:
            differing.append((path, a, b))

    undeclared = [d for d in differing if d[0] not in allowed]

    for path, a, b in differing:
        state = "DECLARED" if path in allowed else "UNDECLARED"
        print(f"\n=== {path}  [{state}]")
        for line in list(difflib.unified_diff(
            a.split(" "), b.split(" "), lineterm="", n=6
        ))[:40]:
            print(f"  {line}")

    print(
        f"\n{len(files)} files compared between {before} and "
        f"{after or 'working tree'}"
    )
    print(f"  visible text differs: {len(differing)}")
    if allowed:
        print(f"  declared by a Text-Change: trailer: {len(allowed)}")
        # A declaration for a file that did not move is stale rather than
        # dangerous - a copied trailer, or a change reverted later in the
        # range. Say so; do not fail, because a commit message cannot be
        # amended once it is pushed.
        for path in sorted(allowed - {d[0] for d in differing}):
            print(f"    declared but unchanged: {path}")
    if undeclared:
        print(f"  UNDECLARED: {len(undeclared)}")
        print(
            "\nVisible wording changed on a page no commit in this range "
            "declared.\nIf the change is deliberate and approved, say so in "
            "the commit message:\n\n    Text-Change: <path>\n\n"
            "one line per path, reason in the body. If it is not deliberate, "
            "this is\nthe accident the check exists to catch."
        )
    if missing:
        print(f"  absent from the later revision: {len(missing)}")
        for m in missing:
            print(f"    {m}")
    return 1 if undeclared else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))

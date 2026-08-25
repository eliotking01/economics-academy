#!/usr/bin/env python3
"""Declared colour pairs in the page stylesheets meet WCAG contrast.

    python3 scripts/verify_contrast.py

Pure stdlib. Exit 1 if any pair is under its threshold, or if a listed
selector or declaration can no longer be found - a renamed selector must
fail loudly, not pass silently.

WHAT THIS CAN AND CANNOT SEE

It checks DECLARED pairs: a maintained list of (selector, foreground,
background) triples below, read out of the committed stylesheets and
measured with the WCAG 2.x relative-luminance formula. It does not compute
the cascade, so it cannot find a NEW failing combination on its own - it
exists so the pairs fixed in the 2026-08 accessibility pass cannot quietly
regress, the same job the pinned literals in verify_page_shell.py do.
Backgrounds that are gradients or washes are entered as the literal
composited colour, noted per entry.

THE LIST

One entry per checked pair:
  (stylesheet, selector, background, threshold)
- selector must appear in the stylesheet, and its first declaring block
  must set `color:` (or `background:` where marked) as a hex value or a
  var() the same file's tokens resolve.
- background is a literal hex: the surface the text actually sits on.
- threshold is 4.5 for normal text, 3.0 where the text is genuinely large
  (>= 24px, or >= 18.7px bold) or a meaningful non-text glyph (WCAG
  1.4.11).
"""

from __future__ import annotations

import pathlib
import re
import sys

REPO = pathlib.Path(__file__).resolve().parent.parent

WHITE = "#ffffff"
PAPER = "#f9f9f9"       # testimonials strip on tutoring.html

# (stylesheet, selector, background hex, threshold). A trailing "bg" flag
# means the checked colour is the block's own `background` (white text on
# it), not its `color`.
PAIRS: list[tuple] = [
    ("css/pages/marking.css", ".price", WHITE, 4.5),
    ("css/pages/marking.css", ".service-best-for", WHITE, 4.5),
    ("css/pages/tutoring.css", ".hero-trust", WHITE, 4.5),
    ("css/pages/tutoring.css", ".testimonial-card-mini .outcome", PAPER, 4.5),
    ("css/pages/tutoring.css", ".price", WHITE, 4.5),
    ("css/pages/tutoring.css", ".popular-badge", WHITE, 4.5, "bg"),
    ("css/pages/home.css", ".hero-trust", WHITE, 4.5),
    ("css/pages/home.css", ".review-role", WHITE, 4.5),
    ("css/pages/home.css", ".newsletter-privacy", WHITE, 4.5),
    ("css/pages/home.css", ".resource-badge", WHITE, 4.5, "bg"),
    # Meaningful icon: WCAG 1.4.11, 3:1.
    ("css/pages/home.css", ".action-card--free .action-icon", WHITE, 3.0),
    ("css/pages/about.css", ".about-hero-trust", WHITE, 4.5),
    ("css/pages/about.css", ".about-testimonial-card .outcome", WHITE, 4.5),
    ("css/pages/contact.css", ".response-time", WHITE, 4.5),
    ("css/pages/privacy.css", ".privacy-notice .privacy-meta", WHITE, 4.5),
    # 3em glyph: large, 3:1.
    ("css/pages/confirmation.css", ".confirmation-header .checkmark",
     WHITE, 3.0),
    ("css/main.css", ".credentials-list li:before", WHITE, 3.0),
    ("css/pages/past-paper-questions.css",
     ".past-paper-questions-page .ppq-badge-theme", WHITE, 4.5, "bg"),
    ("css/pages/past-papers-list.css", ".exam-board-tag", WHITE, 4.5, "bg"),
    ("css/pages/macro-application.css", ".section-placeholder", WHITE, 4.5),
    # revision-notes-textbook.css serves macro-application only since the
    # family consistency pass (2026-08-25, D62) moved the two diagram
    # galleries onto revision-notes-topic.css; the galleries' redesign kept
    # its own pairs below, and macro-application's revert (Eliot's call the
    # same day) kept these four textbook pairs live.
    ("css/pages/revision-notes-textbook.css",
     ".revision-notes-content .exam-tip strong", "#eef8f2", 4.5),
    # An h3 in the notes: 1.4em Merriweather bold >= 18.7px bold, so 3:1.
    ("css/pages/revision-notes-textbook.css",
     ".revision-notes-content .evaluation-point h3", "#fef4ea", 3.0),
    # The small-caps labels the topic-tail redesign already darkened - held
    # here against regression.
    ("css/pages/revision-notes-textbook.css",
     ".revision-notes-content .topic-contents__label", "#f8fafc", 4.5),
    ("css/pages/revision-notes-textbook.css",
     ".revision-notes-content .topic-related__label", WHITE, 4.5),
    # The galleries' own sheet, on the D61 tokens.
    ("css/pages/revision-notes-diagrams.css",
     ".revision-notes-content.micro-diagrams-page .diagram-card__meta",
     WHITE, 4.5),
    ("css/pages/revision-notes-diagrams.css",
     ".revision-notes-content.micro-diagrams-page .exam-note strong",
     "#f2faf5", 4.5),
    # The notes-redesign sheet (2026-08-25, D61), the 166 topic pages. The
    # tints are declared as hex tokens in the sheet precisely so these pairs
    # stay computable. The exam-tip and evaluation labels are the two pairs
    # the a11y pass left for this overhaul - white-on-#27ae60 at 2.9:1 and
    # white-on-#f57c00 at 2.7:1, both closed here for good.
    ("css/pages/revision-notes-topic.css",
     ".revision-notes-content .topic-contents__label", "#f8fafc", 4.5),
    ("css/pages/revision-notes-topic.css",
     ".revision-notes-content .exam-tip::before", "#f2faf5", 4.5),
    ("css/pages/revision-notes-topic.css",
     ".revision-notes-content .evaluation-point::before", "#fef8f2", 4.5),
    ("css/pages/revision-notes-topic.css",
     ".revision-notes-content .application::before", "#f4f5f8", 4.5),
    # The definition chip, inline on white and opening its card's tint.
    ("css/pages/revision-notes-topic.css",
     ".revision-notes-content .key-definition", WHITE, 4.5),
    ("css/pages/revision-notes-topic.css",
     ".revision-notes-content .key-definition", "#fdf6f8", 4.5),
    # The muted meta line under the h1.
    ("css/pages/revision-notes-topic.css",
     ".revision-notes-content .topic-meta", WHITE, 4.5),
    # The flow chain's end node: white text, so the checked colour is the
    # node's own background.
    ("css/pages/revision-notes-topic.css",
     ".revision-notes-content .flow-node--end", WHITE, 4.5, "bg"),
]

HEX = re.compile(r"^#(?:[0-9a-fA-F]{3}|[0-9a-fA-F]{6})$")
TOKEN = re.compile(r"--([\w-]+)\s*:\s*(#[0-9a-fA-F]{3,6})\s*[;}]")
COMMENT = re.compile(r"/\*.*?\*/", re.S)


def luminance(hexcolour: str) -> float:
    h = hexcolour.lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    channels = []
    for i in (0, 2, 4):
        c = int(h[i:i + 2], 16) / 255
        channels.append(c / 12.92 if c <= 0.04045
                        else ((c + 0.055) / 1.055) ** 2.4)
    r, g, b = channels
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def ratio(fg: str, bg: str) -> float:
    lighter, darker = sorted((luminance(fg), luminance(bg)), reverse=True)
    return (lighter + 0.05) / (darker + 0.05)


def declared(css: str, selector: str, prop: str, tokens: dict) -> str | None:
    """The first hex value `prop` is set to in a block for `selector`."""
    at = 0
    while True:
        at = css.find(selector, at)
        if at == -1:
            return None
        brace = css.find("{", at)
        if brace == -1:
            return None
        # the selector list this block belongs to must contain it exactly
        selectors = [s.strip() for s in css[css.rfind("}", 0, at) + 1:brace]
                     .split(",")]
        block = css[brace + 1:css.find("}", brace)]
        if selector in selectors:
            m = re.search(
                rf"(?:^|[;{{\s]){prop}\s*:\s*([^;}}]+)", block)
            if m:
                value = m.group(1).strip()
                var = re.match(r"var\(\s*--([\w-]+)\s*\)", value)
                if var:
                    value = tokens.get(var.group(1), "")
                first = value.split()[0] if value else ""
                if HEX.match(first):
                    return first.lower()
                return None  # declared, but not a plain hex - fail loudly
        at = brace + 1
    return None


def main() -> int:
    problems: list[str] = []
    cache: dict[str, tuple[str, dict]] = {}
    for entry in PAIRS:
        file, selector, bg, threshold = entry[:4]
        prop = "background" if len(entry) > 4 and entry[4] == "bg" else "color"
        if file not in cache:
            path = REPO / file
            if not path.is_file():
                problems.append(f"{file}: missing stylesheet")
                continue
            css = COMMENT.sub("", path.read_text(encoding="utf-8"))
            cache[file] = (css, dict(TOKEN.findall(css)))
        css, tokens = cache[file]
        value = declared(css, selector, prop, tokens)
        if value is None:
            problems.append(
                f"{file}: no hex `{prop}` found for `{selector}` - "
                "renamed or restructured? Update PAIRS in the same commit.")
            continue
        r = ratio(value, bg)
        line = (f"{file}: {selector} {prop} {value} on {bg} = {r:.2f}:1 "
                f"(needs {threshold}:1)")
        if r < threshold:
            problems.append(line)
        else:
            print(f"  ok  {line}")

    print(f"{len(PAIRS)} declared pairs checked")
    if problems:
        print(f"\n{len(problems)} problem(s):")
        for p in problems:
            print(f"  {p}")
        return 1
    print("every declared pair meets its threshold")
    return 0


if __name__ == "__main__":
    sys.exit(main())

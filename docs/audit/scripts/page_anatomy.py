"""Phase 6 — page anatomy: boilerplate volume, head/body skeletons, drift.

READ-ONLY. Opens site files for reading only; writes nothing outside stdout.

Three questions, in order:

  1. How many bytes of each page are identical to every other page in its
     family?  ("boilerplate volume")
  2. How many *distinct* structural shapes exist inside a family, once the
     economics prose is stripped out?  ("structural drift")
  3. Where do those shapes diverge?

Skeletons deliberately keep tag + id + class and throw away all text, all
attribute values that carry content (title, description, href targets in
prose), and all whitespace.  Two pages with the same skeleton differ only in
words; two pages with different skeletons differ in markup, which is what a
template layer would have to reconcile.
"""

import re
import sys
from collections import Counter, defaultdict
from html.parser import HTMLParser

sys.path.insert(0, __file__.rsplit("/", 1)[0])
import lib  # noqa: E402


# ---------------------------------------------------------------- families

def family_of(path):
    """The page family, as Phase 0 defined them in 00-INVENTORY.md §4."""
    if path.startswith("revision-notes/glossary/"):
        return "glossary"
    if path.startswith("revision-notes/"):
        rest = path[len("revision-notes/"):]
        if rest.endswith("/index.html") and rest.count("/") == 1:
            return "notes-hub"
        if "/" not in rest:
            return "notes-other"
        if rest.startswith("macro-application/"):
            return "notes-other"
        return "notes-topic"
    if path.startswith("practice-questions/"):
        return "mcq-hub" if path.endswith("/index.html") else "mcq-topic"
    if path.startswith("past-paper-questions/"):
        return "ppq"
    if path.startswith("past-papers/"):
        return "past-papers"
    if path.startswith("flashcards/"):
        return "flashcards"
    return "root"


GENERATED = {"glossary", "mcq-hub", "mcq-topic", "ppq", "flashcards"}


# ---------------------------------------------------------------- skeleton

VOID = {"meta", "link", "br", "hr", "img", "input", "source", "col", "area"}


class Skeleton(HTMLParser):
    """Token stream for one document, split at </head>."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.head = []
        self.body_open = []          # (depth, token) for every start tag
        self.in_head = False
        self.in_body = False
        self.depth = 0
        self.headings = []
        self.imgs = []               # (has_alt, alt_is_empty, has_dims, has_loading)
        self.anchor_text = []
        self._a_buf = None
        self.tables = 0
        self.tables_with_th = 0
        self._table_has_th = False
        self.landmarks = Counter()
        self.ld_types = []
        self._in_ld = False
        self._ld_buf = ""
        self._in_title = False
        self.title = ""
        self.inline_style_attrs = 0
        self.style_blocks = 0
        self.buttons_aria = [0, 0]   # [buttons, buttons with aria-expanded]

    # -- helpers
    @staticmethod
    def _tok(tag, attrs):
        d = dict(attrs)
        bits = [tag]
        if d.get("id"):
            bits.append("#" + d["id"])
        if d.get("class"):
            bits.append("." + ".".join(sorted(d["class"].split())))
        if tag == "meta":
            key = d.get("name") or d.get("property") or ("charset" if "charset" in d else "?")
            bits.append("[" + key + "]")
        elif tag == "link":
            bits.append("[" + (d.get("rel") or "?") + "]")
            if d.get("rel") == "stylesheet":
                bits.append("=" + (d.get("href") or ""))
        elif tag == "script":
            if d.get("src"):
                bits.append("=" + d["src"] + (" defer" if "defer" in d else ""))
            elif d.get("type") == "application/ld+json":
                bits.append("[ld+json]")
            else:
                bits.append("[inline]")
        return "".join(bits)

    def handle_starttag(self, tag, attrs):
        d = dict(attrs)
        if tag == "head":
            self.in_head = True
            return
        if tag == "body":
            self.in_body, self.in_head = True, False
            self.depth = 0
            return

        if self.in_head:
            self.head.append(self._tok(tag, attrs))
            if tag == "script" and d.get("type") == "application/ld+json":
                self._in_ld, self._ld_buf = True, ""
            if tag == "title":
                self._in_title = True
            return

        if not self.in_body:
            return

        self.body_open.append((self.depth, self._tok(tag, attrs)))
        if "style" in d:
            self.inline_style_attrs += 1
        if tag == "style":
            self.style_blocks += 1
        if tag in ("h1", "h2", "h3", "h4", "h5", "h6"):
            self.headings.append(int(tag[1]))
        if tag in ("main", "nav", "header", "footer", "aside", "section", "article"):
            self.landmarks[tag] += 1
        if tag == "img":
            self.imgs.append((
                "alt" in d,
                d.get("alt", "x").strip() == "",
                "width" in d and "height" in d,
                "loading" in d,
            ))
        if tag == "a":
            self._a_buf = ""
        if tag == "table":
            self.tables += 1
            self._table_has_th = False
        if tag == "th":
            self._table_has_th = True
        if tag == "button":
            self.buttons_aria[0] += 1
            if "aria-expanded" in d:
                self.buttons_aria[1] += 1
        if tag not in VOID:
            self.depth += 1

    def handle_endtag(self, tag):
        if tag == "head":
            self.in_head = False
            return
        if tag == "title":
            self._in_title = False
        if tag == "script" and self._in_ld:
            self._in_ld = False
            self.ld_types = sorted(set(re.findall(r'"@type"\s*:\s*"([^"]+)"', self._ld_buf)))
        if not self.in_body:
            return
        if tag == "a" and self._a_buf is not None:
            self.anchor_text.append(" ".join(self._a_buf.split()))
            self._a_buf = None
        if tag == "table" and self._table_has_th:
            self.tables_with_th += 1
        if tag not in VOID:
            self.depth = max(0, self.depth - 1)

    def handle_data(self, data):
        if self._in_ld:
            self._ld_buf += data
        if self._in_title:
            self.title += data
        if self._a_buf is not None:
            self._a_buf += data


def parse(path):
    s = Skeleton()
    s.feed(lib.read(path))
    return s


def chrome(s, maxdepth):
    return "|".join(t for d, t in s.body_open if d <= maxdepth)


def spine(s, needle):
    """Direct children of the first element whose token contains `needle`.

    This is the page's content spine: the ordered list of top-level blocks a
    template would have to emit. Nested prose is invisible to it, which is the
    point - it measures shape, not words.
    """
    start = None
    for i, (d, t) in enumerate(s.body_open):
        if needle in t:
            start, base = i, d
            break
    if start is None:
        return None
    out = []
    for d, t in s.body_open[start + 1:]:
        if d <= base:
            break
        if d == base + 1:
            out.append(t)
    return out


# ---------------------------------------------- boilerplate blocks, measured

# Each block is a regex matched against the raw source. These are the literal,
# byte-identical repeats - not "similar", identical modulo whitespace.
BLOCKS = {
    "gtag script pair": re.compile(
        r"<!-- Google tag \(gtag\.js\) -->.*?gtag\(\"config\", \"G-YVCNRW4QH6\"\);\s*</script>",
        re.S),
    "charset + viewport": re.compile(
        r'<meta charset="utf-8" />\s*<meta name="viewport"[^>]*/>', re.S),
    "og:type/site_name/locale": re.compile(
        r'<meta property="og:type"[^>]*/>\s*<meta property="og:site_name"[^>]*/>'
        r'\s*<meta property="og:locale"[^>]*/>', re.S),
    "og:image set (5 tags)": re.compile(
        r'<meta\s+property="og:image"\s+content="https://economicsacademy\.co\.uk/og-image\.png\?v=1"'
        r'\s*/>.*?og:image:alt"\s+content="Economics Academy logo"\s*/>', re.S),
    "twitter:card + twitter:image": re.compile(
        r'<meta name="twitter:card" content="summary_large_image" />', re.S),
    "favicon / manifest trio": re.compile(
        r'<link rel="icon".*?<link rel="manifest" href="/site\.webmanifest" />', re.S),
    "@import-hoist comment": re.compile(r"<!-- Linked here rather than @imported.*?-->", re.S),
    "preconnect pair": re.compile(
        r'<link rel="preconnect" href="https://fonts\.googleapis\.com" />\s*'
        r'<link rel="preconnect" href="https://fonts\.gstatic\.com" crossorigin />', re.S),
    "fontawesome + fonts + main.css": re.compile(
        r'<link rel="stylesheet" href="/css/fontawesome-all\.min\.css" />\s*<link\s+'
        r'rel="stylesheet"\s+href="https://fonts\.googleapis\.com/css2\?family=Merriweather'
        r'.*?display=swap"\s*/>\s*<link rel="stylesheet" href="/css/main\.css" />', re.S),
    "seven-script tail": re.compile(
        r'<script src="/js/jquery\.min\.js"></script>.*?<script src="/js/main\.js"></script>', re.S),
    "body wrapper + placeholders": re.compile(
        r'<body class="is-preload">\s*<div id="page-wrapper">\s*(?:<!--[^>]*-->\s*)?'
        r'<div id="header-placeholder"></div>', re.S),
    "footer placeholder + close": re.compile(
        r'(?:<!-- Footer -->\s*)?<div id="footer-placeholder"></div>\s*</div>', re.S),
}


def main():
    pages = lib.pages()
    fam = defaultdict(list)
    for p in pages:
        fam[family_of(p)].append(p)

    print(f"pages analysed: {len(pages)}\n")

    # ---------------------------------------------------------- 1. boilerplate
    print("=== 1. Byte-identical boilerplate, per block, across all pages ===")
    print(f"{'block':34} {'pages':>6} {'bytes/pg':>9} {'total KB':>9}")
    grand = 0
    for name, rx in BLOCKS.items():
        hits, total = 0, 0
        for p in pages:
            m = rx.search(lib.read(p))
            if m:
                hits += 1
                total += len(m.group(0))
        grand += total
        per = total // hits if hits else 0
        print(f"{name:34} {hits:6} {per:9} {total/1024:9.1f}")
    print(f"{'TOTAL':34} {'':6} {'':9} {grand/1024:9.1f}")
    total_bytes = sum(len(lib.read(p)) for p in pages)
    print(f"\nall published page bytes: {total_bytes/1024/1024:.2f} MB"
          f"  ->  identical boilerplate is {100*grand/total_bytes:.1f}% of it\n")

    # ------------------------------------------------- 2. per-family skeletons
    print("=== 2. Structural drift: distinct skeletons per family ===")
    print(f"{'family':14} {'pages':>5} {'gen':>4} {'head':>5} {'chrome':>7} {'tail':>5} {'css':>4}")
    detail = {}
    for f in sorted(fam):
        ps = fam[f]
        heads, chromes, tails, csss = Counter(), Counter(), Counter(), Counter()
        parsed = {}
        for p in ps:
            s = parse(p)
            parsed[p] = s
            heads["|".join(s.head)] += 1
            chromes[chrome(s, 3)] += 1
            tail = "|".join(t for d, t in s.body_open
                            if t.startswith("script=") and d <= 2)
            tails[tail] += 1
            csss["|".join(t for t in s.head if t.startswith("link[stylesheet]"))] += 1
        detail[f] = (parsed, heads, chromes, tails, csss)
        print(f"{f:14} {len(ps):5} {'Y' if f in GENERATED else '.':>4} "
              f"{len(heads):5} {len(chromes):7} {len(tails):5} {len(csss):4}")

    # -------------------------------------------- 3. where notes-topic diverges
    print("\n=== 3. notes-topic: the 166 pages, broken down ===")
    parsed, heads, chromes, tails, csss = detail["notes-topic"]

    print("\n-- body chrome variants (depth<=3) --")
    for i, (sk, n) in enumerate(chromes.most_common(), 1):
        ex = next(p for p in fam["notes-topic"]
                  if "|".join(t for d, t in parsed[p].body_open if d <= 3) == sk)
        print(f"  [{i}] {n:4} pages   e.g. {ex}")
    if len(chromes) > 1:
        variants = list(chromes)
        base = variants[0].split("|")
        for i, v in enumerate(variants[1:], 2):
            cur = v.split("|")
            print(f"\n  variant [{i}] vs [1]:")
            only_a = [t for t in base if t not in cur]
            only_b = [t for t in cur if t not in base]
            for t in only_a[:12]:
                print(f"    - {t}")
            for t in only_b[:12]:
                print(f"    + {t}")

    print("\n-- body chrome at depth<=6 --")
    deep = Counter(chrome(parsed[p], 6) for p in fam["notes-topic"])
    print(f"  {len(deep)} distinct variants across {len(fam['notes-topic'])} pages")
    for i, (sk, n) in enumerate(deep.most_common(8), 1):
        ex = next(p for p in fam["notes-topic"] if chrome(parsed[p], 6) == sk)
        print(f"  [{i}] {n:4} pages   e.g. {ex}")

    print("\n-- content spine: direct children of div.notes-container --")
    spines = Counter()
    missing = []
    for p in fam["notes-topic"]:
        sp = spine(parsed[p], "notes-container")
        if sp is None:
            missing.append(p)
        else:
            spines["|".join(sp)] += 1
    print(f"  {len(spines)} distinct spines; {len(missing)} pages have no .notes-container")
    for p in missing[:5]:
        print(f"      no container: {p}")
    for i, (sk, n) in enumerate(spines.most_common(12), 1):
        print(f"  [{i:2}] {n:4}  {sk}")
    if len(spines) > 12:
        rest = sum(n for _, n in spines.most_common()[12:])
        print(f"  [ +{len(spines)-12} more variants covering {rest} pages ]")

    print("\n-- spine element vocabulary: how many of the 166 carry each block --")
    vocab = Counter()
    for p in fam["notes-topic"]:
        sp = spine(parsed[p], "notes-container") or []
        for t in set(sp):
            vocab[t] += 1
    for t, n in vocab.most_common(25):
        print(f"  {n:4}  {t}")

    print("\n-- component-library census (CLAUDE.md 'max two per page') --")
    COMPONENTS = ["spec-alert", "worked-example", "exam-tip", "concept-table",
                  "calculation-table", "key-definition", "formula-box",
                  "flow-chain", "diagram-figure", "notes-cta",
                  "notes-questions-link", "table-container"]
    comp = Counter()
    over = 0
    for p in fam["notes-topic"]:
        src = lib.read(p)
        n_here = 0
        for c in COMPONENTS:
            k = src.count(f'class="{c}')
            if k:
                comp[c] += 1
            if c in ("worked-example", "exam-tip", "concept-table",
                     "calculation-table", "formula-box", "flow-chain"):
                n_here += k
        if n_here > 2:
            over += 1
    for c in COMPONENTS:
        print(f"  {comp[c]:4}/166  {c}")
    print(f"  pages exceeding the 'max two components' rule: {over}")

    print("\n-- head skeleton variants --")
    for i, (sk, n) in enumerate(heads.most_common(), 1):
        ex = next(p for p in fam["notes-topic"] if "|".join(parsed[p].head) == sk)
        print(f"  [{i}] {n:4} pages   e.g. {ex}")
    if len(heads) > 1:
        vs = list(heads)
        base = vs[0].split("|")
        for i, v in enumerate(vs[1:], 2):
            cur = v.split("|")
            only_a = [t for t in base if t not in cur]
            only_b = [t for t in cur if t not in base]
            print(f"  [{i}] differs by: -{only_a[:6]} +{only_b[:6]}")

    print("\n-- stylesheet sets --")
    for sk, n in csss.most_common():
        print(f"  {n:4}  {sk.replace('link[stylesheet]=', '')}")

    print("\n-- script tails --")
    for sk, n in tails.most_common():
        print(f"  {n:4}  {sk.replace('script=', '')}")

    # ------------------------------------------------ 4. headings & a11y basics
    print("\n=== 4. Heading hierarchy and accessibility basics, per family ===")
    print(f"{'family':14} {'pg':>4} {'h1!=1':>6} {'skips':>6} {'img':>5} "
          f"{'noalt':>6} {'nodim':>6} {'nolazy':>7} {'main':>5} {'style=':>7}")
    a11y_detail = defaultdict(list)
    for f in sorted(fam):
        ps = fam[f]
        bad_h1 = skips = imgs = noalt = nodim = nolazy = no_main = inline = 0
        for p in ps:
            s = detail[f][0][p] if f in detail else parse(p)
            h1 = s.headings.count(1)
            if h1 != 1:
                bad_h1 += 1
                a11y_detail[f + "/h1"].append(f"{p} ({h1})")
            prev = 0
            for h in s.headings:
                if prev and h > prev + 1:
                    skips += 1
                    a11y_detail[f + "/skip"].append(f"{p} h{prev}->h{h}")
                    break
                prev = h
            imgs += len(s.imgs)
            noalt += sum(1 for a, _, _, _ in s.imgs if not a)
            nodim += sum(1 for _, _, d, _ in s.imgs if not d)
            nolazy += sum(1 for _, _, _, l in s.imgs if not l)
            if not s.landmarks.get("main"):
                no_main += 1
            inline += 1 if s.inline_style_attrs else 0
        print(f"{f:14} {len(ps):4} {bad_h1:6} {skips:6} {imgs:5} {noalt:6} "
              f"{nodim:6} {nolazy:7} {no_main:5} {inline:7}")

    print("\n-- first 12 heading problems --")
    shown = 0
    for k in sorted(a11y_detail):
        for v in a11y_detail[k][:4]:
            print(f"  {k:22} {v}")
            shown += 1
            if shown >= 12:
                break
        if shown >= 12:
            break

    # ----------------------------------------------------- 5. cost of a change
    print("\n=== 5. Cost of one global change today ===")
    counts = {
        "add a nav item": sum(1 for p in ["templates/header.html"]),
        "add a <head> tag sitewide": len(pages),
        "  ...of which need a generator edit": sum(
            1 for p in pages if family_of(p) in GENERATED),
        "  ...of which are hand-edited": sum(
            1 for p in pages if family_of(p) not in GENERATED),
        "change notes page layout": len(fam["notes-topic"]),
        "change the script tail": len(pages),
        "add a breadcrumb level": sum(
            1 for p in pages if 'class="breadcrumb' in lib.read(p)),
    }
    for k, v in counts.items():
        print(f"  {k:44} {v:5} files")


if __name__ == "__main__":
    main()

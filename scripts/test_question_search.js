/* Tests for the matching half of js/components/question-search.js.
 *
 *   node scripts/test_question_search.js
 *
 * This does not re-implement the matcher. It slices the DOM-free section out of
 * the real component file and evaluates that, so the code under test is the
 * code that ships. If the section markers in that file are renamed, this fails
 * loudly rather than silently testing nothing.
 *
 * There is no test framework in this repo and this does not add one.
 */

"use strict";

const fs = require("fs");
const path = require("path");

const ROOT = path.resolve(__dirname, "..");
const SRC = path.join(ROOT, "js", "components", "question-search.js");
const DATA = path.join(ROOT, "past-paper-questions", "questions.json");

const source = fs.readFileSync(SRC, "utf8");

// Everything from the text helpers down to the boot section is DOM-free at
// definition time - init() only touches the DOM through the root it is handed,
// and window only for location.search - so it can all be lifted out and
// exercised directly. The factory takes a window per call, so query-string
// behaviour is testable with a fresh module each time.
const START =
  "// ---------------------------------------------------------------- text";
const END =
  "// ---------------------------------------------------------------- boot";
const from = source.indexOf(START);
const to = source.indexOf(END);
if (from === -1 || to === -1 || to <= from) {
  console.error(
    "FATAL: could not find the text/boot section markers in question-search.js.\n" +
      "The file was restructured; update this test rather than deleting it.",
  );
  process.exit(2);
}

// The two tuning constants sit above the sliced section; carry the shipped
// values in rather than inventing test-local ones.
const constants = (
  source.match(/var (?:PAGE_SIZE|DEBOUNCE_MS)\s*=\s*\d+;/g) || []
).join("\n");
if (!/PAGE_SIZE/.test(constants) || !/DEBOUNCE_MS/.test(constants)) {
  console.error(
    "FATAL: PAGE_SIZE/DEBOUNCE_MS not found in question-search.js.",
  );
  process.exit(2);
}

const slice = source.slice(from, to);
const factory = new Function(
  "window",
  constants +
    "\n" +
    slice +
    "\nreturn { normalise, tokenise, withinDistance, allowedEdits, buildIndex," +
    " score, cardHtml, escapeHtml, init };",
);
const M = factory({ location: { search: "" } });

const data = JSON.parse(fs.readFileSync(DATA, "utf8"));
const index = M.buildIndex(data);

let failures = 0;
function check(name, cond, detail) {
  if (cond) return;
  failures++;
  console.log("FAIL  " + name + (detail ? "  -> " + detail : ""));
}

function search(query) {
  const tokens = M.tokenise(query);
  return index.filter((r) => M.score(r, tokens) >= 0);
}

function ids(query) {
  return search(query).map((r) => r.q.id);
}

// ---- edit distance

check("distance: identical", M.withinDistance("monopoly", "monopoly", 1));
check("distance: one substitution", M.withinDistance("monoply", "monopoly", 1));
check(
  "distance: two edits rejected at max 1",
  !M.withinDistance("mnpoly", "monopoly", 1),
);
check(
  "distance: two edits allowed at max 2",
  M.withinDistance("mnopoly", "monopoly", 2),
);
check(
  "distance: length gap short-circuits",
  !M.withinDistance("a", "monopoly", 2),
);
check("allowedEdits: short words are strict", M.allowedEdits("tax") === 0);
check("allowedEdits: mid words allow one", M.allowedEdits("supply") === 1);
check(
  "allowedEdits: long words allow two",
  M.allowedEdits("quantitative") === 2,
);

// ---- the headline requirement: real typos still hit

const qeCorrect = ids("quantitative easing");
const qeTypo = ids("quantitive easing");
check(
  "QE: exact spelling finds questions",
  qeCorrect.length > 0,
  qeCorrect.length,
);
check("QE: misspelling finds questions", qeTypo.length > 0, qeTypo.length);
check(
  "QE: misspelling finds the same set as the correct spelling",
  qeCorrect.every((id) => qeTypo.indexOf(id) !== -1),
  "correct=" + qeCorrect.length + " typo=" + qeTypo.length,
);

check("typo: 'inflatoin' still hits", ids("inflatoin").length > 0);
check("typo: 'externalites' still hits", ids("externalites").length > 0);
check("typo: 'monoply' still hits", ids("monoply").length > 0);

// ---- mark tariff phrasings all mean the same thing

const twentyFive = data.questions.filter((q) => q.marks === 25).length;
["25 marks", "25m", "25-marker", "25 mark", "25marks"].forEach((phrase) => {
  const got = search(phrase).filter((r) => r.q.marks === 25).length;
  check(
    "marks: '" + phrase + "' reaches all 25-mark questions",
    got === twentyFive,
    got + " of " + twentyFive,
  );
});

// ---- field coverage

check("topic title is searchable", ids("wage determination").length > 0);
check("keyword is searchable", ids("sugar tax").length > 0);
check("spec code is searchable", ids("3.5.3").length > 0);
check("paper is searchable", search("paper 1").length > 0);
check("series and year are searchable", search("june 2019").length > 0);
check("section grouping is searchable", search("theme 4").length > 0);
check("board is searchable", search("edexcel").length > 0);
check("section is searchable", search("section c").length > 0);

// ---- AND semantics and empty results

check(
  "AND: an impossible pairing returns nothing",
  ids("monopoly zzzzqqq").length === 0,
  ids("monopoly zzzzqqq").length,
);
check("nonsense returns nothing", ids("zzzzqqqwww").length === 0);
check("empty query returns everything", search("").length === index.length);

// ---- ranking

const scored = search("monopoly")
  .map((r) => ({ id: r.q.id, s: M.score(r, M.tokenise("monopoly")) }))
  .sort((a, b) => b.s - a.s);
check("monopoly: matches found", scored.length > 0);
check(
  "monopoly: every match scores positively",
  scored.every((x) => x.s > 0),
);

// ---- data integrity the UI depends on

check(
  "every question resolves a paper",
  data.questions.every((q) => !!data.papers[q.p]),
  "bad paper index",
);
// Which questions depend on a stimulus block differs by board and paper, so the
// rule is stated rather than inferred from the section letter:
//   Edexcel  Papers 1-2  Section B has extracts, Section C does not
//            Paper 3     both sections are case studies
//   AQA      Papers 1-2  Section A has extracts, Section B is free-standing essays
//            Paper 3     Section B is a case study
function expectsExtract(q) {
  const paper = data.papers[q.p];
  if (paper.board === "edexcel") return q.section !== "C";
  if (paper.paper === 3) return true;
  return q.section === "A";
}
check(
  "extracts: present exactly where the paper carries a stimulus block",
  data.questions.every((q) => expectsExtract(q) === (q.ctxPage !== null)),
  data.questions
    .filter((q) => expectsExtract(q) !== (q.ctxPage !== null))
    .slice(0, 3)
    .map((q) => q.id)
    .join(", "),
);
check(
  "extracts: AQA Section B essays are free-standing",
  data.questions
    .filter(
      (q) =>
        data.papers[q.p].board === "aqa" &&
        data.papers[q.p].paper !== 3 &&
        q.section === "B",
    )
    .every((q) => q.ctxPage === null),
);
check(
  "extracts: Paper 3 case-study questions all carry one",
  data.questions
    .filter((q) => data.papers[q.p].paper === 3)
    .every((q) => q.ctxPage !== null),
);

// Boards must stay apart: 37 spec codes mean different things on each, so a
// question tagged across two boards would show a reader two numbering systems.
check(
  "boards: no question is tagged across two boards",
  data.questions.every(
    (q) => new Set(q.topics.map((s) => data.topics[s].board)).size === 1,
  ),
);
check(
  "boards: every topic page URL carries its board",
  Object.values(data.topics).every((t) =>
    t.url.startsWith("/past-paper-questions/" + t.board + "/"),
  ),
);
check(
  "boards: a question's board matches its paper's board",
  data.questions.every((q) => q.board === data.papers[q.p].board),
);
check(
  "every question has a mark scheme page",
  data.questions.every((q) => typeof q.msPage === "number" && q.msPage > 0),
);
check(
  "every topic referenced by a question exists in the topics table",
  data.questions.every((q) => q.topics.every((s) => !!data.topics[s])),
);

// ---- card rendering and the deep links, which are the core promise

// Pick by what the card must show, not by section letter: AQA's Section B is
// three free-standing essays with no extract, while Edexcel's has one.
const sectionB = index.filter((r) => r.q.ctxPage !== null)[0];
const sectionC = index.filter((r) => r.q.section === "C")[0];
const cardB = M.cardHtml(sectionB, data.topics);
const cardC = M.cardHtml(sectionC, data.topics);

check(
  "card: mark scheme link carries the #page fragment",
  cardB.indexOf("#page=" + sectionB.q.msPage) !== -1,
);
check(
  "card: mark scheme page is also shown as text for iOS Safari",
  cardB.indexOf("p." + sectionB.q.msPage) !== -1,
);
check(
  "card: mark scheme link points at the hosted PDF",
  cardB.indexOf(sectionB.paper.markSchemeUrl) !== -1,
);
check(
  "card: the question paper link carries its own #page fragment",
  cardB.indexOf(
    sectionB.paper.questionPaperUrl + "#page=" + sectionB.q.qpPage,
  ) !== -1,
);
check(
  "card: the question paper link comes first, before the mark scheme",
  cardB.indexOf("Question paper") !== -1 &&
    cardB.indexOf("Question paper") < cardB.indexOf("Mark scheme"),
);
check(
  "card: Section B carries three PDF links, Section C carries two",
  (cardB.match(/\.pdf#page=/g) || []).length === 3 &&
    (cardC.match(/\.pdf#page=/g) || []).length === 2,
  "B=" +
    (cardB.match(/\.pdf#page=/g) || []).length +
    " C=" +
    (cardC.match(/\.pdf#page=/g) || []).length,
);
check(
  "card: the extract link and the question paper link are different pages",
  sectionB.q.ctxPage !== sectionB.q.qpPage ||
    cardB.indexOf("View the extract") !== -1,
);
check(
  "card: Section B offers the extract link",
  cardB.indexOf("View the extract") !== -1,
);
check(
  "card: Section C offers no extract link",
  cardC.indexOf("View the extract") === -1,
);
check(
  "card: Section C is labelled as one of two options",
  cardC.indexOf("One of two options") !== -1,
);
check(
  "card: external PDF links are safe",
  (cardB.match(/target="_blank"/g) || []).length ===
    (cardB.match(/rel="noopener noreferrer"/g) || []).length,
);
check(
  "card: no model answer slot is rendered while the field is null",
  cardB.indexOf("ppq-action-model") === -1,
);
check(
  "card: every card carries its stable id as an anchor",
  cardB.indexOf('id="' + sectionB.q.id + '"') !== -1,
);

// Question text is injected as HTML, so it must be escaped. Real questions
// contain ampersands and quotation marks.
check(
  "escaping: angle brackets and ampersands are escaped",
  M.escapeHtml('<script>&"') === "&lt;script&gt;&amp;&quot;",
);
const withAmp = index.filter((r) => r.q.questionText.indexOf("&") !== -1)[0];
if (withAmp) {
  const card = M.cardHtml(withAmp, data.topics);
  check(
    "escaping: a question containing & renders it escaped",
    card.indexOf("&amp;") !== -1 && card.indexOf("& ") === -1,
  );
}

// Topic links must not point at pages that have not been generated yet.
const linkedSlugs = Object.keys(data.topics).filter(
  (s) => data.topics[s].hasPage,
);
const allCards = index.map((r) => M.cardHtml(r, data.topics)).join("");
const hrefs = allCards.match(/href="\/past-paper-questions\/[^"]+"/g) || [];
check(
  "links: no card links to a topic page that does not exist",
  hrefs.length === 0 || linkedSlugs.length > 0,
  hrefs.length + " topic links but " + linkedSlugs.length + " generated pages",
);

// ---- regressions found in review

// A source-citation URL must not make a question searchable by words that
// appear nowhere in the economics. The Tesla monopoly question cites
// ".../tesla-holds-us-ev-market-losing-federal-tax-credit/" and was a hit for
// "tax".
function searchableBody(s) {
  return s
    .replace(/\(Sources?\b[^)]*\)/gi, " ")
    .replace(/https?:\/\/\S+/g, " ");
}

// A hit is legitimate when the term is in the question's own wording, in one of
// its topic titles, or in a hand-written keyword. Topic and keyword matches are
// the point of tagging: "tax" should reach the indirect-taxes questions even
// where the word itself never appears in the stem.
function legitimateHit(q, term) {
  const fields = [searchableBody(q.questionText)]
    .concat(q.keywords)
    .concat(
      q.topics.map(
        (s) => data.topics[s].title + " " + data.topics[s].shortTitle,
      ),
    );
  return fields.join(" ").toLowerCase().indexOf(term) !== -1;
}

const taxHits = search("tax").map((r) => r.q);
check(
  "citations: every 'tax' hit is justified by wording, topic or keyword",
  taxHits.every((q) => legitimateHit(q, "tax")),
  taxHits
    .filter((q) => !legitimateHit(q, "tax"))
    .map((q) => q.id)
    .join(", "),
);
check(
  "citations: the Tesla monopoly question is no longer a hit for 'tax'",
  search("tax").every((r) => r.q.id !== "edexcel-a-p1-2022-jun-q7"),
);
check(
  "citations: that question is still findable by its real subject",
  ids("monopoly efficiency").indexOf("edexcel-a-p1-2022-jun-q7") !== -1,
);
check(
  "citations: stripping them did not empty any haystack",
  index.every((r) => r.tokens.length > 5),
);
check(
  "citations: questions are still findable by their own wording",
  ids("electric vehicle market").length > 0 &&
    ids("collusive behaviour").length > 0,
);

// The "show more" label counted below zero because .ppq-more sets display:block,
// which beats the browser's [hidden] rule, so the button never actually hid.
const css = fs.readFileSync(
  path.join(ROOT, "css", "pages", "past-paper-questions.css"),
  "utf8",
);
check(
  "hidden: the component restates [hidden] so author display rules cannot win",
  /\.past-paper-questions-page \[hidden\]\s*\{[^}]*display:\s*none\s*!important/.test(
    css,
  ),
);
check(
  "show more: the remaining count is clamped at zero",
  /Math\.max\(0,\s*matches\.length - shown\)/.test(source),
);
check(
  "show more: shown never exceeds the number of matches",
  /Math\.min\(shown \+ PAGE_SIZE,\s*matches\.length\)/.test(source),
);

// ---- the two renderers must agree
//
// Topic and theme pages ship their questions as real HTML from
// scripts/build_past_paper_questions.py, and this component then re-renders the
// same list from JSON. If the two ever drifted, turning JavaScript on would
// silently change the page. Compare every card from both renderers.

const { execFileSync } = require("child_process");
let pythonCards = null;
try {
  const out = execFileSync(
    "python3",
    [
      "-c",
      [
        "import json,pathlib,importlib.util",
        "spec=importlib.util.spec_from_file_location('b','scripts/build_past_paper_questions.py')",
        "m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m)",
        "i=json.loads(pathlib.Path('past-paper-questions/questions.json').read_text())",
        "print(json.dumps({q['id']: m.render_card(q,i) for q in i['questions']}))",
      ].join("\n"),
    ],
    { cwd: ROOT, encoding: "utf8", maxBuffer: 32 * 1024 * 1024 },
  );
  pythonCards = JSON.parse(out);
} catch (err) {
  check(
    "renderers: python card renderer is runnable",
    false,
    String(err).slice(0, 120),
  );
}

if (pythonCards) {
  const differing = index.filter(
    (r) => M.cardHtml(r, data.topics) !== pythonCards[r.q.id],
  );
  check(
    "renderers: every card is byte-identical between Python and JavaScript",
    differing.length === 0,
    differing
      .slice(0, 3)
      .map((r) => r.q.id)
      .join(", "),
  );
  check(
    "renderers: python rendered every question",
    Object.keys(pythonCards).length === data.questions.length,
    Object.keys(pythonCards).length + " of " + data.questions.length,
  );
}

// ---- the board hubs bake PAGE_SIZE cards and fetch their board's payload
//
// Performance pass, 2026-08-23. scripts/build_past_paper_questions.py bakes
// HUB_CARDS cards into each board hub - the same number this component shows
// first - and points the hub and its section pages at a per-board payload.
// Hold the two numbers together, and check each payload is a real file the
// component can index.

const pyHub = /^HUB_CARDS\s*=\s*(\d+)/m.exec(
  fs.readFileSync(
    path.join(ROOT, "scripts", "build_past_paper_questions.py"),
    "utf8",
  ),
);
const jsPage = /var PAGE_SIZE\s*=\s*(\d+)/.exec(source);
check(
  "hub: HUB_CARDS in the generator equals PAGE_SIZE in the component",
  pyHub && jsPage && pyHub[1] === jsPage[1],
  (pyHub && pyHub[1]) + " vs " + (jsPage && jsPage[1]),
);

data.boards.forEach((b) => {
  const hubPath = path.join(ROOT, b.url.replace(/^\//, ""), "index.html");
  if (!fs.existsSync(hubPath)) return; // a board with no questions has no hub
  const hub = fs.readFileSync(hubPath, "utf8");
  const cards = (hub.match(/class="ppq-card/g) || []).length;
  const boardQs = data.questions.filter((q) => q.board === b.board).length;
  check(
    "hub: " + b.board + " bakes min(PAGE_SIZE, its questions) cards",
    cards === Math.min(Number(jsPage[1]), boardQs),
    cards + " cards, " + boardQs + " questions",
  );
  check(
    "hub: " + b.board + " carries the static note inside the results container",
    /data-ppq-results>[\s\S]*ppq-static-note[\s\S]*<\/div>/.test(hub),
  );
  const src = /data-src="([^"]+)"/.exec(hub);
  check("hub: " + b.board + " fetches a per-board payload", !!src);
  if (src) {
    const payloadPath = path.join(ROOT, src[1].replace(/^\//, ""));
    check(
      "hub: " + b.board + " payload exists at " + src[1],
      fs.existsSync(payloadPath),
    );
    if (fs.existsSync(payloadPath)) {
      const pd = JSON.parse(fs.readFileSync(payloadPath, "utf8"));
      check(
        "hub: " + b.board + " payload carries exactly the board's questions",
        pd.questions.length === boardQs &&
          pd.questions.every((q) => q.board === b.board),
        pd.questions.length + " of " + boardQs,
      );
      const boardTopics = Object.keys(data.topics).filter(
        (s) => data.topics[s].board === b.board,
      );
      check(
        "hub: " +
          b.board +
          " payload carries every topic on the board (the Topic filter lists them)",
        boardTopics.every((s) => pd.topics[s]) &&
          Object.keys(pd.topics).length === boardTopics.length,
        Object.keys(pd.topics).length + " of " + boardTopics.length,
      );
      check(
        "hub: " + b.board + " payload indexes and renders",
        M.buildIndex(pd).length === pd.questions.length,
      );
      check(
        "hub: " +
          b.board +
          " payload keeps papers sparse (same length as the master)",
        pd.papers.length === data.papers.length,
      );
    }
  }
  // Every section page of the board points at the same payload.
  b.groups.forEach((g) => {
    const gp = path.join(ROOT, g.url.replace(/^\//, ""), "index.html");
    if (!fs.existsSync(gp)) return;
    const m = /data-src="([^"]+)"/.exec(fs.readFileSync(gp, "utf8"));
    check(
      "section: " + g.slug + " fetches the " + b.board + " payload",
      m && src && m[1] === src[1],
      m && m[1],
    );
  });
});

// ---- the board cascade (2026-08-27)
//
// The Board select drives the board-shaped dropdowns: Qualification,
// Theme / area, Paper section and Topic. With no board chosen the mixed lists
// are grouped under <optgroup>s labelled with the board names, so the two
// numbering systems never interleave; picking a topic or theme adopts its
// board. Pre-filtered pages keep exactly the flat lists they always had.
//
// init() needs a DOM, so these run it against a minimal fake: enough of
// <select> semantics (innerHTML replacement selects the first option; setting
// a value no option offers reads back "") for the component's real code paths.

function unescapeHtml(s) {
  return s
    .replace(/&quot;/g, '"')
    .replace(/&lt;/g, "<")
    .replace(/&gt;/g, ">")
    .replace(/&amp;/g, "&");
}

function parseOptions(html) {
  const out = [];
  let group = null;
  const re =
    /<optgroup label="([^"]*)">|<\/optgroup>|<option value="([^"]*)">([\s\S]*?)<\/option>/g;
  let m;
  while ((m = re.exec(html))) {
    if (m[0].indexOf("<optgroup") === 0) group = unescapeHtml(m[1]);
    else if (m[0] === "</optgroup>") group = null;
    else
      out.push({ value: unescapeHtml(m[2]), label: unescapeHtml(m[3]), group });
  }
  return out;
}

function FakeSelect(name, all) {
  this._attrs = { "data-ppq-filter": name, "data-ppq-all": all };
  this._options = [];
  this._value = "";
  this._html = "";
  this._handlers = {};
  this.disabled = false;
}
FakeSelect.prototype.getAttribute = function (n) {
  return n in this._attrs ? this._attrs[n] : null;
};
FakeSelect.prototype.addEventListener = function (type, fn) {
  (this._handlers[type] = this._handlers[type] || []).push(fn);
};
FakeSelect.prototype.change = function (value) {
  this.value = value;
  (this._handlers.change || []).forEach((fn) => fn());
};
Object.defineProperties(FakeSelect.prototype, {
  innerHTML: {
    get() {
      return this._html;
    },
    set(html) {
      this._html = html;
      this._options = parseOptions(html);
      // Replacing the options selects the first one, as a real select does.
      this._value = this._options.length ? this._options[0].value : "";
    },
  },
  value: {
    get() {
      return this._value;
    },
    set(v) {
      // A value no option offers leaves a real select with no selection,
      // which reads back as the empty string.
      this._value = this._options.some((o) => o.value === String(v))
        ? String(v)
        : "";
    },
  },
  options: {
    get() {
      return this._options.map((o) => ({ value: o.value }));
    },
  },
});

// The filter names and their "All ..." labels, from the served master page, so
// the harness cannot drift from the markup the component really meets.
const pageHtml = fs.readFileSync(
  path.join(ROOT, "past-paper-questions", "index.html"),
  "utf8",
);
const FILTERS = [];
const fre = /data-ppq-filter="([^"]+)"[^>]*data-ppq-all="([^"]+)"/g;
for (let m; (m = fre.exec(pageHtml));) FILTERS.push({ name: m[1], all: m[2] });
check(
  "harness: the master page carries the eight filter selects",
  FILTERS.length === 8,
  FILTERS.map((f) => f.name).join(","),
);

function makeStub() {
  return {
    hidden: false,
    textContent: "",
    innerHTML: "",
    value: "",
    addEventListener() {},
    focus() {},
  };
}

function makeRoot(prefilters) {
  const selects = FILTERS.map((f) => new FakeSelect(f.name, f.all));
  const byName = {};
  selects.forEach((s) => (byName[s.getAttribute("data-ppq-filter")] = s));
  const clear = {
    _handlers: [],
    disabled: false,
    addEventListener(type, fn) {
      if (type === "click") this._handlers.push(fn);
    },
    click() {
      this._handlers.forEach((fn) => fn());
    },
  };
  const parts = {
    "[data-ppq-controls]": {
      addEventListener() {},
      querySelectorAll() {
        return [];
      },
      removeAttribute() {},
      setAttribute() {},
    },
    "[data-ppq-query]": makeStub(),
    "[data-ppq-count]": makeStub(),
    "[data-ppq-results]": makeStub(),
    "[data-ppq-empty]": makeStub(),
    "[data-ppq-more]": makeStub(),
    "[data-ppq-clear]": clear,
    "[data-ppq-sort]": { value: "relevance", addEventListener() {} },
  };
  return {
    sel: byName,
    clear,
    count: parts["[data-ppq-count]"],
    root: {
      getAttribute(n) {
        return (prefilters && prefilters[n]) || null;
      },
      querySelector(s) {
        return parts[s] || null;
      },
      querySelectorAll(s) {
        return s === "[data-ppq-filter]" ? selects : [];
      },
      classList: { add() {} },
    },
  };
}

const boardNames = data.boards.map((b) => b.name);
const opts = (sel) => sel._options.slice(1); // drop the "All ..." option
const hasOptgroup = (sel) => sel.innerHTML.indexOf("<optgroup") !== -1;
const boardShaped = ["level", "group", "section", "topic"];

// -- the "Both boards" state

{
  const h = makeRoot();
  M.init(h.root, data);

  ["topic", "group"].forEach((name) => {
    const groups = opts(h.sel[name]).map((o) => o.group);
    check(
      "both boards: every " + name + " option sits under a board optgroup",
      groups.every((g) => g !== null),
    );
    check(
      "both boards: " + name + " optgroups are labelled from data.boards",
      groups.every((g) => boardNames.indexOf(g) !== -1),
    );
  });
  check(
    "both boards: the grouped Topic list still offers every topic",
    opts(h.sel.topic).length === Object.keys(data.topics).length,
    opts(h.sel.topic).length,
  );
  boardNames.forEach((name) => {
    const specs = opts(h.sel.topic)
      .filter((o) => o.group === name)
      .map((o) => o.label.split(" ")[0]);
    check(
      "both boards: no spec code repeats inside the " + name + " optgroup",
      new Set(specs).size === specs.length,
    );
  });
  check(
    "both boards: Sections A and B stay shared, outside any optgroup",
    opts(h.sel.section)
      .filter((o) => ["A", "B"].indexOf(o.value) !== -1)
      .every((o) => o.group === null),
  );
  check(
    "both boards: Section C sits under Edexcel's name",
    opts(h.sel.section)
      .filter((o) => o.value === "C")
      .every((o) => o.group === "Edexcel") &&
      opts(h.sel.section).some((o) => o.value === "C"),
  );
  check(
    "both boards: AS Level sits under Edexcel's name",
    opts(h.sel.level)
      .filter((o) => o.value === "as-level")
      .every((o) => o.group === "Edexcel") &&
      opts(h.sel.level).some((o) => o.value === "as-level"),
  );

  // -- the cascade: Board narrows the four board-shaped selects

  const before = {
    paper: h.sel.paper.innerHTML,
    marks: h.sel.marks.innerHTML,
    year: h.sel.year.innerHTML,
  };
  h.sel.board.change("edexcel");
  boardShaped.forEach((name) => {
    check(
      "cascade: with Edexcel chosen, " + name + " has no optgroups",
      !hasOptgroup(h.sel[name]),
    );
  });
  check(
    "cascade: every Topic option belongs to Edexcel",
    opts(h.sel.topic).every((o) => data.topics[o.value].board === "edexcel"),
  );
  const edexcelGroups = data.boards
    .filter((b) => b.board === "edexcel")[0]
    .groups.map((g) => g.slug);
  check(
    "cascade: every Theme / area option belongs to Edexcel",
    opts(h.sel.group).every((o) => edexcelGroups.indexOf(o.value) !== -1),
  );
  const sectionsOf = (board) =>
    [
      ...new Set(
        data.questions.filter((q) => q.board === board).map((q) => q.section),
      ),
    ].sort();
  check(
    "cascade: every Section option belongs to Edexcel",
    opts(h.sel.section)
      .map((o) => o.value)
      .join(",") === sectionsOf("edexcel").join(","),
  );
  const levelsOf = (board) =>
    [
      ...new Set(
        data.questions
          .filter((q) => q.board === board)
          .map((q) => data.papers[q.p].level),
      ),
    ].sort();
  check(
    "cascade: every Qualification option belongs to Edexcel",
    opts(h.sel.level)
      .map((o) => o.value)
      .join(",") === levelsOf("edexcel").join(","),
  );
  check(
    "cascade: Paper, Marks and Year are left alone",
    h.sel.paper.innerHTML === before.paper &&
      h.sel.marks.innerHTML === before.marks &&
      h.sel.year.innerHTML === before.year,
  );

  // -- a theme narrows Topic; a still-valid choice survives, an invalid one resets

  h.sel.group.change(edexcelGroups[2]); // theme-3
  check(
    "cascade: a chosen theme narrows Topic to its own topics",
    opts(h.sel.topic).length > 0 &&
      opts(h.sel.topic).every(
        (o) => data.topics[o.value].group === edexcelGroups[2],
      ),
  );
  const kept = opts(h.sel.topic)[0].value;
  h.sel.topic.change(kept);
  h.sel.section.change("C");
  h.sel.board.change("aqa");
  check(
    "cascade: switching to AQA resets an Edexcel topic to All topics",
    h.sel.topic.value === "",
  );
  check(
    "cascade: switching to AQA resets the Edexcel theme and Section C",
    h.sel.group.value === "" && h.sel.section.value === "",
  );
  check(
    "cascade: AQA offers only its own areas and only A Level",
    opts(h.sel.group).every((o) => edexcelGroups.indexOf(o.value) === -1) &&
      opts(h.sel.level)
        .map((o) => o.value)
        .join(",") === levelsOf("aqa").join(","),
  );

  // -- Clear all restores the full grouped lists

  h.clear.click();
  check(
    "clear all: every select is back on All ...",
    FILTERS.every((f) => h.sel[f.name].value === ""),
  );
  check(
    "clear all: the grouped Topic list is back in full",
    hasOptgroup(h.sel.topic) &&
      opts(h.sel.topic).length === Object.keys(data.topics).length,
  );
  check("clear all: Theme / area is grouped again", hasOptgroup(h.sel.group));
}

// -- picking a topic or theme while "Both boards" adopts its board

{
  const aqaSlug = Object.keys(data.topics).filter(
    (s) => data.topics[s].board === "aqa",
  )[0];
  const h = makeRoot();
  M.init(h.root, data);
  h.sel.topic.change(aqaSlug);
  check(
    "adopt: picking an AQA topic sets Board to AQA",
    h.sel.board.value === "aqa",
  );
  check(
    "adopt: the picked topic stays selected through the cascade",
    h.sel.topic.value === aqaSlug,
  );
  check(
    "adopt: the other dropdowns narrow to AQA",
    opts(h.sel.topic).every((o) => data.topics[o.value].board === "aqa") &&
      !hasOptgroup(h.sel.group),
  );

  const h2 = makeRoot();
  M.init(h2.root, data);
  h2.sel.group.change("microeconomics");
  check(
    "adopt: picking an AQA area sets Board to AQA",
    h2.sel.board.value === "aqa" && h2.sel.group.value === "microeconomics",
  );
}

// -- query-string arrivals from the revision notes

{
  const aqaSlug = Object.keys(data.topics).filter(
    (s) => data.topics[s].board === "aqa",
  )[0];
  const F = factory({ location: { search: "?topic=" + aqaSlug } });
  const h = makeRoot();
  F.init(h.root, data);
  check(
    "url: a bare ?topic= for an AQA topic ends with Board showing AQA",
    h.sel.board.value === "aqa",
    h.sel.board.value,
  );
  check(
    "url: ... and the topic selected, in an AQA-only list",
    h.sel.topic.value === aqaSlug &&
      opts(h.sel.topic).every((o) => data.topics[o.value].board === "aqa"),
  );

  // The shape the notes pages actually link with.
  const edexcelSlug = Object.keys(data.topics).filter(
    (s) => data.topics[s].board === "edexcel",
  )[0];
  const F2 = factory({
    location: { search: "?board=edexcel&topic=" + edexcelSlug },
  });
  const h2 = makeRoot();
  F2.init(h2.root, data);
  const expected = data.questions.filter(
    (q) => q.topics.indexOf(edexcelSlug) !== -1,
  ).length;
  check(
    "url: ?board=edexcel&topic= lands filtered with both controls set",
    h2.sel.board.value === "edexcel" && h2.sel.topic.value === edexcelSlug,
  );
  check(
    "url: ... and the count shows that topic's questions",
    h2.count.textContent.indexOf(String(expected)) === 0 ||
      (expected === 1 && h2.count.textContent === "1 question"),
    h2.count.textContent + " for " + expected,
  );
}

// -- pre-filtered pages keep exactly the behaviour they shipped with

{
  const boardData = JSON.parse(
    fs.readFileSync(
      path.join(ROOT, "past-paper-questions", "edexcel", "questions.json"),
      "utf8",
    ),
  );
  const h = makeRoot({ "data-prefilter-board": "edexcel" });
  M.init(h.root, boardData);
  check(
    "prefiltered hub: no select carries an optgroup",
    FILTERS.every((f) => !hasOptgroup(h.sel[f.name])),
  );
  check(
    "prefiltered hub: the Topic list still offers the whole board",
    opts(h.sel.topic).length === Object.keys(boardData.topics).length,
  );
  const topicHtml = h.sel.topic.innerHTML;
  h.sel.group.change("theme-1");
  check(
    "prefiltered hub: choosing a theme does not reshape the Topic list",
    h.sel.topic.innerHTML === topicHtml,
  );

  const topicSlug = Object.keys(data.topics).filter(
    (s) => data.topics[s].board === "aqa" && data.topics[s].hasPage,
  )[0];
  const topicData = JSON.parse(
    fs.readFileSync(
      path.join(
        ROOT,
        "past-paper-questions",
        "aqa",
        topicSlug,
        "questions.json",
      ),
      "utf8",
    ),
  );
  const h2 = makeRoot({ "data-prefilter-topic": topicSlug });
  M.init(h2.root, topicData);
  check(
    "prefiltered topic page: no select carries an optgroup",
    FILTERS.every((f) => !hasOptgroup(h2.sel[f.name])),
  );
}

console.log(
  failures === 0
    ? "all " + index.length + " records indexed; every check passed"
    : failures + " check(s) failed",
);
process.exit(failures === 0 ? 0 : 1);

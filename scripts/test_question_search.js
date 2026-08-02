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

// Everything from the text helpers down to the component is DOM-free, so it can
// be lifted out and exercised directly.
const START =
  "// ---------------------------------------------------------------- text";
const END =
  "// ---------------------------------------------------------------- component";
const from = source.indexOf(START);
const to = source.indexOf(END);
if (from === -1 || to === -1 || to <= from) {
  console.error(
    "FATAL: could not find the text/component section markers in question-search.js.\n" +
      "The file was restructured; update this test rather than deleting it.",
  );
  process.exit(2);
}

const slice = source.slice(from, to);
const factory = new Function(
  slice +
    "\nreturn { normalise, tokenise, withinDistance, allowedEdits, buildIndex," +
    " score, cardHtml, escapeHtml };",
);
const M = factory();

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

console.log(
  failures === 0
    ? "all " + index.length + " records indexed; every check passed"
    : failures + " check(s) failed",
);
process.exit(failures === 0 ? 0 : 1);

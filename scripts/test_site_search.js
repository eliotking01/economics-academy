/* Tests for the matching half of js/components/site-search.js.
 *
 *   node scripts/test_site_search.js
 *
 * Same approach as test_question_search.js: this does not re-implement the
 * matcher, it slices the DOM-free section out of the real component file and
 * evaluates that, so the code under test is the code that ships. It then
 * runs the real /search-index.json through it, so the schema the generator
 * writes and the schema the client reads are proved against each other on
 * every CI run.
 *
 * There is no test framework in this repo and this does not add one.
 */

"use strict";

const fs = require("fs");
const path = require("path");

const ROOT = path.resolve(__dirname, "..");
const SRC = path.join(ROOT, "js", "components", "site-search.js");
const DATA = path.join(ROOT, "search-index.json");

const source = fs.readFileSync(SRC, "utf8");

// Everything from the config constants down to the overlay state is DOM-free.
const START =
  "// -------------------------------------------------------------- config";
const END =
  "// ---------------------------------------------------------------- state";
const from = source.indexOf(START);
const to = source.indexOf(END);
if (from === -1 || to === -1 || to <= from) {
  console.error(
    "FATAL: could not find the config/state section markers in site-search.js.\n" +
      "The file was restructured; update this test rather than deleting it.",
  );
  process.exit(2);
}

const slice = source.slice(from, to);
const factory = new Function(
  slice +
    "\nreturn { normalise, tokenise, escapeHtml, withinDistance, allowedEdits," +
    " buildRows, scoreRow, search, highlight, GROUP_ORDER, GROUP_CAPS };",
);
const M = factory();

const data = JSON.parse(fs.readFileSync(DATA, "utf8"));
const rows = M.buildRows(data);

let failures = 0;
function check(name, cond, detail) {
  if (cond) return;
  failures++;
  console.log("FAIL  " + name + (detail ? "  -> " + detail : ""));
}

function titles(result, group) {
  return (result.groups[group] || []).map((x) => x.row.title);
}

// ---------------------------------------------------------------- schema

// One row per topic for notes and practice, one per gated topic for the
// bank, one per deck, one per glossary record, one per page.
const ppqCount = data.topics.filter((t) => t[6]).length;
check(
  "row expansion matches the payload",
  rows.length ===
    data.topics.length * 2 +
      ppqCount +
      data.decks.length +
      data.glossary.length +
      data.pages.length,
  String(rows.length),
);
check(
  "every row has a rooted url",
  rows.every((r) => r.url.charAt(0) === "/"),
);
check(
  "every glossary row keeps its definition and at least one link",
  rows
    .filter((r) => r.group === "glossary")
    .every((r) => r.def && r.links.length >= 1),
);

// ------------------------------------------------------------- matching

let res = M.search(rows, "monopsony");
check("monopsony floats the exact glossary term", !!res.exact);
check(
  "the float is the term itself",
  res.exact && res.exact.row.title === "Monopsony",
);
check(
  "monopsony finds the Edexcel notes page",
  titles(res, "notes").indexOf("Monopsony") !== -1,
);
check(
  "monopsony reaches AQA labour-market notes through their headings",
  (res.groups.notes || []).some((x) => x.row.meta.indexOf("AQA") !== -1),
);

res = M.search(rows, "theme 2 flashcards");
check(
  "theme 2 flashcards resolves to the deck",
  titles(res, "practice")[0] === "Edexcel A-Level Economics Theme 2 Flashcards",
);

res = M.search(rows, "how much is marking");
check(
  "stopwords: 'how much is marking' finds the marking page",
  titles(res, "pages").some((t) => t.indexOf("Marking") !== -1),
);
check(
  "strict pass wins: no fuzzy 'Making' notes for 'marking'",
  titles(res, "notes").every((t) => t.indexOf("Making") === -1),
  titles(res, "notes").join(", "),
);

res = M.search(rows, "monetry policy");
check(
  "typo falls back to fuzzy and finds Monetary Policy",
  titles(res, "notes").some((t) => t.indexOf("Monetary Policy") !== -1),
  titles(res, "notes").join(", "),
);

res = M.search(rows, "asdfghjkl");
check("garbage finds nothing", !res.any);

res = M.search(rows, "the is a");
check("an all-stopword query still searches rather than vetoing", res !== null);

// Exact title beats prefix siblings.
res = M.search(rows, "demand");
check(
  "exact title match ranks first",
  titles(res, "notes")[0] === "Demand",
  titles(res, "notes").join(", "),
);

// ------------------------------------------------------------ highlight

check(
  "highlight marks the token",
  M.highlight("Monetary Policy", ["policy"]) ===
    "Monetary <mark>Policy</mark>",
  M.highlight("Monetary Policy", ["policy"]),
);
check(
  "highlight escapes markup in titles",
  M.highlight("<script>alert(1)</script>", ["alert"]).indexOf("<script>") === -1,
);
check(
  "escapeHtml escapes quotes and angles",
  M.escapeHtml('a<b>"c"') === "a&lt;b&gt;&quot;c&quot;",
);

// ---------------------------------------------------------------- done

if (failures) {
  console.log(failures + " failure(s)");
  process.exit(1);
}
console.log("site-search: all checks passed (" + rows.length + " rows)");

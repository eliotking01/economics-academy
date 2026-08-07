/* Tests for js/components/glossary-filter.js and the markup it depends on.
 *
 *     node scripts/test_glossary_filter.js
 *
 * Same approach as scripts/test_question_search.js: slice the DOM-free half out
 * of the shipped component and run it, so the code tested is the code that
 * ships. The second half asserts the generated page still carries the markup
 * contract the component reads - a generator change that dropped data-groups,
 * or shipped the controls visible, would break the filter silently.
 *
 * No framework and no dependency; exits 0 or 1, or 2 if the file was
 * restructured and the section markers can no longer be found.
 */
const fs = require("fs");
const src = fs.readFileSync("js/components/glossary-filter.js", "utf8");
const START =
  "// ---------------------------------------------------------------- text";
const END =
  "// ---------------------------------------------------------------- index";
const from = src.indexOf(START);
const to = src.indexOf(END);
if (from < 0 || to < 0 || to <= from) {
  console.error("FATAL: section markers missing from glossary-filter.js");
  process.exit(2);
}
const M = new Function(
  src.slice(from, to) +
    "\nreturn {normalise,tokenise,withinDistance,allowedEdits," +
    "score,SEARCH_FIELDS,NO_MATCH,fieldTokens};",
)();

/* A record as buildIndex would make one, without needing a DOM. */
function rec(term, definition) {
  return {
    termText: M.normalise(term),
    termTokens: M.tokenise(term),
    definitionTokens: M.tokenise(definition || ""),
  };
}
function rank(term, query, definition) {
  return M.score(
    rec(term, definition),
    M.normalise(query.trim()),
    M.tokenise(query),
    M.SEARCH_FIELDS,
  );
}

let fails = 0;
function ck(name, cond) {
  if (!cond) {
    console.log("  FAIL " + name);
    fails++;
  }
}

ck(
  "tokenise splits punctuation",
  JSON.stringify(M.tokenise("Price Elasticity of Demand (PED)")) ===
    JSON.stringify(["price", "elasticity", "of", "demand", "ped"]),
);
ck("normalise curly quotes", M.normalise("don’t") === "don't");
ck("normalise en dash", M.normalise("A–B") === "a-b");
ck("withinDistance one edit", M.withinDistance("elasticty", "elasticity", 1));
ck(
  "withinDistance rejects two edits at max 1",
  !M.withinDistance("elastic", "elasticity", 1),
);
ck(
  "allowedEdits scales with length",
  M.allowedEdits("ped") === 0 &&
    M.allowedEdits("demand") === 1 &&
    M.allowedEdits("elasticity") === 2,
);

// ---- term-only matching and the rank order -------------------------------

ck(
  "search fields are term only",
  JSON.stringify(M.SEARCH_FIELDS) === '["term"]',
);

ck(
  "definition text is not searched",
  rank("Opportunity cost", "elasticity", "the responsiveness of demand ...") ===
    M.NO_MATCH,
);
ck(
  "a term still matches its own words",
  rank("Elasticity", "elasticity", "") === 0,
);

// exact < starts-with < word-start < contains < fuzzy
ck("rank 0 is an exact term", rank("Demand", "demand") === 0);
ck("rank 1 is a term prefix", rank("Demand curve", "demand") === 1);
ck(
  "rank 2 is a word inside the term",
  rank("Aggregate Demand (AD)", "demand") === 2,
);
ck(
  "rank 4 is a typo",
  rank("Elasticity", "elasitcity") === 4 &&
    rank("Elasticity", "elasticity") === 0,
);
ck(
  "the ordering actually holds",
  rank("Demand", "demand") < rank("Demand curve", "demand") &&
    rank("Demand curve", "demand") < rank("Aggregate Demand (AD)", "demand"),
);

ck(
  "an abbreviation in brackets is a term token",
  rank("Price Elasticity of Demand (PED)", "PED") === 2,
);
ck("matching is case insensitive", rank("Demand", "DEMAND") === 0);
ck("leading and trailing space is ignored", rank("Demand", "  demand  ") === 0);
ck(
  "accents are folded",
  M.normalise("Laissez-fáire") === M.normalise("Laissez-faire"),
);
ck(
  "every query token must hit",
  rank("Demand curve", "demand elasticity") === M.NO_MATCH,
);
/* One good token must not carry a bad one: "demand" is a clean word-start hit,
 * "elasitcity" only matches fuzzily, so the pair ranks as the fuzzy one. */
ck(
  "the weakest token sets the rank",
  rank("Elasticity of demand", "demand elasitcity") === 4 &&
    rank("Elasticity of demand", "demand elasticity") === 2,
);

// The real page must actually carry what the filter reads.
const page = fs.readFileSync("revision-notes/glossary/aqa/index.html", "utf8");
const entries = (page.match(/data-term="/g) || []).length;
const groups = (page.match(/data-groups="/g) || []).length;
ck("page has data-term on every entry", entries > 200);
ck("page has data-groups on every entry", groups === entries);
ck("controls ship hidden", /data-gl-controls\s+hidden/.test(page));
ck(
  "count region is a live region",
  /data-gl-count/.test(page) && /aria-live="polite"/.test(page),
);
ck("empty state ships hidden", /data-gl-empty\s+hidden/.test(page));
ck("noscript fallback present", /<noscript>/.test(page));
ck(
  "ranked results container ships hidden and empty",
  /data-gl-results\s+hidden/.test(page) &&
    /data-gl-results[\s\S]{0,120}<dl class="gl-list"><\/dl>/.test(page),
);
ck("empty state echoes the query", /data-gl-echo/.test(page));
ck(
  "the box says it searches terms only",
  /placeholder="Search key terms[^"]*"/.test(page) &&
    /Searches term names, not definition text/.test(page),
);
ck(
  "hidden rule exists in the stylesheet",
  /\.glossary-page \[hidden\][\s\S]{0,80}display:\s*none\s*!important/.test(
    fs.readFileSync("css/pages/glossary.css", "utf8"),
  ),
);

console.log(
  fails === 0 ? "  all checks passed" : "  " + fails + " check(s) failed",
);
process.exit(fails === 0 ? 0 : 1);

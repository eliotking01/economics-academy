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
const START = "// ---------------------------------------------------------------- text";
const END = "// ---------------------------------------------------------------- index";
const from = src.indexOf(START);
const to = src.indexOf(END);
if (from < 0 || to < 0 || to <= from) {
  console.error("FATAL: section markers missing from glossary-filter.js");
  process.exit(2);
}
const M = new Function(
  src.slice(from, to) +
    "\nreturn {normalise,tokenise,withinDistance,allowedEdits};",
)();

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

// The real page must actually carry what the filter reads.
const page = fs.readFileSync("revision-notes/glossary/aqa/index.html", "utf8");
const entries = (page.match(/data-term="/g) || []).length;
const groups = (page.match(/data-groups="/g) || []).length;
ck("page has data-term on every entry", entries > 200);
ck("page has data-groups on every entry", groups === entries);
ck("controls ship hidden", /data-gl-controls\s+hidden/.test(page));
ck("count region is a live region", /data-gl-count/.test(page) && /aria-live="polite"/.test(page));
ck("empty state ships hidden", /data-gl-empty\s+hidden/.test(page));
ck("noscript fallback present", /<noscript>/.test(page));
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

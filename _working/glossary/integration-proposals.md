# Phase 4.3 — integration proposals

**Nothing here has been done.** Each item is an additive change to an existing
file and needs your sign-off, per the brief. Approve by number.

The glossary is live in the repo and fully linked *outward* — every entry links
to its notes page — but nothing on the site links *in* yet. These are the ways in.

---

## P1. Nav item in the Revision Notes dropdown

`templates/header.html`, inside the Revision Notes `<li>`, after Macro
Application. One `<li>`, nothing else changes.

```html
          <li>
            <a href="/revision-notes/macro-application/index.html"
              >Macro Application</a
            >
          </li>
+         <li>
+           <a href="/revision-notes/glossary/">Glossary &amp; Formulae</a>
+         </li>
        </ul>
      </li>
```

**No JavaScript change is needed.** `inject-templates.js` already highlights
"Revision Notes" for any `/revision-notes/…` path, which is why the URL was put
there.

**Alternative (P1b)** — a third-level submenu matching how Edexcel and AQA work,
so a student reaches their board in one click:

```html
+         <li>
+           <a href="#" role="button">Glossary</a>
+           <ul>
+             <li><a href="/revision-notes/glossary/edexcel-a/">Edexcel</a></li>
+             <li><a href="/revision-notes/glossary/aqa/">AQA</a></li>
+           </ul>
+         </li>
```

I would take **P1**. The dropdown already has two three-level branches, and a
third makes it heavy for one destination; the landing page exists to make that
choice, and it also carries the "same term, different board" explanation.

---

## P2. Button on the Revision Notes hub

`revision-notes/index.html`, the "More Free Resources" block at the bottom.
It currently holds three `.col-4` buttons — Micro Diagrams, Macro Diagrams,
Macro Application.

**This one cannot be purely additive.** A fourth button in a three-column row
either wraps onto its own line or the existing three must change from `col-4`
to `col-3`. So it is a real edit to existing markup, and needs a decision:

- **P2a — four across.** Change all four `col-4 col-12-medium` to
  `col-3 col-12-medium`. Tidiest result, but touches the three existing lines.
- **P2b — leave the three, add a fourth that wraps.** Purely additive; the
  glossary button sits alone on a second row, which looks unbalanced.
- **P2c — do nothing here**, and rely on the nav item and the notes-page links.

I would take **P2a**.

One thing worth knowing either way: that block uses inline
`style="width: 100%"` on every button, which the house rules forbid. If you take
P2a I would move those four inline styles into a class in
`css/pages/revision-notes.css` at the same time — say so and I will, or leave it
and I will match the existing inline style exactly.

```html
              <div class="col-3 col-12-medium">
                <a
                  href="/revision-notes/glossary/"
                  class="button primary"
                  style="width: 100%"
                  >Glossary &amp; Formulae</a
                >
              </div>
```

---

## P3. Links from the topic pages

This is the one with real traffic behind it and the one to be most careful
about, because it touches all 166 topic pages.

Every topic page already ends with `.notes-cta`, and most also carry a
`.notes-questions-link` block and a `.notes-past-papers-link` block. A glossary
link would follow the same pattern.

**P3a — one line inside the existing `.notes-cta`.** Smallest change, one extra
button on a row that already has three:

```html
              <a href="/revision-notes/glossary/edexcel-a/?topic=theme-1"
                class="button alt"
                >Glossary</a
              >
```

**P3b — deep-link to the terms this page defines.** The glossary filter already
accepts `?q=` and `?topic=`, and every term has its own anchor, so a page could
link to exactly the terms it introduces:

```html
            <div class="notes-questions-link">
              <h2>Key terms from this topic</h2>
              <p>The four terms this page defines, with the same wording, in the
                Edexcel glossary.</p>
              <a href="/revision-notes/glossary/edexcel-a/?topic=theme-1"
                class="button primary"
                >Glossary: Theme 1 terms</a
              >
            </div>
```

**P3c — hub and gallery pages only.** Link from `revision-notes/index.html`
(that is P2), the two diagram galleries and the macro-application page. Five
pages instead of 166.

I would take **P3c now and P3a later**, for one specific reason: the
`.notes-past-papers-link` blocks on those pages were added by a script and their
indentation is visibly mangled, which is exactly the failure mode `CLAUDE.md`
warns about. Touching 166 pages again is worth doing deliberately, with
`verify_text_integrity.py` and `verify_markup_integrity.py` run against the
before-commit, rather than as a footnote to this build.

If you want P3a or P3b now, say so and I will do it with those two verifiers
gating the commit.

---

## P4. Not proposed, but available

- The past-papers hub and the practice-questions hub have no glossary link
  either. Same shape as P2 if you want them.
- `?q=` deep links mean a tutoring email can point a student at one definition:
  `…/glossary/edexcel-a/#price-elasticity-of-demand-ped`.

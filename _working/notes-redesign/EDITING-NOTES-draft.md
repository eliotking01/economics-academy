# Editing the revision notes — DRAFT for Gate 2 review

> This becomes `docs/EDITING-NOTES.md` at Gate 3. Written for Eliot, in
> plain English. Two pages, as briefed.

## Which file to open

A page's URL maps straight to its source file:

    economicsacademy.co.uk/revision-notes/edexcel-theme-1/1-2-2-demand.html
    →              notes-data/topics/edexcel-theme-1/1-2-2-demand.html

Never edit anything under `revision-notes/` itself — the next build
overwrites it. Edit the file under `notes-data/topics/`, then run:

```bash
python3 scripts/build.py
```

Check the page in Live Server, then commit. `python3
scripts/suggest_trailers.py` prints any `Text-Change:` lines your commit
message needs (editing the notes' wording always needs them — one per page).
For a brand-new topic, run `python3 scripts/new_topic.py` first; it
scaffolds the slice, the metadata and the practice-questions record.

## The skeleton of a slice

```
breadcrumb  ← leave alone
<div class="notes-container">
  <header class="major"><h1>Title</h1></header>   ← one h1, plain text
  <div class="spec-alert">…</div>                 ← must contain "unit X.Y.Z"
  <section> … </section>                          ← your content, repeated
  (optional: one <p class="notes-diagrams-link">) ← Edexcel diagram pages
</div>
```

Do not touch: the breadcrumb, the container div, the spec-alert's
"unit X.Y.Z" phrase (the build reads the code from it), and do not add
anything after the last `</section>` except that one optional paragraph.
The build derives everything else — heading ids, the "On this page" list,
definition cards, the tap-to-enlarge on diagrams, WebP image versions, the
whole tail — so there is nothing to number, no id to invent, and no
attribute to remember. If a slice breaks one of these rules the build stops
and names the file and what to fix; it never half-builds a page.

## Copy-paste snippets

**A new section** — the contents list picks it up automatically:

```html
<section>
  <h2>Heading</h2>
  <p>Text.</p>
</section>
```

**A definition** — becomes a pink definition card, and the glossary
extracts it. The chip must open the paragraph; a chip mid-sentence renders
as an inline highlight instead, which is also fine:

```html
<p>
  <span class="key-definition">Term:</span> The definition.
</p>
```

**An inline example** (green):

```html
<span class="content-example">Example:</span>
```

**An exam tip** — one paragraph, no heading, bold lead sentence:

```html
<div class="exam-tip">
  <p><strong>Lead sentence.</strong> Two or three more sentences.</p>
</div>
```

**An evaluation point** — like an exam tip, orange:

```html
<div class="evaluation-point">
  <p>…</p>
</div>
```

**A diagram** — PNG into `images/diagrams/`, then run
`python3 scripts/build_diagram_webp.py --apply` once (it makes the smaller
WebP copy; the build fails loudly if you forget). Width and height are the
image's real pixel size (Finder → Get Info). Real alt text, always.
`loading="lazy"` on every diagram except the first on the page:

```html
<figure class="diagram-figure">
  <img
    src="/images/diagrams/NAME.png"
    alt="What the diagram shows"
    class="diagram-image"
    width="1731"
    height="1280"
    loading="lazy"
  />
  <figcaption class="diagram-caption">Figure 2: caption.</figcaption>
</figure>
```

**A comparison table** — always inside the container div (that is what
scrolls on phones):

```html
<div class="table-container">
  <table class="concept-table">
    <thead>
      <tr><th>Column</th><th>Column</th></tr>
    </thead>
    <tbody>
      <tr><td>…</td><td>…</td></tr>
    </tbody>
  </table>
</div>
```

**A formula** — the comment line stops the formatter mangling the maths;
`\[ … \]` for a displayed formula, `\( … \)` inline. A page with maths
loads MathJax by itself:

```html
<!-- prettier-ignore -->
<div class="formula-box">
  \[ \text{Formula} = \frac{a}{b} \times 100 \]
</div>
```

**A worked example** — its heading always opens "Worked Example:"; use the
two-column calculation table (never wrapped in the container) for a running
calculation, and end on a sentence interpreting the number, never on the
arithmetic:

```html
<div class="worked-example">
  <h3>Worked Example: Title</h3>
  <p>Setup…</p>
  <table class="calculation-table">
    <tr><td>Step</td><td>Value</td></tr>
    <tr><td><strong>Answer</strong></td><td>…</td></tr>
  </table>
  <p>What the number means.</p>
</div>
```

## When something goes wrong

The build's checks talk in file paths: a message like
`notes-data/topics/edexcel-theme-1/1-2-2-demand.html: the slice does not
end at its last </section>` means exactly that — open the file, look at
what follows the last section, remove or move it. If you paste a diagram
and the page shows it without the tap-to-enlarge frame, the PNG is missing
its WebP twin — run the `build_diagram_webp.py` line above. If a
definition does not render as a card, the chip is not the first thing in
its paragraph — that is allowed, just a different look.

House style reminders (the full rules are `revision-notes/CLAUDE.md`):
`<strong>` for key terms, `<em>` for contrast only; escape `&` as `&amp;`
and `<` as `&lt;`; at most two components per page; UK English and £.

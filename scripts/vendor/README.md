# scripts/vendor

Build-time only. **Nothing here is served to the browser.**

## `katex.min.js` — KaTeX 0.16.11

`scripts/build_glossary.py` shells out to `node` with this file to pre-render
every glossary formula to static HTML, so the published pages carry no maths
JavaScript at all and formulae display with JavaScript disabled.

It is vendored rather than fetched with `npx` because `npx --package` does not
put the module on `NODE_PATH` for `node -e`, and resolving it out of the npx
cache means depending on a hashed path that npm is free to change. Vendoring
makes the build deterministic and offline.

What the browser gets is `css/vendor/katex/` — the stylesheet and the woff2
fonts, and nothing else.

To upgrade, replace both together and re-run the generator:

    npx --yes katex@<version> --version
    cp <npx-cache>/katex/dist/katex.min.js  scripts/vendor/
    cp <npx-cache>/katex/dist/katex.min.css css/vendor/katex/
    cp <npx-cache>/katex/dist/fonts/*.woff2 css/vendor/katex/fonts/
    python3 scripts/build_glossary.py

The stylesheet has its `woff` and `ttf` sources stripped; see the comment at
the top of `css/vendor/katex/katex.min.css`.

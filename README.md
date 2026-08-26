# Economics Academy

The hand-written static site behind **economicsacademy.co.uk**: free A-Level
Economics revision notes, past papers, flashcards and practice questions,
plus paid tutoring and marking. No framework, no build step — GitHub Pages
serves the `main` branch as-is, so **merging to `main` is publishing**. What
is public is decided by `_config.yml`'s `exclude` list and Jekyll's
underscore rule, nothing else.

Read these four first:

1. `PROGRESS.md` — every project on the site, and what is still open.
2. `OWNER-TODO.md` — the things only Eliot can do.
3. `CLAUDE.md` — the working rules: the hard rules, the commands, where to
   look for everything else.
4. `docs/REPO-MAP.md` — a plain-English tour of every file and folder.

The two commands that matter:

```bash
python3 scripts/verify_generated.py         # the 9 generators vs the committed tree
python3 scripts/build_sitemap.py --check    # ends SITEMAP OK or SITEMAP STALE
```

Run the whole suite before any push — every check in
`.github/workflows/verify.yml` runs locally, and `scripts/CLAUDE.md` maps
them.

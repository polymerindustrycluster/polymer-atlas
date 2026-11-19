# CI and Pages

Both workflows are live in `.github/workflows/`. Edit them there; there is no second copy.

- **`validate.yml`** runs on every pull request and every push to `main`:
  - `scripts/validate.py`;
  - the row-loss guard;
  - the vocabulary export check;
  - the unit and mutation tests;
  - the SQLite build;
  - the generated-artifact guard.

  The repository ruleset "main: require validate" makes the `validate` check required, so a red PR cannot merge.
  Added 2026-11-02 (c485cfad).
- **`pages.yml`** runs on every push to `main`. It validates the data first, so a red tree is never published. Then it
  builds the site with `scripts/build_pages.py` (public fields only; nothing generated is committed) and deploys it to
  GitHub Pages at https://polymerindustrycluster.github.io/polymer-atlas/.

Preview the site locally with
`python3 scripts/build_pages.py && python3 -m http.server -d build/pages 8000`, then open http://localhost:8000.

Until 2026-11-02 the agents' GitHub App could not write workflow files, so this folder held proposed copies for the
owner to commit. That is why AGENTS.md §2 keeps a historical campaign-mode rule. Campaign mode was retired on
2026-11-03 (owner battery B-CAMP).

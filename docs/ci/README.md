# CI and Pages

Both workflows are live in `.github/workflows/`. Edit them there; there is no second copy.

- **`validate.yml`** runs on every pull request and every push to `main`:
  - `scripts/validate.py`;
  - the personal-account URL guard on `tasks/` and `docs/` (`scripts/check_account_urls.py`, since 2026-11-19);
  - the row-loss guard;
  - on pull requests, the evidence binding gate (`scripts/check_evidence_binding.py --new-since`, since 2026-11-22):
    - **What it checks:** the evidence rows the PR adds or re-points.
    - **FAIL rows:** any one fails the PR, and there is no waiver. A row FAILs when:
      - the quoted operator is not a name the record holds;
      - the site street is not equal under `street_key`;
      - a headquarters address comes from a source other than an entity-address source;
      - a web quote is off the record's own domain, or lacks the site's street.
    - **UNINSPECTABLE rows:** admitted only by a gate-chosen sample. That is the 30 rows per `created_by` label with the
      lowest sha256 of evidence_id, each VERIFIED in `tasks/<folder>/BINDING_SAMPLE.csv`.
    - **Rows already on `main`:** reported by `--all`, not failed;
  - on pull requests, the evidence provenance check (`--provenance-since`, since 2026-11-22): each `created_by` label of
    an added evidence row must name, by one of its words, a `tasks/<folder>/` holding a `check.py`;
  - the vocabulary export check;
  - the unit and mutation tests;
  - the SQLite build;
  - the generated-artifact guard.

  The workflow was added 2026-11-02 (c485cfad). Since 2026-11-14 the repository ruleset "main: require validate" makes
  the `validate` check required before a merge into `main`. Repository admins can bypass it in an emergency
  (DECISIONS.md, 2026-11-14).
- **`pages.yml`** runs on every push to `main`. It runs `scripts/validate.py` first, so a tree that fails the CSV
  validator is never published. It does not wait for the separate `validate` workflow, so a commit that fails only a
  later `validate` step can still be deployed. It then builds the site with `scripts/build_pages.py` (public fields
  only; nothing generated is committed) and deploys it to GitHub Pages at
  https://polymerindustrycluster.github.io/polymer-atlas/. The Pages source is set to GitHub Actions.

Preview the site locally with
`python3 scripts/build_pages.py && python3 -m http.server -d build/pages 8000`, then open http://localhost:8000.

Until 2026-11-02 the agents' GitHub App could not write workflow files, so this folder held proposed copies for the
owner to commit. That is why AGENTS.md §2 keeps a historical campaign-mode rule. Campaign mode was retired on
2026-11-03 (owner battery B-CAMP).

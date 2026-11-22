# CI and Pages

Both workflows are live in `.github/workflows/`. Edit them there; there is no second copy.

- **`validate.yml`** runs on every pull request and every push to `main`:
  - `scripts/validate.py`;
  - the personal-account URL guard on `tasks/` and `docs/` (`scripts/check_account_urls.py`, since 2026-11-19);
  - the row-loss guard;
  - on pull requests, two evidence binding steps (`scripts/check_evidence_binding.py`, since 2026-11-22). **These
    steps are early feedback, not authoritative:** `validate` runs the PR's own copy of the checker, so a PR that edits
    the checker or the workflow changes the result. The authoritative run is a `pull_request_target` workflow that runs
    `main`'s checker with `--tree <PR checkout>` (owned by the working-rules lane, PR #466).
    - **`--new-since`** gates every evidence row the PR adds, and every row whose content changed in any column.
      - **PASS** (structured sources only): the quoted operator is a held name, compared whole and never split on
        commas; a site-name part counts only when it holds the organization's own name tokens. For a site,
        `scripts/matching.py` `same_street()` holds (the same street test the last-activity derivation uses: a suite,
        unit or building stated on both sides must agree), and a quoted city or state equals the record's. For a
        headquarters address, an entity-address source states the record's city and state.
      - **FAIL**: any FAIL fails the PR, and there is no waiver.
      - **READ_REQUIRED and UNINSPECTABLE** also fail the PR: a web quote is never PASS, and this gate has no
        admission path for it. Take such a row out and hold it as a lead. Admission of web rows by per-row proof is
        follow-up work on branch `agent/claude-code/evidence-binding-web-proofs-2026-11-22`, not yet a PR.
    - **`--provenance-since`**: each `created_by` label must name exactly one `tasks/<folder>/`. That folder must hold a
      non-empty `check.py`, and a new label adds its own folder in the PR. **The gate checks presence only and executes
      nothing from the tree it gates.** The replay that `check.py` performs is run by the lane, and again by the
      reviewing family; their results go in the PR, not in this job.
    - `--sample N --seed S` is an audit and admits nothing. Rows already on `main` are reported by `--all`, not failed;
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

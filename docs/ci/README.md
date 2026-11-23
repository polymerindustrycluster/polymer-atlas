# CI and Pages

Both workflows are live in `.github/workflows/`. Edit them there; there is no second copy.

- **`validate.yml`** runs on every pull request and every push to `main`:
  - `scripts/validate.py`;
  - the personal-account URL guard on `tasks/` and `docs/` (`scripts/check_account_urls.py`, since 2026-11-19);
  - the row-loss guard;
  - on pull requests, two evidence binding steps (`scripts/check_evidence_binding.py`, since 2026-11-22). **These
    steps are early feedback, not authoritative:** `validate` runs the PR's own copy of the checker, so a PR that edits
    the checker or the workflow changes the result. The authoritative run is a `pull_request_target` workflow that runs
    `main`'s checker with `--tree <PR checkout>` (owned by the working-rules lane, PR #466). **Condition:** the binding
    gate decides nothing until that trusted workflow is merged and made a required check under the ruleset's strict
    (branch up to date) policy; until then these steps are early feedback only.
    - **The gate is a floor, not proof** (owner ruling 2026-11-22, "strict floor, then merge"). PASS means every
      mechanical leg matched positively. Admitting a data PR still needs two model families reading its rows. A
      counterexample found after merge becomes a test and a fix as a follow-up.
    - **`--new-since`** gates every evidence row the PR adds, and every row whose content changed in any column.
      - **PASS** (structured sources only) needs every leg to match: the quoted operator is a held name, whole, or a
        held name plus corporate-form words only, with no parenthetical or trailing text dropped, never a recorded
        parent's name, and never a site-name part made only of generic labels. For a site, `scripts/matching.py`
        `same_street()` holds; any suite, unit, room, floor or building stated on either side is stated and equal on
        both; and `same_locality()` holds (state on both sides and equal, and the city or the ZIP5 equal). The same
        quote must not pass on a second site record. For a headquarters address, an entity-address source states the
        record's city and state.
      - **FAIL**: a demonstrated conflict (another name, street, unit, city or state). No waiver.
      - **HELD** (`held_for_reading:<legs>`): a leg did not match positively and nothing conflicts. It fails the PR
        like a FAIL; the difference is only which reader's queue the row goes to.
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

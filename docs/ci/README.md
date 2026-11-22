# CI and Pages

Both workflows are live in `.github/workflows/`. Edit them there; there is no second copy.

- **`validate.yml`** runs on every pull request and every push to `main`:
  - `scripts/validate.py`;
  - the personal-account URL guard on `tasks/` and `docs/` (`scripts/check_account_urls.py`, since 2026-11-19);
  - the row-loss guard;
  - on pull requests, three evidence binding steps (`scripts/check_evidence_binding.py`, since 2026-11-22). **These
    steps are early feedback, not authoritative:** `validate` runs the PR's own copy of the checker, so a PR that edits
    the checker or the workflow changes the result. The authoritative run is a `pull_request_target` workflow that runs
    `main`'s checker with `--tree <PR checkout>` (owned by the working-rules lane, PR #466).
    - **`--new-since`** gates every evidence row the PR adds, and every row whose content changed in any column.
      - **PASS** (structured sources only): the quoted operator is a held name, compared whole and never split on
        commas. For a site, `scripts/matching.py` `same_street()` holds; this is the same street test the
        last-activity derivation uses. For a headquarters address, an entity-address source states the record's
        city and state.
      - **FAIL**: any FAIL fails the PR, and there is no waiver. A web quote can FAIL, for example when it is off the
        record's own site, when the civic number is not directly followed by the record's street word, or when it gives
        a different suite.
      - **READ_REQUIRED and UNINSPECTABLE**: a web quote is never PASS. These rows are admitted only one at a time,
        each by its own line in `tasks/<folder its created_by names>/BINDING_PROOF.csv`. Each line holds:
        - the capture: the row's `data/archive_links.csv` ref, or a repo file when the row has no archive line;
        - the sha256 of the capture's bytes;
        - the offset and length of the quote in the capture's text;
        - a reading: the verdict VERIFIED, the reader's model family and model (a different family from the folder
          README's "Built by:"), and one sentence on what ties the quote to this record.

        The reading is recorded, not verified.
    - **`--verify-proofs`** fetches each archived capture a proof cites, checks the digest, and finds the quote at its
      offset. A failed fetch exits 2: re-run the job, because a fetch failure is never a pass. A PR carries at most
      1,000 evidence rows (rule 5), which bounds the fetches.
    - **`--provenance-since`**: each `created_by` label must name exactly one `tasks/<folder>/`. That folder must hold a
      non-empty `check.py`, and a new label adds its own folder. The checker runs that `check.py` and it must exit 0.
      It runs last, on a copy of the tree, with no token in its environment. It can read the checkout's git history (`GIT_DIR`), so the authoritative workflow
      checks out with `persist-credentials: false`. It has no network only where `unshare -rn` works: with `--tree` the
      checker refuses to run a `check.py` without that and exits 2; in this job it runs anyway and the log says "network
      NOT isolated". Whether the hosted runner allows `unshare -rn` is unverified.
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

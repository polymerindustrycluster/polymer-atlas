# CI and Pages

The workflows are live in `.github/workflows/`. Edit them there; there is no second copy.

- **`validate.yml`** runs on every pull request and every push to `main`:
  - `scripts/validate.py`;
  - the personal-account URL guard on `tasks/` and `docs/` (`scripts/check_account_urls.py`, since 2026-11-19);
  - the row-loss guard;
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
- **`nightly-watch.yml`** runs once a day (11:17 UTC) and on demand. It runs `scripts/nightly_watch.py` over the last 24
  hours on `main` and fails the run, so GitHub emails the owner, when a bulk add, a data PR without two "**Review
  record**" comments, a merge before `validate` finished, a red `main`, a flat PIC-18 outcome, an unexplained evidence
  label or undeclared row loss shows up (rules a to g in the script's docstring). A second job, the only one with
  `issues: write`, opens or updates one issue titled "Nightly watch: findings". What it cannot see, and what the owner
  must set for the email to arrive: `tasks/nightly-watch-2026-11-22/README.md`.

- **`pr-rules.yml`** (since 2026-11-22) runs on `pull_request_target` (a PR opened, pushed to, reopened or marked ready).
  It runs the checker and the workflow as they are on the base branch and never executes anything from the PR; it
  reads no PR comment and no review record. It is a separate workflow from `validate.yml`. Review (working rules 1 and
  4, AGENTS.md section 2a) is practice and is not checked here. It publishes two check runs on the PR head:
  - **`pr-rules`** (`scripts/check_pr_rules.py`, working rules 5 and 6):
    - a PR adds at most 1,000 evidence rows and 1,000 new registry identities (org_id, registry, registry_id, site_id)
      unless it adds a `DECISIONS.md` line with the words "size waiver" and `branch=<its complete branch name>`;
    - a PR that touches `data/` fails while any `created_by` label on `main` is neither in
      `tasks/working-rules-2026-11-22/audit_baseline.txt` nor named by a valid `tasks/<folder>/AUDIT.md` on `main`
      (lines `Label:`, `Result: PASS|FAIL`, `Sample:`, `Reviewers:`), or whose audit says FAIL;
    - a PR that adds evidence rows or registry links adds `tasks/<folder>/INPUTS.sha256` (`<sha256>  <path>`, a file
      below `raw/` or `provenance/`, or an existing repo file); format only, a reviewer checks the hashes against the
      shared store.
  - **`binding-gate`** (rules 2 and 3): when `scripts/check_evidence_binding.py` exists on `main`, the job checks out the
    PR merge result as data into `./pr` (both checkouts with `persist-credentials: false`, job `permissions: {}`;
    nothing from the PR tree is executed) and runs main's script twice with `--tree pr`: `--new-since origin/main` and
    `--provenance-since origin/main`. Until the script is on `main` the check run says "gate not yet on main: nothing
    was checked" and passes; every other step that cannot run its check fails. A separate job, which never touches PR
    code, posts the result.

  Every check prints what it inspected and what it could not; whatever it could not inspect, including a failed read of
  a tracked git object, fails the run. Rules 2 and 3 are `scripts/check_evidence_binding.py` (PR #467), documented with
  that script. The planted cases and the limits are in `tasks/working-rules-2026-11-22/README.md`. Locally:
  `python3 scripts/check_pr_rules.py --pr <number>` (needs `gh`).

  **Replay is not run in hosted CI.** A PR that adds evidence rows or registry links gets a `NOT RUN` line for each
  `tasks/*/check.py` it adds or changes, and for the sentence "source replay not run in hosted CI: needs the shared
  store; it is run by the reviewers and recorded in the Review record comment"; the `pr-rules` title then ends "source
  replay NOT RUN in hosted CI". The conclusion is still decided by the other rules.

  **Required since 2026-11-22** (ruleset "main: require validate", id 27269436): `validate`, `pr-rules` and `binding-gate`
  are required status checks and the strict (branch up to date with `main`) policy is on, so the audit gate of AGENTS.md
  section 2a, rule 5 is re-judged against current `main` before a merge. Exactly one check run is named `pr-rules` (the
  job that posts it is `evaluate`) and exactly one is named `binding-gate` (posted by `publish-binding-gate`; the job
  that does the work is `gate-run`). If `gate-run` fails on a fresh head, nothing is posted under that name and the merge waits; a repeat run on a head that already has a green `binding-gate` posts no replacement. While
  `scripts/check_evidence_binding.py` is not on `main`, the posted check is titled "binding-gate: NOT CHECKED (gate not
  yet on main)": a pass that inspected nothing.

Preview the site locally with
`python3 scripts/build_pages.py && python3 -m http.server -d build/pages 8000`, then open http://localhost:8000.

Until 2026-11-02 the agents' GitHub App could not write workflow files, so this folder held proposed copies for the
owner to commit. That is why AGENTS.md §2 keeps a historical campaign-mode rule. Campaign mode was retired on
2026-11-03 (owner battery B-CAMP).

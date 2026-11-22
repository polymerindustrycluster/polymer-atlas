# CI and Pages

Both workflows are live in `.github/workflows/`. Edit them there; there is no second copy.

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

- **`pr-rules.yml`** (since 2026-11-22) runs `scripts/check_pr_rules.py` on `pull_request_target` and on every PR
  comment created, edited or deleted, and publishes the result as the check run `pr-rules` on the PR head. It checks
  out the base branch only and never runs anything from the PR, so a PR that changes the checker or the workflow is
  judged by the version on `main` (and needs one independent review record). It is a separate workflow from `validate.yml`. The check covers working rules 1, 4,
  5 and 6 (AGENTS.md section 2a):
  - the PR body carries `Built by: <harness>, <model family>`; review is tiered by risk (owner ruling 2026-11-22): a
    PR that changes any file under `data/` carries `**Review record**` comments from two model families (derived from
    the model named), every other PR one record from a family other than the builder's; each is APPROVE at the current
    full head SHA with a "What it checked" line, the latest record per verifier governing;
  - a PR adds at most 1,000 evidence rows and 1,000 registry links (new registry identities: org_id, registry,
    registry_id, site_id) without a "size waiver" line added to `DECISIONS.md` that names its exact branch; a PR that
    touches `data/` fails while any `created_by` label on `main` is neither in
    `tasks/working-rules-2026-11-22/audit_baseline.txt` nor named by a valid `tasks/<folder>/AUDIT.md` on `main`
    (lines `Label:`, `Result: PASS|FAIL`, `Sample:`, `Reviewers:`), or whose audit says FAIL;
  - a PR that adds evidence rows or registry links adds `tasks/<folder>/INPUTS.sha256` (`<sha256>  <path>`, a relative
    file path under `raw/`, `provenance/` or an existing repo file); format only, a reviewer checks the hashes against
    the shared store.

  The same workflow has a second check run, `binding-gate` (rules 2 and 3): when `scripts/check_evidence_binding.py`
  exists on `main`, the job fetches the PR head as data into a plain directory (`check_pr_rules.py --export-tree`) and
  runs main's script against it with `--tree <dir>` and `--new-since <merge-base>` and `--provenance-since <merge-base>`.
  Until the script is on `main` the check run is neutral and says "gate not yet on main". The gate's provenance check
  executes one PR-supplied file, `tasks/<folder>/check.py`, so this job has `permissions: {}`, keeps no credential, and
  runs the gate as an unprivileged user in a network namespace with no network (`unshare --net`), proving the isolation
  first. If the runner cannot isolate, the gate is **not executed there**: the check run is neutral with "SKIPPED", and
  the `validate` job is the only place the gate runs. A separate job, which never touches PR code, posts the result.
  The two flags and `--tree` are the interface assumed from PR #467; the job fails closed if `--tree` is missing.

  Every check prints what it inspected and what it could not; whatever it could not inspect, including a failed read of
  a tracked git object, fails the run. Rules 2 and 3 are `scripts/check_evidence_binding.py`, documented with that
  script. The planted cases and the limits are in `tasks/working-rules-2026-11-22/README.md`. Locally:
  `python3 scripts/check_pr_rules.py --pr <number>` (needs `gh`). The ruleset requires `pr-rules` with strict mode on;
  see the PR that added it.

Preview the site locally with
`python3 scripts/build_pages.py && python3 -m http.server -d build/pages 8000`, then open http://localhost:8000.

Until 2026-11-02 the agents' GitHub App could not write workflow files, so this folder held proposed copies for the
owner to commit. That is why AGENTS.md §2 keeps a historical campaign-mode rule. Campaign mode was retired on
2026-11-03 (owner battery B-CAMP).

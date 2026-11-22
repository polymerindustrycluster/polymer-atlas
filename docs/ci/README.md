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

- **`pr-rules.yml`** (since 2026-11-22) runs `scripts/check_pr_rules.py` on every pull request and again when a PR
  comment that contains "Review record" is added. It is a separate workflow from `validate.yml`. The check named
  `pr-rules` covers working rules 1, 4, 5 and 6 (AGENTS.md section 2a):
  - the PR body carries `Built by: <harness>, <model family>`; a PR that touches `data/` or `scripts/` carries two
    `**Review record**` comments from two model families, each APPROVE at the current head SHA (one record for any
    other PR), and at least one reviewer is not from the builder's family;
  - a PR adds at most 1,000 evidence rows and 1,000 registry links without a "size waiver" line in `DECISIONS.md`
    that names its branch; a PR that touches `data/` fails while any `created_by` label on `main` is neither in
    `tasks/working-rules-2026-11-22/audit_baseline.txt` nor named in a `tasks/<folder>/AUDIT.md` on `main`;
  - a PR that adds evidence rows or registry links adds `tasks/<folder>/INPUTS.sha256` in the `<sha256>  <path>` format
    (format only; a reviewer checks the hashes against the shared store).

  Every check prints what it inspected and what it could not; whatever it could not inspect fails the run. Rules 2
  and 3 are `scripts/check_evidence_binding.py`, documented with that script. The planted cases and the limits are in
  `tasks/working-rules-2026-11-22/README.md`. Locally: `python3 scripts/check_pr_rules.py --pr <number>` (needs `gh`).

Preview the site locally with
`python3 scripts/build_pages.py && python3 -m http.server -d build/pages 8000`, then open http://localhost:8000.

Until 2026-11-02 the agents' GitHub App could not write workflow files, so this folder held proposed copies for the
owner to commit. That is why AGENTS.md §2 keeps a historical campaign-mode rule. Campaign mode was retired on
2026-11-03 (owner battery B-CAMP).

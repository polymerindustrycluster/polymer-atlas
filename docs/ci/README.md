# CI and Pages

The workflows are live in `.github/workflows/`. Edit them there; there is no second copy.

- **`validate.yml`** runs on every pull request and every push to `main`:
  - `scripts/validate.py`;
  - the personal-account URL guard on `tasks/` and `docs/` (`scripts/check_account_urls.py`, since 2026-11-19);
  - the row-loss guard;
  - on pull requests, two evidence binding steps (`scripts/check_evidence_binding.py`, since 2026-11-22). **These
    steps are early feedback, not authoritative:** `validate` runs the PR's own copy of the checker, so a PR that edits
    the checker or the workflow changes the result. The authoritative run is a `pull_request_target` workflow that runs
    `main`'s checker with `--tree <PR checkout>` (`pr-rules.yml`, check run `binding-gate`, merged with PR #466 at a7053b2b). **Condition:**
    the binding gate decides nothing until `binding-gate` is made a required check under the ruleset's strict (branch up
    to date) policy, which are repository settings (see below); until then these steps are early feedback only.
    - **The gate is a floor, not proof** (owner ruling 2026-11-22, "strict floor, then merge"). PASS means every
      mechanical leg matched positively. Admitting a data PR still needs two model families reading its rows. A
      counterexample found after merge becomes a test and a fix as a follow-up.
    - **`--verify-proofs`** (also `--new-since`) gates every evidence row the PR adds, and every row whose content changed in any column.
      - **PASS for structured sources** needs every leg to match: the quoted operator is a held name, whole, or a
        held name plus corporate-form words only, with no parenthetical or trailing text dropped, never a recorded
        parent's name, and never a site-name part made only of generic labels. For a site, `scripts/matching.py`
        `same_street()` holds; any suite, unit, room, floor or building stated on either side is stated and equal on
        both; and `same_locality()` holds (state on both sides and equal, and the city or the ZIP5 equal). The same
        quote must not pass on a second site record. For a headquarters address, an entity-address source states the
        record's city and state.
      - **FAIL**: a demonstrated conflict (another name, street, unit, city or state). No waiver.
      - **HELD** (`held_for_reading:<legs>`): a leg did not match positively and nothing conflicts. It fails the PR
        like a FAIL; the difference is only which reader's queue the row goes to.
      - **PASS for own-site web quotes** requires a per-row proof and capture replay under SCHEMA §4.13.
        Missing proof, a fetch error, or a replay mismatch blocks admission.
      - **READ_REQUIRED and UNINSPECTABLE** fail the PR. Hold these rows as leads until they can be proved.
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
- **`nightly-watch.yml`** runs once a day (11:17 UTC) and on demand. It runs `scripts/nightly_watch.py` over the last 24
  hours on `main` and fails the run, so GitHub emails the owner, when a bulk add, a data PR without two "**Review
  record**" comments, a merge before `validate` finished, a red `main`, a flat PIC-18 outcome, an unexplained evidence
  label or undeclared row loss shows up (rules a to g in the script's docstring). A second job, the only one with
  `issues: write`, opens or updates one issue titled "Nightly watch: findings". What it cannot see, and what the owner
  must set for the email to arrive: `tasks/nightly-watch-2026-11-22/README.md`.

- **`pr-rules.yml`** (since 2026-11-22) runs on `pull_request_target` (a PR opened, pushed to or reopened). It does not run when a PR is marked ready: that does not change the head, and a second run on the same head could be cancelled while queued, leaving the posted `pr-rules` and `binding-gate` check runs in a cancelled check suite that blocks the merge (owner ruling 2026-11-23). Reopening a PR, re-running a run by hand, or moving the branch back to a commit already tested can still repeat work on one head; if a merge is blocked with every required check green, push a new commit. A merge blocked for another reason, such as a branch behind `main` under the strict policy, needs its own remedy.
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
  - **`binding-gate`** (rules 2 and 3) checks out the PR merge result as data into `./pr`. Both checkouts use
    `persist-credentials: false`, and the job has `permissions: {}`. It runs main's checker with `--tree pr` in
    two modes, `--verify-proofs origin/main` and `--provenance-since origin/main`. If the base checker is missing
    or cannot run either mode, the published check fails with `cannot_inspect`. A separate trusted job posts
    the result.

  Every check prints what it inspected and what it could not; whatever it could not inspect, including a failed read of
  a tracked git object, fails the run. Rules 2 and 3 are `scripts/check_evidence_binding.py` (PR #467), documented with
  that script. The planted cases and the limits are in `tasks/working-rules-2026-11-22/README.md`. Locally:
  `python3 scripts/check_pr_rules.py --pr <number>` (needs `gh`).

  **Packet replay uses the shared store.** A PR that adds evidence rows or registry links gets a `NOT RUN` line for each
  `tasks/*/check.py` it adds or changes, and for the sentence "source replay not run in hosted CI: needs the shared
  store; it is run by the reviewers and recorded in the Review record comment"; the `pr-rules` title then ends "source
  replay NOT RUN in hosted CI". The conclusion is still decided by the other rules.

  **SCHEMA §4.13 structured address routes.** In a map-listing evidence row, use
  `source_class=platform_category`, `source_ref=<google-places|overture-maps-places> <place ID>`, and
  `claim_detail=<street>; quote: name: <operator>; street: <street>; city: <city>; state: <US state code>`.
  The entire `notes` cell is `capture_sha256: <digest>; second_source: <EVD-ID or lead: exact base note>`.
  A cited evidence row must already be held for the same site. An address quoted from the operator's site must give
  the street and locality as one address. Held notes can cite a full `Street (per <origin>): <street>` clause or a dated
  strong EPA FRS facility address note. Google or Overture counts as a different origin only when the note identifies
  that provider. Other accepted lead origins are OSHA, EPA, Ohio EPA, SBA PPP and SAM.gov. Incomplete or ambiguous
  provenance is held. The base street must be blank. Keep the listing's city and state and use its exact street in the
  merge tree. Leave `address_role` empty for the supported provider formats, which give an address without stating
  its role. A mailing, agent, registered-office or private-looking street cannot qualify.

  The hosted gate compares the quoted fields only. The fill packet pins the raw capture in `INPUTS.sha256`. The
  lane's `check.py` and reviewing family replay that file from the shared store. For a JSON capture, the gate also
  offers a local check via `--verify-proofs <base> --map-store <shared store root>`. Store the Google Place JSON or
  Overture place GeoJSON projection at `raw/map-listings/<provider>/<digest>.json`. It must contain one US address.
  Capture reads are by exact SHA-256. Parquet inputs are replayed in the fill packet's `check.py`.

  For a filing name variant, append the `(OSHA filing name)` or `(EPA filing name)` marker to the new alias and use
  `claim_detail=trade_names + <marked alias>; quote: <filing quote>`. Cite a specific filing record in `source_ref`.
  The gate checks the operator field, the distinctive words of a base-held organization name, parent names, the
  private-address screen and one base-held street with the exact city and state. It also requires one passing evidence
  row per marked addition. The second model family checks the original filing and records its verdict on the PR.

  **Required since 2026-11-22** (ruleset "main: require validate", id 27269436): `validate`, `pr-rules` and `binding-gate`
  are required status checks and the strict (branch up to date with `main`) policy is on, so the audit gate of AGENTS.md
  section 2a, rule 5 is re-judged against current `main` before a merge. Exactly one check run is named `pr-rules` (the
  job that posts it is `evaluate`) and exactly one is named `binding-gate` (posted by `publish-binding-gate`; the job
  that does the work is `gate-run`). If `gate-run` fails on a fresh head, nothing is posted under that name and the merge waits; a repeat run on a head that already has a green `binding-gate` posts no replacement.

Preview the site locally with
`python3 scripts/build_pages.py && python3 -m http.server -d build/pages 8000`, then open http://localhost:8000.

Until 2026-11-02 the agents' GitHub App could not write workflow files, so this folder held proposed copies for the
owner to commit. That is why AGENTS.md §2 keeps a historical campaign-mode rule. Campaign mode was retired on
2026-11-03 (owner battery B-CAMP).

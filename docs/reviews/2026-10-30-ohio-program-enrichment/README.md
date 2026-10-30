# Five Ohio program enrichments — reviewed application packet

**PR #3 is a docs-only packet, not applied canonical data.** Large-file GitHub
connector transport stalled twice; neither attempt reached a commit/ref update.
This compact exact patch preserves the reviewed changes without claiming they
landed. Merging this PR alone does not enrich the canonical tables.

Scope: PROG-000001, 000002, 000008, 000014, 000024; five VERIFIED scoped
program enrichments, one generated Shawnee ecosystem ORG-001298 URL correction,
and 20 evidence rows. Five program tiers remain A; ecosystem tier remains C and
its last_verified remains unchanged. No CIP/completions inferred. Sources,
before/after values and qualifications are in proposals.json and patch evidence.
PENRA held because source access failed; failure is not closure evidence.

## Integrator handoff — no blind application

Base is main9d7a33f (AGENTS-only successor to research base3036121). Patch is
exactly the independently reviewed local7431c32 canonical diff. Manifest gives
SHA-256 of the patch and each before/after file. Read current AGENTS/schema/queue
first. Fetch latest main and all open PRs. Confirm every before hash and patch
hash; if any mismatch, STOP and re-adjudicate against current data. Never use a
fuzzy/partial apply or overwrite concurrent evidence. Review provisional
EVD-003713–EVD-003732 against latest maximum and open PRs; these are NOT globally
reserved. If occupied, designated integrator must reallocate and update packet,
manifest and tests together. PR #2 uses CAP IDs only; #1/#4/#5 allocate none.

On a clean isolated integration branch, after the checks and contemporaneous
pre-pass backups outside the checkout:

```
git apply --check docs/reviews/2026-10-30-ohio-program-enrichment/proposed-data.patch
git apply docs/reviews/2026-10-30-ohio-program-enrichment/proposed-data.patch
python3 scripts/validate.py
python3 scripts/build_sqlite.py
```

Confirm every after hash, review the exact diff, journal the application, and
publish only as a reviewed PR. Never commit generated SQLite/exports or push
main. The original local application predated observing amended AGENTS; original
blobs were backed up from immutable3036121 afterward, not falsely represented
as contemporaneous disk backups. Codex-dot is packet integrator of record.

## Verification and merge coordination

The full canonical candidate passed independent source review, validator and
SQLite build (3732 evidence records); an isolated combined rehearsal with other
four PRs passed43 tests and retained497 capabilities. The packet-only tree also
passes validator/build. Patch was apply-checked and reconstructed hashes tested
on a clean temp copy; see review report. Current CSV files in this PR are
unchanged. Append-only task queue conflicts must preserve all lane sections.
This branch-local `in-pr` claim is visible, not a lock on main.

VERDICT: REFUTE (Codex/OpenAI, PR #193)

Reviewed pinned 0f0551f3add23fae838f67176f9a9ed5f1e33aa2 on own review-193-clerk-codex-1 checkout. Three demonstrated findings. Complete SPEC, README, brief, producer, tests, real-history checker, packet manifest and check records inspected. implementation.patch reconstructs both reviewed script files exactly; all 11 manifest artifact digests match. No lane checkout edits, product authorship, push or merge.

## 1. P1 — Final output-file symlinks escape the advertised write boundary

scripts/build_changelog.py:215–217 resolves and checks only the output directory. Lines249/251 open the two filenames normally and follow symlinks.

Reproduction uses only disposable Git fixtures. First generate a valid feed. Replace build/changelog/CHANGELOG.md with a symlink to an existing sentinel file outside the fixture repository, leaving build/ and changelog/ ordinary directories. build(repo,'main') succeeds and overwrites that outside file. Repeating with feed.xml yields the same result. Both runs returned successfully; outside_overwritten=true twice. The existing test covers only a symlink at build/ and misses the two leaves.

This contradicts the claimed “Only build/changelog/ is written” boundary and the explicit output-symlink acceptance criterion. Validate the actual output targets and use a write strategy that cannot follow a final-file link outside the allowed directory; add both leaf cases. This is a demonstrated file-clobber risk, not a claim that an actual user file was overwritten. All sentinel files were temporary reviewer fixtures.

## 2. P2 — An output failure leaves a partially updated artifact pair

scripts/build_changelog.py:249 replaces Markdown before attempting the Atom write at251. Generate both outputs, commit an actual status change, then chmod the existing feed.xml to0444 while its directory remains writable. On this host (uid501), the next build raises PermissionError on feed.xml after updating CHANGELOG.md. The old XML remains unchanged while the Markdown describes the new snapshot.

This directly violates the brief's requirement that fail-closed output errors preserve previous generated artifacts. Source-validation errors correctly preserve outputs, but output errors do not. Stage and validate both outputs and handle replacement failures so the previous pair survives a failed generation. Add a real output-failure control; testing source errors alone does not establish this property. A replacement strategy may legitimately succeed on a read-only old file when the directory permits replacement; the required outcome is a consistent successful pair or an unchanged pair on failure.

## 3. P2 — Arbitrary ID prefixes bypass the public-output allowlist

scripts/build_changelog.py:41 and79–81 accept any uppercase alphanumeric/underscore prefix before six digits. A throwaway organization row whose org_id is PRIVATE_CRM_ACQUISITION_TARGET-000002 passes the purported immutable-ID check and is emitted verbatim in both Markdown and Atom. A valid equipment-format EQP-000002 also passes in organizations and is reported as a newly created organization row.

These are fabricated reviewer markers, not real private information. The demonstrated issue is that arbitrary source text can masquerade as an allowed public ID. SCHEMA§4.4 specifies ORG-###### and the existing validator enforces that at scripts/validate.py:246; other tables have their own declared prefixes. The feed runs over historical snapshots without running that validator, so it must enforce the table's actual ID namespace (with any justified historical exceptions explicit) before copying IDs. Add unknown-prefix and valid-prefix/wrong-table negative fixtures and verify existing artifacts remain unchanged on rejection.

## Independent reproduction

From the reviewed checkout:

`python3 /Users/johnswanson/.bb/thread-storage/thr_9i2c6byhcz/2026-11-06-atlas/reviews/193-clerk-codex-1/clerk193-adversarial.py`

This reuses the lane's disposable real-Git fixture setup but adds independent cases. Complete results are in clerk193-adversarial-results.json:
- leaf_symlink_CHANGELOG.md: success, outside_overwritten=true;
- leaf_symlink_feed.xml: success, outside_overwritten=true;
- readonly_xml_preserves_previous_pair: PermissionError, changed_files=[CHANGELOG.md];
- arbitrary prefix and wrong-table prefix: accepted, published_in_both=true in both cases.

## Ground truth and inspected scope

- Unit suite: five tests PASS.
- Full scripts suite: 226 passed,1 skipped,45 subtests passed in58.85seconds.
- Validator: zero errors;36,720 evidence rows on reviewedHEAD. Existing warnings only.
- Row-loss guard: PASS at merge-base8a5821b37e308a31b22ed57015edb54636641f1c. Branch lacks the installed guard; executed the exact origin/agent/claude-code/row-loss-guard version with __file__ rooted at this checkout, without editing its logic.
- Data/schema/workflow diff is empty. Only the two new scripts and task packet are changed. No IDs or canonical data rows are created; data-row sample, source tier/dedupe and evidence allocation checks are therefore inapplicable. Neither excluded federal-frame file is in the diff. Checkout remained clean.
- The complete implementation patch matches current source byte-for-byte. All11 listed artifact hashes validate; review-packet.json itself hashes542edfb6f6ac546486232e3d9ee3b263a4f61b24796ea8da3cdc812f4b68295c.

Re-ran the real-history checker for its recorded c2674712c0c9f8aeefac9179597b8a4c6e5eda5f snapshot. Only its chosen ref and JSON report destination were redirected in a temporary copy, to reproduce the pinned claim without overwriting the committed task report; generator/check logic was unchanged. Both complete passes ran successfully. Results exactly match the packet:214 data-history entries=78PR+136direct, PR140 equipment34, PR143 sites18, PR133 ORG000132 C→A, evidence balance36,606, Atom214 unique stableIDs, contact scan PASS, deterministic byte replay PASS. First generation48.23seconds. Both output hashes match the packet exactly:
- feed.xml5eb7d7ad95711090c8348bc1bfe3e8cc072b3cf3816b98e3b6bc6de3cd2f7335
- CHANGELOG.mdab8d4f6ab75659eb4239c88071e671c719b681dcfb4d8dbb5b3c73cfa399cfa3

Read and exercised the supplied cases covering first-parent net merge changes, squash/direct attribution, unmerged exclusion, shard and unique org/ecosystem transfers, legacy simultaneous collisions, registry/person composites, archive grain, restorations versus creations, blank transitions, per-target new EVD counts, unknown-value redaction, conflicting projections, bad headers/IDs, shallow history and directory symlink refusal. The code's counting policy matches those stated cases; no additional counting defect demonstrated. Normal-column subject/author/notes/contact injections remain excluded; finding3 is the uncovered ID path.

Limits: no hosted publication, feed-reader UI, external Atom validator or actual usage tested, as explicitly out of scope. Real-history reproduction uses the requested pinned snapshot, not the subsequently advancing origin/main. The three defects affect output boundary, failure consistency and allowlist enforcement and remain blockers despite the passing nominal checks.

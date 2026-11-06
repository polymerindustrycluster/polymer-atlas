# REFUTE B-12 SEC own-filer identity completion

Claim: 103 frozen held organizations with ticker/public_parent signal and no own SEC_CIK have exact verdict coverage; 67 own source-verified CIK links append, 36 remain uncertain. Only data/registry_links.csv and this task packet change. No organization, status, tier, derived qualifier or parent edits. No evidence IDs; SCHEMA §4.8 registry identity provenance is carried in match_basis/source receipts, not §4.13 record_table.

Try to disprove the result. In particular, audit any legal entity versus parent/brand/recycled-ticker confusion, source-entry projection corruption, skipped frame member, false no-hit, stale ticker misinterpretation, overwriting an inherited registry row, or partial writes after a late conflict. STERIS/PLC, ExxonMobil Holdings, Synventive/Barrick, Gates, Afton, Oxy, Legend, Valmont, Lippert and Carlstar remain held. CSW versus held CSWI is an explicit same-name issuer match; held organization columns are unchanged. Pentair and GrafTech held names lack a legal form; no conflicting form is normalized away.

The complete official ticker-file snapshot is now preserved verbatim with source manifest: SHA76b4b2abb9f7dd0e9cff38e2f20336952bb41806057b2dd1033e244f3e1faec2,796507bytes,10409associations/8004distinctCIKs. Initial partialweb retrieval is historical only. All73oldcandidate records/76literalreceipt tokens match the new completefile exactly. Three previously unresolved ownissuers(Huntsman/Stepan/PreformedLineProducts) now pass fresh direct company checks; original64linkdicts/11collisionholdsunchanged. Missing associations remain uncertain because thisfile is not allEDGARfilers. Official SEC submissions JSON was fetched directly and raw name tokens checked before projection; fresh independent refetch is encouraged. Controller explicitly authorized the source-system record in place of a rendered company page; README and BOARD record this superseding instruction. No browse-page identity is claimed as seen.

Run:

    python3 tasks/sec-cik-links-2026-11-06/check.py
    python3 tasks/sec-cik-links-2026-11-06/test_build.py
    python3 scripts/validate.py
    python3 scripts/check_row_loss.py --base origin/main
    git diff --check

Rebuild packet CSVs with build.py; replay --apply is byte-identical. fetch.py --known independently calibrates Apple/IBM/Sherwin/Avient; fetch.py without arguments refreshes all 76 candidate company records. Tests include four real negative entity cases, three corrupted source fields, two broken frame shapes and a conflict on the final proposed row that must cause zero writes. Existing legacy registry writer is reused; the single-ID shard writer cannot handle registry composite keys. No shared script changes.

Review limits to preserve: no comprehensive foreign ticker search; 25 unresolved source candidates; no subsidiary exhibit/current-ownership or liveness audit; no claim to repair the held ticker fields. Please return APPROVE or REFUTE with concrete findings and limits. Draft only; controller owns merge/status.

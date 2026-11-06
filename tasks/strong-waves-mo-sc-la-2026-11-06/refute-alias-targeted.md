# Targeted R-grok-1 re-review — PR141

Prior finding: EVD-161300 (and analogous new-org own_site rows) still stated federal aliases while citing operator pages.
The controller explicitly authorized regenerating these not-yet-on-main lane observations in place, same IDs, rather than
retaining the false source attribution. This supersedes our earlier local-append-only interpretation for this correction.
No evidence row present on main was edited/deleted.

Fix: build.py new-org existence now emits `legal_name {name}; website {own}` only. No federal aliases in any own-site
observation. Source-specific government alias observations and trade_names remain intact. EVD-161300 now reads:
`legal_name KOLLER-CRAFT PLASTIC PRODUCTS; website https://www.koller-craft.com/about`.
EVD-166300 remains the actual EFAST2 KOLLER ENTERPRISES registrant witness.

Executable gate: check.py asserts no row created_by atlas-L3-strong-mo-sc-la whose source_class is own_site contains
`federal registrant aliases`. All280 lane observations checked, zero matches. validate.py0errors, check.pyPASS;
19sites/15org/280EVD and T3 unchanged. Main bdb8b98 merged; conflicting evidence_OH taken from main then all three state
builders replayed, no hand merges. Earlier scope/plant/parent quotations and parent flag unchanged, already checked by you.

Please APPROVE or REFUTE this finding's cure on current PR head. Prior approvals do not cancel a valid finding.

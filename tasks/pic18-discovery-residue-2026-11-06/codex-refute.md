VERDICT: REFUTE — Codex (OpenAI), PR #159, 9a0622c8845f18b10bbecd329140a210348a02a9

Reviewer atlas-clerk-codex-4; lane L14, reply-to thr_yk63cjf9xu. Blocking findings: 1. Latest5f0eff4 was fetched during review; its diff from reviewed9a0622c changes only README.md and grok-review.md. Per lane instruction this technical verdict remains pinned to9a0622c; canonical data and implementation are unchanged by that documentation update.

1. P2 — New SITE-013100 lacks its mandatory parent/operator-linkage evidence row.
   The new site assigns org_id=ORG-009600. SCHEMA.md §4.13 lane-brief contract explicitly lists sites.parent (the org_id linkage) among must-have claims, lines1623–1627, and says a verdict without evidence rows for its must-have claims does not integrate. The complete evidence corpus contains only existence, scope, activity and address for SITE-013100 (EVD295004–295007); no parent row exists. The new-site create cannot use the legacy partial-restatement exception. The EPA permit visually supports the named applicant/facility relationship, so this is a missing typed observation, NOT a demonstrated wrong operator. Add an immutable parent evidence row explicitly supporting SITE-013100→ORG-009600 from the appropriate primary witness and update the packet/counts/check accordingly. Passing V25 does not prove absent claim types exist.

Reproduce from repository root:

    duckdb -csv -c "SELECT claim_type,count(*) FROM read_csv_auto('data/evidence_*.csv',all_varchar=true) WHERE record_table='sites' AND record_id='SITE-013100' GROUP BY claim_type ORDER BY claim_type;"

Observed: activity1, address1, existence1, scope1; parent0. Compare `sed -n '1605,1628p' docs/SCHEMA.md` and `tasks/pic18-discovery-residue-2026-11-06/creates_sites.csv`. No original evidence row should be repurposed or overwritten to fix the gap.

Ground truth independently run:
- `python3 scripts/validate.py | tail -3` with pipefail: OK, 0 errors.
- Row-loss guard from fetched `origin/agent/claude-code/row-loss-guard:scripts/check_row_loss.py`, imported with ROOT set to this repository and `--base origin/main`: OK; merge-base85b85600c7.
- `python3 tasks/pic18-discovery-residue-2026-11-06/build.py --raw-check`: PASS8/8 original evidence quotes,3/3 sources/hand-known answers plus fabricated negative. Within this command, verify_registry.py freshly retrieves all3FRS records, DOL PY2024 bulk, and Ohio EPA CRO joint-label witness:4/4 identities plus corroboration pass, no skipped source.
- `python3 tasks/pic18-discovery-residue-2026-11-06/check.py`: exact26census, all-CSV replay byte-identical, cross-shard reserved-ID collision and changed registry triple both rejected before writes; Form5500 snapshot screens IAC3names/0establishment matches and Ultimate0names.
- `git diff --check` passes. No federal-frame file in committed diff. Review did not mutate canonical data or implementation.

Independent raw-source attack:
Random seed15920261106 selected10 of19 newly added canonical rows: Convertapax FRS link, Dover FRS link, EVD295012,295008,295009,295010,295000,295003,295005,295001. Expanded beyond that sample: independently fetched9 URLs (Peak, Ohio EPA NOE, NEXXTA,3FRS records, CRO, Huron and Sandusky documents) with browser-UA curl; all9succeeded. All12non-DOL evidence quotations appear in whole-token order; the DOL observation was additionally verified by rerunning the live source checker against the exact ACK and source fields. Local files/results are under `/tmp/atlas-clerk4-pr159/`.

- Peak homepage explicitly states custom polyurethane manufacturing and describes production of climbing handholds. This supports existing Ring1/PU vocabulary; no specific molding method, NAICS, HQ or current-operation fact is invented.
- Fresh Ohio EPA NOE.pdf page277 was rendered and visually read. The Peak row gives Tuscarawas county, permit0GRN00360*BG, applicant Peak Performance Polymers, named Peak facility,9109StateRoute250NW,Strasburg, issue2025-01-10/expiry2030-01-09. Applicant and facility columns were not confused. Organization HQ remains unknown in residualUS; physical site is in OH. Permit validity is not treated as liveness. Source: https://dam.assets.ohio.gov/image/upload/epa.ohio.gov/Public/DSW/NOE.pdf
- Fresh FRS XML has exactly one record for each proposed ID:110000741822 Dover at3676DavisRdNW;110007706900 Convertapax onGundyDriveBldg3,Midvale;110000390390 Quest Automotive Products at2290ZimmermanRdSE,Gnadenhutten. Checked source RegistryId, name and locality against held sites. Convertapax's omitted street number is disclosed, and no new address fact is written.
- Fresh Ohio EPA CRO text jointly labels Quest Automotive Products/Catalyst Systems at2290Zimmerman with CRO2557 and RCRA OHD020626800. It supports historical facility identity, not a parent/operator/status change. Source: https://dam.assets.ohio.gov/image/upload/epa.ohio.gov/Portals/30/hazwaste/Historical_list_Facilities_CRO.pdf
- Fresh DOL filing check selects exactly ACK20251015110824NAL0008891586001 with Dover Chemical Corporation,3676DavisRoadNW,Dover, and EIN391205755. Link remains organization-grain, no site_id; no ICC parent inference. Source: https://askebsa.dol.gov/FOIA%20Files/2024/Latest/F_5500_2024_Latest.zip
- NEXXTA locations page supports150E.Longview and26injection presses; duplicate chain terminates at held SITE001473/ORG001426 without creating another site.
- Huron council minutes2024-06-25p6 independently rendered and visually read: municipal speaker describes the revenue lost when IAC closed. Sandusky2018-01-09memo independently read in2018-01-22agenda: explicitly vacant former Ultimate factory at1702Campbell and inspection/demolition history. These are historical outcomes, not WARN-only predictions; no held record status changes. The dated Form5500 snapshot gate passes, with its vintage limitation disclosed.

Dedupe, IDs, counts and preservation:
- Re-ran all four atlas.py dedupe steps and independently excluded the new IDs. Only self-matches for newORG009600/SITE013100; no prior domain, normalized-name, street, trade-name/notes hit. Ecosystem included in shared organization namespace. No accidental duplicate creation found.
- Controller BOARD continuation reservation is ORG009600–009699,SITE013100–013199,EVD295000–299999. All proposed immutable IDs are unique, in that block and absent from base. Registry composite keys are unique and correspond exactly to the four originally pinned candidates.
- Compared every row in six affected canonical files to main85b8560: unchanged prior rows247orgUS,2009sitesOH,1019EVDorgUS,2549EVDorgOH,4226EVDsitesOH,5373registrylinks. Additions exactly1Corg+1Csite+13evidence+4links; no edits/removals. Six packet/value CSVs byte-identical tocf6c9cd.
- Recomputed all prior STILL_UNCERTAIN inputs from L1–L4:26unique leads exactly equal inputs/verdicts;1VERIFIED,1DUPLICATE_OF,2REJECT,22STILL_UNCERTAIN.25entity/site leads plus1source-route unit are distinguished. All-status Ohio sites in PIC18counties1135→1136, not an active-establishment coverage claim.
- Evidence ceilings checked: new create observationsC; registry existenceB; government filing existenceA/B; no tier upgrades or unsupported status claims. The one missing new-site parent observation remains the blocker.

Limits: remaining22holds were reviewed as a reconciled packet but not all independently refetched. Historical closure screening uses the stated2026-11-01Form5500 snapshot; it is not a current all-filings absence claim. No merge, push, status adjudication or issue closure performed.

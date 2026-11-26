# Census audit of the SBA PPP size-band fills

Label: claude-code ppp-size-bands-rerun-2026-11-26
Result: PASS
Sample: Scripted census of all 93 merged evidence rows bearing the label, all 93 associated band fills, and the three newer-filing holds in PR #573.
Reviewers: atlas-review-573-codex, GPT-6.2 Astra (OpenAI). Claude Sonnet built the batch.

At main f921eba8, the Git tree IDs for data/ and tasks/ppp-size-bands-rerun-2026-11-26/ each matched the reviewed head 75bb5830 byte for byte. The squash title says “96 bands on 59 owners”. The merged data contains 93 bands on 56 owners. Against merge parent d4059b9b, all 48 organization employee_band_ohio cells and all 45 site employee_band_site cells were blank before the fill.

Both stored PPP inputs passed shasum -a 256 -c against INPUTS.sha256 before replay. Across all evidence shards, the 93 rows with the label matched the packet as a whole-row multiset. Each quote reproduced the stored borrower name, business type and address. Each source reference identified the correct loan number, file and release. Every selected loan met the business-type whitelist and the inclusive 2016-11-26 cutoff and was the latest qualifying match for its single-site Ohio owner. Independent §4.4 thresholds applied to JobsReported reproduced all 93 bands in the evidence and the corresponding filled cells.

ORG-000322, ORG-001394 and ORG-001710 remained held for newer_contradicting_filing. No fill or batch evidence row was admitted for these owners. Retired IDs EVD-483215, EVD-483238 and EVD-483271 were absent from all merged evidence shards.

The task checker's verify() returned zero findings on the merged tables. In a scratch copy, changing SITE-000011 from 10-49 to 5000+ returned band_mismatch and named SITE-000011, the planted band and the expected band. The pic18_unknown.py harness on f921eba8 counted 335 size-unknown owners among the 792 PIC-18 owners of active tier A–C sites.

## What this audit is not

The census verifies the merged batch against two checksum-pinned historical PPP inputs. It does not measure current employment, independently verify borrower-reported employment, or establish coverage of loans outside those inputs.

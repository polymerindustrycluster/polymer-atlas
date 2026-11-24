# Audit record: PIC-18 street fills from held OSHA filings (PR #547)

Label: codex pic18-street-gaps-2026-11-24
Result: PASS
Sample: 2 of 2 fills, replayed from the OSHA raw rows
Reviewers: Claude Sonnet 5.5 (atlas-p1-map-streets; a family other than #547's Codex builder); second family on PR #552

## What was audited

Done with a short script of my own, not the packet's `build.py` or `check.py`, on 2026-11-24:

- Both inputs in `tasks/pic18-street-gaps-2026-11-24/INPUTS.sha256` were found in the shared store and their SHA-256 matched (2 of 2).
- SITE-000650: the OSHA inspection row (`OSHA_inspection.zip`, chunk 6, line 185178) names `TOWER INDUSTRIES, LTD.` at `2101 9TH STREET SW`, Massillon, OH 44647, opened 2025-08-08. The street cell on main is `2101 9TH STREET SW`, equal to the filing. The site is named Tower Industries LTD in Massillon.
- SITE-000678: the OSHA ITA CY2025 row (line 174589) names `Wrap Tite - Site 3` at `6250 Camp Industrial Rd.`, Solon, OH 44139. The street cell on main is `6250 Camp Industrial Rd.`, equal to the filing. The site name is the filing's name.
- Both addresses are inspection-site or establishment street lines: no PO box, mailing, agent or registered-office wording. The cell diff of the #552 branch against main touches neither site, so main holds what #547 merged.

Not audited: the choice of the other 16 held sites (they changed nothing), the tier ceilings, and any business status.

# Targeted record fixes: 28 organizations (2026-11-04)

The repo owner requested this pass in session on 2026-11-03 and 2026-11-04. It covers 28 Ring 1–2 organizations
with sites in NE Ohio whose records had a blocking gap:
- tier C or U;
- a probable duplicate;
- no website;
- no processes and no materials.

Four packet lanes (`lanes/F1`–`F4`, `LANE_BRIEF.md`) gathered evidence from the companies' own sites, SEC filings and
dated press. The integrator re-fetched every quote raw (`rawcheck.csv`): 69 of 84 evidence quotes and 31 of 31
capability quotes were found verbatim.

## Applied (`build_fixes.py`), 25 organization records touched

| Change | Rows |
|-|-:|
| Evidence rows (`evidence_organizations_<TAG>.csv`, EVD-062464 onward) | 93: scope 49 (24 are capability-term quotes), existence 24, address 20 |
| `processes` / `materials` filled with SCHEMA §3.1 / §3.2 terms the page states | 15 cells |
| `verification_tier` restated under §4.1 / §4.13 (only raised; requires existence, address and scope all evidenced) | 11: C→A 5, B→A 5, U→A 1 |
| `last_verified` → 2026-11-04 | 25 |

EVD ids start at EVD-062464, because open PRs used up to EVD-023879 at build time.

## Held (`holds.csv`, 22)
- 11 failed the raw check, either not found or unfetchable. These include the three SEC 10-K quotes for
  Sherwin-Williams: sec.gov refuses scripted fetches.
- 5 address quotes name a different city from the record, so they are findings, not evidence (see below).
- 3 code claims are held: lanes found only SIC codes, and a SIC is not a NAICS claim.
- 2 duplicate rows.
- 1 website, for RFD Beaufort: the only site found is its parent Survitec's.

## Findings for the integrator (not applied: they need their own pass)
- **HQ on record looks wrong:**
  - BASF Corporation: its own page says Florham Park, NJ, not Greenville, OH.
  - BioVerde: the company's own site says Houston, TX, not Akron.
  - Pretium Packaging: its own page says St. Louis, MO, not Chesterfield.

  Correcting an HQ moves the record to another shard (Appendix C).
- **Ownership:**
  - Ashtabula Rubber is now part of ASC Engineered Solutions. Its gasket and seal division went to Grand River Rubber
    & Plastics (Rubber World, March 2023).
  - Continental announced the sale of ContiTech to Lone Star Funds, an unconfirmed search lead.
  - Flexsys was bought by One Rock Capital in 2021.
  - HC Companies was bought by Platinum Equity in 2023.
- **Scope questions:** Chemical Solvents (a solvent blender and waste handler) and Hy-Ko (keys, signs and numbers) state
  no polymer production on their own sites. Their ring and scope need review.
- **Duplicate verdicts (link or flag, never merged):**
  - AltraSet (ORG-001327) is a Mar-Bal division with the same office, so link it to Mar-Bal (ORG-000430) as its
    parent.
  - BASF (ORG-000698) and ORG-004037 are a 60/40 joint venture, a parent-child link.
  - DuPont Valley View (ORG-000313) is a sibling division to ORG-000042 and ORG-000805. Its tie to ORG-000785 is still
    uncertain, and an Exhibit 21 would settle it.
  - The Röchling records ORG-000550, ORG-000551 and ORG-004176 are sibling divisions, as already ruled on 2026-10-29.

## Checks
- Rehearsed on a temp copy of `data/`.
- Evidence was appended, and the cell edits applied with `scripts/apply_p1_crm_scrub.py`.
- `python scripts/validate.py` exits 0.

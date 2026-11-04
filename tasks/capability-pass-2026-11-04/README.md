# Capability pass: process and material terms from companies' own sites (2026-11-04)

The repo owner requested this pass in session on 2026-11-04. It covers 66 NE Ohio (PIC-18) Ring 1–2 organizations
whose records had no `processes` and no `materials`.
- **How the work was done:** three lanes read each company's own website and recorded every SCHEMA §3.1 / §3.2 term
  the site explicitly states, one quote per term. Nothing was inferred.
- **How the lanes found where to look:** an internal list of candidate pages pointed them to the right sites. It is
  not committed and not cited.
- **Raw check:** the integrator re-fetched every page raw and kept a term only when its quote appears word for word
  (`rawcheck.csv`). 218 of 228 quotes passed.

## Applied (`build_fixes.py`, reused from `tasks/record-fixes-2026-11-03/`), 40 organization records

| Change | Rows |
|-|-:|
| `processes` / `materials` cells filled with SCHEMA terms | 66 |
| `scope` evidence rows carrying each term's quote (own_site, supports_A) | 218 |
| `last_verified` → 2026-11-04 | 40 |

EVD ids start above EVD-076000, a block clear of every open PR and of the state waves' reserved ranges. No tier
moves.

## Not applied
- **Held, 10 terms (`holds.csv`):** the quote was not on the re-fetched page.
- **No mappable terms, 22 organizations:**
  - The site was down or blocked: Okamoto Sandusky, Custom Pultrusions, Polycase and others.
  - The site states no SCHEMA term: Koroseal, Chemical Solvents, Akron Dispersions, CermeTech and others.
  - Identity was unconfirmed: Formco/Molded Devices redirects to Aptyx, and ORG-001777's domain is a different
    company.
- **Site gone:** Plymouth Foam now redirects to ALTOR Solutions, and ECM BioFilms returns HTTP 526. Both are findings
  for a status review, not applied.

Checks: rehearsed on a temp copy. `python scripts/validate.py` exits 0.

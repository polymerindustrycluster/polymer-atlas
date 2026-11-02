# Registry links: FRS, EIN, UEI, FDA_FEI (2026-11-02)

**Integrator for this pass:** claude-code. The repo owner requested this pass in
session on 2026-11-02, and it goes in as a PR.
**Rulings applied:** owner battery 2026-11-01:
- R10: optional `site_id` on `registry_links` for facility-grain IDs.
- R11: the employer `EIN` value, plus its mint rule.

Both were recorded in SCHEMA v1.7.7, and the validator already enforced them.
**Builder:** `build_links.py`. Its docstring holds the rules; `new_links.csv` and
`holds.csv` are its output.

## Applied (rows added to `data/registry_links.csv`)

| registry | rows | grain | rule | source (verified at source, AGENTS.md §4) |
|---|---:|---|---|---|
| FRS | 2,304 | org + `site_id` | MATCH_SITE, strong (2,091) or strong_id_corroborated_name_differs (213) | EPA ECHO exporter `REGISTRY_ID` column (`tasks/echo-frs-spine-2026-11-01/`) |
| EIN | 320 | org | R11: MATCH_ORG with sponsor name + a street on one of the org's sites (step `2+3`) | DOL EFAST2 Form 5500 sponsor EIN (`tasks/form5500-spine-2026-11-01/`) |
| UEI | 146 | org | packet `link_candidate = Y` | USAspending recipient record (`tasks/federal-leads-2026-11-01/`) |
| FDA_FEI | 2 | org | packet `link_candidate = Y` | openFDA establishment listing (same packet) |
| **total** | **2,772** | | | |

**Schema change in the file:** `registry_links.csv` gains the `site_id` column
that R10 ruled. Existing rows get an empty trailing field and are otherwise
byte-identical. `registry_links.csv` sha256 went from `5d4cbd773e3ddaf9…` to
`1912ddc90e175a0c…`.

## Held (46 rows, `holds.csv`)

FRS matches of strength `moderate`: name + zip agree, but the street is unknown
on one side. They need a street check before they mint.

## Not minted (non-candidates, not holds)

- **EIN:** 509 MATCH_ORG sponsors agree on name and state but have no street hit
  (most Ohio sites lack `street_address`). R11 does not mint them.
- **UEI / FDA_FEI:** 83 UEI REVIEW and 8 FEI REVIEW candidates. They need
  per-row review.

## Checks

- `validate.py` passes, including V-6 / R10: each `site_id` exists and belongs
  to the row's org, and site IDs appear on facility-grain registries only.
- `derive_tier1.py` reports 0 drift (FRS/EIN/UEI/FEI are not qualifier inputs).
- `build_sqlite.py` builds, and all unit tests pass.

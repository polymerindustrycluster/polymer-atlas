# Evidence repair, round 2: scope rows (2026-11-04)

The repo owner requested this pass in session on 2026-11-04. It repeats `tasks/evidence-repair-2026-11-03/` on 172
weak `scope` evidence rows: rows whose cited page, re-fetched, no longer showed the claimed activity, or showed only part
of it.

- **Lanes:** three packet lanes (`lanes/S1..S3_out.csv`, brief in `LANE_BRIEF.md`) looked for a fresher source for each
  row.
- **Raw check:** `prep.py` joins the lanes to today's evidence rows (`checked.csv`) and re-fetches every FOUND and
  CONTRADICTED quote raw (`replacements.csv`, column `raw`).
- **Append-only:** `build_repair.py` (reused from round 1; constants and one source-class step changed) appends a new
  row that answers each weak one. The weak row is never edited (SCHEMA §4.13).

## Outcomes (unit: queued weak evidence rows; 172)

| Lane outcome | Raw check | Rows | Applied |
|-|-|-:|-:|
| FOUND | quote found verbatim | 70 | 63 |
| FOUND | quote not on the page | 4 | 0 |
| FOUND | page unfetchable | 3 | 0 |
| CONTRADICTED | quote found verbatim | 4 | 0 |
| NONE_FOUND | n/a | 91 | 0 |

63 new `scope` rows were applied, EVD-078028..EVD-078090, across 27 evidence shards.

## Source classes
The lanes wrote `company` and `company_site`. SCHEMA §4.13 defines `own_site` as the entity's own domain, so a row maps
to `own_site` only when its page is on the record's own organization's domain.

Seven raw-verified rows are held because their page sits on a parent's, brand owner's or association's domain:

| Weak row | Page |
|-|-|
| EVD-008259 | CPChem, for AmSty |
| EVD-007962 | Arkema, for Bostik |
| EVD-011189 | Toray |
| EVD-007842 | TotalEnergies |
| EVD-007605 | Rmax |
| EVD-008076 | Florestone |
| EVD-010929 | the Fluid Sealing Association |

They are in `holds.csv`, so a later pass can rule whether a parent's page counts. One `trade_association` row is held too,
because `directory` has no scope ceiling in this builder.

## Findings held for their own pass (not applied)
- **EVD-009091, allnex Louisville:** the 2026-05-08 release says gelcoat production at the site ends by 2026-06-30. This is
  a status and scope finding that needs a dated outcome record.
- **EVD-007626, Sika Aurora:** the cited 2017 release describes decorative-concrete colorants and sealers, not polymers.
  This is a scope question.
- The other two CONTRADICTED rows and every NONE_FOUND row stay as they are. A failed search is not evidence of absence.

Checks: rehearsed on a temp copy. `python scripts/validate.py` exits 0.

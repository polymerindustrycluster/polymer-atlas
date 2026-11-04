# Integrator backlog: HQ, parent and owner fixes (2026-11-04)

The repo owner requested this pass in session on 2026-11-04. Earlier lanes had flagged these findings. A dedicated
evidence lane confirmed each one with a quote (`findings.csv`), and the integrator re-fetched every quote raw and found
it word for word (`rawcheck.csv`: 12 of 12).

## Applied (`build.py`), 9 evidence rows (EVD-077001+)

| Record | Change |
|-|-|
| ORG-000698 BASF | HQ Greenville, OH → Florham Park, NJ; record moved to the NJ shard |
| ORG-000097 BioVerde | HQ Akron, OH → Houston, TX; record moved to the TX shard |
| ORG-000523 Pretium | HQ city Chesterfield → St. Louis, MO |
| ORG-004456 MonoSol | HQ city Lebanon → Portage, IN |
| ORG-001327 AltraSet | `parent_org_id` ORG-000430, plus its generated `parent_of` edge (V-27) |
| ORG-000201, 000343, 000366, 003666 | `ultimate_parent_name` set or corrected from dated releases |

`tier1_qualifier` is derived and was not touched; the derivation re-runs separately.

## Held (notes only)
- BASF's 60/40 joint venture: the page does not name the LLC.
- ContiTech sale: announced, not closed.
- Viskase Osceola: no site row is held.
- HEXPOL: identity not confirmed.

Checks: rehearsed on a temp copy. `python scripts/validate.py` exits 0.

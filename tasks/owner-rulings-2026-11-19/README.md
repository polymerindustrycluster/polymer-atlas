# Owner rulings, 2026-11-19 (W18 close-out battery)

The repo owner ruled the W18 close-out battery in session on 2026-11-19, as multiple choice. Every item was ruled as
recommended. This file records each item. Nothing in `data/` changes here; each ruling that touches data is applied in
its own pull request. Counts are at main ec7e19be unless stated.

## E1. Evidence IDs: next-free at merge

SCHEMA's `evidence_id` field is "next-free at application", and AGENTS.md §3 says to allocate above the tree-wide
maximum and never fill a gap. On 2026-11-18, three merges used evidence IDs below main's maximum:

| PR | Merge | Rows | IDs | Maximum at the merge's parent |
|---|---|---|---|---|
| #385 | e1df30e4 | 4 | EVD-396200 to 396203 | EVD-396506 |
| #390 | dd07afc9 | 45 | EVD-396600 to 396645 (one ID unused) | EVD-397103 |
| #393 | f35fb750 | 7 | EVD-396900 to 396906 | EVD-397103 |

The IDs came from fixed ranges written into lane briefs. Another orchestration's merge (566eccb1) then raised the
maximum to EVD-397103. None of the 56 IDs had appeared on main before (a `git log -G` search of the evidence shards).

- **Ruled:** the 56 rows stand as they are; evidence IDs are immutable. This record is the note of the deviation.
- **Ruled:** a PR allocates its new evidence IDs from one above the maximum across all `data/evidence_*.csv` shards at
  its final merge of `origin/main`. If the maximum has moved, it re-allocates through its build script in an ID-only
  commit, and the reviewers check that commit with the IDs masked. Before each merge, the integrator checks that the
  lowest new ID exceeds main's maximum. PRs #383, #396, #397 and #400 followed this rule.
- Not chosen: disjoint ID blocks for each concurrent orchestration.

## P1. Gel coat in open-molding spray-up (PR #400, SITE-000248)

The Ohio EPA permit's units K001 to K005 read "Polyester gelcoat and FRP (fiberglass reinforced plastic parts) spray up
booth". The review families split twice on whether the gel-coat spraying is also §3.1 `coating_applying`.

- **Ruled:** gel coat applied inside an open-molding spray-up unit is part of `composites_spray_up`, not a separate
  `coating_applying`. `coating_applying` stays for coating lines and finishing. SITE-000248 keeps
  `composites_spray_up` only.

## P2 to P4. Air-permit binding and mapping (PR #400, "Proposed follow-ups")

These extend owner ruling 2026-11-18b item 1 (B-PERMIT, option b).

- **P2, ruled:** a USPS-standard abbreviation (`Pkwy`, `Rte`) or a `Twp.` suffix does not break binding. The printed
  Facility ID, holder, street number and street name must still agree with the Atlas site. Three sites held in PR #400
  differ only in this way: SITE-000264, SITE-001137 and SITE-002113.
- **P3, ruled:** a permit's "Permit Description" field counts as a witness at `supports_C` only, never higher. On a
  tier A or B site it gives a `site_capabilities` row only (owner ruling 2026-11-14). The example is SITE-000814.
- **P4, ruled:** `site_capabilities` mapping. `compounding_unspecified` maps to the capability term `compounding`, and
  `extrusion_unspecified` to `extrusion`, their §3.6 parents. `coating_applying` and `foam_molding_bead` stay unmapped,
  as §3.6 keeps applying out of the capability vocabulary.

## M1 and M2. Market attribution (PRs #390 and #396)

- **M1, ruled:** a market claim on a group's website may be attributed to a subsidiary or division record only where
  the page names that subsidiary, its brand or its plant as the subject of the claim. A group-wide claim alone is not
  attributable. The scale batches held 17 organization records whose only website is the group site:
  - batch 1: ORG-000036, ORG-000119, ORG-000169, ORG-000438, ORG-000606, ORG-000752, ORG-001447, ORG-001461,
    ORG-001462, ORG-001513;
  - batch 2: ORG-001534, ORG-001949, ORG-002038, ORG-002047, ORG-003196, ORG-003771, ORG-004022.
  The holds are class `group_or_redirect_attribution` in each batch's `verdicts.csv`.
- **M2, ruled:** Myrava's (ORG-001558) note "do not promote above C without own-site check" caps the record's tier.
  It does not stop filling `markets_served` at tier C from a claim on the company's own site.

# Owner rulings, 2026-11-18 (second battery, W18)

The repo owner ruled the W18 battery in session on 2026-11-18, as multiple choice: B-PERMIT option (b); two of three
proposed process terms; the narrower identifier widening; and the remaining five "all as recommended". This file
records each item. Nothing in `data/` is changed here; each ruling is applied in its own pull request. Counts are at
main e1df30e4 unless stated.

## 1. B-PERMIT: Ohio EPA air permits as process evidence (PR #387)

The canary (PR #387) drew 10 of the 33 PIC-18 sites with a retrievable final Ohio EPA permit, from a frame of 58
sites (organizations with process unknown, one active PIC-18 site, an FRS link). Under the rule registered before the
draw, 7 of 10 bound and 6 of 10 named a specific §3.1 process in a unit heading or equipment description.

- **Ruled, option (b):** an Ohio EPA air permit's emissions-unit description is a `government_filing` witness for a
  §3.1 process at site grain.
  - A unit narrative may be proposed at the class ceiling; a unit-table row or heading is a list item, `supports_C`.
  - A permit past its printed expiry caps at `supports_C`.
  - Binding: the printed Facility ID, the holder and the street and city must all match the Atlas site.
  - Each evidence row carries the permit's issue and expiry dates.
  - Ancillary units (boilers, generators, tanks, baghouses, finishing paint booths, cleaning) name no process.
  - Use the `_unspecified` term where the permit does not state the type.
- On a tier-A or tier-B record a `supports_C` term is a `site_capabilities` row only (owner ruling 2026-11-14).
- The packet lane over the other 23 retrievable sites runs after the market scale-up.

## 2. New §3.1 process terms

- **Ruled: add `rubber_molding_transfer`** (rubber transfer molding). §3.1 lists `transfer_molding` under plastics
  only. It joins the `rubber_molding` rollup. This settles the SITE-000562 hold (PR #381).
- **Ruled: add `composites_spray_up`** (spray-up open molding, distinct from `composites_hand_layup`). This settles
  the SITE-000248 vocabulary gap (PR #387).
- **Ruled: no term for spiral-wound paper and phenolic tube making** (ORG-001855); it stays held.
- Both additions come as a dated §3.1 revision in SCHEMA.md, with the validator and vocabulary export updated.

## 3. Account-style identifiers in people URLs (follow-up 1 of PR #379)

Rows at e1df30e4: `?unid=` on 3 `people.csv` rows; `researchdirectory.uc.edu/p/<shortname>` on 6 `people.csv` rows,
and 13 `evidence_people.csv` rows for the same 6 people; `experts.colorado.edu/...fisid_<id>` on 5 `people.csv` rows.

- **Ruled:** treat `?unid=` and `researchdirectory.uc.edu/p/<shortname>` exactly as rulings 1 and 1b of
  2026-11-18 (`tasks/owner-rulings-2026-11-18/README.md`). Validator V-62 is widened to both.
- **Evidence rows are never edited.** The rulings 1 and 1b procedure applies.
- **Ruled:** `fisid_<id>` is accepted; V-62 is not widened to it. What the institution uses the number for is not
  established.

## 4. Company-wide headcounts (PR #383)

- **Ruled:** a company-wide or worldwide count on an organization's own page never sets `employee_band_ohio`, which
  is the Ohio band (SCHEMA field table). The 12 held leads in PR #383 stay held: 11 company-wide or worldwide
  statements, and ORG-004022's count, which is for its Dutch headquarters (the page gives a separate worldwide group
  count). No `employee_band_global` column is added now.

## 5. Graphite electrode producers (ORG-000157, GrafTech)

The record has been staged since integration pass 14 (2026-10-30), noted "WATCHLIST-FOR-EXCLUSION ... pending the
owner ruling". Carbon black is already in scope as a §3.6 material (v1.6.1), so this ruling covers only graphite.

- **Ruled:** graphite-electrode and synthetic-graphite producers are out of scope unless a polymer process is
  evidenced at the site.
- The ruling is recorded in the record's note in the existing "out of scope. Do not promote." form. Such records
  leave the PIC-18 outcome frames.

## 6. People status (PERSON-000359)

- **Ruled:** add `status` (`active` | `deceased`) and `status_date` to people by dated schema revision. A status
  change needs dated evidence (AGENTS.md §3).
- PERSON-000359 is set once a dated source is fetched. The department page listing the person under In Memoriam is the
  lead.

## 7. Confirmations

- **`tooling_repair_maintenance`** means the repair of polymer-processing tooling (molds, dies, screws, barrels).
  Refurbishing metal industrial knives is not covered (ORG-001774 stays held).
- **An equipment maker's statement that its machines serve, for example, injection molders** is not a process claim
  for the maker. A process claim is the organization's own operation.

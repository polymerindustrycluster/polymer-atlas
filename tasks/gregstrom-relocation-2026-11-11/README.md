# Gregstrom relocation correction (2026-11-11)

One of the four findings surfaced by the licensed-source cleanup lanes (PR #258) and adjudicated in
`tasks/licensed-source-cleanup-2-2026-11-11/` (PR #266). The finding is confirmed on the company's own site,
so the record itself is corrected here — one task, one PR, per protocol.

## The deciding source

Gregstrom Corporation's own post, **"Gregstrom Moves Rotomolding Business and Looks to the Future"**,
published **2025-07-30**, https://gregstrom.com/gregstrom-moves-rotomolding-business/ (read first-hand
2026-11-11):

- "Gregstrom Corporation, a 79-year-old plastics manufacturer, is moving its rotomolding business from
  Woburn, Massachusetts to Bedford, New Hampshire"
- "Gregstrom's relocation follows the merger of its thermoforming business with C&K Plastics in 2024.
  By focusing exclusively on rotational molding…"

Later posts (Dec 2025) style the company "Gregstrom Corporation of Bedford, New Hampshire". A dated company
statement is the status-change standard (AGENTS §3). Bedford street address from the company's current place
listings (10 Iron Horse Dr, Bedford, NH 03110, carrying Gregstrom's phone, consistent across listings);
Bedford is in Hillsborough County.

## Changes

- **ORG-003645** — HQ fields Woburn / MA / Middlesex → Bedford / NH / Hillsborough; the row moves from
  `organizations_MA.csv` to `organizations_NH.csv` (a record's shard follows its HQ); description corrected
  (founded 1946; rotomolding-only since the 2024 C&K merger); the post added to `sources`; `last_verified`
  2026-11-11; tier held at B.
- **SITE-004416** (Woburn) — `operating_status` → `closed`, tombstoned in place; its processes/materials stay
  as the historical record; notes carry the closure and the successor. No keyed row is removed, so no
  REMOVALS.csv is needed (the org's shard move keeps its key in the organizations table union).
- **SITE-019101** (new, allocated above the tree-wide site maximum) — the Bedford establishment:
  `hq_and_plant`, rotational_molding only (thermoforming is not carried — it left in the 2024 merger),
  tier C (existence and process from the company's own post; street address from a place listing).
- **Evidence** — EVD-333054/55 (org liveness + scope, `evidence_organizations_NH.csv`), EVD-333056/58 (new
  site existence + scope, `evidence_sites_NH.csv` — the evidence contract's two legs for a create),
  EVD-333057 (Woburn closure, `evidence_sites_MA.csv`); all quote the post verbatim (re-verified against the
  live page 2026-11-11), `own_site`, `supports_B`.
- **inclusion_log.csv** — one row recording the correction and the rule cited.

## Borderline calls

- The org's pre-move notes record that a roster's "Unit C Bedford NH" address was superseded in pass 18.
  That roster line predates the actual move; the current place listing gives 10 Iron Horse Dr without a
  unit, and no unit is carried into the new site row.
- Materials (PE/PP) are carried from the Woburn record to the Bedford site on the post's statement that the
  company continues with its existing rotomolding equipment set; flagged here and in the site's notes, and
  the site sits at tier C.
- The Woburn site's `employee_band_site` is not carried to Bedford (it was an OSHA filing for Woburn).

Reproduce: `python3 tasks/gregstrom-relocation-2026-11-11/build.py --data-dir data` (dry run);
`--apply --i-am-the-integrator` writes.

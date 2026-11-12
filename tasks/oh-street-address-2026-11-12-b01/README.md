# Ohio street addresses, batch 01 (own-site route), 2026-11-12

Claim: `claimed:grok 2026-11-12`, Ohio streets remaining (QUEUE.md "Ohio streets remaining"). Lane and integrator: Grok, branch
`agent/grok/oh-street-address-2026-11-12-b01`. Reserved ID range for this lane: EVD-340000–EVD-349999 (above the tree-wide maximum
EVD-333979 on main at the start; no open PRs at the start). This batch uses EVD-340000–EVD-340033.

## Frame
- Active Ohio site rows (`data/sites_OH.csv`, `operating_status=active`) with blank `street_address`, PIC-18 counties, PIC core first:
  Summit, then Portage, Stark, Medina, Wayne, Cuyahoga, Lake, Geauga, Lorain, Mahoning, Trumbull, Ashtabula, Columbiana,
  Tuscarawas, Richland, Ashland, Erie, Huron. Within a county, site_id order. 734 rows; this batch is the first 100 Summit rows
  (SITE-000007 … SITE-000449) after excluding the 100 PIC-18 rows whose prior Codex hold names a conflict (those need adjudication,
  not a new witness). `frame.csv` is the frozen batch frame.
- Every row in the frame was worked in an earlier Codex street round and held. Earlier C/U rounds used federal routes; this batch adds
  the operator's own website as the route for every tier.

## Method
- Route: the organization's held `website` only (homepage plus up to 5 same-host contact/location/about pages, then `/contact`,
  `/contact-us`, `/locations`). https and www variants were tried. A failed fetch is recorded as unavailable, never as absence.
- Extraction: a numbered physical street followed by the recorded city and OH/Ohio. PO boxes are dropped.
- VERIFIED only when all of these hold: exactly one street at the recorded city, or one that agrees with the street already in notes;
  the page ZIP agrees with the recorded ZIP (or no ZIP is recorded); the street agrees with any street in notes; the operator holds
  one site in that city; and the quote is not only a mailing, warehouse or PO context.
- Raw re-check: every VERIFIED quote was re-fetched raw with curl at build time. The street words had to appear in order with the
  recorded city within 160 characters. 34 of 35 passed. One (SITE-000181 Vertex) returned an empty body on re-fetch and is held.
- Changes: only `street_address` on 34 existing site rows, plus one appended evidence row each (`own_site` / `address` / `supports_A`)
  in `data/evidence_sites_OH.csv`. One row (SITE-000022) also gets an ADDRESS-OVERLAP LEAD note. County, county_source, ZIP,
  coordinates, tier, status, ring and registry links are unchanged. No entity creates, deletes or merges.
- Sources: company websites only. No licensed source, directory or PIC CRM data. No personal contact data.

## Result (unit: active Ohio site rows in this frame)
- 100 rows: **34 VERIFIED**, **66 STILL_UNCERTAIN**, 0 REJECT. VERIFIED by tier: A 5, B 1, C 17, U 11.
- Hold reasons, each with its settling fact in `holds.csv`:
  - 29: pages read but no street printed at the recorded city;
  - 18: own-site fetch unavailable;
  - 12: no held website;
  - 2: ZIP conflicts;
  - 2: mailing or warehouse context only;
  - 1: several streets;
  - 1: same-operator sibling site at the same address;
  - 1: raw re-fetch failed.
- Fetches: 434 attempts, 293 returned 2xx.
- Ohio coverage: active Ohio site rows with a street go from 466 to 500 of 1,877 on main at the base commit.

## Leads for the integrator (`leads.csv`), no data change made
- Address-first:
  - SITE-000385 (H.B. Chemical, warehouse_distribution) and SITE-004436 (HB Chemical Twinsburg HQ) are the same org at the same
    street, 1665 Enterprise Pkwy. This is a probable single establishment recorded twice, so the street was held.
  - SITE-000085 Ohio Precision Molding's own site prints 8220 Bavaria Dr E, Macedonia, the street filled here for Design Molded
    Plastics SITE-000069.
  - SITE-000022 Ravizza shares 526 S Main St with SITE-002107 Biena Tech. This is a multi-tenant building, not a merge.
- ZIP conflicts:
  - SITE-000007 Struktol: the own page says Stow 44224, but the record says 44223.
  - SITE-000043 Alterra: the own page gives 222 S Main St 44308, but the notes give 1200 E Waterloo Rd.
- Own site prints another city (possible relocation):
  - SITE-000014 Diamond America: Mogadore;
  - SITE-000077 Mantaline: Hiram and Mantua;
  - SITE-000084 Q Model: Akron;
  - SITE-000098 Spazzolplastica: Stow and Mentor.

## Files
- `frame.csv`, `verdicts.csv`, `holds.csv`, `evidence.csv`, `audit.csv` (fresh raw re-check), `fetch_log.csv` (every attempt with
  HTTP code and SHA-256), `leads.csv`, `summary.json`, `scripts/` (frame, fetch, extract, adjudicate, build, leads, packet).
- Raw pages stay outside git.

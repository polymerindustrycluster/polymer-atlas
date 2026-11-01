# PIC-12 capability wave — tranche 1 summary (2026-11-01)

**Five packet lanes, 150 Ohio site rows**, chosen by an even stride from the
586 candidates (see `LANE_BRIEF.md`). These are packets only. The integrator of
record applies them after review, nothing under `data/` was edited, and no IDs
were allocated.

Every lane checked its quotes by script against the fetched page text. The
orchestrating session then re-checked every packet as a whole:

- **856 proposed values, 0 outside `docs/schema/vocab.json`.** This counts
  processes, materials, markets and certifications, with lane 3's `;`-packed rows
  split into single values.
- **0 quotes over 25 words.**
- **0 rows without a source URL.**

## Results (unit: assigned Ohio site rows, n = 150)

| Lane | VERIFIED | STILL_UNCERTAIN | REJECT | Hard fetch-failure rate |
|---|---:|---:|---:|---:|
| 1 | 11 | 19 | 0 | 20.7% |
| 2 | 16 | 14 | 0 | 5.7% |
| 3 | 15 | 15 | 0 | 10.6% |
| 4 | 15 | 15 | 0 | 10.1% |
| 5 | 11 | 19 | 0 | 13.2% |
| **all** | **68 (45%)** | **82** | **0** | — |

Plus the pilot (`tasks/pilot-pic12-capabilities-2026-11-01/`): 12 VERIFIED and
13 STILL_UNCERTAIN of 25.

**Values proposed (unit: record × field × value, in-vocab):** 856 in total.
- **By field:** materials 357, markets 230, processes 221, certifications 48.
- **By scope:** 480 site and 376 org. Org-scope values are never pushed down to
  sites.

**Markets coverage (unit: assigned site rows):**
- **Site scope:** 40 of 150 sites (27%) get at least one `markets_served` value.
- **Counting org scope:** 87 of 150 (58%).
- **Baseline:** in this population, `markets_served` was essentially empty
  (about 1% across Ohio PIC-12 ring 1–2 sites).

## Why sites stayed uncertain (from the lanes' `verdicts.csv`)

1. **Multi-plant companies with no plant-specific page** (org scope only). This
   is the largest cause, around 50 sites. Settling it needs plant pages,
   certificate annexes (which often name each address and its activity), or
   permits.
2. **Own site unreachable.** About 20 sites hit a TLS error, 403, captcha,
   parked domain or JS-only shell. These need a human-browser pass. They are
   never closure evidence.
3. **The row is not a plant.** Corporate offices, warehouses, distributors and a
   supply store appear as ring 1–2 `manufacturing_plant` rows. These go to the
   integrator and owner for type and ring correction.
4. **Vocabulary gaps.** See `tasks/OWNER_BATTERY_2026-11-01.md` R2/R3 and items
   R8–R9. "Automotive" with no OEM or aftermarket split came up at about 30 sites.

## Hygiene findings worth an integration pass

The lane reports list each finding with IDs. In summary:

- **Unrecorded acquisitions or parents:**
  - Iten Defense → NP Aerospace (Sept 2026);
  - Ashtabula Rubber → ASC Engineered Solutions;
  - Pilot Plastics → Preformed Line Products (2023);
  - Hy-Ko → Midwest Fastener (2020);
  - Soft-Lite → Harvey Building Products;
  - Third Dimension → Green Bay Packaging (2020);
  - the ContiTech sale announced (pending).
- **Ohio plants listed on companies' own sites with no Atlas site row:**
  - Treemen, North Lima;
  - Mantaline, Hiram;
  - Vibrantz, Cleveland, Independence and Lockland;
  - Kent Elastomer, Winesburg;
  - Ashtabula Rubber, 5013 Benefit Ave;
  - CG Thermal, Twinsburg production center;
  - Mar-Bal and others.
- **Wrong addresses:**
  - System Seals (the main office is Midwest Ave, Cleveland);
  - Tribotech (Midwest Ave, Cleveland);
  - MultiPlast (Harper Rd, Solon);
  - Avery Dennison Performance Tapes (Painesville);
  - Ferriot (the zip);
  - SITE-001798 (the zip field holds a street number).
- **`street_address` blank, with the street only in `notes`:** most of the
  sampled rows. This blocks address-first dedupe (AGENTS.md §3).

## Measured cost

- **Agent tokens:** about 1.56M for 150 sites, roughly 10k per site or about
  23k per VERIFIED site.
- **Time:** about 15–17 minutes of wall-clock per 30-site lane, with lanes
  running in parallel.
- **Fetches:** about 3.1–4.1 per site.

## Recommendation for tranche 2 (436 remaining candidates)

- **Same method,** in up to 15 lanes of 30.
- **Plant-tying:** add certificate annexes and plant pages as the first step for
  multi-plant parents. This is where most of the uncertainty sits.
- **Separate lanes:**
  - a human-browser pass for the roughly 13% of unreachable sites;
  - a desk pass that copies `notes` street addresses into a `street_address`
    proposal packet.
- **Timing:** start tranche 2 after the owner rules on R2 (automotive). That
  ruling changes the value of roughly a fifth of all market claims.

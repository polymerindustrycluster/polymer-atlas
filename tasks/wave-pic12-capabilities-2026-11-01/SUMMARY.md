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

---

## Tranche 2 summary (2026-11-01, SCHEMA v1.7.6 vocabulary)

**8 packet lanes, 436 Ohio site rows.** This covers every remaining candidate.
The orchestrator re-checked every packet as a whole. With packed rows split, it
found 0 values outside vocab v1.7.6, 0 quotes over 25 words, and 0 rows without
a URL.

| Lane | Sites | VERIFIED | STILL_UNCERTAIN | REJECT |
|---|---:|---:|---:|---:|
| t2-1 | 55 | 30 | 25 | 0 |
| t2-2 | 55 | 25 | 30 | 0 |
| t2-3 | 55 | 28 | 27 | 0 |
| t2-4 | 55 | 30 | 25 | 0 |
| t2-5 | 54 | 18 | 36 | 0 |
| t2-6 | 54 | 18 | 36 | 0 |
| t2-7 | 54 | 32 | 22 | 0 |
| t2-8 | 54 | 29 | 25 | 0 |
| **all** | **436** | **210 (48%)** | **226** | **0** |

**In-vocab values proposed:** 2,335 (unit: record × field × value).
- **By field:** markets 837, materials 785, processes 600, certifications 113.
- **By scope:** 1,437 site and 898 org.

**Markets coverage (unit: assigned site rows):** 141 of 436 at site scope (32%),
and 285 of 436 (65%) counting org scope.

**Certificates.** About 40 site-scope certifications rest on certificate PDFs or
annexes that name the plant address. Several expired certificates were caught
and not recorded under R3c: Wooster Elastomers, Rauh, Eckart ISO 14001.

**Privacy.** No personal emails were recorded. One generic company mailbox
(`info@…`) appears inside a quoted page string in `t2_lane5/packet.csv`. The
quote must stay verbatim for the substring check, so it was left in place, and
the integrator must keep it out of `data/`.

## Campaign totals (pilot + tranche 1 + tranche 2)

All units are Ohio PIC-12 site rows, active, ring 1–2. Every one of the 611
candidates from the filter was researched.

| | Sites | VERIFIED | Values proposed | Markets at site scope | Markets incl. org scope |
|---|---:|---:|---:|---:|---:|
| Pilot | 25 | 12 | 117 | 7 | 13 |
| Tranche 1 | 150 | 68 | 856 | 40 | 87 |
| Tranche 2 | 436 | 210 | 2,335 | 141 | 285 |
| **Total** | **611** | **290 (47%)** | **3,308** | **188 (31%)** | **385 (63%)** |

- **Baseline:** before this campaign, `markets_served` was filled on 7 of 640 such
  rows (1.1%).
- **Cost:** about 5M agent tokens, roughly 8k per site.

## What the integrator gets from the lane reports (summary; IDs are in each REPORT.md)

- **Unrecorded acquisitions, renames and parents:**
  - Gabriel → Huntsman (2021)
  - Iten Defense → NP Aerospace
  - Ashtabula Rubber → ASC Engineered Solutions
  - Pilot Plastics → PLP
  - Hy-Ko → Midwest Fastener
  - Harwood → Coreline Rollers
  - AMD Plastics → Forming Technologies
  - Ohio Precision Molding → Design Molded Plastics
  - Degussa Initiators = United Initiators
  - BVPV = Styropek
  - ChromaScape moves (Independence HQ 2021, Stow production 2022)
- **Ohio plants listed on companies' own sites with no Atlas row:** about 20,
  including:
  - Akro-Mils Wadsworth;
  - Philpott Aurora;
  - Eckart Perry;
  - Peak Nano Macedonia;
  - Mantaline Hiram;
  - Kent Elastomer Winesburg;
  - Treemen North Lima;
  - Synthomer Beachwood;
  - Vibrantz Cleveland, Independence and Lockland;
  - Novagard warehouse.
- **Rows typed as ring 1–2 plants that are HQs, offices, warehouses, distributors
  or equipment makers:** about 40, for R9 correction.
- **Wrong or conflicting addresses:** about 30.
- **Same-address duplicate pairs:** e.g. SITE-000599 / SITE-000680, the three Cast
  Nylons rows, and Zehrco-Giancola.
- **Domains that now serve unrelated content** (Sietins, Neo Industries,
  Cell-O-Core) or are parked. These are re-verification leads only.

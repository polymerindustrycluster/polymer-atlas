# Lane brief: PIC-12 capability wave, tranche 1 (2026-11-01)

**Packet lanes only.** A lane never edits `data/`, never allocates IDs, and never
commits or pushes (AGENTS.md §2 rules 7–8). The integrator of record applies
packets after review.

## Population

- **Pinned at:** commit `665e5c5`.
- **Candidate filter:** active sites in `data/sites_OH.csv`, in a PIC-12 county,
  ring 1 or 2, blank `processes` or `markets_served`, parent org with a website,
  and not in the pilot (`tasks/pilot-pic12-capabilities-2026-11-01/`). That gives
  586 site rows.
- **Tranche 1 (150 site rows):** taken at an even stride across the site_id-sorted
  list, then split round-robin into `lane1_assignment.csv` … `lane5_assignment.csv`
  (30 each).
- **Not yet assigned:** the other 436 are in `remaining_candidates.csv`.

## Method

Follow the pilot's method (`tasks/pilot-pic12-capabilities-2026-11-01/REPORT.md`):

- **Sources.** Use the company's **own website** only (source_class `own_site`), with
  **≤ 6 fetches per site**. Fetch with curl through the configured proxy and keep
  the page text. Use WebFetch only as a fallback route; never quote from its
  summary.
- **Quotes.** Each proposed value carries the exact URL and a quote of ≤ 25 words.
  Check every quote programmatically as a substring of the fetched text.
- **Values.** Use only values from `docs/schema/vocab.json` (PROCESSES, MATERIALS,
  MARKETS, CERTS). Anything else goes in a `*_other_note` row marked OFF-VOCAB.
  Never map "automotive" to `automotive_oem` or `automotive_aftermarket` unless
  the page says which.
- **Scope rule (hard).** If the company has several locations and no page ties a
  capability to this plant, the value is `org` scope and is never pushed down to
  the site. A value is `site` scope only when the page names the plant or the
  company plainly has a single location (say why in notes).
- **Verdicts.**
  - **VERIFIED:** at least one in-vocab value at site scope.
  - **STILL_UNCERTAIN:** name the settling fact.
  - **REJECT:** only with the deciding fact on a dated page.
- **Failed fetches.** A 403, TLS error, captcha, parked domain or JS-only shell is
  an availability failure, **never** evidence of closure. Do not try to defeat a
  bot wall: no faked user-agents, no captcha workarounds.
- **Other problems.** Hygiene problems you notice go in `notes` for the
  integrator: wrong address, redirect to a new owner, an office row carrying a
  plant ring, a scope doubt. Do not resolve them.
- **Certifications.** Record them only if they're current. A superseded edition
  (e.g. ISO 9001:2008) gets flagged, not recorded.

## Output per lane (in `lane<N>/`)

- **`packet.csv`** with the same columns as the pilot: record_id, record_scope,
  field, proposed_value, source_url, quote, observed_date, source_class, verdict,
  notes.
- **`verdicts.csv`** with columns site_id, org_id, site_name, verdict,
  deciding_or_settling_fact, fetches_used, availability_failures.
- **`REPORT.md`** with:
  - counts with units;
  - yield per site;
  - fetch-failure rate;
  - vocabulary gaps met;
  - hygiene findings.

---

## Tranche 2 (2026-11-01, after owner ruling R2 / SCHEMA v1.7.6)

- **Assignment:** the 436 remaining candidates, split round-robin into
  `t2_lane1_assignment.csv` … `t2_lane8_assignment.csv` (54–55 sites each).
  Outputs go to `t2_lane<N>/`.
- **Method:** the same as tranche 1, with three changes.
  1. **Use the v1.7.6 vocabulary** in `docs/schema/vocab.json`:
     - "Automotive" with no OEM or aftermarket split → `automotive_unspecified`.
     - Tire customers → `tire_rubber_goods`.
     - "Medical" without "device" → `medical_healthcare_general`.
     - Food processing that is not packaging → `food_processing_foodservice`.
     - Type-unstated thermoforming → `thermoforming_unspecified`.
     - Also available: `asa`, `specialty_elastomers` (name the specific
       elastomer in notes), `iso_45001`, `iso_17025`.
  2. **Certification currency (R3c).** Record only current certificates, or
     current pages naming a non-superseded edition. Expired certificates and
     "ISO certified" with no standard named are not recorded.
  3. **Tie values to plants first.** For a multi-plant parent, look first for
     certificate annexes, plant pages and plant-named job postings that name
     this address and its activity. Only then fall back to org scope.
- **Scratch directory:** use `/tmp/claude-0/wave/t2_lane<N>/` exclusively. In
  tranche 1, two lanes collided by sharing a scratch path.
- **REPORT.md:** if your tool refuses to write it, return the full report as
  text. The orchestrator saves it.

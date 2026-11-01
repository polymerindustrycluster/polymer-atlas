# Owner battery — 2026-11-01

> **RULED 2026-11-01 — "all as recommended"** (repo owner, in session).
> Recorded in SCHEMA v1.7.6 ("Owner rulings — 2026-11-01" in §1, plus the
> revision history), with matching amendments to AGENTS.md §4 and §5.1.
> The vocabulary is live in `scripts/validate.py` and `docs/schema/vocab.json`.
>
> Two items need something only the owner can supply:
> - **R7c delegate:** a named person.
> - **R7d news-monitor activation:** the monitor lives in local staging.
>
> Applying the rulings to data rows is queued for the integrator of record in
> `tasks/QUEUE.md`.

Every open question from the 2026-11-01 tooling, debt, pilot and wave lanes that
needs the owner's ruling (AGENTS.md §2 rule 9). Each item has a recommendation and
its evidence. Agents hold the work an item gates until it's ruled.

**To rule:** reply "all as recommended", or give item numbers with changes.
Rulings that touch vocabulary need a dated SCHEMA revision before any data uses
the new value.

## Actions only the owner can take (no ruling needed)

| # | Action | Why | How |
|---|---|---|---|
| X1 | **Turn on CI** | No PR from any harness gets automated validation today | `docs/ci/README.md`: paste `docs/ci/validate.yml` into `.github/workflows/validate.yml` through the GitHub web UI |
| X2 | **First release + LICENSE** | The README promises releases and CC BY 4.0, but there is no release and no LICENSE file | `docs/RELEASE_HOWTO.md`; add a root `LICENSE` |
| X3 | **Get local staging into version control** (a private repo is fine) | Pass journals, the snapshot sync log, raw snapshots and denominator inputs exist only on one machine. F5 was already blocked by this. | Push the staging folder to a private repo |
| X4 | **Close or refresh stale draft PRs** | #7, #11 (and likely #8, #9) carry packets that QUEUE records as applied, so they mislead agents checking for claims | GitHub UI |
| X5 | **Publish the static explorer** (once built) | Chamber staff and members can use the Atlas without git | `docs/SITE_HOWTO.md` |

## Priority — public-data hygiene (found while rendering the static site)

### P1. PIC CRM references in public organization rows
- **The finding.** 31 organization rows carry PIC CRM references in `sources`,
  e.g. "CRM conflict adjudication …". 9 rows have descriptions that say a fact
  "rests on the CRM record only": ORG-001770, ORG-001805, ORG-001815, ORG-001833,
  ORG-001863, ORG-001872, ORG-001877, ORG-001890, ORG-001930.
- **What the rules say.** AGENTS.md §5.1 says the CRM "is never the cited source
  for a membership fact". §6 bars the CRM for people. Neither rule names other
  organization facts, but the CRM is described throughout as private and
  internal, and these rows publish the fact that CRM records exist and what
  they say.
- **Recommend.** Rule that the CRM is never a cited source in any public row.
  The integrator then re-sources these rows to public evidence, or drops them to
  tier U or C where nothing public supports the fact, and removes the CRM text
  from `sources` and descriptions.
- **Validator follow-up.** Add a validator tripwire on organization sources like
  the one people.csv already has.
- **Meanwhile.** The static site generator hides these strings.

### P2. Email-like string in a people record
- **The finding.** PERSON-000366's `public_profile_url` contains an individual's
  email address as a URL path.
- **Recommend.** The integrator replaces it with the institution's
  profile-page URL that has no email in it. Add a validator check that rejects
  `@` in `public_profile_url` (AGENTS.md §6).

### P3. Workshop paths in public `sources`
- **The finding.** Most organization `sources` strings embed local staging paths
  (`working/…`, `(staging …)`). They mean nothing to a public reader and leak
  internal file layout.
- **Recommend.** Rule whether `sources` should carry only public citations, with
  workshop provenance moved to the evidence rows or the pass journals.
  *Recommend yes,* as a dedicated cleanup pass.

## Rulings

### R1. Vocabulary: `site_type` (validator debt V-45)

**R1a.** Add `office_other` for in-scope non-HQ, non-sales offices (11 rows)?
*Recommend yes.*

**R1b.** Mixed-use addresses: keep one `site_type` (the dominant physical function)
and put the rest in notes? *Recommend yes.* This matches how ring and NAICS already
work.

**R1c.** Add `service_repair` for machinery service and repair centers (Ring 3)?
*Recommend yes.*

Evidence: `tasks/validator-debt-2026-11-01/PROPOSALS.md`, `v45_site_type_proposals.csv`.

### R2. Vocabulary: markets (from the pilot and wave lanes)

**R2a.** "Automotive" stated with no OEM or aftermarket split happens often. Add
`automotive_unspecified`, or keep the rule that it maps to nothing until the
source says which?
*Recommend adding `automotive_unspecified`.* Otherwise the most common market
claim in NE Ohio is lost.

**R2b.** Add a `tire_rubber_goods` market (suppliers to tire makers)? *Recommend
yes.* Tire is the defining Akron market.

**R2c.** Add `plastics_rubber_processors` (upstream customers: resin, additive and
compound suppliers selling to processors)? *Recommend yes.*

**R2d.** Add `cosmetics_personal_care`? *Recommend yes.* This is a recurring
packaging and compounding customer.

Evidence: `tasks/pilot-pic12-capabilities-2026-11-01/REPORT.md` (Observations 1),
and the wave lane reports.

### R3. Vocabulary: processes and certifications

**R3a.** Add a process `additive_dry_blending` (additive masterbatch and dry-blend
makers)? *Recommend yes.*

**R3b.** Add certifications `iso_45001` and `iso_17025` (testing labs)? *Recommend
yes.*

**R3c.** A certification is recorded only from a current certificate or a current
page that names a non-superseded edition? *Recommend yes.* Example: Colonial
Machine shows "ISO 9001:2005".

### R4. NAICS confidence scale

There are 18 rows using `low-medium` or `medium-high`. Keep the three-point scale
(high, medium, low) and round down, or adopt five points?
*Recommend keeping three points and rounding down.* The validator and SCHEMA §2.1
already say three.

### R5. `members.member_since` year-only

AGENTS.md §4 says a year-only date is invalid, but `validate.py` requires a
four-digit year for `member_since`. Which governs?
*Recommend an explicit exception:* `member_since` is a year field by design. Amend
AGENTS.md §4 to say so.

### R6. Scope items surfaced by the pilot

**R6a.** Etched Metal (SITE-001426) is mainly a metal nameplate maker, and plastic
printing is one line. Is it in scope as Ring 3/4, or excluded? *Recommend applying
the Ring 4 two-of-three test and logging it in `inclusion_log.csv`.*

**R6b.** SITE-001836 (Robin Industries, Independence, `hq_office`, ring 1). The
company's own site lists no Independence address. *Recommend routing it to
re-verification.* This is not a ruling, just a flag.

### R7. Process

**R7a.** Move from one `QUEUE.md` to one file per task (`tasks/open/T-####.md`)?
*Recommend yes, after the current campaign.* QUEUE.md is the main merge-conflict
hotspot for parallel harnesses.

**R7b.** Consolidate SCHEMA into a v2: fold the rulings into the rules and move the
history to a changelog (`docs/IDEAS_AND_RESOURCES.md` F-07)? *Recommend yes,* as one
dedicated pass with a diff review.

**R7c.** Appoint a delegate for routine battery items (G-02)? *Recommend yes.*

**R7d.** Activate the built news / WARN monitor (QUEUE "Weekly signals sweep")?
*Recommend yes.* Its hits only queue re-verification.

**R7e.** North America scope for held parents' Canada and Mexico plants (A-12)?
*Recommend holding until the US national spine is further along.*

**R7f.** Is a Form 5500 plan-participant count admissible as an employee-band input
(B-02)? *Recommend yes,* as `government_filing` with the plan year, banded, and never
as a precise headcount.

### R8. Vocabulary gaps from the wave (tranche 1, 150 sites)

Recurring gaps. Each was flagged in the lanes' `*_other_note` rows and none has
been settled. The candidate terms are listed below. *Recommend* adding the ones
marked ★ in a single dated SCHEMA revision. The rest stay in notes until they
recur.

**Markets:**
- ★ `automotive_unspecified` (R2a; about 30 sites)
- ★ `tire_rubber_goods` (R2b)
- ★ `food_processing_foodservice` (non-packaging)
- ★ `medical_healthcare_general` ("medical" without "device")
- ★ `chemical_mining_metals_processing`
- ★ `rv_powersports_trailers`
- ★ `telecom_datacom`
- `lighting`
- `hvac_plumbing_hardware`
- `law_enforcement_personal_protection`

**Processes:**
- ★ `additive_dry_blending` / pigment and colorant dispersion
- ★ `pressure_sensitive_tape_manufacture`
- ★ `potting_encapsulation_casting`
- ★ `fluoropolymer_lining`
- ★ `thermoforming` (type unstated)
- `rubber_molding` (type unstated)
- `vacuum_metallization`
- `low_pressure_molding`
- `bag_converting`

**Materials:**
- ★ `asa`
- ★ `specialty_elastomers` (HNBR / FFKM / CSM / butyl / ECO / fluorosilicone)
- ★ `polyester_vinyl_ester_resins`
- ★ `acrylic_pmma`
- `pps`, `pei`, `pbt`
- `tpv`, `tpo`

**Certifications:**
- ★ `iso_45001`
- ★ `iso_17025` (R3b)
- `sqf`
- `rcms`

### R9. Rows that aren't plants

The wave found corporate offices, warehouses, distributors and a supply store
carried as ring 1–2 `manufacturing_plant` rows. Examples: Jerico Wadsworth,
Knight Material East Canton, Mantaline Twinsburg, Gem City, Infinity
Composites, Promerus, Winsell.

*Recommend:* the integrator corrects `site_type` and ring from the lane evidence.
B14 already says an office row's ring is not the parent's. List any row whose
scope becomes doubtful (a distributor rather than a processor) in
`inclusion_log.csv` for a ruling.

---

## Addendum — new items from the federal-data lanes (2026-11-01)

> **RULED 2026-11-01 — "do it all" (repo owner, in session, in reply to these recommendations).** Recorded as SCHEMA v1.7.7. The validator now enforces R10 (optional `site_id` on registry links) and R11 (`EIN`).

### R10. Facility-grain registry IDs (FRS, TRI)
`registry_links.csv` is keyed to organizations (§4.8), but FRS and TRIFID IDs
identify facilities. The 2,156 existing TRIFID rows already carry this mismatch,
and the ECHO spine adds 2,350 FRS candidates. Options:
- **(a)** keep org-keyed rows with `:<site_id>` in `match_basis`;
- **(b)** add a nullable `site_id` column to `registry_links`;
- **(c)** create a separate site-keyed link table.

*Recommend (b),* with a validator rule: when `site_id` is present, it must belong
to `org_id`, and several IDs per site are allowed. Evidence:
`tasks/echo-frs-spine-2026-11-01/REPORT.md` §3.

### R11. Employer EIN registry value
Form 5500 publishes sponsor EINs.

*Recommend:* add a single `EIN` registry value and keep `EIN_NONPROFIT`
grandfathered. Mint an `EIN` row only on MATCH_ORG with a name match plus a
street match on one of that org's sites. 320 sponsors qualify today. Evidence:
`tasks/form5500-spine-2026-11-01/REPORT.md`.

### R12. Edition-less certifications
Several lanes met "ISO 9001 certified" (or IATF / AS9100) on current pages that
name no edition. R3c currently bars these.

*Recommend:* keep the bar. A standard stated with no edition is not recorded,
but it may be noted in site notes as "claims ISO 9001 (edition not stated)", so
a later certificate pass can settle it.

### R13. Size data sources and conflicts
Three band sources now exist:
- Form 5500 participants: R7f, organization-level.
- OSHA inspection `nr_in_estab`: site-level.
- OSHA ITA annual average employees: site-level; packet pending.

*Recommend this precedence for site bands:* ITA (most recent calendar year)
first, then the OSHA inspection (most recent), then Form 5500. Form 5500 applies
only to a single-establishment organization. Where sources disagree by more than
one band, the row goes to review, not to automatic application.

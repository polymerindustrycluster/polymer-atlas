# SAM PUBLIC entity scout — filtered leads only, 2026-11-16

Worker atlas-w16-sam-scout; controller-assigned claim `sam-entity-scout`; packet only. No data/ edits, IDs, evidence rows, canonical names/addresses, registry links or inclusion-log entries applied. First user: Atlas controller/PIC researcher; review non-use by 2026-11-23.

## Owner ruling and recommendation

The initial terms review held bulk acquisition on SAM's conditional legacy D&B restrictions. On November 16 the owner ruled in session **“Filtered, leads only.”** Controller instruction: download PUBLIC, exclude all D&B-sourced records and records last updated before **2022-04-04** (explicit correction of the initially stated 2026 cutoff); use the remainder only as discovery leads and government-issued UEI-link candidates. Never copy SAM names/addresses into canonical Atlas data: each fact must be verified against another source, following AGENTS §5. That ruling supersedes the initial hold; it does not waive D&B restrictions.

**Recommendation:** use name+street for targeted UEI identity review, name+city for targeted discovery/address research; do not apply name-only or street-only matches automatically. All proposals here are **held**, not applied. The 35 reviewed new UEI pair candidates need integration/identity approval. No population-wide number of mintable links is asserted.

## Source, rights, acquisition and filter

[Current SAM terms](https://sam.gov/about/terms-of-use) permit public sharing from public API versions subject to source-specific restrictions. Legacy D&B Open Data requires attribution and cannot be bulk accessed/used/disseminated as a substitute for the source. FOUO and sensitive responses do not authorize public views. Public registrant facts are discovery material here; no personal contact fields were indexed or published. Addresses remain private discovery candidates requiring home-address screening and independent verification before any publication.

[Official extract documentation](https://open.gsa.gov/api/sam-entity-extracts-api/) describes monthly PUBLIC active registrations plus registrations expired within six months, **not all firms or proven operating plants**. Two HTTP-200 official-page witnesses are hashed in `sources.json` and cached privately. [PUBLIC V2 layout](https://open.gsa.gov/api/sam-entity-extracts-api/v1/SAM%20Master%20Extract%20Mapping%20v6.0%20Public%20File%20V2%20Layout.xlsx) defines LAST UPDATE DATE (10), D&B OPEN DATA FLAG (24), ENTITY EVS SOURCE (122). The actual extract has 142 pipe-delimited fields; projection uses the documented positions and rejects unexpected widths.

Downloaded `SAM_PUBLIC_MONTHLY_V2_20261101.ZIP`, dated 2026-11-01, 148,636,178 bytes. SHA256 `2db04ae10f237f048b28b6354884431c7b8d61d122b437647b29d23a6cdb5e4d`. It contains a nested ZIP and then a 557,871,365-byte DAT. **911,820 source rows** counted independently, matching both BOF/EOF declared counts. Duplicate UEIs exist (including differing CAGE/DODAAC rows); source-row identity is retained, UEIs are not falsely assumed unique.

Two authenticated API requests (header only), plus one keyless S3 download = **3 total requests**, below the five-request cap. First HTTP 302 was a redirect, not refusal; the second API call followed the redirect without forwarding the key. `download.json` records the sanitized receipt, not a signed URL. Raw outer and inner ZIPs were deleted after hash/count reconciliation. Filtered index: controller persistence `persist/sam-entity-scout/sam.sqlite`, 275 MiB, under 1.5 GB. It retains only UEI/name/DBA/physical address/NAICS/CAGE/registration dates/status/EVS plus derived match keys and source row number; no contact fields.

| Source-row filter | Rows |
|---|---:|
| D&B EVS source or D&B Open Data flag | 466 |
| Valid update date before 2022-04-04 | 0 |
| Overlap of those two filters | 0 |
| Additional fail-closed missing/malformed date holds | 2 |
| Total excluded | 468 |
| Retained source rows | 911,352 |
| Distinct retained UEIs | 903,667 |

EVS input distribution: E&Y 830,406; blank 80,948; D&B 466. Blank EVS is not treated as D&B, but the date rule still applies. The D&B flag is blank on every input row. No dropped record's name/address is published.

## Match population and seeded manual samples

Every **5,026 organization** and **7,196 site** row in the baseline was queried. Reuses atlas.py name/street normalization, organization trade names (including held registrant aliases per B-ALIAS), parenthetical aliases and locality-stripped site names; ecosystem operators are resolved for sites. Organization matches use HQ city/state but have no organization street field. Street matches require state agreement; name+city requires state and city agreement. Each Atlas-ID/UEI pair has exactly one strongest class. Names alone may cross states; empty keys never match.

| Class | Atlas-ID/UEI pairs | Manually consistent / sampled | Wilson 95% | Rejected / uncertain |
|---|---:|---:|---|---|
| name+street | 685 | 20/20 | 83.9–100% | 0 / 0 |
| name+city | 1,436 | 14/20 | 48.1–85.5% | 4 / 2 |
| street-only, different name | 781 | 2/20 | 2.8–30.1% | 5 / 13 |
| name-only | 86,393 | 0/20 | 0–16.1% | 20 / 0 |

3,990 distinct Atlas records have at least one candidate. Samples are the 20 lowest SHA256 values of `20261116|class|Atlas-ID|UEI`, without replacement within each class. `sample.csv` holds all 80 manual judgments. VERIFIED means pair-consistent at target grain on manual inspection of held Atlas and indexed SAM fields; **not independent source verification**. REJECT rejects that match only, never an organization's existence/status. Uncertainties count as non-successes in the confirmed fraction; Wilson intervals describe that conservative consistency yield, not adjudicated independent identity precision. Sampling unit is a pair, not a parent; name-only is dominated by Sherwin-Williams cross-location pairs. Parent registrant identity cannot locate an individual plant.

## Proposals and remaining holds

| Proposal / metric | Result | Applied/held and settling fact |
|---|---|---|
| New UEI pairs in manually consistent sample | 35 (36 consistent pairs minus 1 existing link) | Held; independently confirm exact entity/site binding and integrate government-issued ID only |
| Population-wide mintable UEI links | Not measured | Held; review all proposed pairs, ambiguous UEIs/registrations and existing links |
| Street-less PIC-18 sites, all statuses/tiers | 577 in current baseline | Frame count, not the brief's older 419 |
| Those sites with name+city and nonempty physical street lead | 79 distinct sites | Held; exact site identity, another-source address and home-address screening |
| Unmatched polymer-NAICS UEIs in held PIC-18 cities | 100 | Held locality-screened leads in `lead_ueis.csv`; verify physical-address county and current polymer activity independently |
| County-verified unmatched PIC-18 polymer entities | Not measured | Held; city/ZIP is not county; no region assignment inferred |

Polymer screen: primary or listed NAICS prefix 3252, 3255 or 326, state OH, city casefold-exact in the held PIC-18 site city set, and no match to any queried Atlas row. This city screen can miss or overinclude county-border cases; 100 is **not** a verified PIC-18 count. Estate search for ZIP/county holdings was incomplete because the Documents inventory/RAG layers are unavailable on this Mac; no private CRM or unverified proxy was substituted. Primary/listed NAICS is registrant-level discovery, not proof of polymer production or a plant's code.

SCHEMA §4.13: SAM is `registry`; identity/UEI and code corroboration ceiling `supports_B`, registry address alone `supports_C`, claims banked on U rows `supports_U`. Owner's stricter rule here permits UEI links and leads only. No SAM-derived name/address evidence row is proposed. Registration dates/status are not operating-status evidence.

## Checks and reproduction

`python3 tasks/sam-entity-scout-2026-11-16/build.py` rebuilds all-shard matches and summaries from the private filtered index. Initial indexing additionally needs the raw archive, deliberately removed per brief; reacquisition is an explicitly budgeted action, not an automatic retry. No dependencies added.

`python3 tasks/sam-entity-scout-2026-11-16/check.py` reconciles source/retained/excluded counts, checks the filtered index and cache hashes, recomputes match totals, reproduces all seeded sample memberships, and recomputes summary/CI/lead counts. Negative controls reject D&B source, legacy date, unknown date and index-row loss. Missing caches fail closed. Source BOF/EOF counts and independent raw-line count were reconciled before deletion; after deletion their provenance is the stored intake receipt, not a fresh raw-file recount.

Proposed follow-ups: independent identity review for UEI candidates; own-source address verification for the 79 sites; county and polymer-operation verification for the 100 locality-screened leads. These are surfaced holds, not new tracked commitments.

Validation on this revision: packet check PASS (including four injected defects); offline builder rerun PASS after raw deletion; `python3 scripts/validate.py` PASS (0 errors); `python3 scripts/check_row_loss.py --base origin/main` PASS; `python3 scripts/export_vocab.py --check` PASS. No scripts/ edits, so full scripts unittest suite not run. Controller review and CI remain required; this packet does not close an issue or claim the independent identity/county holds complete.

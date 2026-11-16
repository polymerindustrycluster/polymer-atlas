# SAM PUBLIC entity extract scout — terms stop, 2026-11-16

Worker: atlas-w16-sam-scout. Claim: controller-assigned `sam-entity-scout`, under the November 16 binding worker contract. Packet only; no canonical data changes, evidence IDs, registry links, or inclusion-log entries. First user: Atlas controller/PIC researcher, for this wave's source selection; review non-use by 2026-11-23.

**Recommendation: do not apply any class.** The brief explicitly says a restrictive term stops the lane. A fresh read of SAM's terms found a conditional restriction on bulk **access and use**, as well as redistribution, of D&B legacy data. This is a terms hold, not an extract refusal or a finding that PUBLIC extracts are generally prohibited. The credential file was not opened; **0 authenticated extract requests** were made. No raw ZIP was created, so no raw ZIP remains to delete. No SQLite index was built.

## Terms and permitted redistribution

Two official pages were fetched directly, HTTP 200; exact hashes, UTC observation times and short raw-checked witnesses are in `sources.json`. The full HTML witnesses remain in controller persistence (the path in `build.py`), not Git.

- [SAM terms, Data Access and Restricted Data Use](https://sam.gov/about/terms-of-use): public sharing must use public API versions. Public-facing facts from that route can be shared subject to the applicable data-source restrictions, privacy requirements and any item-specific rights. FOUO/sensitive responses cannot provide a public view. This is not authorization to scrape the browser or automate Login.gov.
- The same terms require D&B attribution and prohibit bulk access/use/dissemination of D&B Open Data in amounts sufficient to substitute for the source. Covered fields include legal name and physical-address components. The terms identify entity registrations last updated before April 4, 2022 as applicable legacy records and say the Entity Validation Service source is identified in APIs/extracts. Other D&B fields also have commercial/resale/marketing restrictions.
- [GSA extract API documentation](https://open.gsa.gov/api/sam-entity-extracts-api/): PUBLIC is distinct from opted-out FOUO/Sensitive data. Monthly files cover active registrants plus entities expired within six months, not all firms or proven operating establishments. The scheduled November filename would be `SAM_PUBLIC_MONTHLY_V2_20261101.ZIP`; it was **not requested or verified as a downloaded file**.

Scout 4 checked general API access but did not record the legacy D&B bulk restriction in its SAM README. Its authorization interpretation remains useful; it does not remove this additional restriction. The monthly population may contain no restricted legacy rows, but that has not been measured. We do not infer that the whole extract is restricted, nor resolve the applicability of a narrower filtered acquisition ourselves.

## Deliverable and holds

| Proposal or measurement | Applied/held | Settling fact |
|---|---|---|
| Download/index complete latest PUBLIC extract | Held | Controller-approved lawful acquisition plan addressing legacy EVS/D&B rows before bulk access/use; confirmation of applicability if needed |
| Match every Atlas organization/site, including registrant aliases | Held | Terms-cleared extract and complete projected index |
| Name+street, name+city, different-name street-only, name-only precision | Held; not measured | Match frame and seeded 20-row hand checks for each available class |
| Mintable UEI links | Held; not measured | Source-verified UEIs and identity adjudication |
| Street-less PIC-18 physical-address candidates | Held; not measured | Source-cleared physical addresses, identity checks and home-address exclusion |
| Unheld PIC-18 polymer-NAICS entity leads | Held; not measured | Cleared extract, address-based county evidence, all-shard dedupe and scope follow-up |

`metrics.json` records null for every unavailable measurement, including extract hash/date/count and Wilson intervals (within the null per-class precision object); zero downloaded records is a workflow count, not a zero-yield estimate. The brief's 9 existing links and 419 street-less PIC-18 sites were motivation, not recounted findings here.

## Evidence posture if the hold is resolved

Under SCHEMA §4.13, SAM is `registry`: exact-entity identity/UEI/CAGE and code corroboration cap at `supports_B`; registry address alone caps at `supports_C`. A tier-U record's banked claim uses `supports_U`. Registration status/dates describe registration, not operating status. A registrant's NAICS is not proof of current site polymer activity; unmatched NAICS entities remain discovery leads until primary scope evidence is obtained. No tier or operating-status change is proposed.

## Reproduction and verification

`python3 tasks/sam-entity-scout-2026-11-16/build.py` regenerates the receipt offline and idempotently; it cannot load a key or call the API. `python3 tasks/sam-entity-scout-2026-11-16/check.py` verifies both inputs against their independent cache count, raw hashes, lengths and verbatim excerpt presence; recomputes all receipt counts; and rejects three injected defects (missing input, invented UEI yield, false witness hash). PASS on November 16. Missing caches fail the check. No parser/matcher/index implementation was added because the terms gate prevented acquisition.

Proposed follow-ups: resolve the conditional D&B legacy restriction and authorize a narrower acquisition plan if appropriate. Do not treat this packet as a request for a new commitment or as authority to resume extraction.

Repository checks: `python3 scripts/validate.py` PASS (0 errors); `python3 scripts/check_row_loss.py --base origin/main` PASS (no keyed row removed); `python3 scripts/export_vocab.py --check` PASS (current). No `scripts/` changes, so its unittest suite was not run. Draft packet remains subject to controller review and CI; no issue is closed by this lane.

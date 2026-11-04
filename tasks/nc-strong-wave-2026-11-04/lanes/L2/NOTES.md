# Lane L2 notes (NC STRONG wave, 2026-11-04)

17 input rows, 17 verdicts in `verdicts.csv`. No data/ edits, no git.

| Verdict | Count | Clusters |
|-|-|-|
| VERIFIED_NEW_SITE | 6 | 00150 IPEX, 00096 + 00062 Sealed Air, 00375 JELD-WEN/VPI, 00362 PTI, 00521 Lawrence |
| VERIFIED_NEW_ORG | 6 | 00107 Arjobex, 00297 Colony Tire, 00015 Stockhausen, 00294 RUBBERlogix, 00104 United Plastics, 00228 Schlaadt |
| REJECT | 2 | 00368 Reagents (lab chemicals), 00023 Albemarle Kings Mountain (lithium) |
| STILL_UNCERTAIN | 3 | 00443 Sarstedt, 00260 Pactiv, 00118 Eaton |
| DUPLICATE_OF | 0 | |

Tier B (own-site witness): 00150, 00375, 00362, 00521. Tier C: everything else that verified.

## Dedupe
Ran `atlas.py dedupe-check` (IPEX) plus a street/ZIP sweep of every sites shard for all 17 rows: no street-level duplicate. Name
hits were resolved by hand (see flags). Brand/domain search of the organization shards run for: ipex, reagents, sarstedt,
arjobex/polyart, colony tire, pactiv, eaton/aeroquip, sealed air/cryovac, jeld-wen/vpi, hickory springs/HSM/PTI,
stockhausen/evonik/ICIG, rubberlogix/new river, lawrence/quanex/amesbury, united plastics, schlaadt, albemarle.

## Flags for the integrator
1. **Wrong held-org pointer (00118 Eaton).** Fusion step 4 pointed at ORG-000655, which is Danfoss Power Solutions (trade name
   Aeroquip Corporation, Van Wert OH). Eaton Aeroquip LLC is Eaton Aerospace; the parent to link is ORG-000155. Row is
   STILL_UNCERTAIN; SCHEMA edge case says Eaton is not auto-included.
2. **HQ disagreements.**
   - ORG-002643 "Jeld-Wen": Atlas HQ Ringtown PA; JELD-WEN's own release says Charlotte NC.
   - ORG-005041 "HSM Solutions": Atlas HQ Monticello IA; hsmsolutions.com says Hickory NC. PTI (00362) is linked to ORG-004394
     (Hickory Springs Manufacturing Co.); ORG-004394 and ORG-005041 may be one group.
   - ORG-000566 Sealed Air: Atlas notes call its HQ unverified.
3. **US subsidiaries of foreign groups (parent decision).** I recorded the US operating company as the org and put the group
   in the note: Arjobex America (parent Polyart Group, Boulogne-Billancourt, France), Schlaadt USA (parent group, Lorch,
   Germany), Stockhausen Superabsorber LLC (owner ICIG; Stockhausen GmbH was Krefeld). If the integrator prefers parent-level orgs, the HQ
   would be France / Germany with `org_hq_county` empty. Also: `org_hq_*` for Arjobex, Schlaadt, Stockhausen, RUBBERlogix and
   United Plastics comes from a contact or footer address, not an explicit "headquarters" statement; blank them under the strict reading.
4. **Scope questions (owner rulings, not self-ruled).**
   - 00375 VPI: steel-reinforced polymer windows; extrusion on site not shown.
   - 00297 Colony Tire: retread shop "in-house", curing not stated (SCHEMA retread edge case needs cure/bond on site).
   - 00228 Schlaadt: group scope stated, New Bern production not stated; downgrade to STILL_UNCERTAIN if the stricter bar applies.
   - 00096/00062 Sealed Air: federal-only plant records; scope rests on company-level product page.
5. **Own-site witness limits.** 00015 uses the owner group's page (ic-investors.com); 00107, 00375, 00362, 00104 quotes are
   activity_only with the plant address on the same site in a separate span.
6. **Possible multiple establishments at one federal cluster (00150 IPEX Pineville).** IPEX says five NC manufacturing sites
   around Pineville; two ITA ids and two ECHO ids sit in this cluster.
7. **Pactiv (00260).** Pactiv Evergreen merged into Novolex (Charlotte) 2025-04-01; ORG-002537 may need an ownership note.
8. **Address variance (00297).** Own site prints 1429 N Broad St; federal row is 1415 N Broad St. Kept federal; dedupe-check on
   both numbers found no hit.
9. **Closures.** No dated closure found for any of the 17.

## Fetch routes and limits
- Direct fetch bot_blocked: reagents.com (home via Jina; sub-pages behind Cloudflare, not used as evidence), sealedair.com locations.
- novolex.com/locations renders no plant list; no Pactiv/Sealed Air plant-naming page was found.
- Search snippets were never used as quotes; every `own_quote` was copied from a page fetched in this run.
- Form 5500 check (AGENTS s2 rule 8) was not needed: no REJECT rests on closure or no-establishment.
- Effort: roughly 5 to 7 fetches per candidate; STILL_UNCERTAIN rows hit the cap without a primary plant witness.

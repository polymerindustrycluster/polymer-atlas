# Lane L4 notes (MI STRONG wave, 2026-11-04)

Input: 21 clusters. Output: `verdicts.csv` (21 rows, one per cluster_id; checked by script).

## Counts (unit: LF-MI STRONG clusters in input.csv)
| Verdict | Tier | n |
|-|-|-|
| VERIFIED_NEW_SITE | B | 6 |
| VERIFIED_NEW_ORG | C | 11 |
| REJECT | none | 2 |
| STILL_UNCERTAIN | none | 2 |
| DUPLICATE_OF | | 0 |

No row dedupes to an existing SITE. Step 3 (street) was clean for all 21 (`atlas.py dedupe-check`, name + street + city + zip). Step 2/4 org hits on 6 rows all became VERIFIED_NEW_SITE under the held org.

## Rejects
- LF-MI-00230 Kolene: Detroit plant strips paint from metal parts and sells salt-bath heat-treat chemistry. No polymer made.
- LF-MI-00045 Premiere Packaging: contract blend/fill/package of liquid products. Federal set carried 325991 and 326199 but the own page shows no resin or plastic work.

## Held (STILL_UNCERTAIN)
- LF-MI-00940 TriStar Molding: building "a total loss" in the 2024-02-25 fire (company Facebook post, reported 2024-02-26), WARN for 32 on 2024-03-11, 35 jobs cut per Plastics News. No rebuild or closure statement found, no own site, and the cluster still shows an F5500 (latest 2026-07-27). Not a REJECT: a fire plus WARN is not a dated closure outcome (AGENTS 3), and the Form 5500 address check was not run (no EFAST2 access in this lane).
- LF-MI-00028 Magni: zinc-flake coatings; own pages show Detroit as R&D only and an inorganic basecoat plus organic topcoat. Needs an own-site statement of Detroit manufacture and an owner scope ruling on zinc-flake coatings.

## Flags for the integrator (not self-ruled)
1. Held-record issues: ORG-000769 Creative Foam is filed with HQ Dayton OH, but the own site says corporate office is 300 N Alloy Dr, Fenton MI. ORG-002345 is a plant-level org ("Novares Us, LLC - Felton Plant"); the Grand Rapids site probably belongs under a Novares US LLC parent. Huntsman Auburn Hills is the polyurethanes division, so ORG-000372 vs ORG-000325 is a placement choice.
2. Weak tier C new orgs: Z Technologies (own site does not name Redford or say it manufactures there; federal only) and Renosol Clare (own site lists Bay City only). Advanced Auto Trends: own site prints 3485 Metamora Rd and no plant street, so 2230 Metamora Rd could not be tied to a plant; do not merge the two addresses. Novares and Inteva B tiers rest on the held org's scope, since the own page names the plant but not the process (see `note`).
3. Quote checks: Creative Foam quote contains the site's typo "begane". Renosol quote casing is as extracted (likely CSS caps). Novares quote uses an en dash. Erwin Quarder quote is German.
4. New-org tier follows the brief: a new organization is C even with an own-site witness; B appears only on new sites under held orgs.
5. Vocabulary gaps (no term used, so processes left blank): hot-cast polyurethane (Argonics); polystyrene foam extrusion not stated on the own page (R.L. Adams).
6. Blank federal counties filled from the city: Romulus = Wayne, Grand Rapids 49544 = Kent, Clare = Clare. "Genesee County" and "Kent County" normalized.

## Method and limits
- WebFetch summarizes pages through a small model; quotes were requested verbatim but the integrator must re-fetch and compare (as the brief says). Pages that failed or returned 403/404 (Plastics News, Inteva node/1351, Huntsman locations, novares.com parked) were treated as availability only.
- Several sources (EGLE air-permit staff reports, Michigan WARN notices, Rubber News, local news) were used for context in `note` only; none is cited as the own-site witness.
- No Form 5500 / EFAST2 bulk check was run, so no verdict here rests on a closure reject except none (both rejects are scope, not status).
- Roughly 6 fetch/search calls per candidate; the cap was held for all but TriStar (status) and Novares (activity quote), which took a few more.

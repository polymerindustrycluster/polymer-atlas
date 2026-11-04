# Lane L3 notes (MN STRONG wave, 2026-11-04)

16 clusters in, 16 verdicts out. Every `own_quote` was re-checked by machine against a fresh fetch of `own_url` (16 of 16 match; two needed a Jina render).

## Counts
| Verdict | n | Clusters |
|-|-|-|
| VERIFIED_NEW_ORG | 9 | 00124 Beacon Engineered, 00160 IMR / Northern Prairie Polymers, 00144 Manus, 00077 Hiawatha Rubber, 00119 T.O. Plastics, 00263 Aggressive Industries, 00223 Pride Solutions, 00075 Plastic Products Co, 00082 Rubber Industries |
| VERIFIED_NEW_SITE | 2 | 00115 Sunrise Fiberglass (under ORG-007026), 00105 Polytek South St. Paul (under ORG-002294) |
| DUPLICATE_OF | 2 | 00183 FilmTec (SITE-004958), 00194 Carfair (SITE-005421) |
| REJECT | 2 | 00269 Kurita America, 00243 Hawkins |
| STILL_UNCERTAIN | 1 | 00084 Berry Global Films, Mankato |

## Flags for the integrator
1. **00183 FilmTec is a same-plant call, not an address match.** Held SITE-004958 carries the legacy TRI address 7200 Ohms Ln; DuPont's own ISO certificate and the federal rows say 5400 Dewey Hill Road. Dedupe step 3 found nothing. I called it a duplicate by operator, city and activity (DuPont names one Edina FilmTec site). Please confirm; the fallback is VERIFIED_NEW_SITE under ORG-000805. If confirmed, correct the held street.
2. **00194 Carfair** is the same address as SITE-005421; the held row says "Heatherwood DR", the company and the federal row say "Rd". Suggest correcting the held street.
3. **00084 Berry Mankato.** The only own-site page I could fetch is an Amcor job posting that names the plant (Amcor Flexibles, Converter and Distribution, 2111 3rd Avenue) but names no polymer product. A sibling posting that mentions film extrusion returned 404. Settling fact: a live Amcor/Berry page stating film extrusion at this plant. Parent chain is ORG-002544 Berry Global, a child of ORG-002907 Amcor plc.
4. **HQ fields.** Only 00075 (Plastic Products Co, nav label "Corporate Office Lindstrom, MN") has an HQ filled. For the other eight new orgs the site prints an address but never labels it headquarters, so HQ is blank per the brief. The printed address is probably the HQ for 00160, 00077, 00263, 00223 and 00082 (single address on the site). Not assumed for 00144 Manus (plants in MN and FL), 00119 T.O. Plastics (Clearwater and Otsego) or 00124 Beacon (group parent separate).
5. **County is not in the federal row** for 00263 (Anoka) and 00223 (McLeod); I filled both from the city (Spring Lake Park / Hutchinson). 00269 and 00243 are rejects and carry derived counties for reference only.
6. **Scope calls.** Kurita (water-treatment chemistry, 86,000 sq ft production area, no polymer named) and Hawkins (corporate office only; industrial operations are at 3100 E Hennepin Ave, Minneapolis, a separate address I did not examine) are rejected on the "no polymer" test; both are reopenable if a page states a polymer product. Neither rejection claims closure.
7. **Held-org noise.** `step4` hit lists on 00119, 00075 and 00082 were substring noise (e.g. Roto Plastics, Proto Plastics, Proton Products). On 00075 the two named held orgs (3M ORG-003178, Seelye-Eiler ORG-003619) are different companies: PPC is a 100% ESOP-owned injection molder; Seelye-Eiler is a distributor under Activar. PPC has nine plants (other Lindstrom, Princeton, Center City, KY, TN, IA, IL, SC, AZ); only the Akerson St plant is claimed. Center City is Smith Metal Products (metal injection molding, out of scope).
8. **00160 name merge.** "Waterous Company" in the federal name variants is an unrelated South St. Paul firm; ignore it.
9. **00263 liveness.** The Aggressive Industries site footer reads Copyright 2009. Liveness rests on the 2026-02 ITA and 2026 OSHA rows.
10. **00124 Beacon** is part of Beacon Manufacturing Group (second EIN 844873467); the group parent was not checked for a separate org record. The plant was formerly Donnelly Custom Manufacturing per the site title.

## Method notes
- Dedupe: `dedupe-check` by name and street for every cluster, plus a csv-aware sweep of all organization shards for brand names (Berry, Beacon, DuPont, Hawkins, Kurita, Polytek, National Manufacturing, Activar, May Wes, Endurance) and domains. Org-level matches found: ORG-002544/002907 (Berry/Amcor), ORG-002294 (Polytek), ORG-004249 (Carfair), ORG-007026 (National Manufacturing Group), ORG-000805 (DuPont).
- Several company sites (beaconengineered.com, imr-inc.com) sit behind a bot wall (sgcaptcha). They fetched only through Jina Reader with the `cf-browser-rendering` engine; own_url stays the company URL.
- Quotes are plant_only for 15 of 16 rows because company sites rarely print address and activity in one span; the activity sentence is given in `note` or `deciding_fact`. Pride (00223) and Polytek (00105) are plant_and_activity.
- Tier: new orgs are C (per brief); the note says when the site is B-eligible. Sunrise and Polytek are new sites under held orgs with an own-site witness, so B.
- Trade-press closure search was run for Berry/Amcor Mankato only; no closure found. No other cluster has a closure signal in the pages read.
- Phones and emails are not in any quote. A quote that contained a phone number (00082) was shortened to the address.

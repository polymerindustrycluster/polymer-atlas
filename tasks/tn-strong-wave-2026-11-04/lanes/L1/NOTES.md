# Lane L1 notes (TN STRONG wave, 2026-11-04)

16 clusters in, 16 verdict rows out (`verdicts.csv`, columns per brief).

| Verdict | Count | Clusters |
|-|-|-|
| VERIFIED_NEW_SITE | 6 | 00053 FRS (ORG-000482, C), 00187 Altium Sparta (ORG-001408, C), 00241 Albea (ORG-003530, B), 00192 Republic K1 (ORG-002937, B), 00322 Zeus (ORG-003941, B), 00299 Nippon Paint (ORG-000464, B) |
| VERIFIED_NEW_ORG | 5 | 00196 Aeroflex USA, 00037 Omega Plastics, 00048 Farrell-Calhoun, 00368 Hamilton Plastics, 00186 Baxter Enterprises (all C) |
| REJECT | 4 | 00279 Kilgore Flares, 00243 Bioenergy Development Group, 00173 Hiwassee Packaging, 00571 Accurate Energetic Systems (all scope) |
| STILL_UNCERTAIN | 1 | 00208 Latham Fayetteville |
| DUPLICATE_OF | 0 | |

## Flags for the integrator
- **Republic Plastics 00192 is not a duplicate.** Republic runs two Knoxville plants: 5316 S National Dr (K1, this cluster) and 5428 N National Dr (held SITE-003246). Own About page lists both. Do not fold.
- **Latham 00208 (STILL_UNCERTAIN).** Held SITE-003070 is 1409 Winchester Hwy; cluster is 1405. Likely one plant, but a trade directory lists Trilogy Pools (acquired by Viking) at 1405. Settling fact: parcel record or Latham page showing one vs two buildings. Recommend an address alias on SITE-003070 if confirmed.
- **Albea 00241.** Live page is behind Cloudflare; the quote comes from the Wayback snapshot (2022-07-03). The integrator cannot re-fetch the live URL without a browser. Street corrected from 1209 Madison Street to 1209 New Tullahoma Hwy (own site).
- **Aeroflex 00196.** Own site prints 232 Industrial Park Road; federal says 282. I applied the brief (own-site address wins) and flagged it; confirm which is right. Parent is Aeroflex Company Ltd / Eastern Polymer Group (Bangkok), not held.
- **Omega Plastics 00037.** Federal registrant is America Plastics LLC dba Omega Plastics; own site says Omega Plastics, LLC. Unrelated to Havpak/Omega Erie PA (ORG-002313) and Omega Extruding CA (ORG-007428). The Carrollton TX campus is a separate site outside this lane.
- **Baxter 00186.** Baxter Enterprises and Hi-Tech Mold & Engineering SE share 466 Baxter Lane (two EINs). The integrator decides the organization of record. The MI and SC affiliates are not held. Held Tepro (590 Baxter Ln) is a different company.
- **FRS 00053 and Altium 00187** are tier C: no own-site page names the plant (FRS is a ParkOhio brand; Altium's Sparta address appears only on a label-guide PDF). The scope claim is org-level.
- **Hamilton Plastics 00368.** Federal county was blank; Hamilton (Chattanooga) assigned and flagged. Own page text came from a rendered fetch (raw HTML is script-built).
- **AES 00571.** Rejected for scope (explosives). Public record reports a fatal explosion on 2025-10-10; no closure found, none asserted.
- **Scope rejections are not closures.** No Form 5500 closure check was needed; none of the four rejects rests on closure.

## Method notes
- Dedupe: `atlas.py dedupe-check` on every street, name and domain; org shards searched for brand and common names (Zeus, Nippon, Latham/Viking, Albea, Altium, Park-Ohio, Omega, Hi-Tech, Baxter). Step-4 hit ORG-001080 (Ridge Corp, Ohio, "Zeus") is a different company.
- Quotes were copied from pages I fetched (direct, Jina or TinyFish rendered) and checked against saved page text where a saved copy exists (11 of 15 quotes machine-matched; Hamilton, Albea (archive), Zeus news and Bioenergy came from rendered fetches and were transcribed). Word counts are 25 or fewer.
- No data/ edits, no git.

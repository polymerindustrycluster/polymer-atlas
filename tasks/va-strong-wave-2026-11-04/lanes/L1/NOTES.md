# Lane L1 notes (VA STRONG wave, 2026-11-04)

12 clusters in, 12 verdict rows out (`verdicts.csv`). No data/ edits, no git.

## Counts
- VERIFIED_NEW_ORG: 5 (LF-VA-00156 Monoflo, 00121 Blue Ridge Industries, 00099 Hanwha Azdel, 00102 Busada, 00124 MGC Advanced Polymers)
- VERIFIED_NEW_SITE: 4 (00091 Rubbermaid/ORG-000555, 00211 Presto/ORG-002892, 00210 Printpack/ORG-003146, 00118 Southeastern Container/ORG-001118)
- DUPLICATE_OF: 1 (00111 CHT USA -> SITE-003305, judgement call, see below)
- REJECT: 1 (00185 Pyrotechnique by Grucci, out of scope)
- STILL_UNCERTAIN: 1 (00159 MAPEI Fredericksburg)

## Flags for the integrator
1. **00111 CHT**: the held SITE-003305 has no street, so the duplicate call rests on "one Virginia site" (CHT Group release and cht.com). Own site prints 7820 Whitepine Road, federal row 8021 Reycan Road, same ZIP 23237. Fill the street on the held site, or split if you disagree.
2. **00118 Southeastern Container HQ**: ORG-001118 carries Bowling Green, OH; the company's own locations page lists Enka, NC as "Corporate Office".
3. **00091 Rubbermaid parent**: the cluster hit is ORG-000555 (Rubbermaid, Mogadore OH). ORG-002045 (Newell Brands, Rubbermaid Home Products) also exists, and Winchester is Rubbermaid Commercial Products. Confirm which org holds it. The own-site quote is a 1968 history line; plastic nature rests on "resin mop bucket" and BRUTE on the same page, and processes and materials are blank.
4. **00099 Azdel and 00124 MAP** have non-US parents with no Atlas record (Hanwha Group, Korea; Mitsubishi Gas Chemical, Japan). HQ fields are the US entity's, taken from its own site.
5. **00124 County**: Colonial Heights is an independent city; federal row and held Colonial Heights sites say Chesterfield, kept.
6. **00210 Printpack**: own site prints ZIP 23603 and "Pickett's Line"; federal row has 23602. Own-site values used. The locations page needs JavaScript or Jina to show addresses.
7. **00159 MAPEI**: no fetched page says what the Fredericksburg plant makes; the MAPEI locations page was bot-blocked, which is an availability signal only. Settling fact is in the row.
8. **00102 Busada**: sold to a private investor in 2023, still operating. No closure.
9. **Scope**: none needed an owner ruling beyond the Grucci reject (explosives, no polymer).

## Method
- Dedupe: `atlas.py dedupe-check` on domain, name and street for every cluster, plus a name/brand grep of all organization and site shards (Mitsubishi Gas Chemical, Hanwha, Azdel, MGC, Monoflo, Busada, Rubbermaid, Presto). New-org rows had 0 hits.
- Fetches: TinyFish fetch for company pages; Jina Reader for printpack.com/locations and mapei.com. Every `own_quote` was copied from a page fetched in this lane, not from a search snippet.
- Naics_primary filled only where the federal set had one clear 6-digit code (or an obvious resin producer, 325211); blank otherwise.
- Tier: new organization = C; new site with own-site witness = B.

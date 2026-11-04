# Lane L1 notes (WI STRONG wave, 2026-11-04)

16 clusters in, 16 verdict rows out (`verdicts.csv`). Counts: VERIFIED_NEW_ORG 13 (tier C), VERIFIED_NEW_SITE 2 (tier B), REJECT 1, DUPLICATE 0, STILL_UNCERTAIN 0.

## Method
- Dedupe: `atlas.py dedupe-check` by name and street for all 16, then by domain for every candidate site found. No street hits. Org-level hits: Flambeau (domain and name = ORG-000340), Pregis (domain and name = ORG-002935), Five Star (name only = ORG-002061, a different company; see below).
- Own-site witnesses via WebFetch and WebSearch (domain-restricted where possible). WebFetch answers come from a small summarizer model and refuses to quote more than about 125 characters, so I re-ran an exact-string presence check on 14 quotes (Placon, Sussex IM, Cellox, Amalga, Copps, Kaysun, Trienda, Ci-Dell, F&M nav label, PAC, Phillips, Flambeau, Pregis, plus the Placon thermoformer phrase). Not re-checked: ChemDesign (single fetch), Five Star (passage returned contiguous), Wisconsin Film & Bag (read from the PDF with pdftotext).
- No 404/SSL/redirect failure was treated as evidence. No closure was found for any candidate. The Form 5500 gate (AGENTS 2 rule 8) was not triggered because no REJECT is for closure.

## Items for the integrator
1. **ORG-000340 Flambeau HQ is probably wrong.** Atlas has HQ Middlefield OH (shard OH). Flambeau's own site footer says "Flambeau World Headquarters, 801 Lynn Avenue, Baraboo, WI 53913". The 715 Lynn Ave Ste 100 row is the injection molding division. Baraboo also has blow molding and Technology Center cards, which may need their own site rows. HQ/shard correction is an owner ruling per AGENTS 2 rule 9.
2. **Phillips-Medisize street mismatch.** Own site prints 1165 S Airport Rd; federal row and one third-party listing say 1156. I used the own-site value per the brief.
3. **Five Star Plastics (Eau Claire) vs ORG-002061.** ORG-002061 is the West Portsmouth OH rotomolder, and its notes already keep the Eau Claire namesake separate. Intek Plastics (Hastings MN) acquired Five Star in January 2025 and is folding it into the Intek brand, so the right owning org (Five Star Plastics, Inc. vs Intek Plastics) is the integrator's call. The input's 5500 link (EIN 412034333) is marked POSSIBLE.
4. **Pregis Sussex witness is dated.** The own-site release is 2018-09-06. Pregis's 2025/26 WARN notice (effective 2026-04-30) is for Germantown WI, not Sussex. A tier-B site row stands on a 2018 own-site witness plus 2026 ECHO/ITA activity.
5. **Wisconsin Film & Bag.** The own-site witness is the parent (Novolex, brand Shields). Atlas has no Novolex org. I wrote no relationship. The Shawano recycling center is a separate address (1075 Airport Dr) and is not folded into this site.
6. **F&M Plastics** carries a federal variant "F & M COMPANIES, INC." with three EINs; parent/affiliate unresolved. The domain fmplastics.com is FM Corporation (Rogers AR), a different company.
7. **ChemDesign REJECT** is a scope reject (fine chemicals, no polymer on the site). If the owner later rules monomer/intermediate producers in scope (SCHEMA 3.2 B-VOC note), re-test.
8. Counties for Copps, Kaysun, Trienda and Ci-Dell were blank in the federal row; I filled them from the city (Ozaukee, Manitowoc, Columbia, Ozaukee). Integrator to confirm.
9. HQ fields are filled only where the own site labels the address as headquarters (Placon, Amalga, TriEnda) or says "based in" (Five Star). Elsewhere blank.
10. `naics_primary` is filled only for Phillips-Medisize (326199) and PAC (326111), the only clusters whose federal NAICS set has a single 6-digit code. All other sets are multi-code with no clear primary.
11. Tier rule applied as briefed: new org = C even where the site has an own-site witness (it would be B once the org exists); new site under a held org with own-site witness = B.

## Not done
- No second-source check on third-party facts quoted in notes (Intek HQ was own-site; Molex ownership was the Phillips-Medisize footer).
- Processes and materials are limited to terms the fetched pages state; sites were not crawled beyond about 6 fetches each.

# Lane L3 notes (IL STRONG wave, 2026-11-04)

Input: 20 clusters. Output: `verdicts.csv` (20 rows, 22 columns, checked with a CSV parse).

## Counts
- VERIFIED_NEW_ORG: 10 (all tier C): MBL (USA), Aargus, D6 Inc (Richmond), NAPCO, Unichem, Clayens, Hansen, Rockford Molded, Midwest Can, Foremost.
- VERIFIED_NEW_SITE: 5. Tier B: Winpak Sauk Village (ORG-003575), TOPPAN Franklin Park ex-Sonoco Clear Pack (ORG-001117). Tier C: Pretium Paris (ORG-000523), D&W Elk Grove Village (ORG-003470), Mauser Addison (ORG-000717). Pretium, D&W and Mauser all have an own-site page that names the plant but does not state what that plant makes.
- STILL_UNCERTAIN: 3 (S&S Urethane, Pactiv Franklin Park, Daubert).
- REJECT: 2, both scope (Belle Aire fragrance, PMP gluconate). No closure rejects, so the Form 5500 closure gate was not triggered.
- DUPLICATE_OF: 0. No cluster had a step 3 (street) hit; the four step 2 hits were organizations only and became new sites.

## Calls the integrator should look at
- LF-IL-00242: operator changed. Good Natured Products (Ex-Tech Plastics) sold the Richmond extrusion plant to D6 Inc on 2025-12-04. Business Wire returned 403, so the release was read through search summaries and mirrors; re-fetch before applying. Own site only lists Richmond, IL.
- LF-IL-00255: federal rows still say Sonoco Clear Pack, but Sonoco sold Thermoformed and Flexibles Packaging to TOPPAN on 2025-04-01 and TOPPAN's locations page lists the Franklin Park address.
- LF-IL-00460: Clayens has a foreign (French) parent; HQ left blank. Needs a placement ruling (AGENTS section 3).
- LF-IL-00559: Pretium filed Chapter 11 on 2026-01-28 and is closing Philmont NY; nothing found for Paris IL.
- Tier C on new sites (D&W, Mauser): own page names the plant but not what is made there.
- Quotes were taken from WebFetch extraction output (a small model), not raw HTML, so character-for-character matches are unconfirmed. Re-fetch each `own_url` as planned. Two quotes carry fragments (Foremost, Mauser) that are shorter than the sentences they come from.
- County for Hansen (Kane), Rockford Molded (Winnebago) and Foremost (Cook) was blank in the federal row and is entered from the city and ZIP; confirm.
- processes/materials are filled only where a page read says so; several are blank on purpose.
- naics_primary is filled only when the federal set has one clear plastics/rubber code (326199 for Pactiv, TOPPAN, Hansen, Rockford, Foremost) and blank where two 6-digit codes compete.
- County casing was normalized from the federal row (Mc Henry and Mchenry to McHenry, Dupage to DuPage); no county was changed otherwise.
- NAPCO and Midwest Can org HQ blank is a choice: each own site prints one address that is not labeled HQ. D6 HQ county is blank for the same reason (site gives city and state only).
- Mauser quote: the locations page shows both a hyphen and an en dash in the listing; I used the hyphen form. Known exact-match risk.

## Fetch effort
About 3 to 6 fetches or searches per cluster. Own-site fetch failures (410 on Pactiv postings, 403 Business Wire, 404 on some guessed paths) were treated as availability signals, not evidence.

# Tranche 2, lane 2 report — PIC-12 capability wave (2026-11-01)

This is a packet, not a data change. The lane's tool refused report files, so
the orchestrating session saved this report from the lane's hand-back.

- **Pin:** `c0192b8` at lane start.
- **Checks:** every row is `own_site`, with a URL and a quote of ≤ 25 words. The
  lane's builder checked quotes as substrings of the fetched text and values
  against vocab v1.7.6, and found no failures and no duplicates.
- **Method:** curl only, with no bot-wall workarounds. One WebSearch looked for
  Poly Tech's real domain and recorded nothing.

## Results (unit: assigned Ohio site rows, n = 55)

VERIFIED 25 (45%) · STILL_UNCERTAIN 30 · REJECT 0.

**In-vocab values (unit: packet rows):** 300 in total.

| field | site | org | total |
|---|---:|---:|---:|
| processes | 57 | 23 | 80 |
| materials | 68 | 28 | 96 |
| markets_served | 66 | 47 | 113 |
| certifications | 11 | 0 | 11 |
| **all** | **202** | **98** | **300** |

Another 20 rows are off-vocab (`*_other_note`). Of the in-vocab rows, 290 are
VERIFIED and 10 are row-level STILL_UNCERTAIN:
- edition-less certifications at IER Fujikura and Specialty Hose;
- self-declared cGMP at ADCAL;
- IER's silicones row, which belongs to its sister company;
- Dalton's org-scope rows.

**Site-scope certificates read:**
- **Transcendia Strongsville:** ISO 9001:2015, from the PJR annex, valid to
  2028-12-15.
- **Qualiform:** ISO 9001:2015, Intertek, valid to 2027-07-22.
- **Polychem:** ISO 9001:2015, Intertek, valid to 2027-09-12.
- **Buckeye:** ISO 9001:2015 and AS9100, named on the page but undated.

**Yield:**
- **Site-scope values:** 3.5 per assigned site, 7.6 per VERIFIED site. All scopes
  together: 5.5 per site.
- **Markets:** present at 20 of 55 sites at site scope, and 37 of 55 counting org
  scope.
- **Coverage:** 45 of 55 sites got at least one value.

**Plant ties:**
- **Certificate annexes or plant-named pages:** Transcendia (converting only at
  22889 Lunn Rd), Qualiform, Polychem, GSH, JACO, Evans, Zero D, Pharmacy-Lite.
- **Org scope only:** Day-Glo, Multibase, Sherwin-Williams HQ, Euclid Chemical,
  Synthomer ATC, DuPont, Dalton, Raven, Rubbermaid, Ohio Foam, Hyload, ASK,
  Polaris, ChromaScape, Master Builders, RPM Industries, Comdess, Certon/HAR,
  Vibrantz Orrville, Paramelt.

## Fetches

206 attempts, 3.7 per site.

- **Cap exceeded once:** Transcendia took 8 attempts (6 distinct URLs). The
  extra 2 came from a scratch-file collision in the lane's own tooling.
- **Hard availability failures: 26 of 206 (12.6%).**
- **The lane's own misses:** 6 guessed 404s.
- **No usable content at all (8 sites):** Paddington (parked domain), Sealed
  Air, Full Circle, Republic Powdered Metals, Vinyl Profiles, Poly Tech (dead Wix
  domain), Custom Pultrusions, Johnsonite.
- **Unavailable is not closed.** None of these is closure evidence.

## Vocabulary gaps (flagged, not settled)

- **Processes:**
  - rubber molding with the type unstated;
  - rubber-to-metal bonding;
  - cast polymer / cultured marble;
  - polyurethane casting;
  - adhesive-patch manufacture;
  - cut-and-sew of textile laminates;
  - vinyl-window fabrication.
- **Materials:** preceramic polymers, polyimide (Vespel), PEI/Ultem, textile
  laminates.
- **Markets:** nutraceutical, firearms / law enforcement, jewelry, plumbing.
- **Certifications:** edition-less ISO / AS9100 / IATF / ISO 17025 statements
  need an R3c follow-up ruling. Is a standard named without an edition
  recordable as "claimed"?
- **v1.7.6 terms used:**
  - `automotive_unspecified` (14 rows);
  - `medical_healthcare_general` (11);
  - `specialty_elastomers` (2: FFKM and fluorosilicone);
  - `thermoforming_unspecified` (2);
  - `tire_rubber_goods` (1);
  - `food_processing_foodservice` (1).
  - IER names both OEM and aftermarket automotive, so both values were proposed.

## Hygiene findings (not resolved — for the integrator)

**Dated company statements with missing or moved sites:**
1. **SITE-001539 ChromaScape.** The company's own page says the HQ moved to
   Independence in 2021 and the Ohio production facility moved to Stow in 2022.
   The Atlas row is Twinsburg, which no page names, and the Independence and Stow
   sites may be missing. This is a dated company statement; check the Form 5500
   and the dated outcome before any status change.
2. **SITE-000104 Transcendia Strongsville.** The certificate annex shows only
   converting at this address, so the row's `extrusion_film_cast` /
   `films_flexible_packaging` are unsupported here. Hebron OH is another plant,
   outside PIC-12.

**Wrong or unconfirmed addresses:**
3. **SITE-001391 Ohio Foam.** The company's own site prints only a Bucyrus PO box
   (Crawford County) and never names Youngstown.
4. **SITE-002033 M. Argueso / Paramelt.** North American sites are listed as
   Muskegon and Rosemead only; Cleveland is absent. That omission is not closure
   evidence.
5. **SITE-000576 Raven Concealment.** The site says "based in Cleveland". The
   Atlas row is North Ridgeville (Lorain County).
6. **SITE-000168 Euclid Chemical.** The company prints 19215 Redwood Rd; the
   Atlas has 19218.
7. **SITE-000237 All Foam Products.** The page title says Buffalo Grove IL, while
   the contact page gives Middlefield.

**Brand pages and dead domains:**
8. **SITE-001420 Hyload.** The domain redirects to IKO HyKote, and no Wadsworth
   plant is named.
9. **SITE-003478 Johnsonite.** Now a Tarkett landing page.
10. **SITE-000020 Paddington.** Parked domain, which is a liveness question.
11. **SITE-002063 Poly Tech.** The org `website` field is not a valid URL.

**Scope doubts (owner):**
12. **SITE-001667 Eleven 10.** Sewn textile gear, and the city is Cleveland per
    the site versus Westlake in the Atlas.
13. **SITE-000315 Dalton.** A contract-manufacturing network.
14. **SITE-000272 Buckeye Rubber.** Molding by partnered manufacturers, so it is
    distributor-like.
15. **SITE-001485 Polaris / Modern Builders.** No page names 45 Karago Ave;
    `vinyl_window_manufacturing` is not in the vocabulary.

**Possibly unheld sites:**
16. **SITE-000217 Synthomer.** The company also lists Beachwood OH, which has no
    Atlas row.

**Not corroborated by the company's own site:**
17. **SITE-000333 DuPont Valley View and SITE-000042 Multibase.** No plant is
    named for either.

**Certifications:**
18. **SITE-001718 RPM Industries.** "ISO 9001:2008" is superseded, so it is not
    recorded. No Elyria address is named.

**Unreachable by every route:**
19. **SITE-000373, 001800, 001939, 002114, 000251.** Availability only.

The per-site table is in the lane's hand-back. The per-site verdicts and settling
facts are in `verdicts.csv`.

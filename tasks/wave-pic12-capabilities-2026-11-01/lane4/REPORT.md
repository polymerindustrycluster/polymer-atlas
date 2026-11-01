# Lane 4 packet: PIC-12 capability wave, tranche 1 (2026-11-01)

**This is a packet, not a data change.** Lane 4 never edits `data/`, allocates IDs, commits or pushes. Every row in `packet.csv` is class `own_site`, carries the exact URL and a quote of 25 words or fewer, and the quote was checked programmatically as a substring of the page text I fetched (whitespace-normalised; Kent Displays' pages contain zero-width spaces inside some lines, which the check ignores). All fetches were curl through the configured proxy. WebFetch was used once each as a second route on the three sites curl could not read at first (Lubrizol, Trans-Foam, MES); it returned 403/503 each time and nothing was quoted from it. No `tier_effect` is proposed. Org-scope rows use the ORG id as `record_id`. Fetched page text is in `/tmp/claude-0/wave/lane4/` (outside the repo).

Pinned: `git rev-parse HEAD` at lane start = 665e5c595d5b415be22b18fda41f85c56208d03b (the wave's pinned commit). Assignment: `lane4_assignment.csv`, 30 site rows (all in PIC-12 counties, ring 1 or 2 per the brief).

## Results (units stated)

**Sites verdicted (unit: assigned Ohio site rows, n=30):** VERIFIED 15, STILL_UNCERTAIN 15, REJECT 0.
Rule: VERIFIED = at least one in-vocab processes, materials, markets_served or certification value stated on the company's own site at **site** scope. Every STILL_UNCERTAIN names its settling fact in `verdicts.csv`. No REJECT: nothing found was a dated closure or non-establishment fact; the unreachable sites are availability failures only.

**In-vocab values proposed (unit: packet rows, one per record, field, value):** 162 total.

| field | site scope | org scope | total |
|---|---|---|---|
| processes | 30 | 8 | 38 |
| materials | 59 | 12 | 71 |
| markets_served | 22 | 21 | 43 |
| certifications | 8 | 2 | 10 |
| **all** | **119** | **43** | **162** |

Plus **16 off-vocab rows** (`*_other_note`, marked OFF-VOCAB, row verdict STILL_UNCERTAIN): processes_other_note 4, materials_other_note 4, markets_other_note 5, certifications_other_note 3. Two in-vocab cert rows are also row-level STILL_UNCERTAIN (APC ISO 9001 announcement is undated; Dura-Line ISO 9001 is edition-less on a history page); the other 160 in-vocab rows are VERIFIED at row level. Several site-scope rows reconfirm values the site row already carried (Ferriot injection_molding, Lattice composites_frp, Salem-Republic hose_belting_manufacturing).

**Measured yield**
- Site-scope capability values (processes, materials, markets) per assigned site: 111/30 = 3.7. Per VERIFIED site: 111/15 = 7.4. All in-vocab values, all scopes, per assigned site: 162/30 = 5.4.
- Sites with at least one `markets_served` value: **8/30 (27%) at site scope; 17/30 (57%) counting org scope**.
- Sites with at least one site-scope `processes` value: 12/30 (40%).
- Sites with at least one in-vocab value at some scope: 24/30 (80%). The six with none: Chemigon, Trans-Foam, Lubrizol (unreachable), Gem City (a sales rep), Blade-Tech and J.J. White (off-vocab notes only).
- VERIFIED rate 15/30 = 50% (n=30, wide interval; the pilot was 48%).

**Plant-specificity (hard rule).** Org scope only, nothing pushed down: PPG Barberton, Vibrantz Mayfield Heights, Dura-Line (Accessories), Sherwin-Williams Massillon, Step2 Streetsboro, PKG Olmsted Falls, Kent Displays, plus two office-suite rows (Promerus, Winsell). Kent Elastomer is split: the Mogadore row gets site scope only for what the company's own pages tie to Mogadore (extrusion; FDA registration and ISO 13485 for all three facilities); materials and markets stay at org scope. Single-location companies with one printed address got site scope, and each row's `notes` says why.

## Fetches (unit: fetch attempts, including WebFetch retries)

- **99 total** across 30 sites, 3.3 per site, maximum 6 (Lattice, MES); the 6-fetch cap was respected.
- Hard availability failures (403, 500, 503, TLS error, connection reset, captcha challenge): **10/99 = 10.1%** (Lubrizol 403 + WebFetch 403; Trans-Foam reset x2 + WebFetch 503; MES TLS + WebFetch 503; Chemigon www TLS name mismatch; Ferriot apex HTTP 500; Lattice /products/ sgcaptcha 202).
- Add content-free 200s: 2 (chemigon.com and http://chemigon.com redirect to odoo.sh, the Odoo hosting landing page): **12/99 = 12.1%**.
- My own misses (not availability): 3 guessed 404s (Lattice x2, P&E x1) and 1 redundant redirect (Sherwin-Williams /about to the same page).
- Sites with no usable company content from any route: **3/30 (10%)**: Chemigon, Trans-Foam, Lubrizol. All three are STILL_UNCERTAIN; none is evidence of closure or absence. No Form 5500 check was run and no REJECT is proposed.
- Routes that recovered content: Ferriot via `www.` after the apex returned a 500; MES via plain `http://` after the HTTPS chain failed (certificate verification was never bypassed).
- **Not done:** no bot-wall workaround (no user-agent changes, no captcha handling). Lubrizol (Cloudflare) and Lattice's /products/ (sgcaptcha) need a human browser or another route.

## Vocabulary gaps met (owner rulings; flagged in `*_other_note`, not settled)

- **No textile-treating process** (J.J. White: RFL adhesion and release treatments, liner sizing/finishing).
- **No thermoset resin / prepreg / SMC-BMC formulation process** (Lattice). composites_prepreg_autoclave and composites_compression_smc_bmc describe part-making.
- **No PEI / ULTEM material** (RP+M); peek_high_performance does not apply.
- **No polynorbornene / cyclic olefin or electronic-grade specialty polymer material** (Promerus).
- **No optical-film / liquid-crystal-film material** (Kent Displays).
- **No tire market** (Chem Tech dispersions; also tire noted in the pilot) and **no telecom/networking market** (Dura-Line).
- **No firearms / law-enforcement / military-gear market** (Blade-Tech); aerospace_defense was not used for it.
- **No automotive OEM/aftermarket split** on FTM ("automotive to energy") and Kent Displays; **no energy sub-split** on FTM. PPG's page says "Automotive OEM" outright, so automotive_oem is proposed there; "Automotive Refinish" was not mapped to aftermarket.
- **Certifications:** no TL 9000, ISRS (DNV safety), SQF or FDA IMS term (Dura-Line, Kent Elastomer); no ISO 45001 (carried over from pilot, not met here). FTM says only "An ISO certified company" (standard unnamed), so iso_9001 was not proposed.
- **No low-pressure-molding or vinyl-window-fabrication process** (Kent Displays mapped to injection_molding with a note; Vinylume left as a note).
- **Mapping calls the integrator may want to override:** ultrasonic welding to ultrasonic_solvent_bonding (Ferriot); aircraft/aviation to aerospace_defense (PPG, Salem-Republic); vinyl to pvc (Vinylume); "electrical" to electronics_electrical and "natural gas" to energy_oil_gas (Dura-Line); "Industrial Automation" to general_industrial (Ferriot); bubble-stability/frost-line control to extrusion_film_blown (PKG; the page never says "blown").

## Hygiene findings (for the integrator; none resolved)

1. **SITE-000016 / ORG-000017 Chemigon:** `chemigon.com` and `http://chemigon.com` redirect to odoo.sh (Odoo hosting platform landing page); `www.chemigon.com` fails TLS name check. The org `website` field points at a domain that no longer serves company content. Availability only; needs another route and a Form 5500 / dated-outcome check before any status change.
2. **SITE-000061 Ferriot:** own site prints 1000 Arlington Cir, Akron, OH 44306-3973. The site row zip is 44312 (the superseded FRS street, 2685 Mogadore Rd). The notes already record the street correction; the `zip` column was not updated.
3. **SITE-000375 / ORG-000351 Gem City Plastic Machinery:** own site: "Manufacturer's representative for industry-leading equipment companies", a sales office at 10235 Brecksville Road Suite 101. It is carried as a `manufacturing_plant`, ring 1. Scope/ring is an owner ruling; this is not a REJECT.
4. **SITE-000527 / ORG-000492 Pilot Plastics:** PLP's own history page: "2023 PLP Acquires Pilot Plastics ... Located in Peninsula, Ohio, it becomes PLP's third U.S. manufacturing plant". ORG-000492 has no `parent_org_id`, and its `website` is `plp.com` (the parent's). Preformed Line Products Company is ORG-004564 in the tree. Parent/successor handling is the integrator's call.
5. **SITE-000628 / ORG-000589 Step2:** About page: plants "in Streetsboro and Perrysville". FAQ: "We manufacture our products at several locations throughout the state of Ohio, but product can only be picked up at our Streetsboro, OH warehouse location". The Streetsboro row (ring 1 `manufacturing_plant`, 10010 Aurora Hudson Rd) may be HQ/warehouse rather than a plant; no page ties rotational molding to a specific plant.
6. **SITE-001396 / ORG-000176 Kent Elastomer:** own About page lists three Ohio facilities: Kent (HQ, latex and dip), Mogadore (extrusion), Winesburg (assembly, quality, shipping). The Atlas has only the Kent and Mogadore rows for this org; **Winesburg is missing**. The certifications page names Winesburg too (FDA registered, ISO 13485:2016, SQF, IMS).
7. **SITE-000169 / ORG-000007 Vibrantz:** the contact-page location dropdown lists Ohio entries Ashtabula, Cleveland, Independence, Lockland, Mayfield Heights and Orrville. The Atlas has Ashtabula (SITE-000006), Mayfield Heights (SITE-000169, `hq_only`) and Orrville (SITE-001842); **Cleveland, Independence and Lockland are not carried** (Independence and Cleveland are in PIC-12 counties; entry types are not stated).
8. **SITE-000336 / ORG-000315 Dura-Line (Accessories):** the contact page lists both Elyria plants (860 Garden St and 669 Sugar Ln) among ~20 plants. The site row's existing `processes` value (`tape weaving; accessory assembly`) is not in vocab.
9. **SITE-003469 Lubrizol:** the row's existing `materials` value (`thermoplastic polyurethane (Estane TPU); hyperdispersants`) and the `TPU synthesis` part of `processes` are not in vocab. The own site was unreachable (Cloudflare 403), so nothing was re-checked.
10. **SITE-001875 Expert Gasket & Seal:** the site calls itself "a leading distributor of custom and standard gaskets"; molded rubber parts come from "partner molders" (domestic and imported). Die/flash cutting is the only in-house process shown, so the ring-1 `manufacturing_plant` scope is a doubt for the owner. No molding process was proposed.
11. **SITE-000564 Promerus / SITE-001663 Winsell:** the own sites label the address "Our Office" (Promerus) and print an office suite (Winsell, Suite 270), yet both rows are ring-2 `manufacturing_plant`. Promerus's page states expertise, not manufacture, so polymerization was not proposed.
12. **SITE-000481 MES:** `https://www.mespecialties.com` fails the certificate chain (curl 60), while the org `website` field is the https URL. The molded/extruded pages list rotational molding and blow molding with 75 to 3,000 ton presses and link to a sister domain (`extrude-n-mold.com`); this reads like shared boilerplate, so rotational_molding and blow_molding were **not** proposed. Cleanroom facilities are claimed without an ISO class, so no cleanroom cert was proposed.
13. **SITE-001437 Kent Displays:** the own site prints no street address (contact page: phone and email only); the Atlas street comes from USPTO/directories (already noted on the row). The about page says "our facilities" (plural).
14. **SITE-000417 J.J. White:** one-page site marked "site maintained ... 2020"; liveness is not independently shown (not evidence of closure).
15. **SITE-000228 APC / SITE-000201 Salem-Republic:** APC's ISO 9001:2015 line is an undated announcement. Salem-Republic's ISO 9001:2015 certificate covers calendered product only (not the hose line). Both are noted on the rows.
16. **SITE-001396 Kent Elastomer:** the SQF cert cited is "Fundamentals Edition 1", which looks superseded; it was flagged, not recorded (and has no vocab term).

## Per-site summary

| site_id | site | verdict | site-scope capability values | site-scope certs | org-scope values | off-vocab notes | fetches |
|---|---|---|---|---|---|---|---|
| SITE-000016 | Chemigon LLC — Akron | STILL_UNCERTAIN | 0 | 0 | 0 | 0 | 3 |
| SITE-000061 | Ferriot, Inc. — Akron | VERIFIED | 10 | 0 | 0 | 0 | 4 |
| SITE-000088 | PPG Industries, Inc. — Barberton | STILL_UNCERTAIN | 0 | 0 | 7 | 0 | 3 |
| SITE-000121 | Lattice Composites — Solon | VERIFIED | 8 | 0 | 0 | 1 | 6 |
| SITE-000169 | Vibrantz Technologies — Mayfield Heights | STILL_UNCERTAIN | 0 | 0 | 3 | 0 | 2 |
| SITE-000201 | Salem-Republic Rubber — Sebring | VERIFIED | 12 | 1 | 0 | 0 | 3 |
| SITE-000228 | Advanced Polymer Coatings — Avon | VERIFIED | 2 | 1 | 0 | 0 | 4 |
| SITE-000263 | Blade-tech Industries — Streetsboro | STILL_UNCERTAIN | 0 | 0 | 0 | 2 | 4 |
| SITE-000289 | Chem Tech — Middlefield | VERIFIED | 4 | 1 | 0 | 1 | 4 |
| SITE-000336 | Dura-Line (Accessories) | STILL_UNCERTAIN | 0 | 0 | 5 | 2 | 3 |
| SITE-000375 | Gem City Plastic Machinery, Inc. — Brecksville | STILL_UNCERTAIN | 0 | 0 | 0 | 0 | 1 |
| SITE-000417 | J. J. White Products, Inc. — Cleveland | STILL_UNCERTAIN | 0 | 0 | 0 | 2 | 1 |
| SITE-000447 | Lewart Co., The — Cleveland | VERIFIED | 10 | 0 | 0 | 0 | 3 |
| SITE-000481 | Molded Extruded Specialties, Div. of Frank Novak & Sons, Inc. — Cleveland | VERIFIED | 28 | 0 | 0 | 0 | 6 |
| SITE-000527 | Pilot Plastics — Peninsula | VERIFIED | 1 | 0 | 0 | 0 | 3 |
| SITE-000564 | Promerus — Akron | STILL_UNCERTAIN | 0 | 0 | 2 | 1 | 4 |
| SITE-000592 | RP+M — Avon Lake | VERIFIED | 6 | 2 | 0 | 1 | 1 |
| SITE-000628 | The Step 2 Company — Streetsboro | STILL_UNCERTAIN | 0 | 0 | 5 | 0 | 3 |
| SITE-000667 | Vinylume Products, Inc. — Youngstown | VERIFIED | 2 | 0 | 0 | 1 | 2 |
| SITE-001396 | Kent Elastomer Products — Mogadore | VERIFIED | 1 | 2 | 5 | 1 | 4 |
| SITE-001437 | Kent Displays — Kent | STILL_UNCERTAIN | 0 | 0 | 6 | 2 | 5 |
| SITE-001538 | Sherwin-Williams — Massillon | STILL_UNCERTAIN | 0 | 0 | 1 | 0 | 3 |
| SITE-001663 | Winsell Incorporated — Medina | STILL_UNCERTAIN | 0 | 0 | 2 | 0 | 3 |
| SITE-001710 | FTM ENGINEERING GROUP — Willoughby | VERIFIED | 3 | 0 | 0 | 2 | 4 |
| SITE-001747 | FastForming.com LLC — Rittman | VERIFIED | 10 | 1 | 0 | 0 | 5 |
| SITE-001824 | PKG, LLC | STILL_UNCERTAIN | 0 | 0 | 7 | 0 | 4 |
| SITE-001875 | Expert Gasket & Seal LLC | VERIFIED | 13 | 0 | 0 | 0 | 4 |
| SITE-001937 | Trans-Foam Inc. | STILL_UNCERTAIN | 0 | 0 | 0 | 0 | 3 |
| SITE-002055 | P & E Sales Ltd. | VERIFIED | 1 | 0 | 0 | 0 | 2 |
| SITE-003469 | Lubrizol — Avon Lake | STILL_UNCERTAIN | 0 | 0 | 0 | 0 | 2 |

## Files

- `packet.csv`: 178 rows (162 in-vocab, 16 off-vocab), columns as in the pilot.
- `verdicts.csv`: 30 rows with the deciding/settling fact, fetches used, availability failures.
- Site-level verdict is in `verdicts.csv`; row-level `verdict` in `packet.csv` is VERIFIED for an in-vocab value, STILL_UNCERTAIN for an off-vocab note (or an unconfirmed-currency cert).

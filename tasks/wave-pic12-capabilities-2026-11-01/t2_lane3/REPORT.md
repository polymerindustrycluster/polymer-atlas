# Lane t2-3 packet: PIC-12 capability wave, tranche 2 (2026-11-01)

**This is a packet, not a data change.** Lane t2-3 never edits `data/`, allocates IDs, commits or pushes. Every row in `packet.csv` is class `own_site`, carries the exact URL and a quote of 25 words or fewer, and each quote was checked programmatically as a substring of the page text I fetched (whitespace-normalised). All fetches were curl through the configured proxy; WebFetch was not used. No `tier_effect` is proposed. Org-scope rows use the ORG id as `record_id`. Fetched page text is in `/tmp/claude-0/wave/t2_lane3/pages/` (outside the repo). Vocabulary: `docs/schema/vocab.json` (v1.7.6), including `automotive_unspecified`, `tire_rubber_goods`, `medical_healthcare_general`, `food_processing_foodservice`, `thermoforming_unspecified`, `iso_45001`. HEAD at lane start was c0192b8, not the wave pin 665e5c5; the assignment file was used as given. Assignment: `t2_lane3_assignment.csv`, 55 site rows.

## Results (units stated)

**Sites verdicted (unit: assigned Ohio site rows, n=55):** VERIFIED 28, STILL_UNCERTAIN 27, REJECT 0 (VERIFIED rate 28/55 = 51%; tranche 1 lane 4 was 50%). VERIFIED = at least one in-vocab value at **site** scope. Every STILL_UNCERTAIN names its settling fact in `verdicts.csv`. No REJECT: nothing found was a dated closure or non-establishment fact. Unreachable sites are availability failures only, and no Form 5500 check was run.

**In-vocab values proposed (unit: packet rows, one per record, field, value):** 286 total, 196 site scope and 90 org scope.

| field | site scope | org scope | total |
|---|---|---|---|
| processes | 52 | 14 | 66 |
| materials | 57 | 25 | 82 |
| markets_served | 73 | 44 | 117 |
| certifications | 14 | 7 | 21 |
| **all** | **196** | **90** | **286** |

Plus **16 off-vocab rows** (`*_other_note`, marked OFF-VOCAB, row verdict STILL_UNCERTAIN): processes_other_note 7, materials_other_note 4, certifications_other_note 3, markets_other_note 2. Nine in-vocab rows are also row-level STILL_UNCERTAIN: ORG-000198 tire_retreading (no page places retreading); ORG-000315 iso_9001 and iso_45001 (Dura-Line, edition not named); ORG-000379 iatf_16949, iso_9001, iso_14001 (Goodyear Air Springs, certificate PDFs not read, plant list unknown); SITE-000437 iso_9001 (Preform, edition not named, certificate PDF is an image); SITE-000565 iso_9001 (Prospect, edition not named); SITE-001876 energy_renewables_battery (G2, solar is a historical statement). The other 277 in-vocab rows are VERIFIED at row level.

**Certifications recorded (unit: packet rows):** site scope iso_9001 x10 (8 VERIFIED: Struktol Stow, MDE Norton, United Initiators Elyria, Jaco Middlefield, Nippon Paint Cleveland, Thogus Avon Lake, Tri-Craft Middleburg Heights, Avient Berea; 2 row-level STILL_UNCERTAIN: Prospect and Preform), iso_14001 x1 (Nippon Cleveland), as9100 x1 (Prospect, AS9100D), itar x1 (Prospect), fda_registered x1 (Thogus). Org scope: as9100 and iso_9001 (Mechanical Rubber, with the Ohio facility explicitly excluded), iso_9001/iso_45001 (Dura-Line), iatf_16949/iso_9001/iso_14001 (Goodyear Air Springs). Dated certificates read for currency: United Initiators (ISO 9001:2015, valid to 2027-01-04), Jaco (ISO 9001:2015, 2025-01-29 to 2028-01-28), Nippon Cleveland (ISO 9001:2015, expires 2029-04-29), Tri-Craft (ISO 9001:2015, valid to 2029-02-04). Not recorded under R3c: General Color ("ISO certified since 2003", no standard named), Polymer 5 (quality guidelines "mirror" ISO 9001-2008, a superseded edition and not a certificate), Preform (image-only certificate).

**Measured yield**
- Site-scope capability values (processes, materials, markets) per assigned site: 182/55 = 3.3; per site that has any (26 sites): 182/26 = 7.0. All in-vocab values, all scopes, per assigned site: 286/55 = 5.2.
- Sites with at least one `markets_served` value: **19/55 (35%) at site scope; 34/55 (62%) counting org scope**.
- Sites with at least one site-scope `processes` value: 21/55 (38%); any scope 29/55. Materials: site 16, any scope 28. Certifications: site 10, any scope 13.
- Sites with at least one in-vocab value at some scope: 43/55 (78%). The twelve with none: APV, Custom Plastic Extrusions (no website), Saint-Gobain, A.r.e. Accessories, Sealed Air/APS Bedford Heights, MIPCO (all availability), Amcor Aurora, Chemical Solvents, J B Jewitt, 3D Dental, BASF Elyria, Wooster Brush (content found but nothing in vocab or nothing tied to the plant).
- Two VERIFIED sites rest on a site-scope certificate alone (Struktol Stow, Avient Berea); 26 sites have a site-scope capability value.
- Reconfirmed existing site values: SITE-000024 elastomers_rubber, SITE-000105 injection_molding, SITE-001487 injection_molding.

**Plant-specificity (hard rule).** Site scope was used only where a page names the plant, a certificate or annex names the address, or the company's own site prints one location that matches the row (each row's notes say which). Org scope only, nothing pushed down: Dura-Line Elyria, Oatey Cleveland, SpringSeal, Ziegler Tire, Infinity/Goodyear Air Springs, Philpott Rubber Extrusions, Refcotec, Schneller, Speed North America, Technoform, Drossbach, Cru/CPC, Advanced Cryogenic, Sterilite, CSP Conneaut, plus the ORG-level materials/markets for Avient Berea, Mechanical Rubber, Styropek and RTS. Split rows: RTS Austinburg gets rotational_molding at site scope (page names Austinburg) but assembly, spin welding and markets stay org. Mechanical Rubber: the Strongsville row gets site scope from the page titled "Mechanical Rubber Ohio" (Durox Extrusions); the AS9100D/ISO 9001:2015 org rows carry a note that the Ohio facility is excluded from that certificate.

## Fetches (unit: fetch attempts)

- **162 total** across 54 sites (SITE-000066 had no website, so 0), 2.9 per assigned site, maximum 6 (Struktol, including one wasted refetch from a scratch-file collision of my own, noted in `verdicts.csv`). The 6-fetch cap was respected.
- Hard availability failures (403 bot wall or Forbidden, 406, empty HTTP 202 shell, TLS certificate name mismatch): **12/162 = 7.4%**: APV 403 x2 (apex and www); Saint-Gobain 403 "Verifying your browser" x2; A.r.e./realtruck.com 202 empty body x2; Sealed Air 403 "Just a moment" x2 (autobag.com goes to the same wall); MIPCO 406 x2; May-Lin TLS name mismatch x2 (the page was then read over plain http, certificate verification never bypassed).
- Content-free 200s: 1 (Preform certificate PDF, image only); 3D Dental's two 200s are a redirect to a different brand's site (camcube.com/fr). With these: 13/162 = 8.0%.
- My own misses (not availability): 7 guessed 404s (Musson, Styropek, Goodyear, Avient, Thogus, ChromaScape, BASF) and 2 guessed Saint-Gobain subdomains that did not resolve (proxy 502): 9/162.
- Sites with no usable company content from any route: **7/55 (13%)**: APV, Saint-Gobain, A.r.e., Sealed Air/APS, MIPCO (availability), 3D Dental (redirect to another brand), Custom Plastic Extrusions (no website on record). All are STILL_UNCERTAIN; none is evidence of closure or absence.
- Routes that recovered content: plain http for May-Lin; PDF certificates read with pdftotext (United Initiators, Jaco, Nippon, Tri-Craft, General Color plant overview).
- **Not done:** no bot-wall workaround (no user-agent changes, no captcha handling, no retry loops). Saint-Gobain, Sealed Air, APV, MIPCO and RealTruck need a human browser or another route.

## Vocabulary gaps met (owner rulings; flagged in `*_other_note`, not settled)

- **Processes:** monofilament/fiber extrusion (Speed); organic peroxide / initiator production (United Initiators); polymer-concrete casting (Castinite); paintbrush and roller-cover manufacture (Wooster Brush); rubber molding with type unstated and rubber/silicone-to-metal bonding (May-Lin; no generic rubber-molding term); metal stamping (Tri-Craft, not a polymer process).
- **Materials:** PBT (MDE, PharoPLAST, Jaco); PPA (MDE); PPO/PPE (PharoPLAST); PEI/Ultem, polysulfone and G10/FR4 laminate (Jaco); no generic composite term for "composite machining" (Prospect); no TPO in MATERIALS although TPO is in CAP_MATERIAL (Artemis mapped to thermoplastic_elastomers_tpe_tpu); EPS has no term (Styropek mapped to polystyrene_ps_hips).
- **Markets:** pet supplies and pool/spa (Chapin); wood mulch, printing inks, paper, corrugated, asphalt sealer, aggregate, recycled rubber (ChromaScape colorant customers); athletic fields (Pioneer mapped to lawn_garden_recreation).
- **Certifications:** TL 9000 (Dura-Line); Responsible Care RC14001 (United Initiators, Avient library); ISO 9001 without edition (Dura-Line, Preform, Prospect) was proposed only as row-level STILL_UNCERTAIN where the standard was named but the edition was not.
- **v1.7.6 terms used:** automotive_unspecified (14 records: 8 site rows, 6 org rows), medical_healthcare_general (General Color, Thogus, May-Lin), food_processing_foodservice (Philpott org, May-Lin), thermoforming_unspecified (SpringSeal org), iso_45001 (Dura-Line org). tire_rubber_goods was proposed for Struktol (org). No `asa` or `specialty_elastomers` case arose.
- **Mapping calls the integrator may want to override:** vinyl to pvc and stair coverings to construction_building_products (Musson); ultrasonic welding to ultrasonic_solvent_bonding (Thogus); corrugated tubing and "conduit production" to extrusion_pipe_tube (Drossbach, Dura-Line; extrusion is not named on those pages); butyl tapes to adhesives_sealants (Preform); composite machining to plastics_machining_cnc (Prospect); "specialty converting" to die_cutting_converting (G2); Plumbing to construction_building_products (Thogus); Semiconductor to electronics_electrical and polymer-concrete epoxy to epoxy (Castinite); Industrial Equipment/Heavy Equipment to industrial_machinery (Jaco, Tri-Craft, Preform); Mining to chemical_mining_metals_processing and Highway to infrastructure_civil (Tri-Craft, MacDivitt); Water treatment to water_wastewater (PharoPLAST); "polymer market" to plastics_rubber_processors (United Initiators); Nippon coating_formulation rests on a 1995 history line plus a 2026 certificate scope (manufacture and sale of automotive coatings).

## Hygiene findings (for the integrator; none resolved)

1. **SITE-000066 / ORG-000066 Custom Plastic Extrusions:** org `website` is `none_found`, yet the candidate filter required a parent org with a website. Nothing was fetched; no discovery search was run (own-site-only method).
2. **SITE-000188 / ORG-000181 SpringSeal:** the only address on its own site is 800 Enterprise Parkway, Ravenna, OH 44266, labelled Corporate Office. The Atlas row is Streetsboro with no street. Either the city is wrong or Streetsboro is a second facility; values were kept at org scope.
3. **SITE-000205 / ORG-000198 Ziegler Tire:** row is a ring-1 `hq_only`; own site is a retail/commercial tire dealer whose commercial location is 6741 Whipple Ave NW, North Canton. The retread page names no plant.
4. **SITE-000220 A.r.e. Accessories:** the org website is realtruck.com (the parent brand); it returns an empty HTTP 202 shell to curl. Possible rebrand to a new owner; not shown.
5. **SITE-000252 Automated Packaging Systems-Sealed Air-Bedford:** org website sealedair.com sits behind a bot challenge; autobag.com routes to the same wall. Site name embeds the Sealed Air acquisition.
6. **SITE-000273 BVPV Styrenics:** own site is Styropek (styropek.com). It lists 786 Hardy Road, Painesville as the single North America manufacturing site (plus an Altamira, Mexico site). Trade-name relationship to BVPV is the integrator's call.
7. **SITE-000319 "Degussa Initiators" / ORG-000618:** the Elyria plant at 555 Garden Street operates as United Initiators, Inc. (present since 1965; the ISO 9001:2015 certificate names United Initiators, Inc.). The row name is a legacy trade name. Ring-2 manufacturing_plant is supported by the certificate scope (production of organic peroxides).
8. **SITE-000335 / SITE-000336 Dura-Line:** the contact page lists both Elyria plants (860 Garden St, 669 Sugar Ln). My org-scope rows on ORG-000315 overlap the lane 4 (tranche 1) rows on the same org; dedupe at integration. The "all US facilities are ISO-certified under 9001 and 45001 and TL 9000" line has no edition.
9. **SITE-000405 / ORG-000379 Infinity Engineered Products:** the row is a ring-1 `manufacturing_plant`, but the own site says 3524 Southwestern Blvd, Fairlawn is the HQ and R&D facility (opened 2016) and names an assembly plant in Mexico. No fetched page ties manufacture to Fairlawn; certificate PDFs (IATF 16949:2016, ISO 9001:2015, ISO 14001:2015) were not read.
10. **SITE-000475 MIPCO:** `mipco.org` and `www.mipco.org` return HTTP 406 even on the error document. Availability only.
11. **SITE-000524 / ORG-000490 Philpott Rubber Extrusions:** own contact page prints HQ at 1010 Industrial Pkwy, N. Brunswick and a Manufacturing Center at 375 Gentry Dr, Aurora; **Mogadore (330 Gilchrist Rd) appears nowhere**. The site also announces the ESP&G / Extruded Silicone Products acquisition (press-release link on the home page). Address and parent handling are for the integrator.
12. **SITE-000639 / ORG-000600 Technoform:** the row address is 1755 Enterprise Parkway Suite 300, Twinsburg, listed on the own contact page as Technoform North America, Inc. beside Oregon and Tennessee offices. A suite address on a ring-1 plant row looks like an office; no plant activity was stated.
13. **SITE-000118 / ORG-000119 Mechanical Rubber:** HQ is Warwick, NY; the Ohio page is "Durox Extrusions" and says it is not covered by the group's AS9100D/ISO 9001:2015 certificate. The Strongsville row is `hq_only` with no street, but the page describes a production facility (extrusion lines, autoclaves).
14. **SITE-000620 Speed North America:** the own site's `/en/` page is an unedited WordPress stub ("Bonjour tout le monde"); only the French pages describe the group. The contact page does list SPEED NORTH AMERICA at 1700A Old Mansfield Road, Wooster.
15. **SITE-001393 Avient / ORG-000001:** the Global ISO Certificate Library lists **Massillon, OH** (and Avon Lake, Berea, North Baltimore and Norwalk OH under other certificates) among Avient sites; compare with Atlas coverage of Avient Ohio establishments.
16. **SITE-001435 Amcor Aurora (PVC Stretch Film):** amcor.com is global and the contact page lists only the Zurich head office; nothing confirms an Aurora plant or a PVC stretch film line.
17. **SITE-001651 Chemical Solvents:** own pages show commodity solvent supply, custom blending of flammable products (100 to 1,000,000 cps), toll manufacture of solvent/aqueous blends, solvent recycling and waste services. No polymer, coating, adhesive or ink product is named. Ring-2 `manufacturing_plant` scope is an owner question.
18. **SITE-001670 J B Jewitt Co (Homestead Finishing Products):** own pages describe a catalog/retail business for wood-finishing supplies; the About page says TransTint dyes are now manufactured by General Finishes. Scope/ring is an owner question.
19. **SITE-001742 Drossbach, Stow:** own contact page labels 1500 Commerce Drive "National Sales and Distribution"; the "Corporate/Manufacturing Office" is Trenton, Ontario. Ring-1 manufacturing_plant is doubtful.
20. **SITE-001777 Cru Performance Coatings / ORG-001701:** own site is Continental Products Company (CPC), HQ 1150 East 222 St, Euclid, OH 44117; the row is 2926 Chester Ave, Cleveland. No page ties anything to Chester Ave.
21. **SITE-001806 3D Dental Designs:** the `zip` column holds `16781`, which is the street number in the row's note (16781 Chagrin Blvd, Suite 434, Shaker Heights, OH 44120); the real ZIP is 44120. Also `www.3ddental.com` redirects to `camcube.com/fr` (a French-language dental technology site that never mentions 3D Dental, Ohio or Shaker Heights).
22. **SITE-001917 Artemis Polymer Processing:** the own site nav carries an "IN MEMORIAM" page (not fetched); continuity is not shown either way.
23. **SITE-001986 Castinite:** `castinite.com` serves the Precision Polymer Casting (PPC Products) brand, copyright 2023, and redirects the home page to precisionpolymercasting.com.
24. **SITE-002035 May-Lin:** the org website field is `https://www.may-lin.com`, which fails certificate verification (name mismatch on www and apex); the site works only over plain http.
25. **SITE-003479 CSP Conneaut:** own site states 15 North American locations and names none in Ohio except Van Wert (news article). The existing site row values `composite_compounding; compression_molding` and `SMC; glass-fiber composites` are not in vocab (compression_molding and the others are not PROCESSES/MATERIALS terms).
26. **Existing site values not supported by the own site:** SITE-000083 MDE (`plastics_machining_cnc`, `polyethylene_pe` not found); SITE-000188 SpringSeal (`rubber_extrusion`, `elastomers_rubber`: the own site describes PVC/TPV/TPE/PP/HDPE/ABS extrusion, no rubber); SITE-000007 Struktol (`custom_compounding`: own site describes an additives maker). Not resolved; for the integrator.
27. **SITE-000437 Kes Industries:** own site is "Preform Sealants, a Division of KES Industries", copyright 2013; ISO 9001 certificate PDF is an image.
28. **SITE-000565 Prospect:** the own site calls it "a global leader in production composite and metallic machining" and a tooling shop; it is not a polymer processor in the narrow sense (AS9100D/ITAR aerospace machining). Ring/scope is an owner question; the CNC value was mapped to plastics_machining_cnc as the nearest term.
29. **APV (SITE-000044), Saint-Gobain (SITE-000170), A.r.e. (SITE-000220), Sealed Air/APS (SITE-000252), MIPCO (SITE-000475) and 3D Dental (SITE-001806):** these unreadable or redirected sites need another route and a Form 5500 / dated-outcome check before any status question arises; none is a REJECT.

## Per-site summary

Columns: site-scope capability values (processes, materials, markets), site-scope certifications, org-scope in-vocab values, off-vocab note rows (site or org), fetch attempts.

| site_id | site | verdict | site-scope capability values | site-scope certs | org-scope values | off-vocab notes | fetches |
|---|---|---|---|---|---|---|---|
| SITE-000007 | Struktol — Stow HQ | VERIFIED | 0 | 1 | 2 | 0 | 6 |
| SITE-000024 | Musson Rubber Co. — Akron | VERIFIED | 3 | 0 | 0 | 0 | 3 |
| SITE-000044 | APV Engineered Coatings — Akron | STILL_UNCERTAIN | 0 | 0 | 0 | 0 | 2 |
| SITE-000066 | Custom Plastic Extrusions, Ltd. — Hudson | STILL_UNCERTAIN | 0 | 0 | 0 | 0 | 0 |
| SITE-000083 | Michael Day Enterprises, LLC — Norton | VERIFIED | 13 | 1 | 0 | 1 | 3 |
| SITE-000105 | PharoPLAST — Cleveland | VERIFIED | 20 | 0 | 0 | 1 | 5 |
| SITE-000118 | Mechanical Rubber — Strongsville | VERIFIED | 3 | 0 | 6 | 0 | 3 |
| SITE-000133 | Oatey — Cleveland | STILL_UNCERTAIN | 0 | 0 | 2 | 0 | 2 |
| SITE-000170 | Saint-Gobain Performance Plastics — Solon | STILL_UNCERTAIN | 0 | 0 | 0 | 0 | 4 |
| SITE-000188 | SpringSeal — Streetsboro | STILL_UNCERTAIN | 0 | 0 | 18 | 0 | 4 |
| SITE-000205 | Ziegler Tire — Massillon | STILL_UNCERTAIN | 0 | 0 | 1 | 0 | 3 |
| SITE-000220 | A.r.e. Accessories — Massillon | STILL_UNCERTAIN | 0 | 0 | 0 | 0 | 2 |
| SITE-000239 | Allpass Corporation — Madison | VERIFIED | 4 | 0 | 0 | 0 | 3 |
| SITE-000252 | Automated Packaging Systems-Sealed Air-Bedford — Bedford Heights | STILL_UNCERTAIN | 0 | 0 | 0 | 0 | 2 |
| SITE-000273 | BVPV Styrenics — Painesville | VERIFIED | 1 | 0 | 1 | 0 | 4 |
| SITE-000286 | Chapin Custom Molding — Elyria | VERIFIED | 7 | 0 | 0 | 1 | 4 |
| SITE-000319 | Degussa Initiators — Elyria | VERIFIED | 1 | 1 | 0 | 1 | 3 |
| SITE-000335 | Dura-Line — Elyria | STILL_UNCERTAIN | 0 | 0 | 5 | 1 | 3 |
| SITE-000357 | Extrudex — Painesville | VERIFIED | 8 | 0 | 0 | 0 | 4 |
| SITE-000376 | General Color & Chemical — Minerva | VERIFIED | 13 | 0 | 0 | 1 | 4 |
| SITE-000405 | Infinity Engineered Products — Fairlawn | STILL_UNCERTAIN | 0 | 0 | 6 | 0 | 3 |
| SITE-000421 | Jaco Products Co. — Middlefield | VERIFIED | 19 | 1 | 0 | 1 | 3 |
| SITE-000437 | Kes Industries — Twinsburg | VERIFIED | 7 | 1 | 0 | 0 | 4 |
| SITE-000456 | Mac Divitt Rubber Co., LLC — North Perry | VERIFIED | 16 | 0 | 0 | 0 | 4 |
| SITE-000475 | Midwest Industrial Products Corporation — Cleveland | STILL_UNCERTAIN | 0 | 0 | 0 | 0 | 2 |
| SITE-000496 | Nippon Paint Automotive Americas — Cleveland | VERIFIED | 3 | 2 | 0 | 0 | 5 |
| SITE-000524 | Philpott Rubber Extrusions — Mogadore | STILL_UNCERTAIN | 0 | 0 | 9 | 0 | 4 |
| SITE-000542 | Polymer 5 — Garrettsville | VERIFIED | 4 | 0 | 0 | 1 | 3 |
| SITE-000565 | Prospect Mold, Inc. — Cuyahoga Falls | VERIFIED | 6 | 3 | 0 | 1 | 2 |
| SITE-000579 | Refcotec — Orrville | STILL_UNCERTAIN | 0 | 0 | 3 | 0 | 3 |
| SITE-000601 | Schneller LLC — Kent | STILL_UNCERTAIN | 0 | 0 | 3 | 0 | 3 |
| SITE-000620 | Speed North America — Wooster | STILL_UNCERTAIN | 0 | 0 | 2 | 1 | 3 |
| SITE-000639 | Technoform — Twinsburg | STILL_UNCERTAIN | 0 | 0 | 6 | 0 | 2 |
| SITE-000655 | Tri-Craft, Inc. — Middleburg Heights | VERIFIED | 9 | 1 | 0 | 1 | 3 |
| SITE-001393 | Avient Corporation — Berea (ColorMatrix) | VERIFIED | 0 | 1 | 2 | 0 | 3 |
| SITE-001423 | Sterilite Corporation — Massillon | STILL_UNCERTAIN | 0 | 0 | 1 | 0 | 3 |
| SITE-001435 | Amcor — Aurora (PVC Stretch Film) | STILL_UNCERTAIN | 0 | 0 | 0 | 0 | 2 |
| SITE-001487 | Thogus Products — Avon Lake | VERIFIED | 13 | 2 | 0 | 0 | 3 |
| SITE-001540 | ChromaScape — Stow (Manufacturing Facility) | VERIFIED | 1 | 0 | 0 | 1 | 3 |
| SITE-001651 | Chemical Solvents Inc — Cleveland | STILL_UNCERTAIN | 0 | 0 | 0 | 1 | 2 |
| SITE-001670 | J B Jewitt Co Inc — Cleveland | STILL_UNCERTAIN | 0 | 0 | 0 | 0 | 2 |
| SITE-001695 | ADVANCED CRYOGENIC ENTERPRISES — Akron | STILL_UNCERTAIN | 0 | 0 | 2 | 0 | 1 |
| SITE-001719 | RTS COMPANIES INC. — Austinburg | VERIFIED | 1 | 0 | 4 | 0 | 3 |
| SITE-001742 | Drossbach Inc — Stow | STILL_UNCERTAIN | 0 | 0 | 10 | 0 | 2 |
| SITE-001777 | Cru Performance Coatings LLC | STILL_UNCERTAIN | 0 | 0 | 4 | 0 | 2 |
| SITE-001806 | 3D Dental Designs and Development LLC | STILL_UNCERTAIN | 0 | 0 | 0 | 0 | 2 |
| SITE-001843 | The Pioneer Manufacturing Company | VERIFIED | 3 | 0 | 0 | 0 | 2 |
| SITE-001876 | G2 Materials Corp | VERIFIED | 6 | 0 | 0 | 0 | 2 |
| SITE-001917 | Artemis Polymer Processing, Inc. | VERIFIED | 7 | 0 | 0 | 0 | 4 |
| SITE-001986 | Precision Polymer Casting LLC (dba Castinite) | VERIFIED | 3 | 0 | 0 | 1 | 2 |
| SITE-002035 | May Lin Silicone Products Inc. | VERIFIED | 10 | 0 | 0 | 1 | 4 |
| SITE-002079 | BASF Elyria site | STILL_UNCERTAIN | 0 | 0 | 0 | 0 | 3 |
| SITE-002131 | Quality Plastics LLC | VERIFIED | 1 | 0 | 0 | 0 | 2 |
| SITE-003479 | CSP — Conneaut Plant | STILL_UNCERTAIN | 0 | 0 | 3 | 0 | 4 |
| SITE-000676 | THE WOOSTER BRUSH COMPANY — Wooster | STILL_UNCERTAIN | 0 | 0 | 0 | 1 | 3 |

## Files

- `packet.csv`: 302 rows (286 in-vocab, 16 off-vocab), columns as in the pilot; every `source_class` is `own_site`.
- `verdicts.csv`: 55 rows with the deciding/settling fact, fetches used, availability failures.
- Site-level verdict is in `verdicts.csv`; row-level `verdict` in `packet.csv` is VERIFIED for a stated in-vocab value, STILL_UNCERTAIN for an off-vocab note or a value whose currency, edition or plant tie is not shown.

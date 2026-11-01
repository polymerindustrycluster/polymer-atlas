# Lane t2-1 packet: PIC-12 capability wave, tranche 2 (2026-11-01)

**This is a packet, not a data change.** Lane t2-1 never edits `data/`, allocates IDs, commits or pushes. Every row in `packet.csv` is class `own_site`, carries the exact URL and a quote of 25 words or fewer, and the quote was checked programmatically as a whitespace-normalised substring of the page text I fetched (PDF certificates were converted with pdftotext). All fetches were curl through the configured proxy; WebFetch was used only as a second route on 7 sites that curl could not read, and nothing was quoted from it. No `tier_effect` is proposed. Org-scope rows use the ORG id as `record_id`. Fetched text and helper scripts are in `/tmp/claude-0/wave/t2_lane1/`.

Vocabulary: `docs/schema/vocab.json` v1.7.6, with the R2 rulings applied (`automotive_unspecified`, `medical_healthcare_general`, `food_processing_foodservice`, `thermoforming_unspecified`, `asa`, `specialty_elastomers`). Certificates follow R3c (current certificate or current page naming a non-superseded edition only).

## Results (units stated)

**Sites verdicted (unit: assigned Ohio site rows, n=55):** VERIFIED 30, STILL_UNCERTAIN 25, REJECT 0.
Rule: VERIFIED = at least one in-vocab processes, materials, markets_served or certifications value at **site** scope. No REJECT: nothing found was a dated closure or non-establishment fact; no Form 5500 check was run because no REJECT is proposed.

**In-vocab values proposed (unit: packet rows, one per record, field, value):** 315 total.

| field | site scope | org scope | total |
|---|---|---|---|
| processes | 74 | 12 | 86 |
| materials | 112 | 24 | 136 |
| markets_served | 60 | 27 | 87 |
| certifications | 5 | 1 | 6 |
| **all** | **251** | **64** | **315** |

Plus **21 off-vocab rows** (`*_other_note`, marked OFF-VOCAB, row verdict STILL_UNCERTAIN): processes_other_note 10, materials_other_note 5, markets_other_note 3, certifications_other_note 3. The 3 certification notes are expired or unconfirmed certificates that were deliberately not recorded (Rauh, Wooster Elastomers, PET Processors; see hygiene). Packet total 336 rows; 315 in-vocab rows are VERIFIED at row level.

**Measured yield**
- Site-scope capability values (processes, materials, markets) per assigned site: 246/55 = 4.5. Per VERIFIED site: 246/30 = 8.2. All in-vocab values, all scopes, per assigned site: 315/55 = 5.7.
- Sites with at least one `markets_served` value: **17/55 (31%) at site scope; 25/55 (45%) counting org scope**.
- Sites with at least one site-scope `processes` value: 22/55 (40%); site-scope `materials`: 25/55 (45%); site-scope certification: 3/55 (CCL Strongsville 3 certificates, Royal Plastics, Akron Coating GMP statement).
- Sites with at least one in-vocab value at some scope: 39/55 (71%). Org-scope only (nine sites, all STILL_UNCERTAIN at site level): SITE-000167, 000250, 000397, 000538, 000559, 001318, 001732, 001839, 003472. The 16 with no in-vocab value: 15 with no usable content or no plant-tied content (below) plus SITE-002110 Alpha/Checkpoint Canton (off-vocab notes only).
- VERIFIED rate 30/55 = 55% (tranche 1 lane 4 was 50%, pilot 48%).

**Plant-specificity (hard rule).** Site scope was used where the company has one printed address and the page says so (each row's notes say why), or where a plant-named page ties the value to the plant: CCL Strongsville (location page plus three NSF-ISR certificates naming 17700 Foltz Parkway), Goodyear Akron (corporate locations page), Newko Strongsville (About page ties HQ to manufacturing). Org scope only, nothing pushed down: Tremco CPG/RPM, Associated Materials, Huntsman, Greenbridge, Pretium, Avery Dennison, ClearSonic, Spazzolplastica plastic spools, Mar-Bal. Royal Plastics is split: processes/materials/markets at org scope because its Quality page says the system covers "operations both in US and China manufacturing", ISO 9001:2015 at site scope because Mentor is the only US address.

## Fetches (unit: fetch attempts, including WebFetch)

- **186 total** across 55 sites (179 curl, 7 WebFetch), 3.4 per site, maximum 6 (CCL, ASK Chemicals, Amros); the 6-fetch cap was respected. WebFetch attempts are counted against the site; SITE-000214 and SITE-001688 share parker.com, which I tried once by WebFetch (counted on 000214).
- Hard availability failures, curl only (403, TLS error, proxy 502, connection reset, 503, DNS failure): **24/179 = 13.4%**. Adding the 7 WebFetch attempts (6 failed; 1 returned a summary for Boardman that is not quotable and was not used) and 3 content-free 200s (Dal-Little image-only site, Huntsman JavaScript locations template, Sun State Wix capabilities shell): **34/186 = 18.3%**.
- My own misses (not availability): 5 guessed 404s (Four Seasons /services, Greenbridge /about/, Bauer /about-us/, ASK /company/locations, Thermo Packaging /thermoforming/).
- Sites with no usable company content from any route: **9/55 (16%)**, all STILL_UNCERTAIN, none evidence of closure: SITE-000103 HEXPOL (proxy 502 / handshake failure / DNS), SITE-000130 Tarkett (403 bot wall), SITE-000214 and SITE-001688 Parker (403 bot wall, same org website), SITE-000266 Boardman Molded (403), SITE-001483 MODRoto (resets, 503), SITE-002025 Vinyltech (proxy 502 / DNS; WebFetch ENOTFOUND), SITE-002059 Canfield (expired TLS certificate, resets, 503), SITE-001868 Dal-Little (all four pages are GIF images with no text). HEXPOL and Vinyltech failed to resolve from both curl and WebFetch; this may be the session network allowlist rather than a dead domain.
- Routes that recovered content: Ace Plastics and Amros via plain `http://` after TLS failure (self-signed certificate; never bypassed); AMD Plastics redirected to forming-tech.com.
- **Not done:** no bot-wall workaround (no user-agent changes, no captcha handling, no TLS bypass).

## Certificates (R3c)

Recorded: CCL Strongsville ISO 9001:2015 (expires 2027-04-07), ISO 14001:2015 (2027-05-29), IATF 16949:2016 (2027-04-07), all NSF-ISR certificates for 17700 Foltz Parkway; Royal Plastics ISO 9001:2015 (page copyright 2026, no certificate shown); Mar-Bal ISO 9001:2015 at org scope (edition named, no certificate shown); Akron Coating glp_gmp (self-stated FDA GMP compliance, no certificate).
**Not recorded:** Rauh Polymers ISO 9001:2015 (own linked certificate expired 2023-11-20); Wooster Elastomers ISO 9001:2015 (own linked certificate expired 2026-10-20, 12 days before this pass; home page still says certified); PET Processors ISO 9001:2015 (undated statement, stale 2009-2022 footer); Tremco CPG ISO9001/ISO14001 badges (no edition or currency); KAPCO "ISO Certification" (a PNG I cannot read, quality policy names no standard).

## Vocabulary gaps met (owner rulings; flagged in `*_other_note`, not settled)

- **Processes:** no rubber-to-metal / rubber-to-substrate bonding (Jet Rubber, TMI); no generic or type-unstated thermoplastic extrusion (Four Seasons); no label converting / pressure-sensitive label manufacture (CCL); no polyurethane machinery / equipment manufacture (Linden); no wire-basket spool (steel) manufacture (Spazzolplastica Mentor); no ATA flight-case construction (Aerocase); no PU foam filling of profiles (Creative Millwork); no type-unstated rubber molding term (Thermoprene "Rubber Molding", analogous to thermoforming_unspecified); PTFE coating (TMI); resin manufacture with process unnamed (Newko).
- **Materials:** no TPO in MATERIALS (CAP_MATERIAL has thermoplastic_olefin_tpo; Newko); no SAN (J&O); no PBT/PEN/PTT/PPS/LCP/EVA (PET Processors); no copolyester (Rauh Optimum); no CPVC or microcellular foam (Royal); polyester resin type unstated (Newko, Royal).
- **Markets:** no entertainment / music / trade-show / sound-reinforcement term (Aerocase); no fleet or school-bus vehicle-marking term (Sun Art Decals); no retail loss-prevention term (Alpha/Checkpoint); no racing term (Goodyear Akron Racing Tires).
- **Certifications:** none missing.
- **Mapping calls the integrator may want to override:** vinyl to pvc (Creative Millwork, Duo-Corp, Sun Art, Associated Materials); ultrasonic welding to ultrasonic_solvent_bonding (J&O); crystal styrene to polystyrene_ps_hips (J&O); solid-state polymerization to polymerization (PET Processors); "Food" to food_processing_foodservice (TMI); "converting" to die_cutting_converting (KAPCO); "functional laminates" to laminating (CCL); hot/cold feed extruders to rubber_extrusion (Akron Gasket); transit bus matting to rail_transportation (Ace Rubber); Aerospace and Military both to aerospace_defense; "Medical" and "Healthcare" to medical_healthcare_general (never medical_device); automotive always automotive_unspecified; "Polyisoprene" to specialty_elastomers (Thermoprene).

## Hygiene findings (for the integrator; none resolved)

1. **SITE-000115 / ORG-000116 AMD Plastics (Euclid):** `amdplastics.com` redirects to forming-tech.com (Forming Technologies: Muskegon MI and Arteaga MX facilities, thermoforming and extrusion). Its About page names no Euclid facility; a stale link still points to amdplastics.com/oem-solutions. Possible acquisition or rebrand; undated, not a REJECT, no outcome record, no Form 5500 check run.
2. **SITE-000080 / ORG-000080 Ace Plastics (Barberton):** own site says it "distributes custom designed promotional products" (license plate frames, key fobs); page copyright 2012; ring-1 `manufacturing_plant` is a scope doubt. `https://aceframes.com` fails TLS (self-signed).
3. **SITE-001318 / ORG-000238 Avery Dennison (Mentor HQ):** the org `website` field is the Performance Tapes division site (tapes.averydennison.com); its North America contact address is 250 Chester St, Painesville OH, not Mentor. Values are division-level at org scope.
4. **SITE-000167 / ORG-000006:** org is RPM International (website rpminc.com) but the row is Tremco CPG, whose own site names Beachwood only as corporate headquarters (3735 Green Road). Row is `hq_only`.
5. **SITE-000538 / ORG-000506 Greenbridge:** own contact page calls Cleveland (7000 Denison Ave, SITE-000540) the "Executive Offices & Manufacturing Facility" and Mentor (6277 Heisley Rd) "Customer Service, Accounting, Manufacturing"; Atlas types Mentor `hq_and_plant` ("HQ & manufacturing") and the org hq as Mentor. Also Clyde OH (202 Watertower Dr, Manufacturing) and Green OH (OMS & Distribution Center, 5555 Massillon Rd) appear on that page; confirm they are carried.
6. **SITE-003472 / ORG-000430 Mar-Bal Pultrusion (Willoughby, 38310 Apollo Pkwy):** mar-bal.com never mentions pultrusion, Willoughby or Apollo Pkwy. Its Facilities page lists Chagrin Falls (corporate/R&D), Painesville (Ohio plant, 787 Renaissance Pkwy), Cuba MO, Dublin VA, Taizhou China. The row's existing `processes` (`pultrusion`) and `materials` (`fiberglass-reinforced plastic (FRP); polyester; epoxy; vinyl ester`) are not in vocab. Confirm the Painesville plant is carried.
7. **SITE-001433 / ORG-000684 ASK Chemicals (Cleveland West):** the own US locations list names only the Dublin OH headquarters, Alfred NY (Hi-Tech Filters) and distributors; no Cleveland plant; the certificate page lists German plants only. Atlas carries 3 Ohio sites for this org.
8. **SITE-000672 / ORG-000631:** the company is now Wooster Elastomers LLC (the Atlas site name still says Wayne County Rubber); its ISO 9001:2015 certificate expired 2026-10-20 (see Certificates).
9. **SITE-000575 / ORG-000539 Rauh Polymers:** certificate expired 2023-11-20 yet the own site (copyright 2017) still claims ISO 9001:2015.
10. **SITE-000283 / ORG-000265 CCL Label (Strongsville):** the NSF-ISR certificate annex lists a second Strongsville address (1789 or 17890 Foltz Industrial Pkwy, extended site) and a CCL Design-TRP plant (illuminated trim) beside the main plant at 17700 Foltz Pkwy; the site row has no street address, so which address the row means is unclear.
11. **SITE-001839 / ORG-000098 Spazzolplastica NA (Mentor):** the Dec 2025 news page says Mentor (9361 Hamilton Dr) is the USA headquarters, wire basket spool (steel) plant and warehouse; Stow (1699 Commerce Dr) is a plastic spool/drum warehouse and "manufacturing partner for plastic products". The org `website` is the Italian parent (.it). Check that Stow is carried.
12. **SITE-000449 / ORG-000420 Linden Polyurethane:** builds polyurethane metering, mixing and dispensing equipment (machinery), not polymer parts; ring-1 `manufacturing_plant` scope is an owner question.
13. **SITE-000591 / ORG-000553 Royal Plastics:** Quality page says its system governs operations in the US and China manufacturing; a China manufacturing operation is not in the Atlas (not a site-shard candidate, flag only).
14. **SITE-000492 / ORG-000460 Newko Polymers:** footer lists a second Ohio address, 147 Kenwood St, Elyria OH 44035, besides the Strongsville HQ (12005 Alameda Dr). The site name "Newko 9" looks like a stray suffix.
15. **SITE-000266 Boardman Molded Products:** curl 403; WebFetch's summary (not used, not quotable) suggested a second location in Ciudad Juarez, Mexico and injection molding at 1110 Thalia Ave, Youngstown. Re-fetch by another route before any use.
16. **SITE-000214 and SITE-001688 (Parker, ORG-000004):** both rows share `parker.com`, behind a 403 bot wall. Needs a human browser or another route.
17. **SITE-000470 Mickey Thompson (Stow):** the consumer site names no address, plant or corporate activity; the row's manufacturing_plant type is unsupported by it.
18. **SITE-001716 Motivo Display Solutions (Massillon):** own site shows custom printed sales cases and rigid boxes ("100% recycled materials"), no polymer process and no address; a plant ring is a scope doubt.
19. **SITE-001647 Aabaco:** site calls itself "designers, fabricators, converters & distributors" of flexible packaging; manufacturing_plant ring is a scope doubt. **SITE-001935 Thermo Packaging:** products are paperboard blister cards and folding cartons (the Thermoforming page 404s); the contact page's email domain is povprint.com (a sister printer).
20. **SITE-001775 Aerocase:** cases are described as ABS, vacuum-formed, rotomolded and blow-molded; in-house forming is not stated, so no molding process was proposed.
21. **SITE-001868 Dal-Little:** image-only site (GIF banners, no text); no content was readable.
22. **Stale pages:** Amros (SITE-001665) pages copyright 2007; Sun State (SITE-000631) 2017; Rauh 2017; Ace Plastics 2012; PET Processors 2009-2022. Values were recorded where the page itself states them; none is evidence of closure.
23. **Off-vocab existing values:** SITE-001419 Bauer `materials` (`fiberglass_composites;aluminum`); ORG-001472 ChemMasters `processes`/`materials` free text; SITE-003472 Mar-Bal (above).
24. **SITE-000200 TMI:** the own contact page prints 6475 Victoria East Rd, Youngstown OH 44515 (44515 is an Austintown ZIP); the site row has no street address, so county should be confirmed from the physical address.
25. **SITE-000063 Akron Gasket:** `akrongasket.com` redirects to `akron-gasket.com`; the home page says "manufacturing and distribution", so the materials list (cork, felt, fiberglass, rubber) mixes stocked and made items; only polymers were proposed, each noted.

## Files

- `packet.csv`: 336 rows (315 in-vocab, 21 off-vocab), columns as in the pilot.
- `verdicts.csv`: 55 rows with the deciding/settling fact, fetches used, availability failures.
- Row-level `verdict` in `packet.csv` is VERIFIED for an in-vocab value, STILL_UNCERTAIN for an off-vocab note.

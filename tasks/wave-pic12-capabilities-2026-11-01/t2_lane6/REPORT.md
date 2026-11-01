# Lane t2-6 packet: PIC-12 capability wave, tranche 2 (2026-11-01)

**A packet, not a data change.** No edits to `data/` or any file outside `t2_lane6/`, no ID allocation, no commit or push. Every row in `packet.csv` is class `own_site`, carries the exact URL and a quote of 25 words or fewer, and every quote was checked programmatically as a whitespace-normalised substring of the page text I fetched (the build also checks each field value against `docs/schema/vocab.json` v1.7.6, requires an OFF-VOCAB mark on every `*_other_note` row, and found no duplicate record/field/value rows). Pages were fetched with curl through the configured proxy; page text and helper scripts are in `/tmp/claude-0/wave/t2_lane6/`. Org-scope rows use the ORG id as `record_id`. No `tier_effect` is proposed.

## Results (units stated)

**Sites verdicted (unit: assigned Ohio site rows, n=54):** VERIFIED 18, STILL_UNCERTAIN 36, REJECT 0. VERIFIED means at least one in-vocab processes, materials, markets_served or certification value at **site** scope. No REJECT: nothing found was a dated closure or non-establishment fact; the unreachable sites are availability failures only (no Form 5500 check was run).

**In-vocab values proposed (unit: packet rows, one per record, field, value):** 251.

| field | site scope | org scope | total |
|---|---|---|---|
| processes | 33 | 36 | 69 |
| materials | 26 | 45 | 71 |
| markets_served | 28 | 71 | 99 |
| certifications | 10 | 2 | 12 |
| **all** | **97** | **154** | **251** |

Plus **28 off-vocab rows** (`*_other_note`, OFF-VOCAB, row verdict STILL_UNCERTAIN): processes_other_note 20, materials_other_note 6, markets_other_note 2. 247 in-vocab rows are VERIFIED at row level; 4 are row-level STILL_UNCERTAIN (Vertex ISO 9001, Vertex rubber_molding_compression, Plastic Platers IATF 16949, Finite Fiber tire_rubber_goods).

Certifications by evidence (unit: cert rows): 6 site-scope rows are backed by a fetched, current certificate that names the plant address: Universal Polymer & Rubber Middlefield ISO 9001:2015 and IATF 16949:2016 (Smithers, expire 2027-07-15), Robin Industries North Canton ISO 9001:2015 (Smithers, expires 2029-03-07), Seco Machine North Canton ISO 9001:2015 (expires 2028-01-16), Viscus Biologics ISO 13485:2016 (BSI, expires 2028-04-10), Novation Solutions ISO 9001:2015 (BSI cert held by RDAbbott, location listed, expires 2027-01-21). The other 6 rest on a current own-site statement naming the standard (Finite Fiber ISO 9001:2015 and PuriCel-line ISO 14001, Vertex, Plastic Platers, and org-scope Dinesol and Timco). Not recorded under R3c: Iten ("ISO-9001 certified", no edition), AML ("ISO 9001", no edition), MFG ("ISO-accredited", no standard), Carlisle TyrFil (certificates belong to the German GmbH, not Berea), Synthomer Akron (2021 RCMS statement, not in vocab and not current).

**Measured yield**
- Site-scope capability values (processes, materials, markets) per assigned site: 87/54 = 1.6; per VERIFIED site 87/18 = 4.8. All in-vocab values, all scopes, per assigned site: 251/54 = 4.6.
- Sites with at least one `markets_served` value: **13/54 (24%) at site scope; 35/54 (65%) counting org scope**.
- Sites with at least one site-scope `processes` value: 13/54 (24%); `materials` 13/54 (24%); `certifications` 8/54 (15%) (site scope).
- Sites with at least one in-vocab value at some scope: 41/54 (76%). The 13 with none: Saint-Gobain, Miles, Apollo, Cast Nylons, Rack Coating, Tarkett, Lubrizol (unreachable); BioVerde, Synthomer, Container Compliance, Mustee, Chalfant, AML (no in-vocab value on the pages read).
- VERIFIED rate 18/54 = 33% (tranche 1 was 50% and 48% in the pilot; this tranche has many multi-plant parents and unreachable sites).

**Plant-specificity (hard rule).** Site scope only where a certificate or page names this address, or the site prints one address and shows no other location (each row's `notes` says which). Org scope, nothing pushed down: Akron Polymer Systems (no address printed), Prime Conduit (office suite only), Protective Industrial Polymers, Synthomer, ADS, BioThane (two NE Ohio locations), Carlisle TyrFil, Flavorseal, Dinesol (two facilities), Johnson Brothers (two plants), MFG (14 locations), Oldcastle, Iten (four facilities), Timco, Datwyler/QSR, Robin (non-certificate values), IML, Smithers, Worthington, Flash It (own site prints a different address), ACO, S&A (four plants), STUCK, LANXESS Rhein Chemie, Universal Polymer (molding types). Tied-to-plant sources used first (R3c point 3): the UP&R, Robin, Seco and Viscus certificates, the Synthomer plant pages, and the Carlisle certificate (which turned out to belong to Germany).

## Fetches (unit: fetch attempts)

- **216 total**: 214 curl fetches plus 2 WebFetch second-route reads (Miles, Apollo). Mean 4.0 per site.
- **Cap overshoot, flagged:** UP&R (SITE-000195) 7 (two certificate PDFs fetched after five pages), Dinesol (SITE-000325) 7 distinct pages, Ultratech (SITE-000055) 7 attempts of which the apex TLS failure and a duplicate http redirect to the same www page add no content (5 distinct content pages). All other sites 6 or fewer. Synthomer, Robin and Plastic Platers sat exactly at 6.
- Availability failures (curl 000 TLS or tunnel errors, 403 bot walls, empty 204): **22/214 = 10.3%** (13 curl errors, 8 HTTP 403, 1 HTTP 204). Add 2 more attempts if WebFetch is counted; it loaded both pages but I did not quote from it.
- My own misses (not availability): 2 guessed 404s (BioVerde /contact-us/, BioThane /contact-us/), 1 duplicate (Ultratech http), the Plastic Platers IATF certificate link (HTTP 204, counted above as an availability failure).
- Sites with no usable company content from any route: **7/54 (13%)**: Saint-Gobain (403 x3, proxy 502 x1), Miles (TLS reset x3), Apollo (TLS reset x3), Cast Nylons (expired certificate x2), Rack Coating (self-signed certificate x2), Tarkett (403 x3), Lubrizol (Cloudflare 403 x2). All STILL_UNCERTAIN; none is evidence of closure. No Form 5500 check run, no REJECT.
- **Disclosure:** the very first fetch of the lane (akronpolysys.com home, SITE-000011) went out with a descriptive non-browser User-Agent string I had put in my helper; I removed it at once and every other fetch used curl's default User-Agent. No bot-wall workaround of any kind, no TLS verification bypass. Routes that recovered content: `www.` for Ultratech (apex fails name check); the Synthomer plant pages and the UP&R certificate PDFs by following own-site links.
- Miles and Apollo: curl cannot complete TLS (connection reset), so no quotable text; WebFetch read both (Miles: rubber gaskets/seals/die-cut for defense, heavy truck, automation; Apollo: custom injection molder, 12 machines, 7555 Tyler Blvd Unit 11 Mentor). These are leads only and are noted in `verdicts.csv`.

## Vocabulary gaps met (owner rulings; flagged in `*_other_note`, not settled)

- **Processes:** no solvent-cast film (APS); no packaging/fulfilment-services (Ultratech); no container reconditioning (Container Compliance); no nonwoven / web-forming (Spunfab, S&A non-woven polyester); no urethane pour casting (Seco; potting_encapsulation_casting not used); no PU tire-fill (Carlisle); no netting extrusion (Flavorseal); no coated-webbing extrusion-coating (BioThane); no RIM or D-LFT (MFG); no fiber cutting / RFL treating (Finite Fiber, same gap as J.J. White in tranche 1); no gas fermentation (BioVerde); no biologics wet processing/lyophilization (Viscus); no rubber-additive predispersion or bladder manufacture (LANXESS); no metalforming lubricant (AML); no laser micro welding of metals (H&B); no pool-liner fabrication method (GLI); no continuous fiberglass wall forming (Uniwall); no polymer concrete casting (Oldcastle).
- **Materials:** no butadiene or other monomer (BioVerde); no PPS or PPE (Dinesol); no polymer concrete (Oldcastle); no ECM / animal-tissue biomaterial (Viscus); no non-woven polyester (S&A); no branded sheet grades Boltaron, Kydex, Royalite or TPO (Jos-Tech).
- **Markets:** no data-center market (UP&R); no heavy-truck market (Plastic Platers); no loading-dock/logistics market (Chalfant).
- **Mapping calls the integrator may want to override:** military to aerospace_defense (UP&R); aerospace "military & defense" menu item to aerospace_defense (MFG); vinyl to pvc (GLI, STUCK); swimming-pool products and pools to lawn_garden_recreation (GLI, Uniwall); motorcycles to rv_powersports_trailers and electroplating of plastics to coating_applying (Plastic Platers); hot-melt adhesive web manufacture to adhesive_sealant_formulation (Spunfab); water purification to water_wastewater (APS); polyisoprene noted under specialty_elastomers (Johnson Bros; epichlorohydrin named there, butyl/HNBR/acrylic on its materials page); mining to chemical_mining_metals_processing and food preparation to food_processing_foodservice (Timco); rubber-industry customers to plastics_rubber_processors (LANXESS).
- v1.7.6 terms used as instructed: automotive_unspecified (APS, Ultratech, Dinesol, MFG, Robin, Seco, Spunfab, Precision Foam, Royal Powder, Datwyler, S&A); automotive_oem only where "OE/OEM" is stated (UP&R, Plastic Platers); automotive_aftermarket only where stated (Anchor); tire_rubber_goods (Carlisle, LANXESS, Finite Fiber historical); medical_healthcare_general for "medical/healthcare" without "device"; food_processing_foodservice; specialty_elastomers (Johnson Bros); asa (Dinesol). thermoforming_unspecified, iso_45001 and iso_17025 were not needed.

## Hygiene findings (for the integrator; none resolved)

1. **SITE-001748 / ORG-001672 Flash It:** own site (contact, about) prints 10025 State Route 82, Windham, OH 44288; the row carries 4494 Orchard St, Mantua. Address mismatch; nothing pushed to the site.
2. **SITE-000587 / ORG-000549 Robin Industries:** about page says corporate HQ "near Akron" and three plants plus a development center near Berlin, Ohio (Holmes County, outside PIC-12) and a plant in Mexico. The Smithers ISO 9001:2015 certificate does name 8562 Port Jackson Avenue NW, North Canton, with scope "design, development, prototyping, and manufacture of molded rubber and plastic products", so the row is real, but `hq_and_plant` may overstate. CAK IATF 16949 and ISO 14001 PDFs are linked on the certifications page but not fetched (cap).
3. **SITE-000606 / ORG-000567 Seco Machine:** an AAR certificate on the same page (A16, bearing adapters) shows an expiry of 14 Oct 2026, past as of 1 Nov 2026; not a vocab certification. Row street (5335 Mayfair Rd) matches the ISO certificate.
4. **SITE-001708 / ORG-001635 Eagle Plastics Group:** company formed 2024 at 5340 Mayfair Rd (neighbour of Seco at 5335); molds come from "mold-making partners", so no mold_tool_making. Row city/county already corrected to Green/Summit (postal North Canton).
5. **SITE-000279 / ORG-000262 Carlisle TyrFil:** the ISO 9001:2015 and ISO 14001:2015 certificates on its ISO page are held by Carlisle TyrFil GmbH, Dortmund, not Berea; no cert recorded. Page also carries a German StörfallV notice.
6. **SITE-000210 / ORG-000050 Synthomer Akron:** the site lists two Akron entries: Synthomer Inc., 1380 Tech Way, Akron 44306 and "Akron ATC" Technical Center, 2990 Gilchrist Rd, Akron 44305 (plus Mogadore and Beachwood). The Atlas row has no zip; one Akron row exists for two establishments. The only item on each page is a 2021 RCMS statement (OMNOVA, Beachwood HQ scope).
7. **SITE-001889 / ORG-001856 Novation Solutions:** presents as NovationSi with RDAbbott (Garden Grove, CA); the ISO certificate is RDAbbott's with a "Novation Solutions" registered location. Parent/affiliation handling needed.
8. **SITE-000097 / ORG-000097 BioVerde:** the row is a virtual_incubator; the own site (bioverde.us now redirects to bioverdegroup.com) never mentions Akron or any location, and describes a methane fermentation to bio-butadiene platform. Existing material bioplastics_biobased looks unsupported.
9. **SITE-000011 / ORG-000012 Akron Polymer Systems:** existing material films_flexible_packaging is not supported by any page (solvent-cast films for displays/electronics).
10. **SITE-000305 Container Compliance, SITE-000386 H&B Machine & Tool, SITE-000109 Team Plastic, SITE-001524 Chalfant, SITE-001790 AML, SITE-001928 Rack Coating, SITE-002047 STUCK, SITE-001856 Anchor, SITE-001591 Viscus, SITE-000445 GLI:** ring-1/2 `manufacturing_plant` scope doubts. Drum reconditioner; metalworking and mold shop (rubber molding is stated); plastics distributor/fabricator; loading-dock equipment maker; metalforming lubricants; powder-coating job shop; online decal seller (own site "Under Construction"); branded aftermarket mounts supplier (no process stated); animal-tissue biologics; pool-liner maker (fine, but no vocab process). Owner rulings; none is a REJECT.
11. **SITE-000123 / ORG-000124 Prime Conduit:** only an office suite is printed (23240 Chagrin Blvd Suite 405); row is already hq_only with ring 1.
12. **SITE-000445 / ORG-000416:** row name says Latham Pool Products (Youngstown - GLI); own site is GLI Pool Products, Inc. at 215 Sinter Court (matches the row).
13. **SITE-001428 / ORG-001389 IML Containers Ohio:** own site (history page) lists plants in Quebec, Iowa and Arizona; no page mentions Ohio or Alliance (street was OSHA-derived).
14. **SITE-000570 / ORG-000534 Quality Synthetic Rubber:** org website is the Datwyler parent; none of its pages name Twinsburg or QSR.
15. **SITE-000412 / ORG-000386 Iten:** four Ashtabula facilities; printed address 4602 Benefit Avenue, PO Box 2150, row street 4001 Benefit Ave (Grok).
16. **SITE-000483 / ORG-000451 MFG:** HQ is 2925 MFG Place, Ashtabula (rd_center row street from Grok); MFG lists 14 North American locations.
17. **SITE-000426 / ORG-000397 Johnson Bros:** second plant at 41 N. Center St, Greenwich (Huron County, outside PIC-12); not in the Atlas data checked here.
18. **SITE-000530 / ORG-000495 Plastic Platers (MPC Plating):** IATF certificate link (URL dated 2021-12-16) returns HTTP 204; currency unproven.
19. **SITE-000181 / ORG-000174 Vertex:** about page says ISO registration "valid until June, 2024"; custom-extrusions page says ISO 9001-2015 certified, undated.
20. **SITE-000463 Cast Nylons and SITE-001928 Rack Coating:** own-site TLS certificates expired / self-signed (availability only, not closure).
21. **SITE-001441 Smithers Medical:** existing process polyurethane_foaming is not in vocab and not seen on the site; no address or plant printed.
22. **SITE-000339 Mustee:** five pages, no address, plant, material or process.

## Per-site summary

See `verdicts.csv` (54 rows: verdict, deciding or settling fact, fetches used, availability failures). Site-level verdict is in `verdicts.csv`; row-level `verdict` in `packet.csv` is VERIFIED for a supported in-vocab value, STILL_UNCERTAIN for an off-vocab note or an unconfirmed-currency cert or mapping.

## Files

- `packet.csv`: 279 rows (251 in-vocab, 28 off-vocab), columns as in the pilot.
- `verdicts.csv`: 54 rows.

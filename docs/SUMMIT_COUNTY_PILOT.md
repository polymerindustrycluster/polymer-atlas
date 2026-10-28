# Summit County Polymer Pilot — Coverage & Dedup Feasibility Test

**For:** John Swanson, Polymer Industry Cluster (PIC)
**Scope:** SUMMIT COUNTY, OHIO ONLY. One-county pilot, speed over depth. No NAICS/address deep-verification.
**Date of harvest:** 2026-10-28
**Question tested:** How hard are coverage and deduplication, really, if you try to build a comprehensive Ohio polymer database from free public web sources alone?

> **Headline result: 99 unique candidate organizations** with a Summit County presence, harvested from 4 public source types.
> **Only 16 of 99 (16.2%) appeared in 2 or more source types. 83 (83.8%) appeared in exactly one.**
> That low overlap is the pilot's most important finding — see Analysis.

---

## 1. Method — 4 source types

| Code | Source type | What was actually queried |
|---|---|---|
| **A — Thomasnet / directory** | Industry directory | Thomasnet "Northern Ohio" category pages surfaced via search: rubber goods, sheet rubber, plastics, extruded plastics, plastic extrusions, recycled plastics, custom/medical plastics, copolymers (multiple category queries) |
| **B — Association / cluster** | Trade-association & cluster lists | SPE Akron Section newsletters & tour/advertiser mentions; Rubber Division, ACS exhibitor list; Ohio Rubber Group contributor/newsletter lists; Greater Akron Chamber Polymer Cluster report + Greater Akron Polymer Innovation Hub partner announcements |
| **C — Process + city web search** | Open web / local listings | Process+city queries: "injection molding Akron", "rubber compounding Akron", "plastics extrusion Cuyahoga Falls / Hudson / Twinsburg", "thermoforming Akron", plus city sweeps for Twinsburg, Hudson/Macedonia, Barberton/Norton, Cuyahoga Falls/Stow/Tallmadge |
| **D — ED / news / other lists** | Economic-development & secondary lists | JobsOhio project announcements, Team NEO / Plastics News regional reporting, Greater Akron Polymer Innovation Hub launch coverage, Inven "plastic manufacturing companies in Ohio" list, company-HQ/news profiles (e.g., Myers Industries) |

**Inclusion rule (pilot, deliberately loose):** any company, startup, nonprofit, OEM, distributor, equipment/testing supplier, university program, or ecosystem org with a plausible Summit County establishment, HQ, plant, branch, or office doing polymer/plastics/rubber work. Borderline polymer-adjacent entries are kept in the list but flagged "borderline" in the description — excluding them silently would hide a real design decision the full database must make explicitly.

**Geography rule:** Summit County cities only — Akron, Barberton, Cuyahoga Falls, Hudson, Macedonia, New Franklin, Norton, Stow, Tallmadge, Twinsburg, Fairlawn, Copley, Bath, Green, Mogadore (Summit portion). Listings in Streetsboro/Aurora (Portage), Sharon Center (Medina), Bedford/Strongsville (Cuyahoga), Middlefield (Geauga), Canton/Hartville (Stark) were **excluded** even when a source labeled them "Akron" or "Northern Ohio" — see False Positives.

**Record rule:** name, city, one-line description, source(s), website if readily available. Nothing else. No NAICS verification, no address verification, no employee counts.

---

## 2. Candidate list — 99 unique organizations (after dedup)

| # | Organization | City (Summit Co.) | What they do (one line) | Source(s) | Website |
|---|---|---|---|---|---|
| 1 | Goodyear Tire & Rubber Co. / Goodyear Chemical | Akron | Tire OEM + synthetic rubber / copolymers (global HQ + Chemical division listing) | A-Thomasnet, B-Assoc/Cluster, D-ED/News | goodyear.com |
| 2 | Bridgestone Americas Technology Center | Akron | Tire R&D / materials labs (~700 staff per Chamber report) | B-Assoc/Cluster, D-ED/News | bridgestoneamericas.com |
| 3 | Myers Industries, Inc. | Akron | Polymer products mfr (injection/rotational/blow molding via brands) + tire-supply distribution; NYSE HQ | C-Process+City, D-ED/News | myersindustries.com |
| 4 | Akron Polymer Systems | Akron | Optical / specialty polymer films and materials | B-Assoc/Cluster, C-Process+City | akronpolysys.com |
| 5 | E & T Plastics Mfg. Co., Inc. | Akron | Plastics distributor / fabricator (sheet, rod, tube, film) | A-Thomasnet, C-Process+City | e-tplastics.com |
| 6 | D & D Plastics, Inc. | Akron | Plastics manufacturer / supplier | C-Process+City | — |
| 7 | Diamond America | Akron | Extrusion systems / dies (polymer processing equipment) | C-Process+City | daextrusion.com |
| 8 | Gabriel Performance Products | Akron | Specialty chemicals / resins for polymers (HQ/sales listing) | C-Process+City | gabrielchem.com |
| 9 | Chemigon LLC | Akron | Rubber / plastics chemicals and compounding support | C-Process+City | chemigon.com |
| 10 | Ace Rubber Products | Akron | Custom rubber products / fabrication | C-Process+City | theacerubber.com |
| 11 | King Machine Molds / King Model and Castings | Akron | Molds, models and castings for plastics | C-Process+City | kingmachinemolds.com |
| 12 | Rapid Mold Solutions / Rapid Mold Repair and Machine | Akron | Mold repair and machining for plastics | C-Process+City | rapidmoldsolutions.com |
| 13 | Paddington Group | Akron | Plastics manufacturer / supplier (listing-level detail only) | C-Process+City | paddingtongroup.com |
| 14 | Greatoo Inc. (U.S.) | Akron | Tire molds / intelligent equipment (U.S. presence) | C-Process+City | greatoo.com |
| 15 | Ravizza Packaging USA Corp. | Akron | Packaging machinery / plastics packaging (U.S. office) — borderline sales-office | C-Process+City | ravizzapackagingusa.com |
| 16 | ALCO Chemical | Akron | Chemical distribution (polymer-adjacent) — borderline | C-Process+City | alco-chem.com |
| 17 | Musson Rubber Co. | Akron | Rubber products mfr + distributor (matting, sheet, belting, hose) | A-Thomasnet | — (Thomasnet profile) |
| 18 | Enterprise Rubber, Inc. | Akron | Custom molded rubber goods, rubber-to-metal bonding | A-Thomasnet | — (Thomasnet profile) |
| 19 | The Hygenic Corp. | Akron | Rubber / latex sheeting and elastomer products | A-Thomasnet | — (Thomasnet profile) |
| 20 | M. F. Murdock Co. (The) | Akron | Sheet rubber distributor | A-Thomasnet | — (Thomasnet profile) |
| 21 | Akron Rubber Development Laboratory, Inc. (ARDL) | Akron / Barberton | Rubber & plastics testing, compounding, development lab | A-Thomasnet, B-Assoc/Cluster, C-Process+City | ardl.com |
| 22 | Piedmont Plastics, Inc. (Akron branch) | Akron | Plastics distribution + fabrication (branch establishment) | A-Thomasnet | piedmontplastics.com |
| 23 | Akron Porcelain & Plastics Co. | Akron | Thermoplastic injection + thermoset molding, porcelain/plastics fabrication | A-Thomasnet | — (Thomasnet profile) |
| 24 | Acme Pattern Works, Inc. | Akron | Wood / metal / plastic patterns for molding | A-Thomasnet | — (Thomasnet profile) |
| 25 | LyondellBasell (Akron / Fairlawn presence, incl. former A. Schulman) | Akron | Polyolefin copolymers / advanced polymer solutions | A-Thomasnet, B-Assoc/Cluster | lyondellbasell.com |
| 26 | Akron Polymer Products | Akron | Custom extruded plastics — tubing, harnesses, automotive lines | A-Thomasnet | — (Thomasnet profile) |
| 27 | Saint-Gobain Performance Plastics (Akron plant) | Akron | High-performance polymer products (plant establishment) | C-Process+City | saint-gobain.com |
| 28 | Win Plastic Extrusions LLC | Akron | Plastic profile extrusion | C-Process+City | extrudedplastics.com |
| 29 | HKB Enterprises, Inc. | Akron | Plastics manufacturing (listing-level detail only) | C-Process+City | hkbenterprises.com |
| 30 | Pioneer Plastics Corp. | Akron / Green | Plastics manufacturer / fabricator | C-Process+City | pioneerplasticscorp.com |
| 31 | Landmark Plastic Corp. | Akron | Thermoformed / molded horticultural plastics | C-Process+City | landmarkplastic.com |
| 32 | Spectrum Plastics Corp. | Akron | Plastics manufacturer / fabricator | C-Process+City | splastics.com |
| 33 | Next Generation Plastics | Akron / Fairlawn | Plastics recycling programs / reprocessing | C-Process+City | nextgenplastics.com |
| 34 | Multibase, Inc. (DuPont) | Akron / Copley | Silicone masterbatch / TPE compounding | B-Assoc/Cluster, C-Process+City | dupont.com/multibase-family.html |
| 35 | Alterra Energy | Akron | Plastics pyrolysis / chemical recycling | D-ED/News | — (Inven Ohio list) |
| 36 | APV Engineered Coatings | Akron | Engineered coatings (polymer coatings) | B-Assoc/Cluster | apvcoatings.com |
| 37 | Akron Ascent Innovations LLC | Akron | Dry-adhesion / advanced materials startup | B-Assoc/Cluster | — |
| 38 | Akron Surface Technologies, Inc. (ASTI) | Akron | Surface treatment / polymer surface technology | B-Assoc/Cluster | — |
| 39 | Smithers (Smithers Scientific / MSE, Akron labs) | Akron | Rubber & plastics testing and consulting labs | B-Assoc/Cluster | smithers.com |
| 40 | Akrochem Corp. | Akron | Rubber chemicals / compounding ingredients supplier | B-Assoc/Cluster | akrochem.com |
| 41 | Akron Polymer Solutions, Inc. | Akron | Polymer / rubber solutions (exhibitor-listed, detail thin) | B-Assoc/Cluster | — |
| 42 | GOJO Industries, Inc. | Akron | Skin-care chemicals + polymer dispensing systems; HQ — polymer-adjacent | D-ED/News | gojo.com |
| 43 | Synthomer, Inc. (Akron / Mogadore presence) | Akron / Mogadore | Synthetic latex / polymer dispersions | B-Assoc/Cluster, D-ED/News | synthomer.com |
| 44 | Continental ContiTech USA (HQ) | Fairlawn | Industrial rubber goods — belts, hose, conveyor systems | B-Assoc/Cluster | continental-industry.com |
| 45 | Harwick Standard Distribution Corp. | Akron | Rubber / polymer chemicals distribution (HQ) | B-Assoc/Cluster | harwickstandard.com |
| 46 | Sovereign Chemical Co. | Akron | Rubber chemicals supplier | B-Assoc/Cluster | — |
| 47 | Americhem, Inc. | Cuyahoga Falls | Color & additive masterbatch, engineered compounds (global HQ + plant) | B-Assoc/Cluster, C-Process+City, D-ED/News | americhem.com |
| 48 | Ultratech Polymers, Inc. | Cuyahoga Falls | Extruded + die-cut polymer products | C-Process+City | ultratechpolymers.com |
| 49 | CF Extrusion Technologies | Cuyahoga Falls | Extrusion technology / systems | C-Process+City | cfextrusion.com |
| 50 | Smithers-Oasis Co. | Cuyahoga Falls | Polymer floral foam + related products — borderline | C-Process+City | smithersoasis.com |
| 51 | Steelastic | Cuyahoga Falls | Tire-building / belt machinery (polymer processing equipment) | C-Process+City | steelastic.com |
| 52 | Struktol Company of America, LLC | Stow | Polymer processing additives / rubber chemicals (U.S. HQ) | B-Assoc/Cluster, D-ED/News | struktol.com |
| 53 | Laird Plastics (Akron branch) | Stow | Plastics distribution + CNC fabrication (branch establishment) | A-Thomasnet, C-Process+City | lairdplastics.com |
| 54 | Esterle Mold & Machine Co., Inc. | Stow | Molds / tooling for plastics | D-ED/News | esterle.com |
| 55 | Ferriot, Inc. | Stow | Custom injection molding | B-Assoc/Cluster | ferriot.com |
| 56 | Chemionics Division, Protech Group | Tallmadge | Plastisol dispersions, dip coatings, foams | A-Thomasnet | — (Thomasnet profile) |
| 57 | Akron Gasket | Tallmadge | Plastic / rubber extrusions, gaskets and seals (despite name, Tallmadge) | A-Thomasnet | — (Thomasnet profile) |
| 58 | Green Technologies of Ohio, LLC | Tallmadge | Gaskets, seals, fabricated foam/rubber/plastic parts | A-Thomasnet | — (Thomasnet profile) |
| 59 | Hudson Extrusions, Inc. | Hudson | Custom extruded plastic tubing + profiles | A-Thomasnet | — (Thomasnet profile) |
| 60 | Custom Plastic Extrusions, Ltd. | Hudson | Custom thermoplastic extrusions / compounds | A-Thomasnet | — (Thomasnet profile) |
| 61 | Taylor Made Pipe Plugs / Hand-Tite | Hudson | Plastic pipe plugs / test plugs | C-Process+City | hand-tite.com |
| 62 | Plastic Process Equipment, Inc. (PPE) | Macedonia | Plastics machinery, equipment + supplies mfr/distributor | A-Thomasnet | ppe.com |
| 63 | Design Molded Plastics | Macedonia | Plastic injection molding (design-to-production) | C-Process+City | designmolded.com |
| 64 | Plastic Materials, Inc. (PMI) | Macedonia | Plastic materials / manufacturing (listing-level detail only) | C-Process+City | plasticmaterialsinc.com |
| 65 | Miles Rubber & Packing | Twinsburg | Die-cut, molded + extruded rubber products | C-Process+City | milesrubber.com |
| 66 | Cima Plastics Group | Twinsburg | Plastics manufacturing group | C-Process+City | cimaplastics.com |
| 67 | Professional Plastics (Twinsburg branch) | Twinsburg | Plastics distribution + fabrication (branch establishment) | C-Process+City | professionalplastics.com |
| 68 | MRP Solutions / Mold-Rite / Weatherchem | Twinsburg | Injection-molded plastic closures / caps (see merge note) | C-Process+City | mrpcap.com |
| 69 | Industrial Mold & Machine | Twinsburg | Mold manufacturing for plastics | C-Process+City | industrialmold.com |
| 70 | Crown Composites Tooling / Crown Mold | Twinsburg | Composites tooling / molds | C-Process+City | crownmold.net |
| 71 | Mantaline Corp. (Twinsburg listing) | Twinsburg | Extruded rubber / polymer seals — HQ is Mantua (Portage); Twinsburg listing needs verification | C-Process+City | mantaline.com |
| 72 | Giesecke+Devrient America (Twinsburg plant) | Twinsburg | Plastic cards / secure devices — borderline polymer product | C-Process+City | gi-de.com |
| 73 | General Plastex, Inc. | Barberton | Screws, barrels + components for injection/extrusion machines | C-Process+City | generalplastex.com |
| 74 | Ace Plastics | Barberton / Akron | Custom injection molding (see merge note — two listings, one firm) | A-Thomasnet, C-Process+City | — (Thomasnet profile) |
| 75 | Novex, Inc. | Barberton | Plastics manufacturer / equipment supplier (listing-level detail) | C-Process+City | novexinc.com |
| 76 | Merryweather Foam, Inc. | Barberton | Foam (polymer foam) components fabrication | C-Process+City | merryweather.com |
| 77 | Michael Day Enterprises, LLC | Norton | UHMW / engineered plastics machining + engineering | C-Process+City | mdayinc.com |
| 78 | Q Model, Inc. | Barberton | Plastic models / patterns / fabrication | C-Process+City | qmodelinc.net |
| 79 | Ohio Precision Molding | Barberton | Precision plastic molding — shares address with Ace Plastics listing; possible co-location/successor | C-Process+City | ohioprecisionmolding.com |
| 80 | Rubber Associates, Inc. | New Franklin | Custom rubber molding / products | C-Process+City | rubberassociates.com |
| 81 | Rainbow Rubber Extrusions | New Franklin | Rubber extrusions | C-Process+City | rainbowrubber.com |
| 82 | PPG Industries (Barberton plant) | Barberton | Coatings / specialty chemicals plant — polymer-adjacent, borderline | C-Process+City | ppg.com |
| 83 | University of Akron — College of Polymer Science & Polymer Engineering / Goodyear Polymer Center / National Polymer Innovation Center | Akron | Largest U.S. academic polymer program; research + pilot facilities | B-Assoc/Cluster, D-ED/News | uakron.edu |
| 84 | Akron Polymer Training Center (APTC) | Akron | Workforce training for plastics + rubber (UA-affiliated, distinct program) | B-Assoc/Cluster | uakron.edu/aptc |
| 85 | Rubber Division, American Chemical Society | Akron | National rubber trade/professional association (HQ in Akron) | B-Assoc/Cluster, C-Process+City | rubber.org |
| 86 | SPE — Akron Section | Akron | Society of Plastics Engineers local section (nonprofit chapter) | B-Assoc/Cluster | akronspe.org |
| 87 | Ohio Rubber Group | Bath | Regional rubber industry association (nonprofit) | B-Assoc/Cluster | ohiorubbergroup.org |
| 88 | Greater Akron Chamber — Polymer Industry Cluster (PIC) | Akron | Cluster convener / economic development (the sponsor org itself) | B-Assoc/Cluster, D-ED/News | greaterakronchamber.org |
| 89 | Bounce Innovation Hub | Akron | Startup hub hosting polymer startups (ecosystem org) | D-ED/News | bouncehub.org |
| 90 | MKV Polymers, Inc. (U.S. sales office) | Akron | Engineering-plastics recycling (German parent; Bounce office) | D-ED/News | — |
| 91 | G3 Mixing Technologies | Akron area | Rubber mixing machinery (recent arrival per Signal Akron reporting) | D-ED/News | — |
| 92 | BioVerde | Akron area | Bio-based precursor to synthetic rubber (recent arrival, detail thin) | D-ED/News | — |
| 93 | Spazzolplastica (U.S. presence) | Akron area | Plastic wire-basket spools (Italian parent; local footprint unverified) | D-ED/News | — |
| 94 | Materium Technologies | Akron area | AI-designed nanocomposite films (recent arrival, detail thin) | D-ED/News | — |
| 95 | R. E. Carroll, Inc. (Hudson / Akron sales presence) | Hudson | Rubber process oils + chemicals distribution | B-Assoc/Cluster | recarroll.com |
| 96 | Polymerics, Inc. | Cuyahoga Falls | Rubber compounding / custom mixing — city attribution needs verification | B-Assoc/Cluster | — |
| 97 | Alpha Technologies | Hudson | Rubber / polymer test instruments (rheometers) — U.S. HQ | B-Assoc/Cluster | alpha-technologies.com |
| 98 | Preferred Compounding (now Hexpol) | Copley | Rubber compounding | B-Assoc/Cluster | hexpolcompounding.com |
| 99 | Omnova Solutions (Mogadore plant, now Synthomer) | Mogadore | Polymer dispersions / specialty chemicals plant — see Synthomer merge note | D-ED/News | synthomer.com |
---

## 3. Analysis

### 3.1 Overlap: the sources barely agree with each other

| Metric | Count | Share |
|---|---|---|
| Unique candidates (post-dedup) | **99** | 100% |
| Found by 2+ source types | **16** | 16.2% |
| Found by exactly 1 source type | **83** | 83.8% |
| Found by 3 source types | 2 (ARDL; Americhem) | 2.0% |
| Found by all 4 source types | **0** | 0% |

The 16 multi-source firms: Goodyear, Bridgestone Americas Tech Center, Myers Industries, Akron Polymer Systems, E & T Plastics, ARDL, LyondellBasell, Multibase, Synthomer, Americhem, Struktol, Laird Plastics, Ace Plastics, University of Akron polymer program, Rubber Division ACS, Greater Akron Chamber/PIC.

**Interpretation:** Multi-source appearance is a proxy for *size and public visibility*, not for existence. The overlap set is almost exactly "the famous names" — global HQs, the university, the national association HQ. Everything below that tier lives in exactly one silo. Any single-source harvest therefore has a hard ceiling: the best single source (C) still missed 48 of 99 candidates (48.5%).

### 3.2 Which source found what the others missed?

| Source type | Total hits (incl. overlaps) | **Unique-only** (found by this source and no other) | What it uniquely contributes |
|---|---|---|---|
| **C — Process+city web/Places** | 51 | **42** | The long tail of small shops: mold shops, extruders, foam fabricators, Twinsburg/Barberton small manufacturers. By far the largest unique yield. Also the noisiest (see false positives). |
| **B — Association/cluster** | 29 | 17 | Testing labs, chemical suppliers, nonprofits, training center, and firms that *convening* surfaces but directories don't (Ferriot, APV, ASTI, Akrochem, Harwick Standard, Alpha Technologies). SPE itself publishes **no usable company directory** — yield came from newsletters, tour hosts, advertisers, and exhibitor/contributor lists, i.e., archaeology, not a list. |
| **A — Thomasnet** | 20 | 14 | Established manufacturers/distributors who pay for / maintain directory profiles (Musson, Enterprise Rubber, Hygenic, Chemionics, Hudson Extrusions). Cleanest data of any source — and the smallest, most self-selected universe. Thomasnet only contains firms that chose to list. |
| **D — ED/news/other lists** | 18 | 10 | HQs, R&D centers, startups and recent arrivals that *sell nothing locally* and so appear in no directory: Bridgestone Tech Center (with B), Myers HQ (with C), MKV Polymers, G3 Mixing, BioVerde, Materium, Alterra, Bounce. JobsOhio/Team NEO publish **project announcements, not rosters** — there is no public ED list to harvest, only press releases. |

**Best source type:** C, on raw unique yield (42 uniques no one else found) — but it is also the least trustworthy per-record.
**Worst source type:** A, on coverage (20 total; a self-selected, pay-to-play-adjacent subset) — but the most trustworthy per-record. D is worst on *effort per record*: hours of narrative reading for 18 hits.
**No source is redundant.** Removing any one source type loses 10–42 organizations outright. That is the signature of a fragmented universe with no spine — not of a mature directory ecosystem.

### 3.3 Duplicates and name variants that had to be merged

Dedup was manual and judgment-heavy even at n≈100. Recurring patterns, with pilot examples:

1. **Legal name vs. directory name vs. brand name (same firm, 3 strings)**
   - *E & T Plastics* (Places) = *E & T Plastics Mfg. Co., Inc.* (Thomasnet).
   - *Akron Rubber Development Laboratory* = *ARDL* = *Akron Rubber Development Laboratory, Inc.* — listed in Akron by Thomasnet, in **Barberton** by Places (it has operations in both; counted once).
   - *Goodyear Chemical* (Thomasnet division listing) = part of *The Goodyear Tire & Rubber Company* — directory logic splits what cluster logic merges.
2. **Acquisitions / renames (old name still ranks in search)**
   - *Weatherchem Corp.* + *Mold-Rite Plastics* + *MRP Solutions* — same Twinsburg closures business, three live names/websites; counted once.
   - *A. Schulman* → *LyondellBasell* Advanced Polymer Solutions (Fairlawn/Akron presence now under LyondellBasell).
   - *Omnova Solutions* (Mogadore plant) → *Synthomer* — sources from different years name different owners for what is very likely the **same establishment**. Retained as two candidate rows in this speed pilot and flagged here as a **probable residual duplicate: true unique count is therefore 98–99, not a clean 99.** A production database needs an establishment-level ID to resolve exactly this.
   - *Preferred Compounding* → *Hexpol Compounding*; *Multibase* → DuPont brand page.
3. **Same address, different firm names (co-location, successor, or error — unresolvable at pilot speed)**
   - *Ace Plastics* and *Ohio Precision Molding* share 122 E. Tuscarawas Ave, Barberton; *Ace Plastics* is also Thomasnet-listed in Akron (44310). Counted Ace once; kept Ohio Precision Molding separate with a flag.
   - *Rubber Associates* (1522 Turkeyfoot Lake Rd) and *Rainbow Rubber Extrusions* (1580 Turkeyfoot Lake Rd), New Franklin — adjacent addresses, similar work; kept separate, likely related.
   - *King Machine Molds* (website) = *King Model and Castings* (listing name); *Crown Composites Tooling* = *Crown Mold*; *Rapid Mold Repair and Machine* = *Rapid Mold Solutions*; *Taylor Made Pipe Plugs* = *Hand-Tite*.
4. **Misleading geographic names**
   - *Akron Gasket* is in **Tallmadge**. *Laird Plastics "Akron"* is in **Stow**. *Ultratech Polymers* says "based in Akron" on its site, lists in **Cuyahoga Falls**. Name-based geocoding would misplace all three.
5. **HQ vs. branch vs. plant collapsed into one row (a schema problem, not just a dedup problem)**
   - Laird Plastics, Piedmont Plastics, Professional Plastics are **branch establishments** of national distributors; Goodyear, Americhem, Myers, Struktol are **HQs**; Saint-Gobain and PPG are **plants** of foreign/national parents. A company-count and an establishment-count will differ materially, and every source type mixes the two without labeling them.

### 3.4 False positives excluded — and why they matter

Excluded from the 99. Each class below consumed real triage time:

| False-positive class | Examples excluded | Why it appeared |
|---|---|---|
| Keyword-only "rubber" | Rubber City Theatre, Rubber City Productions, Rubber City Reuse (compost drop-off) | "Rubber compounding Akron" query matches any "Rubber City" branding |
| Radius / "Northern Ohio" spillover (Thomasnet's worst flaw) | Transcendia (Strongsville), Mercury Plastics & Universal Plastics (Middlefield), Cuyahoga Plastics (Cleveland), Tencom (Holland), Resco (East Canton), Hamilton Polymers (Leetonia), Profile Rubber (Sharon Center, Medina) | Thomasnet category pages are regional, not county-bounded; roughly half the names on a given page were out-of-county |
| Near-Akron, wrong county | **Aurora Plastics (Streetsboro — Portage Co.)**, Orazen Extruded Polymers (Aurora — Portage), Seglian (Bedford — Cuyahoga), USA Injection Molding (Hartville — Stark) | Search engines and even JobsOhio treat "Akron area / Northeast Ohio" as the geography. Aurora Plastics is the dangerous one: a major, legitimate polymer compounder, repeatedly presented as local, that a Summit-only (or Summit-credited) database must not claim |
| National list mistaken for local list | ~150+ Rubber Division, ACS exhibitors (Dow, Evonik, Cabot, Zeon, etc.); Ohio Rubber Group contributors (RT Vanderbilt, Sid Richardson, Continental Carbon…); SPE advertisers (Dover Chemical — Dover, OH) | Association lists are national/orbit lists. Only ~6 Rubber Division exhibitors have a Summit presence. Using exhibitor lists as a local roster without a location filter produces a >90% false-positive rate |
| Generic distributors / incidental sellers | Grainger (Akron branch) — Thomasnet "rubber" hit | Sells rubber among 1M+ SKUs; not a polymer-industry organization in any useful membership sense |
| Category-adjacent services | Summit Environmental Technologies, Envisage Environmental (Thomasnet "chemical analysis" hits) | Analytical services ≠ polymer testing; contrast ARDL/Smithers, which are genuinely polymer-specific and were kept |
| Big Akron employers, not polymer | Babcock & Wilcox, FirstEnergy, Summa Health | Surface in "Akron major employers" content alongside Goodyear/Myers |
| Stale / historical names still ranking | Advanced Elastomer Systems, BFGoodrich/Goodrich, Firestone HQ, General Tire as Akron HQs | Akron's rubber history is so well documented that dead/absorbed HQs outrank living small firms. Without a currency check, a web harvest builds a museum, not a database |

**Borderline entries kept, deliberately flagged in the table:** PPG Barberton plant, Smithers-Oasis (floral foam), Giesecke+Devrient (plastic cards), Ravizza Packaging USA (sales office), ALCO Chemical, GOJO. Whether these are "in" is a *definition* decision (how far down the value chain / how polymer-specific?) that John/PIC must make once, in writing, before any statewide build — six borderline calls in one county implies ~hundreds statewide.

### 3.5 Large employers expected — that no source surfaced easily

- **Bridgestone Americas Technology Center, Akron (~700 associates per the Chamber's own cluster report): invisible to Thomasnet and to every process+city query.** It surfaced only in cluster/ED narrative (Source B/D). R&D centers don't sell, don't list, and don't optimize for "rubber Akron" searches. Any directory-led method systematically misses the region's R&D establishments — arguably the highest-value PIC targets.
- **Goodyear's Akron HQ as an establishment:** Thomasnet surfaced only a *division* listing ("Goodyear Chemical"); no source produced a clean HQ record. The most famous polymer employer in Ohio is, in directory terms, a partial record.
- **Hankook Tire America Technical Center (Uniontown/Green area) and Kenda's American Technology Center (Green): zero hits in any pilot query.** Cited here from background knowledge, *not* from any pilot source — which is precisely the point. Two substantial tire-R&D employers in the county were completely absent from a 4-source harvest. If the method misses known R&D centers in the densest county, its recall on unknown small firms is unknowable from web data alone.
- **PPG's Barberton plant:** surfaced only as a map pin categorized "paint store." A large chemical plant, effectively invisible as an industrial employer.

### 3.6 What Summit's N does — and does not — imply statewide

**The arithmetic that must not be done:** 99 × 88 counties ≈ 8,700. Summit is not an average county; it is the extreme outlier (Akron, the historical "Rubber Capital," the University of Akron polymer program, two tire-company R&D centers). Ohio polymer employment is Pareto-distributed: a handful of counties (Summit, Cuyahoga, Lake, Stark, Geauga/Portage, Franklin, Hamilton, Butler, Montgomery, Lucas) plausibly hold the large majority of establishments.

**What the pilot does support:**
- The user's heard figure of **~900 polymer/plastics/rubber companies in Ohio is plausible as a *company* count** — and may even be conservative as an *establishment* count. Cross-checks found in this harvest: PolymerOhio/Ohio Supercomputer Center material has claimed **"more than 2,800 polymer-related facilities"** and ~140,000 employees statewide (dated, definitional, facilities ≠ companies); the University/Wikipedia "Polymer Valley" tradition cites **400+ polymer companies in Northeast Ohio alone** (also dated). If one county yields ~99 candidates at pilot speed — with known misses ( §3.5) implying a true Summit establishment count nearer **130–180** under NAICS 326 / 325211 / 333 / 424610-style definitions — then a statewide total in the high hundreds (companies) to low thousands (establishments) is the right order of magnitude. The 900 figure cannot be confirmed or refuted by web harvest; it can only be settled against an establishment spine (see Verdict).
- **Density falloff will be brutal.** After the top ~10 counties, expect single digits per county, then zeros. A statewide build is therefore not "88× the Summit work" — it is ~10 deep county builds plus ~78 shallow ones. Budgeting by county count misprices it in both directions.

**What the pilot does NOT support — rural-county transfer:**
- Web-harvest recall in Summit is propped up by exactly the assets rural counties lack: a Thomasnet-listing culture among established firms, a local SPE section and Rubber Division HQ generating paper trails, a chamber that publishes cluster reports, and local news covering arrivals. A 15-person molder in a rural county with a one-page website, no directory listing, no association membership, and no press will be found by **none** of Sources A–D reliably. The method's recall collapses precisely where density is lowest — and because there is no ground truth, you will not know it collapsed.
- Precision also degrades rurally: with few true firms in a search radius, search engines backfill with out-of-county results (the §3.4 spillover problem gets worse, not better, as true density falls).

---

## 4. Verdict — web harvest alone cannot reach comprehensiveness

**Honest verdict: No. Web harvest alone cannot deliver a comprehensive, defensible Ohio polymer database. A paid/licensed establishment list is required as the spine.**

Reasoning, in one paragraph per leg:

1. **Coverage leg.** 83.8% single-source overlap at the *source-type* level, zero firms in all four sources, and known large R&D employers (Hankook, Kenda) absent from every source together prove the free-web universe is not a superset of reality — it is four partial, biased samples of it (self-listed firms; association-adjacent firms; web-visible shops; newsworthy firms). Stacking more free sources adds yield with diminishing returns and never fixes the shared blind spot: quiet firms.
2. **Ground-truth leg.** Without a spine, there is no denominator. You cannot state coverage ("we have X% of Ohio polymer establishments"), cannot detect misses, and cannot distinguish "rural county has 2 firms" from "rural county harvest failed." Census County Business Patterns / QCEW can supply county×NAICS denominators even where firm names are suppressed.
3. **Identity leg.** §3.3's merges (acquisitions, brands, HQ/branch/plant conflation, same-address firms) cannot be resolved reliably from scraped strings. Licensed establishment data (Data Axle / Dun & Bradstreet) ships with persistent company/establishment IDs, parent-linkage, NAICS/SIC, employee size, and HQ-vs-branch flags — i.e., it pre-solves the hardest 60% of dedup.

**Recommended architecture (spine + enrichment, not spine *or* swarm):**

- **Spine (buy/license once, refresh annually):** Data Axle ReferenceUSA, D&B, or the Ohio manufacturers directory equivalent — filtered to Ohio × relevant NAICS (326 plastics & rubber products; 325211 resins/synthetic rubber; plus explicitly-decided adjacencies: 333248/333511 machinery & molds, 424610 plastics distribution, 541715/541380 testing & R&D, 813920 associations, 611310 university programs). This gives the establishment list, IDs, and county denominators.
- **Enrichment (the swarm's real job):** agent teams do exactly what this pilot did — Thomasnet, association, process+city, ED/news — but as *enrichment and discovery on top of the spine*: filling websites, capabilities, contacts, and flagging spine-missing firms (startups, R&D centers, recent arrivals like MKV/G3/BioVerde/Materium, which licensed lists lag by 6–18 months).
- **Maintenance:** news/LinkedIn/social scanning is well-suited to *change detection* (openings, expansions, closures, M&A renames — the §3.3 failure modes) once the spine exists to detect changes *against*. As a discovery-only system with no baseline, it drifts silently.
- **Definition first:** PIC must fix, in writing, (a) company vs. establishment as the unit, (b) the NAICS/borderline boundary tested in §3.4, before purchase — the license filter depends on both.

**Pilot limitations (stated plainly):** single harvester, search-engine-mediated access to Thomasnet/association PDFs (not direct database queries), no LinkedIn, no site visits, no phone verification, ~half-day effort. Counts are therefore a *floor* for Summit and an *illustration* of overlap/dedup mechanics — not a Summit census. That limitation strengthens, rather than weakens, the verdict: even a competent, multi-source free harvest in the easiest county in Ohio produced a fragmented, partially unverifiable list with known holes.

*File: summit-county-pilot.md — candidate rows are pilot-grade (unverified) and must not be published as a PIC directory without spine reconciliation and firm-level verification.*

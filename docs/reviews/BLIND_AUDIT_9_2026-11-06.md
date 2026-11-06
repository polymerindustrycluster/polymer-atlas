# Blind audit 9 — six merged 2026-11-06 state waves

**50 sampled sites: 32 agreement on tested claims (64%), 1 confirmed field-error site (2%), 1 closed-before-create error site (2%), and 16 unresolved sites (32%).** Canonical rows changed: **0**, at every tier. Correction application belongs to the controller/L11, not this audit.

The two confirmed findings are Dart Corona’s manufacturing classification and Yokohama Spartanburg’s active creation after a confirmed closure. A warehouse is a lawful establishment under SCHEMA4.5/5.3, so Dart is a field error. The controller’s audit9 assignment expressly includes **closed** in creation errors; Yokohama is counted there although the historical plant was real. This does not recommend deleting its history. No inferred closure day is supplied.

Agreement certifies only address/operator/polymer-scope/site-function claims actually tested. It does **not** certify every field, NAICS, county, legal continuity, headcount, verification tier or continuous present operation. Canonical `unknown` status is not an error merely because an operating witness exists. Unresolved is never counted as agreement or confirmed absence.

## Confirmed corrections — not applied

| Sampled site | Grade and held claim | Settling public primary source | Proposed correction |
|---|---|---|---|
| SITE-014003 — Dart, 150 S Maple St, Corona CA | Field error: `site_type=manufacturing_plant` | [Current operator location](https://corporate.dartcontainer.com/location/corona-ca/) explicitly describes the **Corona Distribution Center** at this address; parent independently re-fetched its words. | Review `warehouse_distribution`; retain the real establishment. Own published ZIP92878 differs from held92880, but that postal conflict is **not** counted as a settled error. |
| SITE-012023 — Yokohama TWS, 570 Trelleborg Dr, Spartanburg SC | Creation error under requested **closed** category: `operating_status=active` at 2026-11-06 creation | [Issuer FY2025 results briefing, 2026-02-19](https://www.y-yokohama.com/global/ir/pdf/document/25_4Qpresentation_en_transcripts.pdf), PDF p.17: **“Y-TWS Spartanburg Plant Closed”**. [Official WARN](https://dew.sc.gov/sites/dew/files/Documents/2025%20South%20Carolina%20WARN_Report%2003032025.pdf) ties the operator to exact570TrelleborgDr. The issuer outcome is later than the notice. | Review `closed`; retain historical plant. WARN projected2025-04-19 is **not** asserted as actual closure date. Closed by2026-02-19 is supported; exact day remains unknown. |

The required Form5500 check was run before the parent’s closure classification: fresh [EFAST2 PY2025 bulk](https://askebsa.dol.gov/FOIA%20Files/2025/Latest/F_5500_2025_Latest.zip), all codes/plans, sponsor EIN061316073 and Yokohama/Trelleborg names. The two Yokohama TWS filings use Wakefield MA, not this Spartanburg establishment; no address-specific operating counter-signal was found. A corporate benefit plan is not plant activity, and absence from this bulk is not proof of closure. The dated issuer outcome decides. Exact filter/hash/selected business addresses: [form5500_gate.json](../../tasks/blind-audit-9-2026-11-06/form5500_gate.json).

## Population and fixed random draw

Data pin: `97ee6bc2a4475a47d8449ca79db688fb9114ab0f`. Exact new site IDs from each merge versus its first parent, reconciled to every PR’s published creation count: **110 unique site creations**. No annotation, watch marker, repoint, organization creation or registry-link row was counted. This uses canonical ID first appearance rather than build-metadata creation-class guesses.

| Wave / lane | Merged PR | New sites by creation tier |
|---|---|---:|
| L7-FL | [#132](https://github.com/polymerindustrycluster/polymer-atlas/pull/132) | 17 C |
| L6-CA | [#135](https://github.com/polymerindustrycluster/polymer-atlas/pull/135) | 3 B, 16 C |
| L11-MI | [#138](https://github.com/polymerindustrycluster/polymer-atlas/pull/138) | 17 C |
| L3-MO-SC-LA | [#141](https://github.com/polymerindustrycluster/polymer-atlas/pull/141) | 18 B, 1 C |
| L7-GA | [#142](https://github.com/polymerindustrycluster/polymer-atlas/pull/142) | 20 C |
| L11-IL | [#143](https://github.com/polymerindustrycluster/polymer-atlas/pull/143) | 18 C |

Eight nonempty lane×creation-tier strata; **44 C + 6 B** sampled versus **89 C + 21 B** in the population (88.0% versus 80.9% C). There are no A creations in this six-wave frame. Sampling was uniform without replacement inside each stratum, using sorted site IDs, the public fixed seed `BLIND-AUDIT-9-2026-11-06-v1`, and independent SHA256-seeded Python Random streams. Allocation was frozen before primary re-verification; no outcome-driven redraws or replacements.

Draw frozen `2026-11-06T11:51:25.121869+00:00`; sample SHA256 `ec9b5cb11ef3c61e30a78df32c06608fca335da57f2d298ba0c775bde4eac39e`. All 50 independent verdicts and the parent’s source-based taxonomy/candidate adjudications froze before original evidence release at `2026-11-06T12:04:59.054703+00:00`. Comparison began `2026-11-06T12:05:28.495209+00:00`. [Frame](../../tasks/blind-audit-9-2026-11-06/frame.csv), [sample](../../tasks/blind-audit-9-2026-11-06/sample.csv), [draw receipt](../../tasks/blind-audit-9-2026-11-06/draw.json), [final freeze](../../tasks/blind-audit-9-2026-11-06/freeze.json).

## Rates by sampling stratum

Unit: sampled sites in the named lane×**creation-tier** stratum. Each cell gives observed count/denominator, percent, and **95% Wilson interval in percent**. All sampled sites, including unresolved, stay in the denominator. These are intervals for observed finding categories, not latent all-field accuracy; Wilson ignores finite-population correction and within-company clustering. A census stratum still shows the requested binomial reference interval, which is not sampling uncertainty.

| Lane | Tier | Population / sample | Agreement [95%] | Field error [95%] | Creation error [95%] | Unresolved [95%] |
|---|:---:|---:|---|---|---|---|
| L11-IL | C | 18 / 9 | 5/9 55.6% [26.7–81.1] | 0/9 0.0% [0.0–29.9] | 0/9 0.0% [0.0–29.9] | 4/9 44.4% [18.9–73.3] |
| L11-MI | C | 17 / 8 | 7/8 87.5% [52.9–97.8] | 0/8 0.0% [0.0–32.4] | 0/8 0.0% [0.0–32.4] | 1/8 12.5% [2.2–47.1] |
| L3-MO-SC-LA | B | 18 / 5 | 4/5 80.0% [37.6–96.4] | 0/5 0.0% [0.0–43.4] | 1/5 20.0% [3.6–62.4] | 0/5 0.0% [0.0–43.4] |
| L3-MO-SC-LA | C | 1 / 1 census | 1/1 100.0% [20.7–100.0] | 0/1 0.0% [0.0–79.3] | 0/1 0.0% [0.0–79.3] | 0/1 0.0% [0.0–79.3] |
| L6-CA | B | 3 / 1 | 1/1 100.0% [20.7–100.0] | 0/1 0.0% [0.0–79.3] | 0/1 0.0% [0.0–79.3] | 0/1 0.0% [0.0–79.3] |
| L6-CA | C | 16 / 9 | 5/9 55.6% [26.7–81.1] | 1/9 11.1% [2.0–43.5] | 0/9 0.0% [0.0–29.9] | 3/9 33.3% [12.1–64.6] |
| L7-FL | C | 17 / 8 | 3/8 37.5% [13.7–69.4] | 0/8 0.0% [0.0–32.4] | 0/8 0.0% [0.0–32.4] | 5/8 62.5% [30.6–86.3] |
| L7-GA | C | 20 / 9 | 6/9 66.7% [35.4–87.9] | 0/9 0.0% [0.0–29.9] | 0/9 0.0% [0.0–29.9] | 3/9 33.3% [12.1–64.6] |

Using stratum design weights N/n, observed-finding points for these 110 created sites are **65.3% agreement /1.6% field error /3.3% creation error /29.8% unresolved**. These are weighted observed-category estimates, not a pooled simple-random-sample error rate. The weighted confirmed-error point is 4.9%; treating every unresolved sampled site as an error would make it 34.7%. That sensitivity calculation is not a confidence interval or a bound on untested facts. No pooled iid CI or improvement claim is made.

## Next to audits 7 and 8

| Audit | Unit / frame | Published observed outcomes | Comparison limit |
|---|---|---|---|
| 7 |65 sampled records; older creation frame |58/65 agreement (89.2%) |Only agreement total is established by QUEUE F1 / audit8’s comparison. The other 7 cannot be assigned to field/creation/unresolved categories here. |
| [8 /PR9](https://github.com/polymerindustrycluster/polymer-atlas/pull/9) |65 TRI-era records: 29 organizations + 36 sites, passes20–25 |53 agreement (81.5%), 2 field (3.1%), 0 creation, 10 unresolved (15.4%) |Original report at4311e9e, not merely a done checkbox. Risk-stratum oversampling, different grain/time/claim coverage. |
|9 /this audit |50 sites only from the six named merged waves |32 agreement (64%), 1 field (2%), 1 closed-creation (2%), 16 unresolved (32%) |Current requested closed-category taxonomy; eight stratified cells, many small. Not a causal trend or equivalent all-field accuracy measure. |

The F1-style blind procedure is comparable as a method; denominators, source availability, observation dates and error taxonomy differ. The lower agreement share can reflect unresolved verification and cannot by itself establish that the newer data are worse. [Historical comparison provenance](../../tasks/blind-audit-9-2026-11-06/historical_comparison.json).

## Evidence blindness and its explicit limitation

Three researchers received only sampled canonical assertions, parent names/websites and lane/tier metadata. Existing `sources`, `notes`, evidence rows, original lane packets and verification prose were withheld. They reported no original evidence access; the parent did not release it until the full frozen census. This is **evidence-blind, not metadata-blind**. The parent verified an ASH single-facility exact-address/polymer example with three fresh raw quote matches and a fabricated negative before scaling the remaining research.

**One first-lock metadata violation is disclosed.** SITE-014014’s two NSF citations changed `source_class` from company_website to certification_registry after its incremental object lock. Grade, facts, quotations, URLs, raw_checked, limitations and lock timestamp were unchanged. Command interval2026-11-06 12:01:38.237–12:01:43.037UTC, before original evidence release. Reversing exactly those two fields reconstructs the first object and exactly reproduces its independently saved hash; it is a reconstruction, not a retained prior file. First hash `97deaa854c3f135ac663181731e31a12734adf8eea2d4d3d73ccfa8de40bf344`, final `90440f2ba108b7ee491f6419516ea08a2180ff6949439c40aaa67f51ed282f75`. The other 49 objects match their first independently observed parent hashes. Final hashes for all 50 verdicts were frozen before unblinding. This breach does not show evidence exposure, but prevents a claim of perfect incremental immutability. [Exact change/timing](../../tasks/blind-audit-9-2026-11-06/blind_metadata_correction.json).

Before unblinding, the parent retained the immutable researcher verdicts and separately adjudicated two matters: Yokohama’s helper field-error label becomes creation_error under the controller’s explicit closed category, after the dated outcome and Form5500 check; Dart ZIP is excluded from confirmed errors. Storopack’s CraigRoad/CraigPlace published conflict remains a candidate until physical-street/alias and dominant-function reconciliation, not an automatically counted field error. [Adjudications](../../tasks/blind-audit-9-2026-11-06/adjudications.json), [unaltered researcher files](../../tasks/blind-audit-9-2026-11-06/freeze.json).

## Sixteen unresolved sites — required settling facts

| Site | Settling primary fact |
|---|---|
| SITE-014007 — NuSil Technology | A fetchable own-site or official record explicitly naming silicone/polymer manufacturing at 2343 Pegasus Drive, with enough current context to establish the held site function. |
| SITE-014010 — Heritage Bag-Rancho | A site-specific primary statement that this Rancho Cucamonga plant manufactures plastic/polymer bags or identifying its polymer extrusion/conversion process. |
| SITE-014015 — MERCURY PLASTICS | Fetchable site-specific process/permit proving polymer manufacturing at 14849 and explaining relationship to own-site 14825 COI factory address; current status also unconfirmed. |
| SITE-016000 — Hilex Poly Co. LLC - Jacksonville | A site-specific own-site process description, permit or inspection proving plastic bag/film manufacturing at 500 N Ellis Rd Suite A and dated current activity. |
| SITE-016006 — FXI, Inc. - Miami | Own-site or official establishment record explicitly tying FXI foam production/fabrication to 11000 NW 32nd Avenue, Miami; a city-only company location list is insufficient. |
| SITE-016009 — Sealed Air Corporation - Lakeland | Own-site or official address-specific record linking 5135 Drane Field to Sealed Air polymer packaging production, rather than an office or another Lakeland facility; dated status evidence. |
| SITE-016010 — Cork Industries Inc. - Jacksonville | Raw-accessible company or official site-specific evidence tying Cork at5555 W Beaver to polymer coating formulation/manufacturing and present physical operation. |
| SITE-016015 — Storopack, Inc. - Medley | Site-specific process/permit or own-site description identifying the dominant physical function and polymer products processed or handled at Medley Suite 4, plus current activity. |
| SITE-016101 — WinCup - Stone Mountain | A current own-site plant listing or issued/current official operating record connecting WinCup to EPS manufacturing at 4640 Lewis Road. Old draft and inaccessible current pages do not settle current establishment claims. |
| SITE-016105 — GAF Materials Corporation - Valdosta | Raw primary brochure or official establishment record confirming operator,2100 Steeda physical address/ZIP and current TPO manufacture; specifically resolve31601 versus31606. |
| SITE-016116 — Altium Packaging - Atlanta | Fetchable official inspection/permit or own-site record naming Altium at 6220 Duquesne and confirming plastic bottle manufacturing versus R&D/distribution, plus current status. |
| SITE-018015 — Lacks Enterprises, Inc. - Kentwood | Fetchable site-specific permit or own-site text identifying plastic molding or other polymer transformation and dominant function at 5801 Kraft, plus current operation if status adjudicated. |
| SITE-019001 — Pella Corporation - Macomb | Fetchable own-site or official address record linking Pella Macomb vinyl-window plant to 111 Pella Place; dated activity if current status is to be adjudicated. |
| SITE-019002 — Pactiv Corporation - Manteno | A primary site-specific production description linking Pactiv at1050 Sycamore to polymer transformation/manufacturing, plus current physical-function confirmation. |
| SITE-019009 — Storopack, Inc. - Hillside | Site-specific primary process/function statement for the Hillside establishment: whether polymer transformation occurs here or the physical function is sales/distribution. |
| SITE-019011 — Reynolds Consumer Products Inc. - Jacksonville | Fetchable official filing or employer plant-specific source confirming plastic film/bag production at 2226 East Morton Avenue; current establishment function must be explicit. |

HTTP403,307 non-content,404, image-only or missing exact-site content are availability/verification limits, never evidence of nonexistence or closure. No hold is replaced by the original evidence after unblinding. Company-wide scope alone is insufficient for a sampled plant-function agreement. GAF’s indexed ZIP difference and Dart/Storopack postal suffix conflicts are referrals, not inflated confirmed-error counts.

## Complete sampled-site index

| Site / identity | Final grade | Primary research record |
|---|---|---|
| SITE-012001 — WATSON COATINGS INC - ST LOUIS | agreement | [source1](https://watsoncoatings.com/wp-content/uploads/2025/07/White_AntiClimb_SafetyData.pdf), [source2](https://watsoncoatings.com/about-us/) |
| SITE-012022 — RE: BUILD CR, LLC - Rock Hill | agreement | [source1](https://cr.rebuildmanufacturing.com/contact/), [source2](https://cr.rebuildmanufacturing.com/about/) |
| SITE-012023 — Yokohama TWS North America, Inc. - Spartanburg | creation_error | [source1](https://www.y-yokohama.com/global/ir/pdf/document/25_4Qpresentation_en_transcripts.pdf), [source2](https://dew.sc.gov/sites/dew/files/Documents/2025%20South%20Carolina%20WARN_Report%2003032025.pdf) |
| SITE-012026 — HAHL INC - Lexington | agreement | [source1](https://www.perlon.com/wp-content/uploads/2019/03/Perlon_Press_March_2017_en.pdf), [source2](https://www.perlon.com/en/portrait-perlon/current-vacancies-2/) |
| SITE-012031 — Sun Drilling Products Corp. - Belle Chasse | agreement | [source1](https://sunspecialtyproducts.com/wp-content/uploads/2024/09/2023-SDS-COASTAL-SPOT.pdf), [source2](https://sunspecialtyproducts.com/about-us/) |
| SITE-012034 — ASH INDUSTRIES, INC. - Lafayette | agreement | [source1](https://www.ashindustries.com/) |
| SITE-014003 — DART CONTAINER CORPORATION | field_error | [source1](https://corporate.dartcontainer.com/location/corona-ca/) |
| SITE-014006 — Cal spas | agreement | [source1](https://dealers.calspas.com/pdf/newsletter/2017_01_se.pdf), [source2](https://calspas.com/contact) |
| SITE-014007 — NuSil Technology | unresolved | [source1](https://www.dir.ca.gov/oshab/DECISIONS-ALJ/2020/1195278-Nusil-Technology.pdf) |
| SITE-014008 — Madera | agreement | [source1](https://www.madera.gov/media/tsgh1yj5/issued-permits-february-2026.pdf), [source2](https://www.adspipe.com/resources/case-studies/hp-storm-creates-savings-in-california-right-of-way-install) |
| SITE-014010 — Heritage Bag-Rancho | unresolved | [source1](https://files.ceqanet.lci.ca.gov/265020-3/attachment/asDIyxasBHOFATlXQOmeEpQysSnhxSEbUUMmlO4iFsdAxn2z3VlcB9q85fawfkDPVIemgExYzKWfrHrT0), [source2](https://novolex.com/pages.php?pageid=101) |
| SITE-014013 — Scientific Specialties, Inc. | agreement | [source1](https://www.ssibio.com/) |
| SITE-014014 — V M INTERNATIONAL | agreement | [source1](https://info.nsf.org/Certified/Food/Listings.asp?Company=C0804305&Standard=002), [source2](https://buylowwholesale.com/pages/about-us) |
| SITE-014015 — MERCURY PLASTICS | unresolved | [source1](https://www.fire.lacounty.gov/wp-content/uploads/2023/07/CUPA-List-Active-7.11.23.pdf) |
| SITE-014017 — ATS PRODUCTS INC | agreement | [source1](https://atsduct.com/FAQ/), [source2](https://atsduct.com/about-us/) |
| SITE-014019 — Altium Packaging - Corona | agreement | [source1](https://ccc.wd5.myworkdayjobs.com/wday/cxs/ccc/ccc_External/job/Production-Packaging-Associates-3rd-Shift_R19690), [source2](https://coronaplasticpackaging.com/) |
| SITE-016000 — Hilex Poly Co. LLC - Jacksonville | unresolved | [source1](https://novolex.com/pages.php?pageid=101), [source2](https://novolex.com/content/PDF/Novolex-Supplier-Onboarding-FAQ.pdf) |
| SITE-016004 — MAPEI Corporation - Wildwood | agreement | [source1](https://cdnmedia.mapei.com/docs/librariesprovider10/products-documents/7_large-tile-and-stone-mortar-white_822e0934af184e5b87c5a7415f8cf2cc.pdf?Status=Master&sfvrsn=4548c265_0), [source2](https://cdnmedia.mapei.com/docs/librariesprovider10/iso-certifications/iso-14001-2015.pdf?sfvrsn=449e7574_23) |
| SITE-016006 — FXI, Inc. - Miami | unresolved | [source1](https://www.fxi.com/what-we-do) |
| SITE-016009 — Sealed Air Corporation - Lakeland | unresolved | [source1](https://careers.sealedair.com/en/jobs/operator-mailer-night-shift-en-57054) |
| SITE-016010 — Cork Industries Inc. - Jacksonville | unresolved | [source1](https://corkindustries.com/) |
| SITE-016013 — Amrize Building Envelope LLC - Jacksonville | agreement | [source1](https://www.elevatecommercialbp.com/ca-en/resources/about-us) |
| SITE-016015 — Storopack, Inc. - Medley | unresolved | [source1](https://www.storopack.us/company/about-us/storopack-worldwide/) |
| SITE-016017 — CANTEX Inc. - Auburndale | agreement | [source1](https://www.cantexinc.com/Portals/0/CANTEX-PVC-Extruded-Electrical-Conduit-Environmental-Product-Declaration-EPD.pdf) |
| SITE-016101 — WinCup - Stone Mountain | unresolved | [source1](https://epd.georgia.gov/document/document/08900097draftpdf/download) |
| SITE-016103 — The Goodyear Tire & Rubber Company - Stockbridge | agreement | [source1](https://epd.georgia.gov/document/document/procsortretrlandjuly2017pdf/download), [source2](https://corporate.goodyear.com/us/en/company/locations.html) |
| SITE-016105 — GAF Materials Corporation - Valdosta | unresolved | [source1](https://documents.gaf.com/brochures-%26-literature/everguard-tpo-brochure-comeg417.pdf) |
| SITE-016108 — MAPEI Corporation - Dalton | agreement | [source1](https://cdnmedia.mapei.com/docs/librariesprovider65/iso-certifications/iso-45001-mapei-na_en.pdf?sfvrsn=680d0f89_0), [source2](https://cdnmedia.mapei.com/docs/librariesprovider65/realta-mapei-magazine/en_2014_19.pdf?sfvrsn=d0142b77_16) |
| SITE-016109 — MAPEI Corporation - Calhoun | agreement | [source1](https://cdnmedia.mapei.com/docs/librariesprovider10/iso-certifications/iso-9001-2015.pdf?sfvrsn=429e7574_15), [source2](https://cdnmedia.mapei.com/docs/librariesprovider10/realta-mapei-magazine/24-2045-rmna38-fullissue-en.pdf?sfvrsn=3cc81888_5) |
| SITE-016111 — The Sherwin-Williams Company - Covington | agreement | [source1](https://industrial.sherwin-williams.com/na/us/en/aerospace/find-location/location-detail.undefined.en_US-10371519-PCG_Manufacturing_GID.html) |
| SITE-016113 — Advanced Drainage Systems, Inc. - Perry | agreement | [source1](https://www.dot.state.al.us/publications/materials/pdf/MSDSAR/QMSD/Li11.pdf) |
| SITE-016116 — Altium Packaging - Atlanta | unresolved | Unresolved route; see frozen record |
| SITE-016119 — Crown USA, Inc. - Thomaston | agreement | [source1](https://crownusa.com/our-story/), [source2](https://crownusa.com/directions/) |
| SITE-018000 — Summit Polymers, Inc. - Kalamazoo | agreement | [source1](https://www.egle.state.mi.us/aps/downloads/permits/finpticon/2017/64-17B.pdf) |
| SITE-018001 — Plastipak Packaging, Inc. - Westland | agreement | [source1](https://www.egle.state.mi.us/aps/downloads/SRN/N3206/N3206_SAR_20160405.pdf) |
| SITE-018003 — Cooper Standard - Gaylord | agreement | [source1](https://www.egle.state.mi.us/aps/downloads/permits/finpticon/1990/62-90C.pdf), [source2](https://careers.cooperstandard.com/job/13314824/production-associate-gaylord-mi/) |
| SITE-018006 — The Spiratex Company - Monroe | agreement | [source1](https://www.spiratex.com/contact-us/), [source2](https://www.spiratex.com/about/) |
| SITE-018007 — Pregis LLC - Marysville | agreement | [source1](https://www.egle.state.mi.us/aps/downloads/srn/N6944/N6944_SAR_20240201.pdf), [source2](https://www.pregis.com/contact-us/) |
| SITE-018012 — Techniplas US LLC - Jonesville | agreement | [source1](https://www.techniplas.com/wp-content/uploads/2024/12/Jonesville-ISO_14001-2015_Jonesville_261220.pdf) |
| SITE-018015 — Lacks Enterprises, Inc. - Kentwood | unresolved | [source1](https://www.michigan.gov/taxes/-/media/Project/Websites/treasury/BLGSS/PSD_CSD/Industrial-Facility-Exemption/2020-STC-Certs/Amended-Certificates-081820.pdf?hash=B0534876C464EA071CCEFF4FEBAB5DEF&rev=716eea688af64e3daeba1eec540fcf8e) |
| SITE-018017 — Advanced Drainage Systems, Inc. - Owosso | agreement | [source1](https://onlinepubs.trb.org/onlinepubs/Archive/NotesDocs/20-07%28191%29_FR.pdf), [source2](https://idot.illinois.gov/content/dam/soi/en/web/idot/documents/doing-business/specialty-lists/highways/materials/materials---physical-research/misticproducers.pdf) |
| SITE-019001 — Pella Corporation - Macomb | unresolved | [source1](https://pressroom.pella.com/women-leaders-at-pella-corporation-recognized-for-excellence-in-manufacturing/) |
| SITE-019002 — Pactiv Corporation - Manteno | unresolved | [source1](https://apps.dot.illinois.gov/eplan/desenv/082214/66429-015/66429-015.pdf) |
| SITE-019007 — Avery Dennison - Mt. Prospect | agreement | [source1](https://reflectives.averydennison.com/en/home/locations.html), [source2](https://d3n9y02raazwpg.cloudfront.net/mountprospect/7187b7ba-4ecf-11eb-920e-0050569183fa-8a553f6f-20df-4e89-9078-a16d8dee3216-1635865563.pdf) |
| SITE-019008 — Trelleborg Corp - Streamwood | agreement | [source1](https://www.trelleborg.com/-/media/tss-media-repository/tss_website/pdf-and-other-literature/brochures/orkot_marine_bearings_engineering_manual_en.pdf), [source2](https://www.trelleborg.com/-/media/tss-media-repository/tss_website/pdf-and-other-literature/brochures/manufact_capabilities_gb_en.pdf) |
| SITE-019009 — Storopack, Inc. - Hillside | unresolved | [source1](https://www.storopack.us/company/about-us/storopack-worldwide/) |
| SITE-019011 — Reynolds Consumer Products Inc. - Jacksonville | unresolved | [source1](https://west-central.org/wp-content/uploads/2026/05/Document_20260501_0002.pdf) |
| SITE-019012 — Berry Global - Alsip | agreement | [source1](https://villageofalsip.org/Current%20Licenses%2005282024.pdf) |
| SITE-019014 — Mauser Packaging Solutions - Elk Grove Village | agreement | [source1](https://www.usplastic.com/catalog/files/specsheets/UNClosingInstructions.pdf), [source2](https://mauserpackaging.com/about-mauser/locations/) |
| SITE-019019 — The Sherwin-Williams Company - Kankakee | agreement | [source1](https://www.epscca.com/en_GB/contact-us/locations/), [source2](https://www.epscca.com/en/terms-of-use/) |

Full source quotations, fields actually tested, temporal limitations and all successful/failed routes remain in the three frozen verdict/receipt files; company-hosted third-party certificates are public certification witnesses, not company-authored claims merely because of hosting. No source classification from this audit is applied to canonical evidence.

## Post-freeze provenance comparison, checks and corrections

Only after freeze, 351 original evidence rows for the 50 sampled sites were read: 314 government_filing and 37 own_site. Typed record coverage: activity40/50, address50/50, code49/50, existence50/50, liveness40/50, parent50/50, scope50/50, size_band6/50. Typed presence is not factual accuracy or complete current-operation proof. Original records did not retroactively settle any blind uncertainty. [Comparison](../../tasks/blind-audit-9-2026-11-06/original_evidence_comparison.json).

Runnable checks: `python3 tasks/blind-audit-9-2026-11-06/frame.py` (110true creations/count reconciliation); `python3 tasks/blind-audit-9-2026-11-06/check.py` (50unique selected verdicts, freeze/admitted-metadata delta, independently reproduced sample/statistics/report, missing/duplicate/unreported-edit defect rejection, and no canonical diff). `stats.py` reuses the house Wilson function, with0/20,20/20,10/20known answers. `python3 scripts/validate.py`:0errors. The three researcher raw checks covered115raw-checked quoted observations (two additional unread/discovery citations excluded),159fetch receipts, fabricated negatives and explicit unread routes; parent independently re-fetched ASH and all four decisive Dart/Yokohama quote observations. Raw-response hashes/temporary paths are receipts, not promises that remote pages will never change.

Coordination limit:159 fetch receipts cover 155 distinct URLs. Each sampled site used at most 6 routes; across multiple sampled sites of the same operator, MAPEI used 7 distinct routes, ADS 8, and Sherwin-Williams 7. The approximate six-per-organization budget was not strictly enforced globally. These overruns are disclosed, not hidden by changing the counting unit. No failed route became a negative finding.

No scripts/ changes; full scripts pytest notrun. Sixteen site verification gaps remain; counties/NAICS/headcount/all-field truth and all 110 sites were not audited. No data/ edits, IDs, registry-link changes, merges or task-status changes. Corrections and qualified candidates sent to controller and L11 correction owner in [correction_handoff.json](../../tasks/blind-audit-9-2026-11-06/correction_handoff.json). L11’s GilkeySITE019018/EastJordanSITE018014 findings are **unsampled** and excluded from all audit numerators. Separate Codex/Grok adversarial approvals remain pending; report is a draft until both required verdicts are recorded.

## Review status

Codex/OpenAI clerk5 APPROVE36b18b5, zero blocking findings: independently reproduced the frame, sample, all rates/intervals/weights; reviewed all50 rationales, verified all159rawhashes/115admittedquotes and fresh14sites/24URLs/32quotations. Qualified blindness/metadata exception and current-activity limits accepted. Grok review remains pending; draft, no two-family completion claim. No frozen result or rate changed.

---

## Addendum — larger-budget follow-up of the 16 unresolved sites (2026-11-06)

The original report and its sampling/grade tables above remain unchanged. This follow-up revisits **exactly its 16 unresolved sites**, against the same frozen canonical assertions. No other sampled record was regraded and no new site entered the sample. Controller authorization raises the budget to **up to 10 source routes per site**. Fresh verifiers received frozen assertions and parent names/websites, with original evidence, original blind results and post-freeze corrections withheld. They knew this was an unresolved-case follow-up. The parent had already seen original evidence and acted as an **unblinded integrator**, not a blind verifier.

**Follow-up 16:** 2 agreement, 0 field_error, 0 creation_error, 14 unresolved. **Updated full 50:** 34 agreement (68.0%), 1 field_error (2.0%), 1 creation_error (2.0%), 14 unresolved (28.0%).

These are updated observed-finding rates after additional, deliberately unequal verification effort. They are not a second random draw, a causal improvement measure, or proof that unresolved/untested facts are correct. Original sampling strata, inclusion probabilities and design weights stay fixed. The original 34 resolved records remain byte-value identical; temporal changes and new-source limits are stated per site.

All 16 fresh verdicts froze at `2026-11-06T13:10:22.542849+00:00` before comparison. All 16 verdict objects still match their first parent-observed lock hashes; separate clarifications never overwrite them. Baseline hashes, fresh-file hashes, per-site route receipts and checks are in [follow-up packet](../../tasks/blind-audit-9-followup-2026-11-06/README.md). The independent parent known-answer checks confirmed literal quotations and rejected fabricated additions; a failed preliminary Storopack NW normalization hypothesis was corrected to the page’s verbatim N.W.100th wording, with no match-rule relaxation or outcome based on the failed hypothesis.

### Updated rates on the original lane×creation-tier strata

Unit: sampled sites from the original 50. Count/denominator, observed percent and 95% Wilson interval in percent. Unresolved cases stay in denominators. These binomial reference intervals do not remove verification-selection bias, site clustering, or uncertainty in untested fields; no pooled iid interval is supplied.

| Lane | Creation tier | Population / sample | Agreement [95%] | Field error [95%] | Creation error [95%] | Unresolved [95%] |
|---|:---:|---:|---|---|---|---|
| L11-IL | C | 18 / 9 | 6/9 66.7% [35.4–87.9] | 0/9 0.0% [0.0–29.9] | 0/9 0.0% [0.0–29.9] | 3/9 33.3% [12.1–64.6] |
| L11-MI | C | 17 / 8 | 7/8 87.5% [52.9–97.8] | 0/8 0.0% [0.0–32.4] | 0/8 0.0% [0.0–32.4] | 1/8 12.5% [2.2–47.1] |
| L3-MO-SC-LA | B | 18 / 5 | 4/5 80.0% [37.6–96.4] | 0/5 0.0% [0.0–43.4] | 1/5 20.0% [3.6–62.4] | 0/5 0.0% [0.0–43.4] |
| L3-MO-SC-LA | C | 1 / 1 | 1/1 100.0% [20.7–100.0] | 0/1 0.0% [0.0–79.3] | 0/1 0.0% [0.0–79.3] | 0/1 0.0% [0.0–79.3] |
| L6-CA | B | 3 / 1 | 1/1 100.0% [20.7–100.0] | 0/1 0.0% [0.0–79.3] | 0/1 0.0% [0.0–79.3] | 0/1 0.0% [0.0–79.3] |
| L6-CA | C | 16 / 9 | 5/9 55.6% [26.7–81.1] | 1/9 11.1% [2.0–43.5] | 0/9 0.0% [0.0–29.9] | 3/9 33.3% [12.1–64.6] |
| L7-FL | C | 17 / 8 | 4/8 50.0% [21.5–78.5] | 0/8 0.0% [0.0–32.4] | 0/8 0.0% [0.0–32.4] | 4/8 50.0% [21.5–78.5] |
| L7-GA | C | 20 / 9 | 6/9 66.7% [35.4–87.9] | 0/9 0.0% [0.0–29.9] | 0/9 0.0% [0.0–29.9] | 3/9 33.3% [12.1–64.6] |

Design-weighted updated observed points (same N/n weights): 69.1% agreement, 1.6% field_error, 3.3% creation_error, 26.0% unresolved. These estimates describe the resulting evidence classifications, not all-field site accuracy or an equivalent-depth population census.

### All 16 follow-up outcomes and remaining settling facts

| Frozen site / identity | New grade | Fresh settling evidence or remaining fact |
|---|---|---|
| SITE-014007 — NuSil Technology | unresolved | Current exact-address NuSil process/manufacturing document linking silicone formulation to 2343 Pegasus and resolving dominant plant versus R&D function. [source1](https://www.dir.ca.gov/oshab/DECISIONS-ALJ/2020/1195278-Nusil-Technology.pdf); [source2](https://www.ewlerp.com/___country___/uploadedfile/rawmaterial/cb/CES-1104%20-%20COMPOSITION.pdf) |
| SITE-014010 — Heritage Bag-Rancho | unresolved | Raw-verifiable primary site-specific permit or company production/job statement linking plastic bag/film processing to 12320 Fourth St and its legal operator, dated by frozen 2026-11-06. [source1](https://novolex.com/pages.php?pageid=101); [source2](https://files.ceqanet.lci.ca.gov/265020-3/attachment/asDIyxasBHOFATlXQOmeEpQysSnhxSEbUUMmlO4iFsdAxn2z3VlcB9q85fawfkDPVIemgExYzKWfrHrT0) |
| SITE-014015 — MERCURY PLASTICS | unresolved | Authoritative parcel/situs or regulator process record establishing whether 14849 is the same Mercury manufacturing campus as 14825, or a distinct physical function/operator. [source1](https://www.sigmaplasticsgroup.com/location/mercury-plastics-inc-ca/); [source2](https://fire.lacounty.gov/wp-content/uploads/2023/07/CUPA-List-Active-7.11.23.pdf) |
| SITE-016000 — Hilex Poly Co. LLC - Jacksonville | unresolved | Exact-address manufacturing permit or company plant process/job statement identifying plastic bag extrusion/conversion at 500 N Ellis Rd Suite A and current operation. [source1](https://novolex.com/pages.php?pageid=101); [source2](https://novolex.com/content/PDF/Novolex-Supplier-Onboarding-FAQ.pdf) |
| SITE-016006 — FXI, Inc. - Miami | unresolved | Employer-controlled exact-address job/process page confirming FXI fabrication/foam work at 11000 NW 32nd Avenue and current legal operator. [source1](https://www.fxi.com/what-we-do); [source2](https://diversityjobs.com/career/18293668/Machine-Operator-Florida-Miami) |
| SITE-016009 — Sealed Air Corporation - Lakeland | unresolved | Accessible company process description, manufacturing permit or EDC original report linking polymer film/Bubble Wrap production to this exact Lakeland address and operator. [source1](https://diversityjobs.com/career/18768823/Operator-Mailer-Night-Shift-Florida-Lakeland) |
| SITE-016010 — Cork Industries Inc. - Jacksonville | agreement | Cork Industries company-authored homepage identifies Jacksonville Lab & Manufacture at the exact address and describes formulation of coatings, adhesives and UV inks. These formulated coatings support Ring 2 under SCHEMA §1. Current page is positive operational evidence; frozen active is consistent. No claim that NAICS or every held field is independently certified. [source1](https://corkindustries.net/) |
| SITE-016015 — Storopack, Inc. - Medley | unresolved | Primary site-specific statement or permit establishing whether Suite 4 manufactures polymer packaging, warehouses it, or performs sales/service, and its operating date. [source1](https://www.storopack.us/company/about-us/storopack-worldwide/) |
| SITE-016101 — WinCup - Stone Mountain | unresolved | Current exact-address company or regulator process record confirming WinCup EPS manufacturing continues at 4640 Lewis Road under the held operator. [source1](https://epd.georgia.gov/document/document/08900097narpdf/download); [source2](https://epd.georgia.gov/document/document/08900097notpdf/download) |
| SITE-016105 — GAF Materials Corporation - Valdosta | unresolved | Dated raw-accessible operating evidence for GAF at 2100 Steeda Way, plus authoritative postal/situs confirmation of ZIP 31606 versus held 31601; current/planned status and legal operator must be tied to exact site. [source1](https://detroitmi.gov/sites/detroitmi.localhost/files/hdc-decisions/2026-02/HDC2026-00021_HDC_COA_Approval_for_%5B1676_Chi.pdf) |
| SITE-016116 — Altium Packaging - Atlanta | unresolved | Raw employer-controlled job or government process document tying Altium legal operator and plastics container manufacturing to 6220 Duquesne Drive. [source1](https://www.talent.com/view?id=625134914376697815) |
| SITE-018015 — Lacks Enterprises, Inc. - Kentwood | unresolved | Raw-verifiable site-specific company certificate or permit tying 5801 Kraft Ave SE to its current legal operator, molding process/material, physical function and operation date. [source1](https://lacksenterprises.com/wp-content/uploads/2025/02/P-C-Lacks-Supplier-Manualv.250203.pdf) |
| SITE-019001 — Pella Corporation - Macomb | agreement | Fresh Pella-authored professional development account explicitly places vinyl-door production work in Macomb. Chamber member profile gives Pella Corporation manufacturing at exact 111 Pella Place (Pl.), Macomb IL 61455. Convergent city-level process and exact establishment listing independently support site manufacturing/polymer identity; no contradiction established. Current pages do not make frozen unknown status erroneous. [source1](https://pressroom.pella.com/pella-celebrates-its-next-generation-of-leaders/); [source2](https://business.macombareachamber.com/list/member/pella-corporation-374) |
| SITE-019002 — Pactiv Corporation - Manteno | unresolved | Current employer-controlled or regulator process document tying the held address and Pactiv operator to polymer manufacturing, and an authoritative situs explanation of Street/Road. [source1](https://www.oshrc.gov/wp-content/uploads/08-1554.pdf); [source2](https://apps.dot.illinois.gov/eplan/desenv/082214/66429-015/66429-015.pdf) |
| SITE-019009 — Storopack, Inc. - Hillside | unresolved | Site-specific permit, company process statement or plant certificate establishing operator, physical function and polymer work at 320 Craig; authoritative situs source resolving Craig Place versus Craig Road. [source1](https://www.storopack.us/company/about-us/storopack-worldwide/) |
| SITE-019011 — Reynolds Consumer Products Inc. - Jacksonville | unresolved | Raw employer-controlled or government source tying 2226 E Morton Avenue Reynolds plant to plastics film/bag manufacturing and operator identity. [source1](https://www.myjournalcourier.com/news/article/jacksonville-reynolds-solar-project-19961647.php) |

New confirmed errors, if any, are referrals to the controller/L11 correction owner; this branch changes **no canonical data**. A real office/warehouse misclassified as a plant is a field error under SCHEMA4.5/5.3; closure and operator/no-establishment errors use the explicit audit9 taxonomy and require dated deciding facts. Source availability failures and uncorroborated postal variants never become errors by themselves. A separate post-lock Heritage temporal clarification preserves the verdict: the EIR cover says May 2021, so its manufacturing observation is historical, not current liveness. Search metadata suggesting recency was discarded; grade remains unresolved. The original frozen object was not edited. NuSil’s hold is not a penalty for unknown status: the joint-address prototype manufacturer document does not assign actual silicone production/dominant function to the Bakersfield site. WinCup has historical EPS production proof; its frozen active status remains unverified. Separate clarifications preserve those distinctions. The complete frozen records retain all tested-field and temporal qualifications.

Raw source check: **32** admitted quote observations, **0** explicitly unread/discovery holdouts, and **117** route attempts: **81** archived raw bodies verified by byte/hash and **36** unarchived discovery/failed routes explicitly excluded from positive source evidence. House word normalizer reused, every admitted quotation matches the extracted primary/public source and fabricated additions fail. Route unit disclosure: worker A also logs35 discovery searches and one failed web-open without archived bodies; worker B logs51 fetched-source URL attempts and used uncounted search queries only for discovery. The comparable source-request count is82 (maximum9 per site); logged discovery searches are additional and do not prove any finding. Parent known-answer re-fetches reused already counted source URLs. Named follow-up check covers exact16/population preservation, immutable locks, original-report-prefix hash, same50/8-strata computation and deliberate missing/duplicate/post-lock-edit failures. Validator0; no scripts/ changes/fullscripts pytest. Review approvals remain pending; draft until both required families approve.

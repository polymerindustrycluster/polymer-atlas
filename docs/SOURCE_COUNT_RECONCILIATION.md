# Polymer / Plastics / Rubber Industry Database — Source & Count Reconciliation

**Scope of this report:** Scoping only. No master list was built. This report (1) inventories every authoritative / semi-authoritative seed source, (2) reconciles the rumored "~900 polymer companies in Ohio" against definitions, and (3) re-prioritizes sources based on John's actual access (updated 2026-10-28).

**Access update (John, 2026-10-28):**
- ✅ **Has:** Plastics News login — will provide via Secure Vault.
- ❌ **Does NOT have:** paid Data Axle, paid D&B Hoovers.
- ✅ **Workaround verified (see §4):** Data Axle Reference Solutions is free with a Cleveland Public Library or Cuyahoga County Public Library card. Akron-Summit County Public Library does **not** carry Data Axle — it carries a competitor, AtoZ Databases.

**Date of research:** 2026-10-28. Every count below carries a source URL. Anything not verified is labeled **NOT VERIFIED** — see §7 for the full list.

---

## 1. Executive answer — the "~900" rumor, reconciled

The rumor is **real, but it is an establishment count for one NAICS code, not a company count for "the polymer industry."**

- **890 establishments** — Ohio, NAICS 326 (Plastics & Rubber Products Manufacturing) only, 2023, Ohio QCEW published by Ohio Dept. of Job & Family Services: 706 plastics product (3261) + 184 rubber product (3262), employing 56,186 people.
  Source: https://prod-ohlmi.mt.gov/_docs/QCEW/annual_n/2023_RS20311N.pdf
- **996 "companies"** — Greater Akron Chamber / Polymer Industry Cluster Strategic Framework figure for Ohio's polymer industry: "more than 72,000 employees in 996 companies contributing $40+ billion to the Ohio GDP," with 516 of the companies in 16 Northeast Ohio counties and 174 in Greater Akron employing 10,743. The framework does **not** publish its NAICS definition or firm-vs-establishment method, so 996 cannot be reproduced from public data — treat as a cluster claim, not a census.
  Source: https://greaterakronchamber.org/wp-content/uploads/2023/07/Polymer-Industry-Cluster-Strategic-Framework-final.pdf
- **616 companies** — the only fully documented, manually cleaned company count found: Shale Crescent USA / JobsOhio onshoring study. It screened **over 1,100 Ohio companies** returned by a DatabaseUSA (Data Axle's predecessor product) pull on a **single 6-digit code, NAICS 326199**, then manually removed defunct firms and firms "only in allied areas such as compounding or plastic resin distribution," leaving **616 Ohio manufacturers** that "met the criteria" for deeper study of processing type, market segment, and resin/feedstock.
  Sources: https://shalecrescentusa.com/wp-content/uploads/2022/12/Full-Study-SCUSA-Plastic-Product-Manufacturing-Over-China-Based-Operations-Final.pdf and https://jobs-ohio.com/files/reports/full_study_-_scusa_plastic_product_manufacturing_over_china-based_operations_-_final.pdf

**The single most important illustration in this report:** a raw commercial-database pull for *one sub-code* (326199) returned **1,100+** Ohio "companies" — more than the official establishment total for *all* of NAICS 326 (890). After human cleaning, only ~616 survived, and that 616 *excludes* compounders and distributors by design. Raw pull ≠ reality, in either direction.

### Defensible ranges by definition (Ohio)

| Ring | Definition | Defensible range | Basis |
|---|---|---|---|
| A | NAICS 326 only, **establishments/sites** | **890** (point estimate, 2023) | QCEW, verified |
| B | NAICS 326 only, **parent companies/firms** | **~700–850** (estimate, NOT VERIFIED) | Firms < establishments; exact Ohio firm count is published in the 2022 Economic Census Geographic Area Statistics but was not pulled in this pass |
| C | Verified plastics **product manufacturers** (cleaned, companies) | **616** (2022, narrow screen) | Shale Crescent, verified methodology |
| D | 326 + resin/synthetic rubber/fibers (3252 group) establishments | **1,005** (890 + 115, arithmetic on QCEW) | QCEW, verified inputs |
| E | D + custom compounding (325991) | **~1,035–1,160** | Compounding sits inside the 153-establishment 3259 group in QCEW's published 4-digit table; 6-digit pull required to isolate it — NOT VERIFIED |
| F | E + plastics distributors + plastics/rubber machinery + mold/tool makers (Ohio sites) | **~1,200–1,450** | IBISWorld Ohio subset counts (109 wholesaling businesses; 32 machinery locations) + national PLASTICS mold/machinery counts pro-rated — commercial estimates, see §6 |
| G | Full ecosystem: F + captive/in-house plastics operations, recyclers, R&D/testing, universities, nonprofits, associations, startups with no polymer primary NAICS | **~1,800–2,800 organizations** (low confidence) | Anchored only by GAC's broad Tech Hub claim of "more than 2,800 companies" / 140,000 employees — methodology NOT VERIFIED |

**Bottom line for John:** If PIC quotes one number publicly, quote it with its definition attached: *"~890 plastics and rubber manufacturing establishments in Ohio (NAICS 326, QCEW 2023), within a wider polymer ecosystem of roughly 1,200–2,800 organizations depending on how much of the supply chain you count."* The unqualified "~900 companies" is defensible only as Ring A mislabeled as companies.

---

## 2. The definitional traps (read before building anything)

1. **Establishments ≠ companies ≠ sites in a commercial directory.** QCEW/CBP count *establishments* (physical locations with paid employees). A 3-plant Ohio molder is 3 establishments, 1 company. Data Axle/D&B list *both* headquarters and branch locations as records. Plastics News lists *companies* in its rankings but ships a *separate plants file*. Any merge that doesn't carry a unit-type field will double-count by 15–40%.
2. **Primary NAICS is assigned differently by every source.** Census/BLS assign one primary NAICS per establishment from payroll/product data. Commercial databases accept **self-assigned, multiple** NAICS codes — Shale Crescent explicitly captured firms listing 326199 "down to the sixth level" (i.e., as a secondary code), which is why one sub-code yielded 1,100+ records in a state with only 890 NAICS-326 establishments total.
3. **NAICS 326 is not "the polymer industry."** Resin and synthetic rubber manufacturing live in **325211 / 325212**; custom compounding — the heart of Akron-area firms like Americhem / GEON-type businesses — lives in **325991**, inside Chemical Manufacturing, *not* 326. A 326-only list systematically deletes the upstream half of Polymer Valley.
4. **Captive production is invisible.** PLASTICS (Plastics Industry Association) counts 14,983 U.S. plastics manufacturing establishments and 817,100 employees under the government definition for 2025, but **1,049,200 employees when captive plastic-products production** (e.g., a plastics shop inside an auto or bottling plant classified under another NAICS) **is included** — a ~28% employment uplift from operations no NAICS-326 list will ever see.
   Source: https://www.plasticsindustry.org/wp-content/uploads/2026/09/Size-Impact-Executive-Summary-2026.pdf
5. **Cluster numbers are advocacy numbers.** Published Ohio totals found in this pass: 616 (cleaned, narrow), 890 (official, 326 establishments), 996 (GAC cluster), 1,100+ (raw pull; also a 1996 processor count and an APEG-era claim), ~1,150 (PolymerOhio-era, "more than 1,150 companies and a workforce greater than 80,000," 2013 — https://www.azom.com/news.aspx?newsID=28286), 1,550 (1996: "some 1,100 plastics product processors" + "about 450 industry-related companies" — https://www.plasticsnews.com/article/19960422/OPINION02/304229973/plastics-mean-bucks-to-buckeyes/), ~2,400 "polymer related companies" in **Northeast Ohio alone** (University of Akron, no methodology published — https://www.uakron.edu/polymer/research/), and 2,800+ (GAC Tech Hub designation narrative, broadest definition — https://www.eda.gov/sites/default/files/2023-11/Sustainable_Polymers_Tech_Hub.pdf). The spread is definition, not error — but none of the cluster figures publishes a reproducible method.
6. **Employment cross-check exposes definition creep.** NAICS 326 Ohio employment (QCEW 2023): 56,186. PLASTICS' broader "plastics industry" Ohio employment: 78,600 (2024) / 77,500 (2025), ranked #2 among states behind Texas. Sources: https://www.plasticsindustry.org/wp-content/uploads/2025/08/Size-Impact-Executive-Summary-2025.pdf and https://www.plasticsindustry.org/blog/manufacturing-day-2026-plastics-manufacturing/ — Same state, same industry label, ~40% gap, purely from including resin, wholesale, machinery, and molds in PLASTICS' definition.

---

## 3. Source table — every seed source assessed

Legend — **Unit:** E = establishments, F = firms/companies, S = sites/locations listed. **Names?** = does it give organization names + addresses (list-building usable) or only aggregates?

| # | Source | What it counts (unit) | Names + addresses? | Cost / access | Freshness | Known blind spots |
|---|---|---|---|---|---|---|
| 1 | **BLS QCEW via Ohio DJFS (Ohio LMI)** | Employer establishments by primary NAICS, state/county (E) | **No** — aggregates only; underlying employer microdata is confidential | Free, public | Annual state table (2023 retrieved); QCEW quarterly nationally | No firms, no names; primary-NAICS only; 4-digit published table lumps 325991 into 3259; excludes nonemployer businesses. **Use as the count truth-set, not a list.** https://prod-ohlmi.mt.gov/_docs/QCEW/annual_n/2023_RS20311N.pdf |
| 2 | **Census County Business Patterns (CBP)** | Establishments with paid employees by NAICS, down to ZIP (E) | **No** — aggregates only | Free, public; CSV/API | Latest = **2023**, released June 26, 2025; Census states no planned 2024 release date yet https://www.census.gov/newsroom/press-releases/2025/2023-county-business-patterns.html ; datasets https://www.census.gov/data/datasets/2023/econ/cbp/2023-cbp.html | Same NAICS/captive limits as QCEW; noise-infusion changes pending. **Use with QCEW to validate every other source's counts by NAICS × county.** |
| 3 | **Census Economic Census 2022 — Geographic Area Statistics** | **Firms AND establishments**, sales, payroll by state × 6-digit NAICS (F + E) | No — aggregates only | Free, public | 2022; Geographic Area Statistics released Dec 5, 2024 https://Www.Census.gov/newsroom/press-releases/2024/2022-economic-census-data.html ; schedule https://www.census.gov/programs-surveys/economic-census/year/2022/news-updates/releases.html | 5-year cadence; aggregates only. **This is the source that resolves the firms-vs-establishments gap (Ring B) — pull it in the build phase.** |
| 4 | **Census Annual Survey of Manufactures → now Annual Integrated Economic Survey (AIES)** | Sample of ~50,000 manufacturing establishments nationally; shipments, materials, products (E) | No — aggregates only | Free, public | ASM folded into AIES starting with 2023 data (March 2024) https://library.morgan.edu/c.php?g=885876&p=10764694 ; ASM description https://www.test.census.gov/programs-surveys/asm/about.html | Sample, not a frame; state × industry detail thinner than CBP. Useful for shipments/product (NAPCS) validation, not list-building. |
| 5 | **Plastics News Data Center (Crain)** — ⭐ top spine, John has login | Surveyed North American **processor companies + their plants** (F + S) | **Yes** — HQ address, parent, top official, plant addresses (see §4) | Paid; John has a login (tier TBD — critical, see §4). Public tiers: $189/yr view-only; **$499/yr All Access** with Excel downloads https://arcxp-prod.plasticsnews.com/subscribe/ | Rankings republished annually through the year; Data Center shows 2025 lists https://www.plasticsnews.com/rankings/rotomolders/20170731/businessdata/429/Rotational%20Molders | Survey-response bias: firms that don't respond drop off published lists (steward notes the active database holds roughly twice the published injection-molder count); plastics-centric — rubber (3262) covered only tangentially; no distributors/OEMs; Ohio subset count requires login to filter — NOT VERIFIED here |
| 6 | **Data Axle Reference Solutions** (formerly ReferenceUSA) — via **library** (see §4) | U.S. business **locations** with primary + secondary NAICS/SIC (S/F mixed) | **Yes** — name, address, phone, executives, employees, sales, NAICS/SIC, HQ/branch flag | **No paid access (John). Free via CPL / CCPL library card** (§4). Direct institutional subscription is the paid alternative | Vendor-claimed weekly updates; library descriptions cite 11M–94M+ business records depending on module/version — counts vary by source consulted | Self-assigned multi-NAICS inflation (the 1,100-for-one-code problem); duplicates, defunct listings, branch/HQ double-counts; **250-record download cap per search in library versions** — plan batching by NAICS × county |
| 7 | **D&B Hoovers (Dun & Bradstreet)** | Companies + locations with D-U-N-S corporate family linkage (F + S) | Yes — incl. corporate family trees, the best parent/subsidiary resolution of any source here | **Paid — John does NOT have it. Unavailable for this project unless purchased or accessed via a university library** (e.g., Hoovers guides exist at university libraries https://libraries.emory.edu/business/research-learning/databases/hoovers-dun-bradstreet) | Continuous | Same self-reported classification issues; family-tree data is its unique value. **Deferred — do not plan around it.** |
| 8 | **Ohio Secretary of State — Business Search** | Every registered Ohio legal entity: name, entity number, type, status, filing date, statutory agent, city/county (F — legal entities) | **Yes, but thin** — legal name + agent address only; **no NAICS, no industry, no plant address, no employees** | Free, public, no account https://businesssearch.ohiosos.gov/ (portal described at https://entityfinder.us/ohio/) | Real-time filings | Cannot be filtered by industry at all — usable only as a **verification/existence layer** (is this org real, active, what's its legal name?) and for new-formation monitoring via name-keyword searches. Includes every defunct/dead entity unless status-filtered. Never a primary seed. |
| 9 | **Thomasnet** | Self-listed North American suppliers by product/service category (S) | **Yes** — company, city, employee/revenue bands, capabilities, certifications | Free to search; suppliers pay for placement (typically est. $7,000–$10,000/yr; free basic profile exists) https://www.webfx.com/blog/manufacturing/is-thomasnet-worth-it/ | Continuous, self-maintained | Category counts ≠ NAICS counts (e.g., Thomas reports **308 Ohio plastic fabrication suppliers** within 4,100+ nationally — a capability category, not an industry https://www.thomasnet.com/articles/top-suppliers/plastic-fabrication-companies-manufacturers/); paid-placement ordering; firms serving Ohio vs located in Ohio are mixed in regional pages; stale profiles persist. **Good for capability/process tags and gap-filling, bad for counts.** |
| 10 | **PLASTICS (Plastics Industry Association)** | Modeled national/state industry totals (establishments, employment, shipments) using a multi-NAICS definition incl. resin, wholesale, machinery, molds; member directory / Marketplace separately | Aggregates in Size & Impact; member names via association channels (membership-gated) | Size & Impact executive summary free; full data/member access membership-gated | Annual; 2025 report (2024 data) and 2026 report (2025 data) both retrieved | Definition is broader than NAICS 326 by design (see trap #6); no public Ohio company list. **Use for national framing and Ohio employment cross-checks.** https://www.plasticsindustry.org/wp-content/uploads/2025/08/Size-Impact-Executive-Summary-2025.pdf |
| 11 | **Ohio Manufacturers' Association (OMA)** | Ohio manufacturer members — "more than 1,300 manufacturers" statewide (all industries) https://en.wikipedia.org/wiki/Ohio_Manufacturers_Association | Member directories are behind member login ("Log into My OMA to access directories of OMA members") https://www.ohiomfg.com/services/information-services/ | Membership organization | Continuous | Members only (self-selected subset); all-manufacturing, not polymer-filterable publicly. **Partnership/ask route, not a scrape route.** |
| 12 | **PolymerOhio (historical) / Polymer Industry Cluster (PIC, Greater Akron Chamber)** | Cluster claims: PolymerOhio-era ~1,150 Ohio companies; PIC framework 996 companies (516 NE Ohio) | PIC partner/member lists exist through the cluster (John is inside this org — internal lists are a legitimate seed) | Internal / partnership | PolymerOhio-era figure dates to ~2013 https://www.azom.com/news.aspx?newsID=28286 ; PIC framework 2023 https://greaterakronchamber.org/wp-content/uploads/2023/07/Polymer-Industry-Cluster-Strategic-Framework-final.pdf | No published methodology for either figure; PolymerOhio as a standalone org/directory could not be verified as currently maintained — **NOT VERIFIED**. PIC's own CRM/partner roster is likely John's single highest-precision NE Ohio seed and costs nothing. |
| 13 | **JobsOhio / Team NEO / Shale Crescent USA** | Shale Crescent study database: 616 cleaned Ohio plastics manufacturers with processing type, market segment, resin, size, location, contacts (F) | **Yes — a real list exists inside that study** (built from DatabaseUSA + Plastics News + IHS Markit cross-checks) | Study PDF free; underlying company-level dataset is **not** published — would require an ask to Shale Crescent USA / JobsOhio | 2022 study | Screen was 326199-led and *excluded* compounders/distributors by design; 4 years stale. **Highest-value "ask" in this report: request the 616-company appendix/dataset.** Exec summary: https://jobs-ohio.com/files/reports/plastics-exec-summary-brochure-pes1122.pdf |
| 14 | **MAGNET (Manufacturing Advocacy & Growth Network)** | NE Ohio MEP center; partner/client network (org list, not an industry census) https://www.manufacturingsuccess.org/regional-partners | Partner network public; client list not public | Free (public pages) / partnership | Continuous | NE Ohio only; clients skew small/mid manufacturers who sought help. Seed for services/ecosystem layer, not core counts. |
| 15 | **BioOhio** | Ohio bioscience member org — captures the polymer-adjacent medical-device / biomaterials slice | Member directory exists via BioOhio (membership org) | Membership / partnership | Continuous | Only the life-sciences slice; most polymer firms absent. Use for the medical-polymer overlap only. (No public member count verified in this pass.) |
| 16 | **Rubber Division, ACS** | Akron-based rubber industry society: member companies, exhibitors (Int'l Elastomer Conference), sponsors | Exhibitor/sponsor lists are public around events; full member directory is member-gated | Membership / event lists free | Annual conference cycle | **This is the main structured rubber-side source** — Plastics News does not substitute for it (see §4.4). Headquartered in Akron; highest rubber relevance per record of any association here. |
| 17 | **SPE (Society of Plastics Engineers) — Akron & Cleveland sections** | Individual members + section sponsors/officers employed at regional firms (people, not companies) | Section newsletters name officers' employers (e.g., Goodyear, Parker Hannifin, University of Akron) https://www.4spe.org/files/resource_library_files/OTL/Chapter/S42/s42newsletter202203.pdf | Free (public newsletters) | Monthly-ish | A people-network signal, not a company census. Use to identify firms + contacts for validation, never for counts. |
| 18 | **Universities & research orgs** | Polymer programs/centers: University of Akron (School of Polymer Science & Polymer Engineering), Case Western Reserve (Macromolecular Science & Engineering), Kent State (Advanced Materials / Liquid Crystal Institute), Ohio State, Cincinnati, Toledo, Dayton + centers (National Polymer Innovation Center, America Makes-adjacent, OAI, etc.) | Public program/center pages; the five Ohio Centers of Excellence in Enabling Technologies (UA, Kent State, Cincinnati, Ohio State, CWRU) are documented at https://www.uakron.edu/im/online-newsroom/news_details.dot?newsId=1043845 | Free | Continuous | Small counts (~15–30 orgs) but high membership value; must be hand-curated — no NAICS will find them (they sit in 611310 / 541715). |
| 19 | **IBISWorld (state industry reports)** | Commercial modeled counts by industry × state (F/E mixed) | Aggregates in report summaries; company lists are paid-report content | Paid reports; **note: Akron-Summit County Public Library offers IBISWorld in-library only** https://www.akronlibrary.org/locations/main-library/sbn | 2026 editions retrieved | Modeled, not enumerated. Useful subset anchors: Ohio plastics wholesaling **109 businesses** https://www.ibisworld.com/united-states/industry/ohio/plastics-wholesaling/35123/ ; Ohio plastics & rubber machinery mfg **32 locations** https://www.ibisworld.com/united-states/industry/ohio/plastics-rubber-machinery-manufacturing/35022/ ; Ohio misc. plastic products (326199-like) **347 businesses** https://www.ibisworld.com/united-states/industry/ohio/plastic-products-miscellaneous-manufacturing/12870/ |
| 20 | **Rubber News / Tire Business (Crain Global Polymer Group)** | Rubber & tire industry news, Global Tire Report rankings, special reports (custom mixing, machinery, molded goods) | News + annual rankings; **no downloadable company data-center equivalent to Plastics News' was found** | **Separate Crain subscriptions — NOT VERIFIED as included in a Plastics News login** (see §4.4) | Continuous; Global Tire Report annual https://crain-platform-rubbernews-prod.s3.amazonaws.com/data-protected/RPN-2022-Global%20tire%20rankings.pdf | Tire-heavy; rankings are company-HQ/global, not Ohio plant lists. Treat as a monitoring feed, not a spine. |

---

## 4. Deep dive — Plastics News (John's login) and the Data Axle library workaround

### 4.1 What a Plastics News login actually unlocks — the tier is everything

Plastics News sells three tiers (prices as published on its subscribe page):
- **Basic Digital — $189/yr ($18/mo)** and **Premium Print+Digital — $189/yr ($20/mo):** articles, resin pricing charts, and **view-only** access to rankings/list data.
- **All Access — $499/yr:** everything above **plus downloadable MS Excel files** of the full rankings and lists, downloadable resin pricing, the **Directory of Compounders**, and the global list of plastics-related industry associations.
  Source: https://arcxp-prod.plasticsnews.com/subscribe/

Plastics News states the rule explicitly on its ranking pages: *"Plastics News paid subscribers can VIEW this list online. DOWNLOADS require an All Access subscription upgrade."*
Source: https://prod.plasticsnews.com/businessdata/438/Injection Molders

> ⚠️ **First action when the vault credential arrives:** determine John's tier. If it is Basic/Premium, the Data Center is a *viewing* tool only — building from it means manual/transcribed extraction (slow, and check Crain's terms of use), or a $499 All Access upgrade decision. If it is All Access, Plastics News becomes the fastest path to a structured, plant-level processor spine in the entire project. This was **NOT VERIFIED** — it cannot be until the login is used.

### 4.2 Data Center inventory (verified from the public Data Center index)

The Data Center landing page reports **2,041 companies, 2,517 people, 21 industry lists** (page crawled Nov 2025 for the 2025 cycle).
Source: https://www.plasticsnews.com/rankings/rotomolders/20170731/businessdata/429/Rotational%20Molders

Lists shown for the current cycle:
- **2025:** Mold/Tool Makers · Blow Molders · Film & Sheet Manufacturers · Rotational Molders · Pipe/Profile/Tubing Extruders · Plastic Lumber Manufacturers · Injection Molders · LSR Processors · Plastics Recyclers/Brokers · Thermoformers · Capital Expenditures Ranking
- **2024:** Compounders · Associations · Top Sheet Manufacturers · Top Film Manufacturers · Capital Expenditures
- **Rankings Data Time Machine (2019 snapshots):** Blow Molders · Film & Sheet · Rotational Molders · Pipe/Profile/Tubing · Injection Molders · Thermoformers — useful for churn/birth-death analysis
- CEO Compensation (2021)

Coverage mapping to PIC's needs: injection molding ✓ · extrusion (pipe/profile/tubing + film & sheet) ✓ · blow molding ✓ · thermoforming ✓ · rotational molding ✓ · recycling/brokers ✓ · **compounders ✓ (directory, 2024)** · mold/tool makers ✓ · LSR (liquid silicone rubber) processors ✓ — the one explicitly rubber-adjacent list. **Missing:** rubber product manufacturing generally (tires, belting, hose, molded rubber goods), resin producers as a list, distributors, machinery builders as a list, OEMs, universities/nonprofits.

### 4.3 Fields — worked example: North American Injection Molders

The ranking's own detail page specifies: **607 companies, 599 people, 1,231 plants** (North America, 2024 sales survey), with fields:
- Company name and **headquarters address**; **parent company**
- Ranked sales (current + previous year) and total corporate sales
- Employee count; number of presses; plant count
- **Top official name and title**
- **Related plant location addresses** — shipped as a *separate Excel file* (operator / address / phone)
- **Contacts** — name/title/company in a *separate Excel contacts file*
- Materials; processes; secondary services; end markets
Source: https://prod.plasticsnews.com/businessdata/438/Injection Molders

The All Access download includes *more* than the web display: "sales breakouts, processes used, secondary services, number of lines or presses, materials volumes and each ranking's related plant location details."
Source: https://prod.plasticsnews.com/all-things-data/plastics-news-all-access-subscription-covers-downloads-ranking-data-files

**Database depth vs published lists:** The rankings steward reports having gathered information on **more than 6,200 companies** historically, with **2,154 companies** having fallen off the active list, and 161 processors added in 2021 of which 126 made the published lists.
Source: https://www.plasticsnews.com/blog/more-data-now-available-your-desk/
A separate ranking commentary notes for injection molders that ~590 companies made the list while "our active database has twice as many more who didn't respond" — i.e., **published lists understate even Plastics News' own known universe by roughly half for non-respondents.** Budget for that gap: Plastics News is a spine, not a census.

**Ohio coverage: NOT VERIFIED.** No public page states an Ohio count per ranking; the Data Center must be filtered by state after login. Planning estimate only (do not quote): Ohio holds ~7–8% of U.S. plastics employment (77,500 of ~1,066,500 in 2025, per PLASTICS), so a naive pro-rate of 2,041 Data Center companies suggests **~140–165 Ohio-HQ companies across all lists before de-duplication**, plus additional Ohio *plants* of out-of-state-HQ firms in the plants files — the plants files are arguably the more valuable Ohio asset. Both numbers must be replaced by the real filter result in the build phase.

**Terms caution:** Excel downloads are a licensed subscriber benefit. Before any automated extraction or bulk reuse in a PIC database, check the subscription terms for data-use/redistribution limits — flagged as an open item, **NOT VERIFIED** in this pass.

### 4.4 Rubber News — is it included in the Plastics News login?

**No evidence found that it is.** Rubber News (formerly Rubber & Plastics News) and Tire Business are *separate* Crain Global Polymer Group publications with their own subscriptions. Rubber News publishes the annual Global Tire Report company rankings and special reports (custom mixing, rubber machinery, molded goods, automotive parts, belting, polyurethanes), but **no downloadable, Plastics-News-style Data Center for rubber companies was found** in this pass.
Sources: https://media-index.kochava.com/ad_partners/rubbernews-com and https://crain-platform-rubbernews-prod.s3.amazonaws.com/data-protected/RPN-2022-Global%20tire%20rankings.pdf

**Implication:** John's login closes most of the *plastics processor* gap and part of compounding/tooling/recycling. The **rubber side (NAICS 3262: 184 Ohio establishments, QCEW) remains the thinnest-covered segment** and will need Rubber Division ACS exhibitor/member channels, Rubber News headlines as a monitoring feed (separate sub decision), and Data Axle NAICS 3262 pulls via the library route.

### 4.5 Data Axle via public libraries — VERIFIED, with one correction

**Cleveland Public Library — VERIFIED.** CPL's database list includes **"Data Axle (formerly Reference USA)" — CPL Cardholders only** — described as "Directory information for 11 million U.S. businesses and 120 million U.S. households. Search for businesses by SIC code, sales volume number of employees and more."
Sources: https://cpl.org/databases/ and https://cpl.org/topic/business-and-investing/

**Cuyahoga County Public Library — VERIFIED.** CCPL's Resources A–Z lists **"Reference Solutions — Business & consumer research"** (Reference Solutions is Data Axle's product name) with access + tutorial links.
Sources: https://cuyahogalibrary.org/research-discover/resources-a-z/reference-solutions and http://researchguides.csuohio.edu/c.php?g=922116&p=6646112

**Akron-Summit County Public Library — NOT Data Axle (correction to the assumption in the task).** ASCPL's Small Business & Nonprofit Resource Center and its Databases-by-Title list offer **AtoZ Databases** ("financial information on over 30 million U.S. businesses & executives") — a *competing* directory product — plus IBISWorld (in Main Library only), Mergent Intellect, and SizeUp. No Data Axle / Reference Solutions listing was found on akronlibrary.org.
Sources: https://www.akronlibrary.org/locations/main-library/sbn , https://www.akronlibrary.org/research/databases-by-title , http://researchguides.csuohio.edu/c.php?g=922116&p=6646112
*AtoZ is still useful as a second, independent commercial pull for cross-validation — different vendor, different errors.*

**Also nearby:** Medina County District Library and Wayne County Public Library list Data Axle Reference Solutions as well (same 11M-business description; Wayne County's page cites a larger 60M figure — vendor module counts vary by library page, treat all such totals as marketing numbers).
Sources: https://www.mcdl.info/dbases?field_category_tid_selective=35 and https://wcpl.info/findinfo/databases

**Practical constraints of the library route (verified from library tutorials/guides):**
- **Download cap: 250 records per search/download** in library versions of Reference Solutions — an Ohio multi-NAICS pull (~1,100+ raw records for 326199 alone, per Shale Crescent) must be batched by NAICS × county/ZIP and reassembled. Sources: https://library.bu.edu/dataaxle/downloading-company-lists and https://guides.lib.unc.edu/geog697/data
- Access is cardholder-authenticated remote access at CPL/CCPL (not in-library-only, per their listings) — but **bulk/commercial reuse terms are the library license's, not John's**; keep use to research/list-building scale and expect the 250-cap to enforce it.
- This is the *same underlying data* Shale Crescent used (DatabaseUSA was Data Axle's business-list product line) — so the library pull reproduces their starting point for free, including its known inflation problem.

**D&B Hoovers via libraries:** University libraries commonly carry Hoovers (e.g., Emory's guide above), but no public-library (CPL/CCPL/ASCPL) Hoovers access was verified, and university access requires affiliation. **Treat D&B as unavailable**, full stop.

---

## 5. Count-reconciliation table — how every published Ohio number is produced

| Published figure | What it actually is | Unit | Definition / screen | Year | Source |
|---|---|---|---|---|---|
| **616** | Cleaned plastics manufacturers studied in depth | Companies | DatabaseUSA pull on NAICS 326199 (any position) → manual removal of defunct + compounding/distribution-only firms | 2022 | https://shalecrescentusa.com/wp-content/uploads/2022/12/Full-Study-SCUSA-Plastic-Product-Manufacturing-Over-China-Based-Operations-Final.pdf |
| **706** | Plastics product manufacturing (3261) | Establishments | Primary NAICS, employer establishments, Ohio QCEW | 2023 | https://prod-ohlmi.mt.gov/_docs/QCEW/annual_n/2023_RS20311N.pdf |
| **184** | Rubber product manufacturing (3262) | Establishments | Primary NAICS, Ohio QCEW | 2023 | (same QCEW table) |
| **890** | **All of NAICS 326 (706 + 184)** — the true source of the "~900" rumor | Establishments | Primary NAICS, Ohio QCEW; 56,186 employees | 2023 | (same QCEW table) |
| **996** | Polymer industry cluster total | "Companies" (unit not documented) | GAC/PIC cluster definition, incl. 516 in 16 NE Ohio counties; 72,000 employees; $40B+ GDP | ~2023 | https://greaterakronchamber.org/wp-content/uploads/2023/07/Polymer-Industry-Cluster-Strategic-Framework-final.pdf |
| **1,005** | 326 + resin/synthetic rubber/fibers group (3252 = 115 est.) | Establishments | Arithmetic on QCEW published groups | 2023 | (same QCEW table) |
| **1,100+** | Raw DatabaseUSA returns for **326199 alone** before cleaning | Database records | Self-assigned NAICS in any position; includes defunct, branches, allied firms | 2022 | Shale Crescent full study (above) |
| **~1,150** | PolymerOhio-era industry total | Companies | Cluster definition incl. resins/composites/advanced materials; 80,000+ workers; establishments in 76 of 88 counties | ~2013 | https://www.azom.com/news.aspx?newsID=28286 |
| **1,550** | 1,100 processors + ~450 related companies (compounders, mold makers, resin producers, machinery, distributors…) | Companies + related | Governor's Ohio Plastics Summit statement | 1996 | https://www.plasticsnews.com/article/19960422/OPINION02/304229973/plastics-mean-bucks-to-buckeyes/ |
| **~2,400** | "Polymer related companies" in **Northeast Ohio** | Companies (claimed) | No methodology published | undated (current UA page) | https://www.uakron.edu/polymer/research/ |
| **2,800+** | Broadest cluster definition incl. secondary/supporting businesses | Companies | GAC Tech Hub designation narrative; paired with 140,000 employees | 2023 | https://www.eda.gov/sites/default/files/2023-11/Sustainable_Polymers_Tech_Hub.pdf |
| 42,000 jobs / 800+ est. | NE Ohio secondary/supporting polymer economy | Establishments | GAC/PIC framework (separate from its 996 core figure) | ~2023 | PIC framework (above) |
| 77,500–78,600 | Ohio "plastics industry" employment under PLASTICS' multi-sector definition (not a company count) | Employees | PLASTICS Size & Impact (resin + products + wholesale + machinery + molds) | 2024–2025 | https://www.plasticsindustry.org/wp-content/uploads/2025/08/Size-Impact-Executive-Summary-2025.pdf |

### Worked ring arithmetic (all QCEW 2023 Ohio unless noted)

- **Ring A (326):** 706 + 184 = **890 establishments**, 56,186 employees.
- **Ring D (+3252 group):** 890 + 115 = **1,005 establishments** (3252 group = resin, synthetic rubber, and artificial/synthetic fibers/filaments; 5,427 employees). Note: the fibers component (325220) is only partly polymer-cluster-relevant — a 6-digit pull would trim this slightly.
- **Ring E (+compounding):** 325991 sits in QCEW's published "Other Chemical Product and Preparation Manufacturing" group = **153 establishments total** for the whole group (which also includes photographic, explosives, and misc. chemical firms). Compounding is a subset — adding the full group gives a hard ceiling of 1,158; the true increment is smaller. **Isolating 325991 requires the 6-digit QCEW/CBP files — do this in the build phase, not from the published PDF.**
- **Ring F (+distribution/machinery/tooling):** IBISWorld Ohio anchors — plastics wholesaling **109 businesses**, plastics & rubber machinery **32 locations**. National cross-check: PLASTICS counts 394 U.S. plastics-machinery establishments and 503 mold-making establishments nationally (2025); Ohio's ~7% plastics share pro-rates to roughly ~28 machinery and ~37 mold establishments, consistent with the IBISWorld machinery figure. These are *estimates layered on estimates* — hence the range, not a point.
- **Ring G (+everything else):** No NAICS-based method reaches captive shops, recyclers classified in waste/wholesale codes (562920 / 423930), testing labs (541380), R&D firms (541714/541715), universities (611310), or associations (813910). This ring is enumerable only by merging directories (Plastics News recyclers list, Thomasnet categories, association rosters, PIC's own partner list) — which is exactly why published totals here (2,400 / 2,800) come with no reproducible method.

---

## 6. What scales nationally later

Every spine above is national by construction — the Ohio build is a filtered view, not a separate system:

- **CBP / QCEW / Economic Census:** identical pulls for all states; ZIP-level CBP enables the national plant map. Free.
- **Plastics News Data Center:** already North American; Ohio is a state filter on companies *and* a state filter on the separate plants files (the plants filter is how you catch Ohio sites of Michigan/Texas-HQ firms). All Access tier decision made once, nationally.
- **Data Axle (library or paid):** national database; the 250-record batching workflow built for Ohio generalizes by state.
- **Thomasnet:** national categories; same capability-taxonomy approach.
- **PLASTICS Size & Impact:** publishes all-state employment tables — the national cross-check frame (Texas #1 at 91,600, Ohio #2 at 77,500, Michigan #3 at 69,000 in 2025).
- **Ohio SOS** is the only Ohio-only source; nationally it generalizes to the other 49 SOS registries, all with the same "no industry field" limitation.
- Association layer generalizes via PLASTICS' global associations list (included in All Access) and Plastics News' Associations list (2024).

---

## 7. What could NOT be verified in this pass (explicit)

1. **John's Plastics News tier** (view-only vs All Access downloads) — requires using the vault login. This is the single highest-leverage unknown.
2. **Plastics News Ohio counts** per ranking / de-duplicated — requires Data Center state filtering after login. The ~140–165 figure in §4.3 is a pro-rated planning estimate only.
3. **Census CBP Ohio NAICS-326 establishment count** — CBP 2023 files exist (state file, 10.9 MB CSV), but the exact Ohio 326 cell was not extracted in this pass; QCEW's 890 is used as the anchor instead. CBP and QCEW typically differ by a few percent (different reference periods/administrative sources).
4. **2022 Economic Census Ohio firm counts** for 326 / 325211 / 325212 / 325991 — published and free, not yet pulled. This resolves Ring B.
5. **6-digit QCEW/CBP counts** for 325211, 325212, 325991, 424610 (plastics merchant wholesalers), 333511 (industrial molds), and the plastics-machinery code — needed to replace Rings E–F ranges with points.
6. **GAC/PIC 996 and 2,800 methodologies**, and UA's 2,400 NE Ohio figure — no published method found for any of them.
7. **PolymerOhio's current status** as a maintained organization/directory — only its ~2013-era figures were verified.
8. **Rubber News bundling** with a Plastics News login — no evidence of bundling found; absence of evidence is noted, not proof. Confirm at login.
9. **Plastics News / Data Axle data-use terms** for building a persistent PIC database from downloads — not reviewed; check before bulk extraction.
10. **BioOhio / Rubber Division / OMA member counts** filterable to polymer firms — directories are member-gated; counts not verified.
11. **ASCPL Data Axle** — affirmatively *not* found (AtoZ Databases instead); if ASCPL added Data Axle after its pages were crawled, that would not be captured here.

---

## 8. Revised priority order — seed spines (given John's actual access)

1. **Plastics News Data Center (John's login — verify tier first).** Richest structured processor data available to this project at zero marginal cost: 2,041 companies / 21 lists nationally, with HQ + parent + top official + separate plants and contacts files, covering injection, extrusion, blow, thermoforming, rotational, film/sheet, LSR, recyclers, compounders, and mold makers. If the tier is view-only, the All Access upgrade ($499/yr list) is the cheapest paid decision in the project.
2. **Free official counts as the validation frame: QCEW (Ohio LMI) + CBP 2023 + 2022 Economic Census.** Not lists — the truth-set every other source gets reconciled against, NAICS × county × unit type. Zero cost, do first in parallel with #1.
3. **Data Axle Reference Solutions via Cleveland Public Library / Cuyahoga County Public Library card.** The only free route to a name-and-address, NAICS-searchable commercial pull — and the same data lineage Shale Crescent started from. Batch around the 250-record download cap by NAICS × county. (Akron route: use ASCPL's AtoZ Databases as an independent second pull instead.)
4. **PIC's own internal rosters + the Shale Crescent 616 dataset (by request).** Highest-precision NE Ohio seeds; the 616 list is already cleaned to a documented definition. Costs an email, not a subscription.
5. **Thomasnet + association/event rosters (Rubber Division ACS exhibitors, SPE sections, OMA, BioOhio, MAGNET) + university/center hand-list.** Gap-filling and ecosystem layer: capabilities/process tags from Thomasnet; the rubber segment, nonprofits, schools, and service firms that no NAICS pull or processor ranking will surface. Ohio SOS runs underneath all of it as the free existence/status verification layer.
- **Deferred (no access):** D&B Hoovers — revisit only if parent-company/family-tree resolution becomes the bottleneck and a purchase or university-library route is approved.

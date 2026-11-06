**REFUTE.** Reviewed CA commit `ace278e`. Three findings prevent approval:

1. **LF-CA-02526 / SITE-014012 — unsupported Ontario B establishment.** Its federal witness is the 2023-07-24 inspection at **1930 South Parco Ave., Ontario**. The quoted own-page text is real, but company-wide. Mission’s [current homepage](https://www.missionplastics.com/) explicitly places manufacturing in **Mexicali, Mexico**, with engineering/support operations in Rancho Cucamonga. **EVD-180102 does not corroborate manufacturing at the Ontario address. Hold pending reconciliation.** This is not a closure determination.

2. **LF-CA-02629 / SITE-014013 — unresolved address discrepancy.** ITA and the created site say **1310 Thurman Rd**. The [company contact page](https://www.ssibio.com/contact-us) and homepage say **1310 Thurman Street**, Lodi. The manufacturing quote is genuine, but the packet does not reconcile the suffix conflict. **Hold until the address is reconciled and documented.**

3. **Four federal-only scope observations are inflated to `supports_B`:** EVD-180089, EVD-180099, EVD-180109 and EVD-180150. These describe NAICS classifications supporting provisional C. The builder copies the selected site tier into each federal claim. **In an isolated reproduction, removing all four own-site scope witnesses still leaves validation passing with all four sites at B.** Classification-only scope evidence should remain C; applicable own evidence can separately support B.

Blind-first inspection: **20/20 rows inspected; 0 missing.** Every supplied row supports provisional C on its face, independently of capabilities, current status or subsequent B promotion.

| Cluster | Inspected identity and physical address | Manufacturing classification | Blind verdict |
|---|---|---|---|
| LF-CA-02526 | Mission Plastics; 1930 South Parco Ave., Ontario | 326199 — other plastics products | C-supported |
| LF-CA-01013 | Advanced Drainage Systems; 1025 Commerce Dr., Madera | 326122 — plastic pipe | C-supported |
| LF-CA-00772 | Dart; 150 **South** Maple St., Corona | 326140 — polystyrene foam products | C-supported |
| LF-CA-01258 | Heritage Bag-Rancho; 12320 Fourth St., Rancho Cucamonga | 326111 — plastics film bags | C-supported |
| LF-CA-02303 | Rubbercraft; 3701 E. Conant St., Long Beach | 326291 — mechanical rubber products | C-supported |
| LF-CA-01400 | American Poly-Foam; 1455 Crocker Ave., Hayward | 326150 — non-polystyrene foam cushions | C-supported |
| LF-CA-00417 | Graham Packaging; 513 South McClure Rd., Modesto | 326160 — plastics bottles | C-supported |
| LF-CA-02120 | Altium Packaging; 22324 Temescal Canyon Rd., Corona | 326160 — plastics bottles | C-supported |
| LF-CA-02901 | MSRS dba VM International; 945 E Church St., Riverside | 326160 — plastics bottles | C-supported |
| LF-CA-00284 | Mercury Plastics; 14849 Salt Lake Ave., City of Industry | 326111 — plastics bags/pouches | C-supported |
| LF-CA-01202 | ATS Products; 2785 Goodrick Ave., Richmond | 326199 — other plastics products | C-supported |
| LF-CA-00489 | Cal Spas; 1462 E Ninth St., Pomona | 326199 — plastics/fiberglass **awnings** | C-supported, caveats |
| LF-CA-00248 | Container Supply; 12571 Western Ave., Garden Grove | 326199 — other plastics products | C-supported |
| LF-CA-02629 | Scientific Specialties; 1310 Thurman **Rd**, Lodi | 326199 — plastics caps/lids | C-supported |
| LF-CA-01076 | Norton Packaging; 5800 S Boyle Ave., Vernon | 326199 — plastics pails | C-supported |
| LF-CA-00077 | Watkins Wellness; 1280 Park Center Dr., Vista | 326191 — plastics/fiberglass hot tubs | C-supported |
| LF-CA-00574 | NuSil; 2343 Pegasus Dr., Bakersfield | 325212 — silicone rubber | C-supported, Ring 2 |
| LF-CA-00174 | Pactiv; 5370 E Home Ave., Fresno | 326140 — polystyrene foam products | C-supported |
| LF-CA-00696 | Jacuzzi/Sundance; 14525 Monte Vista Ave., Chino | 326191 — plastics/fiberglass plumbing fixtures | C-supported |
| LF-CA-00362 | National Diversified Sales; 851 N Harvard Ave., Lindsay | 326122 — plastics pipe/fittings | C-supported |

Cal Spas also carries `reliability=review` and an inconsistent size code; its awnings description does not validate spa capability. VM’s establishment label misspells “Church”; Altium’s company field misspells “Packaging.” These caveats were recorded.

All 20 federal rows matched their repository extracts exactly. All **four raw own-page quotes and hashes matched**; textual presence alone failed to establish Mission’s site applicability. Dart’s North Maple witness was correctly excluded, and Cytec’s latest peripheral 325998 code remains held.

The builder, validator and byte-identical apply replay **passed** on the frozen commit. The committed revision contains **161 evidence rows**, including 13 size-band observations added after the supplied 148-row version. Unknown status, blank county, new-parent C tiers and reserved IDs are not findings.

[Full record-level audit and reproduction details](/tmp/council-codex-cwd.CR8CqW/review-report.md).

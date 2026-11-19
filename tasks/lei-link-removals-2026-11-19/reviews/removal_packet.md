Refute this data change for the Polymer Atlas (public dataset of US polymer organizations). Do not edit anything.
Each row proposes REMOVING one row from registry_links.csv: an LEI link minted by name match ("gleif_exact_confident") that
appears to point at a different company with the same name. SCHEMA 4.8: a registry link asserts the identifier belongs to
THIS organization; a wrong link is worse than none. Removal is recorded in a REMOVALS.csv manifest; nothing else changes.
Each verified_fact is a quote re-fetched on 2026-11-19 and matched word for word on the URL given (format: what it shows |
URL | quote). The LEI facts come from our raw copy of the GLEIF record. The Muse note is an unverified lead, context only.
Other registry links on the org (for example a federal UEI) are NOT being removed; say if one of them is also suspect.
For EACH row: SOUND (remove the link), WRONG (keep it, and why), or DOUBT (the fact that would settle it). Be strict about
identity: same name is not same company, and different address is not different company (registered agents, HQ moves).
End with the count of SOUND / WRONG / DOUBT. Under 600 words; one line per row, starting with the org_id.

ROWS:
[
 {
  "org_id": "ORG-000174",
  "our_name": "Vertex, Inc.",
  "our_city": "Mogadore, OH",
  "our_website": "http://www.vertexseals.com/",
  "our_description": "Custom elastomeric seals and rubber extrusions (est. 1992/93)",
  "registry_rows_on_this_org": [
   "LEI 549300QMYW171MP1PL50 (gleif_exact_confident)"
  ],
  "link_to_remove": "LEI 549300QMYW171MP1PL50 (match_basis gleif_exact_confident, as_of 2026-10-28)",
  "lei_record": {
   "legal_name": "VERTEX, INC.",
   "jurisdiction": "US-DE",
   "registered_as": "3139983",
   "creation_date": "2020-06-26",
   "legal_address": "C/O CORPORATION SERVICE COMPANY, 251 LITTLE FALLS DRIVE, WILMINGTON, US-DE",
   "hq_address": "2301 RENAISSANCE BLVD, UPPER MERION TOWNSHIP, US-PA"
  },
  "verified_fact_1": "other company's own address = LEI HQ | https://www.vertexinc.com/contact-us | 2301 Renaissance Blvd King of Prussia, PA 19406",
  "verified_fact_2": "our org's own page, our city | https://vertexseals.com/contact-us/ | VERTEX, Incorporated 3956 Mogadore Industrial Parkway Mogadore, Ohio 44260 USA",
  "muse_note_unverified": "The LEI record names the entity VERTEX, INC. and records its headquarters at 2301 Renaissance Blvd, Upper Merion Township, PA 19406 (Delaware file 3139983, creationDate 2020-06-26, no parent relationship recorded). That address is the King of Prussia headquarters of Vertex, Inc., the enterprise tax-software company (NASDAQ: VERX) — a different company. Our Vertex, Inc. is the Mogadore, OH rubber manufacturer: its own site (vertexseals.com, opened) describes custom seals and custom rubber extrusions and lists phone 330-628-6230, the number on the Mogadore listing."
 },
 {
  "org_id": "ORG-000780",
  "our_name": "Custom Molded Products, LLC",
  "our_city": "Wilmington, OH",
  "our_website": "https://www.custommolded.com/",
  "our_description": "Custom plastic injection molder: insert, two-shot, PVC and antimicrobial molding, assembly.",
  "registry_rows_on_this_org": [
   "LEI 549300PFONU4YY4GYS55 (gleif_exact_confident)"
  ],
  "link_to_remove": "LEI 549300PFONU4YY4GYS55 (match_basis gleif_exact_confident, as_of 2026-10-28)",
  "lei_record": {
   "legal_name": "Custom Molded Products, LLC",
   "jurisdiction": "US-DE",
   "registered_as": null,
   "creation_date": "",
   "legal_address": "C/O Corporation Service Company, 2711 Centerville Road, Suite 400, Wilmington, US-DE",
   "hq_address": "36 Herring Road, Newnan, US-GA"
  },
  "verified_fact_1": "other company's own address = LEI HQ | https://www.c-m-p.com/faq/cmp-warranty-full-text/ | Custom Molded Products, LLC. 36 Herring Road, Newnan, Georgia 30265",
  "verified_fact_2": "our org's own page, our city | https://www.custommolded.com/contact-us/ | Custom Molded Products LLC 92 Grant Street Wilmington, Ohio 45177",
  "muse_note_unverified": "The LEI entity's GLEIF headquarters address (36 Herring Road, Newnan, GA 30265) is the address the pool/spa company CMP prints on its own product literature (quoted); that company makes pool, spa and whirlpool components. The Wilmington, OH business is a separate custom injection molder (its own site, custommolded.com, offers turnkey two-shot injection molding) with no connection to the Newnan company shown on any page opened. The GLEIF record is also weak: corroborationLevel ENTITY_SUPPLIED_ONLY, registeredAt RA999999, registeredAs null, registration status LAPSED."
 },
 {
  "org_id": "ORG-001383",
  "our_name": "Delco, LLC",
  "our_city": "Akron, OH",
  "our_website": "https://delcollc.com/",
  "our_description": "Akron precision machining and fabrication shop (est. 1971) whose listed work includes custom molds and dies for plastics molding.",
  "registry_rows_on_this_org": [
   "LEI 5493008QN54WVMZHGF61 (gleif_exact_confident)",
   "FRS 110009634217 (echo_exporter_street_city_zip_name:SITE-001422)",
   "UEI TK37ASDR6529 (sam_exact_uei)"
  ],
  "link_to_remove": "LEI 5493008QN54WVMZHGF61 (match_basis gleif_exact_confident, as_of 2026-10-28)",
  "lei_record": {
   "legal_name": "Delco LLC",
   "jurisdiction": "US-NJ",
   "registered_as": "0600099697",
   "creation_date": "2000-10-11",
   "legal_address": "200 Campbell Drive, Suite 200, Willingboro, US-NJ",
   "hq_address": "200 Campbell Drive, Suite 200, Willingboro, US-NJ"
  },
  "verified_fact_1": "other company's own address = LEI HQ | https://delcodevelopment.com/ | 200 Campbell Dr #200, Willingboro, NJ 08046",
  "verified_fact_2": "our org's federal record (SAM UEI TK37ASDR6529, already on our record), our city | https://api.usaspending.gov/api/v2/recipient/ddcde7b3-fdae-a532-27b1-346a40382373-C/ | 3300 MASSILLON RD",
  "muse_note_unverified": "The LEI record (api.gleif.org, viewed 2026-11-19) is a New Jersey LLC: legal name Delco LLC, legal and headquarters address 200 Campbell Drive, Suite 200, Willingboro, NJ, jurisdiction US-NJ, registeredAs 0600099697, creationDate 2000-10-11. That address is the headquarters of Delco Development, whose own site footer reads 200 Campbell Dr #200, Willingboro, NJ 08046 and which describes itself as a real estate company (quoted). Our Akron business is a separate Ohio manufacturer: FMCSA SAFER (safer.fmcsa.dot.gov, USDOT 1577001) lists a carrier whose Legal Name is DELCO LLC with Physical Address 3300 MASSILLON ROAD, AKRON, OH 44312 and cargo STEEL MOLDS, and the Akron company's own site (delcollc.com) publishes AS9100/ISO 9001 supplier quality terms for machining and tooling work. Same name, unrelated companies in different states and industries."
 }
]
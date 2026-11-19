# Three LEI links removed: a same-name company in another state (2026-11-19)

**−3 rows in `data/registry_links.csv`.** Each removed link was minted on 2026-10-28 by name match
(`gleif_exact_confident`). Each points at a different company that has the same legal name. SCHEMA §4.8: a registry
link asserts the identifier belongs to this organization, and a guarded no-hit is never recorded as a negative fact. So
the wrong link is deleted, and nothing replaces it. The removals are declared in `REMOVALS.csv` for the row-loss guard.

| org | Atlas organization | LEI removed | LEI entity |
|-|-|-|-|
| ORG-000174 | Vertex, Inc., Mogadore, OH: rubber seals and extrusions | 549300QMYW171MP1PL50 | VERTEX, INC., DE file 3139983, HQ 2301 Renaissance Blvd, Upper Merion Twp, PA: the tax-software company |
| ORG-000780 | Custom Molded Products, LLC, Wilmington, OH: injection molder | 549300PFONU4YY4GYS55 | Custom Molded Products, LLC, DE, HQ 36 Herring Road, Newnan, GA: the pool and spa parts maker |
| ORG-001383 | Delco, LLC, Akron, OH: machining and mold building | 5493008QN54WVMZHGF61 | Delco LLC, NJ file 0600099697, 200 Campbell Drive, Willingboro, NJ: the office address of Delco Development, a real estate developer |

**Evidence.** Two facts per row were re-fetched on 2026-11-19 and matched word for word. Neither is GLEIF's own record.
- The other company's own page carries the LEI record's address:
  - vertexinc.com/contact-us: "2301 Renaissance Blvd King of Prussia, PA 19406";
  - c-m-p.com warranty page: "Custom Molded Products, LLC. 36 Herring Road, Newnan, Georgia 30265";
  - delcodevelopment.com: "200 Campbell Dr #200, Willingboro, NJ 08046".
- Our organization's own page, or a federal record, places it in our city:
  - vertexseals.com/contact-us: "3956 Mogadore Industrial Parkway Mogadore, Ohio 44260";
  - custommolded.com/contact-us: "92 Grant Street Wilmington, Ohio 45177";
  - USAspending's record for Delco's UEI TK37ASDR6529, which is already on our record: "3300 MASSILLON RD", Akron, OH.

**Kept.** Delco's UEI and FRS links stay: USAspending places that UEI at the Akron shop. Vertex and Custom Molded Products
held no other registry rows.

**Not changed: two other leads from the same check.**
- **Sterilite (ORG-001384).** OSHA names the Massillon plant's operator "Sterilite Corporation Of Ohio, Llc". The LEI
  belongs to the Massachusetts parent. No page states the ownership, so the link stays pending a ruling on parent LEIs.
- **LyondellBasell Advanced Polymers (ORG-000735).** No page ties this entity to the Perrysburg plant, so the link stays.

**Source of the leads.** Muse (Meta) answered "is this the right LEI?" for the 29 links that failed the address gate in
`tasks/gleif-founded-2026-11-19`. Its answers are leads only; every fact used here was re-read. The packet, the re-read log
and the reviews are kept outside the repo in `_atlas-corpus/muse-2026-11-19/`.

## Review

Codex (deep) and Antigravity (Gemini, deep) each reviewed all three rows: **3 SOUND, 0 WRONG, 0 DOUBT** from both. Grok
returned HTTP 402 (no credits), so Antigravity stood in.
- **Codex's caveat on Delco.** The developer's own terms of use name it Delco Development, LLC. So the shared address does
  not prove which New Jersey company the LEI entity is. It does show the LEI is not the Akron shop, which is all this change
  asserts.
- **The other links on Delco.** Both families checked them. UEI TK37ASDR6529 and FRS 110009634217 both place DELCO, LLC at
  3300 Massillon Road, Akron, and neither is suspect.

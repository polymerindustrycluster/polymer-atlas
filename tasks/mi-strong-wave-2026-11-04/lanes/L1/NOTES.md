# L1 notes, MI STRONG wave (2026-11-04)

22 clusters in, 22 verdicts out. Dedupe: `scripts/atlas.py dedupe-check` (name, street, domain) and `show` on the
fusion_refs and hit IDs. Own-site pages read with WebFetch and, where it failed, a read-only HTTP GET.

## Counts
| Verdict | Tier | n |
|-|-|-|
| VERIFIED_NEW_ORG | C | 15 |
| VERIFIED_NEW_SITE | B | 4 (two US Farathane sites, TH Plastics Mendon, Creative Foam Fenton) |
| STILL_UNCERTAIN | n/a | 3 (Lacks Raleigh Dr, EFI Ypsilanti, PDS Dorr) |
| REJECT / DUPLICATE_OF | n/a | 0 / 0 |

Tier C on the new-org rows follows the brief ("a new organization is C"). Most of those rows also have an own-site
witness, so the site would be B-eligible once the org exists.

## Cross-row items for the integrator
- US Farathane: one org (EIN 463221181), three rows. LF-MI-00604 (Auburn Hills HQ) is the NEW_ORG row;
  LF-MI-00330 (Port Huron) and LF-MI-00576 (Sterling Heights Mound Rd) carry `held_org_id = NEW:LF-MI-00604`.
  The fusion_refs on those rows (ORG-003054, -003244, -003517, -000950) are other companies, not US Farathane.
- Held-org HQ fields look wrong: ORG-001151 TH Plastics (HQ Bowling Green MI; own site gives Mendon MI) and
  ORG-000769 Creative Foam (HQ Dayton OH; own site gives Fenton MI corporate office).
- Robinson Industries (LF-MI-00836): ORBIS Corporation (held ORG-000474) announced the acquisition 2026-02-02. The
  witness is ORBIS's page because Robinson's site returned 403 or certificate errors. Not a closure. Created as its own
  org to avoid a false merge; link parent_of if the deal structure supports it.
- Regency Plastics - Ubly (LF-MI-00758): witness is a historical entry on the parent Gemini Group site. Could be shaped
  as a site under a new Gemini Group org instead.

## Weak spots (checked, not hidden)
- WebFetch summarizes pages; quotes are what the tool returned verbatim, not byte-checked against HTML. Quotes with
  curly apostrophes (SPI, Regency) or very short spans (Wright, Vaupell list item) need the integrator's re-fetch.
- vaupell.com blocked direct GETs (403); the Michigan page text came through WebFetch.
- Weakest verified rows: East Jordan Plastics Beaverton and Wright Sheridan (activity is company-wide, not plant-level);
  Do-It (plastic hang tabs, forming process not stated, scope borderline).
- EFI is an owner scope question (inkjet UV ink), not self-ruled.
- No Form 5500 check was needed: no REJECT for closure or no-establishment was issued.
- Several org_hq_county and site county cells are blank where the input county was blank; the schema requires county
  only for Ohio sites.

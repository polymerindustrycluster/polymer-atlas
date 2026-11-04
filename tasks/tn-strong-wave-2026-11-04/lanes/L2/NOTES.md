# Lane L2 notes (TN STRONG wave, 2026-11-04)

15 input clusters, 15 verdicts in `verdicts.csv`. No data/ edits, no git.

## Counts
| Verdict | n | Clusters |
|-|-|-|
| VERIFIED_NEW_SITE | 6 | 00199 Sekisui, 00250 Hankook, 00060 INOAC, 00191 Westlake Royal, 00220 Rapac/Ring, 00217 Carpenter |
| VERIFIED_NEW_ORG | 6 | 00143 SaarGummi, 00140 FIT, 00122 Manar/Tennplasco, 00270 Kordsa, 00132 Diversatech, 00252 Sanderson Pipe |
| REJECT | 1 | 00003 Bridgestone LaVergne (closed) |
| STILL_UNCERTAIN | 2 | 00219 Sanford LP (scope), 00159 Polyform (no own site) |
| DUPLICATE_OF | 0 | no street-level hit anywhere |

Tiers: B x5 (Sekisui, Hankook, INOAC, Ring/Rapac, Carpenter), C x7 (all six new orgs plus Westlake Bristol).

## Method
- Dedupe: `atlas.py dedupe-check` by name, street and domain, plus a name/brand/domain scan of all organization and site shards (`scratchpad/l2_find.py`). Domains checked for every new org: saargummi.com, fitfibers.com, universalfibers.com, dpgllc.com, kordsa.com, sandersonpipe.com, manarinc.com. No hits, so no brand-name miss like Dart/WinCup.
- Every `own_quote` was copied from a page I fetched, then re-checked programmatically against the live URL (whitespace and quote-mark normalized): 13 of 13 present (11 direct, 2 via Jina). Search snippets were never used as quotes.
- Fetch route: TinyFish fetch for most pages; Jina for fitfibers.com/contacts (to see the address) and the paywalled Rubber News piece (still paywalled, not used).

## Flags for the integrator
1. **Closure, Bridgestone LaVergne (00003):** REJECT on Bridgestone's own 2025-01-23 release (closure effective 2025-07-31). ORG-000011 has no LaVergne site, so there is nothing to tombstone; log in inclusion_log if wanted. Cluster has no F5500 source, so the 5500 gate does not apply.
2. **Announced closure, INOAC Livingston (00060):** plant still operating; wind-down Feb 2027, cease April 2027 per Overton County News 2026-10-06 (chamber announcement, not the company). Verified as a site; suggest monitor_watch and re-verify after 2027-04.
3. **HQ disagreements with held records:** Sekisui Kasei USA ORG-001108 held HQ Kenton OH, own site says HQ is Mt. Pleasant TN. Ring Container ORG-001082 held HQ Sidney OH, own site says Corporate Headquarters is Oakland TN. Both held HQs are marked unverified staging values.
4. **Scope questions (owner rulings, not self-ruled):**
   - Thermoplastic fiber/filament producers: FIT (00140, melt-spun bicomponent fibers) and Kordsa Chattanooga (00270, nylon 66 yarn for tire cord). Atlas has fiber_filament precedent but no ruling that fiber producers are Ring 1/2.
   - Writing-instrument ink, Sanford LP Manchester (00219): no polymer or resin production stated (B28); PIC counts inks where resin is the binder. Held as STILL_UNCERTAIN.
5. **Possible overlaps, not merged:** Kordsa Chattanooga (4501 North Access Rd) vs SITE-004194 Microtex Chattanooga (no street held, also a Kordsa plant, also on the former DuPont property). Ring/Rapac `65 Industrial Park` vs the own site's `One Industrial Park Rd.` in the same Oakland park.
6. **Org-vs-operator choices:** Kordsa (parent Kordsa Teknik Tekstil A.S., Izmit, Turkey, vs operating Kordsa, Inc.); SaarGummi (operating SaarGummi Tennessee Inc. vs Luxembourg group parent, HQ left blank because the own site states none); Hankook (operator is Hankook Tire Manufacturing Tennessee, LP; I attached the site to held ORG-000204). Manar, Inc. is the org for Tennplasco (HQ Edinburgh IN, county blank).
7. **Second sites outside this lane:** Sekisui Mount Pleasant Molding Facility, 1331 North Main Street (own contact page). Manar KEY Manufacturing (Madison IN) and Manar Medical (Edinburgh IN).
8. **Weak own-site witnesses:** SaarGummi (names plant and division only), Westlake Royal Bristol (page prints only "Bristol, TN" under Manufacturing), Kordsa (activity stated regionally). Tiered C; downgrade to STILL_UNCERTAIN if the integrator wants a plant-level activity statement.
9. **Polyform (00159):** the polyforminc.net / extrudedplastics.com "Polyform, Inc." pages are the Oregon company, not Decatur TN; ignored.
10. **NAICS:** `naics_primary` left blank where the set had no clear primary (Sekisui, Kordsa, Diversatech). FIT carries 325220 (SCHEMA 2.2 code) though the rows show 325222/325200/325220.

## Unchecked
- No Form 5500 pull beyond what the cluster rows carry. Edinburgh IN county (Manar HQ) not stated on the site, so blank.
- Nashville Post (LaVergne sale) and Plastics News (Manar land purchase) appear only as search snippets; they are not relied on.

# Lane L3 notes (MA STRONG wave, 2026-11-04)

18 clusters in, 18 verdicts out. Tooling: WebFetch and WebSearch, plus read-only `atlas.py dedupe-check` (name and domain). No data files touched.

## Counts (unit: LF-MA clusters in L3 input)
| Verdict | Tier | n |
|-|-|-|
| VERIFIED_NEW_ORG | B | 7 (00444, 00122, 00548, 00036, 00008, 00087, 00527) |
| VERIFIED_NEW_ORG | C | 3 (00019, 00469, 00402) |
| VERIFIED_NEW_SITE | C | 2 (00147 Sterilite -> ORG-001384; 00331 ADS -> ORG-000651) |
| REJECT | - | 1 (00372 Dodge Company) |
| STILL_UNCERTAIN | - | 5 (00359, 00356, 00124, 00592, 00107) |

## Method calls the integrator should know
- **Tier B rule applied:** B only when one own-site page prints the plant address or city and states polymer work (quote kinds are mostly `activity_only`, since address and activity sit in different spans of the same page). Where the activity page does not name the city, the tier is C.
- **Quotes:** WebFetch returns summarized text, with quoted spans capped near 125 characters. Every `own_quote` is a span the tool reported as verbatim and is kept under 25 words. Please re-fetch before applying; none was checked against raw HTML.
- **No-site or unreadable-site cases are not evidence:** gregorymfg.com and easternpackaging.com redirect to for-sale pages; cmtmaterials.com failed with a TLS certificate error; ADS facility locator is script-driven. These stay STILL_UNCERTAIN or C, never REJECT.
- **Scope strictness:** a NAICS code, a third-party directory, or an FDA registration did not count as showing polymer work.

## Notable items
- **Dodge Company (00372): REJECT.** Embalming chemicals and cosmetics; own history page shows no polymer. Both step4 atlas hits (Kent Pultrusion ORG-000406, CITO ORG-003735) are note-text substring matches on the name, not this company.
- **ZRC / Norfolk Corporation (00124): STILL_UNCERTAIN, owner-ruling flavored.** Own site: corrosion-resistant zinc-rich coatings made in Marshfield, but never names a resin or binder. Third-party spec sheet says organic zinc compound. If the owner rules zinc-rich coatings in scope, it becomes a B. Own site prints 145 Enterprise Drive; federal row says Ave. Step4 hit ORG-001414 Flexmag is a false positive.
- **CMT Materials (00356): STILL_UNCERTAIN.** Fusion says HELD_ORG_OTHER_LOCATION (ORG-004046 Globe Composite Solutions, Stoughton). CMT Materials LLC and Globe Composite share an ESCO-branded site, and the Attleboro address appears there only on a Sales Partners page. Need: legal-entity relationship and a page showing resin-based syntactic foam made at Attleboro.
- **Restech (00527): cluster is polluted.** It merges unrelated names and EINs (Ossco Bolt Distribution, Mediterranean Fine Foods, IN Acquisition LLC, Danis Reading LLC and others) at 34 Tower St. Only the molder is verified; do not create the others. Upstream fusion should be reviewed for this address.
- **Eastern Packaging (00107):** fusion_refs ORG-003926 is RH Adhesives in Acton, a different company; ignore. A MassDEP fact sheet (403 on fetch, snippet only) says plastic packaging manufacturing and printing; a readable copy would likely settle it.
- **Sterilite (00147):** the held record ORG-001384 lists Massillon OH as HQ, but third-party sources put Sterilite HQ in Townsend since 1968. Review the held org HQ field; the Townsend site may be the HQ site.
- **Mayhew Basque (00402):** own releases say the plastics operation consolidated into Leominster in 2016; Westminster 100 Simplex Dr rests on federal rows plus a third-party WBJ item. Parent Mayhew Steel Products (Turners Falls) is not in the Atlas; integrator may prefer holding the parent.
- **Duromar (00469):** own site active (2025 copyright) but silent on manufacturing, and one directory shows it closed. Tier C and flagged for a manufacture check before create. `/about` returned 404 while `/about-us` returned content.
- **Counties filled by lane:** Foxboro (Norfolk), Chicopee (Hampden), Hudson (Middlesex) were blank in the federal rows.

## Dedupe record
Name searches (steps 2 and 4) run for all 18; domain search (step 1) for all org websites found; step 3 street scan of `sites_MA.csv` for all 18 streets found no existing site. Only hits: Sterilite -> ORG-001384 and ADS -> ORG-000651 (same companies, other states), plus the false positives above.

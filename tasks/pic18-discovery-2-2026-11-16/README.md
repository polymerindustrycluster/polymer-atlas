# PIC-18 discovery, real research pass (DISC2) — 2026-11-16

Claim: atlas-w16-disc2 (integrator for exactly this scope). First user: PIC membership prospector; non-use finding due 2026-12-15. Draft packet for controller review, not a completion or merge approval.

## Result
72 held leads adjudicated (unit: ranked lead names from PR #356's frozen frame: 80 ranked names minus its 8 DUPLICATE_OF). Lead names, URLs and quotes are not published (owner ruling 2026-11-17); rank, verdict, held-record target and settling fact only, as in the first packet. **Zero were VERIFIED, so zero organization, site or evidence rows were applied.** data/ is untouched and the ID blocks ORG-014300..014499, SITE-020400..020599, EVD-391000..392999 are unused. The pass found that the first lane's guessed-domain dedupe had missed 6 companies the Atlas already holds, and it did not reach a create for any not-held company inside the time box.

## Counts (unit: held leads adjudicated)
Verdicts, recomputed by check.py: DUPLICATE_OF 6, STILL_UNCERTAIN 65, REJECT 1, VERIFIED 0. Applied 0; held 72.
- DUPLICATE_OF 6 (ranks 1, 28, 39, 41, 43, 80): each maps to a held Atlas record in `target_record`. No existing row is edited (rule 13); these are alias follow-ups. Ranks 28, 39 and 43 were settled by reading the company's own site (the first lane's guessed domains were wrong or absent); ranks 1 and 41 by the street check with no own page read; rank 80 by name (borrower spelling variant) plus city only.
- REJECT 1 (rank 74): the own page, whose domain a web search returned, states a business with no polymer link. Ranks 11, 62, 68, 77 and 79 were first drafted as REJECT on pages reached through the first lane's guessed domains; under the controller's rule against guessed addresses they are STILL_UNCERTAIN.
- STILL_UNCERTAIN 65: ranks 6, 17, 18, 19, 23, 32, 48, 52, 59, 64, 65 share a street, domain, name or group with a held record (target_record carries it); ranks 7, 34, 36, 37, 58 are metal, coating-removal, chemical-blending or wire businesses needing an owner scope ruling (recommendation: out of scope); ranks 47, 69, 75, 76 look like polymer companies but no own page could be read; the rest keep the first lane's hold.
Work done (`work_done`): own-site read 10 leads, search only 13, dedupe only 49. 10 stored witness quotes (hashes only here).

## Dedupe
All 72 went through `atlas.dedupe` with name, street and city and no domain, so AGENTS 3 steps 2 to 5 ran for all of them; step 1 (domain) ran only for confirmed own-site domains and for the first lane's guessed-domain run, which proves nothing about identity. A street search of site notes and a first-token name screen of organizations and sites were added. The CLI misses a street that sits only in held site notes (ranks 18 and 59), exactly the first lane's rank 23 case; those are holds with that fact.

## Order and limits (about 35 minutes)
The brief said to work the frame in order; I did not. After one bulk dedupe pass I prioritised polymer-sounding names and leads whose guessed domain had a stored page, so a low rank may have had less attention than a high one.

23 of 72 leads got a search or own-site read; the other 49 carry the first lane's generic hold. No create was possible because no plausibly polymer, not-held lead had an own-site URL I could tie to it by name and location (ranks 47, 69, 75, 76). A failed fetch is availability, never absence.

## URL provenance
Every verdict row has `url_provenance`: `held-record` (10), `web-search` (8) or `none` (54). Per the controller's rule a URL is used only if it is on a held record, was returned by a search I ran, or is linked from a fetched page; the first lane's guessed domains are discarded, and check.py fails a witness on a `none` row. Before that rule reached me I fetched a few URLs I had constructed; none is cited. Search results and directory listings were used only to find leads and real domains; nothing from them, SAM or PPP is recorded.

## Proposed follow-ups (not in this PR)
1. Rank 47 (sheet rubber flooring per directories; not held): read a current own page or a federal filing, then create at tier C.
2. Ranks 69 and 75 (injection molding, vinyl packaging; not held): find an own-site URL by search, then read it and create.
3. Alias notes for the 6 DUPLICATE_OF ranks, if the owner wants them (needs a column edit this lane may not make).
4. Method fix for any lead lane: dedupe by name, street and site notes before guessing domains.
5. Owner scope rulings for ranks 7, 34, 36, 37 and 58.

## Files
verdicts.csv (all 72), witnesses.csv (witness id, rank, sha256), make_readme.py, build.py (idempotent; asserts zero VERIFIED and unused ID blocks), check.py (recomputes counts, yield 72 vs frame 80 minus 8, re-verifies quotes and hashes from private storage, scans every committed file for lead names and URL hosts from the private name list, checks held-record facts, proves failure on 8 injected defects). Names, URLs, quotes, the packet generator and the first lane's verdict copy live in controller storage (S/persist/pic18-discovery-2/private), as do raw pages (contract rule 8). Earlier commits on this branch still contain the names; history is not rewritten.

## Applied / held register
| Rank | Verdict | Applied / held | Target | Work | URL provenance | Settling fact |
|---|---|---|---|---|---|---|
| 1 | DUPLICATE_OF | held | ORG-000416;SITE-000445 | dedupe | held-record | Street identical to held SITE-000445 (ORG-000416); alias follow-up only. No own page read. |
| 2 | STILL_UNCERTAIN | held |  | dedupe | none | Polymer-containing formulated product evidence needed (cleaning or packaging alone insufficient). Owner scope question. |
| 3 | STILL_UNCERTAIN | held |  | dedupe | none | Independent company identity, polymer activity, physical PIC-18 business address and address-exact county; candidate route unavailable or insufficient. |
| 4 | STILL_UNCERTAIN | held |  | dedupe | none | Exact lead identity after the first lane's route redirected to a different company; polymer scope and PIC-18 establishment unconfirmed. |
| 5 | STILL_UNCERTAIN | held |  | dedupe | none | The first lane noted a possible alias of a held parent; resolve held-parent identity before any create. |
| 6 | STILL_UNCERTAIN | held | ORG-000290 | dedupe | held-record | Domain is the held website of ORG-000290; the own pages read do not print the lead's borrower name. Alias unconfirmed; no edit. |
| 7 | STILL_UNCERTAIN | held |  | own-site | web-search | Own page (URL from a web search) shows a metal-substrate label manufacturer; owner scope ruling (recommendation: out of scope). |
| 8 | STILL_UNCERTAIN | held |  | dedupe | none | Polymer-specific formulation or predominant polymer-customer evidence needed, not general chemical supply. |
| 9 | STILL_UNCERTAIN | held |  | dedupe | none | Needs evidence of physical polymer transformation at the establishment; the product line alone does not identify the operator's process. |
| 10 | STILL_UNCERTAIN | held |  | dedupe | none | Independent company identity, polymer activity, physical PIC-18 business address and address-exact county; candidate route unavailable or insufficient. |
| 11 | STILL_UNCERTAIN | held |  | search | none | No own URL found by search; directory pages describe a blasting and explosives business, so scope looks outside polymer. |
| 12 | STILL_UNCERTAIN | held |  | search | web-search | Own group page (URL from a web search) names no establishment in the lead's city. A search summary of local news says production there ended in 2023; unfetched, so no status change is asserted. Settling fact: dated outcome record plus the Form 5500 check (AGENTS 8). |
| 13 | STILL_UNCERTAIN | held |  | dedupe | none | Polymer research or production scope needed at the exact establishment. |
| 14 | STILL_UNCERTAIN | held |  | dedupe | none | Polymer formulation evidence and exact facility address needed. |
| 16 | STILL_UNCERTAIN | held |  | dedupe | none | Independent company identity, polymer activity, physical PIC-18 business address and address-exact county; candidate route unavailable or insufficient. |
| 17 | STILL_UNCERTAIN | held | ORG-000825 | dedupe | held-record | Domain is the held website of ORG-000825 (sites elsewhere in Ohio); the own page read names no establishment in the lead's city. Unconfirmed alias or new site of the held parent. |
| 18 | STILL_UNCERTAIN | held | SITE-000928 | search | none | Street sits in the notes of held SITE-000928 (ORG-000354). No own page tied to the lead. Settling fact: an own page or federal filing tying the establishment to the lead or to the held group. |
| 19 | STILL_UNCERTAIN | held | ORG-000636 | dedupe | held-record | Domain is the held website of ORG-000636; the site answered 403, so alias and establishment are unconfirmed. |
| 20 | STILL_UNCERTAIN | held |  | dedupe | none | Independent company identity, polymer activity, physical PIC-18 business address and address-exact county; candidate route unavailable or insufficient. |
| 21 | STILL_UNCERTAIN | held |  | dedupe | none | Owner scope ruling for injectable polymer microspheres and the physical production location. |
| 22 | STILL_UNCERTAIN | held |  | dedupe | none | Independent company identity, polymer activity, physical PIC-18 business address and address-exact county; candidate route unavailable or insufficient. |
| 23 | STILL_UNCERTAIN | held | SITE-000237 | dedupe | none | Street shared with held SITE-000237 (ORG-000223); the first lane's refutation stands. Settling fact: primary operator and distinct-establishment evidence. |
| 24 | STILL_UNCERTAIN | held |  | dedupe | none | Independent company identity, polymer activity, physical PIC-18 business address and address-exact county; candidate route unavailable or insufficient. |
| 25 | STILL_UNCERTAIN | held |  | dedupe | none | Independent company identity, polymer activity, physical PIC-18 business address and address-exact county; candidate route unavailable or insufficient. |
| 27 | STILL_UNCERTAIN | held |  | dedupe | none | Polymer-specific scope of a water-treatment chemical business. |
| 28 | DUPLICATE_OF | held | ORG-000117;SITE-000116 | own-site | held-record | Own contact page (held ORG-000117 website) prints the street of held SITE-000116. DUPLICATE_OF; no edit. |
| 31 | STILL_UNCERTAIN | held |  | dedupe | none | Independent company identity, polymer activity, physical PIC-18 business address and address-exact county; candidate route unavailable or insufficient. |
| 32 | STILL_UNCERTAIN | held | ORG-000600;SITE-000639 | own-site | held-record | Own page (held ORG-000600 website) prints a Twinsburg street and suite; held SITE-000639 has no street. Subsidiary-versus-parent and site grain not settled; no edit. |
| 34 | STILL_UNCERTAIN | held |  | search | none | No own URL tied to the lead; search returned only directory pages describing private-label aerosol and liquid products. Owner scope question (recommendation: out of scope unless an own page shows polymer products). |
| 36 | STILL_UNCERTAIN | held |  | own-site | web-search | Own page (URL from a web search) shows coating-removal and surface-preparation services; owner scope ruling (recommendation: out of scope). |
| 37 | STILL_UNCERTAIN | held |  | own-site | web-search | Own page (URL from a web search) shows private-label blending of water-treatment and cleaning products; owner scope ruling (recommendation: out of scope). |
| 38 | STILL_UNCERTAIN | held |  | dedupe | none | Identity and scope ruling for a commercial flooring installation business. |
| 39 | DUPLICATE_OF | held | ORG-000336;SITE-000357 | own-site | held-record | Own contact page (held ORG-000336 website) prints the street of held SITE-000357. DUPLICATE_OF; no edit. |
| 40 | STILL_UNCERTAIN | held |  | dedupe | none | Independent company identity, polymer activity, physical PIC-18 business address and address-exact county; candidate route unavailable or insufficient. |
| 41 | DUPLICATE_OF | held | ORG-000215;SITE-000228 | dedupe | none | Street is the held street of SITE-000228 (ORG-000215). No own page read. DUPLICATE_OF; no edit. |
| 42 | STILL_UNCERTAIN | held |  | dedupe | none | Independent company identity, polymer activity, physical PIC-18 business address and address-exact county; candidate route unavailable or insufficient. |
| 43 | DUPLICATE_OF | held | ORG-001597;SITE-001669 | own-site | held-record | Own site is the held website of ORG-001597; page text states rubber processing, injection molding and extrusion technology in the lead's city. DUPLICATE_OF; no edit. |
| 44 | STILL_UNCERTAIN | held |  | dedupe | none | Independent company identity, polymer activity, physical PIC-18 business address and address-exact county; candidate route unavailable or insufficient. |
| 45 | STILL_UNCERTAIN | held |  | dedupe | none | Polymer-specific business evidence needed for a biosolids processor. |
| 46 | STILL_UNCERTAIN | held |  | dedupe | none | Identity or alias question between two near-identical borrower spellings (see rank 51), and the physical business address. |
| 47 | STILL_UNCERTAIN | held |  | search | web-search | Best create prospect left: directory pages describe a sheet-rubber-flooring maker in the lead's city (not held; dedupe zero hits at all steps). The directory-listed domain answers with a redirect stub (availability observation). Settling fact: a current own page or federal filing for the establishment. |
| 48 | STILL_UNCERTAIN | held | ORG-001931;SITE-001925 | dedupe | none | Held ORG-001931/SITE-001925 is a large-group site in the same city; whether the lead's address is that establishment or a separate company is unsettled. |
| 49 | STILL_UNCERTAIN | held |  | dedupe | none | Owner ruling on print finishing and laminating scope, and the exact physical establishment. |
| 50 | STILL_UNCERTAIN | held |  | dedupe | none | Independent company identity, polymer activity, physical PIC-18 business address and address-exact county; candidate route unavailable or insufficient. |
| 51 | STILL_UNCERTAIN | held |  | dedupe | none | Resolve spelling variant against rank 46 before any create. |
| 52 | STILL_UNCERTAIN | held | ORG-000600;SITE-000639 | own-site | held-record | Same street and group as rank 32 and held ORG-000600; a second borrower name at one address. Same settling fact as rank 32. |
| 53 | STILL_UNCERTAIN | held |  | dedupe | none | Independent company identity, polymer activity, physical PIC-18 business address and address-exact county; candidate route unavailable or insufficient. |
| 54 | STILL_UNCERTAIN | held |  | dedupe | none | Independent company identity, polymer activity, physical PIC-18 business address and address-exact county; candidate route unavailable or insufficient. |
| 55 | STILL_UNCERTAIN | held |  | dedupe | none | Independent company identity, polymer activity, physical PIC-18 business address and address-exact county; candidate route unavailable or insufficient. |
| 57 | STILL_UNCERTAIN | held |  | dedupe | none | Independent company identity, polymer activity, physical PIC-18 business address and address-exact county; candidate route unavailable or insufficient. |
| 58 | STILL_UNCERTAIN | held |  | own-site | web-search | Own page (URL from a web search) shows spiral-formed wire products for electric utilities; no polymer scope shown. |
| 59 | STILL_UNCERTAIN | held | SITE-001777 | dedupe | none | Street is the held street of SITE-001777 (ORG-001701). Needs the company's own page naming its operator and establishment, as with the rank 23 refutation. |
| 61 | STILL_UNCERTAIN | held |  | dedupe | none | Independent company identity, polymer activity, physical PIC-18 business address and address-exact county; candidate route unavailable or insufficient. |
| 62 | STILL_UNCERTAIN | held |  | search | none | Guessed domain discarded (the page there is a different company); no own URL for the lead. |
| 63 | STILL_UNCERTAIN | held |  | dedupe | none | Independent company identity, polymer activity, physical PIC-18 business address and address-exact county; candidate route unavailable or insufficient. |
| 64 | STILL_UNCERTAIN | held |  | search | none | No own URL tied to the lead; the first lane's guessed domain is discarded. Settling fact: an own page naming the lead and its establishment. |
| 65 | STILL_UNCERTAIN | held | ORG-000354 | dedupe | none | Shares a group with held ORG-000354 (SITE-000378, SITE-000928). Needs an own page for the establishment and its operator. |
| 66 | STILL_UNCERTAIN | held |  | dedupe | none | Independent company identity, polymer activity, physical PIC-18 business address and address-exact county; candidate route unavailable or insufficient. |
| 67 | STILL_UNCERTAIN | held |  | dedupe | none | Alias and held-parent identity question for a packaging supplier; a redirect alone is insufficient. |
| 68 | STILL_UNCERTAIN | held |  | search | none | Guessed domain discarded (the page there is a different company); no own URL for the lead. |
| 69 | STILL_UNCERTAIN | held |  | search | web-search | Not held (dedupe zero hits). Directory pages describe an injection molder in the lead's city; the directory-named domain does not resolve. Settling fact: an own page. |
| 70 | STILL_UNCERTAIN | held |  | dedupe | none | Independent company identity, polymer activity, physical PIC-18 business address and address-exact county; candidate route unavailable or insufficient. |
| 71 | STILL_UNCERTAIN | held |  | dedupe | none | Owner scope decision for soldering flux formulations. |
| 72 | STILL_UNCERTAIN | held |  | dedupe | none | Exact operator identity; the first lane's guessed route named a business in another state. |
| 73 | STILL_UNCERTAIN | held |  | dedupe | none | Exact operator identity and alias relationship to rank 72. |
| 74 | REJECT | held |  | own-site | web-search | Own page (domain returned by a web search), same name as the lead, shows a skin-care business: no polymer link. |
| 75 | STILL_UNCERTAIN | held |  | search | none | Not held (dedupe zero hits). Directory pages describe a vinyl packaging maker in the lead's city but name no own URL tied to it; the first lane's guessed domain is discarded. Settling fact: an own URL from search or a linked page, then its page. |
| 76 | STILL_UNCERTAIN | held |  | search | none | No company found at this name and address by search; guessed domain discarded. Settling fact: an own page or filing. |
| 77 | STILL_UNCERTAIN | held |  | search | none | Guessed domain discarded; no own URL tied to the lead. |
| 78 | STILL_UNCERTAIN | held |  | dedupe | none | Independent company identity, polymer activity, physical PIC-18 business address and address-exact county; candidate route unavailable or insufficient. |
| 79 | STILL_UNCERTAIN | held |  | search | none | No own URL found by search; directory pages describe dealer license-plate frames, so scope looks outside polymer. |
| 80 | DUPLICATE_OF | held | ORG-000140;SITE-000140 | dedupe | held-record | Held ORG-000140 has the same name modulo a spelling variant, same city; match is name plus city only. Alias follow-up only. |

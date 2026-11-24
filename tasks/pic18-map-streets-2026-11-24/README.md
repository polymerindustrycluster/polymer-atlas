# PIC-18 street fills by the map-listing route (SCHEMA §4.13, v1.20.0)

Built by: Claude Code (Anthropic)

Claimed by atlas-p1-map-streets on 2026-11-24. First user is City of Akron economic development staff. Check for use by 2026-12-20. Base `9e281a8d` (includes #549, the gate route).

## Result

One street fill passes every leg and the binding gate: SITE-000011 (Akron Polymer Systems, tier C) takes `62 N Summit St` from Overture place `ddb95786-fece-4e56-b124-ca5400c3e0e0` (release 2026-11-18.0, source dataset BrightQuery), seconded by the held EPA FRS STRONG address note on the same site. The packet changes one cell (`street_address`), adds one evidence row (`map_listing` route: `platform_category`, `supports_C`) and removes the cured V-68 debt entry. **Unit and filter: active Ohio PIC-18 sites at tier A, B or C with a blank street. The base holds 153 of 879 (the 155 measured at e9bcabf, less the two #547 fills). This PR makes it 152.**

The expected yield was about 55. The rules give 1. The controller's 59 "listings that agree with a held lead" counted leads the gate does not accept as a second source: OSHA ITA, TRI and Ohio EPA candidates that failed binding in the street-gaps lane, PPP and SAM discovery rows from a task file, and free-text street mentions in site notes. The route accepts only a whole `Street (per <origin>): <street>` clause with a known non-matching origin, a STRONG EPA FRS address note, or an evidence row already bound to the site (own site or filing). Mint no second-source rows and edit no notes: both would be a different route. **36 of the 68 sites held for lack of an accepted second source (the 47 and 21 rows below) have a free-text note street that agrees with the listing (BASIS.csv `detail`).** Admitting them needs an owner or gate decision about lead forms, not a data change.

## Dispositions (unit: active PIC-18 tier A-C sites with a blank street on the base; 153)

| Disposition | Reason | Sites |
|---|---|---:|
| FILLED | listing and second source agree on every leg | 1 |
| HELD | no Overture or Google place with a held name in the site city | 64 |
| HELD | a listing exists, the site holds no second source in any form | 47 |
| HELD | a listing and candidate second sources exist, none in a gate-accepted form (`map_second_source_unbound`) | 21 |
| HELD | listings disagree with each other on the street (Overture two streets, or Overture against Google) | 11 |
| HELD | second source names a different street (`map_second_street_differs`: SITE-000061, SITE-000112) | 2 |
| HELD | listing ZIP differs from the held ZIP (SITE-001440: 44647 vs 44746; SITE-001480: 44281 vs 44274) | 2 |
| HELD | judgment hold, SITE-001824 (below) | 1 |
| STATUS_LEAD | a matched listing shows closed (SITE-000148, SITE-001718, SITE-001917, SITE-002035) | 4 |

Total 153. Tier of the one fill: C.

**Closed leads.** SITE-000148 and SITE-001917 are permanently closed in Google; SITE-001718 and SITE-002035 are `permanently_closed` in Overture. They are leads for a separate status check (AGENTS §3: status needs dated evidence). A listing's closed flag is not a status change, and no site was filled or edited. The check runs before any fill, so a closed listing can never reach the street route.

## Rules applied, and where they are stricter than the gate

1. Every leg must match: listing name equals a held name of the operator and is not a parent name; city equals the site city; base street blank; listing street equals a second-source street by the gate's `same_street` and `designators_compare`.
2. **Independence.** An Overture row may be seconded by a Google-origin lead only if the place's own source dataset is not Google-derived. For the filled row the dataset is BrightQuery (the stored capture lists it), and the second source is an EPA registry note, so the question does not arise. No Google-origin lead seconds anything in this packet. A Google row is never seconded by a Google-origin lead; the gate refuses that. Unknown lead origin is held.
3. **A `contradicts` row is never a second source.** The gate does not check this (review follow-up on #549); `build.py` and `check.py` do, and a planted defect proves it.
4. **ZIP leg (stricter than the gate, which ignores ZIP).** If the site holds a ZIP and the listing states one, the first five digits must match. Two sites fail this. No ZIP cell is filled: none of the passing candidates had a blank ZIP, and §4.13 says the route fills the street and nothing else.
5. **Two listings that disagree: hold.** 11 sites.
6. **Judgment hold, SITE-001824.** The gate passes it (own-site evidence rows EVD-422730 and EVD-422731, Overture and Google all give `7856 Brookside Dr`). The held note about this address is cut off mid-sentence ("a different Olm…") and the street-gaps packet classed the site's notes SUPERSEDED_OR_HISTORICAL. STILL_UNCERTAIN; the named fact is the full text of verification wave 5 verdict W5-0064.

## Captures and replay

Each cited listing capture is stored by SHA-256 in the shared store, at the brief's path `raw/overture/2026-11-18.0/<digest>.json` and, byte-identical, at `raw/map-listings/overture-maps-places/<digest>.json` because that is the only path the gate's `--map-store` replay reads. The capture is the cited release record projected into the gate's Overture shape (name, address, status, sources; no phone, email or person). `check.py` re-reads the record from the full release in the store (`raw/overture/2026-11-23-places`, part pinned from MANIFEST.sha256) by id and bounding box and requires the same bytes. No Google record is cited, so none is stored.

The hosted gate compares the quoted fields only and does not replay the capture or the second source. `check.py` and the reviewers do. Hold reasons depend on the controller's measurement packets (Overture bounding-box pull, Google raw.jsonl, street-gaps candidates.csv); they are not in the store, so `check.py` replays BASIS.csv from them when present and prints NOT RUN when absent. Their hashes are in PACKETS.sha256.

## Not checked

The hold reasons for 64 "no listing" sites rest on one Overture pull and one Google text search of three results each; absence of a match is a route signal, not evidence of absence. The 36 free-text agreements were not read against sources.

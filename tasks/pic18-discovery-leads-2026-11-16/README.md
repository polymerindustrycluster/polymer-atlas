# PIC-18 discovery leads — 2026-11-16

Claim: atlas-w16-discovery; designated integrator under controller contract. First user: PIC membership prospector; non-use finding due 2026-12-15. This is a draft packet for controller review, not a completion or merge approval.

## Counts and selection

342 privacy-filtered PPP loan rows collapse to 296 normalized borrower names. The supplied SAM cache yields 180 unmatched Ohio registration rows under the explicit filter in `frame.py`: city appears in held PIC-18 sites or supplied PIC-18 PPP leads, and primary/listed NAICS begins 325/326. This is broader than the brief's approximate 100: listed codes and city-name inclusion are discovery filters, not independently proved county or polymer scope. No SAM field is published as a company fact. The union has 460 normalized lead names; the largest loan JobsReported per name determines rank (never the sum). Missing PPP employment ranks as zero; ties use normalized name. All selected 80 names have PPP jobs, so this SAM-filter discrepancy does not change their order. Typos/legal alias equivalence remains a hold where not proved; normalized-name uniqueness is not proof of unique legal entities.

80 ranked lead names screened: 1 VERIFIED/applied, 8 DUPLICATE_OF/held alias follow-ups, 71 STILL_UNCERTAIN/held. Zero REJECTs. Net canonical additions: 1 organization at C, 1 headquarters site at C, 9 evidence rows (4 organization, 5 site). No existing record changed. No inclusion-log rows; ambiguous scope held.

## Sources and limits

MVP Plastics' own home/contact pages establish corporate injection-molding activity, legal styling and the physical corporate headquarters. Census address match establishes Geauga County. Its held Form 5500 sponsor spine also names MVP at the same address; no filing employment, code, identifier or mailing-location inference is published. The headquarters site is `hq_only`, with no manufacturing process asserted there. NAICS, employment, ownership, PIC membership and current liveness are unasserted. The false membership/watch booleans are required schema defaults, not evidence of non-membership.

`research.py` journals up to three candidate-route fetches per lead under controller storage; candidate domains are hypotheses, not verified identities. Some redirects lead to unrelated businesses and are explicitly held. Source availability is never closure evidence. MVP's successful www home/contact follow-ups and brochure retrieval remain below six fetches. Shared corpus manifest was inspected; it covers held organizations rather than establishing net-new company identity, so no new fact cites it. Raw HTML/text hashes and dedupe output remain in private controller persistence, not public contact data. `witnesses.csv` contains short public-source excerpts and exact raw hashes. The checker requires the original controller storage.

Dedupe used the canonical `atlas.dedupe` backend for all 80 across all shards, passing name, candidate domain and street/city; all five steps and successor chains are retained privately in `dedupe.json`. Candidate domains do not settle identity. MVP also received the CLI dedupe check with its verified name/domain/street. A name, address or guessed-domain candidate alone is not marked duplicate without adjudication. No alias is written to existing rows.

## Applied / held register

Rank refers to the private frozen frame; unverified borrower streets and loan facts are not exported here.

| Rank | Verdict | Applied / held | Target | Settling fact / follow-up |
|---|---|---|---|---|
| 1 | STILL_UNCERTAIN | held |  | Independent company identity, polymer activity, physical PIC-18 business address and address-exact county; candidate route unavailable or insufficient. |
| 2 | STILL_UNCERTAIN | held |  | Polymer-containing formulated product evidence (cleaning/packaging alone insufficient). |
| 3 | STILL_UNCERTAIN | held |  | Independent company identity, polymer activity, physical PIC-18 business address and address-exact county; candidate route unavailable or insufficient. |
| 4 | STILL_UNCERTAIN | held |  | Exact borrower identity after route redirects to Spring Valley; polymer-specific scope and PIC-18 establishment. |
| 5 | STILL_UNCERTAIN | held |  | Royal Chemical alias confirmed by FDA; resolve held-parent identity before create. |
| 6 | STILL_UNCERTAIN | held |  | Cosmo Plastics/Cosmo Corporation legal alias confirmation; own route returns server error. |
| 7 | STILL_UNCERTAIN | held |  | Independent company identity, polymer activity, physical PIC-18 business address and address-exact county; candidate route unavailable or insufficient. |
| 8 | STILL_UNCERTAIN | held |  | Polymer-specific formulation or predominant polymer customer evidence, not general chemical supply. |
| 9 | STILL_UNCERTAIN | held |  | Establish physical polymer transformation at the Stow site; therapy products alone do not identify operator process. |
| 10 | STILL_UNCERTAIN | held |  | Independent company identity, polymer activity, physical PIC-18 business address and address-exact county; candidate route unavailable or insufficient. |
| 11 | STILL_UNCERTAIN | held |  | Polymer relevance of explosive/drill-and-blast business. |
| 12 | STILL_UNCERTAIN | held |  | Independent company identity, polymer activity, physical PIC-18 business address and address-exact county; candidate route unavailable or insufficient. |
| 13 | STILL_UNCERTAIN | held |  | Polymer research or production scope at the exact Olon establishment. |
| 14 | STILL_UNCERTAIN | held |  | Polymer formulation evidence and exact facility address. |
| 15 | DUPLICATE_OF | held | ORG-000031 | Alias follow-up: confirm and bank borrower spelling against held record; no existing row edited. |
| 16 | STILL_UNCERTAIN | held |  | Independent company identity, polymer activity, physical PIC-18 business address and address-exact county; candidate route unavailable or insufficient. |
| 17 | STILL_UNCERTAIN | held |  | EP Holdings legal alias to Engineered Profiles and exact Mansfield establishment. |
| 18 | STILL_UNCERTAIN | held |  | Independent company identity, polymer activity, physical PIC-18 business address and address-exact county; candidate route unavailable or insufficient. |
| 19 | STILL_UNCERTAIN | held |  | Independent company identity, polymer activity, physical PIC-18 business address and address-exact county; candidate route unavailable or insufficient. |
| 20 | STILL_UNCERTAIN | held |  | Independent company identity, polymer activity, physical PIC-18 business address and address-exact county; candidate route unavailable or insufficient. |
| 21 | STILL_UNCERTAIN | held |  | Owner scope ruling for injectable polymer microspheres and physical production location. |
| 22 | STILL_UNCERTAIN | held |  | Independent company identity, polymer activity, physical PIC-18 business address and address-exact county; candidate route unavailable or insufficient. |
| 23 | VERIFIED | applied | ORG-014100;SITE-020200 | Own-company headquarters and scope; Census county confirmed. |
| 24 | STILL_UNCERTAIN | held |  | Independent company identity, polymer activity, physical PIC-18 business address and address-exact county; candidate route unavailable or insufficient. |
| 25 | STILL_UNCERTAIN | held |  | Independent company identity, polymer activity, physical PIC-18 business address and address-exact county; candidate route unavailable or insufficient. |
| 26 | DUPLICATE_OF | held | ORG-001806 | Alias follow-up: confirm and bank borrower spelling against held record; no existing row edited. |
| 27 | STILL_UNCERTAIN | held |  | Polymer-specific scope of water-treatment chemical business. |
| 28 | STILL_UNCERTAIN | held |  | Independent company identity, polymer activity, physical PIC-18 business address and address-exact county; candidate route unavailable or insufficient. |
| 29 | DUPLICATE_OF | held | ORG-001945 | Alias follow-up: confirm and bank borrower spelling against held record; no existing row edited. |
| 30 | DUPLICATE_OF | held | ORG-001827 | Alias follow-up: confirm and bank borrower spelling against held record; no existing row edited. |
| 31 | STILL_UNCERTAIN | held |  | Independent company identity, polymer activity, physical PIC-18 business address and address-exact county; candidate route unavailable or insufficient. |
| 32 | STILL_UNCERTAIN | held |  | Resolve Technoform subsidiary vs held parent and exact Ohio site. |
| 33 | DUPLICATE_OF | held | ORG-000610 | Alias follow-up: confirm and bank borrower spelling against held record; no existing row edited. |
| 34 | STILL_UNCERTAIN | held |  | Independent company identity, polymer activity, physical PIC-18 business address and address-exact county; candidate route unavailable or insufficient. |
| 35 | DUPLICATE_OF | held | ORG-000407 | Alias follow-up: confirm and bank borrower spelling against held record; no existing row edited. |
| 36 | STILL_UNCERTAIN | held |  | Independent company identity, polymer activity, physical PIC-18 business address and address-exact county; candidate route unavailable or insufficient. |
| 37 | STILL_UNCERTAIN | held |  | Independent company identity, polymer activity, physical PIC-18 business address and address-exact county; candidate route unavailable or insufficient. |
| 38 | STILL_UNCERTAIN | held |  | Identity and scope ruling for commercial flooring installation business. |
| 39 | STILL_UNCERTAIN | held |  | Correct Extrudex LP polymer-company domain; fetched Extrudex Aluminum is unrelated. |
| 40 | STILL_UNCERTAIN | held |  | Independent company identity, polymer activity, physical PIC-18 business address and address-exact county; candidate route unavailable or insufficient. |
| 41 | STILL_UNCERTAIN | held |  | Correct Advanced Polymer Coatings domain; apcoat.com is unrelated distributor. |
| 42 | STILL_UNCERTAIN | held |  | Independent company identity, polymer activity, physical PIC-18 business address and address-exact county; candidate route unavailable or insufficient. |
| 43 | STILL_UNCERTAIN | held |  | Correct itps-inc.com own route found; owner scope determination for inorganic polymer modifier manufacturer. |
| 44 | STILL_UNCERTAIN | held |  | Independent company identity, polymer activity, physical PIC-18 business address and address-exact county; candidate route unavailable or insufficient. |
| 45 | STILL_UNCERTAIN | held |  | Polymer-specific business evidence for biosolids processor. |
| 46 | STILL_UNCERTAIN | held |  | Identity/alias of Murrubber vs Murubber, and company physical business address. |
| 47 | STILL_UNCERTAIN | held |  | Independent company identity, polymer activity, physical PIC-18 business address and address-exact county; candidate route unavailable or insufficient. |
| 48 | STILL_UNCERTAIN | held |  | Independent company identity, polymer activity, physical PIC-18 business address and address-exact county; candidate route unavailable or insufficient. |
| 49 | STILL_UNCERTAIN | held |  | Owner ruling on print finishing/laminating scope and exact physical establishment. |
| 50 | STILL_UNCERTAIN | held |  | Independent company identity, polymer activity, physical PIC-18 business address and address-exact county; candidate route unavailable or insufficient. |
| 51 | STILL_UNCERTAIN | held |  | Resolve spelling variant against rank 46 before creation. |
| 52 | STILL_UNCERTAIN | held |  | Resolve Technoform subsidiary vs held parent and exact Ohio site. |
| 53 | STILL_UNCERTAIN | held |  | Independent company identity, polymer activity, physical PIC-18 business address and address-exact county; candidate route unavailable or insufficient. |
| 54 | STILL_UNCERTAIN | held |  | Independent company identity, polymer activity, physical PIC-18 business address and address-exact county; candidate route unavailable or insufficient. |
| 55 | STILL_UNCERTAIN | held |  | Independent company identity, polymer activity, physical PIC-18 business address and address-exact county; candidate route unavailable or insufficient. |
| 56 | DUPLICATE_OF | held | ORG-001089 | Alias follow-up: confirm and bank borrower spelling against held record; no existing row edited. |
| 57 | STILL_UNCERTAIN | held |  | Independent company identity, polymer activity, physical PIC-18 business address and address-exact county; candidate route unavailable or insufficient. |
| 58 | STILL_UNCERTAIN | held |  | Correct Ohio company identity; guessed domain reaches Japanese company. |
| 59 | STILL_UNCERTAIN | held |  | Independent company identity, polymer activity, physical PIC-18 business address and address-exact county; candidate route unavailable or insufficient. |
| 60 | DUPLICATE_OF | held | ORG-000352 | Alias follow-up: confirm and bank borrower spelling against held record; no existing row edited. |
| 61 | STILL_UNCERTAIN | held |  | Independent company identity, polymer activity, physical PIC-18 business address and address-exact county; candidate route unavailable or insufficient. |
| 62 | STILL_UNCERTAIN | held |  | Correct Ohio operator identity; guessed route reaches Washington transporter. |
| 63 | STILL_UNCERTAIN | held |  | Independent company identity, polymer activity, physical PIC-18 business address and address-exact county; candidate route unavailable or insufficient. |
| 64 | STILL_UNCERTAIN | held |  | Zenex acquisition/alias and held-parent check; no closure inference. |
| 65 | STILL_UNCERTAIN | held |  | GMR-Kent dba Industrial Molded Plastics identity; exact operator and own site. |
| 66 | STILL_UNCERTAIN | held |  | Independent company identity, polymer activity, physical PIC-18 business address and address-exact county; candidate route unavailable or insufficient. |
| 67 | STILL_UNCERTAIN | held |  | Intellipak/Berlin Packaging alias and held-parent identity; redirect alone insufficient. |
| 68 | STILL_UNCERTAIN | held |  | Correct Ohio legal entity; guessed route reaches unrelated law practice. |
| 69 | STILL_UNCERTAIN | held |  | Current operator identity after auction lead; dated company/federal evidence; no closure inference. |
| 70 | STILL_UNCERTAIN | held |  | Independent company identity, polymer activity, physical PIC-18 business address and address-exact county; candidate route unavailable or insufficient. |
| 71 | STILL_UNCERTAIN | held |  | Owner scope decision for soldering flux formulations. |
| 72 | STILL_UNCERTAIN | held |  | Exact Akron operator identity; guessed route names New Albany Indiana business. |
| 73 | STILL_UNCERTAIN | held |  | Exact Akron operator identity and alias relationship to rank 72. |
| 74 | STILL_UNCERTAIN | held |  | Polymer-specific scope ruling for soap/salve maker. |
| 75 | STILL_UNCERTAIN | held |  | Independent company identity, polymer activity, physical PIC-18 business address and address-exact county; candidate route unavailable or insufficient. |
| 76 | STILL_UNCERTAIN | held |  | Independent company identity, polymer activity, physical PIC-18 business address and address-exact county; candidate route unavailable or insufficient. |
| 77 | STILL_UNCERTAIN | held |  | Correct Conneaut operator; guessed route names unrelated port-service business. |
| 78 | STILL_UNCERTAIN | held |  | Independent company identity, polymer activity, physical PIC-18 business address and address-exact county; candidate route unavailable or insufficient. |
| 79 | STILL_UNCERTAIN | held |  | Own-manufacturing versus contract/sales-only evidence and exact Ohio street. |
| 80 | STILL_UNCERTAIN | held |  | Correct Cleveland Specialty Products operator; guessed route names inspection-services business. |

## Replay and verification

`python3 tasks/pic18-discovery-leads-2026-11-16/frame.py` independently rebuilds the supplied lead union and rank order.
`python3 tasks/pic18-discovery-leads-2026-11-16/build.py --apply` preflights all IDs/headers and uses `scripts/shard_io.py append_sorted`; missing, changed or colliding IDs cannot overwrite held rows. Pre-pass shard backups are in controller persistence under `pre-pass/`.
`python3 tasks/pic18-discovery-leads-2026-11-16/check.py` recomputes counts/coverage, exact raw quotes, county and byte-identical replay; missing verdict, repeated rank and invented quote controls must fail.
Required pre-push checks: `python3 scripts/validate.py`, `python3 scripts/check_row_loss.py --base origin/main`, `python3 scripts/export_vocab.py --check`. No shared scripts changed.

## Proposed follow-ups

- Resolve each held identity/scope/address fact above with primary evidence; do not convert route failures into rejections.
- Resolve the 180-registration SAM filter against the scout's narrower intended city/code frame before expanding beyond this fixed top 80.
- Resolve near-spelling aliases (including Murubber/Murrubber) before treating the broader union as unique companies.
- Confirm a manufacturing establishment for MVP independently; the added headquarters record does not establish one.
- Controller supplies independent multi-family review before merge. No council calls or other-worker messages made under contract rule 3.

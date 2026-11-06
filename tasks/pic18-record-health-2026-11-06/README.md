# L4 PIC-18 record health, 2026-11-06

First user: Atlas campaign controller / PIC analyst, using the baseline now. Non-use finding date: 2026-12-15 (campaign T1 checkpoint). The controller owns task commitments and status.

Acceptance: reproducible organization-grain T1, tested matching, append-only evidence for every changed cell, validator zero errors, and Codex + independent family deep refutation before PR. No new entities or status/ring/vocabulary changes.

## Measure

Baseline commit `bd57a08dfe87bce7ee82894ae02eb9212200205c`: **428/632 PIC-18 Ring 1–2 organizations (67.72%)** free of blocking gaps. After this pass: **431/632 (68.20%)**. `health_before.csv` is the frozen baseline; `health.csv` is the current output.

Denominator: distinct organizations with at least one exactly `active` site, site ring 1 or 2, state OH, county in `scripts/regions.py` PIC18. Ecosystem-owned sites are outside organization grain. Duplicate peers include all live organization shards (exclude closed/merged/acquired), using shared CLI domain/subdomain and legal-name normalization, or active-site normalized street + city + state. No inferred merge is performed. `none_found` is missing website, never a matching domain. Blank keys do not match. Related parents/divisions and co-location can trigger probable-duplicate review; flags are deliberately not legal identity verdicts. Capabilities count org or any held site, as requested; historical/free-text capability presence counts as presence, not verified quality. Site-only off-vocab note fields do not count as controlled capabilities.

Baseline overlapping flags among **204 unhealthy organizations**: tier C/U 72; probable duplicate 31; no website 32; no processes/materials 117. Single-gap counts: tier 45, duplicate 25, website 9, capabilities 85. Largest gap class is capabilities; the controller requested a separate continuation PR targeting that class. Size bands are absent for the eight initial three-gap organizations, so no unsupported ranking by size is claimed.

## Applied

8 changed cells across 4 organization records: Sherwin-Williams tier C→A; Roppe parent_org_id; Pittsburgh Paint website/processes/materials; Faull website/materials/tier C→A. Twelve evidence rows EVD-170000–170011: existence 4, address 3, scope 3, parent 2. One generated parent_of edge REL-000400 from canonical Roppe parent column. Organization tiers among changed records after application: A 3, B 1. PPG already A: two new government_filing corroborations, no organization edit. No creates, site edits, registry edits or inclusion decisions.

Sources: PPG and Sherwin-Williams 2025 Form 10-K copies linked by their own investor pages (government_filing; period 2025-12-31, retrieved 2026-11-06); Roppe news page; Pittsburgh Paints corporate about/acquisition pages; Faull contact/about pages. Quotes re-fetched raw with curl browser UA, PDF text extracted with pdftotext. SEC direct routes returned blocking pages; Jina returned an authentication block; neither was used as negative evidence. Full source text and personal contact details are not committed. `refetch.py` reproduces raw retrieval into disposable /tmp files; it fails closed on any route failure. Matching reuses the existing record-fix `has` function, not a new quote algorithm.

## Holds and existing dispositions

| Record | Verdict | Settling fact / recommendation |
|---|---|---|
| HEXPOL ORG-002044 / ORG-000103 | STILL_UNCERTAIN | Already merged by an earlier pass, generated lineage edge exists. Legacy narrative cites plant identity, not dated same-legal-entity proof. Hold any new merge/re-graining; obtain dated entity proof. Existing status untouched. |
| AltraSet ORG-001327 / Mar-Bal ORG-000430 | VERIFIED | Already linked with EVD-077005 and REL-000344; no edit needed. |
| SITE-000818 / SITE-001925 | DUPLICATE_OF | SITE-000818 already closed/tombstoned duplicate of held SITE-001925; same address documented by prior pass. No new status decision or data edit. |
| Permatex ORG-000138 → ITW | STILL_UNCERTAIN | Illinois Tool Works legal parent endpoint not held; ITW business units are not that legal parent. Hold link under both-endpoints-held rule. |
| PPG / Sherwin Exhibit 21 | STILL_UNCERTAIN | Item 2 and legal identity fetched raw. Separate Exhibit 21 content blocked at SEC; report index is not a subsidiary list. No subsidiary edges inferred. Obtain raw Exhibit 21 if a specific parent linkage is proposed. |
| Pittsburgh Paint ORG-001470 Huron address | STILL_UNCERTAIN | Corporate page proves identity/products/acquisition, not Huron establishment address. Hold address/HQ correction; obtain current own-site Huron street evidence. AIP named parent corroborated, no unheld parent ID minted. |
| D & D ORG-000014 / Custom Plastic Extrusions ORG-000066 | STILL_UNCERTAIN | No confidently matched own-domain primary page found in bounded search; obtain exact identity+location page. No closure inference. |
| Paddington ORG-000021 | STILL_UNCERTAIN | Prior domain cleared as for-sale; obtain current primary identity/location page. |
| Truco ORG-001721 | STILL_UNCERTAIN | Candidate domain failed fetch; old street 4301 Train vs candidate Cleveland 3033 W44 identity unresolved. Obtain current operator/address bridge. |
| Endura ORG-001726 | STILL_UNCERTAIN | Candidate enduraplastics.com presents Chesterland PO box, not held Kirtland establishment; obtain explicit identity/address bridge to endura.com. |
| Lawrence / Tristan ORG-001920 / ORG-001944 | STILL_UNCERTAIN | Obtain current primary identity/activity at held address; no current primary page established. |
| Potters ORG-001921 | STILL_UNCERTAIN | Current corporate site names Malvern HQ, held legacy row names Cleveland. Hold website/parent-grain linkage until establishment/identity bridge is proven; no silent HQ move. |
| Akron Polymer Solutions ORG-000049 / Chemigon ORG-000017 | STILL_UNCERTAIN | APS graphene wording does not establish a controlled polymer material without interpretation; Chemigon redirects to an Odoo typo page. Obtain explicit controlled capability witness; do not self-rule scope. |

## Checks

```
python3 tasks/pic18-record-health-2026-11-06/refetch.py
python3 tasks/pic18-record-health-2026-11-06/build.py --raw-check
python3 tasks/pic18-record-health-2026-11-06/check.py
python3 tasks/pic18-record-health-2026-11-06/health.py --self-check
python3 scripts/validate.py
```

`health.py --self-check`: passed (domain/name/street, geography, site capabilities, dead peers, missing website defect). Known-answer checks before use: CLI normalizers on synthetic Acme Inc/LLC, example.com/www, Main Street/St; raw matcher on PPG exact legal name, One PPG Place, Item 2 Properties; negative Sherwin-on-PPG check rejected. Full raw-check: 12/12 quotes present. `check.py`: passed, 8/8 changed cells evidenced and 12/12 evidence rows append-only. Validator: 0 errors, existing warnings. `scripts/` untouched, so no scripts pytest requirement triggered.

Builder re-run: identical data hashes (idempotent). It preserves unrelated columns, refuses drift and evidence/relationship ID collisions, and derives tier only from evidence strengths per V-25; missing legacy claims remain visible. `append_sorted` reorders existing out-of-order evidence rows in PA; `check.py` proves their cell content remains identical.

Reviews: pending.

Takeover atlas-L4b-pic18-health: repeated health self-check, check.py, seven-source raw refetch, build.py --raw-check (12/12), and validate.py (zero errors) successfully. Prior council output files were empty. Controller BOARD 05:55 supersedes council-only routing and authorizes draft PR before clerk review. Reviews remain pending; no completion claim yet.

Refresh on main 9489b60: controller explicitly authorized taking main's LF federal-frame files (#139), then merging main and replaying data builder (supersedes earlier no-touch constraint for this integration only). Original dirty bytes preserved in /tmp/l4b-inherited-federal-backup. Net federal-frame diff vs main is zero. All main data taken before builder replay; exact-delta check now compares against refreshed main. T1 remains431/632; original frozen campaign baseline unchanged. Validate0 and raw packet checks pass.

Codex clerk verdict: APPROVE, zero blocking findings (reviewed04592d0, 2026-11-06). Independent DuckDB denominator632; all12 quotes across7URLs freshly matched; V25 and every named check pass; temporary fresh-main replay loses zero keys; builder drift injection rejects before writes. Integration qualification subsequently addressed by25c81b2's main9489b60 replay and renewed exact-delta/validate checks. Grok verdict still pending. Clerk detail retained by controller in reviews/133-clerk-codex-2.md. Neither draft is called Done or merge-authorized.

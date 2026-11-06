# IFS Coatings parent of record — 2026-11-06

Controller task C (thr_9i2c6byhcz). Question: is IFS Coatings, Inc. a separate company from Ifs Industries Inc. (ORG-002633, Reading PA, adhesives), and who operates the Ardmore, OK site that main holds as SITE-006097 under ORG-002633? First user: the campaign integrator, 2026-11-06. If nothing uses this record by 2026-11-13, record that as a non-use finding.

## Verdict: VERIFIED. SITE-006097 is operated by IFS Coatings, Inc., not Ifs Industries.

| Fact | Primary witness |
|---|---|
| IFS Coatings, Inc. runs a multi-site ISO 9001 system. Its central functions are at 3601 North I-35, Gainesville TX, and it has a second site at **3430 Cypert Way, Ardmore, OK 73401, "Manufacturing & warehousing"** | Own ISO 9001:2015 certificate 112094.00 issued by DEKRA on 2026-04-14 and hosted on ifscoatings.com ([PDF](https://www.ifscoatings.com/downloads/IFS-Coatings-Inc.-9001-Certificate-Exp-April-13-2029-2026.pdf), sha256 `5c32583138f5…cd12a1`; text in `ifs-coatings-iso9001-certificate.txt`) |
| Ardmore and Gainesville file under one employer: ITA 73266 "IFS Coatings, Inc. (Oklahoma)" and ITA 73137 "IFS Coatings, Inc.(Texas)" share EIN 233013356 | OSHA ITA 300A CY2025 (tasks/osha-ita-2026-11-01/establishments.csv) |
| Ifs Industries is a different employer: EIN 231628033 (ITA 962374 Reading, 80910 and 305593 Garland TX) | Same extract |
| Ifs Industries' own pages list adhesives, polyurethanes, polymers and corrugated additives. Its manufacturing is listed as Garland TX, Reading PA, Montreal and Craiova (Romania); no Oklahoma plant and no IFS Coatings | Wayback captures of ifscos.com from 2026-07-11, [home](http://web.archive.org/web/20260711110903/https://ifscos.com/) and [contact](http://web.archive.org/web/20260711121526/https://ifscos.com/contact-us) (persisted text, phone and email removed) |

The 2026-11-04 placement was the OK skimpy wave's own flagged judgment call. Its README says: "placed under held ORG-002633 Ifs Industries Inc. (Reading PA) as the same powder-coatings group - integrator check". Its parent evidence row, EVD-023985, cites an FRS record that names only "IFS COATINGS, INC" and no parent. That row stays as it is (evidence is append-only). It is superseded by EVD-332008 and EVD-332009.

## Change (applied by `build.py`, idempotent)

- **Create ORG-013500 "IFS Coatings, Inc."** in `organizations_TX.csv`, at tier C from birth (AGENTS §3 step 5). HQ is Gainesville, TX. `hq_county` is left blank, following TX org precedent. NAICS 325510 comes from the ITA filing; ring 2 `coating_formulation`; website ifscoatings.com; `parent_org_id` is empty. Dedupe (`atlas.py dedupe-check`: domain, name, street 3601 N I-35, trade names and notes) found 0 hits at every step.
- **SITE-006097:** four cells change. `org_id` moves from ORG-002633 to ORG-013500. `sources` gains the certificate. `notes` gains a dated re-point note that keeps the old link on record. `last_verified` becomes 2026-11-06. Nothing is tombstoned or deleted. ORG-002633 itself is untouched and keeps SITE-002623 Reading, its TRI link and its tier1 basis.
- **11 evidence rows, EVD-332000 to EVD-332010, all `supports_C`.** Seven are on the org: existence, address, activity, scope, code, liveness, and entity_type `corporation_private`. Four are on the site: existence, two parent rows (the certificate and the shared ITA EIN) and activity. Own-site quotes were re-checked raw, in order, with the house matcher; government rows were checked against the ITA extract fields.

**Ring.** This applies SCHEMA; it is not a new scope ruling. SCHEMA §2 Ring 2 includes paints and coatings "by deliberate PIC decision" where a polymer resin is the binder. §2.1 lists 325510 as P* for manufacturers. SITE-006097 already carries `ring_primary 2 / coating_formulation` on main, and the new org takes on that existing ring. If a reviewer reads the create as an owner scope item, the fallback is to withdraw ORG-013500 and its seven org rows, revert the site cells, and keep only the wrong-link flag. The PR can be cut to that shape without a rewrite.

**§5.2.** IFS Coatings gets its own org record either way. If it is an unrelated company, it needs one. If it were an IFS Industries subsidiary, it passes all three §5.2 tests: its own trade name, its own HQ (Gainesville), and its own website.

## Holds and settling facts

- **parent_org_id stays empty.** IFS Coatings calls itself "privately owned" and Ifs Industries calls itself "family-owned", and neither names the other. Settling fact for a parent link: a primary statement of common ownership from either company, or a state SOS filing whose officers or registered agent overlap. Neither SOS was consulted: the operator question was settled without them, and a parent link is not proposed.
- **Gainesville plant.** LF-TX-00505 (held in merged #170) can now settle: its open fact, the parent of record, is ORG-013500. The Gainesville site create belongs to that lane's follow-up, not this PR.

## Fetches (cap ~6 per organization)

- IFS Coatings: 1 new fetch (the certificate PDF), plus 3 pages reused from #170's persisted fetches (about, home, facilities).
- Ifs Industries: 3 fetches. Live ifscos.com failed: the server omits its intermediate TLS certificate and then redirects to itself in a loop. That is availability only. The Wayback home and contact captures loaded.

The witness texts are in `thread-storage/thr_9i2c6byhcz/2026-11-06-atlas/persist/ifs-coatings-parent-2026-11-06/`, and the certificate text is also committed here.

## Checks

- `python3 tasks/ifs-coatings-parent-2026-11-06/check.py`: PASS. Against the merge-base, only the four data files change. There is exactly one new org, the site edit is exactly the four cells listed, and the 11 evidence rows are exactly the witnessed ones. All 11 raw witnesses re-check. Three injected defects fail: a fabricated quote, IFS Industries' EIN given as the operator's, and the site left at ORG-002633. A rebuild leaves the bytes unchanged.
- `python3 scripts/validate.py`: OK, 0 errors.
- `python3 scripts/check_row_loss.py --base origin/main`: OK.
- No council review was run (controller override). The controller routes review.

# P1 ATLAS-8 and PIC-18 contradictions

Built by: Codex GPT-6.2 Sol

ATLAS-8 and contradiction-queue correction pass, 2026-11-23. Integrator of record and first user of the hand-off are atlas-p1-integrator-1 and the Atlas controller, respectively. The controller uses the claim count when reviewing the PR. An unused hand-off at the next P1 review is a finding.

## Acceptance criteria

Every counted claim must trace to an in-scope sealed verdict, with the combined Claude-built and PIC-18 packets counted once. Every canonical data edit must match a corrected or withdrawn claim. Each sourced correction must have a new binding-gate PASS witness. The validator and row-loss guard must pass, with no additions or removals of canonical records. The two independent families review the final PR head.

## Results

| Published claim unit | PIC-18 | Rest | Total |
| --- | ---: | ---: | ---: |
| Reader-verified claims | 350 | 243 | 593 |
| Corrected cells | 6 | 0 | 6 |
| Withdrawn cells | 4 | 6 | 10 |
| Verified rule re-derivations | 860 | 547 | 1,407 |
| Total unique claim rows | 1,220 | 796 | 2,016 |

The 1,407 rule checks are 1,016 `entity_type` and 391 `hq_in_scope` cells. They re-derive from stored legal names and counties, so a wrong legal name or county could still pass. One `entity_type` key also has a matching reader verdict and is counted in the rule line once. Geography follows the frozen ATLAS-8 frame and the PIC-18 contradiction assignment.

| Reader packet | Units | VERIFIED | REJECT | STILL_UNCERTAIN |
| --- | ---: | ---: | ---: | ---: |
| #418 street and ZIP cells | 209 | 190 | 4 | 15 |
| Other ATLAS-8 cells | 61 | 54 | 6 | 1 |
| Program and ecosystem claims and people cells | 184 | 157 | 1 | 26 |
| PIC-18 contradiction sites, one field per site | 53 | 47 | 3 | 3 |
| Claude-built ATLAS-8 and contradiction claims | 194 | 152 | 0 | 42 |

The combined Claude-built packet has 220 verdicts, including 26 ATLAS-9 and blind evidence or link readings outside this P1 pass. Its 84-cell subpacket is a duplicate. The people record verdicts use audit 12 B8, which treats sources, verification tier and last verified as bookkeeping. Sixty whole-record people verdicts and 20 whole-record program verdicts use the packets' `*record*` key. The 796 supporting people field readings are checked against those record verdicts and are excluded from the count.

## Applied dispositions

- Correct the street on SITE-000133, SITE-000336, SITE-000677, SITE-001438 and SITE-001484 and the ZIP on SITE-001484. Five dated OSHA 300A physical-address witnesses support these six cells and carry `supports_A` for the address claim. The two SITE-001484 cells share the same witness. These observations do not change the records' verification tiers.
- Withdraw the streets on SITE-000156, SITE-001416, SITE-001579 and SITE-001725. The SITE-001579 reader sourced `549 E Washington Street` from the S4 Medical contact page. Main's extractor returns empty text because it excludes the document body based on its CSS class. Keep that replacement queued pending proof support, per the controller's 2026-11-23 decision. No ZIP was rejected for that record.
- Withdraw the unsupported specialty tags from six cells on four programs per the owner's round 20 decision in `DECISIONS.md`. PROG-000362 loses `biomedical_polymers`; PROG-000377 loses `rheology` and `polymer_physics`; PROG-000378 loses `composites_frp` in both tag fields; PROG-000384 loses `liquid_crystals`, `characterization_methods` and `polymer_physics` from research areas and `liquid_crystals` from specialty materials. The separate credential question for PROG-000384 remains open. Its remaining `polymer_synthesis` tag is carried forward with no new observation.
- The four SAM-only street witnesses pass R-SAM. Raw fields 24 and 122 show no D&B source. Update dates are 2026-03-03 for SITE-000037, 2026-06-12 for SITE-000592, 2026-09-01 for SITE-001611 and 2026-06-26 for SITE-001723. This also covers the two ZIP claims read from those witnesses.
- Six historical street claims remain verified as place facts under the controller's ruling. SITE-000079 uses OSHA 2016, SITE-000142 and SITE-000603 and SITE-001992 use ITA 2017, SITE-001802 uses ITA 2018, and SITE-000170 uses ITA 2019.

## Open queue

[OPEN_QUEUE.csv](OPEN_QUEUE.csv) lists each unresolved key. Its packet-only uncertainty rows use the original sealed packets for deciding and settling facts.

- SITE-001661 street has two different verdicts. The #441 reader could not distinguish the Kenmore Boulevard and Miller Avenue plant records. The contradiction reader verified Kenmore against EPA FRS and RCRA. The controller gets the unresolved key.
- The controller held ORG-000503 `polymer_program_name` together with PROG-000014 `program_name`. Fixing only the rollup would fail V-16, and the binding gate returns `other_table` for program evidence even before own-site proof replay.
- Potential record changes for controller triage are the #418 reader's duplicate or co-location pairs (SITE-000281/000463, SITE-000385/004436, SITE-000592/001487, SITE-001399/003477, SITE-002021/001905 and SITE-000093/000049), the shared department question for PROG-000383/000361 and the degree grain question for PROG-000368. The contradiction reader noted additional facility leads on SITE-000001, SITE-000043, SITE-000133, SITE-000676, SITE-001522, SITE-001530, SITE-001531, SITE-001560, SITE-001661, SITE-001680, SITE-002125 and SITE-002001; the CREO operating-status question on SITE-001438; and operator or name questions on SITE-000044, SITE-000202, SITE-000383, SITE-001506 and SITE-001573. These stay with the controller.
- Other follow-ups from the contradiction and people readers are SITE-000003 ZIP and PERSON-000871 profile-link currency. The Swagelok facility grain on SITE-000156 needs an owner ruling before a replacement can be read into the record.

## Replay

Run from the repo root with the controller's sealed packet directory and an accessible shared store. The default paths are in `check.py`. Override them with `--packets` and `--store` if needed.

```sh
lockf -k /tmp/polymer-atlas-heavy.lock python3 -I tasks/p1-atlas8-corrections-2026-11-23/check.py
lockf -k /tmp/polymer-atlas-heavy.lock python3 scripts/validate.py
lockf -k /tmp/polymer-atlas-heavy.lock python3 scripts/check_row_loss.py --base origin/main
python3 scripts/check_evidence_binding.py --verify-proofs origin/main
python3 scripts/check_evidence_binding.py --provenance-since origin/main
```

The replay tests current field and record hashes against Git, reconstructs both disposition files and compares the full data delta against the PR base. `PACKETS.sha256` pins the packet files used by the replay. `INPUTS.sha256` pins the SAM extract and OSHA filings to the raw-store manifest. Canonical evidence remains append-only.

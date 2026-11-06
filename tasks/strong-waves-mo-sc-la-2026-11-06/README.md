# L3 STRONG wave — Missouri, South Carolina, Louisiana

Scope: 36 lead-fusion STRONG establishment clusters, MO 15 / SC 14 / LA 7. `verdicts.csv` is exhaustive, not a sampling frame.
The original recipe is `../mi-strong-wave-2026-11-04/`; the binding lane acceptance criteria are in `LANE_BRIEF.md`.

Sources: public operator pages selected in `research.py`, re-fetched in `rawcheck.csv`; OSHA ITA CY2025 establishments,
OSHA inspection records and DOL EFAST2 sponsor packets already held under tasks/. ECHO/FRS identifiers are notes only;
no FRS REST requests were made (shared-IP restriction from controller 2026-11-06, recorded on BOARD).

`dedupe.json` records atlas.py's four steps, including domain, normalized legal/trade names, street and successor chains.
Street matching additionally ignores mailing-city and ZIP variations. JM Eagle ORG-002260 is tombstoned: Columbia attaches
to survivor ORG-002261. Insulfab uses held ORG-006173; Nike uses ORG-003555; Yokohama TWS uses ORG-001336.
The Aurora substring in Polyply notes is a lead, not proof of common legal identity; the Aurora cases remain held.
No organizations were merged, no ownership/status changes were applied, and no inclusion-log borderline create was made.

## Build and checks

Before applying: `python3 tasks/strong-waves-mo-sc-la-2026-11-06/prepare.py`, then `adjudicate.py` in that directory.
The three known published witnesses (TG Missouri, Manchester Packaging, Insulfab) passed 3/3; appending a nonexistent token
to each quote failed 3/3. Script/style content is excluded. Failed routes are not evidence of absence.

Apply each state: `python3 tasks/strong-waves-mo-sc-la-2026-11-06/build.py --state MO --apply` (then SC, LA).
IDs are deterministic input-index offsets in the reserved block. `append_sorted` is used for every append. Reapplication
asserts exact equality for held IDs instead of overwriting evidence. On fresh main, re-run adjudication and inspect new
dedupe hits before re-running the builder; do not merge CSV conflicts by hand.

Named checks: `python3 scripts/validate.py`; `python3 tasks/strong-waves-mo-sc-la-2026-11-06/check.py`.
`check.py` injects three missing/duplicate census defects and requires all three to fail. It also checks exact creates,
unique IDs and the per-state NAICS 326 strict-site/QCEW rise using `scripts/build_qcew_denominators.py::atlas_numerators`.
Denominator = QCEW 2023 private establishments, NAICS 326: MO 368, SC 406, LA 117; held official-source denominator file.
A ratio is not matched establishment coverage. No QCEW downloads or denominator changes are needed.

## Holds

`holds.csv` is the holds table: one cluster and named settling fact per row. Fetch availability holds remain explicit.
Agfa is held pending dated closure outcome + address-matched EFAST2, never rejected solely on a closure headline.
PIDC is excluded under owner B-SCOPE (2026-11-04), inorganic alumina output; deciding regulator source is in its verdict.
County/HQ are not inferred from postal city or plant location. Blank fields remain honest unknowns.

## Pass journal and reviews

Application counts, before/after ratios and independent review verdicts are appended below before PR publication.

- Missouri application: 7 new organizations (tier C), 9 new establishments {'C': 1, 'B': 8}; 98 evidence observations. `validate.py`: zero errors. Builder replay: passed.

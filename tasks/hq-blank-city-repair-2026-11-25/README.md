# Repair of #563: clear the Kenda HQ fill (audit FAIL)

Built by: Claude Code (Anthropic)

Claimed by atlas-p1-hq-blank-city-repair on 2026-11-25. First user: the Atlas controller, whose audit 13 smoke runner refuses a frame record that declares `hq_county` with a blank `hq_city`. Check for use by 2026-12-01. Base `5164203c`.

## Why

The Codex census audit of label `claude-code hq-blank-city-2026-11-25` (PR #563) came back FAIL on one cell group: the four HQ cells #563 filled on ORG-000197 Kenda American Technology Center (`hq_city` Green, `hq_state` OH, `hq_country` US, `hq_in_scope` ne_ohio). The cited capture (EVD-483143) lists the 5801 Mayfair Road centre under "Offices" and never calls it the headquarters, and the same organization holds SITE-000988 (Reynoldsburg), whose notes call it a distribution/HQ establishment. The seven withdrawals passed. This PR follows the 2026-11-23 precedent (audit of #486, settled by the repair #493): a failed audit is settled by a repair PR, not by landing the FAIL record. The audit's `AUDIT.md` for the repaired batch is added after this PR's data change, unchanged, by the controller's instruction.

## Rule applied

The rule of #563 for the seven organizations whose HQ no readable source stated within its effort cap: **no HQ cells and no county**. Kenda is the eighth. No reading and no new evidence.

## Result

Unit: organization row ORG-000197 in `data/organizations_*.csv`; evidence rows in `data/evidence_organizations_*.csv`.

- **Cleared, 5 cells:** `hq_city` Green, `hq_state` OH, `hq_country` US, `hq_in_scope` ne_ohio (the four #563 filled) and `hq_county` Summit (held before #563, withdrawn like the other seven). `CLAIMS_CHECKED.csv` holds one `withdrawn` row per cell.
- **Moved, `organizations_OH` to `organizations_US`:** with `hq_state` and `hq_country` blank, SCHEMA Appendix C §2 places a record in the residual shard `US`, which is where #563's base (`7ea75205`) held it. Its two evidence rows move with it, unchanged: EVD-421274 (back to the end of `evidence_organizations_US`, where it stood) and EVD-483143. EVD-483143 stays as the record of what the page prints at that street (it does not call the centre the headquarters, and nothing in the record now rests on it as an HQ statement); its archive link stays. No evidence row, registry link or archive link is added or lost; a row that moves shards is counted as an added row by `check_pr_rules.py`, which reads each file on its own.
- **Noted:** one dated entry appended to the notes of ORG-000197 (the old notes kept whole). The physical location (Green, Summit County) stays on SITE-000204 and in the county note.
- **Unchanged:** every other cell of every other record, all site rows, the seven other withdrawals of #563.

After this PR no organization holds `hq_county` with a blank `hq_city` (the audit 13 frame).

## Settles it

A page or filing that names the headquarters of Kenda American Technology Center, or of its US parent. Until then the HQ cells stay blank.

## Check

`python3 tasks/hq-blank-city-repair-2026-11-25/check.py` is the named check, run against the merge-base with `origin/main` (or a base given as its argument). It asserts that the only changed organization cells are the five cleared ones plus the notes of ORG-000197, that the notes are the old notes plus one 2026-11-25 entry, that `CLAIMS_CHECKED.csv` is exactly the five withdrawn rows, that no organization holds a county without a city, that ORG-000197 sits in the shard Appendix C gives it and no other organization changed shard, that no evidence row is added, lost or altered and that Kenda's two travel with it, that `archive_links.csv` is unchanged, and that only allowed files changed. It catches 19 planted defects, one or more per assertion (an extra changed cell, another organization's cell, a ninth county cleared, a cleared cell left, a refilled city, a county with no city, the move missing, a move to a state shard, a lost note, an overwritten note, a dropped or mislabelled claim row, a ninth claim, an evidence row lost, left behind, added or altered, a dropped archive link, a changed site file). `python3 scripts/validate.py` passes.

`INPUTS.sha256` repeats the one line of #563's: this PR reads no input and adds no evidence row, but `check_pr_rules.py` counts a row that moves between shard files as added (2 rows here), so rule 6 asks for the file. The line is the capture behind EVD-483143, already in the shared store (hash verified there on 2026-11-25); EVD-421274's input is recorded with the burn-down batch that minted it (#448).

Not checked: this repair reads no source; whether Kenda's actual headquarters is Green, N. Canton or Reynoldsburg is not decided here.

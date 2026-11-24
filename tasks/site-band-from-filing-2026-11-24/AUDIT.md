# Audit record for the site band repair from bound filings

Label: atlas-p1 site-band-from-filing-2026-11-24
Result: PASS
Sample: census of all 12 appended size evidence rows, 12 changed employee_band_site cells, their 12 dated notes and 36 CLAIMS_CHECKED.csv rows in PR #544. No sample was drawn.
Reviewers: Codex GPT-6.2 Astra and Gemini 4 Hydrogen approved head 2e5d831750a86a84badd56524eab54fd312f9dee. The builder was a separate Codex GPT-6.2 Astra thread; Gemini is the only reviewer from a different family.

Both reviewers replayed every corrected site against the checksummed
store files listed in `INPUTS.sha256`: the CY2025 OSHA ITA summary CSV
and the OSHA inspection archive. For each site they compared the
filing's establishment name, street, city and state with the site record,
and the filing's employee count with the new band under R13.

The binding gate passed all 12 evidence rows. `check.py`, `validate.py`
and the row-loss guard passed at the reviewed head.

The merged commit e2c7f07a22d64a49283db07af6c38f50ec6a8635 carries the
same 12 evidence rows, byte for byte, as the reviewed head, and the same
task folder.

## What this audit is not

It is not a second read beyond the two merge reviews. The reviews checked
the 11 hold dispositions; those sites received no edits or appended
evidence. The separate 104 PIC-18 bands that rest only on Form 5500
counts were outside scope.

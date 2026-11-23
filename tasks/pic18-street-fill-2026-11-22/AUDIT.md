# Audit record: PIC-18 street fill from OSHA files (PR #486), with the one-row repair (PR #493)

Label: codex pic18-street-fill-2026-11-22
Result: PASS
Sample: census, 13 of 13 evidence rows (EVD-483002, 483003, 483006, 483009, 483010, 483011, 483012, 483014, 483015, 483016, 483017, 483018, 483019), plus all 8 street cells and 5 size-band cells in edits.csv. No sampling.
Reviewers: Antigravity (Gemini 4 Hydrogen); Claude Sonnet 5.5. Neither built the batch (builder: Codex GPT-6.2 Sol).

## What was audited

Each reviewer, with its own code and not the packet's `build.py` or `check.py`, checked the 9 input files against
`INPUTS.sha256` (9 of 9 match), opened each row's cited raw record by path, archive member and row number, and compared:

- 13 of 13 rows reproduce from the raw files. The 8 street cells and 5 size-band cells on `main` equal the packet's
  edits; each band follows from the cited OSHA ITA annual average employment.
- `git diff 59d3197864607712e34555496a5e927e92c4b58c origin/main -- data/` was empty: `main` holds what was reviewed at #486.

## The split, and its repair

The two reviewers first disagreed on EVD-483012 (SITE-001455, Salem). Its OSHA inspection quote names the establishment
"AMERICAN STANDARD INC.", which the record holds only as a licensed brand and which its notes say does not operate the
plant. Gemini passed it under the held-name test; Sonnet failed it as a binding to a disclaimed operator. The street cell
itself was right: the 2025 OSHA ITA 300A row 352594, filed under the held legal name American Bath Group, carries the same
street.

Evidence rows are never edited (SCHEMA §4.13). PR #493 answers EVD-483012 with EVD-483020, a fresher `supports_A` row for
the same street citing ITA row 352594 at the held legal name. Both reviewers approved #493 at `f48af0e9` and, with
EVD-483020 in place, both grade this label PASS (Gemini: PASS before and after; Sonnet: PASS after the repair).

## What this audit is not

It does not re-check the 110 frame sites the packet did not fill, any live source, or whether American Bath Group still
operates the Salem plant: an OSHA inspection opened 2026-10-20 names American Standard Inc. at the same street, recorded
as a lead in `tasks/pic18-street-fill-repair-2026-11-23/README.md`, not a status or operator change. EVD-483012 itself
remains on `main`, unedited, answered by EVD-483020.

# Lane brief: Ohio (non-PIC-12) capability wave (2026-11-01)

**Packet lanes only.** A lane never edits `data/`, never allocates IDs, and never
commits or pushes (AGENTS.md §2 rules 7–8).

## Population

- **Pinned at:** commit `eb79f3b`.
- **Candidate filter:** active site rows in `data/sites_OH.csv` outside the
  PIC-12 counties, ring 1–2, with `processes` or `markets_served` blank, and a
  parent org with an `http` website. 636 rows qualify.
- **Assignments:** split round-robin into `oh_lane1_assignment.csv` …
  `oh_lane8_assignment.csv`.
- **Pennsylvania:** the 369 PA candidates under the same filter are in
  `pa_candidates.csv`, held for a later wave.

## Method

Exactly as in `tasks/wave-pic12-capabilities-2026-11-01/LANE_BRIEF.md`,
including its "Tranche 2" section. In summary:

- **Sources.** Use the company's own website only (`own_site`), with ≤ 6 fetches
  per site. Fetch with curl and keep the page text. Never quote from a WebFetch
  summary.
- **Quotes.** Each quote is ≤ 25 words, checked by script as a substring of the
  fetched text.
- **Values.** Use only vocab v1.7.6 values (`docs/schema/vocab.json`), one value
  per row. Anything else goes in a `*_other_note` row marked OFF-VOCAB.
- **Plant ties first.** Look for certificate annexes, plant pages and plant-named
  job postings. Org-scope values are never pushed down to a site.
- **Certifications (R3c).** Record only current certificates, or current pages
  that name a non-superseded edition.
- **Verdicts.** Exactly VERIFIED, STILL_UNCERTAIN or REJECT. A failed fetch is
  never closure evidence. No bot-wall workarounds: no faked user-agent, no TLS
  bypass, no captcha workarounds.
- **Privacy.** Never record personal emails, direct phones or individual names
  (AGENTS.md §6).
- **Scratch directory.** Use `/tmp/claude-0/wave-oh/lane<N>/` exclusively, and
  give fetched files per-site locked filenames. Earlier lanes lost data by
  running parallel fetches for one site that overwrote each other.

## Output per lane (in `oh_lane<N>/`)

- `packet.csv`
- `verdicts.csv`
- `REPORT.md`

Use the same columns as the PIC-12 wave. If your tool refuses to write
`REPORT.md`, return the full report as text.

# Process-wording lexicon pass (ATLAS-40, owner-controller instruction 2026-11-23)

Purpose: stop finding build and process wording one review at a time. One list, one test, one scan of every user-facing text surface.

## What changed in the code

- `scripts/build_site.py`: `BUILD_PROSE_RE` is now the full lexicon of process wording in descriptions (verification timing and "crawled",
  settling and "witness", fetch and HTTP status words, workflow verdicts, tier words, "opened" for a source site, the evidence ladder,
  queue and retry words). `PROCESS_WATCH_RE` is a wider net. `PROSE_ALLOW` lists ordinary uses (a street name, "Tier-1 supplier", a plant
  that opened in 1995, an OSHA inspection that opened on a date, "expert witness") with a reason each; the allowed span is removed before the list runs.
  `internal_wording` stays the one shared test that the pages, `graph.json`, `map-network.json`, `orgs.json`, `sites.json` and the release use.
- `published_role`: a researcher's published role line with build wording falls back to the vocabulary role (one hit on `experts.json`).
- `scripts/export_release.py`: a withheld description is also withheld where it is copied into another cell with its temporary id cut out (ORG-003111's notes).
- `scripts/test_site_release.py`: `ProcessLexiconTests` (fail on 5ad991eb: the new families, the named records, the role fallback, the copy without its id, and
  that no real description has a watch-list word that is neither withheld nor allowed; every allowance has a reason and is used by a real description).

## The scan (`scan.py`)

`python3 tasks/site-lexicon-2026-11-23/scan.py build/pages build/release tasks/site-lexicon-2026-11-23`

Surfaces: record-specific text of every built HTML page, every string in every built JSON file, the `directory.csv` and `prospects.csv` downloads, the
`description_1line` and `notes` columns of the release CSVs and of the bundled SQLite copy. `HITS.csv` lists every hit (surface, record, field, phrase,
status with the reason for an allowance, snippet). `before/` is the same scan, same lists, on the build of 5ad991eb. Notes cells are counted in `COUNTS.md`, not
listed (about 40,000 cells).

## Reading the hit list

- Real build prose in a description: now withheld (descriptions withheld, organizations + ecosystem records + programs: 206 -> 409 of 5,267 shown descriptions;
  organizations alone 204 -> 397). They include Gemini's 12 audit-timing ledes, the six "settles identity" ledes, ORG-001997, ORG-002044 and ORG-002045.
  A withheld description is withheld whole: about 190 of the new ones also describe the company, inside the process narrative; the repository CSV keeps them.
- Ordinary uses: `PROSE_ALLOW` (descriptions) and the scan's `LABEL_ALLOW` (non-description fields: the site's own "verification tier" and "last verified" labels,
  company, street and URL names the word-based blind-audit scan catches, suite numbers). Each has its reason in the status column.
- After: 0 SHOWN hits on every surface.

## Not done, owner decision

Notes cells are published as they are in the repository CSVs and the release (`notes` is the build narrative: "Created ... in integration pass 17 ..."). Cells with a
process-word hit in the release: organizations 4,673, sites 6,875, evidence 23,859 (counts in `COUNTS.md`). Only temporary ids and copies of withheld descriptions are
blanked there. Withholding or reducing notes in the release is a release-format and privacy-of-process choice: proposed for the owner, with the recommendation to
drop the `notes` column from the release's organization and site CSVs and keep it in the repository. Nothing was changed.

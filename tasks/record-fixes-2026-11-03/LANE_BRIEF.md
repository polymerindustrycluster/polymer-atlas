# Lane brief: targeted record fixes, 28 organizations (2026-11-03)

These are packet lanes (AGENTS.md §2 rule 7). **Never edit `data/` and never run git.** Write only
`tasks/record-fixes-2026-11-03/lanes/<lane>/` (`evidence.csv`, `fields.csv`, `duplicates.csv`, `NOTES.md`).

Read first:
- `docs/SCHEMA.md` §3.1 (processes) and §3.2 (materials). Use **only** the terms listed there.
- §4.1 (tiers) and §4.13 (evidence classes and ceilings).

Each input row is one organization. `needs` says what is missing, and you do only that:
- **`tier C` / `tier U`, or `org evidence missing: …`.** Find evidence for each missing must-have claim. Give one row
  per claim in `evidence.csv`.
  - `existence`: a page names the legal or trade name.
  - `address`: a page prints the HQ or Ohio site street and city.
  - `scope`: a page states the polymer activity: molding, compounding, resin, rubber, composites, coatings, and so on.
  - `code`: a page states the NAICS or SIC code, such as a 10-K cover or a SAM or OSHA record. If none exists, skip it;
    never infer a code.
  - Prefer the company's own site (`own_site`) or an SEC or state filing (`government_filing`). Press is allowed but
    capped at supports_B. Never use directories or aggregators (D&B, ZoomInfo, Manta, OpenCorporates, LinkedIn).
- **`no processes` / `no materials`.** From the company's own site, list each §3.1 or §3.2 term that the page
  **explicitly** states. Give one `fields.csv` row per term, with its quote.
  - Never infer. "Plastic parts" is not `injection_molding`, and "resins" is not a family.
  - If the site states nothing mappable, say so in NOTES.
- **`no website`.** Give the official domain in `fields.csv` (`field=website`). The page you cite must be that
  company's own site and name it.
- **`possible duplicate: …`.** Read both records' own pages and decide the relationship.

  | verdict | meaning |
  |-|-|
  | `SAME_ENTITY` | the same legal entity |
  | `PARENT_CHILD` | one owns the other; say which |
  | `SIBLING_DIVISIONS` | distinct units under the same parent |
  | `UNRELATED` | not connected |
  | `STILL_UNCERTAIN` | name the fact that would settle it |

  Give the deciding quote and URL in `duplicates.csv`. **Do not propose merges yourself.** The integrator decides
  merges, and when in doubt they link and flag rather than merge.

About 6 fetches per organization. A failed fetch is never evidence. No emails, phones or personal data.

## Output files (UTF-8, comma, quoted as needed)
- `evidence.csv`: `org_id, claim_type, source_class, source_url, quote, claim_detail`
  - `quote` is at most 25 words, one continuous span copied **exactly** from the page.
  - `claim_detail` is one sentence.
- `fields.csv`: `org_id, field, value, source_url, quote`
  - `field` is `processes`, `materials` or `website`.
  - `value` is one vocabulary term per row.
- `duplicates.csv`: `org_id, other_org_id, verdict, source_url, quote, note`
- `NOTES.md`: 5–15 lines with counts, plus anything odd, such as a closure or a change of owner.

**Quotes are re-checked word for word.** The integrator re-fetches every URL raw and keeps a row only if the quote
appears verbatim. WebFetch returns a model's summary of the page, so copy short exact spans (8–20 words) and flag any
you are unsure of.

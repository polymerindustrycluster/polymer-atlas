# Lane brief: STRONG wave, IL (2026-11-04)

These are packet lanes (AGENTS.md §2 rule 7). **Never edit `data/` and never run git.** Write only
`tasks/il-strong-wave-2026-11-04/lanes/<lane>/verdicts.csv` and `NOTES.md`.

**Input.** Each row is a lead-fusion STRONG cluster: an IL establishment that three or more independent federal
families record, drawn from OSHA ITA, OSHA inspections, EPA ECHO/FRS and Form 5500
(`tasks/lead-fusion-2026-11-01/REPORT.md`).
- `sources_with_ids` gives each source ID.
- `current_atlas_hits` lists dedupe hits against today's Atlas (step 2 = name, step 3 = street).

Federal rows are **leads**. A NAICS code never settles scope.

Read first: AGENTS.md §2–§4 and docs/SCHEMA.md §1–§2, which cover rings, the scope test and the NAICS map, plus §3.1
and §3.2 for the vocabularies.

## Per candidate (about 6 fetches)
1. **Dedupe.** If `current_atlas_hits` names a site at this street, the verdict is `DUPLICATE_OF:<SITE-id>`. If it
   names an organization only, decide whether this is a new site under that organization (`held_org_id`) or a
   different company.
2. **Identity and activity, from the company's own site.** Find a page that names this plant or this city and states
   what is made there.
   - That page is the own-site witness.
   - If the company has no site, or the site does not name this plant, the record stands on federal sources only.
3. **Scope.** The page must show in-scope polymer work under SCHEMA §1–§2: making polymer resins, compounds, plastic
   or rubber products, composites, or polymer coatings, adhesives or sealants. Examples that fail are blending
   chemicals with no polymer, distribution only, or metal parts.
4. **Status.** A dated closure on the company's own site or in trade press is `REJECT`, with the quote. A failed fetch
   is never evidence.

## Verdicts (AGENTS §2 rule 8)
- `VERIFIED_NEW_SITE`: the site belongs under a held organization (`held_org_id`).
- `VERIFIED_NEW_ORG`: a new organization plus its site.
- `REJECT`: give the deciding fact.
- `STILL_UNCERTAIN`: name the settling fact.
- `DUPLICATE_OF:<id>`.

**Tier proposal, the same as the UT pilot (#41):**
- a site with a federal source plus an own-site witness is **B**;
- a site on federal sources only is **C**;
- a new organization is **C**.

## Output: `verdicts.csv` (UTF-8, comma, quoted as needed)
`cluster_id, verdict, held_org_id, org_legal_name, org_website, org_hq_city, org_hq_state, org_hq_county,
site_name, street, city, zip, county, processes, materials, naics_primary, own_url, own_quote, own_quote_kind, tier,
deciding_fact, note`
- `org_*` fields apply only to VERIFIED_NEW_ORG. The HQ comes from the company's own site. If the HQ is not stated,
  leave it blank.
- `street`, `city`, `zip` and `county` come from the federal row, corrected only if the own site prints a different
  address. Say so in `note`.
- `processes` and `materials`: `;`-separated §3.1 and §3.2 terms that the own page **explicitly** states. Never infer.
- `naics_primary`: the 6-digit code from `naics_set` that the ITA or OSHA row carries, if one is clearly primary.
- `own_quote`: at most 25 words, one continuous span copied **exactly**, naming the plant or city and the activity.
  `own_quote_kind` is `plant_and_activity`, `plant_only` or `activity_only`. The integrator re-fetches `own_url` and
  checks the words.
- No emails, phones or personal data.

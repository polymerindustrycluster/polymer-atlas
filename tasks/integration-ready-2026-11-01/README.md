# Integration-ready change sets — PIC-12 capability wave + employee bands (2026-11-01)

**These are proposals, not data changes.** Produced by `scripts/build_integration_sets.py` (stdlib, re-runnable) by a packet lane that never edits `data/`. Every new ID is the placeholder `<ALLOC>`; the integrator of record allocates IDs, applies one writer per file, and reviews first (AGENTS.md §2 rule 7). Nothing was committed or pushed.

## Files

| File | What it is |
|---|---|
| `capability_site_updates.csv` | one row per site with VERIFIED site-scope packet rows: current vs proposed `processes` / `materials` / `markets_served`, certification route, packet row refs, APPLY/HOLD |
| `capability_org_updates.csv` | one row per organization with VERIFIED org-scope rows, deduplicated across lanes: all four fields incl. `certifications` |
| `evidence_rows.csv` | draft rows in `data/evidence.csv`'s exact header order; `evidence_id` = `<ALLOC>` |
| `band_updates.csv` | per site (and per Ohio org): existing band, each source's proposal, the R13 pick, APPLY / REVIEW / SKIP |
| `conflicts.csv` | everything not mechanically appliable, with a class and a suggested disposition |
| `validate_dryrun.md` | the temp-copy application and `validate.py` result |

## Counts (units stated)

- **Inputs:** 14 packet folders (pilot + 5 tranche-1 lanes + 8 tranche-2 lanes); 3570 packet rows; 611 verdicted Ohio PIC-12 sites (290 site-level VERIFIED); 3308 in-vocab single values after splitting `;`-packed rows (unit: record x field x value, all verdicts and scopes).
- **Site capability rows:** 294 sites carry VERIFIED site-scope rows (unit: site rows); **286 APPLY, 8 HOLD** (non-active, non-plant `site_type` per R9, or lane/parent mismatch).
- **Sites with at least one field change under APPLY (unit: site rows): 282.**
- **Values added at sites (unit: new in-vocab values, APPLY rows only):** processes 489, materials 721, markets_served 532, certifications (to site notes) 100. Held back because the field's existing value has off-vocabulary text (REVIEW_EXISTING_OFFVOCAB): materials 5, processes 16.
- **Organization capability rows:** 182 orgs carry VERIFIED org-scope rows (unit: org rows, after dedupe: 1302 single-value rows collapse to 1125 org x field x value; 28 orgs appear in more than one lane); **182 APPLY, 0 HOLD**; orgs with at least one field change: 181.
- **Values added at orgs (unit: new in-vocab values, APPLY rows only):** processes 229, materials 328, markets_served 481, certifications 37. Held (existing off-vocab text): materials 9, processes 3.
- **Evidence rows drafted (unit: rows, one per record x field x value):** 3012 (organizations 1113, sites 1899); 95 of them reconfirm a value the row already carried. All claim_type=`scope`, source_class=`own_site`, tier_effect=`supports_A` (the own_site ceiling, §4.13), created_by=`claude-code-integration-prep-2026-11-01`. 8 quote(s) had an email or phone string replaced with `[email omitted]` / `[phone omitted]` (AGENTS.md §6; the packet's own quote stays in `tasks/`).
- **Bands (unit: rows):** sites APPLY 1811 (fill 1794, already-equal no-op 17), REVIEW 140, SKIP 139; Ohio orgs (`employee_band_ohio`, Form 5500, R7f) APPLY 221 (fill 202, no-op 19), REVIEW 31, SKIP 0. Site fills by winning source: form5500 278, inspection 334, ita 1384.
- **Conflicts rows (unit: rows):** 689 — by class: offvocab_note 300, band_review 171, band_skip 139, row_still_uncertain 45, existing_offvocab_field 20, site_hold 8, site_verdict_su_row_verified 4, cross_lane_verdict_disagreement 2.

## Band precedence

**R13 band precedence was owner-ruled on 2026-11-01** (`tasks/OWNER_BATTERY_2026-11-01.md` addendum header: RULED "do it all"; recorded as SCHEMA v1.7.7 §1). `band_updates.csv` is therefore ruled work; statuses below apply that ruling mechanically.

Precedence: ITA (CY2025) -> OSHA inspection (latest with a count) -> Form 5500 (single-establishment org only). REVIEW = another source more than one band from the pick, or the pick differs from an existing in-vocabulary band (or the existing band is off-vocabulary). SKIP = the ITA row's `reliability` is `review`/`suspect` (the lane's own screens), or a Form 5500 site pick whose org no longer has exactly one site. Conservative extras added here, each visible in `reason`: site not active, ITA `site_caution`, a non-`strong` match on the pick source, other ITA filings at the site in a different band, Form 5500 `match_via_address_not_name` or matched org status not active. If the owner wants a flagged ITA row to fall back to the inspection band, the columns are all in the file.

## Decisions I made (the integrator may overrule)

1. **Certifications.** `sites` has no `certifications` column (header checked: False); `organizations` does (True). Site-scope certifications therefore go to a `CERT-SITE:` site-notes append (the R12 precedent records certification facts in site notes) and are NOT pushed up to the organization, because a plant's certificate is not a company-wide fact (the Parker rule). Org-scope certifications go to `organizations.certifications`. If the owner prefers a sites column, that is a schema revision.
2. **Value order** = the order of the lists in `docs/schema/vocab.json` (alphabetical). Proposed values are the union of the existing in-vocab tokens and the new ones in that order. Where nothing new is added the existing text is left byte-for-byte (no reordering).
3. **Off-vocab existing text is never merged.** A field whose current value holds any non-vocabulary token is REVIEW_EXISTING_OFFVOCAB: the new values are listed in `new_*` but `proposed_*` is blank, and the pair goes to `conflicts.csv`. Existing free text is frequent in Ohio rows (e.g. 'injection molding', 'polyurethane foam'). Normalizing that text is a vocabulary pass of its own.
4. **Never org-scope into sites; never site-scope into orgs.** Org rows are built only from org-scope packet rows.
5. **Not covered:** `site_capabilities.csv` (CAP rows under SCHEMA §3.6/§4.15 use a different vocabulary and grain rule). The QUEUE line names it as an alternative target; these sets update the tag columns only. Off-vocabulary `*_other_note` rows are not applied (they are in `conflicts.csv` with a v1.7.6 candidate-term hint for the tranche-1 packets that predate the vocabulary).
6. **Band evidence** is not drafted (no §4.13 claim_type fits a band; see `validate_dryrun.md`). The source date goes to a `BAND-SOURCE:` notes append because neither table has an `employee_count_source_date` column.
7. Tranche `wave-oh-capabilities-2026-11-01` (non-PIC-12 Ohio) is not an input of this pass; its packets are not here.

## Application order for the integrator of record

1. Review `conflicts.csv` (largest classes first) and `HOLD` rows; decide or return packets to lanes.
2. Claim the task in `tasks/QUEUE.md`. Take pre-pass backups of `data/sites_OH.csv`, the other touched site shards, `data/organizations_*.csv` shards touched, and `data/evidence.csv`.
3. Allocate `EVD-` IDs above the tree-wide maximum (`python3 scripts/atlas.py next-id EVD`) and replace each `<ALLOC>` in `evidence_rows.csv`; append to `data/evidence.csv`.
4. Apply `capability_site_updates.csv` APPLY rows to the site shards (`processes`, `materials`, `markets_served`) and append each `proposed_notes_append` to the site's `notes`.
5. Apply `capability_org_updates.csv` APPLY rows to the organization shards (four fields).
6. Apply `band_updates.csv` APPLY rows with action `fill` (`employee_band_site` / `employee_band_ohio`), appending `notes_append` to `notes`. REVIEW and SKIP rows wait for a ruling or a fresh source.
7. Re-run the `tier1_qualifier` derivation (the Ohio-band fills change the `employees_250plus` input); never hand-edit it.
8. `python3 scripts/validate.py` must pass; journal the pass with counts and unit labels; read back if pushing in campaign mode.

## Dry-run result

**OK** — details in `validate_dryrun.md`. Errors after applying: 0; warnings new vs. baseline: 13.

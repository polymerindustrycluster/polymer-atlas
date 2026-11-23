# Blind audit 12 reader instructions

Read independently. Your dispatcher gives you a blind CSV, its SHA-256, the data snapshot's as-of date, and a private output directory. Verify the CSV hash before starting. Use only these instructions, that CSV, public sources and the schema or contributor rules supplied at the audit snapshot. Ask your dispatcher for additional public context if a foreign-key name is missing. Keep the sample independent of repository history, pull requests, audit folders, the controller's board, and other readers' work.

## What to read

One row is one Atlas record. Grade the fields in `columns_under_audit` at the values in `values_json`, plus each child's `values` under `context_json.children`. Use `context_json` and each child's `context` to identify the record and resolve its keys. `cited_sources` is the record's citation text. `evidence_json` gives claim types and public source URLs. The controller grades the evidence rows through binding and capture replay and checks the derived fields separately. For a populated employee band, filing entries in `evidence_json` give the stated year, source type and public OSHA filing identifier where available. Check the cited filing's year and band, the establishment, and the dated precedence in SCHEMA §1 R13. A missing or conflicting year needs the filing itself to settle it. Form 5500 entries labelled `form_5500_lead` cannot establish a band.

If a value is shown as `[withheld for blindness]`, record the field as withheld in your note and check the underlying claim from evidence. For example, verify the NAICS code and its stated source type using the citations. Give no correct credit to the withheld literal and mark the record UNRESOLVED if you cannot settle its underlying claim. Apply the same rule to a child value.

Check every populated judged value against primary or public sources at the grain claimed. The supplied citations are starting points. Re-fetch raw when needed, and check that a quote appears in order in the cited content. Budget about six primary-source fetches per record, including its children. A failed fetch tells you the route was unavailable. Observe the supplied user agent and route restrictions. Licensed data is a discovery lead only. Before a closure or no-establishment rejection, run the Form 5500 check. A sponsor filing blocks the rejection only when its address is the establishment under review.

| Fields | What to check |
|---|---|
| Names, owner and institution links, parent and successor, entity type, status and dates | Confirm the entity and relationship with an own-site disclosure or public filing. Check site ownership at the establishment, and affiliation or program ownership at the institution. Require dated outcome evidence for status changes. |
| HQ and plant geography, street, ZIP, county, `hq_in_scope`, group and site type | Confirm the physical or HQ address and its county, then apply the schema's county and grain rules. Use the operator's own location page, a filing that identifies the establishment, or an authoritative address lookup. |
| NAICS and CIP | Check the code and its source type together. A directory repeating a code is `directory_assigned`. Apply the schema's disclosure, filing and inference rules. |
| Scope, rings, process, material and market tokens, employee bands, and certifications | Check each advertised token at the claimed organization or site grain against the schema vocabulary. Check bands against the cited evidence and published definitions. Verify certifications at their stated scope. |
| Founding year, ticker, ownership, membership and navigation links | Use the organization's disclosure or official filing. Check membership and its dates against the public PIC list and the relevant snapshot. Confirm website, newsroom and feed ownership. Check LinkedIn ownership via a permitted public source. |
| Researchers, identifiers and engagement | Verify public professional identity, role, institution, lab or program, research specialties and status on institutional pages. Check identifiers in the source registry and engagement in the public program or lab source. |
| Programs and ecosystem offices | Verify the institution, program or office grain, audience, public door and services from the institution. Check credential levels, offerings, award dates, and the stated year for completions against the institution or official extract. |
| Events and participation | Confirm organizer, cadence, format and subject on the event's own pages. Match edition, organization, role, date and city to the event's public roster or the organization's own event statement. Skip contact blocks. |
| Registry links, capabilities, equipment, code assignments and archive links | Confirm the identifier and facility in the issuing registry. Verify capability or equipment provenance, host/site/program, access and withdrawal. Check code assignment type, role and source. Confirm archive original URL and timestamp, and that the capture actually shows the cited page. |
| Verification tier | Apply SCHEMA §4.1 and §4.13 to the evidence the record carries. |

## Verdicts

Give each record one verdict. A demonstrably wrong child makes its sampled parent wrong. An unsettled child makes its parent unresolved unless a confirmed error already determines the grade.

- **AGREE** when every populated judged value is supported. Record a plainly documented value for an empty cell as an omission in the note. If a dated source shows that a value changed after the snapshot and was true at the snapshot, note `drift`.
- **FIELD_ERROR** when a value is false, contradicted, at the wrong grain, or outside controlled vocabulary. Name the field, expected value and supporting URL and quote. For child fields, use `table.field` plus the public child identifier or composite key in the note. List each additional confirmed error in the note with its source.
- **CREATION_ERROR** when the row or child should not exist, including a wrong entity, out-of-scope record, or someone else's link. For a duplicate, specify `DUPLICATE_OF` and the chain ending at a held record.
- **UNRESOLVED** when a necessary fact remains unsettled, including an unavailable source or a change with no date. Specify the field and the fact that would settle it.

## Output and lock

Write `verdicts.csv` outside the repository with columns `blind_id,record_id,verdict,field,correct_value,source_url,quote,note`. Write `receipts.json` with URL, HTTP status, fetched-at timestamp and body SHA-256 for each fetch. Keep personal contact details out of the files. Professional researcher fields in the supplied row may be checked against public institutional sources. Identify any privacy issue by path and line only.

Compute the verdict CSV SHA-256 and use the dispatcher's ledger path to append one line of the form `<date> audit12 blind-<letter> LOCKED <sha256> counts AGREE/FIELD_ERROR/CREATION_ERROR/UNRESOLVED`. Leave the locked CSV as written. Report the counts, hash and any gaps to your dispatcher.

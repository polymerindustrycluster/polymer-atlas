# Blind audit 11: reviewer instructions

You are one of two independent blind reviewers. Do not contact the other reviewer, or any thread other than the one that
dispatched you. In what follows, `<x>` is your letter, `a` or `b`.

## Input

Use only your copy of the blind file, `blind_<x>.csv` (120 rows). Your dispatcher gives you its path and sha256. Check the
hash before you start.

Each row is one **record change**: one Polymer Atlas record (table + `record_id`) under one change class. The same record
can appear in more than one row under different classes. Grade each row **only** on the columns named in
`columns_under_audit`, at the values shown in `values_json`.

- `context_json`: fields that locate the record, with foreign keys resolved to names (organization, site, parent).
- `cited_sources`: the record's own citation text.
- `evidence_json`: the URL and claim type of each evidence row the record carries.

A `created` row is a new record, so every column shown is under audit.

All values are as of repo commit `4182519` (current `main` when the audit was drawn). If you read `data/` for context, read
it at that commit, `git show 4182519:data/<file>`, never from a working tree that may be behind or ahead of it.

## Blindness rules

You must not read:
- `tasks/blind-audit-11-*` or any git branch named `blind-audit-11`;
- `git log` or `git blame` output;
- GitHub pull requests or issues;
- the BOARD or `docs/reviews/` folders.

You may read:
- `AGENTS.md` and `docs/SCHEMA.md`, for field definitions, vocabularies and tier rules;
- `data/*.csv` at commit `4182519`, for context about related records.

## How to check

For each row, decide independently whether every audited value is true and supported, using public primary sources.

The cited sources are a starting point, not the answer. Re-fetch raw. A quote counts only if its words appear in order on
the page.

Spend at most about 6 fetches per row. That is a cap, not a target: many rows settle in one or two.

A failed fetch (403, timeout, bot wall, empty result) tells you the route was unavailable. It is never evidence of
absence, closure or error.

What each change class claims, and where to check it:

| Change class | The claim | Where to check |
|---|---|---|
| `archive_links` | Per SCHEMA §4.22, `archive_ref` is a Wayback Machine capture of the page the evidence row cites (one of `archived_evidence_source_urls`, ignoring scheme, `www.` and a trailing slash), made on `captured_at`. It exists so a later audit can read the cited page. | Open the capture. Compare the original URL and the timestamp the capture actually resolves to. Check that it replays the cited page itself, not an error page, a redirect to another page, or a bot wall. |
| `uei_links` | Per SCHEMA §4.8, `registry_id` is, verbatim, this organization's SAM.gov Unique Entity ID | The SAM.gov entity record or the SAM public entity extract; USAspending recipient records. Compare name and address. Unauthenticated SAM.gov search does not return entity registrations, and USAspending holds only award recipients, so use the key or extract your dispatcher provides, if any. |
| `registry_federal_links` | Per SCHEMA §4.8, `registry_id` (EPA FRS registry ID or TRI facility ID, verbatim) identifies this organization's facility. Where `site_id` is set, it is that site. | EPA ECHO detailed facility report, FRS, TRI search or Envirofacts. Compare name and address. |
| `zips` | `zip` is the ZIP code of the site's street address | USPS ZIP lookup; Census geocoder; the operator's own contact page. |
| `streets` | `street_address` is this establishment's street address | The operator's own site; government filings naming the establishment. |
| `bands` | `employee_band_ohio` / `employee_band_site` is the band the cited source supports | The cited source; SCHEMA's band definitions. |
| `members` | The organization is listed on the public PIC website member list as shown (name, tier, listing URL). `snapshot_date` is the date the list was read. | https://polymerindustrycluster.org/ |
| `markets`, `capabilities`, `ownership_founding`, `parents` | Each value is stated by the organization's own disclosure or a public filing, at the grain the record claims (organization or site), in SCHEMA vocabulary | The organization's own site; SEC, state or federal filings. |
| `tier_changes` | `verification_tier` is supported by the record's evidence under SCHEMA's tier rules | The cited evidence; SCHEMA §4.13. |
| `navigation_links` | `linkedin_url` / `newsroom_url` / `newsroom_feed_url` is this organization's own page or feed | The organization's own site. |
| `program_status` | The value (a `polymer_program` flag or a program row's `status`) is what public sources support, under SCHEMA §4.6 and §4.11 | The organization's own site; SCHEMA. |

## Verdicts

Give each row exactly one of:

- **AGREE**: every audited value is supported.
- **FIELD_ERROR**: the record is real, but at least one audited value is wrong or unsupported. Name the field, the value
  you would record (blank if it should be empty), and the source.
- **CREATION_ERROR**: the row should not exist. That covers a wrong entity, a record out of scope under SCHEMA, a
  duplicate of another record, or an identifier or link that belongs to someone else.
- **UNRESOLVED**: you could not settle it. Name the fact that would.

## Output

Write to the output folder your dispatcher names, never the repo:

- `verdicts.csv`, with columns `blind_id,record_id,verdict,field,correct_value,source_url,quote,note`.
- `receipts.json`, with url, HTTP status, fetched_at and the sha256 of the body for each fetch.

Do not save page bodies or any personal contact data.

## Lock

When you finish:

1. Compute the sha256 of `verdicts.csv`.
2. Append one line to the BOARD file your dispatcher names:
   `<date> blind-<x> audit11 LOCKED <sha256> counts AGREE/FIELD/CREATION/UNRESOLVED`
3. Do not edit `verdicts.csv` after that.

Do not message any thread. Your final reply, under 1500 characters, gives your counts, the lock hash, and what you could
not check.

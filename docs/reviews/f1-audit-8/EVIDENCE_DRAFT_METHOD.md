# ID-free independent evidence drafts

`evidence_drafts.csv` is a **review-only derivative**, not canonical data or an
integration request. All `evidence_id` cells are empty; no IDs were allocated.
Record table comes from `identity_only.json`, not an inferred identifier prefix.
The script reads only that identity manifest and the five immutable `blind/*.json`
files. It does not read canonical evidence or comparison results and makes no
network requests. Frozen files remain unchanged.

## Reproduce

From this directory run `python build_evidence_drafts.py` (Python standard library).
The script deterministically writes the CSV and `evidence_normalization_log.json`.
The log includes frozen input hashes, every included observation's field/claim/
source/date normalization, and each excluded observation with a reason.
Observation references are zero-based indexes into the named immutable file.

## Claim and source discipline

- Exactly the SCHEMA §4.13 columns are emitted. Claims describe independently
  observed **facts**, not completeness of a record, automatic tier changes, or
  findings of error. `source_ref` is always an exact frozen observation URL.
- Composite identity/address facts are split into appropriate claims. Facts with
  one record/claim/witness/date/class/effect are joined with semicolons. Detailed
  original field names, observation references and caveats are preserved.
- Actual activity/process/material/product observations generally map to
  `activity`; explicit polymer-scope observations may map to `scope`. No ring
  classification is derived. EO/EG/ethylene precursor observations do not settle
  the owner's inclusion boundary. Operator and group affiliation facts map to
  `parent` without inventing held Atlas parent IDs or corporate legal chains.
- Every source-specific third-party certificate listed in the build script is
  normalized to `registry`, irrespective of the company-hosted URL. Company
  documents hosted by third parties remain `own_site` where frozen authorship
  is explicit. Government labels normalize to `government_filing`. Public
  reseller observations are conservative `directory`/C, not operator testimony.
- **All** otherwise admissible rows are conservatively capped at B, even where
  the class permits A. Registry/directory address claims are C. These are claim-
  local ceilings, never full-record verification tiers. Certificate citations
  identify opened issuer documents; no new live certification-registry lookup
  is claimed. Integrators must retain the certificate identifier and check its
  applicability and the §4.13 registry-resolution contract before application.

## Dates and limits

A precise frozen source date becomes `observed_date`; a source year, range or
undated label is preserved in notes and the full ISO retrieval date is used
without inventing a day. The explicitly identified OSHA inspection date is
separated from later case closure. Retrieval is always 2026-10-30. Historical
facts stay historical: retrieval does not establish present operation, a filing
period is not its publication date, and a closed inspection case is not a closed
plant. Original summaries qualify mailing vs physical address, group vs plant
scope, brand vs legal entity, and planned vs completed activity.

Inferred rings, researcher classification proposals, fetch outcomes, potential
relationships and conditional relocation outcomes are excluded. Alternate-site
or group-only facts that cannot safely support the sampled establishment are
held out. Certification validity/qualification alone is not operating liveness;
standalone certification and headcount observations do not fit a primary-
activity assertion and are held out. Holdouts remain available in the immutable
blind records and normalization log, not silently discarded from the audit.
Two sampled sites consequently have no safe derivative rows; that is a coverage
limitation, **not** proof that either establishment does not exist.

No new sources were fetched. No original blind labels or verdicts were rewritten.
A draft row does not repair all missing must-have claims, settle a scope or grain
question, prove current legal status, or authorize canonical edits.

# dedupe-leads-a — 2026-11-06

Packet-only review of the five allocated pairs D01–D05, with exact endpoints
preserved from read-only `input.json`. Baseline **542629e** replaces the earlier
620c2ec briefing pin per L5b correction; no input scope changed.

| Pair | Verdict / decision | Result |
|---|---|---|
| D01 Cooper Standard / Lauren site pair | STILL_UNCERTAIN / LINK_FLAG | Dated acquisition agreement is not same-legal-operator plus same-establishment proof. Existing duplicate/closed note remains unproven by this packet. |
| D02 Iten / TDM | STILL_UNCERTAIN / LINK_FLAG | Historic Iten Plant 3 at 1303 West 38th verified in 2008 inventory; TDM identity/effective-date bridge remains missing. |
| D03 Roppe holding / operator | VERIFIED / DISTINCT | Own dated release expressly names holding parent; own-hosted dated EPD separately names Roppe Corporation as wholly owned division. |
| D04 Bridgestone Americas / Firestone Polymers | VERIFIED / DISTINCT | FY2025 group report lists separate named companies; own administrative page expressly describes subsidiary relationship. |
| D05 Royal shared TRI lead | STILL_UNCERTAIN / LINK_FLAG | Dated Ohio regulator rows distinguish north/south establishments. Exact legal equivalence of held organization abstractions and source-system TRI assignment remain unresolved. |

No SAME_ENTITY, DUPLICATE_OF, merge, rekey, closure or registry-removal proposal.
DISTINCT here rejects collapse of the parent and operating-business records; it
is not a new incorporation/registry finding or an instruction to alter parents.
The current held parent fields are read-only context. Existing Roppe Corp parent
pointer, if retained by the integrator, must follow its source-class and generated
relationship gate. The EPD's word “division” is preserved; not silently rewritten
as a legal alias. All new claims have bounded source receipts in `verdicts.json`.

Source dates are separated from observation date. The Roppe release is dated
2018-10-23; EPD SCS-EPD-10146 validity begins 2024-05-09 and ends 2029-05-08.
The Bridgestone report covers 2025-01-01 through 2025-12-31, published in 2026;
its evidence date is explicitly period end, not publication date. Its corporate
report is delivered through the issuer's external IR document host. The separate
live administrative page is undated, marked as such, and only corroborates the
dated company distinction. The Iten inventory supplies a 2008 base-year period,
not an exact date: source_date stays blank rather than inventing January 1.
Royal north/south issue dates are 2025-09-11 and 2025-09-04 respectively.

Every quoted source/page has at most 25 total words. ` || ` separates explicit
ordered excerpts; PDF raw extraction and HTML visible text are matched against
curl bytes. Raw pages, PDF bytes, extracted text and any incidental personal
contacts remain only in `/tmp/dedupe-leads-a/`; no full raw pages or personal
contacts are copied into this packet. `receipts.json` records 20 fetch attempts,
including availability failures; max five per organization, leaving the reserved
lead fetch. Search discovery queries and redirect hops are not page-fetch counts.
Cooper's five routes exhausted the lane cap; certificate paths returned a real
not-found page, not the certificates seen as search leads. No further route was
tried. TRI/OSHA and TDM routes that failed prove nothing about entity absence.

Read task129 `tasks/dedupe-hq-2-2026-11-04/README.md` and `journal.txt`. Banked
notes, sponsor leads and prior duplicate decisions were context, not primary
identity evidence. Local estate/entity catalogues remain partial on this Mac;
no absence claim was made from that platform gap. No private/CRM/licensed facts
were used. No unrelated source/domain name was promoted to a TDM alias.

Calibration agreement: first dated identity result D03 was sent to sole writer
L5b `thr_ii6ybubss4`. L5b independently matched the 2018 own PDF quote and date,
accepted the parent/operator distinction without a merge, and captured it once
in its calibration.json for reuse. The 2024 own-hosted EPD strengthens the exact
Corporation-name seam. Controller owns shared BOARD/status updates; no other
lane/controller files were edited.

Named check:

```
PYTHONDONTWRITEBYTECODE=1 python3 tasks/dedupe-leads-2026-11-06/lanes/a/check.py
```

PASS: exact five unique pairs and endpoints; input hash; all 20 raw SHA-256
receipts; quote word/order checks; explicit dates/periods; max five helper fetches
per org. Three real-source known answers: Roppe parent wording; Firestone explicit
subsidiary wording corroborating dated company table; Royal separate north/south
plant rows. Negative controls reject address-only, parent-only, missing-date,
different-establishment, fabricated quote, reversed excerpts and missing/duplicate
pair defects. The synthetic merge predicate only demonstrates the conjunctive
merge guard; it does not turn source text into an automated legal-identity verdict.
The checker never authorizes application or certifies that unresolved identity
facts have been settled.

No data, Git/branch, settings, queue, tracker, ID, commitment or status changes.
No EVD allocation (318000 block is lead-only). Parent owns independent raw checks,
identity adjudication, any bounded application, deterministic integration checks
and cross-family completion review. This packet is not self-approved Done.

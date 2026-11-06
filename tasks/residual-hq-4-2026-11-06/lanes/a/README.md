# residual-hq4-a — final packet, 2026-11-06

Exactly 25 allocated organization IDs: **3 proposed HQ_FOUND / 22 STILL_UNKNOWN**.
Every hold has an explicit settling_fact. County remains blank; held legal names
remain unchanged. No confidence, status or parent field was changed.

| Held organization | Proposed HQ | Own witness |
|---|---|---|
| ORG-007432 Poly Processing Company, LLC | Monroe, LA, US | September 2023 installation/operation/maintenance manual, final page Company Headquarters block |
| ORG-007712 Plasman Precision Parts LLC | Hopkins, MN, US | Current TPM about page: Hopkins Minnesota; Hopkins Plant expressly at headquarters; 2024 rebrand history |
| ORG-007729 T.O. Plastics, Inc. | Clearwater, MN, US | Own Custom Solutions brochure Headquarters column, distinct from Otsego Manufacturing column |

Agreements with sole integration writer L5b `thr_ii6ybubss4`:

- T.O. Plastics was the first actual positive sent for calibration. L5b independently
  fetched its PDF and inspected both pdftotext -layout and -raw. Layout interleaves
  the left HQ and right manufacturing columns. The final quote therefore uses
  three explicit ordered excerpts separated by ` || `, totaling under 25 words.
  L5b accepted Clearwater and will reuse the one captured integrator receipt.
- L5b independently fetched TPM's page and accepted the current Hopkins Minnesota
  plus current Hopkins Plant-at-HQ statements for the held operating business.
  The page expressly states Plasman Precision Parts became stand-alone in 2023
  and rebranded to TPM in 2024. A historical 2001 line says Hopkins MI, conflicting
  with the current opening's Minnesota; this typo/seam is disclosed in verdicts.
  No legal rename, parent or status change is proposed.
- LEI-only discovery remains held. Official state-registry HQ/principal-office
  evidence could support held C at supports_C; no registry finding was needed here.
  Controller owns shared BOARD updates; lane writes remain confined here.

Poly Processing's manual is a dated own HQ statement, not a historical building
construction event. The freshly fetched own contact page also lists the same
Monroe street/city/state address; contact evidence alone was not used to designate
HQ. The manual quote carries its September 2023 edition date, without asserting
that this is the newest published edition. US country follows explicit US states.

Known websites came first, followed by cheap own about/contact/location pages
and targeted public search for explicit HQ documents. Parent/global headquarters,
contact addresses and plant locations were not assigned to subsidiaries. Reiss
names only Virginia as HQ and separately distinguishes manufacturing from AR/AP
addresses; Pride names only Minnesota as HQ. Both remain held for the city fact.
Failed fetches were availability signals only. No private CRM or paid-source
content was used as evidence.

`receipts.json`: **67 actual curl attempts, maximum 3 per organization**, below
five helper routes and preserving the lead's reserved check. Counts include failed
routes and Jina attempts, excluding search-index discovery queries and redirect
hops. Raw responses and extracted text are only in `/tmp/residual-hq4-a/`; the
packet contains no full raw pages or personal contacts. Each positive quote is
at most 25 total words; excerpts match the source in order.

Named check:

```
PYTHONDONTWRITEBYTECODE=1 python3 tasks/residual-hq-4-2026-11-06/lanes/a/check.py
```

PASS: exact 25-ID coverage/uniqueness; unchanged held names/input hash; 3 findings
and 22 holds; 67 raw SHA-256 receipts; maximum 3 routes; quote word/order checks.
Three real-source known answers are Poly Processing Monroe, TPM Hopkins and T.O.
Plastics Clearwater. Omega's parent-Sigma HQ is an additional negative case. Six
fault controls reject missing row, duplicate ID, missing header, fabricated quote,
hidden-script HQ and reversed excerpt order. This checks packet integrity;
independent re-fetch, application and completion review remain the parent's work.

No data/Git/branch/settings/queue/tracker/ID/commitment/task-status writes. No
self-approved Done. This is the final batch; research stops after packet handoff.

# residual-hq3-a — observed 2026-11-06

Packet for exactly 50 read-only input organization IDs. `verdicts.csv` has
5 proposed HQ_FOUND and 45 STILL_UNKNOWN outcomes; `verdict` mirrors `outcome`.
Every hold names the fact needed to settle HQ. County is empty throughout;
no county, confidence, entity rename or status change was inferred.

Proposed HQ observations (all own_site):

| Held organization ID | Headquarters | Witness |
|---|---|---|
| ORG-004558 Paneltech International, LLC | Hoquiam, WA, US | Own homepage explicit operating-name HQ |
| ORG-006109 Central Ink Corporation | West Chicago, IL, US | Own Corporate Headquarters block |
| ORG-006114 Sandstrom Products Company | Port Byron, IL, US | Own Headquarters block with street address |
| ORG-007026 National Manufacturing Group | Troy, MI, US | Own homepage explicit Troy Michigan headquarters |
| ORG-007032 PTI Engineered Plastics, Inc. | Macomb, MI, US | Own 2023 announcement About section explicit HQ |

Agreements with sole integrator L5b `thr_ii6ybubss4`:

- Paneltech was sent as first real positive for calibration. L5b independently
  re-fetched the raw quote and accepted the entity seam because the held record
  already has Paneltech;PaperStone trade names and the same own domain.
  The footer says Paneltech LLC, while held legal spelling includes International.
  Retain held legal spelling unchanged. Integrator captured the calibration once
  in its HQ3 rawcheck.json and will reuse it, reserving unnecessary extra fetches.
- LEI-only leads remain holds. Official state-registry HQ/principal-office evidence
  could support held C-tier rows at supports_C, while held A/B requires an own
  witness. This packet ultimately proposes only own-site HQ observations.
- SECON ORG-006116 was changed from a provisional positive to STILL_UNKNOWN after
  L5b challenged currency. The page reports a 2001 HQ construction event followed
  by expansions and a current facility description; it does not expressly confirm
  current HQ. No new fetch was needed to make that correction.

National Manufacturing Group's own homepage says Troy Michigan headquarters,
but a recent announcement has a Clarkston dateline and the locations page names
Clarkston. Neither alternate block explicitly labels HQ. This currency caveat is
preserved in the verdict for the integrator's independent re-fetch. PTI's witness
is a dated 2023 own announcement; it states HQ as an entity fact, rather than a
past construction event. No stronger currency claim is made by this packet.

Known websites were checked first, followed by inexpensive own contact/about/
locations pages. Public search discovery located missing primary domains. Plant,
contact, mailing and parent/global headquarters were not converted to subsidiary
HQ. Fabrik's separate Midwest HQ and McHenry Corporate Office wording, Eclipse's
ambiguous facility antecedent and CSI's different legal-entity HQ are held. No
private CRM or paid-source content was used as evidence. All held records are
active; no tombstone movement is proposed.

`receipts.json` records 103 actual curl page-fetch attempts, requested URLs,
raw SHA-256 hashes, errors and temporary raw paths. Maximum is 3 per organization,
below the FIVE-attempt lane cap, leaving the reserved integrator fetch. The count
includes failed/blocked fetches but excludes search-index discovery queries and
redirect hops. No failed fetch was treated as evidence of absence. Raw responses
and extracted text remain only in `/tmp/residual-hq3-a/`; the packet contains no
full page cache or personal contact details. Positive quote text is at most 25
words per source and matches the fetched visible page text in order.

Named packet check:

```
PYTHONDONTWRITEBYTECODE=1 python3 tasks/residual-hq-3-2026-11-06/lanes/a/check.py
```

Result: PASS — exactly 50 unique allocated IDs; 5 HQ_FOUND / 45 STILL_UNKNOWN;
103 hash receipts; max 3 fetches/org; all positive quotes match raw visible text
and word limits. Three real-source known answers: calibrated Paneltech Hoquiam,
Central Ink West Chicago and PTI Macomb. Five fault controls reject a missing row,
a duplicate ID, a missing header, a fabricated quote and hidden-script HQ text.
Input hash is recorded and checked; held legal names are retained verbatim.

This is a completed research packet, not a self-approved integration or Done
declaration. Independent factual re-fetch, any application, builder collision/
preimage/replay checks, validator and cross-family completion review belong to
L5b/controller. No data, Git/branch, queue, tracker, ID allocation, settings,
commitment or task-status writes were made. All persistent lane work is confined
to this folder; controller-owned shared ledger updates remain with the controller.

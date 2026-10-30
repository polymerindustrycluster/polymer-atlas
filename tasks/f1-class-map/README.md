# F1 (blind audit 8) — authoritative record-level TRI-class mapping

Published by the orchestrator 2026-10-30 for the F1 lane (PR #9), whose sampler
was blocked on this map. Source pin for the frame: main `eceead3a`.

`f1_record_tri_class_mapping.csv` — 2,199 rows = every ORG (682) and SITE
(1,517) created in integration passes 20–25: the full F1 sampling frame.

## How it was built (deterministic; retained in orchestrator staging)
Each creation was taken from its pass's `id_allocation.csv` (create classes
only — flips, repoints, folds, edits excluded), matched by `source_key` to the
design files of the packet that fed the pass, and — for TRI creations — joined
via the creating facility's TRIFID to the TRI worklist's `priority_group`.
Counts reconcile exactly with the published per-pass create counts and the
wave summaries (e.g. tranche 1 = 46 TRI creations: 3 orgs + 43 sites).

## Columns
- `tri_class` = the CREATING FACILITY's worklist priority class: P0 forward
  link · P1 held Tier-1 missing site · P2 held missing site · P3 unheld w/
  Tier-1 signal · P4 unheld single facility. Class labels the facility's
  worklist stratum, not the record's prior held status (a P1 facility whose
  operator proved unheld created a brand-new org; it is still P1-stratum).
- `packet_id`, `trifids` — the creating facility's worklist packet / TRIFID(s).
- `mixed_class` — orgs whose creating facilities span >1 class (primary =
  lowest P, others in parentheses in `tri_class`). Count in this build: 0.

## Distribution
P0 **0** · P1 417 · P2 180 · P3 771 · P4 604 · NOT_TRI 227 · unresolved 0.

- **P0 has ZERO creations by construction** — P0 was link mechanics on
  already-held records, so no P0 stratum exists in the creations frame.
  Auditing P0 means sampling registry-link rows on pre-existing records:
  a different frame, flagged here rather than silently dropped.
- NOT_TRI = 227, all pass 20: SC wave 1 = 89 (28 orgs + 61 sites);
  candidate queue Q01–Q02 = 138 (65 orgs + 73 sites). Pass 21's PR #6 packet
  produced ZERO creations (flips/repoints/edits only); all 287 pass-21
  creations are TRI.
- The five watch-seed orgs (Carlstar ORG-004252, Barnhardt ORG-004218,
  Jasper ORG-004131, Fiberon ORG-004229, Timken ORG-004288) each carry an
  additional `org_create_watch` marker row in their pass's allocation file.
  The marker is not a creation. **Correction (2026-10-30):** v1 of this map
  treated the markers as separate creations, double-counting all five
  (2,204 rows, P3 776, and a wrong note here claiming samplers counting
  only `org_create` rows would land 5 short — they land exactly right).
  Duo's pre-draw duplicate check caught it. v2: 2,199 unique creations,
  P3 771; the five orgs are ordinary `org_create` rows, all P3.

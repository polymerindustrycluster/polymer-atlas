# OMG Thermoforming reframing correction (2026-11-11)

The last of the four findings surfaced by the licensed-source cleanup lanes (PR #258), adjudicated in
`tasks/licensed-source-cleanup-2-2026-11-11/` and evidenced in PR #266. The evidence is already on main;
this packet corrects the two records to match it — one task, one PR, per protocol.

## The deciding evidence (already on main, PR #266)

- **EVD-333050 / EVD-333051 / EVD-333052** — the original existence, scope, and parent claims for
  ORG-003807, each recorded as **contradicted** (`own_site`), quoting OMG srl's own
  agents-and-distributors page (https://www.omgitaly.com/agenti-e-distributori, read 2026-11-11):
  "USA-Midwest 3407 Avenue D, Arlington TX 76011". The entry sits in the parent's agent/distributor
  network (omgusa.net contacts, incl. "USA-South and Southwest" at the same address). No public page
  names OMG Thermoforming Inc. as a subsidiary of OMG srl.

The records still say otherwise: ORG-003807's description calls it a "US subsidiary of Italy's OMG srl",
its `ultimate_parent_name` asserts OMG srl, and SITE-004251 is typed `hq_only` with notes calling it a
"US subsidiary facility" — all resting on the pass-18 packet's Plastics News reporting.

## Changes

- **ORG-003807** — description rewritten to the agent/distributor reality; `ultimate_parent_name`
  **cleared** (the asserted parent link is supported by no public source; `parent_org_id` was already
  blank and no `relationships.csv` row references the org — asserted in build.py — so there is no
  parity impact); `sources` rewritten to public citations only, the Plastics News citation removed
  under AGENTS §5; notes carry the correction and cite EVD-333050..52; `last_verified` and
  `last_activity_evidence_date` 2026-11-11 (the parent's current page lists the operation today);
  tier held at **C**.
- **SITE-004251** — `site_type` `hq_only` → **`sales_office`**; sources rewritten the same way; notes
  corrected, with the est.-2018 and ~15,000 sq ft details explicitly marked as original-packet and not
  re-verified; operating status stays active (the agent operation is currently listed); tier held at
  **B** (address and sales function corroborated by the parent's own current page).
- **inclusion_log.csv** — one row recording the correction and the rules cited.
- No new evidence rows: EVD-333050..52 are the evidence for this correction.

## Judgment call, flagged

Clearing `ultimate_parent_name` is this packet's one judgment call. The alternative readings: leave the
field and correct only prose (leaves a contradicted structured assertion in place, still feeding the
public record), or go further and tombstone SITE-004251 as not an OMG establishment at all. The middle
course is taken here: the unsupported structured claim comes out, both records stay, and everything is
reversible by a follow-up PR if a corporate record for OMG Thermoforming Inc. surfaces. The tombstone
question is the owner's call and is flagged as such in the final report, not decided here.

Reproduce: `python3 tasks/omg-reframing-2026-11-11/build.py --data-dir data` (dry run);
`--apply --i-am-the-integrator` writes.

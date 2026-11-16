# Public PIC membership re-sync — 2026-11-16

Claim: atlas-w16-members, Lane MBR, controller thr_9i2c6byhcz; owner uses the Atlas for member prospecting. This full public-list snapshot is the usage check for this pass; no outreach or private source was used.

Source: https://polymerindustrycluster.org/ fetched raw with curl on 2026-11-16. `public-list.html` is the complete raw witness, SHA256 c626c7a8c28d20df900c499b57edd2e712f30b372a1f321ce25b9fd0ba32efdc. No mailto/tel links occur in the witness. `members.before.csv` is the pre-pass backup.

| Proposal | Applied/held | Result / settling fact |
|---|---|---|
| Refresh 60 existing member rows | Applied | snapshot_date=2026-11-16; schema has no last_verified field on members |
| TeamNEO displayed name | Applied | Existing MBR-000060 retained; public title now includes the Northeast Ohio Region / JobsOhio tagline; linked teamneo.org agrees with held ecosystem record |
| Custom Rubber Corp | Held | Public Investing Partner links customrubbercorp.com, exact domain match ORG-000113. Adding MBR-000061 fails validator membership parity unless organizations_OH.csv pic_member and membership_source_url are changed together. Controller must authorize the expanded data scope; no member row added here. |

Counts: 61 public listing entries (54 Investing Partners, 7 Cornerstone Partners); 60 match existing member rows; 1 additional listing matches held organization ORG-000113; 0 added member rows; 0 existing members no longer listed; 0 new listings unmatched to a held record. Existing matches include 10 member_only rows, retained as-is: not all 61 listings are linked Atlas organizations. Output remains 60 member rows: 35 organization, 15 ecosystem, 10 member_only. No new organizations or evidence IDs allocated; §4.13 does not admit members as a record_table and has no membership claim class.

Dedupe: atlas.py dedupe-check --name 'Custom Rubber Corp' --domain customrubbercorp.com stops at exact domain ORG-000113 (step 1); normalized name and site name also agree. No identity merge or organization create. No verification tiers exist in members.csv; organization tiers unchanged. No borderline inclusion decisions or inclusion_log edits.

Checks: `python3 tasks/pic-members-resync-2026-11-16/build.py` is idempotent; `python3 tasks/pic-members-resync-2026-11-16/check.py` checks full output equality and independent HTMLParser listing count, and rejects injected dropped row, duplicate ID, and stale snapshot date. All 60 output rows are compared against the pre-pass backup replay.

Proposed follow-ups:
- Apply Custom Rubber membership in both member and organization tables in one authorized pass. Proposed member ID MBR-000061 is not reserved/allocated; recheck maximum at application.
- Schema has no lapsed-listing field; if a future roster omits a held member, hold for owner ruling rather than delete or invent a status.

Not checked: existing member-to-organization identity links were retained, not re-researched; member_since and organization membership flags were not refreshed. A public listing establishes membership only, not current operations. Independent family reviews remain with the controller before merge.

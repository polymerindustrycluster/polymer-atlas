# Tarkett hold revert (2026-11-14)

Owner ruling H-TARKETT (a), 2026-11-12 (`tasks/owner-rulings-2026-11-12/`, PR #313): keep SITE-003477 and SITE-003478
held until a dated primary legal-name bridge equates filed operator Tarkett USA Inc. with ORG-000131 Tarkett North
America; do not repoint on the group name alone.

PR #256 (2026-11-06) had already repointed both sites from ORG-001836 Johnsonite Inc. to ORG-000131, citing EPA TRI's
2025 filing "TARKETT USA INC DBA JOHNSONITE" and an EPA FRS registrant link. The ruling packet was written from the
older PR #201 holds and did not see that repoint. The owner chose (2026-11-14, in session) that the later ruling
governs.

| Record | Column | Before | After |
|-|-|-|-|
| SITE-003477 Johnsonite — Middlefield Rubber Tile Plant | `org_id` | ORG-000131 | ORG-001836 (its value before #256) |
| SITE-003478 Johnsonite — Chagrin Falls Plant | `org_id` | ORG-000131 | ORG-001836 (its value before #256) |

Each row's `notes` gains a dated line naming the ruling. Rows changed (unit: site rows): 2. Nothing else changes:
- The #256 evidence rows (EVD-333008..333011, EVD-333015) stay; evidence is append-only, and each still states a true
  observation (an FRS or TRI registrant, or the 2005 acquisition announcement).
- SITE-000427, closed by #256 as a duplicate of SITE-003478, keeps its tombstone.
- ORG-001836 stays `acquired` with successor ORG-000131.
- No tier-1 qualifier changes (`derive_tier1.py` preview: 0 rows).

Settling fact to lift the hold: a dated primary record (e.g. a state SOS merger or name-change filing) showing that
Tarkett USA Inc. is ORG-000131 Tarkett North America's legal entity, or naming the actual held legal operator.

Builder: `python3 tasks/tarkett-hold-revert-2026-11-14/build.py --apply` (idempotent; a second run changes 0 rows).
Checks: `python3 scripts/validate.py` OK; `python3 scripts/check_row_loss.py --base origin/main` OK.

# Registry-links restore (2026-11-06)

## What happened
Commit `805528a` ("ID skimpy-state wave (rebased by integrator)", merged with PR #67 as `91cd1a8` on 2026-11-04)
added its 4 intended FRS links and rewrote `data/registry_links.csv` from a stale copy. The file went from 5,158
links (at its parent `92393de`) to 1,811. Nothing failed: `validate.py` checks each link row, not how many there are.

What was lost, by registry: TRI_TRIFID 1,943 · FRS 1,223 · LEI 104 · OHIO_SOS_CHARTER 28 · EIN 16 · WIKIDATA 15 ·
SEC_CIK 9 · UEI 9 · SEC_CIK_PARENT_FILER 5 (unit: link rows, key = org_id + registry + registry_id + site_id).

The visible symptom was 1,015 `tier1_qualifier drift` warnings (V-29): organizations whose stored qualifier still
says `tri_reporter` or `public_parent`, but whose TRI or SEC link had gone.

## How the loss was scoped
- Every first-parent commit on `main` since 2026-10-28 was scanned for IDs or link keys that existed then and are
  absent now, across every table (shards unioned). Evidence: 0 IDs lost. Organizations and sites: 0. Registry links:
  3,352 (3,351 at `805528a`, plus 1 deliberate re-point in #123, the Ametek Nesquehoning plant moved to Niche Polymer).
  The other differences are documented (the pass-43e ecosystem revert, the seed renumber, and the 14 people merged in
  the 2026-11-03 cleanup).
- `805528a` added only its own 4 rows. It did not bring back any older superseded row.
- Every other "rebased by integrator" commit since 2026-11-01 was checked for deleted lines in `data/`. Only two
  delete anything, 3 ecosystem lines each. Both are intended ROR-id additions (PR #47). So the stale-copy rewrite
  happened in this one commit only.

## What `restore.py` does
It re-appends every lost link that is still valid on the current tree, in order:
1. A link whose facility id is now held by another organization (a re-point after 2026-11-04) is **held**.
2. An organization-grain link whose id is now held by another organization is **held**.
3. A link whose organization or site no longer exists is **held**.
4. A site-keyed link whose site now belongs to another organization is restored under that organization (none here).
5. Every other link is restored exactly as it was. Links on acquired or merged organizations stay on that record
   as history (2 rows).

`journal.csv` lists every lost row, with its action and reason. The script is idempotent: a second run finds nothing
left to restore.

## Result (unit: registry link rows)
| | Rows |
|-|-|
| Lost at `805528a` and still absent | 3,352 |
| Restored | 3,348 (TRI_TRIFID 1,940 · FRS 1,222 · LEI 104 · OHIO_SOS 28 · EIN 16 · WIKIDATA 15 · SEC_CIK 9 · UEI 9 · SEC_CIK_PARENT_FILER 5) |
| Held | 4: the Ametek re-point, and 3 TRIFIDs each recorded on two organizations before the loss: Iten Industries ORG-000386 / TDM LLC ORG-002079 (the pass-10 operator re-point), Cooper Standard ORG-000755 / its Lauren Manufacturing group ORG-001931, and Roppe Holding ORG-001088 / Roppe Corp. ORG-001087. Each TRIFID stays on the organization that holds it now. |
| `registry_links.csv` after | 5,373 rows |

## Checks
- `python3 scripts/validate.py`: passes, 0 errors.
- V-29 drift warnings: 1,015 before, 52 after. All 52 remaining are `gain:national_footprint`, organizations that
  reached 3 states through the November state waves. No organization would *lose* a qualifier, so no pass ran
  `derive_tier1.py --write` on the damaged file.
- The `tier1_qualifier` column is not touched here. The 52 gains go in a separate re-derive PR after this one merges,
  as in `tasks/tier1-rederive-2026-11-02/`.

## Not done here
- No guard yet stops a file losing rows. A row-count floor in `validate.py` follows in its own PR.
- The Cooper Standard pair is already queued as a possible duplicate site (SITE-000818 / SITE-001925, 2228 Reiser
  Ave SE). The held rows change nothing there.

# Wave 4 tranche 2 — Schoolcraft College (ORG-002857)

Lane: research only, 2026-11-12. Paid calls: zero.
Carried target per brief: PROG-000069 Plastic Technology (degree, aas_associate).
Unlinked pool at this institution: 0 people — no pool; links.csv/census.csv not
delivered per brief.

## HEADLINE FINDING — the brief's premise is wrong for this row: PROG-000069 is TOMBSTONED

This is not an active 0/5 row awaiting depth fills. The carried row reads
`status: tombstoned`, `admissions_status: not_admitting`, verification tier B, and the
institution's ecosystem row already carries `polymer_program: false` with an empty
program rollup (validator V-16 excludes tombstoned rows). Depth fills do not apply to
a tombstoned row; fills.csv records all five cells REFUSED on that ground. Nothing in
this packet proposes changing the row.

History, from the row's own notes (read in full this pass):

- Created 2026-10-30 (integration pass 15) from GitHub-lists mining. At creation the
  college's own catalog page already stated the Plastic Technology programme was
  "'on hold pending inactivation'" and directed interested students to Academic
  Advising; the hold was disclosed in the row's notes and on the parent record.
- RETIRED 2026-10-31 (integration pass 37, owed-checks workstream C re-verification,
  c_verdicts.md): the Plastic Technology AAS was found **absent from the current
  2026-2027 catalog** — the 2023-24 'on hold pending inactivation' had matured into
  removal. Status set to tombstoned; the dated inactivation evidence rides in the
  row's sources (including https://catalog.schoolcraft.edu/content.php?catoid=15&navoid=3651,
  "2026-2027 Programs and Areas of Study", read 2026-10-31) and the pass-37 liveness
  evidence row.

This is also why the wave-3 screen treated Schoolcraft as institution-only: the
institution's only program row is the tombstoned one.

## Currency re-check this pass — tombstone STANDS; no revival evidence

The Form 5500-style existence check appropriate to a program row (is it in the
institution's current catalog?) was re-run as far as the routes allow:

- Every "Plastic Technology" listing surfaced this pass is archival or stale:
  the 2023-2024 catalog's Programs and Areas of Study page (catoid=5) lists "Plastic
  Technology Skills Certificate / Plastic Technology Certificate / Plastic Technology
  AAS Degree"; a "Programs by Degree" page from the 2024-2025 catalog still lists the
  AAS; third-party scholarship aggregators repeat older college content. None of
  these is the current catalog.
- No current-catalog (2026-2027) or college-web source found this pass lists a
  Plastic Technology program at Schoolcraft.
- WEAKEST LINK: a direct fetch of the Atlas-cited 2026-2027 Programs page returned
  HTTP 403 this pass, so the fresh check rests on the pass-37 first-party reading
  (2026-10-31, twelve days before this pass) plus the absence of the program from
  every current-index result. A 403 is an availability signal, not evidence either
  way; if the integrator wants a same-day first-party read, the URL is
  https://catalog.schoolcraft.edu/content.php?catoid=15&navoid=3651.

Verdict: the tombstone stands. If a future catalog re-lists the program, that is a
new verification event (un-tombstoning is an integrator action on dated evidence),
not something this lane asserts.

## Depth fills

All five cells REFUSED for PROG-000069 — see fills.csv. Reason, once for all cells:
the row is tombstoned (retired 2026-10-31 on dated catalog evidence); depth fields
are not carried on retired rows.

# P2 applications — Vasquez dedupe merge, Adam Miller application, §4.21 v1.13.1 (2026-11-12)

Owner-approved 2026-11-12 (P2 battery). Three applications ride one PR:

1. **Vasquez dedupe merge** — `vasquez-dedupe-packet-2026-11-12.md`
   (verdict DUPLICATE_OF). PERSON-001331 is removed (declared in
   `REMOVALS.csv` in this folder, logged in `data/inclusion_log.csv`; ID
   retired, never reused); the survivor PERSON-000066 takes the folded
   field set from the packet, including tier A on the packet's
   recommendation (the A-tier witness — his own directory profile page —
   folds into the survivor's sources and was re-read 2026-11-12).
2. **Adam Miller application** — `adam-miller-recheck-2026-11-12.md`
   (verdict VERIFIED). PERSON-000030 gains `program_org_id` =
   PROG-000001 (Shawnee State Plastics Engineering Technology) on the
   2025–2026 catalog faculty line, and a P1 title refresh:
   `role_as_published` becomes "Associate Professor of Plastics
   Engineering Technology; Dean of the College of Business and
   Engineering Technology" — each half verbatim from Shawnee's own
   pages (catalog/cabinet bio; college page), joined in the established
   rank-plus-administrative-title pattern (cf. PERSON-000001,
   PERSON-000151). `role` stays `associate_professor`: the §4.9 enum
   carries no dean value, and the catalog still lists his faculty rank
   as associate professor. The deanship itself is Board Resolution
   E01-26, effective 2026-07-01.
3. **§4.21 micro-revision (SCHEMA v1.13.1)** — the identifier_type enum
   gains `GOOGLE_SCHOLAR`, `WOS_RESEARCHER_ID`, `GITHUB` (SCHEMA text +
   validator V-54 set), under the owner's 2026-11-12 mint rules:
   Scholar mints only on an institution-page link or exact name +
   stated affiliation + verified institutional-domain email;
   ResearcherID on the institution-page basis; GitHub for the
   computational subset whose profiles state name + institution.
   ResearchGate declined (auto-created unclaimed profiles); Scopus,
   Semantic Scholar and OpenAlex author IDs declined (algorithmically
   assigned). No identifier rows are minted in this PR — the revision
   enables future passes.

Evidence: EVD-333536 (Vasquez merge, supports_A), EVD-333537 (Miller
program link, catalog), EVD-333538 (Miller title, cabinet page).
People 1,451 → 1,450; evidence 40,598 → 40,601.

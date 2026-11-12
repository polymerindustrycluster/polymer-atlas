# Wave 4 tranche 2 — Northwest State Community College, Ohio (ORG-001271)

Lane: research only, 2026-11-12. Paid calls: zero.
Carried targets: PROG-000150 Plastics (degree, aas_associate, tier A, depth 0/5) and
PROG-000151 Plastics Manufacturing (certificate, tier A, depth 0/5).
Unlinked pool at this institution: 0 people — no pool; links.csv/census.csv not
delivered per brief.

## Currency check — VERIFIED for both rows (with a named weakest link)

- The Atlas's own verification of both rows is ten days old and catalog-exact:
  PROG-000150's notes record "'Plastics, AAS in Mechanical Engineering' in the current
  2026-2027 catalog" and PROG-000151's "active in the current 2026-2027 catalog",
  both accessed 2026-11-02 on catalog.northweststate.edu (catoid=7; poid=1284 and
  poid=1214 respectively).
- Fresh corroboration this pass: the Ohio TechNet partner page for Northwest State
  (crawled 4 days before this pass) lists "Plastics Manufacturing" among the college's
  Advanced Manufacturing degree programs (https://ohiotechnet.org/partner-school/northwest-state-community-college/);
  the State of Ohio transfer guide for the college (revised June 18, 2025, effective
  AY2025-26) links live catoid=7 catalog program pages in the same poid neighborhood
  as both rows (dam.assets.ohio.gov).
- WEAKEST LINK: a direct fetch of the catalog program pages this pass returned
  HTTP 403 (access denied). Under the protocol that is an availability signal about
  the route, never evidence of absence — so the currency verdict rests on the
  2026-11-02 tier-A catalog verification plus the corroboration above, not on a fresh
  first-party read. A readable fetch of
  https://catalog.northweststate.edu/preview_program.php?catoid=7&poid=1284 settles
  it outright.

## Depth fills — all five cells REFUSED for both rows (see fills.csv)

The catalog text retrievable this pass for the host degree (Mechanical Engineering
Technology, AAS) is generic — "educate students in technology based, entry-level
occupations related to the mechanical and manufacturing engineering fields… knowledge
of mechanical systems, engineering materials and equipment" — and names no polymer
process, material family, facility, or enrollment. The plastics-specific course
evidence visible in older college material (PET115/PET215 "Plastics Processes I/II" on
a legacy College Credit Plus pathway sheet) is curriculum grain and stale; under the
standing rule (research areas rest on research statements, not curriculum lines;
specialty values never inferred beyond the program's own page), nothing is coded from
it. Both rows honestly stay 0/5.

## Weakest link

The 403 catalog route (above). Everything else in this packet is a refusal, and the
refusals do not depend on the blocked fetch: even a readable catalog would need
program-level statements beyond course lists to fill any cell.

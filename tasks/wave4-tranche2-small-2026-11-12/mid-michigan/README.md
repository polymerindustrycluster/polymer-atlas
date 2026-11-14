# Wave 4 tranche 2 — Mid Michigan College (ORG-004813)

Lane: research only, 2026-11-12. Paid calls: zero.
Carried target: PROG-000160 Advanced Integrated Manufacturing (AIM) Plastics Pathway
(degree, aas_associate, tier A, depth 0/5).
Unlinked pool at this institution: 0 people — no pool; links.csv/census.csv not
delivered per brief.

## Currency check — VERIFIED (pathway still offered in the current catalog)

The college's own 2026-2027 catalog program guides (indexed copy crawled one day
before this pass) carry the pathway by name and code:

- "AAS.AIM Associate in Applied Science Degree: Advanced Integrated Manufacturing
  Requirements — A minimum of 60 credits is required… Completion of one of the
  following tracks: … Plastics — PLT.101 Survey of the Plastics Industry 2 Credits;
  PLT.110 Plastics and Polymer Materials 3 Credits; PLT.225 Production Planning and
  Control 3 Credits"
  https://midmich.edu/catalog/2026-2027-catalog/program-guides/assoc-app-sci26-27
- The college's Program Cost Estimates page lists "Adv Integrated Manufacturing -
  Plastics (AAS) AAS.AIM.PATHPLT — Credit Hours, 60" with current tuition figures —
  the same program code the Atlas row carries.
  https://midmich.edu/admissions/tuition/cost-estimates

This matches the carried row's structure exactly (a Plastics pathway/track inside the
AIM AAS). No currency flag; the program has NOT disappeared.

URL ROT (integrator note, not a depth fill): the row's carried url,
https://midmich.edu/degrees-programs/programs/aim/plastics-aas-pathway, returned the
college's 404 page on direct fetch this pass (both host forms), although the search
index holds the page's full content from ~69 days ago ("AIM Plastics | Associate in
Applied Science Pathway… Program Code AAS.AIM.PATHPLT… Last Reviewed: March 2024").
The college has restructured its catalog under /catalog/2026-2027-catalog/; the
program-guide URL above is the natural repoint candidate. A 404 on one page is a
site-restructure signal, not program absence — the current catalog and cost pages
above are the deciding evidence.

## Depth fills — all five cells REFUSED (see fills.csv)

Everything retrievable about the pathway is course-sequence grain (PLT.101/110/225
titles and credit counts). The pathway pages state no research areas (workforce AAS),
name no §3.1 process in a program-level statement ("Survey of the Plastics Industry"
and "Plastics and Polymer Materials" are course titles), state no §3.2 material
family as a specialty, publish no facilities/equipment statement, and publish no
enrollment (tuition cost figures never convert to scale_band). The row honestly
stays 0/5.

## Weakest link

The currency verdict rests on search-index retrieval of the college's own current
catalog/cost pages (crawled 1 day before this pass) because the legacy program page
404s and the new catalog pages were read via the index rather than a direct fetch.
The two independent college pages (program guides + cost estimates) agree on name,
code, and credit hours, so the verdict is firm; a direct fetch of the program-guide
URL is the belt-and-braces confirmation.

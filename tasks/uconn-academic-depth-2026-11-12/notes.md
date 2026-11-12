# UConn depth pass — lane notes (2026-11-12)

## Witness architecture (what counted as a program tie)

The single decisive source is the Polymer Program's own faculty page
(`polymer.ims.uconn.edu/polymer-program-faculty/`). It publishes three groups —
**Faculty** (core), **Associate Faculty**, **Emeritus Faculty** — and each row carries a
`data-person-tags` attribute in which "Polymer Program" is the academic-program tag.
The 12 LINK verdicts are exactly the pool members of the core **Faculty** table; each
also carries the "Polymer Program" tag except Jie He (see borderline calls). The same
table styles Mu-Ping Nieh "Director, IMS Polymer Program" outright. All LINK quotes in
links.csv are the person's roster row (name + title) on that page.

## Borderline calls

- **Jie He (PERSON-001295) — LINK, flagged.** He sits in the core Faculty table (last
  row, immediately before the Associate Faculty heading) and has a person page on the
  Polymer Program site, but his row's tag set is the only core-Faculty one lacking
  "Polymer Program" (it also lacks "Polymers" and "Faculty", which other rows carry
  inconsistently — tagging on this page is uneven). The core-table listing governed;
  the integrator may overrule if the tag is treated as the membership marker.
- **Jeffrey McCutcheon (PERSON-001292) — NO_WITNESS.** He appears on the program
  site's people directory only in the **Associate Faculty** group, untagged for the
  Polymer Program, and his program-site person page states only "Professor of Chemical
  and Biomolecular Engineering". Associate-group presence was not treated as a
  program tie. (Contrast Richard Parnas and Montgomery Shaw: Emeritus group, but
  tagged "Polymer Program" — neither is in the pool.)
- **Yang Cao (PERSON-001344) — NO_WITNESS.** His IMS roles (Director EIRC, Assistant
  Director IMS) are institute-level, and the EIRC appears among the Polymer Program's
  core facilities, but no page lists him as Polymer Program faculty and he is absent
  from the program faculty page. Institute leadership was not treated as a program tie.
- **Evgueni Pinkhassik (PERSON-001151) — NO_WITNESS.** His IMS person page states no
  program affiliation; absent from the Polymer Program faculty page. (IMS also runs a
  separate Materials Science Program; no page checked ties him to Polymer Science.)
- **Lakshmi Nair (PERSON-001296) — NO_WITNESS.** IMS person page styles her
  "Professor, Department of Orthopedic Surgery" (UConn Health); no Polymer Program tie.
- **Seok Woo Lee (PERSON-001143) — NO_WITNESS.** IMS resident faculty on the MSE side
  (mechanical behavior of structural materials); absent from the program faculty page.
- **Ali Tamayol (PERSON-001391) — NO_WITNESS.** Biomedical Engineering, UConn Health;
  no IMS/Polymer Program listing found.

## Scale figure discrepancy (for the integrator)

The About page's "19 faculty from 6 departments" (the scale_band fill) does not match
the program's own current faculty page, which lists 13 core Faculty + 4 Associate
Faculty = 17 (plus 8 Emeritus). The fill carries the institution's published statement
verbatim; the mismatch is the institution's own.

## Currency notes (not defects)

- Kelly Burke (PERSON-001107): the program faculty page now styles her "Department
  Head and Professor of Chemical and Biomolecular Engineering", consistent with the
  pool note's 2024 IMS article (stepped down as Polymer Program director to head CBE).
  She remains core Polymer Program faculty → LINK stands.
- Mu-Ping Nieh (PERSON-001038) is now Director, IMS Polymer Program, per the roster.
- No pool person was found to have left UConn. Tamayol is currently Associate
  Professor of Biomedical Engineering at UConn Health (Farmington); the pool's BME
  profile URL failed to connect from the lane environment (availability only — the
  profile is live in the search index).

## Failed fetches (availability only — never treated as absence)

- `polymer.ims.uconn.edu/academic-program/` returned 404 (a nav link target on the
  prospective-students page); program facts were taken from the About, Research, and
  Prospective Students pages instead.
- `www.bme.uconn.edu/faculty-staff/core-faculty/tamayol-ali/` failed to connect
  (curl exit 52/000) on the attempt made; Tamayol's current UConn Health affiliation
  was confirmed via the search index instead.

## Paid calls

None. All sources were fetched directly (curl) or found via free web search.
No Tavily/Exa/Firecrawl use.

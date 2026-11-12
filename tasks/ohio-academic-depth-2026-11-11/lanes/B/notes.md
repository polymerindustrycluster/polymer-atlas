# Lane B notes — Ohio academic depth pass (2026-11-11)

Scope as worked: 11 programs (CWRU ×6, OSU ×4, EWI ×1); 58 people (CWRU 25, OSU 33).
Deliverables: 45 fill rows, 63 link rows (29 LINK covering 24 people; 34 NO_WITNESS).
Every fill and link rests on an institution page (`source_kind=institution_page` throughout). No paid calls (no Tavily/Exa/Firecrawl); web search + curl + browser text fetch only.

## How quotes were taken

- Directory/roster witness quotes join the person's heading line with their title line from the same listing block on the same page (word sequence preserved; Atlas quote matching is punctuation-insensitive).
- PROG-000108's `specialty_processes` / `specialty_materials` quotes are cells of the major page's focus-area table read row-wise ("Areas of focus | Example of application"); the table is the only place the page publishes process/material content.
- PROG-000117 `research_areas` is split across two fill rows because the department's eight-area list exceeds the 25-word quote cap.

## Borderline calls (flagged for the integrator)

1. **Lei Zhu → PROG-000011 (Soft Matter Characterization Laboratory), LINK — weakest witness in the packet.** The CWRU iLab core listing names Zhu as the lab's contact in the same block as the lab's description (the listing's columns are core name / description / primary contact). That is a center page naming a person, but a primary-contact listing, not a faculty or member roster. His PROG-000117 link is clean (department faculty page).
2. **Genevieve Sauve → PROG-000117, LINK on a secondary appointment.** Her own lab page styles her "Professor of Chemistry / Secondary appointment in Macromolecular Science and Engineering." The witness names the program explicitly, but the appointment is secondary; tier accordingly.
3. **Laura Bruckman → PROG-000012 (SDLE), LINK via roster listing.** She appears under "Research Faculty" on SDLE's Researchers page; her listing line there carries her MSE title, so the tie to SDLE is the roster placement, not the quoted line. Her PROG-000106 (MSE faculty listing) and PROG-000027 (MDS-Rely — CWRU news styles her "director of MDS-Rely") links are direct.
4. **PROG-000028 (CAPP) scale_band** rests on the director page's statement of the director's own project portfolio ("five scientific R&D projects and another twelve in cooperation with industry, for a total funding in excess of $5,000,000"). It is the only size fact CAPP's own pages publish, but it is a director-portfolio figure, not a center budget.
5. **PROG-000011 scale_band** is a staffing fact ("managed by two technical staff and a number of graduate students and postdocs") — the only size fact the lab's dedicated page publishes.
6. **Degree-program fills (PROG-000106, PROG-000117, PROG-000108)** use curriculum/catalogue phrasing where the institution publishes nothing lab-like: PROG-000106 `specialty_processes` is a curriculum sentence and its `specialty_materials` is the ABET program-criteria list; PROG-000117 `specialty_materials` rests on the single word "biopolymers" in the MS course description. These are the institutions' own words, but they are catalogue grain, not capability grain.
7. **PROG-000018 (PSRF) research_areas** is drawn from the facility's capability text (anionic polymerization). The PSRF page publishes equipment and capabilities only — no research-area statement as such.
8. **Avi Benatar → PROG-000108.** The pool styles him "Professor of Welding Engineering"; OSU's MSE Department Faculty directory lists him as "Professor, Materials Science and Engineering" with research areas Polymers / Welding Engineering. The directory is the witness used; the two titles coexist (Edison Joining Technology Center).

## Gaps left unfilled (with reason)

- **PROG-000011 specialty_materials** — the lab is technique-defined; neither its dedicated page nor the iLab listing publishes a materials phrase ("soft matter" appears only in the name).
- **scale_band** unfilled for PROG-000013 (EWI's polymers capability page publishes no size fact), PROG-000019 (PENRA publishes none), PROG-000106 and PROG-000117 (bulletin pages publish no cohort/faculty size; a department news headline about an Army grant is funding news, not a size fact, and was not used).
- **PROG-000018 scale_band** — the one candidate fact (kiloclave reactor range 0.5–10 L) survives only inside a garbled, table-merged sentence in the page's text layer; not quotable verbatim, so not proposed.

## NO_WITNESS scope

Verdicts rest on the lane's program/department/center pages (the witnesses cited in links.csv), read in full — including the complete OSU MSE Department Faculty directory (two pages, surnames Ahadi–Windl). Employment at CWRU or OSU alone was not treated as a link, per the brief. Notable near-misses:

- **Péter Polyák (PERSON-000096) → PENRA: NO_WITNESS.** He is a research scientist in the Puskas group and co-authors natural-rubber work, but neither PENRA page names him, and OSU's own FABE awards page lists PENRA's FABE members as Cornish, Michel, Soboyejo, Shah, and Puskas — he is not among them. Group membership was not upgraded to program membership.
- **Judit Puskas → PENRA: LINK** on that same FABE awards page (an institution page), because PENRA's own Researchers/Members pages do not name her.
- PSRF's page names its two staff (Dr. Luke Lewis, Dr. Maria Quiñonez-Angulo); neither is in the people pool. CEMAS's industry page names no pool person. No pool person is named by any lane-B center page other than those linked above.

## Ohio Innovation Exchange (OIEx) — yield

**Grade: no usable yield for this lane.** The OIEx homepage is reachable and its Experts/Equipment/Services databases exist, but expert-profile and facility deep pages are script-driven and exposed no verifiable profile text to web search or to page fetches in this lane (a site search for a known expert surfaced only other institutions' pages). No fill and no link in this packet rests on OIEx — there are zero `source_kind=oiex` rows — and no OIEx lead changed any outcome: every gap was either settled on an institution page or left open for a stated reason. OIEx remains a plausible corroboration source for a browser-driven pass, but it cannot be cited from what is fetch-verifiable here, and nothing was silently upgraded from it.

## Failed / odd fetches (availability signals only — never treated as absence)

- `cwru.corefacilities.org/service_center/4627/?tab=about` redirects to the general core listing `/landing/76`; the Soft Matter lab has no dedicated iLab page reachable that way. Its dedicated CWRU page (case.edu core-facilities) was used instead.
- `mds-rely.org` — curl returned 000; browser text fetch succeeded.
- `mse.osu.edu` and `cemas.osu.edu` — curl blocked (403 / Cloudflare wall); browser text fetch succeeded for the directory (both pages), the MSE major page, and the CEMAS industry page.
- `fabe.osu.edu/node/10332` — curl returned a 404 page; the browser text fetch returned the full article and the PENRA member sentence was verified there verbatim.
- `fabe.osu.edu/our-people/dr-peter-polyak` (the pool's profile URL for PERSON-000096) — curl returned a 404 page. Recorded as a route failure only; the NO_WITNESS verdict rests on the PENRA and FABE pages above, not on this fetch.
- CAPP's `engineering.case.edu/centers/capp/about` is thin/legacy; the substantive citable page is the center's Director page (used).

## Record defects spotted

1. **PROG-000028 (CAPP) — worklist/record URL points at the wrong page.** The URL on the row is the Macromolecular Science & Engineering department page, not CAPP's own pages. CAPP = Center for Advanced Polymer Processing; its citable page found is the Director page at `engineering.case.edu/research/centers/advanced-polymer-processing/director`. Recommend repointing the record URL.
2. **PROG-000011 — record URL is the generic CWRU iLab landing** (`cwru.corefacilities.org`, redirecting to a listing of all cores). The lab's dedicated page is `case.edu/research/resources-facilities/core-research-facilities/soft-matter-characterization-laboratory` (used for the fills). Recommend repointing.
3. **People-pool title staleness (minor).** Svetlana Morozova (PERSON-000080) is carried in the pool as Assistant Professor; CWRU's current department faculty page styles her Associate Professor. The pool also styles PERSON-000013's name "Joao Maia" where CWRU's pages use "João Maia".

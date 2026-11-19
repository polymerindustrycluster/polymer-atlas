Refute this data PR for the Polymer Atlas (public dataset of US polymer professors). Do not edit anything. Each row below is a
proposed new people record. An earlier pass held each one on a single open question; a second source (Meta's Muse) answered
it, and every quote below was then machine-verified word for word on the university's own page by a fresh re-fetch
(surname within 40 words of the Gate A quote). The note says what changed. Rules (SCHEMA 4.9):
- Gate A: the university's own page styles the person, CURRENTLY, as professor / associate_professor / assistant_professor /
  research_professor (assistant/associate/full research professor) / center_director_professor (director with a professor
  title) / senior_lecturer. Emeriti, adjuncts, lecturers (other than senior lecturer), professors of practice, teaching
  professors, research or staff scientists, visiting and courtesy titles FAIL. A person whose primary appointment is
  elsewhere FAILS at this institution.
- Gate B: the person's own profile or lab page states polymer-specific research (polymers, macromolecules, plastics,
  rubber/elastomers, polymer-matrix composites, polymer membranes, hydrogels/polymer networks, polymer coatings/adhesives,
  polymer processing). Generic soft matter / materials / biomaterials / nanomaterials with no polymer named FAIL; so do a
  department blurb, a news story, a publication or grant title, or polymers named only as a tool in non-polymer work.
For EACH row: SOUND, or WRONG (which gate fails and why), or DOUBT (the fact that would settle it). Be strict: the record is
public. End with the count of SOUND / WRONG / DOUBT. Under 800 words; one line per row, starting with the lead_id.

ROWS:
[
{
"lead_id": "BB-0212",
"name": "Daniel Vincent Krogstad",
"institution": "ORG-004657",
"role": "research_professor",
"role_as_published": "Associate Research Professor",
"gate_a_quote": "Associate Research Professor, Materials Science and Engineering, University of Illinois at Urbana-Champaign, 2025-present",
"gate_a_url": "https://matse.illinois.edu/people/profile/dkrogsta",
"gate_b_quote": "His specialty is in understanding and controlling the self-assembly of polymers, gels, composites, and organic biomaterials",
"gate_b_url": "https://matse.illinois.edu/people/profile/dkrogsta",
"note": "Lane row unchanged. Held only for the lead's 'Former' label; Muse re-read the profile: Associate Research Professor, 2025-present."
},
{
"lead_id": "BB-0308",
"name": "Bongtae Han",
"institution": "ORG-004708",
"role": "professor",
"role_as_published": "Keystone Professor",
"gate_a_quote": "Keystone Professor",
"gate_a_url": "https://enme.umd.edu/clark/faculty/546/Bongtae-Han",
"gate_b_quote": "Dr. Han’s research interests include: Characterization of advanced polymers;",
"gate_b_url": "https://calce.umd.edu/our-team-ii",
"note": "Gate B replaced: the lane quoted a project title; the CALCE team page (his own bio entry on the University of Maryland center he works in) lists polymer characterization first among his research interests."
},
{
"lead_id": "BB-0380",
"name": "Renzo Shamey",
"institution": "ORG-002851",
"role": "professor",
"role_as_published": "CIBA Distinguished Professor",
"gate_a_quote": "CIBA Distinguished Professor",
"gate_a_url": "https://textiles.ncsu.edu/people/rshamey/",
"gate_b_quote": "Works of interest include exploring novel techniques to dye polyolefins, as well as the study of photodegradation of fibers",
"gate_b_url": "https://textiles.ncsu.edu/people/rshamey/",
"note": "Lane row unchanged; the lane asked a reviewer to rule. Muse adds the profile's Research Interests item 'Dyeing of Polyolefins (Polypropylene, PE)'. Primary research is color science."
},
{
"lead_id": "BB-0241",
"name": "Vilas Pol",
"institution": "ORG-004662",
"role": "professor",
"role_as_published": "Professor of Chemical Engineering",
"gate_a_quote": "Vilas Pol Professor of Chemical Engineering",
"gate_a_url": "https://engineering.purdue.edu/ChE/research/catalysis-energy?action=view_person&block_id=people_list_2026-07-23-16-28-30-863&group_id=342795&resource_id=105208&profile_id=profile_setting_000",
"gate_b_quote": "reducing interfacial impedance in all-solid-state batteries through hybrid polymer/garnet electrolyte and interface engineering for improved room-temperature performance",
"gate_b_url": "https://engineering.purdue.edu/ChE/research/catalysis-energy?action=view_person&block_id=people_list_2026-07-23-16-28-30-863&group_id=342795&resource_id=105208&profile_id=profile_setting_000",
"note": "Both gates new: the ChE profile now renders. Polymer appears inside his battery research (polymer/garnet electrolytes; also 'flexible polymer-based devices'); his field is electrochemical energy storage."
},
{
"lead_id": "BB-0233",
"name": "Kelly M. Schultz",
"institution": "ORG-004662",
"role": "professor",
"role_as_published": "Professor of Chemical Engineering",
"gate_a_quote": "Kelly Schultz Professor of Chemical Engineering",
"gate_a_url": "https://engineering.purdue.edu/ChE/about/faculty-staff",
"gate_b_quote": "Polymers and Materials",
"gate_b_url": "https://engineering.purdue.edu/ChE/research/bioeng-biotech?action=view_person&block_id=people_list_2026-07-23-15-21-43-297&group_id=342790&resource_id=293892&profile_id=profile_setting_000",
"note": "Gate B new: her ChE profile's Research Interests list 'Polymers and Materials' (with gels and fluid mechanics). Gate A from the lane."
},
{
"lead_id": "BB-0617",
"name": "Michael Scott Arnold",
"institution": "ORG-004632",
"role": "professor",
"role_as_published": "Professor",
"gate_a_quote": "directed by Professor Michael Arnold of the Department of Materials Science and Engineering at UW-Madison",
"gate_a_url": "https://arnold.engr.wisc.edu/about.html",
"gate_b_quote": "Semiconducting molecules and polymers",
"gate_b_url": "https://arnold.engr.wisc.edu/research.html",
"note": "Gate B from the group's research page, under 'The group has a current focus on materials including:', one of five material classes beside carbon nanotubes and graphene. Gate A from the group's About page (his directory profile did not load at the raw check)."
}
]
# Band-B faculty: leads settled by a second source (2026-11-19)

**+2 people, tier A** (PERSON-002498 and 002499), **+6 evidence rows** (EVD-399385 to 399390, own_site, supports_A).
- Six candidates passed the raw check, and both families judged three SOUND.
- After the review, one of those three is held by the integrator: Han's Gate B page turned out to be stale.
- The other two are admitted (`outcomes.csv`).

**Stacked on #407.** This branch starts from #407 (`agent/claude-code/bandb-people`, +95 people). Its ids sit above #407's:
PERSON-002498 up and EVD-399385 up. The same-name check sees #407's 95. Merge #407 first.

**Where the leads came from.** #407 left 13 faculty held on one open question each, and 34 the lanes could not settle.
Muse (Meta) was asked each open question, with the rule that only the university's own pages count. Its answers are
leads only:
- Muse's Gate B rule was looser than ours: it accepted a department research page. This batch uses #407's lane rule
  (`tasks/bandb-people-2026-11-19/LANE_BRIEF.md`): Gate B must be the person's own profile or lab page.
- Each candidate starts from the lane's own row and replaces only the gate Muse settled (`make_candidates.py`, run from
  the corpus folder `_atlas-corpus/muse-faculty-2026-11-19/`, which holds the lane rows and Muse's answers).

**Gates, unchanged from #407.**
- **Raw check** (`rawcheck.csv`): both quotes were re-fetched and matched word for word, with the surname within 40 words
  of the Gate A quote. All 6 candidates passed.
- **Two-family review** of every candidate (`review_part1.md`, `review_<family>_part1.txt`). Only rows both families judged
  SOUND are admitted (`review_holds.csv`, hash-bound to the packet and the reviews).
- **`build.py`**: a copy of #407's `build_people.py`; only the input file, the id floors and the output folder differ. Own
  domains, SCHEMA 4.9 roles, no `@` or account-identifier URLs, and no name already held.

| lead | name | what Muse settled | outcome |
|-|-|-|-|
| BB-0212 | Daniel Vincent Krogstad | Gate A is current: Associate Research Professor, 2025-present (the lead carried a "Former" label) | admitted, PERSON-002498 |
| BB-0233 | Kelly M. Schultz | Gate B: her ChE profile lists "Polymers and Materials" among her research interests | admitted, PERSON-002499 |
| BB-0308 | Bongtae Han | Gate B: a CALCE bio lists "Characterization of advanced polymers" first among his research interests | held by the integrator: the page is stale (below) |
| BB-0380 | Renzo Shamey | Gate B: his profile's research interests include dyeing polyolefins | held: Antigravity WRONG |
| BB-0241 | Vilas Pol | both gates: his ChE profile now renders; polymer/garnet electrolytes in his battery research | held: Antigravity WRONG |
| BB-0617 | Michael Scott Arnold | Gate B: his group's current materials focus includes "Semiconducting molecules and polymers" | held: Antigravity DOUBT |

**Han is held after the review.** His Gate B quote re-reads, but `calce.umd.edu/our-team-ii` is a legacy team page: it
says a colleague "currently serves" at ARPA-E and lists a 2014 assistant professor. CALCE's current team page
(`calce.umd.edu/our-team`) gives his area as "Reliability Assessment of Packaging Materials, Components and Assemblies".
His ME profile lists project titles but states no research. Neither reviewer was told the page's age.

**Not admitted: owner questions** (`owner_rows.csv`, re-read in `owner_rawcheck.csv`):
- **Muse said PASS on both gates, but the Gate B page fails our rule.** Every quote below re-reads.
  - Healy (BB-0037): the hydrogel quote describes lab members' projects, not his own research.
  - Aguado (BB-0046): the hydrogel quote is on a department REU program page.
  - Szleifer (BB-0181): the polymer quote is on a research-center page.
  - Gabrielson (BB-0218): the hydrogel quote is a 2011–12 postdoc entry in another faculty member's lab.
  - Correa (BB-0406): the polymer quote is on his lab's own site, which is off the university domain. His Columbia profile
    did not load at the raw check.
- **Gate A conflicts.** These are not Gate B questions.
  - Zimmerman (BB-0220): Illinois's own pages style him both Research Professor and Professor Emeritus.
  - Allcock (BB-0491): Penn State's own pages style him both Atherton Professor and Professor Emeritus. Muse answered
    NOT FOUND.

Every other Muse answer was FAIL or NOT FOUND on a gate; those leads stay held.

## Review

Codex (deep) and Antigravity (Gemini, deep) each reviewed all six candidates. Grok returned HTTP 402 (no credits), so
Antigravity stood in.
- **Codex:** 6 SOUND.
- **Antigravity:** 3 SOUND, 2 WRONG, 1 DOUBT.
  - **Shamey, WRONG.** Polyolefins are only the substrate in color-science work.
  - **Pol, WRONG.** Polymer is only a component in battery research. Its other reason, that the quote is a publication
    title, is wrong: the quote is from his profile's research statement. The judgment on the first reason stands.
  - **Arnold, DOUBT.** Gate A rests on his group's About page. His university directory profile did not load on any route
    at the raw check or on a retry; it would settle the doubt.

The three it did not judge SOUND are held (`review_holds.csv`). Han, whom both judged SOUND, is held in `build.py` (above).

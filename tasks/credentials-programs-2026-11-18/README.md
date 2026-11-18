# US non-degree polymer credentials into programs.csv (2026-11-18)

**Owner ruling 2026-11-18:** polymer-programs-db's US non-degree credentials layer comes into the Atlas "As programs.csv
rows".

**+4 program rows (PROG-000350 to 000353), +8 evidence rows (EVD-397100 to 397107), 2 rollup cells.** The rollup
cells are `polymer_program_name` and `polymer_program_url` on ORG-000090 (Rubber Division, ACS) and ORG-002089
(Ferris State); validator V-16 requires them to follow the program rows.

| Program | Provider | Prong |
|-|-|-|
| Plastics Institute (workshops) | Ferris State University, ORG-002089 | (a) |
| Rubber Technology Self-Paced Training (Basic, Intermediate, Advanced) | Rubber Division, ACS, ORG-000090 | (a) |
| Paulson University online plastics training | Paulson Training Programs, ORG-002934 | (a) |
| Paulson ProMolder 1 | Paulson Training Programs, ORG-002934 | (b) |

**Method.** Each row has an existence quote and a scope quote from the provider's own page (`packet.csv`), and both
passed an independent raw re-fetch (Firecrawl, then Jina) with a word-sequence match (`rawcheck.csv`).

**Field choices.**
- **`admissions_status` = unknown:** no dated intake was checked.
- **Blank fields:** location, specialty and geography are left blank because they are unverified.
- **`engagement_modes`:** `training_seats_open_enrollment` for the three public courses. `customized_employer_training`
  for Paulson University, which is sold to companies for their own staff; that is the closest term in the vocabulary.

**The other 25 of the 29 credentials** are dispositioned in `holds.csv` (unit: credential rows). The 4 applied rows are
credentials 5, 6, 19 and 20; #20, Paulson's ProMolder certification, is recorded as ProMolder 1 under Paulson, without
the Penn College credit link.

| Disposition | Rows |
|-|-|
| Already held under the same institution and name | 9 |
| REJECT: an occupation code, and a credential that is not polymer by name | 2 |
| Provider has no Atlas record (Plastics Institute of America, AIChE, Ivy Tech, Northwood Tech) | 4 |
| Owner question: polymer-process training without a polymer word in its name (RJG x3) | 3 |
| Other STILL_UNCERTAIN: Beaumont x3 bot-walled, Routsis 404, SPE and Adhesion Society cited only to secondary pages, SAMPE tutorials at event grain | 7 |

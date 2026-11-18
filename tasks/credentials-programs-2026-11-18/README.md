# US non-degree polymer credentials into programs.csv (2026-11-18)

**Owner ruling 2026-11-18:** polymer-programs-db's US non-degree credentials layer comes into the Atlas "As programs.csv
rows".

**+2 program rows (PROG-000350, PROG-000351), +4 evidence rows (EVD-397100 to 397103), 2 rollup cells.** The
rollup cells are `polymer_program_name` and `polymer_program_url` on ORG-000090 (Rubber Division, ACS) and ORG-002089
(Ferris State); validator V-16 requires them to follow the program rows.

| Program | Provider | Prong |
|-|-|-|
| Plastics Institute (workshops) | Ferris State University, ORG-002089 | (a) |
| Rubber Technology Self-Paced Training (Basic, Intermediate, Advanced) | Rubber Division, ACS, ORG-000090 | (a) |

**Codex refute (deep) of the 4-row draft:** 2 SOUND and 2 WRONG.
- **Paulson University** duplicated PROG-000302; my duplicate check needed an exact name.
- **Paulson ProMolder 1** failed prong (b): plastics-processing course content is not a polymer track.

Both are now in `holds.csv`.

**Grok refute (deep) of the 2-row set:** both rows pass the inclusion rule, prong (a). Fields it found unsupported,
now fixed:
- `credential_types` was `incumbent_worker_training`; it is now blank.
- `engagement_modes` had no quote; it now carries a raw-checked quote in the row notes.
- Ferris's one-line description used words outside the quotes; it now uses only the page's own wording.

The Rubber Division rollup cells now show the course name and URL instead of the association's. Validator V-16
requires this once an institution has a program row.

**Method.** Each row has an existence quote and a scope quote from the provider's own page (`packet.csv`), and both
passed an independent raw re-fetch (Firecrawl, then Jina) with a word-sequence match (`rawcheck.csv`).

**Field choices.**
- **`admissions_status` = unknown:** no dated intake was checked.
- **Blank fields:** location, specialty and geography are left blank because they are unverified.
- **`engagement_modes`:** `training_seats_open_enrollment` for both courses. The quotes are "This course is intended for anyone with
  a basic knowledge of injection molding concepts" (Ferris) and "You can complete your studies at your own pace" (Rubber
  Division).
- **`credential_types`:** left blank; neither page states a credential type.

**The other 27 of the 29 credentials** are dispositioned in `holds.csv` (unit: credential rows). The 2 applied rows are
credentials 5 and 6.

| Disposition | Rows |
|-|-|
| Already held under the same institution and name | 10 |
| REJECT: an occupation code, and a credential that is not polymer by name | 2 |
| Provider has no Atlas record (Plastics Institute of America, AIChE, Ivy Tech, Northwood Tech) | 4 |
| Owner question: polymer-process training without a polymer word in its name (RJG x3, Paulson ProMolder 1) | 4 |
| Other STILL_UNCERTAIN: Beaumont x3 bot-walled, Routsis 404, SPE and Adhesion Society cited only to secondary pages, SAMPE tutorials at event grain | 7 |

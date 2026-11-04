# Lane L2 notes (MI STRONG wave, 2026-11-04)

Input: 21 clusters. Output: `verdicts.csv` (21 rows, 22 columns).

## Counts
- VERIFIED_NEW_ORG 14 (all tier C): NCP Coatings, Vintech, Acrofab, JAC Products, Intex Technologies, KAM Plastics, Stone Plastics, Gemini Group, Eclipse Mold, Andex, National Manufacturing Group (MPI), Polyply, Sturgis Molded, Forming Technologies.
- VERIFIED_NEW_SITE 2 (tier B): Royal Technologies Quincy under ORG-004107; Huhtamaki Coleman under ORG-000885.
- REJECT 2: American Jetway (Quest Specialty cleaning chemicals), Freiborne (metal pretreatment chemistry).
- STILL_UNCERTAIN 3: Plast-O-Foam (no reachable own site), Creative Foam Fenway (site named, activity not stated), Aspen Technologies (identity and activity unknown).
- DUPLICATE_OF 0. No dated closure found for any candidate.

## Method
- `atlas.py dedupe-check` (name, street, city, zip) for all 21; Huhtamaki also by domain. Step 3 (street) found no held site anywhere.
- Own-site text pulled with a stdlib script and every `own_quote` re-checked as a verbatim substring of its `own_url` page text (18 of 18 true; whitespace-normalized, TLS verification off because acrofab.com serves a mismatched certificate).
- Federal rows are leads; NAICS never settled scope. New org = tier C by the lane rule even where an own-site witness exists.

## For the integrator
- Royal: 3765 Quincy St (Royal Center HQ) and 2905 Corporate Grove are further unheld sites under ORG-004107.
- Huhtamaki: ORG-000885 is named "Huhtamaki, Inc. - New Vienna"; domain matches exactly. Consider renaming or reparenting before adding Coleman.
- Creative Foam: ORG-000769 carries HQ Dayton OH, but the own site gives Corporate at 300 N Alloy Dr, Fenton. Engineering and Development at 1139 S Fenway Circle is unheld.
- Vintech Complex 620 (620 Industrial Park Dr), Gemini's other Ubly plants (Regency, Valley Enterprises), Eclipse's tooling and assembly plants, JAC Pontiac HQ are additional unheld sites.
- Org HQ is filled only where the site gives a labeled HQ or a sole address (noted per row). Eclipse and MPI left blank.
- Counties blank in the federal row were filled from city geography (Holland, Zeeland, Chesterfield, Escanaba, Sturgis, Muskegon); flagged in notes.
- Gemini: Ubly entity Pepro Enterprises dba Gemini Plastics; org proposed at Gemini Group level. MPI: org proposed at National Manufacturing Group level; a division-level org is the alternative.
- Stone Plastics Zeeland is not the Cadiz KY Stone Plastics acquired by CM Packaging / D&W Fine Pack.
- NCP: own site names Niles only as Headquarters; plant production at Niles rests on an EGLE inspection report (not own-site). Still new org, tier C.
- Unchecked: Form 5500 gate (only required before closure or no-establishment rejects, none issued); Vintech TPV material not mapped to a vocabulary term.

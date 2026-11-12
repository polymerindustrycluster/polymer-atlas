# Integrator notes (running)

## Shawnee PROG-000148 — SETTLED 2026-11-11 (integrator browser check)

Lane C's settling check, run by the integrator in the live browser 2026-11-11: PROG-000148's own
catalog URL (https://catalog.shawnee.edu/preview_program.php?catoid=60&poid=4352, 2026-2027 Course
Catalog) loads fine in a real browser. Heading verbatim: **"Plastics Engineering Technology Minor"**.
Opening sentence verbatim: "A minor in plastics engineering technology offers students in any of
Shawnee State's other baccalaureate programs an opportunity to broaden their major course of study
with an auxiliary focus in plastics engineering technology."

Verdict: PROG-000148 **is the Minor** — not a duplicate of PROG-000001 (the BS). Its defect is
`program_type=degree` with `credential_types=minor`, `level=none`. Integration fix: retype the row
(check how the other minor-carrying rows are typed — e.g. the Penn State Polymer Science Minor row is
program_type `course` — and match precedent so validate stays green), keep credential_types=minor,
and name the program "Plastics Engineering Technology Minor" if the row's program_name is amended
under the same fix. Evidence: one scope row quoting the heading + opening sentence, own_site.

## Shawnee AAS sub-question — SETTLED 2026-11-11 (integrator browser check): NO AAS

Second browser check, same catalog (catoid=60, 2026-2027): exactly three Plastics program pages exist —
"Plastics Engineering Technology BS" (poid=4351), "Plastics Engineering Technology Minor" (poid=4352),
"Plastics Manufacturing Certificate (12 Hours)" (poid=4460). No Associate/AAS plastics page: the
exact-phrase search returned only BS + Minor; the broader "Plastics" search added only differently
named programs (CADM AAS, Electromechanical AAS, CADD Minor); the full Degrees and Programs listing's
AAS section holds 10 programs, none plastics. Lane C's "AAS" line came from a non-catalog listing and
does not survive the catalog; the 2026-11-02 two-way feed's "AAS lapsed" was right on that point (it
missed the active BS, which the Atlas has). **No create.** Shawnee's three Atlas rows map 1:1 to the
three real credentials; the only fix is PROG-000148's retype.

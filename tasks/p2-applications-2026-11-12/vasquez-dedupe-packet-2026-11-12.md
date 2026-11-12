# People dedupe packet — Erick S. Vasquez-Guardado (2026-11-12)

**Verdict: DUPLICATE_OF.** PERSON-001331 ("Erick Vasquez") is the same person as
PERSON-000066 ("Erick S. Vasquez-Guardado"), both recorded at the University of Dayton.
Merge into the **older** record, PERSON-000066 (standing rule; owner decision 2026-11-03;
PRs #260/#264/#265 pattern); PERSON-001331's row is removed from `people.csv`, declared in
the integration packet's `REMOVALS.csv`, logged in `data/inclusion_log.csv`, and its ID
retired, never reused. Merge authorized by the owner 2026-11-12. This packet is research
only — the integrator applies it.

**Lead:** the Ohio academic depth pass (PR #269, packet
`tasks/ohio-academic-depth-2026-11-11/`) flagged the pair: identical directory profile
URL, title, and specialty. Re-verified against Dayton's own pages 2026-11-12 (below) —
the flag holds on every leg.

## The two records (as they stand on main, head `223253e3`)

| field | PERSON-000066 (survivor) | PERSON-001331 (duplicate) |
| --- | --- | --- |
| full_name | Erick S. Vasquez-Guardado | Erick Vasquez |
| institution_org_id | ORG-001315 (University of Dayton) | ORG-001315 |
| program_org_id | *(blank)* | *(blank)* |
| role | associate_professor | associate_professor |
| role_as_published | Associate Professor | Associate Professor |
| research_specialties | biomedical_polymers | biomedical_polymers; nanocomposites |
| public_profile_url | https://udayton.edu/directory/engineering/chemical-and-materials/vasquez-guardado-erick.php | *(identical)* |
| sources | https://udayton.edu/engineering/academics/chemical-materials/faculty-staff.php | https://udayton.edu/directory/engineering/chemical-and-materials/vasquez-guardado-erick.php |
| verification_tier | B | A |
| last_verified | 2026-10-29 | 2026-11-03 |

**Identifiers:** PERSON-000066 carries ORCID `0000-0002-4811-6155`
(`orcid_record_employment_match_ror`, as of 2026-11-09). PERSON-001331 carries none —
the iD was never double-claimed, so there is no §4.21 dedupe alarm to resolve and no
identifier motion in the merge.

**Evidence rows:** neither record has any row in `data/evidence_people.csv` (Dayton's
Ohio-pass lane returned no program link for either). PERSON-001331 is referenced nowhere
outside `data/people.csv` (full-tree grep 2026-11-12) — the merge touches `people.csv`,
`people_identifiers.csv` (no change), one appended evidence row, and one inclusion_log
row. People count effect: 1,451 → 1,450.

## Identity evidence (fetched 2026-11-12)

1. **One person in Dayton's own directory.** The Chemical and Materials Engineering
   faculty listing (https://udayton.edu/engineering/academics/chemical-materials/faculty-staff.php)
   carries exactly one Vasquez entry: "Erick S. Vasquez-Guardado — Associate Professor"
   (photo alt text "Erick Vasquez-Guardado"). No second Erick Vasquez appears anywhere
   in the department.
2. **The shared profile page is his**, titled "Erick S. Vasquez-Guardado"
   (https://udayton.edu/directory/engineering/chemical-and-materials/vasquez-guardado-erick.php):
   "Dr. Vasquez-Guardado's technical research focuses on designing advanced
   nanocomposite materials, mainly using magnetic nanoparticles, for water
   purification, biological applications and bacteria detection and eradication…
   encapsulation of magnetic nanoparticles using biocompatible and electrically
   responsive polymers for drug delivery applications." That one paragraph grounds
   **both** records' specialty sets — `nanocomposites` verbatim, `biomedical_polymers`
   in the biological/drug-delivery work. The page's publication list is bylined
   "Vasquez, E. S." — the short form is his publication name.
3. **His own ORCID record carries the short form.** iD 0000-0002-4811-6155 (already on
   the survivor): given-names "Erick S", family-name "Vasquez-Guardado", credit name
   "Erick S Vasquez-Guardado", and **other-names: "Erick S. Vasquez"** — the duplicate's
   name form is the same person's self-published variant (ORCID public record read
   2026-11-12).

Same profile URL + same institution + same title + one directory person + the ORCID
other-name: the identity is established, not merely probable.

## Recommended survivor field set (PERSON-000066)

- `full_name`: **Erick S. Vasquez-Guardado** (unchanged — the institution's current
  styling and his ORCID credit name; the fuller form wins per the Modestino precedent).
- `institution_org_id`: ORG-001315 (unchanged; no re-homing — both records agree).
- `program_org_id`: blank (unchanged; neither record has a program witness).
- `role` / `role_as_published`: associate_professor / "Associate Professor"
  (unchanged — both records agree, and Dayton's listing still styles him so today;
  no title refresh needed).
- `research_specialties`: **biomedical_polymers; nanocomposites** — fold the
  duplicate's superset in; the profile page supports both (evidence point 2).
- `public_profile_url`: unchanged (identical on both records).
- `sources`: **union** — the profile page first, then the faculty-staff listing:
  `https://udayton.edu/directory/engineering/chemical-and-materials/vasquez-guardado-erick.php; https://udayton.edu/engineering/academics/chemical-materials/faculty-staff.php`.
- `verification_tier` / `last_verified`: **A / the integration date** — see the
  judgment call below.

## Judgment call for the integrator (one)

The survivor stands at tier **B** (2026-10-29, witnessed by the department listing);
the duplicate stands at tier **A** (2026-11-03, witnessed by the profile page itself).
**Recommendation: the survivor takes tier A**, with `last_verified` set to the
integration date. Grounds: the A-tier witness (his own directory profile page) folds
into the survivor's `sources` with the merge, and that page was re-read 2026-11-12 for
this packet — still live, same title, same research text — so the A claim stands on a
current read, not only on the duplicate's November 3 one. The merge evidence row then
carries `supports_A`, matching the Modestino/Advincula rows. The conservative
alternative (keep B, note the folded A witness in the evidence row's text) is defensible
but discards a verification the data already holds; every other field merges without
judgment.

## Exact tombstone motion for PERSON-001331 (integrator)

1. `data/people.csv`: delete the PERSON-001331 row; apply the survivor field set above
   to PERSON-000066.
2. Packet folder `REMOVALS.csv` (rides the merge PR), exact row:
   `people,PERSON-001331,"merged into PERSON-000066 (same person: University of Dayton chemical and materials engineering associate professor); id retired, never reused; logged in inclusion_log.csv"`
3. Append one evidence row on the survivor in `data/evidence_people.csv` (next EVD at
   integration), on the EVD-333029 shape: record_table `people`, record_id
   PERSON-000066, claim_type `parent`, claim_detail naming the folded fields and
   "merged duplicate PERSON-001331", source_class `own_site`, source_ref the profile
   page URL, tier_effect `supports_A`, notes carrying the page's styling in order
   ("Erick S. Vasquez-Guardado Associate Professor") plus this packet's ORCID
   other-name fact.
4. Append one `data/inclusion_log.csv` row recording the merge, the authorizing owner
   decision (2026-11-12), and this packet as the record.
5. QUEUE/integration notes: the Ohio packet's PERSON-000066/PERSON-001331 defect flag
   closes with this merge. ID PERSON-001331 is never reused.

# People dedupe — Rigoberto Advincula (2026-11-11)

**Verdict: DUPLICATE_OF.** PERSON-001402 is the same person as PERSON-000477; it is merged into the
older record and its id retired, never reused (owner decision 2026-11-03; AGENTS §3). Declared in
this folder's `REMOVALS.csv`; logged in `data/inclusion_log.csv`; executed by this folder's `build.py`
on the PR #260 pattern.

**Lead:** the ORCID pass 2 dedupe screen (`tasks/people-orcid-2-2026-11-11/`): same name, split
across the two institutions of one joint appointment. Neither record carries an ORCID iD, and no
identifier, engagement, or evidence row references either id — the merge touches `people.csv` plus
one appended evidence row and one inclusion_log row.

## The two records

| field | PERSON-000477 (kept) | PERSON-001402 (removed) |
| --- | --- | --- |
| full_name | Rigoberto Advíncula | Rigoberto Advincula |
| institution | ORG-002814 (ORNL) | ORG-004681 (UT Knoxville) |
| program_org_id | *(none)* | PROG-000154 (UTK MSE graduate programme) |
| role / role_as_published | group_leader / "Governor's Chair Professor and Group Leader" | named_chair / "Governor's Chair Professor" |
| public_profile_url | ORNL staff profile | UTK Governor's Chairs page |
| research_specialties | design, synthesis and characterization of polymers and nanomaterials; macromolecular materials | polymer nanomaterials |
| verification_tier / last_verified | A / 2026-10-31 | B / 2026-11-04 |

## Primary home: UT Knoxville

The Governor's Chair is one joint UT/ORNL appointment, so AGENTS §6 records it once, at the primary
home institution. Both institutions' pages were read 2026-11-11:

- UTK's Governor's Chairs page styles the chair "Governor's Chair for Advanced and Nanostructured
  Materials", places him in UT's Department of Chemical and Biomolecular Engineering, and calls ORNL
  the joint side in so many words: "**Under his dual appointment at Oak Ridge National Laboratory**,
  Advincula leads ORNL's macromolecular nanomaterials group in the Center for Nanophase Materials
  Sciences."
- ORNL's staff page styles the role jointly: "Governor's Chair Professor and Group Leader at Oak
  Ridge National Laboratory **and University of Tennessee**."

That is the PR #260 tie-break (there, the university page styling the lab as the joint appointment
settled UChicago over Argonne): **UT Knoxville is the primary home; ORNL is the dual appointment.**

## Merge

- Survivor PERSON-000477 is re-homed to ORG-004681 (UT Knoxville), mirroring #260's re-homing of the
  older record; takes `program_org_id` PROG-000154 and `role` named_chair from the removed record,
  and the UTK Governor's Chairs page as `public_profile_url`.
- Name normalised to "Rigoberto Advincula" — the form both institutions publish; the kept record's
  accented "Advíncula" does not appear on either institution's page.
- Specialties and sources unioned (UTK page first); the ORNL staff profile remains in `sources`, so
  the lab appointment stays cited. Tier set to A: every surviving field was re-read today on
  institution pages. `last_verified` 2026-11-11.
- One evidence row (EVD-333030, parent claim, own_site, supports_A) records the merge and quotes the
  UTK page's deciding sentence.

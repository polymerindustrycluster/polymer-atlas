# PIC academic-data architecture
Ratified by the owner 2026-11-02; landed at pass 42. Describes how the three PIC academic-data repositories divide the work.

Three repositories, one pipeline:

| Repo | Role | Truth standard |
|---|---|---|
| polymer-programs-db | Institution & program FRAME | IPEDS/NCES records; institution identity keyed by UNITID |
| polymer-faculty-census | DISCOVERY (Layer A) | Unverified candidates only — never cited as fact |
| polymer-atlas | VERIFIED public layer | Gate A/B verification on institutions' own pages; publishes programs + people |

## Flow
1. programs-db maintains the institution frame (UNITID-keyed) and program candidates.
2. The census discovers candidate polymer faculty (OpenAlex/NSF/NIH/patents/rosters)
   and publishes school-level signal counts (census_faculty_by_school.tsv).
3. The Atlas consumes the census's signals to PRIORITIZE its verification queue and
   verifies person-by-person (its R2 machinery is the census's deferred "Layer B").
   Only Atlas-verified records are public facts.
4. Atlas program verification (owed-checks gate) likewise draws candidates from
   programs-db gap lists and the vault, never from the census.

## Join keys and sync points
- IPEDS UNITID is the join key everywhere. On Atlas ecosystem rows it is carried ONLY
  by institution-grain university_college rows (schema-enforced); sub-unit rows join
  through parent_institution_org_id; workforce_training_provider rows join by name.
- The census consumes PINNED snapshots of Atlas/programs-db inputs (no live coupling).
- Atlas consumes census school-signal files by date (as_of), recorded in the wave plan.

## Non-goals
- Verified people are not moved out of the Atlas into the census.
- Census rows are never promoted to Atlas facts without Gate A/B.
- No repo writes into another; exchanges are files with dates and provenance.

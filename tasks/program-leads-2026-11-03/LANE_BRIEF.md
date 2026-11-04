# Lane brief: program leads, Ohio and Pennsylvania (2026-11-03)

**What this is.** These are packet lanes (AGENTS.md §2 rule 7). Each lane runs the **named-program test** (SCHEMA
§4.11 inclusion rule) on leads from two existing lead files:
- `tasks/programs-db-crosswalk-2026-11-03/leads.csv`
- `tasks/ipeds-completions-2026-11-01/leads.csv`

A lead is never evidence. That is the Lakeland rule: a CIP code, an ABET listing, a society chapter, a grant record or
a history note only tells you where to look.

**You never edit `data/` and never run git.** You write only `tasks/program-leads-2026-11-03/lanes/<lane>/`.

## Read first
- SCHEMA §4.11 (programs table, the inclusion rule, `program_type` values) and §4.6 (`engagement_modes`,
  `geography_served`). Search `docs/SCHEMA.md` for "4.11" and "4.6".
- `data/programs.csv`: check every candidate against it, by institution and program name.
- `data/ecosystem.csv`: `org_id` in your input is the held institution record, if there is one.

## Per lead (about 6 fetches max)
1. Find the institution's **own** page or official catalog for the program, center, credential or facility the lead
   points at.
2. Apply the named-program test. It passes only on the institution's own pages, under one of three prongs:
   - (a) a program, center, institute or credential is named, and is polymer, plastics, rubber, composites or
     coatings **by name**;
   - (b) a degree or certificate's own published description names a polymer track, concentration or research area;
   - (c) a facility or service states polymer materials, processes or characterization services as its offer.
3. Verdict:
   - `VERIFIED`: name the prong, and quote the deciding phrase verbatim, in at most 25 words of one continuous span.
   - `REJECT`: give the deciding fact. Examples: the catalog no longer carries it, the institution's own page says
     it closed, or the name is generic with no polymer object.
   - `STILL_UNCERTAIN`: name the fact that would settle it.
   - `DUPLICATE_OF:<PROG-id>`: it is already in `programs.csv`.
4. A failed fetch (403, 404, timeout) is never evidence. A single named course qualifies as `program_type=course`,
   but flag it. Record `admissions_status` only where the page states it.
5. One lead can yield more than one program, for example an AAS and a certificate. Use one output row per program
   found. A lead that yields nothing gets one row.

## Output: `lanes/<lane>/programs.csv`
UTF-8, comma-separated, quoted as needed, LF line endings. Columns:

`lead_institution,org_id,verdict,prong,program_name,program_type,credential_types,level,unit_department,url,evidence_quote,admissions_status,engagement_modes,city,state,verdict_note,observed_date`

- `program_name`: as the page prints it.
- `program_type`: degree, certificate, center, apprenticeship, training, lab_facility or course.
- `credential_types` and `level`: as SCHEMA §4.11 defines them.
- `engagement_modes`: only modes the page states, from the §4.6 set.
- `city` and `state`: the campus where it runs.
- `observed_date`: 2026-11-03.

Also write `lanes/<lane>/NOTES.md`, 5–15 lines. Give counts with units (leads examined, programs VERIFIED, REJECT,
STILL_UNCERTAIN, DUPLICATE_OF) and anything odd.

**Quotes are re-checked word for word.** The integrator re-fetches every `url` raw. WebFetch returns a model's summary
of the page, so copy short exact spans (8–20 words). Say in `verdict_note` when you are unsure a quote is exact. No
emails, phones or personal data.

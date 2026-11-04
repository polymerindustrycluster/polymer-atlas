# Lane P2 notes (2026-11-03)

- Input: 25 lead rows (14 institutions). Output: 32 rows in programs.csv (17 columns, checked). Some leads share one row (the two Penn State Greater Allegheny leads, the two Wright State leads, the two Villanova leads); extra programs found beside a lead get their own rows.
- Counts (output rows): 9 VERIFIED, 10 REJECT, 6 STILL_UNCERTAIN, 7 DUPLICATE_OF (PROG-000001, -000035, -000041, -000068, -000115 x2, -000162).
- VERIFIED: 6 non-course programs (Behrend Polymer Engineering and Science BS, Behrend Plastics Training Academy, Penn State Polymer Science minor, Akron PSPE minor, two Akron certificates) and 3 single courses (Miami MME 232, Villanova ME 7270, Wright ME 4720). Course rows are flagged; they do not pass the institution test alone.
- The Behrend academy, the Penn State minor and the Akron minor and certificates are extras found beside a lead, not named by one. The Akron minor may belong inside PROG-000115 (its note says the minor was recorded but not designed).
- Access: psu.edu program pages and careertraining.sinclair.edu returned 403. Penn State bulletins.psu.edu worked, so the Behrend and Penn State minor evidence uses the bulletin URLs. 403 was never treated as evidence.
- WebFetch gives summaries, so every quote is flagged "confirm" where the span came back paraphrase-prone. Two quotes are list-item strings (Akron certificates). The Akron Chemical Engineering/Polymer Engineering certificate has no page of its own in this pass.
- Odd: Behrend org_id ORG-002779 was taken from held PROG-000035, not from the input (blank there). Terra State and Wright State city values: Terra State "Fremont" is from general knowledge, not the fetched page.
- Seam cases for owner: Wright Materials Characterization Facility (one Raman sentence mentions polymeric materials); UC MSE "Polymers and Soft Matter" area with polymer-named labs (research area, not a degree description).
- Toledo plastics AAS (1992-95) stays STILL_UNCERTAIN because the current catalog was not read; a Toledo Chemical Engineering "Polymer Studies" concentration was seen and is probably PROG-000025.
- No data/ edits, no git, no personal data. Searches via WebSearch were used only to find institution URLs; verdicts rest on fetches of the institution's own domains.

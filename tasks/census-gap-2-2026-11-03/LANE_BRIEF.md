# Lane brief: census-gap follow-up wave (2026-11-03)

This wave follows up the first census-gap wave. **Read `tasks/census-gap-people-2026-11-03/LANE_BRIEF.md` first.**
Its gates, privacy line, effort cap, verdict grammar and output columns all apply unchanged. Only the following differs.

**You never edit `data/` and never run git.** You write only `tasks/census-gap-2-2026-11-03/lanes/<your lane>/`.

## Your input
`lanes/<lane>/input.csv` lists people the first wave left STILL_UNCERTAIN. `verdict_note` names the fact that would
settle each one, and the row shows the URLs already tried. Settle each person on that fact, using at most ~6 fetches
per person. Try the person's own profile and lab or group page on the university domain first.
- Gate B needs a sentence about the person's **current** research that names a polymer object.
- A research-area label alone ("Polymers" in a tag list), a publication title, or past work (a postdoc, a former
  honor) does **not** pass.
- If no such sentence exists after the budget, the verdict stays STILL_UNCERTAIN, and the note names what was read.

## Lane-specific work
- **Lane T (Johns Hopkins, Columbia).** These hosts are bot-walled to ordinary fetches.
  - Fetch them **only** with
    `python "C:\Users\JOHNSW~1\AppData\Local\Temp\claude\C--Users-JohnSwanson\1cac4ecb-7586-49c4-86de-a3851b347614\scratchpad\tavily_fetch.py" <url> [<url> ...]`.
    It prints the saved text file per URL. Read the file. Batch up to 20 URLs per call.
  - It is metered, with a hard cap of 150 URLs in total. Do not re-request a URL that already succeeded.
  - Never use WebFetch or any other route on jhu.edu or columbia.edu.
  - Two roster pages are already saved:
    - https://engineering.jhu.edu/chembe/faculty/
    - https://www.cheme.columbia.edu/faculty
  - Besides your input rows, **sweep both schools**: Chemical and Biomolecular Engineering, Materials Science and
    Engineering, Chemistry, and Mechanical Engineering. Take up to 15 VERIFIED people per school, the clearest
    polymer researchers first.
- **Lane R1.** Besides your input rows, sweep the **Northeastern** College of Engineering rosters, which returned
  503 in the first wave. Cover Chemical Engineering, Mechanical and Industrial Engineering, and Bioengineering. Take
  up to 15 VERIFIED people at Northeastern **in total**, counting the 6 already held from the first wave.
- **Lane R2:** input rows only.

## Already held: check before you add anyone
Check every name against `data/people.csv` (exact name, and surname plus first initial). A person held at the same
university gets `already_in_atlas=yes` and no further work. A person held at a different institution gets
`already_in_atlas=other:<person_id>`; do not verify them again.

## Quotes are re-checked word for word
The integrator re-fetches every gate URL raw and checks that each quote appears verbatim, word for word in order. A
quote that is paraphrased, stitched from two places, or taken from a summary is a failed row. Copy the words exactly
as they appear on the page, at most 25 words, in one continuous span.

## Output
`lanes/<lane>/people.csv` takes the first wave's columns. It has one row per input person, in input order, then any
sweep people. `lanes/<lane>/NOTES.md` takes 5–15 lines and gives counts with units: people examined, VERIFIED,
REJECT, STILL_UNCERTAIN, and already held.

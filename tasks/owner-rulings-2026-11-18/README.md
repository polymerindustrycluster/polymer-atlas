# Owner rulings, 2026-11-18

The repo owner ruled the held battery of 2026-11-17 in session on 2026-11-18, as multiple choice: **"All as
recommended"**, including the added item 1b (AGENTS.md §2 rule 9). This file records each item. Nothing in `data/` is
changed here; each ruling is applied in its own pull request.

## 1. Identifier URLs on people rows: `?u=` network IDs

University of Akron profile URLs of the form `?u=<network id>` carry a person's university account name. On main they
appear in 18 `people.csv` rows and 4 `evidence_people.csv` rows (count at 099497f).

- **Ruled:** replace each such people URL with an identifier-free department or lab page where one exists. Otherwise
  blank the URL and keep the source on the evidence row.
- **Evidence rows are never edited** (SCHEMA §4.13):
  - where an identifier-free page is cited, a later evidence row cites it and answers the old row;
  - where no such page exists, the old evidence row stays as the record's source.
- **No exception for new rows:** a person whose only witness is a `?u=` URL stays held. This applies to the two
  identifier-URL holds of PR #371.

## 1b. Identifier URLs on people rows: `/~username` home directories

The same class as item 1. A `/~username` path also carries a personal account name. On main: 11 `people.csv` rows
(one written without a scheme) on 10 university hosts, and 4 `evidence_people.csv` rows (count at 099497f). A reviewer refuted one on PR #371.

- **Ruled:** treat `/~username` URLs exactly as item 1.

## 2. Teaching-track professors

The question was whether "Professor of Instruction", "Professor of Practice" and "Professor of Engineering Practice"
count as professor rank for Gate A (SCHEMA §4.9). This covers the 13 Akron holds of PR #371.

- **Ruled: no, for now.** Any change comes as a dated §4.9 revision. The 13 stay STILL_UNCERTAIN.

## 3. Faculty Gate B calls (PR #370)

- **West (Kent State, Trustees Research Professor):** accepted as `research_professor`, following the Lavrentovich
  precedent. Add him when a current page states the research.
- **Kothapalli (Cleveland State, ECM hydrogels):** hydrogels are a polymer object. Hold until his own profile states
  the work.
- **Mao (Kent State, DNA and protein biomacromolecules):** not polymer research under §4.9. REJECT stands.
- **Lu (Case Western Reserve, macromolecular contrast agents):** keep, as verified at supports_B.
- **CWRU bulletin lines:** these are roster-grade Gate B evidence (Sen Gupta, Akkus), as YSU catalog lines already
  are (PERSON-000071).

## 4. Mallik (Akron Physics)

The page uses polymers only as substrates.

- **Ruled: REJECT**, following the McComb precedent.

## 5. Pedro Cortes

The Atlas holds him at UTEP (PERSON-001142), but the 2022-23 catalog lists him at Youngstown State.

- **Ruled:** a re-verify task, not an edit (see `tasks/QUEUE.md`).

## 6. B-MARKETS-VOCAB (PR #360)

The candidate terms were Alternative Energy, retail security, water heaters, recreation surfaces and window
coverings.

- **Ruled:** no new `markets_served` terms. The holds stay.

## 7. Die and tooling manufacture (PR #365, SITE-000014)

- **Ruled:** not mapped to `mold_tool_making`. Any change comes as a dated vocabulary revision.

## 8. Castinite (SITE-001986, PR #361) and verified terms on non-blank cells

Two questions:

1. Does polymer-concrete casting map to `potting_encapsulation_casting`?
2. May a verified term be appended to a non-blank processes or materials cell?

- **Ruled:**
  1. Not mapped.
  2. Yes. A verified term may be appended to a non-blank cell (union with the existing values, nothing removed).

  The second ruling covers SITE-001986's materials cell. The same union operation for the 10 held terms on 7 sites
  from PR #365 was a controller decision of 2026-11-17, consistent with this ruling.

## Recorded with these rulings: PPP historical employee bands (owner ruling 2026-11-16, "Strict matches")

The ruling was first recorded in `tasks/ppp-size-bands-2026-11-16/README.md` and applied in PR #348. It is now recorded
as SCHEMA v1.13.3, an addendum to §1 R13.

PPP loan job counts may fill **blank** employee bands only, under all of these conditions:

- each value is labelled with its 2020 or 2021 loan date;
- an existing band is never overwritten;
- only for single-site, Ohio-only organizations where the borrower's name, street and city all match.

Name-and-city matches and every other use stay leads.

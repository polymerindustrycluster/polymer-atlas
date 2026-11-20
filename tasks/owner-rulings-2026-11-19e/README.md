# Owner rulings 2026-11-19e: the Muse follow-ups (2026-11-20)

**+2 `year_founded` values on 2 organizations, +2 evidence rows (EVD-400500 and 400501).** Seven candidates, 2 filled and
5 held (`outcomes.csv`). The other three rulings change no data; they are recorded in `DECISIONS.md` (2026-11-20).

## The rulings (owner, in session, 2026-11-19/20, as multiple choice)

1. **Gate B for people stays strict.** Muse accepted looser Gate B pages for four faculty held by #413 (Aguado: a
   department REU page; Szleifer: a research-center page; Healy: his lab page describing members' projects; Correa: an
   off-domain lab site). All four stay held. Gabrielson also stays held, because his only quote is a 2011–12 postdoc entry.
2. **Emeritus conflicts are held.** Zimmerman (Illinois) and Allcock (Penn State) stay leads until one current university
   page settles the conflict.
3. **Sterilite's LEI stays.** Muse called the link PARENT because our record's HQ field says Massillon, OH. The record is
   the parent, though: its legal name is Sterilite Corporation, and it holds that company's plants in Townsend MA (the
   company's HQ), Birmingham AL, Davenport IA and Clinton SC as well as Massillon. OSHA names "Sterilite Corporation" as
   the operator of the out-of-state plants. The owner first chose "remove" when the question framed the record as an Ohio
   plant. That framing was wrong, and the owner reversed the choice on the corrected facts. The HQ field is the error (follow-up below).
4. **`year_founded` may use a second source in place of #406's address gate.** For an LEI whose GLEIF address does not
   name the organization's HQ, Muse's SAME verdict (2026-11-19) plus a re-read quote from the company's own page may
   stand in. Plastipak is excluded, because its only quote is on a third-party page (ndt.org).

## The fills (`build.py`)

`build.py` runs every other #406 gate live against main: the organization is active, its `year_founded` is blank and
it is not tier A, and the LEI entity is ACTIVE, US-registered and has a creation date. It adds one check:
GLEIF's field-modification history (`raw/`, fetched 2026-11-20) must show no change to the creation date. A candidate
that is not held and fails a gate stops the build. Planted defects (an edited date, a set year, tier A, a non-US
entity, an inactive entity) were each refused.

Before review, each company's own pages were re-read (`sources.csv`). Three state a different year, so they were held
before review:

| org | GLEIF | outcome | why |
|-|-|-|-|
| ALPLA Inc. (ORG-000664) | 2001-03-14 | **filled 2001** | ALPLA's page: "ALPLA North America was established and headquartered in McDonough Georgia in 2001." Its location list gives ALPLA INC.'s regional HQ at GLEIF's address and the Lima plant |
| Storopack, Inc. (ORG-001128) | 1978-02-08 | **filled 1978** | Storopack's fact sheet: "1978 Start of business activities in the USA." Its imprint gives Storopack Inc. in Cincinnati |
| Molten North America Corp. (ORG-000965) | 1990-11-01 | held after review | Antigravity DOUBT (codex SOUND): the company says it "extended its business to ... the United States, in December 1991" |
| Sealed Air Corporation (ORG-000566) | 1996-01-29 | held before review | its FY2020 10-K: "was incorporated in Delaware in 1960"; possibly a successor or reorganization, which the formation-year ruling does not cover |
| Ridge Corporation (ORG-001080) | 1994-02-14 | held before review | its own site: "Ridge Corporation was incorporated in 2004"; GLEIF's record is the renamed Techna Composites Incorporated |
| MSI Express Inc (ORG-001471) | 1998-12-31 | held before review | its FAQ: "formed through the merger of Express Packaging (founded in 1988) and Manufacturing Solutions International (founded in 2008)"; a year-end date, and Ohio SOS was unreachable |
| Plastipak Packaging, Inc. (ORG-001033) | 1982-05-24 | held | ruling 4 excludes it |

The two evidence rows are `existence` claims from the `registry` class at `supports_B`, citing the GLEIF record. Each note gives
the ruling, the tie quote and the year quote with their URLs.

## Review

Codex (deep) and Antigravity (Gemini, deep) reviewed the three candidates in `review_packet.md`. Grok still returns HTTP 402
(no credits), so Antigravity stood in again.
- **Codex:** 3 SOUND.
- **Antigravity:** ALPLA SOUND, Storopack SOUND, Molten DOUBT.

Only rows both families judged SOUND are applied: 2. Molten is held in `build.py` with the reviewer's reason. Codex's
reading, that a November 1990 formation can precede a December 1991 market entry, is plausible but not settled. The Ohio SOS
filing for charter 783787 would settle it.

## Follow-ups (not done here)

- **HQ fields that name a plant.** Sterilite (ORG-001384, Massillon, OH; the company's HQ is Townsend, MA) and ALPLA
  (ORG-000664, Lima, OH; ALPLA INC.'s regional HQ is McDonough, GA). MSI Express (ORG-001471, Groveport, OH; corporate
  offices in Portage, IN) may be the same case. Moving an HQ moves the record's shard (AGENTS.md §3), so each needs its own pass.
- **Ohio SOS charters** 783787 (Molten), 864734 (Ridge) and 1054053 (MSI Express) would settle three holds. The
  business-checker `ohsos_fetch.py` returned "maintenance" on 2026-11-20.
- **SCHEMA `year_founded` row:** a dated revision should carry the 2026-11-19 formation-year ruling (open since #406).

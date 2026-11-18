# Plastics-processing training under SCHEMA v1.14.1 (2026-11-18)

**Owner ruling 2026-11-18.** Asked whether a polymer-process training program qualifies when its name has no polymer
word, the owner answered "Yes, if the page states plastics processing". SCHEMA §4.11 records the ruling as v1.14.1.

**+3 program rows (PROG-000352 to 000354), +6 evidence rows (EVD-397110 to 397115).**

| Program | Provider | The page's own processing statement |
|-|-|-|
| Master Molder I | RJG, Inc., ORG-003020 | "the manipulation of key processing variables from the plastic’s point of view" |
| Master Molder II | RJG, Inc., ORG-003020 | "focusing on what the plastic experiences in the cavity" |
| Paulson ProMolder 1 | Paulson Training Programs, ORG-002934 | "test your knowledge of plastics processing" |

Each row carries three quotes from the provider's own page, all raw-checked by independent re-fetch (`rawcheck.csv`):
- **Existence:** a sentence naming the program.
- **Scope:** the plastics-processing statement above.
- **Engagement:** the open-enrollment basis.

The existence and scope quotes are evidence rows; the engagement quote is in the row notes. `credential_types` is
blank and `admissions_status` is unknown.

**Held: RJG Train the Trainer Qualification.** The course qualifies trainers to teach RJG's other courses. Its own
description says "injection molding" but never plastics or polymer, and RJG's site-wide navigation does not count under
the ruling.

**Already held:** Paulson ProMolder 1 was not in `programs.csv`. Paulson's only existing row is PROG-000302, Paulson
University Online Training.

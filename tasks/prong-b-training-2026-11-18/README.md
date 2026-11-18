# Plastics-processing training under SCHEMA v1.15.1 (2026-11-18)

**Owner ruling 2026-11-18.** Asked whether a polymer-process training program qualifies when its name has no polymer
word, the owner answered "Yes, if the page states plastics processing". SCHEMA §4.11 records the ruling as v1.15.1.

**+3 program rows (PROG-000352 to 000354), +6 evidence rows (EVD-397110 to 397115).**

| Program | Provider | The page's own processing statement |
|-|-|-|
| Master Molder I | RJG, Inc., ORG-003020 | "the manipulation of key processing variables from the plastic’s point of view" |
| Master Molder II | RJG, Inc., ORG-003020 | "focusing on what the plastic experiences in the cavity" |
| Paulson ProMolder 1 | Paulson Training Programs, ORG-002934 | "test your knowledge of plastics processing" |

The ruling text records the option the owner chose: its label "Yes, if the page states plastics processing"
and its description, "extend prong (b) to non-degree training whose own description says plastics or polymer
processing". The test is the meaning, not a literal phrase, and it applies to `training` rows only.

Each row carries three quotes from the provider's own page, all raw-checked by independent re-fetch (`rawcheck.csv`):
- **Existence:** a sentence naming the program.
- **Scope:** the plastics-processing statement above.
- **Engagement:** the open-enrollment basis.

The existence and scope quotes are evidence rows; the engagement quote is in the row notes. `credential_types` is
blank and `admissions_status` is unknown.

**Held: RJG Train the Trainer Qualification.** The course qualifies trainers to teach RJG's other courses. Its own
description says "injection molding" but never plastics or polymer, and RJG's site-wide navigation does not count under
the ruling.

**Duplicate check:** RJG had no program rows. Paulson's only existing row is PROG-000302, Paulson University Online
Training, which is a different offering.

## Reviews

- **codex (deep): UNSOUND as submitted.** All three programs' scope was supported. Two fixes followed:
  - full-clause examples in the ruling text;
  - the RJG pages' own "This course is available publicly" lines as the enrollment basis.

  Codex also had the text narrowed to "plastics processing" only. That reading was undone below, because the option
  the owner chose says "plastics or polymer processing".
- **grok (deep): UNSOUND.** Its points and what was done:
  - The ruling's reach was extended to `course` rows. Fixed: `training` only.
  - The ProMolder 1 enrollment quote stated no registration. Fixed: "Ask us about the option to register for our new
    online virtual classroom…".
  - Not taken: its reading that the page must contain the literal phrase "plastics processing", which would admit
    only ProMolder 1. The owner chose an option described as "whose own description says plastics or polymer
    processing" and naming these programs as the ones that would be added. That meaning governs.
- **Disclosure:** the option shown to the owner said four programs would be added, including RJG Train the Trainer.
  Under the ruling as described, Train the Trainer does not qualify, because its own description never says plastics
  or polymer. It stays held, and the owner is told.

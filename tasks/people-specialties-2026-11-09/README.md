# People research specialties: HELD, not for merge (2026-11-09)

This pass fills empty `research_specialties` on people records. It is **held** because both review families rated it
UNSOUND. The branch keeps the work so that a stricter second pass can start from it rather than repeat it.

## What ran

- **Frame:** the 396 people records with empty `research_specialties`.
- **Lanes:** eight Sonnet lanes read each person's profile page. Each proposed terms from §3.1, §3.2 and §3.5, plus one
  quote copied verbatim from the page. 306 rows came back VERIFIED and 90 STILL_UNCERTAIN (`packet.csv`).
- **Integrator checks:** all 295 rows that passed are on the institution's own domain.
  - 256 quotes matched word for word on the raw page cached before any lane ran, and 39 on a fresh Jina fetch.
  - 11 rows were held: 5 failed the raw match, 3 used only `other_specified_in_notes`, 1 had a name mismatch, 1 quoted
    a student project, and 1 page could not be fetched.
- **Term gate:** after the first refute, `build.py` drops a term unless its own trigger words appear in the quote. That
  took 295 rows to 259, removing 83 terms and 36 rows.

## Why it is held

| Review | Sample | Result |
|-|-|-|
| codex (deep), before the gate | 40 | 6 WRONG, 8 DOUBT, verdict UNSOUND. The gate fixed all 4 substantive errors; the other 2 are the open vocabulary question below. |
| grok (deep), after the gate | 40 fresh | 9 WRONG, 7 DOUBT, verdict UNSOUND |

The gate checks that a term's word is in the quote. It does not check that the quote states the term as the person's
specialty. Grok's recurring patterns:

1. `characterization_methods` wherever a page says materials were characterized.
2. News ledes about "the team", grant titles, slogans and prospective "hopes to" lines read as the person's research.
3. Terms pulled from example lists ("polymers such as polyurethane") and from passing mentions.
4. `biomedical_polymers` on any sentence pairing hydrogels with biology.
5. Non-polymer work admitted on one polymer-adjacent keyword.

## What a second pass needs

- **Second reading:** an independent adjudication of every term against its definition, kept only where two readings
  agree.
- **Page types:** faculty-profile research statements only, never news, grants or project lists.
- **Vocabulary ruling (owner):** for academic research, the lanes and earlier passes used both §3.1 terms (defined as
  industrial capabilities, e.g. `polymerization` = "resin production as a capability") and the matching §3.5 research
  terms (`polymer_synthesis`), with the same split for recycling and additive manufacturing. Which one people records
  take is a vocabulary question for the owner.
- **Evidence ids:** EVD-333028 is now used by #260. Re-allocate above main and every open PR before applying.

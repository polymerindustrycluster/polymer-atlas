# year_founded from GLEIF for LEI-linked organizations (2026-11-19)

**+25 `year_founded` values on 25 organizations, +25 evidence rows (EVD-399000 to 399024).** The source is GLEIF's
LEI record, `entity.creationDate`, which is the legal entity's formation date. That matches the SCHEMA definition of
`year_founded`: "Legal-entity formation year where a source states it". GLEIF data is CC0. The raw records, fetched
2026-11-19 from api.gleif.org, are in `raw/`.

A value is written only when every gate in `build.py` passes:
- the organization is active, not tier A, and its `year_founded` is blank;
- the LEI entity is ACTIVE and US-registered;
- its legal or headquarters address names the organization's HQ city and state;
- the record has a creation date.

**Not filled (unit: LEI links; 132 in all, 25 filled):**

| Reason | Links |
|-|-|
| REGISTRY_CEILING | 41 |
| LEI address | 28 |
| HELD | 3 |
| LEI entity registered outside the US | 9 |
| no entity.creationDate in the LEI record | 7 |
| LEI entity status INACTIVE | 1 |
| year_founded already set, or organization not active | 18 |

The REGISTRY_CEILING links belong to tier A organizations. A registry source caps at `supports_B`, which validator V-25
refuses as the only existence support for a tier A record. The same ceiling applies to the PIC-18 street lanes.

**Link findings.** `link_findings.csv` lists every link that failed a gate. The address and non-US failures are worth a
look as possible wrong LEI links. At least one is plainly wrong: the Atlas's Vertex, Inc. is a Mogadore, Ohio company,
but its LEI belongs to a Pennsylvania company of the same name. Many address failures are Delaware registered-agent
addresses that cannot confirm the entity either way. This pass changes no link.

**Caveat on meaning.** A legal-entity formation year can be later than the business's founding, for example after a
re-incorporation or a holding-company formation. That is the schema's chosen meaning. Where a page later states a
different founding year, the schema's multi-inception rule applies: the conflict is noted, never silently resolved.

**Owner ruling 2026-11-19.** `year_founded` is the formation year of the legal entity the record describes, even when
the business is older or the entity was later renamed. The older business year goes in the evidence note. This does
not cover a conversion, a re-incorporation into a new entity, a predecessor's charter, or a placeholder date.
Ruled in session as the recommended option ("go with your recommendations"). Follow-up: SCHEMA's `year_founded` row
still says formation conventions are unruled. A dated SCHEMA revision should carry this ruling.

## Reviews

- **codex (deep), all 28 fills:** 27 SOUND, 1 DOUBT. Kraton's LEI was renamed in 2023 from Kraton Polymers
  LLC, and the 10-K dates the corporation to 2009, succeeding a 2003 LLC. Its creation date may be a predecessor's, so
  Kraton is HELD. Codex's general point: name, address and status checks do not prove historical continuity
  through renames. A renamed LEI therefore needs the GLEIF field-modification history before its date is used.
- **grok (deep), the 27 remaining:** 18 SOUND, 1 WRONG, 8 DOUBT; verdict UNSOUND.
  - **WRONG:** Hexion's 1899 date is the Borden Company's New Jersey charter.
  - **DOUBT, rename or conversion dates:** Vibrantz, Struktol, Flow Polymers and Flow Dry.
  - **DOUBT, charter dates later than the business:** Nordson, Molded Fiber Glass, H.B. Fuller and Lear.

  **Only rows both families judged SOUND are applied: 18.** The 9 others were HELD in `build.py` with their
  reasons. A charter or name-history source settles each one. Grok's general point stands: a GLEIF creation date
  can be an ancestor's charter or a conversion date. A further GLEIF pass should check the field-modification
  history and the predecessor links before using a date.
- **Re-review of the 8 holds after the owner ruling (2026-11-19).**
  - **The evidence.** Muse (Meta) sourced each hold. Every fact used was re-read: SEC 10-K text matched word for word,
    the company's own pages, and the previous legal names in our raw GLEIF records. Anything not re-read is labeled
    unverified in the packet.
  - **The reviewers.** Codex (deep) and Antigravity (Gemini 3.8, deep). Grok still returns HTTP 402 (no credits).
  - **The verdicts.** Both judged 7 SOUND and Hexion DOUBT.
  - **7 applied:** Vibrantz 2011, Nordson 1935, Molded Fiber Glass 1946, Flow Dry 2006, H.B. Fuller 1915, Lear 1987
    and Flow Polymers 2010. Their evidence notes carry the older business year or the former name where a re-read
    source gives one.
  - **Hexion stays HELD.** The verified 10-Ks say "a New Jersey corporation with predecessors dating from 1899". The
    proof that it is one continuous corporation rests on sources the SEC blocked us from re-fetching: the 2001
    Borden Chemical 10-K and a WV SOS record. Kraton (a predecessor's date) and Struktol (a possible placeholder date)
    also stay HELD.
  - The packet, the reviews and the re-check logs are kept outside the repo, in
    `_atlas-corpus/muse-2026-11-19/`.

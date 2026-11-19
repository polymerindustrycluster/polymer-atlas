# year_founded from GLEIF for LEI-linked organizations (2026-11-19)

**+27 `year_founded` values on 27 organizations, +27 evidence rows (EVD-399000 to 399026).** The source is GLEIF's
LEI record, `entity.creationDate`, which is the legal entity's formation date. That matches the SCHEMA definition of
`year_founded`: "Legal-entity formation year where a source states it". GLEIF data is CC0. The raw records, fetched
2026-11-19 from api.gleif.org, are in `raw/`.

A value is written only when every gate in `build.py` passes:
- the organization is active, not tier A, and its `year_founded` is blank;
- the LEI entity is ACTIVE and US-registered;
- its legal or headquarters address names the organization's HQ city and state;
- the record has a creation date.

**Not filled (unit: LEI links; 132 in all, 27 filled):**

| Reason | Links |
|-|-|
| REGISTRY_CEILING | 41 |
| LEI address | 28 |
| LEI entity registered outside the US | 9 |
| no entity.creationDate in the LEI record | 7 |
| LEI entity status INACTIVE | 1 |
| HELD | 1 |
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

## Reviews

- **codex (deep), all 28 fills:** 27 SOUND, 1 DOUBT. Kraton's LEI was renamed in 2023 from Kraton Polymers
  LLC, and the 10-K dates the corporation to 2009, succeeding a 2003 LLC. Its creation date may be a predecessor's, so
  Kraton is HELD. Codex's general point: name, address and status checks do not prove historical continuity
  through renames. A renamed LEI therefore needs the GLEIF field-modification history before its date is used.

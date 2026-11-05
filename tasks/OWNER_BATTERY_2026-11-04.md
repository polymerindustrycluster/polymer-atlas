# Owner battery: 2026-11-04

> **RULED 2026-11-04: every item (a), as recommended.** The repo owner ruled in session, as multiple choice. The items
> are B-PARENT, B-SCOPE, B-NEWS, B-LINKEDIN, B-ARCHIVE, B-ALIAS, B-GUARDS and B-SHARD.
> - Each item is applied in its own PR, which cites this file.
> - Schema changes land as dated SCHEMA revisions.
> - B-SHARD needs no change: foreign plants stay held.

Every item needs the owner's ruling (AGENTS.md §2 rule 9). Each item has a recommendation, marked (a), with the
evidence behind it.

## B-PARENT: does a parent's or brand owner's page count as `own_site`? (SCHEMA §4.13)
SCHEMA §4.13 defines `own_site` as "the entity's own domain / own issued document". Evidence repair round 2 (#117)
holds seven raw-verified scope quotes whose page sits on a parent's or brand owner's domain, not the record's own.

| Weak row | Page |
|-|-|
| EVD-008259 | CPChem, about AmSty |
| EVD-007962 | Arkema, about Bostik |
| EVD-011189 | Toray, about Toray PMC |
| EVD-007842 | TotalEnergies |
| EVD-007605 | Rmax |
| EVD-008076 | Florestone |
| EVD-010929 | a Fluid Sealing Association member profile written by Gore |

The same case recurs in every state wave: plants named only on a parent's site.
- **(a) Recommended:** the page counts as `own_site` when two conditions hold. First, the Atlas already records that
  parent, through `parent_org_id` or `ultimate_parent_name` (both are documented relationships, not guesses). Second,
  the page names the plant's city and its activity. Otherwise it counts as `press` (ceiling `supports_B`).
  Association member profiles count as `directory`.
- (b) A parent's page always counts as `press` (ceiling `supports_B`).
- (c) Only the record's own domain counts, and parent pages stay leads.

## B-SCOPE: activity classes the state lanes left STILL_UNCERTAIN (SCHEMA §1–§2)
The state waves (#93, #116) did not rule on these. Each class is listed with the recommended reading of the scope
test: making polymer resins, compounds, plastic or rubber products, composites, or polymer coatings, adhesives or
sealants.

| Class | Example | (a) Recommended |
|-|-|-|
| UV-curable inkjet inks | the lane notes in #116 | in scope when the maker formulates the curable (acrylate) system: a polymer coating chemistry |
| Zinc-rich and zinc-flake coatings | the lane notes in #116 | in scope when the binder is organic (epoxy or urethane); out when it is inorganic silicate |
| Microencapsulation | the lane notes in #116 | in scope when the capsule wall is a polymer the company makes |
| Epoxy photoresists | Kayaku (#116 lane notes) | in scope: epoxy resin formulation |
| Bio-based plasticizers | ACS (#116 lane notes) | Ring 3 (additive supplier), not Ring 1–2 |
| Decorative polymer flake | Torginol | in scope: a vinyl or acrylic polymer product |
| Inorganic oxide colloidal additives | Nyacol (MA lane) | out of scope: no polymer is made or shaped |
| Thermoplastic pavement marking | Crown (GA lane) | in scope: a thermoplastic compound |

- **(a)** As in the table.
- (b) Rule class by class.
- (c) Hold every class as STILL_UNCERTAIN.

## B-NEWS: a newsroom field, and switching on the news monitor (SCHEMA §4.4, QUEUE.md signals sweep)
The v1.6 columns already exist: `monitor_watch` (14 organizations set), `liveness_signal` (305 set) and
`last_activity_evidence_date`. QUEUE.md records that the news monitor is built and validated in a dry run (35 genuine
matches on day one) but not switched on. It has no per-company place to look.
- **(a) Recommended:**
  - Add an optional `newsroom_url` organization column: the company's own news, press or announcements page, own
    domain only. Add an optional `newsroom_feed_url` for an RSS or Atom feed.
  - Fill both first for Tier-1-qualified and PIC-18 organizations.
  - Switch on the monitor in dry-run-to-PR mode. Each hit becomes a re-verification queue item, never an automatic
    status change, as §5 already requires.
- (b) Add the columns, and keep the monitor off.
- (c) No change.

## B-LINKEDIN: a LinkedIn company URL (SCHEMA §4.4 nice-to-have)
SCHEMA ranks a LinkedIn page on its own as tier C, and LinkedIn industry labels as `platform_category`. Post content
sits behind a login, and LinkedIn's terms bar automated scraping.
- **(a) Recommended:** add an optional `linkedin_url` column as a navigation link only. It is never an evidence row or
  a monitoring source.
- (b) Keep LinkedIn pages in `sources` only, as now.

## B-ARCHIVE: archive each own-site quote at mint time (SCHEMA §4.13)
Evidence repair rounds 1 and 2 exist because cited pages changed or vanished after minting: 172 weak scope rows in
round 2, 91 of them with no replacement found.
- **(a) Recommended:** add an optional `archive_ref` evidence column holding a Wayback Machine capture made when the
  row is minted, so a later audit can read what the integrator read. It is a provenance aid only: it never changes
  the source class or the tier.
- (b) No change.

## B-ALIAS: federal registrant names as dedupe aliases (AGENTS.md §3)
The lead-fusion clusters carry federal registrant names that differ from Atlas legal names. Because of this, Dart
(ORG-002441) and WinCup (ORG-000984) were missed as held organizations in the Florida wave.
- **(a) Recommended:** when a federal source is attached to a site, record its registrant name in the organization's
  `trade_names`, marked as a registrant name, so the AGENTS.md §3 name search finds it next time. No new column is
  needed.
- (b) Add a separate `registrant_names` column.
- (c) No change.

## B-GUARDS: validator checks for failures hit on 2026-11-04
- **CRLF files:** three data files are committed with CRLF despite `.gitattributes eol=lf`
  (`organizations_OH.csv`, `organizations_IA.csv`, `evidence_organizations_IA.csv`). CI did not notice.
- **Missing country:** a non-USPS `hq_state` with an empty `hq_country` surfaced only as a V-35 shard mismatch.
- **Appending builders:** they break V-36 (ids ascending) whenever two waves share a shard.
- **(a) Recommended:**
  - a validator error for CRLF line endings in `data/`, plus a one-time normalization PR;
  - a direct error when `hq_country` is empty and `hq_state` is not a USPS code;
  - a shared sorted-append helper in `scripts/` for builders to use.
- (b) Normalize the three files only.

## B-PARENT-WEB (addendum, RULED 2026-11-04): a corporate group's domain as a plant's `website`
The website pass (#121) gave some plant records their corporate group's domain, for example Siliconature, Valmet,
Viscofan USA and Tecomet. The owner ruled in session, as multiple choice: **allow it, and flag it in notes.** A group
domain may stand as a plant's `website`. Each such record carries a notes flag saying so. Applied in
`tasks/ownership-status-2026-11-04/`.

## B-ARCHIVE storage (addendum, RULED 2026-11-05)
B-ARCHIVE was ruled as an `archive_ref` evidence column. Implementing it as a column would rewrite all of the roughly
35,000 evidence rows and change the header every builder writes. The owner ruled in session, as multiple choice:
**store it as a side table**, `data/archive_links.csv` (SCHEMA §4.22, v1.11), with one row per archived evidence id.
The intent is unchanged. The news-monitor switch-on (B-NEWS) waits on its code, which lives in another harness's
working area (`working/news-monitor/`, per QUEUE.md) and is not in this repository.

## B-SHARD: foreign establishments of US organizations (AGENTS.md §3)
Bryant Rubber's Tijuana plant has no lawful site shard, so it is held (#116).
- **(a) Recommended:** keep holding foreign plants, noting each on the organization record, until a dated schema
  revision adds an `INTL` site shard.
- (b) Add the `INTL` site shard now, by schema revision.

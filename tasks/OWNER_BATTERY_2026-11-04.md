# Owner battery: 2026-11-04 (proposed, not yet ruled)

Every item needs the owner's ruling (AGENTS.md §2 rule 9). Each item has a recommendation, marked (a), with the
evidence behind it. Nothing these items gate has been applied: the rows they affect are held in the PRs named below.

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

## B-SHARD: foreign establishments of US organizations (AGENTS.md §3)
Bryant Rubber's Tijuana plant has no lawful site shard, so it is held (#116).
- **(a) Recommended:** keep holding foreign plants, noting each on the organization record, until a dated schema
  revision adds an `INTL` site shard.
- (b) Add the `INTL` site shard now, by schema revision.

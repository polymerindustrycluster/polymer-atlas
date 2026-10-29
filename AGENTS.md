# AGENTS.md — Binding protocol for ALL contributors (human and AI)

This repo is worked on by multiple AI harnesses (Muse, Claude Code,
Codex, Grok, Antigravity, others) and human researchers, in parallel.
These rules exist so parallel work merges instead of colliding. They are
not suggestions. If a rule blocks your task, stop and flag it in your PR —
do not work around it.

## 1. Where truth lives

- The CSVs in `data/` are canonical. SQLite is generated
  (`scripts/build_sqlite.py`); never edit or commit a hand-modified .db.
- Schema, ring rules, NAICS map, and controlled vocabularies live in
  `docs/SCHEMA.md`. Vocabulary/ring changes require a dated schema
  revision in that file — never improvise a new tag, ring, or status
  value inline. Use the `*_other_note` / notes field and flag it.

## 2. How work happens

1. **Claim before you build.** Pick (or add) a task in `tasks/QUEUE.md`,
   mark it `claimed:<your-id> <date>`. One task = one branch = one PR.
2. **Never push to `main`.** Branch name: `agent/<harness>/<task-slug>`.
3. Keep PRs small and single-purpose (one county, one source, one ring
   pass). A PR that touches 400 rows across 6 topics will not be merged.
4. Run `python3 scripts/validate.py` before opening the PR. It must pass.
5. In the PR description state: task claimed, sources used, rows
   added/changed, how many at each verification tier, and any borderline
   calls you logged in `data/inclusion_log.csv`.

## 3. Creating a record — the dedupe check (in order, stop at first hit)

1. Search `organizations.csv` by **website domain** — same domain =
   presumptive same parent.
2. Search by **normalized name** (lowercase; strip Inc/LLC/Corp/Co/The
   and punctuation).
3. Search `sites.csv` by **street address** — one address = one site,
   owned by the *operator* (who runs the process), never the brand owner.
4. Search trade_names / notes for rebrands and acquisitions; follow
   `successor_org_id`.
5. No hit → create the record at tier **U** or **C**, and note in the PR
   which searches you ran.

When in doubt, **do not merge** — create/link and flag for review.
A false merge destroys data; a false split is cheap to fix.
Never delete a record: closed/acquired/merged entities are tombstoned
(`status` + `status_date` + source + `successor_org_id` where applicable).

## 4. Provenance — no naked facts

- Every record: ≥1 source, `verification_tier`, `last_verified` (the date
  a contributor actually checked it — not a scrape date alone).
- **NAICS codes are never company facts by default.** Companies almost
  never publish a corporate 6-digit NAICS. Every NAICS value must carry
  `naics_primary_source_type` (`company_disclosed` |
  `government_filing` | `directory_assigned` | `researcher_inferred`)
  and a confidence. A directory repeating a code is still
  `directory_assigned`.
- Multi-value fields use `;` as the separator, values from the controlled
  vocabularies in `docs/SCHEMA.md` only.
- County is required for every Ohio site, from the physical address —
  never inferred from the mailing city (ZIP codes straddle boundaries).

## 5. Licensed sources — the hard line

Plastics News, Rubber News, D&B, Data Axle, ZoomInfo, and similar paid
sources may be used **as discovery leads only** (where a contributor's
human principal holds a subscription). Do NOT copy their rankings,
datasets, descriptions, or bulk listings into this public repo.
Every fact that enters the repo must be verified against a primary or
public source (company website, SEC / Ohio SOS / SAM.gov filing,
government data, association directory, trade-press news reporting of a
specific event) and cited to *that* source.

### 5.1 PIC membership

**PIC membership.** Membership status is published in the Atlas only
where it is already public: a record may carry the public membership
flag only for a member **findable on the public PIC website member
list**, and the record's `sources` cite that public list. The PIC CRM
is a private, internal system: it may be used to reconcile the
website list against the Atlas internally, but it is never the cited
source for a membership fact, and no membership information that
exists only in the CRM is published. Where the website list and the
CRM disagree, the website governs what publishes and the discrepancy
is an internal reconciliation item, not a publishable fact.

## 6. Privacy

No personal data. No individual emails, direct-dial phones, or home
addresses — ever. Public business switchboard numbers and generic
contact pages only, and only where a schema field exists for them.
Ownership demographics (woman/minority/veteran-owned) only when
self-disclosed by a primary or authoritative source; never inferred.

**People records.** The Atlas may carry records for **professors** —
and only professors — where every field is an independently public
professional fact: name, institution, role, research specialty, and a
public lab or profile URL, each cited to its public source in the
record's `sources`. A professor is recorded only when those facts are
public; no record is created from, or corroborated by, any private
system. In particular, **the PIC CRM is never a source for people
records**: people held in the CRM are not recorded, exported, or
exposed in the Atlas, and CRM-only information about a person never
enters a record. Personal contact data (individual emails, direct-dial
phones, home addresses) remains barred for people records exactly as
for every other record class.

## 7. Counting honesty

Any count you state — in a PR, a README, a report — must name its unit
and filter: "Parents with an Ohio footprint", "Ohio establishments",
"Ring 1–2 establishments in PIC-12", etc. A bare "900 companies" is a
protocol violation.

## 8. Geography (frozen definitions)

- **PIC-12** (Evidence Room / cluster reporting): Ashtabula, Cuyahoga,
  Geauga, Lake, Lorain, Mahoning, Medina, Portage, Stark, Summit,
  Trumbull, Wayne.
- A wider 19-county GAC footprint has been proposed in schema drafts.
  Until the repo owner rules, tag records with the **county** and let
  reports apply either definition — do not hard-code a region into a
  record.

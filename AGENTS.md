# AGENTS.md — Binding protocol for ALL contributors (human and AI)

This repo is worked on by multiple AI harnesses (Muse, Claude Code,
Codex, Grok, Antigravity, others) and human researchers, in parallel.
These rules exist so parallel work merges instead of colliding. They are
not suggestions. If a rule blocks your task, stop and flag it in your PR —
do not work around it.

## Start here

Read this file first, then `docs/SCHEMA.md`, then `tasks/QUEUE.md` —
in that order, before touching anything. The merged `*_all.csv`
exports and the SQLite database are generated artifacts: never edit
them and never commit a hand-modified one. Never commit anything
produced in a local staging or workshop area; only changes under
`data/`, `docs/`, `scripts/`, and `tasks/` travel.

**Where things live** (owner ruling 2026-11-22; this is a pointer, not an
enforced rule, and no script checks it): `tasks/QUEUE.md` is the claim
ledger, the line you mark `claimed:` before you build. The board is the
tracker: commitments live in Kaneo, PIC workspace, project ATLAS (the repo's
declared tracker from 2026-11-22). Decisions live in `DECISIONS.md`.
Chat (the crosswalk `polymeratlas`) is for messages only: a decision or a
commitment that exists only in chat does not exist.

## 1. Where truth lives

- The CSVs in `data/` are canonical. Organizations and sites are
  stored as per-state shards (`data/organizations_<TAG>.csv`,
  `data/sites_<TAG>.csv`) under the placement function in SCHEMA.md
  Appendix C; every other table is a single file. SQLite and the
  merged `*_all.csv` exports are generated (`scripts/build_sqlite.py`);
  never edit or commit a hand-modified .db or a merged export.
- Schema, ring rules, NAICS map, and controlled vocabularies live in
  `docs/SCHEMA.md`. Vocabulary/ring changes require a dated schema
  revision in that file — never improvise a new tag, ring, or status
  value inline. Use the `*_other_note` / notes field and flag it.
- **Derived fields are hands-off.** `tier1_qualifier` is refreshed by
  the derivation procedure, in its canonical basis formats — never
  hand-edit it. Coordinates (`lat` / `lon`, `geocode_precision`) are
  reference data: never evidence, and never an input to a
  verification tier.

## 2. How work happens

1. **Claim before you build.** Pick (or add) a task in `tasks/QUEUE.md`,
   mark it `claimed:<your-id> <date>`. One task = one branch = one PR —
   except in campaign mode (rule 2, retired), where one task = one integration pass.
2. **Campaign mode — RETIRED 2026-11-03 (owner battery B-CAMP).** Since
   2026-11-02 the `validate` workflow runs on every PR and push, so the
   reason for direct pushes is gone. **No harness, the campaign
   orchestrator included, pushes to `main`.** Every change, campaign
   integration passes too, lands through a PR that passes `validate`;
   integration passes keep their pass journal and pre-pass backups. The
   historical rule is kept below for the record of passes 4–46.
   *(Historical, 2026-10-29 to 2026-11-03, owner ruling C2:)* The campaign
   orchestrator may push directly to `main` for a campaign integration
   pass when **all** of the following hold for that push:
   a. the repo owner has approved **that push** (per-push approval; a
      general go-ahead for a pass series is not approval of each push);
   b. `python3 scripts/validate.py` passes locally on the exact tree being
      pushed, before the push;
   c. after the push, the pushed files are read back from the remote and
      verified byte-identical to the validated local copies;
   d. the push is appended to the snapshot sync log
      (`polymer-atlas.muse-github-snapshot-sync.json`, maintained alongside
      the local repo) with its paths and, where the push route returns one,
      its commit SHA.
   Campaign mode exists because the GitHub App has no Workflows
   permission: `.github/workflows/validate.yml` is not on the remote, so a
   PR would run **no** automated validation, while a campaign push is
   gated by b–d. (The workflow landed on the remote 2026-11-02.) If Workflows permission is ever granted and the workflow
   lands on the remote, this rule is revisited by dated revision — it is
   not self-expiring and it is not self-extending.
3. **Never push to `main`.** Branch name:
   `agent/<harness>/<task-slug>`. This binds every harness and every
   contribution, without exception (rule 2 is retired).
4. Keep changes small and single-purpose (one county, one source, one ring
   pass). A PR that touches 400 rows across 6 topics will not be merged.
   A campaign integration pass is single-purpose **by pass**: its scope is
   fixed by its pass journal/manifest before application, and nothing
   outside that scope rides the push, however convenient.
5. Run `python3 scripts/validate.py` before opening the PR — and, in
   campaign mode, before the push. It must pass.
6. State your provenance. In the PR description state: task claimed,
   sources used, rows added/changed, how many at each verification tier,
   and any borderline calls you logged in `data/inclusion_log.csv`. A
   campaign push carries the same record in its pass journal and its
   snapshot-log entry instead of a PR description; a push without that
   record is a protocol violation even if the data validates.
7. **Swim lanes: lanes produce packets; one integrator writes.** Research
   and verification work runs as packet lanes: a lane produces verdict
   and evidence packets and **never edits files under `data/`**. Only a
   designated integrator of record applies packets to data files — one
   writer per file at a time (different files may be held
   concurrently), with pre-pass backups of every edited file and a pass
   journal. ID allocation, cross-shard moves, and dedupe decisions stay
   serialized through the integrator of record, in campaign mode too.
   Work by outside harnesses on wave-scale research arrives as packets
   on the branch, not as data edits; small single-purpose data PRs
   remain as rule 4 allows.
8. **Verdict grammar.** Lane verdicts are exactly: **VERIFIED**;
   **REJECT**, with the deciding fact; **STILL_UNCERTAIN**, with the
   named fact that would settle it; **DUPLICATE_OF**, whose chain must
   terminate at a held record. The effort cap is ~6 primary-source
   fetches per organization — when the budget is spent without a
   primary signal, the verdict is STILL_UNCERTAIN. A failed fetch
   (403, timeout, bot wall, empty result) is an availability signal
   about the route — never evidence of absence, closure, or
   non-existence. Before any REJECT for closure or no-establishment,
   run the Form 5500 check (bulk EFAST2): a sponsor filing blocks the
   reject only when the filing's address **is** the establishment in
   question. A TRI parent name never overrides the Atlas parent of
   record.
9. **Owner rulings are never self-ruled.** Scope, ring, and vocabulary
   questions are owner rulings: propose them as battery items with a
   recommendation and the evidence, and hold the work they gate. Do
   not settle them inside a task, a lane, or a PR.
10. **Derived frames and extracts.** Any sampling frame, extract,
    count, or other derived product built from build metadata (pass
    allocation files, journals, packet design files) must:
    a. whitelist the exact creation classes in that pass's own
       vocabulary — marker and annotation classes (e.g.
       `org_create_watch`, `org_edit_*`, `*_no_create`,
       `site_note_append`, `next_free_*`) and flips, repoints, and
       folds are never creations;
    b. assert record-ID uniqueness before the product is used or
       published;
    c. reconcile its per-pass (or per-source) counts against the
       published counts it claims to represent — and stop and
       investigate any conflicting count, including one reported by
       another harness, rather than explain the discrepancy away.
    (Origin: the F1 class-map v1 double-count of the five watch orgs,
    2026-10-30 — an `org_create_watch` marker row was counted as a
    second creation; the lane's own lower count was the correct one.)

*Revision note — 2026-10-30: §2 rule 10 added (derived-frame discipline),
after the F1 class-map correction. No other section is amended by this
revision.*

*Revision note — 2026-10-29 (owner ruling C2): §2 amended to formalize the
campaign mode under which integration passes 4–11, the schema v1.1+v1.2
implementation, the network-layer application, and the schema v1.3
micro-pass were pushed directly to `main` — 19 logged pushes, each with
per-push owner approval, local validation, and read-back verification.
The branch/PR rule is unchanged for outside harnesses and non-campaign
contributions. No other section is amended by this revision.*

## 2a. Working rules — owner adoption 2026-11-22

On 2026-11-21/22 one harness built, verified and merged about 34,000
evidence rows in a day; 28% did not bind to their record, and every check
was green. The owner adopted these seven rules on 2026-11-22 ("Adopt all
seven"), and rule 8 on 2026-11-23. A rule without a check gets one or is
not called a rule, so this section says for each rule what is checked and
what is only practice. **Rules 1, 4 and 7 are practice: nothing mechanical
checks them. Rule 8 is practice; the controller's own harness checks
part of its spawn side, outside the repo.** What
each check cannot catch is in `tasks/working-rules-2026-11-22/README.md`.

1. **The agent that builds a batch never merges it.** *Practice.* The
   controller arranges the reviews. Nothing checks who merges: every
   harness shares one GitHub account, so a merge by the builder looks the
   same as a merge by anyone.
2. **No evidence row or registry link merges without its packet and a
   replay check in the repo.** *Partly checked.* The binding gate
   (`scripts/check_evidence_binding.py`, run by the `binding-gate`
   check run of workflow `pr-rules`) judges evidence
   rows from structured sources (site rows have a street test; organization
   existence and HQ address have different checks). It checks that the
   batch's task folder exists with a `check.py` and executes nothing from
   the PR tree. Own-site web rows need a per-row proof in
   `tasks/<folder>/BINDING_PROOF.csv` and capture replay in the gate
   (owner ruling 2026-11-23, SCHEMA §4.13). The lane and reviewing family
   run packet replays. The binding gate does not replay a packet and does not sample rows.
   Registry links, people and program rows remain
   outside this admission path.
3. **A binding gate in CI: the quoted operator is a name the record holds
   and the quoted street equals the record's street, or the row is a
   lead.** *Checked by the same gate, for structured evidence rows:* PASS
   means that every binding check applicable to the row's record and claim
   matched positively and the quote contains no unexplained detail. Other
   rows are held for reading. PASS is a minimum condition for admission;
   source replay and independent review still apply.
   Own-site web rows must also clear the web mechanics, replay against
   the cited main text, and carry a reading with a self-reported family
   different from the builder’s.
4. **Review is tiered by risk, recorded on the PR.** *Practice.* (Owner
   ruling 2026-11-22, "tier by risk".) A PR that changes any file under
   `data/` gets review records from two model families at the current head;
   every other PR gets one, from a family other than the builder's.
   Exception (owner ruling 2026-11-24, "One family for mechanical"): a data
   PR that applies a written rule by script, with no reading or judgment,
   adds no evidence row, and passes a deterministic check that rejects
   planted defects needs one review record, from Codex (OpenAI). A data PR
   that rests on a read, a judgment or new evidence keeps two. The
   controller arranges the reviews and posts a `**Review record**` comment
   per verifier on the PR, naming the model, the verdict at the head SHA and
   what was checked. A non-data PR is capped at two review rounds; after
   that the open findings go to the owner. On a later round only the family
   that refused re-reviews, unless the fix adds a file or changes more than
   30 lines. Every finding is marked BLOCKING (a defect that reaches data or
   users, publishes personal data, lets a check pass on what it could not
   inspect, or lets CI be defeated) or FOLLOW-UP; follow-ups do not hold a
   merge and are listed in the PR and on the board; a verdict is REFUTE
   only when at least one finding is BLOCKING. **Nothing mechanical checks
   any of this, and the records are self-reported comments on a shared
   account.** The way to enforce it, if the owner later wants that, is
   separate GitHub accounts for builders and reviewers with GitHub-required
   reviews.
5. **A batch is audited before the next one builds on it, with a size cap
   per PR.** *Checked* by `scripts/check_pr_rules.py` (check run
   `pr-rules`). A PR may add at most 1,000 evidence rows and 1,000 registry
   links unless it adds a line to `DECISIONS.md` that contains the words
   "size waiver" and `branch=<its complete branch name>` (compared for
   equality with the PR's branch). A PR that touches `data/` fails while any
   `created_by` label on `main` lacks an audit record: a file
   `tasks/<folder>/AUDIT.md` on `main` or added by the PR itself, with the
   lines `Label:`, `Result: PASS`, `Sample:` and `Reviewers:` (a
   `Result: FAIL` blocks).
   The labels on `main` on 2026-11-22 are grandfathered in
   `tasks/working-rules-2026-11-22/audit_baseline.txt`. **Deployment
   condition:** the audit stays current for a PR only once the controller
   has made `pr-rules` a required check and turned on the ruleset's strict
   (branch up to date with `main`) policy; until then two data PRs can both
   pass against the same `main`.

   **Standing freeze (owner policy 2026-11-22; no mechanical check).**
   National evidence backfill outside PIC-18 is frozen until the PIC-18
   unknown shares move. Exempt: repairs, re-admission of reverted rows that
   answer a PIC-18 question, and the whole-Atlas audit. The next data work is
   a PIC-18 size sprint from files already pulled and a 25-organization
   live-site trial for process and markets, each as a packet through the
   binding gate.
6. **Raw inputs live in the shared store by checksum.** *Checked, format
   only,* by `scripts/check_pr_rules.py`: a PR adding evidence rows or
   registry links adds `tasks/<folder>/INPUTS.sha256` (lines of
   `<sha256>  <path>`; the path is a file below `raw/` or `provenance/`, or
   an existing repo file). The hashes themselves are checked by a reviewer
   against the store; the check says so in its output.
7. **Decisions in `DECISIONS.md`, commitments on the board, chat for
   messages only.** *Practice.* Stated under "Start here"; no script can
   tell a decision from a message.
8. **A fan-out is priced and piloted before it scales; an audit is lean.**
   *Practice: CI checks none of it.* The controller's own harness checks
   only these parts of the spawn side. It refuses a spawn command it
   inspects directly when the brief has no `Budget:` line, tag or not; for
   an owner-tagged fan-out script, the controller checks each child brief
   by hand. Unless the owner's fan-out tag is on the command, it
   also refuses a spawn run from a script file or a loop, and one made
   while 8 or more of the controller's children are live. When the
   children's spend over two hours passes the line, the harness turns the
   outcome line RED. A RED line refuses spawns that are not marked critical
   path or owner-approved, and the controller sets the critical-path mark
   itself. Pricing, the pilot, the audit design and stopping idle threads
   are controller practice; the harness cannot see spawns by other
   harnesses. (Owner ruling 2026-11-23, after audit 12 spent ~450M input
   tokens across 20 threads to confirm a FAIL its pilot had already shown.)
   a. An owner question that authorizes 3+ parallel threads, or an audit,
      states projected token spend per provider and the cheaper
      alternative.
   b. A pilot of a few units runs first. Before scale-up its rate is
      compared with the pre-registered stop line and its tokens per unit
      are written down; if the pilot already decides the question, the
      work stops there.
   c. An audit is lean: a smoke sample disjoint from the draw decides
      whether to draw; sources are fetched once and quotes replayed by
      script; each record gets one reader from a family that did not build
      it, with plants; a second family reads only flagged records plus a
      random check share; a stratum stops as soon as it crosses its fail
      line. Sizes and false-pass risk for this design are recomputed in the
      protocol, never assumed.
   d. Spend is measured while work runs, from provider usage logs; a
      thread that spends without producing output is stopped.

The `pr-rules` and `binding-gate` checks are evaluated by the checker and
workflow on `main`, never by the PR's own copy (`pull_request_target`): a PR
that changes `scripts/check_pr_rules.py` or `.github/workflows/pr-rules.yml`
is judged by the version already on `main`. Neither reads a PR comment or a
review record. A change to these rules or to their checks is an owner ruling
(section 2 rule 9).

*Revision note — 2026-11-22 (owner adoption, working rules): §2a added with
the seven working rules; "Start here" gains the where-things-live paragraph
and states that `tasks/QUEUE.md` is the claim ledger and the board is the
tracker. Rules 1, 4 and 7 are practice, with no mechanical check; rule 4 is
tiered by risk (two families for a PR touching `data/`, one for any other);
rules 5 and 6 are checked by `pr-rules`; rules 2 and 3 are partly checked by
the structured-row gate. The freeze joins rule 5 as owner policy. No data
file is changed by this revision.*

*Revision note — 2026-11-23 (owner ruling, round 15): §2a rule 5 allows
the prior batch's audit record to be added by the next data PR.*

*Revision note — 2026-11-23 (owner ruling, "make this a durable rule
change"): §2a gains rule 8 (fan-outs priced and piloted, audits lean, spend
measured while work runs). It is practice in this repo. The controller's
harness refuses a directly inspected spawn whose brief has no budget line, and, without the
owner's tag, spawns from a script or loop and spawns at its live-thread cap.
It turns its outcome line RED above a spend line. Recorded in `DECISIONS.md`.
No data file is changed by this revision.*

*Revision note — 2026-11-24 (owner ruling, "One family for mechanical"):
§2a rule 4 lets a mechanical data PR (a written rule applied by script, no
reading or judgment, no new evidence row, a deterministic check with planted
defects) merge on one review record, from Codex. Recorded in `DECISIONS.md` with the
same day's rulings "Publish only what's stated" and "PIC-18 only". No data
file is changed by this revision.*

## 3. Creating a record — the dedupe check (in order, stop at first hit)

1. Search the organization shards (`organizations_*.csv`, all of
   them) by **website domain** — same domain =
   presumptive same parent.
2. Search by **normalized name** (lowercase; strip Inc/LLC/Corp/Co/The
   and punctuation).
3. Search the site shards (`sites_*.csv`, all of them) by **street
   address** — one address = one site,
   owned by the *operator* (who runs the process), never the brand owner.
4. Search trade_names / notes for rebrands and acquisitions; follow
   `successor_org_id`.
5. Search the site shards by **site name**, normalized like an
   organization name with a trailing locality removed ("IFS Coatings -
   Ardmore" → "IFS Coatings"): `python3 scripts/atlas.py dedupe-check`
   runs this as its step 5. A site name that matches another
   organization's site or name is a lead to settle, not a merge.
6. No hit → create the record at tier **U** or **C**, and note in the PR
   which searches you ran.

**IDs — allocate from the maximum, never fill a gap.** Before creating
records, scan **all** shards of the target table and allocate above the
tree-wide maximum ID in that table. Row counts are not the maximum:
gaps exist and are permanent. Never reuse an ID — including a
tombstoned one — and never fill a gap.

When in doubt, **do not merge** — create/link and flag for review.
A false merge destroys data; a false split is cheap to fix.
Never delete a record: closed/acquired/merged entities are tombstoned
(`status` + `status_date` + source + `successor_org_id` where applicable).

**Status changes need dated evidence.** An operating-status change
requires dated primary or near-primary evidence: a company statement,
a WARN notice (an announcement) **plus** a dated outcome record, a
regulatory action, or dated trade-press reporting. A WARN notice
alone settles nothing. A final Form 5500 filing is a plan fact, never
a status change. An organization flagged `monitor_watch` is
re-verified when the watch fires — a hit queues re-verification and
never auto-changes a status.

A record’s shard is a function of its HQ (organizations) or physical
state (sites) — see SCHEMA.md Appendix C. Correcting that fact moves
the record in the same pass; never leave a record in a shard its fields
contradict. Site shards exist for US states, plus any the schema later
adds by dated revision: an establishment outside that set has **no
lawful shard** — hold it and flag it for an owner/schema ruling; never
force-place it into a US shard or the residual.

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
- Date fields carry a full ISO date or are empty. A year-only value
  is invalid. The single exception is `members.member_since`, which
  is a year field by design (owner ruling 2026-11-01, SCHEMA v1.7.6).
- **Evidence contract.** A create integrates only with evidence rows
  in the `data/evidence_*.csv` shards covering its existence and scope claims at
  minimum, per SCHEMA.md §4.13, which also sets the per-source-class
  tier ceilings. A platform or roster category is a discovery lead:
  it can never support a scope claim.
- **Relationships are generated, not authored.** `parent_of`,
  `successor_of`, and `merged_into` edges in `data/relationships.csv`
  are generated from the organization columns and parity-checked
  (validator V-27) — never hand-author them. The only authored
  exceptions are those created by a dated owner ruling recorded in
  SCHEMA.md §4.14. `member_of` edges **are** authored — for
  association membership only, sourced to a public directory
  snapshot. PIC membership is never carried by `member_of`; §5.1
  governs it.
- **Registry identifiers must be verified at the source.** A registry
  ID (TRI TRIFID, FRS, or similar) may be recorded as a link only
  after it is verified against the source system's own extract or
  record. An identifier that appears only in this project's own
  files is a phantom and mints nothing.

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
source for a membership fact — nor for any other fact in any public
row, and no public row names CRM content (owner ruling 2026-11-01;
validator V-50) — and no membership information that
exists only in the CRM is published. Where the website list and the
CRM disagree, the website governs what publishes and the discrepancy
is an internal reconciliation item, not a publishable fact.

## 6. Privacy

No personal data. No individual emails, direct-dial phones, or home
addresses — ever. In record fields: public business switchboard numbers and generic
contact pages only, and only where a schema field exists for them.
Evidence quotes are the one exception, and it is narrow (owner ruling
2026-11-22): where a verbatim quote that witnesses another claim
incidentally shows a company's public switchboard phone or fax number
or a role address (info@, sales@), the quote may keep it. A quote is
never a place to record contact data, and every narrower bar stands:
exhibitor contact blocks are never transcribed (SCHEMA §4.12), an
ecosystem office carries its generic contact page and never an office
phone number (§4.6), and equipment records carry no contact data
(§4.19).
A quote never carries an individual's email, a direct line, an
extension, a mobile number, or a home address — cut the quote before
it.
Ownership demographics (woman/minority/veteran-owned) only when
self-disclosed by a primary or authoritative source; never inferred.

**People records.** The Atlas may carry records for **professors** —
and, under the owner ruling of 2026-10-31, **research staff at
federal laboratories with real polymer programs** — where every field
is an independently public professional fact: name, institution,
role, research specialty, and a public lab or profile URL, each cited
to its public source in the record's `sources`. A professor is
recorded only when those facts are public; no record is created from,
or corroborated by, any private system. A lab research-staff record
stands on the same discipline at lab grain: the laboratory's own
public staff or program pages must style the person as research staff
with polymer research stated, the recorded affiliation is the
laboratory, and a joint university appointment is recorded and
verified at the primary home institution. In particular, **the PIC
CRM is never a source for people
records**: people held in the CRM are not recorded, exported, or
exposed in the Atlas, and CRM-only information about a person never
enters a record. Personal contact data (individual emails, direct-dial
phones, home addresses) remains barred for people records exactly as
for every other record class.

**Event participation.** Rows in `data/event_participation.csv` name
organizations only. A speaker is recorded as their employer
organization, never as an individual.

## 7. Counting honesty

Any count you state — in a PR, a README, a report — must name its unit
and filter: "Parents with an Ohio footprint", "Ohio establishments",
"Ring 1–2 establishments in PIC-12", etc. A bare "900 companies" is a
protocol violation.

## 8. Geography (frozen definitions)

- **PIC-18** is the cluster reporting region (Evidence Room / cluster reporting), by **owner ruling 2026-11-03**. It is the
  NEO-SMART 18-county Northeast Ohio region, the union of the two JobsOhio network regions that cover it:
  - **Team NEO (14):** Ashland, Cuyahoga, Erie, Geauga, Huron, Lake, Lorain, Medina, Portage, Richland, Stark, Summit,
    Tuscarawas, Wayne;
  - **Lake to River (4):** Ashtabula, Columbiana, Mahoning, Trumbull.

  Sources: jobsohio.com/ohio-regional-network and the NEO-SMART map, both read 2026-11-03. The machine-readable form is
  `scripts/regions.py`, and every script reads its region from there.
- **PIC-12** (Ashtabula, Cuyahoga, Geauga, Lake, Lorain, Mahoning, Medina, Portage, Stark, Summit, Trumbull, Wayne) is the
  earlier definition. Reports dated before 2026-11-03 used it and stay as written; it is not used for new reporting.
- The 19-county GAC footprint once proposed in schema drafts is superseded by PIC-18.
- **Unchanged:** tag records with the **county**, never a region. Reports apply the region; a region change touches no data row.

*Revision note — 2026-10-30 (swim-lanes amendment): the Start-here
block is added (amendment item 11); §1 gains the derived-fields
rule; §2 gains rules 7–9 (packet lanes and the single integrator of
record, the verdict grammar with its effort cap and Form 5500 gate,
and the bar on self-ruled scope questions); §3 gains the ID-allocation
rule, the status-change evidence standard, and the foreign-site hold;
§4 gains the ISO-date rule, the evidence contract, the relationships
parity rule, and the registry phantom rule; §6 gains the
event-participation grain. The owner confirmed the same day that
§2 rule 3 stands for all non-orchestrator harnesses: branch/PR only,
with no campaign-mode grant. No data file is changed by this
revision.*

*Revision note — 2026-10-31 (people-scope extension): §6's
people-records passage is extended under the owner's ruling of the
same day — research staff at federal laboratories with real polymer
programs are recordable alongside professors, under the same
public-facts discipline (SCHEMA v1.7.3, §4.9). No data file is
changed by this revision.*

*Revision note — 2026-11-03 (owner battery 2026-11-03, item B-CAMP):
§2 rule 2's campaign mode is retired now that `validate` runs on every
PR and push; rule 3 binds every harness. Recorded in
`tasks/OWNER_BATTERY_2026-11-03.md`. No data file is changed by this
revision.*

*Revision note — 2026-11-01 (owner battery 2026-11-01, SCHEMA v1.7.6):
§4's date rule gains the `members.member_since` year-field exception,
and §5.1 extends the CRM bar to every fact in every public row
(validator V-50). The owner ruled the battery "all as recommended".
No data file is changed by this revision.*

*Revision note — 2026-11-03 (owner ruling, PIC-18): §8 replaces PIC-12 with PIC-18 for cluster reporting. PIC-18 is the
NEO-SMART 18-county region, which equals the JobsOhio Team NEO (14) and Lake to River (4) regions together. PIC-12 is kept
as the historical definition for earlier reports, and the 19-county GAC proposal is superseded. No data file is changed by
this revision.*

*Revision note — 2026-11-06 (owner instruction in session): §3 gains
step 5, a site-name search, after the 2026-11-06 IFS Coatings case
(PR #243), where a site named for its operator sat under another
organization because no step searched site names. The tool support
landed in PR #244. No data file is changed by this revision.*

*Revision note — 2026-11-22 (owner ruling in session): §6 gains the
evidence-quote exception and scopes the existing sentence to record
fields. A company switchboard number or role address that a verbatim
evidence quote incidentally shows may stay; an individual's contact
detail may not, and the narrower bars of SCHEMA §4.6, §4.12 and §4.19
stand. Recorded in `DECISIONS.md`. No data file is changed by this
revision.*

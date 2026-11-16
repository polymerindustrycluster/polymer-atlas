# Decisions ledger

Append-only record of why the Atlas is the way it is (portfolio rule 5). Newest last. Each entry names its date, the
decision, who made it, and where the detail lives. Scope, ring and vocabulary rulings stay in the owner-battery files
and dated SCHEMA revisions; this ledger records release and operating decisions and points to those rulings.

## 2026-11-14: first public release, first user, and non-use review

- **Decision:** cut the first dated release of the Atlas (`v2026.11.14`) from main at the main commit that merges this ledger (data identical to `accc03b`), built with
  `scripts/export_release.py` (see the release notes on GitHub).
- **First user (portfolio rule 8):** John Swanson, using the Atlas for PIC work.
- **Non-use review date:** 2026-12-14 (30 days after the release). On that date, check whether the release has been
  used for PIC work, and record the result here; non-use is a finding, and "parked" is a legitimate outcome.
- **Decided by:** the repo owner, in session, 2026-11-14.
- **Quality basis:** blind audit 10 (`docs/reviews/BLIND_AUDIT_10_2026-11-14.md`): 45 of 50 sampled changed records
  agreed, 2 field errors (both corrected in #332), 0 creation errors, 3 unresolved; design-weighted confirmed-error
  rate 4.6% (Wilson 95% about 1.3% to 15.5%).

## 2026-11-14: `validate` is a required check on main

- **Decision:** a repository ruleset ("main: require validate") requires the `validate` workflow to pass before any
  merge into main; repository admins may bypass in an emergency.
- **Why:** after #271 (SCHEMA v1.13) left `docs/schema/vocab.json` stale, 37 consecutive pushes merged on a red check,
  and the unit-test, SQLite-build and artifact steps never ran (fixed in #329).
- **Decided by:** the repo owner, in session, 2026-11-14.

## 2026-11-16: the public site becomes a working tool (PIC-18 prospects, CSV, evidence on organization pages)

- **Decision:** the site gains a PIC-18 prospects page (one row per organization row with at least one site row in a
  PIC-18 county, operating status active, tier A-C), a "Download these rows (CSV)" button on table pages, a
  `prospects.csv` built with the site, a latest-release link on every page, an "active, tier A-C" column on the county
  index that sums to the PIC-18 headline, county tables by process and employee band, and the evidence rows on
  organization pages in place of source strings. Graph, map + network and street map open on PIC-18.
- **Why:** the site audit of 2026-11-16 (first user: John Swanson, non-use review 2026-12-14) answered 2 of 12 real
  tasks, mostly because nothing could be filtered or taken away. Detail and the 12-task tally are in the PR.
- **Rules fixed here:** (1) an unknown value (blank or the literal "unknown") is shown as unknown and counted per
  filter, never read as zero or small; (2) employee band is the PIC-18 site band, else the organization's Ohio band,
  and each row says which; process, material and market follow the same rule; (3) public membership is shown only as
  "on the public member list" or "not on the public member list" (AGENTS.md section 5.1), and the page says the second is
  not "not a member"; (4) evidence rows are shown without lane ids or notes, a row whose source cites a contact or a
  pipeline reference is withheld, and a claim text that does is shown as "detail not shown"; (5) every page number is
  recomputed from `data/` in `scripts/test_build_site.py`.
- **Not decided here:** whether to publish a non-member list or keep a private membership overlay (audit finding 3) stays an
  owner ruling.
- **Decided by:** built to the controller's task from the audit; no owner ruling is claimed or needed for the wording
  above, which restates AGENTS.md section 5.1.

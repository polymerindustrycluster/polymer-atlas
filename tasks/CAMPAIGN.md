# Atlas campaign plan (from 2026-11-04)

This is the shared plan for every harness working the Atlas: Claude Code, Grok, Codex, Muse and others. It sits
beside `QUEUE.md`. The queue lists tasks; this file says what the tasks are for, who works where, and the rules that
keep parallel waves from colliding. AGENTS.md still binds everything. This file adds no new rule; it records
conventions already applied in merged PRs.

**Status: targets proposed by claude-code, awaiting the repo owner's confirmation.** Until he confirms them, they guide
the order of work only.

## Goal
An evidence-backed database of US polymer entities that supports PIC's members and goals.

## Targets (proposed)

| # | Target | Measured by | By |
|-|-|-|-|
| T1 | 90% of PIC-18 Ring 1–2 organizations are free of blocking gaps: not tier C or U, no probable duplicate, a website on record, and processes or materials on record | the integrator's record-health view, organization grain | 2026-12-15 |
| T2 | Every lead-fusion STRONG cluster in the ten largest QCEW-gap states has a lane verdict | the verdict files, against `tasks/lead-fusion-2026-11-01/clusters.csv` | 2026-12-31 |
| T3 | The NAICS 326 strict-site share of QCEW rises in each state worked | `scripts/build_qcew_denominators.py`, unit: establishments | rerun after each state merges |
| T4 | Every upcoming edition in the conferences repo passes the R6 age gate | `python scripts/validate.py` in `polymerindustrycluster/conferences` | rolling |

## Who works where (claims, to avoid two harnesses on one state)

**State waves from the lead-fusion spine.**
- **Grok** takes the states with thin Atlas coverage, working from the two-source queue. Its PRs from #41 onward cover
  UT, DE, ID, NH, RI, NV, ME, MT, VT, ND, NM, SD, NE, MS, WV, OK, AZ, MD, CO, AR, WA, OR, CT, KS, IA and AL.
- **Claude Code** takes the large-gap states, STRONG clusters first:
  - IN: the pilot, #75;
  - MI and IL: in progress;
  - CA, TX, FL, GA, WI and MA: next.
- **Claiming:** a harness claims a state in `QUEUE.md` before starting it. A state that is already claimed is never
  started by a second harness.
- OH and PA are well covered and not part of the wave.

**Record quality.** Claude Code runs:
- the record-health fixes, members and large PIC-18 organizations first;
- the evidence repair passes (`tasks/evidence-audit-2026-11-03/`, `tasks/evidence-repair-2026-11-03/`);
- the capability passes.

**Events.** The dated calendar lives in the `polymerindustrycluster/conferences` repo. The Atlas keeps the series
(`events.csv`) and the organization-grain exhibitor and sponsor rows (`event_participation.csv`).

## ID allocation when several PRs are open
- Before minting, scan **every open PR's diff** (`git fetch origin "+refs/pull/*/head:refs/remotes/pr/*"`) for the
  highest ORG, SITE, EVD, EVP and PERSON ids it adds. Allocate above the maximum of main and all open PRs, with
  headroom.
- Gaps are permanent and allowed. Reuse is never allowed (AGENTS §3).
- When two open PRs collide anyway, the integrator rebases the later one, as was done for #48 and #49.

## Conventions already applied in merged PRs
- **Creates from federal sources (the UT pilot, #41, and the IN pilot, #75):**
  - a site with a federal record plus an own-site witness whose quote was re-fetched raw and found verbatim is
    **tier B**;
  - a site on federal sources only is **tier C**;
  - a new organization is **tier C**.

  ECHO/FRS ids go in `notes` unless a fresh dated fetch is cited, because of the §4.13 grep rule.
- **Every lane quote is re-checked raw.** WebFetch returns a model's summary, so the integrator re-fetches each cited
  page and keeps a row only if the quote's words appear in order. For a rank or name quote taken from a roster page,
  the record's surname or name must also appear near the quote.
- **Evidence is append-only:** a weak row is answered by a fresher row, never edited.
- **Duplicates are linked and flagged, not merged**, unless the integrator has dated proof that they are the same legal
  entity.
- **Findings are held, not applied.** Moves, closures and HQ corrections need dated evidence and their own pass.
- **Private sources never cross into this repo.** The PIC CRM, the faculty census and the vault are discovery leads
  at most. Prospect and outreach lists are internal and never committed.

## Order of work
1. Merge-ready PRs first: every open wave raises the ID floor for the next.
2. Record quality on members and large PIC-18 organizations (T1).
3. State waves for the large-gap states, STRONG then CORROBORATED (T2, T3).
4. Events: series rows for shows with rosters, then exhibitor links (organizations only).
5. Evidence repair rounds, ordered by the audit's weakest claim types (existence, address, parent).

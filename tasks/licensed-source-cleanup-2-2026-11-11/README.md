# Licensed-source cleanup, finish pass (2026-11-11)

Owner instruction in session, 2026-11-11: "Just run the 24-row finish now." This pass answers the 24 evidence
rows that `tasks/licensed-source-cleanup-2026-11-09/` (PR #258) left held — each cites Plastics News or Rubber
News, which AGENTS.md §5 allows as discovery leads only — and adjudicates the four findings its lanes surfaced
but did not apply. Evidence is append-only (SCHEMA §4.13): the old rows stay; each is answered by a new row
citing a public source. No record row changes in this PR.

## Method

Same discipline as the first pass, one change of personnel: no packet lanes. The integrator of record
re-fetched every candidate page first-hand on 2026-11-11 and took each quote verbatim from the fetched text
(a word sequence, punctuation-insensitive, at most 25 words). `answers.csv` is the packet; `build.py` mints a
row only for FOUND / PARTIAL / CONTRADICTED with a non-licensed source, claims only what the quote states, and
caps the tier effect at the weaker of the old row's effect and the source class's ceiling. Most first-pass
holds were quote defects, not missing facts — the quote did not name the record's entity, or stated a
neighboring fact (a distributor listing is not ownership; "joined forces" is not an acquisition) — so most
cures are a better page or a tighter quote from a page the first pass already had.

## Outcomes (unit: licensed-source evidence rows held by PR #258; 24)

| Result | Rows |
|-|-:|
| Answered by a public source stating part of the claim | 20 |
| Contradicted by a public source | 3 |
| Still held | 1 |

23 new evidence rows, EVD-333031..EVD-333053, all at `supports_B` (every old row's effect was `supports_B`, so
the cap bound everywhere), plus three at `contradicts`. Per-row verdicts, sources and quotes: `answers.csv`
and `journal.txt`.

The one still-held row: **EVD-004782** (Matsui America, parent). The parent company's global-network page
gives the Hanover Park operation's functions and address, but the entity name does not appear in the page's
fetchable text, and no other public page states the Matsui Mfg. Co., Ltd. parent link in fetchable text. Held
rather than answered from an unverifiable quote; the settling fact is a public page (the parent's subsidiary
list, or Matsui America's own about page) that names both companies in fetchable text.

## The four surfaced findings, adjudicated

- **Dakota Molding → Nott (date):** already corrected of record. PR #258's answering row EVD-333024 cites
  Nott's own release, and its notes carry the source date 2023-05-05, which supersedes the old row's
  "Aug 2023". No further row minted.
- **Mauer USA (year):** correction **not applied**. The Kentucky Cabinet for Economic Development report's
  "Established: 2008" is a company-establishment field; EVD-005085 claims the Hebron plant *opened* in 2007.
  The contemporaneous public record — the June 2007 PlasticsToday brief reporting the plant announcement and
  the January 2007 KEDFA incentive approval — is consistent with a 2007 opening, and no public source states
  the plant opened in 2008. Establishment and plant opening are different facts; the old claim stands.
- **Gregstrom (relocation):** confirmed on the company's own site (post dated 2025-07-30): the thermoforming
  business merged into C&K Plastics in 2024 and the remaining rotomolding business moved from Woburn, MA to
  Bedford, NH. The record correction (HQ and site) is a separate single-purpose PR.
- **OMG Thermoforming (Arlington):** confirmed and answered here at the evidence layer: OMG srl's own
  "Agenti e Distributori" page assigns 3407 Avenue D, Arlington TX to its US agent/distributor network
  (omgusa.net), so all three Arlington rows are answered `contradicts` (EVD-333050..EVD-333052). The record
  correction (ORG-003807 / SITE-004251 framing) is a separate single-purpose PR.

## Borderline calls

- **Talco (EVD-006293):** the quote spans the site's two address blocks (Corona post-industrial, Long Beach
  post-consumer); the fetcher interleaved an image marker between them. The words are the page's own, in
  order; accepted and flagged here.
- **Republic Bag (EVD-005038):** the quote is one entry of Sigma Plastics Group's own locations list
  ("Republic Bag Inc CA Corona, CA"); the Houston entry sits in the same list and is named in the row's notes.
- **Matsui America scope (EVD-004781):** answered from the company's own NPE2024 exhibitor profile, hosted on
  the show's site; classed `press` (a third-party surface), not `own_site`.
- **OMG contradicts rows:** the quoted words are a listing entry; their force comes from the page they sit
  on — the parent's own agents-and-distributors page — which each row's notes state.
- **Century Pipe (EVD-004058):** the first pass's Tri-Cities Business News page was unreachable on
  2026-11-11 (the text fetcher is blocked on that domain; the live site returned 500). A failed fetch is an
  availability signal, not evidence; the company's own contact page answered the row instead. That page's
  "Currently Under Construction" line is stale (the plant opened in July 2026 per local reporting) and is
  flagged in the row's notes.
- **SK Chemicals America (EVD-005290):** PolySource's release styles the party "SK Chemical Americas"; the
  answer is quote-bounded to the copolyester distribution it states.

Checks: rehearsed as a dry run first (`journal.txt`). `python scripts/validate.py` exits 0.
`scripts/check_row_loss.py` against the merge base passes (no keyed row is removed; evidence is append-only).
The V-60 baseline in `scripts/validate_debt_baseline.json` is untouched: the 36 grandfathered rows still cite
their publications (append-only), and the baseline shrinks only when a row itself is fixed.

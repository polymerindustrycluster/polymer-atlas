# Federal frame — two-source create queue (built 2026-11-04)

A deterministic join of the three Nov-1 federal spine packets already in
this repo (`tasks/echo-frs-spine-2026-11-01`, `tasks/osha-ita-2026-11-01`,
`tasks/osha-spine-2026-11-01`), re-deduped against the Atlas tree as of
2026-11-04 (main `4284e6fd`, SCHEMA v1.9). No network calls, no LLM —
`build_frame.py` in this folder reproduces it end to end.

## What the build did

1. Took every spine record whose Nov-1 match verdict was `NO_MATCH`
   (ECHO/FRS 13,255 · OSHA ITA 9,145 · OSHA inspections 5,256).
2. Re-ran the dedupe against today's sites: **527 dropped** (added to the
   Atlas since Nov 1), **1 hit only a closed site** (see
   `closed_site_hits.csv` — treat as a liveness lead, not a create).
3. Joined the remaining 27,128 records across sources on normalized
   name + street address / ZIP into **21,448 establishment groups**.

## The queue

`QUEUE_MULTISOURCE.csv` — **3,179 groups attested by ≥2 independent
federal sources**, Ohio and Pennsylvania excluded (mature coverage):

| Class | Meaning | Groups |
|---|---|---|
| A_TRIPLE | ECHO + ITA + inspections | 643 |
| B_ECHO_ITA | EPA FRS ∩ OSHA 300A filings | 1,225 |
| B_ECHO_INSP | EPA FRS ∩ OSHA inspections | 646 |
| B_ITA_INSP | OSHA 300A ∩ OSHA inspections | 665 |

Rows carry the FRS registry ID, ITA establishment ID, and inspection key
for the underlying records, plus NAICS, employee count where a source
reports one, and the freshest activity date any source shows. Sorted by
class strength, then thinnest-state-first.

**How to work it:** the two-source attestation replaces one research leg,
not the verdict. A create still needs the company-website witness for
scope and liveness (AGENTS.md verdict grammar), caps at tier B, and ships
with its evidence rows in the same PR. Anything that fails the witness
stays a STILL_UNCERTAIN residue entry with its settling fact.

## What is NOT in this packet

16,798 single-source groups (ECHO 9,078 · ITA 5,349 · inspections 2,371)
— residue by design; they verify only with a company-site witness and are
not a burn-down list. The full joined file (19,977 groups incl. singles)
is staged locally with the Atlas staging archive (`federal-frame-2026-11-04/
QUEUE.csv`) and can be published if a state wave earns it. Per-state counts
for every class are in `SUMMARY.md`.

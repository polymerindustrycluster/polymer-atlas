# Binding-gate route for SBA PPP size_band rows

Built by: Claude Sonnet 5.5 (Claude Code), thread thr_rqdexkkube

Owner ruling 2026-11-26 07:36, "Gate PR for PPP first" (the controller's option A). This is a non-data PR: no evidence row and no data row changes.

## Why

The PPP re-run (owner rulings 2026-11-26 07:20, "PPP now, street route next" and "Same ten-year rule") was stopped because `scripts/check_evidence_binding.py` could not PASS any PPP row. At base `e4fd6585`: the 248 rows of 2026-11-16 give `UNINSPECTABLE no_quote`; a PPP-shaped row with a quote and an `SBA PPP ` source gives `UNINSPECTABLE unknown_source_family`; an http source gives `READ_REQUIRED web_class_untested`, which a `BINDING_PROOF.csv` cannot rescue (proofs cover own-site, press and SEC EDGAR rows). The gate is judged from `main`, so the route has to merge before the data PR.

## What changes

| File | Change |
|---|---|
| `scripts/check_evidence_binding.py` | One `FAMILIES` entry, `SBA PPP ` (operator `borrower_name`, address `address`), and `judge_ppp`, called from `judge()` for a source_ref that starts `SBA PPP `. |
| `scripts/test_check_evidence_binding.py` | `SbaPppRoute`, 16 cases. |
| `docs/SCHEMA.md` | v1.21.1: §4.13 row format; §1 R13 ten-year limit extended to source 4 (the age line is folded in here, so the data PR changes no SCHEMA text). |
| `DECISIONS.md` | Entry for this route. |

Row format: `source_ref` `SBA PPP LoanNumber <n> (<file>, release <date>)`; `claim_detail` `<band field>=<band>; historical <year> borrower-reported employment figure, JobsReported=<n>, band only; quote: borrower_name: X; business_type: T; address: STREET, CITY, ST ZIP`.

`judge_ppp` rules: source class `government_filing`; `source_ref` a full match of the form above with a valid date; claim `size_band` (every other use of PPP data stays a lead); the quote has exactly the three fields; `business_type` one of the five whitelisted types (Corporation, Subchapter S Corporation, Limited Liability Company(LLC), Partnership, Limited Liability Partnership). A site row then meets the shared street and designator legs, with PPP-specific name, city and ZIP legs: the borrower key must be one of the operator's own names (legal, trade, former; never a site label, and no corporate-words extension), the quoted city must be stated and equal the record's (a quote with no city is HELD), and the quoted ZIP5 must equal the record's where the record holds one (a quote with no ZIP is HELD). An organization row is judged on its one active site, and is HELD unless the organization has exactly one active site and every held site is in Ohio.

Round 1 review (Codex, REFUTE at d5d2d80) found four false passes, each observed through `judge` and each now a planted test: a source_ref of `SBA PPP garbage`; city and ZIP accepted as alternatives (Akron OH 99999 and Canton OH 44305 against Akron 44305); a borrower equal to a site label; and `source_class` other than `government_filing`. A DECISIONS wording follow-up is also done.

Round 2 (Codex, REFUTE at 80af661) found one more: a quote with the city omitted (`OH 44305`) passed on the matching ZIP alone, because the city comparison ran only when the quote supplied a city. It is now HELD `ppp_quote_city_missing`, planted on both grains, with a mutation (the gate before this fix passes the row).

**Departure from the controller's format, flagged:** the quote carries `business_type` as a third field. The controller's brief asked for "an individual borrower type if the row carries one"; the proposed quote had no such field, so the privacy line (no sole proprietor, self-employed or individual borrower) could not be inspected. A gate has to fail on what it cannot inspect, so a quote without it is HELD (`ppp_quote_fields`).

## Check

`python3 tasks/gate-sba-ppp-2026-11-26/check.py` plants each defect on an organization row and a site row and prints the gate's verdict:

| Planted defect | Verdict |
|---|---|
| wrong borrower name | FAIL `name_not_held` |
| wrong street | FAIL `street_differs` |
| wrong city and ZIP | FAIL `city_differs` |
| right ZIP, wrong city | FAIL `ppp_city_differs` |
| right city, wrong ZIP | FAIL `ppp_zip_differs` |
| city omitted, ZIP matches | HELD `ppp_quote_city_missing` |
| garbage, truncated or impossible-date source_ref | UNINSPECTABLE `ppp_source_ref` |
| source class other than `government_filing` | UNINSPECTABLE `ppp_source_class` |
| borrower equal only to a site label, or the operator name plus extra words | FAIL `name_not_held` |
| missing quote | UNINSPECTABLE `no_quote` |
| sole proprietor / self-employed borrower type | FAIL `ppp_individual_borrower_type` |
| business type not stated | UNINSPECTABLE `ppp_quote_fields` |
| suite on one side only (borrower or record) | HELD `designator_not_on_both_sides` |
| a different suite | FAIL `unit_differs` |
| claim other than `size_band` | UNINSPECTABLE `ppp_claim_not_size_band` |
| organization with two active sites, a held site outside Ohio, or no active site | HELD `ppp_not_single_site_ohio_organization` |
| the correct row, the same suite on both sides, a trade-name borrower | PASS |

It also mutates the gate to show each guard is what catches its defect: without the type whitelist a sole proprietor PASSES; without the site delegation a wrong organization street PASSES; without the PPP guards all five round-1 false passes PASS on the site grain; without the family a correct row is `unknown_source_family` (the state before this PR).

## Not done, and a prediction

- The gate does not read the loan date, the job count or the band mapping. The re-run's own `check.py` applies the ten-year limit and the band mapping.
- Lane prediction, not a gate result on a merged tree: the 101 planned fills of the re-run (base `e4fd6585`, 53 organization and 48 site bands), written in this format and judged by this gate against main's records, give 94 PASS, 3 HELD `designator_not_on_both_sides`, 2 HELD `passes_on_two_records`, 2 FAIL `unit_differs`. The two FAILs are ORG-001525 and its site (Suite 500 against Ste 110), which the controller has ruled held. The five other non-PASS rows will be dropped from the data PR and listed with their reasons.
- Not run here: the full scripts suite beyond `test_check_evidence_binding`, and CI.

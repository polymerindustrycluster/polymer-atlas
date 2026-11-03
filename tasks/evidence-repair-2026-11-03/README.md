# Evidence repair pass (2026-11-03)

This pass follows the evidence audit (`tasks/evidence-audit-2026-11-03/`, PR #39). The repo owner requested it in
session on 2026-11-03. Evidence is append-only (SCHEMA §4.13): no existing row is edited. Where a weak row's cited
page no longer shows the claim, a fresher row answers it.

## Population (unit: evidence rows)
The population is 1,176 `own_site` rows (`checked.csv`) in any of three weak categories:
- site existence, address or parent claims citing a home, about, contact or locations page;
- parent claims;
- rows from the October `tri-national` packets.

37 were already covered by a government filing or registry row, or by a second own-site source, for the same claim.
The other 1,139 were re-checked on the raw page today, through the NAS Firecrawl with a full-page fetch.

## Deterministic re-check (address, existence, parent)

Checked against the record's own fields (street and city, legal or trade name, parent name):

| Claim | Rows | PASS | City only (street absent) | FAIL | Page unfetchable |
|-|-:|-:|-:|-:|-:|
| address | 455 | 241 | 109 | 73 | 32 |
| existence | 155 | 138 | | 5 | 12 |
| parent | 129 | 77 | | 44 | 8 |

**False-pass test:** each PASS check was re-run against a different record's page. It passed 0 of 241 address
trials and 0 of 138 existence trials.

## Scope judging (370 rows with a loaded page)

Four Sonnet judges worked only from the saved pages, using the audit's `JUDGE_BRIEF.md`. Their quotes were
verbatim-checked by the judges; this pass mints nothing from them. Results are in `scope_verdicts.csv`:

| Verdict | Rows |
|-|-:|
| SUPPORTED | 192 |
| PARTIAL | 139 |
| NOT_SUPPORTED | 29 |
| WRONG_PAGE | 4 |
| CANNOT_JUDGE | 6 |

The commonest PARTIAL is a company or group page that does not name the cited site.

## Replacement sources (174 rows: address, existence or parent FAIL or unfetchable)

Four Sonnet lanes looked for a government filing first, then the company's own plant or location page, then dated
press. The integrator re-fetched every FOUND page raw and checked the quote word for word (`replacements.csv`):
- 98 FOUND; 81 passed the raw check;
- 81 NONE_FOUND;
- 1 CONTRADICTED.

**Applied:** +81 evidence rows, EVD-022276 onward, above every id used by open PRs, across 43 shards.

| Claim | Rows |
|-|-:|
| address | 49 |
| parent | 25 |
| existence | 7 |

| Source class | Rows | Tier effect |
|-|-:|-|
| own_site | 38 | the weak row's tier effect |
| government_filing | 28 | the weak row's tier effect |
| press | 15 | capped at supports_B |

Each row's `notes` names the weak row it answers.

**Held (`holds.csv`, 93):**
- 81 NONE_FOUND: many were fetch limits (403s, TLS errors), not proof of absence;
- 8 where the source page could not be fetched;
- 3 where the quote was not on the page;
- 1 CONTRADICTED: Pro-Tops' own site prints only a Monroe NC address, not Matthews.

## Leads for the integrator, not applied
Status and parent changes need dated evidence and their own pass.
- **Viskase:** news and SEC text say the Osceola AR plant closed on 2025-04-30.
- **AquaWorx:** the held parent is Sentinel Capital Partners, but PlayCore was sold to Court Square in 2017.
- **AOC:** Nippon Paint announced its acquisition of AOC in November 2024; closing is unconfirmed.
- **TotalEnergies Petrochemicals & Refining USA:** the immediate parent is Total Holdings USA Inc. (EPA GHG listing).
- **Janco:** the buyer was MacLean Investment Partners, not MacLean-Fogg Company.
- **Pioneer Plastics:** listed at Auburn ME; the Morristown TN site may be wrong.
- **Kyowa America:** the parent name may be wrong ("Kyowa Electric & Chemical").
- **Conceptual Creations and Dadi:** sister records are flagged closed while one site of each is open.

## Not done
- The 109 address rows where the page shows the city but not the street.
- The 168 scope rows judged PARTIAL, NOT_SUPPORTED or WRONG_PAGE. Their replacement round is queued.

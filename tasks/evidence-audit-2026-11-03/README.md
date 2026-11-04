# Evidence audit: do `own_site` evidence rows hold up on the raw page? (2026-11-03)

This audit is read-only. No `data/` file changed. The repo owner requested it in session on 2026-11-03.

## Method
- **Frame:** the 11,425 `own_site` evidence rows on main at `4284e6f`, not withdrawn. 10,536 of them carry a URL in
  `source_ref`.
- **Sample:** 200 drawn at random (seed 20261103) from those 10,536 (`sample_fetch.py`).
- **Fetch:** each cited page was fetched raw today with the NAS Firecrawl (full page). 191 loaded and 9 did not: 6
  fetch errors, 1 with no content, 1 HTTP 500 and 1 HTTP 595. A failed fetch is an availability signal, not a verdict.
- **Judging:** four Sonnet judges worked only from the saved page text, with no web access, under `JUDGE_BRIEF.md`.
  Verdicts are SUPPORTED, PARTIAL, NOT_SUPPORTED, WRONG_PAGE or CANNOT_JUDGE.
  - Every SUPPORTED or PARTIAL quote was then checked word for word against the saved page (`analyze.py`).
  - 2 quotes failed that check and are not counted as SUPPORTED.
- **Second family:** Codex judged a random 40 of the same rows blind.
  - Its verdict matched the Sonnet judges on 35 of 40.
  - All 5 disagreements sit on the SUPPORTED/PARTIAL line, and in 4 of them the Sonnet judges were the more lenient.

## Result (unit: evidence rows)

| Measure | Rows | Rate (95% CI) |
|-|-:|-|
| SUPPORTED, of pages that loaded | 142 / 191 | 74% (68–80%) |
| SUPPORTED or PARTIAL, of pages that loaded | 179 / 191 | 94% (89–96%) |
| SUPPORTED, whole sample (an unloadable page counts against) | 142 / 200 | 71% |
| WRONG_PAGE: the page is another company's | 5 / 191 | 3% |
| NOT_SUPPORTED: right company, claim absent | 5 / 191 | 3% |

**By claim type, SUPPORTED:**

| Claim type | Rows |
|-|-:|
| scope | 122 / 151 |
| existence | 12 / 24 |
| address | 7 / 13 |
| parent | 0 / 2 |

Scope claims hold up. Existence and address claims are about a coin flip, mostly because a corporate home page is
cited for a specific plant.

**By observation date, SUPPORTED:** rows observed in 2026-11 hold up at 110 / 130, and rows observed in 2026-10 at
32 / 61.

**By creator, SUPPORTED:**

| Creator | Rows |
|-|-:|
| `claude-code-integration-prep-2026-11-01` (the 2026-11-01 packets) | 109 / 128 |
| `tri-national` packets | 6 / 19 |

The other creators have too few rows to rank.

## What fails, and how often
- **A corporate home page is cited for a plant claim (address or existence).** Examples: Aptar Cary, Pregis
  IntelliPack Tulsa, Pella Murray, Sika Lyndhurst, INEOS Carson.
- **The URL belongs to a parent or another brand, and the page never names the record.**
  - Examples: Durez on the Sumitomo Bakelite site, RPM on Tremco CPG, M. Argueso on Paramelt, Inventive Extrusion on
    Premere Enterprises, and Hyload on IKO.
  - Several are probably real acquisitions or rebrands. Even so, the evidence row does not show the link, so it
    should cite a page that names both companies.
- **Taxonomy inferred from the page rather than stated.**
  - Examples: "plastic" recorded as `thermoplastics`, "vinyl" as `pvc`, "mass transit" as rail.
  - Many SUPPORTED rows rest on one menu or link label. They count as SUPPORTED here, so the 74% is an upper bound
    for "the page explicitly states it in prose".

## What this means for the next steps
- The existing evidence is mostly real. Re-verifying all 20,236 rows is not warranted.
- A targeted repair pass is warranted:
  - existence and address rows that cite a corporate home page for a plant;
  - parent rows;
  - the October `tri-national` packets.
- New evidence should keep the raw-quote check used here. Plant-level claims should cite a plant-level page, a
  registry row, or a government filing (OSHA, Form 5500, TRI) rather than a corporate home page.

## Files
- `audit_rows.csv`: one row per sampled evidence row, with fetch status, Sonnet verdict, quote, reason and Codex
  verdict. Page text is not committed.
- `sample_fetch.py` and `analyze.py`: rerun them to reproduce; the page cache is local.
- `JUDGE_BRIEF.md`.

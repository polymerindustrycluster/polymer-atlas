# Ohio faculty wave (2026-11-03)

**Integrator:** claude-code, at the owner's request in session on 2026-11-03 ("OIEx data: Both" — use the Ohio Innovation
Exchange as a lead list, verify on university pages).

**Lead source, not committed.** The candidate names came from the Ohio Innovation Exchange expert search (`polymer`; 432 profiles).
- That site's terms reserve all rights, and its profiles show faculty emails.
- So the lead list, the rejected names and the full lane outputs are **not** in this repo, and nothing here cites the site.
- What is committed: `verified_gates.csv`, which holds the 19 VERIFIED rows with their gate URLs and quotes, all from the
  universities' own pages, plus `people_rows.csv` and `holds.csv`.

## Funnel (unit: Ohio Innovation Exchange expert profiles matching "polymer")

| Step | People |
|---|---:|
| Profiles returned | 432 |
| Already in the Atlas (name match) | 51 |
| Selected for checking: polymer in title or bio, or professor rank | 342 |
| VERIFIED on university pages (Gate A and Gate B) | 19 |
| REJECT | 193 |
| STILL_UNCERTAIN | 130 |
| **Added to `people.csv`** (`PERSON-001320`–`001333`) | **14** |

The counts include a same-day re-run of the 137 rows first left STILL_UNCERTAIN. It added 1 VERIFIED (Reilly, Ohio State) and
6 REJECTs. Most of the re-run stalled because the shared web-search budget was used up, so the re-run is not finished.

Most rejects are a candidate matched only on a publication title (medicine, biology, metals and so on). Gate B on the person's own
university page settled them.

Most STILL_UNCERTAIN rows are budget limits, not evidence: the lanes' web-search budget ran out partway. Pages returning 503s (the UC
research directory) and login walls also left rows unsettled.

## Held (5)

- **Already in the Atlas under a name variant:** Sangoro (PERSON-000093), Palmer (PERSON-000476), Khabaz (PERSON-000046) and Yavitt
  (PERSON-000063, recorded as "Ben Merkel Yavitt").
  - Yavitt's record carries role `professor`, but his page styles him "Asst Professor (F2)". That is a rank fix for the next
    title pass.
- **Integrator Gate B review:** McComb (Ohio State). His page names polymers only as an example of what his electron microscopy studies.

## Accepted on review

Per-person research-area entries on a department's own people page count as person-level Gate B (Uz and Holland at Cleveland State;
Cooper and Wang at Ohio State). Thin but direct statements were also accepted: Olesik (polymer nanofibers), Modarelli (polymers
among his studied materials) and Park (polymer composites in manufacturing).

## Re-running the 130 STILL_UNCERTAIN

Rebuild the candidate list locally from the Ohio Innovation Exchange search (people.ohioinnovationexchange.org, `POST /api/users`
with text `polymer`). Take names, titles and institutions only, never emails. Drop names already in `people.csv` or listed in
`verified_gates.csv`. Then run `LANE_BRIEF.md` and integrate with `build_integration.py`.

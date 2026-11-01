# Discovery wave status: paused 2026-11-01 (owner out of API credit)

The four lanes were stopped before they finished.

- **CA and IL:** the lanes wrote packet files (`creates_orgs.csv`,
  `creates_sites.csv`, `evidence_rows.csv`, `registry_link_candidates.csv`,
  `verdicts.csv`) but did **not** finish.
  - **Not done:** no `REPORT.md`, no validator dry run on a temp copy, and no
    orchestrator review.
  - **Treat as unreviewed drafts:** re-run the brief's dry run (LANE_BRIEF.md)
    and review every row before any integration.
- **MI and TX:** stopped before writing any output.
- **To resume:** relaunch a lane per state with `LANE_BRIEF.md` and the
  `<ST>_assignment.csv` file. For CA and IL, tell the lane to finish and validate
  the existing packet rather than start over.

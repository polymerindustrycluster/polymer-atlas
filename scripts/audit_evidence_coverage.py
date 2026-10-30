#!/usr/bin/env python3
"""Read-only §4.13 coverage inventory, not a validator or verification verdict.

Only reads CSVs and writes the requested report to stdout. Run validate.py first.
No network requests, inferred evidence, tier changes, or canonical-data writes.
"""
import argparse
import csv
from collections import Counter, defaultdict
from datetime import date
import hashlib
import json
from pathlib import Path
import sys

TABLES = {
    "organizations": ("organizations_*.csv", "org_id", "legal_name"),
    "sites": ("sites_*.csv", "site_id", "site_name"),
    "ecosystem": ("ecosystem.csv", "org_id", "legal_name"),
    "programs": ("programs.csv", "program_id", "program_name"),
}
BASE_CLAIMS = {
    "organizations": {"existence", "address", "scope", "code"},
    "sites": {"existence", "address", "scope", "code", "parent"},
    "ecosystem": {"existence", "address", "scope"},
    "programs": {"existence", "scope"},
}
CLAIMS = {"existence", "address", "scope", "code", "parent", "activity", "liveness"}
EFFECTS = {"supports_A", "supports_B", "supports_C", "contradicts"}
POSTURES = ("no_rows_history_unknown", "started_with_gaps", "claim_rows_present")


def expected_claims(table, row):
    """Current-value planning checklist, matching validate.py's V-25 claim set.

An organization parent-motion requirement cannot be inferred from a snapshot;
review the lane journal separately. Never use this checklist as a shipment gate.
"""
    claims = set(BASE_CLAIMS[table])
    status_key = "operating_status" if table == "sites" else "status"
    if table in ("organizations", "sites") and row.get(status_key) == "active":
        claims.update(("activity", "liveness"))
    if table == "programs" and row.get("cip_code", "").strip():
        claims.add("code")
    return claims


def read_csv(path, required):
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if not set(required).issubset(reader.fieldnames or []):
            raise ValueError(f"{path.name}: missing required columns {sorted(set(required) - set(reader.fieldnames or []))}")
        rows = list(reader)
    if any(None in r or any(v is None for v in r.values()) for r in rows):
        raise ValueError(f"{path.name}: malformed CSV row")
    return rows


def inventory(data_dir):
    """Return table-qualified records, evidence and byte-level input manifest."""
    records, paths = {}, []
    for table, (pattern, id_col, _) in TABLES.items():
        files = sorted(data_dir.glob(pattern))
        # Generated merged exports must never be counted as another shard.
        files = [p for p in files if p.name not in ("organizations_all.csv", "sites_all.csv")]
        if not files:
            raise ValueError(f"No canonical files found for {table}: {pattern}")
        for path in files:
            paths.append(path)
            for row in read_csv(path, (id_col, "verification_tier")):
                key = (table, row[id_col])
                if not key[1] or key in records:
                    raise ValueError(f"{path.name}: blank or duplicate record ID {key}")
                records[key] = row
    path = data_dir / "evidence.csv"
    evidence = read_csv(path, ("evidence_id", "record_table", "record_id", "claim_type", "tier_effect", "source_class", "observed_date"))
    paths.append(path)
    seen = set()
    for row in evidence:
        eid = row["evidence_id"]
        if not eid or eid in seen:
            raise ValueError(f"Blank or duplicate evidence ID {eid}")
        seen.add(eid)
        key = (row["record_table"], row["record_id"])
        if key not in records:
            raise ValueError(f"Evidence {eid} references absent table-qualified record {key}")
        if row["claim_type"] not in CLAIMS or row["tier_effect"] not in EFFECTS:
            raise ValueError(f"Evidence {eid} has unsupported claim/effect")
        if date.fromisoformat(row["observed_date"]).isoformat() != row["observed_date"]:
            raise ValueError(f"Evidence {eid} has non-ISO date")
    manifest = [{"path": p.name, "sha256": hashlib.sha256(p.read_bytes()).hexdigest()} for p in sorted(paths)]
    return records, evidence, manifest


def analyze(records, evidence, limit=25):
    if limit < 0:
        raise ValueError("limit must be non-negative")
    by_record = defaultdict(list)
    for row in evidence:
        by_record[(row["record_table"], row["record_id"])].append(row)
    summary, gaps, candidates = {}, Counter(), []
    all_claim_rows = Counter()
    for row in evidence:
        all_claim_rows[(row["record_table"], row["claim_type"])] += 1
    for (table, rid), record in sorted(records.items()):
        rows = by_record[(table, rid)]
        expected = expected_claims(table, record)
        present = {r["claim_type"] for r in rows}
        missing = expected - present
        contradicted, unsupported = [], []
        for claim in sorted(present):
            group = [r for r in rows if r["claim_type"] == claim]
            supporting = [r["observed_date"] for r in group if r["tier_effect"].startswith("supports_")
                          and not (claim == "scope" and r["source_class"] == "platform_category")]
            contradicting = [r["observed_date"] for r in group if r["tier_effect"] == "contradicts"]
            if not supporting:
                unsupported.append(claim)
            if contradicting and (not supporting or max(contradicting) >= max(supporting)):
                contradicted.append(claim)
        posture = "no_rows_history_unknown" if not rows else ("started_with_gaps" if missing else "claim_rows_present")
        tier = record.get("verification_tier", "") or "blank"
        key = (table, tier)
        if key not in summary:
            summary[key] = {"table": table, "tier": tier, "records": 0, "evidence_rows": 0,
                            **{p: 0 for p in POSTURES}, "records_with_current_contradiction": 0,
                            "records_with_unsupported_present_claim": 0}
        item = summary[key]
        item["records"] += 1
        item["evidence_rows"] += len(rows)
        item[posture] += 1
        item["records_with_current_contradiction"] += bool(contradicted)
        item["records_with_unsupported_present_claim"] += bool(unsupported)
        # No-row records are deliberately absent from this focused queue.
        if rows:
            for claim in missing:
                gaps[(table, claim)] += 1
        status = record.get("operating_status" if table == "sites" else "status", "")
        if rows and (missing or contradicted or unsupported) and status in ("active", "unknown"):
            candidates.append({"table": table, "record_id": rid, "name": record.get(TABLES[table][2], ""),
                               "tier": tier, "status": status, "missing_claim_rows": sorted(missing),
                               "contradicted_claims": contradicted, "unsupported_present_claims": unsupported,
                               "evidence_ids": sorted(r["evidence_id"] for r in rows),
                               "review_action": "Inspect integration journal and freshly verify missing/disputed claims; do not auto-edit tier or status."})
    candidates.sort(key=lambda r: (not bool(r["contradicted_claims"]), not bool(r["unsupported_present_claims"]),
                                   r["tier"] not in ("A", "B", "C"), "scope" not in r["missing_claim_rows"],
                                   -len(r["missing_claim_rows"]), r["table"], r["record_id"]))
    return {"summary": [summary[k] for k in sorted(summary)],
            "claim_row_counts": [{"table": t, "claim": c, "evidence_rows": n} for (t, c), n in sorted(all_claim_rows.items())],
            "gaps_among_records_with_rows": [{"table": t, "claim": c, "records": n} for (t, c), n in sorted(gaps.items())],
            "review_queue_total": len(candidates), "review_queue": candidates[:limit]}


def cell(value):
    return str(value).replace("|", "\\|").replace("\n", " ").replace("\r", " ")


def markdown(result):
    lines = ["# Evidence coverage inventory", "", f"Generated date: {result['as_of']}",
             f"Snapshot label: `{result['snapshot_ref']}` (caller supplied; input digests below identify actual bytes).", "",
             "## Interpretation and limits", "",
             "Read-only inventory of all canonical organization, site, ecosystem and program rows, including tombstones, grouped by their recorded verification tier. Counts are not company/establishment headline totals.", "",
             "- **No rows/history unknown** is not an error: §4.13 grandfathered legacy sources. These CSVs do not identify creation/claim-change time; `last_verified` is not a migration flag. A no-row record might be grandfathered or might need a post-contract journal review. This report cannot decide which.",
             "- **Started with gaps** has at least one evidence row but lacks one or more current-value checklist claim types. Partial legacy touches remain possible; gaps are review signals, not violations or re-grading instructions.",
             "- **Claim rows present** means claim types are represented, not that the facts are true, current, supported at the claimed tier, or free of contradiction. Contradictions and unsupported present claims are reported separately across all observed claim types, including optional claims.",
             "- Checklist mirrors schema §4.13 / validator V-25: organizations existence/address/scope/code; sites add parent; active organizations/sites add activity/liveness; ecosystem existence/address/scope; programs existence/scope and code when CIP is populated. Organization parent changes require journal-specific review; they cannot be inferred from this snapshot.",
             "- Current contradiction uses §4.13 date ordering: contradiction on/after newest support. Platform categories never count as scope support. This is not V-22/V-25 validation, source fetching, source-class adjudication, tier computation, or status adjudication; run `scripts/validate.py` separately.",
             "- Evidence is append-only history. This inventory does not decide whether claim_detail refers to a superseded value; humans must inspect the cited rows and journals. No legacy source strings are parsed into evidence.", "",
             "## Coverage by record table and recorded tier", "",
             "| Table | Tier | Record rows | Evidence rows | No rows/history unknown | Started with gaps | Claim rows present | Current contradiction | Unsupported present claim |",
             "|---|---|---:|---:|---:|---:|---:|---:|---:|"]
    fields = ["table", "tier", "records", "evidence_rows", *POSTURES, "records_with_current_contradiction", "records_with_unsupported_present_claim"]
    for row in result["summary"]:
        lines.append("| " + " | ".join(cell(row[f]) for f in fields) + " |")
    lines += ["", "## Missing claim types among records that already have evidence", "",
              "One record can contribute several missing claim types; do not sum these as distinct records.", "",
              "| Table | Missing claim | Record rows |", "|---|---|---:|"]
    for row in result["gaps_among_records_with_rows"]:
        lines.append(f"| {row['table']} | {row['claim']} | {row['records']} |")
    lines += ["", "## Bounded review queue", "", f"Showing {len(result['review_queue'])} of {result['review_queue_total']} active/unknown records with evidence and a gap, unsupported claim or current contradiction. No-row records are excluded to avoid treating grandfathered records as failures. Priority: contradictions, unsupported claims, A–C tiers, missing scope, number of gaps, table and ID. This is research triage, not an entity verdict.", "",
              "| Table / ID | Name | Tier | Missing | Contradicted | Unsupported | Evidence IDs |", "|---|---|---|---|---|---|---|"]
    for row in result["review_queue"]:
        lines.append("| " + " | ".join(cell(v) for v in [f"{row['table']} / {row['record_id']}", row['name'], row['tier'], ", ".join(row['missing_claim_rows']) or "—", ", ".join(row['contradicted_claims']) or "—", ", ".join(row['unsupported_present_claims']) or "—", ", ".join(row['evidence_ids'])]) + " |")
    lines += ["", "For each candidate: inspect the integration journal to establish whether the prospective contract applies; then observe the original witnesses afresh and submit an evidence packet. Do not promote, demote, merge or change status from this report.", "",
              "## Reproduce", "", "```sh", "python3 scripts/validate.py", f"python3 scripts/audit_evidence_coverage.py --as-of {result['as_of']} --snapshot-ref {result['snapshot_ref']} --limit {result['limit']} --format markdown", "python3 -m unittest discover -s scripts -p 'test_audit_evidence_coverage.py'", "```", "",
              "Use `--format json` for claim-row counts, structured review records and the same input manifest. Output goes only to stdout; redirect only to a report, never a canonical CSV.", "", "## Input SHA-256 manifest", "", "| CSV | SHA-256 |", "|---|---|"]
    lines += [f"| {row['path']} | `{row['sha256']}` |" for row in result['input_manifest']]
    return "\n".join(lines) + "\n"


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", type=Path, default=Path(__file__).resolve().parents[1] / "data")
    parser.add_argument("--format", choices=("json", "markdown"), default="json")
    parser.add_argument("--limit", type=int, default=25)
    parser.add_argument("--as-of", required=True, help="Report date YYYY-MM-DD; not a source-verification date")
    parser.add_argument("--snapshot-ref", default="working-tree", help="Caller-supplied label; file digests are authoritative")
    args = parser.parse_args(argv)
    try:
        if date.fromisoformat(args.as_of).isoformat() != args.as_of:
            raise ValueError("as-of must be YYYY-MM-DD")
        records, evidence, manifest = inventory(args.data_dir)
        result = analyze(records, evidence, args.limit)
        result.update(as_of=args.as_of, snapshot_ref=args.snapshot_ref, limit=args.limit, input_manifest=manifest)
    except (ValueError, OSError) as exc:
        parser.error(str(exc))
    print(markdown(result) if args.format == "markdown" else json.dumps(result, indent=2, ensure_ascii=False), end="" if args.format == "markdown" else "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())

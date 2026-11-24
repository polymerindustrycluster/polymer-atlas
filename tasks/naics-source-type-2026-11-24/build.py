from pathlib import Path
import json
import re
import sys
from collections import defaultdict

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "tasks/entity-type-from-name-2026-11-22"))
import common as C

COLUMN = "naics_primary_source_type"

def mentions(detail, code):
    """True if the six-digit code appears anywhere in claim_detail as its own number."""
    return re.search(r"(?<!\d)" + re.escape(code) + r"(?!\d)", detail) is not None

def changes(data):
    evidence = defaultdict(list)
    for _, e in C.tagged(data, "evidence_*.csv"):
        evidence[e["record_table"], e["record_id"]].append(e)
    for table in ("organizations", "sites"):
        for file, row in C.tagged(data, table + "_*.csv"):
            rid = next(iter(row.values()))
            code = row["naics_primary"]
            before = row[COLUMN]
            if not code or before in {"company_disclosed", "directory_assigned", "government_filing", "researcher_inferred"} or row["naics_confidence"] not in {"high", "medium", "low"}:
                continue
            # A code the record's evidence mentions anywhere needs a reader (disclosure, filing or directory): hold it.
            # Only a code no evidence row mentions is relabelled, to the residual type researcher_inferred.
            if any(mentions(e["claim_detail"], code) for e in evidence[table, rid]):
                continue
            yield file, rid, before, "researcher_inferred"

if __name__ == "__main__":
    packet = [dict(file=f, record_id=r, column=COLUMN, before=b, after=a)
              for f, r, b, a in changes(ROOT / "data")]
    C.apply_changes(ROOT / "data", packet)
    baseline = ROOT / "scripts/validate_debt_baseline.json"
    state = json.loads(baseline.read_text())
    fixed = {c["record_id"] for c in packet}
    if fixed:
        state["rules"]["V-47"] = [rid for rid in state["rules"]["V-47"] if rid not in fixed]
        # Preserve the baseline's existing JSON escaping and indentation outside V-47.
        old = baseline.read_text()
        section = json.dumps(state["rules"]["V-47"], indent=1).replace("\n", "\n  ")
        baseline.write_text(re.sub(r'("V-47": )\[[^\]]*\]', lambda m: m[1] + section, old, count=1))
    print(f"Changed {len(packet)} cells.")


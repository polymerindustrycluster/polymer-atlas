#!/usr/bin/env python3
"""Write the V-65 adoption baseline: every organizations/sites/ecosystem/programs/people record with no row in
data/evidence_*.csv, keyed "<record_table>:<record_id>:<identity fingerprint>", into scripts/validate_debt_baseline.json.

Run once, at adoption, from the repo root:  python3 tasks/evidence-presence-floor-2026-11-20/build_baseline.py --write
It reconciles its count against scripts/audit_evidence_coverage.py (an independent implementation) and refuses to
write if the two disagree or if V-65 is already in the baseline file. Without --write it prints both counts and the
drift between the data and the checked-in baseline. Stdlib only.
"""
import csv, hashlib, json, re, subprocess, sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATA, BASELINE = ROOT / "data", ROOT / "scripts" / "validate_debt_baseline.json"
# must stay identical to scripts/validate.py V65_TABLES / v65_key (validate.py proves it: 0 new V-65 errors after a write)
TABLES = {"organizations": ("organizations_*.csv", "org_id", ("legal_name", "hq_city", "hq_state")),
          "sites": ("sites_*.csv", "site_id", ("org_id", "site_name", "street_address", "city", "state")),
          "ecosystem": ("ecosystem.csv", "org_id", ("legal_name", "city", "state")),
          "programs": ("programs.csv", "program_id", ("institution_org_id", "program_name")),
          "people": ("people.csv", "person_id", ("full_name", "institution_org_id"))}


def v65_key(table, rid, values):
    ident = "|".join(re.sub(r"[^a-z0-9]+", "", (v or "").lower()) for v in values)
    return f"{table}:{rid}:{hashlib.sha1(ident.encode()).hexdigest()[:8]}"


def rows(pattern):
    for path in sorted(DATA.glob(pattern)):
        with open(path, newline="", encoding="utf-8") as fh:
            yield from csv.DictReader(fh)


with_rows = {(r["record_table"].strip(), r["record_id"].strip()) for r in rows("evidence_*.csv")}
keys = sorted(v65_key(t, r[col].strip(), [r.get(c) for c in ident]) for t, (pat, col, ident) in TABLES.items()
              for r in rows(pat) if (t, r[col].strip()) not in with_rows)
assert len(keys) == len(set(keys)), "duplicate record key"
by_table = Counter(k.split(":", 1)[0] for k in keys)

# Independent count: the repo's own coverage audit sums records with no rows as `no_rows_history_unknown` per table/tier.
audit = json.loads(subprocess.run([sys.executable, str(ROOT / "scripts" / "audit_evidence_coverage.py"),
                                   "--data-dir", str(DATA), "--as-of", "2026-11-20"],
                                  capture_output=True, text=True, encoding="utf-8", check=True, cwd=ROOT).stdout)
audit_by_table = Counter()
for s in audit["summary"]:
    audit_by_table[s["table"]] += s["no_rows_history_unknown"]
print("baseline:", len(keys), dict(sorted(by_table.items())))
print("audit   :", sum(audit_by_table.values()), dict(sorted(audit_by_table.items())))
if dict(by_table) != {t: n for t, n in audit_by_table.items() if n}:
    sys.exit("baseline and audit_evidence_coverage.py disagree: stop and investigate before writing (AGENTS.md §2 rule 10c)")

doc = json.loads(BASELINE.read_text(encoding="utf-8"))
if "V-65" in doc["rules"]:
    old, stale = set(doc["rules"]["V-65"]), set(doc["rules"]["V-65"]) - set(keys)
    repaired = {k for k in stale if tuple(k.split(":")[:2]) in with_rows}  # the record now has a row
    print(f"V-65 baselined: {len(old)}; repaired (record now has a row; removable): {len(repaired)}; "
          f"obsolete (identity fields changed or record gone, still row-less): {len(stale - repaired)}; "
          f"row-less but not baselined (validate.py errors on these): {len(set(keys) - old)}")
    if "--write" in sys.argv:
        sys.exit("V-65 already baselined; regenerating it needs an owner-approved PR (see the file's _doc)")
elif "--write" in sys.argv:
    doc["rules"]["V-65"] = keys
    doc["amended"] += (f" 2026-11-20: V-65 (SCHEMA §4.13 presence floor: every organizations/sites/ecosystem/programs/"
                       f"people record has at least one evidence row) adopted under owner ruling 2026-11-20 with "
                       f"{len(keys)} records grandfathered ({', '.join(f'{t} {n}' for t, n in sorted(by_table.items()))}); "
                       f"keys are <record_table>:<record_id>:<identity fingerprint>; "
                       f"tasks/evidence-presence-floor-2026-11-20/.")
    BASELINE.write_text(json.dumps(doc, indent=1, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    print("wrote", BASELINE.relative_to(ROOT))

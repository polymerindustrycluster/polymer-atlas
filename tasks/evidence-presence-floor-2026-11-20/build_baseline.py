#!/usr/bin/env python3
"""Write the V-68 adoption baseline: every tier-C/U organizations/sites/ecosystem/programs/people record with no row in
data/evidence_*.csv, keyed "<record_table>:<record_id>:<identity fingerprint>", into scripts/validate_debt_baseline.json.
(Tier A/B records are V-65's: SCHEMA v1.17 "no naked tier-A/B".)

Run once, at adoption, from the repo root:  python3 tasks/evidence-presence-floor-2026-11-20/build_baseline.py --write
It reconciles its count, table by table, against scripts/audit_evidence_coverage.py (an independent implementation) and
refuses to write if the two disagree or if V-68 is already in the baseline file. Without --write it prints both counts
and the drift between the data and the checked-in baseline. Stdlib only.
"""
import csv, hashlib, json, re, subprocess, sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATA, BASELINE = ROOT / "data", ROOT / "scripts" / "validate_debt_baseline.json"
# must stay identical to scripts/validate.py V68_TABLES / v68_key (validate.py proves it: 0 new V-68 errors after a write)
TABLES = {"organizations": ("organizations_*.csv", "org_id", ("legal_name", "hq_city", "hq_state")),
          "sites": ("sites_*.csv", "site_id", ("org_id", "site_name", "street_address", "city", "state")),
          "ecosystem": ("ecosystem.csv", "org_id", ("legal_name", "city", "state")),
          "programs": ("programs.csv", "program_id", ("institution_org_id", "program_name")),
          "people": ("people.csv", "person_id", ("full_name", "institution_org_id"))}


def v68_key(table, rid, values):
    ident = "|".join(re.sub(r"[^a-z0-9]+", "", (v or "").lower()) for v in values)
    return f"{table}:{rid}:{hashlib.sha1(ident.encode()).hexdigest()[:8]}"


def rows(pattern):
    for path in sorted(DATA.glob(pattern)):
        with open(path, newline="", encoding="utf-8") as fh:
            yield from csv.DictReader(fh)


with_rows = {(r["record_table"].strip(), r["record_id"].strip()) for r in rows("evidence_*.csv")}
keys = sorted(v68_key(t, r[col].strip(), [r.get(c) for c in ident]) for t, (pat, col, ident) in TABLES.items()
              for r in rows(pat) if (r.get("verification_tier") or "").strip() not in ("A", "B") and (t, r[col].strip()) not in with_rows)
assert len(keys) == len(set(keys)), "duplicate record key"
by_table = Counter(k.split(":", 1)[0] for k in keys)

# Independent count: the repo's coverage audit reports records with no rows as `no_rows_history_unknown` per table/tier.
audit = json.loads(subprocess.run([sys.executable, str(ROOT / "scripts" / "audit_evidence_coverage.py"),
                                   "--data-dir", str(DATA), "--as-of", "2026-11-20"],
                                  capture_output=True, text=True, encoding="utf-8", check=True, cwd=ROOT).stdout)
audit_by_table = Counter()
for s in audit["summary"]:
    if s["tier"] not in ("A", "B"):  # same predicate as validate.py V-68 (blank or invalid tiers fall in)
        audit_by_table[s["table"]] += s["no_rows_history_unknown"]
print("baseline:", len(keys), dict(sorted(by_table.items())))
print("audit   :", sum(audit_by_table.values()), dict(sorted(audit_by_table.items())))
if dict(by_table) != {t: n for t, n in audit_by_table.items() if n}:
    sys.exit("baseline and audit_evidence_coverage.py disagree: stop and investigate before writing (AGENTS.md §2 rule 10c)")

doc = json.loads(BASELINE.read_text(encoding="utf-8"))
if "V-68" in doc["rules"]:
    old, stale = set(doc["rules"]["V-68"]), set(doc["rules"]["V-68"]) - set(keys)
    repaired = {k for k in stale if tuple(k.split(":")[:2]) in with_rows}  # the record now has a row
    print(f"V-68 baselined: {len(old)}; repaired (record now has a row; removable): {len(repaired)}; "
          f"obsolete (identity fields or tier changed, or record gone): {len(stale - repaired)}; "
          f"row-less but not baselined (validate.py errors on these): {len(set(keys) - old)}")
    if "--write" in sys.argv:
        sys.exit("V-68 already baselined; regenerating it needs an owner-approved PR (see the file's _doc)")
elif "--write" in sys.argv:
    doc["rules"]["V-68"] = keys
    doc["amended"] += (f" 2026-11-20: V-68 (SCHEMA §4.13 presence floor for tier C/U: every tier-C/U record has at least one "
                       f"evidence row; V-65 covers tier A/B) adopted under owner ruling 2026-11-20 with {len(keys)} records "
                       f"grandfathered ({', '.join(f'{t} {n}' for t, n in sorted(by_table.items()))}); keys are "
                       f"<record_table>:<record_id>:<identity fingerprint>; tasks/evidence-presence-floor-2026-11-20/.")
    BASELINE.write_text(json.dumps(doc, indent=1, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    print("wrote", BASELINE.relative_to(ROOT))

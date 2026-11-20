#!/usr/bin/env python3
"""Append the TRI-lane rows that BOTH review families judged SOUND, then shrink V-65's baseline by the records they
evidence.

    python3 tasks/evidence-tri-filings-2026-11-20/apply.py . --start EVD-410026 <codex.json> <agy.json> [<agy-part2.json> ...]

The first review file must cover every packet row (one family). The remaining files are the second family's review,
possibly split across parts, which must also cover every row. A row applies only if every verdict on it is SOUND.
IDs are allocated ascending from --start and must be absent tree-wide; rows go to the record's home shard file.
Writes applied.csv and withheld.csv beside this script. Stdlib only.
"""
import csv, json, re, subprocess, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
FIELDS = ["evidence_id", "record_table", "record_id", "claim_type", "claim_detail", "source_class", "source_ref",
          "observed_date", "tier_effect", "created_by", "notes"]
a = sys.argv[1:]
repo = Path(a[0])
start = int(a[a.index("--start") + 1].split("-")[1])
files = [p for p in a[1:] if p.endswith(".json")]
rd = lambda p: list(csv.DictReader(open(p, encoding="utf-8", newline="")))


def verdicts(path):
    txt = Path(path).read_text(encoding="utf-8")
    return {(v["record_id"], v["claim_type"]): v for v in json.loads(txt[txt.index("{"):txt.rindex("}") + 1])["verdicts"]}


rows = rd(HERE / "packet_rows.csv")
keys = {(r["record_id"], r["claim_type"]) for r in rows}
fam1 = verdicts(files[0])
fam2 = {}
for p in files[1:]:
    fam2.update(verdicts(p))
for name, fam in (("first family", fam1), ("second family", fam2)):
    missing = keys - set(fam)
    assert not missing, f"{name} has no verdict for {sorted(missing)}"  # an unreviewed row never applies
used = {r["evidence_id"] for f in (repo / "data").glob("evidence_*.csv") for r in rd(f)}
applied, withheld, n = [], [], start
for r in rows:
    k = (r["record_id"], r["claim_type"])
    v1, v2 = fam1[k], fam2[k]
    if v1["verdict"] != "SOUND" or v2["verdict"] != "SOUND":
        withheld.append({"record_id": k[0], "claim_type": k[1], "codex": f"{v1['verdict']}: {v1.get('reason', '')}",
                         "antigravity": f"{v2['verdict']}: {v2.get('reason', '')}"})
        continue
    eid = f"EVD-{n:06d}"; n += 1
    assert eid not in used, eid
    applied.append({"evidence_id": eid, **{f: r[f] for f in FIELDS[1:]}, "_shard": r["_shard"]})
for x in applied:
    path = repo / "data" / f"evidence_organizations_{x['_shard']}.csv"
    assert path.exists(), path
    with open(path, "a", encoding="utf-8", newline="") as fh:
        csv.writer(fh, lineterminator="\n").writerow([x[f] for f in FIELDS])
with open(HERE / "applied.csv", "w", encoding="utf-8", newline="") as fh:
    d = csv.DictWriter(fh, fieldnames=FIELDS + ["_shard"], lineterminator="\n"); d.writeheader(); d.writerows(applied)
with open(HERE / "withheld.csv", "w", encoding="utf-8", newline="") as fh:
    d = csv.DictWriter(fh, fieldnames=["record_id", "claim_type", "codex", "antigravity"], lineterminator="\n")
    d.writeheader(); d.writerows(withheld)
print(f"applied {len(applied)} rows ({applied[0]['evidence_id'] if applied else '-'}..{applied[-1]['evidence_id'] if applied else '-'}); "
      f"withheld {len(withheld)}")

# V-65 shrink-only doctrine: an ID leaves the list when a lane evidences the record. 'amended' is left alone (no conflict
# with other PRs editing that line); the README records the shrink.
out = subprocess.run([sys.executable, str(repo / "scripts" / "validate.py"), "--debt-details"],
                     capture_output=True, text=True, encoding="utf-8", cwd=repo).stdout
still = set(re.findall(r"V-65 debt: \w+ (\S+) is tier", out))
base = repo / "scripts" / "validate_debt_baseline.json"
doc = json.loads(base.read_text(encoding="utf-8"))
old = doc["rules"]["V-65"]
assert still and still <= set(old), "validate.py output not understood; V-65 baseline untouched"
doc["rules"]["V-65"] = [i for i in old if i in still]
base.write_text(json.dumps(doc, indent=1, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
print(f"V-65 baseline {len(old)} -> {len(still)} (dropped {len(old) - len(still)} records this lane evidenced)")

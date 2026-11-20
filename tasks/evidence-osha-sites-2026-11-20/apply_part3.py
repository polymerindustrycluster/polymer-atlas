#!/usr/bin/env python3
"""Apply OSHA-lane part 3 under the owner's waiver of 2026-11-20 ("Codex-only for now": Codex alone gates the evidence
lanes until a second family returns). Takes the rows withheld as "awaiting review by antigravity", applies those Codex
judged SOUND (a site whose existence row Codex rejected loses all its rows), then shrinks V-65/V-68.

    python3 tasks/evidence-osha-sites-2026-11-20/apply_part3.py . --start EVD-410357

Writes applied_part3.csv beside this script. IDs ascend from --start and must be absent tree-wide. Stdlib only.
"""
import csv, json, re, subprocess, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
FIELDS = ["evidence_id", "record_table", "record_id", "claim_type", "claim_detail", "source_class", "source_ref",
          "observed_date", "tier_effect", "created_by", "notes"]
a = sys.argv[1:]
repo, start = Path(a[0]), int(a[a.index("--start") + 1].split("-")[1])
rd = lambda p: list(csv.DictReader(open(p, encoding="utf-8", newline="")))
t = (HERE / "review_codex_3.json").read_text(encoding="utf-8")
codex = {(v["record_id"], v["claim_type"]): v["verdict"] for v in json.loads(t[t.index("{"):t.rindex("}") + 1])["verdicts"]}
waiting = {(w["record_id"], w["claim_type"]) for w in rd(HERE / "withheld.csv") if w["held"].startswith("awaiting review")}
assert waiting and waiting <= set(codex), "every part-3 row must carry a Codex verdict"
bad = {rid for rid, c in waiting if c == "existence" and codex[(rid, c)] != "SOUND"}
used = {r["evidence_id"] for f in (repo / "data").glob("evidence_*.csv") for r in rd(f)}
applied, n = [], start
for r in rd(HERE / "packet_rows.csv"):
    k = (r["record_id"], r["claim_type"])
    if k not in waiting or codex[k] != "SOUND" or k[0] in bad:
        continue
    eid = f"EVD-{n:06d}"; n += 1
    assert eid not in used, eid
    notes = r["notes"] + " Reviewed by Codex only, under the owner's waiver of 2026-11-20 (no second family available)."
    applied.append({"evidence_id": eid, **{f: r[f] for f in FIELDS[1:]}, "notes": notes, "_shard": r["_shard"]})
for x in applied:
    path = repo / "data" / f"evidence_sites_{x['_shard']}.csv"
    assert path.exists(), path
    with open(path, "a", encoding="utf-8", newline="") as fh:
        csv.writer(fh, lineterminator="\n").writerow([x[f] for f in FIELDS])
with open(HERE / "applied_part3.csv", "w", encoding="utf-8", newline="") as fh:
    d = csv.DictWriter(fh, fieldnames=FIELDS + ["_shard"], lineterminator="\n"); d.writeheader(); d.writerows(applied)
print(f"part 3: {len(waiting)} rows waiting on {len({k[0] for k in waiting})} sites; applied {len(applied)} rows "
      f"({applied[0]['evidence_id'] if applied else '-'}..{applied[-1]['evidence_id'] if applied else '-'}) on "
      f"{len({x['record_id'] for x in applied})} sites; {len(bad)} sites lost existence")

out = subprocess.run([sys.executable, str(repo / "scripts" / "validate.py"), "--debt-details"],
                     capture_output=True, text=True, encoding="utf-8", cwd=repo).stdout
base = repo / "scripts" / "validate_debt_baseline.json"
doc = json.loads(base.read_text(encoding="utf-8"))
v65 = set(re.findall(r"V-65 debt: \w+ (\S+) is tier", out))
v68 = set(re.findall(r"V-68 debt: (\w+) (\S+) is tier", out))
assert v65 and v68, "validate.py output not understood; baselines untouched"
before = (len(doc["rules"]["V-65"]), len(doc["rules"]["V-68"]))
doc["rules"]["V-65"] = [i for i in doc["rules"]["V-65"] if i in v65]
doc["rules"]["V-68"] = [k for k in doc["rules"]["V-68"] if tuple(k.split(":")[:2]) in v68]
base.write_text(json.dumps(doc, indent=1, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
print(f"V-65 {before[0]} -> {len(doc['rules']['V-65'])}; V-68 {before[1]} -> {len(doc['rules']['V-68'])}")

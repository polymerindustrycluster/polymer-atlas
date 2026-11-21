#!/usr/bin/env python3
"""Append the Form 5500-lane rows the review families judged SOUND, then shrink V-65/V-68 by the orgs they evidence.

    python3 tasks/evidence-form5500-orgs-2026-11-20/apply.py . --start EVD-410701 --codex c1.json c2.json [--agy a1.json a2.json]

Reviews are HELD until at least 2026-11-22 (owner, 2026-11-20). With --agy, a row applies only if both families judged
it SOUND (the standing two-family rule). Without it, Codex alone gates the lane under the owner's waiver of 2026-11-20
("Codex-only for now"), and each applied row's notes say so. Each family's files must cover every packet row. An org
whose `existence` row a family rejected loses all its rows. IDs ascend from --start and must be absent tree-wide; rows
go to the org's home shard. Writes applied.csv and withheld.csv beside this script. Stdlib only.
"""
import csv, json, subprocess, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
FIELDS = ["evidence_id", "record_table", "record_id", "claim_type", "claim_detail", "source_class", "source_ref",
          "observed_date", "tier_effect", "created_by", "notes"]
WAIVER = " Reviewed by Codex only, under the owner's waiver of 2026-11-20 (no second family available)."
a = sys.argv[1:]
repo, start = Path(a[0]), int(a[a.index("--start") + 1].split("-")[1])
rd = lambda p: list(csv.DictReader(open(p, encoding="utf-8", newline="")))


def files(flag):
    if flag not in a:
        return []
    i = a.index(flag) + 1
    return a[i:next((j for j in range(i, len(a)) if a[j].startswith("--")), len(a))]


def verdicts(paths):
    out = {}
    for p in paths:
        t = (HERE / p).read_text(encoding="utf-8")
        out.update({(v["record_id"], v["claim_type"]): v for v in json.loads(t[t.index("{"):t.rindex("}") + 1])["verdicts"]})
    return out


fams = {name: verdicts(files("--" + name)) for name in ("codex", "agy") if files("--" + name)}
assert "codex" in fams, "Codex verdicts are required"
packet = rd(HERE / "packet_rows.csv")
for name, v in fams.items():
    miss = [(r["record_id"], r["claim_type"]) for r in packet if (r["record_id"], r["claim_type"]) not in v]
    assert not miss, f"{name}: {len(miss)} packet rows have no verdict, e.g. {miss[:3]}"
sound = lambda k: all(v[k]["verdict"] == "SOUND" for v in fams.values())
bad = {r["record_id"] for r in packet if r["claim_type"] == "existence" and not sound((r["record_id"], "existence"))}
used = {r["evidence_id"] for f in (repo / "data").glob("evidence_*.csv") for r in rd(f)}
applied, withheld, n = [], [], start
for r in packet:
    k = (r["record_id"], r["claim_type"])
    if not sound(k) or r["record_id"] in bad:
        why = "; ".join(f"{name} UNSOUND: {v[k].get('reason', '')}" for name, v in fams.items() if v[k]["verdict"] != "SOUND")
        withheld.append(dict(r, held=why or "org existence rejected"))
        continue
    eid = f"EVD-{n:06d}"; n += 1
    assert eid not in used, eid
    applied.append(dict(r, evidence_id=eid, notes=r["notes"] + ("" if "agy" in fams else WAIVER)))
for x in applied:
    path = repo / "data" / f"evidence_organizations_{x['_shard']}.csv"
    assert path.exists(), path
    with open(path, "a", encoding="utf-8", newline="") as fh:
        csv.writer(fh, lineterminator="\n").writerow([x[f] for f in FIELDS])
for name, rows, extra in (("applied.csv", applied, ["_shard"]), ("withheld.csv", withheld, ["_shard", "held"])):
    with open(HERE / name, "w", encoding="utf-8", newline="") as fh:
        d = csv.DictWriter(fh, fieldnames=FIELDS + extra, lineterminator="\n", extrasaction="ignore"); d.writeheader(); d.writerows(rows)
print(f"families {sorted(fams)}; applied {len(applied)} rows ({applied[0]['evidence_id'] if applied else '-'}.."
      f"{applied[-1]['evidence_id'] if applied else '-'}) on {len({x['record_id'] for x in applied})} orgs; withheld {len(withheld)}; "
      f"{len(bad)} orgs lost existence", flush=True)
subprocess.run([sys.executable, str(HERE.parent / "evidence-tri-filings-2026-11-20" / "prune_baselines.py")], check=True, cwd=repo)

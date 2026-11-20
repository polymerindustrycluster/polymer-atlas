#!/usr/bin/env python3
"""Append the FRS-lane rows Codex judged SOUND, then shrink V-65/V-68 by the sites they evidence.

    python3 tasks/evidence-frs-sites-2026-11-20/apply.py . --start EVD-410477 review_codex_1.json review_codex_2.json

Codex alone gates this lane under the owner's waiver of 2026-11-20 ("Codex-only for now": no second review family was
available); each applied row's notes say so. The review files must cover every packet row. A site whose `existence` row
Codex rejected loses all its rows. IDs ascend from --start and must be absent tree-wide; rows go to the site's home
shard. Writes applied.csv and withheld.csv beside this script. Stdlib only.
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
codex = {}
for p in a[a.index("--start") + 2:]:
    t = (HERE / p).read_text(encoding="utf-8")
    codex.update({(v["record_id"], v["claim_type"]): v for v in json.loads(t[t.index("{"):t.rindex("}") + 1])["verdicts"]})
packet = rd(HERE / "packet_rows.csv")
missing = [(r["record_id"], r["claim_type"]) for r in packet if (r["record_id"], r["claim_type"]) not in codex]
assert not missing, f"{len(missing)} packet rows have no Codex verdict, e.g. {missing[:3]}"
bad = {r["record_id"] for r in packet if r["claim_type"] == "existence" and codex[(r["record_id"], "existence")]["verdict"] != "SOUND"}
used = {r["evidence_id"] for f in (repo / "data").glob("evidence_*.csv") for r in rd(f)}
applied, withheld, n = [], [], start
for r in packet:
    v = codex[(r["record_id"], r["claim_type"])]
    if v["verdict"] != "SOUND" or r["record_id"] in bad:
        withheld.append(dict(r, held=("codex UNSOUND: " + (v.get("reason") or "")) if v["verdict"] != "SOUND"
                             else "site existence rejected by codex"))
        continue
    eid = f"EVD-{n:06d}"; n += 1
    assert eid not in used, eid
    applied.append(dict(r, evidence_id=eid, notes=r["notes"] + WAIVER))
for x in applied:
    path = repo / "data" / f"evidence_sites_{x['_shard']}.csv"
    assert path.exists(), path
    with open(path, "a", encoding="utf-8", newline="") as fh:
        csv.writer(fh, lineterminator="\n").writerow([x[f] for f in FIELDS])
for name, rows, extra in (("applied.csv", applied, ["_shard"]), ("withheld.csv", withheld, ["_shard", "held"])):
    with open(HERE / name, "w", encoding="utf-8", newline="") as fh:
        d = csv.DictWriter(fh, fieldnames=FIELDS + extra, lineterminator="\n", extrasaction="ignore"); d.writeheader(); d.writerows(rows)
print(f"applied {len(applied)} rows ({applied[0]['evidence_id'] if applied else '-'}..{applied[-1]['evidence_id'] if applied else '-'}) "
      f"on {len({x['record_id'] for x in applied})} sites; withheld {len(withheld)} rows; {len(bad)} sites lost existence")
subprocess.run([sys.executable, str(HERE.parent / "evidence-tri-filings-2026-11-20" / "prune_baselines.py")], check=True, cwd=repo)

#!/usr/bin/env python3
"""Append the OSHA-lane rows that BOTH review families judged SOUND, then shrink V-65/V-68 by the sites they evidence.

    python3 tasks/evidence-osha-sites-2026-11-20/apply.py . --start EVD-410106 --codex c1.json c2.json c3.json --agy a1.json a2.json a3.json

Each family's files together must cover every packet row. A row applies only if both families judged it SOUND, and a
site whose `existence` row either family rejected loses all its rows (a filing that is not this site's witnesses
nothing). IDs are allocated ascending from --start and must be absent tree-wide; rows go to the site's home shard.
Writes applied.csv and withheld.csv beside this script. Stdlib only.
"""
import csv, json, re, subprocess, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
FIELDS = ["evidence_id", "record_table", "record_id", "claim_type", "claim_detail", "source_class", "source_ref",
          "observed_date", "tier_effect", "created_by", "notes"]
a = sys.argv[1:]
repo, start = Path(a[0]), int(a[a.index("--start") + 1].split("-")[1])
files = lambda flag, stop: a[a.index(flag) + 1: a.index(stop) if stop in a and a.index(stop) > a.index(flag) else len(a)]
rd = lambda p: list(csv.DictReader(open(p, encoding="utf-8", newline="")))


def verdicts(paths):
    out = {}
    for p in paths:
        t = Path(p).read_text(encoding="utf-8")
        out.update({(v["record_id"], v["claim_type"]): v for v in json.loads(t[t.index("{"):t.rindex("}") + 1])["verdicts"]})
    return out


rows = rd(HERE / "packet_rows.csv")
keys = {(r["record_id"], r["claim_type"]) for r in rows}
codex, agy = verdicts(files("--codex", "--agy")), verdicts(files("--agy", "--codex"))
# A row either family has not judged never applies: it is withheld as unreviewed (e.g. a second family out of quota).
unreviewed = {k: ", ".join(n for n, fam in (("codex", codex), ("antigravity", agy)) if k not in fam) for k in keys
              if k not in codex or k not in agy}
ok = lambda k: k not in unreviewed and codex[k]["verdict"] == "SOUND" and agy[k]["verdict"] == "SOUND"
bad_site = {rid for rid, c in keys if c == "existence" and (rid, c) not in unreviewed and not ok((rid, c))}
used = {r["evidence_id"] for f in (repo / "data").glob("evidence_*.csv") for r in rd(f)}
applied, withheld, n = [], [], start
for r in rows:
    k = (r["record_id"], r["claim_type"])
    if not ok(k) or k[0] in bad_site:
        held = (f"awaiting review by {unreviewed[k]}" if k in unreviewed else
                "existence not SOUND in both families" if k[0] in bad_site and ok(k) else "")
        v = lambda fam: f"{fam[k]['verdict']}: {fam[k].get('reason', '')}" if k in fam else ""
        withheld.append({"record_id": k[0], "claim_type": k[1], "held": held, "codex": v(codex), "antigravity": v(agy)})
        continue
    eid = f"EVD-{n:06d}"; n += 1
    assert eid not in used, eid
    applied.append({"evidence_id": eid, **{f: r[f] for f in FIELDS[1:]}, "_shard": r["_shard"]})
for x in applied:
    path = repo / "data" / f"evidence_sites_{x['_shard']}.csv"
    assert path.exists(), path
    with open(path, "a", encoding="utf-8", newline="") as fh:
        csv.writer(fh, lineterminator="\n").writerow([x[f] for f in FIELDS])
with open(HERE / "applied.csv", "w", encoding="utf-8", newline="") as fh:
    d = csv.DictWriter(fh, fieldnames=FIELDS + ["_shard"], lineterminator="\n"); d.writeheader(); d.writerows(applied)
with open(HERE / "withheld.csv", "w", encoding="utf-8", newline="") as fh:
    d = csv.DictWriter(fh, fieldnames=["record_id", "claim_type", "held", "codex", "antigravity"], lineterminator="\n")
    d.writeheader(); d.writerows(withheld)
print(f"applied {len(applied)} rows ({applied[0]['evidence_id'] if applied else '-'}..{applied[-1]['evidence_id'] if applied else '-'}) "
      f"on {len({x['record_id'] for x in applied})} sites; withheld {len(withheld)} rows ({len(bad_site)} sites lost existence)")

# Shrink-only doctrine: drop baseline entries this lane now satisfies ('amended' left alone to avoid merge conflicts).
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

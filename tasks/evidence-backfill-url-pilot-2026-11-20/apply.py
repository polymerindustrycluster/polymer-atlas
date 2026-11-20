#!/usr/bin/env python3
"""Append the pilot rows that BOTH review families judged SOUND to the evidence shards.

    python apply.py <atlas repo> <corpus dir> --start EVD-410001 [--hold-claims liveness] <review1.json> <review2.json> [re-review.json ...]

The first two review files must cover every packet row. Any further file (a re-review) vetoes the rows it covers
unless it too says SOUND. A record whose existence row any review judged UNSOUND loses every row (a wrong-entity page
witnesses nothing). --hold-claims withholds whole claim types pending an owner ruling.
IDs are allocated ascending from --start and must be absent tree-wide; rows go to the record's home-shard file.
Writes <corpus>/applied.csv (row -> evidence_id) and <corpus>/withheld.csv (row -> verdicts, hold reason).
"""
import csv, glob, json, sys
from pathlib import Path

a = sys.argv[1:]
atlas, corpus = Path(a[0]), Path(a[1])
start = int(a[a.index("--start") + 1].split("-")[1])
held_claims = set(a[a.index("--hold-claims") + 1].split(",")) if "--hold-claims" in a else set()
reviews = [p for p in a[2:] if p.endswith(".json")]
assert len(reviews) >= 2, "need at least two review files"
rd = lambda p: list(csv.DictReader(open(p, encoding="utf-8-sig", newline="")))
FIELDS = ["evidence_id", "record_table", "record_id", "claim_type", "claim_detail", "source_class", "source_ref",
          "observed_date", "tier_effect", "created_by", "notes"]


def verdicts(path):
    txt = Path(path).read_text(encoding="utf-8")
    data = json.loads(txt[txt.index("{"):txt.rindex("}") + 1])
    return {(v["record_id"], v["claim_type"]): v for v in data["verdicts"]}


rows = rd(corpus / "packet_rows.csv")
vs = [verdicts(p) for p in reviews]
keys = {(r["record_id"], r["claim_type"]) for r in rows}
for i, v in enumerate(vs[:2]):
    missing = keys - set(v)
    assert not missing, f"review {reviews[i]} has no verdict for {sorted(missing)}"  # an unreviewed row never applies
sound = lambda k: all(v[k]["verdict"] == "SOUND" for v in vs if k in v)
bad_entity = {rid for (rid, c) in keys if c == "existence" and not sound((rid, c))}
shard = {s["record_id"]: s["shard"] for s in rd(corpus / "sample.csv")}
used = {r["evidence_id"] for f in glob.glob(str(atlas / "data" / "evidence_*.csv")) for r in rd(f)}
applied, withheld, n = [], [], start
for r in rows:
    k = (r["record_id"], r["claim_type"])
    hold = ("claim type held for owner ruling" if k[1] in held_claims else
            "existence row not SOUND in every review" if k[0] in bad_entity and k[1] != "existence" else "")
    if hold or not sound(k):
        withheld.append({"record_id": k[0], "claim_type": k[1], "held": hold,
                         **{f"verdict_{Path(reviews[i]).stem}": v[k]["verdict"] + ": " + v[k]["reason"] if k in v else ""
                            for i, v in enumerate(vs)}})
        continue
    eid = f"EVD-{n:06d}"; n += 1
    assert eid not in used, eid
    applied.append({"evidence_id": eid, **{f: r[f] for f in FIELDS[1:]}, "_shard": shard[r["record_id"]]})
for x in applied:
    path = atlas / "data" / f"evidence_{x['record_table']}_{x['_shard']}.csv"
    assert path.exists(), path
    with open(path, "a", encoding="utf-8", newline="") as fh:
        csv.writer(fh, lineterminator="\n").writerow([x[f] for f in FIELDS])
for name, rs in (("applied.csv", applied), ("withheld.csv", withheld)):
    if rs:
        with open(corpus / name, "w", encoding="utf-8", newline="") as fh:
            d = csv.DictWriter(fh, fieldnames=list(rs[0]), lineterminator="\n"); d.writeheader(); d.writerows(rs)
print(f"applied {len(applied)} rows ({applied[0]['evidence_id'] if applied else '-'}..{applied[-1]['evidence_id'] if applied else '-'}) "
      f"on {len({x['record_id'] for x in applied})} records; withheld {len(withheld)} rows")

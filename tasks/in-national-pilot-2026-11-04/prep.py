"""Indiana pilot inputs: the lead-fusion STRONG clusters for IN, re-deduped against the CURRENT Atlas with
scripts/atlas.py dedupe() (name + street), split into 3 lanes. Writes into the Atlas task folder (federal leads and
Atlas ids only; public data)."""
import csv, sys
from pathlib import Path
atlas, task = Path(sys.argv[1]), Path(sys.argv[2])
sys.path.insert(0, str(atlas / "scripts"))
import atlas as A  # noqa: E402
tables = A.load_tables(str(atlas / "data"))
rows = [x for x in csv.DictReader(open(atlas / "tasks/lead-fusion-2026-11-01/clusters.csv", encoding="utf-8"))
        if x["state"] == "IN" and x["class"] == "STRONG"]
out = []
for x in rows:
    res = A.dedupe(tables, name=x["best_name"], street=x["street"], city=x["city"], state="IN", zip_=x["zip5"])
    steps = res["steps"] if isinstance(res, dict) else res
    hits = [f"step{s['step']}:{h['id']}" for s in steps if isinstance(s, dict) for h in s.get("hits", [])]
    out.append({"cluster_id": x["cluster_id"], "best_name": x["best_name"], "name_variants": x["name_variants"][:200],
                "street": x["street"], "city": x["city"], "zip5": x["zip5"], "county": x["county"],
                "naics_set": x["naics_set"], "size_band": x["size_band"], "sources_with_ids": x["sources_with_ids"],
                "eins": x["eins"], "latest_activity": x["latest_activity"], "fusion_relation": x["atlas_relation"],
                "fusion_refs": x["atlas_refs"], "current_atlas_hits": ";".join(dict.fromkeys(hits))})
for i in range(3):
    d = task / "lanes" / f"I{i + 1}"; d.mkdir(parents=True, exist_ok=True)
    with open(d / "input.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(out[0]), lineterminator="\n"); w.writeheader(); w.writerows(out[i::3])
print(len(out), "IN STRONG candidates;", sum(bool(o["current_atlas_hits"]) for o in out), "with a current Atlas dedupe hit")

"""State STRONG wave inputs: lead-fusion STRONG clusters for one state, re-deduped against the current Atlas
(scripts/atlas.py dedupe), split into N lanes, plus the lane brief (state-generalized from the Indiana pilot).

    python prep_state.py <atlas worktree> <STATE> <n_lanes>   -> tasks/<st>-strong-wave-2026-11-04/"""
import csv, sys
from pathlib import Path
atlas, st, n = Path(sys.argv[1]), sys.argv[2].upper(), int(sys.argv[3])
sys.path.insert(0, str(atlas / "scripts"))
import atlas as A  # noqa: E402
task = atlas / "tasks" / f"{st.lower()}-strong-wave-2026-11-04"
tables = A.load_tables(str(atlas / "data"))
rows = [x for x in csv.DictReader(open(atlas / "tasks/lead-fusion-2026-11-01/clusters.csv", encoding="utf-8"))
        if x["state"] == st and x["class"] == "STRONG"]
out = []
for x in rows:
    res = A.dedupe(tables, name=x["best_name"], street=x["street"], city=x["city"], state=st, zip_=x["zip5"])
    steps = res["steps"] if isinstance(res, dict) else res
    hits = [f"step{s['step']}:{h['id']}" for s in steps if isinstance(s, dict) for h in s.get("hits", [])]
    out.append({"cluster_id": x["cluster_id"], "best_name": x["best_name"], "name_variants": x["name_variants"][:200],
                "street": x["street"], "city": x["city"], "zip5": x["zip5"], "county": x["county"],
                "naics_set": x["naics_set"], "size_band": x["size_band"], "sources_with_ids": x["sources_with_ids"],
                "eins": x["eins"], "latest_activity": x["latest_activity"], "fusion_relation": x["atlas_relation"],
                "fusion_refs": x["atlas_refs"], "current_atlas_hits": ";".join(dict.fromkeys(hits))})
for i in range(n):
    d = task / "lanes" / f"L{i + 1}"; d.mkdir(parents=True, exist_ok=True)
    with open(d / "input.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(out[0]), lineterminator="\n"); w.writeheader(); w.writerows(out[i::n])
brief = (atlas / "tasks/in-national-pilot-2026-11-04/LANE_BRIEF.md").read_text(encoding="utf-8")
brief = brief.replace("national-spine pilot, Indiana", f"STRONG wave, {st}").replace("tasks/in-national-pilot-2026-11-04", task.relative_to(atlas).as_posix()).replace("Indiana", st)
(task / "LANE_BRIEF.md").write_text(brief, encoding="utf-8", newline="\n")
print(st, len(out), "STRONG candidates;", sum(bool(o["current_atlas_hits"]) for o in out), "with a current Atlas hit ->", task)

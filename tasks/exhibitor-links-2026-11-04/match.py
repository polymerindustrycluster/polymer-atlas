"""Match roster exhibitor names to Atlas organizations, using atlas.name_key on legal and trade names; exact keys only,
and a key held by two orgs is ambiguous and held.
Map each conference series to an Atlas event (EVT) by name key.
Writes <dir>/matches.csv (proposed participation rows, unminted), <dir>/leads.csv (unmatched names, discovery only)
and <dir>/event_map.csv."""
import csv, glob, re, sys
from collections import Counter, defaultdict
from pathlib import Path
atlas, d = Path(sys.argv[1]), Path(sys.argv[2])
sys.path.insert(0, str(atlas / "scripts"))
import atlas as A  # noqa: E402
rd = lambda p: list(csv.DictReader(open(p, encoding="utf-8")))
by_key = defaultdict(set)
for f in glob.glob(str(atlas / "data/organizations_*.csv")):
    for o in rd(f):
        if o["status"] not in ("active", "unknown"):
            continue
        for n in [o["legal_name"]] + (o.get("trade_names") or "").split(";"):
            k = A.name_key(n)
            if k and len(k) >= 4:
                by_key[k].add(o["org_id"])
events = rd(atlas / "data/events.csv")
ekey = {}
for e in events:
    for n in [e["name"]] + (e.get("trade_names") or "").split(";"):
        k = A.name_key(re.sub(r"\b(19|20)\d\d\b", "", n))
        if k:
            ekey[k] = e["event_id"]
names = rd(d / "names.csv")
emap, matches, leads = {}, [], []
for key in sorted({n["key"] for n in names}):
    k = A.name_key(re.sub(r"[-_]", " ", key))
    emap[key] = ekey.get(k) or next((v for kk, v in ekey.items() if kk and (kk in k or k in kk) and min(len(kk), len(k)) >= 5), "")
held = Counter()
for n in names:
    ids = by_key.get(A.name_key(n["name"]), set())
    row = {"conf_key": n["key"], "event_id": emap.get(n["key"], ""), "edition_year": n["year"], "exhibitor_name": n["name"],
           "roster_url": n["roster_url"], "org_ids": ";".join(sorted(ids))}
    if len(ids) == 1:
        matches.append(row)
    else:
        leads.append({**row, "why": "ambiguous name key" if ids else "no Atlas org by name"})
for name, rs in (("matches.csv", matches), ("leads.csv", leads), ("event_map.csv", [{"conf_key": k, "event_id": v} for k, v in emap.items()])):
    if rs:
        with open(d / name, "w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=list(rs[0]), lineterminator="\n"); w.writeheader(); w.writerows(rs)
print(f"names {len(names)}; matched to one org {len(matches)}; leads {len(leads)}; rosters mapped to an Atlas event "
      f"{sum(bool(v) for v in emap.values())}/{len(emap)}")
print("matches by roster:", Counter(m["conf_key"] for m in matches).most_common(12))

#!/usr/bin/env python3
"""ROR holds from the programs-db crosswalk (2026-11-03): look each held institution up at api.ror.org.

    python3 tasks/ror-holds-2026-11-03/find_ror.py --data-dir data   -> candidates.csv, ror_cache/

For each of the 10 holds in tasks/programs-db-crosswalk-2026-11-03/holds.csv, query ROR's search by the record's name
and keep the top five results with their status, state, domains and names, so the verdict is made from ROR's own
record. Stdlib only.
"""
import argparse, csv, json, re, urllib.parse, urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def get(url, cache):
    p = cache / (re.sub(r"[^A-Za-z0-9]+", "_", url)[-120:] + ".json")
    if not p.exists():
        with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "polymer-atlas/1.0"}), timeout=30) as r:
            p.write_bytes(r.read())
    return json.loads(p.read_text(encoding="utf-8"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data-dir", default=str(ROOT / "data"))
    data = Path(ap.parse_args().data_dir)
    eco = {r["org_id"]: r for r in csv.DictReader(open(data / "ecosystem.csv", encoding="utf-8"))}
    holds = list(csv.DictReader(open(ROOT / "tasks" / "programs-db-crosswalk-2026-11-03" / "holds.csv", encoding="utf-8")))
    cache = HERE / "ror_cache"; cache.mkdir(exist_ok=True)
    out = []
    for h in holds:
        r = eco[h["org_id"]]
        q = urllib.parse.quote(h["legal_name"])
        res = get(f"https://api.ror.org/v2/organizations?query={q}", cache).get("items", [])[:5]
        for i in res:
            g = (i.get("locations") or [{}])[0].get("geonames_details", {})
            out.append({"org_id": h["org_id"], "atlas_name": h["legal_name"], "atlas_state": r["state"],
                        "atlas_website": r["website"], "ror_id": i["id"], "status": i.get("status"),
                        "ror_state": g.get("country_subdivision_code"), "country": g.get("country_code"),
                        "domains": ";".join(i.get("domains") or []),
                        "names": ";".join(n.get("value", "") for n in i.get("names") or [])[:200],
                        "successors": ";".join(x.get("id", "") for x in i.get("relationships") or [] if x.get("type") == "successor")})
    with open(HERE / "candidates.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(out[0]), lineterminator="\n"); w.writeheader(); w.writerows(out)
    print(f"{len(holds)} holds, {len(out)} candidates")


if __name__ == "__main__":
    main()

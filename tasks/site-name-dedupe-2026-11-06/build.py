#!/usr/bin/env python3
"""Site-name dedupe sweep (leads only). Read-only on data/; writes leads.csv and counts.json next to this file.

A cluster is a set of records that share one name key (atlas.site_name_key: name_key of the name with a trailing
" - <city>" / " (<city>)" removed) where at least one record is a SITE name and the records sit under 2+ different
organizations. Members: every site_name, plus every organization / ecosystem legal_name and organization trade_name.
Same-org matches (a plant named after its own parent) are the normal case and never a cluster.
"""
import csv
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import atlas  # noqa: E402

# Keys made only of these words ("Headquarters - Houston") name a kind of place, not a company: never a cluster.
GENERIC = {"headquarters", "hq", "plant", "facility", "office", "warehouse", "distribution", "center", "site", "location",
           "branch", "campus", "manufacturing", "main", "corporate", "division", "operations", "factory", "mill", "and", "of"}

TRAILING_NOTE_RE = re.compile(r"\s*\([^()]*\)\s*$")

COLS = ["cluster_id", "name_key", "strength", "orgs_linked", "n_sites", "n_orgs", "record_ids", "names", "org_ids", "orgs",
        "streets", "why"]


def members(tables):
    """Yield (kind, record_id, org_id, name_text, key, street, city, state) for every name that can form a cluster."""
    for r in tables["sites"].rows:
        k = atlas.site_name_key(r["site_name"], r["city"])
        if k:
            yield "site", r["site_id"], r["org_id"], r["site_name"], k, r.get("street_address", ""), r["city"], r["state"]
    for r in tables["organizations"].rows:
        # trade_names carry annotations such as "(former name)" / "(federal registrant name)": drop that trailing parenthetical
        trade = [TRAILING_NOTE_RE.sub("", t) for t in atlas.tokens_semicolon(r.get("trade_names"))]
        for kind, v in [("org_legal_name", r["legal_name"])] + [("org_trade_name", t) for t in trade]:
            k = atlas.site_name_key(v, r["hq_city"])
            if k:
                yield kind, r["org_id"], r["org_id"], v, k, "", r["hq_city"], r["hq_state"]
    for r in tables.get("ecosystem", atlas.Table("ecosystem")).rows:
        k = atlas.site_name_key(r["legal_name"], r["city"])
        if k:
            yield "eco_legal_name", r["org_id"], r["org_id"], r["legal_name"], k, "", r["city"], r["state"]


def linked_components(org_ids, edges):
    """Union-find over the cluster's own orgs, joined by direct parent_org_id / successor_org_id edges."""
    parent = {o: o for o in org_ids}

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x
    for a, b in edges:
        if a in parent and b in parent:
            parent[find(a)] = find(b)
    return len({find(o) for o in org_ids})


def sweep(tables, skipped=None):
    """Return the cluster rows; keys dropped as generic are added to `skipped` (a set) so the caller can report them."""
    org_name = {}
    edges = set()
    for r in list(tables["organizations"].rows) + list(tables.get("ecosystem", atlas.Table("ecosystem")).rows):
        org_name.setdefault(r["org_id"], r["legal_name"])
    for r in tables["organizations"].rows:
        for col in ("parent_org_id", "successor_org_id"):
            if r.get(col):
                edges.add((r["org_id"], r[col]))
    by_key = defaultdict(list)
    for m in members(tables):
        by_key[m[4]].append(m)
    out = []
    for key in sorted(by_key):
        ms = sorted(set(by_key[key]), key=lambda m: (m[0] != "site", m[1], m[3]))
        orgs = sorted({m[2] for m in ms})
        if len(orgs) < 2 or not any(m[0] == "site" for m in ms):
            continue
        if set(key.split()) <= GENERIC:
            if skipped is not None:
                skipped.add(key)
            continue
        sites = [m for m in ms if m[0] == "site"]
        streets = defaultdict(set)
        for m in sites:
            sk = atlas.street_key(m[5])
            if sk:
                streets[sk].add(m[2])
        same_street = any(len(o) > 1 for o in streets.values())
        places = defaultdict(set)
        for m in ms:
            if m[6]:
                places[(atlas.squash(m[6]), m[7].upper())].add(m[2])
        same_city = any(len(o) > 1 for o in places.values())
        ncomp = linked_components(orgs, edges)
        linked = "all" if ncomp == 1 else "none" if ncomp == len(orgs) else "some"
        strength = "strong" if same_street else "medium" if same_city else "weak"
        kinds = Counter(m[0] for m in ms)
        why = (f"{len(sites)} site name(s) + {len(ms) - len(sites)} org-name(s) share key {key!r} across {len(orgs)} orgs "
               f"({', '.join(f'{n} {k}' for k, n in sorted(kinds.items()))}); "
               f"{'same street across orgs' if same_street else 'same city across orgs' if same_city else 'no shared street or city'}; "
               f"orgs linked by parent/successor: {linked}")
        clean = lambda s: (s or "").replace(";", ",")  # noqa: E731  ';' is the list separator
        out.append({"name_key": key, "strength": strength, "orgs_linked": linked, "n_sites": len(sites), "n_orgs": len(orgs),
                    "record_ids": ";".join(m[1] for m in ms), "names": ";".join(clean(m[3]) for m in ms),
                    "org_ids": ";".join(m[2] for m in ms), "orgs": ";".join(clean(org_name.get(m[2], "(org not found)")) for m in ms),
                    "streets": ";".join(clean(m[5]) or "-" for m in ms), "why": why})
    for i, r in enumerate(out, 1):
        r["cluster_id"] = f"SND-{i:04d}"
    return out


def counts(rows):
    ids = [i for r in rows for i in r["record_ids"].split(";")]
    sites = {i for i in ids if i.startswith("SITE-")}
    orgs = {o for r in rows for o in r["org_ids"].split(";")}
    site_vs_site = sum(len({o for i, o in zip(r["record_ids"].split(";"), r["org_ids"].split(";")) if i.startswith("SITE-")}) > 1
                       for r in rows)
    return {"clusters (name-key groups spanning 2+ orgs, >=1 site name)": len(rows),
            "clusters with site names under 2+ orgs (site vs site)": site_vs_site,
            "clusters whose site names sit under one org, matched by another org's name": len(rows) - site_vs_site,
            "clusters by strength": dict(Counter(r["strength"] for r in rows)),
            "clusters by orgs_linked": dict(Counter(r["orgs_linked"] for r in rows)),
            "clusters by strength x orgs_linked": dict(Counter(f"{r['strength']}/{r['orgs_linked']}" for r in rows)),
            "distinct sites in clusters": len(sites), "distinct organizations in clusters": len(orgs)}


def main():
    tables = atlas.load_tables(str(ROOT / "data"))
    skipped = set()
    rows = sweep(tables, skipped)
    with open(HERE / "leads.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=COLS, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
    c = counts(rows)
    c["generic keys dropped (would be clusters)"] = sorted(skipped)
    c["input"] = {"sites rows": len(tables["sites"].rows), "organizations rows": len(tables["organizations"].rows),
                  "ecosystem rows": len(tables["ecosystem"].rows)}
    (HERE / "counts.json").write_text(json.dumps(c, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(c, indent=2))


if __name__ == "__main__":
    main()

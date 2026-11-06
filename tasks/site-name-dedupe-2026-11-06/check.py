#!/usr/bin/env python3
"""Named check for the site-name dedupe lane. Exit 0 only if every assertion holds.

1. Known answers on the real tree: `dedupe-check --name "IFS Coatings"` finds SITE-006097 (step 5); two real clusters
   (Snyder Industries, Latham Pool Products) appear in leads.csv with the expected records.
2. Injected defects on a planted fixture: the sweep must find the planted cross-org pair (strong: same street) and the
   linked pair, and must NOT report a same-org pair, a near-miss name, or a generic "Headquarters" key.
3. leads.csv equals a fresh sweep of data/ (idempotent) and data/ has no uncommitted change.
"""
import csv
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
import build  # noqa: E402
import atlas  # noqa: E402


def table(name, rows):
    t = atlas.Table(name)
    t.rows = rows
    return t


def org(i, name, city="Akron", state="OH", **kw):
    return {"org_id": i, "legal_name": name, "trade_names": "", "hq_city": city, "hq_state": state, "parent_org_id": "",
            "successor_org_id": "", **kw}


def site(i, o, name, city, street, state="OH"):
    return {"site_id": i, "org_id": o, "site_name": name, "city": city, "state": state, "street_address": street}


def fixture_clusters():
    orgs = [org("ORG-1", "Foo Corp"), org("ORG-2", "Zed Inc", city="Canton"), org("ORG-3", "Foo Widgets LLC", city="Canton"),
            org("ORG-4", "Bar Inc"), org("ORG-5", "Baz Parent"), org("ORG-6", "Baz Child", parent_org_id="ORG-5"),
            org("ORG-7", "Qux One"), org("ORG-8", "Qux Two")]
    sites = [
        site("SITE-1", "ORG-1", "Foo Widgets - Akron", "Akron", "1 Main St"),            # planted pair, same street
        site("SITE-2", "ORG-2", "Foo Widgets (Akron)", "Akron", "1 Main Street"),
        site("SITE-3", "ORG-2", "Foo Widgets Group - Akron", "Akron", "9 Other Rd"),     # near-miss: other name, no cluster
        site("SITE-4", "ORG-4", "Bar - Akron", "Akron", "2 Elm St"),                     # same-org control: org Bar Inc
        site("SITE-5", "ORG-5", "Baz — Akron", "Akron", "3 Oak St"),                # linked orgs (parent_org_id)
        site("SITE-6", "ORG-6", "Baz - Canton", "Canton", "4 Oak St"),
        site("SITE-7", "ORG-7", "Headquarters - Akron", "Akron", "5 Pine St"),           # generic key
        site("SITE-8", "ORG-8", "Headquarters - Canton", "Canton", "6 Pine St"),
    ]
    skipped = set()
    rows = build.sweep({"sites": table("sites", sites), "organizations": table("organizations", orgs)}, skipped)
    return {r["name_key"]: r for r in rows}, skipped


def main():
    # 1. known answers on the real tree
    tables = atlas.load_tables(str(ROOT / "data"))
    hits = [h["id"] for h in atlas.dedupe(tables, name="IFS Coatings")["steps"][4]["hits"]]
    assert hits == ["SITE-006097"], hits
    leads = {r["name_key"]: r for r in csv.DictReader(open(HERE / "leads.csv", encoding="utf-8"))}
    snyder = set(leads["snyder industries"]["record_ids"].split(";"))
    assert {"SITE-005080", "ORG-004866"} <= snyder and {"ORG-003687", "ORG-004866"} <= set(leads["snyder industries"]["org_ids"].split(";"))
    assert {"ORG-002885", "ORG-000416"} <= set(leads["latham pool products"]["org_ids"].split(";"))

    # 2. injected defects
    got, skipped = fixture_clusters()
    assert set(got) == {"foo widgets", "baz"}, sorted(got)
    foo = got["foo widgets"]
    assert foo["strength"] == "strong" and foo["orgs_linked"] == "none", foo
    assert foo["record_ids"].split(";") == ["SITE-1", "SITE-2", "ORG-3"] and foo["n_orgs"] == 3, foo
    assert got["baz"]["orgs_linked"] == "all" and got["baz"]["strength"] == "weak", got["baz"]
    assert skipped == {"headquarters"}, skipped

    # 3. idempotent and read-only
    fresh = build.sweep(tables)
    on_disk = list(csv.DictReader(open(HERE / "leads.csv", encoding="utf-8")))
    assert [{k: str(v) for k, v in r.items()} for r in fresh] == on_disk, "leads.csv is stale: re-run build.py"
    assert len({r["cluster_id"] for r in on_disk}) == len(on_disk)
    dirty = subprocess.run(["git", "status", "--porcelain", "--", "data"], cwd=ROOT, capture_output=True, text=True).stdout
    assert not dirty.strip(), dirty
    print(f"OK: {len(on_disk)} clusters; known answers, injected defects, idempotence, data/ untouched")


if __name__ == "__main__":
    main()

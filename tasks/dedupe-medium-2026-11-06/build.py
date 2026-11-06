#!/usr/bin/env python3
"""Render decisions.py to the packet CSVs. Idempotent; read-only on data/. Run from anywhere.

Writes verdicts.csv, pairs.csv, operator_actions.csv, evidence.csv, frs_excerpt.csv, counts.json next to this file.
Needs the cached pages under PERSIST and the EPA ECHO exporter cache (frs.sqlite) to (re)build evidence.csv and
frs_excerpt.csv; if either is missing it keeps the committed copy and says so.
"""
import csv
import hashlib
import json
import sqlite3
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import check  # noqa: E402  (derive_verdict and path constants live there so build and check cannot drift)
import decisions as D  # noqa: E402


def write_csv(name, cols, rows):
    with open(HERE / name, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)


def tokens(s):
    return [t for t in s.split(";") if t]


def main():
    leads = check.load_leads()
    # ---- evidence.csv
    ev_rows = []
    for eid, fname, url, quote in D.EVIDENCE:
        f = check.PERSIST / fname
        if not f.exists():
            sys.exit(f"missing cached page {f}: restore persist/dedupe-medium-2026-11-06 or re-fetch {url}")
        ev_rows.append(dict(id=eid, url=url, file=fname, sha256=hashlib.sha256(f.read_bytes()).hexdigest(),
                            retrieved="2026-11-06", quote=quote))
    write_csv("evidence.csv", ["id", "url", "file", "sha256", "retrieved", "quote"], ev_rows)

    # ---- frs_excerpt.csv
    if check.FRS_DB.exists():
        db = sqlite3.connect(f"file:{check.FRS_DB}?mode=ro", uri=True)
        fr = []
        for rid in sorted(set(D.FRS_IDS)):
            rows = db.execute("select payload from records where id=?", (rid,)).fetchall()
            if len(rows) != 1:
                sys.exit(f"FRS id {rid}: {len(rows)} rows in cache (want 1)")
            p = json.loads(rows[0][0])
            fr.append(dict(registry_id=rid, fac_name=p["FAC_NAME"], fac_street=p["FAC_STREET"], fac_city=p["FAC_CITY"],
                           fac_state=p["FAC_STATE"], fac_zip=p["FAC_ZIP"]))
        write_csv("frs_excerpt.csv", ["registry_id", "fac_name", "fac_street", "fac_city", "fac_state", "fac_zip"], fr)
    else:
        print("WARNING: FRS cache absent; kept committed frs_excerpt.csv")

    # ---- pairs / actions
    pairs, actions = [], []
    for i, p in enumerate(D.PAIRS, 1):
        pairs.append(dict(pair_id=f"P{i:03d}", **p))
    for i, a in enumerate(D.ACTIONS, 1):
        actions.append(dict(action_id=f"A{i:03d}", **a))
    write_csv("pairs.csv", check.PAIR_COLS, pairs)
    write_csv("operator_actions.csv", check.ACTION_COLS, actions)

    # ---- verdicts.csv (one row per cluster, verdict derived from the org-level pairs)
    out = []
    for L in leads:
        cid = L["cluster_id"]
        cp = [p for p in pairs if p["cluster"] == cid]
        verdict, survivor, state = check.derive_verdict([p for p in cp if p["level"] == "org"])
        folds = ";".join(f"{check.folded_of(p)}>{p['survivor']}"
                         for p in cp if p["level"] == "site" and p["verdict"] == "DUPLICATE_OF" and p["state"] == "to_apply")
        acts = ";".join(f"{a['action']}:{a['record']}>{a['target']}" for a in actions if a["cluster"] == cid)
        c = D.CLUSTER[cid]
        toks = set(tokens(c["sources"]))
        for p in cp:
            toks |= set(tokens(p["sources"]))
        for a in actions:
            if a["cluster"] == cid:
                toks |= set(tokens(a["sources"]))
        lookups = f"frs={sum(t.startswith('FRS:') for t in toks)};web={sum(t.startswith('WEB:') for t in toks)}"
        out.append(dict(cluster=cid, name_key=L["name_key"], records=L["record_ids"], verdict=verdict, survivor=survivor,
                        org_state=state, deciding_or_settling_fact=c["fact"], sources=c["sources"],
                        site_folds_to_apply=folds, operator_actions=acts, lookups=lookups))
    write_csv("verdicts.csv", check.VERDICT_COLS, out)

    # ---- counts.json
    cnt = check.counts(out, pairs, actions)
    (HERE / "counts.json").write_text(json.dumps(cnt, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(cnt, indent=2))


if __name__ == "__main__":
    main()

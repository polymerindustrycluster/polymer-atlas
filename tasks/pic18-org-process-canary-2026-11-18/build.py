#!/usr/bin/env python3
"""pic18 org-process canary (2026-11-18). Idempotent. Writes pages.csv, verdicts.csv, and applies claims.csv.

claims.csv holds the proposed fills. A claim is VERIFIED only if check.validate_claims passes it; build refuses otherwise.
Writes (only when claims exist): a blank `processes` cell on the organization row and EVD-396000..396099 evidence rows.
"""
import csv, hashlib, io, json, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent; ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from shard_io import append_sorted
S = Path("/Users/johnswanson/.bb/thread-storage/thr_9i2c6byhcz/2026-11-06-atlas/persist")
CORPUS, LIVE = S / "pic18-corpus-2026-11-16", S / "pic18-org-process-canary-2026-11-18"
SEED = 20261118
FRAME = {"H": "ORG-000488 ORG-001513 ORG-001774 ORG-001986 ORG-002047".split(), "N": "ORG-000066 ORG-000107 ORG-000192 ORG-001497 ORG-001855".split()}
ORGS = [o for v in FRAME.values() for o in v]; STRATUM = {o: s for s, v in FRAME.items() for o in v}
ORG_SHARD, EVD_SHARD = "organizations_OH.csv", "evidence_organizations_OH.csv"
EVD_LO, EVD_HI = 396000, 396099
sha = lambda b: hashlib.sha256(b).hexdigest()
read = lambda p: list(csv.DictReader(open(p, newline="", encoding="utf-8")))


def stored_pages():
    """Every manifest row of the 10 orgs; sha_ok recomputes the stored file's hash (raw if kept, else the text copy)."""
    out = []
    for o in ORGS:
        for m in sorted((CORPUS / o).glob("manifest*.csv")):
            for r in read(m):
                f = CORPUS / o / Path(r["raw_file"] or r["text_file"] or "x").name if r["status"] == "ok" else None
                txt = CORPUS / o / Path(r["text_file"]).name if r["text_file"] else None
                out.append(dict(org_id=o, source="stored", manifest=m.name, url=r["url"], status=r["status"], sha256=r["sha256"],
                                sha_ok=bool(f and f.exists() and sha(f.read_bytes()) == r["sha256"]),
                                text_file=str(txt) if txt and txt.exists() else "", observed_date=r["fetched_at"][:10]))
    cache = LIVE / "cache"
    for r in json.load(open(LIVE / "live-fetches.json")):
        raw = cache / (r["sha256"] + ".raw"); txt = cache / r["text_file"]
        out.append(dict(org_id=r["org"], source="live", manifest="live-fetches.json", url=r["url"], status=r["status"], sha256=r["sha256"],
                        sha_ok=r["status"] == "ok" and raw.exists() and sha(raw.read_bytes()) == r["sha256"],
                        text_file=str(txt) if r["status"] == "ok" and txt.exists() else "", observed_date=r["fetched_at"][:10]))
    return out


def write_csv(path, rows):
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, list(rows[0]), lineterminator="\n"); w.writeheader(); w.writerows(rows)


def apply(claims, shard_dir, pages):
    """Fill blank processes cells; append evidence rows. Re-running with the same claims is a no-op."""
    by_org = {}
    for c in claims: by_org.setdefault(c["org_id"], []).append(c)
    p = shard_dir / ORG_SHARD
    rows = read(p); header = list(rows[0]); ev_path = shard_dir / EVD_SHARD
    have = {r["claim_detail"] + r["record_id"] for r in read(ev_path)}
    nid = max([EVD_LO - 1] + [int(r["evidence_id"][4:]) for r in read(ev_path) if EVD_LO <= int(r["evidence_id"][4:]) <= EVD_HI]) + 1
    new_ev = []
    for r in rows:
        cs = by_org.get(r["org_id"])
        if not cs: continue
        terms = sorted({c["term"] for c in cs})
        if r["processes"] and r["processes"] != ";".join(terms): raise SystemExit(f"{r['org_id']}: non-blank processes, refusing")
        r["processes"] = ";".join(terms)
        for c in cs:
            pg = next(x for x in pages if x["org_id"] == c["org_id"] and Path(x["text_file"]).name == c["page"])
            detail = f"processes={c['term']}; quote: {c['quote']}"
            if detail + c["org_id"] in have: continue
            new_ev.append(dict(evidence_id=f"EVD-{nid}", record_table="organizations", record_id=c["org_id"], claim_type="scope", claim_detail=detail,
                               source_class="own_site", source_ref=pg["url"], observed_date=c["observed_date"], tier_effect=c["strength"],
                               created_by="atlas-w18-orgproc", notes=f"Stored page SHA-256 {pg['sha256']}; quote: {c['quote']}. Organization row only; no site row changed."))
            nid += 1
    if new_ev:
        assert nid - 1 <= EVD_HI, "evidence block exhausted"
        append_sorted(ev_path, new_ev, "evidence_id")
    b = io.StringIO(); w = csv.DictWriter(b, header, lineterminator="\n"); w.writeheader(); w.writerows(rows)
    p.write_bytes(b.getvalue().encode("utf-8"))
    return len(new_ev)


def main():
    sys.path.insert(0, str(HERE)); import check
    pages = stored_pages(); write_csv(HERE / "pages.csv", [{**p, "text_file": Path(p["text_file"]).name if p["text_file"] else ""} for p in pages])
    claims = read(HERE / "claims.csv"); holds = {h["org_id"]: h for h in read(HERE / "holds.csv")}
    check.validate_claims(claims, pages)  # raises on any defect
    done = {c["org_id"] for c in claims}
    write_csv(HERE / "verdicts.csv", [dict(org_id=o, stratum=STRATUM[o], verdict="VERIFIED" if o in done else "STILL_UNCERTAIN",
        terms=";".join(sorted(c["term"] for c in claims if c["org_id"] == o)), hold_reason="" if o in done else holds[o]["reason"],
        settling_fact="" if o in done else holds[o]["settling_fact"]) for o in ORGS])
    n = apply(claims, ROOT / "data", pages) if claims else 0
    print(f"pages={len(pages)} claims={len(claims)} orgs_applied={len(done)} evidence_rows_added={n}")


if __name__ == "__main__":
    main()

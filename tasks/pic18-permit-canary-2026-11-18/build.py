"""Build the PIC-18 air-permit scout packet from frozen caches. Idempotent; writes only inside this folder.

  python3 build.py --regen-pool   # regenerate pool.csv from the controller's frame code at the pinned ref (needs S)
  python3 build.py                # screen.csv from caches; draws the canary only once screen.csv is frozen
"""
import csv, glob, json, math, random, re, subprocess, sys
from pathlib import Path
HERE = Path(__file__).parent; ROOT = HERE.parents[1]
S = Path("/Users/johnswanson/.bb/thread-storage/thr_9i2c6byhcz/2026-11-06-atlas"); P = S / "persist/pic18-permit-canary-2026-11-18"
REF = "832ea1b3"  # origin/main the pool and the controller frame were drawn against
ECHO_ZIP = S / "persist/oh-federal-rematch/echo.zip"; ECHO_SHA = "00b3017d9dd5c23b1bcd192c99a895df543a970fd3db210a2701b6d4ead04e1e"

def wilson(k, n):
    z = 1.959963984540054; d = 1 + z * z / n; c = (k / n + z * z / (2 * n)) / d
    h = z * math.sqrt(k / n * (1 - k / n) / n + z * z / (4 * n * n)) / d
    return [round(max(0, c - h), 4), round(min(1, c + h), 4)]

def final_permit(text, fid):
    """A final permit, not a letter: printed Facility ID, >=15,000 chars, emissions-unit terms present."""
    return fid in text and len(text) >= 15000 and bool(re.search(r"Emissions?\s+Unit", text)) and bool(re.search(r"Terms\s+and\s+Conditions", text, re.I))

def regen_pool():
    src = (S / "briefs/w1118b/draw_frames.py").read_text().replace("print(json.dumps(out, indent=1))", "")
    ns = {"__name__": "x"}; sys.argv = ["x", str(ROOT), REF, str(S)]; exec(compile(src, "draw_frames", "exec"), ns)
    sites = {}
    for f in glob.glob(str(ROOT / "data/sites_*.csv")):
        for r in csv.DictReader(open(f)): sites[r["site_id"]] = r
    import zipfile, io
    frs = {}
    for r in csv.DictReader(open(ROOT / "data/registry_links.csv")):
        if r["registry"] == "FRS": frs.setdefault(r["org_id"], []).append((r["registry_id"], r["site_id"]))
    z = zipfile.ZipFile(ECHO_ZIP); want = {i for v in frs.values() for i, _ in v}; echo = {}
    for r in csv.DictReader(io.TextIOWrapper(z.open("ECHO_EXPORTER.csv"), encoding="utf-8", errors="replace", newline="")):
        if r["REGISTRY_ID"] in want: echo[r["REGISTRY_ID"]] = r
    rows = []
    for s in ns["ppool"]:
        r = sites[s]; ids = [i for i, sid in frs[r["org_id"]] if sid in ("", s)]
        air = [(i, echo[i]["AIR_IDS"], echo[i]["CAA_PERMIT_TYPES"]) for i in ids if i in echo and echo[i]["AIR_FLAG"] == "Y"]
        rows.append({"site_id": s, "org_id": r["org_id"], "site_name": r["site_name"], "street_address": r["street_address"], "city": r["city"], "zip": r["zip"],
                     "county": r["county"], "frs_ids": ";".join(ids), "echo_air_ids": ";".join(a for _, a, _ in air), "echo_caa_permit_types": ";".join(t for _, _, t in air)})
    with open(HERE / "pool.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
    print("pool.csv", len(rows))

def pool(): return list(csv.DictReader(open(HERE / "pool.csv")))

def screen():
    hits = json.load(open(P / "ohio_epa_search_hits.json")); names = json.load(open(P / "ohio_epa_name_hits.json")) if (P / "ohio_epa_name_hits.json").exists() else {}
    J = {}
    for l in open(P / "fetch_journal_v2.jsonl"): d = json.loads(l); J[d["docid"]] = d
    out = []
    for p in pool():
        s = p["site_id"]; h = hits[s]; air = [a for a in p["echo_air_ids"].split(";") if a]
        fids = [x["fid"] for x in h["searches"]]; n_hits = sum(x.get("n") or 0 for x in h["searches"])
        docs = [d for x in h["searches"] for d in x.get("hits", [])]
        fetched = [d for d, _ in docs if d in J]
        fin = [d for d in fetched if any(final_permit(open(P / "docs" / f"{d}.txt").read(), f) for f in fids)]
        if not air: status, why = "no_air_record", "ECHO exporter AIR_FLAG is not Y for the FRS ID(s) on the Atlas record"
        elif not n_hits: status, why = "air_record_no_document_found", "ECHO air record; Ohio EPA eDocument Permit search by printed Facility ID returned 0 documents (availability signal, not absence)"
        elif not fin: status, why = "air_record_no_final_permit_in_newest_6", "documents listed but none of the newest 6 non-draft ones is a final permit with unit terms"
        else: status, why = "retrievable_permit", "final permit with printed Facility ID and emissions-unit terms stored"
        out.append({"site_id": s, "air_record": "Y" if air else "N", "echo_air_ids": p["echo_air_ids"], "edoc_documents_listed": n_hits, "docs_fetched": len(fetched),
                    "final_permit_docids": ";".join(sorted(fin)), "status": status, "reason": why})
    with open(HERE / "screen.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(out[0])); w.writeheader(); w.writerows(out)
    from collections import Counter
    print(Counter(o["status"] for o in out), "air_record", sum(o["air_record"] == "Y" for o in out))

if __name__ == "__main__":
    if "--regen-pool" in sys.argv: regen_pool()
    else: screen()

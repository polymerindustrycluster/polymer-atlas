"""Build the PIC-18 air-permit scout packet from frozen caches. Idempotent; writes only inside this folder.

  python3 build.py --regen-pool   # regenerate pool.csv from the controller's frame code at the pinned ref (needs S)
  python3 build.py                # screen.csv from caches; draws the canary only once screen.csv is frozen
"""
import csv, glob, hashlib, importlib.util, json, math, random, re, subprocess, sys
from collections import Counter
from pathlib import Path
HERE = Path(__file__).parent; ROOT = HERE.parents[1]
S = Path("/Users/johnswanson/.bb/thread-storage/thr_9i2c6byhcz/2026-11-06-atlas"); P = S / "persist/pic18-permit-canary-2026-11-18"
REF = "832ea1b3"  # origin/main the pool and the controller frame were drawn against
ECHO_ZIP = S / "persist/oh-federal-rematch/echo.zip"; ECHO_SHA = "00b3017d9dd5c23b1bcd192c99a895df543a970fd3db210a2701b6d4ead04e1e"

AS_OF = "2026-11-18"
SEED = 20261118

def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(spec); sys.modules[name] = m; spec.loader.exec_module(m); return m
_c = _load("s6common", ROOT / "tasks/source-scout-6-2026-11-06/common.py")  # existing Wilson helper
wilson = lambda k, n: [round(x, 4) for x in _c.wilson(k, n)]

def processes():
    return _load("export_vocab", ROOT / "scripts/export_vocab.py").literal_constants()["PROCESSES"]

def words(s): return re.findall(r"[a-z0-9]+", s.lower())
def in_order(quote, text):
    q = words(quote); t = words(text); n = len(q)
    return any(t[i:i + n] == q for i in range(len(t) - n + 1))

STREET = {"street": "st", "avenue": "ave", "drive": "dr", "road": "rd", "north": "n", "south": "s", "east": "e", "west": "w", "court": "ct"}
def street_key(x): return " ".join(STREET.get(w, w) for w in words(x or ""))
LEGAL = {"inc", "llc", "co", "corp", "corporation", "company", "ltd", "lp"}
def name_tokens(x): return {w for w in words(x) if w not in LEGAL}
def holder_ok(holder, names):
    h = name_tokens(holder)
    return any(n and (n <= h or h <= n) for n in (name_tokens(x) for x in names))

def header(t):
    h = {}
    for k, pat in [("facility_id", r"Facility ID:\s*(\d{10})"), ("permit_number", r"Permit Number:\s*(\S+)"), ("issue_date", r"Issue Date:\s*(\S+)"),
                   ("effective_date", r"Effective Date:\s*(\S+)"), ("expiration_date", r"Expiration Date:\s*(\S+)")]:
        m = re.search(pat, t); h[k] = m.group(1).strip() if m else ""
    L = t.split("\n"); h["holder"] = h["holder_street"] = ""
    for i, l in enumerate(L):
        if l.strip().endswith("to:") and ("issuance" in l or (i and "issuance" in L[i - 1])):
            nb = [x.strip() for x in L[i + 1:i + 8] if x.strip()][:3]; h["holder"], h["holder_street"] = nb[0], nb[1]; break
    return h

def final_permit(text, fid):
    """A final permit, not a letter or draft: printed Facility ID, a 'RE: FINAL ... PERMIT' line (drafts/proposed say DRAFT/PROPOSED),
    >=15,000 chars, emissions-unit terms present."""
    return (fid in text and len(text) >= 15000 and bool(re.search(r"RE:\s*FINAL\s+AIR", text[:4000]))
            and bool(re.search(r"Emissions?\s+Unit", text)) and bool(re.search(r"Terms\s+and\s+Conditions", text, re.I)))

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
        w = csv.DictWriter(f, fieldnames=list(rows[0]), lineterminator="\n"); w.writeheader(); w.writerows(rows)
    print("pool.csv", len(rows))

def pool(): return list(csv.DictReader(open(HERE / "pool.csv")))

def screen_rows():
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
    return out

def screen():
    out = screen_rows()
    with open(HERE / "screen.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(out[0]), lineterminator="\n"); w.writeheader(); w.writerows(out)
    print(Counter(o["status"] for o in out), "air_record", sum(o["air_record"] == "Y" for o in out))

def writecsv(name, rows):
    with open(HERE / name, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]), lineterminator="\n"); w.writeheader(); w.writerows(rows)

def pdate(t):
    import datetime
    m = re.search(r" - (\d+)/(\d+)/(\d{4}) - ", t); return datetime.date(int(m[3]), int(m[1]), int(m[2])).isoformat() if m else ""

def mdy(x):
    import datetime
    m = re.fullmatch(r"(\d+)/(\d+)/(\d{4})", x or ""); return datetime.date(int(m[3]), int(m[1]), int(m[2])).isoformat() if m else ""

def strength_of(source_part):
    """Narrative permit/unit description sentence may reach the class ceiling; a table row or heading is a list item (contract rule 5c): supports_C."""
    return "supports_A" if re.search(r"permit description|emissions-unit description|recordkeeping term", source_part) else "supports_C"

def canary():
    scr = {r["site_id"]: r for r in csv.DictReader(open(HERE / "screen.csv"))}
    ids = sorted(s for s, r in scr.items() if r["status"] == "retrievable_permit")
    draw = random.Random(SEED).sample(ids, 10)
    pl = {p["site_id"]: p for p in pool()}; V = json.load(open(HERE / "canary_verdicts.json"))["sites"]
    assert set(V) == set(draw), "verdict file does not cover the draw exactly"
    hits = json.load(open(P / "ohio_epa_search_hits.json")); J = {}
    for l in open(P / "fetch_journal_v2.jsonl"): d = json.loads(l); J[d["docid"]] = d
    orgs = {}; sites = {}
    for f in glob.glob(str(ROOT / "data/organizations_*.csv")):
        for r in csv.DictReader(open(f)): orgs[r["org_id"]] = r
    for f in glob.glob(str(ROOT / "data/sites_*.csv")):
        for r in csv.DictReader(open(f)): sites[r["site_id"]] = r
    import zipfile, io
    frs_ids = {i for p in pl.values() for i in p["frs_ids"].split(";") if i}; echo = {}
    for r in csv.DictReader(io.TextIOWrapper(zipfile.ZipFile(ECHO_ZIP).open("ECHO_EXPORTER.csv"), encoding="utf-8", errors="replace", newline="")):
        if r["REGISTRY_ID"] in frs_ids: echo[r["REGISTRY_ID"]] = r
    srows, qrows, dh = [], [], {}
    for k, s in enumerate(draw, 1):
        v = V[s]; p = pl[s]; st = sites[s]; org = orgs[p["org_id"]]; fid = p["echo_air_ids"].split(";")[0][-10:]
        docs = {d: open(P / "docs" / f"{d}.txt").read() for d in v["docs"]}
        for d in docs: dh[d] = {"url": f"https://edocpub.epa.ohio.gov/publicportal/ViewDocument.aspx?docid={d}", **{x: J[d][x] for x in ("pdf_sha256", "text_sha256", "bytes", "fetched_utc")}}
        top = header(docs[v["docs"][0]]); echo_street = next((echo[i]["FAC_STREET"] for i in p["frs_ids"].split(";") if i in echo), "")
        names = [org["legal_name"]] + [x for x in org["trade_names"].split(";") if x.strip()]
        reasons = []
        if not all(header(t)["facility_id"] == fid for t in docs.values()): reasons.append("printed Facility ID differs from the ECHO-linked ID")
        if not holder_ok(top["holder"], names): reasons.append("holder name does not match the organization legal/trade names")
        sk = street_key(top["holder_street"])
        if st["street_address"]: street_basis = "atlas_street"; ok = sk == street_key(st["street_address"])
        else: street_basis = "echo_exporter_street (Atlas site row has no street)"; ok = sk == street_key(echo_street)
        if not ok: reasons.append("permit street does not match " + street_basis)
        nondraft = sorted(pdate(t) for x in hits[s]["searches"] for _, t in x.get("hits", []) if "DRAFT" not in t and "CORRESPONDENCE" not in t)
        exps = [mdy(header(t)["expiration_date"]) for t in docs.values()]; exp = max(e for e in exps if e)
        qs = V[s]["quotes"]
        specific = any(q["term_class"] == "specific" for q in qs); anyt = any(q["term_class"] in ("specific", "unspecified") for q in qs)
        bound = not reasons
        srows.append({"canary_rank": k, "site_id": s, "org_id": p["org_id"], "record_tier": st["verification_tier"], "facility_id_printed": top["facility_id"],
                      "permits": ";".join(sorted({header(t)["permit_number"] for t in docs.values()})), "docids": ";".join(v["docs"]), "holder_printed": top["holder"],
                      "permit_street_printed": top["holder_street"], "street_basis": street_basis, "bind": "BOUND" if bound else "HELD", "bind_reasons": "; ".join(reasons),
                      "newest_doc_effective": max(mdy(header(t)["effective_date"]) for t in docs.values()), "newest_face_expiration": exp,
                      "face_expired_at_as_of": "Y" if exp < AS_OF else "N", "newest_nondraft_listed": nondraft[-1] if nondraft else "",
                      "specific_hit": "Y" if specific and bound else "N", "any_term_hit": "Y" if anyt and bound else "N",
                      "terms": ";".join(sorted({t for q in qs for t in q["terms"]})), "currency_note": v["note"]})
        for q in qs:
            h = header(docs[q["doc"]])
            strength = strength_of(q["source_part"]); tier = st["verification_tier"]
            qrows.append({"quote_id": f"CQ-{len(qrows) + 1:02d}", "site_id": s, "docid": q["doc"], "permit_number": h["permit_number"], "issue_date": mdy(h["issue_date"]),
                          "quote": q["quote"], "source_part": q["source_part"], "terms": ";".join(q["terms"]), "term_class": q["term_class"], "map_note": q["map_note"],
                          "source_class": "government_filing", "class_ceiling": "supports_A", "proposed_strength": strength,
                          "held_route": ("site_capabilities row only (tier-A/B record, C-strength term, owner ruling 2026-11-14)" if strength == "supports_C" and tier in ("A", "B") else "evidence row after owner ruling"),
                          "proposal_status": "HELD",
                          "settling_fact": "owner ruling B-PERMIT (may a regulator's emissions-unit description carry a process claim, at what strength); on a tier-A/B record a C-strength term is a site_capabilities row only"})
    writecsv("canary_sites.csv", srows); writecsv("canary_quotes.csv", qrows); json.dump(dh, open(HERE / "doc_hashes.json", "w"), indent=1, sort_keys=True)
    scr_rows = list(scr.values()); ret = sum(r["status"] == "retrievable_permit" for r in scr_rows); air = sum(r["air_record"] == "Y" for r in scr_rows)
    sp = sum(r["specific_hit"] == "Y" for r in srows); an = sum(r["any_term_hit"] == "Y" for r in srows)
    spn = len({q["site_id"] for q in qrows if q["term_class"] == "specific" and q["proposed_strength"] == "supports_A"})
    m = {"pool_sites": len(scr_rows), "unknown_process_orgs": 331, "air_record_sites": air, "retrievable_permit_sites": ret, "status_counts": dict(Counter(r["status"] for r in scr_rows)),
         "canary_draw": draw, "canary_n": 10, "bound": sum(r["bind"] == "BOUND" for r in srows), "specific_hit": sp, "specific_wilson95": wilson(sp, 10),
         "specific_hit_narrative_strength": spn, "specific_narrative_wilson95": wilson(spn, 10), "any_term_hit": an, "any_term_wilson95": wilson(an, 10), "retrievable_wilson95_of_58": wilson(ret, len(scr_rows)),
         "projected_specific_sites_of_58": round(ret * sp / 10, 1), "projected_specific_range": [round(ret * x, 1) for x in wilson(sp, 10)],
         "projected_share_of_331_pct": round(100 * ret * sp / 10 / 331, 1), "projected_share_range_pct": [round(100 * ret * x / 331, 1) for x in wilson(sp, 10)],
         "hard_ceiling_sites": len(scr_rows), "hard_ceiling_share_of_331_pct": round(100 * len(scr_rows) / 331, 1)}
    json.dump(m, open(HERE / "metrics.json", "w"), indent=1); print(json.dumps(m, indent=1))

if __name__ == "__main__":
    if "--regen-pool" in sys.argv: regen_pool()
    elif "--canary" in sys.argv: screen(); canary()
    else: screen()

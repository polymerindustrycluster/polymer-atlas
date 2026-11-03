#!/usr/bin/env python3
"""Identity crosswalk for university_college rows, from the polymer-programs-db
crosswalk (IPEDS UNITID -> ROR) verified at source (AGENTS.md section 4: a
registry identifier is recorded only after it is checked against the source
system's own record).

    python3 tasks/programs-db-crosswalk-2026-11-03/build_crosswalk.py \
        --data-dir data --hd <HD2024.csv> --ipeds-ror <polymer-programs-db/incoming/ipeds_ror.tsv> \
        --cache <dir for ROR API responses>

Outputs (this folder):
  unitid_check.csv  every held ipeds_unitid against NCES IPEDS HD2024 (name, city, state, web address)
  edits.csv         hash-checked cell edits for scripts/apply_p1_crm_scrub.py --packet-dir
  holds.csv         ROR candidates that did not verify, with the reason
  evidence_append.csv  identity evidence for the corrected record(s), EVD ids above the tree max
                    (append target: data/evidence_ecosystem.csv, the ecosystem shard at SCHEMA v1.8)

Rules
  * ROR is proposed only for institution-grain rows (no parent_institution_org_id):
    SCHEMA 4.6 keeps ror_id unique across the file, and sub-units carry the parent's
    UNITID by reference but never its ROR.
  * The crosswalk TSV is a lead. A ROR id is VERIFIED only when the live ROR record
    (api.ror.org v2) is active, located in the US, in the row's state, and agrees on
    the institution: its domain equals the row's (or IPEDS's) web domain, or one of
    its names equals the row's legal name or the IPEDS name after normalization.
  * A UNITID whose IPEDS record is a system office, or whose name/state disagree,
    is reported, never silently re-pointed. Corrections are listed in CORRECTIONS
    below with their deciding fact and land as explicit edits.
Stdlib only.
"""
import argparse, csv, hashlib, json, re, sys, time, urllib.request
from pathlib import Path

csv.field_size_limit(10 ** 9)
OUT = Path(__file__).resolve().parent
TODAY = "2026-11-03"
EDIT_COLS = ["file", "row_id", "column", "old_sha256", "new_value", "edit_class", "rationale"]

# Identity corrections decided on IPEDS HD2024 (deciding fact in the rationale).
CORRECTIONS = {
    "ORG-004656": {
        "ipeds_unitid": ("228723", "IPEDS HD2024: UNITID 228732 is 'Texas A & M University-System Office' "
                                   "(web tamus.edu); the campus that employs the record's people is 228723 "
                                   "'Texas A&M University-College Station' (web www.tamu.edu)"),
        "website": ("https://www.tamu.edu/", "tamus.edu is the Texas A&M University System's site; "
                                             "the College Station campus is www.tamu.edu (IPEDS HD2024 WEBADDR)"),
    },
}


def sha(s):
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def read(p, delim=","):
    with open(p, newline="", encoding="utf-8-sig") as fh:
        lines = [l for l in fh if not l.startswith("#")]
    return list(csv.DictReader(lines, delimiter=delim))


def norm(s):
    s = (s or "").lower().replace("&", " and ").replace("–", "-").replace("—", "-")
    s = re.sub(r"\bthe\b", " ", s)
    s = re.sub(r"[^a-z0-9]+", " ", s)
    return " ".join(s.split())


def dom(u):
    u = (u or "").strip().lower()
    u = re.sub(r"^https?://", "", u).split("/")[0]
    return u[4:] if u.startswith("www.") else u


def ror_get(rid, cache):
    key = rid.rsplit("/", 1)[-1]
    p = cache / f"{key}.json"
    if p.exists():
        return json.loads(p.read_text())
    url = f"https://api.ror.org/v2/organizations/{key}"
    for attempt in range(4):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers={"Accept": "application/json"}), timeout=30) as r:
                body = r.read()
            p.write_bytes(body)
            time.sleep(0.3)
            return json.loads(body)
        except Exception as e:  # availability signal, never evidence
            err = str(e)
            time.sleep(2 * (attempt + 1))
    return {"_error": err}


def ror_facts(rec):
    names = [n.get("value", "") for n in rec.get("names", [])]
    locs = rec.get("locations", [])
    g = locs[0].get("geonames_details", {}) if locs else {}
    return {
        "status": rec.get("status"),
        "names": names,
        "domains": [d.lower() for d in rec.get("domains", [])] + [dom(l.get("value")) for l in rec.get("links", []) if l.get("type") == "website"],
        "country": g.get("country_code"),
        "state": (g.get("country_subdivision_code") or ""),
        "city": g.get("name", ""),
        "types": rec.get("types", []),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data-dir", required=True)
    ap.add_argument("--hd", required=True)
    ap.add_argument("--ipeds-ror", required=True)
    ap.add_argument("--cache", required=True)
    a = ap.parse_args()
    data, cache = Path(a.data_dir), Path(a.cache)
    cache.mkdir(parents=True, exist_ok=True)
    hd = {r["UNITID"]: r for r in read(a.hd)}
    xw = {r["unitid"]: r for r in read(a.ipeds_ror, "\t")}
    eco = read(data / "ecosystem.csv")
    held_ror = {r["ror_id"] for r in eco if r["ror_id"]}

    # 1. every held UNITID against HD2024
    checks = []
    for r in eco:
        u = r["ipeds_unitid"]
        if not u:
            continue
        h = hd.get(u)
        row = {"org_id": r["org_id"], "legal_name": r["legal_name"], "state": r["state"], "website": r["website"],
               "ipeds_unitid": u, "parent_institution_org_id": r["parent_institution_org_id"],
               "hd_name": h["INSTNM"] if h else "", "hd_city": h["CITY"] if h else "", "hd_state": h["STABBR"] if h else "",
               "hd_web": h["WEBADDR"] if h else ""}
        issues = []
        if not h:
            issues.append("UNITID not in HD2024")
        else:
            if h["STABBR"] != r["state"]:
                issues.append("state differs")
            if "system office" in h["INSTNM"].lower() or re.search(r"\bsystem\b", h["INSTNM"].lower()):
                issues.append("IPEDS record is a system office")
            if not r["parent_institution_org_id"] and dom(h["WEBADDR"]) and dom(r["website"]) and dom(h["WEBADDR"]) != dom(r["website"]) \
                    and not dom(r["website"]).endswith("." + dom(h["WEBADDR"])):
                issues.append("web domain differs")
        if r["org_id"] in CORRECTIONS:
            issues.append("CORRECTED in this packet")
        row["issues"] = "; ".join(issues)
        checks.append(row)
    with open(OUT / "unitid_check.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(checks[0]), lineterminator="\n")
        w.writeheader(); w.writerows(checks)

    # 2. corrections as edits
    edits, holds, minted = [], [], set()
    rows = {r["org_id"]: r for r in eco}
    for oid, cols in CORRECTIONS.items():
        r = rows[oid]
        for col, (new, why) in cols.items():
            edits.append({"file": "ecosystem.csv", "row_id": oid, "column": col, "old_sha256": sha(r[col]),
                          "new_value": new, "edit_class": "IDENTITY_FIX_" + col.upper(), "rationale": why})
            r[col] = new  # downstream steps see the corrected value
        add = "https://www.tamu.edu/; NCES IPEDS HD2024 UNITID 228723 (https://nces.ed.gov/ipeds/datacenter/data/HD2024.zip, retrieved 2026-11-03)"
        edits.append({"file": "ecosystem.csv", "row_id": oid, "column": "sources", "old_sha256": sha(r["sources"]),
                      "new_value": r["sources"].rstrip() + "; " + add, "edit_class": "IDENTITY_FIX_SOURCES",
                      "rationale": "cite the campus site and the IPEDS record behind the corrected identity"})
        note = (f"IDENTITY FIX {TODAY} (programs-db crosswalk packet): UNITID 228732 and tamus.edu named the Texas A&M "
                f"University System Office, not the College Station campus whose faculty this record anchors; "
                f"re-pointed to UNITID 228723 and www.tamu.edu per IPEDS HD2024.")
        edits.append({"file": "ecosystem.csv", "row_id": oid, "column": "notes", "old_sha256": sha(r["notes"]),
                      "new_value": (r["notes"].rstrip() + " " + note).strip(), "edit_class": "IDENTITY_FIX_NOTE",
                      "rationale": "dated record of the correction"})
        r["sources"] = r["sources"].rstrip() + "; " + add
        r["notes"] = (r["notes"].rstrip() + " " + note).strip()

    # 3. ROR at institution grain
    for r in eco:
        if r["ecosystem_subtype"] != "university_college" or r["parent_institution_org_id"] or r["ror_id"] or not r["ipeds_unitid"]:
            continue
        u = r["ipeds_unitid"]
        x = xw.get(u)
        base = {"org_id": r["org_id"], "legal_name": r["legal_name"], "ipeds_unitid": u}
        if not x or not x.get("ror"):
            holds.append(base | {"ror_candidate": "", "reason": "no crosswalk candidate"}); continue
        rid = x["ror"].strip()
        if x.get("flag"):
            holds.append(base | {"ror_candidate": rid, "reason": f"crosswalk flag: {x['flag']}"}); continue
        rec = ror_get(rid, cache)
        if "_error" in rec:
            holds.append(base | {"ror_candidate": rid, "reason": "ROR fetch failed (availability, not evidence): " + rec["_error"][:80]}); continue
        f = ror_facts(rec)
        h = hd.get(u, {})
        dom_ok = bool({dom(r["website"]), dom(h.get("WEBADDR", ""))} - {""} & set(f["domains"]))
        nm = {norm(n) for n in f["names"]}
        name_ok = norm(r["legal_name"]) in nm or norm(h.get("INSTNM", "")) in nm
        state_ok = f["state"].endswith("-" + r["state"]) or f["state"] == r["state"]
        reasons = []
        if f["status"] != "active": reasons.append(f"ROR status {f['status']}")
        if f["country"] != "US": reasons.append(f"ROR country {f['country']}")
        if not state_ok: reasons.append(f"ROR state {f['state'] or '?'} vs {r['state']}")
        if not (dom_ok or name_ok): reasons.append(f"neither domain nor name agrees (ROR {f['names'][:2]}, {f['domains'][:2]})")
        full = "https://ror.org/" + rid.rsplit("/", 1)[-1]
        if full in held_ror or full in minted: reasons.append("ROR already held by another row (V-14 uniqueness)")
        if reasons:
            holds.append(base | {"ror_candidate": full, "reason": "; ".join(reasons)}); continue
        minted.add(full)
        basis = "domain" + ("+name" if name_ok else "") if dom_ok else "name"
        edits.append({"file": "ecosystem.csv", "row_id": r["org_id"], "column": "ror_id", "old_sha256": sha(""),
                      "new_value": full, "edit_class": "ROR_LINK",
                      "rationale": f"crosswalk lead verified at api.ror.org {TODAY}: active, US-{r['state']}, {basis} agree ({f['names'][0]})"})
        edits.append({"file": "ecosystem.csv", "row_id": r["org_id"], "column": "sources", "old_sha256": sha(r["sources"]),
                      "new_value": r["sources"].rstrip() + "; " + full, "edit_class": "ROR_LINK_SOURCE",
                      "rationale": "cite the ROR record behind ror_id"})
        r["sources"] = r["sources"].rstrip() + "; " + full
    # one edit per cell: a later edit to the same cell was built on the earlier new value,
    # so keep the first old hash and the last new value (TAMU gets both a fix and a ROR source)
    merged = {}
    for e in edits:
        k = (e["file"], e["row_id"], e["column"])
        if k in merged:
            merged[k] = merged[k] | {"new_value": e["new_value"], "edit_class": merged[k]["edit_class"] + "+" + e["edit_class"],
                                     "rationale": merged[k]["rationale"] + "; " + e["rationale"]}
        else:
            merged[k] = e
    edits = list(merged.values())
    with open(OUT / "edits.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=EDIT_COLS, lineterminator="\n"); w.writeheader(); w.writerows(edits)
    with open(OUT / "holds.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=["org_id", "legal_name", "ipeds_unitid", "ror_candidate", "reason"], lineterminator="\n")
        w.writeheader(); w.writerows(holds)

    # 4. identity evidence for the corrected record
    ev = [r for f in sorted(data.glob("evidence*.csv")) for r in read(f)]   # sharded at SCHEMA v1.8
    nxt = max(int(e["evidence_id"][4:]) for e in ev if re.fullmatch(r"EVD-\d+", e["evidence_id"])) + 1
    hdr = list(ev[0].keys())
    rowsev = [{"evidence_id": f"EVD-{nxt:06d}", "record_table": "ecosystem", "record_id": "ORG-004656", "claim_type": "existence",
               "claim_detail": "Texas A&M University-College Station (College Station, TX) is IPEDS UNITID 228723, web www.tamu.edu; "
                               "UNITID 228732 is the Texas A&M University System Office (tamus.edu).",
               "source_class": "registry", "source_ref": "https://nces.ed.gov/ipeds/datacenter/data/HD2024.zip",
               "observed_date": TODAY, "tier_effect": "supports_B", "created_by": "claude-code programs-db-crosswalk-2026-11-03",
               "notes": "HD2024.csv fetched 2026-11-03 from NCES; identity correction; the R2 people records anchored here are College Station faculty"}]
    with open(OUT / "evidence_append.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=hdr, lineterminator="\n"); w.writeheader(); w.writerows(rowsev)

    n_ror = sum(1 for e in edits if e["edit_class"] == "ROR_LINK")
    print(f"unitid checks {len(checks)} ({sum(1 for c in checks if c['issues'])} with issues); "
          f"edits {len(edits)} (ROR_LINK {n_ror}); holds {len(holds)}; evidence {len(rowsev)} ({rowsev[0]['evidence_id']})")


if __name__ == "__main__":
    main()

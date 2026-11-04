#!/usr/bin/env python3
"""Federal two-source frame: join the Nov-1 spine packets (ECHO/FRS, OSHA ITA,
OSHA inspections) against the CURRENT Atlas tree (fresh main, 2026-11-04).
Deterministic; no network, no LLM. Output: a ranked create-candidate queue
(multi-source first), deduped against today's sites."""
import csv, glob, os, re
from collections import Counter, defaultdict

MAIN = "/workspace/polymer-atlas"
OUT = "/tmp/frame"
os.makedirs(OUT, exist_ok=True)
T = os.path.join(MAIN, "tasks")

SUFFIX = {"INC", "LLC", "CORP", "CORPORATION", "CO", "COMPANY", "LTD", "LP", "LLP", "INC.", "THE"}
SUFFIX_RE = re.compile(r"[^A-Z0-9 ]")
STREET_SUFFIX = {"STREET": "ST", "AVENUE": "AVE", "ROAD": "RD", "DRIVE": "DR", "LANE": "LN",
                 "COURT": "CT", "BOULEVARD": "BLVD", "HIGHWAY": "HWY", "PARKWAY": "PKWY",
                 "PLACE": "PL", "TRAIL": "TRL", "CIRCLE": "CIR"}

def name_norm(n):
    n = SUFFIX_RE.sub(" ", (n or "").upper())
    toks = [t for t in n.split() if t not in SUFFIX]
    return " ".join(toks).strip()

def street_parts(s):
    s = SUFFIX_RE.sub(" ", (s or "").upper())
    toks = s.split()
    num = toks[0] if toks and toks[0].isdigit() else ""
    core = ""
    for t in toks[1 if num else 0:]:
        if t.isalpha() and len(t) > 1:
            core = STREET_SUFFIX.get(t, t)
            break
    return num, core

def zip5(z):
    d = re.sub(r"\D", "", z or "")
    return d[:5]

def keys(name, street, city, state, zp):
    nn, z = name_norm(name), zip5(zp)
    num, core = street_parts(street)
    ks = set()
    if num and core and z: ks.add(("A", state, z, num, core))
    if nn and z: ks.add(("N", nn, z))
    if nn and city and state: ks.add(("C", nn, city.upper().strip(), state))
    return ks

# ---------- Atlas sites (fresh main) ----------
site_keys = {}          # key -> (site_id, operating_status)
state_sites = Counter()
for f in glob.glob(os.path.join(MAIN, "data", "sites_*.csv")):
    for r in csv.DictReader(open(f, encoding="utf-8")):
        if r["state"]:
            state_sites[r["state"]] += 1
        for k in keys(r["site_name"], r["street_address"], r["city"], r["state"], r["zip"]):
            site_keys.setdefault(k, (r["site_id"], r["operating_status"]))
print("atlas sites loaded; states:", len(state_sites))

# ---------- Candidate extraction (NO_MATCH only) ----------
def load_matches(packet):
    return {r["registry_id"] if "registry_id" in r else r.get("establishment_id", ""): r
            for r in csv.DictReader(open(os.path.join(T, packet, "site_matches.csv"), encoding="utf-8"))}

cands = []  # dicts with source tag
# ECHO
m = {}
for r in csv.DictReader(open(os.path.join(T, "echo-frs-spine-2026-11-01", "site_matches.csv"), encoding="utf-8")):
    m[r["registry_id"]] = r
for r in csv.DictReader(open(os.path.join(T, "echo-frs-spine-2026-11-01", "facilities.csv"), encoding="utf-8")):
    v = m.get(r["registry_id"], {})
    if v.get("verdict") == "NO_MATCH":
        cands.append(dict(src="ECHO", eid=r["registry_id"], name=r["facility_name"], street=r["street"],
                          city=r["city"], state=r["state"], zip=r["zip"], county=r["county_frs"],
                          naics=r["naics_codes"], employees="", latest=r["last_activity_date"],
                          major=r["major_flag"]))
# ITA
m = {}
for r in csv.DictReader(open(os.path.join(T, "osha-ita-2026-11-01", "site_matches.csv"), encoding="utf-8")):
    m[r["establishment_id"]] = r
for r in csv.DictReader(open(os.path.join(T, "osha-ita-2026-11-01", "establishments.csv"), encoding="utf-8")):
    v = m.get(r["establishment_id"], {})
    if v.get("verdict") == "NO_MATCH":
        cands.append(dict(src="ITA", eid=r["establishment_id"], name=r["establishment_name"] or r["company_name"],
                          street=r["street"], city=r["city"], state=r["state"], zip=r["zip5"], county="",
                          naics=r["naics_code"], employees=r["annual_average_employees"], latest=r["date_submitted"],
                          major=""))
# Inspections
m = {}
for r in csv.DictReader(open(os.path.join(T, "osha-spine-2026-11-01", "site_matches.csv"), encoding="utf-8")):
    m[r.get("est_key", "")] = r
insp_verdicts = Counter(v.get("verdict", "") for v in m.values())
print("inspections site_matches verdicts:", dict(insp_verdicts))
for r in csv.DictReader(open(os.path.join(T, "osha-spine-2026-11-01", "establishments.csv"), encoding="utf-8")):
    v = m.get(r["est_key"], {})
    if v.get("verdict") in ("NO_MATCH", "") and not v.get("site_id"):
        cands.append(dict(src="INSP", eid=r["est_key"], name=r["name"], street=r["street"],
                          city=r["city"], state=r["state"], zip=r["zip"], county="",
                          naics=r["naics_latest"], employees=r["nr_in_estab_latest_valid"],
                          latest=r["latest_inspection"], major=""))
print("raw NO_MATCH candidates:", len(cands), Counter(c["src"] for c in cands))

# ---------- Re-dedupe against fresh main ----------
kept, closed_hits, rededuped = [], [], 0
for c in cands:
    c["keys"] = keys(c["name"], c["street"], c["city"], c["state"], c["zip"])
    hits = [site_keys[k] for k in c["keys"] if k in site_keys]
    live = [h for h in hits if h[1] in ("active", "unknown", "")]
    if live:
        rededuped += 1
        continue
    if hits:
        closed_hits.append(c | {"matched_closed_site": hits[0][0]})
        continue
    kept.append(c)
print(f"re-deduped vs fresh main: {rededuped} dropped; closed-site-only hits: {len(closed_hits)}; kept: {len(kept)}")

# ---------- Cross-source join (union-find on shared keys) ----------
parent = list(range(len(kept)))
def find(x):
    while parent[x] != x:
        parent[x] = parent[parent[x]]; x = parent[x]
    return x
def union(a, b):
    ra, rb = find(a), find(b)
    if ra != rb: parent[ra] = rb
key_owner = {}
for i, c in enumerate(kept):
    for k in c["keys"]:
        if k in key_owner: union(i, key_owner[k])
        else: key_owner[k] = i
groups = defaultdict(list)
for i, c in enumerate(kept):
    groups[find(i)].append(c)

CLASS_ORDER = {"A_TRIPLE": 0, "B_ECHO_ITA": 1, "B_ECHO_INSP": 2, "B_ITA_INSP": 3,
               "C_ECHO": 4, "C_ITA": 5, "C_INSP": 6}
rows = []
for g in groups.values():
    srcs = sorted({c["src"] for c in g})
    if len(srcs) == 3: cls = "A_TRIPLE"
    elif len(srcs) == 2: cls = {"ECHO+ITA": "B_ECHO_ITA", "ECHO+INSP": "B_ECHO_INSP",
                                "INSP+ITA": "B_ITA_INSP"}["+".join(srcs)]
    else: cls = "C_" + srcs[0]
    pref = next((c for c in g if c["src"] == "ECHO"), g[0])
    emp = next((c["employees"] for c in g if c["employees"]), "")
    latest = max((c["latest"] for c in g if c["latest"]), default="")
    rows.append(dict(queue_class=cls, sources="+".join(srcs),
                     name=pref["name"], street=pref["street"], city=pref["city"], state=pref["state"],
                     zip5=zip5(pref["zip"]), county=pref["county"],
                     naics=";".join(sorted({c["naics"] for c in g if c["naics"]})),
                     employees=emp, latest_activity=latest,
                     frs_id=next((c["eid"] for c in g if c["src"] == "ECHO"), ""),
                     ita_id=next((c["eid"] for c in g if c["src"] == "ITA"), ""),
                     insp_key=next((c["eid"] for c in g if c["src"] == "INSP"), ""),
                     atlas_sites_in_state=state_sites[pref["state"]]))
rows.sort(key=lambda r: (CLASS_ORDER[r["queue_class"]], r["atlas_sites_in_state"],
                         -(int(r["employees"]) if str(r["employees"]).isdigit() else 0)))

queue = [r for r in rows if r["state"] not in ("OH", "PA")]
with open(os.path.join(OUT, "QUEUE.csv"), "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=list(queue[0].keys())); w.writeheader(); w.writerows(queue)
with open(os.path.join(OUT, "closed_site_hits.csv"), "w", newline="", encoding="utf-8") as f:
    if closed_hits:
        w = csv.DictWriter(f, fieldnames=["src", "eid", "name", "street", "city", "state", "zip", "matched_closed_site"])
        w.writeheader()
        for c in closed_hits: w.writerow({k: c[k] for k in w.fieldnames})

by_state = defaultdict(Counter)
for r in rows: by_state[r["state"]][r["queue_class"]] += 1
lines = ["# Federal frame — build summary (2026-11-04)", "",
         f"Groups total: {len(rows)} (from {len(kept)} kept candidates after re-dedupe; "
         f"{rededuped} dropped as already in the Nov-3 tree; {len(closed_hits)} matched only closed sites).",
         f"Queue (excl. OH/PA): {len(queue)} groups.", "",
         "| State | Atlas sites | Triple | ECHO+ITA | ECHO+INSP | ITA+INSP | ECHO only | ITA only | INSP only |",
         "|---|---|---|---|---|---|---|---|---|"]
for st in sorted(by_state, key=lambda s: state_sites[s]):
    c = by_state[st]
    lines.append(f"| {st} | {state_sites[st]} | {c['A_TRIPLE']} | {c['B_ECHO_ITA']} | {c['B_ECHO_INSP']} | "
                 f"{c['B_ITA_INSP']} | {c['C_ECHO']} | {c['C_ITA']} | {c['C_INSP']} |")
open(os.path.join(OUT, "SUMMARY.md"), "w", encoding="utf-8").write("\n".join(lines) + "\n")
print("\n".join(lines[:12]))
print("QUEUE rows:", len(queue), "| classes:", dict(Counter(r["queue_class"] for r in queue)))

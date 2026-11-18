"""PIC-18 Ohio EPA air-permit lane (owner ruling 2026-11-18b item 1, B-PERMIT option b). Idempotent.

  python3 build.py            # stage stored permits (hash-checked), compute everything, write the packet files in this folder
  python3 build.py --apply    # also apply the planned writes to data/ (only after PR #396 merges; re-run after every merge of origin/main)

Writes only inside this folder, except --apply, which (a) unions a term into `processes` of the planned site rows in data/sites_OH.csv,
(b) appends evidence rows to data/evidence_sites_OH.csv and (c) appends capability rows to data/site_capabilities.csv, with scripts/shard_io.py.
Ids are allocated at apply time above the maximum of every other row in the tree; this lane's own rows are re-allocated the same way after a merge.
Strength, route, bind, expiry and witness position are computed here from the stored permits and the Atlas rows; verdicts.json asserts none of them.
"""
import csv, glob, importlib.util, io, json, re, shutil, subprocess, sys
from collections import Counter
from pathlib import Path
HERE = Path(__file__).resolve().parent; ROOT = HERE.parents[1]; sys.path.insert(0, str(ROOT / "scripts"))
S = Path("/Users/johnswanson/.bb/thread-storage/thr_9i2c6byhcz/2026-11-06-atlas")
CAN = S / "persist/pic18-permit-canary-2026-11-18"; LANE = S / "persist/pic18-permit-lane-2026-11-18"; CANARY = ROOT / "tasks/pic18-permit-canary-2026-11-18"
AS_OF = "2026-11-18"; WHO = "claude-code atlas-w18-permit-lane"; N_FRAME = 33
URL = "https://edocpub.epa.ohio.gov/publicportal/ViewDocument.aspx?docid="

def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(spec); sys.modules[name] = m; spec.loader.exec_module(m); return m
cb = _load("canary_build", CANARY / "build.py")   # header(), bind_registered(), final_permit(), words(), in_order(), mdy(), street_key(), city_key()
PROCESSES = set(_load("export_vocab", ROOT / "scripts/export_vocab.py").literal_constants()["PROCESSES"])
CAP_PROCESS = set(re.search(r"CAP_PROCESS = \{(.*?)\}", (ROOT / "scripts/validate.py").read_text(), re.S).group(1).replace('"', "").replace("\n", "").replace(" ", "").split(","))
# §3.1 term -> §3.6 capability term, only where the §3.6 `capability_type = process` table states the mapping (identity, rollup, "covers")
CAP_MAP = {t: t for t in CAP_PROCESS}
CAP_MAP.update({"rubber_calendering": "calendering", "compounding_extrusion": "compounding", "custom_compounding": "compounding",
                "rubber_molding_compression": "rubber_molding", "rubber_molding_transfer": "rubber_molding", "rubber_molding_injection": "rubber_molding",
                "blow_molding_extrusion": "blow_molding", "blow_molding_injection": "blow_molding", "blow_molding_stretch": "blow_molding",
                "thermoforming_vacuum": "thermoforming", "thermoforming_pressure": "thermoforming",
                **{t: "extrusion" for t in ("extrusion_film_blown", "extrusion_film_cast", "extrusion_sheet", "extrusion_profile", "extrusion_pipe_tube", "extrusion_wire_cable_coating", "foam_extrusion")},
                **{t: "injection_molding" for t in ("injection_molding_micro", "injection_molding_lsr_silicone", "insert_overmolding", "two_shot_molding")},
                "additive_manufacturing_polymer_production": "additive_manufacturing_polymer", "regrind_pelletizing": "recycling_mechanical"})
CAP_MAP.pop("composites_pultrusion", None); CAP_MAP["composites_pultrusion"] = "composites_pultrusion"
ANCILLARY = re.compile(r"\b(boilers?|generators?|storage tanks?|baghouses?|dust collectors?|paint(?:ing)?\s+(?:spray\s+)?booths?|spray\s+paint\s+booths?|hand\s+spray|clean(?:ing|up)|degreas\w*)\b", re.I)
NEAR = {"pkwy": "parkway", "rte": "route"}   # the only format variants the near-bound report tries; none is accepted as a bind

def read_csv(p): return list(csv.DictReader(open(p, newline="")))
def git(*a): return subprocess.run(["git", "-C", str(ROOT), *a], capture_output=True, text=True, check=True).stdout
def sha(p): import hashlib; return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write_csv(path, rows, fields=None):
    fields = fields or list(rows[0])
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields, lineterminator="\n", extrasaction="ignore"); w.writeheader(); w.writerows(rows)

def atlas():
    sites = {r["site_id"]: r for p in sorted(glob.glob(str(ROOT / "data/sites_*.csv"))) for r in read_csv(p)}
    orgs = {r["org_id"]: r for p in sorted(glob.glob(str(ROOT / "data/organizations_*.csv"))) for r in read_csv(p)}
    return sites, orgs

def doc_text(d): return (LANE / "docs" / f"{d}.txt").read_text()

def expiry(text):
    """(ISO date | '', guard_ok). A permit-to-install prints no expiration; a regex miss on a printed one is guard_ok False."""
    e = cb.mdy(cb.header(text)["expiration_date"])
    return e, bool(e) or not re.search(r"Expiration(?:\s+Date)?:?\s*\d", text)

def position(text, quote):
    """Structural witness class of the first non-TOC occurrence of the quote that sits in a recognised place: unit_heading | unit_paragraph | unit_table_row | permit_description | facility_description; else 'other'; '' if absent."""
    toks = [(m.group(), text.count("\n", 0, m.start())) for m in re.finditer(r"[a-z0-9]+", text.lower())]
    q = cb.words(quote); n = len(q); w = [t for t, _ in toks]; lines = text.split("\n"); found = ""
    for i in range(len(w) - n + 1):
        if w[i:i + n] != q: continue
        ln = toks[i][1]
        if "....." in lines[ln]: continue
        found = "other"
        if re.match(r"\s*\d+\.\s+([A-Z]\d{3}\b|Emissions Unit Group)", lines[ln]): return "unit_heading"
        for k in range(ln, max(-1, ln - 60), -1):
            L = lines[k]
            if re.search(r"Permit Description:", L): cls = "permit_description" if ln - k < 6 else ""
            elif re.search(r"Facility Description:", L): cls = "facility_description" if ln - k < 3 else ""
            elif re.search(r"Operations,?\s+Propert\S*\s+and/or\s+Equipment\s+Description:\s*$", L): cls = "unit_paragraph" if ln - k < 8 else ""
            elif re.match(r"\s*EU\s*ID\b", L): cls = "unit_table_row"
            else: continue
            if cls: return cls
            break
    return found

def bind_near(h, st, org, fid):
    """Strict canary bind first; if it fails only on street/city, retry with the NEAR format variants. Returns (strict_reasons, near_rule or '')."""
    r = cb.bind_registered([h], fid, st, org)
    if not r: return [], ""
    if any(x.startswith(("printed Facility", "holder")) for x in r) or "Atlas site row has no street" in r: return r, ""
    sk = " ".join(NEAR.get(x, x) for x in cb.street_key(h["holder_street"]).split()) == " ".join(NEAR.get(x, x) for x in cb.street_key(st["street_address"]).split())
    ck = re.sub(r"\b(twp|township)\b", "", cb.city_key(h["holder_city"])).strip() == cb.city_key(st["city"])
    return r, ("format variant only (street abbreviation or Twp. suffix)" if sk and ck else "")

def compute(inp):
    """Everything derived. Returns dict(frame, sites, props, viol). `viol` lists build-time inconsistencies between verdicts.json and the permits."""
    V = inp["V"]["sites"]; scr = inp["scr"]; sites, orgs = inp["sites"], inp["orgs"]; viol = []
    frame = sorted(r["site_id"] for r in scr if r["status"] == "retrievable_permit")
    if len(frame) != N_FRAME: viol.append(f"frame: {len(frame)} sites with status retrievable_permit, expected {N_FRAME}")
    if set(V) != set(frame): viol.append("verdicts.json does not cover the frame exactly")
    S_rows, P_rows = [], []
    for r in sorted(scr, key=lambda x: x["site_id"]):
        s = r["site_id"]
        if s not in V or r["status"] != "retrievable_permit": continue
        st = sites[s]; org = orgs[st["org_id"]]; tier = st["verification_tier"]; v = V[s]
        allowed = {x[-10:] for x in re.split(r"[;\s]+", r["echo_air_ids"]) if x}
        docs = r["final_permit_docids"].split(";"); hdr = {d: cb.header(inp["text"](d)) for d in docs}
        fids = {h["facility_id"] for h in hdr.values()}
        if len(fids) != 1 or not fids <= allowed: viol.append(f"{s}: printed Facility IDs {sorted(fids)} not one of the ECHO-linked {sorted(allowed)}")
        fid = sorted(fids)[0]
        newest = sorted(docs, key=lambda d: (cb.mdy(hdr[d]["issue_date"]), d), reverse=True)[0]
        strict, near = bind_near(hdr[newest], st, org, fid)
        site_bound = not strict
        n_ok = False
        for q in v["quotes"]:
            d = q["doc"]
            if d not in hdr: viol.append(f"{s}: quote document {d} is not one of the site's final permits"); continue
            text = inp["text"](d); h = hdr[d]; exp, guard = expiry(text)
            if not guard: viol.append(f"{s}/{d}: expiration printed but not parsed")
            reasons, near_d = bind_near(h, st, org, fid)
            pos = position(text, q["quote"]) if cb.in_order(q["quote"], text) else ""
            if not pos: viol.append(f"{s}/{d}: quote not found in order in the stored permit: {q['quote'][:60]}")
            expired = bool(exp) and exp < AS_OF
            unit_level = pos in ("unit_heading", "unit_paragraph", "unit_table_row")
            ceiling = "supports_A" if (pos == "unit_paragraph" and q["grade"] == "narrative" and not expired) else "supports_C"
            terms = q["terms"] or [""]
            for t in terms:
                if t and t not in PROCESSES: viol.append(f"{s}: term {t} is not in SCHEMA §3.1")
                if t and ANCILLARY.search(q["quote"]): viol.append(f"{s}: ancillary unit text mapped to {t}")
                if not t: route, why = "no_term", "ancillary or no §3.1 term"
                elif reasons: route, why = "hold", "not_bound" if not near_d else "near_bound"
                elif not unit_level: route, why = "hold", "permit_description_only"
                elif tier == "C" or ceiling in ("supports_A", "supports_B"): route, why = "processes", ""
                elif t in CAP_MAP and (s, "process", CAP_MAP[t]) in inp["caps"]: route, why = "already_held", "capability_already_held"
                elif t in CAP_MAP: route, why = "capability", ""
                else: route, why = "hold", "no_capability_destination"
                n_ok |= route in ("processes", "capability", "already_held")
                P_rows.append(dict(site_id=s, tier=tier, docid=d, permit_number=h["permit_number"], issue_date=cb.mdy(h["issue_date"]), expiry=exp or "none printed (permit-to-install)",
                                   expired=("Y" if expired else "N"), bind_doc="BOUND" if not reasons else "NOT_BOUND", position=pos, grade=q["grade"], term=t,
                                   capability_term=CAP_MAP.get(t, "") if route in ("capability", "already_held") else "", strength=ceiling if t else "", route=route, hold_reason=why,
                                   quote=q["quote"], note=q["note"]))
        if v["verdict"] == "VERIFIED" and not n_ok: viol.append(f"{s}: verdict VERIFIED but no proposal routes to processes or capability")
        if v["verdict"] != "VERIFIED" and n_ok: viol.append(f"{s}: a proposal routes to a write but the verdict is {v['verdict']}")
        if v["hold_reason"] == "not_bound" and (site_bound or near): viol.append(f"{s}: verdict says not_bound but the strict/near bind says otherwise")
        if v["hold_reason"] == "near_bound" and not near: viol.append(f"{s}: verdict says near_bound but the format-variant retry fails")
        if v["verdict"] == "VERIFIED" and not site_bound: viol.append(f"{s}: VERIFIED but the site is not strictly bound")
        S_rows.append(dict(site_id=s, org_id=st["org_id"], tier=tier, facility_id=fid, atlas_street=st["street_address"], atlas_city=st["city"], printed_holder=hdr[newest]["holder"],
                           printed_street=hdr[newest]["holder_street"], printed_city=hdr[newest]["holder_city"], strict_bind="BOUND" if site_bound else "NOT_BOUND",
                           strict_reasons="; ".join(strict), near_bound_rule=near, newest_permit=hdr[newest]["permit_number"], newest_issue=cb.mdy(hdr[newest]["issue_date"]),
                           newest_expiry=expiry(inp["text"](newest))[0] or "none printed", verdict=v["verdict"], hold_reason=v["hold_reason"] or "", note=v["note"]))
    return dict(frame=frame, sites=S_rows, props=P_rows, viol=viol)

def loaded():
    caps = {(r["site_id"], r["capability_type"], r["term"]) for r in read_csv(ROOT / "data/site_capabilities.csv") if r["created_by"] != WHO}
    return dict(V=json.load(open(HERE / "verdicts.json")), scr=read_csv(CANARY / "screen.csv"), text=doc_text, caps=caps, **dict(zip(("sites", "orgs"), atlas())))

def stage():
    """Copy the frame sites' stored permits into this lane's persist folder, hash-checked against the canary's fetch journal. No fetch runs: the canary's Facility-ID route already stored them."""
    J = {}
    for l in open(CAN / "fetch_journal_v2.jsonl"): d = json.loads(l); J[d["docid"]] = d
    out = {}
    for r in read_csv(CANARY / "screen.csv"):
        if r["status"] != "retrievable_permit": continue
        for d in r["final_permit_docids"].split(";"):
            for ext, key in (("pdf", "pdf_sha256"), ("txt", "text_sha256")):
                src = CAN / "docs" / f"{d}.{ext}"; dst = LANE / "docs" / f"{d}.{ext}"
                assert sha(src) == J[d][key], f"{d}.{ext}: sha256 differs from the fetch journal"
                if not dst.exists() or sha(dst) != J[d][key]: shutil.copy2(src, dst)
            h = cb.header((LANE / "docs" / f"{d}.txt").read_text())
            out[d] = dict(site_id=r["site_id"], url=URL + d, pdf_sha256=J[d]["pdf_sha256"], text_sha256=J[d]["text_sha256"], bytes=J[d]["bytes"], fetched_utc=J[d]["fetched_utc"],
                          permit_number=h["permit_number"], facility_id=h["facility_id"], issue_date=cb.mdy(h["issue_date"]), expiration_date=cb.mdy(h["expiration_date"]))
    json.dump(out, open(HERE / "doc_hashes.json", "w"), indent=1, sort_keys=True)
    return out

# ----------------------------------------------------------------------------------------------------------------------------- apply
def max_id(prefix, shards, col, mine=False):
    m = 0
    for p in shards:
        for r in read_csv(p):
            if mine or r["created_by"] != WHO: m = max(m, int(r[col][len(prefix):]))
    return m

def evidence_rows(props, hashes, sites, first_id):
    rows, i = [], first_id
    for p in props:
        if p["route"] != "processes": continue
        h = hashes[p["docid"]]
        note = (f"government_filing: Ohio EPA air permit {p['permit_number']}, issued {p['issue_date']}, expiry {p['expiry']}"
                + (f"; past its printed expiry on {AS_OF}, capped at supports_C" if p["expired"] == "Y" else "")
                + f"; Facility ID {h['facility_id']}; printed Facility ID, holder, street and city equal the Atlas site row; witness: {p['position'].replace('_', ' ')} "
                  f"({'a sentence stating the operation' if p['strength'] == 'supports_A' else 'a label, heading, table row or equipment list: a list item'}); "
                  f"PDF sha256 {h['pdf_sha256']}; retrieved 2026-11-18 (Ohio EPA eDocument search by the printed Facility ID), stored text re-read; term unioned into processes "
                  "(owner ruling 2026-11-18b item 1, B-PERMIT option b); a permit is a statement as of its issue date, not a status finding.")
        rows.append(dict(evidence_id=f"EVD-{i:06d}", record_table="sites", record_id=p["site_id"], claim_type="scope", claim_detail=f"processes={p['term']}; quote: {p['quote']}",
                         source_class="government_filing", source_ref=URL + p["docid"], observed_date=p["issue_date"], tier_effect=p["strength"], created_by=WHO, notes=note)); i += 1
    return rows

def capability_rows(props, hashes, sites, first_id):
    rows, i = [], first_id
    for p in props:
        if p["route"] != "capability": continue
        h = hashes[p["docid"]]
        rows.append(dict(capability_id=f"CAP-{i:06d}", site_id=p["site_id"], org_id=sites[p["site_id"]]["org_id"], capability_type="process", term=p["capability_term"], provenance="government_filing",
                         source_ref=URL + p["docid"], observed_date=p["issue_date"], withdrawn_date="", created_by=WHO,
                         notes=(f"Quote: {p['quote']}. Basis: {p['position'].replace('_', ' ')} of Ohio EPA air permit {p['permit_number']} (issued {p['issue_date']}, expiry {p['expiry']}"
                                + (f"; past its printed expiry on {AS_OF}" if p["expired"] == "Y" else "") + f"). supports_C on a tier {p['tier']} site: capability row only (owner ruling 2026-11-14); "
                                f"§3.1 term {p['term']} -> §3.6 `{p['capability_term']}`. Printed Facility ID, holder, street and city equal the Atlas site row. PDF sha256 {h['pdf_sha256']}; retrieved 2026-11-18."))); i += 1
    return rows

def apply(model, hashes):
    from shard_io import append_sorted
    SH, EV, CP = ROOT / "data/sites_OH.csv", ROOT / "data/evidence_sites_OH.csv", ROOT / "data/site_capabilities.csv"
    ev_all = [Path(p) for p in glob.glob(str(ROOT / "data/evidence_*.csv"))]
    # re-allocation: drop this lane's own rows, then append again above the maximum of every other row (idempotent; ids never fill a gap)
    for path, col in ((EV, "evidence_id"), (CP, "capability_id")):
        rows = read_csv(path); fields = list(rows[0]); keep = [r for r in rows if r["created_by"] != WHO]
        if len(keep) != len(rows): write_csv(path, keep, fields)
    sites_now = {r["site_id"]: r for r in read_csv(SH)}
    ev = evidence_rows(model["props"], hashes, sites_now, max_id("EVD-", ev_all, "evidence_id") + 1)
    cp = capability_rows(model["props"], hashes, sites_now, max_id("CAP-", [CP], "capability_id") + 1)
    if ev: append_sorted(EV, ev, "evidence_id")
    if cp: append_sorted(CP, cp, "capability_id")
    unions = {}
    for p in model["props"]:
        if p["route"] == "processes": unions.setdefault(p["site_id"], []).append(p["term"])
    rows = read_csv(SH); fields = list(rows[0])
    for r in rows:
        if r["site_id"] in unions:
            cur = [x for x in r["processes"].split(";") if x]
            r["processes"] = ";".join(cur + [t for t in dict.fromkeys(unions[r["site_id"]]) if t not in cur])
    write_csv(SH, rows, fields)
    return len(ev), len(cp), len(unions)

# ----------------------------------------------------------------------------------------------------------------------------- outputs
def metrics(model):
    P, Sr = model["props"], model["sites"]
    wr = Counter(p["route"] for p in P)
    proc_sites = sorted({p["site_id"] for p in P if p["route"] == "processes"}); cap_sites = sorted({p["site_id"] for p in P if p["route"] == "capability"})
    return {"frame_sites": len(model["frame"]), "strict_bound_sites": sum(r["strict_bind"] == "BOUND" for r in Sr), "near_bound_sites": sum(bool(r["near_bound_rule"]) for r in Sr),
            "verified_sites": sum(r["verdict"] == "VERIFIED" for r in Sr), "still_uncertain_sites": sum(r["verdict"] == "STILL_UNCERTAIN" for r in Sr), "reject_sites": sum(r["verdict"] == "REJECT" for r in Sr),
            "sites_with_process_written": len(proc_sites), "process_sites": proc_sites, "process_terms_written": wr["processes"], "capability_rows": wr["capability"], "already_held_rows": wr["already_held"], "capability_only_sites": sorted(set(cap_sites) - set(proc_sites)),
            "held_sites_by_reason": dict(Counter(r["hold_reason"] for r in Sr if r["verdict"] == "STILL_UNCERTAIN")),
            "proposal_holds_by_reason": dict(Counter(p["hold_reason"] for p in P if p["route"] == "hold")), "strength_of_writes": dict(Counter(p["strength"] for p in P if p["route"] == "processes"))}


SETTLE = {"ancillary_only": "a unit description that names a polymer process (the listed units are finishing paint booths)",
          "no_capability_destination": "tier A/B and supports_C, and the term has no §3.6 capability term: a unit narrative stating the operation (supports_A/B), or an owner ruling that adds a capability term",
          "permit_description_only": "a unit-level description that states the term (the permit-level description is not an emissions-unit description), or an owner ruling that permit descriptions count at supports_C",
          "near_bound": "owner ruling on whether USPS-standard abbreviations and a Twp. suffix bind (the printed and Atlas forms differ in format only)"}

def settle(r):
    if r["hold_reason"] == "not_bound": return "bind: " + r["strict_reasons"].replace("Atlas site row has no street", "Atlas street blank (a blank street does not bind)")
    return SETTLE.get(r["hold_reason"], "")

def readme(model, m):
    P = {}
    for p in model["props"]: P.setdefault(p["site_id"], []).append(p)
    def writes(s):
        out = []
        for p in P.get(s, []):
            if p["route"] == "processes": out.append(f"processes: `{p['term']}` ({p['strength']})")
            elif p["route"] == "capability": out.append(f"capability `{p['capability_term']}` (supports_C)")
            elif p["route"] == "already_held": out.append(f"none: capability `{p['capability_term']}` already held")
        return "; ".join(out) or "none"
    rows = []
    for r in model["sites"]:
        ps = P.get(r["site_id"], []); terms = "; ".join(sorted({p["term"] for p in ps if p["term"]})) or "none"
        rows.append(f"| {r['site_id']} | {r['tier']} | {r['strict_bind']}{' (near: format only)' if r['near_bound_rule'] else ''} | {r['newest_permit']} {r['newest_issue']} → {r['newest_expiry']} | {terms} | {writes(r['site_id'])} | "
                    f"{r['verdict']}{(': ' + r['hold_reason']) if r['hold_reason'] else ''}{('; ' + settle(r)) if r['verdict'] != 'VERIFIED' else ''}{('. ' + r['note']) if r['note'] and r['hold_reason'] == 'not_bound' else ''} |")
    outcome = (HERE / "outcome.txt").read_text() if (HERE / "outcome.txt").exists() else "_(run after the data apply)_"
    return f"""# PIC-18 Ohio EPA air-permit lane: {m['sites_with_process_written']} sites with a process written, {m['capability_rows']} capability row, {m['process_terms_written']} terms, {m['still_uncertain_sites']} sites held

Claim: atlas-w18-permit-lane, controller-assigned, 2026-11-18. Owner ruling 2026-11-18b item 1 (B-PERMIT option b, `tasks/owner-rulings-2026-11-18b/README.md`). Generated by `build.py`; checked by `check.py`.

First user: the Atlas integrator, who decides at the next wave review whether the {m['still_uncertain_sites']} held sites go to an owner battery. Non-use is a finding if that review has not taken the three rulings under "Proposed follow-ups".

## The frame

**{m['frame_sites']} PIC-18 sites (units: sites with exactly one active PIC-18 site, organization process unknown, an FRS link, status `retrievable_permit` by the Facility-ID route in the canary's `screen.csv`).** `build.py` recomputes the count from the canary's caches (`screen_rows()`, which re-reads each stored permit for the printed Facility ID) and `check.py` fails if it is not 33. The 10 canary sites are re-scored under the ruling; the other 23 are scored for the first time.

**No new fetch ran.** The canary's Facility-ID route (`fetch_permits.py`) had already stored the newest six non-draft documents for all 58 pool sites, so every document these 33 sites need was on disk. Each is copied to `persist/pic18-permit-lane-2026-11-18/docs/` and its PDF and text sha256 are checked against the canary's `fetch_journal_v2.jsonl` and `doc_hashes.json` here ({len(json.load(open(HERE / 'doc_hashes.json')))} documents). PDFs stay in controller storage because cover letters name individuals; no person's name, email or phone is in this folder (`check.py` builds the name list from the stored permits at run time and scans every task file).

## Rules applied (the ruling, plus what the lane had to decide)

- **Bind** = the canary's registered `bind_registered` (printed Facility ID; holder equals the Atlas legal or trade name; printed street and city equal the Atlas street and city; a blank Atlas street does not bind), applied **to each cited document**, not only the newest. Strictly bound: **{m['strict_bound_sites']}** of 33. **{m['near_bound_sites']}** more differ in format only (SITE-000264 `Pkwy` vs `Parkway`, SITE-001137 `Rte` vs `Route`, SITE-002113 `Newbury Twp.` vs `Newbury`); they are held, not applied, and listed for an owner ruling. No normalization is accepted.
- **Witness** = an emissions-unit description (heading, table row or the Operations/Property/Equipment Description paragraph). The permit's own `Permit Description` and `Facility Description` lines are not emissions-unit descriptions: a term witnessed only there is held (`permit_description_only`).
- **Strength**: a sentence stating the operation in a unit paragraph is the class ceiling `supports_A`; a label, heading, table row or equipment list is `supports_C` (rule 15c); a permit past its printed expiry on 2026-11-18 caps at `supports_C`. A permit-to-install prints no expiry and is not expired.
- **Route**: tier C site -> the term unions into `processes`; tier A/B and `supports_C` -> a `site_capabilities` row only (owner ruling 2026-11-14), and only for a term with a §3.6 `capability_type = process` mapping (V-30). A term with no mapping (`coating_applying`, `foam_molding_bead`, any `_unspecified`) has no destination and is held.
- **Ancillary**: boilers, generators, tanks, baghouses, dust collectors, finishing paint/spray booths and cleaning name no process (`check.py` rejects a term mapped from text matching that list). A unit counts as a coating line, not a finishing booth, only if its own text says coating line, coater, dip station or saturation line.
- **Own-operation only** (ruling 7): every quote is the holder's own permit; no maker-of-equipment statement is used.

## Outcome

| Measure (unit: frame sites) | Value |
|---|---|
| Frame | **{m['frame_sites']}** |
| Strictly bound / near-bound (format only) / not bound | **{m['strict_bound_sites']}** / **{m['near_bound_sites']}** / **{m['frame_sites'] - m['strict_bound_sites'] - m['near_bound_sites']}** |
| VERIFIED / STILL_UNCERTAIN / REJECT | **{m['verified_sites']}** / **{m['still_uncertain_sites']}** / **{m['reject_sites']}** |
| Sites with a process written to `processes` (all tier C) | **{m['sites_with_process_written']}** ({', '.join(m['process_sites'])}) |
| Process terms written / evidence rows | **{m['process_terms_written']}** / **{m['process_terms_written']}** (strength: {m['strength_of_writes']}) |
| Capability rows written (tier A/B, `supports_C`) | **{m['capability_rows']}** (sites with only a capability row: {', '.join(m['capability_only_sites']) or 'none'}) |
| Proposals already held as a capability (no write) | **{m['already_held_rows']}** |
| Held sites by reason | {m['held_sites_by_reason']} |

### Outcome check (harness `pic18_unknown.py`, process-unknown organizations)

{outcome}

## Per site

| Site | Tier | Bind (strict) | Newest permit issued → expiry | §3.1 terms proposed | Write | Verdict |
|---|---|---|---|---|---|---|
""" + "\n".join(rows) + f"""

Per quote: `proposals.csv` (document, permit number, issue and expiry dates, bind of that document, computed witness position, term, strength, route, hold reason, the verbatim quote). Per site: `sites.csv`. Documents: `doc_hashes.json` (sha256 of PDF and text, portal document id).

## Judgment calls the owner may want to review

1. **Canary flips.** Under the ruling, SITE-000664 (`laminating`) and SITE-000248 (now `composites_spray_up`, not `coating_applying`) stand; SITE-000997 (dip stations) and SITE-000814 (paint manufacture) are now held, because the only words that name the process are in the permit description, not the unit description; SITE-000601 and SITE-001530 are not written (tier A, no capability term; tier B, already held as a capability from TRI); SITE-000535, SITE-000140 and SITE-001833 stay unbound. SITE-000248's `coating_applying` is not carried: the spray-up unit is the process.
2. **Permit descriptions.** If the owner rules that a `Permit Description` line counts at `supports_C`, the permit_description_only holds become writes (3 sites; see the per-site table). Not applied.
3. **`coating_applying` has no capability term** (§3.6: applying is a trade service, not seeded), so it can never land on a tier A/B site from a `supports_C` witness.

## Self-refute (contract rule 15)

- self-refute: Grain — {len(model['props'])} proposals checked, 3 changed: SITE-000630, SITE-000814 and SITE-000997 rested on the permit's own summary line (a facility- or permit-level description), not a unit description, and are held. Every cited document is bound on its own printed Facility ID, holder, street and city (`check.py` rule BIND); a 2022 permit for SITE-000448 that prints a different (mailing) street is not cited, and its "ABS Compound Plant" line is not used; the 16 sites that do not bind carry no write.
- self-refute: Founding — 0 rows checked, 0 changed (no founding claim).
- self-refute: Strength — {len(model['props'])} proposals checked, 5 changed in drafting (`supports_A` -> `supports_C`): the unit equipment lists and one-line labels (Blair Rubber, Plymouth Foam, Mitsubishi, Huntsman, LG Chem) are list items. Only SITE-000664's laminating sentence is `supports_A`. Five of six process writes are `supports_C`.
- self-refute: Truncated quote — {len(model['props'])} proposals checked, 1 changed: SITE-000997's dip-station row never says "coating", so the term moved to the permit-description quote (held). `check.py` confirms each quote is in its stored permit, in order.
- self-refute: Attribution — {len(model['props'])} proposals checked, 0 changed: every quote is from the holder's own permit; none is from a parent, customer, equipment maker or explainer page.

## Reproduction and checks

- `python3 tasks/pic18-permit-lane-2026-11-18/build.py` stages and hash-checks the stored permits, recomputes everything and writes `sites.csv`, `proposals.csv`, `metrics.json`, `doc_hashes.json` and this README. `--apply` writes the planned rows to `data/`; ids are allocated above the maximum of every other row at apply time and re-allocated the same way after each merge of origin/main.
- Named check: `python3 tasks/pic18-permit-lane-2026-11-18/check.py`. It recomputes the frame (and recounts it from the canary's caches), every bind, expiry (and fails on a printed expiry it cannot parse), witness position, strength and route; compares the published files with the recomputed ones; audits the data diff against the merge-base (only a planned `processes` union on a planned OH site row, and new evidence or capability rows by this lane; ids above the base maximum); scans every task file for emails, phones and the names printed in the stored permits; then runs 14 injected defects and fails unless each is caught: a quote not in its document; a reordered quote; a term not in §3.1; ancillary text mapped to a process; an unbound site written (two ways); a `supports_C` term in `processes` on a tier A/B site; an expired permit at `supports_A`; a changed cell other than `processes`; a changed existing row; an evidence id not above the base maximum; a person's name; an email; a changed frame count.

## Proposed follow-ups (not in this PR)

- Owner ruling: do USPS-standard abbreviations (`Pkwy`, `Rte`) and a `Twp.` suffix bind? (3 near-bound sites.)
- Owner ruling: does a permit's `Permit Description` count as an emissions-unit description at `supports_C`? (3 held sites.)
- Owner ruling: capability terms for `coating_applying` and the `_unspecified` process terms, so a tier A/B `supports_C` witness has a destination.
- The 16 not-bound sites: 8 have a blank Atlas street; filling it from a primary source would let a later pass bind them.

Not checked: permits beyond the newest six documents per site; local-agency permits; whether any plant still runs the permitted equipment; OCR accuracy beyond the quoted words. A permit is a statement as of its issue date and never a status finding.
"""

def main():
    hashes = stage(); inp = loaded(); model = compute(inp)
    write_csv(HERE / "sites.csv", model["sites"]); write_csv(HERE / "proposals.csv", model["props"])
    m = metrics(model); json.dump(m, open(HERE / "metrics.json", "w"), indent=1)
    if not model["viol"]: (HERE / "README.md").write_text(readme(model, m))
    if model["viol"]: print("VIOLATIONS:\n" + "\n".join(model["viol"])); sys.exit(1)
    if "--apply" in sys.argv: print("applied (evidence, capability, site rows):", apply(model, hashes))
    print(json.dumps(m, indent=1))

if __name__ == "__main__": main()

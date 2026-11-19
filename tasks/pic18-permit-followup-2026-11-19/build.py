"""PIC-18 Ohio EPA air-permit lane (owner ruling 2026-11-18b item 1, B-PERMIT option b). Idempotent.

  python3 build.py            # stage stored permits (hash-checked), compute everything, write the packet files in this folder
  python3 build.py --apply    # also apply the planned writes to data/ (only after PR #396 merges; re-run after every merge of origin/main)

Writes only inside this folder, except --apply, which (a) unions a term into `processes` of the planned site rows in data/sites_OH.csv,
(b) appends evidence rows to data/evidence_sites_OH.csv and (c) appends capability rows to data/site_capabilities.csv, with scripts/shard_io.py.
Ids are allocated at apply time above the maximum of every other row in the tree; this lane's own rows are re-allocated the same way after a merge.
Strength, route, bind, expiry and witness position are computed here from the stored permits and the Atlas rows; verdicts.json asserts none of them.
"""
import csv, glob, importlib.util, json, os, re, shutil, subprocess, sys
from collections import Counter
from pathlib import Path
HERE = Path(__file__).resolve().parent; ROOT = HERE.parents[1]; sys.path.insert(0, str(ROOT / "scripts"))
S = Path("/Users/johnswanson/.bb/thread-storage/thr_9i2c6byhcz/2026-11-06-atlas")
CAN = S / "persist/pic18-permit-canary-2026-11-18"; LANE = S / "persist/pic18-permit-lane-2026-11-18"; CANARY = ROOT / "tasks/pic18-permit-canary-2026-11-18"
AS_OF = "2026-11-19"; WHO = "claude-code atlas-w18-permit-followup"; N_FRAME = 33
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
CAP_MAP.update({"compounding_unspecified": "compounding", "extrusion_unspecified": "extrusion"})   # owner ruling 2026-11-19 P4: their §3.6 parents; coating_applying and foam_molding_bead stay unmapped
ANCILLARY = re.compile(r"\b(boilers?|generators?|tanks?|baghouses?|dust collectors?|paint(?:ing)?\s+(?:spray\s+)?booths?|spray\s+paint\s+booths?|hand\s+spray|clean(?:ing|up)|degreas\w*)\b", re.I)
NEAR = {"pkwy": "parkway", "rte": "route"}   # the only format variants the near-bound report tries; none is accepted as a bind

def read_csv(p): return list(csv.DictReader(open(p, newline="")))
def git(*a): return subprocess.run(["git", "-C", str(ROOT), *a], capture_output=True, text=True, check=True).stdout
def sha(p): import hashlib; return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write_csv(path, rows, fields=None):
    fields = fields or list(rows[0])
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields, lineterminator="\n", extrasaction="ignore"); w.writeheader(); w.writerows(rows)

def read_rows_text(text):
    import io
    return list(csv.DictReader(io.StringIO(text, newline="")))

def atlas():
    sites = {r["site_id"]: r for p in sorted(glob.glob(str(ROOT / "data/sites_*.csv"))) for r in read_csv(p)}
    orgs = {r["org_id"]: r for p in sorted(glob.glob(str(ROOT / "data/organizations_*.csv"))) for r in read_csv(p)}
    return sites, orgs

def header(text):
    """The canary's header(), with the facility municipality read from the issuance block's own `City, OH` line (a PO box line may sit between street and city)."""
    h = cb.header(text); L = text.split("\n")
    for i, l in enumerate(L):
        if l.strip().endswith("to:") and ("issuance" in l or (i and "issuance" in L[i - 1])):
            for x in [y.strip() for y in L[i + 1:i + 8] if y.strip()][1:5]:
                m = re.match(r"(.+?),\s*OH\b", x)
                if m: h["holder_city"] = m.group(1).strip(); break
            break
    return h

def doc_text(d): return (LANE / "docs" / f"{d}.txt").read_text()

def expiry(text):
    """(ISO date | '', guard_ok). A permit-to-install prints no expiration; a regex miss on a printed one is guard_ok False."""
    e = cb.mdy(header(text)["expiration_date"])
    return e, bool(e) or not re.search(r"Expiration(?:\s+Date)?:?\s*\d", text)

FIELD = re.compile(r"^\s*[A-Z][A-Za-z/ ]{2,30}:(\s|$)")
def next_field(lines, k, ln):
    """True if a new labelled field ('Permit Type:', 'Issue Date:', ...) starts after line k and at or before the quote's first line: the description field has ended."""
    return any(FIELD.match(lines[j]) for j in range(k + 1, ln + 1))

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
            if re.match(r"\s*[a-z]\)\s", L): break   # a lettered term opens the terms and conditions: not a unit description
            if re.search(r"Permit Description:", L): cls = "permit_description" if ln - k < 6 and not next_field(lines, k, ln) else ""
            elif re.search(r"Facility Description:", L): cls = "facility_description" if ln - k < 3 and not next_field(lines, k, ln) else ""
            elif re.search(r"Operations,?\s+Propert\S*\s+and/or\s+Equipment\s+Description:\s*$", L): cls = "unit_paragraph" if ln - k < 8 else ""
            elif re.match(r"\s*EU\s*ID\b", L): cls = "unit_table_row"
            else: continue
            if cls: return cls
            break
    return found

def first_line(text, quote):
    toks = [(m.group(), text.count("\n", 0, m.start())) for m in re.finditer(r"[a-z0-9]+", text.lower())]
    q = cb.words(quote); n = len(q); w = [t for t, _ in toks]; lines = text.split("\n")
    return next((toks[i][1] for i in range(len(w) - n + 1) if w[i:i + n] == q and "....." not in lines[toks[i][1]]), None)

def is_ancillary(text, quote, pos):
    """Ancillary by the unit, not by one word in a mixed equipment list: the unit's heading title and the quote's own head clause (the whole quote if it is a heading)."""
    head = quote if pos == "unit_heading" else re.split(r"[,:.]|\s-\s|\bconsisting\b|\bincluding\b", quote)[0]
    ln = first_line(text, quote); title = ""; L = text.split("\n")
    for k in range(ln if ln is not None else 0, max(-1, (ln or 0) - 15), -1):
        m = re.match(r"\s*\d+\.\s+[A-Z]\d{3},?\s*(.*)", L[k])
        if m: title = m.group(1); break
    return bool(ANCILLARY.search(head) or ANCILLARY.search(title))

def twp_suffix_off(city_key_):
    """P2: a trailing 'Twp.'/'Township' on either side is a suffix difference; a leading one is not."""
    return re.sub(r"\s+(twp|township)$", "", city_key_)

def bind_near(h, st, org, fid):
    """Strict canary bind first; if it fails only on street/city, retry with the NEAR format variants. Returns (strict_reasons, near_rule or '')."""
    r = cb.bind_registered([h], fid, st, org)
    if not r: return [], ""
    if any(x.startswith(("printed Facility", "holder")) for x in r) or "Atlas site row has no street" in r: return r, ""
    sk = " ".join(NEAR.get(x, x) for x in cb.street_key(h["holder_street"]).split()) == " ".join(NEAR.get(x, x) for x in cb.street_key(st["street_address"]).split())
    ck = twp_suffix_off(cb.city_key(h["holder_city"])) == twp_suffix_off(cb.city_key(st["city"]))
    return r, ("format variant only (street abbreviation or Twp. suffix)" if sk and ck else "")

HELD = "owner_ruled_not_carried"   # owner ruling 2026-11-19 P1: SITE-000248 keeps composites_spray_up only
def held_pairs(props):
    """(site, term) pairs held for an owner ruling by ANY proposal: the hold binds the pair, not the row that carries the flag."""
    return {(p["site_id"], p["term"]) for p in props if p["hold_reason"] == HELD}

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
        docs = r["final_permit_docids"].split(";"); hdr = {d: header(inp["text"](d)) for d in docs}
        fids = {h["facility_id"] for h in hdr.values()}
        if len(fids) != 1 or not fids <= allowed: viol.append(f"{s}: printed Facility IDs {sorted(fids)} not one of the ECHO-linked {sorted(allowed)}")
        fid = sorted(fids)[0]
        newest = sorted(docs, key=lambda d: (cb.mdy(hdr[d]["issue_date"]), d), reverse=True)[0]
        strict, near = bind_near(hdr[newest], st, org, fid)
        site_bound = (not strict) or bool(near)   # owner ruling 2026-11-19 P2: a format variant (USPS abbreviation, Twp.) does not break the bind
        n_ok = False; capseen = set()
        for q in v["quotes"]:
            d = q["doc"]
            if d not in hdr: viol.append(f"{s}: quote document {d} is not one of the site's final permits"); continue
            text = inp["text"](d); h = hdr[d]; exp, guard = expiry(text)
            if not guard: viol.append(f"{s}/{d}: expiration printed but not parsed")
            reasons, near_d = bind_near(h, st, org, fid); bound_doc = (not reasons) or bool(near_d)
            pos = position(text, q["quote"]) if cb.in_order(q["quote"], text) else ""
            if not pos: viol.append(f"{s}/{d}: quote not found in order in the stored permit: {q['quote'][:60]}")
            expired = bool(exp) and exp < AS_OF
            unit_level = pos in ("unit_heading", "unit_paragraph", "unit_table_row")
            ceiling = "supports_A" if (pos == "unit_paragraph" and q["grade"] == "narrative" and not expired) else "supports_C"
            terms = q["terms"] or [""]
            for t in terms:
                if t and t not in PROCESSES: viol.append(f"{s}: term {t} is not in SCHEMA §3.1")
                if t and is_ancillary(text, q["quote"], pos): viol.append(f"{s}: ancillary unit text mapped to {t}")
                if not t: route, why = "no_term", "ancillary or no §3.1 term"
                elif q.get("hold"): route, why = "hold", q["hold"]
                elif not bound_doc: route, why = "hold", "not_bound"
                elif pos == "facility_description": route, why = "hold", "facility_description_not_covered"
                elif not (unit_level or pos == "permit_description"): route, why = "hold", "not_a_unit_or_permit_description"
                elif tier == "C" or ceiling in ("supports_A", "supports_B"):
                    route, why = ("already_held", "applied_earlier") if (s, t) in inp["ev_keys"] else ("processes", "")
                elif t in CAP_MAP and (s, "process", CAP_MAP[t]) in inp["caps"]: route, why = "already_held", "capability_already_held"
                elif t in CAP_MAP and (s, CAP_MAP[t]) in capseen: route, why = "already_held", "capability_in_plan"
                elif t in CAP_MAP: route, why = "capability", ""; capseen.add((s, CAP_MAP[t]))
                else: route, why = "hold", "no_capability_destination"
                n_ok |= route in ("processes", "capability", "already_held")
                P_rows.append(dict(site_id=s, tier=tier, docid=d, permit_number=h["permit_number"], issue_date=cb.mdy(h["issue_date"]), expiry=exp or "none printed (permit-to-install)",
                                   expired=("Y" if expired else "N"), bind_doc="BOUND" if bound_doc else "NOT_BOUND", position=pos, grade=q["grade"], term=t,
                                   capability_term=CAP_MAP.get(t, "") if route in ("capability", "already_held") else "", strength=ceiling if t else "", route=route, hold_reason=why,
                                   quote=q["quote"], note=q["note"]))
        if v["verdict"] == "VERIFIED" and not n_ok: viol.append(f"{s}: verdict VERIFIED but no proposal routes to processes or capability")
        if v["verdict"] != "VERIFIED" and n_ok: viol.append(f"{s}: a proposal routes to a write but the verdict is {v['verdict']}")
        if v["hold_reason"] == "not_bound" and site_bound: viol.append(f"{s}: verdict says not_bound but the bind (P2) says bound")
        if v["verdict"] == "VERIFIED" and not site_bound: viol.append(f"{s}: VERIFIED but the site is not bound")
        S_rows.append(dict(site_id=s, org_id=st["org_id"], tier=tier, facility_id=fid, atlas_street=st["street_address"], atlas_city=st["city"], printed_holder=hdr[newest]["holder"],
                           printed_street=hdr[newest]["holder_street"], printed_city=hdr[newest]["holder_city"], strict_bind="BOUND" if not strict else "NOT_BOUND", bind="BOUND" if site_bound else "NOT_BOUND",
                           strict_reasons="; ".join(strict), near_bound_rule=near, newest_permit=hdr[newest]["permit_number"], newest_issue=cb.mdy(hdr[newest]["issue_date"]),
                           newest_expiry=expiry(inp["text"](newest))[0] or "none printed", verdict=v["verdict"], hold_reason=v["hold_reason"] or "", note=v["note"]))
    hp = held_pairs(P_rows)
    for p in P_rows:   # enforce the hold on the (site, term) pair across every proposal, whichever quote supplies it
        if (p["site_id"], p["term"]) in hp and p["route"] != "hold": p["route"], p["hold_reason"], p["capability_term"] = "hold", HELD, ""
    return dict(frame=frame, sites=S_rows, props=P_rows, viol=viol)

def loaded():
    caps = {(r["site_id"], r["capability_type"], r["term"]) for r in read_csv(ROOT / "data/site_capabilities.csv") if r["created_by"] != WHO}
    ev_keys = {(r["record_id"], r["claim_detail"].split("=", 1)[1].split(";")[0]) for p in glob.glob(str(ROOT / "data/evidence_sites_*.csv")) for r in read_csv(p)
               if r["created_by"] != WHO and r["claim_type"] == "scope" and r["claim_detail"].startswith("processes=")}
    return dict(V=json.load(open(HERE / "verdicts.json")), scr=read_csv(CANARY / "screen.csv"), text=doc_text, caps=caps, ev_keys=ev_keys, **dict(zip(("sites", "orgs"), atlas())))

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
            h = header((LANE / "docs" / f"{d}.txt").read_text())
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
                + f"; Facility ID {header(doc_text(p['docid']))['facility_id']}; printed Facility ID, holder, street and city equal the Atlas site row; witness: {p['position'].replace('_', ' ')} "
                  f"({'a sentence stating the operation' if p['strength'] == 'supports_A' else 'the permit description field, a permit-level summary: supports_C only, owner ruling 2026-11-19 P3' if p['position'] == 'permit_description' else 'a label, heading, table row or equipment list: a list item'}); "
                  f"PDF sha256 {h['pdf_sha256']}; retrieved 2026-11-18 by the canary (Ohio EPA eDocument search by the printed Facility ID), stored text re-read; term unioned into processes "
                  "(owner ruling 2026-11-18b item 1, B-PERMIT option b; follow-up rulings 2026-11-19 P2-P4); a permit is a statement as of its issue date, not a status finding.")
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

def stage_shard(live, rows, fields, key=None, new=()):
    """Write the complete new content of a live shard next to it and verify it. Returns the stage path; the live file is untouched."""
    live = Path(live); stage = live.with_name(live.name + ".stage")
    try:
        write_csv(stage, rows, fields)
        if key and new:
            from shard_io import append_sorted
            append_sorted(stage, list(new), key)
        got = read_csv(stage)
        assert len(got) == len(rows) + len(new), f"{live.name}: staged {len(got)} rows, expected {len(rows) + len(new)}"
        if key: ids = [r[key] for r in got]; assert ids == sorted(ids) and len(set(ids)) == len(ids), f"{live.name}: staged ids not unique and ascending"
        with open(stage, "rb") as f: os.fsync(f.fileno())
    except BaseException:
        stage.unlink(missing_ok=True); raise
    return stage

def apply(model, hashes, root=ROOT, base=None):
    """Plan every write in memory, verify it against the live files (and the merge-base rows when given), then replace each shard atomically."""
    hp = held_pairs(model["props"])
    assert not [p for p in model["props"] if (p["site_id"], p["term"]) in hp and p["route"] != "hold"], "a (site, term) pair held for an owner ruling is planned as a write"
    SH, EV, CP = root / "data/sites_OH.csv", root / "data/evidence_sites_OH.csv", root / "data/site_capabilities.csv"
    ev_all = [Path(p) for p in glob.glob(str(root / "data/evidence_*.csv"))]
    cur = {p: read_csv(p) for p in (SH, EV, CP)}; fields = {p: list(cur[p][0]) for p in cur}
    sites_now = {r["site_id"]: r for r in cur[SH]}
    keep = {p: [r for r in cur[p] if r["created_by"] != WHO] for p in (EV, CP)}   # re-allocation: this lane's own rows go, then return above every other id
    ev = evidence_rows(model["props"], hashes, sites_now, max_id("EVD-", ev_all, "evidence_id") + 1)
    cp = capability_rows(model["props"], hashes, sites_now, max_id("CAP-", [CP], "capability_id") + 1)
    unions = {}
    for p in model["props"]:
        if p["route"] == "processes": unions.setdefault(p["site_id"], []).append(p["term"])
    new_sites = []
    for r in cur[SH]:
        r = dict(r)
        if r["site_id"] in unions:
            have = [x for x in r["processes"].split(";") if x]
            r["processes"] = ";".join(have + [t for t in dict.fromkeys(unions[r["site_id"]]) if t not in have])
        new_sites.append(r)
    if base:   # every merge-base row survives; a site row may differ from its base row only by that site's own planned union
        for p, key in ((SH, "site_id"), (EV, "evidence_id"), (CP, "capability_id")):
            after = {r[key]: r for r in (new_sites if p == SH else keep[p] + (ev if p == EV else cp))}
            for r in base[p]:
                assert r[key] in after, f"{p.name}: base row {r[key]} would be lost"
                want = dict(r)
                if p == SH and r["site_id"] in unions:
                    have = [x for x in r["processes"].split(";") if x]; want["processes"] = ";".join(have + [t for t in dict.fromkeys(unions[r["site_id"]]) if t not in have])
                assert after[r[key]] == want, f"{p.name}: row {r[key]} differs from its base row by more than its planned change"
    stages = {}
    try:
        stages[EV] = stage_shard(EV, keep[EV], fields[EV], "evidence_id", ev)
        stages[CP] = stage_shard(CP, keep[CP], fields[CP], "capability_id", cp)
        stages[SH] = stage_shard(SH, new_sites, fields[SH])
        for live in (EV, CP, SH): os.replace(stages[live], live); stages.pop(live)   # evidence first: no cell is ever published without its rows
    finally:
        for s in stages.values(): s.unlink(missing_ok=True)
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


SETTLE = {"ancillary_only": "a unit description that names a polymer process (the listed units are finishing booths or wood)",
          "no_capability_destination": "tier A/B and supports_C, and the term has no §3.6 capability term: a unit narrative stating the operation (supports_A/B), or an owner ruling that adds a capability term",
          "term_not_stated": "a source that states spray-up or hand lay-up (or an owner ruling adding a composites _unspecified term)"}

def settle(r):
    if r["hold_reason"] == "not_bound": return "bind: " + r["strict_reasons"].replace("Atlas site row has no street", "Atlas street blank (a blank street does not bind)")
    return SETTLE.get(r["hold_reason"], "")

def readme(model, m):
    EXPECTED_DEFECTS = int(re.search(r"EXPECTED_DEFECTS = (\d+)", (HERE / "check.py").read_text()).group(1))
    P = {}
    for p in model["props"]: P.setdefault(p["site_id"], []).append(p)
    def writes(s):
        out = []
        for p in P.get(s, []):
            if p["route"] == "processes": out.append(f"**new** processes: `{p['term']}` ({p['strength']})")
            elif p["route"] == "capability": out.append(f"**new** capability `{p['capability_term']}` (supports_C)")
            elif p["route"] == "already_held": out.append(f"none (already held: `{p['term']}`)")
        return "; ".join(dict.fromkeys(out)) or "none"
    def cited(r):
        ps = sorted({(p["permit_number"], p["issue_date"], p["expiry"]) for p in P.get(r["site_id"], []) if p["term"]})
        return "; ".join(f"{a} {b} → {c.replace(' (permit-to-install)', '')}" for a, b, c in ps) if ps else f"(none cited; newest {r['newest_permit']} {r['newest_issue']} → {r['newest_expiry']})"
    changed = {"SITE-000264", "SITE-001137", "SITE-002113", "SITE-000814", "SITE-000601", "SITE-001530", "SITE-001888", "SITE-002124"}
    rows = []
    for r in model["sites"]:
        mark = " (P2)" if r["bind"] == "BOUND" and r["strict_bind"] != "BOUND" else ""
        terms = "; ".join(sorted({p["term"] for p in P.get(r["site_id"], []) if p["term"]})) or "none"
        rows.append(f"| {r['site_id']}{' *' if r['site_id'] in changed else ''} | {r['tier']} | {r['bind']}{mark} | {cited(r)} | {terms} | {writes(r['site_id'])} | "
                    f"{r['verdict']}{(': ' + r['hold_reason']) if r['hold_reason'] else ''}{('; ' + settle(r)) if r['verdict'] != 'VERIFIED' else ''}{('. ' + r['note']) if r['note'] and r['hold_reason'] in ('not_bound', 'term_not_stated', 'ancillary_only') else ''} |")
    pd = [p for p in model["props"] if p["position"] == "permit_description" and p["route"] in ("capability", "processes")]
    pd_n, pd_p = len(pd), sum(p["route"] == "processes" for p in pd)
    pd_list = ", ".join(f"{p['site_id']} `{p['capability_term'] or p['term']}` ({'processes' if p['route'] == 'processes' else 'capability'})" for p in pd)
    outcome = (HERE / "outcome.txt").read_text() if (HERE / "outcome.txt").exists() else "_(run after the data apply)_"
    return f"""# PIC-18 air-permit follow-up (owner rulings 2026-11-19 P2-P4): {m['sites_with_process_written']} sites with a process written, {m['capability_rows']} capability rows

Claim: atlas-w18-permit-lane, controller-assigned, 2026-11-19; new lane task on PR #400's tooling. Rulings: `tasks/owner-rulings-2026-11-19/README.md` P2, P3, P4 (P1 settled: SITE-000248 keeps `composites_spray_up` only; nothing changes there; E1: ids from one above main's maximum). Generated by `build.py`; checked by `check.py`.

First user: the Atlas integrator, who decides at the next wave review whether the {m['still_uncertain_sites']} sites still held go to an owner battery. Non-use is a finding if that review has not taken the follow-ups below.

## What the three rulings change (rows marked * in the table are the re-scored ones)

- **P2 (binding):** a USPS-standard abbreviation (`Pkwy`, `Rte`) or a `Twp.` suffix does not break binding; the printed Facility ID, holder, street number and street name must still agree with the Atlas site. SITE-000264 (`Pkwy`), SITE-001137 (`Rte`) and SITE-002113 (`Twp.`) now bind. The township marker is a suffix difference only, in either direction (printed `Newbury Twp.` binds Atlas `Newbury`, and printed `Newbury` binds Atlas `Newbury Twp.`); a leading `Twp. Newbury` does not. The rule is narrow: SITE-000936 (printed `302 Conwell Ave.` vs Atlas `302 S. Conwell Ave`: a direction word), SITE-002114 (street number 1333 vs 1331) and SITE-001510 (`Sharon Twp.` vs `Sharon Center`) stay unbound, and `check.py` injects a binding with a different street number.
- **P3 (permit description):** the permit's `Permit Description` field is a witness at `supports_C` only. The field ends at the next labelled field (`Permit Type:`, `Issue Date:`, ...); text after that boundary does not count. A `Facility Description` field is not that field and is not used. SITE-000814 (tier C) gets `coating_formulation` in `processes`; on tier A/B it gives a capability row only (SITE-001530 `adhesive_sealant_formulation`, SITE-000264's rubber mixing/compounding).
- **P4 (capability mapping):** `compounding_unspecified` -> `compounding` and `extrusion_unspecified` -> `extrusion`; `coating_applying` and `foam_molding_bead` stay unmapped. Unlocked: SITE-000601 (tier A, `compounding_unspecified` on the Compounding unit-group heading) and SITE-000264 (`compounding_unspecified` in the P921 equipment list). The three sites #400 held for "no capability term": SITE-000601 gains a row; SITE-001888 (`coating_applying`) and SITE-002124 (`foam_molding_bead`) stay held.
- **Writes:** tier C: union into `processes`; tier A/B at `supports_C`: a `site_capabilities` row only. Union only; nothing removed. Everything else is #400's rule set unchanged: unit descriptions bind to the printed Facility ID, holder, street and city of each cited document; ancillary units (boilers, generators, tanks, baghouses, finishing booths, cleaning) name no process; a permit past its printed expiry caps at `supports_C`; a label or equipment list is `supports_C`; the (site, term) hold rule; evidence staged and published before the cells it supports.

## Frame and sources

The frame is #400's: **{m['frame_sites']} PIC-18 sites** (unit: sites with exactly one active PIC-18 site, organization process unknown, an FRS link, final Ohio EPA permit retrievable by the canary's Facility-ID route), recomputed from the canary's caches and asserted at 33. **No fetch ran**: the same stored permits (sha256 against the canary's journal; {len(json.load(open(HERE / 'doc_hashes.json')))} documents). Rows already written by #400 are recognized from their evidence and capability rows and are not written again. No person's name, email or phone is in this folder (`check.py` reads names from the whole stored text, signatories included, and scans every task file).

## Outcome

| Measure (unit: frame sites) | Value |
|---|---|
| Frame | **{m['frame_sites']}** |
| VERIFIED / STILL_UNCERTAIN / REJECT | **{m['verified_sites']}** / **{m['still_uncertain_sites']}** / **{m['reject_sites']}** |
| New in this PR: sites with a process written to `processes` / terms / evidence rows | **{m['sites_with_process_written']}** ({', '.join(m['process_sites']) or 'none'}) / **{m['process_terms_written']}** / **{m['process_terms_written']}** |
| New in this PR: capability rows (tier A/B, `supports_C`) | **{m['capability_rows']}** |
| Sites that got only a capability row | **{len(m['capability_only_sites'])}** ({', '.join(m['capability_only_sites']) or 'none'}) |
| Proposals already held (earlier PR, existing capability, or duplicate in plan; no write) | **{m['already_held_rows']}** |
| Held sites by reason | {m['held_sites_by_reason']} |

### Outcome check (harness `pic18_unknown.py`, process-unknown organizations)

{outcome}

## Per site (* = re-scored under P2-P4)

| Site | Tier | Bind | Permit(s) cited: issued → expiry | §3.1 terms proposed | Write | Verdict |
|---|---|---|---|---|---|---|
""" + "\n".join(rows) + f"""

Per quote: `proposals.csv` (document, permit number, issue and expiry dates, bind of that document, computed witness position, term, strength, route, hold reason, the verbatim quote). Per site: `sites.csv`. Documents: `doc_hashes.json`.

## Judgment calls

1. **SITE-000264's rubber terms come from the permit description** (P3, `supports_C`): "banbury mixers, mills, calenders, mixing tanks, extruder, and rotocure used to fabricated rubber membrane products". `rubber_mixing_compounding` maps to itself. `rubber_calendering` and the P921 `calendering` both map to the capability `calendering`; one row is written (the unit-level one). `rubber_extrusion` has no §3.6 mapping (the `extrusion` rollup lists only the plastics subtypes) and is held.
2. **SITE-000601's `coating_applying`** (coaters in the 2020 permit, past its printed expiry 2025-04-01; permit description "coating lines") stays held: no capability term.
3. **SITE-001137 gets `coating_applying` from unit R005 only** (tier C, `supports_C`). R005 "Vinyl Coatings Makor Flatline": "Conveyorized spray coatings of vinyl products with a 0.64 MMBtu/hr natural gas-fired drying oven"; the unit's own terms call it "the vinyl coating line". By the lane predicate (a coating line, not a booth) it is the holder's own process, and it is an equipment phrase, so `supports_C`. The Q-One spray booth and the drive-thru booth are finishing booths (ancillary), R006 coats wood, and the woodworking unit is not a polymer process: none is carried.
4. **SITE-002113 stays held** although it now binds: "spray booth for lay-up of polyester resin mixes" does not say spray-up or hand lay-up, and no composites `_unspecified` term exists.
5. **{pd_n} writes rest on a Permit Description alone** ({pd_list}); {pd_p} of them is a `processes` write (SITE-000814, tier C). The unit text of each names no process in the words the term needs. All are `supports_C` (P3), and the tier A/B ones are capability rows only.

## Self-refute (contract rule 15)

- self-refute: Grain — {len(model['props'])} proposals checked, 0 changed: every cited document binds on its own printed Facility ID, holder, street number and street name and city (P2 relaxes only an abbreviation or Twp. suffix); SITE-000264's permit description names its own permit's units; no sister-site or company-wide page is used.
- self-refute: Founding — 0 rows checked, 0 changed (no founding claim).
- self-refute: Strength — {len(model['props'])} proposals checked, 0 changed: every Permit Description proposal is `supports_C` (`check.py` rule PD_STRENGTH); every tier A/B proposal is `supports_C` and a capability row only.
- self-refute: Truncated quote — {len(model['props'])} proposals checked, 0 changed: SITE-000264's and SITE-000814's quotes are whole sentences carrying the claim words; each is verified in order against its stored permit.
- self-refute: Attribution — {len(model['props'])} proposals checked, 0 changed: every quote is from the holder's own permit; none is from a parent, customer, equipment maker or explainer page.

## Reproduction and checks

- `python3 tasks/pic18-permit-followup-2026-11-19/build.py` hash-checks the stored permits, recomputes everything and writes the packet files and this README; `--apply` plans the writes in memory, stages and verifies each shard, and publishes evidence, then capability rows, then the site cells, replacing each atomically. Ids are allocated at apply time above the maximum of every other row (owner ruling 2026-11-19 E1) and re-allocated the same way after each merge of origin/main.
- Named check: `python3 tasks/pic18-permit-followup-2026-11-19/check.py`: recomputes the frame, every bind, expiry, witness position, strength and route; derives each Facility ID from the hashed text; requires the applied state to equal the plan; audits the data diff against the merge-base; rebuilds the written rows and requires equality; scans task files for emails, phones and names; runs the interrupted-replay and unrelated-cell probes; then runs {EXPECTED_DEFECTS} injected defects and fails unless each is caught, including: a binding with a different street number; a Permit Description proposed above `supports_C`; a Facility Description routed to a write; a quote not in its document; a reordered quote; a term not in §3.1; ancillary text mapped to a process; a `supports_C` term in `processes` on a tier A/B site; an expired permit at `supports_A`; a held (site, term) pair written (duplicate proposal and applied cell); a changed `tier_effect`; a falsified Facility ID (note and manifest); a restore of the site and capability shards to the base; a changed cell other than `processes`; a changed existing row; an evidence id not above the base maximum; a person's name; a signatory's name; an email; a changed frame count.

## Proposed follow-ups (not in this PR)

- Owner question: a §3.6 capability term for `rubber_extrusion` (SITE-000264 permit description), or leave unmapped.
- Owner question: a direction word missing from the printed street (SITE-000936, `Conwell Ave.` vs `S. Conwell Ave`): extend P2 to a missing direction word when the street number and Facility ID agree? Recommend no: a direction can distinguish two streets.
- The 16 sites still not bound are unchanged from #400: 8 have a blank Atlas street.

Not checked: permits beyond the newest six documents per site; local-agency permits; whether any plant still runs the permitted equipment. A permit is a statement as of its issue date and never a status finding.
"""

def main():
    hashes = stage(); inp = loaded(); model = compute(inp)
    write_csv(HERE / "sites.csv", model["sites"]); write_csv(HERE / "proposals.csv", model["props"])
    m = metrics(model); json.dump(m, open(HERE / "metrics.json", "w"), indent=1)
    if not model["viol"]: (HERE / "README.md").write_text(readme(model, m))
    if model["viol"]: print("VIOLATIONS:\n" + "\n".join(model["viol"])); sys.exit(1)
    if "--apply" in sys.argv:
        bs = git("merge-base", "HEAD", "origin/main").strip()
        base = {ROOT / f: read_rows_text(git("show", f"{bs}:{f}")) for f in ("data/sites_OH.csv", "data/evidence_sites_OH.csv", "data/site_capabilities.csv")}
        print("applied (evidence, capability, site rows):", apply(model, hashes, base=base))
    print(json.dumps(m, indent=1))

if __name__ == "__main__": main()

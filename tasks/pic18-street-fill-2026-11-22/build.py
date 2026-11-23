#!/usr/bin/env python3
"""Build the PIC-18 street and size packet without modifying canonical data."""
import argparse
import csv
import importlib.util
import json
import hashlib
import re
import subprocess
from collections import Counter, defaultdict
from datetime import datetime
from itertools import combinations
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SPRINT = HERE.parent / "pic18-size-sprint-2026-11-22"
STORE = Path("/Volumes/johnpswan/work/GAC/polymer-atlas/atlas-store")
CACHE = Path.home() / ".bb/thread-storage/thr_9i2c6byhcz/2026-11-06-atlas/persist/size-sprint-2026-11-22/cache"
CUTOFF, AS_OF = "2021-11-22", "2026-11-22"
BY = "codex " + HERE.name


def load(name, file):
    spec = importlib.util.spec_from_file_location(name, file)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


B = load("size_sprint", SPRINT / "build.py")
G = load("binding", ROOT / "scripts/check_evidence_binding.py")
from matching import corporate_form_extension, same_locality, same_street
from atlas import name_key, squash, street_key

B.same_street = same_street
B.city_ok = lambda site, city, zip: same_locality(site["city"], "OH", site["zip"], city, "OH", zip)
EPA = {
    "frs": ("registry_id", "fac_name", "fac_street", "fac_city", "fac_zip", ""),
    "rcra": ("id_number", "facility_name", "street_address", "city_name", "zip_code", "evaluation_start_date"),
    "air": ("pgm_sys_id", "facility_name", "street_address", "city", "zip_code", "actual_end_date"),
    "npdes": ("npdes_id", "facility_name", "location_address", "city", "zip", "actual_end_date"),
}
LAKE = {
    "sam": ("sam/sam_entities.parquet", "k_site_state", "f012_legal_business_name", "f013_dba_name",
            "f016_physical_address_line_1", "f017_physical_address_line_2", "f018_physical_address_city",
            "k_site_zip5", "f010_last_update_date",
            " AND coalesce(trim(f024_d_b_open_data_flag),'') <> 'Y' AND coalesce(trim(f122_entity_evs_source),'') <> 'D&B' AND f010_last_update_date >= '20220404'"),
    "form5500": ("form5500/form5500_main_*.parquet", "k_loc_state", "SPONSOR_DFE_NAME", "SPONS_DFE_DBA_NAME",
                 "SPONS_DFE_LOC_US_ADDRESS1", "SPONS_DFE_LOC_US_ADDRESS2", "SPONS_DFE_LOC_US_CITY",
                 "SPONS_DFE_LOC_US_ZIP", "DATE_RECEIVED", ""),
    "form5500_sf": ("form5500/form5500_sf_*.parquet", "k_loc_state", "SF_SPONSOR_NAME", "SF_SPONSOR_DFE_DBA_NAME",
                    "SF_SPONS_LOC_US_ADDRESS1", "SF_SPONS_LOC_US_ADDRESS2", "SF_SPONS_LOC_US_CITY",
                    "SF_SPONS_LOC_US_ZIP", "DATE_RECEIVED", ""),
}
LOCATION = re.compile(r"^\s*(?:Facility|Site|Premises?)\s+(?:Street Address|Physical Address|Address|Location)\s*:\s*(.*)$", re.I)
FACILITY = re.compile(r"^\s*(?:Facility|Site|Premises?)\s+Name\s*:\s*(.+)$", re.I)
CITY = re.compile(r"^\s*([^,]+),\s*(?:OH|Ohio)\s+(\d{5}(?:-\d{4})?)\s*$", re.I)


def dmy(value):
    value = (value or "").strip()
    for fmt, width in (("%Y-%m-%d", 10), ("%Y%m%d", 8), ("%m/%d/%Y", 10), ("%m-%d-%Y", 10)):
        try:
            return datetime.strptime(value[:width], fmt).date().isoformat()
        except ValueError:
            continue
    return ""


def locator(file, member, row):
    return "raw/" + file + ("!" + member if member else "") + "@" + str(row)


def family(kind):
    if kind in ("ita", "insp"):
        return "OSHA"
    if kind in EPA or kind == "permit":
        return "EPA"
    return "SAM" if kind == "sam" else "Form 5500"


def unsafe(name, street):
    return (not name or B.personal(name) or B.personal(name_key(name)) or bool(re.search(r"@|\bsole propriet(?:or|orship)\b|\d{3}[-. ]\d{3}[-. ]\d{4}", name, re.I))
            or bool(re.search(r"@|\b(?:apt|apartment|residence|home address)\b|\d{3}[-. ]\d{3}[-. ]\d{4}", street, re.I)))


def witness(kind, ref, names, street, city, zip, date, event=""):
    return dict(kind=kind, ref=ref, names=[n.strip() for n in names if n and n.strip()],
                street=street.strip(), city=city.strip(), zip=zip.strip(), date=date, event=event)


def osha(entry):
    raw = entry["r"]
    return witness(entry["kind"], locator(raw["file"], raw["member"], raw["row"]), entry["names"],
                   entry["st"], entry["city"], entry["zip"], B.source_date(entry))


def lake_rows(store):
    queries = []
    for kind, (file, state, name, alt, first, second, city, zip, dt, filt) in LAKE.items():
        queries.append(f"""SELECT '{kind}' AS kind, src_path AS path, src_row AS ordinal, {name} AS name, {alt} AS alt,
                       concat_ws(' ', nullif(trim({first}),''), nullif(trim({second}),'')) AS street,
                       {city} AS city, {zip} AS zip, {dt} AS stamp FROM read_parquet('{file}', union_by_name=true)
                       WHERE {state}='OH' AND coalesce(trim({first}),'')<>'' {filt}""")
    run = subprocess.run(["duckdb", "-batch", "-json"], cwd=store / "lake/2026-11-22",
                         input=" UNION ALL ".join(queries) + ";", text=True, capture_output=True, check=True)
    for r in json.loads(run.stdout):
        yield witness(r["kind"], "raw/" + r["path"] + "@" + str(r["ordinal"]), [r['name'], r['alt']],
                      r["street"], r["city"] or "", r["zip"] or "", dmy(r["stamp"]))


def permit_rows(store, files=None):
    folder = store / "raw/permits-oh-air/2026-11-22"
    docs = {f"{r['facility_id']}_{r['document_id']}.pdf": dmy(r["document_date"])
            for r in B.rd(folder / "manifest.csv")}
    for file in sorted(folder.glob("*.pdf")):
        if files is not None and "raw/" + str(file.relative_to(store / "raw")) not in files:
            continue
        text = subprocess.run(["pdftotext", "-layout", str(file), "-"], text=True, capture_output=True, check=True).stdout
        for page, content in enumerate(text.split("\f"), 1):
            lines = content.splitlines()
            names = {m[1].strip() for line in lines if (m := FACILITY.match(line))}
            if len(names) != 1:
                continue
            for i, line in enumerate(lines):
                if not (m := LOCATION.match(line)):
                    continue
                parts = [x.strip() for x in [m[1], *lines[i + 1:i + 4]] if x.strip()]
                prev = [x.strip() for x in lines[max(i - 2, 0):i] if x.strip()]
                if parts and (place := CITY.match(parts[0])):
                    street = prev[-1] if prev else ""
                elif len(parts) > 1 and (place := CITY.match(parts[1])):
                    street = parts[0]
                else:
                    continue
                if re.match(r"^\d+[A-Za-z-]*\s+[^:]+$", street) and same_street(street, street):
                    ref = f"raw/{file.relative_to(store / 'raw')}@{page}:{i + 1}"
                    yield witness("permit", ref, names, street, place[1], place[2], docs[file.name])


def held_name(idx, site, name):
    key = name_key(name)
    sid = site["site_id"]
    held, parents = idx.held_keys("sites", sid), idx.parent_keys("sites", sid)
    if key in parents or any(corporate_form_extension(k, key) for k in parents):
        texts = {squash(n) for n in idx.parent_names("sites", sid)}
        if squash(name) not in idx.own_texts(site["org_id"]) - texts:
            return False
    return key in held or any(corporate_form_extension(k, key) for k in held)


def safe_name(idx, site, w):
    return next((n for n in w["names"] if held_name(idx, site, n) and not unsafe(n, w["street"])), "")


def dated(w):
    return bool(w["date"] and CUTOFF <= w["date"] <= AS_OF)


def street_decision(candidates, occupied):
    current = [w for w in candidates if dated(w)]
    if not current:
        return "no_current_held_witness", []
    if any(not same_street(a["street"], b["street"]) for a, b in combinations(current, 2)):
        return "dated_witnesses_disagree", current
    if street_key(current[0]["street"]) in occupied:
        return "duplicate_site_lead", current
    return "eligible", current


def source_and_quote(w, name):
    kind = w["kind"]
    addr = f"{w['street']}, {w['city']}, OH {w['zip']}"
    if kind in ("ita", "insp"):
        return ("OSHA ITA Form 300A" if kind == "ita" else "OSHA inspection"), f"{name}, {addr}"
    if kind in EPA:
        return "EPA ECHO facility filing", f"{name}; {addr}; facility record"
    if kind == "permit":
        return "Ohio EPA air permit", f"permittee: {name}; address: {addr}"
    return "", ""


def evidence(w, name, sid, band=""):
    label, quote = source_and_quote(w, name)
    extra = ("; dated EPA event " + w["event"]) if w["event"] else ""
    return dict(evidence_id="", record_table="sites", record_id=sid, claim_type="size_band" if band else "address",
                claim_detail=(f"employee_band_site={band}; " if band else "physical site street; ") + "quote: " + quote,
                source_class="registry" if w["kind"] in EPA else "government_filing",
                source_ref=f"{label}; {w['ref']}", observed_date=w["date"],
                tier_effect="supports_B" if band else "supports_C" if w["kind"] in EPA else "supports_A",
                created_by=BY, notes=f"Packet {HERE.name}; physical role{extra}.", address_role="" if band else "physical")


def inputs(store):
    return {k.removeprefix("./"): v for ln in (store / "raw/MANIFEST.sha256").read_text().splitlines()
            for v, k in [ln.split("  ", 1)]}


def ref_file(r):
    return r.rsplit("@", 1)[0].split("!", 1)[0]


def fact(w):
    fields = {k: w[k] for k in ("kind", "ref", "names", "street", "city", "zip", "date", "event")}
    encoded = json.dumps(fields, sort_keys=True, ensure_ascii=False).encode()
    return dict(ref=w["ref"], kind=w["kind"], observed_date=w["date"], event_ref=w["event"],
                fields_sha256=hashlib.sha256(encoded).hexdigest())


def snapshot(ref):
    return G.Index.load(ref)


def write(path, rows):
    assert rows, f"{path.name}: cannot infer columns without rows"
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def build(base, store, cache, first):
    idx = snapshot(base)
    sites, orgs = idx.sites, idx.orgs
    frame = sorted(B.rd(SPRINT / "no_street_sites.csv"), key=lambda r: r["site_id"])
    assert len(frame) == len({r["site_id"] for r in frame}) == 121
    active = [s for s in sites.values() if s["operating_status"] == "active"]
    active_n = Counter(s["org_id"] for s in active)
    by_street = defaultdict(list)
    for s in sites.values():
        s["_held"] = B.held_names(s, orgs)
        if s["street_address"].strip():
            by_street[street_key(s["street_address"])].append(s)
    occupied = set(by_street)
    # These indexes are discovery routes. The replay reads cited rows in the archives.
    ix, pools = {}, defaultdict(list)
    have_keys = {k.split()[0] for f in frame for k in idx.held_keys("sites", f["site_id"]) if k}

    def index(w):
        firsts = {k.split()[0] for n in w["names"] if (k := name_key(n))}
        for k in firsts & have_keys:
            pools[k].append(w)

    for kind, filename in (("ita", "ita_oh.csv"), ("insp", "insp_oh.csv")):
        entries = B.unify(B.rd(cache / filename), kind)
        ix[kind] = B.index(entries)
        for e in entries:
            if any((k := name_key(n)) and k.split()[0] in have_keys for n in e["names"]):
                index(osha(e))
    for r in B.rd(cache / "epa_oh.csv"):
        if (k := name_key(r["name"])) and k.split()[0] in have_keys:
            event = locator(r["event_file"], r["event_member"], r["event_row"]) if r["event_file"] else ""
            index(witness(r["family"], locator(r["file"], r["member"], r["row"]), [r["name"]],
                          r["street"], r["city"], r["zip"], dmy(r["event_date"]), event))
    for w in lake_rows(store):
        index(w)
    for w in permit_rows(store):
        index(w)
    results, proposals, admitted, evs, witnesses = [], {}, {}, [], {}
    for f in frame:
        s = sites[f["site_id"]]
        sid = s["site_id"]
        prefixes = {k.split()[0] for k in idx.held_keys("sites", sid) if k}
        candidates = {}
        for k in prefixes:
            for w in pools[k]:
                if not same_street(w["street"], w["street"]) or not B.city_ok(s, w["city"], w["zip"]):
                    continue
                # Keep private-looking held-name witnesses in the consensus check. They cannot supply a quote.
                if any(held_name(idx, s, n) for n in w["names"]):
                    candidates[w["ref"]] = w
        ordered = sorted(candidates.values(), key=lambda w: (w["date"], w["ref"]), reverse=True)
        reason, current = street_decision(ordered, occupied)
        if s["street_address"].strip():
            reason = "already_addressed_on_base"
        row = dict(site_id=sid, org_id=s["org_id"], tier=s["verification_tier"], result=reason,
                   families=";".join(sorted({family(w["kind"]) for w in current})),
                   current_witnesses=len(current), undated_or_stale=len(ordered) - len(current),
                   current_witness_refs="|".join(w["ref"] for w in current),
                   address_ref="", band="", band_ref="", band_disposition="")
        results.append(row)
        witnesses.update({item["ref"]: item for item in current})
        if reason != "eligible":
            continue
        registry_below_tier = False
        for w in current:
            if not source_and_quote(w, "")[0] or not (n := safe_name(idx, s, w)):
                continue
            old = s["street_address"]
            s["street_address"] = w["street"]
            ev = evidence(w, n, sid)
            verdict = G.judge(ev, idx, _alone=True)[0]
            s["street_address"] = old
            if verdict == "PASS" and w["kind"] in EPA and s["verification_tier"] in ("A", "B"):
                registry_below_tier = True
                continue
            if verdict == "PASS":
                proposals[sid] = (w, ev, row, current)
                break
        else:
            row["result"] = "registry_address_below_site_tier" if registry_below_tier else "no_bindable_address_quote"

    proposed_keys = Counter(street_key(w["street"]) for w, _, _, _ in proposals.values())
    for sid, (w, ev, row, current) in proposals.items():
        if proposed_keys[street_key(w["street"])] > 1:
            row["result"] = "duplicate_site_lead"
            continue
        s = sites[sid]
        s["street_address"] = w["street"]
        by_street[street_key(w["street"])].append(s)
        row.update(result="street_fill", address_ref=w["ref"])
        admitted[sid] = (s, w, ev, row)
    for sid, (s, _, address_ev, row) in admitted.items():
        evs.append(address_ev)
        pairs, notes = {}, {}
        for kind in ix:
            pairs[kind], notes[kind] = B.classify(s, s["_held"], ix[kind])
        pairs["f5500"] = []
        near = {k: v for k, values in notes.items() if (v := B.would_be_band(k, values))}
        decision = B.evaluate(s, "suffix", pairs, active_n, by_street, near, notes)
        if decision[0] != "fill":
            row["band_disposition"] = decision[1] if decision[0] == "hold" else "no_osha_match"
            continue
        result = decision[1]
        w = osha(result["e"])
        n = safe_name(idx, s, w)
        ev = evidence(w, n, sid, result["band"])
        if not n or G.judge(ev, idx, _alone=True)[0] != "PASS":
            row["band_disposition"] = "band_quote_not_bindable"
            continue
        row.update(band=result["band"], band_ref=w["ref"], band_disposition="band_fill")
        evs.append(ev)
        witnesses[w["ref"]] = w
    for i, ev in enumerate(evs, first):
        ev["evidence_id"] = f"EVD-{i:06d}"
    for s in sites.values():
        s.pop("_held", None)
    return (results, [dict(site_id=sid, street_address=s["street_address"], employee_band_site=row["band"])
                      for sid, (s, _, _, row) in admitted.items()], evs,
            [fact(w) for _, w in sorted(witnesses.items())])


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--base", required=True)
    ap.add_argument("--first", type=int, required=True)
    ap.add_argument("--store", type=Path, default=STORE)
    ap.add_argument("--cache", type=Path, default=CACHE)
    a = ap.parse_args()
    rows, edits, evs, facts = build(a.base, a.store, a.cache, a.first)
    write(HERE / "frame.csv", rows)
    write(HERE / "edits.csv", edits)
    write(HERE / "witnesses.csv", facts)
    write(HERE / "evidence_rows.csv", evs)
    man = inputs(a.store)
    filepaths = {ref_file(v) for f in facts for v in (f["ref"], f["event_ref"]) if v}
    if any(f["kind"] == "permit" for f in facts):
        filepaths.add("raw/permits-oh-air/2026-11-22/manifest.csv")
    (HERE / "INPUTS.sha256").write_text("".join(f"{man[p[4:]]}  {p}\n" for p in sorted(filepaths)))
    print(dict(Counter(r["result"] for r in rows)), "bands", sum(bool(r["band"]) for r in rows))
    print("street fills by family combination", dict(Counter(r["families"] for r in rows if r["result"] == "street_fill")))
    print("band dispositions", dict(Counter(r["band_disposition"] for r in rows if r["result"] == "street_fill")))


if __name__ == "__main__":
    main()

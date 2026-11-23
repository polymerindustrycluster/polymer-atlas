#!/usr/bin/env python3
"""Rebuild the EPA identifier packet from the pinned lake."""
import argparse
from collections import Counter, defaultdict
import csv
from functools import lru_cache
import io
from pathlib import Path
import random
import re
import sys
import zipfile

import duckdb

ROOT = Path.cwd()
sys.path.insert(0, str(ROOT / "scripts"))
from atlas import LOCALITY_SEP_RE, street_key
from derive_last_activity import _units, same_street
from regions import PIC18
from build_echo_spine import STATE_NAMES

QUARANTINE = ROOT / "tasks/revert-batches-5-6-2026-11-22/quarantine/registry_links.csv"
FIELDS = ("org_id", "registry", "registry_id", "match_basis", "as_of", "site_id")
EXACT = "echo_join_name_street_exact"
ANCHOR = "echo_join_frs_anchor"
FRS, RCRA, NPDES = "FRS", "RCRA_EPA_ID", "NPDES_PERMIT_ID"
CROSSWALK = "echo_frs_program_links"
FACILITIES = {
    FRS: ("echo_frs_facilities", "REGISTRY_ID", "FAC_NAME", "FAC_STREET", "FAC_CITY", "FAC_STATE", "FAC_ZIP"),
    RCRA: ("echo_rcra_facilities", "ID_NUMBER", "FACILITY_NAME", "STREET_ADDRESS", "CITY_NAME", "STATE_CODE", "ZIP_CODE"),
    NPDES: ("echo_npdes_facilities", "NPDES_ID", "FACILITY_NAME", "LOCATION_ADDRESS", "CITY", "STATE_CODE", "ZIP"),
}
PROGRAM = {"RCRAINFO": RCRA, "NPDES": NPDES}
FORM = set("inc incorporated llc corp corporation co company ltd limited lp llp holdings holding group us usa americas".split())
GENERIC = set("plant facility warehouse works site office hq headquarters building unit main north south east west northeast northwest southeast southwest central n s e w ne nw se sw oh ohio".split())
LOCATORS = ("src_path", "src_sha256", "src_row")
OTHER_DESIGNATORS = re.compile(r"\b(bldg|building|floor|fl|dept|department)\b\.?\s*#?\s*([a-z0-9-]+)", re.I)
DESIGNATOR_KIND = {"bldg": "building", "fl": "floor", "dept": "department"}
PROOF_FIELDS = (*LOCATORS, *("crosswalk_" + k for k in LOCATORS), *("frs_" + k for k in LOCATORS))
HISTORICAL = re.compile(r"\b(?:formerly|previously|predecessor|prior operator|former operator|former|f\s*/?\s*k\s*/?\s*a)\b", re.I)
FORMER_LEGAL = re.compile(r"\b(?:former|previous) (?:legal |corporate )?name\b[^:;\n]{0,70}:\s*([^;—\n]+)", re.I)
RENAME_FROM = re.compile(r"\blegal rename\s*[—–:]\s*([^;\n]+?)\s*(?:->|→)", re.I)


def read(path):
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def write(path, fields, rows):
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f, lineterminator="\n")
        writer.writerow(fields)
        writer.writerows(rows)


def tokenise(value):
    return tuple(re.findall(r"[a-z0-9]+", value.lower()))


@lru_cache(maxsize=65536)
def name_key(value):
    for dotted, compact in ((r"l\.l\.c\.?", "llc"), (r"u\.s\.a\.?", "usa"), (r"u\.s\.?", "us")):
        value = re.sub(r"\b" + dotted + r"\b", compact, value, flags=re.I)
    return tokenise(value)


def names_match(a, b):
    if not a or not b or a[:len(b)] != b:
        return False
    rest = " ".join(a[len(b):]).replace("north america", "americas").split()
    return FORM.issuperset(rest)


def operator_core(value):
    # Crosswalk corroboration can reconcile omitted corporate words; direct proof cannot.
    key = name_key(value)
    if key[:1] == ("the",):
        key = key[1:]
    while key and key[-1] in FORM:
        key = key[:-1]
    if key[-2:] == ("north", "america"):
        key = key[:-2]
    return key


def city_keys(value):
    return {tokenise(part) for part in re.split(r"[()]", value)} - {()}


def zip5(value):
    hit = re.fullmatch(r"(\d{5})(?:-?\d{4})?", value.strip())
    return hit[1] if hit else ""


def owner_fields(site, orgs):
    org = orgs[site["org_id"]]
    cities = city_keys(site["city"])
    county = re.sub(r"\s+County$", "", site["county"].strip(), flags=re.I)
    generic = cities | {tokenise(county), *(tokenise(state) for state in STATE_NAMES),
                        *(tokenise(code) for code in STATE_NAMES.values())}
    label_words = GENERIC | {t for phrase in generic for t in phrase}
    parts = LOCALITY_SEP_RE.split(site["site_name"])
    # Strip only recognised locality/label suffixes in parentheses.
    tail = re.fullmatch(r"(.*?)\s*\(([^()]*)\)", parts[-1])
    if tail:
        parts.extend(tail.groups())
    site_names = [name_key(x) for x in [site["site_name"], *parts]]
    site_names = {x for x in site_names if x and x not in generic
                  and not all(t in label_words or re.fullmatch(r"\d+(?:st|nd|rd|th)?", t) for t in x)}
    held = site_names | {name_key(x) for x in [org["legal_name"], *org["trade_names"].split(";")]}
    parent = []
    seen = {site["org_id"]}
    while org:
        parent.append(org["ultimate_parent_name"])
        oid = org["parent_org_id"]
        org = orgs.get(oid) if oid not in seen else None
        if org:
            parent.extend([org["legal_name"], *org["trade_names"].split(";")])
            seen.add(oid)
    return cities, zip5(site["zip"]), held - {()}, {name_key(x) for x in parent if x}


def designators(street):
    other = {(DESIGNATOR_KIND.get(kind.lower(), kind.lower()), re.sub(r"[^a-z0-9]", "", value.lower()))
             for kind, value in OTHER_DESIGNATORS.findall(street)}
    return _units(OTHER_DESIGNATORS.sub("", street)), other


def address_reason(site, owner, street, city, state, zipcode):
    cities, site_zip, _, _ = owner
    atlas_street = site["street_address"]
    if state.strip().upper() != site["state"]:
        return "state_mismatch"
    if designators(street) != designators(atlas_street):
        return "unit_or_building_mismatch"
    if not same_street(atlas_street, street):
        return "street_mismatch"
    if not (tokenise(city) in cities or (site_zip and site_zip == zip5(zipcode))):
        return "city_and_zip_mismatch"
    return ""


def name_reason(owner, name):
    _, _, held, parents = owner
    key = name_key(name)
    if any(names_match(key, p) or names_match(p, key) for p in parents):
        return "recorded_parent_only"
    if any(names_match(key, h) for h in held):
        return ""
    return "name_not_held"


def frame_data(conn, lake, region):
    site_columns = ("site_id", "org_id", "site_name", "city", "state", "zip", "county", "operating_status", "street_address")
    org_columns = ("org_id", "legal_name", "trade_names", "parent_org_id", "ultimate_parent_name")
    def load(columns, file):
        return [dict(zip(columns, (v or "" for v in row))) for row in conn.execute(
            f"SELECT {', '.join(columns)} FROM read_parquet(?)", [str(lake / "atlas" / file)]
        ).fetchall()]
    sites = load(site_columns, "atlas_sites.parquet")
    orgs = load(org_columns, "atlas_orgs.parquet")
    assert len({s["site_id"] for s in sites}) == len(sites), "duplicate Atlas site ID"
    ecosystem = read(ROOT / "data/ecosystem.csv")
    orgs.extend({"org_id": o["org_id"], "legal_name": o["legal_name"], "trade_names": "",
                 "parent_org_id": o["parent_institution_org_id"], "ultimate_parent_name": ""} for o in ecosystem)
    assert len({o["org_id"] for o in orgs}) == len(orgs), "duplicate Atlas org ID"
    ohio = {s["site_id"]: s for s in sites if s["state"] == "OH"}
    canonical = {s["site_id"]: {c: s[c] for c in site_columns} for s in read(ROOT / "data/sites_OH.csv")}
    assert ohio == canonical, "Atlas lake and canonical OH site shard differ"
    all_oh = [s for s in ohio.values() if s["operating_status"] == "active" and same_street(s["street_address"], s["street_address"])]
    pic = {s["site_id"] for s in all_oh if re.sub(r"\s+County$", "", s["county"].strip(), flags=re.I) in PIC18}
    selected = sorted((s for s in all_oh if (s["site_id"] in pic) == (region == "pic18")), key=lambda s: s["site_id"])
    return sites, {o["org_id"]: o for o in orgs}, ohio, selected, len(all_oh) - len(pic)


def pull_facilities(conn, lake, registry, needed_ids, include_oh=True):
    table, *cols = FACILITIES[registry]
    path = str(lake / "echo" / (table + ".parquet"))
    return conn.execute(
        f"""SELECT {', '.join(cols)}, src_path, src_sha256, src_row
        FROM read_parquet(?) WHERE (? AND k_site_state = 'OH') OR "{cols[0]}" IN (SELECT unnest(?))
        ORDER BY src_row""",
        [path, include_oh, sorted(needed_ids)]
    ).fetchall()


def raw_fields(lake, sources):
    """Read only the requested columns from raw CSV records at the supplied locators."""
    readings = {}
    for path, locators in sources.items():
        archive, member = path.split("!", 1)
        with zipfile.ZipFile(lake.parents[1] / "raw" / archive) as zf, zf.open(member) as f:
            reader = csv.reader(io.TextIOWrapper(f, encoding="utf-8-sig", newline=""))
            header = next(reader)
            max_row = max(locators)
            for row_no, row in enumerate(reader, 1):
                if row_no in locators:
                    readings[path, row_no] = {field: row[header.index(field)] for field in locators[row_no]}
                if row_no == max_row:
                    break
            assert (path, max_row) in readings, f"missing raw CSV row {max_row} of {path}"
    return readings


def pull_crosswalk(conn, lake, frs_ids, program_ids):
    return conn.execute(
        """SELECT PGM_SYS_ACRNM, PGM_SYS_ID, REGISTRY_ID, src_path, src_sha256, src_row
        FROM read_parquet(?) WHERE PGM_SYS_ACRNM IN ('RCRAINFO', 'NPDES')
        AND (REGISTRY_ID IN (SELECT unnest(?)) OR PGM_SYS_ID IN (SELECT unnest(?))) ORDER BY src_row""",
        [str(lake / "echo" / (CROSSWALK + ".parquet")), sorted(frs_ids), sorted(program_ids)]
    ).fetchall()


def historical_name(name, notes):
    key = " ".join(name_key(name))
    if not key:
        return False
    core = operator_core(name)
    for note in notes:
        former = FORMER_LEGAL.findall(note) + RENAME_FROM.findall(note)
        if core and any(core == operator_core(value.rstrip(".")) for value in former):
            return True
        for hit in HISTORICAL.finditer(note):
            after = " ".join(name_key(note[hit.end():].lstrip(" :-=\t\"'")))
            after = re.sub(r"^(?:known as|operated (?:by|as)|the company|was|of|is|by|the former) ", "", after)
            if after == key or after.startswith(key + " "):
                return True
    return False



def operator_reason(owner, notes, name):
    if historical_name(name, notes):
        return "recorded_former_operator"
    return name_reason(owner, name)


def binding_reason(site, owner, notes, facility, anchor=None):
    _, name, street, city, state, zipcode, *_ = facility
    reason = address_reason(site, owner, street, city, state, zipcode)
    if reason:
        return reason
    reason = operator_reason(owner, notes, name)
    if anchor and reason == "name_not_held":
        if not operator_core(name) or operator_core(name) != operator_core(anchor[1]):
            return "program_operator_conflicts_with_frs"
        return ""
    return reason


def held_elsewhere(site, rows):
    return any(row["site_id"] != site["site_id"] or row["org_id"] != site["org_id"] for row in rows)


def evaluate(lake, region, canary=False):
    conn = duckdb.connect()
    sites, orgs, ohio, frame, remaining = frame_data(conn, lake, region)
    quarantine = read(QUARANTINE)
    links = read(ROOT / "data/registry_links.csv")
    removed_oh = [r for r in quarantine if r["site_id"] in ohio]
    assert len(quarantine) == 6837 and len(removed_oh) == 549, "quarantine count differs from owner brief"
    assert len({tuple(r[k] for k in FIELDS) for r in quarantine}) == len(quarantine), "duplicate quarantine row"
    frame_ids = {s["site_id"] for s in frame}
    removed_frame = sum(r["site_id"] in frame_ids for r in removed_oh)
    sample = list(frame)
    if canary:
        random.Random(20261122).shuffle(sample)
        sample = sample[:25]
    sample_ids = {s["site_id"] for s in sample}
    sample_removed = { (r["site_id"], r["registry"], r["registry_id"]): r
                       for r in removed_oh if r["site_id"] in sample_ids }
    assert len(sample_removed) == sum(r["site_id"] in sample_ids for r in removed_oh)
    geos = {s["site_id"]: owner_fields(s, orgs) for s in sites if s["org_id"] in orgs}
    assert sample_ids <= geos.keys(), "a frame site has no organization record"
    by_street = defaultdict(list)
    for s in sites:
        if s["site_id"] in geos:
            by_street[s["state"], street_key(s["street_address"])].append(s)
    notes = {r["org_id"]: r["notes"] for r in read(ROOT / "data/ecosystem.csv")}
    for kind, id_field, ids in (
        ("sites", "site_id", [s["site_id"] for s in sites]),
        ("orgs", "org_id", list(orgs)),
    ):
        notes.update(conn.execute(
            f"SELECT {id_field}, notes FROM read_parquet(?) WHERE {id_field} IN (SELECT unnest(?))",
            [str(lake / "atlas" / f"atlas_{kind}.parquet"), ids]
        ).fetchall())
    held = defaultdict(list)
    for row in links:
        held[row["registry"], row["registry_id"]].append(row)
    absent = "identifier_absent_from_facility_file"
    candidates = defaultdict(dict)
    leads = defaultdict(set)
    inspected = {}

    def site_notes(site):
        return [notes.get(k) or "" for k in (site["site_id"], site["org_id"])]

    def test(site, row, anchor=None):
        return binding_reason(site, geos[site["site_id"]], site_notes(site), row, anchor)

    for reg, rid in [(k[1], k[2]) for k in sample_removed]:
        assert reg in FACILITIES and rid, "unsupported quarantine identifier in frame"
    source_rows = {}
    for registry in FACILITIES:
        needed = {rid for _, reg, rid in sample_removed if reg == registry}
        results = pull_facilities(conn, lake, registry, needed)
        by_id = defaultdict(list)
        by_locality = defaultdict(set)
        sample_address = defaultdict(set)
        for site in sample:
            sid = site["site_id"]
            cities, zipcode, *_ = geos[sid]
            for city in cities:
                by_locality["city", city].add(sid)
            if zipcode:
                by_locality["zip", zipcode].add(sid)
            sample_address[street_key(site["street_address"])].add(sid)
        sample_map = {s["site_id"]: s for s in sample}
        for rid, name, street, city, state, zipcode, *loc in results:
            if not rid:
                continue
            row = tuple(v or "" for v in (rid, name, street, city, state, zipcode, *loc))
            by_id[rid].append(row)
            state = (state or "").strip().upper()
            matched_street = sample_address[street_key(street)] if state == "OH" else set()
            locality = (by_locality["city", tokenise(city or "")] | by_locality["zip", zip5(zipcode or "")]) if state == "OH" else set()
            name_candidates = {sid for sid in locality if name_reason(geos[sid], name or "") != "name_not_held"}
            forced = {sid for sid, reg, identifier in sample_removed if reg == registry and identifier == rid} if rid in needed else set()
            for sid in matched_street | name_candidates | forced:
                key = sid, registry, rid
                reason = test(sample_map[sid], row)
                if reason:
                    leads[key].add(reason)
                else:
                    candidates[key].setdefault(EXACT, (row,))
        source_rows[registry] = by_id

    frs_sites = defaultdict(set)
    for sid, reg, rid in candidates:
        if reg == FRS:
            frs_sites[rid].add(sid)
    program_ids = {rid for _, reg, rid in sample_removed.keys() | candidates.keys() if reg != FRS}
    crosswalks = pull_crosswalk(conn, lake, frs_sites, program_ids)
    anchored_ids = {rid for _, rid, frs_id, *_ in crosswalks if frs_id in frs_sites}
    # Check reverse cardinality for each newly nominated program ID, including
    # FRS anchors outside this frame. Project every EPA row for proposed IDs.
    crosswalks += pull_crosswalk(conn, lake, (), anchored_ids - program_ids)
    crosswalks = sorted(set(crosswalks), key=lambda row: row[-1])
    for registry in FACILITIES:
        identifiers = {rid for _, reg, rid in candidates if reg == registry}
        if registry != FRS:
            identifiers |= {rid for code, rid, frs_id, *_ in crosswalks
                            if PROGRAM[code] == registry and frs_id in frs_sites}
        rows = pull_facilities(conn, lake, registry, identifiers, include_oh=False)
        for rid in identifiers:
            source_rows[registry][rid] = []
        for row in rows:
            source_rows[registry][row[0]].append(tuple(v if v is not None else "" for v in row))

    linked_frs = defaultdict(set)
    for code, rid, anchor_id, *_ in crosswalks:
        linked_frs[PROGRAM[code], rid].add(anchor_id)
    for code, rid, anchor_id, *loc in crosswalks:
        registry = PROGRAM[code]
        for sid in frs_sites.get(anchor_id, ()):
            key = sid, registry, rid
            if len(linked_frs[registry, rid]) > 1:
                leads[key].add("program_id_has_multiple_frs_anchors")
                continue
            rows = source_rows[registry].get(rid, ())
            if not rows:
                leads[key].add(absent)
            anchor = candidates[sid, FRS, anchor_id][EXACT][0]
            for row in rows:
                reason = test(sample_map[sid], row, anchor)
                if reason:
                    leads[key].add(reason)
                else:
                    candidates[key].setdefault(ANCHOR, (row, (code, rid, anchor_id, *loc), anchor))

    def collision(site, registry, rid):
        if held_elsewhere(site, held[registry, rid]):
            if all(row["org_id"] == site["org_id"] and not row["site_id"] for row in held[registry, rid]):
                return "identifier_held_at_org_grain"
            return "identifier_already_held_elsewhere"
        # An EPA identifier repeating at more than one eligible operator/address is
        # held for R10 adjudication. Exact shared address alone does not prove co-location.
        for row in source_rows[registry][rid]:
            for other in by_street[row[4].strip().upper(), street_key(row[2])]:
                if other["site_id"] != site["site_id"] and not test(other, row):
                    return "identifier_matches_multiple_sites"
        if len({s for s, r, i in candidate_owners[registry, rid]}) > 1:
            return "identifier_matches_multiple_sites"
        return ""

    candidate_owners = defaultdict(set)
    for key in candidates:
        candidate_owners[key[1:]].add(key)
    accepted = {}
    for key, choices in sorted(candidates.items()):
        sid, registry, rid = key
        site = sample_map[sid]
        old = sample_removed.get(key)
        basis = old["match_basis"] if old else (EXACT if EXACT in choices else ANCHOR)
        if basis not in choices:
            leads[key].add("original_match_basis_not_reproduced")
            continue
        proof = choices[basis]
        if registry == FRS and not re.fullmatch(r"\d{12}", rid) or registry == RCRA and not re.fullmatch(r"[A-Z0-9]{12}", rid) or registry == NPDES and not re.fullmatch(r"[A-Z0-9]{7,12}", rid):
            leads[key].add("registry_id_shape")
            continue
        reason = collision(site, registry, rid)
        if not reason and len(proof) == 3:
            reason = collision(site, FRS, proof[2][0])
        if reason:
            leads[key].add(reason)
            continue
        if held[registry, rid]:
            leads[key].add("already_held_at_this_site")
            continue
        canonical = (site["org_id"], registry, rid, basis, "2026-11-22", sid)
        if old:
            assert old["org_id"] == site["org_id"]
            canonical = tuple(old[k] for k in FIELDS)
        accepted[key] = canonical, proof
        inspected[key] = site, geos[sid]
    for key in sample_removed:
        if key not in accepted and not leads[key]:
            leads[key].add(absent if key[2] not in source_rows[key[1]] else "no_exact_frs_anchor")
    refused = {key: sorted(leads[key]) for key in sample_removed.keys() - accepted.keys()}
    leads = {key: sorted(reasons) for key, reasons in leads.items() if key not in accepted}
    return frame, sample, remaining, removed_frame, accepted, inspected, leads, refused


def verify_raw(lake, accepted):
    requests = defaultdict(dict)
    expected = {}
    for canonical, proof in accepted.values():
        registry = canonical[1]
        fields = [FACILITIES[registry][1:]]
        if len(proof) > 1:
            fields.extend([("PGM_SYS_ACRNM", "PGM_SYS_ID", "REGISTRY_ID"), FACILITIES[FRS][1:]])
        for row, columns in zip(proof, fields, strict=True):
            path, _, number = row[-3:]
            expected[path, number] = dict(zip(columns, row[:-3], strict=True))
            requests[path][number] = columns
    raw = raw_fields(lake, requests)
    for key, values in expected.items():
        observed = {k: v or "" for k, v in raw[key].items()}
        assert observed == values, f"raw projection disagrees with lake at {key}"
    return len(raw)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--lake", type=Path, required=True)
    ap.add_argument("--region", choices=("pic18", "rest-oh"), default="pic18")
    ap.add_argument("--canary", action="store_true")
    ap.add_argument("--out", required=True, type=Path)
    args = ap.parse_args()
    frame, sample, remaining, removed_frame, accepted, _, leads, refused = evaluate(args.lake, args.region, args.canary)
    print(f"{len(frame)} active civic-street sites in {args.region}; {removed_frame} quarantined links; {remaining} sites in rest-of-Ohio frame", flush=True)
    print(f"{len(sample)} selected sites; {len(accepted)} proposed links", flush=True)
    args.out.mkdir(exist_ok=True, parents=True)
    write(args.out / "frame.csv", ("site_id", "org_id", "county"), ((s["site_id"], s["org_id"], s["county"]) for s in sample))
    write(args.out / "packet.csv", (*FIELDS, *PROOF_FIELDS),
          (canonical + tuple(v for row in proof for v in row[-3:]) + ("",) * (9 - 3 * len(proof))
           for canonical, proof in accepted.values()))
    write(args.out / "leads.csv", ("site_id", "registry", "registry_id", "reason"),
          ((*key, reason) for key, reasons in sorted(leads.items()) for reason in reasons))
    print(f"{verify_raw(args.lake, accepted)} raw CSV rows verified field by field", flush=True)
    print("Proposed by registry", dict(Counter(k[1] for k in accepted)))
    print("Leads by reason", dict(Counter(r for reasons in leads.values() for r in reasons)))
    print("Quarantine refused", len(refused), dict(Counter(r for reasons in refused.values() for r in reasons)))
    if args.canary:
        print("Quarantine refused by identifier", sorted(refused.items()))
    q = {(r["site_id"], r["registry"], r["registry_id"]) for r in read(QUARANTINE)}
    print("Verbatim returns", dict(Counter(k[1] for k in accepted.keys() & q)))
    print("New", dict(Counter(k[1] for k in accepted.keys() - q)))


if __name__ == "__main__":
    main()

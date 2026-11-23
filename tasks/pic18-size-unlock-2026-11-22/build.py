#!/usr/bin/env python3
"""Reproduce both held-files canaries and their known-answer controls."""
import argparse
import csv
import hashlib
import importlib.util
import json
import math
import random
import re
import subprocess
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SPRINT = HERE.parent / "pic18-size-sprint-2026-11-22"
STORE = Path("/Volumes/johnpswan/work/GAC/polymer-atlas/atlas-store")
DEFAULT_CACHE = Path.home() / ".bb/thread-storage/thr_9i2c6byhcz/2026-11-06-atlas/persist/size-sprint-2026-11-22/cache"
SEED = 20261122
FRAMES = {"name_not_held": 96, "no_street": 121}
AMBIGUOUS_CONTROLS = ("SITE-000043", "SITE-000060")
spec = importlib.util.spec_from_file_location("sprint", SPRINT / "build.py")
B = importlib.util.module_from_spec(spec)
spec.loader.exec_module(B)
from derive_last_activity import _units
from regions import PIC18

STREET_SOURCES = {
    "echo_frs": "registry_id", "echo_air": "pgm_sys_id", "echo_rcra": "id_number",
    "echo_npdes": "icis_facility_interest_id", "sam": "uei",
    "form5500_loc": "ack_id", "form5500_sf_loc": "ack_id",
}
ALIASES = {
    "sam": ("sam/sam_entities.parquet", "f012_legal_business_name", "f013_dba_name", "r_sam_pass"),
    "fmcsa": ("fmcsa/fmcsa_census.parquet", "LEGAL_NAME", "DBA_NAME", ""),
    "5500": ("form5500/form5500_main_*.parquet", "SPONSOR_DFE_NAME", "SPONS_DFE_DBA_NAME", ""),
    "5500_SF": ("form5500/form5500_sf_*.parquet", "SF_SPONSOR_NAME", "SF_SPONSOR_DFE_DBA_NAME", ""),
}
PDF_LOCATION = re.compile(r"^\s*(?:Facility|Site|Premises?)\s+(?:Street Address|Physical Address|Address|Location)\s*:\s*(.*)$", re.I)
PDF_NAME = re.compile(r"^\s*(?:Facility|Site|Premises?)\s+Name\s*:\s*(.+)$", re.I)
PDF_CITY = re.compile(r"^\s*([^,]+),\s*(?:OH|Ohio)\s+(\d{5})(?:-\d{4})?\s*$", re.I)


def sqlstr(value):
    return "'" + value.replace("'", "''") + "'"


def values(items):
    return "(" + ",".join(sqlstr(v) for v in sorted(set(items) - {""})) + ",'')"


def select(lake, queries):
    code = (lake / "views.sql").read_text() + "\n" + " UNION ALL ".join(queries) + ";"
    result = subprocess.run(["duckdb", "-batch", "-json"], cwd=lake, input=code, text=True, capture_output=True)
    if result.returncode:
        raise RuntimeError("DuckDB held-source query failed; inspect view/schema compatibility")
    return json.loads(result.stdout or "[]")


def own(held):
    return {key: val for key, val in held.items() if not val.startswith("parent:")}


def bind(held, names):
    return B.RANK[B.name_class(held, names)[0]] >= 2


def nonpersonal(name):
    return bool(name and not B.personal(name) and not re.search(r"\bsole propriet(?:or|orship)\b", name, re.I))


class Lane:
    def __init__(self, store, cache):
        self.store = store
        self.lake = store / "lake/2026-11-22"
        self.orgs, sites = B.load_atlas()
        self.sites = {s["site_id"]: s for s in sites}
        assert len(self.sites) == len(sites)
        self.active = [s for s in sites if s["operating_status"] == "active"]
        self.active_n = Counter(s["org_id"] for s in self.active)
        self.by_street, self.by_name, self.ix = defaultdict(list), defaultdict(list), {}
        for s in self.active:
            s["_held"] = B.held_names(s, self.orgs)
            if s["street_address"]:
                self.by_street[B.street_key(s["street_address"])].append(s)
        for kind, filename in (("ita", "ita_oh.csv"), ("insp", "insp_oh.csv")):
            rows = B.unify(B.rd(cache / filename), kind)
            self.ix[kind] = B.index(rows)
            for entry in rows:
                keys = {B.coll(B.name_key(n)).split()[0] for n in entry["names"] if B.name_key(n)}
                for key in keys:
                    self.by_name[key].append(entry)
        self.manifest = {line.split("  ", 1)[1].removeprefix("./"): line.split("  ", 1)[0]
                         for line in (store / "raw/MANIFEST.sha256").read_text().splitlines()}

    def cite(self, path, ordinal):
        return {"path": "raw/" + path, "row": str(ordinal), "sha256": self.manifest[path.split("!", 1)[0]]}

    def ocite(self, entry):
        r = entry["r"]
        return self.cite(r["file"] + ("!" + r["member"] if r["member"] else ""), r["row"])

    def street_rows(self, sites):
        cities, zips = values(B.squash(s["city"]) for s in sites), values(B.zip5(s["zip"]) for s in sites)
        queries = []
        for src, native_id in STREET_SOURCES.items():
            alt = "dba_name" if src == "sam" else "''"
            extra = " AND r_sam_pass" if src == "sam" else ""
            queries.append(f"""SELECT '{src}' AS kind, src_path AS path, src_row AS ordinal, {native_id} AS native_id,
                  name, {alt} AS alt, street_raw AS street, std_city_norm AS city, std_zip5 AS zip
                FROM {src} WHERE std_state='OH' AND std_street_ok {extra}
                AND ((std_city_norm <> '' AND std_city_norm IN {cities}) OR (std_zip5 <> '' AND std_zip5 IN {zips}))""")
        return select(self.lake, queries)

    def permits(self):
        rows, checked = [], 0
        for p in sorted((self.store / "raw/permits-oh-air/2026-11-22").glob("*.pdf")):
            checked += 1
            result = subprocess.run(["pdftotext", "-layout", str(p), "-"], text=True, capture_output=True)
            if result.returncode:
                raise RuntimeError(f"air permit text extraction failed: {p.name}")
            for page_number, page in enumerate(result.stdout.split("\f"), 1):
                names = [m[1].strip() for line in page.splitlines() if (m := PDF_NAME.match(line))]
                if len(set(names)) != 1:
                    continue
                lines = page.splitlines()
                for i, line in enumerate(lines):
                    if not (m := PDF_LOCATION.match(line)):
                        continue
                    following = [x.strip() for x in [m[1], *lines[i + 1:i + 5]] if x.strip()]
                    preceding = [x.strip() for x in lines[max(0, i - 2):i] if x.strip()]
                    if not following:
                        continue
                    if place := PDF_CITY.match(following[0]):
                        # eDocPub labels the municipality line; the immediately preceding civic line is its street.
                        street = preceding[-1] if preceding else ""
                    elif len(following) > 1 and (place := PDF_CITY.match(following[1])):
                        street = following[0]
                    else:
                        continue
                    if not re.match(r"^\d+[A-Za-z-]*\s+[^:]+$", street) or not B.same_street(street, street):
                        continue
                    rows.append(dict(kind="oh_air_pdf", path=str(p.relative_to(self.store / "raw")),
                                     ordinal=f"page {page_number} line {i + 1}", name=names[0], alt="",
                                     city=place[1], zip=place[2], street=street, native_id=p.stem))
        return rows, checked

    def identity_rows(self, keys):
        norm = lambda col: f"regexp_replace(lower({col}), '[^a-z0-9]+', ' ', 'g')"
        prefixes = values(k.split()[0] for k in keys if k)
        queries = []
        for kind, (file, legal, dba, policy) in ALIASES.items():
            table = "sam" if kind == "sam" else f"read_parquet('{file}', union_by_name=true)"
            if kind == "sam":
                legal, dba = "name", "dba_name"
                location = ("street_raw", "std_city_norm", "std_state", "std_zip5")
            elif kind == "fmcsa":
                location = ("PHY_STREET", "k_site_city_norm", "k_site_state", "k_site_zip5")
            else:
                street = "SPONS_DFE_LOC_US_ADDRESS1" if kind == "5500" else "SF_SPONS_LOC_US_ADDRESS1"
                location = (street, "k_loc_city_norm", "k_loc_state", "k_loc_zip5")
            street, city, state, zipcode = location
            queries.append(f"""SELECT '{kind}' AS kind, src_path AS path, src_row AS ordinal,
                 {legal} AS legal, {dba} AS alias, '' AS charter, '' AS filing,
                 {street} AS street, {city} AS city, {state} AS state, {zipcode} AS zip
               FROM {table}
               WHERE coalesce(trim({dba}), '') <> '' {"AND " + policy if policy else ""}
               AND (split_part(trim({norm(legal)}), ' ', 1) IN {prefixes}
                 OR split_part(trim({norm(dba)}), ' ', 1) IN {prefixes})""")
        queries.append("""SELECT 'oh_sos' AS kind, src_path AS path, src_row AS ordinal,
               "BUSINESS NAME" AS legal, '' AS alias, trim("CHARTER NUMBER") AS charter,
               coalesce("TRANSACTION CODE DESCRIPTION","TRANSACTION CODE DESCIPTION",'') AS filing,
               '' AS street, "BUSINESS CITY" AS city, 'OH' AS state, '' AS zip
               FROM read_parquet('entity/entity_oh_*.parquet', union_by_name=true)
               WHERE coalesce(trim("CHARTER NUMBER"),'') <> '' """)
        return select(self.lake, queries)

    def osha_at(self, site):
        held = site["_held"]
        exact, notes = {}, {}
        for kind, index in self.ix.items():
            exact[kind], notes[kind] = B.classify(site, held, index)
        return exact, notes

    def band(self, site):
        pairs, notes = self.osha_at(site)
        pairs["f5500"] = []  # R13 source slot stays empty under the round-14 ruling.
        near = {k: v for k, rows in notes.items() if (v := B.would_be_band(k, rows))}
        return B.evaluate(site, "suffix", pairs, self.active_n, self.by_street, near, notes)

    def find_street(self, s, government):
        h = own(s["_held"])
        prefixes = {B.coll(k).split()[0] for k in h}
        matches, dates = {}, {}
        for prefix in prefixes:
            for r in self.by_name.get(prefix, ()):
                if B.city_ok(s, r["city"], r["zip"]) and bind(h, r["names"]) and B.same_street(r["st"], r["st"]):
                    if any(nonpersonal(n) and bind(h, [n]) for n in r["names"]):
                        c = self.ocite(r)
                        key = c["path"], c["row"]
                        matches[key] = (r["st"], c, r["kind"])
                        dates[key] = B.source_date(r)
        for r in government:
            names = [n for n in (r["name"], r["alt"]) if nonpersonal(n)]
            if names and B.city_ok(s, r["city"] or "", r["zip"] or "") and bind(h, names) and B.same_street(r["street"], r["street"]):
                c = self.cite(r["path"], r["ordinal"])
                matches[(c["path"], c["row"])] = (r["street"], c, r["kind"])
        groups = defaultdict(list)
        for row in matches.values():
            groups[B.street_key(row[0])].append(row)
        if len(groups) != 1:
            return ("MULTIPLE_STREETS" if groups else "NO_HELD_STREET", "", tuple(matches[k] for k in sorted(matches)))
        key, rows = next(iter(groups.items()))
        units = {frozenset(u) for st, _, _ in rows if (u := _units(st))}
        if len(units) > 1:
            return "MULTIPLE_UNITS", "", tuple(rows)
        rows.sort(key=lambda r: (r[1]["path"], r[1]["row"]))
        rows.sort(key=lambda r: (bool(_units(r[0])), dates.get(evidence_key(r[1]), "")), reverse=True)
        selected = rows[0][0]
        occupied = any(other["site_id"] != s["site_id"] and other["org_id"] == s["org_id"]
                       and B.city_ok(s, other["city"], other["zip"]) and B.same_street(selected, other["street_address"])
                       for other in self.by_street[key])
        if occupied:
            return "ALREADY_HELD_SIBLING_STREET", "", tuple(rows)
        return "STREET_FOUND", selected, tuple(rows)

    def classify_name(self, site, identities, known=False):
        h = own(site["_held"])
        parent = {k: v for k, v in site["_held"].items() if v.startswith("parent:")}
        pairs, _ = self.osha_at(site)
        potential = [e for rows in pairs.values() for e, _, _ in rows]
        if known:
            matched = [e for e in potential if B.fresh(e) and any(nonpersonal(n) and bind(h, [n]) for n in e["names"])]
            if matched:
                return "ALREADY_HELD", "", "Exact held operator and site street in a fresh OSHA row", [self.ocite(matched[-1])]
        eligible = [(e, n) for e in potential for n in e["names"]
                    if nonpersonal(n) and not bind(h, [n]) and not B.parent_match(parent, [n])]
        verified = []
        charters = defaultdict(list)
        for r in identities:
            if r["charter"]:
                charters[r["charter"]].append(r)
            tied_to_plant = (r["state"] == "OH" and r["street"] and B.same_street(site["street_address"], r["street"])
                             and B.city_ok(site, r["city"] or "", r["zip"] or ""))
            if tied_to_plant and nonpersonal(r["legal"]) and nonpersonal(r["alias"]):
                for mine, other in ((r["legal"], r["alias"]), (r["alias"], r["legal"])):
                    if bind(h, [mine]) and not B.parent_match(parent, [mine, other]):
                        verified.append((other, [r], "Explicit legal/DBA pairing on one public filing"))
        for group in charters.values():
            for mine in group:
                if (nonpersonal(mine["legal"]) and bind(h, [mine["legal"]])
                        and mine["city"] and B.squash(mine["city"]) == B.squash(site["city"])):
                    for other in group:
                        if other is not mine and nonpersonal(other["legal"]) and not B.parent_match(parent, [other["legal"]]):
                            verified.append((other["legal"], [mine, other], "Both public filings carry the same Ohio charter"))
        for alias, proof, reason in verified:
            found = [e for e, n in eligible if B.name_key(n) == B.name_key(alias)]
            if found:
                return ("SAME_COMPANY", alias, reason,
                        [self.cite(r["path"], r["ordinal"]) for r in proof] + [self.ocite(found[-1])])

        # Independent legal charters distinguish businesses; a shared street or different display name alone cannot.
        own_ch = {r["charter"]: r for group in charters.values() for r in group if bind(h, [r["legal"]])}
        for entry, other in eligible:
            foreign_ch = {r["charter"]: r for group in charters.values() for r in group if B.name_key(r["legal"]) == B.name_key(other)}
            if len(own_ch) == len(foreign_ch) == 1 and own_ch.keys().isdisjoint(foreign_ch):
                mine, tenant = next(iter(own_ch.values())), next(iter(foreign_ch.values()))
                # Merger, conversion, dissolution and cancellation notices cannot establish concurrent tenancy.
                articles = lambda r: r["filing"].startswith(("DOMESTIC ARTICLES", "ARTICLES OF ORGNZTN"))
                cities_agree = all(r["city"] and B.squash(r["city"]) == B.squash(site["city"]) for r in (mine, tenant))
                if cities_agree and articles(mine) and articles(tenant) and B.fresh(entry):
                    return ("OTHER_TENANT", "", "Distinct domestic formation charters and a fresh OSHA establishment filing at this street",
                            [self.ocite(entry), self.cite(mine["path"], mine["ordinal"]),
                             self.cite(tenant["path"], tenant["ordinal"])])
        reason = ("Ohio SOS charter history, registered DBA or merger instrument tying the OSHA filer to this operator"
                  if eligible else "Matching OSHA filing row or public site/operator record resolving the original street/identity lead")
        return "STILL_UNCERTAIN", "", reason, [self.ocite(e) for e in potential[-4:]]


def wilson(k, n):
    z = 1.959963984540054
    p = k / n
    center = (p + z * z / (2 * n)) / (1 + z * z / n)
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / (1 + z * z / n)
    return max(0, center - half), min(1, center + half)


def pack(citations):
    return "|".join(f"{r['path']}@{r['row']}#{r['sha256']}" for r in citations)


def evidence_key(r):
    return r["path"], r["row"]


def result_band(lane, site):
    result = lane.band(site)
    if result[0] == "fill":
        return result[1]["band"], result[1]["source"], pack([lane.ocite(result[1]["e"])]), ""
    return "", "", "", result[1] if result[0] == "hold" else "no_osha_band_at_street"


def controls(lane, permit_rows):
    issued = sorted(B.rd(SPRINT / "packet.csv"), key=lambda row: row["site_id"])[:12]
    gov = lane.street_rows([lane.sites[p["site_id"]] for p in issued]) + permit_rows
    for sid in AMBIGUOUS_CONTROLS:
        site = lane.sites[sid]
        status, _, refs = lane.find_street(dict(site, street_address=""), gov)
        assert status == "MULTIPLE_STREETS", f"{sid}: ambiguous hidden-street guard failed"
        assert any(B.same_street(r[0], site["street_address"]) for r in refs), f"{sid}: ambiguity guard lost the known street"
    out = []
    for old in issued:
        sid = old["site_id"]
        site = lane.sites[sid]
        identity, _, _, _ = lane.classify_name(site, [], known=True)
        status, street, supports = lane.find_street(dict(site, street_address=""), gov)
        assert identity == "ALREADY_HELD", f"{sid}: positive identity control failed"
        if status != "STREET_FOUND":
            continue
        assert B.same_street(street, site["street_address"]), f"{sid}: positive street control supplied a different street"
        band, source, cite, why = result_band(lane, dict(site, street_address=street))
        assert (source, band) == (old["source"], old["band"]), f"{sid}: positive band control failed ({why})"
        out.append(dict(site_id=sid, identity=identity, street=status, band=band, source=source, band_witness=cite,
                        street_witness=pack([supports[0][1]])))
        if len(out) == 3:
            return out
    raise ValueError("fewer than three unambiguous known answers in the first 12 #468 fills")


def compute(lane, permit_rows):
    holds = B.rd(SPRINT / "holds.csv")
    assert len(holds) == len({h["site_id"] for h in holds}) == 415
    fr0, fr1 = [sorted((h for h in holds if h["reason"] == key), key=lambda h: h["site_id"]) for key in FRAMES]
    assert (len(fr0), len(fr1)) == (96, 121)
    name_sample, street_sample = [random.Random(SEED).sample(f, 20) for f in (fr0, fr1)]
    gov = lane.street_rows([lane.sites[h["site_id"]] for h in street_sample]) + permit_rows
    sites = [lane.sites[h["site_id"]] for h in name_sample]
    keys = set().union(*(set(s["_held"]) for s in sites))
    for site in sites:
        pairs, _ = lane.osha_at(site)
        keys.update(B.name_key(n) for rows in pairs.values() for e, _, _ in rows for n in e["names"])
    identities = lane.identity_rows(keys)
    nresults, sresults = [], []
    for sample in name_sample:
        site = lane.sites[sample["site_id"]]
        cls, alias, why, refs = lane.classify_name(site, identities)
        band = source = witness = reason = ""
        if cls == "SAME_COMPANY":
            held = dict(site["_held"], **{B.name_key(alias): alias})
            band, source, witness, reason = result_band(lane, dict(site, _held=held))
        families = sorted(set(re.findall(r"\[(ita|insp|f5500)\]", sample["detail"])))
        if families == ["f5500"] and cls == "STILL_UNCERTAIN":
            why = "Original hold lists only a Form 5500 lead; an exact-plant OSHA filing would establish a size route"
        nresults.append(dict(site_id=site["site_id"], org_id=site["org_id"], result=cls, finding=why,
                             original_source_families=";".join(families),
                             witness=pack(refs), band=band, band_source=source, band_witness=witness, band_hold=reason))
    for sample in street_sample:
        site = lane.sites[sample["site_id"]]
        cls, street, refs = lane.find_street(site, gov)
        band = source = witness = reason = ""
        if cls == "STREET_FOUND":
            band, source, witness, reason = result_band(lane, dict(site, street_address=street))
        sresults.append(dict(site_id=site["site_id"], org_id=site["org_id"], result=cls,
                             street_sources=";".join(sorted({r[2] for r in refs})),
                             street_witness=pack([refs[0][1]]) if cls == "STREET_FOUND" else "",
                             witness=pack(sorted({evidence_key(r[1]): r[1] for r in refs}.values(), key=evidence_key)[:8]),
                             band=band, band_source=source, band_witness=witness, band_hold=reason))
    return nresults, sresults


def metrics(lane, controls_rows, names, streets, permits_count, permit_blocks):
    stats = []
    for col, rows, total, labels in (("name_not_held", names, 96, ("SAME_COMPANY", "OTHER_TENANT", "STILL_UNCERTAIN")),
                                    ("no_street", streets, 121, ("STREET_FOUND", "NO_HELD_STREET", "MULTIPLE_STREETS",
                                                                "MULTIPLE_UNITS", "ALREADY_HELD_SIBLING_STREET"))):
        assert len(rows) == len({r["site_id"] for r in rows}) == 20
        assert {r["result"] for r in rows} <= set(labels)
        for label in (*labels, "OSHA_BAND"):
            q = sum(bool(r["band"]) if label == "OSHA_BAND" else r["result"] == label for r in rows)
            lo, hi = wilson(q, 20)
            stats.append(dict(frame=col, result=label, count=q, n=20, total_sites=total,
                              wilson_low_pct=round(100 * lo, 1), wilson_high_pct=round(100 * hi, 1),
                              projected_sites=round(total * q / 20, 1),
                              projected_low=round(total * lo, 1), projected_high=round(total * hi, 1)))
    fr, n, unk = B.frame(lane.orgs, list(lane.sites.values()))
    assert (n, unk) == (794, 396)
    unknown = {s["org_id"] for s in fr}
    filled = {r["org_id"] for r in names + streets if r["band"]} & unknown
    name_frame = [r for r in B.rd(SPRINT / "holds.csv") if r["reason"] == "name_not_held"]
    original_5500_only = sum(not re.search(r"\[(ita|insp)\]", r["detail"]) for r in name_frame)
    return dict(seed=SEED, controls=len(controls_rows), permits_scanned=permits_count, labeled_permit_blocks=permit_blocks,
                name_frame_form5500_only=original_5500_only,
                name_sample_form5500_only=sum(r["original_source_families"] == "f5500" for r in names),
                outcome=dict(pic18_population=n, starting_unknown=unk, sampled_org_rows_unlocked=len(filled),
                             counterfactual_unknown=unk - len(filled), sampled_org_ids=sorted(filled)), canaries=stats)


def verify_raw(lane, controls_rows, names, streets):
    """Hash proposed evidence and reopen each selected OSHA witness in its original file."""
    citations = set()
    for r in controls_rows + streets:
        for key in ("street_witness", "band_witness"):
            if value := r.get(key):
                citations.add(value)
    for r in names:
        if r["result"] != "STILL_UNCERTAIN":
            citations.update(r["witness"].split("|"))
        if r["band_witness"]:
            citations.add(r["band_witness"])
    packed = {}
    for ref in sorted(citations):
        path, row_hash = ref.rsplit("@", 1)
        ordinal, sha = row_hash.split("#")
        file, _, member = path.partition("!")
        packed[ref] = (file, member, ordinal, sha)
    for file, sha in sorted({(r[0], r[3]) for r in packed.values()}):
        with (lane.store / file).open("rb") as src:
            assert hashlib.file_digest(src, "sha256").hexdigest() == sha, f"raw SHA mismatch: {file}"

    spec = importlib.util.spec_from_file_location("sprint_check", SPRINT / "check.py")
    check = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(check)
    osha = {ref: p for ref, p in packed.items() if p[0].startswith("raw/osha/")}
    requests = [dict(source_file=p[0], row_locator=f"{p[1]}|row={p[2]}|id=") for p in osha.values()]
    rows = check.fetch_rows(str(lane.store / "raw"), requests)
    entries = {}
    for ref, (file, member, ordinal, _) in osha.items():
        raw = rows[(file, member)].get(int(ordinal))
        assert raw is not None, f"missing raw row: {file}:{ordinal}"
        kind = "insp" if "inspection" in file else "ita"
        assert raw["site_state" if kind == "insp" else "state"].strip().upper() == "OH"
        entries[ref], = B.unify([raw], kind)
    for r in controls_rows + streets:
        site = lane.sites[r["site_id"]]
        street = entries.get(r.get("street_witness"))
        if street:
            assert bind(own(site["_held"]), street["names"]) and B.city_ok(site, street["city"], street["zip"])
            assert B.same_street(street["st"], street["st"]), f"{r['site_id']}: street witness has no civic street"
        if r.get("band"):
            e = entries[r["band_witness"]]
            assert B.band_of(B.count_of(e)) == r["band"] and B.fresh(e), f"{r['site_id']}: raw band/date mismatch"
            assert bind(own(site["_held"]), e["names"]) and B.city_ok(site, e["city"], e["zip"])
            if street:
                assert B.same_street(street["st"], e["st"]), f"{r['site_id']}: raw street/band binding mismatch"
    print(f"Verified {len({p[0] for p in packed.values()})} cited raw hashes and reopened {len(entries)} raw OSHA rows.", flush=True)



def save(path, rows, check):
    import io
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=list(rows[0]), lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    save_text(path, stream.getvalue(), check)


def save_text(path, text, check):
    if check:
        assert path.read_text() == text, f"replay differs: {path.name}"
    else:
        path.write_text(text)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--store", type=Path, default=STORE)
    parser.add_argument("--cache", type=Path, default=DEFAULT_CACHE)
    parser.add_argument("--controls-only", action="store_true")
    parser.add_argument("--check", action="store_true")
    a = parser.parse_args()
    lane = Lane(a.store, a.cache)
    permits, n = lane.permits()
    c = controls(lane, permits)
    print(f"Known answers: {len(c)} of 3 exact identities, streets and R13 size bands reproduced.", flush=True)
    save(HERE / "known_answers.csv", c, a.check)
    if a.controls_only:
        return
    names, streets = compute(lane, permits)
    m = metrics(lane, c, names, streets, n, len(permits))
    save(HERE / "name_canary.csv", names, a.check)
    save(HERE / "street_canary.csv", streets, a.check)
    save_text(HERE / "counts.json", json.dumps(m, indent=2) + "\n", a.check)
    print("Names:", Counter(r["result"] for r in names), "| Streets:", Counter(r["result"] for r in streets))
    print("PIC-18 outcome:", m["outcome"])
    if a.check:
        verify_raw(lane, c, names, streets)


if __name__ == "__main__":
    main()

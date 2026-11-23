#!/usr/bin/env python3
"""PIC-18 evidence queue (V-65 / V-68) from the NAS Parquet lake: frame, candidates, one witness per missing claim.

  cd <repo> && uv run --with duckdb --with numpy python tasks/pic18-evidence-queue-2026-11-22/build.py [--canary]

Reads: repo data/*.csv at HEAD; the lake at LAKE (read-only). Writes frame.csv, packet.csv, leads.csv, discards.csv, stats.json
next to this file (canary: under canary/). A quote is built by code from the source record's own fields; no model writes one.
"""
import csv
import glob
import json
import os
import random
import re
import subprocess
import sys
from collections import Counter, defaultdict
from datetime import date, datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import binding as B  # noqa: E402
from binding import ROOT  # noqa: E402
from regions import PIC18  # noqa: E402
from atlas import squash, name_key, street_key  # noqa: E402
from derive_last_activity import has_civic_number  # noqa: E402

LAKE = Path(os.environ.get("ATLAS_LAKE", "/Volumes/johnpswan/work/GAC/polymer-atlas/atlas-store/lake/2026-11-22"))
TODAY = date(2026, 11, 22)
STALE_BEFORE = date(2021, 11, 22)          # a filing older than five years is never the only witness
CREATED_BY = "claude-code pic18-evidence-queue-2026-11-22"
SEED = 20261122
RANK = {"supports_U": 0, "supports_C": 1, "supports_B": 2, "supports_A": 3}
EFFECT = {v: k for k, v in RANK.items()}
CLAIMS = ("existence", "address")


def rd(pattern):
    for f in sorted(glob.glob(str(ROOT / "data" / pattern))):
        with open(f, newline="", encoding="utf-8") as fh:
            yield from csv.DictReader(fh)


def parse_date(s):
    """ISO date (first 10 chars), m/d/yyyy [time], yyyymmdd (SAM), or the ITA CY2021 form 01APR22:00:04:00 (first 7 chars)."""
    s = (s or "").strip()
    if re.fullmatch(r"\d{2}[A-Z]{3}\d{2}:.*", s):
        try:
            return datetime.strptime(s[:7], "%d%b%y").date()
        except ValueError:
            return None
    for fmt, n in (("%Y-%m-%d", 10), ("%m/%d/%Y", None), ("%Y%m%d", 8)):
        try:
            return datetime.strptime(s[:n] if n else s.split(" ")[0], fmt).date()
        except ValueError:
            pass
    return None


# ------------------------------------------------------------------------------------------------ frame
def load():
    orgs = {o["org_id"]: o for o in rd("organizations_*.csv")}
    sites = {s["site_id"]: s for s in rd("sites_*.csv")}
    ev = list(rd("evidence_*.csv"))
    ap = HERE / "applied_ids.csv"       # after apply.py the frame is rebuilt as it was before: this packet's own rows are not counted
    if ap.exists():
        done = {r["evidence_id"] for r in csv.DictReader(open(ap, newline="", encoding="utf-8"))}
        ev = [r for r in ev if r["evidence_id"] not in done]
    return orgs, sites, ev


REGION = "pic18"   # "pic18" | "oh_rest" (Ohio outside PIC-18); set by --region


def in_region(state, county):
    return state == "OH" and ((county in PIC18) if REGION == "pic18" else (county not in PIC18))


def build_frame(orgs, sites, ev):
    """PIC-18 records in V-65 (tier A/B, best supporting row below the tier's strength) or V-68 (tier not A/B, no evidence row at
    all). Sites: state OH and county in PIC-18. Organizations: hq_state OH and hq_county in PIC-18 (an org with HQ elsewhere and a
    PIC-18 site is outside PIC-18 for this lane and is counted in stats). Merged orgs are out of V-65 but in V-68 (tombstones)."""
    best, has = {}, set()
    claim_best = defaultdict(lambda: -1)          # (table, id, claim) -> best supporting rank
    contra = defaultdict(set)
    for r in ev:
        k = (r["record_table"], r["record_id"])
        has.add(k)
        v = RANK.get(r["tier_effect"], -1)
        if r["tier_effect"] == "contradicts":
            contra[k].add(r["claim_type"])
        elif v >= 0:
            best[k] = max(best.get(k, -1), v)
            claim_best[k + (r["claim_type"],)] = max(claim_best[k + (r["claim_type"],)], v)
    rows = []

    def add(table, rid, rec, tier, status_excl, in_scope):
        k = (table, rid)
        if tier in ("A", "B"):
            if status_excl or best.get(k, -1) >= (3 if tier == "A" else 2):
                return
            rule, need = "V-65", 3 if tier == "A" else 2
        else:
            if k in has:
                return
            rule, need = "V-68", RANK["supports_C"] if tier == "C" else RANK["supports_U"]
        rows.append(dict(record_table=table, record_id=rid, tier=tier or "(blank)", rule=rule, need_rank=need,
                         existing_rows=sum(1 for r in ev if (r["record_table"], r["record_id"]) == k) if k in has else 0,
                         **{f"best_{c}": (EFFECT.get(claim_best[k + (c,)], "") if claim_best[k + (c,)] >= 0 else "") for c in CLAIMS},
                         contradicted=";".join(sorted(contra[k]))))

    for sid, s in sorted(sites.items()):
        if in_region(s["state"], s["county"]):
            add("sites", sid, s, s["verification_tier"], False, True)
    outside = 0
    for oid, o in sorted(orgs.items()):
        if in_region(o["hq_state"], o["hq_county"]):
            add("organizations", oid, o, o["verification_tier"], o["status"] == "merged", True)
    return rows


# ------------------------------------------------------------------------------------------------ candidates
# One pool per family: Ohio rows whose city or ZIP5 is a city/ZIP of interest. Street, name and unit binding is done in Python
# (binding.py) so that the same functions replay in check.py. `role` is the address role of the source row.
POOL_SQL = {
    "osha_inspection": ("SELECT src_path, src_sha256, src_row, ACTIVITY_NR AS rid, ESTAB_NAME AS name, k_estab_name_key AS nk, SITE_ADDRESS AS street, "
                        "SITE_CITY AS city, SITE_STATE AS state, SITE_ZIP AS zip, OPEN_DATE AS d, 'physical' AS role "
                        "FROM read_parquet('osha/osha_inspection_chunk*.parquet', union_by_name=true) "
                        "WHERE k_site_state = 'OH' AND k_site_street_ok AND (k_site_city_norm IN (SELECT v FROM want_cities) OR k_site_zip5 IN (SELECT v FROM want_zips))"),
    "osha_ita": ("SELECT src_path, src_sha256, src_row, id AS rid, establishment_name AS name, k_estab_name_key AS nk, street_address AS street, "
                 "city, state, zip_code AS zip, coalesce(created_timestamp, date_submitted) AS d, 'physical' AS role "
                 "FROM read_parquet('osha/osha_ita_*.parquet', union_by_name=true) "
                 "WHERE k_site_state = 'OH' AND k_site_street_ok AND (k_site_city_norm IN (SELECT v FROM want_cities) OR k_site_zip5 IN (SELECT v FROM want_zips))"),
    "form5500_main_loc": ("SELECT src_path, src_sha256, src_row, ACK_ID AS rid, SPONSOR_DFE_NAME AS name, k_sponsor_name_key AS nk, SPONS_DFE_LOC_US_ADDRESS1 AS street, "
                          "SPONS_DFE_LOC_US_CITY AS city, SPONS_DFE_LOC_US_STATE AS state, SPONS_DFE_LOC_US_ZIP AS zip, DATE_RECEIVED AS d, 'physical' AS role "
                          "FROM read_parquet('form5500/form5500_main_*.parquet', union_by_name=true) "
                          "WHERE k_loc_state = 'OH' AND k_loc_street_ok AND (k_loc_city_norm IN (SELECT v FROM want_cities) OR k_loc_zip5 IN (SELECT v FROM want_zips))"),
    "form5500_sf_loc": ("SELECT src_path, src_sha256, src_row, ACK_ID AS rid, SF_SPONSOR_NAME AS name, k_sponsor_name_key AS nk, SF_SPONS_LOC_US_ADDRESS1 AS street, "
                        "SF_SPONS_LOC_US_CITY AS city, SF_SPONS_LOC_US_STATE AS state, SF_SPONS_LOC_US_ZIP AS zip, DATE_RECEIVED AS d, 'physical' AS role "
                        "FROM read_parquet('form5500/form5500_sf_*.parquet', union_by_name=true) "
                        "WHERE k_loc_state = 'OH' AND k_loc_street_ok AND (k_loc_city_norm IN (SELECT v FROM want_cities) OR k_loc_zip5 IN (SELECT v FROM want_zips))"),
    "form5500_main_mail": ("SELECT src_path, src_sha256, src_row, ACK_ID AS rid, SPONSOR_DFE_NAME AS name, k_sponsor_name_key AS nk, SPONS_DFE_MAIL_US_ADDRESS1 AS street, "
                           "SPONS_DFE_MAIL_US_CITY AS city, SPONS_DFE_MAIL_US_STATE AS state, SPONS_DFE_MAIL_US_ZIP AS zip, DATE_RECEIVED AS d, 'mailing' AS role "
                           "FROM read_parquet('form5500/form5500_main_*.parquet', union_by_name=true) "
                           "WHERE k_mail_state = 'OH' AND k_mail_street_ok AND (k_mail_city_norm IN (SELECT v FROM want_cities) OR k_mail_zip5 IN (SELECT v FROM want_zips))"),
    "form5500_sf_mail": ("SELECT src_path, src_sha256, src_row, ACK_ID AS rid, SF_SPONSOR_NAME AS name, k_sponsor_name_key AS nk, SF_SPONS_US_ADDRESS1 AS street, "
                         "SF_SPONS_US_CITY AS city, SF_SPONS_US_STATE AS state, SF_SPONS_US_ZIP AS zip, DATE_RECEIVED AS d, 'mailing' AS role "
                         "FROM read_parquet('form5500/form5500_sf_*.parquet', union_by_name=true) "
                         "WHERE k_mail_state = 'OH' AND k_mail_street_ok AND (k_mail_city_norm IN (SELECT v FROM want_cities) OR k_mail_zip5 IN (SELECT v FROM want_zips))"),
    # held, never a row: the owner question on SAM's D&B flag (SOURCE_MAP.md); r_sam_pass is the owner's filter as the lake defines it
    "sam": ("SELECT src_path, src_sha256, src_row, src_key AS rid, f012_legal_business_name AS name, k_legal_name_key AS nk, f016_physical_address_line_1 AS street, "
            "f018_physical_address_city AS city, f019_physical_address_province_or_state AS state, f020_physical_address_zip_postal_code AS zip, f010_last_update_date AS d, 'physical' AS role "
            "FROM read_parquet('sam/sam_entities.parquet') "
            "WHERE k_site_state = 'OH' AND k_site_street_ok AND coalesce(trim(f024_d_b_open_data_flag), '') <> 'Y' AND coalesce(trim(f122_entity_evs_source), '') <> 'D&B' "
            "AND f010_last_update_date >= '20220404' AND (k_site_city_norm IN (SELECT v FROM want_cities) OR k_site_zip5 IN (SELECT v FROM want_zips))"),
}
FAMILY_LABEL = {"osha_inspection": "OSHA establishment inspection", "osha_ita": "OSHA ITA Form 300A establishment filing",
                "form5500_main_loc": "DOL EFAST2 Form 5500", "form5500_sf_loc": "DOL EFAST2 Form 5500-SF", "form5500_main_mail": "DOL EFAST2 Form 5500",
                "form5500_sf_mail": "DOL EFAST2 Form 5500-SF", "sam": "SAM.gov public entity extract"}
FAMILY_PREF = {"osha_ita": 0, "form5500_main_loc": 1, "form5500_sf_loc": 1, "osha_inspection": 2, "form5500_main_mail": 3, "form5500_sf_mail": 3, "sam": 9}


def lake_connect():
    import duckdb
    os.chdir(LAKE)
    return duckdb.connect()


def fetch_pool(con, cities, zips):
    con.execute("CREATE OR REPLACE TEMP TABLE want_cities(v VARCHAR)")
    con.executemany("INSERT INTO want_cities VALUES (?)", [(c,) for c in sorted(cities)])
    con.execute("CREATE OR REPLACE TEMP TABLE want_zips(v VARCHAR)")
    con.executemany("INSERT INTO want_zips VALUES (?)", [(z,) for z in sorted(zips)])
    pool = {}
    for fam, sql in POOL_SQL.items():
        cur = con.execute(sql)
        cols = [c[0] for c in cur.description]
        pool[fam] = [dict(zip(cols, r), fam=fam) for r in cur.fetchall()]
        print(f"  pool {fam}: {len(pool[fam])} rows", file=sys.stderr)
    return pool


# ------------------------------------------------------------------------------------------------ quote and row text
def addr_line(c, with_street=True):
    parts = [(c.get("street") or "").strip() if with_street else "", (c.get("city") or "").strip(),
             f"{(c.get('state') or '').strip()} {(c.get('zip') or '').strip()}".strip()]
    return ", ".join(p for p in parts if p)


def street_shown(table, c, own_sites):
    """The street line is quoted for a site and for a physical-role source. A mailing-role address (owner ruling 2026-11-22: it proves
    existence and city only) never shows its street: the quote carries name, city, state and ZIP."""
    return table == "sites" or c["role"] == "physical"


def quote(c, with_street=True):
    """Built from the source record's own establishment/entity name and address fields only. No person, phone, e-mail or home address."""
    return f"{(c['name'] or '').strip()} | {addr_line(c, with_street)}"


def source_ref(c):
    """A named source plus its identifier (SCHEMA 4.13); the raw path is in notes."""
    fam, lab = c["fam"], FAMILY_LABEL[c["fam"]]
    if fam == "osha_inspection":
        return f"{lab}, activity {c['rid']}"
    if fam == "osha_ita":
        return f"{lab}, ITA record id {c['rid']}"
    if fam.startswith("form5500"):
        return f"{lab} sponsor filing, ACK_ID {c['rid']}"
    return f"{lab}, {c['rid']}"


def row_notes(c, d):
    return (f"Replayable from the raw store: file raw/{c['src_path']} sha256 {c['src_sha256']}, row {c['src_row']} (1-based CSV record in the member file, "
            f"header not counted), source key {c['rid']}. Source record date {d.isoformat()} is observed_date. Quote built by code from the source row; "
            f"lake snapshot 2026-11-22.")


def make_row(table, rec, claim, c, d, basis, eff_rank, own_sites=()):
    """The packet row's text columns, from the repo record and the replayed source row. Shared with check.py so both build the same text."""
    q = quote(c, street_shown(table, c, own_sites))
    if table == "sites":
        detail = (f"site of '{basis.split(chr(39))[1]}' at recorded address; quote: {q}" if claim == "existence"
                  else f"street_address {rec['street_address']}, {rec['city']}, OH {rec['zip']} witnessed; quote: {q}")
        role = "physical" if claim == "address" else ""
    else:
        detail = (f"organization '{rec['legal_name']}' answers to a held name in the source; quote: {q}" if claim == "existence"
                  else f"hq_city/hq_state {rec['hq_city']}, {rec['hq_state']} as recorded (county {rec['hq_county']} not stated by the source"
                       + ("; mailing-role filing: city and state only, no street claimed" if c["role"] == "mailing" else "") + f"); quote: {q}")
        role = c["role"] if claim == "address" else ""
    return dict(record_table=table, record_id=rec.get("site_id") or rec["org_id"], claim_type=claim, claim_detail=detail, source_class="government_filing",
                source_ref=source_ref(c), observed_date=d.isoformat(), tier_effect=EFFECT[eff_rank], created_by=CREATED_BY, notes=row_notes(c, d), address_role=role,
                source_family=c["fam"], src_path_under_raw=c["src_path"], src_sha256=c["src_sha256"], src_row=c["src_row"], src_key=c["rid"],
                binding_basis=basis, quote=q)


PERSONAL = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+|\(?\b\d{3}\)?[-. ]\d{3}[-. ]\d{4}\b")


# ------------------------------------------------------------------------------------------------ selection
def pick(cands):
    """cands: [(c, d, basis)] that passed binding. Freshest wins; a filing older than five years is never the sole witness.
    -> (chosen | None, surplus list, stale list)"""
    fresh = [x for x in cands if x[1] and x[1] >= STALE_BEFORE]
    stale = [x for x in cands if x[1] and x[1] < STALE_BEFORE]
    if not fresh:
        return None, [], stale
    fresh.sort(key=lambda x: (-x[1].toordinal(), FAMILY_PREF[x[0]["fam"]], str(x[0]["rid"])))
    return fresh[0], fresh[1:], []


def main():
    global REGION
    canary = "--canary" in sys.argv
    if "--region" in sys.argv:
        REGION = sys.argv[sys.argv.index("--region") + 1]
        assert REGION in ("pic18", "oh_rest")
    out = HERE / ("canary" if canary else ("" if REGION == "pic18" else REGION))
    if "--out" in sys.argv:
        out = Path(sys.argv[sys.argv.index("--out") + 1])
    out.mkdir(parents=True, exist_ok=True)
    orgs, sites, ev = load()
    frame = build_frame(orgs, sites, ev)
    ids = [(f["record_table"], f["record_id"]) for f in frame]
    shuffled = sorted(ids)                                   # seeded shuffle of the sorted frame ids
    random.Random(SEED).shuffle(shuffled)
    canary_ids = set(shuffled[:25])
    work = [f for f in frame if not canary or (f["record_table"], f["record_id"]) in canary_ids]
    if "--frame-only" in sys.argv:
        c = Counter((f["record_table"], f["rule"], f["tier"]) for f in frame)
        print(REGION, len(frame), sorted(c.items()))
        return 0
    print(f"frame {len(frame)} records; working on {len(work)}", file=sys.stderr)

    org_sites = defaultdict(list)
    for sid, s in sites.items():
        if in_region(s["state"], s["county"]):
            org_sites[s["org_id"]].append(s)
    # cities and ZIP5s of interest: the frame sites', the frame orgs' HQ cities, and the own PIC-18 sites of frame orgs
    cities, zips = set(), set()
    for f in work:
        recs = [sites[f["record_id"]]] if f["record_table"] == "sites" else [orgs[f["record_id"]]] + org_sites.get(f["record_id"], [])
        for r in recs:
            for c in B.city_parts(r.get("city") or r.get("hq_city")):
                cities.add(c)
            z = (r.get("zip") or "")[:5]
            if z.isdigit():
                zips.add(z)
    con = lake_connect()
    pool = fetch_pool(con, cities, zips)
    by_street, by_city = defaultdict(list), defaultdict(list)
    for fam, rows in pool.items():
        for c in rows:
            by_street[street_key(c["street"])].append(c)
            by_city[squash(c["city"])].append(c)

    packet, leads, discards, frame_out = [], [], [], []
    date_bad, sam_holds = Counter(), Counter()
    cand_mail = []

    for f in work:
        table, rid = f["record_table"], f["record_id"]
        rec = sites[rid] if table == "sites" else orgs[rid]
        need = f["need_rank"]
        eff_rank = 3     # tier_effect describes the witness (controller ruling Q2): SCHEMA 4.13's class ceiling for government_filing is supports_A
        missing = [c for c in CLAIMS if RANK.get(f[f"best_{c}"], -1) < need]
        bound = {c: [] for c in CLAIMS}
        mail_bound = []
        reasons = Counter()

        def note_lead(c, why, claim=""):
            leads.append(lead(f, c["fam"], c, why, claim))
            reasons[why] += 1

        def dated(c):
            """parsed source date, or None after recording the unreadable-date reason (never filed as stale)."""
            d = parse_date(str(c["d"])) if c.get("d") else None
            if d is None:
                note_lead(c, "source_date_missing_or_unreadable")
                date_bad[c["fam"]] += 1
            return d

        if table == "sites":
            org = orgs.get(rec["org_id"])
            porg = orgs.get((org or {}).get("parent_org_id", ""))
            sk = street_key(rec["street_address"])
            civic = bool(sk) and has_civic_number(sk) and len(sk.split()) >= 2
            if not civic:
                reasons["site_has_no_civic_street"] += 1
            else:
                for c in by_street.get(sk, []):
                    verdict, why = B.bind_site(rec, org, c, porg)
                    if verdict != "ok":
                        note_lead(c, why)
                    elif c["fam"] == "sam":
                        sam_holds["sites"] += 1
                        note_lead(c, "sam_held_owner_question_dnb_flag")
                    elif (d := dated(c)) is not None:
                        for claim in missing:
                            bound[claim].append((c, d, why))
            # name + city match at a different street (the reverted batch-5 route): a lead, never a row
            held = B.held_names(rec, org, porg)
            for c in by_city.get(squash(re.sub(r"\(.*?\)", " ", rec["city"])), []):
                if c["role"] == "physical" and B.match_held(name_key(c["name"]), held) and not B.same_street(rec["street_address"], c["street"]):
                    note_lead(c, "held_name_in_the_same_city_at_a_different_street" if civic else "held_name_in_the_same_city_site_has_no_street")
        else:
            own = org_sites.get(rid, [])
            porg = orgs.get(rec.get("parent_org_id", ""))
            pool_o = by_city.get(squash(re.sub(r"\(.*?\)", " ", rec["hq_city"])), []) + [x for s in own for x in by_street.get(street_key(s["street_address"]), [])]
            seen_o = set()
            for c in pool_o:
                if (c["fam"], c["src_path"], c["src_row"]) in seen_o:
                    continue
                seen_o.add((c["fam"], c["src_path"], c["src_row"]))
                v, why = B.bind_org_existence(rec, c, own, porg)
                if v != "ok":
                    if why in ("different_entity_trade_name", "source_name_looks_like_a_natural_person", "name_is_recorded_parent_only") and (squash(c["city"]) in B.city_parts(rec["hq_city"])):
                        note_lead(c, why, "existence")
                    continue
                if c["fam"] == "sam":
                    sam_holds["organizations"] += 1
                    note_lead(c, "sam_held_owner_question_dnb_flag", "existence")
                    continue
                d = dated(c)
                if d is None:
                    continue
                bound["existence"].append((c, d, why))
                v2, why2 = B.bind_org_address(rec, c, own, porg)
                if v2 == "ok":
                    bound["address"].append((c, d, why2))
                else:
                    v3, why3 = B.bind_org_address(rec, c, own, porg, allow_mailing=True)
                    if v3 == "ok":
                        mail_bound.append((c, d, why3))
                    else:
                        note_lead(c, why2, "address")
        wrote = {}
        for claim in missing:
            seen, cands = set(), []
            for x in bound[claim]:
                if (x[0]["fam"], x[0]["src_row"], x[0]["src_path"]) not in seen:
                    seen.add((x[0]["fam"], x[0]["src_row"], x[0]["src_path"])); cands.append(x)
            chosen, surplus, stale = pick(cands)
            for c, d, why in stale:
                note_lead(c, "stale_filing_older_than_five_years_would_be_the_sole_witness", claim)
            for c, d, why in surplus:
                discards.append(dict(record_table=table, record_id=rid, claim_type=claim, reason="second_witness_for_a_claim_already_witnessed",
                                     source_family=c["fam"], src_row=c["src_row"], src_key=c["rid"], date=d))
            if chosen is None:
                continue
            c, d, basis = chosen
            row = make_row(table, rec, claim, c, d, basis, eff_rank, org_sites.get(rid, []) if table == "organizations" else ())
            row["rule"] = f["rule"]
            row["street_in_atlas"] = int(any(B.same_street(s["street_address"], c["street"]) for s in (org_sites.get(rid, []) if table == "organizations" else [rec])))
            packet.append(row)
            wrote[claim] = True
        if "address" in missing and "address" not in wrote and mail_bound and table == "organizations":
            seen_m, cm = set(), []
            for x in mail_bound:
                if (x[0]["fam"], x[0]["src_row"], x[0]["src_path"]) not in seen_m:
                    seen_m.add((x[0]["fam"], x[0]["src_row"], x[0]["src_path"])); cm.append(x)
            chosen, surplus, stale = pick(cm)
            for c, d, why in surplus:
                discards.append(dict(record_table=table, record_id=rid, claim_type="address", reason="second_witness_for_a_claim_already_witnessed",
                                     source_family=c["fam"], src_row=c["src_row"], src_key=c["rid"], date=d))
            if chosen:
                c, d, basis = chosen
                row = make_row(table, rec, "address", c, d, basis, eff_rank, org_sites.get(rid, []))
                row["rule"] = f["rule"]
                row["street_in_atlas"] = 0
                cand_mail.append(row)
        if not wrote:
            if not reasons:
                reasons["no_source_record_at_the_street" if table == "sites" else "no_held_name_record_at_the_hq_city_or_own_site_street"] += 1
        frame_out.append(dict(f, name=rec.get("site_name") or rec["legal_name"], street=rec.get("street_address", ""),
                              city=rec.get("city") or rec.get("hq_city"), county=rec.get("county") or rec.get("hq_county"),
                              missing_claims=";".join(missing), rows_written=len(wrote), claims_cured=";".join(sorted(wrote)),
                              record_cured=int(bool(wrote)), address_only_by_mailing_reading=int("address" in missing and "address" not in wrote and any(r["record_id"] == rid for r in cand_mail)),
                              no_row_reasons=";".join(f"{k}:{v}" for k, v in sorted(reasons.items())) if not wrote else ""))

    def wr(name, rows, cols=None):
        cols = cols or (list(rows[0].keys()) if rows else [])
        with open(out / name, "w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=cols, lineterminator="\n")
            w.writeheader()
            w.writerows(rows)
    PRIVATE = Path(os.environ.get("PIC18_PRIVATE_DIR", "/Users/johnswanson/.bb/thread-storage/thr_9i2c6byhcz/2026-11-06-atlas/persist/pic18-evidence-2026-11-22"))
    if not canary and REGION == "pic18":
        PRIVATE.mkdir(parents=True, exist_ok=True)
    else:
        PRIVATE = out / "_private_not_for_repo"
        PRIVATE.mkdir(exist_ok=True)
    LEAD_COLS = ["record_table", "record_id", "claim_type", "source_family", "src_path_under_raw", "src_row", "src_key", "reason"]
    wr("frame.csv", frame_out)
    wr("packet.csv", packet)
    with open(PRIVATE / "candidates_mailing.csv", "w", newline="", encoding="utf-8") as fh:   # not delivered: owner ruling 2026-11-22 keeps street-level mailing rows out
        w = csv.DictWriter(fh, fieldnames=list(cand_mail[0].keys()) if cand_mail else ["none"])
        w.writeheader()
        w.writerows(cand_mail)
    wr("leads.csv", [{k: l[k] for k in LEAD_COLS} for l in leads], LEAD_COLS)          # ids, reasons and locators only: no third-party name or address
    wr("discards.csv", discards, ["record_table", "record_id", "claim_type", "reason", "source_family", "src_row", "src_key", "date"])
    with open(PRIVATE / "leads_with_source_names.csv", "w", newline="", encoding="utf-8") as fh:   # controller storage only
        w = csv.DictWriter(fh, fieldnames=LEAD_COLS + ["source_name", "source_address"], lineterminator="\n")
        w.writeheader()
        w.writerows(leads)
    held = Counter((l["record_id"], l["reason"]) for l in leads if l["reason"] in ("different_entity_trade_name", "source_name_looks_like_a_natural_person"))
    wr("held_filer_not_the_record.csv", [dict(record_id=k[0], reason=k[1], source_rows=n) for k, n in sorted(held.items())], ["record_id", "reason", "source_rows"])
    nolead = Counter(l["record_id"] for l in leads if l["reason"] == "held_name_in_the_same_city_site_has_no_street")
    ns = [dict(site_id=r["record_id"], site_name=r["name"], city=r["city"], county=r["county"], tier=r["tier"], rule=r["rule"],
               held_name_rows_in_same_city_as_leads=nolead.get(r["record_id"], 0)) for r in frame_out if "site_has_no_civic_street" in r["no_row_reasons"]]
    wr("sites_without_civic_street.csv", ns, ["site_id", "site_name", "city", "county", "tier", "rule", "held_name_rows_in_same_city_as_leads"])
    for nm in ("frame.csv", "packet.csv", "leads.csv", "discards.csv", "held_filer_not_the_record.csv", "sites_without_civic_street.csv"):
        txt = (out / nm).read_text(encoding="utf-8")
        hit = PERSONAL.findall(txt)
        assert not hit, f"{nm}: e-mail or phone-like strings {hit[:3]}"
    rec_strict = {(p["record_table"], p["record_id"]) for p in packet}
    both = {k for k in rec_strict if {p["claim_type"] for p in packet if (p["record_table"], p["record_id"]) == k} >= set(CLAIMS)}
    mail_ids = {("organizations", p["record_id"]) for p in cand_mail}
    json.dump(dict(region=REGION, frame=len(frame_out), date_unreadable_by_family=dict(date_bad), sam_holds=dict(sam_holds),
                   strict=dict(rows=len(packet), records_cured=len(rec_strict), records_with_both_claims=len(both)),
                   mailing_reading=dict(extra_address_rows=len(cand_mail), records_with_both_claims=len(both | mail_ids & rec_strict))), open(out / "stats.json", "w"), indent=1)
    print(f"date unreadable {dict(date_bad)}; sam holds {dict(sam_holds)}; mailing candidates {len(cand_mail)}")
    print(f"frame {len(frame_out)}; packet rows {len(packet)}; records with >=1 row {len(rec_strict)}; leads {len(leads)}; discarded {len(discards)}")
    return 0


SHOW_TEXT_REASONS = {"held_name_in_the_same_city_at_a_different_street", "held_name_in_the_same_city_site_has_no_street",
                     "mailing_role_only_not_a_physical_location_witness", "stale_filing_older_than_five_years_would_be_the_sole_witness",
                     "establishment_address_is_not_the_entitys_own_address", "quoted_city_state_is_not_the_recorded_hq", "source_date_missing_or_unreadable",
                     "sam_held_owner_question_dnb_flag", "quoted_location_is_not_the_recorded_hq_or_an_own_site_street", "name_is_recorded_parent_only",
                     "different_entity_trade_name", "mailing_role_address_owner_question_q1"}


def lead(f, fam, c, reason, claim=""):
    """Name and address text only where the source's name is a held name of the record (or the parent's); otherwise path, row, key and reason
    only: another tenant's or filer's name and address never enter a repo-bound file."""
    show = reason in SHOW_TEXT_REASONS and not B.looks_like_person(c.get("name") or "")   # unknown record context: suppress on the stricter test
    return dict(record_table=f["record_table"], record_id=f["record_id"], claim_type=claim, source_family=fam, src_path_under_raw=c["src_path"],
                src_row=c["src_row"], src_key=c["rid"], source_name=(c.get("name") or "").strip() if show else "",
                source_address=addr_line(c, c["role"] == "physical") if show else "", reason=reason)


if __name__ == "__main__":
    sys.exit(main())

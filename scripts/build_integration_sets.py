#!/usr/bin/env python3
"""Build integration-ready change sets from the PIC-12 capability packets and the
employee-band proposals (2026-11-01).  Stdlib only.  Re-runnable.

PACKET-LANE TOOL: it READS data/ and tasks/ and WRITES only
tasks/integration-ready-2026-11-01/.  It never writes under data/ (AGENTS.md
section 2 rule 7), never allocates an ID (evidence_id stays `<ALLOC>`), never
commits or pushes.  The dry run copies data/ to a temp directory, applies the
sets there, validates the copy, and deletes it.

  python3 scripts/build_integration_sets.py                # build + dry run
  python3 scripts/build_integration_sets.py --no-dryrun    # build only
  python3 scripts/build_integration_sets.py --tmp-root DIR # where the temp copy lives

Inputs (all read-only):
  tasks/pilot-pic12-capabilities-2026-11-01/{packet,verdicts}.csv
  tasks/wave-pic12-capabilities-2026-11-01/{lane*,t2_lane*}/{packet,verdicts}.csv
  tasks/osha-ita-2026-11-01/band_proposals.csv       (R13 source 1)
  tasks/osha-spine-2026-11-01/band_proposals.csv     (R13 source 2, OSHA inspection)
  tasks/form5500-spine-2026-11-01/band_proposals.csv (R13 source 3, R7f)
  docs/schema/vocab.json                              (vocabulary and its order)

Design decisions (restated in the generated README.md):
  * Vocabulary order = the order of the value lists in docs/schema/vocab.json.
  * A field whose CURRENT value holds any off-vocabulary token is never merged
    mechanically: it is REVIEW_EXISTING_OFFVOCAB and goes to conflicts.csv.
  * Sites have NO certifications column (checked from the sites header).  Site-
    scope certifications are routed to a site-notes append (`CERT-SITE:`),
    following the R12 precedent of recording certification facts in site notes;
    they are never pushed up to organizations.certifications (Parker rule).
    Org-scope certifications go to organizations.certifications.
  * Neither sites nor organizations carry an employee_count_source_date column,
    so the R13 source date travels in a `BAND-SOURCE:` notes append and in
    band_updates.csv.
"""
import argparse
import csv
import glob
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from collections import Counter, OrderedDict, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
# --packets / --out let the same builder run on other capability waves (e.g. the
# rest-of-Ohio + PA lanes); defaults reproduce the PIC-12 build.
_pre = argparse.ArgumentParser(add_help=False)
_pre.add_argument("--packets", nargs="+", help="packet directories or globs (repo-relative)")
_pre.add_argument("--out", help="output directory (repo-relative or absolute)")
_PRE, _ = _pre.parse_known_args()
OUT = Path(_PRE.out).resolve() if _PRE.out else ROOT / "tasks" / "integration-ready-2026-11-01"
CREATED_BY = "claude-code-integration-prep-2026-11-01"
ALLOC = "<ALLOC>"
csv.field_size_limit(10 ** 8)

if _PRE.packets:
    PACKET_DIRS = sorted({str(Path(p).relative_to(ROOT)) for g in _PRE.packets for p in glob.glob(str(ROOT / g))
                          if (Path(p) / "packet.csv").exists()})
else:
    PACKET_DIRS = ["tasks/pilot-pic12-capabilities-2026-11-01"] + sorted(
        str(Path(p).relative_to(ROOT)) for p in glob.glob(str(ROOT / "tasks/wave-pic12-capabilities-2026-11-01/*lane*"))
        if (Path(p) / "packet.csv").exists())
ITA_PATH = ROOT / "tasks/osha-ita-2026-11-01/band_proposals.csv"
INSP_PATH = ROOT / "tasks/osha-spine-2026-11-01/band_proposals.csv"
F5500_PATH = ROOT / "tasks/form5500-spine-2026-11-01/band_proposals.csv"
BATTERY = ROOT / "tasks/OWNER_BATTERY_2026-11-01.md"

# ---------------------------------------------------------------- vocabulary
_V = json.loads((ROOT / "docs/schema/vocab.json").read_text(encoding="utf-8"))["vocabularies"]
VOC_FIELDS = OrderedDict([("processes", "PROCESSES"), ("materials", "MATERIALS"),
                          ("markets_served", "MARKETS"), ("certifications", "CERTS")])
VOC = {f: list(_V[k]["values"]) for f, k in VOC_FIELDS.items()}
VOC_SET = {f: set(v) for f, v in VOC.items()}
VOC_RANK = {f: {t: i for i, t in enumerate(v)} for f, v in VOC.items()}
BANDS = ["1-9", "10-49", "50-99", "100-249", "250-499", "500-999", "1000-4999", "5000+"]
BAND_RANK = {b: i for i, b in enumerate(BANDS)}
OFF_FIELDS = {"processes_other_note": "processes", "materials_other_note": "materials",
              "markets_other_note": "markets_served", "certifications_other_note": "certifications"}
NON_PLANT_TYPES = {"hq_only", "sales_office", "warehouse_distribution", "office_other"}
EVD_HEADER = ["evidence_id", "record_table", "record_id", "claim_type", "claim_detail", "source_class",
              "source_ref", "observed_date", "tier_effect", "created_by", "notes"]
# SCHEMA 4.13 per-class ceiling: own_site / government_filing may carry supports_A.
OWN_SITE_EFFECT = "supports_A"
# validate.py V-23 source_ref tripwires, restated so a draft that would fail is held.
V23_PHANTOM = re.compile(r"verdict|working/|packets/|integration-pass", re.I)
V23_LICENSED = re.compile(r"plastics news|rubber news|dun & bradstreet|\bD&B\b|data axle|zoominfo", re.I)
EMAIL_RE = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")
PHONE_RE = re.compile(r"(?<!\d)(?:\+?1[\s.-]?)?\(?\d{3}\)?[\s.-]\d{3}[\s.-]\d{4}(?!\d)")

# v1.7.6 / v1.7.7 candidate hints for packets written before the 2026-11-01 vocabulary landed.
# A HINT only: the lane's proposed_value is a paraphrase; a lane re-pass or the integrator decides.
HINTS = [
    ("markets_served", r"automotive", r"oem|aftermarket", "automotive_unspecified"),
    ("markets_served", r"\btire|\btyre", None, "tire_rubber_goods"),
    ("markets_served", r"medical|health", r"device", "medical_healthcare_general"),
    ("markets_served", r"food", r"packag", "food_processing_foodservice"),
    ("markets_served", r"cosmetic|personal care", None, "cosmetics_personal_care"),
    ("markets_served", r"mining|metals|chemical process", None, "chemical_mining_metals_processing"),
    ("markets_served", r"\brv\b|powersport|trailer", None, "rv_powersports_trailers"),
    ("markets_served", r"telecom|datacom", None, "telecom_datacom"),
    ("markets_served", r"plastics? (and|&|/) rubber processor|upstream customer|plastics processor", None,
     "plastics_rubber_processors"),
    ("processes", r"thermoform", None, "thermoforming_unspecified"),
    ("processes", r"dry.?blend", None, "additive_dry_blending"),
    ("processes", r"pigment|colorant disper", None, "pigment_colorant_dispersion"),
    ("processes", r"pressure.sensitive tape", None, "pressure_sensitive_tape_manufacture"),
    ("processes", r"potting|encapsulat", None, "potting_encapsulation_casting"),
    ("processes", r"fluoropolymer lining|ptfe lin", None, "fluoropolymer_lining"),
    ("materials", r"\basa\b", None, "asa"),
    ("materials", r"hnbr|ffkm|\bcsm\b|butyl|fluorosilicone|\beco\b", None, "specialty_elastomers"),
    ("materials", r"vinyl ?ester|polyester resin", None, "polyester_vinyl_ester_resins"),
    ("materials", r"acrylic|pmma", None, "acrylic_pmma"),
    ("certifications", r"45001", None, "iso_45001"),
    ("certifications", r"17025", None, "iso_17025"),
]


# ---------------------------------------------------------------- helpers
def norm(s):
    return re.sub(r"\s+", " ", (s or "")).strip()


def tokens(s):
    return [t.strip() for t in (s or "").split(";") if t.strip()]


def read_rows(path):
    """Yield (first_physical_line, row_dict) for a CSV; first_physical_line is where the row starts."""
    with open(path, newline="", encoding="utf-8") as f:
        rdr = csv.DictReader(f)
        rdr.fieldnames  # noqa: B018  (forces the header read)
        prev = rdr.line_num
        for row in rdr:
            yield prev + 1, row
            prev = rdr.line_num


def load_table(prefix):
    rows, files = {}, OrderedDict()
    for f in sorted(DATA.glob(f"{prefix}_*.csv")):
        with open(f, newline="", encoding="utf-8") as fh:
            rdr = csv.DictReader(fh)
            files[f.name] = (list(rdr.fieldnames), [])
            for r in rdr:
                files[f.name][1].append(r)
                rows[r[rdr.fieldnames[0]]] = (f.name, r)
    return rows, files


def write_csv(path, header, rows):
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(header)
        for r in rows:
            w.writerow([r.get(h, "") for h in header])


def vocab_union(field, existing_in_vocab, new):
    return sorted(set(existing_in_vocab) | set(new), key=lambda t: VOC_RANK[field][t])


def hint_for(field, text):
    low = (text or "").lower()
    out = []
    for f, pat, excl, term in HINTS:
        if f != field:
            continue
        if re.search(pat, low) and not (excl and re.search(excl, low)):
            out.append(term)
    return ";".join(out)


# ---------------------------------------------------------------- load repo state
SITES, SITE_FILES = load_table("sites")
ORGS, ORG_FILES = load_table("organizations")
with open(DATA / "ecosystem.csv", newline="", encoding="utf-8") as _f:
    ECO_IDS = {r["org_id"] for r in csv.DictReader(_f)}
SITES_PER_ORG = Counter(r["org_id"] for _, r in SITES.values())
SITE_HEADER = next(iter(SITE_FILES.values()))[0]
ORG_HEADER = next(iter(ORG_FILES.values()))[0]
SITES_HAVE_CERT_COLUMN = "certifications" in SITE_HEADER
ORGS_HAVE_CERT_COLUMN = "certifications" in ORG_HEADER
assert all(c in ORG_HEADER for c in ("processes", "materials", "markets_served", "certifications", "employee_band_ohio"))
assert all(c in SITE_HEADER for c in ("processes", "materials", "markets_served", "employee_band_site"))

CONFLICTS = []


def conflict(cls, table, rid, field, value, detail, refs, disposition):
    CONFLICTS.append({"conflict_class": cls, "record_table": table, "record_id": rid, "field": field,
                      "value": value, "detail": norm(detail)[:700], "packet_refs": refs,
                      "suggested_disposition": disposition})


# ---------------------------------------------------------------- 1. read capability packets
VERDICTS = {}      # site_id -> verdict row (+lane)
ENTRIES = []       # in-vocab packet rows, one per single value
LANES_OF_ORG = defaultdict(set)
LANE_SITE_ORGS = defaultdict(set)   # lane -> parent org ids of that lane's assigned sites
RAW_ROWS = 0
for d in PACKET_DIRS:
    lane = "pilot" if "pilot" in d else Path(d).name
    for line, v in read_rows(ROOT / d / "verdicts.csv"):
        v["_lane"] = lane
        VERDICTS[v["site_id"]] = v
        LANE_SITE_ORGS[lane].add(v["org_id"])
    for line, p in read_rows(ROOT / d / "packet.csv"):
        RAW_ROWS += 1
        ref = f"{lane}/packet.csv:{line}"
        field = p["field"]
        if field in OFF_FIELDS:
            tgt = OFF_FIELDS[field]
            conflict("offvocab_note", "sites" if p["record_scope"] == "site" else "organizations", p["record_id"],
                     field, p["proposed_value"],
                     f"scope={p['record_scope']}; lane note: {p['notes']}; v1.7.6 candidate hint: "
                     f"{hint_for(tgt, p['proposed_value'] + ' ' + p['notes']) or 'none'}", ref,
                     "not applied (lane marked OFF-VOCAB). If the hint names a v1.7.6/v1.7.7 term, a lane "
                     "re-pass or the integrator re-reads the quoted page; never auto-mapped.")
            continue
        if field not in VOC:
            conflict("unknown_packet_field", "?", p["record_id"], field, p["proposed_value"],
                     "field is not processes/materials/markets_served/certifications or an *_other_note", ref,
                     "inspect packet row")
            continue
        for val in tokens(p["proposed_value"]):
            ENTRIES.append({"lane": lane, "line": line, "ref": ref, "scope": p["record_scope"],
                            "rid": p["record_id"], "field": field, "value": val, "url": norm(p["source_url"]),
                            "quote": norm(p["quote"]), "date": norm(p["observed_date"]),
                            "verdict": norm(p["verdict"]), "klass": norm(p["source_class"]),
                            "notes": norm(p["notes"])})

# classify entries
site_adds = defaultdict(lambda: defaultdict(OrderedDict))
org_adds = defaultdict(lambda: defaultdict(OrderedDict))
verdict_seen = defaultdict(set)
for e in ENTRIES:
    verdict_seen[(e["rid"], e["field"], e["value"])].add(e["verdict"])
    if e["scope"] == "org":
        LANES_OF_ORG[e["rid"]].add(e["lane"])
for e in ENTRIES:
    key = (e["rid"], e["field"], e["value"])
    tbl = "sites" if e["scope"] == "site" else "organizations"
    if e["value"] not in VOC_SET[e["field"]]:
        conflict("offvocab_value_in_vocab_field", tbl, e["rid"], e["field"], e["value"],
                 "value is not in the vocabulary", e["ref"], "not applied")
        continue
    if e["klass"] != "own_site":
        conflict("source_class_not_own_site", tbl, e["rid"], e["field"], e["value"],
                 f"source_class={e['klass']}", e["ref"], "not applied")
        continue
    if e["verdict"] != "VERIFIED":
        extra = ""
        if e["field"] == "certifications" and re.search(r"edition", e["notes"], re.I):
            extra = (f" R12 option (edition not stated): site/org notes could carry "
                     f"'claims {e['value']} (edition not stated, {e['url']}, {e['date']})'.")
        conflict("row_still_uncertain", tbl, e["rid"], e["field"], e["value"],
                 f"scope={e['scope']}; lane row verdict STILL_UNCERTAIN; lane note: {e['notes']}.{extra}",
                 e["ref"], "not applied; settles with the fact named in the lane note")
        continue
    if "VERIFIED" in verdict_seen[key] and "STILL_UNCERTAIN" in verdict_seen[key]:
        conflict("cross_lane_verdict_disagreement", tbl, e["rid"], e["field"], e["value"],
                 "the same record/field/value is VERIFIED in one packet row and STILL_UNCERTAIN in another",
                 e["ref"], "hold until the two lanes' facts are reconciled")
        continue
    bucket = site_adds if e["scope"] == "site" else org_adds
    bucket[e["rid"]][e["field"]].setdefault(e["value"], []).append(e)

# ---------------------------------------------------------------- 2/3. site and org update sets
EMAILS_REDACTED = 0


def field_status(field, existing_raw, new_vals):
    """Return (status, existing_tokens, existing_in_vocab, offvocab, added, proposed)."""
    ex = tokens(existing_raw)
    inv = [t for t in ex if t in VOC_SET[field]]
    off = [t for t in ex if t not in VOC_SET[field]]
    added = [v for v in new_vals if v not in inv]
    if not new_vals:
        return "NONE", ex, inv, off, [], existing_raw
    if not added:
        return "NOOP_ALREADY_PRESENT", ex, inv, off, [], existing_raw
    if off:
        return "REVIEW_EXISTING_OFFVOCAB", ex, inv, off, added, ""
    return "APPLY", ex, inv, off, added, ";".join(vocab_union(field, inv, added))


def refs_of(bucket_rid):
    seen, out = set(), []
    for fld in VOC:
        for val, es in bucket_rid.get(fld, {}).items():
            for e in es:
                if e["ref"] not in seen:
                    seen.add(e["ref"])
                    out.append(e["ref"])
    return out


SITE_UPD = []      # dict rows
SITE_PLAN = {}     # sid -> {field: (status, proposed, added)}, cert list, apply flag
for sid in sorted(site_adds):
    adds = site_adds[sid]
    ver = VERDICTS.get(sid)
    hold = []
    rec = SITES.get(sid)
    refs = refs_of(adds)
    if rec is None:
        hold.append("site_id_not_in_data")
        conflict("site_missing", "sites", sid, "", "", "packet site-scope rows name a site not held in data/sites_*.csv",
                 ";".join(refs), "return packet to lane")
        SITE_UPD.append({"site_id": sid, "apply_status": "HOLD", "hold_reason": ";".join(hold), "packet_row_refs": "|".join(refs)})
        continue
    shard, r = rec
    if ver is None:
        hold.append("no_verdict_row")
    elif ver["org_id"] != r["org_id"]:
        hold.append(f"lane_org_{ver['org_id']}_vs_site_org_{r['org_id']}")
    if r["operating_status"].strip() != "active":
        hold.append(f"site_operating_status_{r['operating_status'].strip() or 'blank'}")
    if r["site_type"].strip() in NON_PLANT_TYPES:
        hold.append(f"site_type_{r['site_type'].strip()}_non_plant_R9")
    row = {"site_id": sid, "org_id": r["org_id"], "site_name": r["site_name"], "shard": shard,
           "county": r["county"], "site_type": r["site_type"], "operating_status": r["operating_status"],
           "tier": r["verification_tier"],
           "site_verdict": ver["verdict"] if ver else "", "lane": ver["_lane"] if ver else ""}
    plan = {}
    for f in ("processes", "materials", "markets_served"):
        st, ex, inv, off, added, prop = field_status(f, r[f], list(adds.get(f, {})))
        plan[f] = (st, prop, added)
        row[f"current_{f}"] = r[f]
        row[f"new_{f}"] = ";".join(added)
        row[f"proposed_{f}"] = prop if st in ("APPLY", "NOOP_ALREADY_PRESENT") else ""
        row[f"{f}_status"] = st
        if st == "REVIEW_EXISTING_OFFVOCAB":
            conflict("existing_offvocab_field", "sites", sid, f, ";".join(added),
                     f"current value {r[f]!r} holds off-vocabulary token(s) {';'.join(off)}; new in-vocab values held "
                     f"back so the existing text is not rewritten or duplicated (e.g. 'injection molding' vs "
                     f"injection_molding)", ";".join(e["ref"] for v in added for e in adds[f][v]),
                     "integrator normalizes the existing tokens first (owner-ruled vocabulary), then re-run")
    certs = list(adds.get("certifications", {}))
    certs = sorted(certs, key=lambda t: VOC_RANK["certifications"][t])
    row["current_certifications"] = "n/a: sites have no certifications column" if not SITES_HAVE_CERT_COLUMN else ""
    row["proposed_certifications"] = ";".join(certs)
    note = ""
    if certs:
        note = f"CERT-SITE (own site, observed {adds['certifications'][certs[0]][0]['date']}): {'; '.join(certs)}."
    row["cert_route"] = "site notes append (CERT-SITE)" if certs else ""
    row["proposed_notes_append"] = note
    row["site_verdict_note"] = ""
    if ver and ver["verdict"] != "VERIFIED":
        row["site_verdict_note"] = "site verdict STILL_UNCERTAIN; the rows applied here are row-level VERIFIED"
        conflict("site_verdict_su_row_verified", "sites", sid, "", "",
                 f"site-level verdict is STILL_UNCERTAIN ({norm(ver['deciding_or_settling_fact'])[:300]}) while the "
                 f"packet carries row-level VERIFIED site-scope rows; the rows are applied only if the site is not held",
                 ";".join(refs), "integrator confirms the plant-named certificate or page before applying")
    if hold:
        conflict("site_hold", "sites", sid, "", "", f"held: {';'.join(hold)}", ";".join(refs),
                 "resolve the hold (status/R9 type correction/org mismatch), then re-run")
    row["apply_status"] = "HOLD" if hold else "APPLY"
    row["hold_reason"] = ";".join(hold)
    row["packet_row_refs"] = "|".join(refs)
    SITE_UPD.append(row)
    SITE_PLAN[sid] = {"plan": plan, "certs": certs, "note": note, "apply": not hold, "adds": adds}

ORG_UPD = []
ORG_PLAN = {}
for oid in sorted(org_adds):
    adds = org_adds[oid]
    refs = refs_of(adds)
    hold = []
    rec = ORGS.get(oid)
    lanes = sorted(LANES_OF_ORG.get(oid, ()))
    if rec is None:
        hold.append("org_in_ecosystem_table_no_org_columns" if oid in ECO_IDS else "org_id_not_in_data")
        conflict("org_missing", "organizations", oid, "", "", f"held: {';'.join(hold)}", ";".join(refs),
                 "return packet to lane / owner")
        ORG_UPD.append({"org_id": oid, "lanes": ";".join(lanes), "apply_status": "HOLD",
                        "hold_reason": ";".join(hold), "packet_row_refs": "|".join(refs)})
        continue
    shard, r = rec
    if r["status"].strip() != "active":
        hold.append(f"org_status_{r['status'].strip() or 'blank'}")
    lane_orgs_ok = any(oid in LANE_SITE_ORGS[l] for l in lanes)
    row = {"org_id": oid, "legal_name": r["legal_name"], "shard": shard, "status": r["status"],
           "hq_state": r["hq_state"], "tier": r["verification_tier"], "lanes": ";".join(lanes),
           "n_lanes": len(lanes)}
    if not lane_orgs_ok:
        conflict("org_scope_org_not_a_lane_site_parent", "organizations", oid, "", "",
                 f"org-scope rows name {oid}, which is not the parent of any site assigned to lane(s) {','.join(lanes)}",
                 ";".join(refs), "integrator checks the org identity (rebrand/parent) before applying")
        hold.append("org_not_parent_of_lane_sites")
    plan = {}
    for f in VOC:
        st, ex, inv, off, added, prop = field_status(f, r[f], list(adds.get(f, {})))
        plan[f] = (st, prop, added)
        row[f"current_{f}"] = r[f]
        row[f"new_{f}"] = ";".join(added)
        row[f"proposed_{f}"] = prop if st in ("APPLY", "NOOP_ALREADY_PRESENT") else ""
        row[f"{f}_status"] = st
        if st == "REVIEW_EXISTING_OFFVOCAB":
            conflict("existing_offvocab_field", "organizations", oid, f, ";".join(added),
                     f"current value {r[f]!r} holds off-vocabulary token(s) {';'.join(off)}; new in-vocab values held "
                     f"back", ";".join(e["ref"] for v in added for e in adds[f][v]),
                     "integrator normalizes the existing tokens first (owner-ruled vocabulary), then re-run")
    if hold:
        conflict("org_hold", "organizations", oid, "", "", f"held: {';'.join(hold)}", ";".join(refs),
                 "resolve the hold, then re-run")
    row["apply_status"] = "HOLD" if hold else "APPLY"
    row["hold_reason"] = ";".join(hold)
    row["packet_row_refs"] = "|".join(refs)
    ORG_UPD.append(row)
    ORG_PLAN[oid] = {"plan": plan, "apply": not hold, "adds": adds}

# ---------------------------------------------------------------- 3. evidence rows
EVD = []
EVD_KEYS = set()


def evidence_row(table, rid, field, value, entries, scope, route_note=""):
    """One draft row per (record, field, value); first lane/source cited, the rest listed in notes."""
    global EMAILS_REDACTED
    e0 = entries[0]
    if V23_PHANTOM.search(e0["url"]) or V23_LICENSED.search(e0["url"]) or not e0["url"]:
        conflict("evidence_source_ref_inadmissible", table, rid, field, value,
                 f"source URL {e0['url']!r} trips the V-23 tripwire or is empty", e0["ref"],
                 "draft evidence row withheld; lane supplies an admissible URL")
        return
    quote = e0["quote"]
    if EMAIL_RE.search(quote) or PHONE_RE.search(quote):
        quote = PHONE_RE.sub("[phone omitted]", EMAIL_RE.sub("[email omitted]", quote))
        EMAILS_REDACTED += 1
    others = sorted({f"{x['url']} ({x['ref']})" for x in entries[1:] if x["url"] != e0["url"]})
    if scope == "site_cert":
        detail = (f"certification {value} held at this site (site scope; recorded in site notes because sites carry "
                  f"no certifications column)")
    elif field == "certifications":
        detail = f"organizations.certifications includes {value} (org scope, own-site certificate or page)"
    else:
        detail = f"{table}.{field} includes {value} ({'site' if table == 'sites' else 'org'} scope, own-site disclosure)"
    notes = f'Quote: "{quote}" | packet row {e0["ref"]}'
    if route_note:
        notes += f" | {route_note}"
    if others:
        notes += " | corroborating: " + "; ".join(others)
    k = (table, rid, detail)
    if k in EVD_KEYS:
        return
    EVD_KEYS.add(k)
    EVD.append({"evidence_id": ALLOC, "record_table": table, "record_id": rid, "claim_type": "scope",
                "claim_detail": detail, "source_class": "own_site", "source_ref": e0["url"],
                "observed_date": e0["date"], "tier_effect": OWN_SITE_EFFECT, "created_by": CREATED_BY,
                "notes": notes})


for sid, p in SITE_PLAN.items():
    if not p["apply"]:
        continue
    for f, (st, prop, added) in p["plan"].items():
        if st not in ("APPLY", "NOOP_ALREADY_PRESENT"):
            continue
        for val, es in p["adds"].get(f, {}).items():
            evidence_row("sites", sid, f, val, es, "site",
                         "reconfirms a value the site row already carried" if val not in added else "")
    for val in p["certs"]:
        evidence_row("sites", sid, "certifications", val, p["adds"]["certifications"][val], "site_cert")
for oid, p in ORG_PLAN.items():
    if not p["apply"]:
        continue
    for f, (st, prop, added) in p["plan"].items():
        if st not in ("APPLY", "NOOP_ALREADY_PRESENT"):
            continue
        for val, es in p["adds"].get(f, {}).items():
            evidence_row("organizations", oid, f, val, es, "org",
                         "reconfirms a value the org row already carried" if val not in added else "")
EVD.sort(key=lambda r: (r["record_table"], r["record_id"], r["claim_detail"]))

# ---------------------------------------------------------------- 4. bands (R13)
def step(b):
    return BAND_RANK[b]


ita, insp, f55s, f55o = {}, {}, {}, {}
for line, r in read_rows(ITA_PATH):
    r["_ref"] = f"osha-ita/band_proposals.csv:{line}"
    ita[r["site_id"]] = r
for line, r in read_rows(INSP_PATH):
    r["_ref"] = f"osha-spine/band_proposals.csv:{line}"
    insp[r["site_id"]] = r
for line, r in read_rows(F5500_PATH):
    r["_ref"] = f"form5500-spine/band_proposals.csv:{line}"
    if r["target_table"] == "sites":
        f55s[r["site_id"]] = r
    elif r["target_table"] == "organizations" and r["target_field"] == "employee_band_ohio":
        f55o[r["org_id"]] = r

BAND_ROWS = []


def existing_state(v):
    v = (v or "").strip()
    if not v:
        return "blank"
    if v == "unknown":
        return "unknown"
    return "in_vocab" if v in BAND_RANK else "off_vocab"


for sid in sorted(set(ita) | set(insp) | set(f55s)):
    a, b, c = ita.get(sid), insp.get(sid), f55s.get(sid)
    rec = SITES.get(sid)
    row = {"record_table": "sites", "record_id": sid}
    refs = [x["_ref"] for x in (a, b, c) if x]
    reasons_skip, reasons_rev = [], []
    if rec is None:
        row.update({"existing_band": "", "existing_band_state": "site_missing", "status": "SKIP",
                    "reason": "site_not_in_data", "packet_refs": "|".join(refs)})
        BAND_ROWS.append(row)
        continue
    shard, s = rec
    ex = (s["employee_band_site"] or "").strip()
    row.update({"org_id": s["org_id"], "name": s["site_name"], "state": s["state"],
                "site_operating_status": s["operating_status"], "existing_band": ex,
                "existing_band_state": existing_state(ex)})
    if a:
        row.update({"ita_band": a["proposed_employee_band_site"], "ita_source_date": a["employee_count_source_date"],
                    "ita_reliability": a["reliability"], "ita_match": a["match_strength"]})
    if b:
        row.update({"inspection_band": b["proposed_employee_band_site"],
                    "inspection_source_date": b["employee_count_source_date"], "inspection_match": b["match_strength"],
                    "inspection_band_stable": b["band_stable"]})
    if c:
        row.update({"f5500_band": c["proposed_value"], "f5500_plan_year": c["plan_year"], "f5500_class": c["proposal_class"]})
    # ----- precedence
    pick_src = "ita" if a else "inspection" if b else "form5500" if c else ""
    pick = {"ita": a["proposed_employee_band_site"] if a else "", "inspection": b["proposed_employee_band_site"] if b else "",
            "form5500": c["proposed_value"] if c else ""}[pick_src]
    row["pick_band"], row["pick_source"] = pick, pick_src
    src_date = ""
    if pick_src == "ita":
        src_date = a["employee_count_source_date"]
    elif pick_src == "inspection":
        src_date = b["employee_count_source_date"]
    row["employee_count_source_date"] = src_date
    if pick not in BAND_RANK:
        reasons_skip.append("pick_band_not_in_vocab")
    # ----- SKIP gates
    if a and a["reliability"] != "ok":
        reasons_skip.append(f"ita_reliability_{a['reliability']}")
    if pick_src == "form5500" and SITES_PER_ORG[s["org_id"]] != 1:
        reasons_skip.append("f5500_org_not_single_establishment")
    # ----- REVIEW gates
    if s["operating_status"].strip() != "active":
        reasons_rev.append(f"site_not_active_{s['operating_status'].strip() or 'blank'}")
    if a and a["site_caution"]:
        reasons_rev.append("ita_site_caution:" + a["site_caution"].replace(";", "+"))
    spread = 0
    if pick in BAND_RANK:
        for nm, bnd in (("ita", a["proposed_employee_band_site"] if a else ""),
                        ("inspection", b["proposed_employee_band_site"] if b else ""),
                        ("form5500", c["proposed_value"] if c else "")):
            if bnd in BAND_RANK and nm != pick_src:
                d = abs(step(bnd) - step(pick))
                spread = max(spread, d)
                if d > 1:
                    reasons_rev.append(f"{nm}_differs_by_{d}_bands")
    row["max_step_spread_vs_pick"] = spread
    ps = {"ita": a, "inspection": b, "form5500": c}[pick_src] if pick_src else None
    if ps and pick_src != "form5500" and ps["match_strength"] != "strong":
        reasons_rev.append(f"{pick_src}_match_{ps['match_strength']}")
    if pick_src == "form5500" and c:
        fl = c["review_flags"]
        if "match_via_address_not_name" in fl:
            reasons_rev.append("f5500_match_via_address_not_name")
        if re.search(r"matched_org_status=(?!active)", fl):
            reasons_rev.append("f5500_matched_org_status_not_active")
    if a and a["other_ita_estabs_at_site"]:
        diffs = 0
        for part in a["other_ita_estabs_at_site"].split(";"):
            if ":" in part and part.split(":", 1)[1] in BAND_RANK and pick in BAND_RANK:
                if part.split(":", 1)[1] != pick:
                    diffs += 1
        if diffs:
            reasons_rev.append(f"ita_other_filings_at_site_in_other_bands({diffs})")
    if row["existing_band_state"] == "in_vocab" and pick in BAND_RANK and ex != pick:
        reasons_rev.append("conflicts_existing_in_vocab_band")
    if row["existing_band_state"] == "off_vocab":
        reasons_rev.append("existing_band_off_vocab")
    # ----- status
    if reasons_skip:
        row["status"], row["reason"], row["action"] = "SKIP", ";".join(reasons_skip), ""
    elif reasons_rev:
        row["status"], row["reason"], row["action"] = "REVIEW", ";".join(reasons_rev), ""
    else:
        row["status"] = "APPLY"
        row["action"] = "noop_matches_existing" if ex == pick else "fill"
        row["reason"] = ""
    note = ""
    if row["status"] == "APPLY" and row["action"] == "fill":
        if pick_src == "ita":
            note = (f"BAND-SOURCE: employee_band_site={pick} from OSHA ITA Form 300A CY2025, filed {src_date} "
                    f"(government_filing; band only, not a headcount).")
        elif pick_src == "inspection":
            note = (f"BAND-SOURCE: employee_band_site={pick} from OSHA inspection record, opened {src_date} "
                    f"(government_filing; band only, not a headcount).")
        else:
            note = (f"BAND-SOURCE: employee_band_site={pick} from Form 5500 plan year {c['plan_year']} active "
                    f"participants (government_filing; plan count, not a headcount; single-establishment org).")
    row["notes_append"] = note
    row["packet_refs"] = "|".join(refs)
    BAND_ROWS.append(row)

for oid in sorted(f55o):
    c = f55o[oid]
    rec = ORGS.get(oid)
    row = {"record_table": "organizations", "record_id": oid, "f5500_band": c["proposed_value"],
           "f5500_plan_year": c["plan_year"], "f5500_class": c["proposal_class"], "pick_band": c["proposed_value"],
           "pick_source": "form5500", "employee_count_source_date": "", "packet_refs": c["_ref"]}
    if rec is None:
        row.update({"existing_band_state": "org_missing", "status": "SKIP", "reason": "org_not_in_organizations_shards",
                    "existing_band": ""})
        BAND_ROWS.append(row)
        continue
    shard, o = rec
    ex = (o["employee_band_ohio"] or "").strip()
    st = existing_state(ex)
    row.update({"org_id": oid, "name": o["legal_name"], "state": o["hq_state"], "existing_band": ex,
                "existing_band_state": st})
    rev = []
    if c["proposed_value"] not in BAND_RANK:
        row.update({"status": "SKIP", "reason": "pick_band_not_in_vocab", "action": ""})
        BAND_ROWS.append(row)
        continue
    if o["status"].strip() != "active":
        rev.append(f"org_status_{o['status'].strip() or 'blank'}")
    if re.search(r"matched_org_status=", c["review_flags"]):
        rev.append("f5500_" + re.search(r"matched_org_status=\w+", c["review_flags"]).group(0))
    if "match_via_address_not_name" in c["review_flags"]:
        rev.append("f5500_match_via_address_not_name")
    if st == "in_vocab" and ex != c["proposed_value"]:
        rev.append("conflicts_existing_in_vocab_band")
    if st == "off_vocab":
        rev.append("existing_band_off_vocab")
    if rev:
        row.update({"status": "REVIEW", "reason": ";".join(sorted(set(rev))), "action": ""})
    else:
        row.update({"status": "APPLY", "reason": "", "action": "noop_matches_existing" if ex == c["proposed_value"] else "fill"})
    if row["status"] == "APPLY" and row["action"] == "fill":
        row["notes_append"] = (f"BAND-SOURCE: employee_band_ohio={c['proposed_value']} from Form 5500 plan year "
                               f"{c['plan_year']} active participants (government_filing; plan count, not a headcount; "
                               f"R7f).")
    BAND_ROWS.append(row)

for r in BAND_ROWS:
    if r["status"] in ("REVIEW", "SKIP"):
        conflict(f"band_{r['status'].lower()}", r["record_table"], r["record_id"],
                 "employee_band_site" if r["record_table"] == "sites" else "employee_band_ohio",
                 r.get("pick_band", ""),
                 f"reason={r['reason']}; existing={r.get('existing_band', '')!r}; ita={r.get('ita_band', '')}; "
                 f"inspection={r.get('inspection_band', '')}; form5500={r.get('f5500_band', '')}",
                 r.get("packet_refs", ""),
                 "R13: disagreement >1 band or against an existing in-vocab band goes to review" if r["status"] == "REVIEW"
                 else "excluded by a reliability / eligibility flag; not applied")

# ---------------------------------------------------------------- write outputs
OUT.mkdir(parents=True, exist_ok=True)
SITE_COLS = ["site_id", "org_id", "site_name", "shard", "county", "site_type", "operating_status", "tier", "lane",
             "site_verdict", "site_verdict_note",
             "current_processes", "new_processes", "proposed_processes", "processes_status",
             "current_materials", "new_materials", "proposed_materials", "materials_status",
             "current_markets_served", "new_markets_served", "proposed_markets_served", "markets_served_status",
             "current_certifications", "proposed_certifications", "cert_route", "proposed_notes_append",
             "apply_status", "hold_reason", "packet_row_refs"]
ORG_COLS = ["org_id", "legal_name", "shard", "status", "hq_state", "tier", "lanes", "n_lanes",
            "current_processes", "new_processes", "proposed_processes", "processes_status",
            "current_materials", "new_materials", "proposed_materials", "materials_status",
            "current_markets_served", "new_markets_served", "proposed_markets_served", "markets_served_status",
            "current_certifications", "new_certifications", "proposed_certifications", "certifications_status",
            "apply_status", "hold_reason", "packet_row_refs"]
BAND_COLS = ["record_table", "record_id", "org_id", "name", "state", "site_operating_status", "existing_band",
             "existing_band_state", "ita_band", "ita_source_date", "ita_reliability", "ita_match",
             "inspection_band", "inspection_source_date", "inspection_match", "inspection_band_stable",
             "f5500_band", "f5500_plan_year", "f5500_class", "pick_band", "pick_source",
             "employee_count_source_date", "max_step_spread_vs_pick", "status", "action", "reason",
             "notes_append", "packet_refs"]
CONF_COLS = ["conflict_class", "record_table", "record_id", "field", "value", "detail", "packet_refs",
             "suggested_disposition"]
write_csv(OUT / "capability_site_updates.csv", SITE_COLS, SITE_UPD)
write_csv(OUT / "capability_org_updates.csv", ORG_COLS, ORG_UPD)
write_csv(OUT / "evidence_rows.csv", EVD_HEADER, EVD)
write_csv(OUT / "band_updates.csv", BAND_COLS, BAND_ROWS)
CONFLICTS.sort(key=lambda r: (r["conflict_class"], r["record_table"], r["record_id"], r["field"], r["value"]))
write_csv(OUT / "conflicts.csv", CONF_COLS, CONFLICTS)

# ---------------------------------------------------------------- stats
S = {}
S["packet_rows"] = RAW_ROWS
S["packet_dirs"] = len(PACKET_DIRS)
S["verdict_sites"] = len(VERDICTS)
S["verdict_sites_verified"] = sum(1 for v in VERDICTS.values() if v["verdict"] == "VERIFIED")
S["entries_in_vocab_values"] = len(ENTRIES)
S["site_rows_total"] = len(SITE_UPD)
S["site_rows_apply"] = sum(1 for r in SITE_UPD if r["apply_status"] == "APPLY")
S["site_rows_hold"] = S["site_rows_total"] - S["site_rows_apply"]
S["org_rows_total"] = len(ORG_UPD)
S["org_rows_apply"] = sum(1 for r in ORG_UPD if r["apply_status"] == "APPLY")
S["org_rows_hold"] = S["org_rows_total"] - S["org_rows_apply"]
sites_changed, orgs_changed = set(), set()
S["site_values_added"] = Counter()
S["site_values_review"] = Counter()
S["org_values_added"] = Counter()
S["org_values_review"] = Counter()
for sid, p in SITE_PLAN.items():
    for f, (st, prop, added) in p["plan"].items():
        if st == "REVIEW_EXISTING_OFFVOCAB":
            S["site_values_review"][f] += len(added)
        if p["apply"] and st == "APPLY":
            S["site_values_added"][f] += len(added)
            sites_changed.add(sid)
    if p["apply"] and p["certs"]:
        S["site_values_added"]["certifications(notes)"] += len(p["certs"])
        sites_changed.add(sid)
for oid, p in ORG_PLAN.items():
    for f, (st, prop, added) in p["plan"].items():
        if st == "REVIEW_EXISTING_OFFVOCAB":
            S["org_values_review"][f] += len(added)
        if p["apply"] and st == "APPLY":
            S["org_values_added"][f] += len(added)
            orgs_changed.add(oid)
S["sites_changed"] = len(sites_changed)
S["orgs_changed"] = len(orgs_changed)
S["evidence_rows"] = len(EVD)
S["evidence_reconfirm"] = sum(1 for r in EVD if "reconfirms" in r["notes"])
S["evidence_by_table"] = Counter(r["record_table"] for r in EVD)
S["emails_redacted"] = EMAILS_REDACTED
bs = Counter((r["record_table"], r["status"]) for r in BAND_ROWS)
S["bands"] = bs
S["bands_apply_fill"] = Counter(r["record_table"] for r in BAND_ROWS if r["status"] == "APPLY" and r["action"] == "fill")
S["bands_apply_noop"] = Counter(r["record_table"] for r in BAND_ROWS if r["status"] == "APPLY" and r["action"] != "fill")
S["bands_apply_fill_by_source"] = Counter(r["pick_source"] for r in BAND_ROWS if r["status"] == "APPLY" and r["action"] == "fill")
S["band_reasons"] = Counter()
for r in BAND_ROWS:
    if r["status"] in ("REVIEW", "SKIP"):
        for t in r["reason"].split(";"):
            S["band_reasons"][(r["status"], re.sub(r"\(.*\)|_\d+_bands", "", t.split(":")[0]).strip())] += 1
S["conflict_classes"] = Counter(r["conflict_class"] for r in CONFLICTS)
S["sites_have_cert_column"] = SITES_HAVE_CERT_COLUMN
S["orgs_have_cert_column"] = ORGS_HAVE_CERT_COLUMN
S["multi_lane_orgs"] = sum(1 for o in org_adds if len(LANES_OF_ORG[o]) > 1)
S["org_entries_before_dedupe"] = sum(1 for e in ENTRIES if e["scope"] == "org" and e["verdict"] == "VERIFIED")
S["org_values_after_dedupe"] = sum(len(v) for o in org_adds.values() for v in o.values())

_bat = BATTERY.read_text(encoding="utf-8")
_i = _bat.find("## Addendum")
S["r13_ruled"] = bool(_i >= 0 and "RULED" in _bat[_i:_i + 400])

# ---------------------------------------------------------------- dry run
APPLY_SITE_FIELDS = ("processes", "materials", "markets_served")


def apply_to_copy(tmpdata):
    """Apply the sets to a COPY of data/ (placeholders filled from atlas.py next-id). Returns stats."""
    st = Counter()
    # sites
    for fname, (hdr, _) in SITE_FILES.items():
        path = tmpdata / fname
        with open(path, newline="", encoding="utf-8") as fh:
            rdr = csv.DictReader(fh)
            hdr = list(rdr.fieldnames)
            rows = list(rdr)
        changed = False
        for r in rows:
            sid = r["site_id"]
            notes_add = []
            p = SITE_PLAN.get(sid)
            if p and p["apply"]:
                for f in APPLY_SITE_FIELDS:
                    s_, prop, added = p["plan"][f]
                    if s_ == "APPLY":
                        r[f] = prop
                        st[f"site_{f}_fields"] += 1
                        changed = True
                if p["note"]:
                    notes_add.append(p["note"])
                    st["site_cert_notes"] += 1
            for br in BAND_INDEX_SITES.get(sid, ()):
                if br["status"] == "APPLY" and br["action"] == "fill":
                    r["employee_band_site"] = br["pick_band"]
                    notes_add.append(br["notes_append"])
                    st["site_bands"] += 1
                    changed = True
            if notes_add:
                r["notes"] = (r["notes"].rstrip() + " " if r["notes"].strip() else "") + " ".join(notes_add)
                changed = True
        if changed:
            with open(path, "w", newline="", encoding="utf-8") as fh:
                w = csv.DictWriter(fh, fieldnames=hdr, lineterminator="\n")
                w.writeheader()
                w.writerows(rows)
    # orgs
    for fname in ORG_FILES:
        path = tmpdata / fname
        with open(path, newline="", encoding="utf-8") as fh:
            rdr = csv.DictReader(fh)
            hdr = list(rdr.fieldnames)
            rows = list(rdr)
        changed = False
        for r in rows:
            oid = r["org_id"]
            notes_add = []
            p = ORG_PLAN.get(oid)
            if p and p["apply"]:
                for f in VOC:
                    s_, prop, added = p["plan"][f]
                    if s_ == "APPLY":
                        r[f] = prop
                        st[f"org_{f}_fields"] += 1
                        changed = True
            br = BAND_INDEX_ORGS.get(oid)
            if br and br["status"] == "APPLY" and br["action"] == "fill":
                r["employee_band_ohio"] = br["pick_band"]
                notes_add.append(br["notes_append"])
                st["org_bands"] += 1
                changed = True
            if notes_add:
                r["notes"] = (r["notes"].rstrip() + " " if r["notes"].strip() else "") + " ".join(notes_add)
        if changed:
            with open(path, "w", newline="", encoding="utf-8") as fh:
                w = csv.DictWriter(fh, fieldnames=hdr, lineterminator="\n")
                w.writeheader()
                w.writerows(rows)
    # evidence: fill <ALLOC> from atlas.py next-id run against the TEMP copy
    out = subprocess.run([sys.executable, str(ROOT / "scripts/atlas.py"), "--data-dir", str(tmpdata), "next-id", "EVD", "--json"],
                         capture_output=True, text=True, check=True).stdout
    nxt = json.loads(out)["prefixes"][0]["next_id"]
    st["first_evd"] = nxt
    n = int(nxt.split("-")[1])
    with open(tmpdata / "evidence.csv", newline="", encoding="utf-8") as fh:
        rdr = csv.DictReader(fh)
        ehdr = list(rdr.fieldnames)
    assert ehdr == EVD_HEADER, ehdr
    with open(tmpdata / "evidence.csv", "a", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=EVD_HEADER, lineterminator="\n")
        for i, r in enumerate(EVD):
            row = dict(r)
            row["evidence_id"] = f"EVD-{n + i:06d}"
            w.writerow(row)
    st["last_evd"] = f"EVD-{n + len(EVD) - 1:06d}" if EVD else ""
    st["evd_appended"] = len(EVD)
    return st


BAND_INDEX_SITES = defaultdict(list)
BAND_INDEX_ORGS = {}
for r in BAND_ROWS:
    if r["record_table"] == "sites":
        BAND_INDEX_SITES[r["record_id"]].append(r)
    else:
        BAND_INDEX_ORGS[r["record_id"]] = r


def run_validate(datadir):
    env = dict(os.environ, ATLAS_DATA_DIR=str(datadir))
    p = subprocess.run([sys.executable, str(ROOT / "scripts/validate.py")], capture_output=True, text=True, env=env)
    lines = (p.stdout + p.stderr).splitlines()
    return p.returncode, lines


def dryrun(tmp_root):
    tmp = Path(tempfile.mkdtemp(prefix="atlas_integration_dryrun_", dir=tmp_root))
    try:
        tmpdata = tmp / "data"
        shutil.copytree(DATA, tmpdata)
        base_rc, base_lines = run_validate(tmpdata)
        with open(tmpdata / "evidence.csv", newline="", encoding="utf-8") as fh:
            prior_ids = {r["evidence_id"] for r in csv.DictReader(fh)}
        stats = apply_to_copy(tmpdata)
        rc, lines = run_validate(tmpdata)
        # independent post-apply checks on the temp copy
        checks = []
        with open(tmpdata / "evidence.csv", newline="", encoding="utf-8") as fh:
            ev = list(csv.DictReader(fh))
        ids = [r["evidence_id"] for r in ev]
        checks.append(("evidence_id unique across the table", len(ids) == len(set(ids))))
        checks.append(("no `<ALLOC>` placeholder left in the temp evidence.csv", all(ALLOC not in r["evidence_id"] for r in ev)))
        new_rows = [r for r in ev if r["evidence_id"] not in prior_ids]
        checks.append(("all new evidence rows created_by = " + CREATED_BY,
                       len(new_rows) == len(EVD) and all(r["created_by"] == CREATED_BY for r in new_rows)))
        post_sites, _ = load_table_from(tmpdata, "sites")
        bad_tokens = 0
        for sid, p in SITE_PLAN.items():
            if not p["apply"]:
                continue
            for f in APPLY_SITE_FIELDS:
                if p["plan"][f][0] == "APPLY":
                    bad_tokens += sum(1 for t in tokens(post_sites[sid][f]) if t not in VOC_SET[f])
        checks.append(("every token in a field this pass wrote is in the vocabulary", bad_tokens == 0))
        return tmp, base_rc, base_lines, rc, lines, stats, checks
    except Exception:
        shutil.rmtree(tmp, ignore_errors=True)
        raise


def load_table_from(datadir, prefix):
    rows = {}
    for f in sorted(Path(datadir).glob(f"{prefix}_*.csv")):
        with open(f, newline="", encoding="utf-8") as fh:
            rdr = csv.DictReader(fh)
            for r in rdr:
                rows[r[rdr.fieldnames[0]]] = r
    return rows, None


def summarise(lines):
    errs = [l for l in lines if l.startswith("ERROR")]
    warns = [l for l in lines if l.startswith("WARN")]
    tail = [l for l in lines if not l.startswith(("ERROR", "WARN")) and l.strip()]
    return errs, warns, tail


def fmt_counter(c):
    return ", ".join(f"{k} {v}" for k, v in sorted(c.items())) or "none"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--packets", nargs="+", help="packet directories or globs (default: the PIC-12 wave)")
    ap.add_argument("--out", help="output directory (default: tasks/integration-ready-2026-11-01)")
    ap.add_argument("--no-dryrun", action="store_true")
    ap.add_argument("--tmp-root", default=None, help="parent directory for the temp copy of data/")
    args = ap.parse_args()

    dry_md = ""
    dry_ok = None
    if not args.no_dryrun:
        tmp, base_rc, base_lines, rc, lines, stats, checks = dryrun(args.tmp_root)
        try:
            b_err, b_warn, b_tail = summarise(base_lines)
            a_err, a_warn, a_tail = summarise(lines)
            newwarn = [w for w in a_warn if w not in set(b_warn)]
            dry_ok = rc == 0 and not a_err and all(ok for _, ok in checks)
            dry_md = "\n".join([
                "# Validation dry run — integration-ready sets (2026-11-01)",
                "",
                "Generated by `scripts/build_integration_sets.py`. The real `data/` was never touched.",
                "A temp copy of `data/` was made, the sets in this folder were applied to the COPY, "
                "`<ALLOC>` evidence IDs were filled from `scripts/atlas.py --data-dir <copy> next-id EVD`, "
                "`ATLAS_DATA_DIR=<copy> python3 scripts/validate.py` was run, and the copy was deleted.",
                "",
                f"**Outcome: {'OK — validation passed' if dry_ok else 'FAILED — see errors below'}** "
                f"(exit code {rc}; {len(a_err)} errors; {len(a_warn)} warnings).",
                "",
                "## What was applied to the copy (units in the label)",
                "",
                f"- site processes fields written: {stats['site_processes_fields']}; materials: {stats['site_materials_fields']}; "
                f"markets_served: {stats['site_markets_served_fields']} (unit: site rows)",
                f"- site notes appended with `CERT-SITE:` (unit: site rows): {stats['site_cert_notes']}",
                f"- organization fields written (unit: org rows): processes {stats['org_processes_fields']}, "
                f"materials {stats['org_materials_fields']}, markets_served {stats['org_markets_served_fields']}, "
                f"certifications {stats['org_certifications_fields']}",
                f"- employee_band_site written (unit: site rows): {stats['site_bands']}; "
                f"employee_band_ohio written (unit: org rows): {stats['org_bands']}",
                f"- evidence rows appended: {stats['evd_appended']} ({stats['first_evd']} to {stats['last_evd']}, "
                f"IDs allocated in the temp copy only; the real tree will allocate at integration)",
                "",
                "## Validator result",
                "",
                f"- Baseline (copy of `data/` before applying): exit {base_rc}; {len(b_err)} errors; {len(b_warn)} warnings.",
                f"- After applying: exit {rc}; {len(a_err)} errors; {len(a_warn)} warnings.",
                f"- Last validator line: `{a_tail[-1] if a_tail else ''}`",
                "",
                "### Errors after applying",
                "",
                *(["- none"] if not a_err else [f"- `{e}`" for e in a_err[:60]]),
                "",
                "### Warnings that are new relative to the baseline",
                "",
                *(["- none"] if not newwarn else [f"- `{w}`" for w in newwarn[:60]]),
                *([f"- ... {len(newwarn) - 60} more"] if len(newwarn) > 60 else []),
                "",
                "## Independent post-apply checks",
                "",
                *[f"- [{'x' if ok else ' '}] {name}" for name, ok in checks],
                "",
                "## Notes for the integrator",
                "",
                "- V-25 (tier restatement) is satisfied by construction: every drafted row is claim_type=`scope`, "
                "source_class=`own_site`, tier_effect=`supports_A` (the own_site ceiling), so no record's scope claim "
                "is supported below its tier.",
                "- Band evidence rows are NOT drafted: SCHEMA §4.13 has no claim_type for an employee band, and an "
                "`activity` row at a weaker-than-A effect would trip V-25 on tier A/B active sites. The R13 source "
                "date travels in the `BAND-SOURCE:` notes append and in band_updates.csv until the owner/schema "
                "names a claim_type.",
                "- Applying `employee_band_ohio` changes an input of the derived `tier1_qualifier` (`employees_250plus`). "
                "The dry run reports any V-29 drift as warnings above; the integrator re-runs the derivation after the "
                "band pass (derived fields are never hand-edited, AGENTS.md §1).",
                "",
            ])
        finally:
            shutil.rmtree(tmp, ignore_errors=True)
        (OUT / "validate_dryrun.md").write_text(dry_md, encoding="utf-8")
        S["dryrun_ok"] = dry_ok
        S["dryrun_errors"] = len(a_err)
        S["dryrun_warnings_new"] = len(newwarn)
        S["dryrun_stats"] = stats
    (OUT / "README.md").write_text(readme(S, dry_ok), encoding="utf-8")
    print(f"site rows APPLY {S['site_rows_apply']} / HOLD {S['site_rows_hold']}; sites changed {S['sites_changed']}")
    print(f"org rows APPLY {S['org_rows_apply']} / HOLD {S['org_rows_hold']}; orgs changed {S['orgs_changed']}")
    print(f"evidence rows {S['evidence_rows']}; bands {dict(S['bands'])}; conflicts {len(CONFLICTS)}")
    if dry_ok is not None:
        print("dry run:", "OK" if dry_ok else "FAILED")
    return 0 if dry_ok in (None, True) else 1


def readme(S, dry_ok):
    r13 = ("**R13 band precedence was owner-ruled on 2026-11-01** (`tasks/OWNER_BATTERY_2026-11-01.md` addendum header: "
           "RULED \"do it all\"; recorded as SCHEMA v1.7.7 §1). `band_updates.csv` is therefore ruled work; statuses below "
           "apply that ruling mechanically." if S["r13_ruled"] else
           "**`band_updates.csv` is pending R13**: the owner battery addendum is not marked ruled. Treat every band row as a proposal.")
    sv, ov = S["site_values_added"], S["org_values_added"]
    bs = S["bands"]
    L = []
    A = L.append
    A("# Integration-ready change sets — PIC-12 capability wave + employee bands (2026-11-01)" if not _PRE.packets
      else f"# Integration-ready change sets — capability lanes {', '.join(Path(d).name for d in PACKET_DIRS)}")
    A("")
    A("**These are proposals, not data changes.** Produced by `scripts/build_integration_sets.py` (stdlib, re-runnable) "
      "by a packet lane that never edits `data/`. Every new ID is the placeholder `<ALLOC>`; the integrator of record "
      "allocates IDs, applies one writer per file, and reviews first (AGENTS.md §2 rule 7). Nothing was committed or pushed.")
    A("")
    A("## Files")
    A("")
    A("| File | What it is |")
    A("|---|---|")
    A("| `capability_site_updates.csv` | one row per site with VERIFIED site-scope packet rows: current vs proposed `processes` / `materials` / `markets_served`, certification route, packet row refs, APPLY/HOLD |")
    A("| `capability_org_updates.csv` | one row per organization with VERIFIED org-scope rows, deduplicated across lanes: all four fields incl. `certifications` |")
    A("| `evidence_rows.csv` | draft rows in `data/evidence.csv`'s exact header order; `evidence_id` = `<ALLOC>` |")
    A("| `band_updates.csv` | per site (and per Ohio org): existing band, each source's proposal, the R13 pick, APPLY / REVIEW / SKIP |")
    A("| `conflicts.csv` | everything not mechanically appliable, with a class and a suggested disposition |")
    A("| `validate_dryrun.md` | the temp-copy application and `validate.py` result |")
    A("")
    A("## Counts (units stated)")
    A("")
    A(f"- **Inputs:** {S['packet_dirs']} packet folders ({'pilot + 5 tranche-1 lanes + 8 tranche-2 lanes' if not _PRE.packets else ', '.join(PACKET_DIRS)}); "
      f"{S['packet_rows']} packet rows; {S['verdict_sites']} verdicted {'Ohio PIC-12 ' if not _PRE.packets else ''}sites "
      f"({S['verdict_sites_verified']} site-level VERIFIED); {S['entries_in_vocab_values']} in-vocab single values "
      f"after splitting `;`-packed rows (unit: record x field x value, all verdicts and scopes).")
    A(f"- **Site capability rows:** {S['site_rows_total']} sites carry VERIFIED site-scope rows "
      f"(unit: site rows); **{S['site_rows_apply']} APPLY, {S['site_rows_hold']} HOLD** "
      f"(non-active, non-plant `site_type` per R9, or lane/parent mismatch).")
    A(f"- **Sites with at least one field change under APPLY (unit: site rows): {S['sites_changed']}.**")
    A(f"- **Values added at sites (unit: new in-vocab values, APPLY rows only):** processes {sv['processes']}, "
      f"materials {sv['materials']}, markets_served {sv['markets_served']}, certifications (to site notes) "
      f"{sv['certifications(notes)']}. Held back because the field's existing value has off-vocabulary text "
      f"(REVIEW_EXISTING_OFFVOCAB): {fmt_counter(S['site_values_review'])}.")
    A(f"- **Organization capability rows:** {S['org_rows_total']} orgs carry VERIFIED org-scope rows "
      f"(unit: org rows, after dedupe: {S['org_entries_before_dedupe']} single-value rows collapse to "
      f"{S['org_values_after_dedupe']} org x field x value; {S['multi_lane_orgs']} orgs appear in more than one lane); "
      f"**{S['org_rows_apply']} APPLY, {S['org_rows_hold']} HOLD**; orgs with at least one field change: {S['orgs_changed']}.")
    A(f"- **Values added at orgs (unit: new in-vocab values, APPLY rows only):** processes {ov['processes']}, "
      f"materials {ov['materials']}, markets_served {ov['markets_served']}, certifications {ov['certifications']}. "
      f"Held (existing off-vocab text): {fmt_counter(S['org_values_review'])}.")
    A(f"- **Evidence rows drafted (unit: rows, one per record x field x value):** {S['evidence_rows']} "
      f"({fmt_counter(S['evidence_by_table'])}); {S['evidence_reconfirm']} of them reconfirm a value the row already "
      f"carried. All claim_type=`scope`, source_class=`own_site`, tier_effect=`{OWN_SITE_EFFECT}` (the own_site ceiling, "
      f"§4.13), created_by=`{CREATED_BY}`. {S['emails_redacted']} quote(s) had an email or phone string replaced with "
      f"`[email omitted]` / `[phone omitted]` (AGENTS.md §6; the packet's own quote stays in `tasks/`).")
    A(f"- **Bands (unit: rows):** sites APPLY {bs[('sites', 'APPLY')]} "
      f"(fill {S['bands_apply_fill']['sites']}, already-equal no-op {S['bands_apply_noop']['sites']}), "
      f"REVIEW {bs[('sites', 'REVIEW')]}, SKIP {bs[('sites', 'SKIP')]}; Ohio orgs (`employee_band_ohio`, Form 5500, R7f) "
      f"APPLY {bs[('organizations', 'APPLY')]} (fill {S['bands_apply_fill']['organizations']}, no-op "
      f"{S['bands_apply_noop']['organizations']}), REVIEW {bs[('organizations', 'REVIEW')]}, "
      f"SKIP {bs[('organizations', 'SKIP')]}. Site fills by winning source: {fmt_counter(S['bands_apply_fill_by_source'])}.")
    A(f"- **Conflicts rows (unit: rows):** {len(CONFLICTS)} — by class: " +
      ", ".join(f"{k} {v}" for k, v in S['conflict_classes'].most_common()) + ".")
    A("")
    A("## Band precedence")
    A("")
    A(r13)
    A("")
    A("Precedence: ITA (CY2025) -> OSHA inspection (latest with a count) -> Form 5500 (single-establishment org only). "
      "REVIEW = another source more than one band from the pick, or the pick differs from an existing in-vocabulary band "
      "(or the existing band is off-vocabulary). SKIP = the ITA row's `reliability` is `review`/`suspect` (the lane's own "
      "screens), or a Form 5500 site pick whose org no longer has exactly one site. Conservative extras added here, each "
      "visible in `reason`: site not active, ITA `site_caution`, a non-`strong` match on the pick source, other ITA filings "
      "at the site in a different band, Form 5500 `match_via_address_not_name` or matched org status not active. "
      "If the owner wants a flagged ITA row to fall back to the inspection band, the columns are all in the file.")
    A("")
    A("## Decisions I made (the integrator may overrule)")
    A("")
    A(f"1. **Certifications.** `sites` has no `certifications` column (header checked: {S['sites_have_cert_column']}); "
      f"`organizations` does ({S['orgs_have_cert_column']}). Site-scope certifications therefore go to a `CERT-SITE:` "
      "site-notes append (the R12 precedent records certification facts in site notes) and are NOT pushed up to the "
      "organization, because a plant's certificate is not a company-wide fact (the Parker rule). Org-scope certifications "
      "go to `organizations.certifications`. If the owner prefers a sites column, that is a schema revision.")
    A("2. **Value order** = the order of the lists in `docs/schema/vocab.json` (alphabetical). Proposed values are the union "
      "of the existing in-vocab tokens and the new ones in that order. Where nothing new is added the existing text is left "
      "byte-for-byte (no reordering).")
    A("3. **Off-vocab existing text is never merged.** A field whose current value holds any non-vocabulary token is "
      "REVIEW_EXISTING_OFFVOCAB: the new values are listed in `new_*` but `proposed_*` is blank, and the pair goes to "
      "`conflicts.csv`. Existing free text is frequent in Ohio rows (e.g. 'injection molding', 'polyurethane foam'). "
      "Normalizing that text is a vocabulary pass of its own.")
    A("4. **Never org-scope into sites; never site-scope into orgs.** Org rows are built only from org-scope packet rows.")
    A("5. **Not covered:** `site_capabilities.csv` (CAP rows under SCHEMA §3.6/§4.15 use a different vocabulary and grain "
      "rule). The QUEUE line names it as an alternative target; these sets update the tag columns only. Off-vocabulary "
      "`*_other_note` rows are not applied (they are in `conflicts.csv` with a v1.7.6 candidate-term hint for the tranche-1 "
      "packets that predate the vocabulary).")
    A("6. **Band evidence** is not drafted (no §4.13 claim_type fits a band; see `validate_dryrun.md`). The source date "
      "goes to a `BAND-SOURCE:` notes append because neither table has an `employee_count_source_date` column.")
    A("7. Tranche `wave-oh-capabilities-2026-11-01` (non-PIC-12 Ohio) is not an input of this pass; its packets are not here.")
    A("")
    A("## Application order for the integrator of record")
    A("")
    A("1. Review `conflicts.csv` (largest classes first) and `HOLD` rows; decide or return packets to lanes.")
    A("2. Claim the task in `tasks/QUEUE.md`. Take pre-pass backups of `data/sites_OH.csv`, the other touched site shards, "
      "`data/organizations_*.csv` shards touched, and `data/evidence.csv`.")
    A("3. Allocate `EVD-` IDs above the tree-wide maximum (`python3 scripts/atlas.py next-id EVD`) and replace each "
      "`<ALLOC>` in `evidence_rows.csv`; append to `data/evidence.csv`.")
    A("4. Apply `capability_site_updates.csv` APPLY rows to the site shards (`processes`, `materials`, `markets_served`) "
      "and append each `proposed_notes_append` to the site's `notes`.")
    A("5. Apply `capability_org_updates.csv` APPLY rows to the organization shards (four fields).")
    A("6. Apply `band_updates.csv` APPLY rows with action `fill` (`employee_band_site` / `employee_band_ohio`), appending "
      "`notes_append` to `notes`. REVIEW and SKIP rows wait for a ruling or a fresh source.")
    A("7. Re-run the `tier1_qualifier` derivation (the Ohio-band fills change the `employees_250plus` input); never hand-edit it.")
    A("8. `python3 scripts/validate.py` must pass; journal the pass with counts and unit labels; read back if pushing in "
      "campaign mode.")
    A("")
    A("## Dry-run result")
    A("")
    if dry_ok is None:
        A("Dry run not executed in this build (`--no-dryrun`).")
    else:
        A(f"**{'OK' if dry_ok else 'FAILED'}** — details in `validate_dryrun.md`. "
          f"Errors after applying: {S['dryrun_errors']}; warnings new vs. baseline: {S['dryrun_warnings_new']}.")
    A("")
    return "\n".join(L)


if __name__ == "__main__":
    sys.exit(main())

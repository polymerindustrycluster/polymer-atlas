#!/usr/bin/env python3
"""Validate the Polymer Atlas CSVs. Stdlib only. Exit 1 on any error.

Checks (v1 gate + schema v1.1/v1.2 additions, per AGENTS.md / docs/SCHEMA.md):
- org_id / site_id format and uniqueness
- ring_primary in 1..5; verification_tier in A/B/C/U
- every record has >=1 source; tier A/B records must have last_verified
- NAICS, when present, must carry source_type + confidence
- Ohio sites must have a county (owner-ruling 2026-10-29 parcel-queue exception)
- sites.org_id must exist in organizations.csv or ecosystem.csv
- [v1.2] pic_relationship_stage must NOT be present (retired at v1.2)
- [v1.1] organizations/sites new-column presence + shape checks
- [v1.2] membership citation rule: pic_member=true requires a
  polymerindustrycluster.org membership_source_url; no orphan citations
- [v1.1] registry_links.csv: FK, registry enum, ID formats, uniqueness
- [v1.2] members.csv: MBR ids, record_class/FK discipline, flag cross-check
- [v1.2] ecosystem record_grain + program/office grain checks
- [v1.2] people.csv: exact header, no contact fields, CRM-source tripwire
- [v1.3] ecosystem §4.6 drift fix: an institution-grain polymer_program=true
  claim must carry polymer_program_url (dated FLAGGED exception list warns,
  never blocks); parent_institution_org_id FK + self-parent check
- [v1.3] ipeds_unitid / ror_id confined to university_college rows, unique
- [v1.3] programs.csv discipline (PROG ids, FK, type/credential/level/CIP/
  completions) and institution rollups recomputed and compared; program
  grain in ecosystem.csv is an error; people.program_org_id → programs.csv
"""
import csv, re, sys
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
errors, warnings = [], []

def load(name, new_file=False):
    p = DATA / name
    if not p.exists():
        if new_file:
            errors.append(f"{name}: file missing (canonical from schema v1.2)")
            return [], []
        raise FileNotFoundError(name)
    with open(p, newline="", encoding="utf-8") as f:
        rdr = csv.DictReader(f)
        return list(rdr.fieldnames or []), list(rdr)

def vals(s):
    return [v.strip() for v in (s or "").split(";") if v.strip()]

PIC_HOST = "polymerindustrycluster.org"

def check_membership(fname, i, r, rid):
    pic = (r.get("pic_member") or "").strip()
    url = (r.get("membership_source_url") or "").strip()
    since = (r.get("member_since") or "").strip()
    if pic not in {"true", "false", ""}:
        errors.append(f"{fname}:{i} {rid} pic_member must be true/false/empty")
    if pic == "true":
        if not url:
            errors.append(f"{fname}:{i} {rid} pic_member=true without membership_source_url")
        elif urlparse(url).hostname != PIC_HOST:
            errors.append(f"{fname}:{i} {rid} membership_source_url is not the public PIC website list (AGENTS.md §5.1)")
    else:
        if url:
            errors.append(f"{fname}:{i} {rid} membership_source_url on a non-member record")
        if since:
            errors.append(f"{fname}:{i} {rid} member_since on a non-member record")
    if since and not re.fullmatch(r"\d{4}", since):
        errors.append(f"{fname}:{i} {rid} member_since is not a 4-digit year")

OWNERSHIP = {"public_company", "private_company", "private_equity_portfolio", "family_owned",
             "employee_owned", "nonprofit", "government", "academic", "cooperative", "unknown"}
CERTS = {"iso_9001", "iso_14001", "iatf_16949", "iso_13485", "as9100", "fda_registered",
         "cleanroom_iso7", "cleanroom_iso8", "itar", "ul_recognized", "nsf_certified_products", "glp_gmp"}
GEO_PRECISION = {"rooftop", "parcel", "address_interpolated", "zip_centroid", "city_centroid"}
REGISTRIES = {"LEI", "OHIO_SOS_CHARTER", "WIKIDATA", "SEC_CIK", "SEC_CIK_PARENT_FILER",
              "FRS", "TRI_TRIFID", "FDA_FEI", "EIN_NONPROFIT", "UEI"}
CREDENTIALS = {"phd", "ms", "bs", "aas_associate", "certificate", "registered_apprenticeship",
               "incumbent_worker_training", "noncredit_workforce"}
ENGAGEMENT = {"research_collaboration", "student_projects_capstone", "internships_coops",
              "testing_characterization_access", "lab_facility_access", "licensing_tech_transfer",
              "training_seats_open_enrollment", "customized_employer_training"}
OFFICE_MODES = {"licensing", "sponsored_research", "startup_formation", "materials_transfer", "facility_access"}
PROGRAM_TYPES = {"degree", "certificate", "apprenticeship", "center", "training",
                 "lab_facility", "course"}  # lab_facility + course added at v1.3 (V-8 amendment note)
LEVEL_MAP = {"phd": "doctorate", "ms": "master", "bs": "bachelor",
             "aas_associate": "associate", "certificate": "certificate",
             "registered_apprenticeship": None, "incumbent_worker_training": None,
             "noncredit_workforce": None}
LEVELS = {"certificate", "associate", "bachelor", "master", "doctorate", "none"}
CIP_SOURCE_TYPES = {"institution_published", "ipeds_listing", "researcher_inferred"}
ROLES = {"professor", "associate_professor", "assistant_professor", "research_professor",
         "center_director_professor"}
PROCESSES = {"injection_molding", "injection_molding_micro", "injection_molding_lsr_silicone",
             "insert_overmolding", "two_shot_molding", "blow_molding_extrusion", "blow_molding_injection",
             "blow_molding_stretch", "extrusion_film_blown", "extrusion_film_cast", "extrusion_sheet",
             "extrusion_profile", "extrusion_pipe_tube", "extrusion_wire_cable_coating",
             "thermoforming_vacuum", "thermoforming_pressure", "rotational_molding", "compression_molding",
             "transfer_molding", "calendering", "foam_molding_bead", "foam_molding_structural",
             "foam_extrusion", "foam_fabrication", "blow_molding", "rubber_mixing_compounding",
             "rubber_molding_compression", "rubber_molding_injection", "rubber_extrusion",
             "rubber_calendering", "tire_manufacturing", "tire_retreading", "latex_dipping_foaming",
             "hose_belting_manufacturing", "vulcanization_curing_services", "polymerization",
             "compounding_extrusion", "custom_compounding", "color_masterbatch", "pulverizing_grinding_resin",
             "coating_formulation", "adhesive_sealant_formulation", "ink_formulation", "silicone_formulation",
             "composites_hand_layup", "composites_rtm_infusion", "composites_pultrusion",
             "composites_filament_winding", "composites_compression_smc_bmc", "composites_prepreg_autoclave",
             "additive_manufacturing_polymer", "additive_manufacturing_polymer_production",
             "additive_manufacturing_metal", "plastics_machining_cnc", "plastics_fabrication_welding",
             "die_cutting_converting", "laminating", "coating_applying", "printing_decorating_plastics",
             "assembly_secondary_ops", "ultrasonic_solvent_bonding", "recycling_mechanical",
             "recycling_chemical_pyrolysis", "recycling_chemical_solvolysis", "regrind_pelletizing",
             "mold_tool_making", "tooling_repair_maintenance"}
MATERIALS = {"thermoplastics", "thermosets", "elastomers_rubber", "thermoplastic_elastomers_tpe_tpu",
             "silicones", "fluoropolymers", "bioplastics_biobased", "recycled_content_pcr_pir",
             "composites_frp", "composites_carbon", "composites_thermoset", "composites_thermoplastic",
             "foams_polymeric", "films_flexible_packaging", "coatings", "adhesives_sealants",
             "inks_colorants_masterbatch", "abs", "polyethylene_pe", "polypropylene_pp", "pvc",
             "pet_petg", "polystyrene_ps_hips", "polycarbonate_pc", "nylon_pa", "acetal_pom",
             "peek_high_performance", "epoxy", "polyurethane_pu", "phenolic", "melamine_urea_formaldehyde",
             "natural_rubber_nr", "sbr", "epdm", "nitrile_nbr", "neoprene_cr", "viton_fkm", "pla", "pha",
             "other_specified_in_notes"}
RESEARCH_SUPPLEMENT = {"polymer_physics", "rheology", "polymer_synthesis", "degradation_biodegradation",
                       "recycling_circularity", "composites_mechanics", "membranes_separations",
                       "biomedical_polymers", "additive_manufacturing_science", "characterization_methods",
                       "sustainable_feedstocks", "elastomer_science"}
RESEARCH_VOCAB = PROCESSES | MATERIALS | RESEARCH_SUPPLEMENT

# [pass 14 Stage C] Shard discovery (SCHEMA Appendix C): organizations and
# sites load as the union of their per-state shards. Pre-existing checks run
# over the union unchanged and keep the logical table names in messages;
# the shard rules V-34..V-38 below use the real file names.
def load_union(prefix):
    files = sorted(DATA.glob(f"{prefix}_*.csv"))
    if not files:
        errors.append(f"{prefix}: no shard files found (Appendix C layout)")
        return [], [], {}
    all_fields, all_rows, per_file = None, [], {}
    for f in files:
        flds, rows = load(f.name)
        if all_fields is None:
            all_fields = flds
        per_file[f.name] = (flds, rows)
        all_rows.extend(rows)
    return all_fields, all_rows, per_file
org_fields, orgs, ORG_SHARDS = load_union("organizations")
site_fields, sites, SITE_SHARDS = load_union("sites")
eco_fields, eco = load("ecosystem.csv")
link_fields, links = load("registry_links.csv", new_file=True)
member_fields, members = load("members.csv", new_file=True)
people_fields, people = load("people.csv", new_file=True)
prog_fields, programs = load("programs.csv", new_file=True)
event_fields, events = load("events.csv", new_file=True)
part_fields, participation = load("event_participation.csv", new_file=True)
evd_fields, evidence = load("evidence.csv", new_file=True)
rel_fields, relationships = load("relationships.csv", new_file=True)
cap_fields, capabilities = load("site_capabilities.csv", new_file=True)

# V-2: retired column must not ship
for fname, fields in (("organizations.csv", org_fields), ("ecosystem.csv", eco_fields)):
    if "pic_relationship_stage" in fields:
        errors.append(f"{fname}: pic_relationship_stage present — retired at schema v1.2; values are archived in staging; the column must not ship")

# V-3b [v1.6]: new columns on organizations + sites
for col in ("last_activity_evidence_date", "liveness_signal", "monitor_watch",
            "tier1_qualifier", "tier1_qualifier_basis"):
    if col not in org_fields:
        errors.append(f"organizations.csv: missing v1.6 column {col}")
for col in ("county_source", "site_group_id"):
    if col not in site_fields:
        errors.append(f"sites.csv: missing v1.6 column {col}")

# V-3: organizations new columns
for col in ("year_founded", "stock_ticker", "ownership_type", "certifications",
            "pic_member", "member_since", "membership_source_url"):
    if col not in org_fields:
        errors.append(f"organizations.csv: missing v1.1/v1.2 column {col}")

org_ids = set()
org_member_true = set()
for i, r in enumerate(orgs, 2):
    oid = r["org_id"].strip()
    if not re.fullmatch(r"ORG-\d{6}", oid):
        errors.append(f"organizations.csv:{i} bad org_id {oid!r}")
    if oid in org_ids:
        errors.append(f"organizations.csv:{i} duplicate org_id {oid}")
    org_ids.add(oid)
    if r["ring_primary"].strip() not in {"1", "2", "3", "4", "5"}:
        errors.append(f"organizations.csv:{i} {oid} ring_primary not 1-5")
    if r["verification_tier"].strip() not in {"A", "B", "C", "U"}:
        errors.append(f"organizations.csv:{i} {oid} bad verification_tier")
    if not r["sources"].strip():
        errors.append(f"organizations.csv:{i} {oid} has no source")
    if r["verification_tier"].strip() in {"A", "B"} and not r["last_verified"].strip():
        errors.append(f"organizations.csv:{i} {oid} tier A/B without last_verified")
    if r["naics_primary"].strip():
        if not r["naics_primary_source_type"].strip() or not r["naics_confidence"].strip():
            errors.append(f"organizations.csv:{i} {oid} NAICS without provenance/confidence")
    if not r["description_1line"].strip():
        warnings.append(f"organizations.csv:{i} {oid} missing description_1line")
    succ = r.get("successor_org_id", "").strip()
    if succ and succ not in org_ids and succ == oid:
        errors.append(f"organizations.csv:{i} {oid} is its own successor")
    yf = (r.get("year_founded") or "").strip()
    if yf and not (re.fullmatch(r"\d{4}", yf) and 1600 <= int(yf) <= 2026):
        errors.append(f"organizations.csv:{i} {oid} year_founded is not a 4-digit year in 1600-2026")
    ot = (r.get("ownership_type") or "").strip()
    if ot and ot not in OWNERSHIP:
        errors.append(f"organizations.csv:{i} {oid} ownership_type {ot!r} not in SCHEMA §4.4 enum")
    for c in vals(r.get("certifications")):
        if c not in CERTS:
            errors.append(f"organizations.csv:{i} {oid} certifications value {c!r} not in §3.4 vocabulary")
    check_membership("organizations.csv", i, r, oid)
    if (r.get("pic_member") or "").strip() == "true":
        org_member_true.add(oid)

eco_ids = {r["org_id"].strip() for r in eco}
all_ids = org_ids | eco_ids

# V-8/V-9/V-10: ecosystem grains + membership
# [pass-15 waiver, owner ruling 2026-10-30] Merged-status ecosystem tombstones that name a
# programs.csv successor are EXEMPT from the SCHEMA §4.6 ecosystem_subtype MUST (see the waiver
# text in docs/SCHEMA.md §4.6). No subtype check is enforced here today; this note records
# that the exemption is deliberate, so a future subtype check must exempt status=merged rows
# whose notes name a PROG- successor rather than flagging them.
# [v1.3 amendment] record_grain narrows to institution|office: program records
# live in data/programs.csv (§4.11), and the v1.2 program-grain columns are
# retired — their substance is enforced on programs.csv by V-15.
eco_by_id = {}
eco_member_true = set()
ECO_NEW = ("record_grain", "parent_institution_org_id", "public_door_url",
           "office_name", "tto_url", "industry_partnership_modes",
           "technology_areas", "pic_member", "member_since", "membership_source_url",
           "polymer_program_url", "ipeds_unitid", "ror_id")
ECO_RETIRED_V13 = ("program_name", "program_type", "credential_types", "program_url",
                   "specialty_processes", "specialty_materials", "research_areas",
                   "engagement_modes", "apprenticeship_registered",
                   "employer_custom_training", "admissions_status", "facilities_note",
                   "scale_band")
for col in ECO_NEW:
    if col not in eco_fields:
        errors.append(f"ecosystem.csv: missing schema column {col}")
for col in ECO_RETIRED_V13:
    if col in eco_fields:
        errors.append(f"ecosystem.csv: {col} present — program-grain columns retired at schema v1.3; program records live in data/programs.csv")
for i, r in enumerate(eco, 2):
    oid = r["org_id"].strip()
    eco_by_id[oid] = r
    grain = (r.get("record_grain") or "").strip()
    if grain == "program":
        errors.append(f"ecosystem.csv:{i} {oid} record_grain=program — program records live in data/programs.csv since v1.3 (V-8 as amended)")
    elif grain not in {"institution", "office"}:
        errors.append(f"ecosystem.csv:{i} {oid} record_grain must be institution/office")
    check_membership("ecosystem.csv", i, r, oid)
    if (r.get("pic_member") or "").strip() == "true":
        eco_member_true.add(oid)
    if grain == "office":
        for col in ("office_name", "tto_url", "public_door_url"):
            if not (r.get(col) or "").strip():
                errors.append(f"ecosystem.csv:{i} {oid} office record without {col}")
        parent = (r.get("parent_institution_org_id") or "").strip()
        if not parent or parent not in all_ids:
            errors.append(f"ecosystem.csv:{i} {oid} office parent_institution_org_id missing/dangling")
        modes = vals(r.get("industry_partnership_modes"))
        if not modes:
            errors.append(f"ecosystem.csv:{i} {oid} office record without industry_partnership_modes")
        for m in modes:
            if m not in OFFICE_MODES:
                errors.append(f"ecosystem.csv:{i} {oid} industry_partnership_modes value {m!r} not in enum")

# V-13 [v1.3]: ecosystem §4.6 institution-grain drift fix
# (design drift_fix_design.md rule V-12, renumbered: the applied sequence
# already ran to V-12 at v1.2, so the v1.3 rules continue it — design V-12 →
# applied V-13, V-13 → V-14, V-14 → V-15, V-15 → V-16.)
# Dated FLAGGED exception list from drift_backfill_packet.csv: these orgs
# claim a polymer program but no program page of their own is in evidence
# yet. They WARN, never block; an org leaves the list only when its value
# lands. Settling fact = the evidence that resolves the entry.
V13_URL_PENDING = {
    "ORG-001211": "AFRL's own page for the Polymer Matrix Composite Materials and Processing Research Team (or its parent Materials and Manufacturing Directorate polymer page) on afrl.af.mil. Current evidence is a GovTribe contract record — not a program page.",
    "ORG-001212": "The museum's own Polymer Palooza program/event page URL. Current evidence is the PIC homepage (a partner listing), not the program's page.",
    "ORG-001213": "Akron Public Schools' own Zipping to STEM program page URL. Current evidence is a Greater Akron Chamber cluster-update article — a partner's page, not the program's.",
    "ORG-001224": "Barberton City Schools' own Polymer Pathway page URL. Current evidence is the funder initiative's page (greaterakronchamber.org/goodjobschallenge) — the initiative's page, not the schools' pathway page.",
    "ORG-001225": "The Polymer Pathway program page (the foundation's own page, or the schools' pathway page adopted as the program's public page). Current evidence is the funder initiative's page only.",
    "ORG-001230": "The chamber's own APEX (Advanced Polymer and Manufacturing Excellence) program page URL. Current evidence is the Good Jobs Challenge initiative page, not the APEX page.",
    "ORG-001247": "The foundation's own Once Upon a Polymer program page URL. Current evidence is a NEO-SMART partners listing.",
    "ORG-001264": "NASA Glenn's own Polymers Branch page URL (nasa.gov/glenn). Current evidence is an NTRS technical-report PDF — a publication, not the branch's page.",
    "ORG-001278": "ODOD's own Ohio Innovation Hubs program page URL (development.ohio.gov). Current evidence is a PIC news post and an ODOD news release — announcements, not the program page.",
    "ORG-001299": "Sinclair's own program page for the AAS in Industrial Engineering Technology, Plastics and Composites Option (sinclair.edu). Current evidence is a campusprogram.com aggregator page — aggregators cannot carry a MUST field.",
    "ORG-001310": "Terra State's own page for its plastics program (terra.edu). Current evidence is aggregator listings only (collegesimply, campusprogram).",
    "ORG-001311": "The Tire Society's own conference page URL (Annual Conference on Tire Science and Technology). The record carries no website at all; its only evidence URL is a chamber directory listing.",
}
V13_PENDING_SINCE = "2026-10-29"
for i, r in enumerate(eco, 2):
    oid = r["org_id"].strip()
    if (r.get("record_grain") or "").strip() != "institution":
        continue
    pp = (r.get("polymer_program") or "").strip()
    url = (r.get("polymer_program_url") or "").strip()
    if pp == "true":
        if not url:
            if oid in V13_URL_PENDING:
                warnings.append(f"ecosystem.csv:{i} {oid} polymer_program=true without polymer_program_url — pending since {V13_PENDING_SINCE}; settles with: {V13_URL_PENDING[oid]}")
            else:
                errors.append(f"ecosystem.csv:{i} {oid} polymer_program=true without polymer_program_url")
        else:
            purl = urlparse(url)
            if purl.scheme not in {"http", "https"} or not purl.hostname:
                errors.append(f"ecosystem.csv:{i} {oid} polymer_program_url is not an http(s) URL")
            if oid in V13_URL_PENDING:
                errors.append(f"ecosystem.csv:{i} {oid} carries a polymer_program_url but is still on the V-13 pending list — remove it from V13_URL_PENDING")
    elif pp == "false" and url:
        errors.append(f"ecosystem.csv:{i} {oid} polymer_program_url on a polymer_program=false row (orphan evidence)")
    parent = (r.get("parent_institution_org_id") or "").strip()
    if parent:
        if parent == oid:
            errors.append(f"ecosystem.csv:{i} {oid} is its own parent_institution")
        elif parent not in all_ids:
            errors.append(f"ecosystem.csv:{i} {oid} parent_institution_org_id {parent!r} dangling")

# V-14 [v1.3]: ecosystem institutional identifiers
# (design identifiers_design.md rule V-13, renumbered.) No completeness
# error: a university_college row without identifiers is legal; absence is
# visible in the file, not a validation failure.
seen_ipeds, seen_ror = {}, {}
for i, r in enumerate(eco, 2):
    oid = r["org_id"].strip()
    sub = (r.get("ecosystem_subtype") or "").strip()
    ip = (r.get("ipeds_unitid") or "").strip()
    rr = (r.get("ror_id") or "").strip()
    if (ip or rr) and sub != "university_college":
        errors.append(f"ecosystem.csv:{i} {oid} carries institutional identifiers but subtype is {sub!r} (identifiers are university_college-scoped)")
    if ip:
        if not re.fullmatch(r"\d{6}", ip):
            errors.append(f"ecosystem.csv:{i} {oid} ipeds_unitid {ip!r} is not a 6-digit IPEDS UnitID")
        if ip in seen_ipeds:
            errors.append(f"ecosystem.csv:{i} {oid} ipeds_unitid duplicates {seen_ipeds[ip]}")
        seen_ipeds[ip] = oid
    if rr:
        if not re.fullmatch(r"https://ror\.org/[0-9a-z]{9}", rr):
            errors.append(f"ecosystem.csv:{i} {oid} ror_id {rr!r} is not a canonical ROR URI")
        if rr in seen_ror:
            errors.append(f"ecosystem.csv:{i} {oid} ror_id duplicates {seen_ror[rr]}")
        seen_ror[rr] = oid

# V-5: sites new columns
for col in ("street_address", "latitude", "longitude", "geocode_precision"):
    if col not in site_fields:
        errors.append(f"sites.csv: missing v1.1 column {col}")
site_ids = set()
for i, r in enumerate(sites, 2):
    sid = r["site_id"].strip()
    if not re.fullmatch(r"SITE-\d{6}", sid):
        errors.append(f"sites.csv:{i} bad site_id {sid!r}")
    if sid in site_ids:
        errors.append(f"sites.csv:{i} duplicate site_id {sid}")
    site_ids.add(sid)
    if r["org_id"].strip() not in all_ids:
        errors.append(f"sites.csv:{i} {sid} org_id {r['org_id']!r} not found")
    if r["state"].strip() == "OH" and not r["county"].strip():
        # Owner ruling 2026-10-29: a blank county is permitted ONLY when the
        # site is explicitly queued for the parcel layer (notes carry the
        # marker "parcel candidate queue"). Any other blank Ohio county is
        # an error — the exception marks a pending state, never missing data.
        if "parcel candidate queue" in r["notes"]:
            warnings.append(f"sites.csv:{i} {sid} Ohio site without county (parcel candidate queue — permitted, owner ruling 2026-10-29)")
        else:
            errors.append(f"sites.csv:{i} {sid} Ohio site without county")
    if r["verification_tier"].strip() not in {"A", "B", "C", "U"}:
        errors.append(f"sites.csv:{i} {sid} bad verification_tier")
    if not r["sources"].strip():
        errors.append(f"sites.csv:{i} {sid} has no source")
    lat, lon = (r.get("latitude") or "").strip(), (r.get("longitude") or "").strip()
    prec = (r.get("geocode_precision") or "").strip()
    if bool(lat) != bool(lon):
        errors.append(f"sites.csv:{i} {sid} latitude/longitude must be present together")
    if lat:
        try:
            if not -90 <= float(lat) <= 90:
                errors.append(f"sites.csv:{i} {sid} latitude out of range")
        except ValueError:
            errors.append(f"sites.csv:{i} {sid} latitude is not a number")
    if lon:
        try:
            if not -180 <= float(lon) <= 180:
                errors.append(f"sites.csv:{i} {sid} longitude out of range")
        except ValueError:
            errors.append(f"sites.csv:{i} {sid} longitude is not a number")
    if prec and prec not in GEO_PRECISION:
        errors.append(f"sites.csv:{i} {sid} geocode_precision {prec!r} not in enum")
    if (lat or lon) and not prec:
        errors.append(f"sites.csv:{i} {sid} coordinates without geocode_precision")

# V-6: registry links
seen_links = set()
for i, r in enumerate(links, 2):
    oid = (r.get("org_id") or "").strip()
    reg = (r.get("registry") or "").strip()
    rid = (r.get("registry_id") or "").strip()
    if oid not in all_ids:
        errors.append(f"registry_links.csv:{i} dangling org_id {oid!r}")
    if reg not in REGISTRIES:
        errors.append(f"registry_links.csv:{i} registry {reg!r} not in §4.8 enum")
    if not rid:
        errors.append(f"registry_links.csv:{i} empty registry_id")
    if reg == "LEI" and not re.fullmatch(r"[A-Z0-9]{18}[0-9]{2}", rid):
        errors.append(f"registry_links.csv:{i} LEI {rid!r} fails ISO 17442 shape")
    if reg in {"SEC_CIK", "SEC_CIK_PARENT_FILER"} and not re.fullmatch(r"\d{10}", rid):
        errors.append(f"registry_links.csv:{i} CIK {rid!r} is not zero-padded 10 digits")
    if reg == "WIKIDATA" and not re.fullmatch(r"Q\d+", rid):
        errors.append(f"registry_links.csv:{i} Wikidata id {rid!r} is not a QID")
    if not (r.get("match_basis") or "").strip():
        errors.append(f"registry_links.csv:{i} link without match_basis")
    try:
        datetime.strptime((r.get("as_of") or "").strip(), "%Y-%m-%d")
    except ValueError:
        errors.append(f"registry_links.csv:{i} as_of is not a date")
    key = (oid, reg, rid)
    if key in seen_links:
        errors.append(f"registry_links.csv:{i} duplicate link triple {key}")
    seen_links.add(key)

# V-7: members + flag cross-check
member_ids, member_org_links, member_eco_links = set(), set(), set()
for i, r in enumerate(members, 2):
    mid = (r.get("member_row_id") or "").strip()
    if not re.fullmatch(r"MBR-\d{6}", mid):
        errors.append(f"members.csv:{i} bad member_row_id {mid!r}")
    if mid in member_ids:
        errors.append(f"members.csv:{i} duplicate member_row_id {mid}")
    member_ids.add(mid)
    cls = (r.get("record_class") or "").strip()
    oid = (r.get("org_id") or "").strip()
    if cls not in {"organization", "ecosystem", "member_only"}:
        errors.append(f"members.csv:{i} {mid} record_class {cls!r} not in enum")
    if cls == "organization":
        if oid not in org_ids:
            errors.append(f"members.csv:{i} {mid} organization FK {oid!r} not in organizations.csv")
        member_org_links.add(oid)
    if cls == "ecosystem":
        if oid not in eco_ids:
            errors.append(f"members.csv:{i} {mid} ecosystem FK {oid!r} not in ecosystem.csv")
        member_eco_links.add(oid)
    if cls == "member_only" and oid:
        errors.append(f"members.csv:{i} {mid} member_only row carries org_id {oid!r}")
    url = (r.get("membership_source_url") or "").strip()
    if not url:
        errors.append(f"members.csv:{i} {mid} without membership_source_url")
    elif urlparse(url).hostname != PIC_HOST:
        errors.append(f"members.csv:{i} {mid} membership_source_url is not the public PIC website list (AGENTS.md §5.1)")
    since = (r.get("member_since") or "").strip()
    if since and not re.fullmatch(r"\d{4}", since):
        errors.append(f"members.csv:{i} {mid} member_since is not a 4-digit year")
if member_org_links != org_member_true:
    errors.append(f"members.csv/organizations.csv pic_member drift: table links {sorted(member_org_links - org_member_true)} unflagged; flags {sorted(org_member_true - member_org_links)} unlinked")
if member_eco_links != eco_member_true:
    errors.append(f"members.csv/ecosystem.csv pic_member drift: table links {sorted(member_eco_links - eco_member_true)} unflagged; flags {sorted(eco_member_true - member_eco_links)} unlinked")

# V-15 [v1.3]: programs.csv
# (design programs_table_design.md rule V-14, renumbered.)
PROGRAM_FIELDS = ["program_id", "institution_org_id", "program_name", "program_type",
    "credential_types", "level", "cip_code", "cip_source_type", "unit_department",
    "description_1line", "url", "public_door_url", "first_year_awarded",
    "last_year_awarded", "latest_completions", "completions_year",
    "specialty_processes", "specialty_materials", "research_areas",
    "engagement_modes", "apprenticeship_registered", "employer_custom_training",
    "admissions_status", "facilities_note", "scale_band", "geography_served",
    "city", "state", "county", "status", "sources", "verification_tier",
    "last_verified", "pic_relevance", "created_by", "notes"]
if prog_fields != PROGRAM_FIELDS:
    errors.append(f"programs.csv: header must be exactly the §4.11 field set, got {prog_fields}")
program_ids = set()
programs_by_inst = {}
for i, r in enumerate(programs, 2):
    pid = (r.get("program_id") or "").strip()
    if not re.fullmatch(r"PROG-\d{6}", pid):
        errors.append(f"programs.csv:{i} bad program_id {pid!r}")
    if pid in program_ids:
        errors.append(f"programs.csv:{i} duplicate program_id {pid}")
    program_ids.add(pid)
    inst = (r.get("institution_org_id") or "").strip()
    if inst not in all_ids:
        errors.append(f"programs.csv:{i} {pid} institution_org_id {inst!r} dangling")
    programs_by_inst.setdefault(inst, []).append(r)
    ptype = (r.get("program_type") or "").strip()
    if ptype not in PROGRAM_TYPES:
        errors.append(f"programs.csv:{i} {pid} program_type {ptype!r} not in §4.11 enum")
    creds = vals(r.get("credential_types"))
    if ptype in {"degree", "certificate", "apprenticeship"} and not creds:
        errors.append(f"programs.csv:{i} {pid} credential_types required for program_type {ptype}")
    for c in creds:
        if c not in CREDENTIALS:
            errors.append(f"programs.csv:{i} {pid} credential_types value {c!r} not in enum")
    lev = vals(r.get("level"))
    for lv in lev:
        if lv not in LEVELS:
            errors.append(f"programs.csv:{i} {pid} level value {lv!r} not in §4.11 enum")
    derived = {LEVEL_MAP[c] for c in creds if LEVEL_MAP.get(c)} or {"none"}
    if set(lev) != derived:
        errors.append(f"programs.csv:{i} {pid} level {sorted(set(lev))} != derivation {sorted(derived)} from credential_types")
    cip = (r.get("cip_code") or "").strip()
    cst = (r.get("cip_source_type") or "").strip()
    if cip:
        if not re.fullmatch(r"\d{2}\.\d{4}", cip):
            errors.append(f"programs.csv:{i} {pid} cip_code {cip!r} is not NN.NNNN")
        if cst not in CIP_SOURCE_TYPES:
            errors.append(f"programs.csv:{i} {pid} cip_code without a valid cip_source_type")
    elif cst:
        errors.append(f"programs.csv:{i} {pid} cip_source_type without cip_code")
    comp = {c: (r.get(c) or "").strip() for c in
            ("first_year_awarded", "last_year_awarded", "latest_completions", "completions_year")}
    if any(comp.values()) and ptype != "degree":
        errors.append(f"programs.csv:{i} {pid} completions fields on a non-degree program")
    for c in ("first_year_awarded", "last_year_awarded", "completions_year"):
        if comp[c] and not re.fullmatch(r"\d{4}", comp[c]):
            errors.append(f"programs.csv:{i} {pid} {c} is not a 4-digit year")
    if comp["latest_completions"]:
        try:
            if int(comp["latest_completions"]) < 0:
                errors.append(f"programs.csv:{i} {pid} latest_completions is negative")
        except ValueError:
            errors.append(f"programs.csv:{i} {pid} latest_completions is not an integer")
        if not comp["completions_year"]:
            errors.append(f"programs.csv:{i} {pid} latest_completions without completions_year")
    for col in ("url", "public_door_url"):
        if not (r.get(col) or "").strip():
            errors.append(f"programs.csv:{i} {pid} without {col}")
    modes = vals(r.get("engagement_modes"))
    if not modes:
        errors.append(f"programs.csv:{i} {pid} without engagement_modes")
    for m in modes:
        if m not in ENGAGEMENT:
            errors.append(f"programs.csv:{i} {pid} engagement_modes value {m!r} not in enum")
    for a in vals(r.get("specialty_processes")):
        if a not in PROCESSES:
            errors.append(f"programs.csv:{i} {pid} specialty_processes value {a!r} not in §3.1 vocabulary")
    for a in vals(r.get("specialty_materials")):
        if a not in MATERIALS:
            errors.append(f"programs.csv:{i} {pid} specialty_materials value {a!r} not in §3.2 vocabulary")
    for a in vals(r.get("research_areas")):
        if a not in RESEARCH_VOCAB:
            errors.append(f"programs.csv:{i} {pid} research_areas value {a!r} not in §3.1/§3.2/§3.5 vocabulary")
    adm = (r.get("admissions_status") or "").strip()
    if adm and adm not in {"admitting", "not_admitting", "unknown"}:
        errors.append(f"programs.csv:{i} {pid} admissions_status {adm!r} not in enum")
    if not (r.get("sources") or "").strip():
        errors.append(f"programs.csv:{i} {pid} has no source")
    if (r.get("verification_tier") or "").strip() not in {"A", "B", "C", "U"}:
        errors.append(f"programs.csv:{i} {pid} bad verification_tier")
    if (r.get("verification_tier") or "").strip() in {"A", "B"} and not (r.get("last_verified") or "").strip():
        errors.append(f"programs.csv:{i} {pid} tier A/B without last_verified")

# V-16 [v1.3]: program rollup + cross-file consistency
# (design programs_table_design.md rule V-15, renumbered; scoped to
# institution-grain rows — the §4.11 rollup binds institutions. Office-grain
# anchors carry no rollup fields; a program row keyed to an office record
# (e.g. ORG-002121) is checked by V-15's FK rule only.)
TYPE_PREC = {"degree": 0, "center": 1, "certificate": 2, "apprenticeship": 3,
             "training": 4, "lab_facility": 5, "course": 6}
for i, r in enumerate(eco, 2):
    oid = r["org_id"].strip()
    if (r.get("record_grain") or "").strip() != "institution":
        continue
    P = [p for p in programs_by_inst.get(oid, [])
         if (p.get("status") or "").strip() != "tombstoned"]
    pp = (r.get("polymer_program") or "").strip()
    if P:
        srt = sorted(P, key=lambda p: (TYPE_PREC[(p.get("program_type") or "").strip()],
                                       (p.get("program_name") or "").strip().lower()))
        expect_name = "; ".join((p.get("program_name") or "").strip() for p in srt)
        expect_url = (srt[0].get("url") or "").strip()
        if (r.get("polymer_program_name") or "").strip() != expect_name:
            errors.append(f"ecosystem.csv:{i} {oid} polymer_program_name drifts from the §4.11 rollup of its program rows")
        if (r.get("polymer_program_url") or "").strip() != expect_url:
            errors.append(f"ecosystem.csv:{i} {oid} polymer_program_url drifts from the §4.11 rollup of its program rows")
        if pp == "false":
            errors.append(f"ecosystem.csv:{i} {oid} polymer_program=false alongside program rows (contradiction)")
    elif pp == "true":
        warnings.append(f"ecosystem.csv:{i} {oid} claims a polymer program with no program rows — un-decomposed claim (V-16)")

# V-11: people
PEOPLE_FIELDS = ["person_id", "full_name", "institution_org_id", "program_org_id", "role",
                 "role_as_published", "research_specialties", "public_profile_url", "sources",
                 "verification_tier", "last_verified"]
if people_fields != PEOPLE_FIELDS:
    errors.append(f"people.csv: header must be exactly the §4.9 field set, got {people_fields}")
for col in people_fields:
    if re.search(r"email|phone|tel|address|contact", col, re.I):
        errors.append(f"people.csv: contact-shaped column {col!r} is barred in the people class (§4.9)")
person_ids = set()
for i, r in enumerate(people, 2):
    pid = (r.get("person_id") or "").strip()
    if not re.fullmatch(r"PERSON-\d{6}", pid):
        errors.append(f"people.csv:{i} bad person_id {pid!r}")
    if pid in person_ids:
        errors.append(f"people.csv:{i} duplicate person_id {pid}")
    person_ids.add(pid)
    if (r.get("institution_org_id") or "").strip() not in all_ids:
        errors.append(f"people.csv:{i} {pid} institution_org_id dangling")
    prog = (r.get("program_org_id") or "").strip()
    if prog and prog not in program_ids:
        errors.append(f"people.csv:{i} {pid} program_org_id does not resolve to a programs.csv record (V-11 as amended at v1.3)")
    if (r.get("role") or "").strip() not in ROLES:
        errors.append(f"people.csv:{i} {pid} role not in §4.9 enum")
    if not (r.get("role_as_published") or "").strip():
        errors.append(f"people.csv:{i} {pid} without role_as_published")
    src = (r.get("sources") or "").strip()
    if not src:
        errors.append(f"people.csv:{i} {pid} has no source")
    if re.search(r"crm|frappe", src, re.I):
        errors.append(f"people.csv:{i} {pid} source references the CRM — CRM is not an admissible source for people records (AGENTS.md §6)")
    if (r.get("verification_tier") or "").strip() not in {"A", "B", "C", "U"}:
        errors.append(f"people.csv:{i} {pid} bad verification_tier")
    if (r.get("verification_tier") or "").strip() in {"A", "B"} and not (r.get("last_verified") or "").strip():
        errors.append(f"people.csv:{i} {pid} tier A/B without last_verified")


# V-17..V-21 [v1.5]: events layer (SCHEMA §4.12)
EVENT_FIELDS = ["event_id", "name", "trade_names", "organizer_name", "organizer_org_id",
                "event_format", "cadence", "cadence_note", "typical_timing", "home_city",
                "home_state", "home_region", "geography_note", "subject_scope",
                "subject_note", "event_url", "status", "status_date", "status_source",
                "sources", "verification_tier", "last_verified", "pic_relevance",
                "created_by", "notes"]
PART_FIELDS = ["participation_id", "event_id", "org_id", "edition_year", "edition_name",
               "role", "role_detail", "edition_dates", "edition_city", "edition_state",
               "evidence_source_name", "evidence_source_url", "evidence_date", "sources",
               "verification_tier", "last_verified", "created_by", "notes"]
SUBJECT_VOCAB = {"plastics_general", "rubber_elastomers", "compounding_formulation",
                 "recycling_circularity", "composites", "tooling_molds",
                 "plastics_processing_technology", "polyurethanes", "silicones",
                 "foams", "adhesives_sealants", "cluster_convening"}
EVENT_FORMATS = {"expo", "conference", "technical_conference", "summit", "meeting_series"}
CADENCES = {"annual", "biennial", "triennial", "irregular"}
HOME_REGIONS = {"ne_ohio", "ohio", "national_us", "international"}
ROLES = {"exhibitor", "sponsor", "speaker", "organizer", "host"}
EVENT_STATUSES = {"active", "active_idled_partial", "idled", "closed", "acquired",
                  "merged", "relocated_in_scope", "relocated_out_of_scope",
                  "pre_revenue", "unknown"}
USPS = {"AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "FL", "GA", "HI", "ID", "IL",
        "IN", "IA", "KS", "KY", "LA", "ME", "MD", "MA", "MI", "MN", "MS", "MO", "MT",
        "NE", "NV", "NH", "NJ", "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI",
        "SC", "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY", "DC"}
EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
PHONE_RE = re.compile(r"(\(\d{3}\)\s*|\b\d{3}[-.])\d{3}[-.]\d{4}\b")
if events or participation:
    if event_fields != EVENT_FIELDS:
        errors.append("events.csv: header does not match the v1.5 field set (V-17)")
    if part_fields != PART_FIELDS:
        errors.append("event_participation.csv: header does not match the v1.5 field set (V-17)")
ALL_ORG_IDS = {r["org_id"] for r in orgs} | {r["org_id"] for r in eco}
evt_ids = set()
for i, r in enumerate(events, 2):
    eid = r["event_id"]
    if not re.fullmatch(r"EVT-\d{6}", eid or ""):
        errors.append(f"events.csv:{i} {eid} event_id does not match EVT-###### (V-17)")
    if eid in evt_ids:
        errors.append(f"events.csv:{i} {eid} duplicate event_id (V-17)")
    evt_ids.add(eid)
    if r["cadence"] not in CADENCES:
        errors.append(f"events.csv:{i} {eid} bad cadence (V-17)")
    if (r["cadence"] == "irregular") != bool((r["cadence_note"] or "").strip()):
        errors.append(f"events.csv:{i} {eid} cadence_note present iff cadence=irregular (V-17)")
    if r["home_region"] not in HOME_REGIONS:
        errors.append(f"events.csv:{i} {eid} bad home_region (V-17)")
    if r["event_format"] not in EVENT_FORMATS:
        errors.append(f"events.csv:{i} {eid} bad event_format (V-17)")
    subs = vals(r["subject_scope"])
    if not subs or not set(subs) <= SUBJECT_VOCAB:
        errors.append(f"events.csv:{i} {eid} subject_scope empty or outside the \u00a74.12.1 vocabulary (V-17)")
    fk = (r["organizer_org_id"] or "").strip()
    if fk and fk not in ALL_ORG_IDS:
        errors.append(f"events.csv:{i} {eid} organizer_org_id {fk} does not resolve (V-17)")
    if not fk and not (r["organizer_name"] or "").strip():
        errors.append(f"events.csv:{i} {eid} organizer_org_id and organizer_name both empty (V-17)")
    if r["status"] not in EVENT_STATUSES:
        errors.append(f"events.csv:{i} {eid} bad status (V-17)")
    if r["status"] != "active" and (not r["status_date"] or not r["status_source"]):
        errors.append(f"events.csv:{i} {eid} non-active status without status_date/status_source (V-17)")
    if (r["verification_tier"] or "").strip() not in {"A", "B", "C"}:
        errors.append(f"events.csv:{i} {eid} verification_tier must be A/B/C \u2014 a series row is never U (V-17)")
    for fld in ("notes", "evidence_source_name"):
        pass
    if EMAIL_RE.search(r["notes"] or "") or PHONE_RE.search(r["notes"] or ""):
        errors.append(f"events.csv:{i} {eid} contact-pattern string in notes (V-21)")
evp_ids = set(); evp_tuples = set()
for i, r in enumerate(participation, 2):
    pid = r["participation_id"]
    if not re.fullmatch(r"EVP-\d{6}", pid or ""):
        errors.append(f"event_participation.csv:{i} {pid} participation_id does not match EVP-###### (V-18)")
    if pid in evp_ids:
        errors.append(f"event_participation.csv:{i} {pid} duplicate participation_id (V-18)")
    evp_ids.add(pid)
    if r["event_id"] not in evt_ids:
        errors.append(f"event_participation.csv:{i} {pid} event_id does not resolve (V-18)")
    if r["org_id"] not in ALL_ORG_IDS:
        errors.append(f"event_participation.csv:{i} {pid} org_id does not resolve (V-18)")
    tup = (r["event_id"], r["org_id"], r["edition_year"], r["role"])
    if tup in evp_tuples:
        errors.append(f"event_participation.csv:{i} {pid} duplicate (event_id, org_id, edition_year, role) tuple (V-18)")
    evp_tuples.add(tup)
    if r["role"] not in ROLES:
        errors.append(f"event_participation.csv:{i} {pid} bad role (V-19)")
    try:
        yr = int(r["edition_year"])
        if not (1990 <= yr <= 2029):
            errors.append(f"event_participation.csv:{i} {pid} edition_year out of range (V-20)")
    except (TypeError, ValueError):
        errors.append(f"event_participation.csv:{i} {pid} edition_year not an integer (V-20)")
    st = (r["edition_state"] or "").strip()
    if st and st not in USPS and len(st) <= 2:
        warnings.append(f"event_participation.csv:{i} {pid} edition_state shape suspect (V-20)")
    for fld in ("role_detail", "notes", "evidence_source_name"):
        if EMAIL_RE.search(r[fld] or "") or PHONE_RE.search(r[fld] or ""):
            errors.append(f"event_participation.csv:{i} {pid} contact-pattern string in {fld} (V-21)")


# V-22..V-33 [v1.6]: evidence, relationships, liveness, tier-1, capabilities, site fields
EVD_FIELDS = ["evidence_id", "record_table", "record_id", "claim_type", "claim_detail",
              "source_class", "source_ref", "observed_date", "tier_effect",
              "created_by", "notes"]
REL_FIELDS = ["relationship_id", "from_org_id", "relationship_type", "to_org_id",
              "effective_from", "effective_to", "basis", "source_ref", "created_by",
              "notes"]
CAP_FIELDS = ["capability_id", "site_id", "org_id", "capability_type", "term",
              "provenance", "source_ref", "observed_date", "withdrawn_date",
              "created_by", "notes"]
CLAIM_TYPES = {"existence", "activity", "scope", "address", "parent", "liveness", "code"}
SOURCE_CLASSES = {"own_site", "government_filing", "registry", "directory", "press",
                  "platform_category", "harvest_roster"}
TIER_EFFECTS = {"supports_A", "supports_B", "supports_C", "contradicts"}
CLASS_CEIL = {"own_site": "supports_A", "government_filing": "supports_A",
              "registry": "supports_B", "directory": "supports_B", "press": "supports_B",
              "harvest_roster": "supports_B", "platform_category": "supports_C"}
EFF_RANK = {"supports_C": 1, "supports_B": 2, "supports_A": 3}
REL_TYPES = {"parent_of", "successor_of", "dba_of", "spun_off_from", "member_of", "merged_into"}
CAP_MATERIAL = {"thermoplastics", "thermosets", "elastomers_rubber",
                "thermoplastic_elastomers_tpe_tpu", "thermoplastic_olefin_tpo",
                "silicones", "fluoropolymers", "polyethylene_pe", "polypropylene_pp",
                "pvc", "pet_petg", "polystyrene_ps_hips", "polycarbonate_pc", "nylon_pa",
                "abs", "acetal_pom", "polyurethane_pu", "epoxy", "bioplastics_biobased",
                "recycled_content_pcr_pir", "custom_compounds",
                "inks_colorants_masterbatch", "coatings", "adhesives_sealants"}
CAP_PROCESS = {"injection_molding", "blow_molding", "extrusion", "thermoforming",
               "rotational_molding", "compression_molding", "rubber_molding",
               "rubber_mixing_compounding", "compounding", "color_masterbatch",
               "calendering", "composites_pultrusion", "reaction_injection_molding",
               "additive_manufacturing_polymer", "polymerization",
               "recycling_mechanical", "coating_formulation",
               "adhesive_sealant_formulation"}
CAP_PRODUCT = {"film_sheet", "sheet_plate", "pipe_profile", "tubing", "medical_tubing",
               "hose_belting", "foam_products", "fiber_filament", "bottles_containers",
               "bags_pouches", "molded_parts", "wire_cable", "gaskets_seals", "tires",
               "flooring"}
CAP_VOCAB = {"material": CAP_MATERIAL, "process": CAP_PROCESS, "product_form": CAP_PRODUCT}
LIVENESS_SIGNALS = {"operating_evidence", "closure_signature", "sos_confirmed_closed",
                    "sos_active"}
QUAL_ORDER = ["public_parent", "tri_reporter", "employees_250plus", "national_footprint"]
COUNTY_SOURCES = {"parcel", "physical_address", "geocoder_centroid", "directory"}
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
def _is_date(s):
    if not DATE_RE.match(s or ""):
        return False
    try:
        datetime.strptime(s, "%Y-%m-%d")
        return True
    except ValueError:
        return False
TABLE_IDS = {"organizations": {r["org_id"] for r in orgs},
             "sites": {r["site_id"] for r in sites},
             "ecosystem": {r["org_id"] for r in eco},
             "programs": {r["program_id"] for r in programs}}
TABLE_TIER = {}
for _t, _rows, _idc in (("organizations", orgs, "org_id"), ("sites", sites, "site_id"),
                        ("ecosystem", eco, "org_id"), ("programs", programs, "program_id")):
    for _r in _rows:
        TABLE_TIER[(_t, _r[_idc])] = (_r.get("verification_tier") or "").strip()
MUST_HAVE = {"organizations": {"existence", "address", "scope", "code"},
             "sites": {"existence", "address", "scope", "code", "parent"},
             "ecosystem": {"existence", "address", "scope"},
             "programs": {"existence", "scope"}}
STATUS_BY_ID = {r["org_id"]: (r.get("status") or "").strip() for r in orgs}
SITE_STATUS = {r["site_id"]: (r.get("operating_status") or "").strip() for r in sites}
def must_have_for(table, rid):
    mh = set(MUST_HAVE[table])
    if table == "programs":
        prow = next((r for r in programs if r["program_id"] == rid), None)
        if prow and (prow.get("cip_code") or "").strip():
            mh.add("code")
    if table == "organizations" and STATUS_BY_ID.get(rid) == "active":
        mh |= {"activity", "liveness"}
    if table == "sites" and SITE_STATUS.get(rid) == "active":
        mh |= {"activity", "liveness"}
    return mh
# V-22 evidence structural
if evidence or True:
    if evd_fields != EVD_FIELDS:
        errors.append("evidence.csv: header does not match the \u00a74.13 field set (V-22)")
    evd_ids = set()
    for i, r in enumerate(evidence, 2):
        eid = r["evidence_id"]
        if not re.fullmatch(r"EVD-\d{6}", eid or ""):
            errors.append(f"evidence.csv:{i} {eid} evidence_id does not match EVD-###### (V-22)")
        if eid in evd_ids:
            errors.append(f"evidence.csv:{i} {eid} duplicate evidence_id (V-22)")
        evd_ids.add(eid)
        rt = r["record_table"]
        if rt not in TABLE_IDS:
            errors.append(f"evidence.csv:{i} {eid} bad record_table (V-22)")
        elif r["record_id"] not in TABLE_IDS[rt]:
            errors.append(f"evidence.csv:{i} {eid} record_id does not resolve in {rt} (V-22)")
        if r["claim_type"] not in CLAIM_TYPES:
            errors.append(f"evidence.csv:{i} {eid} bad claim_type (V-22)")
        sc = r["source_class"]
        if sc not in SOURCE_CLASSES:
            errors.append(f"evidence.csv:{i} {eid} bad source_class (V-22)")
        te = r["tier_effect"]
        if te not in TIER_EFFECTS:
            errors.append(f"evidence.csv:{i} {eid} bad tier_effect (V-22)")
        elif te != "contradicts" and sc in CLASS_CEIL and EFF_RANK[te] > EFF_RANK[CLASS_CEIL[sc]]:
            errors.append(f"evidence.csv:{i} {eid} tier_effect {te} exceeds the {sc} ceiling {CLASS_CEIL[sc]} (V-22)")
        if sc in ("registry", "directory") and r["claim_type"] == "address" and te == "supports_B":
            errors.append(f"evidence.csv:{i} {eid} registry/directory address alone caps at supports_C (V-22)")
        if not (r["source_ref"] or "").strip() or not (r["claim_detail"] or "").strip():
            errors.append(f"evidence.csv:{i} {eid} source_ref and claim_detail must be non-empty (V-22)")
        if not _is_date(r["observed_date"]) or r["observed_date"] > "2026-12-31":
            errors.append(f"evidence.csv:{i} {eid} observed_date invalid or in the future (V-22)")
        if not (r["created_by"] or "").strip():
            errors.append(f"evidence.csv:{i} {eid} created_by empty (V-22)")
        # V-23 admissibility
        sref = (r["source_ref"] or "")
        if re.search(r"verdict|working/|packets/|integration-pass", sref, re.I):
            errors.append(f"evidence.csv:{i} {eid} source_ref points at our own verdict/packet/journal files \u2014 phantom shape (V-23)")
        if re.search(r"plastics news|rubber news|dun & bradstreet|\bD&B\b|data axle|zoominfo", sref, re.I):
            errors.append(f"evidence.csv:{i} {eid} source_ref names a licensed-class source \u2014 discovery provenance belongs in notes (V-23)")
        if sc == "registry" and "raw/" not in (sref + " " + (r["notes"] or "")) and not re.search(r"fetched \d{4}-\d{2}-\d{2}", r["notes"] or ""):
            errors.append(f"evidence.csv:{i} {eid} registry source_ref carries no raw/ extract pointer and no dated live-fetch marker (V-23)")
    # V-23(b) PMIR bar + V-25 tier restatement
    from collections import defaultdict as _dd
    by_record = _dd(list)
    for r in evidence:
        by_record[(r["record_table"], r["record_id"])].append(r)
    for (rt, rid), rows_ in by_record.items():
        scope_rows = [x for x in rows_ if x["claim_type"] == "scope"]
        if scope_rows and all(x["source_class"] == "platform_category" for x in scope_rows):
            errors.append(f"evidence: {rt} {rid} scope claim rests on platform_category rows alone \u2014 unevidenced (V-23, PMIR bar)")
        tier = TABLE_TIER.get((rt, rid), "")
        if tier in ("A", "B"):
            for claim in must_have_for(rt, rid):
                crows = [x for x in rows_ if x["claim_type"] == claim]
                sup = [x for x in crows if x["tier_effect"] != "contradicts"]
                con = [x for x in crows if x["tier_effect"] == "contradicts"]
                if con:
                    newest_sup = max((x["observed_date"] for x in sup), default="")
                    if any(x["observed_date"] >= newest_sup for x in con):
                        errors.append(f"evidence: {rt} {rid} must-have claim {claim} is contradicted at tier {tier} \u2014 cap is C until resolved (V-25)")
                        continue
                if sup:
                    strongest = max(EFF_RANK[x["tier_effect"]] for x in sup)
                    if strongest == 1 and tier in ("A", "B"):
                        errors.append(f"evidence: {rt} {rid} must-have claim {claim} supported only at C strength but tier is {tier} (V-25)")
                    elif strongest == 2 and tier == "A":
                        errors.append(f"evidence: {rt} {rid} must-have claim {claim} supported only at B strength but tier is A (V-25)")
# V-24 liveness (organizations)
for i, r in enumerate(orgs, 2):
    sig = (r.get("liveness_signal") or "").strip()
    if sig and sig not in LIVENESS_SIGNALS:
        errors.append(f"organizations.csv:{i} {r['org_id']} bad liveness_signal (V-24)")
    if (r.get("monitor_watch") or "").strip() not in ("true", "false"):
        errors.append(f"organizations.csv:{i} {r['org_id']} monitor_watch must be explicit true/false (V-24)")
    lad = (r.get("last_activity_evidence_date") or "").strip()
    if lad and not _is_date(lad):
        errors.append(f"organizations.csv:{i} {r['org_id']} last_activity_evidence_date not a date (V-24)")
    if lad and (r.get("last_verified") or "") and lad > r["last_verified"]:
        warnings.append(f"organizations.csv:{i} {r['org_id']} last_activity_evidence_date later than last_verified (V-24)")
    if (r.get("status") or "").strip() == "active" and sig == "closure_signature" and (r.get("monitor_watch") or "").strip() == "true":
        if "Settling fact:" not in (r.get("notes") or ""):
            errors.append(f"organizations.csv:{i} {r['org_id']} active + closure_signature + watched without a named Settling fact: in notes (V-24)")
    if sig == "sos_confirmed_closed" and (r.get("status") or "").strip() == "active":
        errors.append(f"organizations.csv:{i} {r['org_id']} sos_confirmed_closed standing next to status=active (V-24)")
# V-26..V-28 relationships
if rel_fields != REL_FIELDS:
    errors.append("relationships.csv: header does not match the \u00a74.14.1 field set (V-26)")
rel_ids = set(); rel_tuples = set()
for i, r in enumerate(relationships, 2):
    rid = r["relationship_id"]
    if not re.fullmatch(r"REL-\d{6}", rid or ""):
        errors.append(f"relationships.csv:{i} {rid} relationship_id does not match REL-###### (V-26)")
    if rid in rel_ids:
        errors.append(f"relationships.csv:{i} {rid} duplicate relationship_id (V-26)")
    rel_ids.add(rid)
    if r["relationship_type"] not in REL_TYPES:
        errors.append(f"relationships.csv:{i} {rid} bad relationship_type (V-26)")
    if r["from_org_id"] == r["to_org_id"]:
        errors.append(f"relationships.csv:{i} {rid} self-edge (V-26)")
    tup = (r["from_org_id"], r["relationship_type"], r["to_org_id"])
    if tup in rel_tuples:
        errors.append(f"relationships.csv:{i} {rid} duplicate edge tuple (V-26)")
    rel_tuples.add(tup)
    if not (r["basis"] or "").strip() or not (r["source_ref"] or "").strip() or not (r["created_by"] or "").strip():
        errors.append(f"relationships.csv:{i} {rid} basis/source_ref/created_by must be non-empty (V-26)")
    for ep in ("from_org_id", "to_org_id"):
        if r[ep] not in ALL_ORG_IDS:
            errors.append(f"relationships.csv:{i} {rid} {ep} {r[ep]} does not resolve \u2014 both endpoints must be held (V-27)")
    for dc in ("effective_from", "effective_to"):
        if r[dc] and not _is_date(r[dc]):
            errors.append(f"relationships.csv:{i} {rid} {dc} not an ISO date (V-28)")
    if r["effective_from"] and r["effective_to"] and r["effective_to"] < r["effective_from"]:
        errors.append(f"relationships.csv:{i} {rid} effective_to before effective_from (V-28)")
gen_parent = {(r["parent_org_id"], "parent_of", r["org_id"]) for r in orgs if (r.get("parent_org_id") or "").strip()}
gen_succ = {(r["org_id"], "successor_of", r["successor_org_id"]) for r in orgs if (r.get("successor_org_id") or "").strip() and r["status"] == "acquired"}
gen_merg = {(r["org_id"], "merged_into", r["successor_org_id"]) for r in orgs if (r.get("successor_org_id") or "").strip() and r["status"] == "merged"}
held_parent = {(r["from_org_id"], r["relationship_type"], r["to_org_id"]) for r in relationships if r["relationship_type"] == "parent_of"}
held_succ = {(r["from_org_id"], r["relationship_type"], r["to_org_id"]) for r in relationships if r["relationship_type"] == "successor_of"}
held_merg = {(r["from_org_id"], r["relationship_type"], r["to_org_id"]) for r in relationships if r["relationship_type"] == "merged_into"}
if held_parent != gen_parent:
    errors.append(f"relationships.csv: parent_of edges drift from parent_org_id columns (missing {sorted(gen_parent - held_parent)}, extra {sorted(held_parent - gen_parent)}) (V-27)")
if held_succ != gen_succ:
    errors.append(f"relationships.csv: successor_of edges drift from successor_org_id columns (V-27)")
if held_merg != gen_merg:
    errors.append(f"relationships.csv: merged_into edges drift from successor_org_id columns (V-27)")
# V-29 tier-1 qualifier (structure = error; basis/drift = warning)
LINKS_BY_ORG = {}
for _l in links:
    LINKS_BY_ORG.setdefault(_l["org_id"], []).append(_l)
SITES_BY_ORG = {}
for _s in sites:
    SITES_BY_ORG.setdefault(_s["org_id"], []).append(_s)
def derive_tier1_set(r):
    vals = set()
    if (r.get("stock_ticker") or "").strip():
        vals.add("public_parent")
    for _l in LINKS_BY_ORG.get(r["org_id"], []):
        if _l["registry"] in ("SEC_CIK", "SEC_CIK_PARENT_FILER"):
            vals.add("public_parent")
        if _l["registry"] == "TRI_TRIFID":
            vals.add("tri_reporter")
    if (r.get("employee_band_ohio") or "").strip() in ("250-499", "500-999", "1000-4999", "5000+"):
        vals.add("employees_250plus")
    _states = {s["state"] for s in SITES_BY_ORG.get(r["org_id"], []) if s["operating_status"] != "closed" and s["state"]}
    if len(_states) >= 3:
        vals.add("national_footprint")
    return vals
for i, r in enumerate(orgs, 2):
    raw_q = (r.get("tier1_qualifier") or "").strip()
    qvals = [x.strip() for x in raw_q.split(";") if x.strip()] if raw_q else []
    if any(x not in QUAL_ORDER for x in qvals):
        errors.append(f"organizations.csv:{i} {r['org_id']} tier1_qualifier value outside the enum (V-29)")
    if len(qvals) != len(set(qvals)):
        errors.append(f"organizations.csv:{i} {r['org_id']} tier1_qualifier duplicate value (V-29)")
    if qvals != [x for x in QUAL_ORDER if x in qvals]:
        errors.append(f"organizations.csv:{i} {r['org_id']} tier1_qualifier values out of the fixed order (V-29)")
    if qvals and not (r.get("tier1_qualifier_basis") or "").strip():
        warnings.append(f"organizations.csv:{i} {r['org_id']} tier1_qualifier non-empty with empty basis (V-29)")
    derived = derive_tier1_set(r)
    if set(qvals) != derived:
        warnings.append(f"organizations.csv:{i} {r['org_id']} tier1_qualifier drift: stored {sorted(qvals)} vs derived {sorted(derived)} (V-29)")
# V-30/V-31 capabilities
if cap_fields != CAP_FIELDS:
    errors.append("site_capabilities.csv: header does not match the \u00a74.15 field set (V-30)")
cap_ids = set(); cap_tuples = set()
SITE_ORG = {s["site_id"]: s["org_id"] for s in sites}
for i, r in enumerate(capabilities, 2):
    cid = r["capability_id"]
    if not re.fullmatch(r"CAP-\d{6}", cid or ""):
        errors.append(f"site_capabilities.csv:{i} {cid} capability_id does not match CAP-###### (V-30)")
    if cid in cap_ids:
        errors.append(f"site_capabilities.csv:{i} {cid} duplicate capability_id (V-30)")
    cap_ids.add(cid)
    ct = r["capability_type"]
    if ct not in CAP_VOCAB:
        errors.append(f"site_capabilities.csv:{i} {cid} bad capability_type (V-30)")
    elif r["term"] not in CAP_VOCAB[ct]:
        errors.append(f"site_capabilities.csv:{i} {cid} term {r['term']} not in the \u00a73.6 vocabulary for {ct} (V-30)")
    if r["provenance"] not in ("company_disclosed", "government_filing"):
        errors.append(f"site_capabilities.csv:{i} {cid} provenance outside the two-value enum \u2014 the PMIR rule is structural here (V-30)")
    if not (r["source_ref"] or "").strip():
        errors.append(f"site_capabilities.csv:{i} {cid} source_ref empty (V-30)")
    if not _is_date(r["observed_date"]) or r["observed_date"] > "2026-12-31":
        errors.append(f"site_capabilities.csv:{i} {cid} observed_date invalid or in the future (V-30)")
    if r["withdrawn_date"] and not _is_date(r["withdrawn_date"]):
        errors.append(f"site_capabilities.csv:{i} {cid} withdrawn_date not a date (V-30)")
    if r["site_id"] not in SITE_ORG:
        errors.append(f"site_capabilities.csv:{i} {cid} site_id does not resolve (V-31)")
    elif r["org_id"] != SITE_ORG[r["site_id"]]:
        errors.append(f"site_capabilities.csv:{i} {cid} org_id does not equal the site row's org_id (V-31)")
    tup = (r["site_id"], r["capability_type"], r["term"])
    if tup in cap_tuples:
        errors.append(f"site_capabilities.csv:{i} {cid} duplicate (site_id, capability_type, term) tuple (V-31)")
    cap_tuples.add(tup)
# V-32/V-33 site fields
GROUP_MEMBERS = {}
for i, s in enumerate(sites, 2):
    cs = (s.get("county_source") or "").strip()
    if cs:
        if cs not in COUNTY_SOURCES:
            errors.append(f"sites.csv:{i} {s['site_id']} bad county_source (V-32)")
        if not (s.get("county") or "").strip():
            errors.append(f"sites.csv:{i} {s['site_id']} county_source set with empty county (V-32)")
        if cs == "geocoder_centroid" and (s.get("geocode_precision") or "").strip() not in ("zip_centroid", "city_centroid"):
            errors.append(f"sites.csv:{i} {s['site_id']} county_source=geocoder_centroid without centroid geocode_precision (V-32)")
    gid = (s.get("site_group_id") or "").strip()
    if gid:
        if not re.fullmatch(r"GRP-\d{6}", gid):
            errors.append(f"sites.csv:{i} {s['site_id']} site_group_id does not match GRP-###### (V-32)")
        GROUP_MEMBERS.setdefault(gid, []).append(s)
for gid, members_ in GROUP_MEMBERS.items():
    if len(members_) < 2:
        errors.append(f"sites.csv: site group {gid} is a singleton \u2014 a group must hold >=2 sites at application close (V-33)")
    if len({(m["city"], m["state"]) for m in members_}) != 1:
        errors.append(f"sites.csv: site group {gid} members do not share city+state (V-33)")


# V-34..V-38 [pass 14] shard layout (SCHEMA Appendix C)
USPS_ALL = {"AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "FL", "GA", "HI", "ID",
            "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD", "MA", "MI", "MN", "MS",
            "MO", "MT", "NE", "NV", "NH", "NJ", "NM", "NY", "NC", "ND", "OH", "OK",
            "OR", "PA", "RI", "SC", "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV",
            "WI", "WY", "DC", "AS", "GU", "MP", "PR", "VI"}
def _org_shard_of(r):
    st = (r.get("hq_state") or "").strip().upper()
    c = (r.get("hq_country") or "").strip().upper()
    if st in USPS_ALL:
        return st
    if c not in ("", "US", "USA", "UNITED STATES"):
        return "INTL"
    return "US"
def _site_shard_of(r):
    st = (r.get("state") or "").strip().upper()
    return st if st in USPS_ALL else None
for _fname, (_flds, _rows) in sorted(ORG_SHARDS.items()):
    _tag = _fname[len("organizations_"):-len(".csv")]
    if _tag not in USPS_ALL and _tag not in ("INTL", "US"):
        errors.append(f"{_fname}: shard tag {_tag} is not a USPS code, INTL, or US (V-34)")
    if _flds != org_fields:
        errors.append(f"{_fname}: header diverges from the table's shard header set (V-34)")
    _ids = [r["org_id"] for r in _rows]
    if _ids != sorted(_ids):
        errors.append(f"{_fname}: org_ids not strictly ascending (V-36)")
    for r in _rows:
        if _org_shard_of(r) != _tag:
            errors.append(f"{_fname}: {r['org_id']} placement mismatch \u2014 computed shard {_org_shard_of(r)} != file tag {_tag}; correct the HQ fact and move the record in the same pass (Appendix C \u00a74), never auto-move (V-35)")
for _fname, (_flds, _rows) in sorted(SITE_SHARDS.items()):
    _tag = _fname[len("sites_"):-len(".csv")]
    if _tag in ("INTL", "US"):
        errors.append(f"{_fname}: sites carry no INTL or residual shard (Appendix C \u00a72.1) (V-35)")
    elif _tag not in USPS_ALL:
        errors.append(f"{_fname}: shard tag {_tag} is not a USPS code (V-34)")
    if _flds != site_fields:
        errors.append(f"{_fname}: header diverges from the table's shard header set (V-34)")
    _ids = [r["site_id"] for r in _rows]
    if _ids != sorted(_ids):
        errors.append(f"{_fname}: site_ids not strictly ascending (V-36)")
    for r in _rows:
        if _site_shard_of(r) is None:
            errors.append(f"{_fname}: {r['site_id']} is unplaceable (blank or non-USPS state) \u2014 held out for correction or an owner ruling (V-35)")
        elif _site_shard_of(r) != _tag:
            errors.append(f"{_fname}: {r['site_id']} placement mismatch \u2014 computed shard {_site_shard_of(r)} != file tag {_tag}; correct the state fact and move the record in the same pass (Appendix C \u00a74), never auto-move (V-35)")
for _mono in ("organizations.csv", "sites.csv"):
    if (DATA / _mono).exists():
        errors.append(f"data/{_mono}: monolith present \u2014 shards are canonical (V-37)")
for _f in sorted(DATA.glob("*_all.csv")):
    errors.append(f"data/{_f.name}: merged export committed to data/ \u2014 merged exports are build/ release artifacts only (V-37)")
if "organizations_US.csv" in ORG_SHARDS:
    warnings.append(f"organizations_US.csv holds {len(ORG_SHARDS['organizations_US.csv'][1])} residual rows \u2014 placement-review queue (V-38)")
print("organizations shards: " + ", ".join(f"{fn[len('organizations_'):-4]} {len(rw)}" for fn, (_, rw) in sorted(ORG_SHARDS.items())) + f" ({len(orgs)} total)")
print("sites shards: " + ", ".join(f"{fn[len('sites_'):-4]} {len(rw)}" for fn, (_, rw) in sorted(SITE_SHARDS.items())) + f" ({len(sites)} total)")

for w in warnings:
    print(f"WARN  {w}")
for e in errors:
    print(f"ERROR {e}")
print(f"\n{len(orgs)} organizations, {len(sites)} sites, {len(eco)} ecosystem rows, "
      f"{len(links)} registry links, {len(members)} member rows, {len(people)} people rows, "
      f"{len(programs)} program rows, {len(events)} event series, "
      f"{len(evidence)} evidence rows, {len(relationships)} relationship rows, "
      f"{len(capabilities)} capability rows, "
      f"{len(participation)} participation rows checked.")
if errors:
    print(f"FAILED with {len(errors)} error(s).")
    sys.exit(1)
print("OK — validation passed.")

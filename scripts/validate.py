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
              "FRS", "TRI_TRIFID", "FDA_FEI", "EIN_NONPROFIT"}
CREDENTIALS = {"phd", "ms", "bs", "aas_associate", "certificate", "registered_apprenticeship",
               "incumbent_worker_training", "noncredit_workforce"}
ENGAGEMENT = {"research_collaboration", "student_projects_capstone", "internships_coops",
              "testing_characterization_access", "lab_facility_access", "licensing_tech_transfer",
              "training_seats_open_enrollment", "customized_employer_training"}
OFFICE_MODES = {"licensing", "sponsored_research", "startup_formation", "materials_transfer", "facility_access"}
PROGRAM_TYPES = {"degree", "certificate", "apprenticeship", "center", "training"}
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

org_fields, orgs = load("organizations.csv")
site_fields, sites = load("sites.csv")
eco_fields, eco = load("ecosystem.csv")
link_fields, links = load("registry_links.csv", new_file=True)
member_fields, members = load("members.csv", new_file=True)
people_fields, people = load("people.csv", new_file=True)

# V-2: retired column must not ship
for fname, fields in (("organizations.csv", org_fields), ("ecosystem.csv", eco_fields)):
    if "pic_relationship_stage" in fields:
        errors.append(f"{fname}: pic_relationship_stage present — retired at schema v1.2; values are archived in staging; the column must not ship")

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
eco_by_id = {}
eco_member_true = set()
ECO_NEW = ("record_grain", "program_name", "parent_institution_org_id", "program_type",
           "credential_types", "program_url", "specialty_processes", "specialty_materials",
           "research_areas", "engagement_modes", "apprenticeship_registered",
           "employer_custom_training", "admissions_status", "facilities_note", "scale_band",
           "public_door_url", "office_name", "tto_url", "industry_partnership_modes",
           "technology_areas", "pic_member", "member_since", "membership_source_url")
for col in ECO_NEW:
    if col not in eco_fields:
        errors.append(f"ecosystem.csv: missing v1.2 column {col}")
for i, r in enumerate(eco, 2):
    oid = r["org_id"].strip()
    eco_by_id[oid] = r
    grain = (r.get("record_grain") or "").strip()
    if grain not in {"institution", "program", "office"}:
        errors.append(f"ecosystem.csv:{i} {oid} record_grain must be institution/program/office")
    check_membership("ecosystem.csv", i, r, oid)
    if (r.get("pic_member") or "").strip() == "true":
        eco_member_true.add(oid)
    if grain == "program":
        for col in ("program_name", "program_url", "public_door_url"):
            if not (r.get(col) or "").strip():
                errors.append(f"ecosystem.csv:{i} {oid} program record without {col}")
        parent = (r.get("parent_institution_org_id") or "").strip()
        if not parent or parent not in all_ids:
            errors.append(f"ecosystem.csv:{i} {oid} program parent_institution_org_id missing/dangling")
        ptype = (r.get("program_type") or "").strip()
        if ptype not in PROGRAM_TYPES:
            errors.append(f"ecosystem.csv:{i} {oid} program_type {ptype!r} not in enum")
        creds = vals(r.get("credential_types"))
        if ptype in {"degree", "certificate", "apprenticeship"} and not creds:
            errors.append(f"ecosystem.csv:{i} {oid} credential_types required for program_type {ptype}")
        for c in creds:
            if c not in CREDENTIALS:
                errors.append(f"ecosystem.csv:{i} {oid} credential_types value {c!r} not in enum")
        modes = vals(r.get("engagement_modes"))
        if not modes:
            errors.append(f"ecosystem.csv:{i} {oid} program record without engagement_modes")
        for m in modes:
            if m not in ENGAGEMENT:
                errors.append(f"ecosystem.csv:{i} {oid} engagement_modes value {m!r} not in enum")
        for a in vals(r.get("research_areas")):
            if a not in RESEARCH_VOCAB:
                errors.append(f"ecosystem.csv:{i} {oid} research_areas value {a!r} not in §3.1/§3.2/§3.5 vocabulary")
        adm = (r.get("admissions_status") or "").strip()
        if adm and adm not in {"admitting", "not_admitting", "unknown"}:
            errors.append(f"ecosystem.csv:{i} {oid} admissions_status {adm!r} not in enum")
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
    if prog and (prog not in eco_by_id or (eco_by_id[prog].get("record_grain") or "").strip() != "program"):
        errors.append(f"people.csv:{i} {pid} program_org_id does not resolve to a program-grain record")
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

for w in warnings:
    print(f"WARN  {w}")
for e in errors:
    print(f"ERROR {e}")
print(f"\n{len(orgs)} organizations, {len(sites)} sites, {len(eco)} ecosystem rows, "
      f"{len(links)} registry links, {len(members)} member rows, {len(people)} people rows checked.")
if errors:
    print(f"FAILED with {len(errors)} error(s).")
    sys.exit(1)
print("OK — validation passed.")

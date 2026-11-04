#!/usr/bin/env python3
"""Export the validator's controlled vocabularies as machine-readable JSON.

The validator (scripts/validate.py) is the enforced form of docs/SCHEMA.md's
controlled vocabularies. This script reads its module-level literal sets,
lists, and dicts with `ast` (nothing is executed) and writes them to
docs/schema/vocab.json, so an agent can load one small file instead of
reading a 200 KB schema to find which values are allowed.

    python3 scripts/export_vocab.py            # rewrite docs/schema/vocab.json
    python3 scripts/export_vocab.py --check    # exit 1 if the file is stale

vocab.json is DERIVED. Never edit it by hand. A vocabulary change is a dated
SCHEMA revision (AGENTS.md §1) plus the matching validate.py change, then
this script is re-run. scripts/test_export_vocab.py checks they agree.
"""
import ast
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
VALIDATE = ROOT / "scripts" / "validate.py"
OUT = ROOT / "docs" / "schema" / "vocab.json"

# Constant name -> (table.column it governs, SCHEMA/AGENTS section). Only
# names listed here are exported; everything else in validate.py is internal.
EXPORT = {
    "SITE_TYPES": ("sites.site_type", "SCHEMA §4.5"),
    "EMPLOYEE_BANDS": ("organizations.employee_band_ohio; sites.employee_band_site", "SCHEMA §4.4"),
    "NAICS_SOURCE_TYPES": ("*.naics_primary_source_type", "AGENTS.md §4; SCHEMA §2.1"),
    "NAICS_CONFIDENCE": ("*.naics_confidence", "SCHEMA §2.1"),
    "MARKETS": ("markets_served (multi, ';') on organizations/sites", "SCHEMA §3.3"),
    "OWNERSHIP": ("organizations.ownership_type", "SCHEMA §4.4 (v1.4)"),
    "CERTS": ("organizations.certifications (multi, ';')", "SCHEMA §3.4"),
    "GEO_PRECISION": ("sites.geocode_precision", "SCHEMA §4.5"),
    "COUNTY_SOURCES": ("sites.county_source", "SCHEMA §4.5 (v1.6)"),
    "REGISTRIES": ("registry_links.registry", "SCHEMA §4.8"),
    "PROCESSES": ("processes (multi, ';') on organizations/sites", "SCHEMA §3.1"),
    "MATERIALS": ("materials (multi, ';') on organizations/sites", "SCHEMA §3.2"),
    "RESEARCH_SUPPLEMENT": ("people/programs research areas (with PROCESSES|MATERIALS)", "SCHEMA §3.5"),
    "CREDENTIALS": ("programs.credential_types", "SCHEMA §4.11"),
    "ENGAGEMENT": ("programs.engagement_modes", "SCHEMA §4.11"),
    "OFFICE_MODES": ("ecosystem.industry_partnership_modes (office grain)", "SCHEMA §4.6"),
    "PROGRAM_TYPES": ("programs.program_type", "SCHEMA §4.11"),
    "LEVELS": ("programs.level", "SCHEMA §4.11"),
    "CIP_SOURCE_TYPES": ("programs.cip_source_type", "SCHEMA §4.11"),
    "ROLES": ("people.role", "SCHEMA §4.9 (v1.7.4)"),
    "PERSON_ID_TYPES": ("people_identifiers.identifier_type", "SCHEMA §4.21 (v1.10)"),
    "PART_ROLES": ("event_participation.role", "SCHEMA §4.12.2"),
    "SUBJECT_VOCAB": ("events subject tags", "SCHEMA §4.12.1"),
    "EVENT_FORMATS": ("events.format", "SCHEMA §4.12.1"),
    "CADENCES": ("events.cadence", "SCHEMA §4.12.1"),
    "HOME_REGIONS": ("events.home_region", "SCHEMA §4.12.1"),
    "EVENT_STATUSES": ("events.status", "SCHEMA §4.12.1"),
    "EVIDENCE_TABLES": ("evidence.record_table", "SCHEMA §4.13"),
    "CLAIM_TYPES": ("evidence.claim_type", "SCHEMA §4.13"),
    "SOURCE_CLASSES": ("evidence.source_class", "SCHEMA §4.13"),
    "TIER_EFFECTS": ("evidence.tier_effect", "SCHEMA §4.13"),
    "CLASS_CEIL": ("evidence: highest tier_effect per source_class", "SCHEMA §4.13"),
    "REL_TYPES": ("relationships.relationship_type", "SCHEMA §4.14"),
    "CAP_MATERIAL": ("site_capabilities.term where capability_type=material", "SCHEMA §3.6"),
    "CAP_PROCESS": ("site_capabilities.term where capability_type=process", "SCHEMA §3.6"),
    "CAP_PRODUCT": ("site_capabilities.term where capability_type=product_form", "SCHEMA §3.6"),
    "EQUIPMENT_CLASSES": ("equipment.equipment_class", "SCHEMA §3.7 (v1.9)"),
    "ACCESS_MODES": ("equipment.access_mode", "SCHEMA §4.19 (v1.9)"),
    "PEOPLE_ENGAGEMENT": ("people_engagement.mode", "SCHEMA §4.20 (v1.9)"),
    "LIVENESS_SIGNALS": ("organizations.liveness_signal", "SCHEMA §4.4 (v1.6)"),
    "QUAL_ORDER": ("organizations.tier1_qualifier (derived; order matters)", "SCHEMA §4.4 (v1.6)"),
    "CODE_SYSTEMS": ("ref_codes.code_system; code_assignments.code_system", "SCHEMA §4.16"),
    "CODE_SOURCE_TYPES": ("code_assignments.source_type", "SCHEMA §4.18"),
}

# Fixed sets written inline in validate.py rather than as named constants.
INLINE = {
    "RING": (["1", "2", "3", "4", "5"], "*.ring_primary", "SCHEMA §1"),
    "VERIFICATION_TIER": (["A", "B", "C", "U"], "*.verification_tier", "SCHEMA §4.1"),
    "ORG_STATUS": (["active", "active_idled_partial", "idled", "closed", "acquired", "merged",
                    "relocated_in_scope", "relocated_out_of_scope", "pre_revenue", "unknown"],
                   "organizations.status; sites.operating_status", "SCHEMA §4.2"),
    "ENTITY_TYPE": (["corporation_public", "corporation_private", "llc", "partnership",
                     "sole_proprietor", "nonprofit", "government", "academic", "cooperative",
                     "unknown"], "organizations.entity_type", "SCHEMA §4.4"),
}


def literal_constants(path=VALIDATE):
    """Return {NAME: python value} for module-level literal assignments."""
    tree = ast.parse(path.read_text(encoding="utf-8"))
    found = {}
    for node in tree.body:
        if isinstance(node, ast.Assign) and len(node.targets) == 1 \
                and isinstance(node.targets[0], ast.Name):
            name = node.targets[0].id
            try:
                found[name] = ast.literal_eval(node.value)
            except ValueError:
                continue  # not a pure literal (e.g. a union); skip
    return found


def build():
    consts = literal_constants()
    vocab = {}
    for name, (governs, section) in EXPORT.items():
        if name not in consts:
            raise SystemExit(f"export_vocab: {name} not found as a literal in validate.py")
        v = consts[name]
        if isinstance(v, (set, frozenset)):
            values = sorted(v)
        elif isinstance(v, dict):
            values = {k: v[k] for k in sorted(v)}
        else:
            values = list(v)
        vocab[name] = {"governs": governs, "section": section, "values": values}
    for name, (values, governs, section) in INLINE.items():
        vocab[name] = {"governs": governs, "section": section, "values": values,
                       "note": "written inline in validate.py / SCHEMA, mirrored here"}
    return {
        "_doc": ("Controlled vocabularies enforced by scripts/validate.py, exported by "
                 "scripts/export_vocab.py. DERIVED: never hand-edit. Multi-value fields use ';'. "
                 "A value not listed here goes in the record's notes field and is flagged, "
                 "never improvised (AGENTS.md §1)."),
        "vocabularies": dict(sorted(vocab.items())),
    }


def main():
    text = json.dumps(build(), indent=1, ensure_ascii=False) + "\n"
    if "--check" in sys.argv:
        current = OUT.read_text(encoding="utf-8") if OUT.exists() else ""
        if current != text:
            print("docs/schema/vocab.json is stale: run python3 scripts/export_vocab.py")
            sys.exit(1)
        print("docs/schema/vocab.json is current")
        return
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(text, encoding="utf-8")
    print(f"wrote {OUT.relative_to(ROOT)} ({len(build()['vocabularies'])} vocabularies)")


if __name__ == "__main__":
    main()

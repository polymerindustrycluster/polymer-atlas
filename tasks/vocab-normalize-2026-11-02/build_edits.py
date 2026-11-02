#!/usr/bin/env python3
"""Normalize off-vocabulary capability values to SCHEMA §3.1–§3.3 terms, mechanical subset only.

    python3 tasks/vocab-normalize-2026-11-02/build_edits.py --data-dir <pre-pass data dir>
        -> edits.csv (for scripts/apply_p1_crm_scrub.py --packet-dir), mapping_used.csv, ruling_candidates.csv

A token is rewritten only when
  (a) SPELLING: lowercase + spaces/hyphens/slashes -> "_" turns it into a vocabulary term
      ("injection molding" -> injection_molding); or
  (b) EQUIV: it is listed below. Every EQUIV entry is the same thing as its target(s):
      the full name or standard abbreviation of the term, or a member of the
      vocabulary's own family bucket (HDPE -> polyethylene_pe). Nothing generic or
      ambiguous ("extrusion", "compounding", "plastic", "fiberglass", "distribution")
      is mapped; those go to ruling_candidates.csv for the owner.
Tokens that do not map are kept verbatim; existing in-vocabulary tokens are untouched.
No value is added that the record did not already state, and none is removed.
"""
import argparse, csv, hashlib, json
from collections import Counter, defaultdict
from pathlib import Path

csv.field_size_limit(10 ** 9)
ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
FIELDS = {"processes": "PROCESSES", "materials": "MATERIALS", "markets_served": "MARKETS"}

EQUIV = {
    "materials": {
        **{k: ["polyethylene_pe"] for k in ("polyethylene", "pe", "hdpe", "ldpe", "lldpe", "uhmwpe", "uhmw_pe", "mdpe",
                                            "high_density_polyethylene", "low_density_polyethylene", "uhmw")},
        **{k: ["polypropylene_pp"] for k in ("polypropylene", "pp")},
        **{k: ["pvc"] for k in ("polyvinyl_chloride", "pvc_compounds", "rigid_pvc", "flexible_pvc", "cpvc")},
        **{k: ["pet_petg"] for k in ("pet", "petg", "polyethylene_terephthalate", "rpet")},
        **{k: ["nylon_pa"] for k in ("nylon", "polyamide", "pa", "nylon_6", "nylon_66", "nylon_6_6", "polyamides")},
        **{k: ["polycarbonate_pc"] for k in ("polycarbonate", "pc")},
        **{k: ["polystyrene_ps_hips"] for k in ("polystyrene", "ps", "hips")},
        **{k: ["acrylic_pmma"] for k in ("pmma", "plexiglass", "plexiglas")},
        **{k: ["acetal_pom"] for k in ("acetal", "pom", "delrin")},
        **{k: ["polyurethane_pu"] for k in ("polyurethane", "pu", "urethane", "polyurethanes", "urethanes")},
        **{k: ["silicones"] for k in ("silicone", "silicone_rubber", "liquid_silicone_rubber", "lsr")},
        **{k: ["epoxy"] for k in ("epoxies", "epoxy_resin", "epoxy_resins")},
        **{k: ["phenolic"] for k in ("phenolics", "phenolic_resin", "phenolic_resins")},
        **{k: ["natural_rubber_nr"] for k in ("natural_rubber", "nr")},
        **{k: ["neoprene_cr"] for k in ("neoprene", "polychloroprene")},
        **{k: ["nitrile_nbr"] for k in ("nitrile", "nbr", "nitrile_rubber", "buna_n")},
        **{k: ["viton_fkm"] for k in ("viton", "fkm", "fluoroelastomer", "fluoroelastomers")},
        **{k: ["sbr"] for k in ("styrene_butadiene_rubber",)},
        **{k: ["peek_high_performance"] for k in ("peek",)},
        **{k: ["fluoropolymers"] for k in ("fluoropolymer", "ptfe", "pvdf", "fep", "pfa")},
        **{k: ["thermoplastic_elastomers_tpe_tpu"] for k in ("tpe", "tpu", "tpv", "thermoplastic_elastomer",
                                                               "thermoplastic_elastomers", "thermoplastic_polyurethane")},
        **{k: ["thermoplastics"] for k in ("thermoplastic", "thermoplastic_resins")},
        **{k: ["thermosets"] for k in ("thermoset", "thermosetting_plastics", "thermoset_resins")},
        **{k: ["elastomers_rubber"] for k in ("elastomers", "elastomer", "rubber", "synthetic_rubber", "rubber_compounds",
                                              "rubber_compound")},
        **{k: ["composites_frp"] for k in ("frp", "fiberglass_reinforced_plastic", "fiberglass_reinforced_plastic_(frp)",
                                           "fiber_reinforced_plastic", "fibre_reinforced_plastic", "glass_reinforced_plastic")},
        **{k: ["composites_carbon"] for k in ("carbon_fiber", "carbon_fibre", "carbon_fiber_composites")},
        **{k: ["polyester_vinyl_ester_resins"] for k in ("polyester_resin", "polyester_resins", "unsaturated_polyester_resins",
                                                         "unsaturated_polyester_resin", "vinyl_ester_resins", "vinyl_ester",
                                                         "vinyl_ester_resin")},
        **{k: ["adhesives_sealants"] for k in ("adhesives", "sealants", "adhesives_and_sealants", "adhesive", "sealant")},
        **{k: ["melamine_urea_formaldehyde"] for k in ("melamine", "urea_formaldehyde", "melamine_formaldehyde")},
        "polyurethane_foam": ["polyurethane_pu", "foams_polymeric"],
        "flexible_polyurethane_foam": ["polyurethane_pu", "foams_polymeric"],
        "eps": ["polystyrene_ps_hips", "foams_polymeric"],
        "expanded_polystyrene": ["polystyrene_ps_hips", "foams_polymeric"],
        "polystyrene_foam": ["polystyrene_ps_hips", "foams_polymeric"],
        "polyethylene_foam": ["polyethylene_pe", "foams_polymeric"],
    },
    "processes": {
        "thermoforming": ["thermoforming_unspecified"],
        "pultrusion": ["composites_pultrusion"],
        "filament_winding": ["composites_filament_winding"],
        **{k: ["extrusion_film_blown"] for k in ("blown_film_extrusion", "blown_film")},
        **{k: ["extrusion_film_cast"] for k in ("cast_film_extrusion", "cast_film")},
        **{k: ["extrusion_sheet"] for k in ("sheet_extrusion",)},
        **{k: ["extrusion_profile"] for k in ("profile_extrusion",)},
        **{k: ["extrusion_pipe_tube"] for k in ("pipe_extrusion", "tube_extrusion", "tubing_extrusion")},
        **{k: ["rubber_mixing_compounding"] for k in ("rubber_compounding", "rubber_mixing")},
        **{k: ["mold_tool_making"] for k in ("mold_making", "moldmaking", "mold_building")},
        **{k: ["laminating"] for k in ("lamination",)},
        **{k: ["insert_overmolding"] for k in ("insert_molding", "overmolding")},
        **{k: ["plastics_fabrication_welding"] for k in ("plastic_welding", "plastics_welding", "plastic_fabrication",
                                                         "plastics_fabrication")},
        **{k: ["plastics_machining_cnc"] for k in ("plastic_machining", "plastics_machining", "cnc_plastic_machining")},
        **{k: ["composites_hand_layup"] for k in ("hand_layup", "hand_lay_up", "open_molding")},
        **{k: ["composites_rtm_infusion"] for k in ("resin_transfer_molding", "rtm", "vacuum_infusion", "resin_infusion")},
        **{k: ["composites_compression_smc_bmc"] for k in ("smc", "bmc", "sheet_molding_compound", "bulk_molding_compound")},
        **{k: ["two_shot_molding"] for k in ("2_shot_molding", "multi_shot_molding")},
        **{k: ["injection_molding_lsr_silicone"] for k in ("lsr_molding", "liquid_silicone_rubber_molding", "liquid_silicone_rubber_injection_molding")},
        **{k: ["rubber_extrusion"] for k in ("extruded_rubber",)},
        **{k: ["tire_retreading"] for k in ("retreading",)},
    },
    "markets_served": {
        "automotive": ["automotive_unspecified"],
        "medical_devices": ["medical_device"],
        "cosmetics": ["cosmetics_personal_care"],
    },
}


def norm(s):
    return "_".join(s.lower().replace("-", " ").replace("/", " ").split())


def read(p):
    with open(p, newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data-dir", required=True)
    a = ap.parse_args()
    data = Path(a.data_dir)
    voc = json.loads((ROOT / "docs" / "schema" / "vocab.json").read_text(encoding="utf-8"))["vocabularies"]
    V = {f: set(voc[k]["values"]) for f, k in FIELDS.items()}
    for f, m in EQUIV.items():
        for k, targets in m.items():
            assert all(t in V[f] for t in targets), (f, k, targets)
    sha = lambda s: hashlib.sha256(s.encode("utf-8")).hexdigest()
    edits, used, left = [], Counter(), Counter()
    for p in sorted(data.glob("sites_*.csv")) + sorted(data.glob("organizations_*.csv")):
        key = "site_id" if p.name.startswith("sites_") else "org_id"
        for r in read(p):
            for f in FIELDS:
                toks = [t.strip() for t in (r.get(f) or "").split(";") if t.strip()]
                if not toks or all(t in V[f] for t in toks):
                    continue
                out, changed = [], False
                for t in toks:
                    if t in V[f]:
                        out.append(t); continue
                    n = norm(t)
                    tgt = [n] if n in V[f] else EQUIV[f].get(n)
                    if tgt:
                        out.extend(tgt); changed = True; used[(f, t, ";".join(tgt), "SPELLING" if n in V[f] else "EQUIV")] += 1
                    else:
                        out.append(t); left[(f, t)] += 1
                if not changed:
                    continue
                seen, final = set(), []
                for t in out:
                    if t not in seen:
                        seen.add(t); final.append(t)
                new = ";".join(final)
                if new != r[f]:
                    edits.append({"file": p.name, "row_id": r[key], "column": f, "old_sha256": sha(r[f]), "new_value": new,
                                  "edit_class": "VOCAB_NORMALIZE", "rationale": f"{r[f][:120]} -> {new[:120]}"})
    with open(OUT / "edits.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=["file", "row_id", "column", "old_sha256", "new_value", "edit_class", "rationale"],
                           lineterminator="\n"); w.writeheader(); w.writerows(edits)
    with open(OUT / "mapping_used.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh, lineterminator="\n"); w.writerow(["field", "from_value", "to_terms", "class", "tokens"])
        for (f, t, tgt, cls), n in sorted(used.items(), key=lambda x: -x[1]): w.writerow([f, t, tgt, cls, n])
    with open(OUT / "ruling_candidates.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh, lineterminator="\n"); w.writerow(["field", "value", "tokens"])
        for (f, t), n in sorted(left.items(), key=lambda x: -x[1]):
            if n >= 5: w.writerow([f, t, n])
    by = Counter()
    for (f, t, tgt, cls), n in used.items(): by[(f, cls)] += n
    print(f"edits {len(edits)} cells over {len({(e['file'], e['row_id']) for e in edits})} records; tokens mapped {dict(by)}; "
          f"off-vocab tokens left {sum(left.values())}")


if __name__ == "__main__":
    main()

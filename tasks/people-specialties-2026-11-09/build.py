#!/usr/bin/env python3
"""Fill blank research_specialties on people records from packet.csv (SCHEMA §4.9; §3-first vocabulary rule, §3.5).

Applies only rows whose outcome starts with "raw_ok": the lane's quote was found word for word on the raw page, the
terms are §3.1 / §3.2 / §3.5 vocabulary, and the page is on the institution's own domain. For each applied person:
  - research_specialties = the terms (the field must be blank: a filled field is never overwritten);
  - the quote's page joins `sources` when it is not already cited;
  - last_verified = the pass date (the page was read live and still names the person);
  - one evidence_people scope row carrying the quote ("Raw words in order: ...").
Idempotent: a person whose specialties are already filled is skipped.

    python3 tasks/people-specialties-2026-11-09/build.py [--apply]
"""
import csv, io, re, sys
from pathlib import Path

# Term gate (after the codex refute of the first draft): a term survives only if its quote carries the term's own
# trigger words. A property is not a specialty ("biocompatible" is not biomedical research), and an inferred class is
# not a stated one ("cross-links" is not "thermosets"). A row with no surviving term is not applied.
# shortcut: keyword triggers are a floor on support, not proof of it; the two-family refute samples what passes.
TRIGGER = {
    "biomedical_polymers": r"biomedic|medical|medicine|drug|tissue|implant|wound|therapeut|clinical|regenerative|"
                           r"biomaterial|surgical|dental|orthop|delivery|vaccine|diagnos|cell",
    "polymer_physics": r"physics|dynamics|thermodynamic|statistical mechanic|structure.{0,20}propert|phase behav|"
                       r"self.assembl|morpholog|conformation|glass transition|chain|entangle|crystalliz|soft matter",
    "polymerization": r"polymeriz", "polymer_synthesis": r"synthes|polymeriz",
    "composites_unspecified": r"composite", "composites_mechanics": r"composite", "composites_carbon": r"carbon.{0,30}composite|composite.{0,30}carbon|carbon fib",
    "composites_frp": r"fib(er|re).{0,15}reinforc|frp",
    "additive_manufacturing_polymer": r"additive manufactur|3d.print|3-d print|printing|printed",
    "additive_manufacturing_science": r"additive manufactur|3d.print|3-d print|printing|printed",
    "characterization_methods": r"characteriz|spectroscop|microscop|scattering|nmr|x.ray|rheometr|calorimetr|imaging|metrolog",
    "membranes_separations": r"membrane|separation|filtrat|barrier|desalinat|purificat",
    "bioplastics_biobased": r"bio.?based|bioplastic|biopolymer|biomass|renewable|plant.based|natural polymer|cellulos|lignin|chitosan|silk|protein",
    "rheology": r"rheolog|viscoelast|viscosit|flow behav", "degradation_biodegradation": r"degradation|\bdegrade|aging|weathering|durabilit|lifetime",
    "coatings": r"coating", "coating_applying": r"coating",
    "recycling_circularity": r"recycl|circular|upcycl|end.of.life|reuse", "recycling_unspecified": r"recycl|upcycl",
    "recycling_chemical_solvolysis": r"solvoly|depolymeriz|chemical recycl",
    "sustainable_feedstocks": r"bio.?based|biomass|renewable|feedstock|waste|co2|carbon dioxide|sustainab",
    "thermoplastics": r"thermoplastic", "thermosets": r"thermoset", "elastomers_rubber": r"elastomer|rubber",
    "elastomer_science": r"elastomer|rubber|vulcaniz", "natural_rubber_nr": r"natural rubber",
    "adhesives_sealants": r"adhesi|sealant|glue", "pet_petg": r"\bpet\b|polyethylene terephthalate|polyester",
    "polyethylene_pe": r"polyethylene|\bpe\b|polyolefin", "polypropylene_pp": r"polypropylene|\bpp\b|polyolefin",
    "polystyrene_ps_hips": r"polystyrene|\bps\b", "polyurethane_pu": r"polyurethane|\bpu\b",
    "nylon_pa": r"nylon|polyamide", "pla": r"\bpla\b|polylactic|poly\(lactic", "pha": r"\bpha\b|polyhydroxyalkano",
    "epoxy": r"epox", "pvc": r"\bpvc\b|polyvinyl chloride|poly\(vinyl chloride", "fluoropolymers": r"fluoropolymer|ptfe|pvdf|fluorinated polymer",
    "foams_polymeric": r"foam", "polymer_additives": r"additive|plasticiz|stabiliz|flame retard|filler",
    "extrusion_unspecified": r"extru",
}


def gate(terms, quote):
    q = quote.lower()
    return [t for t in terms.split(";") if t and re.search(TRIGGER.get(t, r"(?!)"), q)]

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
DATE = "2026-11-09"
FIRST_EVD = 333028  # above main and every open PR on 2026-11-09
BY = "claude-code people-specialties-2026-11-09"


def read(path):
    raw = path.read_bytes()
    eol = "\r\n" if b"\r\n" in raw[:4096] else "\n"
    rdr = csv.DictReader(io.StringIO(raw.decode("utf-8"), newline=""))
    return rdr.fieldnames, list(rdr), eol


def write(path, head, rows, eol):
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=head, lineterminator=eol)
    w.writeheader(); w.writerows(rows)
    path.write_bytes(buf.getvalue().encode("utf-8"))


def main():
    apply = "--apply" in sys.argv
    packet = [r for r in csv.DictReader(open(HERE / "packet.csv", encoding="utf-8")) if r["outcome"].startswith("raw_ok")]
    phead, people, peol = read(ROOT / "data/people.csv")
    ehead, evidence, eeol = read(ROOT / "data/evidence_people.csv")
    by_id = {p["person_id"]: p for p in people}
    assert len(by_id) == len(people)
    held_evd = {e["evidence_id"] for e in evidence}
    nxt, applied, skipped, new_ev, gated, dropped_terms = FIRST_EVD, 0, 0, [], [], 0
    for r in packet:
        p = by_id[r["person_id"]]
        if p["research_specialties"].strip():
            skipped += 1; continue
        kept = gate(r["terms"], r["quote"])
        dropped_terms += len(r["terms"].split(";")) - len(kept)
        if not kept:
            gated.append(r["person_id"]); continue
        r["terms"] = ";".join(kept)
        p["research_specialties"] = r["terms"]
        src = [s for s in p["sources"].split(";") if s]
        if r["source_url"] not in src:
            p["sources"] = ";".join(src + [r["source_url"]])
        p["last_verified"] = DATE
        eid = f"EVD-{nxt:06d}"; nxt += 1
        assert eid not in held_evd
        new_ev.append({"evidence_id": eid, "record_table": "people", "record_id": p["person_id"], "claim_type": "scope",
                       "claim_detail": "research_specialties " + r["terms"], "source_class": "own_site",
                       "source_ref": r["source_url"], "observed_date": DATE, "tier_effect": "supports_A",
                       "created_by": BY, "notes": "Raw words in order: " + " ".join(r["quote"].split())})
        applied += 1
    print(f"packet rows to apply {len(packet)}; applied {applied}; already filled {skipped}; evidence rows {len(new_ev)}; "
          f"terms dropped by the gate {dropped_terms}; rows with no surviving term {len(gated)}")
    with open(HERE / "gated_out.csv", "w", newline="", encoding="utf-8") as fh:
        fh.write("person_id\n" + "".join(g + "\n" for g in gated))
    if apply and applied:
        write(ROOT / "data/people.csv", phead, people, peol)
        write(ROOT / "data/evidence_people.csv", ehead, evidence + new_ev, eeol)
        print("written")


if __name__ == "__main__":
    main()

"""Muse Parts 3-4 (band-B faculty) -> candidate rows in the band-B lane format, for the raw check and the two-family review.

Admission standard is the band-B LANE_BRIEF plus build_people.py, NOT Muse's looser prompt: Gate B must be the person's
own profile or lab page (a department, center or program page fails), both gate URLs on the institution's domain, quotes
<= 25 words, current research only, no CV URLs. Muse rows that pass only under Muse's wording are owner questions
(owner_rows), raw-checked for the report but never admitted. Muse FAIL / NOT FOUND rows stay held.
Each candidate starts from the lane's own row (out/laneNN.csv or verified.csv) and replaces only the gate Muse settled.
    python -I make_candidates.py"""
import csv, glob
from pathlib import Path

HERE = Path(__file__).resolve().parent
BB = HERE.parent / "bandb-2026-11-19"
COLS = ["lead_id", "full_name", "institution_org_id", "role", "role_as_published", "public_profile_url", "gate_a_url",
        "gate_a_quote", "gate_b_url", "gate_b_quote", "verdict", "verdict_note", "observed_date"]
lane = {}
for f in sorted(glob.glob(str(BB / "out" / "lane*.csv"))) + [str(BB / "verified.csv")]:
    lane.update({r["lead_id"]: r for r in csv.DictReader(open(f, encoding="utf-8"))})
POL = ("https://engineering.purdue.edu/ChE/research/catalysis-energy?action=view_person&block_id=people_list_2026-07-23-16-28-30-863"
       "&group_id=342795&resource_id=105208&profile_id=profile_setting_000")
SCH = ("https://engineering.purdue.edu/ChE/research/bioeng-biotech?action=view_person&block_id=people_list_2026-07-23-15-21-43-297"
       "&group_id=342790&resource_id=293892&profile_id=profile_setting_000")
# lead -> (fields replaced on the lane row, why); quotes are contiguous spans of the page, <= 25 words
CAND = {
    "BB-0212": ({}, "Lane row unchanged. Held only for the lead's 'Former' label; Muse re-read the profile: Associate Research "
                    "Professor, 2025-present."),
    "BB-0308": ({"gate_b_url": "https://calce.umd.edu/our-team-ii",
                 "gate_b_quote": "Dr. Han’s research interests include: Characterization of advanced polymers;"},
                "Gate B replaced: the lane quoted a project title; the CALCE team page (his own bio entry on the University "
                "of Maryland center he works in) lists polymer characterization first among his research interests."),
    "BB-0380": ({}, "Lane row unchanged; the lane asked a reviewer to rule. Muse adds the profile's Research Interests item "
                    "'Dyeing of Polyolefins (Polypropylene, PE)'. Primary research is color science."),
    "BB-0241": ({"full_name": "Vilas Pol", "role": "professor", "role_as_published": "Professor of Chemical Engineering",
                 "public_profile_url": POL, "gate_a_url": POL, "gate_a_quote": "Vilas Pol Professor of Chemical Engineering",
                 "gate_b_url": POL,
                 "gate_b_quote": "reducing interfacial impedance in all-solid-state batteries through hybrid polymer/garnet "
                                 "electrolyte and interface engineering for improved room-temperature performance"},
                "Both gates new: the ChE profile now renders. Polymer appears inside his battery research (polymer/garnet "
                "electrolytes; also 'flexible polymer-based devices'); his field is electrochemical energy storage."),
    "BB-0233": ({"public_profile_url": SCH, "gate_b_url": SCH, "gate_b_quote": "Polymers and Materials"},
                "Gate B new: her ChE profile's Research Interests list 'Polymers and Materials' (with gels and fluid "
                "mechanics). Gate A from the lane."),
    # the lane's Gate A page (engineering.wisc.edu/directory/profile/michael-arnold) was unfetchable on every route at
    # the 2026-11-19 raw check, so Gate A moves to the group's own About page, which Muse quoted
    "BB-0617": ({"role_as_published": "Professor", "public_profile_url": "https://arnold.engr.wisc.edu/about.html",
                 "gate_a_url": "https://arnold.engr.wisc.edu/about.html",
                 "gate_a_quote": "directed by Professor Michael Arnold of the Department of Materials Science and Engineering at UW-Madison",
                 "gate_b_url": "https://arnold.engr.wisc.edu/research.html",
                 "gate_b_quote": "Semiconducting molecules and polymers"},
                "Gate B from the group's research page, under 'The group has a current focus on materials including:', "
                "one of five material classes beside carbon nanotubes and graphene. Gate A from the group's About page "
                "(his directory profile did not load at the raw check)."),
}
# rows Muse called PASS that fail the lane rule: raw-checked for the report, never admitted
OWNER = {
    "BB-0037": "Healy: Gate B quote lists lab members' projects (hydrogels), not his own research statement",
    "BB-0046": "Aguado: Gate B is a department REU program page (his mentor project, his own voice), not his profile or lab page",
    "BB-0181": "Szleifer: Gate B is a research-center page listing his topics, not his profile or lab page",
    "BB-0218": "Gabrielson: Gate B is a 2011-12 postdoc alumni entry in another faculty member's lab",
    "BB-0220": "Zimmerman: Gate A conflict on Illinois's own pages (Research Professor vs Professor Emeritus)",
    "BB-0491": "Allcock: Gate A conflict on Penn State's own pages (Atherton Professor vs Professor Emeritus)",
}
out = []
for lid, (rep, note) in CAND.items():
    r = {c: lane[lid].get(c, "") for c in COLS}
    r.update(rep, verdict="VERIFIED", observed_date="2026-11-19", verdict_note=note)
    assert all(r[c] for c in COLS), (lid, [c for c in COLS if not r[c]])
    for q in ("gate_a_quote", "gate_b_quote"):
        assert len(r[q].split()) <= 25, (lid, q)
    out.append(r)
muse = {r["lead_id"]: r for f in ("part3_faculty.csv", "part4_faculty.csv")
        for r in csv.DictReader(open(HERE.parent / "muse-2026-11-19" / f, encoding="utf-8"))}
own = [{"lead_id": k, "full_name": muse[k]["name"], "gate_a_url": muse[k]["gate_a_url"], "gate_a_quote": muse[k]["gate_a_quote"],
        "gate_b_url": muse[k]["gate_b_url"], "gate_b_quote": muse[k]["gate_b_quote"], "why_not_admitted": v} for k, v in OWNER.items()]
for name, rows in (("candidates.csv", out), ("owner_rows.csv", own)):
    with open(HERE / name, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]), lineterminator="\n"); w.writeheader(); w.writerows(rows)
print(len(out), "candidates;", len(own), "owner rows")

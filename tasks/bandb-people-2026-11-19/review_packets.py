"""Full-set review packets for the band-B people (only rows that passed the raw check), split to fit the grok lane."""
import csv, json, sys
from pathlib import Path
C = Path(__file__).resolve().parent
ver = {r["lead_id"]: r for r in csv.DictReader(open(C / "verified.csv", encoding="utf-8"))}
rc = {r["lead_id"]: r for r in csv.DictReader(open(C / "rawcheck.csv", encoding="utf-8"))}
ok = [ver[k] for k, x in rc.items() if x["gate_a"] == "yes" and x["gate_b"] == "yes" and x["gate_a_surname"] == "yes"]
rows = [{"lead_id": r["lead_id"], "name": r["full_name"], "institution": r["institution_org_id"], "role": r["role"],
         "role_as_published": r["role_as_published"], "gate_a_quote": r["gate_a_quote"], "gate_a_url": r["gate_a_url"],
         "gate_b_quote": r["gate_b_quote"], "gate_b_url": r["gate_b_url"], "lane_note": r["verdict_note"][:200]} for r in ok]
HEAD = """Refute this data PR for the Polymer Atlas (public dataset of US polymer professors). Do not edit anything. Each row below is a
proposed new people record: a lane judged both gates passed, and every quote was machine-verified word for word on the
university's own page (surname within 40 words of the Gate A quote). Rules (SCHEMA 4.9):
- Gate A: the university's own page styles the person, CURRENTLY, as professor / associate_professor / assistant_professor /
  research_professor (assistant/associate/full research professor) / center_director_professor (director with a professor
  title) / senior_lecturer. Emeriti, adjuncts, lecturers (other than senior lecturer), professors of practice, teaching
  professors, research or staff scientists, visiting and courtesy titles FAIL. A person whose primary appointment is
  elsewhere FAILS at this institution.
- Gate B: the person's own page states polymer-specific research (polymers, macromolecules, plastics, rubber/elastomers,
  polymer-matrix composites, polymer membranes, hydrogels/polymer networks, polymer coatings/adhesives, polymer processing).
  Generic soft matter / materials / biomaterials / nanomaterials with no polymer named FAIL; so do a department blurb, a
  news story about others, or polymers named only as a tool in non-polymer work.
For EACH row: SOUND, or WRONG (which gate fails and why), or DOUBT (the fact that would settle it). Be strict: the record is
public. End with the count of SOUND / WRONG / DOUBT. Under 1200 words; one line per row.

ROWS:
"""
half = (len(rows) + 1) // 2
for i, part in enumerate((rows[:half], rows[half:]), 1):
    (C / f"review_part{i}.md").write_text(HEAD + json.dumps(part, indent=0, ensure_ascii=False), encoding="utf-8")
    print(f"part {i}: {len(part)} rows, {len((C / f'review_part{i}.md').read_bytes())} bytes")
print("raw-check pass", len(ok), "of", len(rc))

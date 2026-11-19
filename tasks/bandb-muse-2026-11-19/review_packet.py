"""Review packet for the Muse-settled band-B candidates: only rows that passed the raw check (both quotes word for word on a
fresh re-fetch, surname within 40 words of the Gate A quote). Same rules text as the band-B packets.
    python -I review_packet.py"""
import csv, json
from pathlib import Path

C = Path(__file__).resolve().parent
cand = {r["lead_id"]: r for r in csv.DictReader(open(C / "candidates.csv", encoding="utf-8"))}
rc = {r["lead_id"]: r for r in csv.DictReader(open(C / "rawcheck.csv", encoding="utf-8"))}
ok = [cand[k] for k, x in rc.items() if x["gate_a"] == x["gate_b"] == x["gate_a_surname"] == "yes"]
rows = [{"lead_id": r["lead_id"], "name": r["full_name"], "institution": r["institution_org_id"], "role": r["role"],
         "role_as_published": r["role_as_published"], "gate_a_quote": r["gate_a_quote"], "gate_a_url": r["gate_a_url"],
         "gate_b_quote": r["gate_b_quote"], "gate_b_url": r["gate_b_url"], "note": r["verdict_note"]} for r in ok]
HEAD = """Refute this data PR for the Polymer Atlas (public dataset of US polymer professors). Do not edit anything. Each row below is a
proposed new people record. An earlier pass held each one on a single open question; a second source (Meta's Muse) answered
it, and every quote below was then machine-verified word for word on the university's own page by a fresh re-fetch
(surname within 40 words of the Gate A quote). The note says what changed. Rules (SCHEMA 4.9):
- Gate A: the university's own page styles the person, CURRENTLY, as professor / associate_professor / assistant_professor /
  research_professor (assistant/associate/full research professor) / center_director_professor (director with a professor
  title) / senior_lecturer. Emeriti, adjuncts, lecturers (other than senior lecturer), professors of practice, teaching
  professors, research or staff scientists, visiting and courtesy titles FAIL. A person whose primary appointment is
  elsewhere FAILS at this institution.
- Gate B: the person's own profile or lab page states polymer-specific research (polymers, macromolecules, plastics,
  rubber/elastomers, polymer-matrix composites, polymer membranes, hydrogels/polymer networks, polymer coatings/adhesives,
  polymer processing). Generic soft matter / materials / biomaterials / nanomaterials with no polymer named FAIL; so do a
  department blurb, a news story, a publication or grant title, or polymers named only as a tool in non-polymer work.
For EACH row: SOUND, or WRONG (which gate fails and why), or DOUBT (the fact that would settle it). Be strict: the record is
public. End with the count of SOUND / WRONG / DOUBT. Under 800 words; one line per row, starting with the lead_id.

ROWS:
"""
(C / "review_part1.md").write_text(HEAD + json.dumps(rows, indent=0, ensure_ascii=False), encoding="utf-8")
print(len(rows), "rows of", len(rc), "raw-checked")

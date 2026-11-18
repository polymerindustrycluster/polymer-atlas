#!/usr/bin/env python3
"""One-shot (re-runnable) author of verdicts.csv + frame.csv from the stored witnesses.
Verdicts are judgments recorded here; build.py consumes verdicts.csv only."""
import csv, json, re, os, sys
sys.path.insert(0, os.path.dirname(__file__))
import common, view
HERE = os.path.dirname(os.path.abspath(__file__))
TODAY = "2026-11-17"
M = common.manifest()
held = common.people()
by_full = {common.norm(p["full_name"]): p for p in held}
by_ft = {common.toks(p["full_name"]): p for p in held}
def heldp(name):
    return by_full.get(common.norm(name)) or by_ft.get(common.toks(name))
INST = {"CWRU": "ORG-000502", "KENT": "ORG-000503", "YSU": "ORG-002175", "WALSH": "ORG-001318", "CSU": "ORG-000158", "NASA": "ORG-001264"}
COLS = ["institution", "institution_org_id", "unit", "full_name", "role", "role_as_published", "research_specialties",
        "public_profile_url", "lab_url", "gate_a_url", "gate_a_sha256", "gate_a_quote", "gate_b_url", "gate_b_sha256",
        "gate_b_quote", "scope_effect", "verdict", "verdict_note", "already_in_atlas", "observed_date"]
rows = []
def add(inst, unit, name, verdict, note, **k):
    r = dict.fromkeys(COLS, ""); r["scope_effect"] = "supports_A" if verdict == "VERIFIED" else ""; r.update(institution=inst, institution_org_id=INST[inst], unit=unit, full_name=name,
                                          verdict=verdict, verdict_note=note, observed_date=TODAY)
    r.update(k)
    for side in ("a", "b"):
        u = r[f"gate_{side}_url"]
        if u:
            r[f"gate_{side}_sha256"] = M[u]
            assert common.quote_in(M[u], r[f"gate_{side}_quote"]), (name, side)
            assert len(r[f"gate_{side}_quote"].split()) <= 25, (name, side)
    rows.append(r)

# ---------- VERIFIED ----------
add("CWRU", "BME", "Jeffrey Capadona", "VERIFIED", "Professor of Biomedical Engineering; own lab page states polymer-based intracortical microelectrodes",
    role="professor", role_as_published="Donnell Institute Professor of Biomedical Engineering, Department of Biomedical Engineering", research_specialties="biomedical_polymers",
    public_profile_url="https://case.edu/engineering/about/faculty-and-staff-directory/jeffrey-capadona",
    lab_url="https://case.edu/bme/research/labs/capadona-lab/capadona-lab-research",
    gate_a_url="https://case.edu/engineering/about/faculty-and-staff-directory/jeffrey-capadona", gate_a_quote="Donnell Institute Professor of Biomedical Engineering, Department of Biomedical Engineering",
    gate_b_url="https://case.edu/bme/research/labs/capadona-lab/capadona-lab-research", gate_b_quote="mechanically-dynamic polymer-based intracortical microelectrodes")
add("CWRU", "BME", "Zheng-Rong Lu", "VERIFIED", "Named professor of Biomedical Engineering; own profile lists biodegradable macromolecular MRI contrast agents as a research project (list item: scope supports_B)",
    scope_effect="supports_B", role="professor", role_as_published="M. Frank and Margaret Domiter Rudy Professor of Biomedical Engineering, Department of Biomedical Engineering",
    research_specialties="biomedical_polymers",
    public_profile_url="https://case.edu/engineering/about/faculty-and-staff-directory/zheng-rong-lu",
    gate_a_url="https://case.edu/engineering/about/faculty-and-staff-directory/zheng-rong-lu", gate_a_quote="M. Frank and Margaret Domiter Rudy Professor of Biomedical Engineering",
    gate_b_url="https://case.edu/engineering/about/faculty-and-staff-directory/zheng-rong-lu", gate_b_quote="Biodegradable macromolecular MRI contrast agents that can be used for contrast enhanced cardiovascular and cancer MRI")
add("KENT", "AMLCI/Materials Science", "Liang-Chy Chien", "VERIFIED", "Professor (Materials Science, AMLCI); own profile states polymer-stabilized liquid crystal fabrication",
    role="professor", role_as_published="Professor", research_specialties="liquid_crystals",
    public_profile_url="https://www.kent.edu/amlci/liang-chy-chien",
    gate_a_url="https://www.kent.edu/amlci/liang-chy-chien", gate_a_quote="Liang-Chy Chien Materials Science Professor",
    gate_b_url="https://www.kent.edu/amlci/liang-chy-chien", gate_b_quote="develops tools and methods of fabrication polymer stabilized liquid crystals")
# ---------- STILL_UNCERTAIN ----------
def su(inst, unit, name, note, **k): add(inst, unit, name, "STILL_UNCERTAIN", note, **k)
su("CWRU", "MACRO", "Pablo Froimowicz", "Gate A met (Research Associate Professor, MACRO) but his case.edu profile carries only the title and no research statement. Settling fact: an institutional page (profile or lab page) stating polymer research in his own words",
   gate_a_url="https://case.edu/engineering/about/faculty-and-staff-directory/pablo-froimowicz", gate_a_quote="Research Associate Professor, Department of Macromolecular Science and Engineering")
su("CWRU", "Chemistry", "John D. Protasiewicz", "Gate A met (Hurlbut Professor of Chemistry). Gate B: roster lists 'Polymers' as one of ten interests ('see website'), lab page fetched states no polymer object. Settling fact: a profile or lab page stating a polymer research object",
   gate_a_url="http://chemistry.case.edu/faculty/john-protasiewicz", gate_a_quote="Hurlbut Professor of Chemistry",
   gate_b_url="http://chemistry.case.edu/faculty/john-protasiewicz", gate_b_quote="Photochemistry, Polymers, Spectroscopy, Synthesis")
su("CWRU", "MAE", "Ya-Ting Liao", "Gate A met (Associate Professor, MAE). Her profile lists 'Fire-safe Polymers' only as an affiliated department research-area tag; her stated research is combustion modelling. Settling fact: her own statement of polymer research",
   gate_a_url="https://case.edu/engineering/about/faculty-and-staff-directory/ya-ting-liao", gate_a_quote="Associate Professor, Department of Mechanical and Aerospace Engineering",
   gate_b_url="https://case.edu/engineering/about/faculty-and-staff-directory/ya-ting-liao", gate_b_quote="Fire-safe Polymers")
su("CWRU", "MACRO (materials-branch page only)", "Alberto Costa", "Directory title says Research Assistant Professor, MACRO (Materials Branch page), but his case.edu profile URL returned the generic directory page with no profile and a web search associated the name with a School of Medicine appointment. Settling fact: a current profile for him in the Case School of Engineering",
   gate_a_url="https://engineering.case.edu/materials-branch/faculty", gate_a_quote="Research Assistant Professor, Macromolecular Science and Engineering")
add("KENT", "AMLCI/Chemistry", "Mietek Jaroniec", "REJECT", "Gate B fails: profile states ordered mesoporous materials; polymer appears only as a template ('surfactant- and polymer-templated ordered silicas'), not as the research object",
    gate_b_url="https://www.kent.edu/chemistry/profile/mietek-jaroniec", gate_b_quote="surfactant- and polymer-templated ordered silicas")
su("CSU", "Chemical and Biomedical Engineering", "Chandra Kothapalli", "Gate A met (Professor, department research page). The only polymer-type statement is on a department research-area page, not his own profile or lab page: 'extracellular matrix-based hydrogels and electrospun nanofibrous composites'. Whether ECM-protein hydrogels are a polymer object is a scope question: owner ruling, see README. Settling fact: owner ruling plus his own profile or lab page text",
   gate_a_url="https://engineering.csuohio.edu/chemical/biomaterials-research", gate_a_quote="Dr. Chandra Kothapalli Professor",
   gate_b_url="https://engineering.csuohio.edu/chemical/biomaterials-research", gate_b_quote="Development of extracellular matrix-based hydrogels and electrospun nanofibrous composites")
su("KENT", "AMLCI affiliated", "Hanbin Mao", "Gate A met (Professor). Profile states single-molecule studies of 'biomacromolecules including DNA and proteins'; whether biomacromolecule biophysics counts as polymer research is a scope question: owner ruling, see README. Settling fact: owner ruling",
   gate_b_url="https://www.kent.edu/amlci/hanbin-mao", gate_b_quote="fundamental properties of biomacromolecules including DNA and proteins")
su("KENT", "AMLCI/Chemistry", "John L. West", "Gate A met on the AMLCI profile ('Trustees Research Professor', same styling held as research_professor for PERSON-000023). Polymer research is stated only on an undated seminar-style bio on the chemistry site ('liquid crystal core surrounded by a polymer sheath'); his AMLCI profile has no research text. Settling fact: a current profile or lab page stating the research",
   gate_a_url="https://www.kent.edu/amlci/john-l-west", gate_a_quote="Trustees Research Professor",
   gate_b_url="https://www.kent.edu/chemistry/dr-john-west-liquid-crystals-flexible-electronics", gate_b_quote="consisting of a liquid crystal core surrounded by a polymer sheath")
su("YSU", "Chemistry", "Russell J. Moser", "Own page states 'Organic, Polymer, Biological & Analytical Chemistry' but shows no faculty rank on the page fetched. Settling fact: a YSU page styling him in a professor rank",
   gate_b_url="http://people.ysu.edu/~<acct>", gate_b_quote="Organic, Polymer, Biological & Analytical Chemistry")
su("YSU", "Chemistry", "Allen D. Hunter", "Home page fetch failed (HTTP 000, availability only). Settling fact: a successful fetch of his YSU page stating rank and polymer research")
su("WALSH", "Chemistry", "Neil Walsh", "Gate A met (Associate Professor of Chemistry) but profile lists only 1990s styrene/butadiene copolymer publications and no current research statement. Settling fact: a statement of current polymer research",
   gate_a_url="https://www.walsh.edu/directory/neil-walsh.html", gate_a_quote="Chair, Mathematics and Sciences; Associate Professor of Chemistry")
su("NASA", "Polymers (lab pages)", "Michael A. Meador", "NTRS record shows Glenn authorship of a polymer-research overview but is a report, not a Glenn staff or program page styling him research staff. Settling fact: a Glenn staff/program page styling him research staff with polymer research (and current employment)")
su("NASA", "Polymers (lab pages)", "Tiffany S. Williams", "NTRS record is a presentation, not a Glenn page styling her research staff. Settling fact: a Glenn staff/program page styling her research staff with polymer research")

# ---------- Re-screen 2026-11-17 (Codex-23 finding on PR #370): CWRU engineering bulletins as the check ----------
BUL = "https://bulletin.case.edu/engineering/biomedical-engineering/"
su("CWRU", "BME", "Anirban Sen Gupta", "Gate A met (Wallace R. Persons Professor, BME). Re-screen: his own profile and the CWRU pathology biography page state 'novel biomaterials' and drug-delivery research with no polymer object, but the CWRU BME bulletin lists 'novel polymeric biomaterials for tissue engineering scaffolds' (lead). Settling fact: his own profile or lab page stating polymer research",
   gate_a_url="https://case.edu/engineering/about/faculty-and-staff-directory/anirban-sen-gupta", gate_a_quote="Wallace R. Persons Professor",
   gate_b_url=BUL, gate_b_quote="novel polymeric biomaterials for tissue engineering scaffolds")
su("CWRU", "MAE", "Ozan Akkus", "Gate A met (Kent H. Smith Professor, MAE). Re-screen: his profile and his Tissue Fabrication and Mechanobiology Lab page state no polymer object, but the CWRU BME bulletin lists 'ductile biocompatible polymer matrices are subjected to mineralization' (lead). Settling fact: his own profile or lab page stating polymer research",
   gate_a_url="https://case.edu/engineering/about/faculty-and-staff-directory/ozan-akkus", gate_a_quote="Kent H. Smith Professor, Department of Mechanical and Aerospace Engineering",
   gate_b_url=BUL, gate_b_quote="ductile biocompatible polymer matrices are subjected to mineralization")

# ---------- CWRU engineering directory: anchor-keyed frame (professor-rank titles in MACRO/MSE/CBE/BME/MAE) ----------
UNITS = [("Macromolecular", "MACRO"), ("Materials Science", "MSE"), ("Chemical", "CBE"), ("Biomedical", "BME"), ("Mechanical", "MAE")]
STMT = re.compile(r"research interests|research information|expertise|my research|our research|his research|her research|research focus|research areas|research summary|research:", re.I)
def has_statement(sha): return bool(STMT.search(common.page_text(sha)))
done = {r["full_name"] for r in rows}
CASE_ENTRIES = [(n, h, t) for n, h, t in common.case_entries() if "Professor" in t and any(k in t for k, _ in UNITS)]
def case_unit(t): return next(c for k, c in UNITS if k in t)
for nm, href, title in CASE_ENTRIES:
    if nm in done: continue
    unit = case_unit(title); url = "https://case.edu" + href; segs = title.split(" | ")
    hp = heldp(nm)
    if hp:
        add("CWRU", unit, nm, "DUPLICATE_OF", "Already held; no row written", already_in_atlas=hp["person_id"]); continue
    if not any("Professor" in x and not re.search(r"Emerit|Visiting|Adjunct", x) for x in segs):
        add("CWRU", unit, nm, "REJECT", "Gate A fails: directory entry styles emeritus/visiting/adjunct, no active professor rank"); continue
    if url not in M: add("CWRU", unit, nm, "STILL_UNCERTAIN", "Profile not fetched in this pass; settling fact: its text"); continue
    if has_statement(M[url]): add("CWRU", unit, nm, "REJECT", "Gate B fails: own profile has a research statement/areas that name no polymer object (lab pages not checked)")
    else: add("CWRU", unit, nm, "STILL_UNCERTAIN", "Gate A met (professor rank on directory) but profile carries no research statement. Settling fact: a profile or lab page stating research")

# ---------- Kent ----------
kent_new = ["Philip Bos", "Arkaprabha Konar", "Robert J. Clements", "Ali Abdul-Aziz", "Dhruba Panthi", "Yanhai Du", "Farid Fouad", "Diana Goncalves-Schmidt", "Min-Ho Kim",
            "Barry Dunietz", "Songping Huang", "Alexander Seed", "Yaorong Zheng"]
for n in kent_new:
    u = "https://www.kent.edu" + json.load(open(os.path.join(HERE, "kent_links.json")))[n][0]
    if has_statement(M[u]): add("KENT", "AMLCI affiliated", n, "REJECT", "Gate B fails: AMLCI profile has a research statement naming no polymer object (lab pages not checked)")
    else: add("KENT", "AMLCI affiliated", n, "STILL_UNCERTAIN", "AMLCI profile carries no research statement. Settling fact: a profile or lab page stating research")
add("KENT", "AMLCI affiliated", "Joycelyn Harrison", "REJECT", "Gate A fails: AMLCI profile styles her 'Research', no professor rank")
add("KENT", "AMLCI affiliated", "Mourad Krifa", "REJECT", "Gate A fails: profile styles him Margaret Clark Morgan Director of the School of Fashion Design and Merchandising, no professor rank on the page; no polymer statement")
# ---------- YSU (catalog graduate-faculty listings) ----------
add("YSU", "Chemistry", "Douglas T. Genna", "REJECT", "Gate B fails: listed interests are metal-organic frameworks, no polymer object")
add("YSU", "Mechanical/Materials", "Pedro Cortes", "DUPLICATE_OF", "Same name is held as PERSON-001142 at ORG-004749, shown here at YSU in a 2022-23 catalog; follow-up for the controller, nothing written",
    already_in_atlas="PERSON-001142")
for n in ["Farzad Ahmadi", "Snjezana Balaz", "Vamsi Borra", "Richard Albert Deschenes, Jr.", "Tom Nelson Oder", "Donald Priour", "Jae Joong Ryu", "Virgil C. Solomon", "Timothy R. Wagner", "Kyosung Choo"]:
    add("YSU", "Materials Science and Engineering (PhD)", n, "REJECT", "Gate B fails: catalog listing of research interests states no polymer object")
for n in ["Ganesaratnam K. Balendiran", "Brian D. Leskiw", "Josef B. Simeonsson", "Michael A. Serra", "Nina V. Stourman", "Robert E. Wardle"]:
    add("YSU", "Chemistry (MS)", n, "REJECT", "Gate B fails: catalog listing of research interests states no polymer object")
# ---------- CSU ----------
for n, why in [("Geyou Ao", "Gate B fails: expertise is nanomaterials liquid crystals, no polymer object"),
               ("Joanne M. Belovich", "Gate B fails: expertise is fermentation and tissue transport modelling"),
               ("Jorge E. Gatica", "Gate B fails: expertise is reaction engineering and transport"),
               ("Chelsea Monty-Bromer", "Gate B fails: expertise is electrochemical sensors and biofuel cells"),
               ("Sridhar Ungarala", "Gate B fails: expertise is process control"),
               ("Shaowei Yang", "Gate B fails: 'microporous materials and membranes' with no polymer object stated"),
                              ("Hannah Cebull", "Gate A fails: Assistant Lecturer"),
               ("Richard Schoephoerster", "Gate B unsettled: no research statement on the department page"),
               ("Marvin E. Thrash", "Gate A fails: Associate Professor of Practice, no polymer statement"),
               ("Lawrence T. Novak", "Gate A fails: adjunct faculty")]:
    add("CSU", "Chemical and Biomedical Engineering", n, "STILL_UNCERTAIN" if why.startswith("Gate B unsettled") else "REJECT", why)
# ---------- Walsh ----------
add("WALSH", "Chemistry", "Peter Tandler", "STILL_UNCERTAIN", "Gate A met (Associate Professor of Chemistry). Fetched profile states no research (a teaching presentation only). Settling fact: a person-specific research statement on a Walsh page",
    gate_a_url="https://www.walsh.edu/directory/peter-tandler.html", gate_a_quote="Associate Professor of Chemistry")
# ---------- CWRU chemistry roster ----------
for n in ["Matthew Bertin", "Natalie Briggs", "Clemens Burda", "Carlos E. Crespo-Hernandez", "Thomas Gray", "Irene Nga Wing Lee", "Fu-Sen Liang", "Divita Mathur",
          "Shane M. Parker", "Robert G. Salomon", "Daniel A. Scherson", "Gregory P. Tochtrop", "Yihang Wang"]:
    add("CWRU", "Chemistry", n, "REJECT", "Gate B fails: department roster research-interest list names no polymer object (lab pages not checked)")
for n in ["Brian Fitch", "Drew A. Meyer", "Rekha Srinivasan"]:
    add("CWRU", "Chemistry", n, "REJECT", "Gate A fails: instructor styling on department roster")

# ---------- DUPLICATE_OF: held people shown in a frame at my institutions ----------
dup_units = {"CWRU": [], "KENT": [], "CSU": ["Nolan B. Holland", "Metin Uz"]}
for nm in ["Torsten Hegmann", "Elda Hegmann", "Antal Jakli", "Oleg Lavrentovich", "Elizabeth Mann", "Peter Palffy-Muhoray", "Marianne Prévôt", "Jonathan Selinger", "Robin Selinger", "Hao Shen",
           "Samuel Sprunt", "Hiroshi Yokoyama", "Michael Fisch", "Robert Twieg"]:
    h = heldp(nm); add("KENT", "AMLCI affiliated", nm, "DUPLICATE_OF", "Already held at this institution; no row written", already_in_atlas=h["person_id"] if h else "")
for nm in ["Nolan B. Holland", "Metin Uz"]:
    h = heldp(nm); add("CSU", "Chemical and Biomedical Engineering", nm, "DUPLICATE_OF", "Already held at this institution; no row written", already_in_atlas=h["person_id"])
for nm in ["Peter Norris", "Clovis Linkous", "Holly J. Martin", "Bharat Yelamanchi", "Byung-Wook Park"]:
    h = heldp(nm); add("YSU", "catalog/chemistry", nm, "DUPLICATE_OF", "Already held at this institution; no row written", already_in_atlas=h["person_id"])
for nm in ["Metin Karayilan", "Genevieve Sauve", "Anna C. Samia"]:
    h = heldp(nm); add("CWRU", "Chemistry", nm, "DUPLICATE_OF", "Already held at this institution; no row written", already_in_atlas=h["person_id"])
h = heldp("Amy Heston"); add("WALSH", "Chemistry", "Amy Heston", "DUPLICATE_OF", "Already held at this institution; no row written", already_in_atlas=h["person_id"])

for r in rows:  # lab page stated his research, so this REJECT rests on a stated statement, not on silence
    if r["full_name"] == "Robert Warburton" and r["verdict"] == "REJECT":
        r["verdict_note"] = "Gate B fails: own lab page (sites.google.com/view/warburton-lab-cwru, linked from his profile) states computational materials research on interfaces for energy storage and catalysis, no polymer object"
# sanity: DUPLICATE ids must be real held people; every other candidate must not be held at same institution
hp = {p["person_id"]: p for p in held}
final = []
seen = set()
for r in rows:
    key = (r["institution"], common.norm(r["full_name"]))
    if key in seen: continue
    seen.add(key)
    if r["verdict"] == "DUPLICATE_OF": assert r["already_in_atlas"] in hp, r["full_name"]
    else:
        h = heldp(r["full_name"])
        assert not h or r["verdict"] == "DUPLICATE_OF" or 2400 <= int(h["person_id"][7:]) <= 2499, ("held but not duplicate", r["full_name"], h["person_id"] if h else "")
    final.append(r)
w = csv.DictWriter(open(os.path.join(HERE, "verdicts.csv"), "w", newline=""), COLS)
w.writeheader(); w.writerows(final)
from collections import Counter
print(len(final), Counter(r["verdict"] for r in final))

# ---------- frame.csv ----------
SRC = {("CWRU", "MACRO"): "https://case.edu/engineering/about/faculty-and-staff-directory", ("CWRU", "MSE"): "https://case.edu/engineering/about/faculty-and-staff-directory",
       ("CWRU", "CBE"): "https://case.edu/engineering/about/faculty-and-staff-directory", ("CWRU", "BME"): "https://case.edu/engineering/about/faculty-and-staff-directory",
       ("CWRU", "MAE"): "https://case.edu/engineering/about/faculty-and-staff-directory", ("CWRU", "other"): "https://case.edu/engineering/about/faculty-and-staff-directory",
       ("CWRU", "Chemistry"): "https://chemistry.case.edu/people/faculty/",
       ("YSU", "Chemistry"): "https://catalog.ysu.edu/graduate/graduate-programs/master-science-chemistry/", ("YSU", "Chemistry (MS)"): "https://catalog.ysu.edu/graduate/graduate-programs/master-science-chemistry/", ("YSU", "catalog/chemistry"): "https://catalog.ysu.edu/graduate/graduate-programs/master-science-chemistry/"}
DEF = {"KENT": "https://www.kent.edu/amlci/faculty", "YSU": "https://catalog.ysu.edu/archives/2022-2023/graduate/graduate-programs/doctor-philosophy-materials-science-engineering/",
       "CSU": "https://engineering.csuohio.edu/chemical/people", "WALSH": "https://www.walsh.edu/directory/neil-walsh.html", "NASA": "https://ntrs.nasa.gov/citations/20070022363"}
cnt = Counter((r["institution"], r["unit"]) for r in final)
LISTED = Counter(case_unit(t) for _, _, t in CASE_ENTRIES)  # frame size per CWRU unit, recomputed from the stored directory page
fr = [{"institution": i, "unit": u, "frame_source_url": SRC.get((i, u), DEF.get(i, "")), "examined": n, "listed": LISTED[u] if i == "CWRU" and u in LISTED else "n/a",
       "verified": sum(1 for r in final if (r["institution"], r["unit"]) == (i, u) and r["verdict"] == "VERIFIED"),
       "note": "examined = verdict rows in this unit (includes held people shown as DUPLICATE_OF)"} for (i, u), n in sorted(cnt.items())]
NOT = [("CWRU", "Engineering directory entries with professor titles outside MACRO/MSE/CBE/BME/MAE and CWRU Physics/Arts and Sciences units other than Chemistry", "https://case.edu/engineering/about/faculty-and-staff-directory"),
       ("KENT", "AMLCI affiliated faculty in Mathematical Sciences, Computer Science, Nursing, Public Health, Podiatric Medicine, Anthropology, Architecture, plus Physics members Maxim Dzero and Margarita Benitez (listed, not fetched); Kent chemistry/engineering/physics faculty outside AMLCI", "https://www.kent.edu/amlci/faculty"),
       ("YSU", "YSU chemistry, chemical, mechanical and civil faculty beyond the two catalog listings; Greg Dillon (current role unverified); current YSU department rosters", "https://catalog.ysu.edu/graduate/graduate-programs/master-science-chemistry/"),
       ("CSU", "Mechanical Engineering, Physics and Chemistry faculty (CSU physics participating-faculty page fetched, not adjudicated)", "https://artsandsciences.csuohio.edu/physics/participating-faculty"),
       ("WALSH", "Walsh faculty other than the chemistry names above", "https://www.walsh.edu/faculty.html"),
       ("NASA", "No Glenn staff directory was reachable from held URLs or search; Robert K. Goldberg is a lead (NTRS-named) not examined", "")]
for i, u, s in NOT: fr.append({"institution": i, "unit": "NOT ADJUDICATED: " + u, "frame_source_url": s, "listed": "not counted", "examined": 0, "verified": 0, "note": "unresolved, not negative"})
w = csv.DictWriter(open(os.path.join(HERE, "frame.csv"), "w", newline=""), ["institution", "unit", "frame_source_url", "listed", "examined", "verified", "note"])
w.writeheader(); w.writerows(fr)

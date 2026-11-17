#!/usr/bin/env python3
"""Write verdicts.csv: one row per distinct person in frame.csv. Automatic verdicts (held at Akron -> DUPLICATE_OF; listing title not a
professor rank -> REJECT Gate A) plus hand adjudications (MANUAL) of the profile pages in persist/. Quotes are taken from stored pages."""
import csv, re, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from frame import build, norm
from pagetext import text, quote_in
TODAY = "2026-11-17"
import csv as _c
SHA = {}  # url -> sha (latest) from the persist manifest
for r in _c.DictReader(open("/Users/johnswanson/.bb/thread-storage/thr_9i2c6byhcz/2026-11-06-atlas/persist/pic18-faculty-akron-2026-11-17/manifest.csv")):
    SHA[r["url"]] = r["sha256"]

def clean(n):
    n = re.sub(r",?\s*(Ph\.?D\.?|M\.T\.|P\.E\.|M\.S\.)", "", n)
    return " ".join(re.sub(r"^(Dr|Mr|Ms|Mrs)\.?\s+", "", n).replace(" ,", ",").split())

def title_quote(sha, title):
    q = f"Title: {title}"
    return q if quote_in(q, sha) else ""

def research_quote(sha, n=25):
    t = text(sha); i = t.find("Dept/Program")
    m = re.search(r" Research (?!Associate|Scientist|Assistant|Center|Institute|and |Laborator|Campus)", t[i:])
    if not m: return ""
    s = t[i + m.start() + 1:]
    s = re.split(r" Education | Courses | Publications ", s)[0]
    return " ".join(s.split()[:n])

# hand adjudications keyed by normalized (first,last). Gate A from the profile's own "Title:"; Gate B from profile text (or lab page).
V = {}
def man(name, verdict, note, **kw): V[norm(name)] = dict(verdict=verdict, note=note, **kw)
man("Hossein Ravanbakhsh", "VERIFIED", "Assistant Professor; own profile states hydrogel and smart-polymer research", role="assistant_professor",
    rap="Assistant Professor", specs="biomedical_polymers",
    b_quote="His research has been focused on engineering hydrogel materials and smart polymers for tissue engineering and regenerative medicine applications.")
man("Bi-min Zhang Newby", "VERIFIED", "Professor and Department Chair; own profile lists polymer thin films as research", role="professor",
    rap="Professor and Department Chair", specs="polymer thin films;surface modification;antifouling and biofilm",
    b_quote="Research Surface modification, antifouling/biofilm, polymer thin films, stimuli responsive bio-materials, biocorrosion")
man("Jutta Luettmer-Strathmann", "VERIFIED", "Professor (Physics; listed as Chemistry joint faculty); own profile states polymer melt and blend research", role="professor",
    rap="Professor", specs="polymer_physics;polymer melts and blends",
    b_quote="Local friction in polymer melts and blends Monte Carlo, Density-of-States, and Molecular Dynamics simulations Static and dynamic properties of polymer melts and blends")
man("Yi Pang", "STILL_UNCERTAIN", "Profile research text is fluorescent dyes and ESIPT sensors; polymer appears only in publication-group headings and titles. Lab page gozips.uakron.edu/~yp5 (link on the profile) did not load (HTTP 000, availability). Settling fact: his lab page or a current profile statement naming polymer research. Recommendation: hold.", b_quote="In the area of polymer-CNT interaction")
man("Sergei F. Lyuksyutov", "STILL_UNCERTAIN", "Profile is a biography and publication list (polymer nanolithography titles) with no stated research paragraph; lab page nebula.physics.uakron.edu/dept/faculty/sfl.htm (link on the profile) did not load (HTTP 000, availability). Settling fact: a page of his own stating polymer research. Recommendation: hold.", b_quote="Electrostatic nanolithography in polymers using atomic force microscopy")
man("Robert R. Mallik", "STILL_UNCERTAIN", "Stated research object is nanoscale thin films and semiconductor surface science; polymers and SBR appear only as substrates his patterning technique was applied to. Owner/integrator scope call on Gate B (McComb precedent argues REJECT). Recommendation: REJECT.", b_quote="to create raised nanostructures on semiconductor and polymer films")
man("Hossein Tavana", "STILL_UNCERTAIN", "Profile research is cancer, microtechnology, tissue engineering; polymer appears only in his PhD description. Lab page tavana.uakron.edu (link on profile) returned only a script shell with no research text. Settling fact: the rendered lab page stating polymer research (for example an aqueous two-phase polymer system). Recommendation: hold.", b_quote="studied interfacial tensions and contact angles of polymer films-fluid systems")
REJ = {  # gate B rejects among profile-fetched candidates: deciding fact
 "Aliaksei Boika": "Research is electroanalytical detection of nanoparticles and macromolecules as analytes; no polymer research object",
 "William Donovan": "Research is chemistry education; no polymer research",
 "Yilin Liu": "Research is heme-protein spectroscopy; no polymer research (not the held PERSON-000593 Yi Liu)",
 "Christopher J. Ziegler": "Research is coordination chemistry, porphyrins and fluorophores; metallopolymers appear only in publication titles",
 "Alper Buldum": "Research is computational nanomaterials and nanotribology; no polymer research stated",
 "Edward A. Evans": "Research is oxide nanofiber synthesis; no polymer research stated",
 "Lu-Kwang Ju": "Research is bioprocess, enzyme and microbial technology; his lab page names no polymer research",
 "Nic Leipzig": "Research is regenerative medicine and generic biomaterials; no polymer object named (his lab site is not on an institutional domain)",
 "Donald P. Visco Jr.": "Research is computer-aided molecular design and thermodynamics; no polymer research",
 "Buket Barkana": "Research is biomedical signal processing; no polymer research",
 "Chen Ling": "Research is cognitive systems and human decision making; no polymer research",
 "Ajay Mahajan": "Profile states no polymer research",
 "Sangeun Song": "Research is robotic surgery and soft robotics; no polymer object named",
 "Yang H. Yun": "Research lists biomaterials and electrospinning with no polymer object named",
 "Ge Zhang": "Research is cardiac tissue engineering and natural biomaterials; no polymer object named",
 "Jiang Zhe": "Research is micro and nano sensors and microfluidics; no polymer research stated",
 "Juan Bosch Giner": "Research is tribology and metallurgy; no polymer research",
 "Wesley Carpenter": "Profile states no research and no polymer research",
 "Yalin Dong": "Research is AI, smart manufacturing and robotics; no polymer research",
 "Sergio Felicelli": "Research is solidification and computational mechanics; no polymer research",
 "Xiaosheng Gao": "Research is mechanics of materials and fracture; no polymer object named",
 "Nicholas Garafolo": "Research is thermo-fluid sciences and aerospace seals; no polymer research stated",
 "Hyeonu Heo": "Research is acoustics, metamaterials and tire noise; no polymer object named",
 "Daniel E. Kandray": "Profile states no research and no polymer research",
 "Manigandan Kannan": "Research is metals and ceramic-matrix and fibre composites; no polymer matrix stated (lab page checked)",
 "Gregory Morscher": "Research is ceramic matrix composites; not polymer",
 "Gopal Nadkarni": "Research is manufacturing and materials generally; no polymer object named",
 "Amir Nourhani": "Research is microscale fluid flow and electrokinetics; polymer engineering appears only in his degree line",
 "Heather Oravec": "Profile states no polymer research",
 "Alex Povitsky": "Research is computational fluid dynamics; no polymer research",
 "D. Dane Quinn": "Research is structural dynamics and mechanics; no polymer research",
 "Susan E. Ramlo": "Profile is physics education research; no polymer research",
 "Scott Sawyer": "Profile states no research and no polymer research",
 "Saikishan Suryanarayanan": "Research is boundary-layer flow control; no polymer research",
 "Kwek-Tze Tan": "Research is composite impact and acoustic metamaterials; neither his profile nor lab page names a polymer matrix",
 "Tanmay Tiwari": "Research is precision machining and tribology; no polymer research",
 "Shengyong Wang": "Profile states no polymer research",
 "Guo-Xiang Wang": "Profile states no research and no polymer research",
}
for k, v in REJ.items(): V.setdefault(norm(k), dict(verdict="REJECT", note=v))

def main():
    rows = build()
    people = list(csv.DictReader(open(HERE.parents[1] / "data/people.csv", newline="", encoding="utf-8")))
    order, units, first = [], {}, {}
    for r in rows:
        k = norm(r["name"])
        units.setdefault(k, []).append(r["unit"])
        if k not in first: first[k] = r; order.append(k)
    out = []
    for k in order:
        r = first[k]
        o = dict(name=r["name"], full_name=clean(r["name"]), units=";".join(dict.fromkeys(units[k])), listing_title=r["title"], held_ids=r["held_ids"], observed_date=TODAY,
                 role="", role_as_published="", research_specialties="", public_profile_url=r["profile_url"], gate_a_url="", gate_a_sha="", gate_a_quote="",
                 gate_b_url="", gate_b_sha="", gate_b_quote="", verdict="", verdict_note="")
        prof_sha = SHA.get(r["profile_url"], "")
        if r["held_at_akron"]:
            hid = [x.split("@")[0] for x in r["held_ids"].split(";") if x.endswith("@ORG-000501")][0]
            o.update(verdict=f"DUPLICATE_OF {hid}", verdict_note="held at Akron; row not edited")
        elif k in V:
            m = V[k]; o["verdict"] = m["verdict"]; o["verdict_note"] = m["note"]
            o["gate_a_url"] = r["profile_url"]; o["gate_a_sha"] = prof_sha; o["gate_a_quote"] = title_quote(prof_sha, r["title"]) or ""
            if m["verdict"] == "VERIFIED":
                o.update(role=m["role"], role_as_published=m["rap"], research_specialties=m["specs"], gate_b_url=r["profile_url"], gate_b_sha=prof_sha, gate_b_quote=m["b_quote"])
            else:
                q = m.get("b_quote") or research_quote(prof_sha)
                o.update(gate_b_url=r["profile_url"], gate_b_sha=prof_sha, gate_b_quote=q)
        elif r["gate_a_listing"] == "fail":
            o.update(verdict="REJECT", verdict_note=("Gate A: teaching-track styling (Instruction/Practice) is not in the 4.9 role vocabulary; not examined for Gate B" if re.search("Instruction|Practice", r["title"]) and r["unit"] not in ("SPSPE-adjunct", "SPSPE-emeritus") else "Gate A: listing title is not a professor rank (emeritus, adjunct, lecturer, staff or non-faculty)"),
                     gate_a_url=r["listing_url"], gate_a_sha=r["listing_sha"], gate_a_quote=title_quote(r["listing_sha"], r["title"]) if r["unit"] not in ("SPSPE-adjunct",) else "")
        else:
            o.update(verdict="STILL_UNCERTAIN", verdict_note="candidate not adjudicated (no verdict rule)")
        if k in V and V[k]["verdict"] == "STILL_UNCERTAIN" and "Mallik" not in r["name"]: pass
        out.append(o)
    cols = list(out[0])
    with open(HERE / "verdicts.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, cols); w.writeheader(); w.writerows(out)
    from collections import Counter
    print(len(out), Counter(o["verdict"].split()[0] for o in out))
    for o in out:
        if o["verdict"] == "STILL_UNCERTAIN" and "not adjudicated" in o["verdict_note"]: print("UNADJ", o["name"], o["units"])
if __name__ == "__main__": main()

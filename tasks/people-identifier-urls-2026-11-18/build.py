#!/usr/bin/env python3
"""Apply owner rulings 2026-11-18 items 1 and 1b: remove personal-account identifier URLs from people rows.

Per frame row (identified by the V-62 pattern, never by a stored URL): either REPLACE the identifier URL with an
identifier-free page that states the same facts (plus one new evidence row per claim, quote verified in the stored
page) or BLANK it (the old evidence row stays the source). Changes only public_profile_url, lab_url, sources and
last_verified on frame rows; appends evidence EVD-396100..396199 only; never edits an evidence row. Idempotent.
Usage: python3 build.py          (pages come from PERSIST; a missing page is fetched with the provenance below)
"""
import csv, io, os, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE)); sys.path.insert(0, str(HERE.parent.parent / "scripts"))
from common import *
from shard_io import append_sorted
import fetch

A = "https://www.uakron.edu/polymer/about-us/our-people"
A2 = "https://www.uakron.edu/polymer/about-us/our-people/?currentPage=2"
SPSPE = "Dept/Program: School of Polymer Science and Polymer Engineering"
ME1, ME2 = "https://www.uakron.edu/engineering/me/our-people", "https://www.uakron.edu/engineering/me/our-people?currentPage=2"
HELD = "held record: people.csv sources of the same row"
SIDE = "side-nav / pagination link on a fetched page"
Q = "search I ran 2026-11-18: WebSearch '%s"
# pid -> (url, how the url became fetchable (rule 14), [(claim_type, claim_detail, tier_effect, [quote segments])], caveat)
EXIST = "name, title and institution as published; people row role unchanged"
PLAN = {
 43: (A, HELD, [("existence", EXIST, "supports_A", ["Dr. Ali Dhinojwala Title: W. Gerald Austen Endowed Chair and H.A. Morton Professor " + SPSPE])], ""),
 45: (A, HELD, [("existence", EXIST, "supports_A", ["Dr. Chunming Liu Title: Assistant Professor of Polymer Science & Chemistry " + SPSPE + " & Department of Chemistry"])], ""),
 46: (A, HELD, [("existence", EXIST, "supports_A", ["Dr. Fardin Khabaz Title: Associate Professor of Polymer Engineering and Chemical, Biomolecular & Corrosion Engineering " + SPSPE])], ""),
 48: (A, HELD, [("existence", EXIST, "supports_A", ["Dr. James Eagan Title: Associate Professor " + SPSPE])], ""),
 49: (A, HELD, [("existence", EXIST, "supports_A", ["Dr. Kevin Cavicchi Title: Professor " + SPSPE])], ""),
 50: (A, HELD, [("existence", EXIST, "supports_A", ["Dr. Li Jia Title: Professor of Polymer Science and Chemistry " + SPSPE])], ""),
 52: (A2, SIDE, [("existence", EXIST, "supports_A", ["Dr. Mesfin Tsige Title: Director, SPSPE; Professor " + SPSPE])], ""),
 55: (A2, SIDE, [("existence", EXIST, "supports_A", ["Dr. Shi-Qing Wang Title: Kumho Professor, Distinguished Professor " + SPSPE])], ""),
 57: (A, HELD, [("existence", EXIST, "supports_A", ["Dr. Steven S.C. Chuang Title: Professor, SPSPE; Adjunct Faculty, CBCE " + SPSPE])], ""),
 58: (A, HELD, [("existence", EXIST, "supports_A", ["Dr. Tianbo Liu Title: A. Schulman Professor " + SPSPE])], ""),
 61: (A2, SIDE, [("existence", EXIST, "supports_A", ["Dr. Yu Zhu Title: Professor " + SPSPE])], ""),
 78: (A, HELD, [("existence", EXIST, "supports_A", ["Dr. Christopher Barney Title: Assistant Professor " + SPSPE])], ""),
 76: (ME1, "side-nav 'Our People' link on https://www.uakron.edu/engineering/me/research/ (held record: people.csv, same table)",
      [("existence", EXIST, "supports_A", ["Dr. Jae-Won Choi Title: Professor, Site Director of Center for Tire Research (CenTiRe) Dept/Program: Mechanical Engineering / Biomedical Engineering"])], ""),
 77: (ME2, "pagination link on the ME Our People page (side-nav link on a held record's page)",
      [("existence", EXIST, "supports_A", ["Dr. Michelle S. Hoo Fatt Title: Professor Dept/Program: Mechanical Engineering"])], ""),
 79: ("https://www.uakron.edu/engineering/cbe/our-people/faculty", Q % "Qixin Zhou associate professor Chemical, Biomolecular and Corrosion Engineering University of Akron faculty' (uakron.edu)",
      [("existence", EXIST, "supports_A", ["Dr. Qixin Zhou Title: Associate Professor Dept/Program: Chemical, Biomolecular, and Corrosion Engineering"])], ""),
 97: ("https://www.artsci.uc.edu/natural-sciences/chemistry/faculty-and-staff-directory.html", Q % "Briana Simms assistant professor chemistry University of Cincinnati' (uc.edu)",
      [("existence", EXIST, "supports_A", ["Briana Simms Asst Professor (F2) , A&S Chemistry"])], "directory line: \"Asst Professor\" read as assistant professor"),
 104: ("https://www.ceas.uc.edu/academics/departments/mechanical-materials-engineering/People/materials-science-faculty.html", Q % "Donglu Shi professor Materials Science and Engineering University of Cincinnati faculty' (uc.edu)",
      [("existence", EXIST, "supports_A", ["Materials Science & Engineering Faculty", "Donglu Shi , Professor (F2)"])], ""),
 779: ("https://www.colorado.edu/mechanical/rong-long", Q % "Rong Long associate professor mechanical engineering CU Boulder soft materials' (colorado.edu)",
      [("existence", EXIST, "supports_A", ["Rong Long Associate Professor Lyall Faculty Fellow Mechanics of Materials"])], ""),
 850: ("https://www.chem.fsu.edu/person/dr-joseph-b-schlenoff/", Q % "Joseph Schlenoff Robert O. Lawton Distinguished Research Professor Chemistry Florida State University' (fsu.edu)",
      [("existence", EXIST, "supports_A", ["Dr. Joseph B. Schlenoff Distinguished Scholar Chair Professor in Chemistry, Robert O. Lawton Professor, and Leo Mandelkern Professor of Polymer Science"])],
      "page title is Professor in Chemistry; the row's role is research_professor and its role_as_published says Distinguished Research Professor (follow-up, not edited)"),
 882: ("https://www.chem.uci.edu/people/zhibin-guan", Q % "Zhibin Guan professor chemistry UC Irvine polymers faculty' (uci.edu)",
      [("existence", EXIST, "supports_A", ["Zhibin Guan", "Professor", "Position: Faculty"])], ""),
 925: ("https://artsandsciences.fsu.edu/article/faculty-spotlight-sachin-shanbhag", Q % "Sachin Shanbhag professor Department of Scientific Computing Florida State University polymers' (fsu.edu)",
      [("existence", EXIST, "supports_B", ["Sachin Shanbhag is a professor in Florida State University’s Department of Scientific Computing"]),
       ("scope", "Gate B: person-level polymer research stated", "supports_B", ["My research lies at the intersection of computational modeling and soft materials, particularly polymers."])],
      "college news article dated 2024-03-07, not a department page: the department page's text did not render"),
 1132: ("https://arts-sciences.buffalo.edu/chemistry/faculty/faculty-directory/rzayev.html", HELD,
      [("existence", EXIST, "supports_A", ["Javid Rzayev PhD Department Chair Professor Department of Chemistry College of Arts and Sciences"])], ""),
 1199: ("https://www.engr.colostate.edu/bce/people/david-wang/", HELD,
      [("existence", EXIST, "supports_A", ["David Wang Professor, Chemical & Biological Engineering"]),
       ("scope", "Gate B: person-level polymer research stated", "supports_B", ["Dr. Wang’s group has worked on the self-assembly of block copolymers under nano-confinement or directed by external fields"])],
      "the page styles the person David Wang; the existing evidence row for this page (EVD-283152) already accepted it for this record"),
}
# A second page for a row whose primary page does not state the recorded title. The institution's own dated news item (V-22 wants own_site for an existence claim); supports_B.
EXTRA = {
 850: ("https://news.fsu.edu/news/university-news/2025/07/11/six-fsu-faculty-named-to-academy-of-science-engineering-and-medicine-of-florida/",
       Q % "Joseph Schlenoff Robert O. Lawton Distinguished Research Professor Chemistry Florida State University' (fsu.edu)",
       [("existence", "title as published (Robert O. Lawton Distinguished Research Professor of Chemistry and Biochemistry), the title the row records; dated 2025-07-11", "supports_B", ["Schlenoff, a Robert O. Lawton Distinguished Research Professor of Chemistry and Biochemistry"])], "", "own_site"),
}
# Identifier-free page exists but does not state the same facts, so the identifier URL is blanked (old evidence stays).
BLANK = {
 51: "the listing gives an endowed professorship and names PERSON-000052 as director; no identifier-free page states the interim director role the row records (old identifier URLs removed; the listing stays in sources)",
 1037: "the one identifier-free page found has a title field (Associate Professor) that conflicts with its overview sentence (assistant professor); it cannot settle the recorded rank",
 54: "listing states name and rank but not the specialty the old evidence row cited from the identifier URL",
 75: "listing and emeritus page style him Distinguished Professor Emeritus; the row says professor",
 1304: "the only identifier-free utah.edu page found is a seminar-series line (a list item, not a directory or profile entry); the page that does state her rank is the BME profile already in sources",
 359: "the only identifier-free department page lists him under In Memoriam; no page states a current rank",
}
# A blanked row whose only source was the identifier URL: keep the identifier-free page found as a plain source (no evidence row,
# no role claim) so `sources` is not empty. Needs the controller's decision: the ruling's hold branch would keep the identifier URL.
KEEP_SOURCE = {1037: "https://www.latech.edu/directory/andrew-j-peters.php"}
pid = lambda n: "PERSON-%06d" % n

def main(write=True):
    people_path, ev_path = REPO + "/data/people.csv", REPO + "/data/evidence_people.csv"
    people = read_csv(open(people_path, "rb").read().decode()); fields = list(people[0])
    ev = read_csv(open(ev_path, "rb").read().decode())
    frame = [r for r in people if any(has_id(r[c]) for c in URL_COLS)]
    if not frame:
        print("nothing to do: no identifier URLs on people rows"); return
    unplanned = {int(r["person_id"][7:]) for r in frame} - set(PLAN) - set(BLANK)
    if unplanned: sys.exit(f"frame rows without a plan: {sorted(unplanned)}")
    if set(PLAN) & set(BLANK): sys.exit("a row is both replaced and blanked")
    man = {}
    new_ev, witness = [], []
    nxt = EVD_LO
    for r in frame:
        n = int(r["person_id"][7:])
        old_ev = [e["evidence_id"] for e in ev if e["record_id"] == r["person_id"] and any(has_id(e[c]) for c in e)]
        if n in BLANK:
            for c in ("public_profile_url", "lab_url"):
                if has_id(r[c]): r[c] = ""
            r["sources"] = ";".join(s for s in sources_list(r["sources"]) if not has_id(s))
            if not r["sources"] and n in KEEP_SOURCE: r["sources"] = KEEP_SOURCE[n]
            if not r["sources"]: sys.exit(f"{r['person_id']}: blanking would empty sources; hold instead")
            continue
        for k, page in enumerate([PLAN[n]] + ([EXTRA[n]] if n in EXTRA else [])):
            url, route, claims, caveat = page[:4]; cls = page[4] if len(page) > 4 else "own_site"
            if url not in manifest_now(man): fetch.fetch(url, route); man.clear()
            sha = manifest_now(man)[url]
            text = page_text(sha)
            for ct, detail, eff, segs in claims:
                if not in_order(text, segs): sys.exit(f"{r['person_id']}: quote not in stored page {sha[:12]}: {segs}")
            if k == 0:  # the primary page replaces the identifier URLs; an extra page is only appended to sources
                for c in ("public_profile_url", "lab_url"):
                    if has_id(r[c]): r[c] = url
                out = []
                for s in sources_list(r["sources"]):
                    s = url if has_id(s) else s
                    if s not in out: out.append(s)
                r["sources"] = ";".join(out)
            if url not in sources_list(r["sources"]): r["sources"] += ";" + url  # a page the new evidence rows cite is a source of the row
            r["last_verified"] = TODAY
            for ct, detail, eff, segs in claims:
                eid = "EVD-%06d" % nxt; nxt += 1
                ans = f"; answers {', '.join(old_ev)} (unedited; they cite an identifier URL)" if old_ev else ""
                note = (f"Raw words in order (segments separated by …; contact details omitted): {SEP.join(segs)}; replaces an identifier URL on the people row (owner rulings 2026-11-18 items 1 and 1b){ans}; "
                        f"page located by: {route}; stored page sha256 {sha[:12]}" + (f"; caveat: {caveat}" if caveat else ""))
                new_ev.append({"evidence_id": eid, "record_table": "people", "record_id": r["person_id"], "claim_type": ct,
                               "claim_detail": detail, "source_class": cls, "source_ref": url, "observed_date": TODAY,
                               "tier_effect": eff, "created_by": CREATED_BY, "notes": note})
                witness.append({"evidence_id": eid, "person_id": r["person_id"], "url": url, "sha256": sha, "segments": SEP.join(segs)})
    if nxt - 1 > EVD_HI: sys.exit("evidence block exhausted")
    if write:
        # Order matters for recovery: derived witness files, then evidence, then people LAST. A failure before the
        # people write leaves the frame in place, so a retry recomputes everything and skips evidence already appended.
        with open(HERE / "witness.csv", "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=["evidence_id", "person_id", "url", "sha256", "segments"], lineterminator="\n")
            w.writeheader(); w.writerows(witness)
        (HERE / "manifest.csv").write_bytes(redact(open(PERSIST + "manifest.csv", encoding="utf-8").read()).replace("\r\n", "\n").encode())
        have = {e["evidence_id"]: e for e in ev}
        for e in new_ev:
            if e["evidence_id"] in have and have[e["evidence_id"]] != e: sys.exit(f"{e['evidence_id']} exists with different content")
        todo = [e for e in new_ev if e["evidence_id"] not in have]
        if todo: append_sorted(ev_path, todo, "evidence_id")
        buf = io.StringIO(); w = csv.DictWriter(buf, fieldnames=fields, lineterminator="\n"); w.writeheader(); w.writerows(people)
        tmp = people_path + ".tmp"; open(tmp, "wb").write(buf.getvalue().encode()); os.replace(tmp, people_path)
    print(f"frame rows {len(frame)}: replaced {len(frame) - len(BLANK)}, blanked {len(BLANK)}; evidence rows appended {len(new_ev)}")

def manifest_now(cache):
    if not cache: cache.update(manifest())
    return cache

if __name__ == "__main__":
    main()

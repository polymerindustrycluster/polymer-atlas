#!/usr/bin/env python3
"""Owner rulings 2026-11-18b item 3 (widened V-62: ?unid= and researchdirectory.uc.edu/p/) and item 6 (people status).

Per frame row (found by the V-62 test, never by a stored URL): REPLACE the identifier URL with an identifier-free page that
states the same facts (one new evidence row, quote verified in order in the stored page), or keep the page as a plain source
with the identifier URL blanked (no evidence row). Changes only public_profile_url, lab_url, sources and last_verified on frame
rows; appends evidence EVD-396900..396949 only; never edits an evidence row. Adds the blank columns status, status_date to
people.csv (every row blank: not recorded). Idempotent: a second run finds no frame rows and no missing columns.
"""
import csv, io, os, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE)); sys.path.insert(0, str(HERE.parent.parent / "scripts"))
from common import *
from shard_io import append_sorted
import fetch

HELD = "held record: people.csv sources of the same row"
Q = "search I ran 2026-11-18: WebSearch '%s'"
EXIST = "name, title and institution as published; people row role unchanged"
CE = "https://www.ceas.uc.edu/academics/departments/chemical-environmental-engineering/people.html"
# pid -> (url, how the url became fetchable (rule 14), [(claim_type, detail, tier_effect, [quote segments])], caveat)
PLAN = {
 941: ("https://bioscience.utah.edu/faculty/kramer/index.php", HELD,
       [("existence", EXIST, "supports_A", ["Jessica Kramer Associate Professor of Biomedical Engineering and Adjunct Associate Professor of Molecular Pharmaceutics and of Chemistry"])], ""),
 1303: ("https://www.mse.utah.edu/faculty/", HELD,
        [("existence", EXIST, "supports_A", ["Sijia Huang Assistant Professor"])], "faculty-list entry; contact details on the page are omitted from the quote"),
 1304: ("https://kramerlab.bme.utah.edu/aboutkramer.html", Q % "Jessica Kramer Stratton associate professor biomedical engineering University of Utah",
        [("existence", EXIST, "supports_A", ["Dr. Jessica R. Kramer Stratton, Ph.D. Associate Professor", "joined the Department of Bioengineering at the University of Utah in January, 2017"])],
        "the lab's own page for this person (kramerlab.bme.utah.edu); PERSON-000941 carries the same person under the name Jessica R. Kramer (same account), a possible duplicate (follow-up, no merge here)"),
 2009: ("https://www.ceas.uc.edu/academics/departments/biomedical-engineering/people.html", Q % "John Martin biomedical engineering faculty University of Cincinnati organoselenium polymer regenerative orthopedic' with allowed_domains uc.edu",
        [("existence", EXIST, "supports_A", ["John Robert Martin , Asst Professor (F2)"])], "department faculty-list entry"),
 2010: (CE, HELD + " (PERSON-000104's search; the page is a source on PERSON-002112)",
        [("existence", EXIST, "supports_A", ["Jonathan David Nickels , Assoc Professor"])], "department faculty-list entry"),
 2111: ("https://www.artsci.uc.edu/natural-sciences/chemistry/faculty-and-staff-directory.html", HELD,
        [("existence", EXIST, "supports_A", ["Jianbing Jiang Assoc Professor , A&S Chemistry"])], "directory line"),
 2112: (CE, HELD,
        [("existence", EXIST, "supports_A", ["Yoonjee Park , Professor (F2)"])], "department faculty-list entry"),
}
# Identifier URL removed, no evidence row: the row's remaining sources (or a plain source) carry it.
BLANK = {
 104: "the identifier-free page (the MSE faculty list) is already the row's public_profile_url and was evidenced today (EVD-396116); only the identifier source is dropped; two other sources remain",
 2011: "the department page lists him as department head and chair holder (George Rieveschl Eminent Scholar), not as Professor; the recorded role is Professor of Chemical Engineering, so no page states it and no evidence row is added; the page is kept as a plain source so `sources` is not empty",
}
KEEP_SOURCE = {2011: CE}
pid = lambda n: "PERSON-%06d" % n

def main(write=True):
    people_path, ev_path = REPO + "/data/people.csv", REPO + "/data/evidence_people.csv"
    people = read_csv(open(people_path, "rb").read().decode()); fields = list(people[0])
    ev = read_csv(open(ev_path, "rb").read().decode())
    frame = [r for r in people if any(has_account_identifier(r[c]) for c in URL_COLS)]
    need_cols = [c for c in NEW_COLS if c not in fields]
    if not frame and not need_cols:
        print("nothing to do: no identifier URLs on people rows, status columns present"); return
    unplanned = {int(r["person_id"][7:]) for r in frame} - set(PLAN) - set(BLANK)
    if unplanned: sys.exit(f"frame rows without a plan: {sorted(unplanned)}")
    man = {}
    new_ev, witness = [], []
    nxt = EVD_LO
    for r in frame:
        n = int(r["person_id"][7:])
        old_ev = [e["evidence_id"] for e in ev if e["record_id"] == r["person_id"] and any(has_account_identifier(e[c]) for c in e)]
        if n in BLANK:
            for c in ("public_profile_url", "lab_url"):
                if has_account_identifier(r[c]): r[c] = ""
            r["sources"] = ";".join(s for s in sources_list(r["sources"]) if not has_account_identifier(s))
            if n in KEEP_SOURCE and KEEP_SOURCE[n] not in sources_list(r["sources"]):
                if KEEP_SOURCE[n] not in manifest_now(man): fetch.fetch(KEEP_SOURCE[n], HELD); man.clear()
                r["sources"] = ";".join(sources_list(r["sources"]) + [KEEP_SOURCE[n]])
            if not r["sources"]: sys.exit(f"{r['person_id']}: blanking would empty sources; hold instead")
            continue
        url, route, claims, caveat = PLAN[n]
        if url not in manifest_now(man): fetch.fetch(url, route); man.clear()
        sha = manifest_now(man)[url]; text = page_text(sha)
        for ct, detail, eff, segs in claims:
            if not in_order(text, segs): sys.exit(f"{r['person_id']}: quote not in stored page {sha[:12]}: {segs}")
        for c in ("public_profile_url", "lab_url"):
            if has_account_identifier(r[c]): r[c] = url
        out = []
        for s in sources_list(r["sources"]):
            s = url if has_account_identifier(s) else s
            if s not in out: out.append(s)
        if url not in out: out.append(url)
        r["sources"] = ";".join(out)
        r["last_verified"] = TODAY
        for ct, detail, eff, segs in claims:
            eid = "EVD-%06d" % nxt; nxt += 1
            ans = f"; answers {', '.join(old_ev)} (unedited; they cite an identifier URL)" if old_ev else ""
            note = (f"Raw words in order (segments separated by …; contact details omitted): {SEP.join(segs)}; replaces an identifier URL on the people row (owner rulings 2026-11-18b item 3, following 2026-11-18 items 1 and 1b){ans}; "
                    f"page located by: {route}; stored page sha256 {sha[:12]}" + (f"; caveat: {caveat}" if caveat else ""))
            new_ev.append({"evidence_id": eid, "record_table": "people", "record_id": r["person_id"], "claim_type": ct,
                           "claim_detail": detail, "source_class": "own_site", "source_ref": url, "observed_date": TODAY,
                           "tier_effect": eff, "created_by": CREATED_BY, "notes": note})
            witness.append({"evidence_id": eid, "person_id": r["person_id"], "url": url, "sha256": sha, "segments": SEP.join(segs)})
    if nxt - 1 > EVD_HI: sys.exit("evidence block exhausted")
    if write:
        # Recovery order: witness files, then evidence, then people LAST (a failure before that leaves the frame, so a retry recomputes).
        with open(HERE / "witness.csv", "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=["evidence_id", "person_id", "url", "sha256", "segments"], lineterminator="\n")
            w.writeheader(); w.writerows(witness)
        (HERE / "manifest.csv").write_bytes(open(PERSIST + "manifest.csv", "rb").read().replace(b"\r\n", b"\n"))
        have = {e["evidence_id"]: e for e in ev}
        for e in new_ev:
            if e["evidence_id"] in have and have[e["evidence_id"]] != e: sys.exit(f"{e['evidence_id']} exists with different content")
        todo = [e for e in new_ev if e["evidence_id"] not in have]
        if todo: append_sorted(ev_path, todo, "evidence_id")
        out_fields = fields + need_cols
        for r in people:
            for c in need_cols: r[c] = ""
        buf = io.StringIO(); w = csv.DictWriter(buf, fieldnames=out_fields, lineterminator="\n"); w.writeheader(); w.writerows(people)
        tmp = people_path + ".tmp"; open(tmp, "wb").write(buf.getvalue().encode()); os.replace(tmp, people_path)
    print(f"frame rows {len(frame)}: replaced {len(frame) - len(BLANK)}, identifier removed without evidence {len(BLANK)}; evidence rows appended {len(new_ev)}; status columns added {need_cols}")

def manifest_now(cache):
    if not cache: cache.update(manifest())
    return cache

if __name__ == "__main__":
    main()

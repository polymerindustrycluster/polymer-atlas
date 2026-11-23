#!/usr/bin/env python3
"""Turn packet.csv into the data edits of the size PR (integrator step; the packet itself changes nothing).
  python3 build_apply.py --data-dir data            writes edits.csv + evidence_rows.csv (checks every cell against the base)
  python3 build_apply.py --data-dir data --append   also appends the evidence rows to data/evidence_sites_<TAG>.csv
The site edits are applied with scripts/apply_p1_crm_scrub.py --packet-dir <this folder> (the 2026-11-02 band pass's route).
Convention followed: tasks/bands-apply-2026-11-02 (band cell + `BAND-SOURCE:` notes append) and tasks/size-band-evidence-2026-11-03
(one `size_band` evidence row per fill, government_filing, supports_B). Deviations: no headcount anywhere (R13 / SCHEMA 4.4), and the
date is the filing's source date (SCHEMA R13 v1.19.3), not the submission date or the pass date."""
import argparse, csv, hashlib, re, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent; ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "tasks/census-gap-people-2026-11-03"))
from build_integration import append_rows  # noqa: E402
csv.field_size_limit(10**9)
EVD_FIRST, EVD_LAST = 481000, 481199   # reserved for this PR by the controller
IDMAP = HERE / "evidence_id_map.csv"   # site -> id as first published (a55f7d93); an id is never reused or renumbered: a site later held leaves a gap
BY = "claude-code pic18-size-bands-2026-11-22"
VOCAB = {"1-9", "10-49", "50-99", "100-249", "250-499", "500-999", "1000-4999", "5000+"}
rd = lambda p: list(csv.DictReader(open(p, newline="", encoding="utf-8")))
sha = lambda s: hashlib.sha256(s.encode("utf-8")).hexdigest()

def label(p):
    loc = p["row_locator"].split("|"); rid = loc[2].split("=", 1)[1]; row = loc[1].split("=", 1)[1]; fn = p["source_file"].rsplit("/", 1)[1]
    if p["source"] == "osha_ita":
        return (f"OSHA ITA Form 300A CY{p['filing_year']}, source date {p['source_date']}", "annual average employees",
                f"OSHA ITA Form 300A CY{p['filing_year']}, record id {rid}, {fn} row {row} (https://www.osha.gov/Establishment-Specific-Injury-and-Illness-Data)",
                f"OSHA ITA Form 300A CY{p['filing_year']}, source date {p['source_date']} (government_filing; band only, not a headcount).")
    if p["source"] == "osha_inspection":
        return (f"OSHA inspection {rid} opened {p['source_date']}", "nr_in_estab", f"OSHA inspection activity_nr {rid}, OSHA_inspection.zip {loc[0]} row {row} (no URL cited: SCHEMA 4.22 archive-at-capture)",
                f"OSHA inspection record, opened {p['source_date']} (government_filing; band only, not a headcount).")
    form = "5500-SF" if "_sf_" in fn.lower() else "5500"
    return (f"Form {form} plan year {p['filing_year']}, ACK_ID {rid}", "active participants", f"DOL EFAST2 Form {form}, sponsor {p['filing_name']}, PY{p['filing_year']}, ACK_ID {rid}",
            f"Form 5500 plan year {p['filing_year']} active participants, plan year end {p['source_date']} (government_filing; plan count, not a headcount; single-establishment org).")

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--data-dir", required=True); ap.add_argument("--append", action="store_true"); a = ap.parse_args()
    data = Path(a.data_dir).resolve(); packet = rd(HERE / "packet.csv")
    where = {}
    for f in sorted(data.glob("sites_*.csv")):
        for r in rd(f): where[r["site_id"]] = (f.name, f.stem.split("_", 1)[1], r)
    used = {r["evidence_id"] for f in data.glob("evidence*.csv") for r in rd(f)} | {r["evidence_id"] for r in rd(data / "archive_links.csv") if "evidence_id" in r}
    idmap = {r["site_id"]: r["evidence_id"] for r in rd(IDMAP)}
    rowref = {r["site_id"]: r["packet_row_646545f6"] for r in rd(IDMAP) if r["packet_row_646545f6"]}   # evidence notes keep the packet.csv row number of head 646545f6, so the 50 kept rows stay byte-identical after the Form 5500 withdrawal
    nxt = max(int(v[4:]) for v in idmap.values()) + 1
    edits, ev = [], []
    for n, p in enumerate(packet):
        sid = p["site_id"]; fname, tag, r = where[sid]
        assert r["employee_band_site"] in ("", "unknown") or (a.append and r["employee_band_site"] == p["band"]), f"{sid}: band cell holds {r['employee_band_site']!r} on the base"   # `unknown` is the schema placeholder for no band (SCHEMA 4.5), as in the frame definition
        assert p["band"] in VOCAB and r["site_id"] == sid and r["operating_status"] == "active", sid
        lab, measure, ref, note = label(p); eid = idmap.get(sid)
        if eid is None: eid = f"EVD-{nxt:06d}"; nxt += 1
        assert EVD_FIRST <= int(eid[4:]) <= EVD_LAST and eid not in used, f"{eid} not unique tree-wide"
        edits.append(dict(file=fname, row_id=sid, column="employee_band_site", old_sha256=sha(r["employee_band_site"]), new_value=p["band"], edit_class=f"BAND_SITE_{p['source'].upper()}", rationale=f"R13 source {p['r13_source']} {lab}; name match {p['name_match']}; packet.csv row {rowref.get(sid, n + 2)}"))
        notes = r["notes"]
        if a.append: notes = notes.split(" BAND-SOURCE: ")[0] if " BAND-SOURCE: " in notes else notes   # already applied: recompute the pre-edit notes
        edits.append(dict(file=fname, row_id=sid, column="notes", old_sha256=sha(notes), new_value=(notes.rstrip() + " " if notes.strip() else "") + f"BAND-SOURCE: employee_band_site={p['band']} from {note}", edit_class="BAND_SOURCE_NOTE", rationale="band provenance (source + date)"))
        ev.append(dict(evidence_id=eid, record_table="sites", record_id=sid, claim_type="size_band", claim_detail=f"employee_band_site={p['band']}: {lab}: {measure} in {p['band']} (band only, not a headcount)",
                       source_class="government_filing", source_ref=ref, observed_date=p["source_date"], tier_effect="supports_B", created_by=BY,
                       notes=f"packet tasks/pic18-size-sprint-2026-11-22/packet.csv row {rowref.get(sid, n + 2)}; {p['name_match']} name match at an equal street; fills a blank or `unknown` cell only; shard {tag}", address_role=""))
    assert len({e["evidence_id"] for e in ev}) == len(ev)
    cols = ["file", "row_id", "column", "old_sha256", "new_value", "edit_class", "rationale"]
    if not a.append:
        with open(HERE / "edits.csv", "w", newline="", encoding="utf-8") as f: w = csv.DictWriter(f, cols, lineterminator="\n"); w.writeheader(); w.writerows(edits)
    ecols = list(ev[0])
    with open(HERE / "evidence_rows.csv", "w", newline="", encoding="utf-8") as f: w = csv.DictWriter(f, ecols, lineterminator="\n"); w.writeheader(); w.writerows(ev)
    gaps = sorted(set(idmap.values()) - {e["evidence_id"] for e in ev})
    print(f"{len(edits)} cell edits over {len(packet)} sites; {len(ev)} evidence rows {ev[0]['evidence_id']}..{ev[-1]['evidence_id']}; ids left as gaps (un-applied rows, never reused): {len(gaps)} {gaps}")
    if a.append:
        by = {}
        for e in ev: by.setdefault(f"evidence_sites_{where[e['record_id']][1]}.csv", []).append(e)
        for name, rows in by.items():
            assert (data / name).exists(), name
            append_rows(data / name, rows)
        print("evidence appended to", sorted(by))

if __name__ == "__main__": main()

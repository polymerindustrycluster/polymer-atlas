#!/usr/bin/env python3
"""Replay the packet from hashed snapshots and prove the two age/recency controls."""
import argparse
import io
import runpy
import subprocess
import sys
from collections import Counter
from pathlib import Path
from tempfile import TemporaryDirectory

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import build as B
import check_evidence_binding as gate

APPLY_BASE = "15183872d30f8974c80fe9df7bc06312cbccbefc"
SITE_SHARD = "data/sites_OH.csv"
EVIDENCE_SHARD = "data/evidence_sites_OH.csv"
LABEL = "codex " + HERE.name
CLAIMS = ("table", "record_id", "field", "verdict", "evidence_id")

prior = runpy.run_path(str(HERE.parent / "p1-atlas8-corrections-2026-11-23/check.py"))
git, parse, require, unique, csv_bytes = (prior[k] for k in ("git", "parse", "require", "unique", "csv_bytes"))


def selftest():
    site = dict(site_id="SITE-test", org_id="ORG-test", street_address="1 Elm St")
    active = Counter({"ORG-test": 1})

    def filing(d, count, rid, kind="insp"):
        fields = dict(open_date=d, nr_in_estab=str(count), rid=rid, estab_name="Acme Plastics")
        if kind == "ita":
            fields.update(year_filing_for=d[:4], annual_average_employees=str(count),
                          establishment_name="Acme Plastics", company_name="", ein="", size="", submitted="")
        entry = dict(kind=kind, names=["Acme Plastics"], r=fields)
        return entry, "exact", "Acme Plastics"

    old = filing("2015-12-31", 20, "stale")
    ita = filing("2016-12-31", 20, "old", "ita")
    newer = filing("2024-01-01", 70, "new")
    boundary = filing("2016-11-23", 20, "boundary")

    def decide(ita_rows, insp_rows):
        return B.decide(site, dict(ita=ita_rows, insp=insp_rows), active, {}, {})

    result, losing = decide([], [old])
    if result[:2] != ("hold", "stale_over_10_years") or losing:
        raise AssertionError("planted 2015 filing was not rejected as stale")
    result, _ = decide([], [boundary])
    if result[0] != "fill":
        raise AssertionError("filing exactly on the cutoff was rejected")
    result, _ = decide([ita], [])
    if result[0] != "fill" or result[1]["band"] != "10-49":
        raise AssertionError("eligible baseline filing did not set its band")
    result, losing = decide([ita], [newer])
    if result[0] != "fill" or result[1]["band"] != "50-99" or losing != [(ita[0], newer[0])]:
        raise AssertionError("planted newer contradictory filing did not displace the old band")
    print("Controls PASS: 2015 filing held, cutoff accepted, newer adjacent band wins")


def application(packet, evidence):
    raw_sites = gate.rows(APPLY_BASE, "sites_*.csv")
    raw_orgs = gate.rows(APPLY_BASE, "organizations_*.csv") + gate.rows(APPLY_BASE, "ecosystem.csv")
    sites = unique(raw_sites, lambda r: r["site_id"], "held sites")
    orgs = unique(raw_orgs, lambda r: r["org_id"], "held owners")
    frame, n_owners, n_unknown = B.M.frame(orgs, raw_sites)
    frame_ids = {r["site_id"] for r in frame}
    require((n_owners, n_unknown, len(frame_ids)) == (794, 392, 404), "corrected-base frame differs")
    require(len(packet) == len({p["org_id"] for p in packet.values()}) == len(evidence) == 18
            and evidence.keys() == packet.keys() <= frame_ids, "packet keys differ from the unknown frame")
    require(Counter(p["source"] for p in packet.values()) == {"osha_ita": 12, "osha_inspection": 6}
            and sum(p["source_date"] < B.FIVE_YEARS for p in packet.values()) == 9, "filing counts differ")
    hashes = {name: digest for digest, name in
              (line.split("  ", 1) for line in (HERE / "INPUTS.sha256").read_text().splitlines())}
    idx = gate.Index(raw_sites, raw_orgs)
    used = unique(gate.rows(APPLY_BASE, "evidence_*.csv"), lambda r: r["evidence_id"], "held evidence")
    archive_ids = {r["evidence_id"] for r in gate.rows(APPLY_BASE, "archive_links.csv")}
    next_id = max(int(eid.split("-")[1]) for eid in used.keys() | archive_ids) + 1
    minted, claims, changes = [], [], {}
    for i, (sid, p) in enumerate(packet.items(), next_id):
        site, source = sites[sid], p["source"]
        kind = "ita" if source == "osha_ita" else "insp"
        label = B.SOURCES[kind]
        member, line, rid = p["row_locator"].split("|")
        date, band = p["source_date"], p["band"]
        require(site["org_id"] == p["org_id"] and site["_at"].startswith(SITE_SHARD + ":")
                and site["employee_band_site"] in ("", "unknown")
                and "BAND-SOURCE:" not in site["notes"], f"{sid}: held site or provenance changed")
        require(B.CUTOFF <= date <= "2026-11-23" and date[:4] == p["filing_year"]
                and (kind != "ita" or date == p["filing_year"] + "-12-31")
                and hashes[p["source_file"]] == p["file_sha256"], f"{sid}: filing date or hash differs")
        ev = evidence[sid]
        require(ev["evidence_id"] == "" and ev["record_table"] == "sites" and ev["created_by"] == LABEL
                and ev["claim_type"] == "size_band" and ev["observed_date"] == date
                and ev["source_class"] == "government_filing" and ev["tier_effect"] == "supports_B"
                and ev["source_ref"] == f"{label}; {p['source_file']}!{member}@{line.removeprefix('row=')}; {rid}"
                and ev["claim_detail"].startswith(f"employee_band_site={band}; {label}, filing year {p['filing_year']}; quote: "),
                f"{sid}: wrong evidence contract")
        require(p["band_source_note"] == f"BAND-SOURCE: employee_band_site={band} from {label}, {date} (government_filing).",
                f"{sid}: source note differs")
        eid = f"EVD-{i:06d}"
        ev = dict(ev, evidence_id=eid)
        verdict, reason, _ = gate.judge(ev, idx)
        require(verdict == "PASS", f"{sid}: binding on corrected base {verdict} {reason}")
        minted.append(ev)
        claims.append(dict(zip(CLAIMS, ("sites", sid, "employee_band_site", "corrected", eid))))
        notes = " ".join(part for part in (site["notes"].rstrip(), p["band_source_note"]) if part)
        changes[sid] = dict(employee_band_site=band, notes=notes)

    _, after_owners, after_unknown = B.M.frame(orgs, [dict(s, **changes.get(s["site_id"], {})) for s in raw_sites])
    require((after_owners, after_unknown) == (794, 374), "applied frame differs")
    old_sites = git("show", f"{APPLY_BASE}:{SITE_SHARD}")
    old_evidence = git("show", f"{APPLY_BASE}:{EVIDENCE_SHARD}")
    lines = list(io.StringIO(old_sites.decode(), newline=""))
    rows = parse(old_sites)
    chunks, end = [lines[0].encode()], 1
    for row in rows:
        start, end = end, rows.line_num
        change = changes.get(row["site_id"])
        chunks.append(csv_bytes([dict(row, **change)], rows.fieldnames, with_header=False)
                      if change else "".join(lines[start:end]).encode())
    return {
        SITE_SHARD: b"".join(chunks),
        EVIDENCE_SHARD: old_evidence + csv_bytes(minted, parse(old_evidence).fieldnames, with_header=False),
        str((HERE / "CLAIMS_CHECKED.csv").relative_to(B.ROOT)): csv_bytes(claims, CLAIMS),
    }


def check_application(head):
    def head_bytes(name):
        path = (HERE / name).relative_to(B.ROOT)
        return git("show", f"{head}:{path}")

    packet = unique(parse(head_bytes("packet.csv")), lambda r: r["site_id"], "packet")
    evidence = unique(parse(head_bytes("evidence_rows.csv")), lambda r: r["record_id"], "packet evidence")
    expected = application(packet, evidence)
    paths = set(git("diff", "--name-only", APPLY_BASE, head, "--", "data/").decode().splitlines())
    require(paths == {SITE_SHARD, EVIDENCE_SHARD}, "unexpected edited data paths")
    for path, raw in expected.items():
        require(raw == git("show", f"{head}:{path}"), f"{path}: application differs from the sealed packet")
    print("Application PASS: 18 PIC-18 site bands, 18 dated notes, 18 tier-B witnesses, 18 claims.")
    print("PIC-18 owners with unknown size: 392 to 374 of 794.")



def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--store", type=Path, default=B.DEFAULT_STORE)
    parser.add_argument("--selftest", action="store_true", help="run only the planted controls")
    parser.add_argument("--at", help="also check the full application at this commit SHA")
    args = parser.parse_args()
    if args.at:
        manifest_path = (HERE / "INPUTS.sha256").relative_to(B.ROOT)
        require(git("show", f"{args.at}:{manifest_path}") == (HERE / "INPUTS.sha256").read_bytes(),
                "the checked head's manifest differs from the replay manifest")
    selftest()
    if args.selftest:
        return
    with TemporaryDirectory(prefix="atlas-size-replay-") as tmp:
        work = Path(tmp)
        data = work / "tree"
        data.mkdir()
        with subprocess.Popen(["git", "archive", B.BASE, "data"], cwd=B.ROOT, stdout=subprocess.PIPE) as archive:
            subprocess.run(["tar", "-xf", "-", "-C", str(data)], stdin=archive.stdout, check=True)
            if archive.wait():
                raise RuntimeError(f"could not export pinned data at {B.BASE}")
        subprocess.run([sys.executable, "-I", str(HERE / "build.py"), "--store", str(args.store),
                        "--data-dir", str(data / "data"), "--out", str(work / "replay")], check=True)
        for name in B.OUTPUTS:
            path = HERE / name
            sealed = git("show", f"{args.at}:{path.relative_to(B.ROOT)}") if args.at else path.read_bytes()
            if sealed != (work / "replay" / name).read_bytes():
                raise AssertionError(f"{name} differs from replay")
    print(f"Replay PASS: {len(B.OUTPUTS)} artifacts match byte-for-byte")
    if args.at:
        check_application(args.at)


if __name__ == "__main__":
    main()

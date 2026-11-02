#!/usr/bin/env python3
"""Turn the PIC-12 capability change sets (tasks/integration-ready-2026-11-01/,
commit dfde7da) into a hash-checked cell-edit packet plus an evidence append,
re-checked against a given data tree.

Scope: capability tag columns only. Site processes / materials / markets_served,
the site CERT-SITE notes append, and organization processes / materials /
markets_served / certifications. Employee bands (band_updates.csv) are NOT in
this pass.

    python3 tasks/capability-apply-2026-11-02/build_edits.py --data-dir <pre-pass data dir>
        -> edits.csv (for scripts/apply_p1_crm_scrub.py --packet-dir), evidence_append.csv, holds.csv
    python3 tasks/capability-apply-2026-11-02/build_edits.py --data-dir data --append-evidence [--i-am-the-integrator]
        -> appends evidence_append.csv to <data-dir>/evidence.csv (byte-preserving append)

Checks per edit: the record exists in the named shard, and the current cell
equals the change set's `current_*` value (otherwise the field is held as
drift). An evidence row is kept only if, after the edits, the record carries the
claimed value: in the named column, or for a site certification, in the
CERT-SITE note being appended. Evidence IDs are allocated above the tree-wide
EVD maximum of --data-dir, never filling a gap.
"""
import argparse, csv, hashlib, io, re, sys
from pathlib import Path

csv.field_size_limit(10 ** 9)
ROOT = Path(__file__).resolve().parents[2]
SETS = ROOT / "tasks" / "integration-ready-2026-11-01"
OUT = Path(__file__).resolve().parent
EDIT_COLS = ["file", "row_id", "column", "old_sha256", "new_value", "edit_class", "rationale"]
HOLD_COLS = ["record_id", "file", "column", "reason"]
SITE_F = ("processes", "materials", "markets_served")
ORG_F = ("processes", "materials", "markets_served", "certifications")


def sha(s):
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def read(p):
    with open(p, newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def toks(s):
    return {t.strip() for t in (s or "").split(";") if t.strip()}


def build(data, SETS=SETS):
    shards = {}
    def rec(fname, rid):
        if fname not in shards:
            rows = read(data / fname)
            key = next(iter(rows[0])) if rows else None
            shards[fname] = {r[key]: r for r in rows}
        return shards[fname].get(rid)

    edits, holds, final = [], [], {}   # final[(table, rid)] = {col: value}
    for s in read(SETS / "capability_site_updates.csv"):
        if s["apply_status"] != "APPLY":
            continue
        r = rec(s["shard"], s["site_id"])
        if r is None:
            holds.append({"record_id": s["site_id"], "file": s["shard"], "column": "*", "reason": "site not in shard"}); continue
        fin = final.setdefault(("sites", s["site_id"]), {f: r[f] for f in SITE_F} | {"notes": r["notes"]})
        for f in SITE_F:
            if s[f + "_status"] != "APPLY":
                continue
            if r[f] != s["current_" + f]:
                holds.append({"record_id": s["site_id"], "file": s["shard"], "column": f, "reason": "drift since change set"}); continue
            edits.append({"file": s["shard"], "row_id": s["site_id"], "column": f, "old_sha256": sha(r[f]),
                          "new_value": s["proposed_" + f], "edit_class": f"CAP_SITE_{f.upper()}",
                          "rationale": f"own-site disclosure, adds {s['new_' + f]} (packet rows {s['packet_row_refs'][:120]})"})
            fin[f] = s["proposed_" + f]
        if s["proposed_notes_append"]:
            new = (r["notes"].rstrip() + " " if r["notes"].strip() else "") + s["proposed_notes_append"]
            edits.append({"file": s["shard"], "row_id": s["site_id"], "column": "notes", "old_sha256": sha(r["notes"]),
                          "new_value": new, "edit_class": "CAP_SITE_CERT_NOTE",
                          "rationale": "site certification recorded in notes (sites carry no certifications column; R12 precedent)"})
            fin["notes"] = new
    for o in read(SETS / "capability_org_updates.csv"):
        if o["apply_status"] != "APPLY":
            continue
        r = rec(o["shard"], o["org_id"])
        if r is None:
            holds.append({"record_id": o["org_id"], "file": o["shard"], "column": "*", "reason": "org not in shard"}); continue
        fin = final.setdefault(("organizations", o["org_id"]), {f: r[f] for f in ORG_F})
        for f in ORG_F:
            if o[f + "_status"] != "APPLY":
                continue
            if r[f] != o["current_" + f]:
                holds.append({"record_id": o["org_id"], "file": o["shard"], "column": f, "reason": "drift since change set"}); continue
            edits.append({"file": o["shard"], "row_id": o["org_id"], "column": f, "old_sha256": sha(r[f]),
                          "new_value": o["proposed_" + f], "edit_class": f"CAP_ORG_{f.upper()}",
                          "rationale": f"own-site disclosure (org scope), adds {o['new_' + f]} (lanes {o['lanes']})"})
            fin[f] = o["proposed_" + f]

    # evidence: keep only rows whose claim the post-edit record carries
    ev_rows, dropped = [], 0
    for e in read(SETS / "evidence_rows.csv"):
        fin = final.get((e["record_table"], e["record_id"]))
        m = re.match(r"(sites|organizations)\.(\w+) includes (\S+)", e["claim_detail"])
        c = re.match(r"certification (\S+) held at this site", e["claim_detail"])
        ok = False
        if fin and m:
            ok = m.group(3) in toks(fin.get(m.group(2)))
        elif fin and c:
            ok = bool(re.search(r"CERT-SITE[^.]*\b" + re.escape(c.group(1)) + r"\b", fin.get("notes", "")))
        if ok:
            ev_rows.append(e)
        else:
            dropped += 1
    return edits, holds, ev_rows, dropped


def next_evd(data):
    mx = 0
    for r in read(data / "evidence.csv"):
        m = re.fullmatch(r"EVD-(\d+)", r["evidence_id"])
        if m:
            mx = max(mx, int(m.group(1)))
    return mx + 1


def write(p, cols, rows):
    with open(p, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=cols, lineterminator="\n", extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)


def append_evidence(data, OUT=OUT):
    path = data / "evidence.csv"
    raw = path.read_bytes()
    nl = b"\r\n" if b"\r\n" in raw else b"\n"
    if not raw.endswith(nl):
        sys.exit("evidence.csv does not end with a newline; refusing to append")
    hdr = next(csv.reader(io.StringIO(raw.decode("utf-8"))))
    rows = read(OUT / "evidence_append.csv")
    held = {r["evidence_id"] for r in read(path)}
    clash = [r["evidence_id"] for r in rows if r["evidence_id"] in held]
    if clash:
        sys.exit(f"{len(clash)} evidence_id(s) already held (e.g. {clash[0]}); rebuild against the current tree")
    if rows and int(rows[0]["evidence_id"][4:]) != next_evd(data):
        sys.exit("first evidence_id is not the tree-wide next free EVD id; rebuild against the current tree")
    buf = io.StringIO(newline="")
    w = csv.writer(buf, lineterminator=nl.decode())
    for r in rows:
        w.writerow([r[c] for c in hdr])
    path.write_bytes(raw + buf.getvalue().encode("utf-8"))
    print(f"appended {len(rows)} evidence rows {rows[0]['evidence_id']}..{rows[-1]['evidence_id']}" if rows else "nothing to append")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data-dir", required=True)
    ap.add_argument("--append-evidence", action="store_true")
    ap.add_argument("--i-am-the-integrator", action="store_true")
    ap.add_argument("--sets", default=str(SETS), help="integration-ready change-set directory (default: the PIC-12 sets)")
    ap.add_argument("--out", default=str(OUT), help="packet directory to write / append from (default: this folder)")
    a = ap.parse_args()
    sets, out = Path(a.sets).resolve(), Path(a.out).resolve()
    out.mkdir(parents=True, exist_ok=True)
    data = Path(a.data_dir).resolve()
    if a.append_evidence:
        if data == (ROOT / "data").resolve() and not a.i_am_the_integrator:
            sys.exit("appending to the real data/ is integrator work (AGENTS.md §2 rule 7); pass --i-am-the-integrator")
        return append_evidence(data, out)
    edits, holds, ev, dropped = build(data, sets)
    n = next_evd(data)
    for i, e in enumerate(ev):
        e["evidence_id"] = f"EVD-{n + i:06d}"
    write(out / "edits.csv", EDIT_COLS, edits)
    write(out / "holds.csv", HOLD_COLS, holds)
    write(out / "evidence_append.csv", list(read(sets / "evidence_rows.csv")[0].keys()), ev)
    recs = {(e["file"], e["row_id"]) for e in edits}
    print(f"edits {len(edits)} over {len(recs)} records "
          f"({sum(1 for f, _ in recs if f.startswith('sites_'))} site, {sum(1 for f, _ in recs if f.startswith('organizations_'))} org); "
          f"holds {len(holds)}; evidence kept {len(ev)} "
          f"({ev[0]['evidence_id'] if ev else '-'}..{ev[-1]['evidence_id'] if ev else '-'}), dropped {dropped}")


if __name__ == "__main__":
    main()

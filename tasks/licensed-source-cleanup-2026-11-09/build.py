#!/usr/bin/env python3
"""Licensed-source cleanup (2026-11-09): answer each evidence row that cites Plastics News or Rubber News with a new row
citing a public source for the same claim (AGENTS.md §5; SCHEMA §4.13 append-only: the old row stays, answered).

    python3 tasks/licensed-source-cleanup-2026-11-09/build.py --data-dir data [--apply --i-am-the-integrator]

Inputs: `licensed_rows.csv` (the 36 rows), `lanes/L1_out.csv`, `lanes/L2_out.csv`, `rawcheck.csv` (each lane quote
re-fetched raw, word-sequence match). A new row is minted only for FOUND / PARTIAL / CONTRADICTED with a raw-verified
quote from a non-licensed host. Its tier_effect is never stronger than the old row's, nor than the source class allows;
CONTRADICTED mints `contradicts`. The new row goes in the same evidence shard as the row it answers.
"""
import argparse, csv, io, re, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
DATE, BY = "2026-11-09", "claude-code licensed-source-cleanup-2026-11-09"
LICENSED = re.compile(r"plasticsnews\.com|rubbernews\.com|dnb\.com|zoominfo\.com|data-axle\.com|dataaxle\.com", re.I)
RANK = {"supports_C": 1, "supports_B": 2, "supports_A": 3}
# Integrator holds: the lane's own note says the quote does not bear on the claim at all.
HOLD = {"EVD-006228": "the quote only gives OMG srl's Italian location; nothing public states the parent link or names OMG Thermoforming Inc."}
CEIL = {"own_site": "supports_A", "government_filing": "supports_A", "press": "supports_B"}


def read(p):
    with open(p, newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def write(p, rows, header):
    eol = "\r\n" if b"\r\n" in p.read_bytes()[:4096] else "\n"
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=header, lineterminator=eol, extrasaction="ignore"); w.writeheader(); w.writerows(rows)
    p.write_bytes(buf.getvalue().encode("utf-8"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data-dir", required=True)
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--i-am-the-integrator", action="store_true")
    a = ap.parse_args()
    data = Path(a.data_dir).resolve()
    if a.apply and data == (HERE.parents[1] / "data").resolve() and not a.i_am_the_integrator:
        sys.exit("editing the real data/ is integrator work; pass --i-am-the-integrator")
    lane = {r["evidence_id"]: r for f in sorted(HERE.glob("lanes/L*_out.csv")) for r in read(f)}
    raw = {r["evidence_id"]: r["raw"] for r in read(HERE / "rawcheck.csv")}
    files = {f: read(f) for f in sorted(data.glob("evidence_*.csv"))}
    where = {e["evidence_id"]: f for f, rows in files.items() for e in rows}
    old = {e["evidence_id"]: e for rows in files.values() for e in rows}
    eid = max(int(k[4:]) for k in old if k[4:].isdigit()) + 1  # AGENTS §3: above the tree-wide maximum
    new, log = {}, []
    for r in read(HERE / "licensed_rows.csv"):
        oid = r["evidence_id"]
        L, o = lane.get(oid), old[oid]
        out, sc, url = (L or {}).get("outcome", "MISSING"), (L or {}).get("source_class", "").strip(), (L or {}).get("source_url", "").strip()
        why = [HOLD[oid]] if oid in HOLD else []
        if out not in ("FOUND", "PARTIAL", "CONTRADICTED"): why.append(f"lane outcome {out}")
        elif raw.get(oid) != "yes": why.append(f"quote not raw-verified ({raw.get(oid)})")
        elif LICENSED.search(url): why.append("replacement is itself a licensed source")
        elif sc not in CEIL: why.append(f"source_class {sc!r}")
        if why:
            log.append(f"HELD {oid} {o['record_id']} {o['claim_type']}: {'; '.join(why)}"); continue
        if out == "CONTRADICTED":
            te = "contradicts"
        else:
            te = min((o["tier_effect"], CEIL[sc]), key=lambda t: RANK.get(t, 0))  # never stronger than the old row or the class
        part = f" (states part of it: {L['note'][:120]})" if out == "PARTIAL" else ""
        new.setdefault(where[oid], []).append({
            "evidence_id": f"EVD-{eid:06d}", "record_table": o["record_table"], "record_id": o["record_id"], "claim_type": o["claim_type"],
            "claim_detail": f"{o['claim_detail'][:200]}{part}: \"{L['quote'].strip()}\"", "source_class": sc, "source_ref": url,
            "observed_date": DATE, "tier_effect": te, "created_by": BY,
            "notes": f"answers {oid}, which cites a licensed publication (AGENTS.md §5, lead only); public source; quote re-fetched raw; source dated {L.get('source_date') or 'n/a'}"})
        log.append(f"{out} {oid} -> EVD-{eid:06d} {o['record_id']} {o['claim_type']} [{sc}, {te}]")
        eid += 1
    print("\n".join(log)); print(f"new rows {sum(len(v) for v in new.values())}; held {sum(1 for l in log if l.startswith('HELD'))}")
    (HERE / "journal.txt").write_text("\n".join(log) + "\n", encoding="utf-8", newline="\n")
    if a.apply:
        for f, rows in new.items():
            write(f, files[f] + rows, next(csv.reader(open(f, encoding="utf-8"))))
        print("applied")


if __name__ == "__main__":
    main()

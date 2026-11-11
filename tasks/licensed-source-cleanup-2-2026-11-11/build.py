#!/usr/bin/env python3
"""Licensed-source cleanup, finish pass (2026-11-11): answer the 24 evidence rows the 2026-11-09 pass
(tasks/licensed-source-cleanup-2026-11-09/, PR #258) left held. Each held row cites Plastics News or Rubber News;
AGENTS.md §5 allows those as discovery leads only. Evidence is append-only (SCHEMA §4.13): the old row stays,
answered by a new row citing a public source for the same claim.

    python3 tasks/licensed-source-cleanup-2-2026-11-11/build.py --data-dir data [--apply --i-am-the-integrator]

Inputs: `answers.csv` — one row per held evidence row, produced by the integrator of record, who re-fetched
every source page first-hand on 2026-11-11 and took each quote verbatim from the fetched text (word sequence,
punctuation-insensitive). A new row is minted only for FOUND / PARTIAL / CONTRADICTED with a quote from a
non-licensed host. Its claim text is the quote alone (the first pass's codex rule: a new row claims only what
its quote states). Its tier_effect is `contradicts` for CONTRADICTED, else never stronger than the old row's,
nor than its source class allows. The new row goes in the same evidence shard as the row it answers.
EVD-004782 stays HELD (see answers.csv): no fetchable public text states the parent link.
"""
import argparse, csv, io, re, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
DATE, BY = "2026-11-11", "spaghetti licensed-source-cleanup-2-2026-11-11"
LICENSED = re.compile(r"plasticsnews\.com|rubbernews\.com|dnb\.com|zoominfo\.com|data-axle\.com|dataaxle\.com", re.I)
RANK = {"supports_C": 1, "supports_B": 2, "supports_A": 3}
CEIL = {"own_site": "supports_A", "government_filing": "supports_A", "press": "supports_B"}
HELD_24 = {  # the journal of PR #258: every row it left held; this pass must account for each exactly once
    "EVD-003872", "EVD-004990", "EVD-005038", "EVD-005290", "EVD-006293", "EVD-003209", "EVD-004298",
    "EVD-004781", "EVD-004782", "EVD-005085", "EVD-005086", "EVD-005390", "EVD-005908", "EVD-005909",
    "EVD-003996", "EVD-006179", "EVD-006232", "EVD-006219", "EVD-003199", "EVD-003200", "EVD-006226",
    "EVD-006227", "EVD-006228", "EVD-004058",
}


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
    answers = {r["evidence_id"]: r for r in read(HERE / "answers.csv")}
    assert set(answers) == HELD_24, f"answers.csv must cover exactly the 24 held rows; diff: {set(answers) ^ HELD_24}"
    files = {f: read(f) for f in sorted(data.glob("evidence_*.csv"))}
    where = {e["evidence_id"]: f for f, rows in files.items() for e in rows}
    old = {e["evidence_id"]: e for rows in files.values() for e in rows}
    eid = max(int(k[4:]) for k in old if k[4:].isdigit()) + 1  # AGENTS §3: above the tree-wide maximum
    order = [r["evidence_id"] for r in read(HERE.parents[1] / "tasks" / "licensed-source-cleanup-2026-11-09" / "licensed_rows.csv")
             if r["evidence_id"] in HELD_24]
    new, log = {}, []
    for oid in order:
        L, o = answers[oid], old[oid]
        out, sc, url = L["outcome"].strip(), L["source_class"].strip(), L["source_url"].strip()
        if out == "HELD":
            log.append(f"HELD {oid} {o['record_id']} {o['claim_type']}: {L['note']}"); continue
        assert out in ("FOUND", "PARTIAL", "CONTRADICTED"), (oid, out)
        assert sc in CEIL and not LICENSED.search(url), (oid, sc, url)
        assert 0 < len(L["quote"].split()) <= 25, (oid, "quote over 25 words")
        if out == "CONTRADICTED":
            te = "contradicts"
        else:
            te = min((o["tier_effect"], CEIL[sc]), key=lambda t: RANK.get(t, 0))  # never stronger than the old row or the class
        scope = "part of the claim answered" if out == "PARTIAL" else ("claim contradicted" if out == "CONTRADICTED" else "claim answered")
        new.setdefault(where[oid], []).append({
            "evidence_id": f"EVD-{eid:06d}", "record_table": o["record_table"], "record_id": o["record_id"], "claim_type": o["claim_type"],
            "claim_detail": f"{o['claim_type']} ({scope} for {oid}), as the public source states it: \"{L['quote'].strip()}\"", "source_class": sc, "source_ref": url,
            "observed_date": DATE, "tier_effect": te, "created_by": BY,
            "notes": f"answers {oid}, which cites a licensed publication (AGENTS.md §5, lead only); public source; quote re-fetched by the integrator 2026-11-11; source dated {L.get('source_date') or 'n/a'}. {L['note'].strip()}"})
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

#!/usr/bin/env python3
"""Build the refetch-pilot value fills: re-fetch each applied page through the binding gate's own fetcher, recompute
digest and offset from those bytes, and write the cells, evidence rows, proofs and trackers.

    python3 build.py            plan only: fetch, replay, print (writes nothing)
    python3 build.py --apply    write data/, the capture store and this folder's CSVs

Input is second_read.csv (rows with applied=yes). Nothing is written until every applied row replays.
"""
import argparse
import csv
import hashlib
import io
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
TASK = HERE.name
LABEL = f"claude-code {TASK}"
STORE = Path("/Volumes/johnpswan/work/GAC/polymer-atlas/atlas-store")
CAPTURES = STORE / "provenance" / TASK / "captures"
OBSERVED = "2026-11-24"
READER = "Codex (OpenAI), refetch pilot reader"  # the pilot's reading, p3-refetch-pilot-2026-11-24
sys.path.insert(0, str(ROOT / "scripts"))
import check_evidence_binding as gate  # noqa: E402

FIELD_HEAD = {"processes": "processes={v}; quote: {q}", "markets_served": "Markets served: {v}; quote: {q}"}
EVIDENCE_COLS = ("evidence_id,record_table,record_id,claim_type,claim_detail,source_class,source_ref,observed_date,"
                 "tier_effect,created_by,notes,address_role").split(",")


def git(*args):
    return subprocess.check_output(["git", "-C", str(ROOT), *args])


def base_ref():
    return git("merge-base", "HEAD", "origin/main").decode().strip()


def read_csv(path):
    with open(path, newline="") as f:
        return list(csv.DictReader(f))


def encode(rows, header, ending):
    stream = io.StringIO(newline="")
    w = csv.DictWriter(stream, header, lineterminator=ending)
    w.writeheader()
    w.writerows(rows)
    return stream.getvalue().encode()


def parse(blob):
    """(header, rows, line ending); refuses a file that does not round-trip, so only the filled cells can change."""
    ending = "\r\n" if b"\r\n" in blob else "\n"
    reader = csv.DictReader(io.StringIO(blob.decode(), newline=""))
    rows = list(reader)
    assert encode(rows, reader.fieldnames, ending) == blob, "base CSV does not round-trip"
    return reader.fieldnames, rows, ending


def vocabulary():
    s = (ROOT / "docs/SCHEMA.md").read_text()
    proc = s.split("### 3.1 Processes")[1].split("### 3.2 Materials")[0]
    market = s.split("### 3.3 Markets")[1].split("### 3.4 Certifications")[0]
    terms = lambda v: set(re.findall(r"`([a-z0-9_]+)`", v))
    regular, ring3 = proc.split("Ring 3 services", maxsplit=1)
    return {"processes": terms(regular), "markets_served": terms(market)}, terms(ring3) - {"processes_other_note"}


def locate(base, org_id):
    """(path, header, rows, ending, row) of the organization in the base tree."""
    for path in git("ls-tree", "--name-only", base, "data/").decode().split():
        if re.fullmatch(r"data/organizations_[A-Z]+\.csv", path):
            header, rows, ending = parse(git("show", f"{base}:{path}"))
            for r in rows:
                if r["org_id"] == org_id:
                    return path, header, rows, ending, r
    raise KeyError(org_id)


def applied():
    return [r for r in read_csv(HERE / "second_read.csv") if r["applied"] == "yes"]


def replay(r):
    """Fetch as the CI gate does; return (bytes, digest, offset). Fails unless the pilot quote occurs exactly once."""
    data = gate.fetch_url(r["url"])
    text = gate.capture_text(data)
    assert text.count(r["quote"]) == 1, f"{r['owner']} {r['value']}: quote occurs {text.count(r['quote'])} times"
    return data, hashlib.sha256(data).hexdigest(), text.index(r["quote"])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()
    base = base_ref()
    vocab, ring3 = vocabulary()
    rows = applied()
    greatest = max(int(e["evidence_id"].split("-")[1]) for p in git("ls-tree", "--name-only", base, "data/").decode().split()
                   if re.fullmatch(r"data/evidence_[A-Za-z_]+\.csv", p) for e in read_csv_blob(base, p))
    plan, cells = [], {}
    for n, r in enumerate(rows, start=1):
        path, header, org_rows, ending, org = locate(base, r["owner"])
        assert not org[r["field"]].strip(), f"{r['owner']} {r['field']} is held: {org[r['field']]!r}"
        allowed = vocab[r["field"]] | (ring3 if r["field"] == "processes" and org["ring_primary"] == "3" else set())
        assert r["value"] in allowed, f"{r['value']} is outside the vocabulary for {r['owner']}"
        assert gate.own_domain(gate.host_path(r["url"]), gate.host_path(org["website"])), f"{r['url']} is not {r['owner']}'s site"
        data, digest, offset = replay(r)
        plan.append(dict(r, path=path, evidence_id=f"EVD-{greatest + n:06d}", digest=digest, offset=offset, data=data,
                         shard=path.split("_")[-1][:-4], ring=org["ring_primary"]))
        cells.setdefault((path, r["owner"], r["field"]), []).append(r["value"])
        print(f"{r['owner']} {r['field']}={r['value']} offset {offset} sha {digest[:12]} ({len(data)} bytes)")
    if not args.apply:
        return
    # captures, shared store
    CAPTURES.mkdir(parents=True, exist_ok=True)
    for p in plan:
        f = CAPTURES / f"{p['digest']}.html"
        if f.exists():
            assert f.read_bytes() == p["data"], f"{f} exists with other bytes"
        else:
            f.write_bytes(p["data"])
    # cells
    for path in sorted({k[0] for k in cells}):
        header, org_rows, ending = parse(git("show", f"{base}:{path}"))
        by_id = {o["org_id"]: o for o in org_rows}
        for (pth, oid, field), values in cells.items():
            if pth == path:
                by_id[oid][field] = ";".join(sorted(values))
        (ROOT / path).write_bytes(encode(org_rows, header, ending))
    # evidence rows
    by_shard = {}
    for p in plan:
        detail = FIELD_HEAD[p["field"]].format(v=p["value"], q=p["quote"])
        ev = dict(evidence_id=p["evidence_id"], record_table="organizations", record_id=p["owner"], claim_type="activity",
                  claim_detail=detail, source_class="own_site", source_ref=p["url"], observed_date=OBSERVED,
                  tier_effect="supports_B", created_by=LABEL,
                  notes="Pilot reading by Codex (p3-refetch-pilot-2026-11-24); second read by Claude; capture is the gate fetch.",
                  address_role="")
        p["ev"] = ev
        by_shard.setdefault(f"data/evidence_organizations_{p['shard']}.csv", []).append(ev)
    for path, evs in by_shard.items():
        old = git("show", f"{base}:{path}")
        ending = "\r\n" if old.endswith(b"\r\n") else "\n"
        assert old.endswith(b"\n")
        (ROOT / path).write_bytes(old + _body(evs, ending))
    # this folder's CSVs
    write(HERE / "BINDING_PROOF.csv", [dict(evidence_id=p["evidence_id"], record_id=p["owner"],
          claim_sha256=gate.claim_sha256(p["ev"]), capture=p["url"], capture_date=OBSERVED, capture_sha256=p["digest"],
          quote_offset=p["offset"], verdict="VERIFIED", reader_family=READER, reader_date=OBSERVED) for p in plan],
          list(gate.PROOF_COLS))
    write(HERE / "FILLS.csv", [dict(record_id=p["owner"], shard=p["path"], field=p["field"], old="", new=p["value"],
          evidence_id=p["evidence_id"], url=p["url"], capture_sha256=p["digest"], quote_offset=p["offset"],
          quote=p["quote"]) for p in plan])
    write(HERE / "CLAIMS_CHECKED.csv", [dict(table="organizations", record_id=p["owner"], field=p["field"],
          verdict="corrected", evidence_id=p["evidence_id"]) for p in plan])
    (HERE / "INPUTS.sha256").write_text("".join(
        f"{d}  provenance/{TASK}/captures/{d}.html\n" for d in sorted({p['digest'] for p in plan})))
    print(f"applied {len(plan)} value(s) on {len({p['owner'] for p in plan})} owner(s)")


def read_csv_blob(base, path):
    return list(csv.DictReader(io.StringIO(git("show", f"{base}:{path}").decode(), newline="")))


def _body(rows, ending):
    stream = io.StringIO(newline="")
    csv.DictWriter(stream, EVIDENCE_COLS, lineterminator=ending).writerows(rows)
    return stream.getvalue().encode()


def write(path, rows, fields=None):
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fields or list(rows[0]), lineterminator="\n")
        w.writeheader()
        w.writerows(rows)


if __name__ == "__main__":
    main()

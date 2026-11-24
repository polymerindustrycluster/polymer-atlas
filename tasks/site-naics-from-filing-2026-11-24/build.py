"""Apply the reviewed site packet. Abort before writing if an input shard has drifted."""

import csv
import io
import json
from collections import defaultdict
from frame import BASE, HERE, REPO, git


def encode(rows, header, base):
    out = io.StringIO(newline="")
    writer = csv.DictWriter(
        out, header, lineterminator="\r\n" if b"\r\n" in base else "\n"
    )
    writer.writeheader()
    writer.writerows(rows)
    return out.getvalue().encode()


def main():
    packet = json.loads((HERE / "packet.json").read_text())
    new = defaultdict(list)
    pending = {}
    applied = set()
    for p in sorted((REPO / "data").glob("sites_*.csv")):
        if p.stem.endswith("_all"):
            continue
        base = git("show", BASE + ":data/" + p.name)
        reader = csv.DictReader(io.StringIO(base.decode(), newline=""))
        sites = list(reader)
        edited = False
        for site in sites:
            sid = site["site_id"]
            if sid not in packet:
                continue
            assert sid not in applied, sid
            applied.add(sid)
            item = packet[sid]
            if not item["changes"]:
                continue
            site.update(item["changes"])
            edited = True
            if item["evidence"]:
                new[p.with_name("evidence_" + p.name)].append(item["evidence"])
        if edited:
            pending[p] = (base, encode(sites, reader.fieldnames, base))
    assert applied == set(packet)
    for p, items in new.items():
        base = git("show", BASE + ":data/" + p.name)
        assert base.endswith(b"\n")
        hdr = next(csv.reader([base.splitlines()[0].decode()]))
        pending[p] = (
            base,
            base
            + encode(sorted(items, key=lambda e: e["evidence_id"]), hdr, base).split(
                b"\n", 1
            )[1],
        )
    for p, (base, result) in pending.items():
        if p.read_bytes() not in (base, result):
            raise ValueError("unrelated edits in " + str(p))
    for p, (_, result) in pending.items():
        if p.read_bytes() != result:
            tmp = p.with_suffix(".csv.tmp")
            tmp.write_bytes(result)
            tmp.replace(p)


if __name__ == "__main__":
    main()

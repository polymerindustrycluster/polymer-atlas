"""Rebuild the frame and expected cells from base plus checksummed source, without calling build.py."""

import csv
import io
import json
from pathlib import Path
from collections import Counter, defaultdict
from frame import BASE, HERE, REPO, build, git
from decision import FIELD, adjudicate
from raw import hashes, read_filings


def parse(blob):
    reader = csv.reader(io.StringIO(blob.decode(), newline=""), strict=True)
    header = next(reader)
    assert len(header) == len(set(header))
    out = []
    for row in reader:
        assert len(row) == len(header), "row width"
        out.append(dict(zip(header, row)))
    return header, out


def compare(before, after, changes, appends):
    hdr, original = parse(before)
    cur, actual = parse(after)
    assert hdr == cur and len(actual) == len(original) + len(appends), (
        "header/row count"
    )
    assert actual[len(original) :] == appends, "unexpected evidence tail"
    for old, now in zip(original, actual):
        assert now == old | changes.get(old[hdr[0]], {}), old[hdr[0]]


def claims(sid, item, old):
    changes = item["changes"]
    fields = changes.keys() if changes else [FIELD]
    for field in fields:
        verdict = (
            item["verdict"]
            if field not in changes or changes[field] != old[field]
            else "verified"
        )
        yield dict(
            table="sites",
            record_id=sid,
            field=field,
            verdict=verdict,
            evidence_id=item["evidence"].get("evidence_id", ""),
        )


def main():
    candidates = build()
    raw, paths = read_filings(candidates)
    assert hashes(paths) == (HERE / "INPUTS.sha256").read_text(), "store checksum"
    packet = adjudicate(candidates, raw)
    assert packet == json.loads((HERE / "packet.json").read_text()), (
        "source replay differs"
    )
    files = git("ls-tree", "-r", "--name-only", BASE, "data").decode().splitlines()
    allowed = set()
    expected_claims = []
    edits = {sid: i["changes"] for sid, i in packet.items() if i["changes"]}
    new = defaultdict(list)
    checked = set()
    for f in files:
        if not f.startswith("data/sites_"):
            continue
        before = git("show", BASE + ":" + f)
        for old in parse(before)[1]:
            sid = old["site_id"]
            if sid not in packet:
                continue
            assert sid not in checked
            checked.add(sid)
            item = packet[sid]
            expected_claims.extend(claims(sid, item, old))
            if item["changes"]:
                allowed.add(f)
            if item["evidence"]:
                new[f.replace("data/sites_", "data/evidence_sites_")].append(
                    item["evidence"]
                )
        compare(before, (REPO / f).read_bytes(), edits, [])
    assert checked == set(packet)
    for f, entries in new.items():
        allowed.add(f)
        compare(
            git("show", BASE + ":" + f),
            (REPO / f).read_bytes(),
            {},
            sorted(entries, key=lambda r: r["evidence_id"]),
        )
    diff = set(git("diff", "--name-only", BASE, "--", "data").decode().splitlines())
    assert diff == allowed, diff ^ allowed
    assert not git("ls-files", "--others", "--exclude-standard", "--", "data")
    path = HERE / "CLAIMS_CHECKED.csv"
    check_claims(path, expected_claims)
    import tempfile

    with tempfile.TemporaryDirectory() as tmp:
        duplicate = Path(tmp) / path.name
        lines = path.read_bytes().splitlines(keepends=True)
        duplicate.write_bytes(b"".join(lines + lines[1:2]))
        try:
            check_claims(duplicate, expected_claims)
        except AssertionError:
            pass
        else:
            raise AssertionError("escaped duplicate claim")
    plant()
    print(
        len(packet),
        "frame sites;",
        Counter(i["verdict"] for i in packet.values()),
        "; four plants rejected",
    )


def check_claims(path, expected):
    header = ["table", "record_id", "field", "verdict", "evidence_id"]
    with path.open(newline="") as stream:
        reader = csv.DictReader(stream)
        assert reader.fieldnames == header
        assert sorted(tuple(r[k] for k in header) for r in reader) == sorted(
            tuple(r[k] for k in header) for r in expected
        )


def plant():
    base = b"site_id,value,other\nA,old,x\nB,old,y\n"
    good = base.replace(b"A,old", b"A,new")
    changes = {"A": {"value": "new"}}
    compare(base, good, changes, [])
    for defect in [
        good.replace(b"new", b"bad"),
        base,
        good.replace(b"old,y", b"old,x"),
        good.replace(b",y\n", b"\n"),
    ]:
        try:
            compare(base, defect, changes, [])
        except AssertionError:
            continue
        raise AssertionError("escaped plant")


if __name__ == "__main__":
    main()

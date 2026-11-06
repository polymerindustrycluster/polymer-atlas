#!/usr/bin/env python3
"""Census, preservation, replay and injected failure checks for the fixed D10 packet."""
import csv
import hashlib
import io
import shutil
import subprocess
import tempfile
from collections import Counter
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
import build

ROOT, HERE = build.ROOT, build.HERE
hashes = lambda data: {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in data.glob("*.csv")}
base = subprocess.check_output(["git", "merge-base", "HEAD", "origin/main"], cwd=ROOT, text=True).strip()
verdicts = build.read(HERE / "verdicts.csv")
assert Counter(r["verdict"] for r in verdicts) == {"VERIFIED": 1, "DUPLICATE_OF": 5, "STILL_UNCERTAIN": 6}
for filename, key, expected in [("ecosystem.csv", "org_id", 1), ("evidence_ecosystem.csv", "evidence_id", 6)]:
    old = list(csv.DictReader(io.StringIO(subprocess.check_output(["git", "show", f"{base}:data/{filename}"], cwd=ROOT, text=True))))
    new = build.read(ROOT / "data" / filename)
    current = {r[key]: r for r in new}
    assert len(current) == len(new)
    assert all(current[r[key]] == r for r in old), "main row lost or changed"
    assert len(new) - len(old) == expected
changed = set(subprocess.check_output(["git", "diff", "--name-only", base, "--", "data/"], cwd=ROOT, text=True).splitlines())
assert changed == {"data/ecosystem.csv", "data/evidence_ecosystem.csv"}, changed

with tempfile.TemporaryDirectory() as tmp:
    data = Path(tmp) / "data"; shutil.copytree(ROOT / "data", data)
    before = hashes(data)
    subprocess.run(["python3", str(HERE / "build.py"), "--data-dir", str(data), "--apply"], capture_output=True, check=True)
    assert hashes(data) == before, "replay changed CSV bytes"
    for filename, key, duplicate, reason in [
        ("organizations_MI.csv", "org_id", "ORG-013300", "duplicate existing ORG ID"),
        ("evidence_sites_MI.csv", "evidence_id", "EVD-296000", "duplicate existing evidence ID")]:
        path = data / filename
        fake = dict(build.read(path)[0]); fake[key] = duplicate
        build.append_sorted(path, [fake], key)
        before = hashes(data)
        result = subprocess.run(["python3", str(HERE / "build.py"), "--data-dir", str(data), "--apply"],
                                capture_output=True, text=True)
        assert result.returncode and reason in result.stderr, result.stderr
        assert hashes(data) == before, "failed preflight wrote CSV"
        shutil.copyfile(ROOT / "data" / filename, path)
        print("PASS cross-shard", key, "collision refused before any write")

    packet = Path(tmp) / "packet"; packet.mkdir()
    for src in HERE.glob("*.csv"): shutil.copyfile(src, packet / src.name)
    evidence = build.read(HERE / "evidence_rows.csv")
    def write_evidence(rows):
        with (packet / "evidence_rows.csv").open("w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=list(evidence[0]), lineterminator="\n")
            writer.writeheader(); writer.writerows(rows)
    before = hashes(data)
    build.HERE = packet
    try:
        creates = build.read(packet / 'creates_ecosystem.csv')
        creates[0]['pic_relevance'] = ''
        with (packet / 'creates_ecosystem.csv').open('w', newline='') as f:
            w = csv.DictWriter(f, fieldnames=list(creates[0]), lineterminator='\n'); w.writeheader(); w.writerows(creates)
        try: build.plan(data)
        except AssertionError as error: assert str(error) == 'missing ecosystem PIC relevance', str(error)
        else: raise AssertionError('blank relevance passed')
        assert hashes(data) == before
        shutil.copyfile(HERE / 'creates_ecosystem.csv', packet / 'creates_ecosystem.csv')
        print('PASS blank relevance refused before any write')
        write_evidence([r for r in evidence if r["claim_type"] != "address"])
        assert len(build.read(packet / "evidence_rows.csv")) == 4
        try: build.plan(data)
        except AssertionError as error: assert str(error) == "missing ecosystem must-have evidence", str(error)
        else: raise AssertionError("missing typed address evidence passed")
        assert hashes(data) == before
        print("PASS missing typed evidence refused before any write")
        bad = [dict(r) for r in evidence]
        bad[0]["claim_detail"] = 'identity: "Fabricated Federal Polymer Program XYZ"'
        write_evidence(bad)
        bodies = {}
        for row in evidence:
            url = row["source_ref"]
            if url not in bodies:
                bodies[url] = subprocess.run(["curl", "-fL", "--max-time", "45", "-A", "Mozilla/5.0", "-sS", url],
                                            capture_output=True, check=True).stdout
        def cached_curl(args, **kwargs):
            assert args[0] == "curl" and args[-1] in bodies
            return SimpleNamespace(stdout=bodies[args[-1]])
        with patch.object(build.subprocess, "run", side_effect=cached_curl):
            try: build.raw_check()
            except AssertionError as error: assert "raw quote absent" in str(error), str(error)
            else: raise AssertionError("fabricated source quote passed")
        assert hashes(data) == before
        print("PASS fabricated evidence quote refuses; all CSVs unchanged")
    finally:
        build.HERE = HERE
print("PASS census12/12;1Cecosystem+6EVD exact main delta; all main rows preserved; all-CSV replay byte-identical")

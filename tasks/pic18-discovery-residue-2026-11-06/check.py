#!/usr/bin/env python3
"""Reconcile verdict population and prove idempotence / cross-shard collision refusal."""
import csv
import hashlib
import shutil
import subprocess
import tempfile
from pathlib import Path
import build


def hashes(data):
    return {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in data.glob('*.csv')}

with tempfile.TemporaryDirectory() as tmp:
    data=Path(tmp)/'data';shutil.copytree(build.ROOT/'data',data)
    before=hashes(data)
    subprocess.run(['python3',str(build.HERE/'build.py'),'--data-dir',str(data),'--apply'],check=True)
    assert hashes(data)==before, 'replay changed bytes'
    # Inject a reserved ID in another shard: every proposed write must remain untouched on failure.
    with (data/'organizations_OH.csv').open() as f: rows=list(csv.DictReader(f))
    bad=dict(rows[0]);bad['org_id']='ORG-009600'
    build.append_sorted(data/'organizations_OH.csv',[bad],'org_id')
    before=hashes(data)
    result=subprocess.run(['python3',str(build.HERE/'build.py'),'--data-dir',str(data),'--apply'],capture_output=True,text=True)
    assert result.returncode != 0 and 'duplicate existing ID' in result.stderr, result.stderr
    assert hashes(data)==before, 'failed preflight wrote data'
print('PASS all-CSV replay byte-identical; injected cross-shard reserved-ID collision fails before write')

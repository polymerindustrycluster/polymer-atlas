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

sponsors=build.read(build.ROOT/'tasks/form5500-spine-2026-11-01/sponsors.csv')
for name, street, expected in [('IAC', '1608', 3), ('Ultimate Industries', '1702', 0)]:
    matches=[r for r in sponsors if name.lower() in (r['sponsor_name']+' '+r['dba_name']).lower()]
    assert len(matches)==expected, ('screen changed; re-review', name)
    assert not any(street in r['street_address'] and r['state']=='OH' for r in matches), ('establishment sponsor blocks reject',name)
print('PASS snapshot2026-11-01 Form5500 screen: IAC3 names/0 establishment matches; Ultimate0 names')

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

#!/usr/bin/env python3
"""Zero-data hold packet, immutable withdrawn rows, replay and re-admission negatives."""
import csv
import hashlib
import io
import shutil
import subprocess
import tempfile
from pathlib import Path
from unittest.mock import patch
import build

ROOT,HERE=build.ROOT,build.HERE
digest=lambda data:{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in data.glob('*.csv')}
base=subprocess.check_output(['git','merge-base','HEAD','origin/main'],cwd=ROOT,text=True).strip()
assert not subprocess.check_output(['git','diff','--name-only',base,'--','data/'],cwd=ROOT,text=True).strip(),'hold packet changes canonical data'
assert not build.plan(ROOT/'data')
for filename in ['creates_ecosystem.csv','evidence_rows.csv']:
    archived=(HERE/'withdrawn'/filename).read_bytes()
    original=subprocess.check_output(['git','show','1342f2d:tasks/federal-programs-2026-11-06/'+filename],cwd=ROOT)
    assert archived==original,'withdrawn rows differ from immutable original'
    assert not build.read(HERE/filename)
assert len(build.read(HERE/'withdrawn/evidence_rows.csv'))==6
assert len(build.read(HERE/'withdrawn/creates_ecosystem.csv'))==1
with tempfile.TemporaryDirectory() as tmp:
    data=Path(tmp)/'data';shutil.copytree(ROOT/'data',data)
    before=digest(data)
    cmd=['python3',str(HERE/'build.py'),'--data-dir',str(data),'--raw-check','--apply']
    subprocess.run(cmd,check=True,capture_output=True)
    subprocess.run(cmd,check=True,capture_output=True)
    assert digest(data)==before,'no-op replay wrote canonical data'
    packet=Path(tmp)/'packet';shutil.copytree(HERE,packet,ignore=shutil.ignore_patterns('__pycache__'))
    original_here=build.HERE
    try:
        build.HERE=packet
        for filename in ['creates_ecosystem.csv','evidence_rows.csv']:
            shutil.copyfile(HERE/'withdrawn'/filename,packet/filename)
            with patch.object(build.sys,'argv',['build.py','--data-dir',str(data),'--apply']):
                try:build.main()
                except AssertionError as error:assert str(error)=='scope hold prohibits canonical creates/evidence',str(error)
                else:raise AssertionError('retired proposal re-admitted')
            assert digest(data)==before,'failed hold preflight wrote data'
            shutil.copyfile(HERE/filename,packet/filename)
            print('PASS retired',filename,'re-admission refused before any write')
    finally:
        build.HERE=original_here
print('PASS 12candidate rows=5held duplicates+7uncertain; exact archived1create/6EVD; retired7IDs; canonical/allCSVdelta0; byte-identical no-op replay')

#!/usr/bin/env python3
"""Frozen census, unresolved-promotion negative, raw receipts and zero-data boundary."""
import copy,csv,hashlib,importlib.util,json,subprocess
from pathlib import Path
from build import H,ROOT,read,validate
base=json.loads((H/'baseline.json').read_text())['commit'];frame=read(H/'input.csv');vs=read(H/'verdicts.csv');validate(frame,vs)
bad=copy.deepcopy(vs);bad[0]['verdict']='VERIFIED'
try:validate(frame,bad)
except AssertionError:pass
else:raise AssertionError('unsupported promotion escaped')
assert not subprocess.check_output(['git','diff','--name-only',base,'--','data/'],cwd=ROOT,text=True).strip(),'canonical data changed'
held={r['site_id']:r for p in (ROOT/'data').glob('sites_*.csv') for r in read(p)};assert held[frame[0]['site_id']]==frame[0]
spec=importlib.util.spec_from_file_location('raw',ROOT/'tasks/strong-waves-mo-sc-la-2026-11-06/prepare.py');raw=importlib.util.module_from_spec(spec);spec.loader.exec_module(raw)
receipts=json.loads((H/'rawcheck.json').read_text());assert len(receipts)==3
for r in receipts:
 name='home' if r['source_url'].endswith('.com/') else 'about';p=Path('/tmp/l3-quality-watson-'+name+'.html')
 if p.exists():
  assert hashlib.sha256(p.read_bytes()).hexdigest()==r['raw_sha256'];t=raw.Text();t.feed(p.read_text());text=' '.join(t.parts)
 else:
  result=raw.fetch(('quality-watson-'+name,(r['source_url'],r['quote'])));assert result['raw']=='yes';text=Path('/tmp/l3-quality-watson-'+name+'.txt').read_text()
 assert raw.contains(text,r['quote']) and not raw.contains(text,r['quote']+' fabricatedplantproof7731')
assert all(r['raw'] and r['fabricated_suffix_rejected'] for r in receipts)
print('PASS1/1 mergedC census;0promotions1hold;unsupported-promotion rejected;3raw known answers/3falsequotes;zero canonical edits/evidence')

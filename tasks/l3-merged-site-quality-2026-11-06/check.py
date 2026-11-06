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
held={r['site_id']:r for p in (ROOT/'data').glob('sites_*.csv') for r in read(p)};assert all(held[r['site_id']]==r for r in frame)
spec=importlib.util.spec_from_file_location('raw',ROOT/'tasks/strong-waves-mo-sc-la-2026-11-06/prepare.py');raw=importlib.util.module_from_spec(spec);spec.loader.exec_module(raw)
receipts=json.loads((H/'rawcheck.json').read_text());assert len(receipts)==5
for r in receipts:
 if 'raw_text_path' in r:
  p=Path(r['raw_text_path']);assert hashlib.sha256(p.read_bytes()).hexdigest()==r['raw_sha256'];text=p.read_text()
 else:
  name='home' if r['source_url'].endswith('.com/') else 'about';p=Path('/tmp/l3-quality-watson-'+name+'.html');assert hashlib.sha256(p.read_bytes()).hexdigest()==r['raw_sha256'];t=raw.Text();t.feed(p.read_text());text=' '.join(t.parts)
 assert raw.contains(text,r['quote']) and not raw.contains(text,r['quote']+' fabricatedplantproof7731')
assert all(r['raw'] and r['fabricated_suffix_rejected'] for r in receipts)
print('PASS3/3 mergedC census;0promotions3holds;unsupported-promotion rejected;5raw known answers/5falsequotes;zero canonical edits/evidence')

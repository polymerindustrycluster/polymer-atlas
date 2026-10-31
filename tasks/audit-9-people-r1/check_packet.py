"""Read-only audit9 packet and sample integrity checks; no canonical writes."""
import csv,json,hashlib,collections,random,subprocess,tempfile
from pathlib import Path
p=Path(__file__).resolve().parent
m=json.loads((p/'sample_manifest.json').read_text()); freeze=json.loads((p/'VERDICT_FREEZE.json').read_text())
assert len(m['random_ids'])==len(set(m['random_ids']))==50
assert sorted(random.Random(m['seed']).sample([f'PERSON-{i:06d}' for i in range(74,477)],50))==m['random_ids']
assert set(m['random_ids'])&set(m['judgment_ids'])=={'PERSON-000448'}
privacy=json.loads((p/'PRIVACY_REDACTIONS.json').read_text())
raw=[]
for f,h in freeze['worker_file_sha256'].items():
 expected=privacy[f]['published_redacted_sha256'] if f in privacy else h
 if f in privacy:assert privacy[f]['original_frozen_sha256']==h
 assert hashlib.sha256((p/f).read_bytes()).hexdigest()==expected
 raw+=json.loads((p/f).read_text())
assert len(raw)==len({r['person_id'] for r in raw})==60
ws=list(csv.DictReader((p/'worksheet.csv').open()));assert len(ws)==len({r['person_id'] for r in ws})==60
assert {r['person_id'] for r in raw}=={r['person_id'] for r in ws}
stats=json.loads((p/'statistics.json').read_text()); by={r['person_id']:r for r in raw}
corrections={(x['person_id'],x['field']):x for x in json.loads((p/'DERIVATIVE_CORRECTIONS.json').read_text())}
for r in ws:
 for k,v in by[r['person_id']].items():
  if (r['person_id'],k) in corrections:
   fix=corrections[(r['person_id'],k)];assert v==fix['old'];v=fix['new']
  if k in r:assert r[k]==('; '.join(v) if isinstance(v,list) else str(v)),(r['person_id'],k)
for fr,ids in [('random',m['random_ids']),('judgment',m['judgment_ids']),('held_correction',m['held_correction_ids'])]:
 c=collections.Counter(next(r['overall_verdict'] for r in ws if r['person_id']==i) for i in ids)
 assert stats[fr]['n']==len(ids)
 for grade in ['AGREE','FIELD_ERROR','CREATION_ERROR','UNRESOLVED']:
  assert stats[fr]['counts'][grade]==c[grade]
  assert abs(stats[fr]['rates'][grade]-100*c[grade]/len(ids))<1e-10
# Every positive Gate B quote is grounded in named opened source inventory.
for r in raw:
 if r['gate_b_verdict']=='AGREE':
  assert r['gate_b_quote'] and r['gate_b_url']
  assert r['gate_b_url'] in {x['url'] for x in r['sources']},r['person_id']
# Immutable draw can be regenerated without displaying any source columns.
with tempfile.TemporaryDirectory() as d:
 subprocess.run(['python3',str(p/'sample.py'),'--output-dir',d],check=True,stdout=subprocess.DEVNULL)
 assert json.loads(Path(d,'sample_manifest.json').read_text())==m
print('PASS: 403-ID frame, seeded 50 draw, 60 unique people/61 memberships, frozen hashes, worksheet parity, sources and raw rates.')

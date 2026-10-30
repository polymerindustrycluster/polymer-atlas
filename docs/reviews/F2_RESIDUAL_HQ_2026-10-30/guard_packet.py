"""Read-only F2 packet checks. Run from the repository root; no canonical writes."""
import csv, hashlib, json, pathlib, re, subprocess
R=pathlib.Path(__file__).resolve().parents[3]
P=pathlib.Path(__file__).resolve().parent
PIN='eceead3a5a59b7a51d13b2ad61d6070e4cfc9a05'
def read(n):return list(csv.DictReader((P/n).open()))
def sha(b):return hashlib.sha256(b).hexdigest()
pop=list(csv.DictReader((R/'data/organizations_US.csv').open()))
v=read('verdicts.csv');e=read('evidence_draft.csv');o=read('original_rows.csv');s=read('source_ledger.csv')
assert len(v)==len(pop)==163
assert [r['org_id'] for r in v]==[r['org_id'] for r in pop]
assert len({r['org_id'] for r in v})==163
for r,orig,snapshot in zip(v,pop,o):
 assert r['pin']==PIN
 assert json.loads(snapshot['original_row_json'])==orig
 assert r['original_fingerprint_sha256']==snapshot['original_fingerprint_sha256']==sha(json.dumps(orig,sort_keys=True,separators=(',',':')).encode())
 assert r['outcome'] in ('HQ_FOUND','STILL_UNKNOWN')
 assert r['verdict']==('VERIFIED' if r['outcome']=='HQ_FOUND' else 'STILL_UNCERTAIN')
 assert 0<=int(r['primary_fetches'])<=6
 for k in ('observed_date','retrieved_date'):assert re.fullmatch(r'\d{4}-\d{2}-\d{2}',r[k])
 if r['outcome']=='HQ_FOUND':assert all(r[k] for k in ('hq_city','hq_state','hq_country','source_ref'))
 else:assert r['settling_fact'] and not any(r[k] for k in ('hq_city','hq_state','hq_country','hq_county'))
ids={r['org_id'] for r in v if r['outcome']=='HQ_FOUND'}
assert len(e)==len(ids) and {r['record_id'] for r in e}==ids
assert len(s)==163 and [r['org_id'] for r in s]==[r['org_id'] for r in v]
for r in e:
 assert r['evidence_id']=='' and r['record_table']=='organizations' and r['claim_type']=='address'
 assert r['source_class'] in ('own_site','government_filing','registry')
 if r['source_class']=='registry':assert r['tier_effect']=='supports_C'
assert subprocess.check_output(['git','diff',PIN,'--','data/'],cwd=R)==b''
q=subprocess.check_output(['git','show',PIN+':tasks/QUEUE.md'],cwd=R).decode()
assert (R/'tasks/QUEUE.md').read_text()==q.replace('- [ ] `open` **F2','- [ ] `claimed:codex-f2-residual-hq 2026-10-30` **F2')
m=json.loads((P/'manifest.json').read_text())
for name,h in m['files'].items():assert sha((P/name).read_bytes())==h
print('PASS: 163 exact rows, outcomes, evidence FKs/IDs/classes/ceilings, source ledger, ISO dates, original fingerprints, unchanged data, queue isolation, manifest.')

#!/usr/bin/env python3
"""Read-only packet checks; no canonical changes or ID allocation."""
import csv,hashlib,json,pathlib,collections
root=pathlib.Path(__file__).resolve().parents[1]
d=root/'docs/reviews/2026-10-30-pa-adjudication-packet'
p=json.load((d/'packet.json').open());tables={}
for t,pat in [('organizations','organizations_*.csv'),('sites','sites_*.csv'),('ecosystem','ecosystem.csv'),('programs','programs.csv')]:
 tables[t]={}
 for f in (root/'data').glob(pat):
  if '_all.' in f.name:continue
  for r in csv.DictReader(f.open()):tables[t][next(iter(r.values()))]=r
union=set().union(*(set(v) for v in tables.values()))
assert len(p['cases'])==9
assert {c['case_id'] for c in p['cases']}=={'PA-'+str(n).zfill(2) for n in range(1,11) if n!=9}
for c in p['cases']:
 assert c['verdict'] in ('VERIFIED','REJECT','STILL_UNCERTAIN','DUPLICATE_OF')
 if c['verdict']=='STILL_UNCERTAIN':assert c['settling_fact']
 for r in c['records']:
  row=tables[r['table']][r['id']]
  assert row==r['row']
  assert hashlib.sha256(json.dumps(row,sort_keys=True,ensure_ascii=False,separators=(',',':')).encode()).hexdigest()==r['sha256']
 for m in c['motions']:
  assert m['motion'] in ('stand separate','fold','re-point','annotate')
  for id in m['affected_ids']:assert id in union,(c['case_id'],id)
  if m.get('verdict')=='STILL_UNCERTAIN':assert m.get('settling_fact')
  if m['motion']=='fold':
   chain=m['successor_chain'];assert len(chain)>1 and len(chain)==len(set(chain))
   assert all(i in tables['organizations'] for i in chain)
   assert not tables['organizations'][chain[-1]]['successor_org_id']
ledger=json.load((d/'source_ledger.json').open())
urls={s['url'] for s in ledger['sources'] if s.get('fetch_status') in ('opened','retrieved')}
assert len({(r['table'],r['id']) for c in p['cases'] for r in c['records']})==p['counts']['referenced_records']==40
ev=list(csv.DictReader((d/'evidence_rows.csv').open()))
assert ev==[e for c in p['cases'] for e in c['evidence_rows']]
assert list(ev[0])==next(csv.reader((root/'data/evidence.csv').open()))
for e in ev:
 assert e['evidence_id']==''
 assert e['record_id'] in tables[e['record_table']]
 assert e['source_ref'] in urls
 assert e['claim_type'] in ('existence','activity','scope','address','parent','liveness','code')
 assert e['tier_effect'] in ('supports_A','supports_B','supports_C','contradicts')
 if e['tier_effect']=='supports_A':assert e['source_class'] in ('own_site','government_filing')
 if e['source_class'] in ('registry','directory') and e['claim_type']=='address':assert e['tier_effect'] in ('supports_C','contradicts')
 if e['source_class']=='platform_category':assert e['tier_effect'] in ('supports_C','contradicts') and not(e['claim_type']=='scope' and e['tier_effect']!='contradicts')
assert len(ev)==p['counts']['draft_evidence_rows']
print('PASS:',len(p['cases']),'cases;',p['counts']['referenced_records'],'fingerprinted records;',len(ev),'unallocated evidence drafts;',len(union),'union IDs')
print('Verdicts:',dict(collections.Counter(c['verdict'] for c in p['cases'])))

"""Blank-only strict-match checker, pinned known answers and adversarial defect injections."""
import copy,csv,hashlib,io,json,subprocess,sys
from collections import Counter
from build import *

def at(rev,path):return list(csv.DictReader(io.StringIO(subprocess.check_output(['git','show',f'{rev}:{path}'],cwd=ROOT,text=True))))

def payload(fills,evs):
 raw={r['LoanNumber']:r for r in loans()};before=P/'pre-pass'
 orgs={r['org_id']:r for p in before.glob('organizations_*.csv') for r in read(p)}
 ss=[r for p in before.glob('sites_*.csv') for r in read(p)];sites={r['site_id']:r for r in ss}
 assert len({(r['record_table'],r['record_id']) for r in fills})==len(fills)
 assert len(evs)==len(fills) and len({r['evidence_id'] for r in evs})==len(evs)
 evidence={r['evidence_id']:r for r in evs}
 for u in fills:
  r=raw[u['loan_id']];o=orgs[u['org_id']];s=sites[u['site_id']];table=u['record_table']
  assert safe(r) and r['BorrowerState']=='OH'
  assert u['old']=='' and (o if table=='organizations' else s)[FIELDS[table]]==''
  assert u['new']==band(r['JobsReported']) and u['new'] in ORDER
  assert u['borrower_name']==r['BorrowerName'] and u['jobs_reported']==r['JobsReported']
  assert atlas.name_key(r['BorrowerName']) in {atlas.name_key(n) for _,n in atlas.org_name_fields(o)}
  assert s['org_id']==u['org_id'] and s['operating_status']=='active' and s['county'] in PIC18
  assert r['BorrowerCity'].casefold()==s['city'].casefold()
  assert s['street_address'] and r['BorrowerAddress'] and atlas.street_key(s['street_address'])==atlas.street_key(r['BorrowerAddress'])
  os=[x for x in ss if x['org_id']==u['org_id']]
  assert sum(x['operating_status']=='active' for x in os)==1 and all(x['state']=='OH' and x['country'] in ('','US','USA') for x in os)
  assert u['record_id']==(o if table=='organizations' else s)[KEYS[table]]
  assert u['field']==FIELDS[table] and u['loan_date']==loan_date(r) and u['loan_date'][:4] in ('2020','2021')
  e=evidence[u['evidence_id']]
  assert e['record_table']==table and e['record_id']==u['record_id'] and e['claim_type']=='size_band'
  assert e['source_class']=='government_filing' and e['tier_effect']==('supports_U' if (o if table=='organizations' else s)['verification_tier']=='U' else 'supports_B')
  assert 376000<=int(e['evidence_id'][4:])<=376999 and e['observed_date']==loan_date(r)
  for key in ['BorrowerName','BorrowerAddress','BorrowerCity','JobsReported','DateApproved']:assert f'{key}="{r[key]}"' in e['claim_detail']
  assert 'historical '+loan_date(r)[:4] in e['claim_detail'] and r['source_url'] in e['source_ref'] and r['LoanNumber'] in e['source_ref']
 expected,ee,held,n=plan(before)
 assert fills==expected and evs==ee,'omitted, added, reordered or altered proposal'
 return held,n

def check_tree(fills,evs):
 before=P/'pre-pass';updates={(r['record_table'],r['record_id']):r for r in fills}
 for table in FIELDS:
  name=f'{table}_OH.csv';b=read(before/name);now=read(ROOT/'data'/name)
  assert {r[KEYS[table]] for r in b}=={r[KEYS[table]] for r in now},'row loss or extra row'
  expected=copy.deepcopy(b)
  for r in expected:
   u=updates.get((table,r[KEYS[table]]))
   if u:r[FIELDS[table]]=u['new']
  assert now==expected,'unauthorized field edit or omitted fill'
  name=f'evidence_{table}_OH.csv';b=read(before/name);now=read(ROOT/'data'/name)
  assert now==sorted(b+[e for e in evs if e['record_table']==table],key=lambda e:e['evidence_id']),'evidence append mismatch'
 all_e=[e for p in (ROOT/'data').glob('evidence_*.csv') for e in read(p)]
 assert len({e['evidence_id'] for e in all_e})==len(all_e),'global evidence ID collision'

def known_answers():
 rows=[r for r in read(D/'known_answers.csv') if r['grain']=='organizations' and r['single_site_ohio']=='True' and r['atlas_band'] in ORDER]
 assert len({r['record_id'] for r in rows})==len(rows)
 raw={r['LoanNumber']:r for r in loans()};base=json.loads((D/'base.json').read_text())['known_answer_base']
 names=subprocess.check_output(['git','ls-tree','-r','--name-only',base,'data'],text=True,cwd=ROOT).splitlines()
 old={r['org_id']:r for p in names if p.startswith('data/organizations_') and p.endswith('.csv') for r in at(base,p)}
 good=0
 for r in rows:
  assert r['atlas_band']==old[r['record_id']]['employee_band_ohio']
  new=band(raw[r['loan_id']]['JobsReported']);assert new==r['loan_band']
  good+=abs(ORDER.index(new)-ORDER.index(r['atlas_band']))<=1
 assert len(rows)==106 and good==104
 print('known answers: 104/106 within one organization band, recomputed from SBA figures + pinned Atlas bands')

def main():
 for p in (P/'pre-pass').glob('*.csv'):
  assert p.read_bytes()==subprocess.check_output(['git','show',f'{BASE}:data/{p.name}'],cwd=ROOT),'pre-pass backup differs from base'
 fills=read(D/'fills.csv');evs=read(D/'evidence_rows.csv');held,n=payload(fills,evs);check_tree(fills,evs);known_answers()
 counts=json.loads((D/'counts.json').read_text());assert counts['fills']==dict(Counter(r['record_table'] for r in fills)) and counts['evidence_rows']==len(evs)
 assert counts['strict_organizations']==n and counts['held_loan_org_pairs']==len(held)
 assert read(D/'holds.csv')==held and counts['loan_years']==dict(Counter(r['loan_date'][:4] for r in fills))
 for defect in ['nonblank','wrong_band','wrong_identity']:
  bad=copy.deepcopy(fills)
  if defect=='nonblank':bad[0]['old']='1-9'
  elif defect=='wrong_band':bad[0]['new']=next(b for b in ORDER if b!=bad[0]['new'])
  else:bad[0]['org_id']=next(r['org_id'] for r in fills if r['org_id']!=bad[0]['org_id'])
  try:payload(bad,evs)
  except AssertionError:print('injected defect rejected:',defect)
  else:raise AssertionError('silent pass: '+defect)
 for key in ['BorrowerAddress','BorrowerCity']:
  bad=copy.deepcopy(evs);u=fills[0];r=next(r for r in loans() if r['LoanNumber']==u['loan_id'])
  bad[0]['claim_detail']=bad[0]['claim_detail'].replace(f'; {key}="{r[key]}"','')
  try:payload(fills,bad)
  except AssertionError:print('injected evidence defect rejected:',key)
  else:raise AssertionError('silent pass: missing '+key)
 snapshots={p:p.read_bytes() for p in [ROOT/'data'/n for n in ['organizations_OH.csv','sites_OH.csv','evidence_organizations_OH.csv','evidence_sites_OH.csv']]}
 subprocess.run([sys.executable,str(D/'build.py'),'--apply'],check=True)
 assert all(p.read_bytes()==b for p,b in snapshots.items()),'apply not idempotent'
 print('PASS: strict blank-only bands, evidence parity, known answers, three defects and idempotence')
if __name__=='__main__':main()

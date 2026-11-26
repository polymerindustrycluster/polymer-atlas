"""Named check for the 2026-11-26 PPP size-band re-run. Run: python3 tasks/ppp-size-bands-rerun-2026-11-26/check.py

Compares every data table the PR touches with the pinned base as WHOLE-ROW MULTISETS (an existing row may not be deleted or
edited; the only row changes allowed are the planned blank-to-band cells), pins the additions to what the rule yields, ties
every fill to a dated evidence row and to CLAIMS_CHECKED.csv, replays each evidence row through the binding gate, and then
plants defects (deleted row, edited row, overwritten non-empty band, loan older than ten years, individual borrower type, fill
with no evidence row) and requires each to be rejected by the rule it exists to trip."""
import copy,functools,hashlib,subprocess,sys
from collections import Counter
from build import *

TOUCHED={'organizations_OH.csv','sites_OH.csv','evidence_organizations_OH.csv','evidence_sites_OH.csv'}
TYPE={'organizations':'organizations_OH.csv','sites':'sites_OH.csv'}
def rows_at(rev,name):return parse(git('show',f'{rev}:data/{name}')) if rev else read(ROOT/'data'/name)
def bag(rows):return Counter(tuple(r.items()) for r in rows)
def tables(rev):return {n:rows_at(rev,n) for n in TOUCHED}
size_evidence=functools.cache(size_evidence)  # the base's size_band evidence, read once

T1=('tier1_qualifier','tier1_qualifier_basis')  # derived columns: only scripts/derive_tier1.py output, pinned in tier1_changes.csv, may change
BANDS250={'250-499','500-999','1000-4999','5000+'}
def verify(base,head,fills,evs,claims,raw,tier1):
 """-> list of (code, message); empty means every rule held. Pure over its arguments so planted defects can be injected."""
 bad=[];err=lambda code,msg:bad.append((code,msg))
 evidence={e['evidence_id']:e for e in evs}
 if len(evidence)!=len(evs) or len({(f['record_table'],f['record_id']) for f in fills})!=len(fills):err('duplicate','duplicate evidence id or fill')
 for table,name in TYPE.items():
  mine=[f for f in fills if f['record_table']==table];key=KEYS[table];field=FIELDS[table]
  rem=bag(base[name])-bag(head[name]);add=bag(head[name])-bag(base[name])
  old={dict(r)[key]:dict(r) for r in rem.elements()};new={dict(r)[key]:dict(r) for r in add.elements()}
  if sum(rem.values())!=len(old) or sum(add.values())!=len(new):err('row_multiset',f'{name}: duplicate ids in the changed rows')
  if set(old)!=set(new):err('row_deleted_or_added',f'{name}: removed ids {sorted(set(old)-set(new))[:5]} added ids {sorted(set(new)-set(old))[:5]}')
  if set(new)!={f['record_id'] for f in mine}:err('unplanned_change',f'{name}: changed rows differ from the planned fills')
  for rid in set(old)&set(new):
   o,n=old[rid],new[rid]
   extra={k for k in o if o[k]!=n[k]}-{field}
   if extra and not (table=='organizations' and extra<=set(T1) and rid in tier1 and (n['tier1_qualifier'],n['tier1_qualifier_basis'])==(tier1[rid]['new_tier1_qualifier'],tier1[rid]['new_tier1_qualifier_basis']) and (o['tier1_qualifier'],o['tier1_qualifier_basis'])==(tier1[rid]['old_tier1_qualifier'],tier1[rid]['old_tier1_qualifier_basis']) and n[field] in BANDS250):err('row_edited',f'{rid}: a field other than {field} changed ({sorted(extra)})')
   if o[field].strip():err('overwrite',f'{rid}: {field} was {o[field]!r} at the base')
  if table=='organizations' and not set(tier1)<=set(new):err('tier1_unplanned','a tier-1 re-derivation row is not a filled organization')
  for f in mine:
   if f['record_id'] in new and new[f['record_id']][field]!=f['new']:err('band_mismatch',f"{f['record_id']}: head {new[f['record_id']][field]!r} != fill {f['new']!r}")
 for table in TYPE:  # each shard's own delta must be exactly the planned rows of its record_table: a row in the other shard, missing or extra fails
  name=f'evidence_{table}_OH.csv'
  if bag(base[name])-bag(head[name]):err('evidence_removed_or_edited',f'{name}: an existing evidence row was deleted or edited')
  if bag(head[name])-bag(base[name])!=bag([e for e in evs if e['record_table']==table]):err('evidence_additions',f'{name}: added rows differ from the planned {table} evidence rows')
 ids=[e['evidence_id'] for e in evs];retired={h['retired_evidence_id'] for h in read(D/'holds.csv') if h['retired_evidence_id']}
 if ids!=[i for i in (f'EVD-{FIRST_EVD+k:06d}' for k in range(len(ids)+len(retired))) if i not in retired]:err('evidence_ids','evidence ids are not the range from EVD-%d less the retired ids of the held loans'%FIRST_EVD)
 orgs={r['org_id']:r for r in base['organizations_OH.csv']};sitebyid={r['site_id']:r for r in base['sites_OH.csv']}
 for f in fills:  # SCHEMA R13 v1.19.7: a different band already held on the same establishment from a newer admissible dated source wins
  klass,_=precedence(f,orgs,sitebyid,size_evidence())
  if klass.startswith('newer_contradicting'):err('newer_contradicting',f"{f['record_id']}: the establishment holds a different band from a newer source ({klass})")
 for f in fills:
  e=evidence.get(f['evidence_id']);r=raw.get(f['loan_id'])
  if not e or (e['record_table'],e['record_id'],e['claim_type'])!=(f['record_table'],f['record_id'],'size_band'):err('no_evidence',f"{f['record_id']}: no size_band evidence row {f['evidence_id']}");continue
  if not r:err('no_loan',f"{f['record_id']}: loan {f['loan_id']} not in the input");continue
  if loan_date(r)<CUTOFF or loan_date(r)!=f['loan_date'] or e['observed_date']!=loan_date(r):err('loan_age',f"{f['record_id']}: loan dated {loan_date(r)}, cutoff {CUTOFF}")
  if r['BusinessType'] not in ALLOWED or not safe(r):err('borrower_type',f"{f['record_id']}: BusinessType {r['BusinessType']!r} is not a named corporation, S corporation, LLC, partnership or LLP")
  if f['new']!=band(r['JobsReported']):err('band_value',f"{f['record_id']}: band {f['new']} != JobsReported {r['JobsReported']}")
  if e['source_class']!='government_filing' or not e['source_ref'].startswith(f"SBA PPP LoanNumber {f['loan_id']} (") or f"borrower_name: {r['BorrowerName']}; business_type: {r['BusinessType']}; address: {r['BorrowerAddress']}, {r['BorrowerCity']}, {r['BorrowerState']} {r['BorrowerZip']}" not in e['claim_detail'] or not e['claim_detail'].startswith(f"{f['field']}={f['new']}; "):err('evidence_content',f"{e['evidence_id']}: row does not quote the loan")
 changed={(t,dict(r)[KEYS[t]],FIELDS[t]) for t,n in TYPE.items() for r in (bag(head[n])-bag(base[n])).elements()}
 if {(c['table'],c['record_id'],c['field']) for c in claims}!=changed or len(claims)!=len(changed) or any(c['verdict']!='corrected' for c in claims):err('claims_checked','CLAIMS_CHECKED.csv differs from the changed cells')
 if {(c['table'],c['record_id'],c['evidence_id']) for c in claims}!={(f['record_table'],f['record_id'],f['evidence_id']) for f in fills}:err('claims_evidence','CLAIMS_CHECKED evidence ids differ from the fills')
 return bad

def codes(bad):return sorted({c for c,_ in bad})
def expect(label,bad,code):
 assert code in codes(bad),f'silent pass: planted {label} was not rejected by {code} (got {codes(bad)})'
 print(f'planted {label}: rejected ({code})')

def main():
 assert git('merge-base','HEAD',BASE).strip()==BASE,'the pinned base is not an ancestor of HEAD'
 changed=set(git('diff','--name-only',BASE,'--','data').split());assert changed=={f'data/{n}' for n in TOUCHED},f'data files touched: {sorted(changed)}'
 for line in (D/'INPUTS.sha256').read_text().splitlines():
  digest,path=line.split('  ',1);assert path.startswith(('raw/','provenance/')),path
  assert hashlib.sha256((STORE/path).read_bytes()).hexdigest()==digest,f'store file differs from INPUTS.sha256: {path}'
 raw={r['LoanNumber']:r for r in loans()}
 fills,evs,claims=read(D/'fills.csv'),read(D/'evidence_rows.csv'),read(D/'CLAIMS_CHECKED.csv')
 tier1={r['org_id']:r for r in read(D/'tier1_changes.csv')}
 drift=subprocess.run([sys.executable,str(ROOT/'scripts/derive_tier1.py')],capture_output=True,text=True,cwd=ROOT);assert drift.returncode==0,'tier1_qualifier drift remains:\n'+drift.stdout[-800:]
 p=plan();assert fills==p['fills'] and evs==p['evidence'],'omitted, added, reordered or altered proposal'
 assert read(D/'holds.csv')==p['holds'] and read(D/'gate_holds.csv')==p['gate_holds'] and read(D/'precedence.csv')==[dict((k.rstrip('_'),v) for k,v in r.items()) for r in p['precedence']]
 assert all(h['reason']=='newer_contradicting_filing' for h in p['holds'] if h['retired_evidence_id']) and len(p['contradicted'])==3,'expected the three newer_contradicting_filing holds'
 base,head=tables(BASE),tables(None)
 bad=verify(base,head,fills,evs,claims,raw,tier1);assert not bad,bad
 all_e=[e for q in (ROOT/'data').glob('evidence_*.csv') for e in read(q)];assert len({e['evidence_id'] for e in all_e})==len(all_e),'tree-wide evidence id collision'
 idx=gate.Index.load(BASE);verdicts=Counter(gate.judge(dict(e,_at='check'),idx)[0] for e in evs);assert verdicts=={'PASS':len(evs)},verdicts
 print(f'rows: {len(fills)} fills ({Counter(f["record_table"] for f in fills)}) on {len({f["org_id"] for f in fills})} owners; {len(evs)} evidence rows, binding gate PASS {verdicts["PASS"]}; every touched table equal to base as a row multiset plus the planned cells')
 if CENSUS.exists():
  before=(D/'reconciliation.csv').read_bytes();r=reconcile(p);assert (D/'reconciliation.csv').read_bytes()==before,'reconciliation.csv is stale'
  print('census reconciliation:',r)
 else:print(f'NOT INSPECTED: census rows {CENSUS} absent, reconciliation.csv not re-derived')
 # planted defects, each on a copy of the verified state
 org=TYPE['organizations'];kept=lambda n:next(r for r in head[n] if r[KEYS['organizations' if n==org else 'sites']] not in {f['record_id'] for f in fills})
 h=copy.deepcopy(head);h[org].remove(kept(org));expect('deleted existing row',verify(base,h,fills,evs,claims,raw,tier1),'row_deleted_or_added')
 h=copy.deepcopy(head);k=kept(org);i=h[org].index(k);h[org][i]=dict(k,website='https://edited.example/');expect('edited existing row',verify(base,h,fills,evs,claims,raw,tier1),'unplanned_change')
 h=copy.deepcopy(head);k=kept(org);i=h[org].index(k);h[org][i]=dict(k,hq_city='Elsewhere');expect('edited existing row (other field)',verify(base,h,fills,evs,claims,raw,tier1),'unplanned_change')
 h=copy.deepcopy(head);k=kept(org);i=h[org].index(k);h[org][i]=dict(k,tier1_qualifier='public_parent');expect('hand-edited tier1_qualifier on an unfilled organization',verify(base,h,fills,evs,claims,raw,tier1),'row_edited')
 t=next(iter(tier1));h=copy.deepcopy(head);i=next(j for j,r in enumerate(h[org]) if r['org_id']==t);h[org][i]=dict(h[org][i],tier1_qualifier='public_parent;employees_250plus');expect('tier1_qualifier differing from the pinned derivation',verify(base,h,fills,evs,claims,raw,tier1),'row_edited')
 fo=next(f for f in fills if f['record_table']=='organizations');b=copy.deepcopy(base)
 for r in b[org]:
  if r['org_id']==fo['record_id']:r[FIELDS['organizations']]=next(x for x in ORDER if x!=fo['new'])  # a different held band that the fill would overwrite
 expect('overwritten non-empty band',verify(b,head,fills,evs,claims,raw,tier1),'overwrite')
 r2=copy.deepcopy(raw);r2[fo['loan_id']]['DateApproved']='04/15/2015';expect('loan older than ten years',verify(base,head,fills,evs,claims,r2,tier1),'loan_age')
 r2=copy.deepcopy(raw);r2[fo['loan_id']]['BusinessType']='Sole Proprietorship';expect('individual borrower type',verify(base,head,fills,evs,claims,r2,tier1),'borrower_type')
 e2=[e for e in evs if e['evidence_id']!=fo['evidence_id']];expect('fill with no evidence row',verify(base,head,fills,e2,claims,raw,tier1),'no_evidence')
 fl,ev=p['contradicted'][0];h=copy.deepcopy(head);t=fl['record_table']  # a fill the precedence rule held, put back with consistent data, evidence and claims
 for r in h[TYPE[t]]:
  if r[KEYS[t]]==fl['record_id']:r[FIELDS[t]]=fl['new']
 h[f'evidence_{t}_OH.csv'].append(ev);expect(f"{fl['record_id']} fill against a newer different ITA band on its sole site",verify(base,h,fills+[fl],evs+[ev],claims+[dict(table=t,record_id=fl['record_id'],field=fl['field'],verdict='corrected',evidence_id=fl['evidence_id'])],raw,tier1),'newer_contradicting')
 ita=dict(source_class='government_filing',source_ref='OSHA ITA Form 300A; raw/osha/2026-11-22-archive-snapshot/raw/ita/x.csv',claim_detail='employee_band_site=100-249; OSHA ITA 300A CY2019; quote: X',observed_date='2026-11-01',evidence_id='EVD-T',band='100-249')  # Codex #573 r2: CY2019 text, retrieval date in observed_date
 klass,_=precedence(dict(record_table='organizations',record_id='O',org_id='O',site_id='S',loan_id='1',loan_date='2020-04-13',new='50-99'),{},{'S':{FIELDS['sites']:'100-249'}},{('sites','S'):[ita]})
 assert klass=='older_differs',f'silent pass: a 2019 filing with a retrieval observed_date was read as newer than a 2020 loan ({klass})';print('planted 2019 ITA filing with a retrieval observed_date: read as older, not a hold (older_differs)')
 mv=next(e for e in reversed(evs) if e['record_table']=='sites');h=copy.deepcopy(head);h['evidence_sites_OH.csv'].remove(mv);h['evidence_organizations_OH.csv'].append(mv);expect(f"evidence row {mv['evidence_id']} moved to the wrong shard",verify(base,h,fills,evs,claims,raw,tier1),'evidence_additions')
 c2=[c for c in claims if c['evidence_id']!=fo['evidence_id']];expect('changed cell missing from CLAIMS_CHECKED',verify(base,head,fills,evs,c2,raw,tier1),'claims_checked')
 assert CUTOFF==WRITE.replace(year=WRITE.year-10).isoformat()=='2016-11-26'
 print('PASS: PPP re-run additions pinned, whole-row multisets equal to the base plus the planned cells, gate PASS on every row, 13 planted defects rejected')
if __name__=='__main__':main()

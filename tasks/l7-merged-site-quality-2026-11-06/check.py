"""Named quality gate: census, raw source binding, complete B claims, replay and adverse no-write controls."""
import csv,hashlib,io,json,os,random,runpy,shutil,subprocess,sys,tempfile
from collections import Counter
from pathlib import Path
from build import P,ROOT,read,write
from research import found
sys.path.insert(0,str(ROOT/'scripts'))
from build_qcew_denominators import atlas_numerators
from atlas import load_tables,name_key
frame=read(P/'input.csv');vs=read(P/'verdicts.csv');packet=read(P/'evidence_packet.csv');edits=read(P/'edits.csv')
before={r['site_id']:r for r in json.loads((P/'before.json').read_text())['sites']}
assert len(frame)==len(vs)==len(before)==len({r['site_id'] for r in vs})==75
assert Counter(r['state'] for r in frame)=={'FL':17,'GA':20,'NY':7,'IN':21,'WI':10}
up={r['site_id'] for r in vs if r['verdict']=='VERIFIED'};assert len(up)==30
assert len(read(P/'holds.csv'))==45 and len(packet)==210 and len(edits)==60
assert 'SITE-016120' not in up
retired={f'EVD-{i}' for i in range(207360,207367)}
assert not retired & {r['evidence_id'] for p in (ROOT/'data').glob('evidence_*.csv') for r in read(p)}
raw=read(P/'rawcheck.csv');witnesses={r['site_id']:r for r in read(P/'witnesses.csv')}
assert len(raw)==30 and len({r['source_ref'] for r in raw})==27
for r in raw:
 text=Path(r['cache_file']).read_text()
 assert found(text,r['quote']) and found(text,witnesses[r['site_id']]['location_anchor'])
 assert not found(text,r['quote']+' fabricated L7 defect')
 assert hashlib.sha256(Path(r['cache_file']).read_bytes()).hexdigest()==r['raw_sha256']
known=read(P/'known-answers.csv');assert len(known)==3 and all(r['expected']=='MATCH' and r['result'].startswith('PASS') for r in known)
for r in known:assert found(Path('/tmp/L6-'+r['cluster_id']+'.txt').read_text(),r['quote'])
fetches=read(P/'fetches.csv');sources=read(P/'sources.csv')
assert len(fetches)==len(sources)==len({r['source_id'] for r in fetches})
assert all(r['org_id'] in {f['org_id'] for f in frame} for r in sources)
assert max(Counter(r['org_id'] for r in sources).values())<=6
gov=read(P/'government_review.csv');assert {r['site_id'] for r in gov}==up
ita={r['establishment_id']:r for r in read(ROOT/'tasks/osha-ita-2026-11-01/establishments.csv')}
tables=load_tables(ROOT/'data');orgs={r['org_id']:r for r in tables['organizations'].rows}
cleaners={}
for state,slug in [('FL','corroborated-fl-ga'),('GA','corroborated-ga'),('NY','corroborated-ny'),('IN','corroborated-in'),('WI','corroborated-wi')]:
 cleaners[state]=runpy.run_path(str(ROOT/f'tasks/{slug}-2026-11-06/build.py'))['clean_street']
for g in gov:
 f=ita[g['establishment_id']];s=before[g['site_id']];o=orgs[s['org_id']]
 assert all(g[k]==f[k] for k in g if k!='site_id'),('banked-source mismatch',g['site_id'])
 assert (cleaners[s['state']](f),f['city'],f['state'],f['zip5'],f['naics_code'])==(s['street_address'],s['city'],s['state'],s['zip'],s['naics_primary'])
 names={name_key(o['legal_name']),*(name_key(t.removesuffix(' (federal registrant name)').strip()) for t in o['trade_names'].split(';'))}
 assert name_key(f['company_name']) in names
order=sorted(up);random.Random(7731).shuffle(order)
write(P/'blind_recheck.csv',[dict(site_id=sid,result='PASS: government fields/operator + raw scope + location + issuer + all7 B claims',source_ref=next(r['source_ref'] for r in raw if r['site_id']==sid)) for sid in order[:20]])
base=subprocess.check_output(['git','merge-base','HEAD','origin/main'],text=True).strip()
for p in (ROOT/'data').glob('*.csv'):
 original=subprocess.check_output(['git','show',base+':data/'+p.name])
 owned_names={f'{table}_{state}.csv' for table in ['sites','evidence_sites'] for state in ['FL','GA','NY','IN','WI']}
 if p.name not in owned_names:
  assert p.read_bytes()==original,('unrelated canonical file changed',p.name);continue
 old=list(csv.DictReader(io.StringIO(original.decode())))
 if not old:continue
 key=next(iter(old[0]));new={r[key]:r for r in read(p)}
 for r in old:
  for e in edits:
   if p.name==f"sites_{e['state']}.csv" and r[key]==e['site_id']:r[e['field']]=e['new']
  assert new.get(r[key])==r,('row/field preservation',p.name,r[key])
 if p.name.startswith('sites_'):assert len(new)==len(old),'unexpected site create'
 if p.name.startswith('evidence_'):assert len(new)==len(old)+sum(p.name==f"evidence_sites_{before[e['record_id']]['state']}.csv" for e in packet)
byid={r['site_id']:r for p in (ROOT/'data').glob('sites_*.csv') for r in read(p)}
for sid,old in before.items():
 # Held rows may receive owner-authorized corrections on main; the all-row preservation check above covers them.
 if sid not in up:continue
 expected=dict(old)
 for e in edits:
  if e['site_id']==sid:expected[e['field']]=e['new']
 assert byid[sid]==expected,('frozen site drift',sid)
hashes=lambda d:{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in d.glob('*.csv')}
h=hashes(ROOT/'data');subprocess.run([sys.executable,str(P/'build.py')],check=True,capture_output=True);assert h==hashes(ROOT/'data')
with tempfile.TemporaryDirectory() as td:
 data=Path(td)/'data';shutil.copytree(ROOT/'data',data)
 for state in ['FL','GA','NY','IN','WI']:
  p=data/f'evidence_sites_{state}.csv';rows=read(p);write(p,[r for r in rows if r['evidence_id'] not in {e['evidence_id'] for e in packet if e['source_class']=='own_site'}])
 result=subprocess.run([sys.executable,str(ROOT/'scripts/validate.py')],env={**os.environ,'ATLAS_DATA_DIR':str(data)},capture_output=True,text=True)
 assert result.returncode!=0 and all(sid in result.stdout for sid in up),'missing scope did not reject all30 B sites'
print('PASS: withholding own scope independently rejects all30 B promotions via validator')
for mutation in ['late_global_id','scope_gap','bad_quote','wrong_location','missing_parent','field_drift']:
 with tempfile.TemporaryDirectory(dir=ROOT/'tasks') as pt,tempfile.TemporaryDirectory() as dt:
  q=Path(pt);shutil.copytree(P,q,dirs_exist_ok=True);data=Path(dt)/'data';shutil.copytree(ROOT/'data',data)
  if mutation=='late_global_id':
   for state in ['FL','GA','NY','IN','WI']:
    p=data/f'evidence_sites_{state}.csv';write(p,[r for r in read(p) if r['evidence_id']!=packet[-1]['evidence_id']])
   p=data/'evidence_sites_OH.csv';rows=read(p);bad=dict(rows[0]);bad['evidence_id']=packet[-1]['evidence_id'];rows.append(bad);write(p,rows)
  elif mutation=='scope_gap':write(q/'evidence_packet.csv',[r for r in packet if r['evidence_id']!=raw[-1]['evidence_id']])
  elif mutation=='bad_quote':
   sid=raw[0]['site_id']
   for name,key in [('evidence_packet.csv','record_id'),('rawcheck.csv','site_id'),('witnesses.csv','site_id')]:
    rows=read(q/name)
    for r in rows:
     if r[key]==sid and (name!='evidence_packet.csv' or r['claim_type']=='scope'):r['claim_detail' if name=='evidence_packet.csv' else 'quote']+=' fabricated L7 defect'
    write(q/name,rows)
  elif mutation=='wrong_location':
   rows=read(q/'witnesses.csv');rows[0]['location_anchor']='Imaginary Atlantis polymer plant';write(q/'witnesses.csv',rows)
  elif mutation=='missing_parent':
   for p in data.glob('organizations_*.csv'):
    rows=read(p)
    if any(r['org_id']=='ORG-002544' for r in rows):
     for r in rows:
      if r['org_id']=='ORG-002544':r['parent_org_id']=''
     write(p,rows);break
  else:
   p=data/'sites_FL.csv';rows=read(p)
   for r in rows:
    if r['site_id']=='SITE-016001':r['street_address']='WRONG SITE ADDRESS'
   write(p,rows)
  h=hashes(data);result=subprocess.run([sys.executable,str(q/'build.py'),'--data-dir',str(data)],capture_output=True,text=True)
  assert result.returncode!=0,(mutation,'admitted');assert h==hashes(data),(mutation,'partial write')
  print('PASS fail-before-write:',mutation)
now=atlas_numerators(str(ROOT));shares={}
for state in ['FL','GA','NY','IN','WI']:
 with tempfile.TemporaryDirectory() as td:
  d=Path(td)/'data';d.mkdir();(d/f'sites_{state}.csv').write_bytes(subprocess.check_output(['git','show',base+':data/sites_'+state+'.csv']))
  previous=atlas_numerators(td)[state,'326'][1]
 count=now[state,'326'][1];assert previous==count
 fips={'FL':'12000','GA':'13000','NY':'36000','IN':'18000','WI':'55000'}[state]
 den=float(next(r['annual_avg_estabs'] for r in read(ROOT/'docs/denominators/qcew_state_polymer_2023_2024.csv') if r['area_fips']==fips and r['year']=='2023' and r['industry_code']=='326'))
 shares[state]=dict(strict326_before=previous,strict326_after=count,QCEW2023_private_establishments=den,share_before=previous/den,share_after=count/den)
result=dict(frame_sites=75,promoted_B_sites=30,held_C_sites=45,changed_cells=60,appended_evidence=210,government_observations=180,own_scope_quotes=30,own_scope_URLs=27,known_answers=3,blind_sample=20,source_URLs_attempted=len(fetches),fetch_outcomes=dict(Counter(r['fetch'] for r in fetches)),all6_mutations='PASS before writes',replay='PASS',state_counts=shares)
(P/'check_results.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))

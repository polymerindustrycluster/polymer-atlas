"""Federal-pass boundary/replay and fail-before-write mutations, in an isolated data tree."""
import contextlib,hashlib,io,shutil,tempfile
from pathlib import Path
import build
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 root=build.ROOT;selected,links,verdicts,ev,transcription=build.plan()
 identity_known=build.read(build.TASK/'known_identity.csv')
 assert len(identity_known)==3 and all(r['result']=='PASS' and r['negative_wrong_operator']=='rejected' for r in identity_known)
 frame=build.read(build.TASK/'frame.csv')
 assert [r['reserved_evidence_id'] for r in frame]==[f'EVD-{153000+i:06d}' for i in range(819)]
 assert {r['site_id'] for r in selected}=={r['site_id'] for r in build.read(build.TASK/'selection.csv')}
 for name,raw in [('Lincoln Electric','LINCOLN ELECTRIC CO'),('ABC, LLC','ABC INC'),('The Parker Corporation','PARKER INC')]:
  assert build.identity(dict(held_legal_name=name,held_trade_names=''),dict(FacilityName=raw))
 assert build.identity(dict(held_legal_name='Held Parent',held_trade_names='Old Registrant;Other Name'),dict(FacilityName='OLD REGISTRANT INC'))
 assert not build.identity(dict(held_legal_name='Held Parent',held_trade_names=''),dict(FacilityName='Different Operator'))
 assert not build.identity(dict(held_legal_name='ABC Polymers',held_trade_names=''),dict(FacilityName='ABC Plastics'))
 audit=build.read(build.TASK/'audit.csv')
 import random
 proposed=build.read(build.TASK/'evidence_proposed.csv')
 sample=random.Random(20261106).sample(sorted(proposed,key=lambda e:e['record_id']),min(30,len(proposed)))
 assert {r['site_id'] for r in audit}=={e['record_id'] for e in sample} and len(audit)==len(sample)
 assert all(r['bulk_transcription']=='PASS' and not r['error'] for r in audit if r['site_id'] in {e['record_id'] for e in ev})

 assert build.note_streets(dict(city='South Euclid',notes='Street (per Grok): 4321 Glenridge Road. county UNVERIFIED — Grok county_check=TRUE'))==['4321 Glenridge Road']
 assert len(ev)==6,'frozen bulk-source yield changed; inspect before revising'
 assert len(build.read(build.TASK/'bulk_known.csv'))==3
 import json,re,subprocess,csv
 original=list(csv.DictReader(subprocess.check_output(['git','show','a9af228:tasks/oh-street-address-cu-2026-11-06/frame.csv'],text=True).splitlines()))
 assert [(r['site_id'],r['reserved_evidence_id']) for r in frame]==[(r['site_id'],r['reserved_evidence_id']) for r in original]
 prior=build.read(build.TASK/'prior_worked.csv')
 assert len(prior)==len({r['site_id'] for r in prior})==140 and not {r['site_id'] for r in prior}&{r['site_id'] for r in selected}
 manifest=json.loads((build.TASK/'bulk_manifest.json').read_text())['source']
 for e in ev:
  assert e['source_class']=='registry' and e['tier_effect']=='supports_C' and e['source_ref']==manifest['url'] and e['observed_date']==manifest['date'][:10]
  assert 'retrieval date not address-effective date' in e['notes'] and re.search(r'REGISTRY_ID \d{12};',e['notes'])
 for sid in ('SITE-000184','SITE-000185','SITE-000205','SITE-000234','SITE-000256','SITE-000282','SITE-000297','SITE-000309','SITE-000333','SITE-000355','SITE-000360','SITE-000387','SITE-000393','SITE-000414','SITE-000427'):
  assert next(v for v in verdicts if v['site_id']==sid)['verdict']=='STILL_UNCERTAIN',sid
 clark=next(r for r in selected if r['site_id']=='SITE-000197')
 assert build.address_warning(clark),'actual Clark deferred-address warning missed'
 assert next(v for v in verdicts if v['site_id']=='SITE-000197')['verdict']=='STILL_UNCERTAIN'
 assert build.address_warning(dict(notes='See org note for address.',held_org_notes='ADDRESS DISCREPANCY: alternatives; resolve at verification.'))
 assert not build.address_warning(dict(notes='NAICS codes conflict; Street: 123 Main Road.',held_org_notes=''))
 expected=len(ev)
 with tempfile.TemporaryDirectory() as tmp:
  build.ROOT=Path(tmp);(build.ROOT/'data').mkdir()
  for p in (root/'data').glob('evidence_*.csv'):shutil.copyfile(p,build.ROOT/'data'/p.name)
  for p in (root/'data').glob('organizations_*.csv'):shutil.copyfile(p,build.ROOT/'data'/p.name)
  shutil.copyfile(root/'data/ecosystem.csv',build.ROOT/'data/ecosystem.csv')
  for name in ('sites_OH.csv','registry_links.csv'):shutil.copyfile(root/'data'/name,build.ROOT/'data'/name)
  for name in ('establishments.csv','site_matches.csv'):
   p=build.ROOT/'tasks/osha-ita-2026-11-01'/name;p.parent.mkdir(parents=True,exist_ok=True)
   shutil.copyfile(root/'tasks/osha-ita-2026-11-01'/name,p)
  frozen={s['site_id']:s for s in selected};before=build.read(build.ROOT/'data/sites_OH.csv')
  for s in before:
   if s['site_id'] in frozen:
    for k in s:s[k]=frozen[s['site_id']][k]
  build.write(build.ROOT/'data/sites_OH.csv',before)
  p=build.ROOT/'data/evidence_sites_OH.csv';old_evidence=[r for r in build.read(p) if r['created_by']!='atlas-L2-oh-address-cu-2'];build.write(p,old_evidence)
  with contextlib.redirect_stdout(io.StringIO()):build.run(apply=True)
  after=build.read(build.ROOT/'data/sites_OH.csv');changed=[]
  assert len(before)==len(after)
  for a,b in zip(before,after):
   fields={k for k in a if a[k]!=b[k]};assert fields<={'street_address','sources'},(a['site_id'],fields)
   if fields:
    changed.append(b);assert not a['street_address'] and b['street_address'] and a['verification_tier'] in ('C','U') and a['operating_status']=='active'
  assert len(changed)==expected
  paths=list((build.ROOT/'data').glob('*.csv'));hashes={p.name:digest(p) for p in paths}
  with contextlib.redirect_stdout(io.StringIO()):build.run(apply=True)
  assert hashes=={p.name:digest(p) for p in paths},'not byte-idempotent'
  saved_warning=build.address_warning;saved_read=build.read
  build.address_warning=lambda *args:False
  build.read=lambda p:[] if Path(p).name=='retired_ids.csv' else saved_read(p)
  try:
   with contextlib.redirect_stdout(io.StringIO()):build.run(apply=True)
  except AssertionError:pass
  else:raise AssertionError('original Clark admission defect bypassed frozen subset')
  finally:build.address_warning=saved_warning;build.read=saved_read
  assert hashes=={p.name:digest(p) for p in paths},'writes happened before Clark defect rejection'
  target=changed[0]
  for field,value in [('street_address','999 WRONG ROAD'),('zip','00000'),('verification_tier','A'),('operating_status','closed')]:
   original=target[field];target[field]=value;build.write(build.ROOT/'data/sites_OH.csv',after)
   hashes={p.name:digest(p) for p in paths}
   try:
    with contextlib.redirect_stdout(io.StringIO()):build.run(apply=True)
   except AssertionError:pass
   else:raise AssertionError('injected '+field+' drift silently accepted')
   assert hashes=={p.name:digest(p) for p in paths},'canonical write before drift refusal'
   target[field]=original;build.write(build.ROOT/'data/sites_OH.csv',after)
  foreign=build.ROOT/'data/evidence_sites_ZZ.csv'
  retired_row=dict(ev[-1],evidence_id='EVD-153109')
  for foreign_row in (ev[-1],retired_row):
   build.write(foreign,[foreign_row])
   paths=list((build.ROOT/'data').glob('*.csv'));hashes={p.name:digest(p) for p in paths}
   try:
    with contextlib.redirect_stdout(io.StringIO()):build.run(apply=True)
   except AssertionError:pass
   else:raise AssertionError('foreign-shard or retired evidence collision accepted')
   assert hashes=={p.name:digest(p) for p in paths},'canonical write before ID collision refusal'

 build.ROOT=root
 print(f'PASS {expected} fills; only street/sources; byte-idempotent; street/ZIP/tier/status/foreign-ID mutations reject before writes')
if __name__=='__main__':main()

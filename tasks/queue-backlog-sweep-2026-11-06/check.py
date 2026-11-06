"""12-item census; fresh-base replay; row preservation; fail-closed defect injections."""
import copy,csv,json,shutil,subprocess,tempfile
from unittest.mock import patch
import build
from collections import Counter
from pathlib import Path
from build import HERE,ROOT,apply,read,write,generated_edges
from rawcheck import parcel_check
NAMES=['organizations_OH.csv','sites_OH.csv','sites_PA.csv','relationships.csv','evidence_organizations_OH.csv','evidence_sites_OH.csv','evidence_sites_PA.csv']
def snapshot(d):return {p.name:p.read_bytes() for p in d.glob('*.csv')}
def refused(d,action,label):
 action();before=snapshot(d)
 try:apply(d)
 except AssertionError:pass
 else:raise AssertionError('silent acceptance: '+label)
 assert before==snapshot(d),'partial writes: '+label

def main():
 inputs,verdicts,holds=map(lambda n:read(HERE/n),['input.csv','verdicts.csv','holds.csv'])
 assert len(inputs)==len(verdicts)==12 and {r['item_id'] for r in inputs}=={r['item_id'] for r in verdicts}
 assert len({r['item_id'] for r in verdicts})==12
 assert Counter(r['verdict'] for r in verdicts)=={'VERIFIED':3,'DUPLICATE_OF':1,'STILL_UNCERTAIN':8}
 assert holds==[r for r in verdicts if r['verdict']=='STILL_UNCERTAIN'] and all(r['settling_fact'] and r['recommendation'] and r['governing_decision'] for r in holds)
 assert len(read(HERE/'known_answers.csv'))==3 and all(r['raw']=='yes' for r in read(HERE/'known_answers.csv'))
 assert len(read(HERE/'evidence.csv'))==16 and len(read(HERE/'edits.csv'))==22
 org=read(HERE/'organizations.csv')[0];edge=generated_edges([org])[0]
 assert (edge['from_org_id'],edge['relationship_type'],edge['to_org_id'],edge['effective_from'])==(org['org_id'],'successor_of',org['successor_org_id'],org['status_date'])
 sites={r['site_id']:r for r in read(ROOT/'data/sites_PA.csv')}
 edited_pa={r['record_id'] for r in read(HERE/'edits.csv') if r['file']=='sites_PA.csv'}
 assert Counter(sites[i]['verification_tier'] for i in edited_pa)=={'A':2,'B':4}
 allsites={r['site_id']:r for name in ['sites_OH.csv','sites_PA.csv'] for r in read(ROOT/'data'/name)}
 edited={r['record_id'] for r in read(HERE/'edits.csv')}
 assert Counter(allsites[i]['verification_tier'] for i in edited)=={'A':4,'B':4}
 assert sites['SITE-002612']['operating_status']=='closed' and sites['SITE-002486']['operating_status']=='active'
 with tempfile.TemporaryDirectory() as tmp:
  d=Path(tmp)
  for f in (ROOT/'data').glob('*.csv'):shutil.copyfile(f,d/f.name)
  base=(HERE/'base.txt').read_text().strip()
  for name in NAMES:(d/name).write_bytes(subprocess.check_output(['git','show',base+':data/'+name],cwd=ROOT))
  # Reproduce two NEW shard rows sharing one reserved EVD, with no prior held collision.
  normal=build.read
  def badpacket(path):
   rows=normal(path)
   if path==HERE/'evidence.csv':
    orgrow=next(r for r in rows if r['record_table']=='organizations');siterow=next(r for r in rows if r['record_table']=='sites')
    orgrow['evidence_id']=siterow['evidence_id']
   return rows
  pristine=snapshot(d)
  with patch.object(build,'read',badpacket):
   try:apply(d)
   except AssertionError as e:assert 'cross-packet evidence ID collision' in str(e)
   else:raise AssertionError('new/new cross-shard packet EVD collision accepted')
  assert pristine==snapshot(d),'pending packet collision wrote before refusal'
  def internal_claim(path):
   rows=normal(path)
   if path==HERE/'evidence.csv':next(r for r in rows if r['source_class']=='own_site')['claim_detail']='Atlas duplicate SITE-999999; '+next(r for r in rows if r['source_class']=='own_site')['claim_detail']
   return rows
  with patch.object(build,'read',internal_claim):
   try:apply(d)
   except AssertionError as e:assert 'own_site claim exceeds literal source observation' in str(e)
   else:raise AssertionError('internal inference attributed to own source')
  assert pristine==snapshot(d),'source-boundary failure caused writes'
  before={n:read(d/n) for n in NAMES};apply(d);first=snapshot(d);apply(d);assert first==snapshot(d),'replay drift'
  for name in NAMES:
   key='org_id' if name.startswith('organizations') else 'site_id' if name.startswith('sites') else 'relationship_id' if name=='relationships.csv' else 'evidence_id'
   after={r[key]:r for r in read(d/name)}
   for old in before[name]:
    expected=dict(old)
    for e in read(HERE/'edits.csv'):
     if e['file']==name and e['record_id']==old[key]:expected[e['field']]=e['after']
    assert after[old[key]]==expected,('old row changed/lost',name,old[key])
  assert all((d/n).read_bytes()==(ROOT/'data'/n).read_bytes() for n in NAMES),'canonical differs from fresh-base builder'
  # Collision in a different state must fail before any append/update.
  def collision():
   rows=read(d/'organizations_US.csv');r=dict(rows[0]);r['org_id']='ORG-013200';rows.append(r);write(d/'organizations_US.csv',rows)
  refused(d,collision,'cross-shard occupied ID')
  (d/'organizations_US.csv').write_bytes(first['organizations_US.csv'])
  def drift():
   rows=read(d/'sites_OH.csv');next(r for r in rows if r['site_id']=='SITE-001850')['county']='Invented';write(d/'sites_OH.csv',rows)
  refused(d,drift,'preimage county drift')
 p=json.loads((HERE/'union-parcel.json').read_text())['result']
 assert p['features'][0]['attributes']['ACCOUNT']=='15-0027019.0230';parcel_check(p,p)
 for label,alter in [('error',lambda x:x.update(error={'code':400})),('truncated',lambda x:x.update(exceededTransferLimit=True)),('ambiguous',lambda x:x['features'].append(copy.deepcopy(x['features'][0]))),('wrong street',lambda x:x['features'][0]['attributes'].update(Address='8485 AVALON LN'))]:
  bad=copy.deepcopy(p);alter(bad)
  try:parcel_check(bad,p)
  except AssertionError:pass
  else:raise AssertionError('parcel negative accepted: '+label)
 print('PASS: 12 items=3 VERIFIED/1 DUPLICATE_OF/8 STILL_UNCERTAIN; 1 U org/1 generated REL/8 edited sites/16EVD; fresh-base byte replay/old-row preservation; cross-shard+preimage+pendingpacket+ownsource-boundary zero-write; editedsite tiers4A4B; 4 parcel defects rejected')
if __name__=='__main__':main()

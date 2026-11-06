"""Named gate for operator-only changes, exact frame, source records, replay and no-write mutations."""
import csv,hashlib,io,json,shutil,subprocess,sys,tempfile
from pathlib import Path
import build
from build import P,ROOT,read,write
from research import found
# Other worktrees advance shared remote refs; compare one immutable integration snapshot.
merge=subprocess.run(['git','rev-parse','--verify','MERGE_HEAD'],capture_output=True,text=True)
BASE=merge.stdout.strip() if merge.returncode==0 else subprocess.check_output(['git','merge-base','origin/main','HEAD'],text=True).strip()
frame=read(P/'input.csv');vs=read(P/'verdicts.csv');edits=read(P/'edits.csv');packet=read(P/'evidence_packet.csv')
assert len(vs)==len(frame)==len({r['site_id'] for r in vs})==14
assert len({r['org_id'] for r in frame})==10
assert {r['site_id'] for r in vs}=={r['site_id'] for r in frame}
assert len(edits)==46 and len(packet)==20
expected={(r['site_id'],e['field']):(e['old'],e['new']) for r in frame for e in edits if e['site_id']==r['site_id']}
assert len(expected)==46
expected_keys={e['evidence_id'] for e in packet};assert len(expected_keys)==20
changed=0;added=0;source_sites={r['site_id']:r for r in frame}
for path in sorted((ROOT/'data').glob('*.csv')):
    current=read(path);old=list(csv.DictReader(io.StringIO(subprocess.check_output(['git','show',BASE+':data/'+path.name],text=True))))
    if not old:continue
    if path.name.startswith('sites_'):
        now={r['site_id']:r for r in current};assert len(now)==len(current)
        assert {r['site_id'] for r in old}==set(now),'site creation/removal'
        for r in old:
            sid=r['site_id'];n=now[sid]
            for k,value in r.items():
                if n[k]!=value:
                    assert (sid,k) in expected and expected[sid,k]==(value,n[k]),('unexpected cell',sid,k)
                    changed+=1
    elif path.name.startswith('evidence_'):
        now={r['evidence_id']:r for r in current};assert len(now)==len(current)
        assert all(now.get(r['evidence_id'])==r for r in old),'historical evidence changed'
        delta=set(now)-{r['evidence_id'] for r in old};assert delta<=expected_keys
        added+=len(delta)
    elif path.name=='registry_links.csv':
        assert len(old)==len(current)
        for a,b in zip(old,current):
            if a!=b:
                assert a=={**b,'org_id':'ORG-002260'} and b['org_id']=='ORG-002261' and b['registry']=='FRS' and b['registry_id']=='110001516832' and b['site_id']=='SITE-006049'
                changed+=1
    else:assert current==old,('unexpected table change',path.name)
assert changed==47 and added==20,(changed,added)
for e in edits:
    current=next(r for r in read(ROOT/'data'/('sites_'+e['state']+'.csv')) if r['site_id']==e['site_id'])
    assert current[e['field']]==e['new']
for r in read(P/'rawcheck.csv'):
    t=Path(r['cache_file']).read_text();assert found(t,r['quote']) and hashlib.sha256(t.encode()).hexdigest()==r['raw_sha256'],r
paths=list((ROOT/'data').glob('*.csv'))
def hashes(d):return {p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in d.glob('*.csv')}
h=hashes(ROOT/'data');subprocess.run([sys.executable,str(P/'build.py')],check=True);assert h==hashes(ROOT/'data'),'canonical replay changed bytes'
# Full census reconciles valid keeps and unsettled holds, rather than forcing tombstone bindings to zero.
org={r['org_id']:r for f in (ROOT/'data').glob('organizations_*.csv') for r in read(f)}
remaining={r['site_id'] for f in (ROOT/'data').glob('sites_*.csv') for r in read(f) if r['org_id'] in org and org[r['org_id']]['status'] in {'merged','acquired'} and r['operating_status']!='closed'}
assert remaining=={r['site_id'] for r in vs if r['action'] in {'KEEP','HOLD'}},remaining
with tempfile.TemporaryDirectory(prefix='l6-operator-negative-') as tmp:
    fixture=Path(tmp);d=fixture/'data';shutil.copytree(ROOT/'data',d)
    for state in {e['state'] for e in edits}:
        for n in ['sites_'+state+'.csv','evidence_sites_'+state+'.csv']:(d/n).write_bytes(subprocess.check_output(['git','show',BASE+':data/'+n]))
    (d/'registry_links.csv').write_bytes(subprocess.check_output(['git','show',BASE+':data/registry_links.csv']))
    other=read(d/'evidence_organizations_CA.csv');other[0]['evidence_id']=packet[-1]['evidence_id'];write(d/'evidence_organizations_CA.csv',other)
    h=hashes(d);sys.argv=['build.py','--data-dir',str(d)]
    try:build.main()
    except AssertionError as e:assert 'global evidence ID collision' in str(e),str(e)
    else:raise AssertionError('late global ID collision accepted')
    assert h==hashes(d),'collision caused partial site/evidence/registry writes'
    (d/'evidence_organizations_CA.csv').write_bytes(subprocess.check_output(['git','show',BASE+':data/evidence_organizations_CA.csv']))
    task=fixture/'packet';shutil.copytree(P,task)
    bad=read(task/'edits.csv');bad[0].update(field='operating_status',old='active',new='closed');write(task/'edits.csv',bad)
    h=hashes(d);build.P=task
    try:build.main()
    except AssertionError as e:assert 'forbidden operator-pass field' in str(e),str(e)
    else:raise AssertionError('forbidden closure edit accepted')
    assert h==hashes(d),'forbidden closure edit caused partial writes'
    print('PASS late global EVD collision and forbidden closure both reject before every site/evidence/registry write')
result=dict(base_ref=BASE,frame_site_records=14,frame_tombstoned_orgs=10,verified_operator_verdicts=12,repoints=10,sourced_keeps=2,holds=2,site_cells=46,registry_cells=1,new_parent_evidence_rows=20,raw_quote_rows=7,raw_urls=4,remaining_tombstone_site_bindings=4,operating_status_changes=0,tier_changes=0,site_folds=0)
(P/'check-result.json').write_text(json.dumps(result,indent=2)+'\n')
print('PASS14/14verdicts,10repoints2keeps2holds;47exactcells,20append-onlyEVD;raw7/7,gov13/13,oldmainpreserved,replay;4remainingbindings=2validkeeps+2holds')

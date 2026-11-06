"""Exact frozen cohort, raw/government census, field boundary, replay and no-write controls."""
import csv,hashlib,io,json,os,shutil,subprocess,sys,tempfile
from pathlib import Path
import build
from build import P,ROOT,read,write
from research import found
sys.path.insert(0,str(ROOT/'scripts'))
from build_qcew_denominators import atlas_numerators
D=Path(os.environ.get('ATLAS_DATA_DIR',ROOT/'data'))
merge_head=subprocess.run(['git','rev-parse','--verify','MERGE_HEAD'],capture_output=True,text=True)
BASE=merge_head.stdout.strip() if merge_head.returncode==0 else subprocess.check_output(['git','merge-base','origin/main','HEAD'],text=True).strip()
frame=read(P/'input.csv');vs=read(P/'verdicts.csv');edits=read(P/'edits.csv');packet=read(P/'evidence_packet.csv');raw=read(P/'rawcheck.csv')
upgraded={r['site_id'] for r in vs if r['verdict']=='VERIFIED'}
assert len(frame)==len(vs)==len({r['site_id'] for r in vs})==38 and len(upgraded)==11
assert len(edits)==22 and len(packet)==57 and len(raw)==13
assert all(r['settling_fact'] for r in vs if r['verdict']=='STILL_UNCERTAIN')
expected={(e['site_id'],e['field']):(e['old'],e['new']) for e in edits};assert len(expected)==22
changed=[];added=[]
for path in sorted(D.glob('*.csv')):
    old=list(csv.DictReader(io.StringIO(subprocess.check_output(['git','show',BASE+':data/'+path.name],text=True))))
    current=read(path)
    if path.name=='sites_TX.csv':
        before={r['site_id']:r for r in old};after={r['site_id']:r for r in current};assert before.keys()==after.keys()
        for sid,r in before.items():
            for k,v in r.items():
                if v!=after[sid][k]:assert expected.get((sid,k))==(v,after[sid][k]),('unauthorized cell',sid,k);changed.append((sid,k))
    elif path.name=='evidence_sites_TX.csv':
        before={r['evidence_id']:r for r in old};after={r['evidence_id']:r for r in current}
        assert all(after.get(k)==r for k,r in before.items()),'old evidence changed'
        added=[r for k,r in after.items() if k not in before];assert added==packet
    else:assert current==old,('unrelated canonical change',path.name)
assert len(changed)==22 and len(added)==57
h=lambda d:{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in d.glob('*.csv')}
before=h(D);subprocess.run([sys.executable,str(P/'build.py'),'--data-dir',str(D)],check=True);assert before==h(D),'replay changed canonical bytes'
# Run the real builder against each semantic/control mutation and compare every CSV hash.
with tempfile.TemporaryDirectory(prefix='l6-txquality-negative-') as tmp:
    d=Path(tmp)/'data';shutil.copytree(D,d)
    ev=read(d/'evidence_sites_TX.csv');keep=[r for r in ev if r['evidence_id'] not in {e['evidence_id'] for e in packet if e['source_class']=='own_site'}]
    assert len(ev)-len(keep)==13;write(d/'evidence_sites_TX.csv',keep)
    r=subprocess.run([sys.executable,str(ROOT/'scripts/validate.py')],env={**os.environ,'ATLAS_DATA_DIR':str(d)},capture_output=True,text=True)
    assert r.returncode!=0 and all(s in r.stdout for s in upgraded),r.stdout[-3000:]
    print('PASS removal of13own-scope rows rejects all11Bpromotions')
    # An identical-payload final planned ID in the wrong shard is still a collision.
    write(d/'evidence_sites_TX.csv',[r for r in ev if r['evidence_id'] not in {e['evidence_id'] for e in packet}])
    other=read(d/'evidence_sites_OH.csv');other.append(packet[-1]);write(d/'evidence_sites_OH.csv',other)
    before=h(d);sys.argv=['build.py','--data-dir',str(d)]
    try:build.main()
    except AssertionError as e:assert 'global evidence ID collision' in str(e),str(e)
    else:raise AssertionError('identical-payload wrong-shard collision accepted')
    assert before==h(d),'collision caused partial writes'
    write(d/'evidence_sites_OH.csv',other[:-1]);rs=read(d/'sites_TX.csv');next(r for r in rs if r['site_id']==packet[0]['record_id'])['city']='Ontario';write(d/'sites_TX.csv',rs)
    before=h(d)
    try:build.main()
    except AssertionError as e:assert 'frozen site drift' in str(e),str(e)
    else:raise AssertionError('wrong-city site binding accepted')
    assert before==h(d),'wrong city caused partial writes'
    print('PASS identical-payload wrong-shard final ID and wrong-city binding reject before every CSV write')
for r in raw:
    t=Path(r['cache_file']).read_text();assert found(t,r['quote']) and hashlib.sha256(t.encode()).hexdigest()==r['raw_sha256']
assert not found('manufacturing in Garland Texas','manufacturing in Ontario')
assert not found('flexible packaging converter','converter flexible packaging')
with tempfile.TemporaryDirectory(prefix='l6-txquality-qcew-') as tmp:
    d=Path(tmp)/'data';d.mkdir();(d/'sites_TX.csv').write_bytes(subprocess.check_output(['git','show',BASE+':data/sites_TX.csv']))
    baseline=atlas_numerators(tmp)['TX','326'][1]
    shutil.copyfile(D/'sites_TX.csv',d/'sites_TX.csv');count=atlas_numerators(tmp)['TX','326'][1]
assert count==baseline
(P/'check-result.json').write_text(json.dumps(dict(base_ref=BASE,frame_C_site_records=38,upgraded_B_site_records=11,held_C_site_records=27,changed_site_cells=22,append_only_evidence_rows=57,raw_quotes=13,raw_urls=11,government_records=11,strict326_before=baseline,strict326_after=count,qcew_denominator=953,strict_share_pct=100*count/953),indent=2)+'\n')
print('PASS38exactverdicts/11upgrades27holds;22cells57EVD;raw13/gov11/alloldmainpreserved/replay;strictTX326',baseline,'→',count,'/953')

"""Named gate: exact frame/cell boundary, append-only evidence, raw quotes, replay, adverse mutations."""
import csv,hashlib,io,json,os,shutil,subprocess,sys,tempfile
from pathlib import Path
import build
from build import P,ROOT,read,write
from research import found
sys.path.insert(0,str(ROOT/'scripts'))
from build_qcew_denominators import atlas_numerators
frame=read(P/'input.csv');verdicts=read(P/'verdicts.csv');packet=read(P/'evidence_packet.csv');edits=read(P/'edits.csv')
assert len(frame)==len(verdicts)==len({r['site_id'] for r in verdicts})==16
upgraded={r['site_id'] for r in verdicts if r['verdict']=='VERIFIED'};assert len(upgraded)==4
before={r['site_id']:r for r in frame};after={r['site_id']:r for r in read(ROOT/'data/sites_CA.csv')}
for e in edits:assert before[e['site_id']][e['field']]==e['old'] and after[e['site_id']][e['field']]==e['new']
for sid,r in before.items():
    expected={k:v for k,v in r.items() if not k.startswith('org_')}
    expected['org_id']=r['org_id']
    for e in edits:
        if e['site_id']==sid:expected[e['field']]=e['new']
    assert after[sid]==expected,('unexpected field change',sid)
# Parsed main rows stay identical except the eight enumerated cells; evidence is append-only.
for name,col in [('sites_CA.csv','site_id'),('evidence_sites_CA.csv','evidence_id')]:
    old=list(csv.DictReader(io.StringIO(subprocess.check_output(['git','show','origin/main:data/'+name],text=True))))
    new={r[col]:r for r in read(ROOT/'data'/name)}
    for r in old:
        for e in edits:
            if name=='sites_CA.csv' and e['site_id']==r[col]:r[e['field']]=e['new']
        assert new[r[col]]==r,('changed main row',name,r[col])
for r in read(P/'rawcheck.csv'):
    text=Path(r['cache_file']).read_text();assert found(text,r['quote']),r
    assert hashlib.sha256(text.encode()).hexdigest()==r['raw_sha256']
assert not found('manufacturing space in Richmond','manufacturing space in Ontario'),'wrong-city matcher control'
assert not found('high-grade vinyl ester resin','ester high-grade resin'),'word order control'
paths=[ROOT/'data/sites_CA.csv',ROOT/'data/evidence_sites_CA.csv'];hashes=lambda:[hashlib.sha256(p.read_bytes()).hexdigest() for p in paths]
h=hashes();subprocess.run([sys.executable,str(P/'build.py')],check=True);assert h==hashes(),'replay changed canonical bytes'
with tempfile.TemporaryDirectory(prefix='l6-quality-check-') as tmp:
    d=Path(tmp)/'data';shutil.copytree(ROOT/'data',d)
    ev=read(d/'evidence_sites_CA.csv');keep=[r for r in ev if not (r['record_id'] in upgraded and r['source_class']=='own_site' and r['claim_type']=='scope' and r['evidence_id'].startswith('EVD-188'))]
    assert len(ev)-len(keep)==5
    write(d/'evidence_sites_CA.csv',keep)
    r=subprocess.run([sys.executable,str(ROOT/'scripts/validate.py')],env={**os.environ,'ATLAS_DATA_DIR':str(d)},capture_output=True,text=True)
    assert r.returncode!=0 and all(sid in r.stdout for sid in upgraded),r.stdout[-3500:]
    print('PASS removing 5 own scope rows rejects all4 B promotions via validator')
    # Collision on the final planned row must reject before any shard write.
    write(d/'evidence_sites_CA.csv',[r for r in ev if int(r['evidence_id'][4:]) not in range(188000,190000)])
    other=read(d/'evidence_sites_OH.csv');other[0]['evidence_id']=packet[-1]['evidence_id'];write(d/'evidence_sites_OH.csv',other)
    all_hash=lambda:{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in d.glob('*.csv')}
    h=all_hash();sys.argv=['build.py','--data-dir',str(d)]
    try:build.main()
    except AssertionError as e:assert 'global evidence ID collision' in str(e),str(e)
    else:raise AssertionError('late cross-shard collision accepted')
    assert h==all_hash(),'collision caused partial writes'
    print('PASS final-EVD collision across shards rejected before any write')
n=atlas_numerators(str(ROOT));count=n['CA','326'][1]
with tempfile.TemporaryDirectory(prefix='l6-quality-qcew-') as tmp:
    d=Path(tmp)/'data';d.mkdir()
    (d/'sites_CA.csv').write_bytes(subprocess.check_output(['git','show','origin/main:data/sites_CA.csv']))
    baseline=atlas_numerators(tmp)['CA','326'][1]
assert count==baseline,('unexpected strict establishment gain',baseline,count)
(P/'check-result.json').write_text(json.dumps(dict(frame_C_sites=16,promoted_B_sites=4,held_C_sites=12,changed_cells=8,appended_evidence=22,raw_urls=5,raw_quotes=6,strict326_before=baseline,strict326_after=count,qcew_denominator=1306,strict_share_pct=100*count/1306),indent=2)+'\n')
print('PASS 16 exact verdicts / 4 upgrades / 12 holds; 8 cells,22EVD; old main rows preserved; raw6/6; replay; strict326',baseline,'→',count,'/1306')

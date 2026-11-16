#!/usr/bin/env python3
"""Recompute frame/yield, inspect the whole cell delta, and reject injected defects."""
import copy
import io
import json
import subprocess
import tempfile
import shutil
import hashlib
from collections import Counter
import build as b
from regions import PIC18
H,R=b.HERE,b.ROOT
base=(H/'base.txt').read_text().strip()
def before(path):
    return list(b.csv.DictReader(io.StringIO(subprocess.check_output(['git','show',f'{base}:{path}'],cwd=R,text=True))))
def run():
    packet=json.loads((H/'proposals.json').read_text());b.validate_packet(packet)
    orgs={r['org_id']:r for f in (R/'data').glob('organizations_*.csv') for r in before('data/'+f.name)}
    sites=[r for f in (R/'data').glob('sites_*.csv') for r in before('data/'+f.name)]
    manifest=b.read(b.CORPUS/'manifest.csv')
    frame={r['org_id'] for r in sites if r['state']=='OH' and r['county'] in PIC18 and r['operating_status']=='active'}
    frame={x for x in frame if x in orgs and not orgs[x]['parent_org_id'] and not orgs[x]['ultimate_parent_name']}&{r['org_id'] for r in manifest if r['status']=='ok' and r['text_file']}
    assert sorted(frame)==json.loads((H/'frame.json').read_text())
    expected={(p['org_id'],p['field']):p['value'] for p in packet};actual={}
    for f in (R/'data').glob('organizations_*.csv'):
        for row in b.read(f):
            old=orgs[row['org_id']]
            for k,v in row.items():
                if old[k]!=v:actual[row['org_id'],k]=v
    assert actual==expected and {p['org_id'] for p in packet}<=frame
    evidence=[e for f in (R/'data').glob('evidence_organizations_*.csv') for e in b.read(f) if e['created_by']=='atlas-w16-parents']
    assert len(evidence)==len(packet)
    for i,p in enumerate(packet):
        e=next(e for e in evidence if e['evidence_id']==f'EVD-{384000+i:06d}')
        assert e['record_id']==p['org_id'] and e['source_ref']==p['url'] and p['quote'] in e['claim_detail']
    dispositions=b.read(H/'dispositions.csv')
    assert len(dispositions)==len(frame) and {d['org_id'] for d in dispositions}==frame
    assert Counter(d['disposition'] for d in dispositions)=={'applied':len(packet),'held':len(frame)-len(packet)}
    readme=(H/'README.md').read_text()
    for claim in [f'**{len(frame)} organizations**',f'**{len(packet)} parent fills**',f'**{len(frame)-len(packet)} held organizations**']:assert claim in readme
    for defect in ('quote','text_sha256','field'):
        bad=copy.deepcopy(packet);bad[0][defect]={'quote':'invented nonpresent parent witness zzzfake','text_sha256':'bad','field':'sources'}[defect]
        try:b.validate_packet(bad)
        except AssertionError:pass
        else:raise AssertionError('silent pass: '+defect)
    with tempfile.TemporaryDirectory() as td:
        data=b.Path(td)
        for f in (R/'data').glob('*.csv'):
            if f.name.startswith(('organizations_','evidence_organizations_')) or f.name=='relationships.csv':shutil.copy2(f,data/f.name)
        hashes={f.name:hashlib.sha256(f.read_bytes()).hexdigest() for f in data.iterdir()}
        subprocess.run(['python3',str(H/'build.py'),td],check=True)
        assert hashes=={f.name:hashlib.sha256(f.read_bytes()).hexdigest() for f in data.iterdir()}
    print('PASS: frame',len(frame),'applied',len(packet),'held',len(frame)-len(packet),'tiers',dict(Counter(orgs[p['org_id']]['verification_tier'] for p in packet)),'3/3 injected defects rejected; idempotent')
if __name__=='__main__':run()

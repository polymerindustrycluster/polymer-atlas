"""Apply only frozen C→B cells and append evidence, refusing all collisions before writes."""
import argparse,csv,sys
from pathlib import Path
P=Path(__file__).resolve().parent;ROOT=P.parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from shard_io import append_sorted

def read(p):
    with open(p,newline='',encoding='utf-8-sig') as f:return list(csv.DictReader(f))

def write(p,rows):
    with open(p,'w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=rows[0],lineterminator='\n');w.writeheader();w.writerows(rows)

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--data-dir',type=Path,default=ROOT/'data');a=ap.parse_args()
    packet=read(P/'evidence_packet.csv');edits=read(P/'edits.csv');verdicts=read(P/'verdicts.csv');frame=read(P/'input.csv')
    assert len(frame)==len(verdicts)==len({r['site_id'] for r in verdicts})==16
    assert {r['site_id'] for r in frame}=={r['site_id'] for r in verdicts}
    upgraded={r['site_id'] for r in verdicts if r['verdict']=='VERIFIED'}
    assert len(upgraded)==4 and {e['site_id'] for e in edits}==upgraded
    assert len(packet)==len({e['evidence_id'] for e in packet})==22
    assert all(188000<=int(e['evidence_id'][4:])<=189999 for e in packet)
    sites=read(a.data_dir/'sites_CA.csv');byid={r['site_id']:r for r in sites};assert len(byid)==len(sites)
    all_ev=[(f.name,e) for f in a.data_dir.glob('evidence_*.csv') for e in read(f)]
    assert len(all_ev)==len({e['evidence_id'] for _,e in all_ev}),'existing duplicate evidence IDs'
    held={e['evidence_id']:(name,e) for name,e in all_ev}
    for e in packet:
        if e['evidence_id'] in held:assert held[e['evidence_id']]==('evidence_sites_CA.csv',e),'global evidence ID collision'
    for sid in upgraded:
        es=[e for e in packet if e['record_id']==sid]
        assert {'existence','address','code','scope','parent'}<={e['claim_type'] for e in es},('must-have gap',sid)
        assert any(e['source_class']=='own_site' and e['claim_type']=='scope' for e in es),('own scope gap',sid)
        assert all(e['tier_effect']=='supports_B' for e in es)
    raw=read(P/'rawcheck.csv')
    assert all(e['claim_detail']==r['quote'] and r['raw_check']=='PASS' for e in packet if e['source_class']=='own_site' for r in [next(r for r in raw if r['site_id']==e['record_id'] and r['quote']==e['claim_detail'] and r['source_ref']==e['source_ref'])])
    orgs={r['org_id']:r for f in a.data_dir.glob('organizations_*.csv') for r in read(f)}
    assert orgs[byid['SITE-014007']['org_id']]['ultimate_parent_name']=='Avantor, Inc.','B-PARENT changed'
    assert byid['SITE-014017']['org_id']=='ORG-010009'
    for e in edits:
        assert e['field'] in {'verification_tier','sources'}
        r=byid[e['site_id']];assert r[e['field']] in {e['old'],e['new']},('field drift',e)
        r[e['field']]=e['new']
    pending=[e for e in packet if e['evidence_id'] not in held]
    # Every drift, claim gap and global collision is rejected before either shard is written.
    write(a.data_dir/'sites_CA.csv',sites)
    if pending:append_sorted(a.data_dir/'evidence_sites_CA.csv',pending,'evidence_id')
    print('PASS: 4 C→B sites, 8 cells, 22 evidence observations; append-only evidence and replay safe.')
if __name__=='__main__':main()

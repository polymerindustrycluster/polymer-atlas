"""Restate only the frozen Texas C→B cells; preflight all claims and IDs before writes."""
import argparse,csv,hashlib,json,sys
from pathlib import Path
from research import found
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
    frame=read(P/'input.csv');vs=read(P/'verdicts.csv');edits=read(P/'edits.csv');packet=read(P/'evidence_packet.csv');raw=read(P/'rawcheck.csv');gov=read(P/'government-review.csv')
    assert len(frame)==len(vs)==len({v['site_id'] for v in vs})==38
    assert {r['site_id'] for r in frame}=={v['site_id'] for v in vs}
    assert all(v['verdict'] in {'VERIFIED','STILL_UNCERTAIN'} for v in vs)
    upgraded={v['site_id'] for v in vs if v['verdict']=='VERIFIED'}
    assert len(upgraded)==10 and {e['site_id'] for e in edits}==upgraded and len(edits)==20
    assert len(packet)==len({e['evidence_id'] for e in packet})==52
    assert all(188100<=int(e['evidence_id'][4:])<=188499 for e in packet)
    sites=read(a.data_dir/'sites_TX.csv');byid={r['site_id']:r for r in sites};assert len(byid)==len(sites)
    orgs={r['org_id']:r for f in a.data_dir.glob('organizations_*.csv') for r in read(f)}
    all_ev=[(f.name,e) for f in a.data_dir.glob('evidence_*.csv') for e in read(f)]
    assert len(all_ev)==len({e['evidence_id'] for _,e in all_ev}),'existing duplicate evidence IDs'
    held={e['evidence_id']:(name,e) for name,e in all_ev}
    retired=set(json.loads((P/'retired-evidence-ids.json').read_text())['retired'])
    assert not retired & {e['evidence_id'] for e in packet},'retired ID reallocated'
    assert not retired & held.keys(),'retired proposal evidence still exists'
    for e in packet:
        assert e['record_table']=='sites' and e['record_id'] in upgraded and e['tier_effect']=='supports_B'
        if e['evidence_id'] in held:assert held[e['evidence_id']]==('evidence_sites_TX.csv',e),'global evidence ID collision'
    for r in frame:
        expected={k:v for k,v in r.items() if not k.startswith('org_')};expected['org_id']=r['org_id']
        current=byid[r['site_id']]
        for e in edits:
            if e['site_id']==r['site_id']:
                assert current[e['field']] in {e['old'],e['new']},('field drift',e)
                expected[e['field']]=current[e['field']]
        assert current==expected,('frozen site drift',r['site_id'])
        o=orgs[r['org_id']]
        for k in ['legal_name','website','parent_org_id','ultimate_parent_name']:assert o[k]==r['org_'+k],('operator drift',r['site_id'],k)
    assert len(gov)==len({g['site_id'] for g in gov})==11 and upgraded<={g['site_id'] for g in gov}
    ita={r['establishment_id']:r for r in read(ROOT/'tasks/osha-ita-2026-11-01/establishments.csv')};osha={r['est_key']:r for r in read(ROOT/'tasks/osha-spine-2026-11-01/establishments.csv')}
    for g in gov:
        if g['source_kind']=='ITA':
            r=ita[g['source_id']];actual=[r[k] for k in ['company_name','establishment_name','street','city','state','zip5','naics_code','date_submitted','industry_description']]
        else:
            r=osha[g['source_id']];actual=[r['name'],r['name'],r['street'],r['city'],r['state'],r['zip'],r['naics_latest'],r['latest_inspection'],'']
        assert actual==[g[k] for k in ['operator','establishment_name','street','city','state','zip','naics','source_date','industry_description']],('government atom drift',g['site_id'])
        site=byid[g['site_id']];assert [site[k] for k in ['street_address','city','state','zip','naics_primary']]==[g[k] for k in ['street','city','state','zip','naics']]
    for sid in upgraded:
        es=[e for e in packet if e['record_id']==sid];rs=[r for r in raw if r['site_id']==sid]
        assert {'existence','address','code','scope','parent'}<={e['claim_type'] for e in es},('must-have gap',sid)
        assert rs and any(found(r['quote'],byid[sid]['city']) for r in rs),('plant city gap',sid)
        for r in rs:
            t=Path(r['cache_file']).read_text();assert r['raw_check']=='PASS' and found(t,r['quote']) and hashlib.sha256(t.encode()).hexdigest()==r['raw_sha256'],('raw witness gap',sid)
        for e in es:
            if e['source_class']=='own_site':assert any(r['quote']==e['claim_detail'] and r['source_ref']==e['source_ref'] for r in rs),('own literal gap',sid)
    for e in edits:
        assert e['field'] in {'verification_tier','sources'}
        byid[e['site_id']][e['field']]=e['new']
    pending=[e for e in packet if e['evidence_id'] not in held]
    write(a.data_dir/'sites_TX.csv',sites)
    if pending:append_sorted(a.data_dir/'evidence_sites_TX.csv',pending,'evidence_id')
    print('PASS 10C→B sites/28holds;20cells/52append-onlyEVD;government11reviewed/raw13;Dacon C/5IDsretired;all preflight before writes')
if __name__=='__main__':main()

"""Apply only evidenced operator cells; append_sorted evidence after a global no-write preflight."""
import argparse,csv,sys
from collections import defaultdict
from pathlib import Path
P=Path(__file__).resolve().parent;ROOT=P.parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from shard_io import append_sorted
from atlas import name_key
from research import found

def read(p):
    with open(p,newline='',encoding='utf-8-sig') as f:return list(csv.DictReader(f))

def write(p,rows):
    with open(p,'w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=rows[0],lineterminator='\n');w.writeheader();w.writerows(rows)

def assert_operator_names(verdicts,gov,orgs,maps,raw):
    for m in maps:
        aliases={name_key(n) for n in [orgs[m['operator_org_id']]['legal_name'],*orgs[m['operator_org_id']]['trade_names'].split(';')] if n}
        assert name_key(m['target_alias']) in aliases,'unheld mapped alias'
        assert found(m['quote'],m['source_name']+' Doing Business As '+m['target_alias']),'DBA bridge not explicit'
        assert any(r['source_ref']==m['source_ref'] and r['quote']==m['quote'] and r['raw_check']=='PASS' for r in raw),'DBA raw witness missing'
    for v in verdicts:
        if v['verdict']!='VERIFIED':continue
        o=orgs[v['operator_org_id']];aliases={name_key(n) for n in [o['legal_name'],*o['trade_names'].split(';')] if n}
        names={name_key(g[k]) for g in gov if g['site_id']==v['site_id'] for k in ['operator','establishment_name']}
        match=bool(names&aliases) or any(m['operator_org_id']==v['operator_org_id'] and name_key(m['source_name']) in names for m in maps)
        assert match,('unresolved named operator',v['site_id'],names,aliases)

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--data-dir',type=Path,default=ROOT/'data');a=ap.parse_args()
    frame=read(P/'input.csv');vs=read(P/'verdicts.csv');edits=read(P/'edits.csv');packet=read(P/'evidence_packet.csv')
    assert len(frame)==len(vs)==len({v['site_id'] for v in vs})==14
    assert {r['site_id'] for r in frame}=={v['site_id'] for v in vs}
    assert all(v['verdict'] in {'VERIFIED','STILL_UNCERTAIN'} for v in vs)
    assert sum(v['action']=='REPOINT' for v in vs)==8 and sum(v['action']=='KEEP' for v in vs)==2 and sum(v['action']=='HOLD' for v in vs)==4
    verified={v['site_id'] for v in vs if v['verdict']=='VERIFIED'};assert {e['site_id'] for e in edits}==verified
    assert len(packet)==len({e['evidence_id'] for e in packet})==18
    assert all(188500<=int(e['evidence_id'][4:])<=188999 for e in packet)
    assert all(e['claim_type']=='parent' and e['record_table']=='sites' for e in packet)
    orgs={r['org_id']:r for f in a.data_dir.glob('organizations_*.csv') for r in read(f)}
    shards={f:read(f) for f in a.data_dir.glob('sites_*.csv')};sites={r['site_id']:(f,r) for f,rs in shards.items() for r in rs}
    assert len(sites)==sum(map(len,shards.values())),'duplicate existing site IDs'
    base={r['site_id']:r for r in frame};byv={v['site_id']:v for v in vs}
    all_ev=[(f.name,e) for f in a.data_dir.glob('evidence_*.csv') for e in read(f)]
    assert len(all_ev)==len({e['evidence_id'] for _,e in all_ev}),'duplicate existing evidence IDs'
    held={e['evidence_id']:(f,e) for f,e in all_ev};pending=defaultdict(list)
    raw=read(P/'rawcheck.csv')
    for e in packet:
        assert e['record_id'] in verified
        sid=e['record_id'];name='evidence_'+sites[sid][0].name
        if e['evidence_id'] in held:assert held[e['evidence_id']]==(name,e),'global evidence ID collision'
        else:pending[a.data_dir/name].append(e)
        if e['source_class']=='own_site':assert any(r['site_id']==sid and r['source_ref']==e['source_ref'] and r['quote']==e['claim_detail'] and r['raw_check']=='PASS' for r in raw),'own quote receipt gap'
    gov=read(P/'government-review.csv')
    assert_operator_names(vs,gov,orgs,read(P/'operator-name-map.csv'),raw)
    ita={r['establishment_id']:r for r in read(ROOT/'tasks/osha-ita-2026-11-01/establishments.csv')}
    osha={r['est_key']:r for r in read(ROOT/'tasks/osha-spine-2026-11-01/establishments.csv')}
    for g in gov:
        r=(ita if g['source_family']=='ITA' else osha)[g['source_id']]
        expected={'operator':r.get('company_name',r.get('name')),'establishment_name':r.get('establishment_name',r.get('name')),'street':r['street'],'city':r['city'],'state':r['state'],'zip':r.get('zip5',r.get('zip')),'date':r.get('date_submitted',r.get('latest_inspection'))[:10]}
        assert all(g[k]==v for k,v in expected.items()),('government packet drift',g['source_id'])
    for e in packet:
        if e['source_class']!='government_filing':continue
        matches=[g for g in gov if g['site_id']==e['record_id'] and g['source_id'] in e['source_ref']]
        assert len(matches)==1,'government evidence witness gap'
        g=matches[0];detail=g['operator']+'; establishment '+g['establishment_name']+'; '+g['street']+', '+g['city']+', '+g['state']+'; Atlas operator '+byv[e['record_id']]['operator_org_id']
        assert e['claim_detail']==detail and e['observed_date']==g['date'],'government claim drift'
    touched=set()
    for sid in verified:
        v=byv[sid];old=base[sid];assert orgs[old['org_id']]['status'] in {'merged','acquired'}
        assert any(e['record_id']==sid and e['claim_type']=='parent' for e in packet),'missing parent evidence'
        if v['action']=='REPOINT':assert v['operator_org_id']==old['successor_org_id'] and orgs[v['operator_org_id']]['status']=='active','invalid successor target'
        else:assert v['operator_org_id']==old['org_id'],'keep changed operator'
    assert orgs['ORG-001752']['ultimate_parent_name']=='Pexco','B-PARENT drift'
    for e in edits:
        assert e['field'] in {'org_id','notes','sources','last_verified'},'forbidden operator-pass field'
        sid=e['site_id'];path,r=sites[sid];assert e['state']==r['state']
        assert r[e['field']] in {e['old'],e['new']},('field drift',sid,e['field'])
        if e['field']=='org_id':assert byv[sid]['action']=='REPOINT' and e['new']==byv[sid]['operator_org_id']
        r[e['field']]=e['new'];touched.add(path)
    links=read(a.data_dir/'registry_links.csv');re=read(P/'registry-edit.csv');assert len(re)==1
    e=re[0];assert (e['registry'],e['registry_id'],e['site_id'],e['old_org_id'],e['new_org_id'])==('FRS','110001516832','SITE-006049','ORG-002260','ORG-002261')
    hit=[r for r in links if (r['registry'],r['registry_id'],r['site_id'])==(e['registry'],e['registry_id'],e['site_id'])]
    assert len(hit)==1 and hit[0]['org_id'] in {e['old_org_id'],e['new_org_id']},'registry FK drift'
    assert all(any(x['evidence_id']==eid and x['record_id']==e['site_id'] for x in packet) for eid in e['evidence_ids'].split(';'))
    hit[0]['org_id']=e['new_org_id']
    # No canonical mutation occurs until every record, claim, FK, preimage and global ID passes.
    for path in sorted(touched):write(path,shards[path])
    for path,rs in pending.items():append_sorted(path,rs,'evidence_id')
    write(a.data_dir/'registry_links.csv',links)
    print('PASS applied8operator re-points,2sourcedkeeps,4unchangedholds;39cells(including1authorizedregistryFK)18append-onlyEVD; no org/status/tier/edge changes')
if __name__=='__main__':main()

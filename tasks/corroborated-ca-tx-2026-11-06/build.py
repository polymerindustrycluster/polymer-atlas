"""Apply the CA CORROBORATED packet; rerun safely on fresh main (no CSV hand merges)."""
import argparse, csv, hashlib, importlib.util, json, random, re, sys
from collections import defaultdict, Counter
from pathlib import Path
P=Path(__file__).resolve().parent
ROOT=P.parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from shard_io import append_sorted
sys.path.insert(0,str(P))
from research import found
DATE='2026-11-06'
BY='atlas-L6-corr-ca-tx'

def read(p):
    with open(p,newline='',encoding='utf-8-sig') as f:return list(csv.DictReader(f))

def write(p,rows):
    with open(p,'w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n');w.writeheader();w.writerows(rows)

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--apply',action='store_true');a=ap.parse_args()
    cs={r['cluster_id']:r for r in read(P/'input.csv')};vs=read(P/'verdicts.csv')
    reserved={r['cluster_id']:r for r in json.loads((P/'reserved-ids.json').read_text())}
    assert len(vs)==len(cs)==len({v['cluster_id'] for v in vs}) and set(cs)=={v['cluster_id'] for v in vs}
    assert all(v['verdict'] in {'VERIFIED','REJECT','STILL_UNCERTAIN','DUPLICATE_OF'} for v in vs)
    ds={r['cluster_id']:r['result'] for r in json.loads((P/'dedupe.json').read_text())}
    for cid,oid in [('LF-CA-01013','ORG-000651'),('LF-CA-00417','ORG-001403'),('LF-CA-00284','ORG-007413')]:
        assert oid in {h['id'] for s in ds[cid]['steps'] if s['step']==1 for h in s['hits']},cid
    ita={r['establishment_id']:r for r in read(ROOT/'tasks/osha-ita-2026-11-01/establishments.csv')}
    ins={r['est_key']:r for r in read(ROOT/'tasks/osha-spine-2026-11-01/establishments.csv')}
    orgs={r['org_id']:r for f in (ROOT/'data').glob('organizations_*.csv') for r in read(f)}
    queue=read(ROOT/'tasks/federal-frame-2026-11-04/QUEUE_MULTISOURCE.csv')
    out=defaultdict(list);alloc=[];raw=[];blind=[]
    oidn,sidn,eidn=10000,14000,180000
    def evidence(shard,table,rid,claim,detail,ref,cls='government_filing',tier='C'):
        nonlocal eidn
        out[shard].append(dict(evidence_id=f'EVD-{eidn:06d}',record_table=table,record_id=rid,claim_type=claim,claim_detail=detail,source_class=cls,source_ref=ref,observed_date=DATE,tier_effect='supports_'+tier,created_by=BY,notes=''))
        eidn+=1
    def key(street):
        words=re.findall(r'[a-z0-9]+',street.lower());replace={'north':'n','south':'s','east':'e','west':'w','street':'st','avenue':'ave','drive':'dr','road':'rd','boulevard':'blvd'}
        return ' '.join(replace.get(w,w) for w in words)
    for v in vs:
        if v['verdict']!='VERIFIED':continue
        c=cs[v['cluster_id']];fed=[];band='unknown'
        slot=reserved[c['cluster_id']];eidn=slot['evidence_start']
        for token in c['sources_with_ids'].split(';'):
            kind,num=token.split(':',1)
            if kind=='ITA':
                r=ita[num];band=(r['band_from_avg_employees'] or 'unknown') if r['reliability']=='ok' and r['size_code_vs_avg_employees']=='consistent' else 'unknown';assert r['state']=='CA' and key(r['street'])==key(c['street'])
                fed.append((f"OSHA ITA Form 300A CY{r['year_filing_for']} establishment {num} ({r['establishment_name']}); https://www.osha.gov/sites/default/largefiles/ITA_300A_Summary_Data_2025_through_08-31-2026.csv; submitted {r['date_submitted'][:10]}; packet 2026-11-01 tasks/osha-ita-2026-11-01/establishments.csv",r['naics_code'],r['date_submitted'][:10],r.get('industry_description','')))
                blind.append(dict(cluster_id=c['cluster_id'],source_family='ITA',**r))
            elif kind=='OSHA':
                r=ins[num];assert r['state']=='CA'
                if key(r['street'])!=key(c['street']):
                    print('Excluded different street witness:',c['cluster_id'],num,r['street']);continue
                fed.append((f"OSHA inspection https://www.osha.gov/ords/imis/establishment.inspection_detail?id={r['latest_activity_nr']} ({r['name']}); tasks/osha-spine-2026-11-01/establishments.csv",r['naics_latest'],r['latest_inspection'],''))
                if not any(b['cluster_id']==c['cluster_id'] for b in blind):blind.append(dict(cluster_id=c['cluster_id'],source_family='OSHA',**r))
        assert fed,c['cluster_id']
        # The government manufacturing classification carries C only; it does not populate capabilities.
        ref,naics,activity,description=fed[0];assert naics.startswith(('3252','3261','3262'))
        ring='2' if naics.startswith('325212') else '1'
        matches=[q for q in queue if q['state']=='CA' and q['zip5']==c['zip5'] and key(q['street'])==key(c['street'])]
        extra='; '.join(f"federal-frame FRS={q['frs_id']} ITA={q['ita_id']} INSP={q['insp_key']}" for q in matches)
        notes=f"{c['cluster_id']}; CORROBORATED; {c['sources_with_ids']}. {extra}. {v['note']}".strip()
        own=v['own_quote'];tier=v['tier'];rawok=False
        if own:
            checked={r['cluster_id']:r for r in read(P/'rawcheck.csv')}
            witness=checked[c['cluster_id']]
            rawok=witness['raw']=='yes' and witness['quote']==own and witness['url']==v['own_url']
            assert rawok,(c['cluster_id'],own)
            raw.append(witness)
        assert tier=='C' or rawok
        oid=v['held_org_id']
        if not oid:
            assert not [h for s in ds[c['cluster_id']]['steps'] for h in s['hits']],c['cluster_id']
            oid=slot['org_id'];oidn+=1
            out['organizations_US.csv'].append(dict(org_id=oid,legal_name=v['org_legal_name'],entity_type='unknown',ring_primary=ring,hq_in_scope='national_us',naics_primary=naics,naics_primary_source_type='government_filing',naics_primary_source_name=ref,naics_confidence='medium',website=v['org_website'],description_1line=f"Federal-recorded polymer manufacturer with an establishment in {c['city']}, California.",pic_relevance='potential_member',status='unknown',sources=ref,verification_tier='C',last_verified=DATE,created_by=BY,notes=notes+' HQ not established; federal establishment address is not asserted as HQ.',monitor_watch='false'))
            for claim,detail in [('existence',v['org_legal_name']),('address','HQ not established; federal establishment only: '+c['street']+', '+c['city']),('scope',f'Government manufacturing classification NAICS {naics}; provisional C, no capability inference'),('code',naics)]:evidence('evidence_organizations_US.csv','organizations',oid,claim,detail,ref)
        else:assert oid in orgs
        sid=slot['site_id'];sidn+=1
        out['sites_CA.csv'].append(dict(site_id=sid,org_id=oid,site_name=c['best_name'],site_type='manufacturing_plant',street_address=v.get('street_override') or c['street'],city=c['city'],state='CA',zip=c['zip5'],country='US',ring_primary=ring,naics_primary=naics,naics_primary_source_type='government_filing',naics_confidence='medium',employee_band_site=band,operating_status='unknown',sources=ref+('; '+v['own_url'] if rawok else ''),verification_tier=tier,last_verified=DATE,created_by=BY,notes=notes+' Federal-only scope remains provisional C unless own witness is cited; current status not adjudicated.'))
        for claim,detail in [('existence',f"{c['best_name']} at {c['street']}"),('address',f"{c['street']}, {c['city']}, CA {c['zip5']}; county unverified"),('scope',f'Federal manufacturing classification NAICS {naics}: {description}; no capability inference'),('code',naics),('parent',f"Federal operator {v['org_legal_name']} linked to {oid}")]:
            evidence('evidence_sites_CA.csv','sites',sid,claim,detail,ref,tier='C' if claim=='scope' else tier)
        if band!='unknown':evidence('evidence_sites_CA.csv','sites',sid,'size_band','employee_band_site='+band,ref,tier=tier)
        if rawok:evidence('evidence_sites_CA.csv','sites',sid,'scope',own,v['own_url'],'own_site',tier)
        if v.get('street_override'):
            addr=read(P/'address-rawcheck.csv')[0]
            assert addr['cluster_id']==c['cluster_id'] and addr['raw']=='yes' and addr['quote']==v['street_override']
            eidn=181000
            evidence('evidence_sites_CA.csv','sites',sid,'address',addr['quote'],addr['url'],'own_site',tier)
        alloc.append(dict(cluster_id=c['cluster_id'],org_id=oid,site_id=sid,tier=tier))
    assert oidn<=11000 and sidn<=16000 and eidn<=200000
    write(P/'allocations.csv',alloc)
    # Fixed shuffled sample omits lane verdicts; reviewer independently reads federal witnesses.
    random.Random(20261106).shuffle(blind)
    fields=sorted({k for r in blind for k in r})
    with open(P/'blind-input.csv','w') as f:
        w=csv.DictWriter(f,fieldnames=fields,lineterminator='\n');w.writeheader();w.writerows(blind[:20])
    print('worked clusters',len(vs),'verdicts',dict(Counter(v['verdict'] for v in vs)),'rows by shard',{k:len(v) for k,v in out.items()},'sites by tier',dict(Counter(r['tier'] for r in alloc)))
    for name,rows in out.items():
        idcol='evidence_id' if name.startswith('evidence') else 'org_id' if name.startswith('organizations') else 'site_id'
        existing={r[idcol]:r for r in read(ROOT/'data'/name)};pending=[]
        for r in rows:
            if r[idcol] in existing:
                assert all(existing[r[idcol]][k]==str(v) for k,v in r.items()),('ID collision or changed packet',r[idcol])
            else:pending.append(r)
        if a.apply and pending:append_sorted(ROOT/'data'/name,pending,idcol)
    if a.apply:print('Applied; repeated identical run is a no-op.')
if __name__=='__main__':main()

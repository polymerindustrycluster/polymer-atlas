#!/usr/bin/env python3
"""Idempotent integrator application of reviewed L3 STRONG verdicts.
Run from repository root: python3 tasks/strong-waves-mo-sc-la-2026-11-06/build.py --state MO --apply
Stable IDs are frozen-verdict-order offsets within the owner's reserved block, never gap-filled.
"""
import argparse, csv, json, re, sys
from collections import Counter, defaultdict
from pathlib import Path
HERE=Path(__file__).resolve().parent; ROOT=HERE.parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from shard_io import append_sorted
DATE='2026-11-06'; BY='atlas-L3-strong-mo-sc-la'

def read(p):
    with open(p,newline='',encoding='utf-8') as f:return list(csv.DictReader(f))
def write(p,rows,fields):
    with open(p,'w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=fields,lineterminator='\n');w.writeheader();w.writerows(rows)

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--state',choices=['MO','SC','LA'],required=True);ap.add_argument('--apply',action='store_true');a=ap.parse_args()
    supplements=read(HERE/'supplements.csv')
    inputs={r['cluster_id']:r for r in read(HERE/'input.csv')};vs=read(HERE/'verdicts.csv')
    assert [v['cluster_id'] for v in vs]==sorted(inputs,key=lambda k:({'MO':0,'SC':1,'LA':2}[inputs[k]['state']],k)), 'verdict order changed'
    assert len(inputs)==len(vs)==36 and Counter(r['cluster_id'] for r in vs)==Counter(inputs.keys()), 'verdict census mismatch'
    raw={r['cluster_id']:r for r in read(HERE/'rawcheck.csv')}
    ita={r['establishment_id']:r for r in read(ROOT/'tasks/osha-ita-2026-11-01/establishments.csv')}
    osha={r['est_key']:r for r in read(ROOT/'tasks/osha-spine-2026-11-01/establishments.csv')}
    plans={r['ein']:r for r in read(ROOT/'tasks/form5500-spine-2026-11-01/sponsors.csv')}
    orgs={r['org_id']:(p,r) for p in (ROOT/'data').glob('organizations_*.csv') for r in read(p)}
    additions=defaultdict(list);alias_updates={};alloc=[]
    for idx,v in enumerate(vs):
        if v['state']!=a.state or v['verdict']!='VERIFIED':continue
        c=inputs[v['cluster_id']];assert raw[v['cluster_id']]['raw']=='yes' and v['own_quote']
        fed=[];aliases=[];alias_sources=[];code='';last='';industry=''
        fed_streets=[]
        for token in c['sources_with_ids'].split(';'):
            family,ident=token.split(':',1)
            if family=='ITA':
                r=ita[ident];ref=f"OSHA ITA Form 300A CY{r['year_filing_for']} establishment {ident} ({r['establishment_name']})"
                fed.append((ref,r['date_submitted'][:10]));aliases += [r['establishment_name'],r['company_name']]
                alias_sources.append(([r['establishment_name'],r['company_name']],ref,r['date_submitted'][:10]))
                fed_streets.append((r['street'],r['city'],r['state'],r['zip5']))
                if not industry:industry=r['industry_description']
                if not code:code=r['naics_code']
            elif family=='OSHA':
                r=osha[ident];ref=f"OSHA inspection {r['latest_activity_nr']} ({r['name']}), https://www.osha.gov/ords/imis/establishment.inspection_detail?id={r['latest_activity_nr']}"
                fed.append((ref,r['latest_inspection'][:10]));aliases.append(r['name'])
                alias_sources.append(([r['name']],ref,r['latest_inspection'][:10]))
                fed_streets.append((r['street'],r['city'],r['state'],r['zip'][:5]))
                if not code:code=r['naics_latest']
            elif family=='F5500':
                r=plans[ident];aliases.append(r['sponsor_name'])
                alias_sources.append(([r['sponsor_name']],f"DOL EFAST2 Form 5500 EIN {ident}, sponsor {r['sponsor_name']}, PY{r['plan_year']}, plan {r['plan_number']}, acknowledgement {r['ack_id']}",r['plan_year']+'-12-31'))
        assert not code or re.fullmatch(r'\d{6}',code), (v['cluster_id'],code)
        aliases=list(dict.fromkeys(x.strip() for x in aliases if x.strip()))
        own=v['own_url'];quote=v['own_quote'];ring=v['ring']
        # Employer filings do not attest plant operations. Without ITA/OSHA the own-site record stays C.
        tier='B' if fed else 'C';eff='supports_'+tier
        oid=v['held_org_id'] or f'ORG-{9000+idx:06d}';sid=f'SITE-{12000+idx:06d}';eid=160000+idx*100
        assert 9000<=int(oid[4:])<=9499 or v['held_org_id']
        assert 12000<=int(sid[5:])<=12999
        if oid.startswith('NEW:'):raise AssertionError('cross-state parent requires resolved ID')
        name=orgs[oid][1]['legal_name'] if oid in orgs else c['best_name']
        source='; '.join([own]+[f[0] for f in fed]);last=max([f[1] for f in fed]+[DATE])
        note=f"L3 STRONG {v['cluster_id']}; held federal packet identifiers (not fresh registry evidence): {c['sources_with_ids']}."
        def E(table,rid,claim,detail,ref=own,cls='own_site',date=DATE,effect=eff,shard=a.state):
            nonlocal eid
            assert 160000<=eid<=169999
            additions[f'evidence_{table}_{shard}.csv'].append(dict(evidence_id=f'EVD-{eid:06d}',record_table=table,record_id=rid,claim_type=claim,claim_detail=detail,source_class=cls,source_ref=ref,observed_date=date,tier_effect=effect,created_by=BY,notes=f'Reviewed {DATE}; '+note));eid+=1
        if not v['held_org_id']:
            aliases=[x for x in aliases if x!=name]
            org=dict(org_id=oid,legal_name=name,trade_names='; '.join(aliases),entity_type='unknown',ring_primary=ring,hq_country='',hq_in_scope='national_us',naics_primary=code,naics_primary_source_type='government_filing' if code else '',naics_primary_source_name=fed[0][0] if code else '',naics_confidence='medium' if code else '',website=own,description_1line=f"Polymer establishment operator in {c['city']}, {a.state}.",pic_relevance='potential_member',status='active',sources=source,verification_tier='C',last_verified=DATE,created_by=BY,notes=note+' HQ not independently established; left blank.',last_activity_evidence_date=DATE,liveness_signal='operating_evidence',monitor_watch='false')
            additions['organizations_US.csv'].append(org)
            for claim,detail in [('existence',f"legal_name {name}; website {own}; federal registrant aliases {'; '.join(aliases)}"),('scope',f"ring_primary {ring}: {quote}"),('activity',f"operator of polymer establishment: {quote}"),('liveness','Live operator page checked '+DATE)]:E('organizations',oid,claim,detail,effect='supports_C',shard='US')
            if code:E('organizations',oid,'code',f'naics_primary {code}; establishment filing, not company disclosure',fed[0][0],'government_filing',fed[0][1],'supports_C',shard='US')
        else:
            assert oid in orgs and not orgs[oid][1]['successor_org_id'], oid
            p,r=orgs[oid];old=[x.strip() for x in r['trade_names'].split(';') if x.strip()]
            new=[x for x in aliases if x!=name and x not in old]
            if new:
                alias_updates.setdefault(p,{})[oid]='; '.join(old+new)
            # Alias observations cite the federal registrant, not the own-site brand.
            alias_ref=fed[0][0] if fed else own
            if any(x!=name for x in aliases):
                E('organizations',oid,'existence','Federal registrant aliases: '+'; '.join(x for x in aliases if x!=name),alias_ref,'government_filing' if fed else 'own_site',fed[0][1] if fed else DATE,'supports_C',shard=p.stem.split('_')[-1])
        site=dict(site_id=sid,org_id=oid,site_name=f"{name} - {c['city']}",site_type='manufacturing_plant',street_address=c['street'],city=c['city'],state=a.state,zip=c['zip5'],country='US',ring_primary=ring,naics_primary=code,naics_primary_source_type='government_filing' if code else '',naics_confidence='medium' if code else '',operating_status='active',sources=source,verification_tier=tier,last_verified=DATE,created_by=BY,notes=note+' County not settled from physical-address evidence; left blank.')
        additions[f'sites_{a.state}.csv'].append(site)
        for claim,detail in [('existence',f"{name} establishment"),('scope',f"ring_primary {ring}: {quote}"),('activity',quote),('parent',f'org_id {oid}: federal registrant/own-site operator linkage'),('liveness','Live operator witness checked '+DATE)]:E('sites',sid,claim,detail)
        if fed:
            E('sites',sid,'address',f"{c['street']}, {c['city']}, {a.state} {c['zip5']}",fed[0][0],'government_filing',fed[0][1])
            E('sites',sid,'code',f'naics_primary {code}',fed[0][0],'government_filing',fed[0][1])
        else:
            E('sites',sid,'address',f"{c['street']}, {c['city']}, {a.state} {c['zip5']}")
        # Supplement, never replace, the original own-site attribution and weak quotations.
        eid=165000+idx*100
        org_shard=orgs[oid][0].stem.split('_')[-1] if v['held_org_id'] else 'US'
        for names,ref,asof in alias_sources:
            values=[n for n in names if n and n!=name]
            if values:E('organizations',oid,'existence','Federal registrant aliases: '+'; '.join(values),ref,'government_filing',asof,'supports_C',shard=org_shard)
        for extra in supplements:
            if extra['cluster_id']!=v['cluster_id']:continue
            assert extra['raw']=='yes'
            kind=extra['claim_type'];detail=f"Raw-checked supplemental witness: {extra['quote']}"
            E('sites',sid,kind,detail,extra['source_url'])
            E('organizations',oid,kind,detail,extra['source_url'],effect='supports_C',shard=org_shard)
            if kind=='scope':
                E('sites',sid,'activity',detail,extra['source_url'])
                E('organizations',oid,'activity',detail,extra['source_url'],effect='supports_C',shard=org_shard)
        if industry:
            # The filing's own activity description complements plant-only own-site witnesses.
            for kind in ('scope','activity'):E('sites',sid,kind,'Filed establishment activity: '+industry,fed[0][0],'government_filing',fed[0][1])
        import atlas
        assert all(atlas.street_key(street)==atlas.street_key(c['street']) and state==c['state'] for street,city,state,zip_ in fed_streets), ('federal street mismatch',v['cluster_id'],fed_streets)
        alloc.append(dict(cluster_id=v['cluster_id'],org_id=oid,new_org=str(not bool(v['held_org_id'])).lower(),site_id=sid,tier=tier))
    if a.apply:
        for filename,rows in additions.items():
            path=ROOT/'data'/filename;pk=next(iter(rows[0]));old={r[pk]:r for r in read(path)}
            fresh=[]
            for r in rows:
                if r[pk] in old:
                    # Re-running must be a no-op; a changed packet is a conflict, never an evidence rewrite.
                    assert all(old[r[pk]].get(k,'')==val for k,val in r.items()), (filename,r[pk])
                else:fresh.append(r)
            if fresh:append_sorted(path,fresh,pk)
        for p,changes in alias_updates.items():
            rows=read(p)
            for r in rows:
                if r['org_id'] in changes:r['trade_names']=changes[r['org_id']]
            write(p,rows,list(rows[0]))
        write(HERE/f'allocations_{a.state}.csv',alloc,['cluster_id','org_id','new_org','site_id','tier'])
    print(a.state,dict(Counter({f:len(r) for f,r in additions.items()})), 'alias updates',sum(len(x) for x in alias_updates.values()))
if __name__=='__main__':main()

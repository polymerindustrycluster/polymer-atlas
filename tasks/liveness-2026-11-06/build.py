"""Rebuild the ranked queue from frozen sweep and exact federal-key inputs; no data writes."""
from collections import defaultdict
import sys
from federal_signals import HERE, ROOT, read, write
sys.path.insert(0, str(ROOT/"scripts"))
from liveness_sweep import normalize_website


def score(signal, years, final, tri):
    return ({'NXDOMAIN':30,'PARKED_SUSPECT':25,'REDIRECT_CROSS_DOMAIN':20}.get(signal,0)
            + (10 if years and max(years)<2024 else 0) + (10 if final else 0)
            + (5 if tri and max(tri)<2024 else 0))


def main():
    orgs = [r for p in sorted((ROOT/'data').glob('organizations_*.csv')) for r in read(p)] + read(ROOT/'data/ecosystem.csv')
    assert len({r['org_id'] for r in orgs}) == len(orgs)
    sponsor_rows=read(ROOT/'tasks/form5500-spine-2026-11-01/sponsors.csv')
    sponsors = {r['ein']:r for r in sponsor_rows}
    assert len(sponsors)==len(sponsor_rows)
    tri = {r['trifid']:r for r in read(HERE/'tri_years.csv')}
    link_rows=[]
    links = defaultdict(list)
    for r in read(HERE/'registry_links_snapshot.csv'):
        if r['registry'] in ('EIN','TRI_TRIFID'):
            links[r['org_id']].append(r)
            key=r['registry_id']
            if r['registry']=='EIN':
                year=sponsors.get(key,{}).get('latest_filed_plan_year_any','')
                coverage='found' if year else 'NOT_IN_SPINE'
            else:
                year=tri[key]['latest_year']; coverage=tri[key]['coverage']
            link_rows.append(dict(org_id=r['org_id'],site_id=r['site_id'],registry=r['registry'],registry_id=key,latest_year=year,coverage=coverage))
    write(HERE/'federal_link_signals.csv',link_rows,list(link_rows[0]))
    sweep = {}
    for r in read(HERE/'sweep/signals.csv'):
        for oid in r['org_id'].split(';'):
            assert oid not in sweep
            sweep[oid] = r
    rows=[]
    for o in orgs:
        if o['status'] not in ('active','unknown'):
            continue
        oid=o['org_id']; f=[]; t=[]
        for link in links[oid]:
            key=link['registry_id']
            if link['registry']=='EIN':
                r=sponsors.get(key,{})
                f.append((key,r.get('latest_filed_plan_year_any',''),r.get('latest_py_all_final_or_short','')))
            else:
                r=tri[key]
                t.append((key,r['latest_year'],r['coverage']))
        sy=[int(y) for _,y,_ in f if y]; ty=[int(y) for _,y,_ in t if y]
        final=any(v=='1' for _,_,v in f)
        s=sweep.get(oid,{})
        current_domain,_=normalize_website(o['website'])
        changed=bool(s and current_domain!=s['domain'])
        signal='WEBSITE_CHANGED_SINCE_SWEEP' if changed else s.get('signal_class','NOT_SWEPT')
        rows.append(dict(rank='',score=score(signal,sy,final,ty),org_id=oid,legal_name=o['legal_name'],
                         domain=current_domain or '',current_website=o['website'],sweep_domain=s.get('domain',''),signal_class=signal,final_url='' if changed else s.get('final_url',''),
                         ein_years=';'.join(k+':'+(y or 'NOT_IN_SPINE') for k,y,_ in f),
                         form5500_latest_year=max(sy) if sy else '',form5500_final_or_short=int(final),
                         trifid_years=';'.join(k+':'+(y or cov) for k,y,cov in t),
                         tri_latest_year=max(ty) if ty else '',tri_unresolved=sum(not y for _,y,_ in t),
                         federal_note='Signal only; sponsor address not assumed to equal establishment; no link is unknown coverage'))
    rows.sort(key=lambda r:(-r['score'],r['org_id']))
    for n,r in enumerate(rows,1): r['rank']=n
    assert len(rows)==len({r['org_id'] for r in rows})
    write(HERE/'signals.csv',rows,list(rows[0]))
    print('active/unknown organization+ecosystem rows:',len(rows),'positive priority:',sum(r['score']>0 for r in rows))

if __name__=='__main__': main()

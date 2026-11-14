import csv,json,sys,shutil,os,collections
b,lo,hi,evr,capr=sys.argv[1],int(sys.argv[2]),int(sys.argv[3]),sys.argv[4],sys.argv[5]
D=f'../repo/tasks/oh-capabilities-2026-11-12-{b}/'; os.makedirs(D+'scripts',exist_ok=True)
fr=list(csv.DictReader(open('cap_frame.csv')))[lo:hi]; ids={r['site_id'] for r in fr}
def W(n,rows,fn=None):
    w=csv.DictWriter(open(D+n,'w',newline=''),fieldnames=fn or list(rows[0].keys()),lineterminator='\n');w.writeheader();w.writerows(rows)
W('frame.csv',fr)
F=json.load(open('cap_fetch.json'))
W('fetch_log.csv',[dict(site_id=r['site_id'],url=m['url'],final_url=m['eff'],http=m['code'],sha256=m['sha256'] if m['bytes'] else '',bytes=m['bytes'],fetched_et=m['fetched']) for r in fr for m in F.get(r['site_id'],[])])
V=list(csv.DictReader(open(f'{b}_cap_verdicts.csv'))); W('verdicts.csv',V)
dec=list(csv.DictReader(open(f'{b}_dec2.csv'))); acc={(d['site_id'],d['term']) for d in dec}
C=[dict(c,basis='narrative') for c in csv.DictReader(open(f'{b}_cands.csv'))]+[dict(m,basis='menu') for m in csv.DictReader(open('cap_menu.csv')) if m['site_id'] in ids]
S={r['site_id']:r for r in fr}; nm=[]
for c in C:
    if (c['site_id'],c['term']) in acc: continue
    s=S[c['site_id']]; col='materials' if c['type']=='material' else 'processes'
    if s['site_mat' if c['type']=='material' else 'site_proc']: why=f'site {col} already populated on main; fill-blank-only rule'
    elif c['site_id']=='SITE-000085': why="website on file is designmolded.com (Design Molded Plastics SITE-000069); another org's page"
    else: why="clause names a customer process, market, end use, brand, supplier network, equipment or generic explainer, not the company's own process/material"
    nm.append(dict(site_id=c['site_id'],type=c['type'],term=c['term'],basis=c['basis'],url=c['url'],quote=c['quote'],reason=why,date='2026-11-12'))
W('not_minted.csv',nm,['site_id','type','term','basis','url','quote','reason','date'])
W('candidates.csv',C,['site_id','name','type','term','basis','url','sha','quote','other','loc','k'])
for f in ['capfetch.py','capextract.py','capfilter.py','capmenu.py','menurev.py','mkdec.py','capbuild2.py','cappacket.py','extract.py','fetch.py']: shutil.copy(f,D+'scripts/')
shutil.copy(f'{b}_dec2.csv',D+'scripts/decisions.csv')
old=D+'scripts/b01_cap_dec.csv'; 
for f in ['capbuild.py','b01_cap_dec.csv']:
    if os.path.exists(D+'scripts/'+f): os.remove(D+'scripts/'+f)
tag=[v for v in V if v['site_ev'] or v['org_ev']]
sites_t={v['site_id'] for v in V if v['site_ev']}; orgs_t={v['org_id'] for v in V if v['org_ev']}
anyt={v['site_id'] for v in tag}
basis_rows=collections.Counter(v['basis'] for v in tag)
site_by_basis={k:len({v['site_id'] for v in V if v['site_ev'] and v['basis']==k}) for k in ('narrative','menu')}
pages=sum(1 for r in fr for m in F.get(r['site_id'],[]) if m['code'].startswith('2'))
okS=len({r['site_id'] for r in fr if any(m['code'].startswith('2') for m in F.get(r['site_id'],[]))})
summ=dict(batch=b,date='2026-11-12',frame_rows=len(fr),frame_slice=f'{lo}:{hi} of cap_frame (306)',sites_fetched_ok=okS,pages_ok=pages,candidates=len(C),accepted_terms=len(V),records_gaining_tag=len(anyt),yield_pct=round(100*len(anyt)/len(fr),1),sites_tagged=len(sites_t),orgs_tagged=len(orgs_t),site_evidence=sum(1 for v in V if v['site_ev']),org_evidence=sum(1 for v in V if v['org_ev']),evidence_rows_by_basis=dict(basis_rows),sites_tagged_by_basis=site_by_basis,cap_rows=sum(1 for v in V if v['cap']),held_tags_V25=sum(1 for v in V if v.get('held')),sites_cap_only_V25=sorted({v['site_id'] for v in V if v.get('held') and v['site_id'] not in anyt}),evd_range=evr,cap_range=capr)
json.dump(summ,open(D+'summary.json','w'),indent=1); print(json.dumps(summ))

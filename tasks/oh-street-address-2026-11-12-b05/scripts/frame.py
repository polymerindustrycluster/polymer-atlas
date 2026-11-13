import csv,glob,collections,json,sys,re
R='/workspace/atlas-ohio-nov12/repo/'
orgs={}
for f in glob.glob(R+'data/organizations_*.csv'):
    for r in csv.DictReader(open(f)): orgs[r['org_id']]=r
prior={}
for f in sorted(glob.glob(R+'tasks/oh-street-address*/verdicts*.csv'))+sorted(glob.glob(R+'tasks/oh-street-address*/holds.csv')):
    for r in csv.DictReader(open(f)):
        if r.get('site_id'): prior[r['site_id']]=(r.get('reason') or '')
rows=list(csv.DictReader(open(R+'data/sites_OH.csv')))
allsites=[]
for f in glob.glob(R+'data/sites_*.csv'): allsites+=list(csv.DictReader(open(f)))
percity=collections.Counter((r['org_id'],r['city'].lower()) for r in allsites)
order=sys.argv[1].split(',')
act=[r for r in rows if not r['street_address'].strip() and r['operating_status']=='active']
out=[]
for c in order:
    for r in sorted([r for r in act if r['county']==c],key=lambda r:r['site_id']):
        pr=prior.get(r['site_id'],'')
        conflict=bool(re.search(r'conflict|disagree',pr))
        o=orgs.get(r['org_id'],{})
        out.append(dict(site_id=r['site_id'],org_id=r['org_id'],site_name=r['site_name'],city=r['city'],zip=r['zip'],county=r['county'],tier=r['verification_tier'],website=o.get('website',''),org_sites_same_city=percity[(r['org_id'],r['city'].lower())],prior_reason=pr[:100],prior_conflict=int(conflict)))
w=csv.DictWriter(open(sys.argv[2],'w'),fieldnames=list(out[0].keys()));w.writeheader();w.writerows(out)
print(len(out),sum(o['prior_conflict'] for o in out),sum(1 for o in out if not o['website']))

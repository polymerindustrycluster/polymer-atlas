import csv,json,sys,os,shutil,collections,io,subprocess
b,date,title=sys.argv[1],sys.argv[2],sys.argv[3]
R='/workspace/atlas-ohio-nov12/repo/'; D=R+f'tasks/oh-street-address-{date}-{b}/'; os.makedirs(D,exist_ok=True)
shutil.copy(f'{b}_frame.csv',D+'frame.csv'); shutil.copy(f'{b}_audit.csv',D+'audit.csv'); shutil.copy(f'{b}_leads.csv',D+'leads.csv')
V=list(csv.DictReader(open(f'{b}_verdicts.csv')))
cols=['site_id','org_id','site_name','city','zip','tier','verdict','street','evidence_id','url','page_zip','pages_tried','pages_ok','reason','flags']
w=csv.DictWriter(open(D+'verdicts.csv','w'),fieldnames=cols,extrasaction='ignore',lineterminator='\n');w.writeheader();w.writerows(V)
w=csv.DictWriter(open(D+'holds.csv','w'),fieldnames=['site_id','verdict','reason'],extrasaction='ignore',lineterminator='\n');w.writeheader();w.writerows([v for v in V if v['verdict']!='VERIFIED'])
E=json.load(open(f'{b}_evidence.json'))
if E:
    w=csv.DictWriter(open(D+'evidence.csv','w'),fieldnames=list(E[0].keys()),lineterminator='\n');w.writeheader();w.writerows(E)
f=json.load(open(f'{b}_fetch.json')); rows=[]
for sid,log in f.items():
    for m in log: rows.append(dict(site_id=sid,url=m['url'],http=m['code'],bytes=m['bytes'],sha256=m['sha256'],fetched=m['fetched']))
w=csv.DictWriter(open(D+'fetch_log.csv','w'),fieldnames=['site_id','url','http','bytes','sha256','fetched'],lineterminator='\n');w.writeheader();w.writerows(rows)
os.makedirs(D+'scripts',exist_ok=True)
for s in ['frame.py','fetch.py','extract.py','adjudicate.py','build.py','leads.py','packet.py']: shutil.copy(s,D+'scripts/'+s)
c=collections.Counter(v['verdict'] for v in V)
rc=collections.Counter()
for v in V:
    if v['verdict']=='VERIFIED': continue
    r=v['reason']
    k=('no held website' if r.startswith('no held') else 'own-site fetch unavailable' if 'unavailable' in r else 'pages read, no street at recorded city' if 'no street at recorded city' in r else 'ZIP conflict' if 'ZIP' in r else 'several streets' if 'several streets' in r else 'mailing/warehouse context' if 'mailing' in r else 'notes street disagrees' if 'notes' in r else 'same-city sibling sites' if 'operator holds' in r else 'fresh re-fetch failed' if 'fresh raw' in r else 'other')
    rc[k]+=1
fetched=len(rows); ok=sum(1 for x in rows if x['http'].startswith('2'))
tiers=collections.Counter(v['tier'] for v in V if v['verdict']=='VERIFIED')
sites=list(csv.DictReader(open(R+'data/sites_OH.csv')))
act=[s for s in sites if s['operating_status']=='active']; filled=sum(1 for s in act if s['street_address'].strip())
json.dump(dict(batch=b,frame=len(V),verdicts=c,hold_reasons=rc,fetch_attempts=fetched,fetch_2xx=ok,verified_by_tier=tiers,active_oh_sites=len(act),active_oh_with_street_after=filled,audit_pass=sum(1 for a in csv.DictReader(open(f'{b}_audit.csv')) if a['result']=='PASS')),open(D+'summary.json','w'),indent=1)
print(json.dumps(dict(verdicts=c,hold_reasons=rc,fetch=(fetched,ok),tiers=tiers,act=len(act),filled=filled)))

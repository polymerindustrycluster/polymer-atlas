"""Apply VERIFIED street fills to data/sites_OH.csv and append own_site address evidence. Fresh raw re-fetch audit first."""
import csv,io,sys,json,re,hashlib,subprocess,time,html
from extract import text_of
R='/workspace/atlas-ohio-nov12/repo/'
UA='Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36'
verd,batch,evd0,evd1,today=sys.argv[1],sys.argv[2],int(sys.argv[3]),int(sys.argv[4]),sys.argv[5]
mode=sys.argv[6] if len(sys.argv)>6 else 'apply'
V=list(csv.DictReader(open(verd)))
def words(s): return [w for w in re.split(r'[^A-Za-z0-9]+',s.lower()) if w]
def inorder(needle,hay):
    n=words(needle); h=words(hay); i=0
    # contiguous match of word sequence
    L=len(n)
    for j in range(len(h)-L+1):
        if h[j:j+L]==n: return True
    return False
audit=[]
cache={}
for v in V:
    if v['verdict']!='VERIFIED': continue
    u=v['url']
    if u not in cache:
        r=subprocess.run(['curl','-sL','--compressed','-m','30','-A',UA,u],capture_output=True)
        cache[u]=(r.stdout,hashlib.sha256(r.stdout).hexdigest())
        time.sleep(0.3)
    body,sha=cache[u]; t=text_of(body)
    street_core=re.split(r',\s*(?:Suite|Ste|Unit|#)',v['street'])[0]
    ok=inorder(street_core,t) and inorder(v['city'],t)
    # tight binding: street then city within 160 chars
    m=None
    idx=t.lower().find(street_core.lower())
    bound= idx>=0 and v['city'].lower() in t[idx:idx+len(street_core)+160].lower()
    audit.append(dict(site_id=v['site_id'],url=u,fresh_sha256=sha,fresh_bytes=len(body),street_in_order=int(inorder(street_core,t)),city_bound=int(bound),result='PASS' if ok and bound else 'FAIL'))
    v['fresh_sha256']=sha; v['audit']='PASS' if ok and bound else 'FAIL'
    if v['audit']=='FAIL': v['verdict']='STILL_UNCERTAIN'; v['reason']='fresh raw re-fetch did not reproduce the quote (route availability, not absence); need a re-readable own-site page'
w=csv.DictWriter(open(f'{batch}_audit.csv','w'),fieldnames=list(audit[0].keys()));w.writeheader();w.writerows(audit)
print('audit',sum(a['result']=='PASS' for a in audit),'/',len(audit))
# apply
p=R+'data/sites_OH.csv'; t=open(p,newline='').read(); rd=csv.DictReader(io.StringIO(t,newline='')); rows=list(rd); hdr=rd.fieldnames
byid={r['site_id']:r for r in rows}
ep=R+'data/evidence_sites_OH.csv'; et=open(ep,newline='').read(); erd=csv.DictReader(io.StringIO(et,newline='')); erows=list(erd); ehdr=erd.fieldnames
have={r['evidence_id'] for r in erows}
n=evd0; newe=[]
for v in V:
    if v['verdict']!='VERIFIED': v['evidence_id']=''; continue
    r=byid[v['site_id']]
    assert r['street_address']=='' , v['site_id']
    eid=f'EVD-{n:06d}'; n+=1; assert n-1<=evd1 and eid not in have
    r['street_address']=v['street']
    if v.get('flags'):
        r['notes']=(r['notes']+' ' if r['notes'] else '')+f"ADDRESS-OVERLAP LEAD ({today}, {batch}): street {v['street']} also held on {v['flags'].split(': ',1)[1]}. No merge, site_group or status adjudication."
    q=re.sub(r'\s*,\s*(,\s*)+',', ',v['quote']).strip(' ,')
    zipnote=f"; own-page ZIP {v['page_zip']}" if v['page_zip'] else ''
    newe.append(dict(evidence_id=eid,record_table='sites',record_id=v['site_id'],claim_type='address',claim_detail=f"street_address {v['street']}, {v['city']}, OH{zipnote}",source_class='own_site',source_ref=v['url'],observed_date=today,tier_effect='supports_A',created_by=f'grok-oh-street-{batch}',notes=f"Raw checked {today}; SHA-256 {v['fresh_sha256']}; quote: {q[:300]}. County, county_source, ZIP and record tier unchanged."))
    v['evidence_id']=eid
wv=csv.DictWriter(open(f'{batch}_verdicts.csv','w'),fieldnames=list(V[0].keys())+[k for k in ('fresh_sha256','audit','evidence_id') if k not in V[0]],restval='');wv.writeheader();wv.writerows(V)
json.dump(newe,open(f'{batch}_evidence.json','w'),indent=1)
if mode=='apply':
    b=io.StringIO(); w=csv.DictWriter(b,fieldnames=hdr,lineterminator='\n'); w.writeheader(); w.writerows(rows); open(p,'w',newline='').write(b.getvalue())
    allr=sorted(erows+newe,key=lambda r:r['evidence_id'])
    b=io.StringIO(); w=csv.DictWriter(b,fieldnames=ehdr,lineterminator='\n'); w.writeheader(); w.writerows(allr); open(ep,'w',newline='').write(b.getvalue())
print('applied',len(newe),'EVD',evd0,'-',n-1)

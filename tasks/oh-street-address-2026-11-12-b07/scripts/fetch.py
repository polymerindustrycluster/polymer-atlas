import csv,sys,os,re,hashlib,json,subprocess,html,urllib.parse,concurrent.futures as cf,time
RAW='/workspace/atlas-ohio-nov12/raw/'; os.makedirs(RAW,exist_ok=True)
UA='Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36'
def get(url):
    h=hashlib.sha1(url.encode()).hexdigest()[:16]; p=RAW+h+'.html'; m=RAW+h+'.json'
    if os.path.exists(m):
        meta=json.load(open(m)); return meta, (open(p,'rb').read() if os.path.exists(p) else b'')
    try:
        r=subprocess.run(['curl','-sL','--compressed','-m','25','-A',UA,'-w','\n%{http_code} %{url_effective}','-o',p,url],capture_output=True,text=True,timeout=40)
        code,eff=(r.stdout.strip().split(' ',1)+[''])[:2] if r.stdout.strip() else ('000',url)
    except Exception as e: code,eff='000',url
    body=open(p,'rb').read() if os.path.exists(p) else b''
    meta=dict(url=url,code=code,eff=eff,sha256=hashlib.sha256(body).hexdigest(),bytes=len(body),fetched=time.strftime('%Y-%m-%dT%H:%M:%S'))
    json.dump(meta,open(m,'w')); return meta,body
KEY=re.compile(r'contact|location|facilit|plant|about|find-us|findus|directions|visit|our-company|company|reach',re.I)
def links(base,body):
    t=body.decode('utf-8','ignore'); out=[]
    for href in re.findall(r'href=["\']([^"\'#]+)',t):
        u=urllib.parse.urljoin(base,html.unescape(href))
        pu=urllib.parse.urlparse(u); pb=urllib.parse.urlparse(base)
        if pu.scheme.startswith('http') and pu.netloc.replace('www.','')==pb.netloc.replace('www.','') and KEY.search(pu.path) and not re.search(r'\.(pdf|jpg|png|zip)$',pu.path,re.I):
            if u not in out: out.append(u)
    # prioritize contact, location
    out.sort(key=lambda u:(0 if re.search('contact',u,re.I) else 1 if re.search('location|facilit|plant',u,re.I) else 2, len(u)))
    return out
def work(row):
    site=row['website'].strip()
    if not site: return row['site_id'],[]
    if site in ('none_found',) or '.' not in site: return row['site_id'],[]
    host=re.sub(r'^https?://','',site).split('/')[0].replace('www.','')
    variants=[site if site.startswith('https') else 'https://'+re.sub(r'^https?://','',site),'https://'+host,'https://www.'+host]
    log=[]; body=b''; base=site
    for v in dict.fromkeys(variants):
        meta,body=get(v); log.append(meta)
        if meta['code']=='429': time.sleep(10); 
        if meta['code'].startswith('2') and body: base=meta.get('eff') or v; break
        body=b''
    cand=links(base,body)[:5] if body else []
    if body:
        for pth in ('/contact','/contact-us','/locations'):
            u=urllib.parse.urljoin(base,pth)
            if len(cand)<6 and not any(c.rstrip('/').endswith(pth) for c in cand): cand.append(u)
    for u in cand: m,_=get(u); log.append(m)
    return row['site_id'],log
if __name__=='__main__':
    rows=list(csv.DictReader(open(sys.argv[1])))
    n=int(sys.argv[2]) if len(sys.argv)>2 else len(rows)
    res={}
    with cf.ThreadPoolExecutor(12) as ex:
        for sid,log in ex.map(work,rows[:n]): res[sid]=log
    json.dump(res,open(sys.argv[3],'w'),indent=0)
    print(len(res),sum(len(v) for v in res.values()))

import csv,sys,re,json,urllib.parse,html,concurrent.futures as cf,time
from fetch import get
KEY=re.compile(r'capabilit|service|product|process|material|manufactur|about|what-we-do|industr|solution|molding|extrusion|compound|equipment',re.I)
def links(base,body):
    t=body.decode('utf-8','ignore'); out=[]
    for href in re.findall(r'href=["\']([^"\'#]+)',t):
        u=urllib.parse.urljoin(base,html.unescape(href)); pu=urllib.parse.urlparse(u); pb=urllib.parse.urlparse(base)
        if pu.scheme.startswith('http') and pu.netloc.replace('www.','')==pb.netloc.replace('www.','') and KEY.search(pu.path) and not re.search(r'\.(pdf|jpg|png|zip|jpeg|gif|svg)$',pu.path,re.I) and pu.path.count('/')<=3:
            u=u.split('?')[0]
            if u not in out: out.append(u)
    out.sort(key=lambda u:(0 if re.search('capabilit',u,re.I) else 1 if re.search('service|process|manufactur',u,re.I) else 2 if re.search('product|material',u,re.I) else 3,len(u)))
    return out
def work(row):
    site=row['website'].strip()
    host=re.sub(r'^https?://','',site).split('/')[0].replace('www.','')
    variants=[site if site.startswith('https') else 'https://'+re.sub(r'^https?://','',site),'https://'+host,'https://www.'+host]
    log=[]; body=b''; base=site
    for v in dict.fromkeys(variants):
        meta,body=get(v); log.append(meta)
        if meta['code'].startswith('2') and body: base=meta.get('eff') or v; break
        body=b''
    if body:
        for u in links(base,body)[:5]: m,_=get(u); log.append(m)
    return row['site_id'],log
rows=list(csv.DictReader(open(sys.argv[1]))); res={}
with cf.ThreadPoolExecutor(12) as ex:
    for sid,log in ex.map(work,rows): res[sid]=log
json.dump(res,open(sys.argv[2],'w'))
print(len(res),sum(len(v) for v in res.values()),sum(1 for v in res.values() if any(m['code'].startswith('2') for m in v)))

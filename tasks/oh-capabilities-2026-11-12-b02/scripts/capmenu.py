import csv,sys,re,json,os,hashlib
from extract import text_of
exec(open('capextract.py').read().split("P=[(re.compile")[0].split("from extract import text_of")[1])
P=[(re.compile(a,re.I),b,c) for a,b,c in P]
HP=re.compile(r'\b(Capabilities|Services|Processes|What We Do|Our Expertise|Manufacturing Capabilities)\b')
HM=re.compile(r'\b(Materials|Resins|Capabilities|Material Selection)\b')
RAW='/workspace/atlas-ohio-nov12/raw/'
frame={r['site_id']:r for r in csv.DictReader(open(sys.argv[1]))}
fetch=json.load(open(sys.argv[2])); out=[]
for sid,log in fetch.items():
    r=frame[sid]; seen=set()
    for meta in log:
        if not meta['code'].startswith('2') or re.search(r'career|job|employ',meta['url'],re.I): continue
        p=RAW+hashlib.sha1(meta['url'].encode()).hexdigest()[:16]+'.html'
        if not os.path.exists(p): continue
        body=open(p,'rb').read(); t=text_of(body)
        for rx,ty,term in P:
            if (ty,term) in seen or term in ('elastomers_rubber','thermoplastics','pet_petg','abs'): continue
            for m in rx.finditer(t):
                pre=t[max(0,m.start()-220):m.start()]
                hs=list((HP if ty=='process' else HM).finditer(pre))
                if not hs: continue
                h=hs[-1]; st=max(0,m.start()-220)+h.start()
                q=t[st:m.end()].strip()
                if len(q.split())>25 or q not in t: continue
                seen.add((ty,term)); out.append(dict(site_id=sid,name=r['site_name'],type=ty,term=term,url=meta['eff'] or meta['url'],sha=hashlib.sha256(body).hexdigest(),quote=q)); break
w=csv.DictWriter(open(sys.argv[3],'w'),fieldnames=['site_id','name','type','term','url','sha','quote']);w.writeheader();w.writerows(out)
print(len(out),len({o['site_id'] for o in out}))

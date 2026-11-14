import csv,sys,re,json,html,os,hashlib
RAW='/workspace/atlas-ohio-nov12/raw/'
def text_of(body):
    t=body.decode('utf-8','ignore')
    t=re.sub(r'(?is)<(script|style|noscript)[^>]*>.*?</\1>',' ',t)
    t=re.sub(r'(?i)<br\s*/?>|</p>|</div>|</li>|</h\d>|</span>',' , ',t)
    t=re.sub(r'<[^>]+>',' ',t); t=html.unescape(t)
    t=re.sub(r'[\u00a0\s]+',' ',t)
    return t
SUF=r'(?:Road|Rd|Street|St|Avenue|Ave|Drive|Dr|Boulevard|Blvd|Parkway|Pkwy|Lane|Ln|Way|Court|Ct|Circle|Cir|Place|Pl|Highway|Hwy|Pike|Trail|Tr|Terrace|Ter|Square|Sq|Center|Ctr|Plaza|Run|Loop|Expressway|Route|Rte|Industrial Pkwy)\.?'
def cands(t,city):
    out=[]
    cityre=re.escape(city)
    pat=re.compile(r'(\b\d{1,6}[A-Z]?(?:-\d+)?\s+(?:[NSEW]\.?\s+|North\s+|South\s+|East\s+|West\s+)?(?:[A-Za-z0-9\.\'\-]+\s+){0,5}?'+SUF+r'(?:\s+(?:[NSEW]|N\.?[EW]\.?|S\.?[EW]\.?|North|South|East|West))?)\b[\s,\.\-–—•|·]*((?:Suite|Ste|Unit|Bldg|Building|#)\.?\s*[\w\-]+)?[\s,\.\-–—•|·]*(?:[^,]{0,40}?,\s*)?('+cityre+r')\s*,?\s*(Ohio|OH)\b\.?\s*,?\s*(\d{5})?',re.I)
    for m in pat.finditer(t):
        st=m.group(1).strip(' ,.')
        if m.group(2): st+=', '+re.sub(r'^Ste\.?\s*','Ste ',m.group(2).strip(' ,.'))
        out.append(dict(street=st,city=m.group(3),zip=m.group(5) or '',quote=t[max(0,m.start()-60):m.end()+10].strip()))
    # route-style "State Route 123"
    for m in re.finditer(r'(\b\d{1,6}\s+(?:(?:State|County|US|U\.S\.)\s+)?(?:Route|Rt\.?|SR|Rte)\s*\d+[A-Z]?)\b[\s,\.\-–—•|·]*('+cityre+r')\s*,?\s*(Ohio|OH)\b\.?\s*,?\s*(\d{5})?',t,re.I):
        out.append(dict(street=m.group(1).strip(' ,.'),city=m.group(2),zip=m.group(4) or '',quote=t[max(0,m.start()-60):m.end()+10].strip()))
    return out
def pobox(s): return bool(re.search(r'p\.?\s*o\.?\s*box',s,re.I))
if __name__=='__main__':
    frame={r['site_id']:r for r in csv.DictReader(open(sys.argv[1]))}
    fetch=json.load(open(sys.argv[2]))
    out=[]
    for sid,log in fetch.items():
        r=frame[sid]; found=[]
        okpages=0
        for m in log:
            if not m['code'].startswith('2'): continue
            h=hashlib.sha1(m['url'].encode()).hexdigest()[:16]; p=RAW+h+'.html'
            if not os.path.exists(p): continue
            okpages+=1
            t=text_of(open(p,'rb').read())
            for c in cands(t,r['city']):
                if pobox(c['street']): continue
                c['url']=m['url']; c['sha256']=m['sha256']; found.append(c)
        norm=lambda s:re.sub(r'[^a-z0-9]','',s.lower().replace('street','st').replace('road','rd').replace('avenue','ave').replace('drive','dr').replace('boulevard','blvd').replace('parkway','pkwy'))
        streets={}
        for c in found: streets.setdefault(norm(c['street']),[]).append(c)
        zips=set(c['zip'] for c in found if c['zip'])
        out.append(dict(site_id=sid,org_id=r['org_id'],site_name=r['site_name'],city=r['city'],zip=r['zip'],tier=r['tier'],website=r['website'],same_city=r['org_sites_same_city'],pages_ok=okpages,pages_tried=len(log),n_streets=len(streets),streets=' || '.join(v[0]['street'] for v in streets.values()),page_zips=';'.join(sorted(zips)),first=json.dumps(found[0]) if found else ''))
    w=csv.DictWriter(open(sys.argv[3],'w'),fieldnames=list(out[0].keys()));w.writeheader();w.writerows(out)
    print('rows',len(out),'with cand',sum(1 for o in out if o['n_streets']),'single',sum(1 for o in out if o['n_streets']==1),'no pages',sum(1 for o in out if not o['pages_ok']))

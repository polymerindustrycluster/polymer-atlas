import csv,json,sys,re,hashlib,os
from extract import text_of,RAW
V=list(csv.DictReader(open(sys.argv[1]))); f=json.load(open(sys.argv[2]))
out=[]
for v in V:
    if v['flags']: out.append(dict(site_id=v['site_id'],lead_type='address_overlap' if v['verdict']=='VERIFIED' else 'same_operator_same_address',detail=v['flags']))
    if 'ZIP' in v['reason'] and 'conflicts' in v['reason']: out.append(dict(site_id=v['site_id'],lead_type='zip_conflict',detail=f"own page {v['url']} prints {v['street']}; {v['reason']}"))
    if v['verdict']!='VERIFIED' and v['pages_ok']!='0' and not v['street']:
        hits=set()
        for m in f.get(v['site_id'],[]):
            if not m['code'].startswith('2'): continue
            p=RAW+hashlib.sha1(m['url'].encode()).hexdigest()[:16]+'.html'
            if not os.path.exists(p): continue
            t=text_of(open(p,'rb').read())
            for mm in re.finditer(r'\b\d{2,6}\s[^,|•]{3,45}?[,\-–•|]?\s+([A-Z][A-Za-z\. ]{2,25}),?\s+(?:OH|Ohio)\.?,?\s+\d{5}',t):
                if v['city'].lower() not in mm.group(0).lower(): hits.add(re.sub(r'\s+',' ',mm.group(0))[:100])
        if hits: out.append(dict(site_id=v['site_id'],lead_type='own_site_other_city_address',detail='recorded city '+v['city']+'; own pages print: '+' || '.join(sorted(hits)[:3])))
w=csv.DictWriter(open(sys.argv[3],'w'),fieldnames=['site_id','lead_type','detail']);w.writeheader();w.writerows(out)
import collections; print(collections.Counter(o['lead_type'] for o in out))

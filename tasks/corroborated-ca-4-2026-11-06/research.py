"""Fetch public operator pages with curl; reuse the house word matcher. No contacts saved."""
import csv, importlib.util, re, subprocess, sys
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
P=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('prep',P.parent/'evidence-repair-2-2026-11-04/prep.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
W=m.W

def fetch(item):
    cid,url=item
    for route in (url,'https://r.jina.ai/'+url):
        r=subprocess.run(['curl','-L','--fail','--max-time','25','-A','Mozilla/5.0',route],capture_output=True)
        if r.returncode==0 and len(r.stdout)>300:
            text=r.stdout.decode('utf-8',errors='replace')
            text=re.sub(r'<(script|style)\b.*?</\1>',' ',text,flags=re.S|re.I)
            text=re.sub('<[^>]+>',' ',text)
            import html
            text=' '.join(html.unescape(text).split())
            Path('/tmp/L6-'+cid+'.txt').write_text(text)
            return {'cluster_id':cid,'url':url,'route':route,'fetch':'loaded','chars':len(text)}
    return {'cluster_id':cid,'url':url,'route':'','fetch':'unfetchable','chars':0}

def found(text,quote):
    p,q=W(text),W(quote)
    return bool(q) and any(p[i:i+len(q)]==q for i in range(len(p)-len(q)+1))

if __name__=='__main__':
    assert found('Foam fabrication in Hayward','foam fabrication')
    assert found('Injection-molding plastics','Injection molding')
    assert found('Norton Packaging, Inc.','Norton Packaging')
    assert not found('Foam fabrication in Hayward','fabrication foam')
    assert not found('Foam fabrication in Hayward','foam extrusion')
    rows=[r for r in csv.DictReader(open(P/'domains.csv')) if r['url'].startswith('http')]
    out=list(ThreadPoolExecutor(max_workers=4).map(fetch,[(r['cluster_id'],r['url']) for r in rows]))
    with open(P/'fetches.csv','w') as f:
        w=csv.DictWriter(f,fieldnames=out[0],lineterminator='\n');w.writeheader();w.writerows(out)
    print('Matcher known answers: 3 positive, 2 injected negatives passed. Fetches:',[(r['cluster_id'],r['fetch']) for r in out])

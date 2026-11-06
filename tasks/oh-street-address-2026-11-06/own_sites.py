"""Raw-check operator home/contact pages for FRS candidate streets; bounded 3 URLs per operator."""
import concurrent.futures
import csv
import hashlib
import re
import subprocess
from html.parser import HTMLParser
from urllib.parse import urljoin,urlparse
from build import TASK,ROOT,read,write,norm,streetkey

class Page(HTMLParser):
    def __init__(self):
        super().__init__(); self.parts=[]; self.links=[]; self.skip=0
    def handle_starttag(self,tag,attrs):
        if tag in ('script','style'): self.skip+=1
        if tag=='a':
            self.links.extend(v for k,v in attrs if k=='href' and re.search('contact|location',v,re.I))
    def handle_endtag(self,tag):
        if tag in ('script','style'): self.skip=max(0,self.skip-1)
    def handle_data(self,s):
        if not self.skip and s.strip(): self.parts.append(s.strip())

def page(url):
    r=subprocess.run(['curl','--fail','-L','--max-time','20','-A','Mozilla/5.0',url],capture_output=True)
    if r.returncode: raise ValueError('HTTP/transport failure '+str(r.returncode))
    p=Page();p.feed(r.stdout.decode(errors='replace'))
    return p,hashlib.sha256(r.stdout).hexdigest()

def main():
    sites={s['site_id']:s for s in read(TASK/'baseline.csv') if not s['street_address']}
    orgs={r['org_id']:r for p in (ROOT/'data').glob('organizations_*.csv') for r in read(p)}
    leads=[r for r in read(ROOT/'tasks/echo-frs-spine-2026-11-01/site_matches.csv') if r['site_id'] in sites and sites[r['site_id']]['verification_tier'] in ('A','B') and r['match_strength'] in ('exact','strong')]
    groups={}
    for r in leads: groups.setdefault(sites[r['site_id']]['org_id'],[]).append(r)
    def work(item):
        oid,rows=item; base=orgs[oid]['website']; todo=[base] if base else []; checked=[]; found={}
        for _ in range(3):
            if not todo: break
            url=todo.pop(0)
            if url in checked: continue
            checked.append(url)
            try:
                p,sha=page(url); text=' '.join(p.parts); key=streetkey(text)
                for r in rows:
                    addr=streetkey(r['street']); pos=key.find(addr)
                    if pos<0: continue
                    window=key[max(0,pos-100):pos+len(addr)+200]
                    if norm(r['city']) in window and r['zip'][:5] in window:
                        # Keep address-only text, never whole pages containing personal contacts.
                        house=re.escape(r['street'].split()[0]);zip_=re.escape(r['zip'][:5])
                        spans=re.findall(r'\b'+house+r'\b.{0,200}?\b'+zip_+r'(?:-\d{4})?',text)
                        quote=next((q for q in spans if addr in streetkey(q) and norm(r['city']) in streetkey(q)),'')
                        if quote and not re.search(r'@|\b\d{3}[-.]\d{3}[-.]\d{4}\b',quote):
                            found[r['site_id']]=dict(site_id=r['site_id'],url=url,quote=quote,sha256=sha,checked_urls=';'.join(checked),result='VERIFIED')
                for link in p.links:
                    u=urljoin(url,link)
                    if urlparse(u).hostname==urlparse(base).hostname and u not in checked and u not in todo: todo.append(u)
            except Exception: pass
            if len(found)==len({r['site_id'] for r in rows}): break
        return [found.get(r['site_id'],dict(site_id=r['site_id'],url=base,quote='',sha256='',checked_urls=';'.join(checked),result='STILL_UNCERTAIN')) for r in rows]
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        out=[r for group in pool.map(work,groups.items()) for r in group]
    write(TASK/'own_site_checks.csv',out)
    print('Own-site rows',len(out),'verified',sum(r['result']=='VERIFIED' for r in out))

if __name__=='__main__':main()

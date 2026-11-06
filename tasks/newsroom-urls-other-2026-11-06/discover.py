"""Bounded own-domain discovery; candidates require human review before build.py."""
import concurrent.futures, csv, json, re, subprocess, sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin, urlparse
from xml.etree import ElementTree as ET

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SLD2 = {'co','com','org','net','ac','gov','edu','ne','or','go','gob','nic','ltd','plc','sch','mil'}
def domain(url):
    p = (urlparse(url).hostname or '').lower().rstrip('.').split('.')
    return '.'.join(p[-3:] if len(p)>2 and p[-2] in SLD2 and len(p[-1])==2 else p[-2:])

class Links(HTMLParser):
    def __init__(self, body):
        super().__init__(); self.links=[]; self.feeds=[]; self.text=[]; self.href=None; self.label=[]
        self.feed(body)
    def handle_starttag(self, tag, attrs):
        a=dict(attrs)
        if tag=='a': self.href=a.get('href'); self.label=[]
        if tag=='link' and 'alternate' in a.get('rel','') and a.get('type') in ('application/rss+xml','application/atom+xml'):
            self.feeds.append(a.get('href',''))
    def handle_data(self, text):
        self.text.append(text)
        if self.href: self.label.append(text)
    def handle_endtag(self, tag):
        if tag=='a' and self.href:
            self.links.append((self.href,' '.join(' '.join(self.label).split()))); self.href=None

def fetch(url):
    p=subprocess.run(['curl','-L','--max-redirs','5','--max-time','45','--connect-timeout','8','-sS','-A','Mozilla/5.0', '-w','\n%{http_code}\t%{url_effective}',url],capture_output=True,text=True,errors='replace')
    body,_,meta=p.stdout.rpartition('\n'); code,_,final=meta.partition('\t')
    return {'url':url,'final':final,'status':code,'body':body,'error':p.stderr[:180]}

def feed_count(body):
    root=ET.fromstring(body)
    assert root.tag in ('rss','{http://www.w3.org/2005/Atom}feed','{http://www.w3.org/1999/02/22-rdf-syntax-ns#}RDF'),root.tag
    return sum(e.tag in ('item','{http://www.w3.org/2005/Atom}entry','{http://purl.org/rss/1.0/}item') for e in root.iter())

LABEL=re.compile(r'^(?:(?:company|latest|corporate|all|our)\s+)?(?:news(?:\s*(?:room|[&+]\s*(?:events|media)|and\s*(?:events|media)))?|press(?:\s*(?:room|releases|center))?|media(?:\s*(?:center|room))?|announcements)(?:\s*[›»→])?$',re.I)
def discover(r):
    attempts=[]
    def get(url):
        v=fetch(url); attempts.append({k:v[k] for k in ('url','final','status','error')}); return v
    home=get(r['website']); result={**r,'verdict':'STILL_UNCERTAIN','newsroom_url':'','newsroom_feed_url':'','label':'','title':'','years':'','feed_items':0,'note':'Need reachable own-domain newsroom navigation','attempts':attempts}
    if home['status']!='200' or domain(home['final'])!=domain(r['website']): return result
    nav=Links(home['body']); candidates=[]
    for href,label in nav.links:
        url=urljoin(home['final'],href).split('#')[0]
        if LABEL.fullmatch(label) and domain(url)==domain(r['website']) and url not in [u for u,l in candidates]: candidates.append((url,label))
    for url,label in candidates[:3]:
        page=get(url)
        if page['status']!='200' or domain(page['final'])!=domain(r['website']): continue
        parsed=Links(page['body']); title=re.search(r'<title[^>]*>(.*?)</title>',page['body'],re.I|re.S)
        result.update(newsroom_url=page['final'],label=label,title=re.sub(r'\s+',' ',title[1]) if title else '',years=';'.join(sorted(set(re.findall(r'\b20(?:1\d|2\d)\b',' '.join(parsed.text))))),note='Candidate: review purpose and dated items')
        feeds=[urljoin(page['final'],f) for f in parsed.feeds]
        if not feeds: feeds=[urljoin(page['final'],'/feed/'),urljoin(page['final'],'/rss.xml')]
        for feed in dict.fromkeys(feeds):
            if len(attempts)>=6: break
            if domain(feed)!=domain(r['website']): continue
            got=get(feed)
            if got['status']!='200' or domain(got['final'])!=domain(r['website']): continue
            try: count=feed_count(got['body'])
            except (ET.ParseError,AssertionError): continue
            if count: result.update(newsroom_feed_url=got['final'],feed_items=count); break
        break
    return result

if __name__=='__main__':
    rows=list(csv.DictReader(open(HERE/'inputs.csv')))
    prior={r['org_id']:r for r in json.loads((HERE/'discovery.json').read_text())} if (HERE/'discovery.json').exists() else {}
    pending=[r for r in rows if r['org_id'] not in prior]
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as pool:
        new=list(pool.map(discover,pending))
    results=sorted(list(prior.values())+new,key=lambda r:r['org_id'])
    (HERE/'discovery.json').write_text(json.dumps(results,indent=2)+'\n')
    for r in results: print(r['org_id'],r['newsroom_url'],r['title'],r['years'],r['newsroom_feed_url'])

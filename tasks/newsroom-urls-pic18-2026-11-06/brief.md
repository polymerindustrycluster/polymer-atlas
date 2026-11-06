Deep adversarial refute: L9 PIC18 continuation. Return VERDICT APPROVE or REFUTE. Full772 active organization frame with website, tier1 empty, physical PIC18 OH site;39 pages+11 feeds=50 empty cells;733 holds. Only navigation columns under SCHEMA4.4, no EVD required. Controller delegated application. Complete code/allacceptedURLsfollow. Inherit prior PR145 corrections: article-entry-only feed overlap, comments rejected, same-path redirects rejected. Challenge identities,indexpurpose,feedrelationship,framecoverage,builder correctness.
# L9 newsroom round 2 — PIC-18, 2026-11-06

Claim: atlas-L9-newsroom continuation, controller BOARD06:30; branch agent/codex/newsroom-urls-pic18, NEW branch off main9489b60. Integrator delegation remains limited to newsroom_url/newsroom_feed_url. PR145 tier1 work is separate and unchanged. First user: existing news-monitor operator (L8/controller), usable after merge; no new operator system.

## Acceptance and provenance

Full772 distinct active organizations with website, empty tier1_qualifier, and >=1 physical OH site in PIC18 (county suffix normalized). inputs.csv freezes scope; independent self_check recomputes it from canonical org/site shards using scripts/regions.py. Priority counts are mutually exclusive: this pass tier1=0, PIC18 non-tier1=772, other=0. No region tags written to data.

Primary sources are the held canonical own websites and directly linked news/press/announcements indexes. discovery.json records <=6 discovery fetches/org and115 candidate indexes; audit.json records title and parsed visible-text date samples; verdicts.csv has exactly772 dispositions, no silent skips. No full website/sitemap crawl; no matching nav link is a route hold, never absence/closure. No licensed, private or contact data. SCHEMA4.4/V-58 navigation aids need no EVD; lane EVD block unused. No creates (dedupe/ID allocation/append_sorted inapplicable), no tier/status/derived/evidence/registry/LinkedIn/inclusion_log changes.

Accept own-domain organization-specific newsroom indexes. Hold homepage redirects, parent/division/brand mismatches, template/tag/post ambiguity and unreachable routes. Final URL must stay on stored path, trailing slash tolerated. Feeds must parse RSS/Atom with >=1 article entry and link at least one article also linked from the selected index; exclude channel/feed metadata and comments feeds. Builder preflights conflicting populated cells, website/eligibility/PIC18 changes and off-domain/comment URLs before writes. Re-fetch also checks current data matches packet and PIC18 eligibility.

## Reproduce and current results

```
python3 tasks/newsroom-urls-pic18-2026-11-06/self_check.py --live
python3 tasks/newsroom-urls-pic18-2026-11-06/build.py
python3 tasks/newsroom-urls-pic18-2026-11-06/check.py
python3 scripts/validate.py
```

**39 active PIC18 non-tier1 organizations:39 newsroom pages+11 feeds=50 empty cells,4 organization shards.** Filled tier1=0; PIC18 non-tier1=39;other=0. Tiers unchanged: A=15, B=18, C=6, U=0. 733 organization holds:657 no candidate,76 candidate identity/purpose/accessibility holds. Five overlapping feed-only holds (Vertex,BaseTek,Flambeau,Godfrey & Wing,iCHOR) because no article item also linked from selected index. Only two named fields change. Branch history is pre-pass backup; this README is pass journal. No borderline inclusion decisions or record creation.

| Hold group | Active organizations | Settling fact/recommendation |
|---|---:|---|
| No bounded-navigation candidate |657|Reachable own-domain index confirmed; no absence asserted|
| Candidate purpose/identity/accessibility |76|Organization-specific reachable index confirmed; candidates individually named in verdicts.csv|
| Feed-only (overlaps accepted organizations) |5|Dedicated feed/article-item overlap confirmed; pages retained|

Manual identity/purpose exclusions include broad Sealed Air/DuPont/Röchling/Honeywell/Datwyler parent pages, Kenda/Nexen technical-center versus tire-company indexes, Prospect Group versus Prospect Mold, Terry versus Tederic, Beacon versus CleveMed, Rubber Mold Design versus Dalin, broad product divisions, homepage redirects and blog-purpose ambiguity. No identity/scope/vocabulary ruling self-applied. Regional routes Spazzolplastica /us/, Hankook /us/, Yokohamaiaohio own domain and BoleAmerica own domain distinguish their own regional indexes.

Calibration inherited the same standard-library fetcher already tested on Avient,RPM,GEON; --live freshly repeats all3 expected URL discoveries for this pass. Default self_check verifies saved results, not fresh fetching. Prior PR145 Codex/Grok v1 REFUTE lessons are built in before this pass: RSS item/Atom entry-only overlap, comments-feed rejection, same-domain home-redirect rejection, conservative parent/tag/template holds. Defect injections prove each rejection, plus403/off-domain/emptyfeed. No new scripts/ change or dependency.

Checks: build applied50 cells/39 orgs; immediate second run0cells/0shards. Fresh3knownanswers,self_check full772-frame reconciliation, final50-URL refetch and validate0 must pass before push; results in refetch.json. Review status: final Codex/Grok clerk refutes pending; no Done claim.

## Potential staleness leads

Only pre-2024 fully parsed dates occur in the following saved index samples (up to12 distinct dates; nonstandard dates may be missed). Candidate liveness signals only, not newest-release/closure assertions. Old newsrooms still qualify under B-NEWS. Posted to BOARD for L8, no liveness/status fields changed.

| Active organization | Parsed date sample |
|---|---|
| ORG-000156 Swagelok | July 31, 2022 |
| ORG-000174 Vertex, Inc. | October 26, 2018;June 3, 2021;June 5, 2017 |
| ORG-000251 Bole Machinery Inc. | Sep 22, 2023;Aug 18, 2023;May 15, 2023;May 12, 2023;April 17, 2023;April 15, 2023;April 14, 2023;Mar |
| ORG-000340 Flambeau, Inc. | July 23, 2023;February 20, 2023;February 2, 2023;May 16, 2022;March 7, 2022;January 6, 2022;December |
| ORG-000405 Keener Rubber Company | 6/15/2000;7/25/2000;11/15/2000;1/18/2001;1/25/2001;10/2/2001;2/19/2002;5/15/2002;7/23/2002;July 23,  |
| ORG-001327 AltraSet Composite Technologies | Feb 18, 2019 |
| ORG-001717 FlexLink, LLC | March 28, 2016 |
| ORG-001830 Impact Sleeve | May 10, 2017 |
| ORG-001937 Smetzer's Tire Center, Inc. | March 28, 2014 |

CODE discover.py
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
    p=subprocess.run(['curl','-L','--max-redirs','5','--max-time','18','--connect-timeout','8','-sS','-A','Mozilla/5.0', '-w','\n%{http_code}\t%{url_effective}',url],capture_output=True,text=True,errors='replace')
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

CODE audit.py
"""Fetch candidate indexes for review; do not infer activity from copyright years."""
import concurrent.futures, json, re
from discover import HERE, Links, fetch
DATE=re.compile(r'\b(?:20\d\d-\d\d-\d\d|\d{1,2}/\d{1,2}/20\d\d|(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)\.?\s+\d{1,2},?\s+20\d\d|\d{1,2}\s+(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+20\d\d)\b',re.I)
def audit(r):
    p=fetch(r['newsroom_url']);body=re.sub(r'<(script|style)\b.*?</\1>','',p['body'],flags=re.I|re.S)
    parsed=Links(body);text=' '.join(' '.join(parsed.text).split());dates=list(dict.fromkeys(m[0] for m in DATE.finditer(text)))
    return {'org_id':r['org_id'],'status':p['status'],'final':p['final'],'dates':dates[:12],'title':r['title'],'newsroom_url':r['newsroom_url']}
if __name__=='__main__':
    rows=[r for r in json.loads((HERE/'discovery.json').read_text()) if r['newsroom_url']]
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as pool:result=list(pool.map(audit,rows))
    (HERE/'audit.json').write_text(json.dumps(result,indent=2)+'\n')
    print(len(result),'candidate indexes inspected for actual text dates')

CODE build.py
"""Apply reviewed navigation URLs; fail on conflicting values; safe to rerun on fresh main."""
import csv, io
from discover import HERE, ROOT, domain

def main():
    verdicts=list(csv.DictReader(open(HERE/'verdicts.csv')))
    assert len({r['org_id'] for r in verdicts})==len(verdicts)
    edits={r['org_id']:r for r in verdicts if r['verdict']=='VERIFIED'}
    assert edits
    import sys
    sys.path.insert(0,str(ROOT/'scripts'))
    from regions import PIC18
    pic={r['org_id'] for path in (ROOT/'data').glob('sites_*.csv') if path.name!='sites_all.csv' for r in csv.DictReader(open(path)) if r['state']=='OH' and r['county'].removesuffix(' County') in PIC18}
    found=set(); writes=[]; cells=0
    for path in sorted((ROOT/'data').glob('organizations_*.csv')):
        if path.name=='organizations_all.csv': continue
        rows=list(csv.DictReader(io.StringIO(path.read_text()))); header=list(rows[0]) if rows else None
        changed=False
        for row in rows:
            if row['org_id'] not in edits: continue
            v=edits[row['org_id']];found.add(row['org_id'])
            assert row['status']=='active' and not row['tier1_qualifier'] and row['org_id'] in pic,row['org_id']
            website=row['website'] if '://' in row['website'] else 'https://'+row['website']
            assert website==v['website'],row['org_id']
            assert domain(v['newsroom_url'])==domain(website)
            for col in ('newsroom_url','newsroom_feed_url'):
                value=v[col]
                if not value: continue
                assert domain(value)==domain(website),(row["org_id"],col)
                assert "/comments/" not in value.lower() and "feed=comments" not in value.lower()
                assert row[col] in ('',value),(row['org_id'],col,'conflict')
                if row[col]!=value:row[col]=value; changed=True; cells+=1
        if changed:
            buf=io.StringIO();w=csv.DictWriter(buf,fieldnames=header,lineterminator='\n');w.writeheader();w.writerows(rows);writes.append((path,buf.getvalue()))
    assert found==set(edits),(set(edits)-found)
    for path,text in writes:path.write_text(text)
    print(f'{len(edits)} active PIC18 non-tier1 organizations; {cells} cells changed; {len(writes)} shards written')
if __name__=='__main__':main()

CODE check.py
"""Re-fetch all accepted URLs; fail on unreadable pages, redirects off-domain or empty feeds."""
import concurrent.futures, csv, json
from urllib.parse import urljoin
from xml.etree import ElementTree as ET
from discover import HERE, ROOT, Links, domain, fetch, feed_count

def check(r):
    out={'org_id':r['org_id'],'checks':[]}; page_links=set()
    for col in ('newsroom_url','newsroom_feed_url'):
        if not r[col]: continue
        p=fetch(r[col]); assert p['status']=='200',(r['org_id'],col,p['status'])
        assert domain(p['final'])==domain(r['website']),(r['org_id'],p['final'])
        assert p['final'].rstrip('/')==r[col].rstrip('/'),(r['org_id'],'stored URL redirected to another path',p['final'])
        result={k:p[k] for k in ('url','final','status')}
        if col=='newsroom_url':
            page_links={urljoin(p['final'],u.strip()).rstrip('/') for u,l in Links(p['body']).links}
        if col=='newsroom_feed_url':
            result['items']=feed_count(p['body']); assert result['items']>0
            root=ET.fromstring(p['body']); links=set()
            titles=root.findall('./channel/title')+root.findall('{http://www.w3.org/2005/Atom}title')
            assert '/comments/' not in p['final'].lower() and 'feed=comments' not in p['final'].lower()
            assert not any('comments' in (e.text or '').lower() for e in titles),'comments feed'
            entries=[e for e in root.iter() if e.tag in ('item','{http://www.w3.org/2005/Atom}entry','{http://purl.org/rss/1.0/}item')]
            for entry in entries:
                links.update(e.text.strip().rstrip('/') for e in entry.iter('link') if e.text)
                links.update(e.attrib.get('href','').rstrip('/') for e in entry.iter('{http://www.w3.org/2005/Atom}link') if e.attrib.get('rel','alternate')=='alternate')
            assert page_links & links,(r['org_id'],'feed items not linked from newsroom')
            result['linked_items']=len(page_links & links)
        out['checks'].append(result)
    return out

if __name__=='__main__':
    rows=[r for r in csv.DictReader(open(HERE/'verdicts.csv')) if r['verdict']=='VERIFIED']
    assert rows and len({r['org_id'] for r in rows})==len(rows)
    actual={r['org_id']:r for path in (ROOT/'data').glob('organizations_*.csv') if path.name!='organizations_all.csv' for r in csv.DictReader(open(path))}
    import sys
    sys.path.insert(0,str(ROOT/'scripts'))
    from regions import PIC18
    pic={r['org_id'] for path in (ROOT/'data').glob('sites_*.csv') if path.name!='sites_all.csv' for r in csv.DictReader(open(path)) if r['state']=='OH' and r['county'].removesuffix(' County') in PIC18}
    for r in rows:
        assert r['org_id'] in pic
        a=actual[r['org_id']]; assert a['status']=='active' and not a['tier1_qualifier']
        assert all(a[col]==r[col] for col in ('newsroom_url','newsroom_feed_url')),(r['org_id'],'builder not applied')
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool: result=list(pool.map(check,rows))
    (HERE/'refetch.json').write_text(json.dumps(result,indent=2)+'\n')
    print(f'PASS: {len(rows)} active organizations; {sum(len(r["checks"]) for r in result)} URLs, all HTTP 200 and feeds nonempty')

CODE self_check.py
"""Defect injection: the URL/feed gate must reject HTTP failure, off-domain redirects and empty feeds."""
from unittest.mock import patch
from check import check
from discover import domain, feed_count, LABEL
assert LABEL.fullmatch('News + Events')
assert not LABEL.fullmatch('Some individual news article')
assert domain('https://news.example.co.uk/a')=='example.co.uk'
assert feed_count('<rss><channel><item/></channel></rss>')==1
row={'org_id':'test','website':'https://example.com','newsroom_url':'https://example.com/news','newsroom_feed_url':''}
for response in [{'status':'403','final':row['newsroom_url']},{'status':'200','final':'https://other.com'}]:
    with patch('check.fetch',return_value=response):
        try:check(row)
        except AssertionError:pass
        else:raise AssertionError('defect missed')
row.update(newsroom_url='',newsroom_feed_url='https://example.com/feed')
with patch('check.fetch',return_value={'status':'200','url':row['newsroom_feed_url'],'final':row['newsroom_feed_url'],'body':'<rss><channel/></rss>'}):
    try:check(row)
    except AssertionError:pass
    else:raise AssertionError('empty feed missed')
print('PASS: label/domain/feed checks; injected HTTP error, off-domain redirect and empty feed all rejected')
import json
from discover import HERE
known=json.loads((HERE/'known_answers.json').read_text())
assert {r['org_id']:r['newsroom_url'] for r in known}=={'Avient':'https://www.avient.com/company/news-events','RPM':'https://www.rpminc.com/news/','GEON':'https://www.geon.com/news'}
print('PASS: 3 saved live known-answer results match expected newsroom indexes')
import csv
inputs=list(csv.DictReader(open(HERE/'inputs.csv')))
verdicts=list(csv.DictReader(open(HERE/'verdicts.csv')))
discovery=json.loads((HERE/'discovery.json').read_text())
for rows in (inputs,verdicts,discovery):assert len({r['org_id'] for r in rows})==len(rows)==772
assert {r['org_id'] for r in inputs}=={r['org_id'] for r in verdicts}=={r['org_id'] for r in discovery}
assert all(1<=len(r['attempts'])<=6 for r in discovery)
assert all(r['note'] for r in verdicts if r['verdict']=='STILL_UNCERTAIN')
print('PASS: 772/772 input IDs uniquely reconciled to discovery and verdicts; discovery fetch budget <=6; holds explicit')
row={'org_id':'test','website':'https://example.com','newsroom_url':'https://example.com/news','newsroom_feed_url':'https://example.com/feed'}
page={'status':'200','url':row['newsroom_url'],'final':row['newsroom_url'],'body':'<a href="/">Home</a>'}
feed={'status':'200','url':row['newsroom_feed_url'],'final':row['newsroom_feed_url'],'body':'<rss><channel><link>https://example.com/</link><item><link>https://example.com/unlisted</link></item></channel></rss>'}
with patch('check.fetch',side_effect=[page,feed]):
    try:check(row)
    except AssertionError:pass
    else:raise AssertionError('channel home link incorrectly accepted as item overlap')
page['body']='<a href="/unlisted">Actual release</a>'
with patch('check.fetch',side_effect=[page,feed]):assert check(row)['checks'][1]['linked_items']==1
print('PASS: channel metadata link cannot satisfy item overlap; actual item link does')
feed['final']='https://example.com/comments/feed/'
row['newsroom_feed_url']=feed['url']=feed['final']
with patch('check.fetch',side_effect=[page,feed]):
    try:check(row)
    except AssertionError:pass
    else:raise AssertionError('comments feed accepted')
print('PASS: comments feed rejected even when its item links overlap')

badrow={'org_id':'test','website':'https://example.com','newsroom_url':'https://example.com/news','newsroom_feed_url':''}
with patch('check.fetch',return_value={'status':'200','url':badrow['newsroom_url'],'final':'https://example.com/','body':'Home'}):
    try:check(badrow)
    except AssertionError:pass
    else:raise AssertionError('same-domain homepage redirect accepted')
print('PASS: same-domain homepage redirect rejected')
import sys
if '--live' in sys.argv:
    from discover import discover
    for saved in known:
        result=discover({'org_id':saved['org_id'],'website':saved['website']})
        assert result['newsroom_url']==saved['newsroom_url'],result
    print('PASS: 3 fresh live known-answer newsroom discoveries')
from discover import ROOT
sys.path.insert(0,str(ROOT/'scripts'))
from regions import PIC18
pic={r['org_id'] for p in (ROOT/'data').glob('sites_*.csv') if p.name!='sites_all.csv' for r in csv.DictReader(open(p)) if r['state']=='OH' and r['county'].removesuffix(' County') in PIC18}
frame={r['org_id'] for p in (ROOT/'data').glob('organizations_*.csv') if p.name!='organizations_all.csv' for r in csv.DictReader(open(p)) if r['status']=='active' and r['website'] and not r['tier1_qualifier'] and r['org_id'] in pic}
assert frame=={r['org_id'] for r in inputs}
print('PASS: full independent current active/PIC18/non-tier1/website frame matches inputs')

ALL ACCEPTED (id|name|website|newsroom|feed|title|dates):
ORG-000060 | Esterle Mold & Machine Co., Inc. | https://esterle.com | https://esterle.com/news |  | News &amp; Updates - ESTERLE Mold &amp; Machine | August 2, 2026;May 10, 2025;November 6, 2023;August 5, 2023;August 2, 
ORG-000098 | Spazzolplastica North America LLC | https://www.spazzolplastica.it | https://www.spazzolplastica.it/us/news-index |  | Company news and updates | Spazzolplastica | 16 October 2026;09 September 2026;05 August 2026;07 July 2026;30 April
ORG-000105 | Transcendia Inc. | https://www.transcendia.com | https://www.transcendia.com/company-news | https://www.transcendia.com/rss.xml | Company News | Transcendia | June 3, 2025;September 10, 2024;May 2, 2024;September 20, 2021;Decembe
ORG-000130 | Peak Nano | https://www.peaknano.com | https://www.peaknano.com/newsroom |  | Newsroom | Peak Nano | October 19, 2026;September 16, 2026;July 13, 2026;April 26, 2026;April
ORG-000153 | Moen Incorporated | https://www.moen.com | https://www.moen.com/blogs/press-room | https://www.moen.com/blogs/press-room.atom | Moen News &amp; Press Room | Updates &amp; Announcements | June 15, 2026;April 20, 2026;February 17, 2026;June 2, 2025;May 29, 20
ORG-000156 | Swagelok | https://www.swagelok.com | https://www.swagelok.com/en/about/news |  | Swagelok News | Swagelok | July 31, 2022
ORG-000174 | Vertex, Inc. | http://www.vertexseals.com/ | https://vertexseals.com/news/ |  | News - Vertex, Inc. | October 26, 2018;June 3, 2021;June 5, 2017
ORG-000243 | BaseTek, LLC | https://basetek.com/ | https://basetek.com/news/ |  | News - BaseTek | September 14, 2026;June 26, 2026;March 26, 2026;November 25, 2025;Octo
ORG-000251 | Bole Machinery Inc. | https://boleamerica.com/ | https://boleamerica.com/news/ |  | News - Bole Machinery USA | Sep 22, 2023;Aug 18, 2023;May 15, 2023;May 12, 2023;April 17, 2023;Apr
ORG-000259 | CANTEX Inc. | https://www.cantexinc.com/ | https://www.cantexinc.com/news |  |  Latest News and Upcoming Events Calendar | Cantex Inc  | February 11, 2026;January 3, 2022;July 18, 2019
ORG-000315 | Dura-Line | https://www.duraline.com/ | https://www.duraline.com/about-us/news/ |  | News - About Us | Dura-Line | May 15, 2026;October 03, 2025;May 29, 2025;January 15, 2024;April 26, 
ORG-000340 | Flambeau, Inc. | https://www.flambeau.com/ | https://www.flambeau.com/news/ |  | Latest Corporate News and Updates | Flambeau, Inc | July 23, 2023;February 20, 2023;February 2, 2023;May 16, 2022;March 7,
ORG-000355 | Godfrey & Wing | https://www.godfreywing.com/ | https://www.godfreywing.com/news-events/ |  | News &amp; Events - Godfrey ＆ Wing | February 1, 2024
ORG-000384 | Intralox, L.L.C. | https://www.intralox.com/ | https://www.intralox.com/media/news |  | News &amp; Insights | Intralox | November 5, 2026;October 29, 2026;October 16, 2026;September 11, 2026;
ORG-000405 | Keener Rubber Company | http://www.keenerrubber.com/ | http://www.keenerrubber.com/news.htm |  | Keener News Page | 6/15/2000;7/25/2000;11/15/2000;1/18/2001;1/25/2001;10/2/2001;2/19/2002
ORG-000412 | Kobelco Stewart Bolling | https://www.ksbi.com/ | https://www.ksbi.com/news/ | https://www.ksbi.com/feed/ | News &#8211; Kobelco Stewart Bolling, Inc. | September 12, 2024;May 16, 2024;May 2, 2024
ORG-000523 | Pretium Packaging | https://www.pretiumpkg.com/ | https://www.pretiumpkg.com/news-and-events/ | https://www.pretiumpkg.com/feed/ | News and Events - Pretium Packaging | 09/03/2026;September 3, 2026;07/08/2026;July 8, 2026;12/28/2023;10/30/
ORG-000570 | Shini USA | https://www.shiniusa.com/ | https://www.shiniusa.com/our-company/news/ | https://www.shiniusa.com/feed/ | News | Blog Posts | Plastics Industry News | Shini USA | October 14, 2024;October 15, 2024;September 14, 2021;October 20, 2022;
ORG-000603 | Tesla NanoCoatings Inc. | https://teslanano.com/ | https://teslanano.com/offshore-coatings-newsroom/ | https://teslanano.com/feed/ | Tesla NanoCoatings Newsroom: Offshore Coating Insights | October 26, 2026;October 21, 2026;April 11, 2025;March 11, 2025;Februa
ORG-000624 | Uway Extrusion LLC | https://www.uwayextrusion.com/ | https://www.uwayextrusion.com/news |  | News-UWAY | 2026-10-23;2026-11-02;2026-10-16;2026-09-23;2026-09-11;2026-08-27
ORG-000625 | Venture Plastics, Inc. | https://ventureplastics.com/ | https://www.ventureplastics.com/news/ |  | Company News &amp; Case Studies | Venture Plastics, Inc. | June 30, 2026;May 1, 2025;September 18, 2024;April 15, 2022;September 
ORG-000638 | Yokohama Industries Americas Ohio Inc. | https://www.yokohamaiaohio.com/ | https://www.yokohamaiaohio.com/about-us/news |  | News | Yokohama | 7/31/2026;October 30, 2026
ORG-000688 | Autoneum | https://autoneum.com/ | https://autoneum.com/news |  | Autoneum | News &amp; Events | November 2, 2026;October 30, 2026;October 12, 2026;October 10, 2026;No
ORG-000883 | Hub Plastics, Inc. | https://hubplastics.com/ | https://hubplastics.com/announcements/ |  | Announcements | Hub Plastics | 05/15/2024;4/4/2023;9/19/2022;5/1/2019
ORG-001033 | Plastipak Packaging, Inc. | https://www.plastipak.com/ | https://www.plastipak.com/?page_id=52 | https://www.plastipak.com/feed/ | Plastipak Newsroom - Plastipak Packaging, Inc. | Oct 14, 2026;Oct 1, 2026;Aug 21, 2026;Jul 9, 2026;Jul 2, 2026;Jun 12, 
ORG-001078 | Rhetech Colors | https://www.rhetechcolors.com/ | https://www.rhetechcolors.com/news-and-events/ | https://www.rhetechcolors.com/feed/ | News &amp; events - RheTech Colors - Additive Masterbatches | January 29, 2026;July 31, 2026;March 4, 2026
ORG-001105 | Liquibox | https://www.liquibox.com/ | https://www.liquibox.com/news/news-and-press-releases/ |  | News and Press Releases Archives - Liquibox- Sealed Air | May 13, 2024;January 18, 2024;February 22, 2023;February 01, 2023;Janu
ORG-001327 | AltraSet Composite Technologies | https://altraset.mar-bal.com/ | https://altraset.mar-bal.com/news/ | https://altraset.mar-bal.com/feed/ | AltraSet Composite Technologies | News | Feb 18, 2019
ORG-001329 | Dunstone Company Inc. | https://www.shrinktape.com/ | https://www.shrinktape.com/resources/news/ | https://www.shrinktape.com/feed/ | News - Heat Shrinkable Tapes &amp; Tubing | Dunstone | September 2, 2026;May 28, 2026;March 24, 2026;December 18, 2025;Septem
ORG-001394 | Kent Displays, Inc. | https://kentdisplays.com/ | https://kentdisplays.com/news/ |  | News | Kent Displays | January 7, 2026;July 29, 2025
ORG-001494 | Allied Machine & Engineering Corp. | https://alliedmachine.com/ | https://alliedmachine.com/company/news/ |  | Allied - Company News | 9/14/2026;8/10/2026;5/8/2026;4/27/2026;9/22/2025;9/2/2025;6/12/2025;3/
ORG-001508 | ICHOR VASCULAR INC | https://ichorvascular.com/ | https://ichorvascular.com/news-events/ |  | NEWS &amp; EVENTS - iCHOR Updates in Removal Technology and Innovation | October 28, 2026;September 26, 2026;September 14, 2026;August 12, 2026
ORG-001515 | S4 Medical Corp | https://s4medical.com/ | https://www.s4medical.com/media/ |  | Media | S4 Medical | February 1, 2024;July 12, 2023;September 27, 2021;June 29, 2020
ORG-001523 | Centerline Biomedical, Inc. | https://centerlinebiomedical.com/ | https://centerlinebiomedical.com/news-events/ |  | News &#038; Events | Centerline Biomedical | Aug 18, 2025;August 18, 2025;Jul 31, 2025;May 23, 2025;Mar 11, 2025;Ma
ORG-001602 | Royal Powder Corp | https://royalpowder.com/ | https://www.royalpowder.com/news |  | News &mdash; Royal Powder | October 12, 2026;August 3, 2026
ORG-001717 | FlexLink, LLC | https://flexlinkllc.com | https://flexlinkllc.com/news/ | https://flexlinkllc.com/feed/ | Flexlink LLC Company &amp; Industry News - Flexlink, LLC | March 28, 2016
ORG-001830 | Impact Sleeve | https://impactsleeves.com | https://www.impactsleeves.com/about-us/news-events |  |  Impact Sleeves News & Events | Industry Updates  | May 10, 2017
ORG-001937 | Smetzer's Tire Center, Inc. | https://smetzertire.com | https://www.smetzertire.com/About-Us/News |  |  Wooster, OH Tires Shop News :: Smetzer's Tire Center, Inc.  | March 28, 2014
ORG-003545 | G-3 Chickadee Purchaser, LLC | https://g-3chickadee.com/ | https://www.g-3chickadee.com/newsroom |  | G-3 Chickadee Media: Press Releases &amp; News Inquiries | May 22, 2025

Adversarial completion refute for Atlas L9. Return APPROVE or REFUTE with concrete defects. You have the complete code and complete accepted URL list below; no external tool access is assumed. Do not demand a full website census: controller scope = every ACTIVE tier1_qualifier-nonempty org with website attempted, fills + explicit holds. Second/third PRs cover PIC18/other separately. Read §4.4: newsroom navigation aids are NOT evidence, own registrable domain only; no EVD needed. V-58 uses short two-level suffix list mirrored here. Branch data changes ONLY 177 empty newsroom_url/newsroom_feed_url cells in 118 existing active tier1 orgs. No status/tier/dates/registry/evidence fields changed.
# L9 newsroom navigation — 2026-11-06

Claim: atlas-L9-newsroom; branch agent/codex/newsroom-urls. Controller delegated application of these two columns.
First user: existing news-monitor operator (L8/controller); URLs usable when this PR lands. This task adds navigation data, not a new user-operated system.

## Scope and acceptance

Controller ruling 2026-11-06 supersedes the proposed 100-org cap: attempt every active organization with a nonempty tier1_qualifier and website, using the column as-is (pending derivation gains excluded). First PR only; PIC-18 non-tier1 and other organizations belong to subsequent PRs. inputs.csv freezes 1,043 distinct active organizations from the 1,261 active tier1 organizations; 218 without a website are outside the fetch frame.

Acceptance: fill only reachable own-domain news/press/announcements indexes; hold redirects to home pages, ambiguous purpose, parent/division mismatches and inaccessible pages. Feeds must parse as RSS/Atom with >=1 item. No status, verification tier, evidence, liveness, derived field, registry or LinkedIn changes. §4.4 explicitly makes these navigation aids, never evidence by themselves; EVD-230000–239999 remains unused. No factual evidence claims or quotes are added. Primary sources are the organization websites and the linked indexes in verdicts.csv.

## Reproduce

- `python3 tasks/newsroom-urls-2026-11-06/self_check.py`
- `python3 tasks/newsroom-urls-2026-11-06/build.py` (idempotent; fail on conflicting nonempty cells, website changes or eligibility changes; fresh-main rebase re-runs this)
- `python3 tasks/newsroom-urls-2026-11-06/check.py` (every accepted page and feed, HTTP 200, final domain check, nonempty RSS/Atom)
- `python3 scripts/validate.py` (0 errors, V-58 clean)

Branch history is the pre-pass backup. The builder preflights all edited shards before any write. No rows are created, so ID allocation, dedupe and append_sorted do not apply. Only two cells per accepted organization can change; generated exports are untouched. Known CRLF-dirty federal-frame files are excluded.

## Discovery and calibration

`discover.py` extracts exact newsroom navigation labels, fetches up to three candidates, then advertised RSS/Atom feeds or /feed/ and /rss.xml. Up to six discovery fetches per organization; prior attempts are retained, not silently retried. No third-party wire service or social platform is accepted. Ambiguous or unavailable routes remain STILL_UNCERTAIN, never evidence of absence.

Three known-answer records: Avient /company/news-events, RPM /news/, GEON /news all PASS (known_answers.json). Initial matcher missed Avient's “News + Events”; fixed before accepting output. Goodyear had no matching link and Lubrizol/Parker returned 403; these are route failures, not negative findings. self_check.py injects 403, an off-domain redirect and empty RSS and confirms each fails. Domain matching mirrors V-58's documented short two-level-suffix heuristic; no new dependency.

## Results and holds

Pending final verification. verdicts.csv will contain one disposition per input, with a named settling fact for every STILL_UNCERTAIN row. Discovery is not complete website crawling: pages without a matching nav link are held even if a newsroom may exist elsewhere. Date years in discovery.json include footer years and are not liveness evidence. Staleness is recorded only after actual dated-item review; no status motion follows.

Baseline `python3 scripts/validate.py`: PASS (4,945 organization rows; existing warnings only). `council-doctor --json`: healthy, all four configured providers pass. No third-party API bulk sources used. Catalogue search was incomplete because the Mac lacks the Windows Documents catalogues; this is not a finding of absence, and discovery uses the already-held canonical website column.

### Potential staleness leads

These indexes have only pre-2024 dates in the parsed date sample (up to 12 distinct dates; nonstandard dates may be missed). This is a **candidate signal**, not a claim about the newest release or operating status. MFG alone was manually confirmed latest 2023-10-26. All remain valid navigation pages.

| Active organization | Date sample |
|---|---|
| ORG-000138 Permatex | February 14, 2020;December 21, 2018 |
| ORG-000430 Mar-Bal Inc. | August 9, 2021;February 24, 2020;February 8, 2021 |
| ORG-000451 Molded Fiber Glass Companies | October 26, 2023;October 5, 2023;August 21, 2023;August 7, 2023;November 17, 2022;October 7, 2022;January 24,  |
| ORG-000835 Fiber-Tech Industries, Inc. | July 30, 2019 |
| ORG-000868 Guardian Manufacturing Company | June 22, 2018;April 5, 2018;September 27, 2018 |
| ORG-001080 Ridge Corporation | September 30, 2021;September 28, 2019;July 26, 2019;January 29, 2018;July 26, 2017;February 29, 2016 |
| ORG-002174 Parker Rust-Proof of Cleveland | 07/08/2022;3/19/2020;2/26/2020 |
| ORG-002401 Mi Windows & Doors Inc. | November 10, 2022;November 02, 2022;October 17, 2022;September 13, 2022;September 07, 2022;August 22, 2022;Jul |
| ORG-002497 The Murus Company | March 15, 2013 |
| ORG-003132 Seasafe, Inc. | Apr 20 2021;April 20, 2021;Jan 25 2021;January 25, 2021;Mar 19 2020;March 19, 2020;Apr 30 2018;April 30, 2018; |
| ORG-003183 AmFine Chemical Corporation | November 12, 2015;June 4, 2014;April 11, 2014 |
| ORG-003194 REXtac, LLC | June 7, 2022;January 1, 2022;December 16, 2021;June 22, 2021;August 20, 2020;April 11, 2019;December 12, 2018; |
| ORG-003219 Covation Biomaterials LLC | May 11, 2023 |
| ORG-003952 Augusta Fiberglass Coatings, Inc. | October 20, 2016;September 6, 2016;July 22, 2016;January 6, 2016;December 10, 2015 |
| ORG-003989 General Plastics Manufacturing Company | May 15, 2019;Oct 20, 2015;September 8, 2015;Oct 6, 2014;October 07, 2014;October 2, 2014;September 23, 2014;Oc |
| ORG-004137 R3 Composites Corp | Feb 11, 2021 |
| ORG-004287 Thorpe Plant Services, Inc. | September 13, 2022;January 18, 2022;June 13, 2016 |
| ORG-004291 Viskase Companies, Inc. | May 31, 2022;February 8, 2022;January 4, 2022;October 6, 2021;April 16, 2021;April 15, 2021;November 24, 2020; |
| ORG-004386 Dicar Inc | May 31, 2022;Mar 23, 2020;March 22, 2020;Mar 20, 2020;Feb 22, 2019;Sep 28, 2018;Jul 18, 2018;Apr 19, 2018 |
| ORG-004533 Bomar Specialties, LLC | January 31, 2023;May 4, 2022;January 31, 2022;June 8, 2021;April 5, 2021;November 2, 2020 |
| ORG-004556 Oregon Rubber Mills Co | 6/3/2016 |
| ORG-004620 Mississippi Polymers, Inc. | 06/01/2017;12/05/2016;11/22/2016;11/01/2016 |

### Final application and checks

Unit/filter: **active organizations**, mutually exclusive priority buckets (tier1 first, then PIC-18 non-tier1, then other). This PR attempts tier1=1,043; PIC-18 non-tier1=0; other=0. Fills: **tier1=118 organizations with 118 newsroom URLs and 59 feeds; PIC-18 non-tier1=0; other=0**. 177 empty cells filled in 118 existing organization rows, across 28 organization shards. No records created. Verification tiers of changed organizations: A=39, B=71, C=7, U=1 (unchanged). 925 STILL_UNCERTAIN organization holds, individually listed in verdicts.csv. No borderline inclusion decisions and no inclusion_log rows.

344 candidate indexes were found. Accepted indexes have an own-domain nav label, matching organization brand in title, and actual text dates in audit.json. Human exclusions include home redirects, parent/group indexes for subsidiary records, investor-only indexes, product-division indexes and page-purpose ambiguity. Identity/page-purpose holds require a confirmed organization-specific index. Route holds require a reachable own-domain index; failed routes make no negative entity assertion. Three candidate feeds (Albemarle, Bryce, R3) were omitted because no item was also linked from the selected index. No external feed hosts filled.

- `self_check.py`: PASS; 3 live known-answer results; injected failure cases caught; full 1,043-ID reconciliation and <=6 discovery requests per organization.
- `build.py`: 118 organizations, 177 cells; immediate second run **0 cells, 0 shards written**.
- `check.py`: **PASS: 118 active organizations; 177 URLs, all HTTP 200 and feeds nonempty**. Every feed additionally has >=1 item linked from its selected newsroom. `refetch.json` records every result.
- `python3 scripts/validate.py`: **0 errors / OK — validation passed**, V-58 clean, existing warnings unchanged.
- `python3 -m unittest discover -s scripts -p 'test_*.py'`: **221 tests, OK (skipped=1)**. Existing build_site.py SyntaxWarning observed; no scripts/ files changed.
- Independent before/after comparison against branch HEAD: **177 changed cells, 118 existing organization IDs, only newsroom_url/newsroom_feed_url, every prior value empty**. No other fields or row sets changed.

### Refute reviews

Pending Codex and Grok deep refute verdicts. No completion claim until both resolved.

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
    found=set(); writes=[]; cells=0
    for path in sorted((ROOT/'data').glob('organizations_*.csv')):
        if path.name=='organizations_all.csv': continue
        rows=list(csv.DictReader(io.StringIO(path.read_text()))); header=list(rows[0]) if rows else None
        changed=False
        for row in rows:
            if row['org_id'] not in edits: continue
            v=edits[row['org_id']];found.add(row['org_id'])
            assert row['status']=='active' and row['tier1_qualifier'],row['org_id']
            website=row['website'] if '://' in row['website'] else 'https://'+row['website']
            assert website==v['website'],row['org_id']
            assert domain(v['newsroom_url'])==domain(website)
            for col in ('newsroom_url','newsroom_feed_url'):
                value=v[col]
                if not value: continue
                assert row[col] in ('',value),(row['org_id'],col,'conflict')
                if row[col]!=value:row[col]=value; changed=True; cells+=1
        if changed:
            buf=io.StringIO();w=csv.DictWriter(buf,fieldnames=header,lineterminator='\n');w.writeheader();w.writerows(rows);writes.append((path,buf.getvalue()))
    assert found==set(edits),(set(edits)-found)
    for path,text in writes:path.write_text(text)
    print(f'{len(edits)} active tier1 organizations; {cells} cells changed; {len(writes)} shards written')
if __name__=='__main__':main()

CODE check.py
"""Re-fetch all accepted URLs; fail on unreadable pages, redirects off-domain or empty feeds."""
import concurrent.futures, csv, json, re
from urllib.parse import urljoin
from xml.etree import ElementTree as ET
from discover import HERE, Links, domain, fetch, feed_count

def check(r):
    out={'org_id':r['org_id'],'checks':[]}; page_links=set()
    for col in ('newsroom_url','newsroom_feed_url'):
        if not r[col]: continue
        p=fetch(r[col]); assert p['status']=='200',(r['org_id'],col,p['status'])
        assert domain(p['final'])==domain(r['website']),(r['org_id'],p['final'])
        result={k:p[k] for k in ('url','final','status')}
        if col=='newsroom_url':
            page_links={urljoin(p['final'],u.strip()).rstrip('/') for u,l in Links(p['body']).links}
        if col=='newsroom_feed_url':
            result['items']=feed_count(p['body']); assert result['items']>0
            root=ET.fromstring(p['body']); links={e.text.strip().rstrip('/') for e in root.iter('link') if e.text}
            links.update(e.attrib.get('href','').rstrip('/') for e in root.iter('{http://www.w3.org/2005/Atom}link'))
            assert page_links & links,(r['org_id'],'feed items not linked from newsroom')
            result['linked_items']=len(page_links & links)
        out['checks'].append(result)
    return out

if __name__=='__main__':
    rows=[r for r in csv.DictReader(open(HERE/'verdicts.csv')) if r['verdict']=='VERIFIED']
    assert rows and len({r['org_id'] for r in rows})==len(rows)
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
for rows in (inputs,verdicts,discovery):assert len({r['org_id'] for r in rows})==len(rows)==1043
assert {r['org_id'] for r in inputs}=={r['org_id'] for r in verdicts}=={r['org_id'] for r in discovery}
assert all(1<=len(r['attempts'])<=6 for r in discovery)
assert all(r['note'] for r in verdicts if r['verdict']=='STILL_UNCERTAIN')
print('PASS: 1043/1043 input IDs uniquely reconciled to discovery and verdicts; discovery fetch budget <=6; holds explicit')

ALL ACCEPTED URLS (org id | name | website | newsroom | feed | title | text date sample):
ORG-000001 | Avient Corporation | https://www.avient.com | https://www.avient.com/company/news-events |  | Avient News Center: Press Releases &amp; Upcoming Events | September 28, 2026;Nov 04, 2026;Oct 14, 2026;Oct 09, 2026;Sep 28, 2026
ORG-000006 | RPM International Inc. | https://www.rpminc.com | https://www.rpminc.com/news/ |  | Company News | RPM International Inc. | 11/02/2026;10/08/2026;10/06/2026;10/01/2026;09/23/2026;09/04/2026;Octo
ORG-000010 | GEON Performance Solutions | https://www.geon.com | https://www.geon.com/news | https://www.geon.com/news/rss.xml | News | GEON® Performance Solutions | July 09, 2026;July 9, 2026;March 10, 2026;March 09, 2026;January 21, 2
ORG-000134 | Novagard Solutions | https://novagard.com | https://novagard.com/news-events/ |  | Novagard News &amp; Events | Awards, Press, Industry | August 26, 2026;January 30, 2026;October 21, 2025;June 5, 2025;9/25/20
ORG-000135 | Valtris Specialty Chemicals | https://www.valtris.com | https://www.valtris.com/news/category/news/ | https://www.valtris.com/news/category/news/feed/ | News Archives - Valtris Specialty Chemicals | August 17, 2026;July 27, 2026;May 4, 2026;April 20, 2026;February 4, 2
ORG-000138 | Permatex | https://www.permatex.com | https://www.permatex.com/category/news-events/ | https://www.permatex.com/feed/ | News &amp; Events Archives | Permatex® | February 14, 2020;December 21, 2018
ORG-000196 | Goldsmith & Eggleton | https://www.goldsmith-eggleton.com/ | https://goldsmith-eggleton.com/latest-news/ | https://goldsmith-eggleton.com/feed/ | Latest News | Goldsmith-Eggleton | July 28, 2025;March 14, 2024;December 7, 2022;January 1, 2023;June 27,
ORG-000234 | Architectural Fiberglass, Inc. | https://www.fiberglass-afi.com/ | https://www.fiberglass-afi.com/press-releases/ | https://www.fiberglass-afi.com/feed/ | Press Releases | Architectural Fiberglass, Inc. | February 19, 2024;October 9, 2005;February 16, 2024;February 15, 2024;
ORG-000317 | Duramax Marine, LLC | https://www.duramaxmarine.com/ | https://www.duramaxmarine.com/news-articles/ |  | Duramax Marine: News Articles | August 31, 2026;July 13, 2026;November 4, 2024;February 24, 2023
ORG-000372 | Huntsman Corporation | https://www.huntsman.com/ | https://www.huntsman.com/news | https://www.huntsman.com/news/media-releases/rss | Read the Latest Huntsman News :: Huntsman Corporation (HUN) | Nov 2, 2026;Oct 6, 2026;November 3, 2026;Sep 11, 2026;Aug 25, 2026;Nov
ORG-000430 | Mar-Bal Inc. | https://www.mar-bal.com/ | https://www.mar-bal.com/category/news/ |  | News Archives - Mar-Bal, Inc. | August 9, 2021;February 24, 2020;February 8, 2021
ORG-000451 | Molded Fiber Glass Companies | https://moldedfiberglass.com/ | https://moldedfiberglass.com/category/company-news/ | https://moldedfiberglass.com/category/company-news/feed/ | Company News Archives - Molded Fiber Glass Companies | October 26, 2023;October 5, 2023;August 21, 2023;August 7, 2023;Novemb
ORG-000473 | Oldcastle Infrastructure (IPG | https://oldcastleinfrastructure.com/ | https://oldcastleinfrastructure.com/press-releases/ | https://oldcastleinfrastructure.com/feed/ | Newsroom | Oldcastle Infrastructure | June 23, 2026;June 1, 2026;February 9, 2026;February 6, 2026;November 
ORG-000483 | Pentair | https://www.pentair.com/ | https://www.pentair.com/en-us/about-pentair/newsroom.html |  | Newsroom | About Pentair | Pentair | Oct. 19, 2026;Oct. 14, 2026;Sep. 22, 2026
ORG-000543 | Refcotec, Inc. | https://www.refcotec.com/ | https://www.refcotec.com/news |  | REFCOTEC News - Refractory Coatings, Foundry Resin Systems, Sand Additives, Heat Resistant Coatings | March 2, 2026;January 29, 2026;February 27, 2023;April 19, 2022;Januar
ORG-000544 | Foundation Wellness | https://foundationwellness.com/ | https://foundationwellness.com/blogs/news | https://foundationwellness.com/blogs/news.atom |  News &ndash; Foundation Wellness | May 13, 2025;September 5, 2024;May 7, 2024;August 6, 2021;December 3, 
ORG-000566 | Sealed Air Corporation | https://www.sealedair.com/ | https://www.sealedair.com/company/media-center/press-releases |  | Press Releases - Sealed Air | October 15, 2026;September 22, 2026;August 24, 2026;April 9, 2026;Janu
ORG-000569 | Shin-Etsu Silicones of America, Inc. | https://www.shinetsusilicones.com/ | https://www.shinetsusilicones.com/news.aspx |  | Shin-Etsu News | 2026-10-28;2025-07-08;2025-03-03;2024-07-02;2024-07-10;2022-12-20;2022
ORG-000698 | BASF Corporation | https://www.basf.com/us/en.html | https://www.basf.com/us/en/media |  | Welcome to the BASF News &amp; Media Center | Nov. 11, 2026;July 29, 2026
ORG-000720 | Capital Resin Corporation | https://capitalresin.com/ | https://capitalresin.com/news/ | https://capitalresin.com/feed/ | Chemical Toll Manufacturing News | Capital Resin | Oct 29 2026;Oct 20 2026;Sep 24 2026
ORG-000763 | Crane ChemPharma & Energy | https://cranecpe.com/ | https://cranecpe.com/news-events/ | https://cranecpe.com/feed/ | News &amp; Events - CRANE ChemPharma &amp; Energy | 10/20/2026;09/08/2026;06/29/2026;06/18/2026;03/25/2026;10/24/2025
ORG-000768 | Creative Composites Group | https://www.creativecompositesgroup.com/ | https://www.creativecompositesgroup.com/about-us/newsroom |  | Newsroom | Creative Composites Group | Oct 6, 2026;October 6, 2026;Nov 10, 2025;October 8, 2025;Oct 10, 2025;
ORG-000769 | Creative Foam Corporation | https://creativefoam.com/ | https://creativefoam.com/news/ |  | News - Creative Foam | March 6, 2025;3/5/2025;July 23, 2021;July 15, 2021;March 8, 2021;Novem
ORG-000786 | Deceuninck North America, LLC | https://deceuninckna.com/ | https://deceuninckna.com/news-and-press/ | https://deceuninckna.com/news-and-press/feed/ | News Archive - Deceuninck North America | September 14, 2026;April 1, 2026;March 26, 2026;February 17, 2026;Dece
ORG-000821 | Emery Oleochemicals | https://www.emeryoleo.com | https://www.emeryoleo.com/news | https://www.emeryoleo.com/rss.xml | Latest News | Innovations and Events| Emery Oleochemicals | March 30, 2026;May 6, 2026;December 15, 2025;August 18, 2025;July 14, 
ORG-000835 | Fiber-Tech Industries, Inc. | https://www.fiber-tech.net/ | https://www.fiber-tech.net/news |  | News | Fiber-Tech Industries | July 30, 2019
ORG-000868 | Guardian Manufacturing Company | https://guardian-mfg.com/ | https://guardian-mfg.com/news/ |  | News | Electrician Gloves for Guardian Manufacturing | June 22, 2018;April 5, 2018;September 27, 2018
ORG-000880 | Hexion Inc. | https://www.hexion.com/ | https://www.hexion.com/news |  | News | Hexion | May 4, 2026;Apr 21, 2026;Feb 9, 2026;Sep 23, 2025;Aug 8, 2025;Jun 30, 
ORG-000931 | Lear Corporation | https://www.lear.com/ | https://www.lear.com/newsroom |  | Newsroom | Lear Corporation | October 30, 2026;October 19, 2026;June 22, 2026;April 28, 2026;October
ORG-000947 | Mason Color Works | https://www.masoncolor.com/ | https://www.masoncolor.com/about/news | https://www.masoncolor.com/feed | News | Mason Color Works | August 26, 2026;November 17, 2025
ORG-000975 | Nagase ChemteX America | https://nagasechemtex.com/ | https://nagasechemtex.com/news/ |  | News | Nagase ChemteX | January 3, 2024;December 14, 2020
ORG-000979 | Neaton Auto Products Manufacturing | https://www.neaton.com/ | https://www.neaton.com/neaton-newsroom |  | Neaton Newsroom &mdash; Neaton Auto Products Manufacturing | September 17, 2025
ORG-001080 | Ridge Corporation | https://ridgecorp.com/ | https://ridgecorp.com/category/news/ | https://ridgecorp.com/category/news/feed/ | News Archives - Ridge Corporation | September 30, 2021;September 28, 2019;July 26, 2019;January 29, 2018;J
ORG-001090 | Rowmark LLC | https://www.rowmark.com | https://www.rowmark.com/news |  | Rowmark | News | January 31, 2024;June 9, 2022;March 4, 2022;July 13, 2021;June 22, 202
ORG-001109 | Shelter Works | https://www.shelterworks.com/ | https://www.shelterworks.com/news.html |  | Shelter Works News & Updates | Oct 05, 2026;Oct 01, 2026;Sep 24, 2026;Aug 25, 2026;Jun 08, 2026;Apr 1
ORG-001110 | The Shepherd Color Company | https://www.shepherdcolor.com | https://www.shepherdcolor.com/news-events/ | https://www.shepherdcolor.com/feed/ | News + Events - Shepherd Color | October 8, 2026;September 25, 2026;September 24, 2026;July 14, 2026;No
ORG-001202 | Woodbridge Corporation | https://www.woodbridgegroup.com/ | https://www.woodbridgegroup.com/Resources/Newsroom |  | Newsroom | Woodbridge  | 6/19/2026;6/18/2026;2/19/2026;6/10/2025;5/7/2025;2/24/2025;2/14/2025;1
ORG-001545 | AtriCure, Inc. | https://atricure.com/ | https://news.atricure.com/ |  | AtriCure News | July 21, 2026
ORG-001572 | Therma-Tru Corp. | https://www.thermatru.com/ | https://www.thermatru.com/newsroom/ |  | Newsroom | Therma-Tru Doors | 10/13/2026;07/20/2026;02/12/2026;6/03/2025;5/29/2025;4/16/2025;2/25/20
ORG-002174 | Parker Rust-Proof of Cleveland | https://www.parkerhq.com | https://www.parkerhq.com/news |  | News | Parker Rust-Proof | 07/08/2022;3/19/2020;2/26/2020
ORG-002350 | Veka Inc. | https://vekainc.com | https://www.vekainc.com/resources/news-events/ |  | VEKA Inc. | News | Events | 08/10/2025;11/08/2025;23/09/2024;21/05/2024
ORG-002353 | Am Stabilizers Corporation | https://amstabilizers.com/ | https://amstabilizers.com/latest/news |  | News | AM Stabilizers | March 24, 2026;February 18, 2026;January 19, 2026;January 7, 2026;Dece
ORG-002401 | Mi Windows & Doors Inc. | https://miwindows.com/hegins-location | https://miwindows.com/news | https://miwindows.com/rss.xml | Window News &amp; Industry Updates | MI Windows and Doors | November 10, 2022;November 02, 2022;October 17, 2022;September 13, 202
ORG-002497 | The Murus Company | https://murus.com | https://murus.com/about/newspress-materials/ |  | News and Events &#187; Murus.com | March 15, 2013
ORG-002547 | Patrick Industries, Inc. | https://patrickind.com/ | https://patrickind.com/news/ |  | News - Patrick Industries | December 3, 2024
ORG-002758 | Neville Chemical Co | https://nevchem.com/ | https://www.nevchem.com/news/ | https://www.nevchem.com/feed/ | News - Neville Chemical | April 29, 2026;March 11, 2026;December 2, 2025;July 24, 2025;July 17, 
ORG-002874 | Solstice Advanced Materials Inc. | https://www.solstice.com | https://www.solstice.com/us/en/news-events |  | News &amp; Events | Solstice Advanced Materials | Nov 04 2026;Oct 16 2026;Oct 10 2026;Oct 1 2026;November 4, 2026;August
ORG-002875 | Rogers Corporation | https://www.rogerscorp.com | https://www.rogerscorp.com/news |  | Rogers Corporation News | Oct 27, 2026;Oct 13, 2026;Sep 30, 2026;September 30, 2026;Sep 09, 2026
ORG-002879 | AdvanSix Inc. | https://www.advansix.com | https://www.advansix.com/newsroom/ | https://www.advansix.com/feed/ | Latest News | Advansix | Nov 4, 2026;Oct 29, 2026;Oct 5, 2026;Sep 4, 2026;Aug 7, 2026;Aug 4, 20
ORG-002888 | Albemarle Corporation | https://www.albemarle.com | https://www.albemarle.com/us/en/newsroom |  | Newsroom | Albemarle | September 29, 2026;March 31, 2026;January 14, 2026;November 04, 2026;N
ORG-002890 | Northann Corp. | https://www.northann.com | https://www.northann.com/news |  | News | Northann Corp | October 16, 2026;October 7, 2026;October 1, 2026;August 31, 2026;June 
ORG-002892 | Reynolds Consumer Products Inc. | https://www.reynoldsconsumerproducts.com | https://www.reynoldsconsumerproducts.com/news |  | NEWS | Reynolds Consumer Products | May 1, 2025;Nov 20, 2024;Nov 1, 2024;Sep 6, 2024;September 25, 2024;Ap
ORG-002908 | Cabot Corporation | https://www.cabotcorp.com | https://www.cabotcorp.com/company/newsroom |  | Newsroom | Cabot Corporation press releases, product launches and current news | 10/13/2026;10/1/2026;9/17/2026;9/15/2026;8/12/2026;7/30/2026;7/10/2026
ORG-002910 | Chevron Phillips Chemical Company LLC | https://www.cpchem.com | https://www.cpchem.com/media-events/news |  | News | Chevron Phillips Chemical | 07/30/2026;07/28/2026;07/22/2026;06/29/2026;06/15/2026;05/28/2026;05/2
ORG-002955 | Modern Dispersions, Inc. | https://www.moderndispersions.com/ | https://www.moderndispersions.com/news/ | https://www.moderndispersions.com/feed/ | News | Modern Dispersions, Inc. | Leominster, MA | April 9, 2026
ORG-003057 | Lion Elastomers LLC | https://www.lionelastomers.com | https://www.lionelastomers.com/news |  | News - Lion Elastomers - A Leader in Synthetic Rubber | Sep 18, 2026;Feb 24, 2026;Feb 14, 2024;February 13, 2024
ORG-003079 | Kaneka North America LLC | https://www.kaneka.com/ | https://www.kaneka.com/kaneka-americas/newsroom/ |  | Newsroom - Kaneka Americas | September 07, 2026
ORG-003082 | NanoXplore Inc. | https://nanoxplore.ca | https://nanoxplore.ca/press-releases/ |  | Press Releases | NanoXplore | November 2, 2026;October 5, 2026;September 17, 2026;September 15, 2026
ORG-003095 | Continental Tire the Americas, LLC | https://www.continentaltire.com | https://continentaltire.com/learn/news-and-events |  | News | Continental Tire | August 18, 2026;July 1, 2026;January 15, 2026;December 12, 2025;Novemb
ORG-003104 | Gelest, Inc. | https://www.gelest.com/ | https://www.gelest.com/about-gelest/news/ | https://www.gelest.com/feed/ | News - Gelest, Inc. | February 12, 2026;February 06, 2026;December 29, 2025;May 19, 2025;Jul
ORG-003129 | Osborne Industries, Inc. | http://www.osborneindustries.com | https://www.osborneindustries.com/news/ | https://www.osborneindustries.com/feed/ | Osborne Company News &amp; Industry Updates | Osborne Industries | June 10, 2026;April 7, 2026;March 30, 2026;February 10, 2026;December 
ORG-003132 | Seasafe, Inc. | http://www.seasafe.com | https://seasafe.com/news/ | https://seasafe.com/feed/ | SeaSafe News Blog, structural fiberglass industry news | Apr 20 2021;April 20, 2021;Jan 25 2021;January 25, 2021;Mar 19 2020;Ma
ORG-003151 | Bryce Corporation | https://www.brycecorp.com | https://brycecorp.com/news |  | News | Bryce Corporation | Apr 29 2025;6/4/2024;June 4, 2024;Apr 12 2023;August 24, 2022;Apr 14 2
ORG-003163 | Stepan Company | https://www.stepan.com | https://www.stepan.com/content/stepan-dot-com/en/news-events.html |  | Stepan Company News and Events | Specialty Chemicals Solutions | April 1, 2026;April 7, 2026;September 15, 2026
ORG-003183 | AmFine Chemical Corporation | https://www.amfine.com | https://amfine.com/news/ | https://amfine.com/news/feed/ | Amfine News | What&#039;s happening at Amfine Chemical Corporation | November 12, 2015;June 4, 2014;April 11, 2014
ORG-003191 | Alberdingk Boley, Inc. | http://www.alberdingkusa.com/ | https://www.alberdingkusa.com/News/ |  | News | Alberdingk Boley | January 26, 2026;October 25, 2025;August 18, 2025;April 23, 2025;Decem
ORG-003194 | REXtac, LLC | http://www.rextac.com | https://www.rextac.com/about-us/news-and-events/ | https://www.rextac.com/feed/ | News and Events | REXtac LLC | June 7, 2022;January 1, 2022;December 16, 2021;June 22, 2021;August 20
ORG-003208 | Ascend Performance Materials Holdings Inc. | http://www.ascendmaterials.com | https://www.ascendmaterials.com/about/newsroom | https://www.ascendmaterials.com/feeds/feed.rss | Newsroom | Ascend Performance Materials | April 29, 2026;February 4, 2026;December 19, 2025;December 10, 2025;De
ORG-003219 | Covation Biomaterials LLC | http://www.covationbio.com | https://covationbio.com/press-room |  | Press Room | Covation Biomaterials | May 11, 2023
ORG-003258 | Pipeline Plastics, LLC | https://www.pipe.us | https://www.pipe.us/news-events/ |  | News &#038; Events | Pipeline Plastics | October 20, 2026;October 24, 2025;October 28, 2025;February 20, 2025;F
ORG-003286 | Altec Industries, Inc. | http://altec.com | https://www.altec.com/about-altec/press-releases |  | Press Releases &#8211; Altec Inc | June 17, 2026;March 1, 2025;November 15, 2021;October 7, 2021;Septembe
ORG-003318 | Interplastic Corporation | http://www.interplastic.com | https://interplastic.com/category/news-events/news/ | https://interplastic.com/feed/ | News &#8211; Interplastic Corporation | September 18, 2026;June 3, 2026;February 18, 2026;March 20, 2026;April
ORG-003361 | Valto Engineered Materials | http://www.valtoem.com | https://valtoem.com/news/ | https://valtoem.com/feed/ | News - VALTO Engineered Materials | February 17, 2026;September 2, 2025;June 28, 2025;May 19, 2025;April 1
ORG-003639 | Douglas Dynamics Inc. | https://www.douglasdynamics.com/ | https://www.douglasdynamics.com/news/ | https://www.douglasdynamics.com/feed/ | News - Douglas Dynamics | September 17, 2026;August 24, 2026;November 11, 2025;September 22, 202
ORG-003922 | Meridian Adhesives Group LLC | https://meridianadhesives.com | https://meridianadhesives.com/about/news/ | https://meridianadhesives.com/feed/ | News | Innovations in Adhesives Market | Meridian Adhesives | 1 October 2026;27 May 2026;18 December 2025;1 October 2025;25 August 2
ORG-003952 | Augusta Fiberglass Coatings, Inc. | http://www.augustafiberglass.com/ | https://www.augustafiberglass.com/news-augusta-fiberglass.html | https://www.augustafiberglass.com/feed/ | Augusta Fiberglass News | October 20, 2016;September 6, 2016;July 22, 2016;January 6, 2016;Decem
ORG-003960 | Ortec Inc | https://ortecinc.com/ | https://ortecinc.com/news/ | https://ortecinc.com/feed/ | Latest News | ORTEC | June 12, 2024;April 3, 2023;February 1, 2023
ORG-003970 | COIM USA Inc. | https://www.us.coimgroup.com | https://www.us.coimgroup.com/about/news-and-events/ | https://www.us.coimgroup.com/feed/ | COIM News &amp; Events | Latest Updates &amp; Industry Insights | August 24, 2026;October 1, 2026;June 9, 2026;May 22, 2026;July 1, 2026
ORG-003989 | General Plastics Manufacturing Company | https://generalplastics.com | https://www.generalplastics.com/news-events | https://www.generalplastics.com/feed | NEWS AND EVENTS - General Plastics | May 15, 2019;Oct 20, 2015;September 8, 2015;Oct 6, 2014;October 07, 20
ORG-004040 | Vybond Group, Inc. | https://vybond.com/ | https://vybond.com/news/ |  | Vybond News | Latest Product Launches and Company Updates | Feb 3, 2026;Feb 2, 2026
ORG-004071 | Manner Polymers, Inc. | https://mannerpolymers.com/ | https://mannerpolymers.com/manner-polymers-news/ | https://mannerpolymers.com/feed/ | News - Manner Polymers | October 6, 2025;July 18, 2025;November 12, 2024;July 17, 2024;June 5, 
ORG-004080 | Rahco Rubber, Inc. | https://rahco-rubber.com/about-us/news/ | https://rahco-rubber.com/about-us/news/ |  | News - Rahco Rubber | October 12, 2026;August 5, 2026
ORG-004106 | Iracore International Inc | https://iracore.com/ | https://iracore.com/about-us/news/ | https://iracore.com/feed/ | News - Iracore | Oct 10, 2026;Aug 8, 2021;Jul 7, 2021
ORG-004123 | Sterling Specialty Chemicals LLC | https://www.sterlingspec.com/ | https://www.sterlingspec.com/news/ | https://www.sterlingspec.com/feed/ | News &#8211; Sterling Specialty Chemicals, LLC | May 4, 2026;April 10, 2026;March 17, 2026;February 17, 2026;December 2
ORG-004135 | Bemis Manufacturing Co | https://www.bemismfg.com/ | https://www.bemismfg.com/blog | https://www.bemismfg.com/blog-feed.xml | NEWS | Bemis Mfg | Oct 23, 2024;Jul 30, 2024
ORG-004137 | R3 Composites Corp | http://www.r3composites.com/ | https://www.r3composites.com/r3c/news-events |  | News &#038; Events &#8211; Compression Molding SMC Manufacturing | R3 Composites Inc | Feb 11, 2021
ORG-004147 | GS Polymers Inc. | https://www.gspolymers.com/ | https://www.gspolymers.com/news/ | https://www.gspolymers.com/feed/ | News Archives &#187; GS Polymers | June 4, 2025;March 20, 2023
ORG-004185 | Anderson Development Company | https://andersondevelopment.com/ | https://www.andersondevelopment.com/news_events/ | https://www.andersondevelopment.com/feed/ | Anderson Development | News &amp; Events | Specialty Chemical Manufacturer | December 18, 2024;December 18, 2021;December 14, 2021;August 5, 2021;J
ORG-004215 | Shaw Industries Group, Inc. | https://shawinc.com/ | https://shawinc.com/Newsroom |  |  Shaw Industries Group, Inc. | Newsroom  | August 21, 2026;July 7, 2026;June 2, 2026;April 30, 2026;April 28, 202
ORG-004219 | SNF Holding Company | https://snf.com | https://www.snf.com/news/ | https://www.snf.com/feed/ |  News - SNF | July 27, 2026;March 31, 2026;March 17, 2026;January 2, 2026;October 31
ORG-004256 | HK Research Corporation | https://www.hkresearch.com/ | https://hkresearch.com/category/news/ | https://hkresearch.com/feed/ | News &#8211; HK Research | America&#039;s Leading Gel Coat Company | September 18, 2026;June 3, 2026;March 20, 2026;April 4, 2026;January 1
ORG-004258 | Barrette Outdoor Living, Inc. | https://www.barretteoutdoorliving.com/ | https://www.barretteoutdoorliving.com/newsroom | https://www.barretteoutdoorliving.com/feed | Newsroom - Barrette Outdoor Living | February 20, 2024;December 18, 2023;October 17, 2023;October 10, 2023;
ORG-004272 | Flex-N-Gate Corporation | https://www.flex-n-gate.com/ | https://flex-n-gate.com/news/ | https://flex-n-gate.com/feed/ | News - Flex N Gate | 16 October 2026;22 July 2026;14 April 2026;17 March 2026;26 January 20
ORG-004273 | Future Pipe Industries | https://futurepipe.com/ | https://futurepipe.com/news-events/ |  | News &amp; Events - Future Pipe Industries | 24 September 2026;10 September 2026;10 August 2026;22 May 2026;12 May 
ORG-004278 | Magnera Corporation | https://www.magnera.com/ | https://magnera.com/news/ | https://magnera.com/feed/ | Magnera News and Press Releases | Corporate Announcements | October 13, 2026;October 22, 2026;October 5, 2026;September 2, 2026;Au
ORG-004287 | Thorpe Plant Services, Inc. | https://thorpeplantmaintenanceandengineering.com/ | https://thorpeplantmaintenanceandengineering.com/category/news/ | https://thorpeplantmaintenanceandengineering.com/feed/ | News Archives - Thorpe Specialty Services | September 13, 2022;January 18, 2022;June 13, 2016
ORG-004289 | Trex Company, Inc. | https://www.trex.com/ | https://www.trex.com/our-company/news/ |  | News | Trex | February 16, 2026;February 13, 2026;January 31, 2026;January 23, 2026;
ORG-004291 | Viskase Companies, Inc. | https://www.viskase.com/ | https://www.viskase.com/news-events/ | https://www.viskase.com/feed/ | News &#038; Events &#8211; Viskase | May 31, 2022;February 8, 2022;January 4, 2022;October 6, 2021;April 16
ORG-004309 | FLEXcon Company, Inc. | https://www.flexcon.com/ | https://www.flexcon.com/press-releases |  | Flexcon | Press Releases | 08/24/2026;04/22/2026;03/24/2026;03/09/2026;02/03/2026;02/02/2026;01/0
ORG-004316 | Stryten Energy LLC | https://www.stryten.com/ | https://www.stryten.com/blog/ | https://www.stryten.com/feed/ | News From Stryten Energy | November 3, 2026;October 21, 2026;October 19, 2026;October 1, 2026;Sep
ORG-004317 | Strongwell Corporation | https://www.strongwell.com/ | https://www.strongwell.com/news/ | https://www.strongwell.com/feed/ | News Archive - Strongwell | Sep 9, 2026;Aug 26, 2026;Aug 25, 2026;Aug 11, 2026;Aug 5, 2026;Jul 9, 
ORG-004324 | Toray Performance Materials Corporation | https://www.toraypmc.com/ | https://www.toraypmc.com/news |  | Latest news and updates - Toray Performance Materials Corporation | 26 August 2026;12 August 2026;1 June 2026;1 April 2026;29 August 2025;
ORG-004328 | Techmer PM LLC | https://www.techmerpm.com/ | https://www.techmerpm.com/press-releases/ | https://www.techmerpm.com/feed/ | Press Releases - Techmer PM | May 12, 2023;June 3, 2023;April 29, 2023;June 15, 2026;Mar. 12, 2026;O
ORG-004386 | Dicar Inc | https://www.dicar.com/ | https://dicar.com/news/ | https://dicar.com/feed/ | News | Dicar | May 31, 2022;Mar 23, 2020;March 22, 2020;Mar 20, 2020;Feb 22, 2019;Sep
ORG-004418 | Duraco Specialty Tapes LLC | https://www.duraco.com/ | https://duraco.com/blog/tag/news |  | news - Posts - Duraco | November 18, 2024;May 22, 2023;December 8, 2021;December 2, 2021
ORG-004449 | Microporous LLC | https://www.microporous.net/ | https://microporous.net/newsroom/ | https://microporous.net/feed/ | Newsroom - Microporous | Apr 30, 2026;March 6, 2026
ORG-004452 | Miller Ingenuity | https://www.milleringenuity.com/ | https://www.milleringenuity.com/news/ | https://www.milleringenuity.com/feed/ |  News | Miller Ingenuity | Oct 28, 2026;Oct 07, 2026;Oct 05, 2026;Sep 23, 2026;Aug 25, 2026;Jul 2
ORG-004500 | Special-Lite, Inc. | https://special-lite.com/ | https://special-lite.com/news/ | https://special-lite.com/feed/ | News Posts Archive - Special-Lite | March 25, 2026;Oct. 15, 2025
ORG-004523 | Wabash National Corporation | https://onewabash.com/ | https://news.onewabash.com/ | https://news.onewabash.com/feed/ | Newsroom One Wabash | 24 September 2026;22 July 2026;01 July 2026;June 15, 2026;May 26, 2026
ORG-004533 | Bomar Specialties, LLC | https://www.bomar-chem.com/ | https://bomar-chem.com/resources/news-and-media |  | News &amp; Media | Bomar Oligomers | January 31, 2023;May 4, 2022;January 31, 2022;June 8, 2021;April 5, 20
ORG-004539 | Epic Resins | https://epicresins.com/ | https://www.epicresins.com/News |  | Epoxy Formulator Capitol Equipment Investments | Product Development News | Epic Resins | February 9, 2026;February 3, 2026;January 21, 2026;August 19, 2025;Sep
ORG-004540 | Estron Chemical, Inc. | https://www.estron.com/ | https://estron.com/news/ |  | News - Estron Chemical | October 14, 2026;October 3, 2026;April 24, 2026;November 12, 2024;Sept
ORG-004556 | Oregon Rubber Mills Co | https://www.oregonrubbermills.com/ | https://www.oregonrubbermills.com/Contact/News |  |  News | Oregon Rubber Mills in Corvallis, OR, [FOCUS AREA 2] and [FOCUS AREA 3]  | 6/3/2016
ORG-004575 | Synray Corporation | https://synray.com | https://synray.com/news/ | https://synray.com/comments/feed/ | NEWS &#8211; Synray Corporation &#8211; Manufacturers of Alkyd Resins, Polyesters and Chemical Specialties | April 30, 2026;March 31, 2025
ORG-004585 | Rodda Paint Company | https://www.roddapaint.com | https://www.roddapaint.com/about-us/newsroom/ | https://www.roddapaint.com/feed/ | Newsroom - Rodda-Miller Paint | October 20, 2026;March 18, 2025;December 3, 2024;June 15, 2020;July 31
ORG-004592 | Hydrite Chemical Co. | https://www.hydrite.com | https://www.hydrite.com/News-Events/Press-Releases.htm |  | Press Releases | Hydrite Chemical Co. | September 3, 2025;April 26, 2024;December 1, 2021;December 15, 2020
ORG-004605 | Proviron Inc. | https://proviron.com/america | https://proviron.com/america/america-news/ | https://proviron.com/feed/ | Proviron Inc - news, blog and resources | October 13, 2026;September 8, 2026;July 14, 2026;July 8, 2026;June 25,
ORG-004620 | Mississippi Polymers, Inc. | https://www.mississippipolymers.com/ | https://www.mississippipolymers.com/calendered-film-manufacturer-news/ | https://www.mississippipolymers.com/feed/ | Mississippi Polymers, Inc.—News | 06/01/2017;12/05/2016;11/22/2016;11/01/2016

Checks have actually passed: validate.py 0 errors; re-fetch 118 pages +59 feeds all HTTP200 and nonempty feed and item overlap; idempotence second build 0 writes; diff all177 cells only specified fields. Coverage 1043 distinct inputs=1043 discovery=1043 verdicts; 925 holds. Attempted 1043 source websites; 344 candidates inspected; accepted conservative title/date matching plus listed manual exclusions. A hold never asserts no newsroom or closure. Challenge hidden false positives and code/check defects, not just counts.

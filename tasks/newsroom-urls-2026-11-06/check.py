"""Re-fetch all accepted URLs; fail on unreadable pages, redirects off-domain or empty feeds."""
import concurrent.futures, csv, json
from urllib.parse import urljoin, urlsplit
from xml.etree import ElementTree as ET
from discover import HERE, ROOT, Links, domain, fetch, feed_count

def url_key(url):
    parts=urlsplit(url)
    return parts._replace(path=parts.path.rstrip('/'))

def check(r):
    out={'org_id':r['org_id'],'checks':[]}; page_links=set()
    for col in ('newsroom_url','newsroom_feed_url'):
        if not r[col]: continue
        p=fetch(r[col]); assert p['status']=='200',(r['org_id'],col,p['status'])
        assert domain(p['final'])==domain(r['website']),(r['org_id'],p['final'])
        assert url_key(p['final'])==url_key(r[col]),(r['org_id'],'stored URL redirected to another path',p['final'])
        result={k:p[k] for k in ('url','final','status')}
        if col=='newsroom_url':
            page_links={url_key(urljoin(p['final'],u.strip())) for u,l in Links(p['body']).links}
        if col=='newsroom_feed_url':
            result['items']=feed_count(p['body']); assert result['items']>0
            root=ET.fromstring(p['body']); links=set()
            titles=root.findall('./channel/title')+root.findall('{http://www.w3.org/2005/Atom}title')
            assert '/comments/' not in p['final'].lower() and 'feed=comments' not in p['final'].lower()
            assert not any('comments' in (e.text or '').lower() for e in titles),'comments feed'
            entries=[e for e in root.iter() if e.tag in ('item','{http://www.w3.org/2005/Atom}entry','{http://purl.org/rss/1.0/}item')]
            for entry in entries:
                links.update(url_key(e.text.strip()) for e in entry.iter('link') if e.text)
                links.update(url_key(e.attrib.get('href','')) for e in entry.iter('{http://www.w3.org/2005/Atom}link') if e.attrib.get('rel','alternate')=='alternate')
            assert page_links & links,(r['org_id'],'feed items not linked from newsroom')
            result['linked_items']=len(page_links & links)
        out['checks'].append(result)
    return out

if __name__=='__main__':
    rows=[r for r in csv.DictReader(open(HERE/'verdicts.csv')) if r['verdict']=='VERIFIED']
    assert rows and len({r['org_id'] for r in rows})==len(rows)
    actual={r['org_id']:r for path in (ROOT/'data').glob('organizations_*.csv') if path.name!='organizations_all.csv' for r in csv.DictReader(open(path))}
    for r in rows:
        a=actual[r['org_id']]; assert a['status']=='active' and a['tier1_qualifier']
        assert all(a[col]==r[col] for col in ('newsroom_url','newsroom_feed_url')),(r['org_id'],'builder not applied')
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool: result=list(pool.map(check,rows))
    (HERE/'refetch.json').write_text(json.dumps(result,indent=2)+'\n')
    print(f'PASS: {len(rows)} active organizations; {sum(len(r["checks"]) for r in result)} URLs, all HTTP 200 and feeds nonempty')

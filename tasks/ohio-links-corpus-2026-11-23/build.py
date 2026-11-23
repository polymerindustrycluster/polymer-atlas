"""Corpus-only navigation fills. No network requests and no evidence rows (schema v1.11)."""
import csv, hashlib, importlib.util, io, json, re, sys, subprocess, random, tempfile, os
from html import escape
from collections import defaultdict
from pathlib import Path
from urllib.parse import urljoin, urlsplit
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
CORPUS=Path('/Users/johnswanson/.bb/thread-storage/thr_9i2c6byhcz/2026-11-06-atlas/persist/ohio-corpus-2026-11-23')
def module(name,path):
    spec=importlib.util.spec_from_file_location(name,path); m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
li=module('li_discover',ROOT/'tasks/linkedin-navigation-2026-11-06/discover.py')
news=module('news_discover',ROOT/'tasks/newsroom-urls-pic18-2026-11-06/discover.py')
sys.path.insert(0,str(ROOT/'scripts'))
from atlas import name_key
COLS=('linkedin_url','newsroom_url','newsroom_feed_url')
BASE='87ba88471ff395d144b4f88605f1b2d81114dbcd'
REPAIR='ORG-001053'
OLD_FEED='https://www.provia.com/feed/'
ARTICLE_FEED='https://www.provia.com/feed/?post_type=article'
FIELDS=['org_id','legal_name','trade_names','website','status','verification_tier',*COLS]
PUBLIC_FIELDS=[k for k in FIELDS if k not in ('legal_name','trade_names')]
PARENT_HOLDS=HERE/'parent_site_holds.csv'
PARENT_SITE=re.compile(r"\b(?:website is the parent['’]s|parent(?: company)?(?:['’]s)? "
                       r"(?:own )?(?:site|homepage|global-network page))\b",re.I)

def snapshot(path, ref=BASE):
    raw=subprocess.check_output(['git','show',ref+':'+str(path)],cwd=ROOT)
    return list(csv.DictReader(io.StringIO(raw.decode(),newline='')))

def shards(prefix, ref=BASE):
    paths=subprocess.check_output(['git','ls-tree','--name-only',ref+':data'],cwd=ROOT,text=True)
    return [Path('data')/n for n in paths.splitlines() if n.startswith(prefix+'_')
            and n.endswith('.csv') and not n.endswith('_all.csv')]

def frame():
    excluded=snapshot('tasks/pic18-links-corpus-2026-11-16/inputs.csv')
    seen={r['org_id'] for r in excluded}
    assert len(seen)==len(excluded)
    ohio={r['org_id'] for p in shards('sites') for r in snapshot(p)
          if r['state']=='OH' and r['operating_status']=='active'}
    orgs=[(p.name,r) for p in shards('organizations') for r in snapshot(p)]
    assert len(orgs)==len({r['org_id'] for _,r in orgs})
    frame=[(p,r) for p,r in orgs if r['org_id'] not in seen and r['status']=='active'
           and r['website'].strip().lower().startswith(('http://','https://'))
           and (p=='organizations_OH.csv' or r['org_id'] in ohio)]
    rows=sorted(({k:r[k] for k in [*FIELDS,'notes']} for _,r in frame),key=lambda r:r['org_id'])
    assert (len(rows),sum(p=='organizations_OH.csv' for p,_ in frame),
            *(sum(not r[c] for r in rows) for c in COLS))==(748,717,717,701,728)
    return rows
def read(path):
    with path.open(newline='') as f:return list(csv.DictReader(f))
def write(path,rows):
    mode=path.stat().st_mode & 0o777 if path.exists() else 0o644
    with tempfile.NamedTemporaryFile(mode='w',newline='',dir=path.parent,delete=False) as f:
        tmp=Path(f.name)
        try:
            w=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n')
            w.writeheader();w.writerows(rows);f.flush()
            tmp.chmod(mode);os.replace(tmp,path)
        finally:
            tmp.unlink(missing_ok=True)
def tables():
    return {p:read(p) for p in sorted((ROOT/'data').glob('organizations_*.csv')) if p.name!='organizations_all.csv'}
def identity(row,value):
    key=name_key(urlsplit(value).path.split('/')[2].replace('-',' ')).replace(' ','')
    return len(key)>=3 and any(name_key(n).replace(' ','')==key for n in [row['legal_name'],*row['trade_names'].split(';')] if n.strip())
def key(url):
    p=urlsplit(url);return p._replace(fragment='',path=p.path.rstrip('/')).geturl()
def index_url(url):
    p=urlsplit(url)
    slug=p.path.rstrip('/').split('/')[-1].lower()
    slug=re.sub(r'\.(html?|php|aspx)$','',slug)
    allowed={'news','newsroom','news-room','news-events','news-and-events','newsevents','newsandevents','news-press','news-and-press','newspress','news-center','news-centre','news-articles','news-updates','news-insights','news-and-insights','company-news','corporate-news','latest-news','press','press-room','pressroom','press-releases','press-release','news-releases','media','media-center','media-room','blog','blogs','news-blog','newsfeed','newsletter','newsletter-archive','newsletter-main','press-releases-and-news','blog-articles'}
    return slug in allowed or (not slug and (p.hostname or '').startswith('blog.'))
class Navigation(news.Links):
    def __init__(self,body):
        self.stack=[]; self.navlinks=[];super().__init__(body)
    def handle_starttag(self,tag,attrs):
        if tag not in li.VOID:self.stack.append(tag)
        super().handle_starttag(tag,attrs)
    def handle_endtag(self,tag):
        if tag=='a' and self.href and any(t in self.stack for t in ('nav','header','footer')) and not any(t in self.stack for t in ('article','main')):
            self.navlinks.append((self.href,' '.join(' '.join(self.label).split())))
        super().handle_endtag(tag)
        if tag in self.stack:del self.stack[len(self.stack)-1-self.stack[::-1].index(tag):]
def digest(raw):
    return hashlib.sha256(raw).hexdigest()

def own_url(url, owner):
    return li.own_url(url,owner)

def label_ok(label):
    return bool(news.LABEL.fullmatch(label) or label.lower() in ('blog','our blog'))

def article_token(url,owner):
    if not own_url(url,owner):return ''
    p=urlsplit(url)
    if p.path.rstrip('/') in ('','/index.html'):return ''
    return 'https://witness.invalid/'+digest(str(overlap.url_key(url)).encode())

# The prior overlap gate lives in check.py. Import its helpers without invoking its fetcher.
sys.path.insert(0,str(ROOT/'tasks/newsroom-urls-other-2026-11-06'))
try:
    overlap=module('previous_news_check',ROOT/'tasks/newsroom-urls-other-2026-11-06/check.py')
finally:
    sys.path.pop(0)

def page_witness(body,base,owner):
    parsed=news.Links(body)
    nav=Navigation(body)
    header={a['href'] for a in li.Links(body).links}
    parts=['<html>']
    for href,label in parsed.links:
        href=href.strip()
        company=li.canonical(href)
        if company:
            tag='header' if href in header else 'main'
            parts.append(f'<{tag}><a href="{escape(company)}"></a></{tag}>')
        try:
            u=urljoin(base,href)
            if own_url(u,owner) and index_url(u) and label_ok(label):
                tag='nav' if (href,label) in nav.navlinks else 'main'
                parts.append(f'<{tag}><a href="{escape(u)}">News</a></{tag}>')
            token=article_token(u,owner)
            if token:parts.append(f'<a href="{token}"></a>')
        except ValueError:
            continue
    for href in parsed.feeds:
        u=urljoin(base,href)
        if own_url(u,owner) and 'comments' not in u.lower():
            parts.append(f'<link rel="alternate" type="application/rss+xml" href="{escape(u)}">')
    return ('\n'.join(parts+['</html>'])).encode()

def feed_witness(body,final,owner):
    import xml.etree.ElementTree as et
    try:
        if b'<!DOCTYPE' in body.upper() or not overlap.feed_count(body):return b''
        root=et.fromstring(body)
    except (et.ParseError,AssertionError):
        return b''
    titles=root.findall('./channel/title')+root.findall('{http://www.w3.org/2005/Atom}title')
    if any('comments' in (e.text or '').lower() for e in titles):return b''
    entries=[e for e in root.iter() if e.tag in ('item','{http://www.w3.org/2005/Atom}entry','{http://purl.org/rss/1.0/}item')]
    links=set()
    for entry in entries:
        links.update(e.text.strip() for e in entry.iter('link') if e.text)
        links.update(e.attrib.get('href','') for e in entry.iter('{http://www.w3.org/2005/Atom}link')
                     if e.attrib.get('rel','alternate')=='alternate')
        links.update(e.text.strip() for e in entry.iter('{http://purl.org/rss/1.0/}link') if e.text)
    tokens=sorted({article_token(urljoin(final,u),owner) for u in links if u}-{''})
    return ('<rss><channel>'+''.join(f'<item><link>{token}</link></item>' for token in tokens)
            +'</channel></rss>').encode()

def feed_overlaps(page,feed):
    from unittest.mock import patch
    row={'org_id':page[0]['org_id'],'website':page[0]['final_url'],
         'newsroom_url':page[0]['final_url'],'newsroom_feed_url':feed[0]['final_url']}
    responses=[dict(status='200',url=p['final_url'],final=p['final_url'],body=body)
               for p,body in (page,feed)]
    with patch.object(overlap,'fetch',side_effect=responses):
        try:return overlap.check(row)['checks'][1]['linked_items']>0
        except AssertionError:return False

def loaded_pages(row,pages):
    owner=li.domain(row['website'])
    loaded=[]
    for p in pages:
        if p['status']!='ok' or not own_url(p['final_url'],owner) or not own_url(p['url'],owner):continue
        raw=(CORPUS/p['raw_file']).read_bytes()
        assert len(raw)==int(p['witness_bytes']) and digest(raw)==p['witness_sha256'],'pinned witness mismatch'
        loaded.append((p,raw.decode()))
    return loaded

def newsroom_values(row,loaded):
    own=row['website'];owner=li.domain(own);values={}
    retained={key(p['url']):p for p,body in loaded if p['page_kind']=='news' and index_url(p['final_url'])}
    for p in retained.values():
        u=p['final_url'];values[key(u)]=(p,u)
    for p,body in loaded:
        if p['page_kind']=='home':
            for href,label in Navigation(body).navlinks:
                u=urljoin(p['final_url'],href).split('#')[0]
                if label_ok(label) and index_url(u) and own_url(u,owner) and key(u)!=key(own):
                    if key(u) in retained:continue
                    values.setdefault(key(u),(p,href))
    return values

def newsroom_page(row,loaded):
    values=newsroom_values(row,loaded)
    target=row['newsroom_url'] or (next(iter(values)) if len(values)==1 else '')
    return next(((p,b) for p,b in loaded if target and key(p['final_url'])==key(target)
                 and p['page_kind'] not in ('feed','repair_feed','repair_old_feed')),None)

def feed_candidates(row,pages):
    loaded=loaded_pages(row,pages)
    room=newsroom_page(row,loaded)
    if not room:return None,{}
    p,body=room;owner=li.domain(row['website'])
    feeds={urljoin(p['final_url'],href):href for href in news.Links(body).feeds
           if own_url(urljoin(p['final_url'],href),owner) and 'comments' not in href.lower()}
    return room,feeds

def site_identity_hold(row,owners):
    if PARENT_SITE.search(row.get('notes','')):
        return 'Need an exact-entity navigation witness; the Atlas record cites a parent site.'
    if owners.get(li.domain(row['website']))!={row['org_id']}:
        return 'Need exact entity bridge; multiple held entities share website domain.'
    return ''

def candidates(row,pages,owners,review_hold=''):
    loaded=loaded_pages(row,pages)
    identity_hold=review_hold or site_identity_hold(row,owners)
    result=[]
    for col in COLS:
        if row[col]:continue
        values={};reason=('Need a header/footer company anchor with an exact held-name slug.' if col=='linkedin_url'
                          else 'Need a link to a recognized own-domain newsroom index.')
        if not loaded:reason='Need a reachable own-domain page that can be retained under the privacy rule.'
        elif row['status']!='active':reason='Need active exact-entity website verification.'
        elif identity_hold:reason=identity_hold
        elif col=='linkedin_url':
            # All company anchors detect ambiguity; only proven header/footer anchors can fill.
            allvalues={li.canonical(h) for p,b in loaded for h,l in news.Links(b).links if li.canonical(h)}
            if len(allvalues)>1:reason='Need one company slug; stored pages link multiple company slugs.'
            else:
                for p,b in loaded:
                    for a in li.Links(b).links:
                        if identity(row,a['linkedin_url']):values[a['linkedin_url']]=(p,a['href'])
                if allvalues and not values:reason='Need header/footer company slug matching held name or trade name.'
        elif col=='newsroom_url':
            values=newsroom_values(row,loaded)
            refused={key(p['url']) for p in pages if p['page_kind']=='news' and p['status']!='ok'}
            if values and any(u in refused for u in values):
                values={}
                reason='Need a reachable, privacy-eligible newsroom index on the held domain.'
        else:
            room,feeds=feed_candidates(row,pages)
            if not room:reason='Need a retained copy of the chosen newsroom.'
            elif not feeds:reason='Need a feed URL advertised by the chosen newsroom.'
            elif len(feeds)>1:reason='Need one unambiguous feed advertised by the chosen newsroom.'
            else:
                target,href=next(iter(feeds.items()))
                feed=next(((p,b) for p,b in loaded if p['page_kind']=='feed' and p['url']==target),None)
                if not feed:reason='Need a successful fetch of the advertised feed.'
                elif not feed_overlaps(room,feed):reason='Need a feed item link also linked by the chosen newsroom.'
                else:values[feed[0]['final_url']]=(room[0],href)
        if len(values)==1:
            value,(p,href)=next(iter(values.items()));reason='Unique deterministic own-site navigation witness.'
        else:
            value='';p={};href=''
            if len(values)>1:reason=('Need one unambiguous newsroom index among the retained candidates.'
                                      if col=='newsroom_url' else 'Need one unambiguous navigation URL.')
        result.append(dict(org_id=row['org_id'],column=col,value=value,applied='yes' if value else 'held',settling_fact=reason,source_url=p.get('final_url',''),raw_file=p.get('raw_file',''),sha256=p.get('witness_sha256',''),href=href))
    return result

def proposals(inputs,manifest):
    groups=defaultdict(list)
    for p in manifest:groups[p['org_id']].append(p)
    owners=defaultdict(set)
    for rows in [*tables().values(),read(ROOT/'data/ecosystem.csv')]:
        for r in rows:
            if r.get('website'):owners[li.domain(r['website'] if '://' in r['website'] else 'https://'+r['website'])].add(r['org_id'])
    reviewed=read(PARENT_HOLDS)
    holds={(r['org_id'],r['website']):r['settling_fact'] for r in reviewed}
    assert len(holds)==len(reviewed) and all(holds.values())
    assert holds.keys()<={(r['org_id'],r['website']) for r in inputs},'stale parent-site hold'
    return [v for r in inputs for v in candidates(r,groups[r['org_id']],owners,
                                                  holds.get((r['org_id'],r['website']),''))]

def repair_row(manifest):
    row=next(r for r in snapshot('data/organizations_OH.csv') if r['org_id']==REPAIR)
    assert row['newsroom_feed_url']==OLD_FEED
    loaded=loaded_pages(row,[p for p in manifest if p['org_id']==REPAIR])
    room=newsroom_page(row,loaded)
    feeds={p['page_kind']:(p,b) for p,b in loaded if p['page_kind'].startswith('repair_')}
    value=''
    if not room:reason='Need a retained ProVia newsroom page.'
    elif 'repair_feed' not in feeds:reason='Need a successful robots-permitted fetch of the ProVia article feed.'
    elif not feed_overlaps(room,feeds['repair_feed']):reason='Need a ProVia article feed item linked on its newsroom.'
    elif 'repair_old_feed' not in feeds:reason='Need a robots-permitted check of the recorded ProVia feed.'
    elif feed_overlaps(room,feeds['repair_old_feed']):reason='Need evidence the recorded ProVia feed lacks an overlapping item.'
    else:
        value=feeds['repair_feed'][0]['final_url']
        reason='The article feed overlaps the newsroom and the recorded feed has no overlap.'
    p=room[0] if room else {}
    return dict(org_id=REPAIR,column='newsroom_feed_url',value=value,applied='yes' if value else 'held',
                settling_fact=reason,source_url=p.get('final_url',''),raw_file=p.get('raw_file',''),
                sha256=p.get('witness_sha256',''),href=ARTICLE_FEED)

def apply(packet):
    ts=tables();actual={r['org_id']:r for rows in ts.values() for r in rows}
    assert len(actual)==sum(map(len,ts.values()))
    assert len({(r['org_id'],r['column']) for r in packet})==len(packet)
    changed=set();cells=0
    for v in packet:
        assert v['column'] in COLS
        if v['applied']!='yes':continue
        r=actual[v['org_id']]
        assert r['status']=='active' and v['value']
        assert own_url(v['source_url'],li.domain(r['website'])),'source no longer on held domain'
        before=OLD_FEED if r['org_id']==REPAIR and v['column']=='newsroom_feed_url' else ''
        assert r[v['column']] in (before,v['value']), 'nonblank conflict'
        if r[v['column']]==before:
            r[v['column']]=v['value'];changed.add(v['org_id']);cells+=1
    for p,rows in ts.items():
        if any(r['org_id'] in changed for r in rows):
            backup=CORPUS/'backups'/p.name;backup.parent.mkdir(exist_ok=True)
            if not backup.exists():backup.write_bytes(p.read_bytes())
            write(p,rows)
    return cells

def sample(packet,repair):
    cells=[r for r in [*packet,repair] if r['applied']=='yes']
    assert len(cells)>=30,'fewer than 30 applied cells'
    groups={col:[r for r in cells if r['column']==col] for col in COLS}
    quotas={col:30*len(rows)/len(cells) for col,rows in groups.items()}
    counts={col:int(quota) for col,quota in quotas.items()}
    for col in sorted(COLS,key=lambda c:quotas[c]-counts[c],reverse=True)[:30-sum(counts.values())]:
        counts[col]+=1
    rng=random.Random(20261123)
    return [r for col in COLS for r in rng.sample(groups[col],counts[col])]

def freeze():
    rows=frame()
    write(HERE/'inputs.csv',[{k:r[k] for k in PUBLIC_FIELDS} for r in rows])
    (HERE/'base.txt').write_text(BASE+'\n')
    manifest=read(CORPUS/'manifest.csv')
    write(HERE/'manifest.csv',manifest)
    packet=proposals(rows,manifest);repair=repair_row(manifest)
    write(HERE/'proposals.csv',packet)
    write(HERE/'repair.csv',[repair])
    write(HERE/'sample.csv',sample(packet,repair))

if __name__=='__main__':
    if '--freeze' in sys.argv:freeze()
    if '--apply' in sys.argv:
        print('Navigation cells applied:',apply(read(HERE/'proposals.csv')+read(HERE/'repair.csv')))

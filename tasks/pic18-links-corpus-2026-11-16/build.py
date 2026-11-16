"""Corpus-only navigation fills. No network requests and no evidence rows (schema v1.11)."""
import csv, hashlib, importlib.util, io, json, re, sys
from collections import defaultdict
from pathlib import Path
from urllib.parse import urljoin, urlsplit
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
CORPUS=Path('/Users/johnswanson/.bb/thread-storage/thr_9i2c6byhcz/2026-11-06-atlas/persist/pic18-corpus-2026-11-16')
def module(name,path):
    spec=importlib.util.spec_from_file_location(name,path); m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
li=module('li_discover',ROOT/'tasks/linkedin-navigation-2026-11-06/discover.py')
news=module('news_discover',ROOT/'tasks/newsroom-urls-pic18-2026-11-06/discover.py')
sys.path.insert(0,str(ROOT/'scripts'))
from atlas import name_key
from regions import PIC18
COLS=('linkedin_url','newsroom_url','newsroom_feed_url')
def read(path):
    with path.open(newline='') as f:return list(csv.DictReader(f))
def write(path,rows):
    with path.open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n');w.writeheader();w.writerows(rows)
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
def candidates(row,pages,owners):
    own=row['website'] if '://' in row['website'] else 'https://'+row['website']
    loaded=[]
    for p in pages:
        if p['status']!='ok' or not p['raw_file'] or not li.own_url(p['final_url'],li.domain(own)) or not li.own_url(p['url'],li.domain(own)):continue
        raw=(CORPUS/p['raw_file']).read_bytes();assert hashlib.sha256(raw).hexdigest()==p['sha256'],'corpus hash mismatch'
        loaded.append((p,raw.decode(errors='replace')))
    result=[]
    for col in COLS:
        if row[col]:continue
        values={};reason='Need a stored own-domain navigation witness for this field.'
        if row['status']!='active':reason='Need active exact-entity website verification.'
        elif col=='linkedin_url':
            # All company anchors detect ambiguity; only proven header/footer anchors can fill.
            allvalues={li.canonical(h) for p,b in loaded for h,l in news.Links(b).links if li.canonical(h)}
            if len(allvalues)>1:reason='Need one company slug; stored pages link multiple company slugs.'
            elif owners.get(li.domain(own))!={row['org_id']}:reason='Need exact entity bridge; multiple held entities share website domain.'
            else:
                for p,b in loaded:
                    for a in li.Links(b).links:
                        if identity(row,a['linkedin_url']):values[a['linkedin_url']]=(p,a['href'])
                if allvalues and not values:reason='Need header/footer company slug matching held name or trade name.'
        elif col=='newsroom_url':
            for p,b in loaded:
                u=p['final_url']; path=urlsplit(u).path
                if p['page_kind']=='news' and index_url(u):values[key(u)]=(p,u)
                if p['page_kind']=='home':
                    for h,label in Navigation(b).navlinks:
                        u=urljoin(p['final_url'],h).split('#')[0]
                        if (news.LABEL.fullmatch(label) or label.lower() in ('blog','our blog')) and index_url(u) and li.own_url(u,li.domain(own)) and key(u)!=key(own):values[key(u)]=(p,h)
        else:
            target=row['newsroom_url'] or next((r['value'] for r in result if r['column']=='newsroom_url' and r['applied']=='yes'),'')
            for p,b in loaded:
                if target and key(p['final_url'])==key(target):
                    for h in news.Links(b).feeds:
                        u=urljoin(p['final_url'],h)
                        if li.own_url(u,li.domain(own)) and 'comments' not in u.lower():values[u]=(p,h)
        if len(values)==1:
            value,(p,href)=next(iter(values.items()));reason='Unique deterministic own-site navigation witness.'
        else:
            value='';p={};href=''
            if len(values)>1:reason='Need one unambiguous index/feed URL; multiple candidates in corpus.'
        result.append(dict(org_id=row['org_id'],column=col,value=value,applied='yes' if value else 'held',settling_fact=reason,source_url=p.get('final_url',''),raw_file=p.get('raw_file',''),sha256=p.get('sha256',''),href=href))
    return result

def proposals(inputs,manifest):
    groups=defaultdict(list)
    for p in manifest:groups[p['org_id']].append(p)
    owners=defaultdict(set)
    for rows in [*tables().values(),read(ROOT/'data/ecosystem.csv')]:
        for r in rows:
            if r.get('website'):owners[li.domain(r['website'] if '://' in r['website'] else 'https://'+r['website'])].add(r['org_id'])
    return [v for r in inputs for v in candidates(r,groups[r['org_id']],owners)]
def apply(packet):
    ts=tables();actual={r['org_id']:r for rows in ts.values() for r in rows};changed=set();cells=0
    assert len({(r['org_id'],r['column']) for r in packet})==len(packet)
    for v in packet:
        assert v['column'] in COLS
        if v['applied']!='yes':continue
        r=actual[v['org_id']];assert r[v['column']] in ('',v['value']), 'nonblank conflict'
        if not r[v['column']]:r[v['column']]=v['value'];changed.add(v['org_id']);cells+=1
    for p,rows in ts.items():
        if any(r['org_id'] in changed for r in rows):
            backup=CORPUS.parent/'pic18-links-corpus-backups'/p.name;backup.parent.mkdir(exist_ok=True)
            if not backup.exists():backup.write_bytes(p.read_bytes())
            write(p,rows)
    return cells
if __name__=='__main__':
    if '--freeze' in sys.argv:
        pic={r['org_id'] for p in (ROOT/'data').glob('sites_*.csv') if p.name!='sites_all.csv' for r in read(p) if r['state']=='OH' and r['county'].removesuffix(' County') in PIC18}
        fields=['org_id','legal_name','trade_names','website','status','verification_tier',*COLS]
        inputs=[{k:r[k] for k in fields} for rows in tables().values() for r in rows if r['org_id'] in pic and r['website']]
        write(HERE/'inputs.csv',inputs);(HERE/'base.txt').write_text(__import__('subprocess').check_output(['git','rev-parse','HEAD'],text=True))
        manifest=read(CORPUS/'manifest.csv');write(HERE/'manifest.csv',manifest)
        write(HERE/'proposals.csv',proposals(inputs,manifest))
    if '--apply' in sys.argv:print('Cells filled:',apply(read(HERE/'proposals.csv')))

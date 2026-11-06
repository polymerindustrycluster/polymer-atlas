"""Own-homepage header/footer anchors; never request LinkedIn or follow external redirects."""
import concurrent.futures
import csv
import hashlib
import json
import re
import subprocess
import tempfile
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin, urlsplit

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
CACHE = ROOT / 'build/linkedin-navigation/raw'
# Reused from the newsroom lane's discover.py and validator V58.
SLD2 = {'co','com','org','net','ac','gov','edu','ne','or','go','gob','nic','ltd','plc','sch','mil'}
VOID = {'area','base','br','col','embed','hr','img','input','link','meta','param','source','track','wbr'}
COMPANY = re.compile(r'/company/([A-Za-z0-9_%-]+(?:\.[A-Za-z0-9_%-]+)*)/?')


def domain(url):
    p = (urlsplit(url).hostname or '').lower().rstrip('.').split('.')
    return '.'.join(p[-3:] if len(p)>2 and p[-2] in SLD2 and len(p[-1])==2 else p[-2:])


def own_url(url, owner):
    try:
        p = urlsplit(url)
        p.port
        host = (p.hostname or '').lower().rstrip('.')
        return (p.scheme in {'https','http'} and not p.username and not p.password
                and '.' in host and domain(url) == owner
                and host != 'linkedin.com' and not host.endswith('.linkedin.com'))
    except ValueError:
        return False


def canonical(href):
    try:
        p = urlsplit('https:' + href if href.startswith('//') else href)
        host = (p.hostname or '').lower()
        if p.scheme not in {'http','https'} or p.username or p.password or p.port:
            return ''
        if host not in {'linkedin.com','www.linkedin.com'} and not re.fullmatch(r'[a-z]{2}\.linkedin\.com', host):
            return ''
        m = COMPANY.fullmatch(p.path)
        if not m or '%2e' in p.path.lower():
            return ''
        return 'https://www.linkedin.com/company/' + m[1] + '/'
    except ValueError:
        return ''


class Links(HTMLParser):
    def __init__(self, html):
        super().__init__(convert_charrefs=True)
        self.stack, self.links = [], []
        self.feed(html)

    def handle_starttag(self, tag, attrs):
        attrs = {k:(v or '') for k,v in attrs}
        marker = tag in {'header','footer'} or (tag in {'div','section','nav','aside','ul','li'} and bool(re.search(r'(?:header|footer)', attrs.get('id','') + ' ' + attrs.get('class',''), re.I)))
        location = tag + ('#' + attrs['id'] if attrs.get('id') else '') + ('.' + '.'.join(attrs['class'].split()) if attrs.get('class') else '')
        ancestors = [loc for _, selected, loc in self.stack if selected]
        if tag == 'a' and ancestors:
            href = attrs.get('href','').strip()
            value = canonical(href)
            if value:
                self.links.append({'href':href,'linkedin_url':value,'location':ancestors[-1]})
        if tag not in VOID:
            self.stack.append((tag,marker,location))

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag not in VOID:
            self.handle_endtag(tag)

    def handle_endtag(self, tag):
        for i in range(len(self.stack)-1,-1,-1):
            if self.stack[i][0] == tag:
                del self.stack[i:]
                break


def fetch(url):
    """curl with automatic redirects disabled; validate every next URL before its request."""
    if '://' not in url:
        url = 'https://' + url
    owner = domain(url)
    attempts = []
    CACHE.mkdir(parents=True, exist_ok=True)
    for _ in range(6):
        if not own_url(url, owner):
            return {'url':url,'status':'blocked_external_or_unsafe','attempts':attempts,'body':''}
        digest = hashlib.sha256(url.encode()).hexdigest()
        path = CACHE / (digest + '.html')
        with tempfile.TemporaryDirectory() as tmp:
            header = Path(tmp) / 'headers'
            result = subprocess.run(['curl','--proto','=http,https','--max-time','25','--connect-timeout','8','-sS','-A','Mozilla/5.0','-D',str(header),'-o',str(path),'-w','%{http_code}',url],capture_output=True,text=True)
            status = result.stdout.strip()
            attempts.append({'url':url,'status':status,'curl_exit':result.returncode})
            if result.returncode:
                return {'url':url,'status':'fetch_failed','attempts':attempts,'body':''}
            if status in {'301','302','303','307','308'}:
                locations = re.findall(r'^location:\s*(.*?)\s*$',header.read_text(errors='replace'),re.I|re.M)
                if not locations:
                    return {'url':url,'status':'redirect_missing_location','attempts':attempts,'body':''}
                url = urljoin(url,locations[-1])
                continue
            if status != '200':
                return {'url':url,'status':status,'attempts':attempts,'body':''}
            body = path.read_text(errors='replace')
            return {'url':url,'status':status,'attempts':attempts,'body':body,'raw_sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
    return {'url':url,'status':'redirect_budget','attempts':attempts,'body':''}


def discover(url):
    page = fetch(url)
    links = Links(page.pop('body')).links if page['status'] == '200' else []
    return {'website':url,**page,'links':links}


def domain_owners():
    owners = {}
    for path in [ROOT/'data/ecosystem.csv', *sorted((ROOT/'data').glob('organizations_*.csv'))]:
        if path.name.endswith('_all.csv'):
            continue
        for row in csv.DictReader(path.open()):
            if row.get('website'):
                url = row['website'] if '://' in row['website'] else 'https://' + row['website']
                owners.setdefault(domain(url),set()).add(row['org_id'])
    return owners


def main():
    rows = list(csv.DictReader((HERE/'inputs.csv').open()))
    owners = domain_owners()
    output = HERE/'discovery.json'
    prior = json.loads(output.read_text()) if output.exists() else []
    have = {r['website'] for r in prior}
    for cohort in ['tier1','pic18_remainder']:
        urls = list(dict.fromkeys(r['website'] for r in rows
                   if r['cohort']==cohort and r['website'] and r['status']=='active'
                   and len(owners.get(domain(r['website'] if '://' in r['website'] else 'https://'+r['website']),set()))==1))
        pending = [u for u in urls if u not in have]
        print(cohort,len(urls),'eligible distinct own URLs;',len(pending),'pending',flush=True)
        with concurrent.futures.ThreadPoolExecutor(max_workers=16) as pool:
            for page in pool.map(discover,pending):
                prior.append(page); have.add(page['website'])
                output.write_text(json.dumps(prior,indent=2)+'\n')
                if len(prior)%50==0:
                    print('Fetched',len(prior),'own URLs;',sum(bool(p['links']) for p in prior),'with company anchors',flush=True)
    print('Completed',len(prior),'own URLs;',sum(bool(p['links']) for p in prior),'with header/footer company anchors',flush=True)


if __name__ == '__main__':
    main()

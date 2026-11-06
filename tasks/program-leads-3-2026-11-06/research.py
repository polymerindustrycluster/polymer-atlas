"""Bounded own-page discovery receipts. Fetches are leads, never automatic verdicts."""
import concurrent.futures, csv, hashlib, html, json, re, runpy, subprocess
from pathlib import Path
from urllib.parse import urlparse
HERE = Path(__file__).resolve().parent
CACHE = Path('/tmp/l13b-pages')
W = runpy.run_path(str(HERE.parent/'evidence-repair-2-2026-11-04/prep.py'))['W']


def found(text, quote):
    text, quote = W(text), W(quote)
    return bool(quote) and any(text[i:i+len(quote)] == quote for i in range(len(text)-len(quote)+1))


def fetch(url):
    CACHE.mkdir(exist_ok=True)
    key = hashlib.sha256(url.encode()).hexdigest()[:16]
    p = subprocess.run(['curl','-L','--max-time','25','-A','Mozilla/5.0','-sS','-w','\n%{http_code}\t%{url_effective}',url],capture_output=True)
    raw, _, metadata = p.stdout.rpartition(b'\n')
    status, _, final = metadata.decode('utf8','replace').partition('\t')
    (CACHE/f'{key}.html').write_bytes(raw)
    text = re.sub(r'<(script|style)\b[^>]*>.*?</\1>', ' ',raw.decode('utf8','replace'),flags=re.S|re.I)
    text = re.sub(r'\s+',' ',html.unescape(re.sub('<[^>]+>',' ',text)))
    if raw.startswith(b'%PDF'):
        subprocess.run(['pdftotext','-layout',str(CACHE/f'{key}.html'),str(CACHE/f'{key}.txt')],check=True,capture_output=True)
        text=(CACHE/f'{key}.txt').read_text()
        if not text.strip():
            subprocess.run(['pdftoppm','-singlefile','-r','200','-png',str(CACHE/f'{key}.html'),str(CACHE/key)],check=True,capture_output=True)
            # Homebrew Tesseract resolves relative image paths correctly; /tmp alias paths fail in this installation.
            result=subprocess.run(['tesseract',key+'.png','stdout','--psm','6'],cwd=CACHE,check=True,capture_output=True,text=True)
            text=result.stdout
        assert text.strip(), f'PDF unreadable: {url}'
    (CACHE/f'{key}.txt').write_text(text)
    return dict(url=url,final_url=final,http_status=status,curl_rc=p.returncode,bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest(),cache_key=key)


def main():
    # Known answers precede use on the research population.
    for url, quote in [('https://www.uwstout.edu/programs/bs-plastics-engineering','Bachelor of Science (B.S.) in Plastics Engineering'),('https://www.winona.edu/academics/programs/composite-materials-engineering/','Composite Materials Engineering'),('https://engineeringdesign.wwu.edu/polymer-materials-engineering','formerly Polymer Materials Engineering')]:
        r=fetch(url);text=(CACHE/(r['cache_key']+'.txt')).read_text()
        assert r['http_status']=='200' and found(text,quote),r
        assert not found(text,'Zyxw fabricated nonexistent qualification 928173')
    print('Calibration PASS: 3 own-page known positives and fabricated negative',flush=True)
    rows=list(csv.DictReader(open(HERE/'research_input.csv')))
    routes={}
    third=('4spe.org','rubber.org','pmsedivision.org','abet.org','skillscommons.org','airwashington.org','cbsnews.com','historylink.org','onetonline.org','adhesivesmag.com')
    for r in rows:
        urls=re.findall(r'https?://[^\s;]+',r['lead_url'])
        if not urls and re.fullmatch(r'[\w.-]+\.\w+/?',r['lead_url']):urls=['https://'+r['lead_url']]
        lead=next((u for u in urls if not any(d in urlparse(u).netloc for d in third)),None)
        url=lead or r['held_website'] or ''
        if url:routes.setdefault(url,[]).append(r['lead_id'])
    receipts=[]
    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:
        for url,result in zip(routes,pool.map(fetch,routes)):
            receipts.append(dict(lead_ids=routes[url],**result))
            print(result['http_status'],','.join(routes[url]),url,flush=True)
    (HERE/'fetches.json').write_text(json.dumps(receipts,indent=2)+'\n')
    print('Initial routes',len(receipts),'lead coverage',len({i for r in receipts for i in r['lead_ids']}),flush=True)


if __name__=='__main__':main()

#!/usr/bin/env python3
"""Raw-check sources using the evidence-repair token matcher and curl/Jina routes.
No data writes. Known answers run before fetching the wave.
"""
import csv, importlib.util, json, re, subprocess, sys, tempfile
from concurrent.futures import ThreadPoolExecutor
from html.parser import HTMLParser
from pathlib import Path
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
from research import SOURCES
spec = importlib.util.spec_from_file_location('repair', ROOT/'tasks/evidence-repair-2-2026-11-04/prep.py')
repair = importlib.util.module_from_spec(spec); spec.loader.exec_module(repair)
W = repair.W

class Text(HTMLParser):
    def __init__(self):
        super().__init__(); self.parts = []; self.skip = 0
    def handle_starttag(self, tag, attrs):
        if tag in ('script', 'style'): self.skip += 1
    def handle_endtag(self, tag):
        if tag in ('script', 'style'): self.skip = max(0, self.skip - 1)
    def handle_data(self, s):
        if not self.skip: self.parts.append(s)

def contains(text, quote):
    words, q = W(text), W(quote)
    return bool(q) and any(words[i:i+len(q)] == q for i in range(len(words)-len(q)+1))

def fetch(pair):
    key, (url, quote, *_) = pair
    attempts = []
    for route in (url, 'https://r.jina.ai/'+url):
        r = subprocess.run(['curl', '-fLsS', '--max-time', '35', '-A', 'Mozilla/5.0', route], capture_output=True, text=True)
        attempts.append(f'{route}: curl={r.returncode}')
        if r.returncode: continue
        t = Text(); t.feed(r.stdout); text = ' '.join(t.parts)
        if contains(text, quote):
            # Cache only outside the repository: pages may contain personal contact details.
            Path('/tmp/l3-'+key+'.txt').write_text(text)
            return dict(cluster_id='LF-'+key, url=url, quote=quote, raw='yes', route=route, attempts='; '.join(attempts))
    return dict(cluster_id='LF-'+key, url=url, quote=quote, raw='not_verified', route='', attempts='; '.join(attempts))

def check_supplements():
    with (HERE/'supplements.csv').open(newline='') as f: rows=list(csv.DictReader(f))
    for r in rows:
        if r['source_url'].endswith('.pdf'):
            with tempfile.TemporaryDirectory() as d:
                pdf=Path(d)/'witness.pdf'
                subprocess.run(['curl','-fLsS','--max-time','35','-A','Mozilla/5.0',r['source_url'],'-o',str(pdf)],check=True)
                text=subprocess.check_output(['pdftotext','-raw',str(pdf),'-'],text=True)
            assert contains(text,r['quote']) and not contains(text,r['quote']+' nonexistentdefect7731'),r
            r['route']='curl / pdftotext -raw'
        else:
            result=fetch((r['cluster_id'][3:],(r['source_url'],r['quote'])))
            assert result['raw']=='yes',r
            r['route']=result['route']
        r['raw']='yes'
    with (HERE/'supplements.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=rows[0],lineterminator='\n');w.writeheader();w.writerows(rows)
    print('supplemental quotes 5/5 raw-verified; PDF injected-quote defect rejected')

def main():
    if '--supplements-only' in sys.argv:
        check_supplements();return
    # Three known published scope witnesses, independently inspected before using this matcher.
    answers = [('MO-00088', 'We manufacture FDA approved polyethylene blown film using prime resins.'),
               ('MO-00023', 'Steering wheels, Airbags, Side Molding, Interior & Exterior plastic trim components for automobiles.'),
               ('SC-00082', 'precision machining and stamping of engineering and high-performance plastic materials')]
    for key, quote in answers:
        r = fetch((key, SOURCES[key])); assert r['raw'] == 'yes', (key, r)
        text = Path('/tmp/l3-'+key+'.txt').read_text()
        assert contains(text, quote), key
        assert not contains(text, quote+' nonexistentdefect7731'), key
    with ThreadPoolExecutor(max_workers=6) as ex: rows = list(ex.map(fetch, SOURCES.items()))
    with (HERE/'rawcheck.csv').open('w', newline='') as f:
        w=csv.DictWriter(f, fieldnames=rows[0], lineterminator='\n'); w.writeheader(); w.writerows(rows)
    print('known answers 3/3; injected quote defects rejected 3/3; raw checks', len(rows))
if __name__ == '__main__': main()

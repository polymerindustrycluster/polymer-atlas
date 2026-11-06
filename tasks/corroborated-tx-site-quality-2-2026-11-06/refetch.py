"""Re-fetch ten curl URLs and check ORBIS's explicitly supplied live rawHtml response."""
import argparse,hashlib,html,re
from pathlib import Path
from build import P,read
from research import fetch,found
ap=argparse.ArgumentParser();ap.add_argument('--orbis-html',required=True,type=Path,help='rawHtml from a fresh Firecrawl scrape of the admitted ORBIS URL with maxAge=0');a=ap.parse_args()
rows=read(P/'rawcheck.csv')
for url in dict.fromkeys(r['source_ref'] for r in rows):
    group=[r for r in rows if r['source_ref']==url];cache=Path(group[0]['cache_file'])
    if group[0]['route']=='firecrawl_live_rawHtml':
        assert 'orbiscorporation.com/en-us/news/orbis-expands-autostore-bin-production-to-texas/' in url
        raw=a.orbis_html.read_text();assert '<html' in raw.lower() and len(raw)>10000
        text=re.sub(r'<(script|style)\b.*?</\1>',' ',raw,flags=re.S|re.I);text=re.sub('<[^>]+>',' ',text);text=' '.join(html.unescape(text).split());cache.write_text(text)
    else:
        result=fetch((cache.stem.removeprefix('L6-'),url));assert result['fetch']=='loaded',result;text=cache.read_text()
    for r in group:
        assert found(text,r['quote']),('raw quote failed',r['site_id'],url,r['quote'])
        assert hashlib.sha256(text.encode()).hexdigest()==r['raw_sha256'],('raw text changed: reread before refreshing receipt',url)
    print('PASS raw',url,len(group),'literal quote rows',group[0]['route'])
print('PASS11URLs/13quotes; ORBIS live rawHtml is an explicit prerequisite, no skipped source')

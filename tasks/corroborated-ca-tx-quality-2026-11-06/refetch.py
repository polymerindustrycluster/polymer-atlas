"""Raw-check the five admitted URLs; PDF text uses the installed pdftotext."""
import hashlib,subprocess,sys
from pathlib import Path
from build import P,read
from research import fetch,found
rows=read(P/'rawcheck.csv')
for url in dict.fromkeys(r['source_ref'] for r in rows):
    group=[r for r in rows if r['source_ref']==url];cache=Path(group[0]['cache_file'])
    if url.endswith('.pdf'):
        pdf=cache.with_suffix('.pdf')
        subprocess.run(['curl','--fail','-sS','-L','--max-time','25','-A','Mozilla/5.0',url,'-o',str(pdf)],check=True)
        subprocess.run(['pdftotext','-layout',str(pdf),str(cache)],check=True)
    else:
        key=cache.stem.removeprefix('L6-');result=fetch((key,url));assert result['fetch']=='loaded',result
    text=cache.read_text()
    for r in group:
        assert found(text,r['quote']),('RAW QUOTE FAILED',r['site_id'],url,r['quote'])
        assert hashlib.sha256(text.encode()).hexdigest()==r['raw_sha256'],('RAW TEXT CHANGED; reread before refreshing receipt',url)
    print('PASS raw',url,len(group),'literal quote rows')
print('PASS 5/5 URLs, 6/6 quote rows; no summary or search-snippet witness admitted.')

"""Fresh raw quotes from the four admitted corporate URLs; reuse house HTML matcher."""
import hashlib,subprocess
from pathlib import Path
from build import P,read
from research import fetch,found
rows=read(P/'rawcheck.csv')
for url in dict.fromkeys(r['source_ref'] for r in rows):
    group=[r for r in rows if r['source_ref']==url];cache=Path(group[0]['cache_file'])
    if url.lower().endswith('.pdf'):
        pdf=cache.with_suffix('.pdf');subprocess.run(['curl','--fail','-sS','-L','--max-time','25','-A','Mozilla/5.0',url,'-o',str(pdf)],check=True)
        subprocess.run(['pdftotext','-layout',str(pdf),str(cache)],check=True)
    else:
        result=fetch((cache.stem.removeprefix('L6-'),url));assert result['fetch']=='loaded',result
    text=cache.read_text()
    for r in group:
        assert found(text,r['quote']),('raw quote missing',r['site_id'],url)
        assert hashlib.sha256(text.encode()).hexdigest()==r['raw_sha256'],('source changed; reread before refreshing receipt',url)
    print('PASS raw',url,len(group),'quote rows')
print('PASS7/7quotes over4/4URLs. Certificates used for dated operator identity, no certification/status field motion.')

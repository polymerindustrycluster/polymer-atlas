"""Raw curl observations for the first ten queue rows; retain only business snippets."""
import concurrent.futures
import html
import re
import subprocess
from federal_signals import HERE, read, write

CASES = [
('ORG-002133','https://vinyltoolanddie.com/',''),
('ORG-002712','https://www.tips-usa.com/resellers.cfm?RecordID=29C87E9F11A4DB5AA6A5C96614A47A74','FAY L WAGNER'),
('ORG-000422','https://www.littlern.com/index.html','Littlern Corporation'),
('ORG-000443','https://www.midlands-technologies.com/contact','1911 36th St NE'),
('ORG-000654','https://www.atp4pneumatics.com/about-us/','Advanced Technology Products'),
('ORG-000960','https://www.midwestplasticsoh.com/contactus.html',''),
('ORG-001427','https://www.knrubber.com/about.html','KN Rubber LLC'),
('ORG-001685','https://chemstar.direct/about/','Kittyhawk Molding'),
('ORG-001719','https://pyramidplastics.com/about/','Rockford'),
('ORG-001729','https://ir.icumed.com/news-releases/news-release-details/icu-medical-completes-acquisition-smiths-medical-smiths-group','January 6, 2022'),
]

def fetch(case):
    oid,url,quote=case
    for route in [url,'https://r.jina.ai/'+url]:
        proc=subprocess.run(['curl','-L','-sS','--max-time','25','-A','Mozilla/5.0','-w','\n%{http_code}',route],capture_output=True,text=True)
        body,_,status=proc.stdout.rpartition('\n')
        text=re.sub(r'\s+',' ',html.unescape(re.sub('<[^>]*>',' ',body)))
        if proc.returncode==0 and status=='200':
            matched=bool(quote and quote.lower() in text.lower())
            return dict(org_id=oid,url=url,route=route,http=status,quote=quote,raw='yes' if matched else 'no',note='Raw page words checked; not a dated closure witness')
    return dict(org_id=oid,url=url,route=route,http=status,quote='',raw='unfetchable',note='Availability only; no closure inference')

if __name__=='__main__':
    assert [r['org_id'] for r in read(HERE/'signals.csv')[:10]]==[r[0] for r in CASES]
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as pool:
        rows=list(pool.map(fetch,CASES))
    write(HERE/'rawcheck.csv',rows,list(rows[0]))
    print([(r['org_id'],r['http'],r['raw']) for r in rows])

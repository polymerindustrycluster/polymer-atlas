"""Fresh curl primary quotes, including explicit PDF text/OCR extraction; fail on every unread route."""
import csv
from research import HERE,CACHE,fetch,found


def main():
    rows=list(csv.DictReader(open(HERE/'quotes.csv')))
    checks=[]
    for url in dict.fromkeys(r['source_url'] for r in rows):
        response=fetch(url)
        assert response['http_status']=='200' and response['curl_rc']==0,response
        text=(CACHE/(response['cache_key']+'.txt')).read_text()
        for row in rows:
            if row['source_url']!=url:continue
            assert found(text,row['quote']),row
            assert not found(text,'Zyxw fabricated nonexistent qualification 928173')
            checks.append(dict(**row,raw='yes',observed_date='2026-11-06',sha256=response['sha256'],final_url=response['final_url']))
    assert len(checks)==len(rows)
    with open(HERE/'rawcheck.csv','w') as f:
        w=csv.DictWriter(f,fieldnames=list(checks[0]),lineterminator='\n');w.writeheader();w.writerows(checks)
    print('PASS',len(checks),'/',len(rows),'quotes;',len({r['source_url'] for r in rows}),'own pages;0skipped;negative rejected')


if __name__=='__main__':main()

"""Re-fetch both duplicate identity quotes; calibration already ran before research."""
import csv
from research import HERE,CACHE,fetch,found


def main():
    rows=list(csv.DictReader(open(HERE/'quotes.csv')));checks=[]
    for r in rows:
        response=fetch(r['source_url']);assert response['http_status']=='200',response
        text=(CACHE/(response['cache_key']+'.txt')).read_text();assert found(text,r['quote']),r
        assert not found(text,'Zyxw fabricated nonexistent qualification 928173')
        checks.append(dict(lead_id=r['lead_id'],source_url=r['source_url'],quote=r['quote'],raw='yes',sha256=response['sha256'],observed_date='2026-11-06'))
    assert len(checks)==2
    with open(HERE/'rawcheck.csv','w') as f:
        w=csv.DictWriter(f,fieldnames=list(checks[0]),lineterminator='\n');w.writeheader();w.writerows(checks)
    print('PASS2/2 raw own quotes;0skipped;fabricated negative rejected')


if __name__=='__main__':main()

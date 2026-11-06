"""Manual observations only; no automatic status adjudication."""
import csv,json,sys
from pathlib import Path
from research import found
HERE=Path(__file__).resolve().parent
FIELDS='rank,org_id,legal_name,verdict,finding,source_url,source_class,source_date,observed_date,quote,raw_check,fetch_count,settling_fact,proposed_status,successor_org_id,ultimate_parent_name,grain_hold,raw_cache_path'.split(',')
def write():
    inputs=list(csv.DictReader(open(HERE/'input.csv'))); logs=list(csv.DictReader(open(HERE/'fetch_log.csv')))
    decisions=json.loads((HERE/'decisions.json').read_text()); out=[]
    for r in inputs:
        if r['rank'] not in decisions: continue
        d=decisions[r['rank']]; ls=[x for x in logs if x['org_id']==r['org_id']]; n=d.get('n',1); log=ls[n-1]
        quote=d.get('quote',''); text=Path(log['raw_cache_path']).with_suffix('.txt').read_text()
        raw='yes' if quote and found(text,quote) else ('unfetchable' if log['http']!='200' else 'no')
        assert not quote or raw=='yes',(r['rank'],quote)
        out.append(dict(zip(FIELDS,[r['rank'],r['org_id'],r['legal_name'],d['verdict'],d['finding'],log['url'],'own_site',d.get('date',''),'2026-11-06',quote,raw,len(ls),d.get('settling',''),'','',d.get('parent',''),d.get('hold',''),log['raw_cache_path']])))
    with open(HERE/'verdicts.csv','w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=FIELDS);w.writeheader();w.writerows(out)
    print('Manually adjudicated:',len(out))
if __name__=='__main__': write()

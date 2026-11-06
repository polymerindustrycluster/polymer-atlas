"""Lead raw refetch of positive packet quotes; this never decides verdicts or writes canonical data."""
import csv
import concurrent.futures
import gzip
import hashlib
import runpy
import subprocess
from pathlib import Path

HERE=Path(__file__).resolve().parent
CACHE=Path('/tmp/atlas-l8-lead');CACHE.mkdir(exist_ok=True)
# Reuse the calibrated HTML extraction and house word matcher from the packet collector.
helpers=runpy.run_path(str(HERE/'lanes/B/research.py'))
Text,found=helpers['Text'],helpers['found']
FIELDS=['org_id','source_url','quote','http','raw_check','legal_name_in_raw','observed_date','body_sha256','raw_cache_path','detail']

def read(path):
    with open(path,newline='',encoding='utf-8') as f:return list(csv.DictReader(f))

def inspect(row,body,http,cache,detail=''):
    parser=Text();parser.feed(body)
    text=' '.join(parser.parts)
    return dict(org_id=row['org_id'],source_url=row['source_url'],quote=row['quote'],http=http,
                raw_check='yes' if http=='200' and found(text,row['quote']) else 'no' if http=='200' else 'unfetchable',
                legal_name_in_raw='yes' if found(text,row['legal_name']) else 'no',observed_date='2026-11-06',
                body_sha256=hashlib.sha256(body.encode()).hexdigest(),raw_cache_path=str(cache),detail=detail)

def main():
    path=HERE/'lead_rawcheck.csv'
    rows=read(path) if path.exists() else []
    done={(r['org_id'],r['source_url'],r['quote']) for r in rows}
    candidates=[r for lane in ('A','B') if (HERE/'lanes'/lane/'verdicts.csv').exists() for r in read(HERE/'lanes'/lane/'verdicts.csv') if r['verdict']=='VERIFIED']
    pending=[r for r in sorted(candidates,key=lambda r:int(r['rank'])) if (r['org_id'],r['source_url'],r['quote']) not in done]
    def refetch(row):
        suffix=hashlib.sha256((row['source_url']+row['quote']).encode()).hexdigest()[:12]
        cache=CACHE/f"{row['org_id']}-{suffix}.html"
        proc=subprocess.run(['curl','-L','-sS','--max-time','30','-A','Mozilla/5.0','-o',str(cache),'-w','%{http_code}',row['source_url']],capture_output=True,text=True)
        raw=cache.read_bytes() if cache.exists() else b''
        if raw.startswith(b'\x1f\x8b'):raw=gzip.decompress(raw)
        body=raw.decode('utf-8','replace')
        return inspect(row,body,proc.stdout if proc.returncode==0 else '000',cache,proc.stderr.strip())
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        for result in pool.map(refetch,pending):
            with open(path,'a',newline='',encoding='utf-8') as f:
                w=csv.DictWriter(f,fieldnames=FIELDS,lineterminator='\n')
                if not rows:w.writeheader()
                w.writerow(result)
            rows.append(result)
            print(result['org_id'],result['http'],result['raw_check'],flush=True)

if __name__=='__main__':main()

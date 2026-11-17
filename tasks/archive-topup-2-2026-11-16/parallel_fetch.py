"""Four disjoint process slices, one locked journal, persistent shared deadline."""
import subprocess,time
from common import *

def repair_journal(grouped):
    journal=[]
    for url,rows in grouped.items():
        path=PROOFS/(sha(url.encode())+'.json')
        if path.exists():
            r=json.loads(path.read_text())
            journal.append(dict(url_order=rows[0]['url_order'],url=url,links=len(r['links']),status=r['status'],finished=r['finished']))
    tmp=PROOFS/'journal.tmp';tmp.write_text(''.join(json.dumps(r)+'\n' for r in journal));tmp.replace(PROOFS/'journal.jsonl')

def main():
    grouped={}
    for r in house.read(HERE/'inputs.csv'):grouped.setdefault(r['url'],[]).append(r)
    slices=[set(list(grouped)[i::4]) for i in range(4)]
    assert set.union(*slices)==set(grouped) and sum(map(len,slices))==len(grouped)
    repair_journal(grouped)
    jobs=[]
    for i in range(4):
        env=dict(os.environ,ARCHIVE_WORKER=str(i),ARCHIVE_WORKERS='4')
        with open(PROOFS/('worker-'+str(i)+'.log'),'a') as log:
            p=subprocess.Popen([sys.executable,'-u',str(HERE/'fetch.py')],env=env,stdin=subprocess.DEVNULL,stdout=log,stderr=log)
        jobs.append(p)
    (PROOFS/'workers.txt').write_text('\n'.join(str(p.pid) for p in jobs)+'\n')
    codes=[p.wait() for p in jobs]
    repair_journal(grouped)
    (PROOFS/'terminal.json').write_text(json.dumps(dict(finished=time.time(),exit_codes=codes,deadline=json.loads((PROOFS/'state.json').read_text())['deadline'])))
if __name__=='__main__':main()

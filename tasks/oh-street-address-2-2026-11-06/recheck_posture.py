"""Monotonic source-context correction: re-fetch only previously accepted witness URLs."""
import concurrent.futures
from fetch import TASK,read,write,fetch,mailing_posture
verdicts=read(TASK/'verdicts.csv');ids={v['site_id'] for v in verdicts if v['verdict']=='VERIFIED'}|{'SITE-000008'}
rows=read(TASK/'rawchecks.csv');urls=sorted({r['url'] for r in rows if r['site_id'] in ids and r['street_address']})
def one(u):
 try:text,links,sha=fetch(u);return u,text,sha,''
 except Exception as ex:return u,'','',str(ex)
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:pages={u:(text,sha,error) for u,text,sha,error in pool.map(one,urls)}
log=[]
for r in rows:
 if r['site_id'] not in ids or not r['street_address']:continue
 text,sha,error=pages[r['url']]
 posture='source unavailable on posture recheck' if error else mailing_posture(text,r['quote'])
 # A previous negative remains negative: broadening the gate never creates a new positive.
 r['posture']=r['posture'] or posture
 log.append(dict(site_id=r['site_id'],url=r['url'],quote=r['quote'],fresh_sha256=sha,posture=r['posture'],error=error))
write(TASK/'rawchecks.csv',rows);write(TASK/'mailing_recheck.csv',log)
print('previous-positive site IDs',len(ids),'uniqueURLs',len(urls),'newly flagged',sorted({r['site_id'] for r in log if r['posture']}))

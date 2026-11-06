"""Named continuation check: no baseline rewrite, exact16, original34 preserved and source limits."""
import copy,hashlib,json,subprocess,sys
from collections import Counter
from pathlib import Path
from freeze import H,collected,digest,main as lockcheck,read
from summarize import combine
from write_addendum import baseline_text,render,REPORT
OLD=H.parent/'blind-audit-9-2026-11-06'
sys.path.insert(0,str(OLD))
from stats import summarize,wilson

def frozen_check(rows,receipt):
 assert len(rows)==len({r['site_id'] for r in rows})==16
 assert {r['site_id']:digest(r) for r in rows}==receipt['records'],'locked follow-up edit'
def main():
 pin=json.loads((H/'baseline.json').read_text());old=json.loads((OLD/'adjudicated_verdicts.json').read_text());inputs=read(H/'input.csv')
 assert len(inputs)==len({r['site_id'] for r in inputs})==16
 assert {r['site_id'] for r in inputs}=={r['site_id'] for r in old if r['grade']=='unresolved'}
 before={r['site_id']:r for r in read(OLD/'sample.csv')}
 assert all(r==before[r['site_id']] for r in inputs),'frozen record assertions changed'
 assert hashlib.sha256((OLD/'adjudicated_verdicts.json').read_bytes()).hexdigest()==pin['original_adjudicated_sha256']
 rows=collected();receipt=json.loads((H/'freeze.json').read_text());frozen_check(rows,receipt);lockcheck()
 for k in 'ab':
  name=f'verdicts_{k}.json';assert hashlib.sha256((H/name).read_bytes()).hexdigest()==receipt['files'][name]
 merged=combine(old,rows,set(pin['followup_ids']));expected=summarize(read(OLD/'sample.csv'),merged);actual=json.loads((H/'updated_statistics.json').read_text())
 assert {k:actual[k] for k in expected}==expected and actual['followup_sites']==16 and 'unequal verification effort' in actual['design_note']
 assert json.loads((H/'updated_50_verdicts.json').read_text())==merged
 assert REPORT.read_text().startswith(baseline_text()) and REPORT.read_text()==render(),'originalprefix/addendumchanged'
 assert wilson(0,20)==[0,0.161125] and wilson(20,20)==[0.838875,1] and wilson(10,20)==[0.299298,0.700702]
 for bad in [rows[:-1],rows[:-1]+[rows[0]]]:
  try:frozen_check(bad,receipt)
  except AssertionError:pass
  else:raise AssertionError('incomplete/duplicate result accepted')
 bad=copy.deepcopy(rows);bad[0]['observations']+=' fabricated unlocked change'
 try:frozen_check(bad,receipt)
 except AssertionError:pass
 else:raise AssertionError('post-lock edit accepted')
 attempts=[]
 for k in 'ab':
  rr=json.loads((H/f'receipts_{k}.json').read_text());attempts+=rr
  cal=json.loads((H/f'calibration_{k}.json').read_text());assert cal,'missing calibration record'
 counts=Counter(r['site_id'] for r in attempts);assert set(counts)==set(pin['followup_ids']) and max(counts.values())<=10,'research budget/extraction coverage failure'
 raw=json.loads((H/'rawcheck_results.json').read_text());assert raw['attempted_routes']==len(attempts) and raw['raw_bodies_verified']+len(raw['unarchived_discovery_or_failed_routes'])==len(attempts)
 assert raw['checked_quote_observations']==sum(bool(s['raw_checked']) for r in rows for s in r['sources'])
 for cached in [False,True]:subprocess.run(['git','diff']+(['--cached'] if cached else [])+['--quiet','--exit-code','--','data/'],check=True)
 assert not subprocess.check_output(['git','diff',pin['audit_head'],'--name-only','--','data/']).strip(),'canonical diff from frozen audit'
 print('PASS16followup/50samerecords/34unchanged/8originalstrata;hashlocks/sourcecensus<=10routes/Wilson3known/frozen3defects/appendonlyreport/0data')
if __name__=='__main__':main()

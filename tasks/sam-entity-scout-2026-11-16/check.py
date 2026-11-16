"""Offline population, filtering, seeded sample and receipt checks."""
import copy,csv,hashlib,json,re,sqlite3
from collections import Counter
from build import CACHE,HERE,excluded
from summarize import summarize

def population(c,m):
 n=c.execute('select count(*) from sam').fetchone()[0];r=m['counts']
 assert n==r['indexed_records']
 assert n+r['dropped_union']==r['declared_record_count']==r['input_records']==911820
 assert r['drop_db_source']==m['evs_sources']['D&B']==466
 assert r['dropped_union']==r['drop_db_source']+r['drop_legacy_date']-r['drop_overlap']+r['missing_or_invalid_date']
 assert not c.execute("select 1 from sam where evs like '%D&B%' or updated<'20220404' or length(updated)<>8 limit 1").fetchone()
 assert (CACHE/'sam.sqlite').stat().st_size<1500000000
 assert dict(c.execute('select class,count(*) from matches group by class'))==m['match_pairs_by_class']

def main():
 sources=json.loads((HERE/'sources.json').read_text());assert len(sources)==2
 for r in sources:
  raw=(CACHE/r['cache_file']).read_bytes();assert len(raw)==r['bytes'] and hashlib.sha256(raw).hexdigest()==r['sha256']
 c=sqlite3.connect(CACHE/'sam.sqlite');m=json.loads((HERE/'metrics.json').read_text());population(c,m)
 assert sum(m['evs_sources'].values())==m['counts']['input_records']
 rows=list(csv.DictReader((HERE/'sample.csv').open()));assert len(rows)==len({(r['record_id'],r['uei']) for r in rows})==80
 for cls in m['match_pairs_by_class']:
  pairs=list(c.execute('select record_id,uei from matches where class=?',(cls,)))
  pairs.sort(key=lambda x:hashlib.sha256(('20261116|'+cls+'|'+x[0]+'|'+x[1]).encode()).hexdigest())
  assert {(r['record_id'],r['uei']) for r in rows if r['match_class']==cls}==set(pairs[:20])
  assert all(r['verdict'] in {'VERIFIED','REJECT','STILL_UNCERTAIN'} and r['reason'] for r in rows if r['match_class']==cls)
 assert summarize()==m
 # Inject forbidden source, pre-cutoff date and absent date into otherwise accepted records.
 for label,pos,val in [('D&B source',121,'D&B'),('legacy date',9,'20220403'),('unknown date',9,'')]:
  r=['']*142;r[9]='20220404';r[121]='E&Y';assert excluded(r)==(False,False)
  r[pos]=val;assert any(excluded(r)),label
  print('caught:',label)
 bad=copy.deepcopy(m);bad['counts']['indexed_records']-=1
 try:population(c,bad)
 except AssertionError:print('caught: index row loss')
 else:raise AssertionError('silent row-loss pass')
 print('PASS: source population, filter accounting, unique seeded 80-row sample, summaries and 4 injected defects')
if __name__=='__main__':main()

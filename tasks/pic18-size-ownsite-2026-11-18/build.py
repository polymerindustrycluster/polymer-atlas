"""Own-site Ohio size bands for the 20 Ohio-only frame organizations; blank-only, organization rows only.
Idempotent: plans from verdicts.csv + the current data/, writes fills/evidence packets, --apply edits data/."""
import argparse,csv,json,os,re,sys
from collections import Counter
from pathlib import Path
D=Path(__file__).resolve().parent;ROOT=GITROOT=D.parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from build_form5500_spine import band_of,BANDS
from shard_io import append_sorted
S=Path('/Users/johnswanson/.bb/thread-storage/thr_9i2c6byhcz/2026-11-06-atlas')
CORPUS=S/'persist/pic18-corpus-2026-11-16'
FIELD='employee_band_ohio';CREATED_BY='claude-code pic18-size-ownsite-2026-11-18'

def base_max_evidence_id(base):
 """Highest EVD number across every data/evidence_*.csv at `base` (SCHEMA: next-free at application; AGENTS 3: never fill a gap)."""
 import subprocess,io
 names=[n for n in subprocess.check_output(['git','ls-tree','--name-only',base,'data/'],cwd=GITROOT,text=True).split() if Path(n).name.startswith('evidence_') and n.endswith('.csv')]
 return max(int(r['evidence_id'][4:]) for n in names for r in csv.DictReader(io.StringIO(subprocess.check_output(['git','show',f'{base}:{n}'],cwd=GITROOT,text=True))))

def merge_base():
 import subprocess
 return subprocess.check_output(['git','merge-base','HEAD','origin/main'],cwd=GITROOT,text=True).strip()

def read(p):return list(csv.DictReader(Path(p).open(newline='')))
def write(p,rows,fields):
 with Path(p).open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=fields,lineterminator='\n');w.writeheader();w.writerows(rows)
def band(n):return '5000+' if n>=5000 else band_of(n)

def load():
 orgs={};shard={}
 for p in sorted((ROOT/'data').glob('organizations_*.csv')):
  for r in read(p):orgs[r['org_id']]=r;shard[r['org_id']]=p.stem.split('_',1)[1]
 sites={}
 for p in (ROOT/'data').glob('sites_*.csv'):
  for r in read(p):sites.setdefault(r['org_id'],[]).append(r)
 return orgs,shard,sites

NOUN=r'(?:full[- ]time\s+)?(?:employees|people|associates|team members|staff)'
def count_kind(quote,n):
 """'exact' or 'closed_range' only: the number must be the employee/people count itself, stated exactly (about/~ allowed)
 or as a closed range whose two ends fall in one band. Any bound that needs inference ("over", "at most", "fewer than",
 "N+", "nearly") or a number for another quantity returns None: the statement is held, "no exact count or closed range"."""
 q=re.sub(r'(?<=\d),(?=\d{3})','',quote)
 if re.search(rf'(?:over|more than|at least|exceeds|at most|no more than|fewer than|less than|under|up to|nearly|almost)\s+(?:about\s+)?~?{n}\b|\b{n}\s*\+',q,re.I):return None
 m=re.search(rf'\b{n}\s*(?:-|–|to)\s*(\d+)\s+{NOUN}\b',q,re.I)
 if m:return 'closed_range' if int(m[1])>=n and band(int(m[1]))==band(n) else None
 if re.search(rf'(?:employ\w*|staff of|team of|organization of)\s+(?:about\s+|approximately\s+)?~?{n}\b(?!\s*(?:-|–|to)\s*\d)',q,re.I) or re.search(rf'\b{n}\s+{NOUN}\b',q,re.I):return 'exact'
 return None

def ohio_only(o,ss):return o['hq_state']=='OH' and bool(ss) and all(s['state']=='OH' for s in ss)

def plan(verdicts=None,check_existing=True,base=None):
 orgs,shard,sites=load();verdicts=verdicts or read(D/'verdicts.csv');fills=[];evs=[];held=[]
 first=base_max_evidence_id(base or merge_base())+1
 applied=sorted((v for v in verdicts if v['disposition']=='applied'),key=lambda v:v['org_id'])
 for k,v in enumerate(applied):
  oid=v['org_id'];o=orgs[oid]
  assert ohio_only(o,sites.get(oid,[])),f'{oid} is not Ohio-only in the current data'
  new=band(int(v['stated_count']));assert new==v['band'],f'{oid} band {v["band"]} != band of {v["stated_count"]}'
  assert count_kind(v['quote'],int(v['stated_count'])),f'{oid}: no exact count or closed range'
  assert o[FIELD] in ('',new),f'{oid} already holds a different band {o[FIELD]!r}'
  eid=first+k
  fills.append(dict(record_table='organizations',record_id=oid,field=FIELD,old='',new=new,stated_count=v['stated_count'],url=v['url'],evidence_id=f'EVD-{eid}',shard=shard[oid]))
  evs.append(dict(evidence_id=f'EVD-{eid}',record_table='organizations',record_id=oid,claim_type='size_band',
   claim_detail=f'{FIELD}={new}; own-site statement: "{v["quote"]}"; a company count for an Ohio-only organization (HQ and every held site in Ohio), band only, never allocated to a site',
   source_class='own_site',source_ref=v['url'],observed_date=v['observed_date'],tier_effect='supports_U' if o['verification_tier']=='U' else 'supports_B',created_by=CREATED_BY,
   notes=f'stored page sha256 {v["raw_sha256"]}; fetched {v["observed_date"]}; observed_date is the stored fetch date; page date: {v['page_date']}; blank-only fill of {FIELD}; no site row written'))
 mine={e['record_id'] for p in (ROOT/'data').glob('evidence_organizations_*.csv') for e in read(p) if e['created_by']==CREATED_BY}
 for f in (fills if check_existing else []):
  if orgs[f['record_id']][FIELD]==f['new']:assert f['record_id'] in mine,'cell already holds this band without this pass\'s evidence row: '+f['record_id']
 return fills,evs,verdicts

def git_base_count(base,path):
 import subprocess,io
 return len(list(csv.DictReader(io.StringIO(subprocess.check_output(['git','show',f'{base}:{path}'],cwd=GITROOT,text=True)))))

def apply(fills,evs,base):
 """Stage every shard as a temp sibling, check each staged row count against its count at base (+ this packet's
 evidence rows), then replace evidence first and organizations last: a failure leaves no cell without its evidence."""
 existing={e['evidence_id']:e for p in (ROOT/'data').glob('evidence_organizations_*.csv') for e in read(p)}
 for e in evs:assert e['evidence_id'] not in existing or existing[e['evidence_id']]==e,'evidence ID collision'
 staged=[];temps=[]  # staged = (temp, target) in replace order; temps = every temp file created
 try:
  for sh in sorted({f['shard'] for f in fills}):
   mine={f['record_id']:f for f in fills if f['shard']==sh}
   org=ROOT/'data'/f'organizations_{sh}.csv';ev=ROOT/'data'/f'evidence_organizations_{sh}.csv'
   rows=read(org)
   for r in rows:
    f=mine.get(r['org_id'])
    if f:assert r[FIELD] in ('',f['new']),'refuse a non-blank cell';r[FIELD]=f['new']
   t_org=org.with_name(org.name+'.stage');temps.append(t_org);write(t_org,rows,list(rows[0]))
   assert len(read(t_org))==git_base_count(base,f'data/{org.name}'),f'{org.name}: staged rows differ from the count at base'
   t_ev=ev.with_name(ev.name+'.stage');temps.append(t_ev);keep=[e for e in read(ev) if not (e['created_by']==CREATED_BY and e['evidence_id'] not in {x['evidence_id'] for x in evs})]
   write(t_ev,keep,list(read(ev)[0]))  # re-allocation: this pass's own rows under stale IDs are replaced; nothing else is touched
   append_sorted(t_ev,[e for e in evs if e['record_id'] in mine and e['evidence_id'] not in {k['evidence_id'] for k in keep}],'evidence_id')
   assert len(read(t_ev))==git_base_count(base,f'data/{ev.name}')+sum(e['record_id'] in mine for e in evs),f'{ev.name}: staged rows differ from base + packet'
   staged+= [(t_ev,ev),(t_org,org)]
  for t,target in staged:os.replace(t,target)
 finally:
  for t in temps:
   if t.exists():t.unlink()

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--apply',action='store_true');ap.add_argument('--base');a=ap.parse_args()
 fills,evs,verdicts=plan(base=a.base)
 write(D/'fills.csv',fills,list(fills[0]));write(D/'evidence_rows.csv',evs,list(evs[0]))
 c=Counter(v['disposition'] for v in verdicts)
 (D/'counts.json').write_text(json.dumps(dict(frame=len(verdicts),ohio_only=sum(v['ohio_only']=='true' for v in verdicts),dispositions=dict(c),fills=len(fills),evidence_rows=len(evs),fills_by_band=dict(Counter(f['new'] for f in fills))),indent=2,sort_keys=True)+'\n')
 if a.apply:
  import subprocess
  apply(fills,evs,a.base or merge_base())
 print(open(D/'counts.json').read())
if __name__=='__main__':main()

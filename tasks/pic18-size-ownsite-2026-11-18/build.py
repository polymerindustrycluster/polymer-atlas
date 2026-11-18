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
FIELD='employee_band_ohio';FIRST_ID=396300;LAST_ID=396399;CREATED_BY='claude-code pic18-size-ownsite-2026-11-18'

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

def open_ended_ok(quote,n,lo,hi):
 """An open-ended count ("over/more than/at least N", "N+") settles no band unless an upper bound under the band's top is also stated."""
 q=re.sub(r'(?<=\d),(?=\d{3})','',quote)
 if not (re.search(rf'(?:over|more than|at least|exceeds)\s+~?{n}\b',q,re.I) or re.search(rf'\b{n}\s*\+',q)):return True
 return any(lo<=n<int(m)<=hi+1 for m in re.findall(r'(?:under|fewer than|less than|up to|no more than|at most)\s+(\d+)',q,re.I))

def ohio_only(o,ss):return o['hq_state']=='OH' and bool(ss) and all(s['state']=='OH' for s in ss)

def plan():
 orgs,shard,sites=load();verdicts=read(D/'verdicts.csv');fills=[];evs=[];held=[]
 applied=sorted((v for v in verdicts if v['disposition']=='applied'),key=lambda v:v['org_id'])
 for k,v in enumerate(applied):
  oid=v['org_id'];o=orgs[oid]
  assert ohio_only(o,sites.get(oid,[])),f'{oid} is not Ohio-only in the current data'
  new=band(int(v['stated_count']));assert new==v['band'],f'{oid} band {v["band"]} != band of {v["stated_count"]}'
  lo,hi=next((l,h) for l,h,lab in BANDS if lab==new) if new!='5000+' else (5000,10**9)
  assert open_ended_ok(v['quote'],int(v['stated_count']),lo,hi),f'{oid}: open-ended count (over/more than/at least/+) with no stated upper bound'
  assert o[FIELD] in ('',new),f'{oid} already holds a different band {o[FIELD]!r}'
  eid=FIRST_ID+k;assert eid<=LAST_ID
  fills.append(dict(record_table='organizations',record_id=oid,field=FIELD,old='',new=new,stated_count=v['stated_count'],url=v['url'],evidence_id=f'EVD-{eid}',shard=shard[oid]))
  evs.append(dict(evidence_id=f'EVD-{eid}',record_table='organizations',record_id=oid,claim_type='size_band',
   claim_detail=f'{FIELD}={new}; own-site statement: "{v["quote"]}"; a company count for an Ohio-only organization (HQ and every held site in Ohio), band only, never allocated to a site',
   source_class='own_site',source_ref=v['url'],observed_date=v['observed_date'],tier_effect='supports_U' if o['verification_tier']=='U' else 'supports_B',created_by=CREATED_BY,
   notes=f'stored page sha256 {v["raw_sha256"]}; fetched {v["observed_date"]}; observed_date is the stored fetch date; page date: {v['page_date']}; blank-only fill of {FIELD}; no site row written'))
 have={e['evidence_id']:e for p in (ROOT/'data').glob('evidence_organizations_*.csv') for e in read(p)}
 for f,e in zip(fills,evs):
  if orgs[f['record_id']][FIELD]==f['new']:assert have.get(e['evidence_id'])==e,'cell already holds this band without this pass\'s evidence row: '+f['record_id']
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
   t_ev=ev.with_name(ev.name+'.stage');temps.append(t_ev);t_ev.write_bytes(ev.read_bytes())
   append_sorted(t_ev,[e for e in evs if e['record_id'] in mine and e['evidence_id'] not in existing],'evidence_id')
   assert len(read(t_ev))==git_base_count(base,f'data/{ev.name}')+sum(e['record_id'] in mine for e in evs),f'{ev.name}: staged rows differ from base + packet'
   staged+= [(t_ev,ev),(t_org,org)]
  for t,target in staged:os.replace(t,target)
 finally:
  for t in temps:
   if t.exists():t.unlink()

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--apply',action='store_true');ap.add_argument('--base');a=ap.parse_args()
 fills,evs,verdicts=plan()
 write(D/'fills.csv',fills,list(fills[0]));write(D/'evidence_rows.csv',evs,list(evs[0]))
 c=Counter(v['disposition'] for v in verdicts)
 (D/'counts.json').write_text(json.dumps(dict(frame=len(verdicts),ohio_only=sum(v['ohio_only']=='true' for v in verdicts),dispositions=dict(c),fills=len(fills),evidence_rows=len(evs),fills_by_band=dict(Counter(f['new'] for f in fills))),indent=2,sort_keys=True)+'\n')
 if a.apply:
  import subprocess
  apply(fills,evs,a.base or subprocess.check_output(['git','merge-base','HEAD','origin/main'],cwd=GITROOT,text=True).strip())
 print(open(D/'counts.json').read())
if __name__=='__main__':main()

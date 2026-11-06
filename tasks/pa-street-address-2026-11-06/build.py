"""Apply raw operator-page streets to the frozen 24-site PA blank cohort; no other geography changes."""
import csv,json,re,sys
from pathlib import Path
TASK=Path(__file__).resolve().parent;ROOT=TASK.parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from shard_io import append_sorted
from fetch import extract,read,write,fetch,known

def key(s):
 aliases={'STREET':'ST','WEST':'W','EAST':'E','NORTH':'N','SOUTH':'S','ROAD':'RD','DRIVE':'DR','AVENUE':'AVE','PARKWAY':'PKWY','PLACE':'PL'}
 return ' '.join(aliases.get(t,t) for t in re.findall('[A-Z0-9]+',s.upper()))

def run(apply=False):
 baseline=read(TASK/'baseline_blank.csv');checks=read(TASK/'rawchecks.csv');sites=read(ROOT/'data/sites_PA.csv');byid={r['site_id']:r for r in sites}
 ev=[];verdicts=[]
 for i,s in enumerate(sorted(baseline,key=lambda r:r['site_id'])):
  rows=[r for r in checks if r['site_id']==s['site_id'] and r['street_address']];why=[]
  if not rows:why.append('need own-operator physical street page for this city; none raw-checked within cap')
  if len({key(r['street_address']) for r in rows})>1:why.append('raw source address blocks disagree')
  if any(s['zip'] and s['zip'][:5]!=r['source_zip'][:5] for r in rows):why.append('existing ZIP conflicts with own-page ZIP; geography correction is outside this pass')
  if any(not re.match(r'^\d+\s+[A-Za-z]',r['street_address']) or not re.search('[A-Za-z]',r['street_address']) for r in rows):why.append('ambiguous physical street')
  # Notes are leads only, but a differing complete address blocks application.
  noted=extract(s['notes'],s['city'])
  if rows and any(key(x[0])!=key(rows[0]['street_address']) for x in noted):why.append('notes address differs from raw page; adjudication required')
  row=dict(site_id=s['site_id'],verdict='STILL_UNCERTAIN' if why else 'VERIFIED',street_address=rows[0]['street_address'] if rows else '',reason='; '.join(why),evidence_id='')
  if not why:
   r=rows[0];eid=f'EVD-{155000+i:06d}';row['evidence_id']=eid
   ev.append(dict(evidence_id=eid,record_table='sites',record_id=s['site_id'],claim_type='address',claim_detail=f"street_address {r['street_address']}, {s['city']}, PA; own-page ZIP {r['source_zip']}",
      source_class='own_site',source_ref=r['url'],observed_date='2026-11-06',tier_effect='supports_A',created_by='atlas-L2-pa-address',
      notes=f"Raw checked 2026-11-06; SHA-256 {r['sha256']}; quote: {r['quote']}. County, county_source, ZIP and record tier unchanged."))
  verdicts.append(row)
 assert len(verdicts)==len({r['site_id'] for r in verdicts})==24
 write(TASK/'verdicts.csv',verdicts);write(TASK/'holds.csv',[r for r in verdicts if r['verdict']!='VERIFIED']);write(TASK/'evidence.csv',ev)
 if apply:
  (TASK/'backups').mkdir(exist_ok=True)
  for name in ('sites_PA.csv','evidence_sites_PA.csv'):
   p=ROOT/'data'/name;b=TASK/'backups'/name
   if not b.exists():b.write_bytes(p.read_bytes())
  existing={r['evidence_id']:r for r in read(ROOT/'data/evidence_sites_PA.csv')};new=[];eb={r['record_id']:r for r in ev}
  for v in verdicts:
   if v['verdict']!='VERIFIED':continue
   s=byid[v['site_id']];old=next(r for r in baseline if r['site_id']==s['site_id'])
   for field in ('org_id','city','zip','county','county_source','verification_tier','operating_status'):assert s[field]==old[field],(s['site_id'],field)
   assert s['street_address'] in ('',v['street_address']),'new street conflict'
   s['street_address']=v['street_address'];e=eb[s['site_id']]
   if e['source_ref'] not in s['sources']:s['sources']+='; '+e['source_ref']
   if e['evidence_id'] in existing:assert existing[e['evidence_id']]==e,'evidence collision'
   else:new.append(e)
  if new:append_sorted(ROOT/'data/evidence_sites_PA.csv',new,'evidence_id')
  write(ROOT/'data/sites_PA.csv',sites)
 summary=dict(active_sites=774,before_filled=750,fills=len(ev),after_filled=750+len(ev),holds=24-len(ev));(TASK/'summary.json').write_text(json.dumps(summary,indent=2)+'\n');print(summary)

def audit():
 ev=read(TASK/'evidence.csv');out=[]
 for e in ev:
  error=''
  try:
   text,_,sha=fetch(e['source_ref']);quote=e['notes'].split('; quote: ')[1].removesuffix('. County, county_source, ZIP and record tier unchanged.')
   assert ' '.join(quote.split()) in ' '.join(text.split()),'quote missing'
  except Exception as ex:error=str(ex)
  out.append(dict(site_id=e['record_id'],source_ref=e['source_ref'],result='PASS' if not error else 'FAIL',error=error))
 write(TASK/'audit.csv',out);assert len(out)==len(ev) and not any(r['error'] for r in out),out
 print(f'Own-page fresh-refetch census: {len(out)}/{len(ev)}, zero errors')

if __name__=='__main__':
 if '--known' in sys.argv:known()
 elif '--audit' in sys.argv:audit()
 else:run('--apply' in sys.argv)

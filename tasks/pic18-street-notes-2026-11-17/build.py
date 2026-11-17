"""Write street_address cells + address evidence from verdicts.csv. Re-verifies every witness from stored raw bytes
before any write (no trust in verdicts.csv); idempotent. Evidence block EVD-395000..395999."""
import hashlib,json,re,shutil,sys
from html.parser import HTMLParser
from pathlib import Path
import scout
from scout import ROOT,TASK,S,CORPUS,TODAY,read,write,norm,ws,sha,FED,LABEL,candidates
sys.path.insert(0,str(ROOT/'scripts'))
from shard_io import append_sorted
from atlas import street_key,notes_candidate_key,NOTES_STREET_RE
CREATOR='atlas-w17-streetnotes';BASE_ID=395000;DATA=ROOT/'data'
class Text(HTMLParser):
 def __init__(s):super().__init__();s.p=[]
 def handle_data(s,d):s.p.append(d)
def words(t):return re.findall(r'[a-z0-9]+',t.lower())
def in_order(hay,needle):
 h,n=words(hay),words(needle);return bool(n) and any(h[i:i+len(n)]==n for i in range(len(h)-len(n)+1))
def refuse(c,msg):assert c,msg
def pins():
 p={r['site_id']:r for r in read(TASK/'evidence_ids.csv')};return p
def plan(verdicts=None):
 verdicts=verdicts if verdicts is not None else read(TASK/'verdicts.csv');frame={r['site_id']:r for r in read(TASK/'frame.csv')}
 sites={s['site_id']:s for s in read(DATA/'sites_OH.csv')};seen={};ev=[];pn=pins();nxt=max(int(r['evidence_id'][4:]) for r in pn.values())+1
 for v in verdicts:
  refuse(v['site_id'] in frame,'not in frame')
  if v['verdict']!='VERIFIED':refuse(v['hold_class'] and v['settling_fact'],'hold without class/fact');continue
  sid=v['site_id'];s=sites[sid];f=frame[sid]
  refuse(s['street_address'] in ('',v['street']),'street conflict on live row')
  refuse(all(s[k]==f[k] for k in ('org_id','city','zip','county','notes')),'frozen site drift')
  q=v['quote'];street=v['street']
  refuse(not LABEL.search(q),'mailing/parent/corporate-labeled address refused')
  refuse(norm(s['city']) in norm(q),'city differs from the site city')
  refuse(not re.search(r'\(\d{3}\)|\d{3}[-.]\d{4}',q),'phone number in quote')
  cs=candidates(f['notes']);refuse(len(cs)==1,'two streets in notes');m=NOTES_STREET_RE.search(street)
  refuse(m and notes_candidate_key(m[0])==next(iter(cs)),'applied street does not match the notes candidate')
  k=(street_key(street),norm(s['city']));refuse(k not in seen,'duplicate street in this pass');seen[k]=sid
  refuse(not any(o['site_id']!=sid and o['street_address'] and street_key(o['street_address'])==k[0] and norm(o['city'])==k[1] for o in sites.values()),'collision with an existing site street')
  if v['source_class']=='own_site':
   mm=next(x for x in read(CORPUS/'manifest.csv') if x['raw_file']==v['raw_file']);refuse(mm['org_id']==s['org_id'],'page belongs to another org')
   raw=(CORPUS/v['raw_file']).read_bytes();refuse(sha(raw)==v['sha256'],'raw sha mismatch')
   t=Text();t.feed(raw.decode(errors='replace'));refuse(in_order(' '.join(t.p),q),'quote words not in raw source in order')
   hist='';ref=v['source_ref'];key=''
  else:
   d,idk=FED[v['kind']];path=ROOT/'tasks'/d/('facilities.csv' if v['kind']=='frs' else 'establishments.csv')
   refuse(sha(path.read_bytes())==v['sha256'],'extract sha mismatch');r=next(x for x in read(path) if x[idk]==v['source_key'])
   b=[x for x in read(ROOT/'tasks'/d/'site_matches.csv') if x[idk]==v['source_key']][0]
   refuse(b['site_id']==sid and b['org_id']==s['org_id'] and b['match_strength']=='strong' and not b.get('alt_site_ids'),'binding drift')
   refuse(r['state']=='OH' and norm(r['city'])==norm(s['city']),'filing city differs')
   z=r.get('zip5',r.get('zip',''));nm=r.get('establishment_name',r.get('name',r.get('facility_name','')))
   refuse(q==f'{nm} | {r["street"]} | {r["city"]} | OH | {z}','quote is not the extract fields');refuse(not s['zip'] or s['zip'][:5]==z[:5],'zip differs')
   refuse(street==re.sub(r'[\s,]+'+re.escape(r['city'])+r'\.?$','',r['street'],flags=re.I),'street not the extract street')
   hist=' The filing witnesses its historical address, not current occupancy.';ref=v['source_ref'];key=v['source_key']
  pr=pn.get(sid)
  if pr:refuse(pr['status']=='applied','withdrawn site must not be applied');eid=pr['evidence_id']
  else:eid=f'EVD-{nxt:06d}';nxt+=1;refuse(int(eid[4:])<396000,'block exhausted')
  ev.append(dict(evidence_id=eid,record_table='sites',record_id=sid,claim_type='address',claim_detail=f"street_address {street}, {s['city']}, OH."+hist,source_class=v['source_class'],source_ref=ref,observed_date=TODAY,tier_effect=v['tier_effect'],created_by=CREATOR,notes=f"Quote (words in order{'; filing fields separated by |' if hist else ''}): {q}; source key {key or 'own page'}; SHA-256 {v['sha256']}; checked {TODAY}. Only street_address changed."))
 return verdicts,ev
def run(apply=False,backup=True):
 verdicts,ev=plan();sites=read(DATA/'sites_OH.csv');by={s['site_id']:s for s in sites};mine={e['evidence_id'] for e in ev};have={}
 for f in DATA.glob('evidence_*.csv'):
  for e in read(f):
   if e['evidence_id'] in mine:have[e['evidence_id']]=(f.name,e)
 new=[]
 for e in ev:
  h=have.get(e['evidence_id']);refuse(h is None or h==('evidence_sites_OH.csv',e),'evidence ID collision')
  if h is None:new.append(e)
 if apply:
  if backup:
   b=S/'streetnotes/backups';b.mkdir(parents=True,exist_ok=True)
   for n in ('sites_OH.csv','evidence_sites_OH.csv'):
    if not (b/n).exists():shutil.copyfile(DATA/n,b/n)
  for v in verdicts:
   if v['verdict']=='VERIFIED':by[v['site_id']]['street_address']=v['street']
  if new:append_sorted(DATA/'evidence_sites_OH.csv',new,'evidence_id')
  write(DATA/'sites_OH.csv',sites)
 print(json.dumps(dict(frame=len(verdicts),filled=len(ev),held=len(verdicts)-len(ev),evidence_rows=len(ev))))
if __name__=='__main__':run('--apply' in sys.argv)

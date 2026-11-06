"""Shared pieces for the S6 federal-dataset scout: Wilson interval, Atlas matcher, sample writer. Read-only on data/."""
import csv,math,random,re,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'scripts'));import atlas
SEED=20261106
PERSIST=Path('/Users/johnswanson/.bb/thread-storage/thr_9i2c6byhcz/2026-11-06-atlas/persist/source-scout-6')
VERDICTS={'VERIFIED','REJECT','STILL_UNCERTAIN','DUPLICATE_OF'}

def wilson(k,n):
 if not n:return None
 z=1.959963984540054;d=1+z*z/n;c=(k/n+z*z/(2*n))/d;h=z*math.sqrt(k/n*(1-k/n)/n+z*z/(4*n*n))/d
 return [round(max(0,c-h),6),round(min(1,c+h),6)]

class Atlas:
 """Registry-ID first (FRS/UEI/FDA_FEI), then AGENTS §3 steps 2-4 via atlas.dedupe (domain is not in these sources)."""
 def __init__(self):
  self.tables=atlas.load_tables(ROOT/'data')
  self.links={}
  for r in self.tables['registry_links'].rows:self.links.setdefault((r['registry'],r['registry_id'].strip()),[]).append(r)
  self.site_ids={r['site_id'] for r in self.tables['sites'].rows};self.org_ids={r['org_id'] for t in ('organizations','ecosystem') for r in self.tables[t].rows}
 def match(self,name,street=None,city=None,state=None,zip_=None,registry=None):
  """registry=(registry_name,id). Returns dict(atlas_ids, site_hits, org_hits, registry_hits, duplicate_of)."""
  reg=[]
  if registry:
   for l in self.links.get((registry[0],str(registry[1]).strip()),[]):reg.append(l['site_id'] or l['org_id'])
  d=atlas.dedupe(self.tables,name=name,street=street or None,city=city,state=state,zip_=zip_)
  site_hits={h['id'] for h in d['steps'][2]['hits']};org_hits={h['id'] for i in (1,3) for h in d['steps'][i]['hits']}
  # singleton exact street+locality site, or a registry link, is a duplicate; a held parent alone never is (site grain)
  dup=sorted(set(reg))[0] if len(set(reg))==1 else (next(iter(site_hits)) if len(site_hits)==1 else '')
  return dict(atlas_ids=';'.join(sorted(site_hits|org_hits|set(reg))),site_hits=';'.join(sorted(site_hits)),org_hits=';'.join(sorted(org_hits)),name_hits=';'.join(sorted({h['id'] for h in d['steps'][1]['hits']})),
   registry_hits=';'.join(sorted(set(reg))),duplicate_of=dup)

PHONE=re.compile(r'(?<![\d.])\(?\b\d{3}\)?[-. ]\d{3}[-. ]\d{4}\b');EMAIL=re.compile(r'[\w.+-]+@[\w-]+(?:\.[\w-]+)+')
def scrub(v):
 """AGENTS section 6: no phone numbers or e-mail addresses in any committed cell (a directory URL slug can carry one)."""
 return EMAIL.sub('[email]',PHONE.sub('[phone]',v)) if isinstance(v,str) else v

def write_csv(path,rows,fields=None):
 fields=fields or list(rows[0]);rows=[{k:scrub(v) for k,v in r.items()} for r in rows]
 with open(path,'w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=fields,lineterminator='\n',extrasaction='ignore');w.writeheader();w.writerows(rows)

def draw(frame,key,n=20):
 """Seeded uniform sample without replacement from the frame sorted by its unique key."""
 frame=sorted(frame,key=lambda r:r[key]);assert len({r[key] for r in frame})==len(frame),'frame keys must be unique'
 return random.Random(SEED).sample(frame,n)

"""Rebuild deterministic full-population request. Run from repository root."""
import csv,glob,re,json,hashlib,subprocess,io,pathlib,collections
OUT=pathlib.Path(__file__).parent
PIN='eceead3a5a59b7a51d13b2ad61d6070e4cfc9a05'
def sha(b): return hashlib.sha256(b).hexdigest()
def disposition(r):
 s=r['street_address'].strip()
 if r['latitude'] or r['longitude']: return 'HELD_EXISTING_COORDINATES'
 if not s: return 'HELD_NO_STREET_ADDRESS'
 if re.search(r'home address|residential address|private residence',r['notes'],re.I): return 'HELD_PRIVACY_REVIEW'
 if not re.match(r'^(?:\d+[A-Z]?\b|ONE\b|[NSEW]\d)',s,re.I): return 'HELD_PARTIAL_ADDRESS'
 if re.search(r'\b(?:PO BOX|P[.]?O[.]? BOX|KM |MILE |INTERSECTION| AT | & )',s,re.I): return 'HELD_PARTIAL_ADDRESS'
 if not (r['state'] and (r['city'] or re.fullmatch(r'\d{5}(?:-\d{4})?',r['zip']))): return 'HELD_INCOMPLETE_LOCALITY'
 return 'REQUESTED'
def build():
 rows=[]; hashes={}
 for p in sorted(glob.glob('data/*')):
  if pathlib.Path(p).is_file(): hashes[p]=sha(pathlib.Path(p).read_bytes())
 for p in sorted(glob.glob('data/sites_*.csv')):
  for r in csv.DictReader(open(p)):
   m=re.match(r'pass-(20|21|22|23|24|25) integrator',r['created_by'])
   if m:
    r.update(shard=p,creation_pass=m[1],cohort='tri_national_wave_note' if 'TRI national wave' in r['notes'] else 'other_pass20_25_creation',input_status=disposition(r),row_sha256=sha(json.dumps(r,sort_keys=True,separators=(',',':')).encode()))
    rows.append(r)
 rows.sort(key=lambda r:r['site_id'])
 assert len(rows)==1517 and len({r['site_id'] for r in rows})==1517
 # Independently prove created-in-pass population by pre-pass-20 ID set difference.
 pre=subprocess.check_output(['git','rev-parse','ec47751^'],text=True).strip()
 paths=subprocess.check_output(['git','ls-tree','-r','--name-only',pre],text=True).splitlines(); old=set()
 for p in paths:
  if re.match(r'data/sites_[A-Z]+\.csv$',p): old.update(r['site_id'] for r in csv.DictReader(io.StringIO(subprocess.check_output(['git','show',pre+':'+p],text=True))))
 now={r['site_id'] for p in glob.glob('data/sites_*.csv') for r in csv.DictReader(open(p))}
 assert now-old=={r['site_id'] for r in rows}
 cols=['site_id','shard','creation_pass','cohort','street_address','city','state','zip','county','site_type','input_status','latitude','longitude','geocode_precision','row_sha256']
 with open(OUT/'population.csv','w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=cols,extrasaction='ignore');w.writeheader();w.writerows(rows)
 with open(OUT/'request.csv','w',newline='') as f:
  w=csv.writer(f);w.writerows([r[k] for k in ['site_id','street_address','city','state','zip']] for r in rows if r['input_status']=='REQUESTED')
 manifest={'pin':PIN,'pre_pass20_commit':pre,'population':len(rows),'creation_pass_counts':dict(collections.Counter(r['creation_pass'] for r in rows)),'cohort_counts':dict(collections.Counter(r['cohort'] for r in rows)),'input_status_counts':dict(collections.Counter(r['input_status'] for r in rows)),'population_sha256':sha((OUT/'population.csv').read_bytes()),'request_sha256':sha((OUT/'request.csv').read_bytes()),'canonical_sha256':hashes,'endpoint':'https://geocoding.geo.census.gov/geocoder/geographies/addressbatch','benchmark':'Public_AR_Current','benchmark_id':'4','vintage':'Current_Current','vintage_id':'4','retrieval_date':'2026-10-30','coordinates_use':'REFERENCE_ONLY; not evidence, verification, or county source'}
 (OUT/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');print(json.dumps({k:v for k,v in manifest.items() if 'counts' in k},indent=2))
if __name__=='__main__':build()

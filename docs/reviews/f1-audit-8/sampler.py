import csv,glob,re,subprocess,json,io,collections,hashlib
from pathlib import Path
import argparse,random,math
parser=argparse.ArgumentParser()
parser.add_argument('--repo',default='.')
parser.add_argument('--wave-map',help='CSV: record_id,wave_class (P0–P4 or explicit NOT_TRI)')
parser.add_argument('--output-dir',default='/tmp/f1-sampling')
a=parser.parse_args()
ROOT=Path(a.repo).resolve()
OUT=Path(a.output_dir);OUT.mkdir(parents=True,exist_ok=True)
PIN='eceead3a5a59b7a51d13b2ad61d6070e4cfc9a05'
def git(*a):return subprocess.check_output(['git','-C',str(ROOT),*a],text=True)
def records(ref):
 out={}
 for f in git('ls-tree','-r','--name-only',ref,'data').splitlines():
  if re.fullmatch(r'data/(organizations|sites)_[A-Z]+\.csv',f):
   for r in csv.DictReader(io.StringIO(git('show',ref+':'+f))):
    table='sites' if '/sites_' in f else 'organizations'; rid=r['site_id' if table=='sites' else 'org_id'];out[rid]={'table':table,'shard':f,'row':r}
 return out
allrows=records(PIN)
logs=git('log','--reverse','--format=%H %s',PIN).splitlines()
ends={}
for line in logs:
 sha,msg=line.split(' ',1);m=re.match(r'Pass (2[0-5]) body (\d+) of (\d+)',msg)
 if m and m[2]==m[3]:ends[int(m[1])]=sha
assert set(ends)==set(range(20,26)),'Missing complete pass-end snapshot'
first=next(l.split()[0] for l in logs if re.search(r'Pass 20 body 1 of ',l)); previous=records(first+'^')
sitecounts=collections.Counter(x['row']['org_id'] for x in allrows.values() if x['table']=='sites')
pop=[]
for p,sha in sorted(ends.items()):
 current=records(sha)
 for rid in sorted(current.keys()-previous.keys()):
  x=current[rid];r=x['row'];pop.append({'record_id':rid,'table':x['table'],'creation_pass':p,'creation_sha':sha,'creation_tier':r['verification_tier'],'wave_class':None,'single_facility_organization':x['table']=='organizations' and sitecounts[rid]==1,'row_at_creation':r,'row_at_pin':allrows[rid]['row']})
 previous=current
# This program parses creation notes only for storage in the sealed comparison frame.
# It never parses data/evidence.csv; verifier-facing output has an explicit allowlist.
meta=[{k:v for k,v in x.items() if k not in ('row_at_creation','row_at_pin')} for x in pop]
files={f:hashlib.sha256(git('show',PIN+':'+f).encode()).hexdigest() for f in git('ls-tree','-r','--name-only',PIN,'data').splitlines()}
frame={'pin':PIN,'population_definition':'All organization/site IDs first introduced in complete integration passes 20–25, ID-set difference from prior complete pass. Includes non-TRI SC/Q01/Q02 creations in pass20. No status filter.','pass_end_shas':ends,'population':meta,'file_sha256':files}
(OUT/'population_metadata_sealed.json').write_text(json.dumps(frame,indent=2)+'\n')
(OUT/'comparison_records_sealed.json').write_text(json.dumps(pop,indent=2)+'\n')
print('Population:',len(pop),'records. Creation tiers and source notes are withheld from verifier manifest.')
if not a.wave_map:
 print('BLOCKED: P0–P4 wave map is absent. No draw performed; no identities released.');raise SystemExit(2)
wm={}
for r in csv.DictReader(open(a.wave_map)):
 assert r['record_id'] not in wm,'Duplicate mapping ID'
 assert r['wave_class'] in ['P0','P1','P2','P3','P4','NOT_TRI'],'Unrecognized wave class'
 wm[r['record_id']]=r['wave_class']
missing=[x['record_id'] for x in pop if x['record_id'] not in wm]
if missing:
 print('BLOCKED:',len(missing),'population records lack explicit wave class. No draw performed.');raise SystemExit(2)
# Explicit non-TRI rows stay in full frame but never enter the TRI audit draw.
pop=[x for x in pop if wm[x['record_id']]!='NOT_TRI']
assert pop,'Empty TRI population'
# Refining tier × wave by record grain and single-facility org makes the
# requested risk oversampling explicit and keeps within-stratum inclusion equal.
strata=collections.defaultdict(list)
for x in pop:
 x['wave_class']=wm[x['record_id']]
 key=(x['creation_tier'],x['wave_class'],x['table'],x['single_facility_organization'])
 strata[key].append(x)
keys=sorted(strata)
N=65
if len(keys)>N:raise SystemExit('BLOCKED: more than65 nonempty refined strata; design must be reviewed before draw.')
allocation={k:1 for k in keys}
# One per nonempty stratum, then D'Hondt-style deterministic allocation to
# weighted population sizes. C gets 3× weight; P4 single-facility orgs 2×.
weight={k:len(strata[k])*(3 if k[0]=='C' else 1)*(2 if k[1]=='P4' and k[3] else 1) for k in keys}
while sum(allocation.values())<N:
 eligible=[k for k in keys if allocation[k]<len(strata[k])]
 if not eligible:break
 k=max(eligible,key=lambda k:(weight[k]/(allocation[k]+1),tuple(str(v) for v in k)))
 allocation[k]+=1
seed='polymer-atlas-audit8-eceead3-2026-10-30-v1'
rng=random.Random(seed);selected=[]
for k in keys:
 for x in rng.sample(sorted(strata[k],key=lambda x:x['record_id']),allocation[k]):
  selected.append({**x,'stratum':list(k),'inclusion_probability':allocation[k]/len(strata[k])})
rng.shuffle(selected)
identity=[]
for x in selected:
 r=x['row_at_pin'];org=allrows[r['org_id']]['row'];site=x['table']=='sites'
 identity.append({'record_id':x['record_id'],'table':x['table'],'name':r['site_name'] if site else r['legal_name'],'street_address':r.get('street_address','') if site else '', 'city':r['city'] if site else r['hq_city'],'state':r['state'] if site else r['hq_state'],'zip':r.get('zip','') if site else '', 'associated_org_name':org['legal_name'],'website':org.get('website','')})
(OUT/'identity_only.json').write_text(json.dumps(identity,indent=2)+'\n')
(OUT/'sampling_sealed.json').write_text(json.dumps({'seed':seed,'pin':PIN,'wave_map_sha256':hashlib.sha256(Path(a.wave_map).read_bytes()).hexdigest(),'strata':[{'key':k,'population_n':len(strata[k]),'sample_n':allocation[k]} for k in keys],'sample':selected},indent=2)+'\n')
print('Draw complete:',len(identity),'records. Keep sampling_sealed.json and comparison_records_sealed.json hidden until all blind verdicts are frozen.')

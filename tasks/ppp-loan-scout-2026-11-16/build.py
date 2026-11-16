"""Rebuild packet frames from privacy-filtered SBA cache and pinned Atlas shards."""
import csv,json,random,sys,hashlib,importlib.util
from pathlib import Path
from fetch import P,safe
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'scripts'));import atlas
from regions import PIC18
D=Path(__file__).parent
spec=importlib.util.spec_from_file_location('common',ROOT/'tasks/source-scout-6-2026-11-06/common.py');common=importlib.util.module_from_spec(spec);spec.loader.exec_module(common)
def read(p):return list(csv.DictReader(p.open()))
def write(p,rows,fields):
 # Unverified addresses stay in the private cache pending physical-business checks.
 p=P/p.name
 with p.open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=fields,lineterminator='\n');w.writeheader();w.writerows(rows)
def main():
 (D/'atlas_inputs.json').write_text(json.dumps({str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for pattern in ('organizations_*.csv','sites_*.csv') for p in (ROOT/'data').glob(pattern)},indent=2)+'\n')
 orgs=[r for p in (ROOT/'data').glob('organizations_*.csv') for r in read(p)]
 sites=[r for p in (ROOT/'data').glob('sites_*.csv') for r in read(p)]
 onames={}
 for o in orgs:
  for _,n in atlas.org_name_fields(o):onames.setdefault(atlas.name_key(n),set()).add(o['org_id'])
 snames={}
 for s in sites:snames.setdefault(atlas.site_name_key(s['site_name'],s['city']),set()).add(s['org_id'])
 streets={}
 for s in sites:
  if s['street_address']:streets.setdefault((str(atlas.street_key(s['street_address'])),s['city'].lower()),set()).add(s['org_id'])
 loans=[r for p in P.glob('*.filtered.csv') for r in read(p)]
 assert len({r['LoanNumber'] for r in loans})==len(loans)
 frame=[s for s in sites if s['state']=='OH' and s['county'] in PIC18 and s['operating_status']=='active']
 matches=[];leads=[]
 for r in loans:
  assert safe(r)
  ids=onames.get(atlas.name_key(r['BorrowerName']),set())|snames.get(atlas.name_key(r['BorrowerName']),set())
  ids|=streets.get((str(atlas.street_key(r['BorrowerAddress'])),r['BorrowerCity'].lower()),set()) if r['BorrowerAddress'] else set()
  if not ids and r['ProjectCountyName'].title() in PIC18 and r['NAICSCode'].startswith(('325','326')):leads.append(r)
  for s in frame:
   if s['org_id'] in ids and s['city'].lower()==r['BorrowerCity'].lower():
    matches.append(dict(site_id=s['site_id'],org_id=s['org_id'],site_name=s['site_name'],atlas_street=s['street_address'],atlas_band=s['employee_band_site'],**r))
 fields=['site_id','org_id','site_name','atlas_street','atlas_band']+list(loans[0])
 write(D/'matches.csv',matches,fields);write(D/'leads.csv',leads,list(loans[0]))
 frames={'address':[s for s in frame if not s['street_address']], 'jobs':[s for s in frame if not s['employee_band_site']]}
 metrics=dict(active_pic18_sites=len(frame),indexed_loans=len(loans),unmatched_polymer_loans=len(leads),unmatched_borrower_names=len({atlas.name_key(r['BorrowerName']) for r in leads}),matched_site_rows=len({r['site_id'] for r in matches}))
 for label,ss in frames.items():
  eligible=[r for r in matches if r['site_id'] in {s['site_id'] for s in ss} and r['BorrowerAddress' if label=='address' else 'JobsReported']]
  ids=sorted({r['site_id'] for r in eligible});sample=random.Random(20261116).sample(ids,min(20,len(ids)))
  write(D/(label+'_sample.csv'),[dict(r,verdict='STILL_UNCERTAIN',settling_fact='Independent plant address and site-grain employee source at the loan date') for r in eligible if r['site_id'] in sample],fields+['verdict','settling_fact'])
  metrics[label]=dict(denominator=len(ss),candidate_sites=len(ids),sample_sites=len(sample),yield_rate=len(ids)/len(ss),wilson95=common.wilson(len(ids),len(ss)))
 paired=[r for r in matches if r['atlas_band'] and r['JobsReported']]
 ids=sorted({r['site_id'] for r in paired});sample=random.Random(20261116).sample(ids,min(20,len(ids)))
 write(D/'band_comparison.csv',[r for r in paired if r['site_id'] in sample],fields)
 metrics['band_comparison_sites']=len(sample)
 (D/'metrics.json').write_text(json.dumps(metrics,indent=2)+'\n')
if __name__=='__main__':main()

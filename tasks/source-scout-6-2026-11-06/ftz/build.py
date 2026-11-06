"""ITA OFIS FTZ Production Database approvals -> company frame (production authority for a finished PRODUCT in HTSUS ch.39 plastics or ch.40 rubber)
and a seeded 20-company sample matched to the Atlas by name. The database carries no addresses.
Usage: python3 -I build.py   (reads PERSIST/ftz/approvals_<heading>.json written by fetch_approvals.py)"""
import json,re,sys,hashlib,collections
from pathlib import Path
HERE=Path(__file__).resolve().parent;sys.path.insert(0,str(HERE.parent));import common
D=common.PERSIST/'ftz'
def poly_product(part):
 """A finished product under plastics (ch.39) or rubber (ch.40). A ch.39/40 COMPONENT only means plastic is an input to something else."""
 return part['PartType']=='Product' and part['HTSUS'][:2] in ('39','40')
def main():
 assert poly_product({'PartType':'Product','HTSUS':'3920.10'}) and poly_product({'PartType':'Product','HTSUS':'4011.10'})
 assert not poly_product({'PartType':'Component','HTSUS':'3920.10'}) and not poly_product({'PartType':'Product','HTSUS':'8414.59'}) and not poly_product({'PartType':'Product','HTSUS':'7039.10'})
 approvals={};files=sorted(D.glob('approvals_*.json'));assert len(files)==43,len(files)
 for f in files:
  for a in json.loads(f.read_bytes())['data']:approvals[(a['CaseDocketNumber'],a['BoardOrderNumber'],a['Company'])]=a
 comp=collections.defaultdict(lambda:dict(approvals=set(),dates=set(),codes=set()))
 for (dk,bo,c),a in approvals.items():
  ps=[p['HTSUS'] for p in a['ManufacturingCompanyParts'] if poly_product(p)]
  if ps:
   d=comp[c.strip()];d['approvals'].add(dk);d['dates'].add(a['ApprovalDate'][:10]);d['codes'].update(ps)
 frame=[dict(company=c,approvals=len(v['approvals']),dockets=';'.join(sorted(v['approvals'])),latest_approval=max(v['dates']),earliest_approval=min(v['dates']),polymer_product_hts=';'.join(sorted(v['codes']))) for c,v in sorted(comp.items())]
 common.write_csv(HERE/'frame.csv',frame)
 A=common.Atlas();out=[]
 for r in common.draw(frame,'company'):out.append(dict(r,**A.match(r['company'])))
 common.write_csv(HERE/'sample_pre.csv',out)
 stats=dict(headings_queried=len(files),approval_records_returned=len(approvals),distinct_companies_any_part=len({k[2].strip() for k in approvals}),
  approvals_with_poly_product=sum(any(poly_product(p) for p in a['ManufacturingCompanyParts']) for a in approvals.values()),frame_companies=len(frame),
  input_sha256={f.name:hashlib.sha256(f.read_bytes()).hexdigest() for f in files})
 (HERE/'counts.json').write_text(json.dumps(stats,indent=1)+'\n');print({k:v for k,v in stats.items() if k!='input_sha256'})
if __name__=='__main__':main()

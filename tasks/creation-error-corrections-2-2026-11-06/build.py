"""Five-site bounded corrections; validate every preimage and witness before canonical writes."""
import argparse,csv,hashlib,json,sys
from collections import defaultdict,Counter
from pathlib import Path
H=Path(__file__).resolve().parent;ROOT=H.parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from shard_io import append_sorted
from fetch import read,write,on_page
DATE='2026-11-06';BY='codex atlas-L11-creation-corrections-2'
KEYS=['CANTEX_DISTRIBUTION','VALMET_SERVICE','MIDLAND_MACHINING','MIDLAND_RETAIL']
SITES=['SITE-016017','SITE-016401','SITE-016410','SITE-016115','SITE-016514']
CHANGES={'SITE-016017':'warehouse_distribution','SITE-016401':'service_repair'}
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--apply',action='store_true');ap.add_argument('--data-dir',type=Path,default=ROOT/'data');a=ap.parse_args();data=a.data_dir
 inputs=read(H/'input.csv');vs=read(H/'verdicts.csv');raw=read(H/'rawcheck.csv')
 assert len(inputs)==len(vs)==len({r['site_id'] for r in vs})==5 and {r['site_id'] for r in inputs}=={r['site_id'] for r in vs}==set(SITES)
 assert Counter(r['verdict'] for r in vs)=={'VERIFIED':2,'STILL_UNCERTAIN':3}
 assert [r['key'] for r in raw]==KEYS and [r['site_id'] for r in raw]==['SITE-016017','SITE-016401','SITE-016410','SITE-016410']
 for r in raw:
  p=ROOT/r['page'];assert p.exists(),'Required public witness missing; run python3 tasks/creation-error-corrections-2-2026-11-06/acquire.py'
  assert hashlib.sha256(p.read_bytes()).hexdigest()==r['page_sha256'],'source hash mismatch'
  assert on_page(r['quote'],p) and on_page(r['binding_quote'],p),('quote/binding absent',r['key'])
  assert all(k not in r['quote'] for k in ['ITA:','EVD-','ORG-'])
 allsites=[(p.name,r) for p in data.glob('sites_*.csv') for r in read(p)];sites={r['site_id']:(n,r) for n,r in allsites};assert len(sites)==len(allsites)
 evs=[(p.name,r) for p in data.glob('evidence_*.csv') for r in read(p)];ev={r['evidence_id']:(n,r) for n,r in evs};assert len(ev)==len(evs),'duplicate global EVD'
 notes={
 'SITE-016017':'Own CANTEX About page places202ProgressRoad under DistributionCenters and101GandyRoad under PipeExtrusionFacilities. Correct physicaltype warehouse_distribution only; Ring1/scope ownerHOLD underB14/R9,no parentprocessinheritance. Keep filedNAICS/status/tier/address;101Gandy is a separate lead,not a relocation/addressreplacement.',
 'SITE-016401':'Own exact1615Matthews NeenahServiceCenter offers roll grinding,re-covering,maintenance pluspolyurethane/composite/rubbercovers. Physicalfunction service_repair; Ring1/scope ownerHOLD given possibleon-sitepolymercovertransformation. This is NOT a no-manufacture finding; no ring/code/status/tier change.',
 'SITE-016410':'Mixedfunction: own2026-07-10article explicitly saysDePere5-axisCNCrouters machinecomplexplasticgeometries; separateownretailpage identifies2151AmericanBoulevard asRetailStore. Plasticmanufacturingactivity is real,notdisprovedbyretail. Dominantphysicalfunction remainsownerHOLD; retain manufacturing_plant/ring/code/status/tier without stronger assertion.'}
 edits=defaultdict(dict)
 for b in inputs:
  sid=b['site_id'];name,now=sites[sid];old={k:b[k] for k in now}
  if sid not in notes:assert now==old,('held preimage changed',sid);continue
  new=old.copy()
  if sid in CHANGES:new['site_type']=CHANGES[sid]
  urls=list(dict.fromkeys(r['source_url'] for r in raw if r['site_id']==sid));new['sources']=old['sources']+';'+';'.join(urls);new['notes']=old['notes']+' | '+DATE+': '+notes[sid];new['last_verified']=DATE
  assert now in [old,new],('stale site preimage',sid);edits[name][sid]=new
 # No street, status, code, tier, ring or operator motion is authorized in this pass.
 out=defaultdict(list);alloc=[]
 for idx,r in enumerate(raw):
  shard='evidence_'+sites[r['site_id']][0]
  e=dict(evidence_id=f'EVD-{278600+idx:06d}',record_table='sites',record_id=r['site_id'],claim_type='scope',claim_detail='"'+r['quote']+'"',source_class='own_site',source_ref=r['source_url'],observed_date=DATE,tier_effect='supports_C',created_by=BY,notes=f"Raw fetched {r['fetched_at']}; source date {r['source_date'] or 'undated/livepage'}. "+r['note'])
  out[shard].append(e);alloc.append(dict(key=r['key'],evidence_id=e['evidence_id'],site_id=r['site_id'],shard=shard))
 log=read(data/'inclusion_log.csv');pendinglog=[]
 for sid,label,question in [('SITE-016017','CANTEX Auburndale Distribution Center','Producer-owned distribution center ring/scope; recommend owner consider Ring3 distribution, alternative exclude or retain unresolved pendinglocalprocess.'),('SITE-016401','Valmet Neenah Service Center','Roll-cover servicing with possible polymertransformation: recommend owner determine dominantfunction/process Ring3 service versus Ring1 transformation; alternative hold until process split verified.'),('SITE-016410','Midland De Pere mixed fabrication/retail','RealplasticCNC plusretail atheldsite: recommend owner retain Ring1 only if fabricationdominant verified; alternative mixedphysicalfunctionrule or hold pendingfunctionalshare.')]:
  row=dict(date=DATE,entity=label+' '+sid,decision='HOLD ring/scope or dominant function — owner battery pending',rule_cited='SCHEMA §1/B14/R9/§4.5 dominant function; AGENTS §2 rule9',researcher=BY,notes=question+' Source '+next(r['source_url'] for r in raw if r['site_id']==sid))
  prior=[r for r in log if r['entity']==row['entity'] and r['researcher']==BY];assert not prior or prior==[row],'seam preimage changed'
  if not prior:pendinglog.append(row)
 pending={}
 for name,rows in out.items():
  header=list(read(data/name)[0]);pending[name]=[]
  for r in rows:
   if r['evidence_id'] in ev:assert ev[r['evidence_id']]==(name,{k:r.get(k,'') for k in header}),('global EVD collision',r['evidence_id'])
   else:pending[name].append(r)
 if a.apply:
  for name,byid in edits.items():
   old=read(data/name);new=[byid.get(r['site_id'],r) for r in old]
   if old!=new:write(data/name,new,list(old[0]))
  for name,rows in pending.items():
   if rows:append_sorted(data/name,rows,'evidence_id')
  if pendinglog:
   with (data/'inclusion_log.csv').open('a',newline='') as f:csv.DictWriter(f,fieldnames=list(log[0]),lineterminator='\n').writerows(pendinglog)
 write(H/'allocations.csv',alloc,['key','evidence_id','site_id','shard'])
 print(json.dumps(dict(frame=5,verdicts=dict(Counter(r['verdict'] for r in vs)),site_rows_annotated=3,physical_type_corrections=2,evidence=4,seams=3,pending_evidence=sum(map(len,pending.values())),pending_seams=len(pendinglog))))
if __name__=='__main__':main()

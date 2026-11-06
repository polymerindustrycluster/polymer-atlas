"""Named full capped-frame/source/data/replay check, with actual before-write defect injections."""
import csv,hashlib,importlib.util,io,json,shutil,subprocess,sys,tempfile
from collections import Counter
from pathlib import Path
H=Path(__file__).resolve().parent;ROOT=H.parents[1];sys.path.insert(0,str(H));sys.path.insert(0,str(ROOT/'scripts'))
from prep import read,write
from site_corpus import on_page
BASE=json.loads((H/'baseline.json').read_text())['base']
def old(name):return list(csv.DictReader(io.StringIO(subprocess.check_output(['git','show',BASE+':'+name],cwd=ROOT,text=True))))
inputs=read(H/'input.csv');eligible=read(H/'eligible_frame.csv');vs=read(H/'verdicts.csv');sel=read(H/'selected.csv');alloc=read(H/'allocations.csv');retired={r['evidence_id'] for r in read(H/'retired_ids.csv')}
assert len(inputs)==40 and inputs==eligible[:40] and len(eligible)==161 and len({r['site_id'] for r in eligible})==161
created=read(H/'creation_frame.csv');assert len(created)==len({r['site_id'] for r in created})==len({r['cluster_id'] for r in created})==220
assert Counter(r['state'] for r in created)=={'MN':40,'NY':25,'NJ':23,'NC':25,'TN':23,'KY':25,'VA':16,'MA':43}
assert all(r['created_by']=='claude-code '+r['state'].lower()+'-strong-wave-2026-11-04' for r in created)
assert len(read(H/'creation_frame.csv'))==220 and Counter(r['state'] for r in inputs)=={'MN':25,'NY':15}
assert len(vs)==len({r['site_id'] for r in vs})==40 and {r['site_id'] for r in vs}=={r['site_id'] for r in inputs}
assert Counter(r['verdict'] for r in vs)=={'VERIFIED':len(sel),'STILL_UNCERTAIN':40-len(sel)}
assert len(alloc)==7*len(sel) and not(retired&{r['evidence_id'] for r in alloc})
assert len({r['evidence_id'] for r in alloc})==len(alloc)
known=json.loads((H/'known_answers.json').read_text());assert len(known)==3 and all(r['positive'] and not r['negative'] for r in known)
bulk=json.loads((H/'bulk_known_answers.json').read_text());assert len(bulk)==3 and all(r['result']=='PASS' for r in bulk)
county=json.loads((H/'county_receipts.json').read_text());assert all(next(r for r in county if r['site_id']==sid)['status']=='PASS' for sid in ['SITE-011028','SITE-011011','SITE-011151'])
positive=0
for r in sel:
 text=(ROOT/r['page']).read_text();assert hashlib.sha256(text.encode()).hexdigest()==r['page_sha256']
 for k in ['quote','activity_quote','city_quote','binding_quote','context_quote']:
  if r[k]:assert on_page(r[k],text);positive+=1
 assert not on_page(r['quote']+' fabricated atlas zebra 7731',text)
expected={'data/sites_MN.csv','data/sites_NY.csv','data/evidence_sites_MN.csv','data/evidence_sites_NY.csv'}
changed=set(subprocess.check_output(['git','diff',BASE,'--name-only','--','data'],cwd=ROOT,text=True).splitlines());assert changed==expected,changed
ids={r['site_id'] for r in sel};newids={r['evidence_id'] for r in alloc};evnew=[];counts={}
for name in changed:
 before=old(name);now=read(ROOT/name);key='site_id' if '/sites_' in name else 'evidence_id';prior={r[key]:r for r in before};current={r[key]:r for r in now};assert len(current)==len(now) and prior.keys()<=current.keys()
 if key=='site_id':
  assert len(before)==len(now)
  for rid,b in prior.items():
   n=current[rid]
   if rid not in ids:assert n==b
   else:
    allowed={'verification_tier','sources','notes','last_verified'};assert {k:v for k,v in b.items() if k not in allowed}=={k:v for k,v in n.items() if k not in allowed}
    assert b['verification_tier']=='C' and n['verification_tier']=='B' and n['operating_status']=='active'
  strict=lambda r:r['country']=='US' and r['verification_tier'] in 'ABC' and r['operating_status'] in ['active','unknown'] and r['naics_primary'].startswith('326')
  counts[name[-6:-4]]=dict(before=sum(map(strict,before)),after=sum(map(strict,now)))
 else:
  assert all(current[rid]==r for rid,r in prior.items());evnew += [r for rid,r in current.items() if rid not in prior]
assert {r['evidence_id'] for r in evnew}==newids and all(r['tier_effect']=='supports_B' for r in evnew)
for sid in ids:assert Counter(r['claim_type'] for r in evnew if r['record_id']==sid)==dict.fromkeys(['existence','address','code','parent','scope','activity','liveness'],1)
all_ev=[r for p in (ROOT/'data').glob('evidence_*.csv') for r in read(p)];assert len(all_ev)==len({r['evidence_id'] for r in all_ev}) and not(retired&{r['evidence_id'] for r in all_ev})
for p in (ROOT/'data').glob('*.csv'):
 if 'data/'+p.name not in expected:assert p.read_bytes()==subprocess.check_output(['git','show',BASE+':data/'+p.name],cwd=ROOT)
paths=list((ROOT/'data').glob('*.csv'));hashes=lambda:{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
first=hashes();subprocess.run([sys.executable,str(H/'build.py'),'--apply'],check=True);assert hashes()==first
spec=importlib.util.spec_from_file_location('quality_builder',H/'build.py');mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
with tempfile.TemporaryDirectory() as td:
 data=Path(td)/'data';task=Path(td)/'task';shutil.copytree(ROOT/'data',data);shutil.copytree(H,task);mod.H=task
 def refuse():
  hs=lambda:{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in data.glob('*.csv')};b=hs();sys.argv=['build.py','--apply','--data-dir',str(data)]
  try:mod.main()
  except (AssertionError,KeyError):pass
  else:raise AssertionError('injected defect escaped')
  assert hs()==b
 for field,value in [('quote','fabricated atlas zebra 7731'),('binding_quote','wrong street city 7731'),('page_sha256','0'*64),('source_url','https://unrelated.example/plant')]:
  rows=read(task/'selected.csv');rows[-1][field]=value;write(task/'selected.csv',rows,list(rows[0]));refuse();shutil.copy2(H/'selected.csv',task/'selected.csv')
 rows=read(task/'verdicts.csv');write(task/'verdicts.csv',rows[:-1],list(rows[0]));refuse();shutil.copy2(H/'verdicts.csv',task/'verdicts.csv')
 rows=read(data/'sites_NY.csv');target=sel[-1]['site_id'];next(r for r in rows if r['site_id']==target)['street_address']='stale street 7731';write(data/'sites_NY.csv',rows,list(rows[0]));refuse();shutil.copy2(ROOT/'data/sites_NY.csv',data/'sites_NY.csv')
 rows=read(data/'evidence_sites_NY.csv');target=alloc[-1]['evidence_id'];moved=next(r for r in rows if r['evidence_id']==target);write(data/'evidence_sites_NY.csv',[r for r in rows if r['evidence_id']!=target],list(rows[0]));rows=read(data/'evidence_sites_DE.csv');rows.append(moved);write(data/'evidence_sites_DE.csv',rows,list(rows[0]));refuse()
result=dict(frame=40,original_eligible=161,unworked=121,promotions=len(sel),holds=40-len(sel),evidence=len(alloc),government=sum(r['source_class']=='government_filing' for r in evnew),own=sum(r['source_class']=='own_site' for r in evnew),raw_pages=len(sel),positive_quotes=positive,known_answers=3,county_known_answers=3,all_seven_claims=True,replay_byte_identical=True,no_write_faults=7,retired_ids=len(retired),strict_counts=counts)
(H/'check_results.json').write_text(json.dumps(result,indent=2)+'\n');print('PASS',json.dumps(result))

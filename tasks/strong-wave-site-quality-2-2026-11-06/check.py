"""Named full frame/source/data/replay check for rows 41-80, with actual before-write defect injections."""
import csv,hashlib,importlib.util,io,json,re,shutil,subprocess,sys,tempfile
from collections import Counter
from pathlib import Path
H=Path(__file__).resolve().parent;ROOT=H.parents[1];sys.path.insert(0,str(H));sys.path.insert(0,str(ROOT/'scripts'))
from prep import read,write
from site_corpus import on_page
R1=ROOT/'tasks/strong-wave-site-quality-2026-11-06'
BASE=json.loads((H/'baseline.json').read_text())['base']
def old(name):return list(csv.DictReader(io.StringIO(subprocess.check_output(['git','show',BASE+':'+name],cwd=ROOT,text=True))))
inputs=read(H/'input.csv');eligible=read(R1/'eligible_frame.csv');vs=read(H/'verdicts.csv');sel=read(H/'selected.csv');alloc=read(H/'allocations.csv');slots=read(H/'id_slots.csv');retired={r['evidence_id'] for r in read(H/'retired_ids.csv')}
# Frame: rows 41-80 of round 1's frozen 161-site frame, in order; rows 1-40 are round 1's (#237) and are untouched here.
assert len(eligible)==len({r['site_id'] for r in eligible})==161 and inputs==eligible[40:80] and len(inputs)==40
assert Counter(r['state'] for r in inputs)=={'NY':8,'NJ':23,'NC':9} and all(r['verification_tier']=='C' and r['operating_status']=='active' for r in inputs)
r1=read(R1/'verdicts.csv');assert not({r['site_id'] for r in r1}&{r['site_id'] for r in inputs}),'frame overlaps round 1'
assert len(vs)==len({r['site_id'] for r in vs})==40 and {r['site_id'] for r in vs}=={r['site_id'] for r in inputs}
assert Counter(r['verdict'] for r in vs)=={'VERIFIED':len(sel),'STILL_UNCERTAIN':40-len(sel)} and all(r['reason'].strip() for r in vs if r['verdict']=='STILL_UNCERTAIN')
assert {r['site_id'] for r in sel}=={r['site_id'] for r in vs if r['verdict']=='VERIFIED'} and len(sel)==9
mp=next(r for r in vs if r['site_id']=='SITE-011453');assert mp['verdict']=='STILL_UNCERTAIN' and 'Not an availability block' in mp['reason'] and not re.search(r'ROBOTS_BLOCKED|FETCH_FAILED',mp['reason']),'011453 hold must carry the corrected reason'
fu=json.loads((H/'modern_polymers_followup.json').read_text());assert all(p['http_default_curl_agent']==200 and p['quotes_in_order'] for p in fu['pages']) and fu['census_address_check']['status']=='PASS'
# Evidence IDs: only inside EVD-330000..330999, seven per promotion, immutable slots, no retired reuse.
assert len(alloc)==7*len(sel) and len({r['evidence_id'] for r in alloc})==len(alloc) and not(retired&{r['evidence_id'] for r in alloc})
assert all(330000<=int(r['evidence_id'][4:])<=330999 for r in alloc) and sorted(int(r['slot']) for r in slots)==list(range(len(sel)))
# Known answers before any fetcher/matcher is trusted: own-site (3), bulk ECHO (3), county/address (3).
known=json.loads((H/'known_answers.json').read_text());assert len(known)==3 and all(r['positive'] and not r['negative'] for r in known)
bulk=json.loads((H/'bulk_known_answers.json').read_text());assert len(bulk)==3 and all(r['result']=='PASS' for r in bulk)
cal=json.loads((H/'county_calibration.json').read_text());assert len(cal)==3 and all(r['status']=='PASS' for r in cal)
county={r['site_id']:r for r in json.loads((H/'county_receipts.json').read_text())};assert set(county)=={r['site_id'] for r in sel} and all(r['status']=='PASS' for r in county.values())
positive=0
for r in sel:
 text=Path(r['page']).read_text();assert hashlib.sha256(text.encode()).hexdigest()==r['page_sha256']
 for k in ['quote','activity_quote','city_quote','binding_quote','context_quote']:
  if r[k]:assert on_page(r[k],text);positive+=1
 assert not on_page(r['quote']+' fabricated atlas zebra 7731',text)
 assert not on_page('wrong street city 7731',text)
created={r['state'] for r in inputs if r['site_id'] in {s['site_id'] for s in sel}}
expected={f'data/sites_{s}.csv' for s in created}|{f'data/evidence_sites_{s}.csv' for s in created}
changed=set(subprocess.check_output(['git','diff',BASE,'--name-only','--','data'],cwd=ROOT,text=True).splitlines());assert changed==expected,changed
ids={r['site_id'] for r in sel};newids={r['evidence_id'] for r in alloc};evnew=[];counts={}
for name in sorted(changed):
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
# 07:20 own_site rule: an own_site row states only what the cited page says (no registrants, aliases, registry or record ids).
own=[r for r in evnew if r['source_class']=='own_site'];assert len(own)==3*len(sel)
assert not [r for r in own if re.search(r'registrant|alias|FRS|ITA|OSHA|ECHO|SITE-|ORG-|EVD-',r['claim_detail'])]
page={r['site_id']:Path(r['page']).read_text() for r in sel}
for r in own:
 for part in re.findall(r'"([^"]+)"',r['claim_detail']):assert on_page(part,page[r['record_id']]),('own_site detail not page words',r['evidence_id'])
all_ev=[r for p in (ROOT/'data').glob('evidence_*.csv') for r in read(p)];assert len(all_ev)==len({r['evidence_id'] for r in all_ev}) and not(retired&{r['evidence_id'] for r in all_ev})
for p in (ROOT/'data').glob('*.csv'):
 if 'data/'+p.name not in expected:assert p.read_bytes()==subprocess.check_output(['git','show',BASE+':data/'+p.name],cwd=ROOT)
paths=list((ROOT/'data').glob('*.csv'));hashes=lambda:{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
first=hashes();subprocess.run([sys.executable,str(H/'build.py'),'--apply'],check=True,stdout=subprocess.DEVNULL);assert hashes()==first
spec=importlib.util.spec_from_file_location('quality_builder',H/'build.py');mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
last=sel[-1]['site_id'];st=next(r['state'] for r in inputs if r['site_id']==last)
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
 rows=read(data/f'sites_{st}.csv');next(r for r in rows if r['site_id']==last)['street_address']='stale street 7731';write(data/f'sites_{st}.csv',rows,list(rows[0]));refuse();shutil.copy2(ROOT/f'data/sites_{st}.csv',data/f'sites_{st}.csv')
 shard=alloc[-1]['shard'];rows=read(data/shard);moved=next(r for r in rows if r['evidence_id']==alloc[-1]['evidence_id']);write(data/shard,[r for r in rows if r['evidence_id']!=alloc[-1]['evidence_id']],list(rows[0]))
 other='evidence_sites_DE.csv';rows=read(data/other);rows.append(moved);write(data/other,rows,list(rows[0]));refuse()
result=dict(frame='41-80 of 161',original_eligible=161,frame_sites=40,promotions=len(sel),holds=40-len(sel),evidence=len(alloc),government=sum(r['source_class']=='government_filing' for r in evnew),own=sum(r['source_class']=='own_site' for r in evnew),raw_pages=len(sel),positive_quotes=positive,known_answers=3,bulk_known_answers=3,county_known_answers=3,all_seven_claims=True,own_site_page_words_only=True,replay_byte_identical=True,no_write_faults=7,retired_ids=len(retired),strict_counts=counts)
(H/'check_results.json').write_text(json.dumps(result,indent=2)+'\n');print('PASS',json.dumps(result))

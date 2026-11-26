"""Re-run of the 2026-11-16 PPP size-band pass on pinned current main (owner rulings 2026-11-26 07:20).

Rule: SCHEMA §1 R13 source 4 (v1.13.3) plus the ten-year age limit (v1.21.1): blank bands only; single-site, Ohio-only
organization; borrower name (atlas.name_key over the held names), street and city all equal; latest qualifying loan per
organization; loan dated on or after the write date minus ten years. Matching is tasks/ppp-size-bands-2026-11-16/build.py's,
not rebuilt. Each candidate evidence row (the SCHEMA §4.13 quote format) is judged by the binding gate against the base tree
and dropped unless it PASSES; the drop and its reason go to gate_holds.csv. SCHEMA §1 R13 v1.19.7 precedence: a fill whose
establishment already holds a DIFFERENT band that rests on an admissible dated source newer than the loan is held
(newer_contradicting_filing); every comparison with a differing held band is recorded in precedence.csv. The base is read
from git, so the plan is reproducible after --apply changes the working tree."""
import argparse,csv,hashlib,io,json,os,re,subprocess,sys
from collections import defaultdict,Counter
from datetime import date,datetime
from decimal import Decimal,InvalidOperation
from pathlib import Path
D=Path(__file__).resolve().parent;ROOT=D.parents[1];sys.path.insert(0,str(ROOT/'scripts'))
import atlas
from regions import PIC18
from build_form5500_spine import band_of,BANDS
import check_evidence_binding as gate
META=json.loads((D/'base.json').read_text());BASE=META['base'];WRITE=date.fromisoformat(META['write_date'])
CUTOFF=WRITE.replace(year=WRITE.year-10).isoformat()  # a loan dated on or after this date qualifies (SCHEMA v1.21.1)
STORE=Path(os.environ.get('ATLAS_STORE','/Volumes/johnpswan/work/GAC/polymer-atlas/atlas-store'))
SOURCE=STORE/'provenance/ppp-loan-scout-2026-11-16'  # INPUTS.sha256 names both files; the sha256 is also checked against source_manifest.json
CENSUS=Path(os.environ.get('CENSUS_ROWS','/Users/johnswanson/.bb/thread-storage/thr_9i2c6byhcz/2026-11-06-atlas/persist/size-ceiling-census-2026-11-26/rows.csv'))
FIELDS={'organizations':'employee_band_ohio','sites':'employee_band_site'}
KEYS={'organizations':'org_id','sites':'site_id'}
ORDER=[b[2] for b in BANDS]+['5000+']
ALLOWED={'Corporation','Subchapter S Corporation','Limited  Liability Company(LLC)','Partnership','Limited Liability Partnership'}
LABEL='claude-code ppp-size-bands-rerun-2026-11-26'
FIRST_EVD=483200  # another open PR holds the range just above EVD-483156
RULINGS='Owner John Swanson 2026-11-26 07:20: "PPP now, street route next" and "Same ten-year rule"; SCHEMA R13 source 4 (v1.13.3), ten-year limit v1.21.1'

csv.field_size_limit(10**9)
def git(*a):return subprocess.check_output(['git',*a],cwd=ROOT,text=True)
def parse(text):return list(csv.DictReader(io.StringIO(text,newline='')))
def read(p):return list(csv.DictReader(Path(p).open(newline='')))
def base_tables(prefix):
 """{shard file name: rows} of data/<prefix>_<TAG>.csv at the pinned base."""
 names=[p for p in git('ls-tree','-r','--name-only',BASE,'data').splitlines() if re.fullmatch(rf'data/{prefix}_[A-Za-z]+\.csv',p)]
 return {Path(p).name:parse(git('show',f'{BASE}:{p}')) for p in sorted(names)}
def write(p,rows,fields):
 with Path(p).open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=fields,lineterminator='\n');w.writeheader();w.writerows(rows)
def band(value):
 try:n=Decimal(value)
 except InvalidOperation:return ''
 return band_of(int(n)) if n.is_finite() and n>=1 and n==n.to_integral_value() else ''
def loan_date(r):return datetime.strptime(r['DateApproved'],'%m/%d/%Y').date().isoformat()
def safe(r):return r['BusinessType'] in ALLOWED and r['BorrowerName'].strip().upper() not in {'','N/A','NOT AVAILABLE','EXEMPTION 6'}
def loans():
 out=[]
 for m in json.loads((D/'source_manifest.json').read_text()):
  p=SOURCE/(m['file']+'.filtered.csv');assert hashlib.sha256(p.read_bytes()).hexdigest()==m['filtered_sha256'],'PPP input differs from source_manifest.json'
  rr=read(p);assert len(rr)==m['counts']['retained'];out.extend(dict(r,source_url=m['url'],source_sha256=m['sha256'],source_file=m['file']) for r in rr)
 assert len(out)==1953 and len({r['LoanNumber'] for r in out})==1953
 assert all(safe(r) for r in out)
 return out
def shard_tag(name):return name.split('_',1)[1][:-4]

BAND_IN_CLAIM=re.compile(r'employee_band_(?:site|ohio)=(\d+-\d+|\d+\+|unknown)(?![\w-])')
def size_evidence():
 """{(record_table, record_id): [size_band evidence rows]} at the base, each with the band it states."""
 out=defaultdict(list)
 for p in git('ls-tree','-r','--name-only',BASE,'data').splitlines():
  if re.fullmatch(r'data/evidence_[A-Za-z]+_[A-Za-z]+\.csv',p):
   for e in parse(git('show',f'{BASE}:{p}')):
    m=BAND_IN_CLAIM.match(e['claim_type']=='size_band' and e['claim_detail'] or '')
    if m:out[(e['record_table'],e['record_id'])].append(dict(e,band=m[1]))
 return out
def source_date(e):
 """The date of the filing a size_band row rests on, or '' when it has none (R13: ITA is 31 December of its year; inspection its open date; old
 2026-11-01 rows carry a retrieval date in observed_date, so the date is read from the claim text; PPP and own-site rows carry theirs in observed_date)."""
 t=e['claim_detail']+' '+e['source_ref']
 if ('filing year' in t or 'raw/osha/' in t) and re.fullmatch(r'\d{4}-\d{2}-\d{2}',e['observed_date']):return e['observed_date']  # rows written since v1.19.7 (and the packet rows citing raw/osha/) carry the filing's own date
 for rx,fmt in ((r'source date (\d{4}-\d{2}-\d{2})','{}'),(r'\bITA\b[^;]*?\bCY(\d{4})','{}-12-31'),(r'\bITA Form 300A (\d{4})\b','{}-12-31'),(r'\bCY(\d{4})\b','{}-12-31'),(r'opened (\d{4}-\d{2}-\d{2})','{}')):
  m=re.search(rx,t)
  if m and (rx!=r'\bCY(\d{4})\b' or 'ITA' in t):return fmt.format(m[1])
 if 'SBA PPP' in e['source_ref'] or e['source_class']=='own_site':return e['observed_date'] if re.fullmatch(r'\d{4}-\d{2}-\d{2}',e['observed_date']) else ''
 return ''
def admissible(e):
 """a dated source that can set or supersede a band under R13: an OSHA ITA or inspection filing, an SBA PPP loan (v1.13.3), or a dated own-site page; Form 5500 is lead-only"""
 return bool(source_date(e)) and (e['source_class']=='own_site' or e['source_class']=='government_filing' and re.search(r'OSHA|SBA PPP',e['source_ref']) and 'EFAST' not in e['source_ref'])
def precedence(fill,orgs,sitebyid,sizeev):
 """-> (class, precedence.csv row) comparing a fill with the band already held on the same establishment (a single-site owner's organization record and its
 sole active site describe one establishment). class: newer_contradicting_filing | newer_contradicting_own_site (held), older_differs | lead_only |
 undated_or_other (fill stands, listed), or '' when nothing is held there or the held band is the same."""
 if fill['record_table']=='organizations':other=('sites',fill['site_id']);held=sitebyid[fill['site_id']][FIELDS['sites']]
 else:other=('organizations',fill['org_id']);held=orgs[fill['org_id']][FIELDS['organizations']]
 held=held.strip()
 if held in ('','unknown') or held==fill['new']:return '',None
 rows=[e for e in sizeev.get(other,[]) if e['band']==held];dated=[(source_date(e),e) for e in rows if admissible(e)]
 if dated:d,e=max(dated,key=lambda x:x[0]);klass=('older_differs' if d<=fill['loan_date'] else 'newer_contradicting_filing' if e['source_class']=='government_filing' else 'newer_contradicting_own_site')
 elif any('EFAST' in e['source_ref'] for e in rows):d,e,klass='',rows[0],'lead_only'
 else:d,e,klass='',(rows[0] if rows else dict(evidence_id='',source_class='',source_ref='')),'undated_or_other'
 return klass,dict(record_table=fill['record_table'],record_id=fill['record_id'],org_id=fill['org_id'],loan_id=fill['loan_id'],loan_date=fill['loan_date'],loan_band=fill['new'],
  held_record=other[1],held_band=held,held_evidence_id=e['evidence_id'],held_source_class=e['source_class'],held_source_date=d,class_=klass)

def plan():
 """-> dict(fills, evidence, holds, skipped, strict): everything derived from the base tree and the PPP input, nothing written."""
 otabs,stabs=base_tables('organizations'),base_tables('sites')
 orgs={r['org_id']:r for t in otabs.values() for r in t};oshard={r['org_id']:n for n,t in otabs.items() for r in t}
 sites=[r for t in stabs.values() for r in t];sshard={r['site_id']:n for n,t in stabs.items() for r in t}
 assert len({s['site_id'] for s in sites})==len(sites)
 byorg=defaultdict(list)
 for s in sites:byorg[s['org_id']].append(s)
 name_index=defaultdict(set)
 for oid,o in orgs.items():
  for field,n in atlas.org_name_fields(o):
   if atlas.name_key(n):name_index[atlas.name_key(n)].add(oid)
 strict=defaultdict(list);held=[]
 for r in loans():
  if not band(r['JobsReported']):continue
  for oid in sorted(name_index[atlas.name_key(r['BorrowerName'])]):
   ss=byorg[oid];active=[s for s in ss if s['operating_status']=='active']
   if len(active)!=1 or any(s['state']!='OH' or s['country'] not in ('','US','USA') for s in ss):continue
   s=active[0]
   if s['county'] not in PIC18 or s['city'].casefold()!=r['BorrowerCity'].casefold():continue
   pair=dict(org_id=oid,site_id=s['site_id'],loan_id=r['LoanNumber'])
   if not s['street_address'] or not r['BorrowerAddress'] or atlas.street_key(s['street_address'])!=atlas.street_key(r['BorrowerAddress']):
    held.append(dict(pair,reason='active-site street missing or not equal',record_id='',retired_evidence_id=''));continue
   if loan_date(r)<CUTOFF:held.append(dict(pair,reason='stale_over_10_years',record_id='',retired_evidence_id=''));continue
   strict[oid].append((s,r))
 have={e['evidence_id'] for p in subprocess.check_output(['git','ls-tree','-r','--name-only',BASE,'data'],cwd=ROOT,text=True).splitlines()
       if re.fullmatch(r'data/evidence_[A-Za-z]+_[A-Za-z]+\.csv',p) for e in parse(git('show',f'{BASE}:{p}'))}
 candidates=[];skipped=[]
 for oid,pairs in sorted(strict.items()):
  s,r=max(pairs,key=lambda pair:(loan_date(pair[1]),pair[1]['LoanNumber']))
  for table,record,shard in [('organizations',orgs[oid],oshard[oid]),('sites',s,sshard[s['site_id']])]:
   rid=record[KEYS[table]];cur=record[FIELDS[table]]
   if cur.strip():skipped.append(dict(record_table=table,record_id=rid,org_id=oid,existing_band=cur,loan_band=band(r['JobsReported']),loan_id=r['LoanNumber']));continue
   effect='supports_U' if record['verification_tier']=='U' else 'supports_B'
   ev=dict(evidence_id='',record_table=table,record_id=rid,claim_type='size_band',
    claim_detail=f'{FIELDS[table]}={band(r["JobsReported"])}; historical {loan_date(r)[:4]} borrower-reported employment figure, JobsReported={r["JobsReported"]}, band only; quote: borrower_name: {r["BorrowerName"]}; business_type: {r["BusinessType"]}; address: {r["BorrowerAddress"]}, {r["BorrowerCity"]}, {r["BorrowerState"]} {r["BorrowerZip"]}',
    source_class='government_filing',source_ref=f'SBA PPP LoanNumber {r["LoanNumber"]} ({r["source_file"]}, release 2024-09-30)',observed_date=loan_date(r),tier_effect=effect,
    created_by=LABEL,notes=f'{RULINGS}; loan approval date {loan_date(r)}; employment reference period unspecified; {r["source_url"]}; source SHA256 {r["source_sha256"]}; exact normalized legal/trade/recorded former name + active-site street key + city; single active site, all held sites Ohio; blank-only fill',address_role='')
   fill=dict(record_table=table,record_id=rid,shard=shard,field=FIELDS[table],old='',new=band(r['JobsReported']),org_id=oid,site_id=s['site_id'],loan_id=r['LoanNumber'],borrower_name=r['BorrowerName'],jobs_reported=r['JobsReported'],loan_date=loan_date(r),tier=record['verification_tier'],evidence_id='')
   candidates.append((fill,ev))
 idx=gate.Index.load(BASE);fills=[];evs=[];gate_holds=[];eid=FIRST_EVD;prec=[];contradicted=[];sizeev=size_evidence();sitebyid={x['site_id']:x for x in sites}
 for fill,ev in candidates:
  v,why,_=gate.judge(dict(ev,evidence_id='EVD-T',_at='build'),idx)
  if v!='PASS':gate_holds.append(dict(record_table=fill['record_table'],record_id=fill['record_id'],org_id=fill['org_id'],loan_id=fill['loan_id'],verdict=v,reason=why));continue
  assert f'EVD-{eid:06d}' not in have,'evidence ID collision'
  ev['evidence_id']=fill['evidence_id']=f'EVD-{eid:06d}';eid+=1  # ids are allotted before the precedence hold so a held row retires its id and no surviving id moves
  klass,row=precedence(fill,orgs,sitebyid,sizeev)
  if row:prec.append(row)
  if klass.startswith('newer_contradicting'):
   held.append(dict(org_id=fill['org_id'],site_id=fill['site_id'],loan_id=fill['loan_id'],reason=klass,record_id=fill['record_id'],retired_evidence_id=ev['evidence_id']));contradicted.append((fill,ev));continue
  fills.append(fill);evs.append(ev)
 return dict(fills=fills,evidence=evs,holds=held,gate_holds=gate_holds,precedence=prec,contradicted=contradicted,skipped=skipped,strict=len(strict),candidates=len(candidates))

def counts(p):
 f=p['fills'];return dict(base=BASE,cutoff=CUTOFF,strict_organizations=p['strict'],fills=dict(Counter(r['record_table'] for r in f)),
  owners_filled=len({r['org_id'] for r in f}),evidence_rows=len(p['evidence']),held_loan_org_pairs=sum(h['reason']!='newer_contradicting_filing' and not h['reason'].startswith('newer_contradicting') for h in p['holds']),newer_contradicting_held=sum(h['reason'].startswith('newer_contradicting') for h in p['holds']),precedence_classes=dict(Counter(r['class_'] for r in p['precedence'])),retired_evidence_ids=[h['retired_evidence_id'] for h in p['holds'] if h['retired_evidence_id']],candidate_cells=p['candidates'],gate_dropped=len(p['gate_holds']),gate_drop_reasons=dict(Counter(f"{h['verdict']} {h['reason']}" for h in p['gate_holds'])),
  held_reasons=dict(Counter(h['reason'] for h in p['holds'])),skipped_nonblank=len(p['skipped']),loan_years=dict(Counter(r['loan_date'][:4] for r in f)),
  tiers=dict(Counter(f"{r['record_table']}:{r['tier']}" for r in f)))

def base_bytes(path):return subprocess.check_output(['git','show',f'{BASE}:data/{Path(path).name}'],cwd=ROOT)
def append_rows(path,rows):
 """Write the base shard plus the new rows at the end: the evidence shards are not id-sorted (V-36 covers record shards only), so no existing row moves."""
 raw=base_bytes(path);assert raw.endswith(b'\n') and b'\r' not in raw
 fields=next(csv.reader(io.StringIO(raw.split(b'\n',1)[0].decode())));buf=io.StringIO()
 w=csv.DictWriter(buf,fieldnames=fields,lineterminator='\n',extrasaction='raise');w.writerows(rows)
 Path(path).write_bytes(raw+buf.getvalue().encode())

def reconcile(p):
 """AGENTS.md section 2 rule 10c: every owner in the pass's fills or the census's 38 PPP-strict owners that is not in both, with its reason.
 A difference with no reason stops the build (never explained away). Unit: owners (org_id), filter: PIC-18 owners of active tier A-C sites."""
 census={r['org_id']:r for r in read(CENSUS)};in38={o for o,r in census.items() if r['ppp_state']=='Y'};assert len(in38)==38 and len(census)==372
 fo={f['org_id'] for f in p['fills']};gate_owner={h['org_id']:h for h in p['gate_holds']}
 otabs,stabs=base_tables('organizations'),base_tables('sites')
 orgs={r['org_id']:r for t in otabs.values() for r in t};sites={r['site_id']:r for t in stabs.values() for r in t}
 skipped={(x['record_table'],x['record_id']):x for x in p['skipped']};cand={(f['record_table'],f['record_id']):f for f in p['fills']}
 out=[]
 for o in sorted(in38|fo):
  if o in in38 and o in fo:continue
  if o in in38:  # census owner with no fill: the gate dropped every cell, or the cells were nonblank
   h=gate_owner.get(o);why=f"gate {h['verdict']} {h['reason']}" if h else None
  else:
   other=[(t,r) for (t,r),x in skipped.items() if x['org_id']==o]
   if o in census:why=f"in the census frame but census ppp_state {census[o]['ppp_state']} ({census[o]['route']}): the census matcher and the 2026-11-16 matcher differ here"  # not expected: stop below
   elif other:why='not in the census frame: its other record already holds a band ('+', '.join(f"{t} {skipped[(t,r)]['existing_band']}" for t,r in other)+'); the PPP fill is on the blank record'
   else:why=None
  if not why:raise SystemExit(f'reconciliation: owner {o} is in only one of the pass and the census 38 with no reason')
  out.append(dict(org_id=o,in_pass=o in fo,in_census_38=o in in38,reason=why))
 write(D/'reconciliation.csv',out,['org_id','in_pass','in_census_38','reason'])
 return dict(pass_owners=len(fo),census_ppp_strict=len(in38),in_both=len(fo&in38),pass_only=len(fo-in38),census_only=len(in38-fo))

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--apply',action='store_true');a=ap.parse_args()
 p=plan();fills,evs=p['fills'],p['evidence']
 write(D/'fills.csv',fills,list(fills[0]));write(D/'CLAIMS_CHECKED.csv',[dict(table=f['record_table'],record_id=f['record_id'],field=f['field'],verdict='corrected',evidence_id=f['evidence_id']) for f in sorted(fills,key=lambda f:f['evidence_id'])],['table','record_id','field','verdict','evidence_id']);write(D/'evidence_rows.csv',evs,list(evs[0]));write(D/'holds.csv',p['holds'],['org_id','site_id','loan_id','reason','record_id','retired_evidence_id']);write(D/'precedence.csv',[dict((k.rstrip('_'),v) for k,v in r.items()) for r in p['precedence']],['record_table','record_id','org_id','loan_id','loan_date','loan_band','held_record','held_band','held_evidence_id','held_source_class','held_source_date','class']);write(D/'gate_holds.csv',p['gate_holds'],['record_table','record_id','org_id','loan_id','verdict','reason'])
 c=counts(p);c['reconciliation']=reconcile(p);(D/'counts.json').write_text(json.dumps(c,indent=2)+'\n')
 if a.apply:
  for table in FIELDS:
   for shard in sorted({r['shard'] for r in fills if r['record_table']==table}):
    target=ROOT/'data'/shard;rows=parse(base_bytes(target).decode());updates={r['record_id']:r for r in fills if r['record_table']==table and r['shard']==shard}
    for r in rows:
     u=updates.get(r[KEYS[table]])
     if u:assert r[FIELDS[table]]=='','refuse to overwrite a band';r[FIELDS[table]]=u['new']
    write(target,rows,list(rows[0]))
    ep=ROOT/'data'/f'evidence_{table}_{shard_tag(shard)}.csv'
    assert not {r['evidence_id'] for r in parse(base_bytes(ep).decode())}&{e['evidence_id'] for e in evs},'evidence ID collision'
    append_rows(ep,[e for e in evs if e['record_table']==table and e['record_id'] in updates])
 print(json.dumps(counts(p)))
if __name__=='__main__':main()

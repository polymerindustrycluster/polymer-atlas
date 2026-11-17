"""Frame + per-site verdicts for promoting notes streets to street_address. Writes frame.csv and verdicts.csv.
Reuses scripts/atlas.py (NOTES_STREET_RE, notes_candidate_key, street_key), scripts/regions.py PIC18."""
import csv,hashlib,re,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];TASK=Path(__file__).resolve().parent
S=Path('/Users/johnswanson/.bb/thread-storage/thr_9i2c6byhcz/2026-11-06-atlas/persist')
CORPUS=S/'pic18-corpus-2026-11-16'
sys.path.insert(0,str(ROOT/'scripts'))
from regions import PIC18
from atlas import NOTES_STREET_RE,notes_candidate_key
TODAY='2026-11-17'
def read(p):return list(csv.DictReader(open(p,newline='')))
def write(p,rows,cols=None):
 with open(p,'w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=cols or list(rows[0]),lineterminator='\n');w.writeheader();w.writerows(rows)
def norm(s):return re.sub(r'[^a-z0-9]','',(s or '').lower())
def ws(t):return re.sub(r'\s+',' ',t)
def sha(b):return hashlib.sha256(b).hexdigest()
def candidates(notes):
 """distinct (key -> first match span) street candidates in notes, in order."""
 out={}
 for m in NOTES_STREET_RE.finditer(notes or ''):out.setdefault(notes_candidate_key(m[0]),m)
 return out
def frame_rows(sites):
 return [s for s in sites if s['operating_status']=='active' and s['county'] in PIC18 and not s['street_address'].strip() and candidates(s['notes'])]
def independent_count(sites):
 """Simple regex count: number + words + street-type word."""
 rx=re.compile(r'\b\d{2,6}\s+[A-Za-z0-9.\' -]{2,40}?\b(?:Rd|Road|St|Street|Ave|Avenue|Dr|Drive|Blvd|Boulevard|Pkwy|Parkway|Way|Ln|Lane|Pike|Hwy|Highway|Ct|Court|Pl|Place|Trl|Trail|Cir|Circle)\b',re.I)
 return {s['site_id'] for s in sites if s['operating_status']=='active' and s['county'] in PIC18 and not s['street_address'].strip() and rx.search(s['notes'] or '')}

FED={'ita':('osha-ita-2026-11-01','establishment_id'),'spine':('osha-spine-2026-11-01','est_key'),'frs':('echo-frs-spine-2026-11-01','registry_id')}
def fedrow(kind):
 d,k=FED[kind];f='facilities.csv' if kind=='frs' else 'establishments.csv'
 return {r[k]:r for r in read(ROOT/'tasks'/d/f)},read(ROOT/'tasks'/d/'site_matches.csv'),ROOT/'tasks'/d/f
HIST=re.compile(r'(?i)different|superseded|former(ly)?|prior address|moved|relocat|old address|street correction|corrected')
LABEL=re.compile(r'(?i)mail(?:ing)?\b|p\.?\s*o\.?\s*box|parent(?:.s)? (?:hq|headquarters|address|office)|corporate|sales office|billing|registered agent')
SRCNOTES=re.compile(r'(?i)own site|own-site|company site|FRS|OSHA|\bTRI\b|SEC filing|EDGAR|form 5500|parcel|auditor|brochure|certificate|\bSOS\b|secretary of state')
class Ctx:
 def __init__(s):
  import glob
  s.orgs={o['org_id']:o for f in glob.glob(str(ROOT/'data/organizations_*.csv')) for o in read(f)}
  s.frsids={}
  for l in read(ROOT/'data/registry_links.csv'):
   if l['registry']=='FRS':s.frsids.setdefault(l['org_id'],set()).add(l['registry_id'])
  s.sites=read(ROOT/'data/sites_OH.csv');s.byid={x['site_id']:x for x in s.sites}
  s.fed={k:fedrow(k) for k in FED};s.bind={}
  for k,(rows,matches,_) in s.fed.items():
   idk=FED[k][1]
   for m in matches:
    if m['site_id'] and m['verdict']=='MATCH_SITE' and m['match_strength']=='strong':s.bind.setdefault(m['site_id'],[]).append((k,m[idk]))
  man=read(CORPUS/'manifest.csv');s.pages={}
  for m in man:
   if m['text_file'] and m['raw_file']:s.pages.setdefault(m['org_id'],[]).append(m)
  s.text={}
 def page_text(s,m):
  p=Path(m['text_file']);p=p if p.is_absolute() else CORPUS/p
  if p not in s.text:s.text[p]=ws(p.read_text(errors='replace'))
  return p,s.text[p]
def same_city(a,b):return norm(a)==norm(b)

def witness(ctx,site,ckey):
 """return list of witness dicts verifying candidate key for this site (strongest first)."""
 out=[];city=norm(site['city'])
 # own-site corpus pages
 org=ctx.orgs.get(site['org_id'],{});dom=lambda u:re.sub(r'^www\.','',(re.match(r'(?:https?://)?([^/\s;,]+)',u or '') or ['',''])[1].lower())
 onrec={dom(u) for u in re.findall(r'https?://[^\s;,)]+',(org.get('website','')+' '+org.get('sources','')+' '+site['sources']))}|{dom(org.get('website',''))}
 for m in ctx.pages.get(site['org_id'],[]):
  if dom(m['final_url'] or m['url']) not in onrec and dom(m['url']) not in onrec:continue
  p,t=ctx.page_text(m)
  for mm in NOTES_STREET_RE.finditer(t):
   if notes_candidate_key(mm[0])!=ckey:continue
   tail=t[mm.end():mm.end()+60]
   if city not in norm(tail):continue
   before=t[max(0,mm.start()-50):mm.start()]
   z=re.search(r'\b(?:OH|Ohio)\b[ ,]*(\d{5})?',tail,re.I)
   if not z or city not in norm(tail[:z.start()]):continue
   q=(mm[0]+tail[:z.end()]).strip()
   if re.search(r'\(\d{3}\)|\d{3}[-.]\d{4}|(?i:fax|phone|tel)',q):continue  # keep phone numbers out of receipts
   sm=re.match(r'(.*?)[\s,.]*'+re.escape(re.split(r'[,\s]',site['city'])[0]),q,re.I)
   street=re.sub(r'[\s,.]+$','',sm[1]) if sm else mm[0]
   out.append(dict(named=True,prob=False,ref='',cls='own_site',url=m['final_url'] or m['url'],quote=q,before=before,page=str(p),raw=m['raw_file'],sha256=m['sha256'],key='',street=street,zip=z[1] or ''));break
  if out and out[-1]['cls']=='own_site':break
 # federal bindings
 for kind,key in ctx.bind.get(site['site_id'],[]):
  rows,_,path=ctx.fed[kind];r=rows[key]
  if r['state']!='OH' or norm(r['city'])!=city:continue
  if next(m for m in ctx.fed[kind][1] if m[FED[kind][1]]==key).get('alt_site_ids'):continue  # another site could own the filing
  if notes_candidate_key(r['street'])!=ckey and not (NOTES_STREET_RE.search(r['street']) and notes_candidate_key(NOTES_STREET_RE.search(r['street'])[0])==ckey):continue
  z=r.get('zip5',r.get('zip',''))
  nm=r.get('establishment_name',r.get('name',r.get('facility_name','')))
  st=re.sub(r'[\s,]+'+re.escape(r['city'])+r'\.?$','',r['street'],flags=re.I)
  notes=site['notes'] or ''
  if kind=='ita':named=bool(re.search(r'OSHA ITA',notes))
  elif kind=='spine':named=bool(re.search(r'OSHA inspection',notes))
  else:named=(key in notes and not re.search(key+r'[^.]{0,30}PROBABLE',notes)) or key in ctx.frsids.get(site['org_id'],set())
  prob=kind=='frs' and bool(re.search(key+r'[^.]{0,30}PROBABLE',notes))
  ref={'ita':'https://www.osha.gov/sites/default/largefiles/ITA_300A_Summary_Data_2025_through_08-31-2026.csv','spine':'https://www.osha.gov/ords/imis/establishment.inspection_detail?id='+r['latest_activity_nr'] if kind=='spine' else '','frs':'https://frs-public.epa.gov/ords/frs_public2/frs_rest_services.get_facilities?registry_id='+key+'&output=JSON'}[kind]
  out.append(dict(named=named,prob=prob,cls={'frs':'registry'}.get(kind,'government_filing'),kind=kind,key=key,street=st,ref=ref,url='',quote=f'{nm} | {r["street"]} | {r["city"]} | OH | {z}',before='',page=str(path.relative_to(ROOT)),raw='',sha256=sha((path).read_bytes()),zip=z[:5]))
 order={'own_site':0,'government_filing':1,'registry':2}
 return sorted(out,key=lambda w:order[w['cls']])

PRIOR=ROOT/'tasks/pic18-street-leads-2026-11-16/leads.csv'
def prior_leads():
 from collections import defaultdict
 d=defaultdict(list)
 for r in read(PRIOR):d[r['site_id']].append(r['street'])
 return d
MANUAL_HOLDS={'SITE-000514':('SITEWIDE_FOOTER_SUITE','Own-site address is an unlabeled site-wide footer with a suite on a distribution site; need a page that states this Westlake location as a warehouse/office of the operator.')}
PL=prior_leads()
def adjudicate(ctx,site):
 sid=site['site_id'];notes=site['notes'] or '';cands=candidates(notes)
 base=dict(site_id=sid,org_id=site['org_id'],city=site['city'],county=site['county'],zip=site['zip'],candidates=' || '.join(m[0] for m in cands.values()),verdict='',hold_class='',settling_fact='',street='',source_class='',tier_effect='',source_ref='',source_key='',quote='',witness_file='',raw_file='',sha256='',notes_mention_any_source='Y' if SRCNOTES.search(notes) else 'N')
 def hold(cls,fact,verdict='STILL_UNCERTAIN'):base.update(verdict=verdict,hold_class=cls,settling_fact=fact);return base
 if len(cands)>1:return hold('TWO_STREETS',f'Need the source that settles which of {len(cands)} notes streets is this establishment: '+' | '.join(m[0] for m in cands.values()))
 ckey,m=next(iter(cands.items()));street=re.sub(r'[.,]+$','',m[0]).strip()
 ctxt=notes[max(0,m.start()-90):m.end()+60]
 if re.search(r'RETIRED \d{4}-\d\d-\d\d|Do not promote',notes):return hold('NOTES_RETIRED_FLAG','Notes carry a RETIRED / do-not-promote annotation; need the owner scope disposition for this site before any cell is filled.')
 if LABEL.search(ctxt):return hold('MAILING_OR_PARENT_LABEL',f'Notes label the address near "{ctxt.strip()[:100]}"; need a source stating {street} is this establishment\'s physical street.')
 if HIST.search(notes[max(0,m.start()-120):m.end()+120]):return hold('SUPERSEDED_OR_HISTORICAL','Notes mark the address corrected/superseded/former; need a current-occupancy witness.')
 after=notes[m.end():m.end()+40];cm=re.match(r'\s*,\s*([A-Za-z .]+?)\s*,\s*(?:OH|Ohio)\b',after)
 if cm and norm(cm[1])!=norm(site['city']):return hold('CITY_MISMATCH',f'Notes give city {cm[1]!r} for {street}; site city is {site["city"]!r}.')
 ws_=witness(ctx,site,ckey)
 if not ws_:
  if base['notes_mention_any_source']=='N':return hold('NO_NAMED_SOURCE','Notes cite no named own-site/filing/parcel source for the street; need a named source (own-site page, filing or parcel record) that shows it for this establishment.')
  return hold('NAMED_SOURCE_NOT_REACHED',f'Notes cite a named source but no stored witness (corpus own-site page or bound federal extract) reproduces {street} with the site city; need that page/record.')
 from atlas import street_key as _sk
 for ls in PL.get(sid,[]):
  if re.match(r'\d+',ls) and re.match(r'\d+',ls)[0]==re.match(r'\d+',street)[0] and not (_sk(ls).startswith(_sk(street)) or _sk(street).startswith(_sk(ls))):return hold('LEAD_STREET_DIFFERS',f'PPP/SAM lead gives {ls!r} against notes {street!r}; need a source choosing between them.')
 named=[x for x in ws_ if x['named']]
 if not named:
  x=ws_[0];return hold('FRS_PROBABLE' if x['prob'] else 'NO_NAMED_SOURCE',(f'Notes mark FRS {x["key"]} only a PROBABLE match; need identity settled.' if x['prob'] else f'No source named on the record for this street; the stored {x["cls"]} witness {x["key"] or x["page"]} ({x["quote"][:80]}) matches via a task-folder binding and is a recommendation, not a record citation.'))
 w=named[0]
 if w['cls']=='registry':return hold('REGISTRY_CEILING',f'Only an EPA FRS registry row ({w["key"]}) shows {w["street"]}: a registry address caps at supports_C (V-25 fails on a tier A/B site) and the stored extract has no raw/ record (V-23); need an own-site or filing address witness, or a dated live FRS fetch.')
 if sid in MANUAL_HOLDS:return hold(*MANUAL_HOLDS[sid])
 if LABEL.search(w['before']+' '+w['quote']):return hold('MAILING_OR_PARENT_LABEL','Witness text labels the address mailing/parent/corporate; need physical-address wording.')
 if w['zip'] and site['zip'] and w['zip'][:5]!=site['zip'][:5]:return hold('ZIP_CONFLICT',f'Witness ZIP {w["zip"]} differs from site ZIP {site["zip"]}; ZIP is an owner/record fix, not an edit here.')
 for o in ctx.sites:
  if o['site_id']==sid:continue
  from atlas import street_key
  if o['street_address'] and street_key(o['street_address'])==street_key(street) and same_city(o['city'],site['city']):return hold('ADDRESS_COLLISION',f'{o["site_id"]} already carries this street in {o["city"]}; one address = one site (AGENTS 3.3).')
  if o['org_id']==site['org_id'] and o['operating_status']!='closed' and same_city(o['city'],site['city']) and not o['street_address'].strip():return hold('SIBLING_SAME_CITY',f'Same organization has {o["site_id"]} (street blank) in {site["city"]}; need a source tying {street} to one of the two.')
 base.update(verdict='VERIFIED',street=w['street'],source_class=w['cls'],tier_effect=('supports_U' if site['verification_tier']=='U' else ('supports_A' if w['cls']!='registry' else 'supports_C')),source_ref=w['url'] or w['ref'],source_key=w['key'],quote=w['quote'],witness_file=w['page'],raw_file=w['raw'],sha256=w['sha256'],hold_class='',settling_fact='')
 base['kind']=w.get('kind','')
 return base
def main():
 ctx=Ctx();fr=frame_rows(ctx.sites)
 write(TASK/'frame.csv',[{k:s[k] for k in ('site_id','org_id','city','county','zip','verification_tier','notes')} for s in fr])
 vs=[adjudicate(ctx,s) for s in fr]
 from atlas import street_key
 seen={}
 for v in vs:
  if v['verdict']=='VERIFIED':seen.setdefault((street_key(v['street']),norm(v['city'])),[]).append(v)
 for g in seen.values():
  if len(g)>1:
   for v in g:v.update(verdict='STILL_UNCERTAIN',hold_class='ADDRESS_COLLISION_IN_PASS',settling_fact='Sites '+', '.join(x['site_id'] for x in g)+' would all carry '+v['street']+'; one address = one site (AGENTS 3.3); need a source assigning the street to one operator.',street='',source_class='',tier_effect='',source_ref='',source_key='',quote='',witness_file='',raw_file='',sha256='')
 cols=['site_id','org_id','city','county','zip','candidates','verdict','hold_class','settling_fact','street','source_class','tier_effect','source_ref','source_key','quote','witness_file','raw_file','sha256','notes_mention_any_source','kind']
 for v in vs:v.setdefault('kind','')
 write(TASK/'verdicts.csv',vs,cols)
 from collections import Counter
 print(len(fr),len(independent_count(ctx.sites)),Counter(v['verdict'] for v in vs),Counter(v['hold_class'] for v in vs),Counter(v['source_class'] for v in vs if v['verdict']=='VERIFIED'))
if __name__=='__main__':main()

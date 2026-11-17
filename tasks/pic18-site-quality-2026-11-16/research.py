"""Banked-source census, strict literal federal binding, and reviewed own-page selections."""
from prep import *
import hashlib,re
from urllib.parse import urlsplit
from atlas import street_key,name_key
from site_corpus import on_page,Text
S=Path('/Users/johnswanson/.bb/thread-storage/thr_9i2c6byhcz/2026-11-06-atlas/persist/pic18-corpus-2026-11-16')
# Acceptance fixed before application: seven claims B+, literal filed identity/street/ZIP/code,
# own operator page with city and present activity, existing A/B county/address, no owner question.
SELECT={
'SITE-000240':('https://alttran.com/rubber-mixing-capabilities/','We provide custom rubber mixing for manufacturers that need consistent compounds developed around their material, processing and application requirements.','5285 Hudson Drive Hudson, Ohio 44236'),
'SITE-000329':('https://drecoinc.com/','From initial prototype to full-scale production, we deliver uncompromising quality and technical expertise in thermoplastic manufacturing','7887 Root Rd North Ridgeville, OH 44039'),
'SITE-000898':('https://fabohio.com/about-us/history/','FabOhio, Inc. opened for business in 1963 and continues to operate at the same facility in Uhrichsville, Ohio. The core business is the same as when we started—engineering flexible synthetic films for use as barrier isolation and containment in many forms and applications.','521 East 7th Street Uhrichsville, OH 44683')}
def census():
 orgs={r['org_id']:r for p in (R/'data').glob('organizations_*.csv') for r in read(p)}
 manifest=read(S/'manifest.csv');ita=read(R/'tasks/osha-ita-2026-11-01/establishments.csv');osha=read(R/'tasks/osha-spine-2026-11-01/establishments.csv')
 ranks={r['site_id']:r for r in read(H/'ranking.csv')};verdicts=[];witness=[];ev=[]
 for s in read(H/'input.csv'):
  sid=s['site_id'];o=orgs[s['org_id']];aliases={name_key(o['legal_name']),*(name_key(t) for t in o['trade_names'].split(';') if t)}
  fs=[r for r in ita if s['street_address'] and r['state']==s['state'] and street_key(r['street'])==street_key(s['street_address'])]
  ins=[r for r in osha if s['street_address'] and r['state']==s['state'] and street_key(r['street'])==street_key(s['street_address'])]
  good=[r for r in fs if name_key(r['company_name']) in aliases and r['zip5']==s['zip'] and r['naics_code']==s['naics_primary']]
  conflict=any(r['naics_code']!=s['naics_primary'] for r in fs) or any(r['naics_latest']!=s['naics_primary'] for r in ins)
  pages=[p for p in manifest if p['org_id']==s['org_id'] and p['text_file']];city_pages=[];activity_pages=[]
  for p in pages:
   path=Path(p['text_file']);path=path if path.is_absolute() else S/path
   text=' '.join(path.read_text().split())
   if s['city'].lower() in text.lower():city_pages.append(p['url'])
   if re.search(r'(?i)manufactur|we provide|we specialize|we produce',text):activity_pages.append(p['url'])
  gaps=[c for c in CLAIMS if ranks[sid][c] not in ['A','B']]
  reason='Obtain B-strength '+', '.join(gaps)+' evidence at this exact establishment; city/footer or corporate activity alone does not settle plant activity.'
  if conflict:reason='Resolve competing filed primary codes at the same street before code corroboration; '+reason
  if not good:reason='Obtain literal filed operator/alias, street, ZIP and held primary-code match; '+reason
  if not pages:reason='Acquire readable own-operator plant page (corpus availability only); '+reason
  if sid=='SITE-000346':reason='Obtain current exact-plant own-operator activity witness covering the retained scope after the documented partial nitrile exit; mechanical B+ strengths alone are not a new activity review.'
  if sid=='SITE-000279':reason='Resolve documented Carlisle operator-grain inconsistency against survivor ORG-002251; existing high-strength claims alone do not settle operator binding.'
  selected=sid in SELECT
  if selected:
   assert good and not conflict and ranks[sid]['address'] in ['A','B']
   url,quote,binding=SELECT[sid];p=next(p for p in pages if p['url']==url)
   path=Path(p['text_file']);path=path if path.is_absolute() else S/path
   text=path.read_text();assert on_page(quote,text),(sid,'quote');assert on_page(binding,text),(sid,'binding')
   assert urlsplit(url).hostname.removeprefix('www.')==urlsplit(o['website']).hostname.removeprefix('www.')
   raw=Path(p['raw_file']);raw=raw if raw.is_absolute() else S/raw
   assert hashlib.sha256(raw.read_bytes()).hexdigest()==p['sha256']
   parser=Text();parser.feed(raw.read_text());rawtext=' '.join(parser.parts)
   assert on_page(quote,rawtext) and on_page(binding,rawtext)
   witness.append(dict(site_id=sid,url=url,quote=quote,binding=binding,text_file=str(path),text_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),raw_file=str(raw),raw_sha256=p['sha256']))
   f=good[0];furl='https://www.osha.gov/sites/default/largefiles/ITA_300A_Summary_Data_2025_through_08-31-2026.csv#establishment_ID='+f['establishment_id']
   for c in ['existence','code','parent']:
    detail={'existence':f['company_name']+'; '+f['street']+', '+f['city']+', '+f['state']+' '+f['zip5'],'code':'NAICS '+f['naics_code']+'; government_filing; filed '+f['date_submitted'],'parent':'Filed operator '+f['company_name']+'; held operator '+o['legal_name']}[c]
    ev.append(dict(record_table='sites',record_id=sid,claim_type=c,claim_detail=detail,source_class='government_filing',source_ref=furl,observed_date='2026-11-01',tier_effect='supports_B',created_by='atlas-w16-quality',notes='Banked ITA CY2025; packet vintage 2026-11-01; jointly corroborated by own-operator street/city/activity witness. Existing address/county evidence retained.'))
   for c in ['scope','activity','liveness']:
    ev.append(dict(record_table='sites',record_id=sid,claim_type=c,claim_detail=quote,source_class='own_site',source_ref=url,observed_date='2026-11-16',tier_effect='supports_B',created_by='atlas-w16-quality',notes='Stored live page, present-tense activity; not a dated production event or status transition. Exact street/city on same page binds establishment; existing address/county evidence retained.'))
   reason='All seven claims B+ after literal filing and own-operator plant witness; existing address/county retained.'
  verdicts.append(dict(site_id=sid,applied='yes' if selected else 'no',verdict='VERIFIED' if selected else 'STILL_UNCERTAIN',settling_fact=reason,missing_before=';'.join(gaps),ita_street_rows=len(fs),inspection_street_rows=len(ins),literal_ita_matches=len(good),code_conflict=str(conflict),corpus_pages=len(pages),city_pages=';'.join(city_pages),activity_pages=';'.join(activity_pages)))
 for n,e in enumerate(ev):e['evidence_id']=f'EVD-{379000+n:06d}'
 return verdicts,witness,ev
if __name__=='__main__':
 v,w,e=census();write(H/'verdicts.csv',v);write(H/'witnesses.csv',w);write(H/'evidence.csv',e);print(len(v),len(w),len(e))

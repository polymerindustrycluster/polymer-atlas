import csv,json,hashlib
from research import BASE,CACHE
rows=list(csv.DictReader((BASE/'input.csv').open()))
receipts=[json.loads(p.read_text()) for p in sorted(CACHE.glob('*.json'))]
pos={
'007432':('Monroe','LA','https://tanks.polyprocessing.com/hubfs/Installation%20Operation%20Maintenance%20Manual/PPC%20Installation%2C%20Operation%2C%20and%20Maintenance%20Manual%209-2023.pdf','Company Headquarters || P.O. Box 4150 (71211) 2201 Old Sterlington Road Monroe, Louisiana 71203','Own September 2023 installation/operation/maintenance manual final page labels company headquarters separately from French Camp and Winchester. HQ designation rather than mailing-address inference; country US from explicit Louisiana state context.'),
'007712':('Hopkins','MN','https://tpmmfg.com/about/','Hopkins, Minnesota || Hopkins Plant TPM HOP is located at the TPM headquarters.','Own current opening identifies Hopkins Minnesota; current Hopkins Plant section explicitly locates HOP at TPM headquarters. Same page states 2023 stand-alone and 2024 Plasman Precision Parts rebrand to TPM. Historical 2001 line says Hopkins MI (typo/conflict); current opening is Minnesota. L5b independently raw-checked and accepted operating-business HQ. Retain held legal name/parent/status unchanged.'),
'007729':('Clearwater','MN','https://www.toplastics.com/hubfs/Resources/Medical/TO%20Plastics_Custom%20Solutions.pdf','HEADQUARTERS || P.O. Box 37 | 830 County Road 75 || Clearwater, MN 55320','Own brochure: left column HEADQUARTERS at Clearwater; separate right column MANUFACTURING at Otsego. pdftotext -layout interleaves columns, so three bounded ordered excerpts from same page are intentional. L5b inspected both layouts, independently fetched and accepted HQ block; reuse captured integrator receipt.')}
obs={
'007428':'Own group location page labels Sigma Plastics Group headquarters in Florida, not held Omega Extruding Corp of California. Subsidiary location is not explicitly HQ.',
'007440':'Known Toray homepage/contact returned access-denied content and Jina fallback failed. Exact held operating-entity current HQ not established.',
'007516':'Known GreenView domain HTTP/HTTPS failed; Jina fallback failed. Availability failure is not evidence of absence.',
'007605':'Own homepage/about/locations inspected; facility and contact locations not explicitly designated headquarters.',
'007606':'Own homepage/locations inspected; locations without explicit HQ designation for held American Vinyl Company.',
'007721':'Own homepage/contact inspected; no explicit current HQ designation.',
'007726':'Known IMR own homepage/about/contact inspected; no current headquarters designation for exact held Northern Prairie Polymers LLC, rather than other group business.',
'007727':'Own homepage/company/contact inspected; Waconia address is a contact address without HQ label.',
'007728':'Own homepage/about/contact inspected; operating/contact address not explicitly headquarters.',
'007730':'Own homepage inspected; guessed about route returned not-found content. No explicit HQ designation obtained.',
'007731':'Own company page says divisions headquartered under one roof in Minnesota, but does not explicitly tie headquarters to a city; Hutchinson contact address alone does not settle the city.',
'007733':'Own homepage/about/contact inspected; company/operating address not explicitly HQ-designated.',
'007908':'Known Flexcraft own homepage/about/contact inspected; no exact held Holocraft Corporation-specific headquarters designation.',
'007912':'Own homepage/about/contact inspected; address without explicit HQ designation.',
'007917':'Own homepage/about/contact inspected; company/facility addresses not explicitly headquarters.',
'008002':'Own group homepage/about/contact inspected; no Darnel Inc-specific HQ designation distinct from group offices.',
'008106':'Own global group homepage/locations inspected; no SaarGummi Tennessee Inc-specific HQ designation; global group HQ excluded.',
'008206':'Own global homepage/about/contact inspected; no Gracious Living Kentucky Inc-specific HQ designation; Canadian parent address excluded.',
'008307':'Own company page says headquartered in Virginia without city. Footer separately labels Blackstone manufacturing and Rumson AR/AP corporate addresses; neither explicitly settles current HQ city.',
'009001':'Own homepage/about/contact inspected; location address not explicitly designated headquarters.',
'009003':'Own profile labels TG North America Troy headquarters and Toyoda Gosei world headquarters, not held TG Missouri; own contact address alone cannot settle HQ.',
'009004':'Own homepage/about/contact inspected; company address without explicit current HQ designation.'}
fields='org_id legal_name verdict outcome hq_city hq_state hq_country hq_county source_url source_class quote fetch_count reason settling_fact note raw_sha256'.split()
output=[]
for r in rows:
 oid=r['org_id'];key=oid[4:];rr=[x for x in receipts if x['org_id']==oid];v=dict.fromkeys(fields,'');v.update(org_id=oid,legal_name=r['legal_name'],fetch_count=len(rr))
 if key in pos:
  city,state,url,q,note=pos[key];rc=next(x for x in rr if x['url']==url)
  v.update(verdict='HQ_FOUND',outcome='HQ_FOUND',hq_city=city,hq_state=state,hq_country='US',source_url=url,source_class='own_site',quote=q,reason=note,note=note,raw_sha256=rc['raw_sha256'])
 else:
  note=obs[key];fact=f'An explicit current HQ city/state/country designation for exact held entity {r["legal_name"]}, distinct from plant/contact/mailing/parent addresses.'
  v.update(verdict='STILL_UNKNOWN',outcome='STILL_UNKNOWN',reason=note,note=note,settling_fact=fact)
  rc=next(x for x in rr if 'r.jina.ai' not in x['url']);v.update(source_url=rc['url'],source_class='own_site',raw_sha256=rc['raw_sha256'])
 output.append(v)
with (BASE/'verdicts.csv').open('w') as f:
 w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(output)
(BASE/'receipts.json').write_text(json.dumps({'observed_date':'2026-11-06','input_sha256':hashlib.sha256((BASE/'input.csv').read_bytes()).hexdigest(),'fetches':receipts},indent=2)+'\n')
print('written',len(output),'HQ_FOUND',len(pos),'STILL_UNKNOWN',len(output)-len(pos),'attempts',len(receipts))

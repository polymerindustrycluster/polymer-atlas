import csv,json,hashlib
from research import BASE,CACHE
rows=list(csv.DictReader((BASE/'input.csv').open()))
receipts=[json.loads(p.read_text()) for p in sorted(CACHE.glob('*.json'))]
positive={
'004558':('Hoquiam','WA','http://paneltechintl.com/','Paneltech along with its sister company, PaperStone, is headquartered at the Port of Grays Harbor in Hoquiam, Washington.','Operating-name HQ; held trade_names already Paneltech;PaperStone. Footer Paneltech LLC versus held International LLC: retain held spelling. L5b independently re-fetched and accepted this identity seam; reuse integrator rawcheck.json without extra fetch.'),
'006109':('West Chicago','IL','https://cicink.com/contact/','CIC Corporate Headquarters 1100 N. Harvester Road West Chicago, IL 60185','Own contact page explicitly labels CIC Corporate Headquarters; footer names Central Ink Corporation. Other contact locations not substituted.'),
'006114':('Port Byron','IL','https://www.sandstromproducts.com/the-company/contact-us/','Sandstrom Products Company Headquarters PO Box 547 224 South Main Street Port Byron, IL 61275','Explicit Headquarters block, including street address; HQ not inferred merely from PO Box or contact page.'),
'007026':('Troy','MI','https://nationalmanufacturing.group','our sales team located in our Troy Michigan headquarters','Exact held group own homepage HQ statement. Recent news dateline Clarkston and locations listing are not HQ-designated; parent should retain that currency caveat during independent check.'),
'007032':('Macomb','MI','https://teampti.com/pti-engineered-plastics-has-been-awarded-the-top-workplace-of-the-year-for-2023-by-the-detroit-free-press/','Headquartered in Macomb, MI, PTI Engineered Plastics','Own 2023 Top Workplace announcement About PTI Engineered Plastics Inc section explicitly gives HQ. Other-entity headquarters elsewhere on site excluded.')}
observations={
'006116':'Own about page explicitly reports building headquarters in Red Bud IL in 2001, then later expansions and a current facility without explicitly confirming current HQ. Historical HQ event alone does not settle 2026 HQ.',
'004553':'Known Mylar domain returned a Cloudflare block; no US Limited Partnership-specific HQ witness obtained.',
'004554':'Own history names Dickerson present site and processing plants, without explicit headquarters designation.',
'004555':'Own homepage/about/contact inspected; company/contact location is not explicitly designated headquarters.',
'004556':'Own homepage and Find Us page supply location/contact evidence without HQ designation.',
'004557':'HTTP and HTTPS own homepage routes did not return usable HQ content.',
'004559':'Own PML company profile states Paris plant facilities and address, without HQ designation; Marugo parent HQ not assigned.',
'004561':'Own homepage/about page identify company operations without an explicit HQ city/state statement.',
'004563':'Own group locations page names German holding-company headquarters and Melamines sites; those do not designate exact Prefere Melamines LLC HQ.',
'004565':'Quad ink-manufacturing route blocked. Parent headquarters and Valdosta resin facility do not establish held Chemical Research/Technology Company HQ.',
'004566':'Own homepage/about/contact describe manufacturing, showroom and address without headquarters designation.',
'004571':'SK group overseas page identifies SK Primacor Americas Freeport location without explicit HQ designation; facility and parent HQ excluded.',
'004819':'Own global-locations page labels Closure Systems International Inc headquarters, not exact held Closure Systems International Americas Inc subsidiary.',
'004826':'Own contact page identifies corporate office in Oakville, Ontario for the IPEX group, without designating IPEX USA LLC HQ.',
'005102':'Known Dorel global page and Dorel Juvenile about route did not yield usable exact US entity HQ content.',
'005108':'Own homepage/about page inspected; no explicit headquarters designation obtained.',
'005117':'Own contact page explicitly labels Japanese Chiyoda Manufacturing Co Ltd as Headquarters, while USA address is company contact only.',
'005118':'Own homepage/contact inspected; company address does not explicitly establish HQ.',
'005119':'Own homepage/about history inspected; manufacturing facility/location is not explicitly HQ-designated.',
'005120':'Own homepage/contact/manufacturing-facilities pages inspected; locations were not explicitly designated headquarters.',
'006101':'Own homepage/company/contact pages give South Elgin address, without an explicit HQ label; other-company HQ search results excluded.',
'006102':'Own global homepage and guessed Chicago page did not provide Chicago LLC-specific HQ designation; global HQ excluded.',
'006105':'Own homepage/about/contact inspected; Northbrook address alone is not HQ evidence.',
'006106':'Own homepage/contact inspected; contact address is not expressly headquarters.',
'006107':'Own about page says headquartered in the Midwest and separately labels a McHenry Corporate Office; explicit city-specific HQ confirmation still needed under strict lane standard.',
'006108':'Own homepage/about inspected, guessed contact route denied; no explicit HQ city/state designation obtained.',
'006110':'Own homepage/about/contact inspected; company/facility addresses without explicit HQ designation.',
'006111':'Own homepage/about/contact give Elgin operating/contact address, without HQ designation.',
'006112':'Own locations page labels La Verpilliere France global Nemera HQ, while Buffalo Grove is a facility; subsidiary HQ not established.',
'006113':'Own homepage/contact inspected; address without explicit HQ label.',
'006115':'Own homepage/company-profile/contact pages identify Bellwood location without HQ designation.',
'006117':'Own USA homepage/company-data inspected; no exact TIGER Drylac USA Inc HQ designation; Austrian parent HQ excluded.',
'006118':'Own VRC locations page expressly says VRC is holding company of Vanseal, Ritus and Cascadia. VRC Milwaukee Corporate Office cannot be assigned to held Vanseal Corporation.',
'006122':'Own homepage/about/contact inspected; no explicit HQ city/state statement obtained.',
'006124':'Own global homepage/contact route inspected; no Clayens NP USA Inc-specific HQ designation obtained.',
'006127':'Own homepage/contact inspected; address does not expressly designate headquarters.',
'007004':'Own Vaupell homepage and contact route returned Cloudflare blocks; exact held Molding & Tooling Inc HQ remains unverified.',
'007009':'Known Gemini group homepage and Regency Plastics route returned Cloudflare blocks; parent HQ cannot settle held Ubly entity.',
'007010':'Known ORBIS acquisition release route returned Cloudflare block; parent HQ and Coleman plant not substituted.',
'007014':'Own homepage/about inspected; operations/manufacturing location not explicitly HQ-designated.',
'007024':'Own about history says a facility acts as headquarters after discussing Mt Clemens, but lists multiple current plant cities without unambiguous HQ city/state anchor.',
'007030':'DENSO official Systex profile route returned access restriction content; search lead describes manufacturing/administrative campus, not HQ designation.',
'007033':'HTTP own homepage inspected; HTTPS alternate route failed. No explicit HQ city/state statement obtained.',
'007034':'Own EFTEC global homepage/contact inspected; no exact EFTEC North America LLC HQ designation; group HQ excluded.',
'007035':'CIE USA guessed primary route returned not-found content; Century plant/parent location leads do not establish exact LLC HQ.'}
fields='org_id legal_name verdict outcome hq_city hq_state hq_country hq_county source_url source_class quote fetch_count reason settling_fact note raw_sha256'.split()
output=[]
for r in rows:
 oid=r['org_id'];key=oid[4:];rr=[x for x in receipts if x['org_id']==oid];v=dict.fromkeys(fields,'');v.update(org_id=oid,legal_name=r['legal_name'],fetch_count=len(rr))
 if key in positive:
  city,state,url,quote,note=positive[key];rc=next(x for x in rr if x['url']==url)
  v.update(verdict='HQ_FOUND',outcome='HQ_FOUND',hq_city=city,hq_state=state,hq_country='US',source_url=url,source_class='own_site',quote=quote,reason=note,note=note,raw_sha256=rc['raw_sha256'])
 else:
  observation=observations[key];fact=f'An explicit HQ city/state/country designation for exact held entity {r["legal_name"]}, distinct from contact/plant/parent addresses.'
  v.update(verdict='STILL_UNKNOWN',outcome='STILL_UNKNOWN',reason=observation,settling_fact=fact,note=observation)
  if rr:
   rc=rr[-1];v.update(source_url=rc['url'],source_class='own_site',raw_sha256=rc['raw_sha256'])
 output.append(v)
with (BASE/'verdicts.csv').open('w') as f:
 w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(output)
(BASE/'receipts.json').write_text(json.dumps({'observed_date':'2026-11-06','input_sha256':hashlib.sha256((BASE/'input.csv').read_bytes()).hexdigest(),'fetches':receipts},indent=2)+'\n')
print('written',len(output),'HQ_FOUND',len(positive),'STILL_UNKNOWN',len(output)-len(positive),'attempts',len(receipts))

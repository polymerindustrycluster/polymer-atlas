import csv,json,pathlib,hashlib
from research import BASE,CACHE
rows=list(csv.DictReader((BASE/'input.csv').open()))
receipts=[json.loads(p.read_text()) for p in sorted(CACHE.glob('*.json'))]
positive={
'ORG-004311':('Chino Hills','CA','https://lei.bloomberg.com/leis/view/549300PSHUGBOQ47QR63','registry','Headquarters Address (English) 13925 City Center Drive Suite 200 Chino Hills, California (US-CA), 91709 UNITED STATES','LEI 549300PSHUGBOQ47QR63 names exact Jacuzzi Brands LLC; last update 2026-04-13. Reported registry HQ, not privacy-office or plant address; parent should check currency against newer group locations.'),
'ORG-004346':('LaPorte','IN','https://www.renolit.com/fileadmin/renolit/corporate/Certificates/American_RENOLIT_Corporation_La_Porte/Certificate_US019775________Item_1-9C3INIF.pdf','own_site','American Renolit Corporation - HQ || 1207 E. Lincolnway LaPorte, IN 46350 USA','Own-hosted Bureau Veritas certificate US019775 issued 2024-06-28, expires 2027-08-06. Two excerpts from same table row on PDF page 2; HQ label belongs to exact entity.'),
'ORG-004348':('Boulder City','NV','https://amerityre.com/company/','own_site','From its headquarters and manufacturing facility in Boulder City, Nevada, Amerityre produces','Own company page explicitly labels headquarters; country US stated elsewhere on same page.'),
'ORG-004350':('Lewiston','ME','https://polyurethanelaboratories.com/poly-labs-fluid-focus/','own_site','manufacturing company headquartered in Lewiston, Maine, USA.','Poly Labs is held trade name of Polymer Laboratories & Solutions LLC; own release April 2022. Same own domain/document footer carries full legal entity name.'),
'ORG-004354':('Henderson','NV','https://lei.bloomberg.com/leis/view/2549007IFQ78ZCCHZO05','registry','Headquarters Address (English) 149 GIBSON RD STE M HENDERSON, Nevada (US-NV), 89014 UNITED STATES','Exact ARMOROCK LLC LEI 2549007IFQ78ZCCHZO05, last updated 2025-11-27; registry HQ takes precedence over unauthenticated plant/third-party Boulder City lead. Parent must independently verify.'),
'ORG-004383':('Elkhart','IN','http://deliveryconcepts.com/','own_site','CORPORATE HQ: 29385 County Road 20 Elkhart, IN','Exact Delivery Concepts Inc footer corporate HQ; no county inferred. US is the country of the explicit Indiana address.')}
reasons={
'ORG-004293':'DeLaval group entities PDF names West Agro Inc at Kansas City, MO, USA but does not label that address HQ. Settling fact: exact West Agro headquarters designation for that address.',
'ORG-004310':'Known website is global Hutchinson group; North American domain fetch failed. Global France HQ is not this held subsidiary. Settling fact: Hutchinson Sealing Systems Inc-specific HQ city and state.',
'ORG-004322':'Held status is merged. Appendix C tombstone rule bars re-homing. Settling fact: none for this pass; retain original shard regardless of successor HQ.',
'ORG-004326':'Known Royal Manufacturing and Royal Baths routes returned Cloudflare blocks; public leads do not settle exact current entity HQ. Settling fact: primary HQ city/state statement for Royal Baths Manufacturing Co.',
'ORG-004347':'Americh about/contact pages do not designate HQ; contact now names Jetta Corporation in Edmond, OK. Settling fact: explicit HQ for exact Americh Corp, not its acquirer or Charlotte plant.',
'ORG-004349':'Own homepage/contact identify Chemprene Inc at Beacon, New York; neither explicitly labels HQ, and held name is Chemprene LLC. Settling fact: exact LLC identity and explicit HQ city/state.',
'ORG-004351':'Pinal County primary page explicitly labels Eloy address a facility address, not HQ. Settling fact: Arizona Environmental Container Corp-specific HQ city/state.',
'ORG-004352':'Own about page provides plant/contact location only; no HQ designation. Settling fact: Armada Rubber Manufacturing Co-specific HQ city/state statement.',
'ORG-004355':'Own about page says based in Dalton, Georgia; this does not explicitly designate headquarters, and footer uses LLC versus held Inc. Settling fact: HQ and legal-entity identity confirmation for Arropol Chemicals Inc.',
'ORG-004356':'Own about/contact pages provide company location without HQ designation. Settling fact: Atlantic Footcare Inc-specific explicit HQ city/state.',
'ORG-004363':'Own about/contact pages give Melrose contact/manufacturing location, without HQ label. Settling fact: Carstens Industries Inc-specific explicit HQ city/state.',
'ORG-004364':'Known carstinbrands.com redirects to Wolf Home Products; Wolf headquarters cannot be assigned to held Carstin Brands LLC. Settling fact: Carstin Brands LLC-specific HQ designation.',
'ORG-004367':'Own website lists Rice Minnesota postal/contact address without HQ designation. Settling fact: Central Marble Products Inc-specific HQ city/state.',
'ORG-004368':'Own locations page labels Lamar main production facility and German group HQ; own mayor-visit article says Lamar is becoming headquarters, without settled effective date or explicit state in HQ sentence. Settling fact: completed US subsidiary HQ relocation/designation with city/state.',
'ORG-004370':'Known Chemelex about routes failed or returned navigation/error content. Houston leads and press datelines do not establish exact held LLC HQ. Settling fact: own-site or registry explicit Chemelex LLC HQ city/state.',
'ORG-004373':'Own about page discusses Marshall operations without headquarters designation. Settling fact: Comcast Urethane-specific explicit HQ city/state.',
'ORG-004374':'Known own-site route returned access denied; alternate Jina route blocked. Settling fact: explicit Comfort Revolution HQ city/state, distinct from Belmont manufacturing plant and parent HQ.',
'ORG-004375':'Own homepage gives Riverside contact address; history describes facilities/retail relocations without HQ designation. Settling fact: Complete Home Concepts Inc-specific HQ city/state.',
'ORG-004376':'Own single-page site gives Leesburg footer address without HQ designation. Settling fact: Composite Designs Inc-specific HQ city/state.',
'ORG-004379':'Own website returned access denied and Jina failed. Settling fact: primary explicit HQ city/state for exact Custom Fiberglass Molding Inc, not unrelated molders.',
'ORG-004380':'Own pages say based in Casper, Wyoming and call address shop/home base, without headquarters designation. Settling fact: exact Custom Fiberglass Inc HQ designation and legal identity, not just brand/shop address.',
'ORG-004381':'Own pages identify Salt Lake City manufacturing facility and earlier Sandy base, without current HQ label. Settling fact: Dadi Bathware-specific current explicit HQ city/state.',
'ORG-004382':'Guessed domain failed; OSHA record is establishment/site evidence, not HQ. Settling fact: Dakota Fiberglass Inc-specific HQ designation for city/state.',
'ORG-004384':'Own-domain route denied; Davie EDC article establishes Mocksville manufacturing relocation, not explicitly HQ. Settling fact: DFA US Inc-specific HQ city/state, not German parent HQ.'}
fields='org_id legal_name verdict hq_city hq_state hq_country hq_county source_url source_class quote fetch_count reason raw_sha256 outcome settling_fact note'.split()
output=[]
for r in rows:
 oid=r['org_id']; rr=[x for x in receipts if x['org_id']==oid]
 v=dict.fromkeys(fields,'');v.update(org_id=oid,legal_name=r['legal_name'],fetch_count=len(rr))
 if oid in positive:
  city,state,url,cl,quote,note=positive[oid]; rc=next(x for x in rr if x['url']==url)
  v.update(verdict='HQ_FOUND',outcome='HQ_FOUND',hq_city=city,hq_state=state,hq_country='US',source_url=url,source_class=cl,quote=quote,reason=note,note=note,raw_sha256=rc['raw_sha256'])
 else:
  reason=reasons[oid];v.update(verdict='STILL_UNKNOWN',outcome='STILL_UNKNOWN',reason=reason,note=reason,settling_fact=reason.split('Settling fact: ')[-1])
  if rr:
   rc=rr[-1];v.update(source_url=rc['url'],source_class='government_filing' if oid in ('ORG-004351','ORG-004382') else 'own_site',raw_sha256=rc['raw_sha256'])
 output.append(v)
with (BASE/'verdicts.csv').open('w') as f:
 w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(output)
(BASE/'receipts.json').write_text(json.dumps({'observed_date':'2026-11-06','input_sha256':hashlib.sha256((BASE/'input.csv').read_bytes()).hexdigest(),'fetches':receipts},indent=2)+'\n')
print('written',len(output),'HQ_FOUND',len(positive),'STILL_UNKNOWN',len(output)-len(positive),'raw fetch attempts',len(receipts))

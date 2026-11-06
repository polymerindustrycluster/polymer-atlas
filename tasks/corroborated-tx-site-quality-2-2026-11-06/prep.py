"""Freeze re-observed source atoms and the exact quality packet; no canonical writes."""
import csv,hashlib,json,re
from pathlib import Path
from research import found
P=Path(__file__).resolve().parent;ROOT=P.parents[1]
def read(p):
    with open(p,newline='',encoding='utf-8-sig') as f:return list(csv.DictReader(f))
def write(p,rows):
    with open(p,'w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=rows[0],lineterminator='\n');w.writeheader();w.writerows(rows)
frame=read(P/'input.csv');raw=read(P/'rawcheck.csv');byid={r['site_id']:r for r in frame}
assert len(frame)==len(byid)==38
holds={
'015000':'Obtain a plant/unit-specific Lolita production witness linking the filed Inteplast establishment, rather than inferring the excluded IBS unit from broad historical campus activity.',
'015001':'Obtain a raw operator-issued Kilgore manufacturing witness for Southern Plastics/CSI; group products alone do not locate the activity.',
'015003':'Obtain a Brownsville plant-specific polymer manufacturing statement; Plant8 plus company-wide injection molding menu does not assign that activity to this establishment.',
'015004':'Obtain a raw New Braunfels production witness and legal/operator bridge for the group page; no group parent relationship is held.',
'015005':'Obtain a raw Katy plant manufacturing witness; own route availability did not settle activity at the filed site.',
'015006':'Obtain an operator-issued Grand Prairie production witness distinguishing manufacture from distribution.',
'015007':'Obtain a clean operator-issued Odessa processing witness; the fetched own page includes unrelated SEO/spam material, so source integrity is unresolved.',
'015008':'Bridge the filed KB Dallas legal operator to the differently styled KB Components USA/OY manufacturing page; no parent or alias invented.',
'015012':'Obtain raw Parker-issued Mansfield plant activity evidence; failed own-page routes are availability only.',
'015013':'Locate StarPak manufacturing at9690W Wingfoot rather than assume the older9333Baythorne plant or company-wide products resolve this street.',
'015014':'Obtain a raw Lone Star Garland production witness; the Inteplast historical acquisition/rebrand and route failure do not assign manufacturing to this plant.',
'015015':'Obtain a Westlake-issued Wichita Falls production witness under the already-held parent relationship.',
'015016':'Obtain polymer manufacture/binder-resin production evidence for the Cleburne establishment; metal-can activity and a chemical-company address do not settle polymer scope.',
'015018':'Resolve own2720Tillar versus filed2710Tillar physical-plant distinction and obtain raw plant activity; route failures do not settle either question.',
'015019':'Obtain raw Solmax plant activity at19103Gundle plus legal/operator bridge where needed; search-index text and the fetched title-only page are not raw manufacturing evidence.',
'015400':'Obtain operator-issued Ennis manufacturing evidence; global ADS pipe activity does not locate the process.',
'015401':'Bridge held DELFINGEN-TX to the group plant/sales-office listing and establish polymer activity at the El Paso unit; no new parent relation inferred.',
'015403':'Resolve filed1200TrinityStreet versus indexedown1200TrinityDrive and obtain raw Mission plant manufacturing text before restating this address atB.',
'015404':'Obtain raw Genpak Longview manufacturing witness; failed routes are availability only.',
'015405':'Assign polymer manufacturing specifically to the Sulphur Springs headquarters rather than infer it from D6 company-wide manufacturing/recycling/distribution activity.',
'015406':'Obtain a raw Altium-owned Sherman manufacturing witness; authorship of an unverified microsite is not assumed.',
'015407':'Obtain a raw Plastipak Highlands production witness; an indexed resin-selling/sustainability facility reference alone does not establish plant manufacturing.',
'015408':'Obtain ADS-issued Yoakum manufacturing evidence distinguishing the brochure plant/distribution symbols; do not infer a process from an address or map legend.',
'015410':'Assign polymer manufacturing specifically to the Sanderson Houston site; global PVC products and contact address alone are insufficient.',
'015414':'Obtain Graham-issued Rockwall plant manufacturing evidence rather than infer process from a material-handler job or global products.',
'015416':'Obtain polymer activity at the UFP El Paso establishment; historical molded-fiber expansion and warehouse/fabrication descriptions do not settle polymer manufacture.',
'015418':'Obtain Fischbach-issued polymer manufacture at1901HuttonCourt, distinguishing office/contact function from a plant.'}
upgraded={r['site_id'] for r in raw};assert len(upgraded)==11 and set(holds)=={s.removeprefix('SITE-') for s in byid if s not in upgraded}
ita={r['establishment_id']:r for r in read(ROOT/'tasks/osha-ita-2026-11-01/establishments.csv')};osha={r['est_key']:r for r in read(ROOT/'tasks/osha-spine-2026-11-01/establishments.csv')}
packet=[];gov=[];edits=[];verdicts=[]
def evidence(sid,claim,detail,cls,source,notes):
    packet.append(dict(record_table='sites',record_id=sid,claim_type=claim,claim_detail=detail,source_class=cls,source_ref=source,observed_date='2026-11-06',tier_effect='supports_B',created_by='atlas-L6-corr-ca-tx',notes=notes,evidence_id=f'EVD-{188100+len(packet):06d}'))
for r in frame:
 sid=r['site_id']
 if sid not in upgraded:
    verdicts.append(dict(site_id=sid,verdict='STILL_UNCERTAIN',action='HOLD_C',settling_fact=holds[sid.removeprefix('SITE-')],own_source=''));continue
 own=[x for x in raw if x['site_id']==sid]
 for x in own:
    t=Path(x['cache_file']).read_text();assert found(t,x['quote']) and hashlib.sha256(t.encode()).hexdigest()==x['raw_sha256']
 m=re.search(r'establishment (\d+)',r['sources'])
 if m:
    g=ita[m[1]];kind='ITA';key=m[1];name=g['establishment_name'];operator=g['company_name'];street=g['street'];city=g['city'];zip5=g['zip5'];code=g['naics_code'];date=g['date_submitted'];description=g['industry_description']
 else:
    key=re.search(r'OSHA:(OSHAE-[a-z0-9]+)',r['notes'])[1];g=osha[key];kind='OSHA';name=operator=g['name'];street=g['street'];city=g['city'];zip5=g['zip'];code=g['naics_latest'];date=g['latest_inspection'];description=''
 assert [street,city,zip5,code]==[r['street_address'],r['city'],r['zip'],r['naics_primary']],sid
 gov.append(dict(site_id=sid,source_kind=kind,source_id=key,operator=operator,establishment_name=name,street=street,city=city,state='TX',zip=zip5,naics=code,source_date=date,industry_description=description,source_ref=r['sources']))
 note=f'Re-observed inherited packet vintage2026-11-01 under controller grant; source as-of {date}; {kind}:{key}. No fresh bulk-download or current-operation claim.'
 evidence(sid,'existence',f'{name} at {street}', 'government_filing',r['sources'],note)
 evidence(sid,'address',f'{street}, {city}, TX {zip5}; county unverified','government_filing',r['sources'],note)
 evidence(sid,'code',f'{code} (government_filing)','government_filing',r['sources'],note)
 evidence(sid,'parent',f'Filed company {operator or "not populated"}; establishment {name}; existing Atlas operator {r["org_id"]}','government_filing',r['sources'],note+' Existing operator link also independently checked against the raw own page; no organization relationship change.')
 for x in own:evidence(sid,'scope',x['quote'],'own_site',x['source_ref'],x['notes'])
 urls=list(dict.fromkeys(x['source_ref'] for x in own));new_sources=r['sources']+'; '+'; '.join(urls)
 edits.extend([dict(site_id=sid,field='verification_tier',old='C',new='B'),dict(site_id=sid,field='sources',old=r['sources'],new=new_sources)])
 verdicts.append(dict(site_id=sid,verdict='VERIFIED',action='RESTATEMENT_C_TO_B',settling_fact='Raw operator-issued city/activity witness plus re-observed site-grade government identity/address/code; no current-operation assertion.',own_source='; '.join(urls)))
assert len(packet)==57 and len(edits)==22 and len(gov)==11
for name,rows in [('verdicts.csv',verdicts),('edits.csv',edits),('evidence_packet.csv',packet),('government-review.csv',gov)]:write(P/name,rows)
blind=[]
for g in gov:
    rs=[r for r in raw if r['site_id']==g['site_id']]
    blind.append({**g,'own_urls':'; '.join(dict.fromkeys(r['source_ref'] for r in rs)),'own_cache_files':'; '.join(dict.fromkeys(r['cache_file'] for r in rs))})
write(P/'blind-input.csv',blind)
(P/'reserved-ids.json').write_text(json.dumps(dict(evidence_block='EVD-188100–EVD-188499',allocated=[r['evidence_id'] for r in packet],unused_remain_reserved=True),indent=2)+'\n')
print('PASS packet38=11Brestatements27holds;22cells57EVD,government11/11,raw13/13')

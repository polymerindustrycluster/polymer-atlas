#!/usr/bin/env python3
"""MS skimpy-state wave (2026-11-04). Run once from repo root. IDs tiled from the owner-supplied ledger (no main rescan)."""
# ---- shared builder (skimpy-state wave, 2026-11-04) -------------------------
import csv, sys
D = 'data'; DATE = '2026-11-04'; BY = 'grok-skimpy-wave'
FRSU = 'https://frs-public.epa.gov/ords/frs_public2/frs_rest_services.get_facilities?registry_id='
def frs(i): return f'EPA FRS registry {i} ({FRSU}{i})'
def ita(i, name): return f'OSHA ITA Form 300A CY2025 establishment {i} ({name})'
def osha(nr): return f'OSHA inspection {nr}, https://www.osha.gov/ords/imis/establishment.inspection_detail?id={nr}'
def rd(p):
    with open(p, newline='') as f: r = csv.reader(f); h = next(r); return h, list(r)
def app(p, header, rows):
    h, _ = rd(p); assert h == header, p
    with open(p, 'a', newline='') as f:
        w = csv.writer(f, lineterminator='\n'); [w.writerow([r.get(c, '') for c in h]) for r in rows]
def fed_of(s):
    out = [('registry', frs(s['frs']))] if s.get('frs') else []
    if s.get('ita'): out.append(('government_filing', ita(s['ita'], s.get('ita_name', s['name']))))
    for nr in s.get('osha', []): out.append(('government_filing', osha(nr)))
    return out
def build(ST, PKT, ORG0, SITE0, EVD0, ORGS, SITES):
    oh, _ = rd(f'{D}/organizations_{ST}.csv'); sh, _ = rd(f'{D}/sites_{ST}.csv'); eh, _ = rd(f'{D}/evidence_sites_{ST}.csv')
    lh, _ = rd(f'{D}/registry_links.csv')
    ids = {}; org_rows = {}; ev = {}; links = []; st = dict(eid=EVD0)
    sites_by_key = {s['key']: s for s in SITES}
    def E(f, table, rid, claim, detail, cls, ref, eff, note=''):
        if cls == 'registry': note = (f'FRS REST fetched {DATE} (copy: {PKT}/frs_fresh_{DATE}.json). ' + note).strip()
        ev.setdefault(f, []).append(dict(evidence_id=f"EVD-{st['eid']:06d}", record_table=table, record_id=rid, claim_type=claim, claim_detail=detail,
            source_class=cls, source_ref=ref, observed_date=DATE, tier_effect=eff, created_by=BY, notes=note)); st['eid'] += 1
    nid = ORG0
    for o in ORGS:
        oid = f'ORG-{nid:06d}'; nid += 1; ids[o['key']] = oid
        s = sites_by_key[o['key']]; fed = fed_of(s); gov = [r for c, r in fed if c == 'government_filing'][0]
        row = {k: v for k, v in o.items() if k in oh}
        row.update(org_id=oid, ring_primary=o.get('ring_primary', '1'), hq_country='US', hq_in_scope='national_us', pic_relevance='potential_member', status='active',
            naics_primary_source_type='government_filing', ownership_type=o.get('ownership_type', 'private_company'),
            sources='; '.join(([o['own']] if o.get('own') else []) + [r for _, r in fed]), verification_tier='C', last_verified=DATE, created_by=BY,
            notes=f"Created {DATE} in the {ST} skimpy-state wave ({PKT}) from a two-source federal overlap (multi-source queue row {s['cluster']}). Tier C at birth per AGENTS s3 step 5. " + o['notes'],
            last_activity_evidence_date=DATE, liveness_signal='operating_evidence', monitor_watch='false')
        oc = 'own_site' if o.get('own') else 'government_filing'; oref = o.get('own') or gov
        sh_ = o.get('shard', ST); org_rows.setdefault(sh_, []).append(row)
        ef = f'evidence_organizations_{sh_}.csv'
        E(ef,'organizations',oid,'existence',f"legal/trade name {o['legal_name']}",oc,oref,'supports_C')
        E(ef,'organizations',oid,'address',f"HQ {o.get('hq_city') or 'not evidenced'} {o.get('hq_state','')}".strip(),oc,oref,'supports_C')
        E(ef,'organizations',oid,'scope',f"ring_primary {row['ring_primary']} via {o.get('processes') or o['naics_primary']}",oc,oref,'supports_C')
        E(ef,'organizations',oid,'code',f"naics_primary {o['naics_primary']} ({o['naics_primary_source_name']})",'government_filing',gov,'supports_C')
        E(ef,'organizations',oid,'activity',f'operating at its {ST} establishment','government_filing',gov,'supports_C')
        E(ef,'organizations',oid,'liveness',f'active at {DATE}' + (' (own site live)' if o.get('own') else ' (latest federal record)'),oc,oref,'supports_C')
    sid = SITE0; site_rows = []
    for s in SITES:
        sidn = f'SITE-{sid:06d}'; sid += 1; ids['site:' + s['key']] = sidn
        oid = ids.get(s['org'], s['org']); tier = s['tier']; eff = 'supports_B' if tier == 'B' else 'supports_C'
        own = s.get('own', ''); fed = fed_of(s); reg = fed[0][1]; gov = [r for c, r in fed if c == 'government_filing']
        site_rows.append(dict(site_id=sidn, org_id=oid, site_name=s['name'], site_type=s.get('type', 'manufacturing_plant'), city=s['city'], state=ST, zip=s['zip'], county=s['county'],
            ring_primary=s.get('ring', '1'), naics_primary=s['naics'], naics_primary_source_type='government_filing', naics_confidence=s.get('conf', 'medium'),
            processes=s.get('proc', ''), materials=s.get('mat', ''), operating_status='active', sources='; '.join(([own] if own else []) + [r for _, r in fed]),
            verification_tier=tier, last_verified=DATE, created_by=BY,
            notes=f"Created {DATE} in the {ST} skimpy-state wave ({PKT}) from a two-source federal overlap (multi-source queue row {s['cluster']}; federal records, name + street agree). " + s['notes'],
            street_address=s['street'], county_source='physical_address', country='US'))
        if s.get('frs'): links.append(dict(org_id=oid, registry='FRS', registry_id=s['frs'], match_basis=f"frs_rest_registry_id_name_street_match:{sidn}", as_of=DATE, site_id=sidn))
        ef = f'evidence_sites_{ST}.csv'
        E(ef,'sites',sidn,'existence',f"{s['name']} at {s['street']}, {s['city']}",'government_filing',gov[0],eff,'federal establishment record; name + street agree with FRS')
        if own: E(ef,'sites',sidn,'existence',f"{s['name']} named by the operator at {s['city']}, {ST}",'own_site',own,eff)
        E(ef,'sites',sidn,'address',f"{s['street']}, {s['city']}, {ST} {s['zip']} ({s['county']} County, from the physical address)",fed[0][0],reg,'supports_C','county from the physical address (Census geocoder or a city wholly in one county)')
        E(ef,'sites',sidn,'address',f"{s['street']}, {s['city']}, {ST} {s['zip']}",'government_filing',gov[-1],eff)
        E(ef,'sites',sidn,'code',f"naics_primary {s['naics']}",'government_filing',gov[0],eff)
        E(ef,'sites',sidn,'scope',f"ring_primary {s.get('ring','1')} ({s.get('proc') or 'NAICS ' + s['naics']})",'own_site' if own else 'government_filing',own or gov[0],eff,
          '' if own else 'scope rests on the federal NAICS only; no own-site read')
        E(ef,'sites',sidn,'parent',f'org_id {oid}','own_site' if own else fed[0][0],own or reg,eff if own else 'supports_C')
        E(ef,'sites',sidn,'activity','manufacturing operations at the site','government_filing',gov[-1],eff)
        E(ef,'sites',sidn,'liveness','active: latest federal activity record' + (f' and live own page {DATE}' if own else ''),'own_site' if own else 'government_filing',own or gov[-1],eff)
    if '--dry-run' in sys.argv:
        print({k: len(v) for k, v in org_rows.items()}, len(site_rows), st['eid'] - EVD0, len(links)); return
    for k, v in org_rows.items(): app(f'{D}/organizations_{k}.csv', oh, v)
    app(f'{D}/sites_{ST}.csv', sh, site_rows)
    for f, rows in ev.items(): app(f'{D}/{f}', eh, rows)
    app(f'{D}/registry_links.csv', lh, links)
    print('ids', ids, 'evidence', EVD0, '..', st['eid'] - 1, 'links', len(links))
def O(key, legal, city, county, naics, src, proc, mat, web, own, desc, notes, conf='high', trade='', parent='', et='corporation_private', ring='1', st=None):
    return dict(key=key, legal_name=legal, trade_names=trade, ultimate_parent_name=parent, entity_type=et, ring_primary=ring, hq_city=city, hq_state=st or ST_, hq_county=county, shard=st or ST_,
                naics_primary=naics, naics_primary_source_name=src, naics_confidence=conf, processes=proc, materials=mat, website=web, own=own, description_1line=desc, notes=notes)
def S(key, cluster, name, city, zip_, county, street, naics, proc, mat, own, frs_, ita_='', ita_name='', osha_=(), notes='', org=None, tier='C', type_='hq_and_plant', ring='1', conf='high'):
    return dict(key=key, org=org or key, cluster=cluster, name=name, type=type_, city=city, zip=zip_, county=county, street=street, naics=naics, conf=conf, proc=proc, mat=mat, ring=ring,
                tier=tier, own=own, frs=frs_, ita=ita_, ita_name=ita_name, osha=list(osha_), notes=notes)
ST_ = 'MS'
I = 'OSHA ITA CY2025 establishment '
ORGS = [
 O('adlam','Adlam Films, LLC','Shannon','Lee','326112',I+'345402','extrusion_film_blown;coating_applying;printing_decorating_plastics','polyethylene_pe;films_flexible_packaging','https://www.adlamfilms.com/','https://www.adlamfilms.com/','Shannon, MS family-owned film extruder, coater and printer (insulation, construction, packaging films).','Own site.', et='llc'),
 O('kaycan','KP Building Products (Kaycan Ltd.)','Holly Springs','Marshall','326199',I+'1507322','extrusion_profile','pvc','https://www.kpproducts.com/','https://www.saint-gobain-northamerica.com/sites/default/files/2024-11/Kaycan_HollySpringsMS_Nov2024.pdf','Vinyl siding and accessories maker; Holly Springs, MS plant.','Parent-group fact sheet (Saint-Gobain North America, Nov 2024) for the Holly Springs vinyl siding plant. Real HQ in Canada; org placed in MS shard with the plant as hq_city - integrator check; possible link to held CertainTeed ORG-002738 not made.', conf='medium', parent='Saint-Gobain'),
 O('corelle','Corelle Brands LLC','Byhalia','Marshall','326199',I+'1474239','molding_unspecified','thermoplastics','https://www.corelle.com/','','Housewares company with a manufacturing and distribution facility in Byhalia, MS.','Federal sources only (FRS + ITA, NAICS 326199). Real HQ Rosemont IL; org placed in MS shard - integrator check. Process low.', conf='low', et='llc'),
 O('aircruisers','Air Cruisers Company, LLC','Liberty','Amite','336413',I+'1084554','plastics_fabrication_welding','other_specified_in_notes','https://www.safran-group.com/','','Safran Aerosystems subsidiary making evacuation slides, life rafts and life vests; Liberty, MS plant.','Federal sources (FRS + ITA; NAICS 326199/326299). Coated-fabric inflatables fabrication researcher_inferred, low. Safran locations page lists Liberty at 269 Main St (FRS street 4575 Dix Dr) - integrator check.', conf='low', parent='Safran SA', et='llc'),
 O('nov','NOV Inc.','Houston','Harris','333132','EPA FRS 110037602920','composites_filament_winding','composites_frp;epoxy','https://www.nov.com/','','Energy equipment company whose Fiber Glass Systems unit makes FRP pipe.','Org created only to parent the Iuka MS FRP plant (no NOV org held). Federal sources only.', conf='medium', et='corporation_public', st='TX'),
 O('ifs','Independent Furniture Supply Co., Inc.','Tupelo','Lee','326150','EPA FRS 110013841432','foam_fabrication','polyurethane_pu;foams_polymeric','http://www.independentfurnituresupply.com/','http://www.independentfurnituresupply.com/','Tupelo, MS polyurethane foam fabricator for upholstered furniture.','Own site: largest foam fabricator in the Southeast, 3609 W Jackson St, Tupelo.'),
 O('confortaire','Confortaire, Inc.','Tupelo','Lee','326150','EPA FRS 110002225716','foam_fabrication','polyurethane_pu;foams_polymeric','https://confortaire.net/','https://confortaire.net/','Tupelo, MS custom foam and fiber fabricator (mattress, pillow and furniture components).','Own site.'),
 O('hybrid','Hybrid Plastics, Inc.','Hattiesburg','Forrest','325211','EPA FRS 110020742810','compounding_unspecified','polymer_additives','https://www.hybridplastics.com/','https://www.hybridplastics.com/history-mission/','Hattiesburg, MS maker of POSS nanostructured chemicals for plastics and coatings.','Own history page: manufacturing facility in Hattiesburg. Ring 2 (polymer additives); process low.', conf='low', ring='2'),
]
SITES = [
 S('dart','QMS-MS-00','Dart Container - Quitman','Quitman','39355','Clarke','197 Harris Ave','326140','foam_extrusion;thermoforming_unspecified','polystyrene_ps_hips;foams_polymeric','https://corporate.dartcontainer.com/location/quitman-ms/','110002227741','1441299','DART CONTAINER CORPORATION LLC',['345813844'],'Placed under ORG-002441. Own Dart location page: Quitman MS foam cups/containers. FRS county Clarke.', org='ORG-002441', tier='B', type_='manufacturing_plant'),
 S('kaycan','QMS-MS-03','KP Building Products - Holly Springs','Holly Springs','38635','Marshall','820 Highway 7 N','326199','extrusion_profile','pvc','https://www.saint-gobain-northamerica.com/sites/default/files/2024-11/Kaycan_HollySpringsMS_Nov2024.pdf','110002338792','1507322','KP BUILDING PRODUCTS',['343868212'],'FRS county Marshall.', type_='manufacturing_plant', conf='medium'),
 S('corelle','QMS-MS-04','Corelle Brands - Byhalia','Byhalia','38611','Marshall','190 Norfolk Southern Way','326199','molding_unspecified','thermoplastics','','110070594990','1474239','CORELLE BRANDS LLC',[],'Federal only (FRS + ITA). FRS county Marshall.', type_='manufacturing_plant', conf='low'),
 S('sherwin','QMS-MS-06','Sherwin-Williams - Olive Branch (Magnolia Dr)','Olive Branch','38654','DeSoto','10136 Magnolia Dr','325510','coating_formulation','coatings','','110000375692','1460382','SHERWIN-WILLIAMS COMPANY',[],'Placed under ORG-000132. Federal only (FRS + ITA; NAICS 325510/325991) - tier C. The 2009 closure news concerns a different (Miller Rd) plant. FRS county DeSoto. Ring 2.', org='ORG-000132', type_='manufacturing_plant', ring='2', conf='medium'),
 S('sonoco','QMS-MS-07','Sonoco Protective Solutions - Tupelo','Tupelo','38801','Lee','2612 President Extended','326140','foam_molding_bead','polystyrene_ps_hips;foams_polymeric','','110001471915','1528148','SONOCO PROTECTIVE SOLUTIONS INC',[],'Placed under ORG-003930 Sonoco. Federal only - tier C. FLAG: state permit shows ThermoSafe Technologies taking coverage Aug 2026 (divestiture) - operator may have changed; integrator check. FRS county Lee.', org='ORG-003930', type_='manufacturing_plant', conf='medium'),
 S('wpipe','QMS-MS-08','Westlake Pipe & Fittings - Booneville','Booneville','38829','Prentiss','401 Industrial Park Rd','326122','extrusion_pipe_tube','pvc','https://www.westlake.com/booneville','110071435845','140677','WESTLAKE PIPE AND FITTINGS CORPORATION',[],'Placed under ORG-003067 Westlake Corporation. Own westlake.com Booneville page. FRS county Prentiss.', org='ORG-003067', tier='B', type_='manufacturing_plant'),
 S('adlam','QMS-MS-09','Adlam Films - Shannon','Shannon','38868','Lee','62 County Road 520','326112','extrusion_film_blown;coating_applying;printing_decorating_plastics','polyethylene_pe;films_flexible_packaging','https://www.adlamfilms.com/','110030740857','345402','ADLAM FILMS LLC',[],'FRS county Lee.'),
 S('sterling','QMS-MS-10','Sterling Specialty Chemicals - Aberdeen','Aberdeen','39730','Monroe','10930 Darracott Rd','325211','polymerization','other_specified_in_notes','https://www.sterlingspec.com/capacity-expansion-at-aberdeen-mississippi-plant/','110000377690','1414476','STERLING SPECIALTY CHEMICALS US LLC',[],'Placed under ORG-004123. Own news page: Aberdeen plant capacity expansion (polyacrylamide / acrylamide). Material: polyacrylamide. FRS county Monroe. Ring 2.', org='ORG-004123', tier='B', type_='manufacturing_plant', ring='2', conf='medium'),
 S('bakelite','QMS-MS-11','Bakelite Chemicals - Taylorsville','Taylorsville','39168','Smith','13136 Hwy 28 W','325211','polymerization','phenolic;melamine_urea_formaldehyde','','110000590691','1089007','BAKELITE CHEMICALS LLC - TAYLORSVILLE FACILITY',[],'Placed under ORG-000696. Federal only (FRS + ITA) - tier C. Phenolic/amino resins for wood panels researcher_inferred. FRS county Smith. Ring 2.', org='ORG-000696', type_='manufacturing_plant', ring='2', conf='medium'),
 S('aircruisers','QMS-MS-12','Air Cruisers (Safran Aerosystems) - Liberty','Liberty','39645','Amite','4575 Dix Dr','336413','plastics_fabrication_welding','other_specified_in_notes','','110000496856','1084554','AIR CRUISERS COMPANY',[],'Federal only (FRS + ITA). FRS county Amite.', type_='manufacturing_plant', conf='low'),
 S('nov','QMS-MS-14','NOV Fiber Glass Systems - Iuka','Iuka','38852','Tishomingo','751 County Road 989','326199','composites_filament_winding','composites_frp;epoxy','','110037602920','1467691','FIBER GLASS SYSTEMS LP, IUKA FRP FACILITY',[],'Federal only (FRS + ITA; MDEQ Title V). FRS county Tishomingo.', type_='manufacturing_plant', conf='medium'),
 S('ifs','QMS-MS-15','Independent Furniture Supply - Tupelo','Tupelo','38801','Lee','3609 W Jackson St','326150','foam_fabrication','polyurethane_pu;foams_polymeric','http://www.independentfurnituresupply.com/','110013841432','','',['345729560'],'FRS county Lee.'),
 S('confortaire','QMS-MS-16','Confortaire - Tupelo','Tupelo','38804','Lee','2133 S Veterans Blvd','326150','foam_fabrication','polyurethane_pu;foams_polymeric','https://confortaire.net/','110002225716','','',['346380744'],'FRS county Lee.'),
 S('hybrid','QMS-MS-18','Hybrid Plastics - Hattiesburg','Hattiesburg','39401','Forrest','55 W L Runnels Industrial Dr','325211','compounding_unspecified','polymer_additives','https://www.hybridplastics.com/history-mission/','110020742810','','',['344202767'],'FRS county Forrest. Ring 2.', conf='low', ring='2'),
 S('hsm','QMS-MS-19','HSM - Verona Fab (458)','Verona','38879','Lee','278 CDF Blvd, Bldg 2','326150','foam_fabrication','polyurethane_pu;foams_polymeric','','','1310375','HSM Verona Fab (458)',['344254925'],'Placed under ORG-004394 Hickory Springs Manufacturing (HSM). Federal only (ITA + OSHA) - tier C. No FRS - no link. County Lee (Verona).', org='ORG-004394', type_='manufacturing_plant', conf='medium'),
]
if __name__ == '__main__': build('MS', 'tasks/ms-skimpy-2026-11-04', 4873, 6059, 23395, ORGS, SITES)

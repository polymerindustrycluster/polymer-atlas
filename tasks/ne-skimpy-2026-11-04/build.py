#!/usr/bin/env python3
"""NE skimpy-state wave (2026-11-04). Run once from repo root. IDs tiled from the owner-supplied ledger (no main rescan)."""
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
ST_ = 'NE'
I = 'OSHA ITA CY2025 establishment '
ORGS = [
 O('plastilite','Plastilite Corporation','Omaha','Douglas','326140',I+'216111','foam_molding_bead','polystyrene_ps_hips;foams_polymeric;recycled_content_pcr_pir','https://www.plastilite.com/','https://www.plastilite.com/blog/foaming-at-the-mouth-edition-4-1','Omaha, NE molder of EPS foam packaging and coolers (Integritemp, REfoam brands).','Own blog (2024-06-10): first recycled-content EPS cooler molded at the Omaha plant.'),
 O('diamond','Diamond Plastics Corporation','Grand Island','Hall','326122',I+'551193','extrusion_pipe_tube','pvc','https://www.dpcpipe.com/','https://www.dpcpipe.com/plants-and-loading-charts.php','Grand Island, NE maker of PVC water, sewer and irrigation pipe.','Own plants page: Grand Island NE (HQ + plant, 1212 Johnstown Rd) and Golconda NV. Golconda plant not created in this NE wave.'),
 O('snyder','Snyder Industries, Inc.','Lincoln','Lancaster','326199',I+'695401','rotational_molding','polyethylene_pe','https://www.snydernet.com/','https://www.snydernet.com/about','Lincoln, NE rotational molder of polyethylene tanks, IBC totes and bins.','Own about page: Lincoln plants incl. world\'s largest rotomolding machine; corporate HQ 6940 O St, Lincoln. Distinct from held ORG-001116 Snyder Manufacturing (Dover OH).'),
 O('hexagon','Hexagon Agility Inc.','Lincoln','Lancaster','326199','EPA FRS 110069463020','composites_filament_winding','composites_carbon;polyethylene_pe','https://hexagonagility.com/','https://hexagonagility.com/contact-2','Maker of Type 4 composite gas cylinders and Mobile Pipeline gas transport modules; Lincoln NE plants.','Own contact page and ISO 14001 certificate: cylinder manufacturing at 5117 and 5150 NW 40th St, Lincoln. Corporate address Salisbury NC; org HQ taken as Lincoln (manufacturing HQ) - medium. Parent Hexagon Composites ASA (not created).', conf='medium', parent='Hexagon Composites ASA'),
 O('gdots','General Dynamics Ordnance and Tactical Systems, Inc.','Lincoln','Lancaster','336419','EPA FRS 110000615488','composites_filament_winding;composites_prepreg_autoclave','composites_carbon;composites_thermoset','https://www.gdots.com/','https://www.gdots.com/lincoln-home/','Defense company whose Lincoln, NE operations make composite motor cases, pressure vessels and launch tubes.','Org created only to parent the Lincoln composites plant (no General Dynamics org held). Real HQ is outside NE (St. Petersburg FL) - org placed in the NE shard with hq_city Lincoln as manufacturing location; integrator check.', conf='medium', parent='General Dynamics Corporation', et='corporation_public'),
 O('wilk','Wilkinson Manufacturing Co.','Fort Calhoun','Washington','326199','EPA FRS 110015848680','extrusion_profile;thermoforming_unspecified','thermoplastics','https://www.wilkmfg.com/','https://www.wilkmfg.com/','Fort Calhoun, NE maker of custom plastic and aluminum extrusions and plastic packaging.','Website named in directories; processes researcher_inferred - medium.', conf='medium'),
 O('majors','Majors Plastics, Inc.','Omaha','Douglas','326199',I+'1430558','injection_molding;insert_overmolding;assembly_secondary_ops','thermoplastics','https://majorsplastics.com/','https://majorsplastics.com/about/','Omaha, NE custom injection molder and contract manufacturer (incl. cleanroom molding).','Own about page.'),
 O('yasufuku','Yasufuku U.S.A., Inc.','Lincoln','Lancaster','326299',I+'1463668','injection_molding;rubber_molding_compression;blow_molding','elastomers_rubber;thermoplastics','https://www.yuinc.com/','https://www.yuinc.com/','Lincoln, NE custom molder of rubber and plastic parts (injection, compression, blow molding).','Own site.', conf='medium'),
 O('premier','Premier Plastics, Inc.','Omaha','Douglas','326199',I+'1363299','injection_molding;insert_overmolding','thermoplastics','https://www.premierplasticsinc.com/','https://www.premierplasticsinc.com/injection-molding','Omaha, NE custom injection molder (tooling, insert/overmolding, short runs).','Own site: 4880 S 134th St, Omaha.'),
]
SITES = [
 S('airlite','QMS-NE-00','Airlite Plastics - Omaha (HQ & plant)','Omaha','68110','Douglas','6110 Abbott Dr','326140','foam_molding_bead;injection_molding','polystyrene_ps_hips;foams_polymeric','https://www.airliteplastics.com/contact-us/','110002358902','1455940','AIRLITE PLASTICS CO',['347657389'],'Placed under ORG-002553 Airlite Plastics Co. Own contact page (corporate office 6110 Abbott Dr) and Fox Blocks (Airlite division) product manual naming Omaha as corporate office and Midwest manufacturing location. FLAG: ORG-002553 records HQ Nazareth PA - own page says Omaha; integrator check.', org='ORG-002553', tier='B', type_='hq_and_plant'),
 S('west','QMS-NE-01','West Pharmaceutical Services - Kearney','Kearney','68845','Buffalo','923 W Railroad St','326299','rubber_molding_compression','elastomers_rubber','https://www.westpharma.com/global-locations','110015738264','1102245','WEST PHARMACEUTICAL SERVICES',['348351347'],'Placed under ORG-002772. Own global-locations page: Kearney, compression molding of rubber stoppers, closures, plungers. FRS county Buffalo.', org='ORG-002772', tier='B', type_='manufacturing_plant'),
 S('plastilite','QMS-NE-03','Plastilite - Omaha','Omaha','68152','Douglas','9409 N 45th St','326140','foam_molding_bead','polystyrene_ps_hips;foams_polymeric;recycled_content_pcr_pir','https://www.plastilite.com/blog/foaming-at-the-mouth-edition-4-1','110012656116','216111','PLASTILITE CORPORATION',[],'FRS county Douglas.'),
 S('diamond','QMS-NE-04','Diamond Plastics - Grand Island','Grand Island','68803','Hall','1212 Johnstown Rd','326122','extrusion_pipe_tube','pvc','https://www.dpcpipe.com/plants-and-loading-charts.php','110001516501','551193','DIAMOND PLASTICS CORP',[],'FRS county Hall.'),
 S('snyder','QMS-NE-05','Snyder Industries - Lincoln (Fremont St)','Lincoln','68504','Lancaster','4700 Fremont St','326199','rotational_molding','polyethylene_pe','https://www.snydernet.com/about','110011042059','695401','SNYDER INDUSTRIES',[],'Own page names Lincoln plants but not this street; street from FRS/ITA. FRS county Lancaster.', type_='manufacturing_plant', conf='medium'),
 S('jm','QMS-NE-06','JM Eagle - Hastings','Hastings','68901','Adams','146 N Maple Ave','326122','extrusion_pipe_tube','pvc;polyethylene_pe','https://jmeagle.com/jm-eagle-hosts-rep-adrian-smith-hastings-plant','110001516832','859924','JM EAGLE',[],'Placed under ORG-002260 J-M Manufacturing Co. Own JM Eagle news page (2010) on the North Maple Ave pipe extrusion plant; current activity from ITA CY2025. FRS county Adams.', org='ORG-002260', tier='B', type_='manufacturing_plant', conf='medium'),
 S('hexl','QMS-NE-09','Hexagon Lincoln - 5150 NW 40th St','Lincoln','68524','Lancaster','5150 NW 40th St','326199','composites_filament_winding','composites_carbon;polyethylene_pe','https://hexagonagility.com/contact-2','110069463020','','',['344580220'],'Own ISO 14001 certificate (hexagonagility.com assets): Hexagon Lincoln LLC, design and manufacture of composite cylinders and gas transport systems. FRS county Lancaster.', org='hexagon', type_='manufacturing_plant'),
 S('hexagon','QMS-NE-16','Hexagon Agility - Lincoln (5117 NW 40th St)','Lincoln','68524','Lancaster','5117 NW 40th St','326199','composites_filament_winding','composites_carbon;polyethylene_pe','https://hexagonagility.com/contact-2','','1434709','Hexagon Agility 5117',['346720568'],'Own contact page: Mobile Pipeline & Cylinder Manufacturing, 5117 NW 40th St. No FRS registry - no link. County Lancaster (Lincoln).'),
 S('gdots','QMS-NE-10','General Dynamics OTS - Lincoln','Lincoln','68504','Lancaster','4300 Industrial Ave','336419','composites_filament_winding;composites_prepreg_autoclave','composites_carbon;composites_thermoset','https://www.gdots.com/lincoln-home/','110000615488','','',['348025503'],'Own GD-OTS Lincoln page: composite motor cases, pressure vessels, nozzles. FRS alt names Lincoln Composites / Brunswick. FRS county Lancaster.', type_='manufacturing_plant'),
 S('wilk','QMS-NE-11','Wilkinson Manufacturing - Fort Calhoun','Fort Calhoun','68023','Washington','1112 Madison St','326199','extrusion_profile;thermoforming_unspecified','thermoplastics','https://www.wilkmfg.com/','110015848680','','',['347919490'],'FRS county Washington.', conf='medium'),
 S('fxi','QMS-NE-13','FXI - Omaha','Omaha','68117','Douglas','5050 F St','326150','foam_fabrication','polyurethane_pu;foams_polymeric','','110002128741','','',['344657655'],'Placed under ORG-000853 FXI. FRS name Foamex Intl. No FXI own page naming Omaha read - tier C federal only (FRS + OSHA, latest 2020). FRS county Douglas.', org='ORG-000853', type_='manufacturing_plant', conf='medium'),
 S('majors','QMS-NE-14','Majors Plastics - Omaha','Omaha','68127','Douglas','10117 I St','326199','injection_molding;insert_overmolding;assembly_secondary_ops','thermoplastics','https://majorsplastics.com/about/','','1430558','Majors Plastics, INC',['348912064'],'No FRS - no link. County Douglas (Omaha).'),
 S('harvey','QMS-NE-15','William H. Harvey (Oatey) - Omaha','Omaha','68132','Douglas','4334 S 67th St','326299','molding_unspecified','elastomers_rubber','https://www.oatey.com/brands/harvey','','1464768','William H. Harvey',['348094038'],'Placed under ORG-000133 Oatey Co. Own Oatey Harvey brand page; Harvey (gaskets/plumbing products) became an Oatey subsidiary in 2006. Process low - integrator check. No FRS - no link. County Douglas.', org='ORG-000133', tier='B', type_='manufacturing_plant', conf='low'),
 S('yasufuku','QMS-NE-17','Yasufuku USA - Lincoln','Lincoln','68521','Lancaster','3201 NW 12th St','326299','injection_molding;rubber_molding_compression;blow_molding','elastomers_rubber;thermoplastics','https://www.yuinc.com/','','1463668','Yasufuku USA Inc',['345318489'],'No FRS - no link. County Lancaster.', conf='medium'),
 S('premier','QMS-NE-18','Premier Plastics - Omaha','Omaha','68137','Douglas','4880 S 134th St','326199','injection_molding;insert_overmolding','thermoplastics','https://www.premierplasticsinc.com/','','1363299','Premier Plastics Inc',['347233488'],'No FRS - no link. County Douglas.'),
]
if __name__ == '__main__': build('NE', 'tasks/ne-skimpy-2026-11-04', 4864, 6044, 23207, ORGS, SITES)

#!/usr/bin/env python3
"""UT skimpy-state pilot (2026-11-04): append the verified creates and their evidence rows.
Run once from the repo root: python3 tasks/ut-skimpy-pilot-2026-11-04/build.py
IDs were allocated with scripts/atlas.py next-id at build time (ORG-004816, SITE-005966, EVD-020270 next free)."""
import csv, os, sys
D = 'data'; DATE = '2026-11-04'; BY = 'grok-ut-pilot'
ORG0, SITE0, EVD0 = 4816, 5966, 20270
FRS = 'https://frs-public.epa.gov/ords/frs_public2/frs_rest_services.get_facilities?registry_id='
def frs(i): return f'EPA FRS registry {i} ({FRS}{i})'
def ita(i, name): return f'OSHA ITA Form 300A CY2025 establishment {i} ({name})'
def osha(nr): return f'OSHA inspection {nr}, https://www.osha.gov/ords/imis/establishment.inspection_detail?id={nr}'

# --- new organizations -------------------------------------------------------
NEW_ORGS = [
 dict(key='envirotech', shard='UT', legal_name='EnviroTech Molded Products, Inc.', trade_names='EnviroTech Custom Injection Molders',
      ultimate_parent_name='Klinkau Group', entity_type='corporation_private', ring_primary='1', hq_city='Salt Lake City', hq_state='UT', hq_county='Salt Lake',
      naics_primary='326199', naics_primary_source_type='government_filing', naics_primary_source_name='OSHA ITA CY2025 establishment 1211981', naics_confidence='high',
      processes='injection_molding', materials='thermoplastics', website='https://empslc.com/',
      description_1line='Custom injection molder of large thick-walled thermoplastic parts (pump/valve components, pipe fittings, filter plates) in Salt Lake City.',
      ownership_type='private_company', own='https://empslc.com/about-us',
      fed=[('registry', frs('110006453480')), ('government_filing', ita('1211981','EnviroTech Custom Injection Molders')), ('government_filing', osha('344211537'))],
      notes='Wholly owned subsidiary of the Klinkau Group per own site (empslc.com/about-us/klinkau-group); parent_org_id left blank: held ORG-002331 Klinkau America Inc. (Exton PA sales office) is a sibling US entity, not shown to be the parent - flagged for the integrator.'),
 dict(key='3form', shard='UT', legal_name='3form', trade_names='3-form LLC;LightArt',
      ultimate_parent_name='', entity_type='llc', ring_primary='1', hq_city='Salt Lake City', hq_state='UT', hq_county='Salt Lake',
      naics_primary='326130', naics_primary_source_type='government_filing', naics_primary_source_name='OSHA ITA CY2025 establishment 420809', naics_confidence='medium',
      processes='', materials='thermoplastics', website='https://www.3-form.com/',
      description_1line='Maker of architectural resin panels (Ecoresin/3form) and LightArt lighting; corporate HQ Salt Lake City.',
      ownership_type='private_company', own='https://www.3-form.com/locations',
      fed=[('registry', frs('110037148565')), ('government_filing', ita('420809','3form'))],
      notes='Own site names 2300 South 2300 West, Salt Lake City as Corporate Headquarters (also LightArt Salt Lake City). ITA CY2025 files this address as a 326130 establishment; processes left blank pending a site source. A separate Ecoresin panel plant at 955 S 3800 W (Utah DAQ memo, single source) is residue, not created.'),
 dict(key='rosti', shard='UT', legal_name='Sports Molding, Inc.', trade_names='Rosti Utah;SMI Molding',
      ultimate_parent_name='Rosti Group', entity_type='corporation_private', ring_primary='1', hq_city='Clearfield', hq_state='UT', hq_county='Davis',
      naics_primary='326199', naics_primary_source_type='government_filing', naics_primary_source_name='OSHA inspection 345761977', naics_confidence='medium',
      processes='injection_molding', materials='thermoplastics', website='https://www.rosti.com/en-us/locations/north-america/utah/',
      description_1line='Injection molder (Rosti Utah, formerly Sports Molding / SMI Molding) in Freeport Center, Clearfield; 30+ cells 55-500 tons.',
      ownership_type='private_company', own='https://www.rosti.com/en-us/locations/north-america/utah/',
      fed=[('registry', frs('110057212788')), ('government_filing', osha('345761977'))],
      notes='Federal records carry the legacy name Sports Molding, Inc.; the Rosti Group own page styles the plant Rosti Utah (Formerly Smi Molding, Inc.) at Freeport Center Bldg Z-13. Org kept at the US operating-entity grain; a Rosti Group parent org is not created (no US HQ; foreign parent = owner/schema question).'),
 dict(key='csi', shard='US', legal_name='Closure Systems International Americas, Inc.', trade_names='CSI Closures',
      ultimate_parent_name='Closure Systems International Group, Inc.', entity_type='corporation_private', ring_primary='1', hq_city='', hq_state='', hq_county='',
      naics_primary='326199', naics_primary_source_type='government_filing', naics_primary_source_name='OSHA ITA CY2025 establishment 1178067', naics_confidence='medium',
      processes='injection_molding', materials='thermoplastics', website='https://www.csiclosures.com/',
      description_1line='Plastic and aluminum closure maker; North American plants include Salt Lake City, UT.',
      ownership_type='private_company', own='https://www.csiclosures.com/global-locations/',
      fed=[('registry', frs('110027235089')), ('government_filing', ita('1178067','Closure Systems International Americas, Inc.')), ('government_filing', osha('346048267'))],
      notes='Residual shard: the own locations page lists plants (Crawfordsville IN x2, Kilgore TX, Salt Lake City UT, Hattiesburg MS, Erie PA) but no HQ street address; HQ state not evidenced, so not placed (SCHEMA App. C s3). Other US plants are not created in this pilot (UT only). Note: held ORG-003811 PolyCycle Innovation names CSI Group as ultimate parent; the Erie PA address 316 W 16th St is held as SITE-002744 under Berry - integrator review lead, not touched.'),
]

# --- new sites ---------------------------------------------------------------
# (key, org_id or new-org key, site_name, site_type, city, zip, county, street, naics, naics_conf, processes, materials, tier, own_url or '', fed list, notes)
SITES = [
 ('presto','ORG-002892','Reynolds Consumer Products (Presto Products) - Lewiston Plant','manufacturing_plant','Lewiston','84320','Cache','1110 E 200 S','326111','high','extrusion_film_blown','polyethylene_pe;films_flexible_packaging','B',
  'https://hourlyjobs-reynoldsconsumerproducts.icims.com/jobs/5991/production-packer/job',
  [('registry',frs('110002160848')),('government_filing',ita('290285','Reynolds Consumer Products, Presto Products')),('government_filing',osha('346442106'))],
  'Reynolds own careers posting 2026-5991 (posted 2026-10-23) names the Manufacturing Plant in Lewiston, UT. ITA/OSHA NAICS 326111 (plastics bags). Process extrusion_film_blown is researcher_inferred from the 326111 code + bag product line; confirm on a site source.'),
 ('charlotte','ORG-002549','Charlotte Pipe & Foundry - Cedar City Plant','manufacturing_plant','Cedar City','84721','Iron','1177 N 5300 W','326122','high','extrusion_pipe_tube;injection_molding','pvc;abs','B',
  'https://www.charlottepipe.com/newsroom/press-releases/charlotte-pipe-adds-plastic-fittings-production-cast-iron-storage-and-jobs-to-utah-location',
  [('registry',frs('110035436258')),('government_filing',ita('1527251','Charlotte Pipe and Foundry PLUT')),('government_filing',osha('346326572'))],
  'Own press release 2018-06-06: Cedar City plant added plastic fittings production (300,000+ sq ft); own about page lists Cedar City among the plastic plants and dates the plant to 2008 (PVC/ABS DWV + CPVC pipe).'),
 ('wl','ORG-003282','WL Plastics - Cedar City','manufacturing_plant','Cedar City','84720','Iron','4660 W Highway 56','326122','high','extrusion_pipe_tube','polyethylene_pe','B',
  'https://www.wlplastics.com/pe-pipes/baba-bead-info',
  [('registry',frs('110022912357')),('government_filing',ita('1068143','WL Plastics - Cedar City')),('government_filing',osha('345281935'))],
  'Own BABA page: pipe manufactured at WL Plastics, 4660 W Hwy 56, Cedar City, UT 84720; own ISO 9001 certificate scope: manufacturing of polyethylene pipe at this address. Fills the plant the parent record notes as not designed.'),
 ('atlas','ORG-002248','Atlas Molded Products - Murray','manufacturing_plant','Murray','84107','Salt Lake','111 W Fireclay Ave','326140','high','foam_molding_bead','polystyrene_ps_hips;foams_polymeric','B',
  'https://www.atlasmoldedproducts.com/locations',
  [('registry',frs('110002270621')),('government_filing',ita('1263129','Atlas Molded Products, A Division of Atlas Roofing Corporation')),('government_filing',osha('348537267'))],
  'Atlas Molded Products is a division of Atlas Roofing Corporation (ITA establishment name). Own locations page lists Murray, Utah, 111 West Fireclay Ave. EPS (326140).'),
 ('carlisle','ORG-002251','Carlisle SynTec - Tooele (TPO)','manufacturing_plant','Tooele','84074','Tooele','1600 W B Ave','326299','medium','calendering','thermoplastic_elastomers_tpe_tpu','B',
  'https://careers.carlisleconstructionmaterials.com/locations/',
  [('registry',frs('110022884315')),('government_filing',osha('348781972'))],
  'Own careers locations page lists Carlisle SynTec - Tooele, 1600 B Avenue (distinct from Hunter Panels/Insulfoam at 501 S Emerald Rd = held SITE-003098). Resolves the TPO-plant lead in SITE-003098 notes. Process/material (TPO membrane) are researcher_inferred; OSHA NAICS 326299.'),
 ('flextrim','ORG-004365','Flex Trim West - Provo','manufacturing_plant','Provo','84601','Utah','533 S 500 W','326150','medium','','polyurethane_pu','B',
  'https://www.flextrim.com/locations.html',
  [('registry',frs('110069463217')),('government_filing',osha('348623901'))],
  'Own locations page (flextrim.com, the held org ORG-004365 domain): UT Flex Trim West, 533 South 500 West, Provo; NC Flex Trim East (HQ) Lexington = held SITE-005684. FRS name FLEXTRIM WEST / ULTRAFLEX MOLDING; Ultra-Flex is syntactic polyurethane per own site. OSHA NAICS 326150/326130 (latest inspection 326150).'),
 ('altium','ORG-001408','Altium Packaging - Clearfield','manufacturing_plant','Clearfield','84016','Davis','398 E 1700 S, Freeport Center Bldg G-8','326160','medium','blow_molding','','C','',
  [('registry',frs('110058287401')),('government_filing',osha('345748255'))],
  'Two federal sources (FRS + OSHA, name + street agree). No own-domain witness read (altiumpkg.com locations route 404; a webpackaging.com-hosted Altium portal lists Clearfield Bldg G8 - vendor-hosted, not cited). Tier C.'),
 ('norwesco','ORG-000991','Norwesco - Tooele','manufacturing_plant','Tooele','84074','Tooele','90 S 1200 W','326199','medium','rotational_molding','polyethylene_pe','C','',
  [('registry',frs('110005194592')),('government_filing',osha('347435026'))],
  'Two federal sources (FRS NORWESCO: A BRAND OF TANK HOLDING CORP. + OSHA 2024). Own locations page renders no plant list (JS map) - availability signal only. Process rotational_molding researcher_inferred from the Norwesco polyethylene tank line. Tier C.'),
 ('envirotech','envirotech','EnviroTech Molded Products - Salt Lake City','hq_and_plant','Salt Lake City','84116','Salt Lake','1075 W North Temple','326199','high','injection_molding','thermoplastics','C','https://empslc.com/about-us',
  NEW_ORGS[0]['fed'],'Own site address 1075 West North Temple (shipping 7 N 1000 W). New org created at tier C (AGENTS s3 step 5).'),
 ('3form','3form','3form Headquarters - Salt Lake City','hq_only','Salt Lake City','84119','Salt Lake','2300 S 2300 W','326130','medium','','','C','https://www.3-form.com/locations',
  NEW_ORGS[1]['fed'],'Own site: Corporate Headquarters. site_type hq_only per the own-site styling; ITA files a 326130 establishment here - if production is on site the integrator may reclassify to hq_and_plant.'),
 ('rosti','rosti','Rosti Utah - Clearfield','manufacturing_plant','Clearfield','84016','Davis','Freeport Center Bldg Z-13','326199','medium','injection_molding','thermoplastics','C','https://www.rosti.com/en-us/locations/north-america/utah/',
  NEW_ORGS[2]['fed'],'Freeport Center lies in Clearfield (Davis County); Census geocoder cannot match a building number, county from the physical address city. 62,000 sq ft, 30+ cells 55-500 tons per own page.'),
 ('csi','csi','Closure Systems International - Salt Lake City','manufacturing_plant','Salt Lake City','84116','Salt Lake','480 N 5600 W','326199','medium','injection_molding','thermoplastics','C','https://www.csiclosures.com/global-locations/',
  NEW_ORGS[2+1]['fed'],'Own locations page lists 480 N 5600 W, Salt Lake City, UT 84116. ITA NAICS 326199; OSHA 326199.'),
]

def rd(p):
    with open(p, newline='') as f: r = csv.reader(f); h = next(r); return h, list(r)
def app(p, header, rows):
    h, _ = rd(p); assert h == header
    with open(p, 'a', newline='') as f:
        w = csv.writer(f, lineterminator='\n'); [w.writerow([r.get(c, '') for c in h]) for r in rows]

oh, _ = rd(f'{D}/organizations_UT.csv'); sh, _ = rd(f'{D}/sites_UT.csv'); eh, _ = rd(f'{D}/evidence_sites_UT.csv')
ids = {}; org_rows = {'UT': [], 'US': []}; ev = {}
nid = ORG0; sid = SITE0; eid = EVD0
def E(shard_file, table, rid, claim, detail, cls, ref, eff, note=''):
    global eid
    if cls == 'registry': note = ('FRS REST fetched 2026-11-04 (copy: tasks/ut-skimpy-pilot-2026-11-04/frs_fresh_2026-11-04.json). ' + note).strip()
    ev.setdefault(shard_file, []).append(dict(evidence_id=f'EVD-{eid:06d}', record_table=table, record_id=rid, claim_type=claim, claim_detail=detail,
        source_class=cls, source_ref=ref, observed_date=DATE, tier_effect=eff, created_by=BY, notes=note)); eid += 1
CAP = {'own_site': 'supports_B', 'government_filing': 'supports_B', 'registry': 'supports_B'}  # creates cap at tier B (kickoff rule)
for o in NEW_ORGS:
    oid = f'ORG-{nid:06d}'; nid += 1; ids[o['key']] = oid
    row = {k: v for k, v in o.items() if k in oh}
    row.update(org_id=oid, hq_country='US', hq_in_scope='national_us', pic_relevance='potential_member', status='active',
        sources='; '.join([o['own']] + [r for _, r in o['fed']]), verification_tier='C', last_verified=DATE, created_by=BY,
        notes=f"Created {DATE} in the UT skimpy-state pilot (tasks/ut-skimpy-pilot-2026-11-04, branch agent/grok/ut-skimpy-pilot) from a two-source federal overlap (lead-fusion {o['key']}). Tier C at birth per AGENTS s3 step 5. " + o['notes'],
        last_activity_evidence_date=DATE, liveness_signal='operating_evidence', monitor_watch='false')
    org_rows[o['shard']].append(row)
    ef = f"evidence_organizations_{o['shard']}.csv"
    E(ef,'organizations',oid,'existence',f"legal/trade name {o['legal_name']}",'own_site',o['own'],'supports_C')
    E(ef,'organizations',oid,'address',f"HQ {o['hq_city'] or 'not evidenced'} {o['hq_state']}".strip(),'own_site',o['own'],'supports_C')
    E(ef,'organizations',oid,'scope',f"ring_primary 1 via {o['processes'] or o['naics_primary']}",'own_site',o['own'],'supports_C')
    E(ef,'organizations',oid,'code',f"naics_primary {o['naics_primary']} ({o['naics_primary_source_name']})",'government_filing',[r for c,r in o['fed'] if c=='government_filing'][0],'supports_C')
    E(ef,'organizations',oid,'activity','operating at its UT establishment','government_filing',[r for c,r in o['fed'] if c=='government_filing'][0],'supports_C')
    E(ef,'organizations',oid,'liveness',f'active at {DATE} (own site live)','own_site',o['own'],'supports_C')
site_rows = []
for (k, org, name, st, city, z, county, street, naics, conf, proc, mat, tier, own, fed, note) in SITES:
    s = f'SITE-{sid:06d}'; sid += 1; ids['site:'+k] = s
    oid = ids.get(org, org); eff = 'supports_B' if tier == 'B' else 'supports_C'
    srcs = ([own] if own else []) + [r for _, r in fed]
    site_rows.append(dict(site_id=s, org_id=oid, site_name=name, site_type=st, city=city, state='UT', zip=z, county=county, ring_primary='1',
        naics_primary=naics, naics_primary_source_type='government_filing', naics_confidence=conf, processes=proc, materials=mat,
        operating_status='active', sources='; '.join(srcs), verification_tier=tier, last_verified=DATE, created_by=BY,
        notes=f'Created {DATE} in the UT skimpy-state pilot (branch agent/grok/ut-skimpy-pilot) from a two-source federal overlap (FRS + OSHA/ITA, name + street agree). ' + note,
        street_address=street, county_source='physical_address', country='US'))
    ef = 'evidence_sites_UT.csv'
    reg = [r for c, r in fed if c == 'registry'][0]; gov = [r for c, r in fed if c == 'government_filing']
    E(ef,'sites',s,'existence',f'{name} at {street}, {city}','government_filing',gov[0],eff,'federal establishment record; name + street agree with FRS')
    if own: E(ef,'sites',s,'existence',f'{name} named by the operator at {city}, UT','own_site',own,eff)
    E(ef,'sites',s,'address',f'{street}, {city}, UT {z} ({county} County, Census geocoder on the physical address {DATE})','registry',reg,'supports_C','FRS pulled fresh 2026-11-04; county cross-checked with Census geocoder')
    E(ef,'sites',s,'address',f'{street}, {city}, UT {z}','government_filing',gov[-1],eff)
    E(ef,'sites',s,'code',f'naics_primary {naics}','government_filing',gov[0],eff)
    E(ef,'sites',s,'scope',f"ring_primary 1 ({proc or 'NAICS '+naics})",'own_site' if own else 'government_filing',own or gov[0],eff,
      '' if own else 'scope rests on the federal NAICS only; no own-site read')
    E(ef,'sites',s,'parent',f'org_id {oid}','own_site' if own else 'registry',own or reg,eff if own else 'supports_C')
    E(ef,'sites',s,'activity','manufacturing operations at the site','government_filing',gov[-1],eff)
    E(ef,'sites',s,'liveness','active: latest federal activity record' + (' and live own page ' + DATE if own else ''),'own_site' if own else 'government_filing',own or gov[-1],eff)
if '--dry-run' in sys.argv:
    print(len(org_rows['UT']), len(org_rows['US']), len(site_rows), eid - EVD0); sys.exit()
app(f'{D}/organizations_UT.csv', oh, org_rows['UT']); app(f'{D}/organizations_US.csv', oh, org_rows['US'])
app(f'{D}/sites_UT.csv', sh, site_rows)
for f, rows in ev.items(): app(f'{D}/{f}', eh, rows)
print('ids', ids, 'evidence', EVD0, '..', eid - 1)

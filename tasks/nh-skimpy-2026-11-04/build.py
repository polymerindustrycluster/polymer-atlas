#!/usr/bin/env python3
"""NH skimpy-state wave (2026-11-04). Run once from repo root. IDs: fresh full-tree scan of main 1cf1917 plus open-PR heads; allocated past open PRs #41 (UT), #42 (DE), #43 (ID)."""
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
    out = [('registry', frs(s['frs']))]
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
            notes=f"Created {DATE} in the {ST} skimpy-state wave ({PKT}) from a two-source federal overlap (lead-fusion {s['cluster']}). Tier C at birth per AGENTS s3 step 5. " + o['notes'],
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
            notes=f"Created {DATE} in the {ST} skimpy-state wave ({PKT}) from a two-source federal overlap (lead-fusion {s['cluster']}; FRS + OSHA/ITA, name + street agree). " + s['notes'],
            street_address=s['street'], county_source='physical_address', country='US'))
        links.append(dict(org_id=oid, registry='FRS', registry_id=s['frs'], match_basis=f"frs_rest_registry_id_name_street_match:{sidn}", as_of=DATE, site_id=sidn))
        ef = f'evidence_sites_{ST}.csv'
        E(ef,'sites',sidn,'existence',f"{s['name']} at {s['street']}, {s['city']}",'government_filing',gov[0],eff,'federal establishment record; name + street agree with FRS')
        if own: E(ef,'sites',sidn,'existence',f"{s['name']} named by the operator at {s['city']}, {ST}",'own_site',own,eff)
        E(ef,'sites',sidn,'address',f"{s['street']}, {s['city']}, {ST} {s['zip']} ({s['county']} County, from the physical address)",'registry',reg,'supports_C','county from the physical address (Census geocoder or a city wholly in one county)')
        E(ef,'sites',sidn,'address',f"{s['street']}, {s['city']}, {ST} {s['zip']}",'government_filing',gov[-1],eff)
        E(ef,'sites',sidn,'code',f"naics_primary {s['naics']}",'government_filing',gov[0],eff)
        E(ef,'sites',sidn,'scope',f"ring_primary {s.get('ring','1')} ({s.get('proc') or 'NAICS ' + s['naics']})",'own_site' if own else 'government_filing',own or gov[0],eff,
          '' if own else 'scope rests on the federal NAICS only; no own-site read')
        E(ef,'sites',sidn,'parent',f'org_id {oid}','own_site' if own else 'registry',own or reg,eff if own else 'supports_C')
        E(ef,'sites',sidn,'activity','manufacturing operations at the site','government_filing',gov[-1],eff)
        E(ef,'sites',sidn,'liveness','active: latest federal activity record' + (f' and live own page {DATE}' if own else ''),'own_site' if own else 'government_filing',own or gov[-1],eff)
    if '--dry-run' in sys.argv:
        print({k: len(v) for k, v in org_rows.items()}, len(site_rows), st['eid'] - EVD0, len(links)); return
    for k, v in org_rows.items(): app(f'{D}/organizations_{k}.csv', oh, v)
    app(f'{D}/sites_{ST}.csv', sh, site_rows)
    for f, rows in ev.items(): app(f'{D}/{f}', eh, rows)
    app(f'{D}/registry_links.csv', lh, links)
    print('ids', ids, 'evidence', EVD0, '..', st['eid'] - 1, 'links', len(links))
def O(key, legal, city, county, naics, src, proc, mat, web, own, desc, notes, conf='high', trade='', parent='', et='corporation_private', ring='1'):
    return dict(key=key, legal_name=legal, trade_names=trade, ultimate_parent_name=parent, entity_type=et, ring_primary=ring, hq_city=city, hq_state='NH', hq_county=county,
                naics_primary=naics, naics_primary_source_name=src, naics_confidence=conf, processes=proc, materials=mat, website=web, own=own, description_1line=desc, notes=notes)
def S(key, cluster, name, city, zip_, county, street, naics, proc, mat, own, frs_, ita_='', ita_name='', osha_=(), notes='', org=None, tier='C', type_='hq_and_plant', ring='1', conf='high'):
    return dict(key=key, org=org or key, cluster=cluster, name=name, type=type_, city=city, zip=zip_, county=county, street=street, naics=naics, conf=conf, proc=proc, mat=mat, ring=ring,
                tier=tier, own=own, frs=frs_, ita=ita_, ita_name=ita_name, osha=list(osha_), notes=notes)
ORGS = [
 O('diacom','DiaCom Corporation','Amherst','Hillsborough','326299','OSHA ITA CY2025 establishment 169058','rubber_molding_compression;transfer_molding;mold_tool_making','elastomers_rubber',
   'https://www.diacom.com/','https://www.diacom.com/contact-us','Custom molded elastomeric diaphragms and seals (fabric-reinforced, rubber-to-metal, PTFE-bonded) with in-house tooling, Amherst, NH.',
   'Own contact/overview pages: 5 Howe Drive, Amherst NH 03031; compression and transfer molding of elastomer diaphragms.', trade='Dia-Com Corporation'),
 O('eptam','EPTAM Plastics, Ltd.','Northfield','Belknap','326199','OSHA ITA CY2025 establishment 1137295','plastics_machining_cnc','thermoplastics',
   'https://eptam.com/','https://eptam.com/about/locations/','Precision plastics and metals machining for medical, semiconductor and aerospace (EPTAM Precision HQ, Northfield, NH).',
   'Own locations page: EPTAM Precision - Northfield, NH, 2 Riverside Business Park, home of EPTAM headquarters (founded 1981): precision machining across plastics and metals. FDA registration on the page names EPTAM Plastics, LTD. Other EPTAM plants (Lakeville MN, Phillipsburg NJ molding, Lancaster MA) not created (NH only). County: see site note.', conf='medium', trade='EPTAM Precision'),
 O('pelham','Pelham Plastics Inc.','Pelham','Hillsborough','326199','OSHA ITA CY2025 establishment 128936','injection_molding;assembly_secondary_ops','thermoplastics',
   'https://pelhamplastics.com/','https://pelhamplastics.com/contact-us/','Custom injection molder and assembler, mainly medical devices, Pelham, NH.',
   'Own site: 42 Dick Tracy Drive, Pelham NH 03076; custom injection molding, assembly, product design.'),
 O('microspec','Microspec Corporation','Peterborough','Hillsborough','326121','OSHA ITA CY2025 establishment 1562633','extrusion_pipe_tube','thermoplastics',
   'https://www.microspecorporation.com/','https://www.microspecorporation.com/about-microspec/contact-us/','Custom medical tubing extruder (multi-lumen, micro, bump, co-extruded) in Peterborough, NH.',
   'Own site: 327 Jaffrey Road, Peterborough NH 03458; exclusively custom advanced medical tubing extrusion.'),
 O('protavic','Protavic America Inc.','Londonderry','Rockingham','325520','OSHA ITA CY2025 establishment 162403','adhesive_sealant_formulation;potting_encapsulation_casting','adhesives_sealants;epoxy',
   'https://www.protavicamerica.com/','http://www.protavicamerica.com/contact-2/','Formulator of electronic-assembly adhesives and encapsulants (epoxy die attach, underfill, potting; Mereco line), Londonderry, NH.',
   'Own contact/product pages: 8 Ricker Avenue, Londonderry NH; Mereco product line. Ring 2 (formulated polymer: SCHEMA s1 Ring 2 test 1/2). Whether compounding happens here vs. distribution of Protex (France) product is not separately stated; ITA files a 325520 establishment here.', conf='medium', trade='Mereco Technologies', ring='2'),
 O('mti','MTI Polyexe Inc.','Brentwood','Rockingham','326112','OSHA ITA CY2025 establishment 1565753','extrusion_film_blown;coating_applying','films_flexible_packaging;polyethylene_pe;silicones',
   'https://www.mtipolyexe.com/','https://www.mtipolyexe.com/contact-mti-polyexe','Integrated maker of blown films and silicone-coated release liners in Brentwood, NH.',
   'Own site: blown film extrusion + silicone coated release liners; 50 Pine Rd, Brentwood NH 03833.'),
 O('app','American Performance Polymers LLC','Colebrook','Coos','326299','OSHA inspection 346599004','latex_dipping_foaming','nitrile_nbr;elastomers_rubber',
   'https://www.americanperformancepolymers.com/','https://www.americanperformancepolymers.com/contact/','Colebrook, NH maker of specialty nitrile gloves and glovebox sleeves; a division of Renco Gloves.',
   'Own contact page: factory 23 Gould St., Colebrook NH 03576. Process latex_dipping_foaming researcher_inferred from dipped nitrile gloves.', conf='medium', parent='Renco Gloves', et='llc'),
 O('plantech','Plan Tech, Inc.','Loudon','Merrimack','326199','OSHA inspection 343706370','potting_encapsulation_casting;plastics_machining_cnc','polyurethane_pu',
   'https://plantech.com/','https://plantech.com/contact/','Custom cast polyurethane parts (wheels, rollers, bearings, sheets, rods) in Loudon, NH.',
   'Own contact page: 7031 Shaker Rd, Loudon NH 03307. Latest OSHA inspection 2019; own site live 2026-11-04 is the liveness witness.', conf='medium'),
]
SITES = [
 S('diacom','LF-NH-00018','DiaCom - Amherst','Amherst','03031','Hillsborough','5 Howe Dr','326299','rubber_molding_compression;transfer_molding;mold_tool_making','elastomers_rubber','https://www.diacom.com/contact-us','110004092776','169058','DiaCom Corporation',['348862939'],'Census: Hillsborough County.'),
 S('eptam','LF-NH-00044','EPTAM Precision - Northfield (HQ)','Northfield','03276','Belknap','2 Riverside Business Park','326199','plastics_machining_cnc','thermoplastics','https://eptam.com/about/locations/','110018932119','1137295','EPTAM Plastics',[],
   'COUNTY FLAG: FRS places the park in TILTON (Belknap); Census matched only a nearby 2 Riverside Dr, Northfield (Belknap); the Town of Northfield itself is in Merrimack County - Belknap kept on FRS+Census, integrator check.', conf='medium'),
 S('pelham','LF-NH-00062','Pelham Plastics - Pelham','Pelham','03076','Hillsborough','42 Dick Tracy Dr','326199','injection_molding;assembly_secondary_ops','thermoplastics','https://pelhamplastics.com/contact-us/','110069517963','128936','Pelham Plastics Inc.',[],'Census: Hillsborough County.'),
 S('microspec','LF-NH-00048','Microspec - Peterborough','Peterborough','03458','Hillsborough','327 Jaffrey Rd','326121','extrusion_pipe_tube','thermoplastics','https://www.microspecorporation.com/about-microspec/contact-us/','110031421101','1562633','Microspec Corporation',[],'Census: Hillsborough County.'),
 S('protavic','LF-NH-00059','Protavic America - Londonderry','Londonderry','03053','Rockingham','8 Ricker Ave','325520','adhesive_sealant_formulation;potting_encapsulation_casting','adhesives_sealants;epoxy','http://www.protavicamerica.com/contact-2/','110064518455','162403','PROTAVIC AMERICA INC',[],'Census: Rockingham County. Ring 2.', ring='2', conf='medium'),
 S('pexco','LF-NH-00014','Pexco - Plaistow (former Scandia Plastics)','Plaistow','03865','Rockingham','55 Westville Rd','326121','extrusion_profile;injection_molding','thermoplastics','https://www.pexco.com/locations/plaistow-nh/','110004087005','1561909','Pexco LLC',['348825779','346770407'],
   'Own Pexco location page for Plaistow NH (custom extrusion; former Scandia Plastics, acquired 2013). Placed under ORG-002534 Pexco LLC (holds the Fife WA and Falls Twp PA Pexco sites). FLAG: ORG-000484 Performance Elastomers (OH) also carries pexco.com - possible Pexco duplicate pair for the integrator. Census: Rockingham County.', org='ORG-002534', tier='B', type_='manufacturing_plant', conf='medium'),
 S('mti','LF-NH-00030','MTI Polyexe - Brentwood','Brentwood','03833','Rockingham','50 Pine Rd','326112','extrusion_film_blown;coating_applying','films_flexible_packaging;polyethylene_pe;silicones','https://www.mtipolyexe.com/contact-mti-polyexe','110007686030','1565753','MTI Polyexe Inc.',[],'Census: Rockingham County.'),
 S('app','LF-NH-00066','American Performance Polymers - Colebrook','Colebrook','03576','Coos','23 Gould St','326299','latex_dipping_foaming','nitrile_nbr;elastomers_rubber','https://www.americanperformancepolymers.com/contact/','110071064151','','',['346599004'],'Census: Coos County.', conf='medium'),
 S('plantech','LF-NH-00029','Plan Tech - Loudon','Loudon','03307','Merrimack','7031 Shaker Rd','326199','potting_encapsulation_casting;plastics_machining_cnc','polyurethane_pu','https://plantech.com/contact/','110007684826','','',['343706370'],'Census: Merrimack County.', conf='medium'),
]
if __name__ == '__main__': build('NH', 'tasks/nh-skimpy-2026-11-04', 4827, 5990, 22503, ORGS, SITES)

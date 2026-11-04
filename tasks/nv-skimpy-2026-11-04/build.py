#!/usr/bin/env python3
"""NV skimpy-state wave (2026-11-04). Run once from repo root. IDs: fresh full-tree scan of main 1cf1917 plus open-PR heads; allocated past open PRs #41-#45."""
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
def O(key, legal, city, county, naics, src, proc, mat, web, own, desc, notes, conf='high', trade='', parent='', et='corporation_private', ring='1', st='NV'):
    return dict(key=key, legal_name=legal, trade_names=trade, ultimate_parent_name=parent, entity_type=et, ring_primary=ring, hq_city=city, hq_state=st, hq_county=county, shard=st,
                naics_primary=naics, naics_primary_source_name=src, naics_confidence=conf, processes=proc, materials=mat, website=web, own=own, description_1line=desc, notes=notes)
def S(key, cluster, name, city, zip_, county, street, naics, proc, mat, own, frs_, ita_='', ita_name='', osha_=(), notes='', org=None, tier='C', type_='hq_and_plant', ring='1', conf='high'):
    return dict(key=key, org=org or key, cluster=cluster, name=name, type=type_, city=city, zip=zip_, county=county, street=street, naics=naics, conf=conf, proc=proc, mat=mat, ring=ring,
                tier=tier, own=own, frs=frs_, ita=ita_, ita_name=ita_name, osha=list(osha_), notes=notes)
ORGS = [
 O('aervoe','Aervoe Industries, Inc.','Gardnerville','Douglas','325510','OSHA ITA CY2025 establishment 1325530','coating_formulation','coatings',
   'https://www.aervoe.com/','https://www.aervoe.com/contact-us/','Gardnerville, NV maker of industrial aerosol and bulk paints, marking paints and specialty coatings, plus MRO chemicals.',
   'Own contact/about pages: corporate HQ and manufacturing at 1100 Mark Circle, Gardnerville NV 89410 (about 95% of products made there). Ring 2 (paints/coatings, SCHEMA s1). Trades as Aervoe LLC on its site.', trade='Aervoe LLC', ring='2'),
 O('polywest','Poly-West, Inc.','Henderson','Clark','326111','OSHA ITA CY2025 establishment 212170','extrusion_film_blown;recycling_mechanical','polyethylene_pe;films_flexible_packaging',
   'https://www.poly-west.com/','https://www.poly-west.com/','Henderson, NV polyethylene trash bag and construction film producer; a subsidiary of Poly-America.',
   'Own site: Poly-West produces polyethylene trash bags and construction films; a subsidiary of Poly-America (Grand Prairie TX; not held, parent org not created). Blown-film process researcher_inferred; recycling per BBB/directory - medium.', conf='medium', parent='Poly-America, L.P.'),
 O('sierra','Sierra Packaging & Converting, LLC','Reno','Washoe','326112','OSHA ITA CY2025 establishment 950390','laminating;printing_decorating_plastics;die_cutting_converting','films_flexible_packaging',
   'https://sierraconverting.com/','https://sierraconverting.com/services/','Reno, NV flexible packaging converter: printed and laminated films, bags, pouches and rollstock for food and snacks.',
   'Own services page: flexo printing, lamination, waxing, slitting and pouch/bag conversion; FRS/ITA address 11005 Stead Blvd, Reno.', conf='medium', et='llc'),
 O('uu','Universal Urethane Inc.','North Las Vegas','Clark','326150','OSHA ITA CY2025 establishment 1177076','potting_encapsulation_casting;foam_molding_structural','polyurethane_pu;foams_polymeric',
   'https://universalurethaneinc.com/','https://www.universalurethaneinc.com/contact.html','North Las Vegas, NV molder of urethane products for automotive, fitness, spa, medical and gaming customers.',
   'Own contact page: 4201 E. Lone Mountain Rd., North Las Vegas NV 89081. Processes researcher_inferred from molded urethane/foam (NAICS 326150).', conf='medium'),
 O('erickson','Erickson International, LLC','Las Vegas','Clark','326113','OSHA inspection 348703075','coating_applying;laminating','pet_petg;films_flexible_packaging',
   'https://aswf.com/','https://aswf.com/about-aswf/','Las Vegas maker of American Standard Window Film (automotive, residential and commercial window films).',
   'Own about page: American Standard Window Film (Erickson International) manufacturing and HQ, 3135 Marco Street, Las Vegas NV 89115. PET film coating/laminating researcher_inferred.', conf='medium', trade='American Standard Window Film (ASWF)', et='llc'),
 O('qp','Quality Plastics, Inc.','Sparks','Washoe','326199','OSHA inspection 348178518','thermoforming_vacuum;plastics_machining_cnc;plastics_fabrication_welding;additive_manufacturing_polymer','thermoplastics',
   'https://qualityplastics.com/','https://qualityplastics.com/contactus.html','Sparks, NV custom plastics shop: vacuum/drape forming, machining, fabrication, laser cutting and 3D printing.',
   'Own contact/about pages: Quality Plastics & Machine, 1685 Industrial Way, Sparks NV 89431.', trade='Quality Plastics & Machine'),
 O('pci','Performance Composites Inc.','Compton','Los Angeles','326199','OSHA inspection 347574501','composites_hand_layup;composites_rtm_infusion;mold_tool_making;assembly_secondary_ops','composites_frp;composites_carbon',
   'https://performancecomposites.com/','https://performancecomposites.com/two-world-class-facilities/','Custom fiberglass and carbon-fiber composite manufacturer with plants in Compton, CA and Reno, NV.',
   'Own facilities page: 53,000 SF Compton CA (1418 Alameda St) and 51,000 SF Reno NV (4902 Ampere Dr). HQ taken as Compton (310 phone) - medium; Compton plant not created (NV wave only). Layup/infusion processes researcher_inferred.', conf='medium', st='CA'),
]
SITES = [
 S('aervoe','LF-NV-00039','Aervoe - Gardnerville (HQ & plant)','Gardnerville','89410','Douglas','1100 Mark Cir','325510','coating_formulation','coatings','https://www.aervoe.com/contact-us/','110058169547','1325530','Aervoe LLC',[],'FRS county Douglas. Ring 2.', ring='2'),
 S('polywest','LF-NV-00025','Poly-West - Henderson','Henderson','89002','Clark','251 Conestoga Way','326111','extrusion_film_blown;recycling_mechanical','polyethylene_pe;films_flexible_packaging','','110027833272','212170','POLY-WEST, INCORPORATED',['347313611','343960613'],'Own site gives no street address; address from FRS/ITA/OSHA. FRS county Clark.', conf='medium'),
 S('berry','LF-NV-00017','Berry Global - Henderson','Henderson','89015','Clark','800 E Horizon Dr','326199','injection_molding','thermoplastics;polypropylene_pp','','110006442769','1433129','BERRY PLASTICS OPCO, INC',['348706052'],
   'Placed under ORG-002544 Berry Global (parent ORG-002907 Amcor plc). No Berry/Amcor own page read for this plant (a third-party catalog portal lists Henderson NV food-contact cups/pails) - tier C, federal sources only. ZIP: ITA 89015 used; FRS shows 89002. Injection molding researcher_inferred from containers/pails.', org='ORG-002544', type_='manufacturing_plant', conf='medium'),
 S('atlas','LF-NV-00063','Atlas Molded Products - Reno','Reno','89506','Washoe','13695 Mt Anderson St','326140','foam_molding_bead','polystyrene_ps_hips;foams_polymeric','https://www.atlasmoldedproducts.com/locations','110071988576','1441731','ATLAS MOLDED PRODUCTS - RENO',['346363708','345680177'],
   'Own Atlas Molded Products locations page lists Reno, Nevada, 13695 Mt. Anderson Street. FRS name: Atlas Molded Products, a division of Atlas Roofing Corporation - placed under ORG-002248. FRS county Washoe.', org='ORG-002248', tier='B', type_='manufacturing_plant'),
 S('sierra','LF-NV-00037','Sierra Packaging & Converting - Reno','Reno','89506','Washoe','11005 Stead Blvd','326112','laminating;printing_decorating_plastics;die_cutting_converting','films_flexible_packaging','https://sierraconverting.com/services/','110045554084','950390','SIERRA PACKAGING & CONVERTING, LLC',['348168139'],'FRS county Washoe.', conf='medium'),
 S('uu','LF-NV-00002','Universal Urethane - North Las Vegas','North Las Vegas','89081','Clark','4201 E Lone Mountain Rd','326150','potting_encapsulation_casting;foam_molding_structural','polyurethane_pu;foams_polymeric','https://www.universalurethaneinc.com/contact.html','110000472747','1177076','UNIVERSAL URETHANE INC.',['347205395'],'ZIP 89081 per FRS and own page (queue showed 89031). FRS county Clark.', conf='medium'),
 S('rtp','LF-NV-00003','RTP Company - Dayton','Dayton','89403','Lyon','23 W Airpark Vista Blvd','325991','custom_compounding;color_masterbatch','thermoplastics','https://www.rtpcompany.com/about/facilities/','110000472809','1451156','RTP Company',[],
   'Own RTP facilities page lists Dayton, Nevada among ISO-certified US plants. Placed under ORG-001093 RTP Company. FLAG: ORG-001093 records HQ Gahanna OH, but the own page names Winona MN (580 E. Front St) as corporate HQ - integrator check; org row not edited. Ring 2 (custom compounder). FRS county Lyon.', org='ORG-001093', tier='B', type_='manufacturing_plant', ring='2'),
 S('erickson','LF-NV-00033','American Standard Window Film (Erickson International) - Las Vegas','Las Vegas','89115','Clark','3135 Marco St','326113','coating_applying;laminating','pet_petg;films_flexible_packaging','https://aswf.com/about-aswf/','110040098685','','',['348703075','345829550'],'FRS county Clark.', conf='medium'),
 S('qp','LF-NV-00028','Quality Plastics & Machine - Sparks','Sparks','89431','Washoe','1685 Industrial Way','326199','thermoforming_vacuum;plastics_machining_cnc;plastics_fabrication_welding;additive_manufacturing_polymer','thermoplastics','https://qualityplastics.com/contactus.html','110031359394','','',['348178518'],'FRS county Washoe.'),
 S('pci','LF-NV-00049','Performance Composites - Reno','Reno','89502','Washoe','4902 Ampere Dr','326199','composites_hand_layup;composites_rtm_infusion;mold_tool_making;assembly_secondary_ops','composites_frp;composites_carbon','https://performancecomposites.com/two-world-class-facilities/','110069233074','','',['347574501'],
   'Own facilities page: 51,000 SF Reno facility, 4902 Ampere Dr. A second FRS registry 110071843032 (RDHC Performance Group LLC) at the same street is not linked - integrator check (possible affiliate/holding entity). FRS county Washoe.', type_='manufacturing_plant', conf='medium'),
]
if __name__ == '__main__': build('NV', 'tasks/nv-skimpy-2026-11-04', 4839, 6005, 22710, ORGS, SITES)

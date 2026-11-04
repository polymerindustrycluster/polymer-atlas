#!/usr/bin/env python3
"""RI skimpy-state wave (2026-11-04). Run once from repo root. IDs: fresh full-tree scan of main 1cf1917 plus open-PR heads; allocated past open PRs #41 (UT), #42 (DE), #43 (ID), #44 (NH)."""
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
    return dict(key=key, legal_name=legal, trade_names=trade, ultimate_parent_name=parent, entity_type=et, ring_primary=ring, hq_city=city, hq_state='RI', hq_county=county,
                naics_primary=naics, naics_primary_source_name=src, naics_confidence=conf, processes=proc, materials=mat, website=web, own=own, description_1line=desc, notes=notes)
def S(key, cluster, name, city, zip_, county, street, naics, proc, mat, own, frs_, ita_='', ita_name='', osha_=(), notes='', org=None, tier='C', type_='hq_and_plant', ring='1', conf='high'):
    return dict(key=key, org=org or key, cluster=cluster, name=name, type=type_, city=city, zip=zip_, county=county, street=street, naics=naics, conf=conf, proc=proc, mat=mat, ring=ring,
                tier=tier, own=own, frs=frs_, ita=ita_, ita_name=ita_name, osha=list(osha_), notes=notes)
ORGS = [
 O('igus','igus, inc.','Rumford','Providence','326199','OSHA ITA CY2025 establishment 1093677','injection_molding;plastics_machining_cnc;assembly_secondary_ops','thermoplastics',
   'https://www.igus.com/','https://www.igus.com/company/visitor-information','North American HQ and plant of igus (motion plastics: polymer plain bearings, energy chains, lead screws), Rumford/East Providence, RI.',
   'Own visitor page: igus, inc., 257 Ferris Avenue, Rumford RI 02916. Press (Robotics 24/7, 2024) reports a separate igus injection-molding building on North Broadway, East Providence - not created (no two-source federal record in this queue). Parent igus GmbH (Germany) not created.', conf='medium', parent='igus GmbH', trade='igus Bearings'),
 O('spectrum','Spectrum Coatings Laboratories, Inc.','Providence','Providence','325510','OSHA inspection 348157181','coating_formulation','coatings;polyurethane_pu;epoxy',
   'https://www.spectrumcoatings.us/','https://www.spectrumcoatings.us/contact','Providence, RI formulator of industrial, military (CARC) and aerospace coatings, including waterborne urethanes and epoxies.',
   'Own site: 217 Chapman Street, Providence RI 02905. Ring 2 per SCHEMA s1 (paints/coatings with a polymer binder).', ring='2'),
 O('epoxyset','EpoxySet, Inc.','Woonsocket','Providence','325520','OSHA inspection 348295999','adhesive_sealant_formulation','adhesives_sealants;epoxy',
   'https://epoxysetinc.com/','https://epoxysetinc.com/contact/','Woonsocket, RI manufacturer of engineered epoxy adhesives, coatings and encapsulants.',
   'Own contact page: 718 Park East Drive, Woonsocket RI 02895. Ring 2 (formulated adhesives).', ring='2'),
 O('iselann','Iselann-Moss Industries, Inc.','Cranston','Providence','326299','OSHA inspection 347677015','potting_encapsulation_casting;mold_tool_making','polyurethane_pu;silicones',
   'https://www.iselann-moss.com/','https://www.iselann-moss.com/contact.htm','Cranston, RI maker of custom molded polyurethane and silicone parts and industrial roll coverings.',
   'Own contact page: 41 Slater Road, Cranston RI 02920. Casting process researcher_inferred from custom molded urethane parts and roll covering.', conf='medium'),
]
SITES = [
 S('igus','LF-RI-00061','igus - Rumford (North American HQ)','Rumford','02916','Providence','257 Ferris Ave','326199','injection_molding;plastics_machining_cnc;assembly_secondary_ops','thermoplastics','https://www.igus.com/company/visitor-information','110071679783','1093677','IGUS BEARINGS, INC.',['348955873'],
   'FRS county Providence (FIPS 44007). Rumford is a village of East Providence. On-site processes: lead-screw production at Ferris Ave per press; the injection molding is reported at the separate North Broadway building - processes medium.', conf='medium'),
 S('spectrum','LF-RI-00024','Spectrum Coatings Laboratories - Providence','Providence','02905','Providence','217 Chapman St','325510','coating_formulation','coatings;polyurethane_pu;epoxy','https://www.spectrumcoatings.us/contact','110002087553','','',['348157181'],'FRS county Providence. Ring 2.', ring='2'),
 S('pmi','LF-RI-00031','PMI MPC (former Polyurethane Molding Industries) - Woonsocket','Woonsocket','02895','Providence','100 Founders Dr','326199','reaction_injection_molding','polyurethane_pu','https://info.mearthane.com/contact-us-wiresaw-components','110004919474','','',['347076978'],
   'Own Mearthane contact page lists PMI MPC LLC, formerly Polyurethane Molding Industries, 100 Founders Drive, Woonsocket. Placed under ORG-000689 Mearthane Products Corporation (holds SITE-004763 Cranston). FLAG: ORG-000689 carries Axillon Aerospace trade names and a Cincinnati OH HQ while Mearthane own page lists HQ 16 Western Industrial Dr, Cranston RI - integrator check of that org row. FRS county Providence.', org='ORG-000689', tier='B', type_='manufacturing_plant', conf='medium'),
 S('epoxyset','LF-RI-00058','EpoxySet - Woonsocket','Woonsocket','02895','Providence','718 Park East Dr','325520','adhesive_sealant_formulation','adhesives_sealants;epoxy','https://epoxysetinc.com/contact/','110070398422','','',['348295999'],'FRS county Providence. Ring 2.', ring='2'),
 S('iselann','LF-RI-00025','Iselann-Moss Industries - Cranston','Cranston','02920','Providence','41 Slater Rd','326299','potting_encapsulation_casting;mold_tool_making','polyurethane_pu;silicones','https://www.iselann-moss.com/contact.htm','110002087820','','',['347677015'],'FRS county Providence.', conf='medium'),
 S('c1','LF-RI-00051','Composites One LLC - Bristol','Bristol','02809','Bristol','4 Minturn Farm Rd','424610','','composites_unspecified','https://www.aerovac.com/about/locations/','110062056607','206742','Composites One LLC',[],
   'Own Aerovac/Composites One locations page lists Composites One LLC, 4 Minturn Farm Road, Bristol RI 02809-4073. Ring 3 distribution branch placed under ORG-000745 Composites One LLC (holds the Ashtabula and Dublin OH sites). Lead-fusion class ring3_primary. FRS county Bristol (FIPS 44001).', org='ORG-000745', tier='B', type_='warehouse_distribution', ring='3', conf='medium'),
]
if __name__ == '__main__': build('RI', 'tasks/ri-skimpy-2026-11-04', 4835, 5999, 22632, ORGS, SITES)

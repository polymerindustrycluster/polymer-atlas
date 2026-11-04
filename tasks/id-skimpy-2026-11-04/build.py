#!/usr/bin/env python3
"""ID skimpy-state wave (2026-11-04). Run once from repo root. IDs: fresh full-tree scan of main c1cc3ae plus open-PR heads; allocated past open PRs #41 (UT) and #42 (DE)."""
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
ORGS = [
 dict(key='unitech', legal_name='Unitech Composites, Inc.', trade_names='APEX Hayden;APEX SDS - UCI', ultimate_parent_name='Apex Space & Defense Systems (Charger Investment Partners)', entity_type='corporation_private',
      hq_city='Hayden', hq_state='ID', hq_county='Kootenai', naics_primary='326113', naics_primary_source_name='OSHA ITA CY2025 establishment 1464818', naics_confidence='medium',
      processes='composites_hand_layup;plastics_machining_cnc', materials='composites_thermoset', website='https://www.apexsds.com/facilities/unitech',
      description_1line='Aerospace/defense composite components (hand layup, cure, 5-axis CNC) in Hayden, ID since 1979; an APEX Space & Defense business unit.',
      own='https://www.apexsds.com/facilities/unitech',
      notes='Own (APEX SDS) facility page: Unitech Composites Inc., 10413 N Aero Dr, Hayden ID; acquired July 2023 by Charger Investment Partners into APEX Space & Defense (no APEX org held; parent not created). ITA NAICS set 326113/336413/325211.'),
 dict(key='yellowstone', legal_name='Yellowstone Plastics, Inc.', trade_names='Yellowstone Plastics', ultimate_parent_name='', entity_type='corporation_private',
      hq_city='Idaho Falls', hq_state='ID', hq_county='Bonneville', naics_primary='326111', naics_primary_source_name='OSHA ITA CY2025 establishment 1096603', naics_confidence='high',
      processes='printing_decorating_plastics;laminating;die_cutting_converting', materials='films_flexible_packaging;polyethylene_pe', website='https://www.volmcompanies.com/about/yellowstone-plastics',
      description_1line='Flexible packaging maker (printed/laminated LLDPE films, flat and pouch bags, rollstock) in Idaho Falls, ID; sister company to Volm Companies.',
      own='https://www.volmcompanies.com/about/yellowstone-plastics',
      notes='Own page (Volm Companies site): sister corporation to Volm Companies (common ownership, not a parent) founded 1999 in Idaho Falls; corporate headquarters Idaho Falls, 3725 W. 65th South. Whether film is extruded on site is not stated (printing/converting/laminating are) - process set kept to the stated ones.'),
 dict(key='ipex', shard='US', legal_name='IPEX USA LLC', trade_names='IPEX', ultimate_parent_name='Aliaxis SA', entity_type='llc',
      hq_city='', hq_state='', hq_county='', naics_primary='326122', naics_primary_source_name='OSHA ITA CY2025 establishment 150335', naics_confidence='medium',
      processes='plastics_fabrication_welding', materials='pvc', website='https://ipexna.com/',
      description_1line='IPEX USA (Aliaxis) PVC pipe and fittings fabrication plant at Preston, ID; US HQ not evidenced in this pass.',
      own='',
      notes='Residual shard: HQ state not evidenced in this pass (no own-site read; the Aliaxis/IPEX workday posting did not render). Created on the two federal sources (FRS IPEX USA + ITA IPEX USA LLC, same street) - org tier C. Idaho DEQ permit material (not cited) describes cutting, belling, gluing and coating PVC pipe/fittings at Preston. Other IPEX USA plants not created (ID only).'),
]
SITES = [
 dict(key='spears', org='ORG-004116', cluster='LF-ID-00005', name='Spears Manufacturing - Jerome', city='Jerome', zip='83338', county='Jerome', street='2152 S Lincoln Ave',
      naics='326122', conf='high', proc='injection_molding', mat='pvc', tier='C', own='', frs='110000888503', ita='1055009', ita_name='Spears Manufacturing Co.', osha=['348200544'],
      notes='Two federal sources (FRS + ITA + OSHA 2025). No own-site read (spearsmfg.com location list not fetched) - tier C. Process injection_molding researcher_inferred (Spears = PVC/CPVC fittings; ITA 326122). Census geocoder no match; Jerome city lies in Jerome County.'),
 dict(key='fiberon', org='ORG-004229', cluster='LF-ID-00014', name='Fiberon Meridian Plant (Fiber Composites)', city='Meridian', zip='83642', county='Ada', street='420 W Franklin Rd',
      naics='326199', conf='medium', proc='extrusion_profile', mat='composites_thermoplastic;polyethylene_pe;pvc;recycled_content_pcr_pir', tier='B',
      own='https://www.fiberondecking.com/blogs/news/fiberon-to-increase-production-capabilities-at-idaho-facility',
      frs='110012576079', ita='1081387', ita_name='Fiber Composites, LLC', osha=['348659384'],
      notes='Own news (fiberondecking.com, held org domain): Meridian, Idaho manufacturing facility, PVC-category capacity expansion (2019). ITA NAICS 326199/321912 (wood-plastic composite). Ownership watch carried on ORG-004229 (Inteplast agreement 2026-10-16) applies. Census: Ada County.'),
 dict(key='unitech', org='unitech', cluster='LF-ID-00012', name='Unitech Composites - Hayden', type='hq_and_plant', city='Hayden', zip='83835', county='Kootenai', street='10413 N Aero Dr',
      naics='326113', conf='medium', proc='composites_hand_layup;plastics_machining_cnc', mat='composites_thermoset', tier='C', own='https://www.apexsds.com/facilities/unitech',
      frs='110005783919', ita='1464818', ita_name='Unitech Composites, Inc.', osha=['343733457'], notes='Census: Kootenai County. Latest OSHA inspection 2019; ITA CY2025 is the current activity record.'),
 dict(key='yellowstone', org='yellowstone', cluster='LF-ID-00013', name='Yellowstone Plastics - Idaho Falls', type='hq_and_plant', city='Idaho Falls', zip='83402', county='Bonneville', street='3725 W 65th S',
      naics='326111', conf='high', proc='printing_decorating_plastics;laminating;die_cutting_converting', mat='films_flexible_packaging;polyethylene_pe', tier='C', own='https://www.volmcompanies.com/about/yellowstone-plastics',
      frs='110005792464', ita='1096603', ita_name='Yellowstone Plastics, Inc', osha=[], notes='Census: Bonneville County.'),
 dict(key='ipex', org='ipex', cluster='LF-ID-00016', name='IPEX USA - Preston', city='Preston', zip='83263', county='Franklin', street='640 S Highway 91',
      naics='326122', conf='medium', proc='plastics_fabrication_welding', mat='pvc', tier='C', own='', frs='110038455720', ita='150335', ita_name='IPEX USA LLC', osha=[],
      notes='Two federal sources only (FRS + ITA). Census: Franklin County.'),
 dict(key='fabrikal', org='ORG-002395', cluster='LF-ID-00018', name='Fabri-Kal - Burley', city='Burley', zip='83318', county='Cassia', street='2457 Washington Ave',
      naics='326199', conf='medium', proc='thermoforming_unspecified', mat='thermoplastics', tier='C', own='', frs='110070029334', ita='1041712', ita_name='Fabri Kal LLC', osha=[],
      notes='Two federal sources (FRS FABRI-KAL DBA PACTIV EVERGREEN + ITA Fabri Kal LLC). Thermoforming plant opened Oct 2015 per a Fabri-Kal PR Newswire release (company release, not own domain) - tier C. Fabri-Kal is a Pactiv Evergreen subsidiary; held ORG-002537 Pactiv Corporation not linked as parent (flag). Census: Cassia County.'),
]
if __name__ == '__main__': build('ID', 'tasks/id-skimpy-2026-11-04', 4824, 5984, 22434, ORGS, SITES)

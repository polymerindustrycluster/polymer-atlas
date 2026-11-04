#!/usr/bin/env python3
"""DE skimpy-state wave (2026-11-04). Run once from repo root. IDs: fresh full-tree scan of main c1cc3ae (atlas.py next-id --all) plus all open-PR heads; ORG/SITE start past open PR #41 (UT pilot) ranges to avoid self-collision."""
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
            sources='; '.join([o['own']] + [r for _, r in fed]), verification_tier='C', last_verified=DATE, created_by=BY,
            notes=f"Created {DATE} in the {ST} skimpy-state wave ({PKT}) from a two-source federal overlap (lead-fusion {s['cluster']}). Tier C at birth per AGENTS s3 step 5. " + o['notes'],
            last_activity_evidence_date=DATE, liveness_signal='operating_evidence', monitor_watch='false')
        sh_ = o.get('shard', ST); org_rows.setdefault(sh_, []).append(row)
        ef = f'evidence_organizations_{sh_}.csv'
        E(ef,'organizations',oid,'existence',f"legal/trade name {o['legal_name']}",'own_site',o['own'],'supports_C')
        E(ef,'organizations',oid,'address',f"HQ {o.get('hq_city') or 'not evidenced'} {o.get('hq_state','')}".strip(),'own_site',o['own'],'supports_C')
        E(ef,'organizations',oid,'scope',f"ring_primary {row['ring_primary']} via {o.get('processes') or o['naics_primary']}",'own_site',o['own'],'supports_C')
        E(ef,'organizations',oid,'code',f"naics_primary {o['naics_primary']} ({o['naics_primary_source_name']})",'government_filing',gov,'supports_C')
        E(ef,'organizations',oid,'activity',f'operating at its {ST} establishment','government_filing',gov,'supports_C')
        E(ef,'organizations',oid,'liveness',f'active at {DATE} (own site live)','own_site',o['own'],'supports_C')
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
 dict(key='franklin', legal_name='Franklin Fibre-Lamitex Corporation', trade_names='Franklin Lamitex LLC;Lamitex', entity_type='corporation_private',
      hq_city='Wilmington', hq_state='DE', hq_county='New Castle', naics_primary='326130', naics_primary_source_name='OSHA inspection 347977852', naics_confidence='high',
      processes='laminating;plastics_machining_cnc', materials='composites_thermoset;phenolic;epoxy', website='https://www.lamitex.com/',
      description_1line='Maker and machinist of thermoset laminates and composites (Lamitex NEMA grades G10/FR4/G11, phenolics) in Wilmington, DE since 1921.',
      own='https://www.lamitex.com/contact-franklin-fibre',
      notes='Own contact page: Franklin Fibre - Lamitex Corporation, 903 East 13th Street, Wilmington DE 19802 (the federal 19899 is the PO-box ZIP). Family-owned (Vachris) per own about page.'),
 dict(key='delstar', legal_name='DelStar Technologies, Inc.', trade_names='Delstar', ultimate_parent_name='Mativ Holdings, Inc.', entity_type='corporation_private',
      hq_city='Middletown', hq_state='DE', hq_county='New Castle', naics_primary='326113', naics_primary_source_name='OSHA ITA CY2025 establishment 1248586', naics_confidence='medium',
      processes='extrusion_unspecified;laminating', materials='thermoplastics', website='https://delstarmedical.com/',
      description_1line='Mativ brand making thermoplastic extruded netting, apertured films, nonwovens and laminates; US plant Middletown, DE.',
      own='https://delstarmedical.com/about-us/',
      notes='Own about page: Delstar, a Mativ brand; Locations USA: 601 Industrial Drive, Middletown DE 19709 (sole US location listed, so HQ placed there). Mativ 10-K Ex.21 (SEC CIK 1000623, FY2024) lists DelStar Technologies, Inc. (Delaware) 100%. PARENT LINK NOT FORCED: held ORG-002642 Schweitzer-Mauduit International, Inc. (= Mativ legal predecessor, carried at a Richland PA DelStar-operation grain) may be the parent or a duplicate grain - integrator ruling.'),
 dict(key='datwyler', legal_name='Datwyler Pharma Packaging USA, Inc.', trade_names='Datwyler Sealing Solutions;Datwyler FirstLine Middletown', ultimate_parent_name='Dätwyler Holding AG', entity_type='corporation_private',
      hq_city='Middletown', hq_state='DE', hq_county='New Castle', naics_primary='326299', naics_primary_source_name='OSHA ITA CY2025 establishment 1068808', naics_confidence='high',
      processes='rubber_molding_unspecified;coating_applying', materials='elastomers_rubber', website='https://datwyler.com/contact/locations/middletown-usa/',
      description_1line='Datwyler FirstLine plant making elastomer pharmaceutical stoppers and closures (cleanroom washing, coating, sterilization) in Middletown, DE.',
      own='https://datwyler.com/contact/locations/middletown-usa/',
      notes='Own locations page and own-hosted ISO 15378 certificate (Datwyler Pharma Packaging USA Inc, Middletown). PARENT LINK NOT FORCED: held ORG-000534 Quality Synthetic Rubber (OH) carries ultimate parent Dätwyler Holding AG but is a sibling, not shown to be the parent. HQ placed at the Middletown plant (US entity address); integrator may re-grain.'),
 dict(key='liveo', legal_name='Liveo Research, Inc.', trade_names='Liveo Research', ultimate_parent_name='Liveo Research GmbH', entity_type='corporation_private',
      hq_city='Delaware City', hq_state='DE', hq_county='New Castle', naics_primary='326112', naics_primary_source_name='OSHA inspection 347187692', naics_confidence='high',
      processes='calendering;laminating', materials='pvc;films_flexible_packaging', website='https://www.liveoresearch.com/',
      description_1line='US unit of Liveo Research (pharma packaging films): calendered and laminated PVC films at 1389 School House Road, Delaware City/New Castle, DE.',
      own='https://www.liveoresearch.com/en/company/global-locations/',
      notes='Own global-locations page: Liveo Research Inc., Delaware - films and foils, calendered and laminated PVC films; own-hosted BSI ISO 15378 certificate (scope: design, manufacture of films). Own pages print New Castle 19720 and Delaware City 19706; OSHA/FRS carry Delaware City 19706 (both New Castle County). DNREC 2026 notice confirms the calender lamination line.'),
]
SITES = [
 dict(key='franklin', org='franklin', cluster='LF-DE-00022', name='Franklin Fibre-Lamitex - Wilmington', type='hq_and_plant', city='Wilmington', zip='19802', county='New Castle', street='903 E 13th St',
      naics='326130', conf='high', proc='laminating;plastics_machining_cnc', mat='composites_thermoset;phenolic;epoxy', tier='C', own='https://www.lamitex.com/contact-franklin-fibre',
      frs='110001748716', osha=['347977852'], notes='Census geocoder: New Castle County. FRS/OSHA carry ZIP 19899 (PO box); own site and Census 19802 used.'),
 dict(key='invista', org='ORG-003240', cluster='LF-DE-00007', name='INVISTA Seaford Plant', city='Seaford', zip='19973', county='Sussex', street='25876 DuPont Rd',
      naics='325220', conf='high', proc='', mat='nylon_pa', tier='B', own='https://koch.avature.net/en_US/careers/JobDetail/Seaford-Delaware-Vereinigte-Staaten-Manufacturing-Technician/188364',
      frs='110000339027', ita='1130772', ita_name='Invista Performance Materials - Seaford', osha=['348810508'],
      notes='Operator INV Performance Materials, LLC (INVISTA). Koch/INVISTA own careers posting: the Seaford facility has produced nylon fibers for 85+ years (spinning/finishing teams); INVISTA own news 2025-04-17 names Seaford among the retained nylon-fiber plants. Nylon 6,6 staple fiber (325220). Census: Sussex County. Fills a gap named in ORG-003240 notes (US plant network not site-verified).'),
 dict(key='delstar', org='delstar', cluster='LF-DE-00021', name='DelStar Technologies - Middletown', type='hq_and_plant', city='Middletown', zip='19709', county='New Castle', street='601 Industrial Dr',
      naics='326113', conf='medium', proc='extrusion_unspecified;laminating', mat='thermoplastics', tier='C', own='https://delstarmedical.com/about-us/',
      frs='110001748618', ita='1248586', ita_name='Delstar Technologies, Inc.', osha=['346139454', '345769038'], notes='Census: New Castle County. ITA/OSHA NAICS 326113/326121.'),
 dict(key='datwyler', org='datwyler', cluster='LF-DE-00050', name='Datwyler FirstLine - Middletown', type='hq_and_plant', city='Middletown', zip='19709', county='New Castle', street='571 Merrimac Ave',
      naics='326299', conf='high', proc='rubber_molding_unspecified;coating_applying', mat='elastomers_rubber', tier='C', own='https://datwyler.com/contact/locations/middletown-usa/',
      frs='110071062124', ita='1068808', ita_name='Datwyler Sealing Solutions', osha=[],
      notes='Second FRS registry 110071201878 also carries this address (not linked here). Census geocoder found no match; Middletown lies wholly in New Castle County.'),
 dict(key='liveo', org='liveo', cluster='LF-DE-00019', name='Liveo Research - Delaware City', type='hq_and_plant', city='Delaware City', zip='19706', county='New Castle', street='1389 School House Rd',
      naics='326112', conf='high', proc='calendering;laminating', mat='pvc;films_flexible_packaging', tier='C', own='https://www.liveoresearch.com/en/company/global-locations/',
      frs='110001736015', osha=['347187692'], notes='Census geocoder no match; Delaware City/New Castle mailing both lie in New Castle County.'),
 dict(key='ashland', org='ORG-002065', cluster='LF-DE-00006', name='Ashland - Wilmington Aquarius Plant', city='Wilmington', zip='19808', county='New Castle', street='500 Hercules Rd',
      ring='2', naics='325211', conf='medium', proc='coating_formulation', mat='coatings', tier='C', own='',
      frs='110000338858', ita='1258704', ita_name='Wilmington Aquarius plant', osha=[],
      notes='Two federal sources (FRS ASHLAND SPECIALTY INGREDIENTS G.P. + ITA Wilmington Aquarius plant). Aquarius film-coating excipients per public trade press; the Ashland workday posting did not render (no own-site read), so tier C. Ring 2 follows the held org. Census: New Castle County.'),
]
if __name__ == '__main__': build('DE', 'tasks/de-skimpy-2026-11-04', 4820, 5978, 22357, ORGS, SITES)

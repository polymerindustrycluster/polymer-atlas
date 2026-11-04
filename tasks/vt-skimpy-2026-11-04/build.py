#!/usr/bin/env python3
"""VT skimpy-state wave (2026-11-04). Run once from repo root. IDs tiled from the owner-supplied ledger (no main rescan)."""
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
ST_ = 'VT'
ORGS = [
 O('vtc','Vermont Composites, Inc.','Bennington','Bennington','336413','OSHA ITA CY2025 establishment 953474','composites_prepreg_autoclave;composites_hand_layup;plastics_machining_cnc','composites_carbon;composites_thermoset',
   'https://www.vermontcomposites.com/','https://www.vermontcomposites.com/','Bennington, VT maker of composite structures and components for aerospace, defense and medical customers.',
   'Own site: composite structures made in Bennington. Formerly Kaman Composites - Vermont, Inc. (FRS/ITA name) - name change flagged for integrator. Processes researcher_inferred.', conf='medium', trade='formerly Kaman Composites - Vermont'),
 O('revision','Revision Military Ltd.','Essex Junction','Chittenden','339115','OSHA ITA CY2025 establishment 1421253','injection_molding;coating_applying','polycarbonate_pc;coatings',
   'https://www.revisionmilitary.com/','https://www.revisionmilitary.com/','Essex Junction, VT maker of military protective eyewear and helmet systems.',
   'Own facilities page: injection molding and lens coating at Essex Junction. Polycarbonate researcher_inferred.', conf='medium'),
 O('quadratek','Arlington Industries, Inc.','Arlington','Bennington','326199','EPA FRS 110015685418','injection_molding;compression_molding','thermoplastics;thermosets',
   'https://www.quadra-tek.com/','https://www.quadra-tek.com/','Arlington, VT custom thermoplastic injection and thermoset molder (dba Quadra-Tek).',
   'Own quadra-tek.com: injection and thermoset molding. Thermoset process (compression) researcher_inferred.', conf='medium', trade='Quadra-Tek'),
]
SITES = [
 S('teknor','QMS-VT-00','Teknor Apex - St Albans','St Albans','05478','Franklin','300 Industrial Park Rd','325991','custom_compounding','thermoplastic_elastomers_tpe_tpu;thermoplastics','https://www.teknorapex.com/','110031342214','156991','TEKNOR APEX',['348942632'],
   'Placed under ORG-003024 Teknor Apex Company. Own Teknor Apex locations page and ISO certificate list St Albans VT (TPE compounds, Medalist). Ring 2 (compounder). FRS county Franklin.', org='ORG-003024', tier='B', type_='manufacturing_plant', ring='2'),
 S('vtc','QMS-VT-01','Vermont Composites - Bennington','Bennington','05201','Bennington','25 Performance Dr','336413','composites_prepreg_autoclave;composites_hand_layup;plastics_machining_cnc','composites_carbon;composites_thermoset','https://www.vermontcomposites.com/','110058315942','953474','KAMAN COMPOSITES - VERMONT, INC.',[],'FRS/ITA name Kaman Composites - Vermont. FRS county Bennington.', conf='medium'),
 S('revision','QMS-VT-02','Revision Military - Essex Junction','Essex Junction','05452','Chittenden','7 Corporate Dr','339115','injection_molding;coating_applying','polycarbonate_pc;coatings','https://www.revisionmilitary.com/','110038915494','1421253','REVISION MILITARY LTD',[],'FRS county Chittenden.', conf='medium'),
 S('mackc','QMS-VT-03','Mack Molding - Cavendish','Cavendish','05142','Windsor','2044 Main St','326199','injection_molding','thermoplastics','https://www.mack.com/locations/cavendish-vt','110008205405','','',['347267692'],
   'Placed under ORG-003198 Mack Molding Co. Own mack.com Cavendish VT location page. FRS county Windsor.', org='ORG-003198', tier='B', type_='manufacturing_plant'),
 S('macka','QMS-VT-04','Mack Molding - East Arlington','Arlington','05250','Bennington','79 E Arlington Rd','326199','injection_molding;printing_decorating_plastics','thermoplastics','https://www.mack.com/locations/east-arlington-vt','110001136155','','',['347478380'],
   'Placed under ORG-003198. Distinct from HQ SITE-003625 (608 Warm Brook Rd). Own mack.com East Arlington page: injection molding and painting. FRS county Bennington.', org='ORG-003198', tier='B', type_='manufacturing_plant'),
 S('quadratek','QMS-VT-05','Quadra-Tek (Arlington Industries) - Arlington','Arlington','05250','Bennington','2617 VT Route 7A','326199','injection_molding;compression_molding','thermoplastics;thermosets','https://www.quadra-tek.com/','110015685418','','',['346609118'],'FRS county Bennington.', conf='medium'),
]
if __name__ == '__main__': build('VT', 'tasks/vt-skimpy-2026-11-04', 4851, 6021, 22924, ORGS, SITES)

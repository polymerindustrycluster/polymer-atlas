#!/usr/bin/env python3
"""ME skimpy-state wave (2026-11-04). Run once from repo root. IDs tiled from the owner-supplied ledger (no main rescan)."""
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
ST_ = 'ME'
ORGS = [
 O('corning','Corning Incorporated','Corning','Steuben','327212','corporate filings (NYSE: GLW)','injection_molding','thermoplastics;polystyrene_ps_hips',
   'https://www.corning.com/','https://www.corning.com/worldwide/en/careers/our-people/racelis-acosta.html','Corning, NY materials-science company; its Life Sciences unit makes plastic labware.',
   'Org created only to parent the Kennebunk ME plastics plant (no Corning org held). HQ Corning NY (Steuben County). Primary NAICS is glass (327212) - org is ring 1 only through its Life Sciences plastics plants; integrator check.', conf='medium', et='corporation_public', st='NY'),
 O('nepco','Northeast Packaging Company','Presque Isle','Aroostook','326111','EPA FRS 110037396332','printing_decorating_plastics;die_cutting_converting','polyethylene_pe;films_flexible_packaging',
   'https://www.nepcobags.com/','https://www.nepcobags.com/','Presque Isle, ME maker of printed poly bags and paper bags (NEPCO).',
   'Own site: poly bags converted with 3 poly presses and 6 wicketers at Presque Isle. Film extrusion on site not stated; processes researcher_inferred.', conf='medium', trade='NEPCO'),
 O('paradigm','Paradigm Window Solutions','Portland','Cumberland','326199','OSHA ITA CY2025 establishment 1069790','extrusion_profile;plastics_fabrication_welding','pvc',
   'https://www.paradigmwindows.com/','https://www.paradigmwindows.com/','Portland, ME manufacturer of vinyl replacement and new-construction windows.',
   'Own site: vinyl windows manufactured at the Portland ME HQ/plant (56 Milliken St). Profile extrusion vs fabrication-only not stated - extrusion_profile researcher_inferred, low; integrator check.', conf='medium', et='llc'),
]
SITES = [
 S('corning','QMS-ME-00','Corning Life Sciences - Kennebunk','Kennebunk','04043','York','2 Alfred Rd','326199','injection_molding','thermoplastics;polystyrene_ps_hips','https://www.corning.com/worldwide/en/careers/our-people/racelis-acosta.html','110000797111','1089330','CORNING LIFE SCIENCES',['343817896'],
   'Own Corning careers page: the Kennebunk plant manufactures plastic labware (nearly 500 people). Injection molding researcher_inferred. FRS county York.', type_='manufacturing_plant', conf='medium'),
 S('nepco','QMS-ME-02','Northeast Packaging Co - Presque Isle','Presque Isle','04769','Aroostook','875 Skyway St','326111','printing_decorating_plastics;die_cutting_converting','polyethylene_pe;films_flexible_packaging','https://www.nepcobags.com/','110037396332','','',['344081419'],'FRS county Aroostook.', conf='medium'),
 S('paradigm','QMS-ME-03','Paradigm Window Solutions - Portland','Portland','04103','Cumberland','56 Milliken St','326199','extrusion_profile;plastics_fabrication_welding','pvc','https://www.paradigmwindows.com/','','1069790','Paradigm Windows Solutions',['344050182'],
   'No FRS registry - no registry link; federal basis ITA + OSHA. County Cumberland (Portland lies wholly in Cumberland County).', conf='medium'),
 S('altium','QMS-ME-04','Altium Packaging - Poland','Poland','04274','Androscoggin','115 Poland Spring Dr','326160','blow_molding_extrusion','polyethylene_pe;pet_petg','https://ccc.wd5.myworkdayjobs.com/en-US/ccc_External/job/Maintenance-Manager_R21182','','1059725','Altium Packaging - Poland Plant',['344258231'],
   'Placed under ORG-001408 Altium Packaging. Own Altium (CCC Workday) job posting for the Poland ME plant at 115 Poland Spring Drive. Bottle process researcher_inferred (blow molding), medium. No FRS registry - no registry link. County Androscoggin (Poland lies wholly in Androscoggin County).', org='ORG-001408', tier='B', type_='manufacturing_plant', conf='medium'),
]
if __name__ == '__main__': build('ME', 'tasks/me-skimpy-2026-11-04', 4846, 6015, 22840, ORGS, SITES)

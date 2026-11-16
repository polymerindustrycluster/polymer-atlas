"""Ohio address-gain federal rematch. Only explicit --apply changes canonical data."""
import ast, csv, io, json, subprocess, sys
from collections import Counter, defaultdict
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]; HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'scripts'))
import build_lead_fusion as fusion
from shard_io import append_sorted
CACHE=Path('/Users/johnswanson/.bb/thread-storage/thr_9i2c6byhcz/2026-11-06-atlas/persist/oh-federal-rematch')
BASE='be2e6084d430f1e6f9de0f66289b1d3c2570e255'
# Reuse the historical normalizers without executing its hardcoded build at import.
tree=ast.parse((ROOT/'tasks/federal-frame-2026-11-04/build_frame.py').read_text())
ns={'re':__import__('re')}
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in ('name_norm','street_parts','zip5') or isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id in ('SUFFIX','SUFFIX_RE','STREET_SUFFIX') for t in n.targets)],type_ignores=[]),'<historical normalizers>','exec'),ns)
name_norm,street_parts,zip5=(ns[k] for k in ('name_norm','street_parts','zip5'))
def read(p):
    with open(p,newline='') as f:return list(csv.DictReader(f))
def at(rev,path):return list(csv.DictReader(io.StringIO(subprocess.check_output(['git','show',f'{rev}:{path}'],cwd=ROOT,text=True))))
def write(p,rows,cols):
    with open(p,'w') as f:
        w=csv.DictWriter(f,cols,lineterminator='\n');w.writeheader();w.writerows(rows)
def frame():
    old={r['site_id']:r for r in at('91cd1a8','data/sites_OH.csv')}
    current=at(BASE,'data/sites_OH.csv')
    assert len(current)==len({r['site_id'] for r in current})
    return [r for r in current if r['operating_status']=='active' and r['state']=='OH' and r['street_address'].strip() and r['site_id'] in old and not old[r['site_id']]['street_address'].strip()]
def agree(names,other):
    # Conservative subset of lead-fusion name compatibility; weak/fuzzy levels are holds.
    pairs=lambda xs:[(fusion.atlas.name_key(n),fusion.dist_tokens(n)) for n in xs if n]
    return fusion.name_compat(pairs(names),pairs(other)) in ('exact','nospace','exact_distinct','subset')
def located(s,r):
    return bool(fusion.skey_of(s['street_address'])) and fusion.skey_of(s['street_address'])==fusion.skey_of(r['street']) and street_parts(s['street_address'])==street_parts(r['street']) and (s['city'].strip().upper()==r['city'].strip().upper() or bool(zip5(s['zip'])) and zip5(s['zip'])==zip5(r['zip']))
def sources():
    result=[]
    for folder,kind in [('osha-ita-2026-11-01','ITA'),('osha-spine-2026-11-01','OSHA')]:
        banked=read(ROOT/'tasks'/folder/'establishments.csv')
        assert len(banked)==(11194 if kind=='ITA' else 6473), 'Banked source count drift'
        for r in banked:
            if r['state']!='OH':continue
            result.append(dict(kind=kind,id=r.get('establishment_id',r.get('est_key')),names=[r.get('establishment_name',r.get('name','')),r.get('company_name','')],street=r['street'],city=r['city'],zip=r.get('zip5',r.get('zip')),raw=r))
    for r in read(CACHE/'ohio.csv'):
        result.append(dict(kind='ECHO',id=r['REGISTRY_ID'],names=[r['FAC_NAME']],street=r['FAC_STREET'],city=r['FAC_CITY'],zip=r['FAC_ZIP'],raw=r))
    return result
def plan():
    sites=frame(); orgs={r['org_id']:r for p in (ROOT/'data').glob('organizations_*.csv') for r in read(p)}
    all_sites=at(BASE,'data/sites_OH.csv')
    atlas_streets=defaultdict(list)
    for s in all_sites:
        key=fusion.skey_of(s['street_address'])
        if key:atlas_streets[key].append(s['site_id'])
    src=sources(); proposals=[]; witnesses=[]
    by_street=defaultdict(list)
    for r in src:
        key=fusion.skey_of(r['street'])
        if key:by_street[key].append(r)
    for s in sites:
        o=orgs.get(s['org_id'],{})
        names=[s['site_name'],o.get('legal_name','')]+o.get('trade_names','').split(';')
        hits=[r for r in by_street[fusion.skey_of(s['street_address'])] if located(s,r)]
        for kind in ('ITA','OSHA','ECHO'):
            candidates=[r for r in hits if r['kind']==kind]
            for r in candidates:
                federal_names=[n for n in r['names'] if name_norm(n) not in (name_norm(s['city']), 'PLANT', 'FACILITY')]
                ok=agree(names,federal_names) and len(candidates)==1 and len(atlas_streets[fusion.skey_of(s['street_address'])])==1
                reason='' if ok else 'Need unique source facility and primary operator/name agreement at this street.'
                proposals.append(dict(site_id=s['site_id'],kind=kind,source_id=r['id'],registrant=' | '.join(n for n in r['names'] if n),atlas_name=s['site_name'],disposition='applied' if ok and kind!='OSHA' else 'held',settling_fact=reason or ('Inspection corroboration only; no requested output field.' if kind=='OSHA' else '')))
                if ok:witnesses.append((s,r))
        if not hits:proposals.append(dict(site_id=s['site_id'],kind='',source_id='',registrant='',atlas_name=s['site_name'],disposition='held',settling_fact='Need federal record with matching street, city/ZIP and operator name.'))
    return sites,src,proposals,witnesses

def main():
    sites,src,proposals,witnesses=plan()
    links=at(BASE,'data/registry_links.csv'); existing={(r['org_id'],r['registry'],r['registry_id']) for r in links}
    newlinks=[]; evidence=[]; edits=[]; band_holds={}
    evdid=360000
    for s,r in witnesses:
        raw=r['raw']; detail=''; typ=''; ref='';date='2026-11-01'
        if r['kind']=='ITA' and not s['employee_band_site'].strip():
            band=fusion.band_of(raw['annual_average_employees'])
            if raw['reliability']!='ok' or not band:
                band_holds[s['site_id']]=f"Need corrected/reliable ITA count: reliability={raw['reliability']}, annual average={raw['annual_average_employees']}."
                continue
            # Inspection disagreement over one band is a review hold (R13).
            inspections=[v for ss,v in witnesses if ss['site_id']==s['site_id'] and v['kind']=='OSHA']
            if any(fusion.band_of(v['raw']['nr_in_estab_latest_valid']) and abs(fusion.BAND_ORDER[band]-fusion.BAND_ORDER[fusion.band_of(v['raw']['nr_in_estab_latest_valid'])])>1 for v in inspections):
                band_holds[s['site_id']]='Need resolution of ITA versus inspection disagreement exceeding one employee band (R13).'
                continue
            edits.append(dict(site_id=s['site_id'],old_value='',new_value=band))
            typ='size_band';detail=f"employee_band_site={band}: OSHA ITA Form 300A {raw['year_filing_for']}, {raw['establishment_name']} / {raw['company_name']}, annual_average_employees={raw['annual_average_employees']} (band only, not a headcount)"
            ref=f"OSHA ITA Form 300A {raw['year_filing_for']}, establishment_id {r['id']} (https://www.osha.gov/Establishment-Specific-Injury-and-Illness-Data)"
        elif r['kind']=='ECHO' and r['id']:
            date='2026-11-16';ref=f"EPA ECHO exporter https://echo.epa.gov/files/echodownloads/echo_exporter.zip REGISTRY_ID={r['id']}"
            before_links=len(newlinks)
            for registry,ids in [('FRS',r['id']),('TRI_TRIFID',raw.get('TRI_IDS',''))]:
                for rid in __import__('re').split(r'[;,\s]+',ids):
                    rid=rid.strip()
                    if not rid or (s['org_id'],registry,rid) in existing:continue
                    newlinks.append(dict(org_id=s['org_id'],registry=registry,registry_id=rid,match_basis=f"echo_exporter_street_city_zip_name:{s['site_id']}",as_of=date,site_id=s['site_id']))
                    existing.add((s['org_id'],registry,rid))
            if len(newlinks)==before_links:continue
            typ='address';detail=f"EPA ECHO registrant {raw['FAC_NAME']}; REGISTRY_ID={r['id']}; {raw['FAC_STREET']}, {raw['FAC_CITY']}, OH {raw['FAC_ZIP']}"
        if typ:
            evidence.append(dict(evidence_id=f'EVD-{evdid:06d}',record_table='sites',record_id=s['site_id'],claim_type=typ,claim_detail=detail,source_class='government_filing' if typ=='size_band' else 'registry',source_ref=ref,observed_date=date,tier_effect='supports_U' if s['verification_tier']=='U' else 'supports_B' if typ=='size_band' else 'supports_C',created_by='atlas-w16-fed-rematch',notes='Banked ITA vintage 2026-11-01; ECHO exporter fetched 2026-11-16; extract receipt and matched raw rows in task packet. No tier change.'))
            evdid+=1
    band_ids={r['site_id'] for r in edits}
    link_ids={r['site_id'] for r in newlinks}
    for p in proposals:
        if p['disposition']=='applied' and p['site_id'] not in (band_ids if p['kind']=='ITA' else link_ids):
            p['disposition']='held'
            p['settling_fact']=band_holds.get(p['site_id'],'Existing band preserved; blank field required.' if p['kind']=='ITA' else 'Registry identity already linked; no duplicate append.')
    write(HERE/'frame.csv',sites,list(sites[0]))
    write(HERE/'proposals.csv',proposals,list(proposals[0]))
    aliases=[p for p in proposals if p['registrant'] and name_norm(p['registrant'])!=name_norm(p['atlas_name'])]
    write(HERE/'alias_followups.csv',aliases,list(proposals[0]))
    write(HERE/'registry_proposals.csv',newlinks,list(links[0]))
    write(HERE/'band_edits.csv',edits,['site_id','old_value','new_value'])
    write(HERE/'evidence.csv',evidence,list(read(ROOT/'data/evidence_sites_OH.csv')[0]))
    # Persist only matched raw public fields needed to audit quotes/counts.
    write(HERE/'witnesses.csv',[dict(site_id=s['site_id'],kind=r['kind'],source_id=r['id'],raw=json.dumps(r['raw'],sort_keys=True)) for s,r in witnesses],['site_id','kind','source_id','raw'])
    summary=dict(frame=len(sites),source_rows=dict(Counter(r['kind'] for r in src)),proposals=len(proposals),registry_links=len(newlinks),band_fills=len(edits),evidence=len(evidence),baseline=BASE)
    (HERE/'summary.json').write_text(json.dumps(summary,indent=2)+'\n');print(summary)
    if '--apply' in sys.argv:
        backup=CACHE/'pre-pass'; backup.mkdir(exist_ok=True)
        for name in ('registry_links.csv','sites_OH.csv','evidence_sites_OH.csv'):
            if not (backup/name).exists():(backup/name).write_bytes((ROOT/'data'/name).read_bytes())
        for file,rows,key in [('registry_links.csv',newlinks,None),('evidence_sites_OH.csv',evidence,'evidence_id')]:
            current=read(ROOT/'data'/file)
            if key:
                have={r[key] for r in current}
                indexed={r[key]:r for r in current}
                assert all(r[key] not in indexed or indexed[r[key]]==r for r in rows), 'Evidence ID collision'
                rows=[r for r in rows if r[key] not in have]
                if rows:append_sorted(ROOT/'data'/file,rows,key)
            else:
                have={(r['org_id'],r['registry'],r['registry_id']) for r in current}
                rows=[r for r in rows if (r['org_id'],r['registry'],r['registry_id']) not in have]
                if rows:write(ROOT/'data'/file,current+rows,list(current[0]))
        current=read(ROOT/'data/sites_OH.csv'); changes={r['site_id']:r['new_value'] for r in edits}
        for s in current:
            if s['site_id'] in changes:
                assert s['employee_band_site'] in ('',changes[s['site_id']]);s['employee_band_site']=changes[s['site_id']]
        write(ROOT/'data/sites_OH.csv',current,list(current[0]))
if __name__=='__main__':main()

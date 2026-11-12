import csv,io,sys,json,re,hashlib,os,collections
from extract import text_of
R='/workspace/atlas-ohio-nov12/repo/data/'; RAW='/workspace/atlas-ohio-nov12/raw/'
batch,evd0,cap0,date=sys.argv[1],int(sys.argv[2]),int(sys.argv[3]),'2026-11-12'
CAPM={'material':None,'process':{'custom_compounding':'compounding','compounding_unspecified':'compounding','compounding_extrusion':'compounding','injection_molding':'injection_molding','rotational_molding':'rotational_molding','compression_molding':'compression_molding','calendering':'calendering','color_masterbatch':'color_masterbatch','composites_pultrusion':'composites_pultrusion','reaction_injection_molding':'reaction_injection_molding','rubber_mixing_compounding':'rubber_mixing_compounding','coating_formulation':'coating_formulation','adhesive_sealant_formulation':'adhesive_sealant_formulation','blow_molding':'blow_molding','blow_molding_extrusion':'blow_molding','extrusion_profile':'extrusion','extrusion_pipe_tube':'extrusion','extrusion_sheet':'extrusion','extrusion_unspecified':'extrusion','thermoforming_unspecified':'thermoforming','thermoforming_vacuum':'thermoforming','thermoforming_pressure':'thermoforming','rubber_molding_compression':'rubber_molding','rubber_molding_injection':'rubber_molding','rubber_molding_unspecified':'rubber_molding','additive_manufacturing_polymer':'additive_manufacturing_polymer','recycling_mechanical':'recycling_mechanical'}}
sys.path.insert(0,'/workspace/atlas-ohio-nov12/repo/scripts')
src=open('/workspace/atlas-ohio-nov12/repo/scripts/validate.py').read()
CAP_MATERIAL=eval(re.search(r'CAP_MATERIAL = (\{.*?\})',src,re.S).group(1))
def trim(q,t):
    w=q.split(' ')
    while w and (not re.match(r'[A-Z0-9“"]',w[0]) or w[0] in(',','|','--')): w=w[1:]
    s=' '.join(w).strip(' ,|')
    m=re.search(r'^(.*[\.\)])\s',s+' ')
    if m and len(m.group(1).split())>=5: s=m.group(1)
    s=s.strip(' ,|')
    return s if s and s in t and len(s.split())<=25 else q
P={(p['site_id'],p['term']):p for p in csv.DictReader(open('cap_props.csv'))}
D=list(csv.DictReader(open(f'{batch}_cap_dec.csv')))
def load(p): 
    rd=csv.DictReader(open(p,newline='')); return rd.fieldnames,list(rd)
def save(p,h,rows):
    b=io.StringIO(); w=csv.DictWriter(b,fieldnames=h,lineterminator='\n'); w.writeheader(); w.writerows(rows); open(p,'w',newline='').write(b.getvalue())
sh,sites=load(R+'sites_OH.csv'); oh,orgs=load(R+'organizations_OH.csv')
S={r['site_id']:r for r in sites}; O={r['org_id']:r for r in orgs}
eh,es=load(R+'evidence_sites_OH.csv'); eoh,eo=load(R+'evidence_organizations_OH.csv'); ch,caps=load(R+'site_capabilities.csv')
live={(c['site_id'],c['capability_type'],c['term']) for c in caps if not c['withdrawn_date']}
col={'material':'materials','process':'processes'}
orig_s={(sid,c):S[sid][c] for sid in S for c in col.values()}
orig_o={(oid,c):O[oid][c] for oid in O for c in col.values()}
ev=evd0; cap=cap0; log=[]
for d in D:
    s=S[d['site_id']]; o=O[s['org_id']]; p=P[(d['site_id'],d['src_term'])]
    body=open(RAW+hashlib.sha1(p['url'].encode()).hexdigest()[:16]+'.html','rb').read() if os.path.exists(RAW+hashlib.sha1(p['url'].encode()).hexdigest()[:16]+'.html') else None
    if body is None:
        # url may be eff; find via fetch json
        for f in os.listdir(RAW):
            if f.endswith('.json'):
                m=json.load(open(RAW+f))
                if m.get('eff')==p['url'] or m.get('url')==p['url']: body=open(RAW+f[:-5]+'.html','rb').read(); break
    t=text_of(body); assert hashlib.sha256(body).hexdigest()==p['sha']
    q=d.get('quote') or trim(p['quote'],t); assert q in t and len(q.split())<=25,(q)
    c=col[d['type']]; out=dict(site_id=d['site_id'],org_id=s['org_id'],type=d['type'],term=d['term'],scope=d['scope'],url=p['url'],sha256=p['sha'],quote=q,site_ev='',org_ev='',cap='')
    note=f"Raw checked {date}; SHA-256 {p['sha']}; quote: {q}"
    if d['scope']=='site' and not orig_s[(d['site_id'],c)]:
        vals=[v for v in s[c].split(';') if v]
        if d['term'] not in vals: vals.append(d['term']); s[c]=';'.join(sorted(vals))
        eid=f'EVD-{ev:06d}'; ev+=1
        es.append(dict(evidence_id=eid,record_table='sites',record_id=d['site_id'],claim_type='scope',claim_detail=f"{c}={d['term']}; site-grain (single-location company); quote: {q}",source_class='own_site',source_ref=p['url'],observed_date=date,tier_effect='supports_A',created_by=f'grok-oh-cap-{batch}',notes=note+'. Site tag only; tier, ring, NAICS and status unchanged.'))
        out['site_ev']=eid
    if not orig_o[(o['org_id'],c)]:
        vals=[v for v in o[c].split(';') if v]
        if d['term'] not in vals: vals.append(d['term']); o[c]=';'.join(sorted(vals))
        eid=f'EVD-{ev:06d}'; ev+=1
        eo.append(dict(evidence_id=eid,record_table='organizations',record_id=o['org_id'],claim_type='scope',claim_detail=f"{c}={d['term']}; quote: {q}",source_class='own_site',source_ref=p['url'],observed_date=date,tier_effect='supports_A',created_by=f'grok-oh-cap-{batch}',notes=note+('. Corporate claim, not site allocation.' if d['scope']=='org' else '. Single-location company.')+' Org tier, ring and status unchanged.'))
        out['org_ev']=eid
    if d['scope']=='site':
        ct=d['term'] if d['type']=='material' and d['term'] in CAP_MATERIAL else (CAPM['process'] or {}).get(d['term']) if d['type']=='process' else None
        if ct and (d['site_id'],d['type'],ct) not in live:
            cid=f'CAP-{cap:06d}'; cap+=1; live.add((d['site_id'],d['type'],ct))
            caps.append(dict(capability_id=cid,site_id=d['site_id'],org_id=s['org_id'],capability_type=d['type'],term=ct,provenance='company_disclosed',source_ref=p['url'],observed_date=date,withdrawn_date='',created_by=f'grok-oh-cap-{batch}',notes=f"Ohio PIC-18 capability pass {batch} (tasks/oh-capabilities-{date}-{batch}/). Own-site page; site grain because the company shows a single location. Quote: {q}"))
            out['cap']=cid
    log.append(out)
save(R+'sites_OH.csv',sh,sites); save(R+'organizations_OH.csv',oh,orgs)
save(R+'evidence_sites_OH.csv',eh,es); save(R+'evidence_organizations_OH.csv',eoh,eo); save(R+'site_capabilities.csv',ch,caps)
w=csv.DictWriter(open(f'{batch}_cap_verdicts.csv','w'),fieldnames=list(log[0].keys()));w.writeheader();w.writerows(log)
print('evd',evd0,'..',ev-1,'cap',cap0,'..',cap-1,'site fills',sum(1 for l in log if l['site_ev']),'org fills',sum(1 for l in log if l['org_ev']),'caps',sum(1 for l in log if l['cap']))

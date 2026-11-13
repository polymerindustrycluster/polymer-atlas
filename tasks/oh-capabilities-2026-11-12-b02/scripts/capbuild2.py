import csv,io,sys,json,re,hashlib,os,subprocess
from extract import text_of
REPO='/workspace/atlas-ohio-nov12/repo/'; R=REPO+'data/'; RAW='/workspace/atlas-ohio-nov12/raw/'
batch,evd0,cap0,date=sys.argv[1],int(sys.argv[2]),int(sys.argv[3]),'2026-11-12'
RUL="owner ruling 2026-11-12 13:51 ET: own-site capability/menu lists count at a lower tier"
PM={'custom_compounding':'compounding','compounding_unspecified':'compounding','compounding_extrusion':'compounding','injection_molding':'injection_molding','rotational_molding':'rotational_molding','compression_molding':'compression_molding','transfer_molding':'compression_molding' if False else None,'calendering':'calendering','color_masterbatch':'color_masterbatch','composites_pultrusion':'composites_pultrusion','reaction_injection_molding':'reaction_injection_molding','rubber_mixing_compounding':'rubber_mixing_compounding','coating_formulation':'coating_formulation','adhesive_sealant_formulation':'adhesive_sealant_formulation','blow_molding':'blow_molding','blow_molding_extrusion':'blow_molding','blow_molding_injection':'blow_molding','blow_molding_stretch':'blow_molding','extrusion_profile':'extrusion','extrusion_pipe_tube':'extrusion','extrusion_sheet':'extrusion','extrusion_film_blown':'extrusion','extrusion_film_cast':'extrusion','extrusion_unspecified':'extrusion','thermoforming_unspecified':'thermoforming','thermoforming_vacuum':'thermoforming','thermoforming_pressure':'thermoforming','rubber_molding_compression':'rubber_molding','rubber_molding_injection':'rubber_molding','rubber_molding_unspecified':'rubber_molding','additive_manufacturing_polymer':'additive_manufacturing_polymer','additive_manufacturing_polymer_production':'additive_manufacturing_polymer','recycling_mechanical':'recycling_mechanical','polymerization':'polymerization'}
src=open(REPO+'scripts/validate.py').read()
CAP_MATERIAL=eval(re.search(r'CAP_MATERIAL = (\{.*?\})',src,re.S).group(1))
idx={}
for f in os.listdir(RAW):
    if f.endswith('.json'):
        m=json.load(open(RAW+f)); 
        for u in (m.get('url'),m.get('eff')):
            if u and os.path.exists(RAW+f[:-5]+'.html'): idx.setdefault(u,RAW+f[:-5]+'.html')
def load(p): rd=csv.DictReader(open(p,newline='')); return rd.fieldnames,list(rd)
def main_rows(p,k):
    t=subprocess.run(['git','-C',REPO,'show','origin/main:data/'+p],capture_output=True,text=True).stdout
    return {r[k]:r for r in csv.DictReader(io.StringIO(t))}
def save(p,h,rows):
    b=io.StringIO(); w=csv.DictWriter(b,fieldnames=h,lineterminator='\n'); w.writeheader(); w.writerows(rows); open(p,'w',newline='').write(b.getvalue())
sh,sites=load(R+'sites_OH.csv'); oh,orgs=load(R+'organizations_OH.csv')
S={r['site_id']:r for r in sites}; O={r['org_id']:r for r in orgs}
MS=main_rows('sites_OH.csv','site_id'); MO=main_rows('organizations_OH.csv','org_id')
eh,es=load(R+'evidence_sites_OH.csv'); eoh,eo=load(R+'evidence_organizations_OH.csv'); ch,caps=load(R+'site_capabilities.csv')
live={(c['site_id'],c['capability_type'],c['term']) for c in caps if not c['withdrawn_date']}
col={'material':'materials','process':'processes'}
ev=evd0; cap=cap0; log=[]
DEC=list(csv.DictReader(open(f'{batch}_dec2.csv')))
# V-25 guard: a C-only scope row on an A/B-tier record fails validate. Records with no A/B-strength scope support
# (main or this batch) keep menu-basis terms as CAP rows only; the section-3 tag is held for a ruling.
MEV={}
for r in es+eo:
    if r['claim_type']=='scope' and r['tier_effect'] in ('supports_A','supports_B'): MEV[r['record_id']]=MEV.get(r['record_id'],0)+1
def strong(rid,kind):
    if MEV.get(rid): return True
    for d in DEC:
        if d['basis']=='menu': continue
        s_=S[d['site_id']]; c_=col[d['type']]
        if kind=='site' and d['site_id']==rid and d['scope']=='site' and not MS[rid][c_]: return True
        if kind=='org' and s_['org_id']==rid and not MO[rid][c_]: return True
    return False
for d in DEC:
    assert d['site_id']!='SITE-000174'
    s=S[d['site_id']]; o=O[s['org_id']]; body=open(idx[d['url']],'rb').read(); t=text_of(body); q=d['quote']
    assert q in t and len(q.split())<=25,(d['site_id'],q)
    sha=hashlib.sha256(body).hexdigest(); c=col[d['type']]; menu=d['basis']=='menu'
    te='supports_C' if menu else 'supports_A'
    basis=f"basis: self-described menu ({RUL}); " if menu else ''
    out=dict(site_id=d['site_id'],org_id=s['org_id'],type=d['type'],term=d['term'],scope=d['scope'],basis=d['basis'],tier_effect=te,url=d['url'],sha256=sha,quote=q,site_ev='',org_ev='',cap='',held='')
    note=f"Raw checked {date}; SHA-256 {sha}; quote: {q}"
    held_s=menu and s['verification_tier'] in ('A','B') and not strong(d['site_id'],'site')
    held_o=menu and o['verification_tier'] in ('A','B') and not strong(o['org_id'],'org')
    out['held']=';'.join(x for x,h in (('site_tag_V25',held_s and d['scope']=='site' and not MS[d['site_id']][c]),('org_tag_V25',held_o and not MO[o['org_id']][c])) if h)
    if d['scope']=='site' and not MS[d['site_id']][c] and not held_s:
        vals=[v for v in s[c].split(';') if v]
        if d['term'] not in vals: vals.append(d['term']); s[c]=';'.join(sorted(vals))
        eid=f'EVD-{ev:06d}'; ev+=1
        es.append(dict(evidence_id=eid,record_table='sites',record_id=d['site_id'],claim_type='scope',claim_detail=f"{c}={d['term']}; site-grain (single-location company); {basis}quote: {q}",source_class='own_site',source_ref=d['url'],observed_date=date,tier_effect=te,created_by=f'grok-oh-cap-{batch}',notes=note+'. Site tag only; tier, ring, NAICS and status unchanged.'))
        out['site_ev']=eid
    if not MO[o['org_id']][c] and not held_o:
        vals=[v for v in o[c].split(';') if v]
        if d['term'] not in vals: vals.append(d['term']); o[c]=';'.join(sorted(vals))
        eid=f'EVD-{ev:06d}'; ev+=1
        eo.append(dict(evidence_id=eid,record_table='organizations',record_id=o['org_id'],claim_type='scope',claim_detail=f"{c}={d['term']}; {basis}quote: {q}",source_class='own_site',source_ref=d['url'],observed_date=date,tier_effect=te,created_by=f'grok-oh-cap-{batch}',notes=note+('. Corporate claim, not site allocation.' if d['scope']=='org' else '. Single-location company.')+' Org tier, ring and status unchanged.'))
        out['org_ev']=eid
    if d['scope']=='site':
        ct=(d['term'] if d['term'] in CAP_MATERIAL else None) if d['type']=='material' else PM.get(d['term'])
        if ct and (d['site_id'],d['type'],ct) not in live:
            cid=f'CAP-{cap:06d}'; cap+=1; live.add((d['site_id'],d['type'],ct))
            caps.append(dict(capability_id=cid,site_id=d['site_id'],org_id=s['org_id'],capability_type=d['type'],term=ct,provenance='company_disclosed',source_ref=d['url'],observed_date=date,withdrawn_date='',created_by=f'grok-oh-cap-{batch}',notes=f"Ohio PIC-18 capability pass {batch} (tasks/oh-capabilities-{date}-{batch}/). Own-site page; site grain because the company shows a single location. "+(f"Basis: self-described menu, lower confidence ({RUL}). "+("Section-3 site tag held: a supports_C scope row on this tier-"+s['verification_tier']+" site would fail V-25; ruling needed. " if held_s else '') if menu else '')+f"Quote: {q}"))
            out['cap']=cid
    log.append(out)
save(R+'sites_OH.csv',sh,sites); save(R+'organizations_OH.csv',oh,orgs)
save(R+'evidence_sites_OH.csv',eh,es); save(R+'evidence_organizations_OH.csv',eoh,eo); save(R+'site_capabilities.csv',ch,caps)
w=csv.DictWriter(open(f'{batch}_cap_verdicts.csv','w'),fieldnames=list(log[0].keys()),lineterminator='\n');w.writeheader();w.writerows(log)
import collections
print('held',sum(1 for l in log if l['held']),'evd',evd0,'..',ev-1,'cap',cap0,'..',cap-1,'site_ev',sum(1 for l in log if l['site_ev']),'org_ev',sum(1 for l in log if l['org_ev']),'caps',sum(1 for l in log if l['cap']),'sites tagged',len({l['site_id'] for l in log if l['site_ev'] or l['org_ev']}),collections.Counter((l['basis']) for l in log if l['site_ev'] or l['org_ev']))

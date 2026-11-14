import csv,sys,re,json,os,hashlib
from extract import text_of
RAW='/workspace/atlas-ohio-nov12/raw/'
P=[ # (regex, type, term) order matters: specific first
(r'liquid silicone rubber|\bLSR\b','process','injection_molding_lsr_silicone'),
(r'micro[- ]?molding','process','injection_molding_micro'),
(r'rubber injection molding|injection molded rubber','process','rubber_molding_injection'),
(r'reaction injection mold','process','reaction_injection_molding'),
(r'insert[- ]molding|over[- ]?molding','process','insert_overmolding'),
(r'(?:two|2|multi)[- ]shot','process','two_shot_molding'),
(r'extrusion blow mold','process','blow_molding_extrusion'),
(r'injection blow mold','process','blow_molding_injection'),
(r'stretch blow mold','process','blow_molding_stretch'),
(r'blow mold(?:ing|ed|er)','process','blow_molding'),
(r'(?<!rubber )(?<!blow )injection mold(?:ing|ed|er)s?','process','injection_molding'),
(r'blown film','process','extrusion_film_blown'),
(r'cast film','process','extrusion_film_cast'),
(r'sheet extrusion|extruded (?:plastic )?sheet','process','extrusion_sheet'),
(r'profile extrusion|extruded profiles?|custom profiles?','process','extrusion_profile'),
(r'(?:tube|tubing|pipe) extrusion|extruded (?:tubing|tubes|pipe)','process','extrusion_pipe_tube'),
(r'rubber extrusion|extruded rubber','process','rubber_extrusion'),
(r'vacuum form(?:ing|ed)','process','thermoforming_vacuum'),
(r'pressure form(?:ing|ed)','process','thermoforming_pressure'),
(r'thermoform(?:ing|ed|er)','process','thermoforming_unspecified'),
(r'rotational(?:ly)? mold(?:ing|ed)|roto[- ]?mold(?:ing|ed)','process','rotational_molding'),
(r'(?<!rubber )compression mold(?:ing|ed)','process','compression_molding'),
(r'rubber compression mold','process','rubber_molding_compression'),
(r'transfer mold(?:ing|ed)','process','transfer_molding'),
(r'calender(?:ing|ed)','process','calendering'),
(r'rubber (?:mixing|compounding)|custom (?:rubber )?mixing','process','rubber_mixing_compounding'),
(r'custom compound(?:ing|er)|toll compound(?:ing|er)','process','custom_compounding'),
(r'color concentrates?|masterbatch(?:es)?','process','color_masterbatch'),
(r'pultru(?:sion|ded)','process','composites_pultrusion'),
(r'filament[- ]wound|filament winding','process','composites_filament_winding'),
(r'hand lay[- ]?up','process','composites_hand_layup'),
(r'sheet molding compound|\bSMC\b|\bBMC\b','process','composites_compression_smc_bmc'),
(r'resin transfer molding|vacuum infusion','process','composites_rtm_infusion'),
(r'3D printing|additive manufacturing','process','additive_manufacturing_polymer'),
(r'CNC machin(?:ing|ed)|plastic machining|machined plastic','process','plastics_machining_cnc'),
(r'plastic(?:s)? fabricat(?:ion|ing|or)|plastic welding','process','plastics_fabrication_welding'),
(r'die[- ]cut(?:ting)?','process','die_cutting_converting'),
(r'\blaminat(?:ing|ion)\b','process','laminating'),
(r'pad printing|screen printing|hot stamping','process','printing_decorating_plastics'),
(r'ultrasonic welding','process','ultrasonic_solvent_bonding'),
(r'mold (?:making|building|design and build)|mold builder|tool (?:and|&) die','process','mold_tool_making'),
(r'foam fabricat','process','foam_fabrication'),
(r'pelletiz(?:ing|ed)|regrind','process','regrind_pelletizing'),
(r'urethane casting|cast urethane|potting|encapsulation','process','potting_encapsulation_casting'),
(r'polypropylene','material','polypropylene_pp'),
(r'polyethylene|\bHDPE\b|\bLDPE\b|\bUHMW','material','polyethylene_pe'),
(r'\bPVC\b|polyvinyl chloride','material','pvc'),
(r'\bPETG?\b','material','pet_petg'),
(r'polystyrene|\bHIPS\b','material','polystyrene_ps_hips'),
(r'polycarbonate','material','polycarbonate_pc'),
(r'\bnylon\b','material','nylon_pa'),
(r'\bABS\b','material','abs'),
(r'\bacetal\b|delrin','material','acetal_pom'),
(r'\bPEEK\b|ultem|\bPEI\b','material','peek_high_performance'),
(r'\bepoxy','material','epoxy'),
(r'polyurethane|\burethane','material','polyurethane_pu'),
(r'phenolic','material','phenolic'),
(r'silicone','material','silicones'),
(r'\bPTFE\b|teflon|fluoropolymer|\bFEP\b|\bPFA\b','material','fluoropolymers'),
(r'\bEPDM\b','material','epdm'),
(r'nitrile|\bNBR\b|buna[- ]n','material','nitrile_nbr'),
(r'neoprene','material','neoprene_cr'),
(r'viton|\bFKM\b','material','viton_fkm'),
(r'natural rubber','material','natural_rubber_nr'),
(r'\bSBR\b','material','sbr'),
(r'\bTPE\b|\bTPU\b|\bTPV\b|thermoplastic elastomer','material','thermoplastic_elastomers_tpe_tpu'),
(r'\bTPO\b','material','thermoplastic_olefin_tpo'),
(r'acrylic|\bPMMA\b|plexiglas','material','acrylic_pmma'),
(r'\bthermoplastics?\b','material','thermoplastics'),
(r'thermoset','material','thermosets'),
(r'\brubber\b','material','elastomers_rubber'),
(r'fiberglass|\bFRP\b','material','composites_frp'),
]
P=[(re.compile(a,re.I),b,c) for a,b,c in P]
def quote(t,m):
    # words window <=25 including match
    a=t[:m.start()].split(' '); b=t[m.end():].split(' ')
    mw=m.group(0)
    pre=' '.join(a[-9:]).strip(); post=' '.join(b[:9]).strip()
    q=(pre+' '+mw if not t[:m.start()].endswith(' ') else pre+' '+mw)
    s=max(0,m.start()-1); 
    # simpler: build from token positions
    L=len(t[:m.start()].rstrip().split()) if t[:m.start()].strip() else 0
    toks=t.split(' ')
    return None
def window(t,m,n=9):
    st=m.start(); en=m.end()
    i=st; c=0
    while i>0 and c<n:
        i-=1
        if t[i]==' ': c+=1
    j=en; c=0
    while j<len(t) and c<n:
        if t[j]==' ': c+=1
        j+=1
    q=t[i:j].strip(' ,|')
    q=re.sub(r'\s*,\s*,\s*',', ',q)
    return q
OTHER=re.compile(r'\b(?:AL|AZ|AR|CA|CO|CT|DE|FL|GA|IL|IN|IA|KS|KY|LA|MD|MA|MI|MN|MS|MO|NC|NE|NV|NH|NJ|NM|NY|OK|OR|PA|SC|TN|TX|UT|VA|WA|WV|WI|Mexico|China)\s*,?\s+\d{5}\b')
LOC=re.compile(r'\b(?:our|other|all|multiple) (?:locations|facilities|plants)\b|\blocations\b',re.I)
frame={r['site_id']:r for r in csv.DictReader(open(sys.argv[1]))}
fetch=json.load(open(sys.argv[2])); out=[]
for sid,log in fetch.items():
    if sid not in frame: continue
    r=frame[sid]; seen={}; other=set(); loc=0
    for meta in log:
        if not meta['code'].startswith('2'): continue
        if re.search(r'career|job|employ',meta['url'],re.I): continue
        h=hashlib.sha1(meta['url'].encode()).hexdigest()[:16]; p=RAW+h+'.html'
        if not os.path.exists(p): continue
        body=open(p,'rb').read(); t=text_of(body)
        for m in OTHER.finditer(t): other.add(m.group(0))
        if LOC.search(t): loc=1
        taken=[]
        for rx,ty,term in P:
            for m in rx.finditer(t):
                if any(a<=m.start()<b for a,b in taken): continue
                taken.append((m.start(),m.end()))
                if (ty,term) not in seen:
                    q=window(t,m)
                    if len(q.split())<=25 and q in t: seen[(ty,term)]=dict(url=meta['eff'] or meta['url'],sha=hashlib.sha256(body).hexdigest(),quote=q)
                break
    for (ty,term),v in seen.items():
        out.append(dict(site_id=sid,name=r['site_name'],type=ty,term=term,**v,other='; '.join(sorted(other))[:120],loc=loc))
w=csv.DictWriter(open(sys.argv[3],'w'),fieldnames=['site_id','name','type','term','url','sha','quote','other','loc']);w.writeheader();w.writerows(out)
import collections
print(len(out),len(set(o['site_id'] for o in out)),collections.Counter(o['term'] for o in out).most_common(15))

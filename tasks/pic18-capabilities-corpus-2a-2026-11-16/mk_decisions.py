"""Writes decisions.csv from the hand-adjudicated entries below (quote + locality witness resolved against the stored corpus)."""
import csv, hashlib, html, re, sys
from pathlib import Path
T = Path(__file__).resolve().parent
CORPUS = Path('/Users/johnswanson/.bb/thread-storage/thr_9i2c6byhcz/2026-11-06-atlas/persist/pic18-corpus-2026-11-16')
ORG = {r['site_id']: r['org_id'] for r in csv.DictReader((T / 'slice.csv').open())}
MAN = [r for r in csv.DictReader((CORPUS / 'manifest.csv').open()) if r['text_file']]
H = 'https://'
# (site number, field, [terms], basis, page url, quote, locality-page url, locality quote)
E = []
def add(n, field, terms, basis, url, quote, gurl, gq):
    for t in terms: E.append((n, field, t, basis, url, quote, gurl, gq))
oe = 'ohioelastomers.com/'
add(198,'processes',['mold_tool_making'],'narrative',H+'ohioelastomers.com/','Our mold makers have decades of rubber mold building experience allowing them to tackle the most challenging part designs.',H+'ohioelastomers.com/','3470 Blackmore Road Perry, OH 44081')
add(198,'processes',['transfer_molding'],'narrative',H+'www.ohioelastomers.com/about-us','Ohio Elastomers is a leading manufacturer of engineered rubber solutions servicing a diverse mix of industries by utilizing our deep knowledge of rubber transfer molding.',H+'ohioelastomers.com/','3470 Blackmore Road Perry, OH 44081')
al = H+'www.allpasscorporation.com/'
add(239,'materials',['polyethylene_pe','polypropylene_pp'],'menu',al,'PEX(Polyethylene), Poly sulfone and Polypropylene Tubing',al,'222 North Lake Street P.O Box 10 Madison, Ohio 44057')
am = H+'americanmoldedplastic.com/about-us.htm'
add(243,'processes',['injection_molding'],'narrative',am,'Since 1990, American Molded Plastic, Inc., has been custom injection molding thermoplastic and other materials and producing molded products to exacting specification.',am,'Newton Falls, Ohio USA')
add(243,'materials',['thermoplastics'],'narrative',am,'Since 1990, American Molded Plastic, Inc., has been custom injection molding thermoplastic and other materials and producing molded products to exacting specification.',am,'Newton Falls, Ohio USA')
ch = H+'chardoncp.com/'
add(287,'processes',['rubber_mixing_compounding'],'narrative',ch,'Chardon Custom Polymers is a manufacturer of elastomeric rubber compounds for a variety of industries and uses in North America.',ch,'373 Washington St. Chardon OH 44024')
add(287,'materials',['elastomers_rubber'],'narrative',ch,'Chardon Custom Polymers is a manufacturer of elastomeric rubber compounds for a variety of industries and uses in North America.',ch,'373 Washington St. Chardon OH 44024')
it = H+'www.industrialtech.info/contact'
add(402,'materials',['silicones','polyurethane_pu'],'narrative',it,'Founded in 1995 in Akron, Ohio. We started building composite tooling for 15 years and began building our silicone and polyurethane product offerings.',it,'Founded in 1995 in Akron, Ohio')
ke = H+'www.keylandpolymer.com/'
add(438,'materials',['epoxy'],'narrative',ke,'Develops, produces, and sells solid polyester, epoxy, and other resins used in powder coatings and other UV cured solid materials.',ke,'4641 Hinckley Industrial Parkway Cleveland, OH 44109')
ma = H+'malishplastics.com/'; mg = 'Malish US 7333 Corporate Boulevard Mentor, Ohio 44060'
add(458,'processes',['extrusion_profile','extrusion_pipe_tube'],'narrative',ma,'Extruders of custom thermoplastic profiles, tube and pipe.',ma,mg)
add(458,'materials',['thermoplastics'],'narrative',ma,'Extruders of custom thermoplastic profiles, tube and pipe.',ma,mg)
add(458,'materials',['polypropylene_pp','polyethylene_pe','abs','asa','pvc'],'narrative',ma,'thermoplastic materials and custom compounds, including, but not limited to Polypropylene, Polyethylene, ABS, ASA, Flexible and rigid PVC,',ma,mg)
add(458,'materials',['polystyrene_ps_hips','thermoplastic_elastomers_tpe_tpu','polycarbonate_pc'],'narrative',ma,'Flexible and rigid PVC, Polystyrene, CAB, TPR, TPE, TPV, Hytrel, and Polycarbonate.',ma,mg)
np_ = H+'neff-perkins.com/capabilities/'; ng = '16080 Industrial Pkwy Middlefield, OH 44062'
add(490,'processes',['compression_molding','transfer_molding','injection_molding'],'narrative',np_,'Whether it’s compression molding, transfer molding, or injection molding, we have the capabilities to select the most suitable process',np_,ng)
add(490,'materials',['elastomers_rubber','silicones'],'narrative',np_,'Our core competency lies in custom molding of rubber, silicone, and plastic',np_,ng)
add(490,'materials',['thermoplastics','thermosets'],'narrative',np_,'From natural and synthetic rubbers to thermoplastics and thermosetting plastics, we have the knowledge',np_,ng)
pr = H+'profilerubber.com/'; pg = H+'profilerubber.com/contact-us.html'; pgq = 'Shipping Address: Profile Rubber Corp., Inc. 350 State Street Building #7 Wadsworth, OH 44281'
add(562,'processes',['compression_molding','transfer_molding'],'menu',pr,'Services Compression Molding Transfer Molding Tooling Custom Moldings',pg,pgq)
add(562,'materials',['elastomers_rubber'],'narrative',pr,'Profile Rubber Corporation has been supplying the world with high-quality custom molded rubber products.',pg,pgq)
ro = H+'royalplastics.com/'
add(591,'processes',['injection_molding'],'narrative',ro,'Since 1966, Royal Plastics, Inc of Mentor, Ohio, has become a leading full-service custom manufacturer of injection molded plastic parts.',ro,'Royal Plastics, Inc of Mentor, Ohio')
sp = H+'www.spartonenterprises.com/'; spg = '861 Norton Ave , Barberton, OH 44203'
add(618,'processes',['recycling_unspecified'],'narrative',sp+'about','Sparton Enterprises started as a small rubber recycling operation and has grown into a fully integrated manufacturer of recycled rubber materials.',sp+'about',spg)
add(618,'materials',['elastomers_rubber'],'narrative',sp+'products','We process millions of pounds of various types of rubber annually.',sp+'products',spg)
add(618,'materials',['epdm','sbr'],'narrative',sp,'We offer readily available EPDM granules, SBR granules, rubber chips, broadcast granules, and spray rubber materials used for running tracks.',sp,spg)
tm = H+'treemen.com/'; tg = 'Treemen Industries, Inc 691 McClurg Road Boardman, OH 44512'
add(651,'processes',['injection_molding'],'narrative',tm,'Thermoplastic Injection Molding Automated robots and conveyors are used with thermoplastic injection presses to remove parts efficiently and effectively',tm,tg)
add(651,'materials',['thermoplastics'],'narrative',tm,'Thermoplastic Injection Molding Automated robots and conveyors are used with thermoplastic injection presses to remove parts efficiently and effectively',tm,tg)
add(651,'materials',['polycarbonate_pc','abs','acrylic_pmma','asa','nylon_pa','polypropylene_pp'],'narrative',tm,'Current materials/resins processed include PC, HT-PC, PC/ABS, PPS, PEI/Ultem, ABS, Acrylic-PMMA, ASA, Nylon, PBT, PAR and PP.',tm,tg)
ai = H+'www.alliance-innovations.com/about'
add(707,'processes',['compression_molding','thermoforming_unspecified'],'narrative',ai,'Our expert team excels in compression molding, thermoforming, tooling, fixtures, and additive manufacturing',ai,'About Us | Alliance Innovations LLC | Mansfield, Ohio')
fx = H+'www.flextechnologies.com/'; fg = '5479 Gundy Drive • Midvale, Ohio 44653'
add(909,'processes',['custom_compounding'],'narrative',fx,'From custom compounding to final assembly, Flex Technologies delivers fully integrated thermoplastic solutions',fx,fg)
add(909,'materials',['thermoplastics'],'narrative',fx,'From custom compounding to final assembly, Flex Technologies delivers fully integrated thermoplastic solutions',fx,fg)
add(909,'materials',['pvc'],'narrative',fx,'Polyflex, a division of Flex Technologies, is your U.S.-based source for precision PVC compounding.',fx,fg)
add(909,'processes',['extrusion_pipe_tube','extrusion_profile'],'narrative',fx,'Custom Extruded Products We produce high-performance extruded tubing and profiles tailored to your material, size, and performance needs.',fx,fg)
add(909,'processes',['injection_molding'],'narrative',fx,'Injection Molded Components Our injection molded components are built to meet strict tolerances and withstand demanding environments.',fx,fg)
add(909,'processes',['plastics_fabrication_welding'],'narrative',fx+'products','We also offer expert thermoplastic tube forming, plastic welding services (USA), injection and shuttle molding, and extrusion to support fully integrated fluid assemblies',fx+'products','Our Midvale, Ohio facility features in-house tooling')
kd = H+'kar-delplastics.com/'; kg = 'Kar-Del Plastics Inc 1177 Faultless Dr, Ashland, OH 44805'
add(987,'processes',['fabrication_unspecified'],'menu',kd+'capabilities','Capabilities We Offer * Custom Fiberglass Fabrication * Installations * QC & Inspections',kd+'capabilities',kg)
add(987,'materials',['polypropylene_pp'],'menu',kd+'capabilities','PVC * CPVC * Polypropylene * Others per request',kd+'capabilities',kg)
add(987,'materials',['composites_frp'],'narrative',kd+'products-%26-services','We manufacture the following standard FRP Fiberglass duct sizes.',kd+'products-%26-services',kg)
add(987,'materials',['pvc','thermoplastics'],'narrative',kd+'products-%26-services','These can be made from a general purpose, a corrosion resistant Fiberglass or a thermoplastic ( PVC, CPVC ) material.',kd+'products-%26-services',kg)
pm = H+'paramontmachinecompany.com/'
add(1109,'processes',['plastics_machining_cnc'],'narrative',pm,'We are capable of holding tight tolerances and fine-machined surface finishes on plastic machined parts.',pm,'963 Commercial Ave. S.E. New Philadelphia, Ohio 44663')
pn = H+'polynew.com/'
add(1125,'processes',['regrind_pelletizing'],'narrative',pn,'Clean, quality regrind processed by Polynew can help you slash material costs and eliminate waste disposal problems.',pn+'about.htm','we moved to a larger facility in Baltic, Ohio')
add(1125,'materials',['thermoplastics'],'narrative',pn,'thermoplastic material destined for regrind often gets confused with shop trash and floor sweep',pn+'about.htm','we moved to a larger facility in Baltic, Ohio')
ps = H+'poly-stamp.com/about-us'
add(546,'processes',['recycling_unspecified'],'narrative',ps,'The ingenuity of our unique formulations enables us to recycle all types of plastic.',ps,'427 Thacher Ln Youngstown, OH 44515')
vv = H+'www.vinylume.com/'
add(667,'processes',['extrusion_unspecified'],'menu',vv,'Contact us about your vinyl extrusion projects.',vv,'3745 Hendricks Rd Youngstown,OH 44515')

def norm(t): return ' '.join(t.split())
def page(url):
    rows = [r for r in MAN if r['url'] == url]
    assert rows, url
    return rows[0]
def raw_has(raw_path, quote):
    plain = html.unescape(re.sub('<[^>]+>', ' ', Path(raw_path).read_text(errors='replace')))
    words = iter(re.findall(r'\w+', plain.lower()))
    return all(any(w == q for w in words) for q in re.findall(r'\w+', quote.lower()))
def main():
    out = []
    for n, field, term, basis, url, quote, gurl, gq in E:
        sid = 'SITE-%06d' % n; p = page(url); g = page(gurl)
        text = norm((CORPUS / p['text_file']).read_text()); gtext = norm((CORPUS / g['text_file']).read_text())
        assert norm(quote) in text, (sid, 'quote', quote); assert norm(gq) in gtext, (sid, 'grain', gq)
        assert len(quote.split()) <= 25, (sid, 'long quote')
        out.append(dict(site_id=sid, field=field, term=term, quote=quote, basis=basis, url=p['url'], raw_file=p['raw_file'], text_file=p['text_file'], sha256=p['sha256'],
                        grain_quote=gq, grain_url=g['url'], grain_text_file=g['text_file']))
    with (T / 'decisions.csv').open('w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(out[0]), lineterminator='\n'); w.writeheader(); w.writerows(out)
    print(len(out), 'term decisions;', len({d['site_id'] for d in out}), 'sites')
if __name__ == '__main__': main()

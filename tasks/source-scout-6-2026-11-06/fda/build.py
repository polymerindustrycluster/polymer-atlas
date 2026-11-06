"""FDA Establishment Registration & Device Listing -> US facility frame (Manufacturer / Contract Manufacturer of polymer-named product codes)
and a seeded 20-row sample matched against the Atlas. Usage: python3 -I build.py   (reads the unzipped FDA files under PERSIST/fda)"""
import csv,re,sys,hashlib,json,collections
from pathlib import Path
HERE=Path(__file__).resolve().parent;sys.path.insert(0,str(HERE.parent));import common
D=common.PERSIST/'fda'
# Product codes carry no material class. Stated filter: DEVICENAME names a polymer/plastic/elastomer material, review panel is not an IVD
# reagent panel (CH HE IM MI PA TX: ion-exchange 'resin' reagents etc. are not polymer products).
POLY=re.compile(r'\b(plastic|polymer|polymeric|silicone|polyethylene|polypropylene|polyvinyl|pvc|polyurethane|polyester|polycarbonate|pmma|polymethyl|acrylic|nylon|polyamide|ptfe|polytetrafluoroethylene|latex|elastomer|rubber|polystyrene|polyimide|polyglycolic|polylactic|polydioxanone|peek|polysulfone|hydrogel|vinyl)\b',re.I)
IVD={'CH','HE','IM','MI','PA','TX'}
def poly_code(devicename,panel):return bool(POLY.search(devicename or '')) and panel not in IVD
def street_of(g):
 # a few registrants put a department or building name in line 1 and the street in line 2: take the line that has a number
 a,b=g['ADDRESS_LINE_1'].strip(),g['ADDRESS_LINE_2'].strip()
 return a if re.search(r'\d',a) or not b else b
def rd(rel):
 return list(csv.DictReader(open(D/rel,encoding='cp1252',errors='replace',newline=''),delimiter='|',quoting=csv.QUOTE_NONE))
def main():
 # known answers for the code filter
 assert poly_code('Bracket, Plastic, Orthodontic','DE') and poly_code('Heart-Valve, Polymeric','CV') and poly_code('Catheter, Silicone Foley','GU')
 assert not poly_code("Resin, Ion-Exchange, Thioglycolic Acid, Colorimetry, Iron Binding Capacity",'CH') and not poly_code('Scalpel, Stainless','GS') and not poly_code('Starch-Dye Bound Polymer, Amylase','CH')
 codes={r['PRODUCTCODE']:r['DEVICENAME'] for r in rd('x_foiclass/foiclass.txt') if poly_code(r['DEVICENAME'],r['REVIEW_PANEL'])}
 reg=rd('x_Registration/Registration.txt');rl=rd('x_registration_listing/registration_listing.txt');pcd=rd('x_Listing_PCD/Listing_PCD.txt');le=rd('x_listing_estabtypes/listing_estabtypes.txt')
 pc=collections.defaultdict(set)
 for r in pcd:pc[r['key_val']].add(r['PRODUCT_CODE'])
 et=collections.defaultdict(set)
 for r in le:et[(r['REG_KEY'],r['REGISTRATION_LISTING_ID'])].add(r['ESTABLISHMENT_TYPE_ID'])
 # ADDRESS_TYPE_ID F = facility; U = the US *agent's* address (a person's name) for a foreign facility: never a US establishment.
 fac={r['REG_KEY']:r for r in reg if r['ADDRESS_TYPE_ID']=='F' and r['ISO_COUNTRY_CODE']=='US' and r['REG_STATUS_ID']=='1'}
 hit={};listed=set()
 for r in rl:
  g=fac.get(r['REG_KEY'])
  if not g:continue
  listed.add(r['REG_KEY']);h=pc[r['KEY_VAL']]&set(codes)
  if h and et[(r['REG_KEY'],r['REGISTRATION_LISTING_ID'])]&{'1','5'}:hit.setdefault(r['REG_KEY'],set()).update(h)
 frame=[dict(registration_number=fac[k]['REGISTRATION_NUMBER'],fei_number=fac[k]['FEI_NUMBER'],name=fac[k]['NAME'].strip(),street=street_of(fac[k]),street2='',
  city=fac[k]['CITY'].strip(),state=fac[k]['STATE_ID'],zip=fac[k]['ZIP_CODE'],polymer_product_codes=';'.join(sorted(h))) for k,h in hit.items()]
 assert len(frame)==len({r['registration_number'] for r in frame})
 common.write_csv(HERE/'frame.csv',sorted(frame,key=lambda r:r['registration_number']))
 A=common.Atlas();out=[]
 for r in common.draw(frame,'registration_number'):
  m=A.match(r['name'],r['street'],r['city'],r['state'],r['zip'],registry=('FDA_FEI',r['fei_number']))
  out.append(dict(r,**m))
 common.write_csv(HERE/'sample_pre.csv',out)
 raw={f:hashlib.sha256((D/f).read_bytes()).hexdigest() for f in ['Registration.zip','registration_listing.zip','Listing_PCD.zip','listing_estabtypes.zip','foiclass.zip','estabtypes.zip']}
 stats=dict(registration_rows=len(reg),us_facility_active=len(fac),us_facility_with_listing=len(listed),polymer_product_codes=len(codes),frame=len(frame),
  states_in_frame=len({r['state'] for r in frame}),input_sha256=raw)
 (HERE/'counts.json').write_text(json.dumps(stats,indent=1)+'\n');print(stats)
if __name__=='__main__':main()

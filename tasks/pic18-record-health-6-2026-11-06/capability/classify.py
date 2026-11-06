"""Freeze initial research routing before new capability work; no canonical writes."""
from inventory import D,norm
import csv,json,re,hashlib
from urllib.parse import urlsplit
F=json.loads((D/'frame.json').read_text());P=json.loads((D/'prior_routes.json').read_text());E=json.loads((D/'prior_evidence.json').read_text());allprior={u for v in P.values() for u in v}
B={
'ORG-000400':('Own Soil Moist PLUS product PDF states synthetic acrylic water-storing polymer; PMMA is not established. Organization lacks material_other_note.','Owner decision on admissible representation of polyacrylamide/unspecified acrylic chemistry, or an explicit different adopted material claim.'),
'ORG-001768':('Own resin/polyimide-bond grinding wheels are explicit; unspecified resin does not establish thermoset/phenolic, and polyimide has no adopted specific material tag.','Owner vocabulary/scope decision for explicit polyimide resin-bond grinding wheels; no new term self-authored.'),
'ORG-001462':('Held record is a technical center rather than an established polymer-producing corporation; organization/center capability grain needs an owner ruling before borrowing Tenneco production claims.','Owner ruling on technical-center versus corporate capability grain and qualifying operations for this held record.')}
DE={
'ORG-000249':'Prior own about page calls BMS a global distributor of mold-building products and plastic processing equipment; supplier sales do not establish own polymer transformation.',
'ORG-000266':'Prior own CermeTech product/about pages explicitly describe SiC ceramic precursors and aluminum/magnesium composites, not polymer composites; positive non-polymer activity warrants scope re-verification.',
'ORG-000289':'Prior own CRT pages describe supplying/stocking tanks and quotation/shipping; own polymer manufacturing was not established. Re-verify held producer scope from positive distribution model.',
'ORG-000351':'Prior own Gem City product-lines page/PDF lists machinery represented/sold; injection/blow-molding applications belong to customers. Re-verify held producer scope.',
'ORG-000420':'Prior own Linden about page expressly describes polyurethane processing machinery/mix-head manufacture. Re-verify held polymer-producer scope; machinery sold does not establish polyurethane production.',
'ORG-000552':'Prior own Rogers home explicitly states Worldwide Manufacturer of Tire Curing Machinery. Re-verify held producer scope, rather than inferring tire/rubber curing activity.',
'ORG-001580':'Prior own CSI toll page explicitly describes solvent/aqueous blends and solvent recycling, not polymer compounding/recycling. Positive non-polymer business model warrants scope re-verification.',
'ORG-001717':'Prior own FlexLink pages say it markets specialty papers/films/laminations using a worldwide supply base; own lamination manufacture was not established. Re-verify held producer scope.'}
C={
'ORG-000014':'No identity-matched own public domain is held; prior Akron/California namesake rejection remains unresolved. Human contact/identity confirmation needed before corporate capability claims.',
'ORG-000021':'No identity-matched own public domain or explicit controlled own-operation witness in reviewed packet; human identity/capability confirmation needed.',
'ORG-000286':'Reviewed own drum/tote reconditioning pages do not specify controlled polymer chemistry or an own adopted transformation; empty disclosure PDF supplies no evidence. Need human explanation of actual polymer operation.',
'ORG-000608':'Reviewed dispensing-product/history pages do not state a controlled polymer chemistry or own polymer processing. Human specification of company-produced polymer components would settle it.',
'ORG-000697':'Reviewed Hedstrom toy/product/about pages do not explicitly identify controlled polymer material or own molding method; brand products do not establish operator capability.',
'ORG-000927':'Reviewed own PMA mechatronics/actuator pages do not explicitly identify controlled polymer chemistry or own processing; needs human process/material confirmation.',
'ORG-001388':'Reviewed Hy-Ko own key-programming/sign PDF and product pages do not state an own polymer process or controlled material specification; human component/manufacturing confirmation needed.',
'ORG-001726':'Reviewed candidate pages style Chesterland POBox/association and government source names Stewart Acquisitions DBA Endura, not held Kirtland Inc continuity. Human/legal identity bridge needed before capability attribution.',
'ORG-001764':'Prior NMC candidate produced no matched identity; unrelated National Material Company excluded. Human exact entity/domain confirmation required, not another unmatched metals name.',
'ORG-001777':'Reviewed own Anchor pages style Anchor Industries Inc, with no explicit American Consolidated Industries bridge; same Solon address does not settle identity. Human/legal bridge required.',
'ORG-001919':'No matched own public domain or corporate operation witness in reviewed packet; human exact identity/domain and polymer operation confirmation needed.',
'ORG-001920':'Reviewed directory heat-sealing/vinyl descriptions have no matched own domain/operator. Human exact corporate public source and operation confirmation required.',
'ORG-001921':'Reviewed Potters candidate own pages name Malvern PA global HQ, not held Potter\'s Inc Cleveland identity. Human/legal identity bridge required before parent glass-additive attribution.',
'ORG-001944':'No matched own domain in reviewed packet; historical OSHA/directory listing does not establish fresh own controlled capability. Human corporate identity/source confirmation needed.',
'ORG-002024':'No matched own corporate source in reviewed packet; human exact Tolloti Pipe identity and polymer versus nonpolymer pipe operation needed.',
'ORG-002050':'No matched own public corporate identity/source in reviewed packet; human exact Diskin entity and controlled polymer operation/material confirmation needed.',
'ORG-002064':'Frozen candidate explicitly rejected as not this firm\'s domain. Human exact Middlefield Poly Tech identity/domain required before assigning any capability.',
'ORG-002145':'No matched own corporate domain in reviewed packet; human exact All Coatings entity and formulation versus application operation required.',
'ORG-002159':'No matched own domain or explicit corporate capability in reviewed packet; human identity/domain/operation confirmation needed.',
'ORG-002168':'Reviewed Akrochem history identifies Revlis in1971 but no current distinct Revlis corporate operation. Human/legal current identity/grain bridge required.'}
FACTS={
'ORG-000017':'Chemigon polymer additives formulation manufacture technical data',
'ORG-000049':'Prophene polymer material production composition manufacturing',
'ORG-000078':'Giesecke Devrient America payment cards recycled PVC PETG manufacturing',
'ORG-000107':'T M Plastics extrusion molding polyethylene manufacturing',
'ORG-000207':'A.R.E. truck caps fiberglass composite manufacturing',
'ORG-000210':'Addipel powder blends compacted pellets polymer additives manufacturing',
'ORG-000363':'Hanlon Composites resin fiberglass fabrication manufacturing',
'ORG-000379':'Infinity Goodyear air springs rubber manufacturing technical materials',
'ORG-000389':'J.J. White Products adhesion coating treatment process manufacturing',
'ORG-000401':'JuggerBot in house polymer additive manufacturing service not printer sales',
'ORG-000407':'American Marble cultured marble polyester resin manufacturing',
'ORG-000414':'Koroseal own wallcovering PVC resin calendering composition',
'ORG-000433':'McCann Plastics custom compounding technical material production',
'ORG-000439':'Mickey Thompson tire manufacturing rubber compound own production',
'ORG-000441':'Mid West Poly Pak polyethylene film bag manufacturing',
'ORG-000484':'Performance Elastomers Ravenna EPDM silicone extrusion manufacturing',
'ORG-000488':'Pharmacy Lite bottles polypropylene manufacturing molding',
'ORG-000581':'Speed North America Wooster nylon monofilament extrusion production',
'ORG-000635':'Wooster Brush own polypropylene nylon bristle manufacturing material',
'ORG-000873':'Hamilton Polymers Leetonia polymer recycling pelletizing manufacturing',
'ORG-000999':'Okamoto Sandusky plastic film manufacturing polyethylene',
'ORG-001183':'Ventra plastics injection molding Flex N Gate manufacturing',
'ORG-001453':'Flow Polymers Cleveland polymer dispersions additives manufacturing',
'ORG-001459':'RFD Beaufort Sharon Center coated fabrics inflatable manufacturing',
'ORG-001526':'Viscus Biologics polymer collagen scaffold manufacturing',
'ORG-001595':'Eleven 10 own RIGID tourniquet case injection molded nylon material',
'ORG-001642':'Motivo display acrylic fabrication plastics manufacturing',
'ORG-001648':'Worthington TUFFBOOM HDPE molded polyethylene boom manufacturing',
'ORG-001653':'Bruns Brush nylon polypropylene filament material manufacture',
'ORG-001698':'Prime Engineered Plastics Canton injection molding manufacture',
'ORG-001703':'Premier Aerosol Packaging polymer adhesive formulation manufacture',
'ORG-001708':'ECM Performance Materials Medina thermoplastic compounds manufacture',
'ORG-001714':'AML Industries polymer coatings formulation manufacturing',
'ORG-001719':'Pyramid Plastics Cleveland extrusion molding manufacturing',
'ORG-001721':'Truco Cleveland elastomeric coating formulation manufacturing',
'ORG-001724':'Republic Powdered Metals roof coating polymer formulation manufacture',
'ORG-001794':'Dal Little vinyl fabric heat sealing fabrication manufacture',
'ORG-001891':'Scherba Inflatable Images vinyl PVC fabric welding manufacturing',
'ORG-001922':'Faull and Son in house nylon molding bearing manufacture not customer use',
'ORG-001929':'HyComp phenolic carbon fiber compression molding manufacture',
'ORG-001931':'Lauren Manufacturing Cooper Standard ISG EPDM extrusion manufacture',
'ORG-001934':'Rack Coating Services own powder coating applying process',
'ORG-001940':'Synthetic Rubber Technologies Uniontown rubber compounding production',
'ORG-001943':'Trans Foam Tallmadge foam fabrication polyurethane manufacturing',
'ORG-001945':'Vinyl Profiles North Jackson PVC profile extrusion manufacture',
'ORG-001997':'Quikey Akron soft vinyl injection molding manufacture',
'ORG-001999':'Raydar Ohio Wadsworth rubber molding manufacture',
'ORG-002010':'Sherwood Advanced Composite Louisville resin molding manufacture',
'ORG-002011':'Solutions in Polycarbonate Medina sheet fabrication manufacture',
'ORG-002030':'Veretec Jefferson plastic composite molding manufacture',
'ORG-002031':'Vinyltech International North Jackson PVC extrusion manufacture',
'ORG-002034':'Gizmo Whip Guide nylon injection molded manufacture',
'ORG-002047':'Wayne Dalton Plastics Conneaut injection molding manufacture',
'ORG-002049':'Sietins Bedford precision plastic molding manufacture',
'ORG-002055':'Neo Industries Conneaut polymer coating formulation manufacture',
'ORG-002057':'Quality Fiberglass Marshallville resin composites manufacture',
'ORG-002080':'Mitsubishi Chemical Performance Polymers Ohio thermoplastic compounding manufacture',
'ORG-002135':'Applied Specialties own polymer water treatment formulation manufacture',
'ORG-002148':'Arthur Corporation Huron plastic injection molding manufacture',
'ORG-002153':'Checkpoint Alpha Canton plastic injection molded security product manufacture',
'ORG-002157':'Custom Pultrusions Aurora fiberglass resin pultrusion manufacture',
'ORG-002167':'Plymouth Foam Newcomerstown expanded polystyrene foam manufacturing'
}
DOM={'ORG-000210':'barentz.com','ORG-001453':'flowpolymers.com','ORG-001459':'survitecgroup.com','ORG-001721':'truco-inc.com','ORG-002080':'m-chemical.co.jp'}
rows=[]
for r in F:
 oid=r['org_id'];ee=E[oid];hold=next((e for e in reversed(ee) if 'STILL_UNCERTAIN' in e['detail']),ee[-1] if ee else {'file':'frame.csv','detail':r['notes'] or 'No detailed prior capability verdict; held gap only.'})
 pri=hold['file']+' :: '+hold['detail'][:650]+' :: prior_routes.csv '+str(len(P[oid]))+' normalized routes; '+ '; '.join(x['url'] for x in list(P[oid].values())[:2])
 route='';basis='No untried decisive own route identified; no claim of public internet absence.'
 if oid in B:cl='b';reason,fact=B[oid]
 elif oid in DE:cl='d';reason=DE[oid];fact='Re-verify actual operator activity against held Ring1–2 producer scope; owner/integrator resolves any scope/status motion. No change inferred here.'
 elif oid in C:cl='c';reason=C[oid];fact=reason+' Reviewed public packet does not settle that fact; human confirmation may identify a new public witness.'
 else:
  assert oid in FACTS,oid
  cl='a';fact='An own corporate statement of '+FACTS[oid]+', attributable to the held entity, with an adopted §3.1 process or §3.2 material explicitly named.'
  domain=DOM.get(oid,(urlsplit(r['website'].split(' (')[0] if '://' in r['website'] else 'https://'+r['website']).hostname or '').removeprefix('www.'))
  assert domain,oid
  query='site:'+domain+' '+FACTS[oid]+' (filetype:pdf OR technical OR capabilities)'
  route='official-domain-search: '+query
  if oid=='ORG-000414':route='https://koroseal.com/getmedia/717ccc84-ec0a-43c9-a4f2-c21a8d97c667/17953?disposition=inline';assert norm(route) not in allprior
  reason='Specific untried own-domain route seeks '+FACTS[oid]+'. Prior pages/routes below did not settle this fact; this is a bounded source attempt, not assurance that an admissible statement exists.'
  basis='Compared against '+str(len(allprior))+' globally normalized known prior URLs from rounds1–5 CSV logs and available .url archives; '+('exact EPD PDF URL absent from prior routes' if route.startswith('http') else 'this named official-domain/fact search is absent from prior route logs; all result URLs will be deduplicated before any source fetch')+'. HTTP/HTTPS, www, trailing slash, fragments, query order and percent encoding normalized.'
 rows.append(dict(org_id=oid,gap='capabilities',**{'class':cl},reason=reason,source_route=route,route_not_tried_basis=basis,prior_evidence=pri,settling_fact=fact,work_outcome='PENDING' if cl=='a' else 'NOT_DESK_ROUTE',attempted_url='',source_date='',raw_quote_evidence='',missing_fact=fact,postwork_recommended_class=cl))
with (D/'classification_routes.csv').open('w') as f:
 w=csv.DictWriter(f,rows[0].keys());w.writeheader();w.writerows(rows)
(D/'initial_classifications.json').write_text(json.dumps(rows,indent=2))
from collections import Counter
print('PASS',len(rows),'unique capability-gap organizations;',dict(Counter(r['class'] for r in rows)),'prior normalized URLs',len(allprior))

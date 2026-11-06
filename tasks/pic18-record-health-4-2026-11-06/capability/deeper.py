"""One targeted follow-up when navigation/index routes consumed the initial six attempts."""
from research import D,fetch
import json
from concurrent.futures import ThreadPoolExecutor
urls={
'ORG-000078':'https://www.gi-de.com/en/industries/payment/eco-innovations',
'ORG-000414':'https://koroseal.com/products/architectural-systems/architectural-products/surface-materials/high-pressure-laminate-(hpl)-ha2t',
'ORG-000439':'https://www.mickeythompsontires.com/en-us/tires',
'ORG-000552':'https://rogersusa.com/products/',
'ORG-001580':'https://chemicalsolvents.com/toll-manufacturing/',
'ORG-001631':'https://www.akrondispersions.com/products/dispersions/',
'ORG-001648':'https://tuffboom.com/products/',
'ORG-001717':'https://flexlinkllc.com/our-products/',
'ORG-001768':'https://actionsuper.com/products/bonded-grinding-wheels/resin-bond-wheels/',
'ORG-001891':'https://inflatableimages.com/custom-inflatable-manufacturer/',
'ORG-002146':'https://altorsolutions.com/cold-chain-packaging/insulated-shippers/',
'ORG-001730':'https://3d-dent.com/product/nano-hybrid-composite-syringe/',
'ORG-000873':'https://hamiltonpolymers.com/products/',
'ORG-002153':'https://www.alphaworld.com/products',
}
def one(item):
 oid,url=item; r,t,h=fetch(oid,url,'targeted_product_followup'); p=D/'raw'/oid/'routes.json'; rr=json.loads(p.read_text()); rr.append(r);p.write_text(json.dumps(rr,indent=2));print(oid,r['http_status'],len(t),flush=True)
with ThreadPoolExecutor(max_workers=7) as ex:list(ex.map(one,urls.items()))

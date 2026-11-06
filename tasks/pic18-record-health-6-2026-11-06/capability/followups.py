from inventory import D,norm
from research import fetch
import json
prior={u for v in json.loads((D/'prior_routes.json').read_text()).values() for u in v}
J=[('ORG-000210','https://www.barentz.com/knowledge/'),('ORG-000401','https://juggerbot3d.com/3d-printing-services/'),('ORG-001595','https://1110gear.com/collections/shop-by-use/products/rigid-tq-case-for-c-a-t'),('ORG-001648','https://tuffboom.com/what-we-do/'),('ORG-001891','https://www.inflatableimages.com/custom-inflatables/'),('ORG-000488','https://www.pharmacylite.com/products/plastic-ovals-with-cr-caps')]
for oid,u in J:
 assert norm(u) not in prior,(oid,u)
 r,t=fetch(oid,u,'targeted_own_fact_followup');print(oid,r['http_status'],len(t),flush=True)

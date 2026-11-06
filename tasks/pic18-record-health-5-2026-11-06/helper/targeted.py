from research import D,fetch
import json
for oid,url in [('ORG-000198','https://www.zieglertire.com/contact-us'),('ORG-000551','https://www.roechling.com/us/industrial/cleveland')]:
 r,t,h=fetch(oid,url,'targeted_location_followup');p=D/'raw'/oid/'routes.json';rr=json.loads(p.read_text());rr.append(r);p.write_text(json.dumps(rr,indent=2));print(oid,r['http_status'],len(t))

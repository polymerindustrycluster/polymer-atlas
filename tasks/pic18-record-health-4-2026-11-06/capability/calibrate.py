from research import D,has
import json
checks=[('CAL-novex','polyurethane_pu','a leading manufacturer of high-performance polyurethane conveyor belting and sheeting'),('CAL-mipco','epoxy','We are the manufacturer and packager of 100% solids epoxy flooring repair and resurfacing materials'),('CAL-tuftex','natural_rubber_nr','TUFTEX Balloons are made from 100% natural rubber latex')]
rows=[]
for oid,value,quote in checks:
 r=json.loads((D/'raw'/oid/'routes.json').read_text())[0]; assert r['availability']=='available'; assert has((D/r['raw_path']).read_text(),quote)
 rows.append(dict(org_id=oid,value=value,quote=quote,source_ref=r['source_ref'],raw_path=r['raw_path']))
assert not has((D/rows[0]['raw_path']).read_text(),'Novex manufactures epoxy floor patch from natural rubber')
(D/'calibration.json').write_text(json.dumps({'positive_checks':rows,'wrong_quote_negative':'PASS: Novex manufactures epoxy floor patch from natural rubber rejected'},indent=2))
print('PASS: 3 own-primary positives, 1 wrong-quote negative')

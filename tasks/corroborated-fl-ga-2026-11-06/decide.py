"""Curated held-parent resolutions; other clusters remain explicit holds."""
import csv,json
from pathlib import Path
H=Path(__file__).parent
pairs='''00292 002521
00217 002643
00134 001033
00421 004300
00344 000853
00261 001408
00116 001403
00441 000566
00014 002349
00286 004965
00379 004516
00009 002723
00209 001128
00154 001128
00582 000259
00744 004995
00028 000132'''
selected={f'LF-FL-{a}':f'ORG-{b}' for a,b in (s.split() for s in pairs.splitlines())}
rows=list(csv.DictReader(open(H/'input.csv')))
with open(H/'verdicts.csv','w') as f:
 w=csv.DictWriter(f,fieldnames=['cluster_id','verdict','held_org_id','reason'],lineterminator='\n');w.writeheader()
 for c in rows:
  oid=selected.get(c['cluster_id'],'')
  reason='Held parent name/registrant resolved; site-grade ITA CY2025 filing; provisional federal-only tier C.' if oid else 'HOLD: needs an unambiguous operator/ultimate-parent and site-scope witness; federal cluster alone does not settle ownership or current scope. Recommend primary operator page before creation.'
  if c['cluster_id']=='LF-FL-00358': reason='HOLD: Dart ORG-002441 is held (B-ALIAS); 1605 Turkey Creek Rd must be reconciled against held SITE-010912 at 4610 Airport Rd before treating it as a distinct establishment.'
  if c['cluster_id']=='LF-FL-00087': reason='HOLD: Carpenter 5100 vs held SITE-005317 at 5150 Frontage Rd S; settle same-campus identity before creating.'
  if c['cluster_id']=='LF-FL-00047': reason='HOLD: TSE campus at 5260 vs held 5180 113th Ave N and 4370 112th Terrace; settle distinct establishment vs campus address.'
  w.writerow(dict(cluster_id=c['cluster_id'],verdict='VERIFIED' if oid else 'STILL_UNCERTAIN',held_org_id=oid,reason=reason))
print('selected',len(selected),'worked',len(rows))

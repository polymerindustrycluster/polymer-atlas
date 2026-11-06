"""Runnable packet/census/novel-route check with positive and negative controls."""
from research import D,has
import csv,json,re,unicodedata
from urllib.parse import urlsplit,urlunsplit,parse_qsl,urlencode,unquote
from collections import Counter

def norm(u):
 s=urlsplit(u.strip().rstrip('.,;'));return urlunsplit(('https',(s.hostname or '').lower().removeprefix('www.'),re.sub('/+','/',unquote(s.path)).rstrip('/') or '/',urlencode(sorted((k,v) for k,v in parse_qsl(s.query,keep_blank_values=True) if not k.startswith('utm_'))),''))
def read(p):return list(csv.DictReader(p.open()))
rows=read(D/'classification_routes.csv');initial=json.loads((D/'initial_classifications.json').read_text());frame=json.loads((D/'frame.json').read_text());assert len(rows)==len({r['org_id'] for r in rows})==93 and {r['org_id'] for r in rows}=={r['org_id'] for r in frame}
assert Counter(r['class'] for r in rows)=={'a':62,'b':3,'c':20,'d':8}
original={r['org_id']:r for r in initial};immutable=['org_id','gap','class','reason','source_route','route_not_tried_basis','prior_evidence','settling_fact']
for r in rows:
 for k in immutable:assert r[k]==original[r['org_id']][k],(r['org_id'],k)
 if r['class']=='a':
  assert r['work_outcome'] in {'VERIFIED','STILL_UNCERTAIN'} and r['attempted_url']
  if r['work_outcome']=='STILL_UNCERTAIN':assert r['missing_fact'] and r['postwork_recommended_class'] in {'b','c','d'}
packet=read(D/'packet.csv');assert len(packet)==len({(r['org_id'],r['field'],r['value']) for r in packet})==14;assert len({r['org_id'] for r in packet})==5
vocab=json.loads((D.parents[2]/'docs/schema/vocab.json').read_text())['vocabularies'];prior={u for vv in json.loads((D/'prior_routes.json').read_text()).values() for u in vv};routes=read(D/'routes.csv')
assert len(routes)==128 and sum(r['kind']=='official_domain_search' for r in routes)==61
for r in packet:
 assert r['field'] in {'processes','materials'} and r['value'] in vocab[r['field'].upper()]['values']
 assert has((D/r['raw_path']).read_text(),r['quote']),(r['org_id'],r['value'])
 assert norm(r['source_ref']) not in prior
 assert r['source_class']=='own_site' and r['observed_date']=='2026-11-06'
 assert any(x['org_id']==r['org_id'] and x['attempted_url']==r['source_ref'] and x['availability']=='available' for x in routes)
assert {r['org_id'] for r in packet}=={r['org_id'] for r in rows if r['work_outcome']=='VERIFIED'}
# Old three positive calibration witnesses reused as controls only, never new evidence.
cal=json.loads((D/'calibration_controls.json').read_text())
for r in cal:assert has((D/r['raw_path']).read_text(),r['quote'])
new=json.loads((D/'calibration.json').read_text());text=(D/new['new_route']['raw_path']).read_text();assert has(text,new['positive_quote'])
assert not has(text,'Koroseal manufactures polyurethane tire curing machinery')
# Reject a boundary/subsequence false positive and detect a proposed wrong quote.
assert not has('polyethylene','poly')
wrong=dict(packet[0],quote='Addipel manufactures steel tire curing machinery')
assert not has((D/wrong['raw_path']).read_text(),wrong['quote'])
print('PASS:93 frozen unique classifications;62 A outcomes(5 VERIFIED/57 held);14 vocabulary-valid raw-matched values/5 organizations;128 route attempts(61 searches/67 fetches);3 prior positives+new PDF positive+wrong-quote and substring negatives.')

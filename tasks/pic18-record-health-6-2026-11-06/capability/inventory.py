"""Read-only prior-route reconciliation for the frozen capability census."""
import csv,json,re,sys
from pathlib import Path
from urllib.parse import urlsplit,urlunsplit,parse_qsl,urlencode,unquote
D=Path(__file__).resolve().parent;H=Path('/tmp/l4-r6-history/tasks')
def norm(u):
 u=u.strip().rstrip('.,;');s=urlsplit(u);host=(s.hostname or '').lower().removeprefix('www.');p=re.sub('/+','/',unquote(s.path)).rstrip('/') or '/';q=urlencode(sorted((k,v) for k,v in parse_qsl(s.query,keep_blank_values=True) if not k.startswith('utm_')));return urlunsplit(('https',host,p,q,''))
def rows(p):
 try:return list(csv.DictReader(p.open()))
 except (UnicodeDecodeError,csv.Error):return []
frame=json.loads((D/'frame.json').read_text()) if (D/'frame.json').exists() else [r for r in rows(D.parent/'frame.csv') if r['gap_capabilities']=='1'];assert len(frame)==len({r['org_id'] for r in frame})==93
ids={r['org_id'] for r in frame};routes={i:{} for i in ids};evidence={i:[] for i in ids}
for p in H.rglob('*.csv'):
 for r in rows(p):
  oid=r.get('org_id') or r.get('record_id') or r.get('record')
  if oid not in ids:continue
  desc='; '.join(r[k] for k in ['verdict','settling_fact','missing_fact','detail','reason','notes'] if r.get(k))
  if desc:evidence[oid].append({'file':str(p),'detail':desc})
  for v in r.values():
   for u in re.findall(r'https?://[^\s<>"\]\[;]+',v or ''):
    try:routes[oid].setdefault(norm(u),{'url':u,'file':str(p)})
    except ValueError:pass
for root in ['/tmp/l4b-capraw','/tmp/l4b-r3-raw','/tmp/l4-r4-duperaw']:
 for p in Path(root).glob('*.url'):
  oid=p.name[:10]
  if oid not in ids:continue
  for u in p.read_text().splitlines():
   if u.startswith('http'):
    try:routes[oid].setdefault(norm(u),{'url':u,'file':str(p)})
    except ValueError:pass
for key,obj in [('frame',frame),('prior_routes',routes),('prior_evidence',evidence)]:
 (D/(key+'.json')).write_text(json.dumps(obj,indent=2))
with (D/'prior_routes.csv').open('w') as f:
 w=csv.DictWriter(f,['org_id','normalized_url','tried_url','prior_log']);w.writeheader()
 for oid,v in sorted(routes.items()):
  for k,r in sorted(v.items()):w.writerow({'org_id':oid,'normalized_url':k,'tried_url':r['url'],'prior_log':r['file']})
if __name__=='__main__':
 for r in frame:
  oid=r['org_id'];ee=evidence[oid];hold=next((e for e in reversed(ee) if 'STILL_UNCERTAIN' in e['detail']),ee[-1] if ee else {'detail':'No prior detailed verdict found'})
  print(oid,r['legal_name'],'ROUTES',len(routes[oid]),hold['detail'][:430])

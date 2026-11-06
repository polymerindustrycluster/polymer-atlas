import urllib.request,os,json,time
out=[]
for code in ['326','3261','3262','3252','3259']:
 u='https://api.census.gov/data/2023/cbp?get=NAME,ESTAB&for=county:*&in=state:39&EMPSZES=001&NAICS2017='+code+'&key='+os.environ['CENSUS_API_KEY']
 for attempt in range(3):
  try:
   with urllib.request.urlopen(u,timeout=45) as r:d=json.load(r)
   break
  except Exception:
   if attempt==2:raise
 if not out:out=d[:1]
 out+=d[1:];print(code,len(d)-1,flush=True)
open('tasks/source-scout-3-2026-11-06/cbp/api_totals.json','w').write(json.dumps(out,indent=2)+'\n')

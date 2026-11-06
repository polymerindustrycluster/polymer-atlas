import urllib.request,os,json,pathlib,concurrent.futures
root=pathlib.Path('/tmp/l5-patents');root.mkdir(exist_ok=True)
d=json.load(open(pathlib.Path(__file__).with_name('bulk_manifest.json')))
class NoRedirect(urllib.request.HTTPRedirectHandler):
 def redirect_request(self,*a,**k):return None
op=urllib.request.build_opener(NoRedirect)
def run(f):
 p=root/f['fileName']
 if p.exists() and p.stat().st_size==f['fileSize']:return
 try:op.open(urllib.request.Request(f['fileDownloadURI'],headers={'X-API-KEY':os.environ['USPTO_API_KEY']}),timeout=60)
 except urllib.error.HTTPError as e:
  assert e.code==302;url=e.headers['Location']
 with urllib.request.urlopen(url,timeout=300) as r,p.open('wb') as out:
  while b:=r.read(1<<20):out.write(b)
 assert p.stat().st_size==f['fileSize'];print(p.name,p.stat().st_size,flush=True)
fs=[f for f in d['productFileBag']['fileDataBag'] if f['fileName'] in [x+'.tsv.zip' for x in ['g_patent','g_cpc_current','g_location_disambiguated','g_assignee_disambiguated']]]
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:list(pool.map(run,fs))

"""Fresh curl receipts; house W matcher and existing page-text extractor."""
import argparse,csv,hashlib,json,runpy,subprocess,sys,tempfile
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
sys.path.insert(0,str(ROOT/'tasks/pic18-record-health-2026-11-06'))
Text=runpy.run_path(str(ROOT/'tasks/pic18-record-health-2026-11-06/refetch.py'))['Text']
W=runpy.run_path(str(ROOT/'tasks/evidence-repair-2-2026-11-04/prep.py'))['W']
def read(p):
 with open(p,newline='') as f:return list(csv.DictReader(f))
def found(text,quote):
 p,q=W(text),W(quote)
 return bool(q) and any(p[i:i+len(q)]==q for i in range(len(p)-len(q)+1))
def parcel_check(result,expected):
 assert 'error' not in result and not result.get('exceededTransferLimit'),'uninspected parcel response'
 assert len(result.get('features',[]))==1,'ambiguous/empty parcel result'
 assert result['features'][0]['attributes']==expected['features'][0]['attributes'],'parcel key/street drift'
def main(known):
 sources=read(HERE/'sources.csv')
 if known:sources=[r for r in sources if r['key'] in ('acsic','wrs','synthomer')]
 out=[];cache={}
 with tempfile.TemporaryDirectory() as tmp:
  for r in sources:
   if r['url'] not in cache:
    p=Path(tmp)/'raw'
    subprocess.run(['curl','-fLsS','--max-time','65','-A','Mozilla/5.0',r['url'],'-o',str(p)],check=True)
    raw=p.read_bytes(); text=raw.decode('utf-8','replace')
    if r['format']=='pdf':
     subprocess.run(['pdftotext','-layout',str(p),str(p)+'.txt'],check=True);text=Path(str(p)+'.txt').read_text()
    elif r['format']=='html':
     parser=Text();parser.feed(text);text=' '.join(parser.parts)
    else:
     j=json.loads(text)
     if r['key'] in ('franklin','union','ashtabula'):parcel_check(j,json.loads((HERE/(r['key']+'-parcel.json')).read_text())['result'])
    cache[r['url']]=(text,hashlib.sha256(raw).hexdigest(),len(raw))
   text,sha,size=cache[r['url']]
   ok=found(text,r['quote']);assert ok,('quote absent',r['key'])
   assert not found(text,'Fabricated authorization for invented parcel 9999 Moonlight Court'),'false match'
   out.append(dict(key=r['key'],url=r['url'],quote=r['quote'],raw='yes',observed_date='2026-11-06',sha256=sha,bytes=size))
   print(r['key'],'PASS',flush=True)
  if not known:
   for e in read(HERE/'evidence.csv'):
    q=e['claim_detail'].split('raw quote: "',1)[1].rsplit('"',1)[0]
    assert found(cache[e['source_ref']][0],q),e['evidence_id']
 with (HERE/('known_answers.csv' if known else 'rawcheck.csv')).open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(out[0]),lineterminator='\n');w.writeheader();w.writerows(out)
 print('PASS',len(out),'source quote checks;',len(cache),'fresh URLs; fabrication rejected on every page')
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--known',action='store_true');main(p.parse_args().known)
